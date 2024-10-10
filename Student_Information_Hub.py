from backend import buv_with_direct_prompting_source_and_follow_up, su_with_direct_prompting_source_and_follow_up
from backend.utils import language_detection_chain, azure_openai, text_embedding_3large, retriever, FAQ
from upload_file import upload_to_blob_storage, processing_uploaded_file
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
import streamlit as st
from streamlit_float import *
from PIL import Image
import base64
from io import BytesIO
import time
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from openai import BadRequestError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('../application/.env'))

host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
database = os.getenv("PGDATABASE5")
pgport = os.getenv("PGPORT")
COLLECTION_NAME = "langchain_collection"
CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:{pgport}/{database}"
# Create an engine that connects to the PostgreSQL database
engine = create_engine(CONNECTION_STRING)
# Create a configured "Session" class
Session = sessionmaker(bind=engine)
# Create a session
session = Session()


# Load the image
image_path = "./images/Starleo-11.png"
image = Image.open(image_path)

# Set the page configuration
st.set_page_config(
    page_title="Student Information Hub",
    page_icon=image,
    layout="wide"
)

# Convert the image to base64
buffered = BytesIO()
image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# Using streamlit_float for the chat input bar
float_init(theme=True, include_unstable_primary=False)


with st.sidebar:
    # st.page_link('Student_Information_Hub.py',
    #             label='Student Information Hub', icon='🔥')
    # st.page_link('pages/Bus_Information_Assistant.py',
    #             label='Bus Information Assistant', icon='🛡️')
    # Display the image as an icon within a link
    # st.markdown(
    # f"""
    # <a href="https://buv-chatbot.azurewebsites.net" target="_blank" style="text-decoration:none;">
    #     <img src="data:image/png;base64,{img_str}" alt="Bus Information Assistant" style="width:32px;height:32px;vertical-align:middle;">
    #     <strong style="color:black;">Bus Information Assistant</strong>
    # </a>
    # """,
    # unsafe_allow_html=True
    # )
    # st.divider()
    # st.subheader("Feedbacks")
    # st.markdown(
    #     "[Feedback file](https://docs.google.com/spreadsheets/d/1HKQZWltMPqFFeUI_j9jjutgjQUP6TcQohvwGD2GWp1Y/edit?usp=sharing)"
    # )
    # st.subheader("Upload Bus Schedule")
    # uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])
    # if uploaded_file is not None:
    #     # get file name
    #     file_name = uploaded_file.name
    #     print(file_name)

    #     upload_to_blob_storage(file_name=file_name, uploaded_file=uploaded_file)
    #     upload_to_blob_storage(file_name=file_name, uploaded_file=uploaded_file)

    #     processing_uploaded_file(file_name)
    # st.divider()
    on = st.toggle("Show Documents", value=True)
    # if on:
    #     st.markdown(
    #         "[Student Handbook 2023-2024](https://drive.google.com/file/d/1bSHCYZt-EbIzUVW9PCM1tvMe_dH2lG-I/view?usp=sharing)"
    #     )
    #     st.markdown(
    #         "[PSG Programme Handbook](https://drive.google.com/file/d/1rTLl8j2d2NgOvUcQK4c_idVbqzqg-l81/view?usp=sharing)")
    #     st.markdown(
    #         "[SU-JUL24-FAQ.pdf](https://drive.google.com/file/d/17nLU_Qpq8ssSwURePxd-dz4kGTlR8KZ5/view?usp=sharing)"
    #     )
        # st.markdown(
        #     "[BUV-JUL24-FAQ.pdf](https://drive.google.com/file/d/1YMw2cHbfMGLF7melD74MgTcdcjMEYcta/view?usp=sharing)"
        # )
    # Add the disclaimer to the bottom of the left sidebar
    # st.markdown(
    #     "Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit [Chatbot Disclaimer and Guidelines](https://www.buv.edu.vn/en/).")


