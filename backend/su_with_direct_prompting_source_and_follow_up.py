from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
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
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
from .utils import language_detection_chain, text_embedding_3large, azure_openai
from dotenv import load_dotenv, find_dotenv
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://dalle3-swo.openai.azure.com/"
# os.environ["AZURE_OPENAI_API_KEY"] = "e51119f8d8774069a6594d92ccf7a70d"
load_dotenv(find_dotenv("../application/.env"))
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# LLM
# gpt_35_turbo_16k = AzureChatOpenAI(
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="gpt-35-turbo-16k",
#     temperature=0
# )
# gpt_4o = AzureChatOpenAI(
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="gpt-4o",
#     temperature=0
# )
# azure_openai = AzureChatOpenAI(
#     # openai_api_version="2023-05-15",
#     openai_api_version="2024-05-01-preview",

#     # azure_deployment="apac-gpt-35-turbo",
#     azure_deployment="demo-gpt-35-turbo-16k",
#     temperature=0
# )
# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://buv-chatbot.openai.azure.com/"
# os.environ["AZURE_OPENAI_API_KEY"] = "f19bcab8b66f421a834731e89ba023f0"

# # LLM
# gpt_35_turbo_16k = AzureChatOpenAI(
#     openai_api_version="2024-05-01-preview",
#     azure_deployment="gpt-35-turbo-new",
#     temperature=0
# )
# gpt_4o = AzureChatOpenAI(
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="gpt-4o",
#     temperature=0
# )


# Embedding

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


# System prompt
# system_prompt = """
# As an AI assistant specializing in student support, your task is to provide concise and comprehensive answers to specific questions based on the provided context. 
# The context is a list of sources. Each source includes source name and information.
# You MUST follow instruction deliminated by ###.

# ###
# Instructions:

# 1. Begin by reading the context carefully.
# 2. Answer the question based on the information in the context.
# 3. If you don’t know the answer, say "Sorry, the documents do not mention about this information. Please contact the Student Information Office via studentservice@buv.edu.vn for further support. Thank you". Do not fabricate responses. And Do not make up references
# 4. Keep your answer as succinct as possible, but ensure it includes all relevant information from the context. For examples: 
#     - if students ask about a department or services, you should answer not only department name or serivec name, but also service link and department contact such as email, phone, ... if those information have in the context. 
#     - if context does not have specific answer, but contain reference information such as reference link, reference contact point, support contact point and so on. Then you should show it up.
#     - if context contains advices for specific student's action, you should show it up.
# 5. Always include the source name from the context for each fact you use in the response in the following format: 
# ```
# {{Answer here}} 

# Sources:
# - Source name 1
# - Source name 2
# ....
# - Source name n
# ```
# ### 

# --- Start Context:
# {context}
# --- End Context

# Note that if the previous conversations contains usefull information, you can response based on provided context and those information too. 
# Only answer in English.
# """

system_prompt = """
As an AI assistant specializing in student support, your task is to provide concise and comprehensive answers to specific questions based on the provided context. 
The context is a list of sources, each including a source name and information.
You MUST follow the instructions delimited by ###.

###
Instructions:

1. Read the context carefully.
2. Answer the question based on the information in the context.
3. If you don’t know the answer, say "Sorry, the documents do not mention this information. Please contact the Student Information Office via studentservice@buv.edu.vn for further support. Thank you". Do not fabricate responses or make up references.
4. Keep your answer as succinct as possible, but ensure it includes all relevant information from the context. For example:
    - If students ask about a department or service, provide the department or service name, as well as the service link and department contact information such as email, phone, etc., if available in the context.
    - If the context does not have a specific answer but contains reference information such as a reference link, reference contact point, support contact point, etc., include that information.
    - If the context contains advice for specific student actions, include that advice.
5. Always include the source name from the context for each fact you use in the response in the following format: 
```
{{Answer here}} 

Sources:
- Source name 1
- Source name 2
....
- Source name n
```
### 

--- Start Context:
{context}
--- End Context

Note that if the previous conversations contain useful information, you can respond based on the provided context and that information too. 
Only answer in English.
"""


# retriever with history aware
# contextualize_q_system_prompt = (
#     """
# As an expert in natural language processing, your task is to transform a given student's question, which may reference prior chat history, into a standalone question that can be understood without any context from the chat history.
# Do not answer the question, simply reformulate it if necessary.

