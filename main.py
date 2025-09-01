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


from project.preprocess import expand_contractions

# text = "I'm going to the store. You shouldn't forget your keys. They'll be there soon."
# text = "I'd love to shed light on that."
# text = "My brother and I aren't on speaking terms."
text = "Aren't I?"

print(f"Original text: {text}")

expanded_text = expand_contractions(text)

print(f"Expanded text: {expanded_text}")
