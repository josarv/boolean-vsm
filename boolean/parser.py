from typing import Protocol, List
from re import compile
from .ast import AST, ASTNode, ASTAndNode, ASTOrNode, ASTNotNode, ASTTermNode, ASTTrueNode, ASTFalseNode

class Parser(Protocol):
    def parse(self, query: str) -> AST: ...

# TODO: add true/false atoms
# TODO: check why regex is different from preserve_boolean_operators
# TODO: move preserve_boolean_operators here?
TOKEN_REGEX = compile(r"&&|\|\||!!|\(\(|\)\)|\S+")

class RecursiveDescentParser:
    def __init__(self):
        self.tokens: List[str] = []
        self.position: int = 0

    def parse(self, query: str) -> AST:
        self.tokens = TOKEN_REGEX.findall(query)
        self.position = 0
        root = self._parse_or()
        if root is None:
            root = ASTFalseNode()  # empty query evaluates to false
        return AST(query, root)

    def _parse_expr(self) -> ASTNode | None:
        return self._parse_or()

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

    def _parse_term(self) -> ASTNode | None:
        if self._current() is None:
            return None
        term = self._current()
        if term in {"&&", "||", "!!", "((", "))"}:
            return None
        self._advance()
        return ASTTermNode(term)

    def _accept(self, token: str) -> bool:
        if self._current() == token:
            self._advance()
            return True
        return False

    def _expect(self, token: str) -> None:
        if not self._accept(token):
            raise SyntaxError(f"Expected token '{token}' at position {self.position}, got '{self._current()}'")

    def _current(self) -> str | None:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def _advance(self) -> None:
        self.position += 1
