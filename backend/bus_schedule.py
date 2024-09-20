import sys
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
from operator import itemgetter
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("../application/.env"))
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://dalle3-swo.openai.azure.com/"
# os.environ["AZURE_OPENAI_API_KEY"] = "e51119f8d8774069a6594d92ccf7a70d"
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# LLM
llm = AzureChatOpenAI(
    openai_api_version="2024-02-15-preview",
    azure_deployment="gpt-35-turbo",
    temperature=0
)
smart_llm = AzureChatOpenAI(
    openai_api_version="2024-02-15-preview",
    azure_deployment="gpt-4",
    temperature=0
)
gpt_35_turbo_instruct = AzureChatOpenAI(
    openai_api_version="2024-02-15-preview",
    azure_deployment="gpt-35-turbo-instruct",
    temperature=0
)
# Embedding
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-ada-002",
    openai_api_version="2024-02-15-preview",
)

# load from disk
vectorstore = Chroma(persist_directory="./processed_data/chroma_db/bus_route",
                     embedding_function=embeddings)
retriever = vectorstore.as_retriever(
    search_type="similarity", search_kwargs={"k": 5})


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


template = """
You are an AI assistant that helps students find information about bus schedule. 

Here are some notes you MUST pay attention to:
- Some slots are just available at several specific days such as Tue to Fri, Tue and Fri, ... So if students want to pick up on Monday, just suggest slots available in Mon.
- The first column of bus schedule table is the bus route. For example, buv campus --> cau giay schedule, the bus starts from buv campus, then go to 87 Lang Ha, then go to Nguyen Quoc Tri. So if students want to take bus from BUV to Lang Ha, use time slot at BUV, not Lang Ha.
- In the document, The date is abbreviated. For example, Mon is Monday, Tue is Tuesday, and so on.
- Some bus schedules are just effective at a specific time range

Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.

{context}

Question: {question}

Helpful Answer:"""
custom_rag_prompt = PromptTemplate.from_template(template)

bus_schedule_rag_chain = (
    {"context": itemgetter("question") | retriever |
     format_docs, "question": itemgetter("question")}
    | custom_rag_prompt
    | smart_llm
    | StrOutputParser()
)