# Because If you change the question a little bit, It can lead the question to have the different meaning and lead to bot answer incorrectly.
# So You should Prioritize returning the latest question as it is, and only reformulate it if absolutely necessary.

# But if it clearly refer to the prior chat history or refering to the chat history makes the question clearer, you should refomulate the question.
# Because your output would be used as a standalone search query to find information.

# So you have to balance it.
# """
# )

# contextualize_q_system_prompt = (
#     """
# As an expert in natural language processing, your task is to transform a given student's question, which may reference prior chat history, into a standalone question that can be understood without any context from the chat history.
# Do not answer the question, simply reformulate it if necessary.
# Because If you change the question a little bit, It can lead the question to have the different meaning and lead to bot answer incorrectly.
# So You Must Prioritize returning the latest question as it is, and only reformulate it if absolutely necessary.
# Sometimes if students just say somethings and can be understood without context, not change it to the question, just keep it as it is.
# """
# )

contextualize_q_system_prompt = (
    """
As an expert in natural language processing, your task is to transform a given student's question, which may reference prior chat history, into a standalone question that can be understood without any context from the chat history.
Do not answer the question; simply reformulate it if necessary.
If you change the question even slightly, it can alter its meaning and lead to incorrect responses from the bot.
Therefore, you must prioritize returning the latest question as it is, and only reformulate it if absolutely necessary.
If students say something that can be understood without context, do not change it to a question; just keep it as it is.
"""
)

# contextualize_q_system_prompt = (
#     "As an expert in natural language processing,"
#     "Given a chat history and the latest user question "
#     "which might reference context in the chat history, "
#     "formulate a standalone question which can be understood "
#     "without the chat history. Do NOT answer the question, "
#     "just reformulate it if needed and otherwise return it as is."
# )

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
# parent_document_with_history_aware_retriever = create_history_aware_retriever(
#     gpt_4o, parent_document_retriever, contextualize_q_prompt
# )
parent_document_with_history_aware_retriever = create_history_aware_retriever(
    azure_openai, parent_document_retriever, contextualize_q_prompt
)
# parent_document_with_history_aware_retriever = create_history_aware_retriever(
#     gpt_35_turbo_16k, parent_document_retriever, contextualize_q_prompt
# )

# main chain
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

custom_retriever_chain = parent_document_with_history_aware_retriever | format_docs_with_sources

# rag_chain_with_parent_retriever_with_sources = (
#     RunnablePassthrough.assign(context=custom_retriever_chain)
#     | qa_prompt
#     | gpt_35_turbo_16k
#     | StrOutputParser()
# )
rag_chain_with_parent_retriever_with_sources = (
    RunnablePassthrough.assign(context=custom_retriever_chain)
    | qa_prompt
    | azure_openai
    | StrOutputParser()
)

# add memory using streamlit session state (can change to db later)+ trimmming message -  just get two latest conversation

demo_ephemeral_chat_history = StreamlitChatMessageHistory(
    key="su_follow_up_memory")

chain_with_message_history = RunnableWithMessageHistory(
    rag_chain_with_parent_retriever_with_sources,
    lambda session_id: demo_ephemeral_chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)


def trim_messages(chain_input):
    stored_messages = demo_ephemeral_chat_history.messages
    if len(stored_messages) <= 2:
        return False

    demo_ephemeral_chat_history.clear()

    for message in stored_messages[-2:]:
        demo_ephemeral_chat_history.add_message(message)

    return True


chain_with_follow_up = (
    RunnablePassthrough.assign(messages_trimmed=trim_messages)
    | chain_with_message_history
)


def route(info):
    if info["language"] == "Vietnamese":
        return """We're sorry for any inconvenience; however, StarLeo can only answer questions in English. Unfortunately, Vietnamese isn't available at the moment. Thank you for your understanding!"""
    else:
        return chain_with_follow_up


full_chain = RunnablePassthrough.assign(
    language=language_detection_chain) | RunnableLambda(route)


def chain_with_follow_up_function(message_history):
    chain_with_message_history = RunnableWithMessageHistory(
        rag_chain_with_parent_retriever_with_sources,
        lambda session_id: message_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    chain_with_follow_up = (
        RunnablePassthrough.assign(messages_trimmed=trim_messages)
        | chain_with_message_history
    )
    return chain_with_follow_up
