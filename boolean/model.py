from typing import Callable, List

from .ast import ASTNode
from .postings import SetPostingList
from .index import InvertedIndex, SimpleInvertedIndex
from .parser import Parser, RecursiveDescentParser
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
        # preprocess query
        processed_query = self.preprocessing_pipeline(query_string)
        # parse into AST
        ast = self.parser.parse(" ".join(processed_query))
        # optimize AST
        ast.root = self.ast_pipeline(ast.root)
        # evaluate AST against the index
        result_postings = ast.root.evaluate(self.index)
        # convert postings to filenames
        return list(self.index.postings_to_filenames(result_postings))