col1, col2, col3 = st.columns([0.2, 0.05,  0.75], gap="small")
col1.image("images/Starleo-11.png", width=200)
col3.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
col3.title("Student Information Hub")


# with st.chat_message("assistant", avatar="./images/Starleo-03.png"):
#     st.write("Hi, I’m StarLeo, I’m happy to assist you!")
#     st.markdown("<style>div.stRadio {margin-top: -30px;}</style>", unsafe_allow_html=True)
#     bot_name = st.radio(
#         "Please select your awarding body for our further support. If you are a dual degree student, please select the option 'British University Vietnam'.",
#         ["Staffordshire University", "British University Vietnam"],
#         on_change=delete_messages_session_state
#     )
#     if bot_name == "British University Vietnam":
#         with st.sidebar:
#             if on:
#                 st.markdown(
#                     "[BUV-JUL24-FAQ](https://drive.google.com/file/d/1YMw2cHbfMGLF7melD74MgTcdcjMEYcta/view?usp=sharing)"
#                 )
#             # Add the disclaimer to the bottom of the left sidebar
#             st.markdown(
#                 "Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit [Chatbot Disclaimer and Guidelines](https://www.buv.edu.vn/en/).")
#     elif bot_name == "Staffordshire University":
#         with st.sidebar:
#             if on:
#                 st.markdown(
#                     "[SU-JUL24-FAQ](https://drive.google.com/file/d/17nLU_Qpq8ssSwURePxd-dz4kGTlR8KZ5/view?usp=sharing)"
#                 )
#             # Add the previous disclaimer to the bottom of the left sidebar
#             st.markdown(
#                 "Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit [Chatbot Disclaimer and Guidelines](https://www.buv.edu.vn/en/).")
#     st.markdown("For professional assistance and official guidance regarding student matters, please contact the Student Information Office via studentservice@buv.edu.vn.")

# Define constants for URLs and messages
BUV_FAQ_URL = "https://buvbus.blob.core.windows.net/docs/BUV-JUL24-FAQ.pdf"
SU_FAQ_URL = "https://buvbus.blob.core.windows.net/docs/SU-JUL24-FAQ.pdf"

DISCLAIMER_MESSAGE = (
    "Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit [Chatbot Disclaimer and Guidelines](https://buvbus.blob.core.windows.net/docs/Chatbot_Disclaimer_190824.pdf)."
)

SURVEY_MESSAGE = (
    "To help us improve and serve you better, we’d love to hear your thoughts and experiences. Please take a moment to share your feedback by filling out this short survey [User Experience Survey](https://forms.office.com/r/EwP0Cg8exN)"
)

CONTACT_MESSAGE = (
    "For professional assistance and official guidance regarding student matters, please contact the Student Information Office via studentservice@buv.edu.vn."
)

def delete_messages_session_state():
    """
    Delete the 'messages_of_sio_follow_up' key from the session state if it exists.
    """
    st.session_state.pop("messages_of_sio_follow_up", None)
        
