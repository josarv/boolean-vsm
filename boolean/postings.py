from typing import Protocol, Iterator, Iterable

class PostingList(Protocol):
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __iter__(self) -> Iterator[int]: ...
    def __contains__(self, item: int) -> bool: ...
    def __and__(self, other) -> "PostingList": ...
    def __iand__(self, other) -> "PostingList": ...
    def __or__(self, other) -> "PostingList": ...
    def __ior__(self, other) -> "PostingList": ...
    def __sub__(self, other) -> "PostingList": ...
    def __isub__(self, other) -> "PostingList": ...
    def __eq__(self, other) -> bool: ...
    def add(self, item: int) -> None: ...
    # the in-place operators mutate the receiver, so anything that starts from a
    # posting list owned by the index must copy it first
    def copy(self) -> "PostingList": ...


class SetPostingList:
    def __init__(self, initial: Iterable[int] = ()):
        self._set: set[int] = set(initial)

    def __len__(self) -> int:
        return len(self._set)

    def __repr__(self) -> str:
        return f"SetPostingList({sorted(self._set)})"

    def __iter__(self) -> Iterator[int]:
        return iter(self._set)

    def __contains__(self, item: int) -> bool:
        return item in self._set

    def __and__(self, other: "PostingList") -> "PostingList":
        if isinstance(other, SetPostingList):
            return SetPostingList(self._set & other._set)
        return SetPostingList(self._set & set(other))

    def __iand__(self, other: "PostingList") -> "PostingList":
        if isinstance(other, SetPostingList):
            self._set &= other._set
        else:
            self._set &= set(other)
        return self

    def __or__(self, other: "PostingList") -> "PostingList":
        if isinstance(other, SetPostingList):
            return SetPostingList(self._set | other._set)
        return SetPostingList(self._set | set(other))

    def __ior__(self, other: "PostingList") -> "PostingList":
        if isinstance(other, SetPostingList):
            self._set |= other._set
        else:
            self._set |= set(other)
        return self

    def __sub__(self, other: "PostingList") -> "PostingList":
        if isinstance(other, SetPostingList):
            return SetPostingList(self._set - other._set)
        return SetPostingList(self._set - set(other))

    def __isub__(self, other: "PostingList") -> "PostingList":
        if isinstance(other, SetPostingList):
            self._set -= other._set
        else:
            self._set -= set(other)
        return self

    def __eq__(self, other) -> bool:
        if isinstance(other, SetPostingList):
            return self._set == other._set
        return NotImplemented

    def add(self, item: int) -> None:
        self._set.add(item)

    def copy(self) -> "PostingList":
        return SetPostingList(self._set)
