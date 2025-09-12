from typing import List

from project.preprocess import (
    tokenize,
    lowercase,
    remove_stopwords,
    add_penn_treebank_tags,
    convert_penn_treebank_to_wordnet_tags,
    lemmatize,
    map_to_synonyms,
    strip_pos_tags
)
from vsm.model import VSM
from boolean.utility import compose

from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever

preprocess = compose(
    tokenize,
    lowercase,
    remove_stopwords,
    add_penn_treebank_tags,
    convert_penn_treebank_to_wordnet_tags,
    lemmatize,
    map_to_synonyms,
    strip_pos_tags
)

vsm = VSM(preprocessing_pipeline=preprocess)
llm = Ollama(model="llama3.1")


class VSMRetriever(BaseRetriever):
    def __init__(self, vsm_model: VSM, top_k: int = 50):
        self.vsm_model = vsm_model
        self.top_k = top_k

    def get_relevant_documents(self, query: str) -> List[Document]:
        results = self.vsm_model.query(query, top_k=self.top_k)
        documents = []
        for filename, score in results:
            try:
                with open(f"..data/documents/{filename}" "r") as file:
                    content = file.read()
            except FileNotFoundError:
                content = f"(Document {filename} not found on disk.)"
            documents.append(
                Document(
                    page_content=content,
                    metadata={"source": filename, "score": score}
            ))
        return documents


vsm_qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=VSMRetriever(vsm)
)
