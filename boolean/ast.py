from typing import Protocol, Set, List

from .index import InvertedIndex

class AST:
    def __init__(self, query: str, root):
        self.query = query
        self.root = root

    def __repr__(self):
        # return f"AST({self.query}, {self.root})"
        return f'{self.root}'


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

# TODO: make proper display functions, maybe methods of AST class?
def display_ast_preorder(node: ASTNode, indent: int = 0):
    prefix = "  " * indent
    print(f"{prefix}{node}")
    if isinstance(node, ASTAndNode) or isinstance(node, ASTOrNode):
        for child in node.children:
            display_ast_preorder(child, indent + 1)
    elif isinstance(node, ASTNotNode):
        display_ast_preorder(node.child, indent + 1)
