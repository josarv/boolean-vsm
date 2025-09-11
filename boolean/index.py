from typing import Protocol, Dict, Callable, Iterable
from .postings import PostingList
from dataclasses import dataclass

# minimal, needs expansion later
class InvertedIndex(Protocol):
    def term_postings(self, term: str) -> PostingList: ...
    def universe_postings(self) -> PostingList: ...
    def term_document_frequency(self, term: str) -> int: ...
    def add_document(self, filename: str, tokens: Iterable[str]) -> None: ...
    # def remove_document(self, document_id: int) -> None: ...
    def empty_postings(self) -> PostingList: ...
    # this one is a factory for the ast to use when it needs an empty posting list
    # because it doesn't know what implementation is used
    def postings_to_filenames(self, postings: PostingList) -> Iterable[str]: ...

# todo: review the scope of these dataclasses, do they need to be nested?
@dataclass
class PerTermData:
    posting_list: PostingList
    document_frequency: int
    # term_frequencies: Dict[int, int]  # doc_id -> term frequency

@dataclass
class PerDocumentData:
    filename: str
    length: int
    # term_frequencies: Dict[str, int]

class SimpleInvertedIndex:
    def __init__(self, posting_list_factory: Callable[[], PostingList]):
        # term string -> PerTermData
        self._index: Dict[str, PerTermData] = {}
        # document_id -> PerDocumentData
        self._doc_id_to_metadata: Dict[int, PerDocumentData] = {}
        # inverse, file name -> document_id
        # here it'd be a good idea to use bidict, but let's keep it simple
        self._filename_to_doc_id: Dict[str, int] = {}
        self._next_doc_id: int = 0  # auto-incrementing document ID
        self._posting_list_factory = posting_list_factory
        self._all_document_ids: PostingList = posting_list_factory()
        # usage: index = SimpleInvertedIndex(posting_list_factory=lambda: SetPostingList())

    def term_postings(self, term: str) -> PostingList:
        return self._index[term].posting_list if term in self._index else self._posting_list_factory()

    def universe_postings(self) -> PostingList:
        return self._all_document_ids

    def term_document_frequency(self, term: str) -> int:
        return self._index[term].document_frequency if term in self._index else 0

    def empty_postings(self) -> PostingList:
        return self._posting_list_factory()

    def add_document(self, filename: str, tokens: Iterable[str]) -> None:
        # check for duplicates
        if filename in self._filename_to_doc_id:
            raise ValueError(f"Document with filename '{filename}' already exists in the index.")

        # assign new document ID
        document_id = self._next_doc_id
        self._next_doc_id += 1
        self._filename_to_doc_id[filename] = document_id

        tokens = list(tokens)

        # store document metadata
        self._doc_id_to_metadata[document_id] = PerDocumentData(filename=filename, length=len(tokens))

        # add to universe postings
        self._all_document_ids.add(document_id)

        # count term frequencies in the document
        # not used in boolean
        # term_frequencies: Dict[str, int] = {}
        # for token in tokens:
        #     term_frequencies[token] = term_frequencies.get(token, 0) + 1

        # update index with term frequencies
        for term in set(tokens):  # if we used term_frequencies, it'd be term_frequencies.keys()
            per_term_data = self._index.setdefault(
                term,
                PerTermData(
                    posting_list=self._posting_list_factory(),
                    document_frequency=0,
                )
            )
            per_term_data.posting_list.add(document_id)
            per_term_data.document_frequency += 1

    def postings_to_filenames(self, postings: PostingList) -> Iterable[str]:
        return [self._doc_id_to_metadata[doc_id].filename for doc_id in sorted(postings)]
