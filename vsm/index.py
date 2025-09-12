from typing import Protocol, Iterable, Callable
from math import log, sqrt

from .postings import PostingList, DictionaryPostingList


class InvertedIndex(Protocol):
    def build(self, collection: dict[str, Iterable[str]]) -> None: ...  # filename, tokens
    def term_postings(self, term: str) -> PostingList: ...
    def term_document_frequency(self, term: str) -> int: ...
    # def document_vector(self, filename: str) -> dict[str, float]: ...
    def document_norm(self, filename: str) -> float: ...
    def postings_to_filenames(self, postings: PostingList) -> Iterable[str]: ...


class SimpleInvertedIndex:
    def __init__(self, posting_list_factory: Callable[[], PostingList] = DictionaryPostingList):
        self._index: dict[str, PostingList] = {}
        self._posting_list_factory = posting_list_factory
        self._doc_id_to_filename: dict[int, str] = {}
        self._filename_to_doc_id: dict[str, int] = {}
        self._next_doc_id: int = 0
        self._document_norms: dict[int, float] = {}

    def build(self, collection: dict[str, Iterable[str]]) -> None:
        term_document_frequencies: dict[str, dict[int, int]] = {}  # term -> (doc_id -> term frequency)
        document_lengths: dict[int, int] = {}  # total terms per document
        # pass 1, assign doc id, count raw term frequencies
        for filename, tokens in collection.items():
            doc_id = self._next_doc_id
            self._next_doc_id += 1
            self._filename_to_doc_id[filename] = doc_id
            self._doc_id_to_filename[doc_id] = filename
            # count raw term frequencies
            term_frequencies: dict[str, int] = {}
            for token in tokens:
                term_frequencies[token] = term_frequencies.get(token, 0) + 1
            document_lengths[doc_id] = sum(term_frequencies.values())
            for term, count in term_frequencies.items():
                if term not in term_document_frequencies:
                    term_document_frequencies[term] = {}
                term_document_frequencies[term][doc_id] = count
        n_documents = len(collection)
        # pass 2, compute tf-idf weights, build posting lists, norms
        self._document_norms = {doc_id: 0.0 for doc_id in self._doc_id_to_filename}
        for term, document_dictionary in term_document_frequencies.items():
            postings = self._posting_list_factory()
            df = len(document_dictionary)
            idf = log(n_documents / df) if df > 0 else 0.0
            for doc_id, count in document_dictionary.items():
                tf = count / document_lengths[doc_id]
                weight = tf * idf
                postings.add(doc_id, weight)
                self._document_norms[doc_id] += weight * weight  # accumulate squared weight into a document norm
            self._index[term] = postings
        # finalize norms
        for doc_id in self._document_norms:
            self._document_norms[doc_id] = sqrt(self._document_norms[doc_id])

    def term_postings(self, term: str) -> PostingList:
        return self._index.get(term, self._posting_list_factory())  # empty if term not present

    def term_document_frequency(self, term: str) -> int:
        postings = self._index.get(term)
        return len(postings) if postings else 0

    # def document_vector(self, filename: str) -> dict[str, float]:
    #     doc_id = self._filename_to_doc_id.get(filename)
    #     if doc_id is None:
    #         raise ValueError(f"Document with filename '{filename}' not found in the index.")
    #     vector: dict[str, float] = {}
    #     for term, postings in self._index.items():
    #         weight = postings[doc_id]  # 0.0 if doc_id not present
    #         if weight > 0.0:
    #             vector[term] = weight
    #     return vector

    def document_norm(self, filename: str) -> float:
        doc_id = self._filename_to_doc_id.get(filename)
        if doc_id is None:
            raise ValueError(f"Document with filename '{filename}' not found in the index.")
        return self._document_norms[doc_id]

    def postings_to_filenames(self, postings: PostingList) -> Iterable[str]:
        for doc_id, _ in postings:
            yield self._doc_id_to_filename[doc_id]
