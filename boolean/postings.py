from typing import Protocol

class PostingList(Protocol):
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __and__(self, other) -> "PostingsList": ...
    def __iand__(self, other) -> "PostingsList": ...
    def __or__(self, other) -> "PostingsList": ...
    def __ior__(self, other) -> "PostingsList": ...
    def __sub__(self, other) -> "PostingsList": ...
    def __isub__(self, other) -> "PostingsList": ...
    def __contains__(self, item: int) -> bool: ...


class SetPostingList:
    def __init__(self, initial: set[int] | None = None):
        self.set = initial if initial is not None else set()

    def __len__(self) -> int:
        return len(self.set)

    def __and__(self, other: "SetPostingList") -> "SetPostingList":
        return SetPostingList(self.set & other.set)

    def __iand__(self, other: "SetPostingList") -> "SetPostingList":
        self.set &= other.set
        return self

    def __or__(self, other: "SetPostingList") -> "SetPostingList":
        return SetPostingList(self.set | other.set)

    def __ior__(self, other: "SetPostingList") -> "SetPostingList":
        self.set |= other.set
        return self

    def __sub__(self, other: "SetPostingList") -> "SetPostingList":
        return SetPostingList(self.set - other.set)

    def __isub__(self, other: "SetPostingList") -> "SetPostingList":
        self.set -= other.set
        return self

    def __contains__(self, item: int) -> bool:
        return item in self.set

    def __repr__(self) -> str:
        return f"Sets({sorted(self.set)})"
