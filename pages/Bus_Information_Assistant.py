from openai import OpenAI
import streamlit as st
from streamlit_float import *
from backend.bus_schedule_with_csv_agent import get_answer
from backend.utils import FAQ
from st_pages import Page, Section, show_pages, add_page_title, hide_pages
from utilize.const import introduction
from utilize.Routing import *
from upload_file import upload_to_blob_storage, processing_uploaded_file

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    page_title="Bus Information Assistant",
    page_icon=image,
    layout="wide"
)

# Using streamlit_float for the chat input bar
float_init(theme=True, include_unstable_primary=False)


with st.sidebar:
    # st.page_link('Student_Information_Hub.py',
    #              label='Student Information Hub', icon='🔥')
    # st.page_link('pages/Bus_Information_Assistant.py',
    #              label='Bus Information Assistant', icon='🛡️')
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
    if on:
        st.markdown(
            "[BUV Shuttle Bus Operation Instruction](https://buvbus.blob.core.windows.net/docs/BUV%20Shuttle%20Bus%20Operation%20Instruction.pdf)"
        )
        # st.markdown(
        #     "[PSG Programme Handbook](https://drive.google.com/file/d/1rTLl8j2d2NgOvUcQK4c_idVbqzqg-l81/view?usp=sharing)")
        # st.markdown(
        #     "[SU-JUL24-FAQ.pdf](https://drive.google.com/file/d/17nLU_Qpq8ssSwURePxd-dz4kGTlR8KZ5/view?usp=sharing)"
        # )
        # st.markdown(
        #     "[BUV-JUL24-FAQ.pdf](https://drive.google.com/file/d/1YMw2cHbfMGLF7melD74MgTcdcjMEYcta/view?usp=sharing)"
        # )
    # Add the disclaimer to the bottom of the left sidebar
    st.markdown(
        "Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit [Chatbot Disclaimer and Guidelines](https://www.buv.edu.vn/en/).")

col1, col2, col3 = st.columns([0.2, 0.05,  0.75], gap="small")
col1.image("images/Starleo-11.png", width=200)
col3.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
col3.title("Bus Information Assistant")

def delete_messages_session_state():
    """
    Delete the 'messages' key from the session state if it exists.
    """
    st.session_state.pop("messages", None)

def update_params():
    if st.session_state.option == "Bus Schedule":
        st.session_state.suggested_questions = [
            "Could you tell me about bus route Hai Ba Trung?",
            "Could you tell me about bus route Tay Ho?",
            "Could you tell me about bus route Cau Giay?",
            "Could you tell me about bus route Ha Dong?",
            "Could you tell me about bus route Ecopark?",
        ]
        st.session_state.state = {
            "route name": [],
            "pick-up point": [],
            "drop-off point": [],
            "specific date": [],
            "specific time": []
        }
    elif st.session_state.option == "Bus General Information":
        st.session_state.suggested_questions = []

def delete_messages_and_update_params():
    delete_messages_session_state()
    update_params()

# st.image("https://www.buv.edu.vn/wp-content/themes/main/assets/images/common/logo.png")
# st.title("💬 Bus Information Assistant")
# st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [
#         {"role": "assistant", "content": "Hi, I’m StarLeo, I’m happy to assist you!"}]

with st.chat_message("assistant", avatar="./images/Starleo-03.png"):
    st.write("Hi, I’m StarLeo. What can I assist you with today?")
    st.markdown("<style>div.stRadio {margin-top: -35px;}</style>", unsafe_allow_html=True)
    chatbot_type = st.radio(
        "",
        ("Bus Schedule", "Bus General Information"),
        key="option",
        on_change=delete_messages_and_update_params
    )
    # if chatbot_type == "Bus Schedule":
    #     with st.sidebar:
    #         if on:
    #             st.markdown(
    #                 "[BUV-JUL24-FAQ](https://drive.google.com/file/d/1YMw2cHbfMGLF7melD74MgTcdcjMEYcta/view?usp=sharing)"
    #             )
    #         # Add the disclaimer to the bottom of the left sidebar
    #         st.markdown(
    #             "Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit [Chatbot Disclaimer and Guidelines](https://www.buv.edu.vn/en/).")
    # elif chatbot_type == "Bus General Information":
    #     with st.sidebar:
    #         if on:
    #             st.markdown(
    #                 "[SU-JUL24-FAQ](https://drive.google.com/file/d/17nLU_Qpq8ssSwURePxd-dz4kGTlR8KZ5/view?usp=sharing)"
    #             )
    #         # Add the previous disclaimer to the bottom of the left sidebar
    #         st.markdown(
    #             "Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit [Chatbot Disclaimer and Guidelines](https://www.buv.edu.vn/en/).")
    st.markdown("If you are required an immediate assistance, please call our hotline at **0704 068 386**")
    st.markdown("If you have any feedback or special request, feel free to contact the Transportation Team via transportation@buv.edu.vn.")

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
# if st.button("Reset Chat", key="reset_chat", help="Click to reset chat history", on_click=delete_messages_and_update_params):
#     pass

# Apply the custom CSS class to the button
st.markdown(
    """
    <script>
    const button = document.querySelector('button[kind="primary"][key="reset_chat"]');
    if (button) {
        button.classList.add('small-button');
    }
    </script>
    """,
    unsafe_allow_html=True
)

#------ create session state -------
if "state" not in st.session_state:
    st.session_state.state = {
        "route name": [],
        "pick-up point": [],
        "drop-off point": [],
        "specific date": [],
        "specific time": []
    }
