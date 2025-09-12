from typing import Protocol, Iterator

class PostingList(Protocol):
    def __iter__(self) -> Iterator[tuple[int, float]]: ...
    def __len__(self) -> int: ...
    def __getitem__(self, doc_id: int) -> float: ...
    def add(self, doc_id: int, weight: float) -> None: ...

class DictionaryPostingList:
    def __init__(self):
        self._postings: dict[int, float] = {}

    def __iter__(self) -> Iterator[tuple[int, float]]:
        return iter(self._postings.items())

    def __len__(self) -> int:
        return len(self._postings)

    def __getitem__(self, doc_id: int) -> float:
        return self._postings.get(doc_id, 0.0)   # return 0.0 if doc_id not present

    def add(self, doc_id: int, weight: float) -> None:
        self._postings[doc_id] = weight

    def __repr__(self) -> str:
        return f"DictionaryPostingList({self._postings})"
