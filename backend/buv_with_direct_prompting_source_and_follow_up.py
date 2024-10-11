from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.retrievers import MultiVectorRetriever
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_postgres.vectorstores import PGVector
from langchain.retrievers.multi_vector import SearchType
from langchain_core.chat_history import BaseChatMessageHistory

import os
import sys
import pprint
from operator import itemgetter
from typing import List
from langchain.docstore.document import Document
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
from .utils import language_detection_chain, text_embedding_3large, azure_openai
from dotenv import load_dotenv, find_dotenv

from backend.custom_docstore import PostgresStore

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

load_dotenv(find_dotenv("../application/.env"))

# Postgres
host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
# database = os.getenv("DEMO_IHMFE")
database = os.getenv("PGDATABASE")
pgport = os.getenv("PGPORT")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:{pgport}/{database}" # use psycopg3 driver

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")



# Vectorstore
vectorstore = PGVector(
    embeddings=text_embedding_3large,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
)

id_key = "doc_id"
# The retriever
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=PostgresStore(connection_string=CONNECTION_STRING),
    id_key=id_key,
    search_kwargs={"k": 6, "fetch_k": 8}
)
retriever.search_type = SearchType.mmr

contextualized_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualized_template = ChatPromptTemplate.from_messages(
    [
        # MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("human", contextualized_system_prompt),
    ]
)

history_aware_retriever = create_history_aware_retriever(azure_openai, retriever, contextualized_template)

#Create system prompt
system_prompt_template = """
As an AI assistant named StarLeo specializing in student support, your task is to provide concise and comprehensive answers to specific questions or inquiries based on the provided context.
The context is a list of sources, each including the main information, the source name and its corresponding page number.
You MUST follow the instructions inside the ###.

###
Instructions:

1. Read the context carefully.
2. Only answer the question based on the information in the context.
3. Keep your answer as succinct as possible, but ensure it includes all relevant information from the context. For example:
    - If students ask about a department or service, provide the department or service name, as well as the service link and department contact information such as email, phone, etc., if available in the context.
    - If the context does not have a specific answer but contains reference information such as a reference link, reference contact point, support contact point, etc., include that information.
    - If the context contains advice for specific student actions, include that advice.
4. When you see the pattern \n in the context, it means a new line. With those texts that contain \n, you should read them carefully to understand the context.
5. Use the word "documents" instead of "context" when referring to the provided information in the answer.
6. The source names are provided right after the answer. Don't include the source names in the answer.
7. Always include the title of the document from the context for each fact you use in the response in the following format:

{{Answer here}}

Sources:
- Source Name 1 - Page <show page number here>
- Source Name 2 - Page <show page number here>
...
- Source Name n - Page <show page number here>

8. If there are duplicate titles, only include that title once in the list of sources.
9. You can only give the answer in British English style. For example, use "programme" instead of "program" or "organise" instead of "organize".
10. If the history conversations contain useful information, you can respond based on the provided context and that information too. 
###

--- Start Context:
{context}
--- End Context

"""

system_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_template),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)

def create_stuff_documents_chain(llm, prompt, output_parser=StrOutputParser()):
    def format_docs(inputs: dict) -> str:
        formatted = []
        for i, doc in enumerate(inputs['context']):
            doc_str = f"""Source Name: {doc.metadata['title']} - Page {doc.metadata['page_number']}\nInformation: {doc.page_content}"""
            formatted.append(doc_str)
        return "\n\n".join(formatted)
        
    return (
        RunnablePassthrough.assign(**{"context": format_docs}).with_config(
            run_name="format_inputs"
        )
        | prompt
        | llm
        | output_parser
        ).with_config(run_name="stuff_documents_chain")
    


history_aware_retriever = create_history_aware_retriever(azure_openai, retriever, contextualized_template)
question_answer_chain = create_stuff_documents_chain(azure_openai, system_template)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain) #runnable

# Managing chat history
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()

    return store[session_id]



# conversational_rag_chain = RunnableWithMessageHistory(
#     rag_chain, 
#     lambda session_id: demo_ephemeral_chat_history,
#     input_messages_key="input",
#     history_messages_key="chat_history",
#     output_messages_key="answer"
# )

# def conversational_chain(query, session_id: str):
#     answer = conversational_rag_chain.invoke(
#         {"input": query},
#         config={
#             "configurable": {"session_id": session_id}
#         }
#     )
#     pprint.pprint(answer)
#     return answer







# chain_with_message_history = RunnableWithMessageHistory(
#     rag_chain_with_parent_retriever_with_sources,
#     lambda session_id: demo_ephemeral_chat_history,
#     input_messages_key="input",
#     history_messages_key="chat_history",
# )


# def trim_messages():
#     # add memory using streamlit session state (can change to db later)+ trimmming message -  just get two latest conversation
#     ephemeral_chat_history = StreamlitChatMessageHistory(
#         key="buv_follow_up_memory")
    
#     stored_messages = ephemeral_chat_history.messages
#     if len(stored_messages) <= 2:
#         return False
#     print("Trimming messages")
#     ephemeral_chat_history.messages = stored_messages[-2:]
#     return True

# chain_with_follow_up = (
#     RunnablePassthrough.assign(messages_trimmed=trim_messages)
#     | conversational_rag_chain
# )


# def route(info):
#     if info["language"] == "Vietnamese":
#         return """We're sorry for any inconvenience; however, StarLeo can only answer questions in English. Unfortunately, Vietnamese isn't available at the moment. Thank you for your understanding!"""
#     else:
#         return chain_with_follow_up


# full_chain = RunnablePassthrough.assign(
#     language=language_detection_chain) | RunnableLambda(route)


def chain_with_follow_up_function(message_history):
    # chain_with_message_history = RunnableWithMessageHistory(
    #     rag_chain_with_parent_retriever_with_sources,
    #     lambda session_id: message_history,
    #     input_messages_key="input",
    #     history_messages_key="chat_history",
    # )
    # chain_with_follow_up = (
    #     RunnablePassthrough.assign(messages_trimmed=trim_messages)
    #     | chain_with_message_history
    # )
    # return chain_with_follow_up
    
    # ephemeral_chat_history = StreamlitChatMessageHistory(key="buv_follow_up_memory")
    
    conversational_rag_chain = RunnableWithMessageHistory(
                            rag_chain, 
                            lambda session_id: message_history,
                            input_messages_key="input",
                            history_messages_key="chat_history",
                            output_messages_key="answer"
                            )
    # print("Trimming history messages")
    # ephemeral_chat_history.messages = ephemeral_chat_history.messages[-2:] if len(ephemeral_chat_history.messages) > 2 else ephemeral_chat_history.messages
    # print("history messages:", ephemeral_chat_history.messages)
    
    # chain_with_follow_up = (
    #                         RunnablePassthrough.assign(messages_trimmed=lambda x: trim_messages())
    #                         | conversational_rag_chain
    #                         )
    return conversational_rag_chain
    # return chain_with_follow_up
    
