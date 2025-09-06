from typing import Protocol, List, Callable
from re import compile, split
from .ast import AST, ASTNode, ASTAndNode, ASTOrNode, ASTNotNode, ASTTermNode, ASTTrueNode, ASTFalseNode

class Parser(Protocol):
    def parse(self, query: str) -> AST: ...

# GRAMMAR PARSED:
# QUERY -> EXPR
# EXPR -> OR_EXPR
# OR_EXPR -> AND_EXPR { "||" AND_EXPR }
# AND_EXPR -> NOT_EXPR { "&&" NOT_EXPR }
# NOT_EXPR -> "!!" NOT_EXPR | "((" EXPR "))" | ATOM
# ATOM -> TERM | "#true" | "#false"
class RecursiveDescentParser:
    TOKEN_REGEX = compile(r"&&|\|\||!!|\(\(|\)\)|#\w+|\S+")

    def __init__(self):
        self.tokens: List[str] = []
        self.position: int = 0

    def parse(self, query: str) -> AST:
        self.tokens = self.TOKEN_REGEX.findall(query)
        self.position = 0
        root = self._parse_expr()
        if root is None:
            root = ASTFalseNode()  # empty query evaluates to false
        return AST(query, root)

    # EXPR -> OR_EXPR
    def _parse_expr(self) -> ASTNode | None:
        return self._parse_or()

    # EXPR -> AND_EXPR { "||" AND_EXPR }
    def _parse_or(self) -> ASTNode | None:
        node = self._parse_and()
        while self._accept("||"):
            right = self._parse_and()
            if right is None:
                right = ASTFalseNode()  # dangling operator, likely from stopword removal
            if node is None:
                node = ASTFalseNode()
            node = ASTOrNode([node, right])
        return node

    # AND_EXPR -> NOT_EXPR { "&&" NOT_EXPR }
    def _parse_and(self) -> ASTNode | None:
        node = self._parse_not()
        while self._accept("&&"):
            right = self._parse_not()
            if right is None:
                right = ASTTrueNode()
            if node is None:
                node = ASTTrueNode()
            node = ASTAndNode([node, right])
        return node

    # NOT_EXPR -> "!!" NOT_EXPR | "((" EXPR ")) | TERM
    def _parse_not(self) -> ASTNode | None:
        if self._accept("!!"):
            child = self._parse_not()
            if child is None:
                child = ASTFalseNode()
            return ASTNotNode(child)
        elif self._accept("(("):
            node = self._parse_expr()
            self._expect("))")
            return node
        else:
            return self._parse_term()

    # TERM -> IDENT | "#true" | "#false"
    def _parse_term(self) -> ASTNode | None:
        if self._current() is None:
            return None
        term = self._current()
        if term in {"&&", "||", "!!", "((", "))"}:
            return None
        self._advance()
        if term.lower() == "#true":
            return ASTTrueNode()
        elif term.lower() == "#false":
            return ASTFalseNode()
        else:
            return ASTTermNode(term)

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
