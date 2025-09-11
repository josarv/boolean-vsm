from typing import Callable, List

from .ast import ASTNode
from .postings import SetPostingList
from .index import InvertedIndex, SimpleInvertedIndex
from .parser import Parser, RecursiveDescentParser, preserve_boolean_operators
from .optimization import fold_constants, flatten_nested_operators, deduplicate_operands, simplify_tautologies_contradictions
from .utility import compose


class BooleanIRModel:
    def __init__(
            self,
            preprocessing_pipeline: Callable[[str], List[str]],
            parser: Parser | None = None,
            index: InvertedIndex | None = None,
    ):
        self.preprocessing_pipeline = preprocessing_pipeline
        self.query_pipeline: Callable[[str], str] = preserve_boolean_operators(preprocessing_pipeline)
        self.parser = parser or RecursiveDescentParser()
        self.ast_pipeline: Callable[[ASTNode], ASTNode] = compose(
            fold_constants,
            flatten_nested_operators,
            deduplicate_operands,
            simplify_tautologies_contradictions,
        )
        self.index = index or SimpleInvertedIndex(posting_list_factory=lambda: SetPostingList())

    def index_document(self, filename: str, content: str) -> None:
        tokens = self.preprocessing_pipeline(content)
        self.index.add_document(filename, tokens)

    def query(self, query_string: str) -> List[str]:
        processed_query = self.query_pipeline(query_string)
        ast = self.parser.parse(processed_query)
        ast.root = self.ast_pipeline(ast.root)
        result_postings = ast.root.evaluate(self.index)
        return list(self.index.postings_to_filenames(result_postings))

    def pretty_query(self, query_string: str) -> str:
        results = self.query(query_string)
        if not results:
            return f"No results found for query: '{query_string}'"
        pretty_result = f"Results for query: '{query_string}':\n"
        for idx, filename in enumerate(results, start=1):
            pretty_result += f"  {idx}. {filename}\n"
        return pretty_result
