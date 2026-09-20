from typing import Callable, List

from .ast import ASTNode
from .postings import SetPostingList
from .index import InvertedIndex, SimpleInvertedIndex
from .parser import Parser, RecursiveDescentParser, preserve_boolean_operators
from .optimization import optimize


class BooleanIRModel:
    def __init__(
            self,
            preprocessing_pipeline: Callable[[str], List[str]],
            parser: Parser | None = None,
            index: InvertedIndex | None = None,
    ):
        self._preprocessing_pipeline = preprocessing_pipeline
        self._query_pipeline: Callable[[str], str] = preserve_boolean_operators(preprocessing_pipeline)
        self._parser = parser or RecursiveDescentParser()
        self._ast_pipeline: Callable[[ASTNode], ASTNode] = optimize
        self._index = index or SimpleInvertedIndex(posting_list_factory=lambda: SetPostingList())

    def index_document(self, filename: str, content: str) -> None:
        tokens = self._preprocessing_pipeline(content)
        self._index.add_document(filename, tokens)

    def query(self, query_string: str) -> List[str]:
        processed_query = self._query_pipeline(query_string)
        ast = self._parser.parse(processed_query)
        ast.root = self._ast_pipeline(ast.root)
        result_postings = ast.root.evaluate(self._index)
        return list(self._index.postings_to_filenames(result_postings))

    def pretty_query(self, query_string: str) -> str:
        results = self.query(query_string)
        if not results:
            return f"No results found for query: '{query_string}'"
        pretty_result = f"Results for query: '{query_string}':\n"
        for idx, filename in enumerate(results, start=1):
            pretty_result += f"  {idx}. {filename}\n"
        return pretty_result
