from typing import Callable, Iterable
from .index import InvertedIndex, SimpleInvertedIndex
from .postings import DictionaryPostingList
from .eval import compute_query_vector, compute_cosine_similarities

class VSM:
    def __init__(
            self,
            preprocessing_pipeline: Callable[[str], list[str]],
            index: InvertedIndex | None = None,
    ):
        self._preprocessing_pipeline = preprocessing_pipeline
        self._index = index or SimpleInvertedIndex(posting_list_factory=lambda: DictionaryPostingList())

    def index_collection(self, collection: dict[str, Iterable[str]]) -> None:
        self._index.build(collection)

    def query(self, query_string: str, top_k: int | None = None) -> list[tuple[str, float]]:
        tokens = self._preprocessing_pipeline(query_string)
        query_vector = compute_query_vector(self._index, tokens)
        similarities = compute_cosine_similarities(self._index, query_vector)
        ranked_results = sorted(similarities, key=lambda x: x[1], reverse=True)
        if top_k is not None:
            ranked_results = ranked_results[:top_k]
        ranked_files = [(self._index.document_id_to_filename(doc_id), score) for doc_id, score in ranked_results]
        return ranked_files