with st.chat_message("assistant", avatar="./images/Starleo-03.png"):
    st.write("Hi, I’m StarLeo, I’m happy to assist you!")
    st.markdown("<style>div.stRadio {margin-top: -30px;}</style>", unsafe_allow_html=True)
    
    # bot_name = st.radio(
    #     "Please select your awarding body for our further support. If you are a dual degree student, please select the option 'British University Vietnam'.",
    #     ["Staffordshire University", "British University Vietnam"],
    #     on_change=delete_messages_session_state
    # )
    
    # Radio button to select awarding body
    if "bot_name" not in st.session_state:
        st.session_state["bot_name"] = "Staffordshire University"
    
    bot_name = st.radio(
        "Please select your awarding body for our further support. If you are a dual degree student, please select the option 'British University Vietnam'.",
        ["Staffordshire University", "British University Vietnam"],
        index=["Staffordshire University", "British University Vietnam"].index(st.session_state["bot_name"]),
        key="bot_name",
        on_change=delete_messages_session_state
    )
    
    # Update session state when radio button changes
    # if st.session_state["bot_name"] != bot_name:
    #     st.session_state["bot_name"] = bot_name
    #     delete_messages_session_state()
    
    # Sidebar content based on selection
    with st.sidebar:
        if bot_name == "British University Vietnam" and on:
            st.empty()
            st.markdown(
                "[Student Handbook 2023-2024](https://buvbus.blob.core.windows.net/docs/Student%20Handbook%202023-2024.pdf)"
            )
            st.markdown(
                "[PSG Programme Handbook](https://buvbus.blob.core.windows.net/docs/PSG%20Programme%20Handbook.pdf)")
            st.markdown(f"[BUV-JUL24-FAQ]({BUV_FAQ_URL})")
        elif bot_name == "Staffordshire University" and on:
            st.empty()
            st.markdown(
                "[Student Handbook 2023-2024](https://buvbus.blob.core.windows.net/docs/Student%20Handbook%202023-2024.pdf)"
            )
            st.markdown(
                "[PSG Programme Handbook](https://buvbus.blob.core.windows.net/docs/PSG%20Programme%20Handbook.pdf)")
            st.markdown(f"[SU-JUL24-FAQ]({SU_FAQ_URL})")
        
        # Add the disclaimer to the bottom of the left sidebar
        st.markdown(DISCLAIMER_MESSAGE)

        # Add the survey to the bottom of the left sidebar
        st.markdown(SURVEY_MESSAGE)
        
    
    # Footer message
    st.markdown(CONTACT_MESSAGE)

