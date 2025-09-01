from typing import Protocol
from query import Query

class Parser(Protocol):
    def parse(self, query: str) -> Query:
        pass

# and, or, not, parentheses
class BooleanParser(Parser):
    def parse(self, query: str) -> Query:
        pass

# and, or, not, parentheses, +, -
class LuceneParser(Parser):
    def parse(self, query: str) -> Query:
        pass
