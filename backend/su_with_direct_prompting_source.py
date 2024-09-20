from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.retrievers import MultiVectorRetriever
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage import InMemoryStore, LocalFileStore
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import sys
from operator import itemgetter
from typing import List
from langchain.docstore.document import Document
from .utils import language_detection_chain, text_embedding_3large, azure_openai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("../application/.env"))
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://dalle3-swo.openai.azure.com/"
# os.environ["AZURE_OPENAI_API_KEY"] = "e51119f8d8774069a6594d92ccf7a70d"


# LLM
# gpt_35_turbo_16k = AzureChatOpenAI(
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="gpt-35-turbo-16k",
#     temperature=0
# )
# azure_openai = AzureChatOpenAI(
#     # openai_api_version="2023-05-15",
#     openai_api_version="2024-05-01-preview",

#     # azure_deployment="apac-gpt-35-turbo",
#     azure_deployment="demo-gpt-35-turbo-16k",
#     temperature=0
# )
# # Embedding
# embeddings = AzureOpenAIEmbeddings(
#     azure_deployment="text-embedding-ada-002",
#     openai_api_version="2024-02-15-preview",
# )

# embeddings_3_large = AzureOpenAIEmbeddings(
#     azure_deployment="text-embedding-3-large",
#     openai_api_version="2024-02-15-preview",
# )
# text_embedding_3large = AzureOpenAIEmbeddings(
#     # model="apac-text-embedding-3-large",
#     model="demo-text-embedding-3-large",

#     openai_api_version="2022-12-01",
#     openai_api_key=AZURE_OPENAI_API_KEY,
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
# )

# load from disk and recreate retriever
# vectorstore_chunk_zie_400 = Chroma(
#     persist_directory="./processed_data/chroma_db/su_embedding_400_large_with_source", embedding_function=embeddings_3_large
# )
vectorstore_chunk_zie_400 = Chroma(
    persist_directory="./processed_data/chroma_db/su_embedding_400_large_with_source", embedding_function=text_embedding_3large
)
# The storage layer for the parent documents
# store = InMemoryStore()
fs = LocalFileStore(
    "./processed_data/parent_document_store/su_embedding_large_with_source")
store = create_kv_docstore(fs)
parent_document_retriever = MultiVectorRetriever(
    vectorstore=vectorstore_chunk_zie_400,
    docstore=store,
    search_kwargs={"k": 2},
)


def format_docs_with_sources(docs: List[Document]) -> str:
    formatted = []
    for i, doc in enumerate(docs):
        doc_str = f"""\
        Source Name: {doc.metadata['file_name']} - Page {doc.metadata['page']}
        Information: {doc.page_content}
        """
        formatted.append(doc_str)
    return "\n\n".join(formatted)


template_with_sources = """
As an AI assistant specializing in student support, your task is to provide concise and comprehensive answers to specific questions based on the provided context. 
The context is a list of sources. Each source includes source name and information.
You MUST follow instruction deliminated by ###.

###
Instructions:

1. Begin by reading the context carefully.
2. Answer the question based on the information given in the context.
3. If the answer is not available in the context, admit that you don't know the answer. Do not fabricate responses.
4. Keep your answer as succinct as possible, but ensure it includes all relevant information from the context. For examples: 
    - if students ask about a department or services, you should answer not only department name or serivec name, but also service link and department contact such as email, phone, ... if those information have in the context. 
    - if context does not have specific answer, but contain reference information such as reference link, reference contact point, support contact point and so on. Then you should show it up.
    - if context contains advices for specific student's action, you should show it up.
5. Always include the source name from the context for each fact you use in the response in the following format: 
```
Response 

Sources:
- Source name 1
- Source name 2
....
- Source name n
```
### 

Context:
{context}

Question: 
{input}

Your Informative Answer and Citations:"""

# rag_chain_with_parent_retriever_with_sources = (
#     {"context": itemgetter("input") | parent_document_retriever | format_docs_with_sources,
#      "input": itemgetter("input")}
#     | PromptTemplate.from_template(template_with_sources)
#     | gpt_35_turbo_16k
#     | StrOutputParser()
# )
rag_chain_with_parent_retriever_with_sources = (
    {"context": itemgetter("input") | parent_document_retriever | format_docs_with_sources,
     "input": itemgetter("input")}
    | PromptTemplate.from_template(template_with_sources)
    | azure_openai
    | StrOutputParser()
)


def route(info):
    if info["language"] == "Vietnamese":
        return """We're sorry for any inconvenience; however, StarLeo can only answer questions in English. Unfortunately, Vietnamese isn't available at the moment. Thank you for your understanding!"""
    else:
        return rag_chain_with_parent_retriever_with_sources


full_chain = RunnablePassthrough.assign(
    language=language_detection_chain) | RunnableLambda(route)