# Inject custom CSS to make the button smaller
st.markdown(
    """
    <style>
    .small-button {
        font-size: 12px !important;
        padding: 5px 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create a smaller reset button to clear the chat history
# if st.button("Reset Chat", key="reset_chat", help="Click to reset chat history", on_click=delete_messages_session_state):
#     pass
# if st.button("Reset Chat", key="reset_chat", help="Click to reset chat history"):
#     delete_messages_session_state()

# Create a new reset button to clear the chat history
# if st.button("Reset Chat"):
#     delete_messages_session_state()

# bot_engine = su_with_direct_prompting_source_and_follow_up.chain_with_follow_up if bot_name == "Staffordshire University" else buv_with_direct_prompting_source_and_follow_up.chain_with_follow_up
# fixed_answer = "For SU students:" if bot_name == "Staffordshire University" else "For BUV students:"

if bot_name == "Staffordshire University":
    message_history = StreamlitChatMessageHistory(key="su_follow_up_memory")
    bot_engine = su_with_direct_prompting_source_and_follow_up.chain_with_follow_up_function(
        message_history)
    fixed_answer = "For SU students:"
else:
    # message_history = StreamlitChatMessageHistory(key="buv_follow_up_memory")
    message_history = StreamlitChatMessageHistory(key="chat_history")
    bot_engine = buv_with_direct_prompting_source_and_follow_up.chain_with_follow_up_function(
        message_history)
    fixed_answer = "For BUV students:"

if "messages_of_sio_follow_up" not in st.session_state:
    st.session_state["messages_of_sio_follow_up"] = []

# print(st.session_state)

for msg in st.session_state.messages_of_sio_follow_up:
    if msg['role'] == "user":
        st.chat_message(msg["role"]).write(msg["content"])
    else:
        st.chat_message(
            msg["role"], avatar="./images/Starleo-13.png").write(msg["content"])

from langchain_core.runnables.config import RunnableConfig
from typing import Optional, Iterator, Any
from langchain_core.runnables.utils import Input, Output

def stream(
    chain,
    input: Input,
    config: Optional[RunnableConfig] = None,
    **kwargs: Optional[Any],
) -> Iterator[Output]:
    """
    Default implementation of stream, which calls invoke.
    Subclasses should override this method if they support streaming output.

    Args:
        input: The input to the Runnable.
        config: The config to use for the Runnable. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the Runnable.

    Yields:
        The output of the Runnable.
    """
    yield chain.invoke(input, config, **kwargs)['answer']


with st.container():
    # Create a 2 column layout
    col4, col5 = st.columns([0.85, 0.15])
    
    with col5:
        reset_button_b_pos = "2rem"
        reset_button_css = float_css_helper(width="12rem", bottom=reset_button_b_pos, right="0rem", transition=0)
        float_parent(css=reset_button_css)
        if st.button("Reset Chat", key="reset_chat", help="Click to reset chat history"):
            delete_messages_session_state()
            st.rerun()

    with col4:
        prompt = st.chat_input("Hi! How can I help you?")
        button_b_pos = "2rem"
        button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
        float_parent(css=button_css)
        # if prompt := st.chat_input():
    
    if prompt:
        # If the bot_engine is Staffordshire University, handle the prompt
        if bot_name == "Staffordshire University":
            # try:
            # retrieved = retriever.get_relevant_documents(prompt)
            retrieved = retriever.invoke(prompt)

            if retrieved:
                handled_prompt, answer = retrieved[0].page_content, retrieved[0].metadata['answer']
                answer = None if answer == " " else answer
            else:
                handled_prompt, answer = prompt, None
            
            st.session_state.messages_of_sio_follow_up.append(
                {"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            with st.spinner("Processing data ..."):
                with st.chat_message("assistant", avatar="./images/Starleo-13.png"):
                    st.write(fixed_answer)
                    language_detection = language_detection_chain.invoke(
                        {"input": prompt})
                    print("language_detection", language_detection)
                    if language_detection == "Vietnamese":
                        response = "We're sorry for any inconvenience; however, StarLeo can only answer questions in English. Unfortunately, Vietnamese isn't available at the moment. Thank you for your understanding!"
                        st.write(response)
                    else:
                        if answer:
                            response = answer
                            st.write(response)
                        else:
                        # print(
                        #     buv_with_direct_prompting_source_and_follow_up.demo_ephemeral_chat_history.messages)
                        # context_q_chain = buv_with_direct_prompting_source_and_follow_up.contextualize_q_prompt | gpt_4o | StrOutputParser()
                        # q_with_context = context_q_chain.invoke({"input": prompt,
                        #                                          "chat_history": buv_with_direct_prompting_source_and_follow_up.demo_ephemeral_chat_history.messages})
                        # print(
                        #     f"Latest question: {prompt} \nNew query: {q_with_context}")
                            stream_response = bot_engine.stream(
                                {"input": handled_prompt},
                                {"configurable": {"session_id": "unused"}},
                            )
                            print("stream_response", stream_response)
                            response = st.write_stream(stream_response)

            st.session_state.messages_of_sio_follow_up.append(
                {"role": "assistant", "content": fixed_answer + "\n\n" + response})
            # Create a new FAQ instance
            new_faq = FAQ(question=prompt, answer=response, bot_type=bot_name)
            # Add the new instance to the session
            session.add(new_faq)
            # Commit the session to insert the data into the table
            session.commit()
            # except BadRequestError:
            #     standard_message = ("Thank you for your question. For further assistance, please contact our Student Information Office via email at studentservice@buv.edu.vn or by phone at 0936 376 136.")
            #     st.markdown(standard_message)
                
            #     # Create a new FAQ instance
            #     new_faq = FAQ(question=prompt, answer=standard_message, bot_type=bot_name)
            #     # Add the new instance to the session
            #     session.add(new_faq)
            #     # Commit the session to insert the data into the table
            #     session.commit()
                
        else:
            try:
                st.session_state.messages_of_sio_follow_up.append(
                    {"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)

                with st.spinner("Processing data ..."):
                    with st.chat_message("assistant", avatar="./images/Starleo-13.png"):
                        st.write(fixed_answer)
                        language_detection = language_detection_chain.invoke(
                            {"input": prompt})
                        print("language_detection", language_detection)
                        if language_detection == "Vietnamese":
                            response = "We're sorry for any inconvenience; however, StarLeo can only answer questions in English. Unfortunately, Vietnamese isn't available at the moment. Thank you for your understanding!"
                            st.write(response)
                        else:
                            # print(
                            #     buv_with_direct_prompting_source_and_follow_up.demo_ephemeral_chat_history.messages)
                            # context_q_chain = buv_with_direct_prompting_source_and_follow_up.contextualize_q_prompt | gpt_4o | StrOutputParser()
                            # q_with_context = context_q_chain.invoke({"input": prompt,
                            #                                          "chat_history": buv_with_direct_prompting_source_and_follow_up.demo_ephemeral_chat_history.messages})
                            # print(
                            #     f"Latest question: {prompt} \nNew query: {q_with_context}")
                            # stream_response = bot_engine.stream(
                            #     {"input": prompt},
                            #     {"configurable": {"session_id": "unused"}},
                            # )
                            stream_response = stream(bot_engine,
                                {"input": prompt},
                                {"configurable": {"session_id": "unused"}},
                            )
                            print("stream_response", stream_response)
                            response = st.write_stream(stream_response)
                            # response = st.write_stream(stream_response['answer'])

                st.session_state.messages_of_sio_follow_up.append(
                    {"role": "assistant", "content": fixed_answer + "\n\n" + response})
                # Create a new FAQ instance
                new_faq = FAQ(question=prompt, answer=response, bot_type=bot_name)
                # Add the new instance to the session
                session.add(new_faq)
                # Commit the session to insert the data into the table
                session.commit()
            except BadRequestError:
                standard_message = ("Thank you for your question. For further assistance, please contact our Student Information Office via email at studentservice@buv.edu.vn or by phone at 0936 376 136.")
                st.markdown(standard_message)
                
                # Create a new FAQ instance
                new_faq = FAQ(question=prompt, answer=standard_message, bot_type=bot_name)
                # Add the new instance to the session
                session.add(new_faq)
                # Commit the session to insert the data into the table
                session.commit()

    # st.session_state.messages_of_sio_follow_up.append(
    #     {"role": "user", "content": prompt})
    # st.chat_message("user").write(prompt)

    # with st.spinner("Processing data ..."):
    #     with st.chat_message("assistant", avatar="./images/Starleo-13.png"):
    #         st.write(fixed_answer)
    #         language_detection = language_detection_chain.invoke(
    #             {"input": prompt})
    #         print("language_detection", language_detection)
    #         if language_detection == "Vietnamese":
    #             response = "We're sorry for any inconvenience; however, StarLeo can only answer questions in English. Unfortunately, Vietnamese isn't available at the moment. Thank you for your understanding!"
    #             st.write(response)
    #         else:
    #             # print(
    #             #     buv_with_direct_prompting_source_and_follow_up.demo_ephemeral_chat_history.messages)
    #             # context_q_chain = buv_with_direct_prompting_source_and_follow_up.contextualize_q_prompt | gpt_4o | StrOutputParser()
    #             # q_with_context = context_q_chain.invoke({"input": prompt,
    #             #                                          "chat_history": buv_with_direct_prompting_source_and_follow_up.demo_ephemeral_chat_history.messages})
    #             # print(
    #             #     f"Latest question: {prompt} \nNew query: {q_with_context}")
    #             stream_response = bot_engine.stream(
    #                 {"input": prompt},
    #                 {"configurable": {"session_id": "unused"}},
    #             )
    #             print("stream_response", stream_response)
    #             response = st.write_stream(stream_response)

    # st.session_state.messages_of_sio_follow_up.append(
    #     {"role": "assistant", "content": fixed_answer + "\n\n" + response})

