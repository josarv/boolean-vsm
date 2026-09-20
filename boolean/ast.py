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
            return inverted_index.universe_postings().copy() # and identity
        # copy: the first operand may be a posting list owned by the index, and
        # the in-place operators below would otherwise corrupt it
        result = self.children[0].evaluate(inverted_index).copy()
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
        # copy, for the same reason as in ASTAndNode
        result = self.children[0].evaluate(inverted_index).copy()
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
        return inverted_index.universe_postings().copy()

    def __repr__(self) -> str:
        return "TRUE"

class ASTFalseNode:
    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        return inverted_index.empty_postings()

    def __repr__(self) -> str:
        return "FALSE"

class ASTIdentityNode:
    """Placeholder for an empty group, e.g. the "(( ))" in "a && (( ))".

    Which constant an empty group stands for depends on the operator that
    contains it: it is TRUE under AND ("a && (( ))" == "a") but FALSE under OR
    ("a || (( ))" == "a"). The parser knows that context and replaces this node
    with the right constant, so it never survives to evaluation.
    """

    def evaluate(self, inverted_index: "InvertedIndex") -> PostingList:
        raise RuntimeError("ASTIdentityNode must be resolved by the parser before evaluation")

    def __repr__(self) -> str:
        return "IDENTITY"
