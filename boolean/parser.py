from typing import Protocol, List, Callable
from re import compile, split
from .ast import (
    AST,
    ASTNode,
    ASTAndNode,
    ASTOrNode,
    ASTNotNode,
    ASTTermNode,
    ASTTrueNode,
    ASTFalseNode,
    ASTIdentityNode,
)

class Parser(Protocol):
    def parse(self, query: str) -> AST: ...

# GRAMMAR PARSED:
# QUERY -> EXPR
# EXPR -> OR_EXPR
# OR_EXPR -> AND_EXPR { "||" AND_EXPR }
# AND_EXPR -> NOT_EXPR { "&&" NOT_EXPR | NOT_EXPR }
# NOT_EXPR -> "!!" NOT_EXPR | "((" EXPR "))" | ATOM
# ATOM -> TERM | "#true" | "#false"
class RecursiveDescentParser:
    TOKEN_REGEX = compile(r"&&|\|\||!!|\(\(|\)\)|#\w+|\w+")

    def __init__(self):
        self.tokens: List[str] = []
        self.position: int = 0

    def parse(self, query: str) -> AST:
        self.tokens = self.TOKEN_REGEX.findall(query)
        self.position = 0
        root = self._parse_expr()
        # every token must be consumed, otherwise we would silently drop part of
        # the query, e.g. "a )) && b" would quietly evaluate as just "a"
        if self._current() is not None:
            raise SyntaxError(
                f"Unexpected token '{self._current()}' at position {self.position}"
            )
        if root is None or isinstance(root, ASTIdentityNode):
            root = ASTFalseNode()  # an empty query matches nothing
        return AST(query, root)

    # EXPR -> OR_EXPR
    def _parse_expr(self) -> ASTNode | None:
        return self._parse_or()

    # EXPR -> AND_EXPR { "||" AND_EXPR }
    def _parse_or(self) -> ASTNode | None:
        # parse first operand
        node = self._parse_and()
        # if there's no "||" after it, return it directly
        if not self._current() == "||":
            return node
        # if there is, parse all operands into a list
        # FALSE is the identity of OR, so it covers both a dangling operator and
        # an empty group ("a || (( ))" == "a")
        children = [self._resolve_identity(node, ASTFalseNode)]
        # loop to parse all subsequent operands
        while self._accept("||"):
            next_node = self._parse_and()
            children.append(self._resolve_identity(next_node, ASTFalseNode))
        return ASTOrNode(children)

    # AND_EXPR -> NOT_EXPR { "&&" NOT_EXPR | NOT_EXPR }
    def _parse_and(self) -> ASTNode | None:
        # parse first operand
        node = self._parse_not()
        children = [] if node is None else [node]
        # loop to parse all subsequent operands
        while True:
            # check for explicit "&&"
            if self._accept("&&"):
                next_node = self._parse_not()
                # a dangling operator leaves a hole, same as an empty group
                children.append(ASTIdentityNode() if next_node is None else next_node)
            # check for implicit AND (no operator, just juxtaposition)
            elif self._current() and self._current() not in {"||", "))"}:
                next_node = self._parse_not()
                if next_node is not None:
                    children.append(next_node)
            else:
                break
        if not children:
            return None
        # a lone operand is passed up untouched: if it is an empty group, the
        # enclosing OR (or the root) decides what it stands for, not this AND
        if len(children) == 1:
            return children[0]
        # AND does apply, so any hole among the operands is its identity, TRUE
        # ("a && (( ))" == "a")
        return ASTAndNode([self._resolve_identity(child, ASTTrueNode) for child in children])

    # NOT_EXPR -> "!!" NOT_EXPR | "((" EXPR ")) | TERM
    def _parse_not(self) -> ASTNode | None:
        if self._accept("!!"):
            # nothing to negate ("!!" alone, or "!!(( ))") negates FALSE
            child = self._resolve_identity(self._parse_not(), ASTFalseNode)
            return ASTNotNode(child)
        elif self._accept("(("):
            node = self._parse_expr()
            self._expect("))")
            # an empty group has no constant value of its own: "term && (( ))"
            # means "term && true", but "term || (( ))" means "term || false".
            # the enclosing operator resolves it (see _parse_and / _parse_or).
            if node is None:
                return ASTIdentityNode()
            return node
        else:
            return self._parse_term()

    # TERM -> IDENT | "#true" | "#false"
    def _parse_term(self) -> ASTNode | None:
        term = self._current()
        if term is None or term in {"&&", "||", "!!", "((", "))"}:
            return None
        self._advance()
        if term.lower() == "#true":
            return ASTTrueNode()
        elif term.lower() == "#false":
            return ASTFalseNode()
        else:
            return ASTTermNode(term)

    # replaces a missing operand or an empty group with the identity element of
    # the enclosing operator (TRUE for AND, FALSE for OR)
    @staticmethod
    def _resolve_identity(node: ASTNode | None, identity: type) -> ASTNode:
        if node is None or isinstance(node, ASTIdentityNode):
            return identity()
        return node

    # checks and consumes a token if present
    def _accept(self, token: str) -> bool:
        if self._current() == token:
            self._advance()
            return True
        return False

    # enforces a token must appear, else error
    def _expect(self, token: str) -> None:
        if not self._accept(token):
            raise SyntaxError(f"Expected token '{token}' at position {self.position}, got '{self._current()}'")

    def _current(self) -> str | None:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def _advance(self) -> None:
        self.position += 1

def preserve_boolean_operators(preprocessing_pipeline: Callable[[str], list[str]]) -> Callable[[str], str]:
    operator_regex = compile(r"&&|\|\||!!|\(\(|\)\)|#\w+")  # tokenizer might split # + true/false
    def wrapper(query_string: str) -> str:
        try:
            substrings = split(operator_regex, query_string)
            operators = operator_regex.findall(query_string)
            processed_substrings = []
            for i, substring in enumerate(substrings):
                if substring.strip():
                    preprocessed_tokens = preprocessing_pipeline(substring)
                    preprocessed_strings = " ".join(preprocessed_tokens)
                    processed_substrings.append(preprocessed_strings)
                if i < len(operators):
                    processed_substrings.append(operators[i])

            return " ".join(filter(None, (s.strip() for s in processed_substrings)))
        except Exception as e:
            print(f"An error occurred during query preprocessing: {e}")
            return query_string
    return wrapper
