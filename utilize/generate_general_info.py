import pandas as pd
import numpy as np
from langchain_core.documents.base import Document
from langchain_community.vectorstores import PGVector
from langchain_openai import AzureOpenAIEmbeddings
from langchain.indexes import SQLRecordManager, index

# from model.embeddings import text_embedding_3large
from backend.utils import text_embedding_3large
# from model.chat import azure_openai
from backend.utils import azure_openai
import streamlit as st
import time
from PIL import Image
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.schema.messages import get_buffer_string
from langchain.schema import format_document
from langchain.schema.runnable import RunnableParallel
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.schema import StrOutputParser
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter



import os

from dotenv import load_dotenv
load_dotenv("../application/.env")

host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
database = os.getenv("PGDATABASE3")
# database = os.getenv("PGDATABASE2")
pgport = os.getenv("PGPORT")
COLLECTION_NAME = "langchain_collection"
# CONNECTION_STRING = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"
# CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:5432/{database}"
CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:{pgport}/{database}"

vector_store = PGVector(
    embedding_function=text_embedding_3large,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
)

# retriever = vector_store.as_retriever()
# retriever = vector_store.as_retriever(
#     search_type="similarity_score_threshold",
#     search_kwargs={
#         "k": 2,
#         "score_threshold": 0.5
#     }
# )
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 1,
        "score_threshold": 0.5
    }
)



def get_prompt_ans(prompt):
    answer, url_ = get_answer(prompt)

    # build suggested question
    # normal suggestion
    suggested_questions = get_similar(prompt)[1:]


    # # advanced suggestion: suggest follow-up question based on current question and answer
    # q, a = generate_suggestion(question=prompt, answer=answer)
    # suggested_questions.append(q)

    return answer, suggested_questions, url_


def get_answer(question):
    # prompt has two input: info and question
#     prompt_template = PromptTemplate(
#         input_variables=["question", "info"],
#         template="""You are a chatbot specialized in answering frequently asked questions from customers about the student shuttle bus service provided by BUV.

# Here is a customer's question: {question}

# Please using the following information as your answer: {info}
#             """
    prompt_template = PromptTemplate(
        input_variables=["question", "info"],
        template="""You are a chatbot specialized in answering frequently asked questions from customers about the student shuttle bus service provided by BUV.\n

        Here is a customer's question: {question}\n

        Use exactly this following information as your answer: {info}
        Do not add any additional or fictional details.
            """
        # template="""Using the provided information: {info},
        # answer the following question: {question}.
        # Ignore the word 'yes' and 'no' in provided information.
        # If any information is irrelevant to the question, please ignore it.
        # Focus on including as much relevant information as possible.
        # Do not invent answers for information that is not provided
        # """
    )

    retrieved = retriever.get_relevant_documents(question)
    # because sometimes k=1 with high threshold will get no relevant docs in retrieved, then keep k=2
    print(retrieved)
    if len(retrieved)>1:
        for ite,doc in enumerate(retrieved):
            if "gps" in doc.metadata["answer"].lower():
                retrieved = retrieved[ite]
                break
    # print(retrieved)

    # create info - combine_doc as a input
    combine_doc = ""
    for i in retrieved:
        combine_doc = combine_doc + str(i.metadata["answer"]) + "\n"
    print("----combine doc-----------")
    print(combine_doc)

    # get the URL from doc
    url_ = {
        "Zalo QR Code": [],
        "Bus images": [],
        "GPS Link": []
    }
    # for doc in retrieved:
    #     if doc.metadata["url"] != "":
    #         if "zalo" in doc.metadata["answer"].lower():
    #             url_["Zalo QR Code"].append(doc.metadata["url"])
    #         elif "Bus_images" in doc.metadata["answer"].lower():
    #             url_["Bus images"].append(doc.metadata["url"])
    #         elif "GPS" in doc.metadata["answer"].lower():
    #             url_["GPS Link"].append(doc.metadata["url"])
    for doc in retrieved:
        if doc.metadata["url"] != "":
            if "zalo" in doc.metadata["answer"].lower():
                url_["Zalo QR Code"].append(doc.metadata["url"])
        if doc.metadata["url_bus_image"] != "":
            url_["Bus images"].append(doc.metadata["url_bus_image"])
        if doc.metadata["url_link"] != "":
            url_["GPS Link"].append(doc.metadata["url_link"])
                
    print(url_)

    # create chain
    chain = prompt_template | azure_openai | StrOutputParser()

    # get answer from chain
    answer = chain.invoke({
        "question": question,
        "info": combine_doc 
    })
    print("===ans===")
    print(answer)
    return answer, url_

def generate_suggestion(question, answer):
    # create prompt with two input: question and answer, then suggest next question
    prompt_template = PromptTemplate(
        input_variables=["question", "answer"],
        template="""Suggest new follow up question, based on this conversation:
        A: {question}
        B: {answer}

        Suggestion: """
    )

    # create chain
    chain = prompt_template | azure_openai | StrOutputParser()

    # get suggestion
    suggestion = chain.invoke({
        "question": question,
        "answer": answer
    })

    # get answer of this suggest question
    suggestion_answer, _ = get_answer(question=suggestion)
    return suggestion, suggestion_answer





def get_similar(question):
    # print("------------ get similar ----------")
    # print([i.page_content for i in vector_store.similarity_search(question, k=3)])
    return [i.page_content for i in vector_store.similarity_search(question, k=4)]



def write_url(url_, url_key):
    for key,val in url_.items():
        url_.update({
            key: list(set(val))
        })
    # if it's not question about route
    if "route" not in url_key.lower():
        if len(url_["Zalo QR Code"]) > 0:
            url_["Zalo QR Code"] = list(set(url_["Zalo QR Code"]))
            st.markdown("Here is Zalo QR Code:")
            image_zaloQR = Image.open(url_["Zalo QR Code"][0])
            st.image(image_zaloQR, width=500)


        if len(url_["Bus images"]) > 0:
            st.markdown("An image of BUV bus:")
            image_NormalBus = Image.open(url_["Bus images"][0])
            st.image(image_NormalBus, width=500)
            # st.image()
    # else:
    #     for idx in range(1,5):
    #         route_nr = "route " + str(idx)
    #         if route_nr in url_key.lower():


    # return
