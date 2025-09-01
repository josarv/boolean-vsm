from typing import Protocol

class Query(Protocol):
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass

class TermQuery(Query):
    def __init__(self, term: str) -> None:
        self.term = term

    def __repr__(self) -> str:
        return f"TermQuery({self.term})"

    def __str__(self) -> str:
        return f"TermQuery({self.term})"

class NotQuery(Query):
    def __init__(self, child: Query) -> None:
        self.child = child

    def __repr__(self) -> str:
        return f"NotQuery({self.child})"

    def __str__(self) -> str:
        return f"NotQuery({self.child})"

class AndQuery(Query):
    def __init__(self, left_child: Query, right_child: Query) -> None:
        self.left_child = left_child
        self.right_child = right_child

    def __repr__(self) -> str:
        return f"AndQuery({self.left_child}, {self.right_child})"

    def __str__(self) -> str:
        return f"AndQuery({self.left_child}, {self.right_child})"

class OrQuery(Query):
    def __init__(self, left_child: Query, right_child: Query) -> None:
        self.left_child = left_child
        self.right_child = right_child

    def __repr__(self) -> str:
        return f"OrQuery({self.left_child}, {self.right_child})"

    def __str__(self) -> str:
        return f"OrQuery({self.left_child}, {self.right_child})"

