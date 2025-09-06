from typing import Protocol, Set, Dict, Any
from collections import defaultdict

# as mentioned in ast.py, change these methods to return a wrapper type
# which will wrap sets, bit arrays or whatever
class InvertedIndex(Protocol):
    def postings(self, term: str) -> Set[int]: ...
    def all_documents(self) -> Set[int]: ...
    def term_posting_count(self, term: str) -> int: ...
    def add_document(self, document_id: int, tokens: list[str]) -> None: ...
    def remove_document(self, document_id: int) -> None: ...
    def vocabulary(self) -> Set[str]: ...
    def metadata(self, document_id: int) -> Dict[str, Any] | None: ...

class InMemoryInvertedIndex:
    def __init__(self):
        self._index: Dict[str, Set[int]] = defaultdict(set)
        self._documents: Set[int] = set()
        self._metadata: Dict[int, Dict[str, Any]] = {}
        self._next_id: int = 1

    def postings(self, term: str) -> Set[int]:
        return self._index.get(term, set())

    def all_documents(self) -> Set[int]:
        return self._documents.copy()

    def term_posting_count(self, term: str) -> int:
        return len(self._index.get(term, set()))

    def vocabulary(self) -> Set[str]:
        return set(self._index.keys())

    def metadata(self, document_id: int) -> Dict[str, Any] | None:
        return self._metadata.get(document_id)

    def add_document(self, document_id: int, tokens: list[str]) -> None:
        pass
