from typing import Protocol, Set

class InvertedIndex(Protocol):
    # TODO: IMPORTANT. ENSURE THE RETURN TYPES OF POSTINGS, etc.
    # TODO: RIGHT NOW THEY ARE INTS, FOR DOCUMENT IDs
    def postings(self, term: str) -> Set[int]: ...
    def all_documents(self) -> Set[int]: ...
