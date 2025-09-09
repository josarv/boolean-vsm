from typing import Protocol, Set, List

from .index import InvertedIndex

# TODO: make proper display functions, maybe methods of AST class?
# TODO: make ast nodes dataclasses?

class AST:
    def __init__(self, query: str, root):
        self.query = query
        self.root = root

    def __repr__(self):
        # return f"AST({self.query}, {self.root})"
        return f'{self.root}'

# built in to the protocol, is that the inverted index returns a set of ids
# this dictates that the nodes are evaluated via set operations (intersection, union, inversion)
# this should be later modified to allow for bit vectors to be returned
# which in turn allow for much faster bitwise operations
# to do this define a type - protocol, say boolean set, with the operations required
# __and__, __or__, __sub__, whatever
# this can be used to wrap sets, bitvectors or otherwise
# the ASTNode class will only depend on that type
class ASTNode(Protocol):
    def evaluate(self, inverted_index: "InvertedIndex") -> Set[int]: ...
    def __repr__(self) -> str: ...

class ASTTermNode:
    def __init__(self, term: str):
        self.term = term

    def evaluate(self, inverted_index: "InvertedIndex") -> Set[int]:
        return inverted_index.postings(self.term)

    def __repr__(self) -> str:
        return f"Term('{self.term}')"

class ASTAndNode:
    def __init__(self, children: List[ASTNode]):
        self.children = children

    def evaluate(self, inverted_index: "InvertedIndex") -> Set[int]:
        if not self.children:
            return inverted_index.all_documents() # and identity
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

    def evaluate(self, inverted_index: "InvertedIndex") -> Set[int]:
        if not self.children:
            return set()  # or identity
        universe = inverted_index.all_documents()
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

    def evaluate(self, inverted_index: "InvertedIndex") -> Set[int]:
        return inverted_index.all_documents() - self.child.evaluate(inverted_index)

    def __repr__(self) -> str:
        return f"NOT({self.child})"

class ASTTrueNode:
    def evaluate(self, inverted_index: "InvertedIndex") -> Set[int]:
        return inverted_index.all_documents()

    def __repr__(self) -> str:
        return "TRUE"

class ASTFalseNode:
    def evaluate(self, inverted_index: "InvertedIndex") -> Set[int]:
        return set()

    def __repr__(self) -> str:
        return "FALSE"
