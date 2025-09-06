# SKETCH FOR A BIG WRAPPER USER FACING CLASS
#
# from parser import QueryParser
# from index import InvertedIndex
# from ast import ASTNode
# from transformation import Transformer
#
#
# class BooleanIRModel:
#     """
#     User-facing class for the Boolean Information Retrieval library.
#
#     Responsibilities:
#     - Manage the inverted index
#     - Parse and transform queries
#     - Evaluate Boolean queries
#     """
#
#     def __init__(self, documents=None):
#         """
#         Initialize the model with an optional set of documents.
#         documents: dict or list, e.g., {doc_id: text} or [text, ...]
#         """
#         self.index = InvertedIndex()
#         self.parser = QueryParser()
#         self.transformer = Transformer()
#
#         if documents:
#             self.add_documents(documents)
#
#     def add_documents(self, documents):
#         """
#         Add documents to the inverted index.
#         """
#         if isinstance(documents, dict):
#             for doc_id, text in documents.items():
#                 self.index.add_document(doc_id, text)
#         else:  # assume list
#             for doc_id, text in enumerate(documents):
#                 self.index.add_document(doc_id, text)
#
#     def query(self, query_string):
#         """
#         Parse, transform, and evaluate a query string against the index.
#         Returns a set of document IDs matching the Boolean query.
#         """
#         # 1. Parse query string into an AST
#         ast = self.parser.parse(query_string)
#
#         # 2. Optionally transform the AST (e.g., simplify, normalize)
#         transformed_ast = self.transformer.transform(ast)
#
#         # 3. Evaluate the AST against the index
#         results = transformed_ast.evaluate(self.index)
#
#         return results
#
#     def __repr__(self):
#         return f"<BooleanIRModel: {len(self.index)} documents>"
#