if "latest_bot_answer" not in st.session_state:
    st.session_state.latest_bot_answer = ""
#-----------------------------------

# def update_params():
#     if st.session_state.option == "Bus Schedule":
#         st.session_state.suggested_questions = [
#             "Could you tell me about bus route Hai Ba Trung?",
#             "Could you tell me about bus route Tay Ho?",
#             "Could you tell me about bus route Cau Giay?",
#             "Could you tell me about bus route Ha Dong?",
#             "Could you tell me about bus route Ecopark?",
#         ]
#         st.session_state.state = {
#             "route name": [],
#             "pick-up point": [],
#             "drop-off point": [],
#             "specific date": [],
#             "specific time": []
#         }
#     elif st.session_state.option == "Bus General Information":
#         st.session_state.suggested_questions = []


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize suggested questions
if "suggested_questions" not in st.session_state:
    # if chatbot_type=="Bus Schedule":
    st.session_state.suggested_questions = [
        "Could you tell me about bus route Hai Ba Trung?",
        "Could you tell me about bus route Tay Ho?",
        "Could you tell me about bus route Cau Giay?",
        "Could you tell me about bus route Ha Dong?",
        "Could you tell me about bus route Ecopark?",
    ]
    # else:
    #     st.session_state.suggested_questions = []

    # st.session_state.suggested_questions = []


# Initialize selected questions
if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []

# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])
for msg in st.session_state.messages:
    if msg['role'] == "user":
        st.chat_message(
            msg["role"]).write(msg["content"])
    else:
        st.chat_message(
            msg["role"], avatar="./images/Starleo-13.png").write(msg["content"])

with st.container():
    # Create a 2 column layout
    col4, col5 = st.columns([0.85, 0.15])
    with col5:
        reset_button_b_pos = "2rem"
        reset_button_css = float_css_helper(width="12rem", bottom=reset_button_b_pos, right="0rem", transition=0)
        float_parent(css=reset_button_css)
        if st.button("Reset Chat", key="reset_chat", help="Click to reset chat history"):
            delete_messages_and_update_params()
            st.rerun()
    
    with col4:
        prompt = st.chat_input("Hi! How can I help you?")
        button_b_pos = "2rem"
        button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
        float_parent(css=button_css)
    
    # if prompt := st.chat_input("Hi! How can I help you?"):
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        # st.chat_message("user").write(prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        print(prompt)
        answer, suggested_questions, url_ = clarify(prompt, chatbot_type)

        with st.spinner("Processing data ..."):
            with st.chat_message("assistant", avatar="./images/Starleo-13.png"):
                response = answer
                st.markdown(answer)
                if len(url_["Zalo QR Code"])>0:
                    print(url_)
                    st.markdown("Here is Zalo QR Code:")
                    # image_zaloQR = Image.open(url_["Zalo QR Code"][0])
                    # image_zaloQR = Image.open("data/img/QR_Code/ZaloQRCode.png")
                    # st.image(image_zaloQR, width=500)
                    image_url = url_["Zalo QR Code"][0]
                    st.markdown(f'<img src="{image_url}" alt="Image" style="width:700px;">', unsafe_allow_html=True)
                if len(url_["Bus images"])>0:
                    print(url_)
                    st.markdown("An image of BUV bus:")
                    # image_NormalBus = Image.open(url_["Bus images"][0])
                    # st.image(image_NormalBus, width=500)
                    image_url = url_["Bus images"][0]
                    # "https://buvbus.blob.core.windows.net/images/Bus_schedule_guide.jpg"
                    st.markdown(f'<img src="{image_url}" alt="Image" style="width:700px;">', unsafe_allow_html=True)
                    # st.image()
                if len(url_["GPS Link"])>0:
                    print(url_)
                    # for link in url_["GPS Link"]:
                    link = url_["GPS Link"][0]
                    st.write(f"""Visit the [Link]({link}) for more information.""")
            # response = get_answer(prompt)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Update suggested questions
        st.session_state.suggested_questions = suggested_questions
        
        # Create a new FAQ instance
        new_faq = FAQ(question=prompt, answer=response, bot_type=chatbot_type)
        # Add the new instance to the session
        session.add(new_faq)
        # Commit the session to insert the data into the table
        session.commit()

        # msg = response  # response["output"]
        # st.session_state.messages.append({"role": "assistant", "content": msg})
        # st.chat_message("assistant", avatar="./images/Starleo-13.png").write(msg)

# Display suggested questions
st.markdown("### Suggestions")
for question in st.session_state.suggested_questions:
    if st.button(question):
        # Add the selected question to the list of selected questions
        st.session_state.selected_questions.append(question)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        # Display user message in chat message container
        with st.chat_message("user"):
            # st.markdown(question)
            st.write(question)

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar="data/img/BUV_assistant_icon.png"):
            # get the answer and suggested questions from vectordb
            try:
                answer, suggested_questions, url_ = clarify(question, chatbot_type)
            except:
                answer = "Sorry, I cannot find related information."
                suggested_questions = []
            # display answer
            # response = st.write_stream(response_generator(answer))
            response = answer
            st.markdown(answer)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Update suggested questions
        st.session_state.suggested_questions = suggested_questions
        
        # Create a new FAQ instance
        new_faq = FAQ(question=question, answer=response, bot_type=chatbot_type)
        # Add the new instance to the session
        session.add(new_faq)
        # Commit the session to insert the data into the table
        session.commit()
        
        st.rerun()
