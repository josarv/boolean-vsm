from typing import Protocol, List

from .index import InvertedIndex
from .postings import PostingList

# TODO: make proper display functions, maybe methods of AST class?

class AST:
    def __init__(self, query: str, root):
        self.query = query
        self.root = root

    def __repr__(self):
        # return f"AST({self.query}, {self.root})"
        return f'{self.root}'

class ASTNode(Protocol):
    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList: ...
    def __repr__(self) -> str: ...

class ASTTermNode:
    def __init__(self, term: str):
        self.term = term

    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        return inverted_index.term_postings(self.term)

    def __repr__(self) -> str:
        return f"Term('{self.term}')"

class ASTAndNode:
    def __init__(self, children: List[ASTNode]):
        self.children = children

    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        if not self.children:
            return inverted_index.universe_postings() # and identity
        result = self.children[0].evaluate(inverted_index)
        for child in self.children[1:]:
            result &= child.evaluate(inverted_index)
            if not result:  # short circuit
                break
        return result

    def __repr__(self) -> str:
        return "AND(" + ", ".join(map(str, self.children)) + ")"

class ASTOrNode:
    def __init__(self, children: List[ASTNode]):
        self.children = children

    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        if not self.children:
            return inverted_index.empty_postings()
        universe = inverted_index.universe_postings()
        result = self.children[0].evaluate(inverted_index)
        for child in self.children[1:]:
            result |= child.evaluate(inverted_index)
            if result == universe:  # short circuit
                break
        return result

    def __repr__(self) -> str:
        return "OR(" + ", ".join(map(str, self.children)) + ")"

class ASTNotNode:
    def __init__(self, child: ASTNode):
        self.child = child

    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        return inverted_index.universe_postings() - self.child.evaluate(inverted_index)

    def __repr__(self) -> str:
        return f"NOT({self.child})"

class ASTTrueNode:
    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        return inverted_index.universe_postings()

    def __repr__(self) -> str:
        return "TRUE"

class ASTFalseNode:
    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        return inverted_index.empty_postings()

    def __repr__(self) -> str:
        return "FALSE"
