from os import listdir
from os.path import join

#
# document_directory = 'data/documents'
#
# inverted_index = {}
# forward_index = {}

# inverted index: {token: [ (document_id, frequency), ... ]}
# forward index: {document_id: (filename, {token: frequency, ...}) }

# for document_id, filename in enumerate(listdir(document_directory), 1):
#     with open(join(document_directory, filename), 'r') as file:
#         token_list = preprocessing_pipeline(file.read())
#         print(token_list)
        # forward_index[document_id] = {}
        # for token in token_list:
        #     forward_index[document_id][token] = forward_index[document_id].get(token, 0) + 1
        #     if token not in inverted_index:
        #         inverted_index[token] = {}
        #     if document_id not in inverted_index[token]:
        #         inverted_index[token].append(document_id)

# from project.preprocess import compose, tokenize, lowercase, add_penn_treebank_tags, convert_penn_treebank_to_wordnet_tags, lemmatize, strip_pos_tags, remove_stopwords, remove_punctuation_tokens
# from boolean import preserve_boolean_operators
#
# preprocessing_pipeline = compose(
#     # expand_contractions,
#     tokenize,
#     lowercase,
#     remove_punctuation_tokens,
#     # remove_digit_tokens,
#     # remove_too_short_tokens,
#     add_penn_treebank_tags,
#     convert_penn_treebank_to_wordnet_tags,
#     lemmatize,
#     # map_to_synonyms,
#     strip_pos_tags,
#     remove_stopwords,
# )
#
# query_pipeline = preserve_boolean_operators(preprocessing_pipeline)

from boolean import ASTAndNode, ASTOrNode, ASTNotNode, ASTTermNode, display_ast_preorder
from boolean.transformation import NNFTransformer, CNFTransformer, Simplifier
# tree = ASTAndNode([ASTTermNode("apple"), ASTOrNode([ASTTermNode("banana"), ASTNotNode(ASTTermNode("Car"))])])
# tree = ASTNotNode(ASTAndNode([ASTTermNode("banana"), ASTTermNode("Car")]))
# tree = ASTOrNode([ASTNotNode(ASTAndNode([ASTTermNode("apple"), ASTOrNode([ASTTermNode("banana"), ASTTermNode("cherry")])])), ASTTermNode("date")])
# display_ast_preorder(tree)
# tree = NNFTransformer().transform(tree)
# tree = ASTOrNode([ASTNotNode(ASTTermNode("A")), ASTAndNode([ASTNotNode(ASTTermNode("B")), ASTNotNode(ASTTermNode("C"))]), ASTTermNode("D")])
# display_ast_preorder(tree)
# tree = CNFTransformer().transform(tree)
tree = ASTAndNode([ASTOrNode([ASTTermNode("A"), ASTTermNode("B")]), ASTOrNode([ASTTermNode("A"), ASTAndNode([ASTTermNode("B"), ASTTermNode("C")])])])
display_ast_preorder(tree)
tree = Simplifier().transform(tree) # TODO: robustify
display_ast_preorder(tree)
