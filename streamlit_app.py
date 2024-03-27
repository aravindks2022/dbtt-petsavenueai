import re
import streamlit as st
import time
from openai import OpenAI

api_key = st.secrets["openai_apikey"]
assistant_id = st.secrets["assistant_id"]

st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6; /* Change the color to your desired background color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def load_openai_client_and_assistant():
    client = OpenAI(api_key=api_key)
    my_assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()

    return client, my_assistant, thread

client, my_assistant, assistant_thread = load_openai_client_and_assistant()

# The following function is to check on loop if the assistant has processed and responded to our message
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

#Initiate a response from the PetsAvenue AI
def get_assistant_response(user_input=""):
    message = client.beta.threads.messages.create(
        thread_id=assistant_thread.id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(
        thread_id = assistant_thread.id,
        assistant_id=assistant_id,
    )

    run = wait_on_run(run, assistant_thread)

    messages = client.beta.threads.messages.list(
        thread_id = assistant_thread.id, order="asc", after=message.id
    )

    message_data = messages.data[0].content[0].text.value

    ## Remove anything in [] brackets to remove source
    message_data = re.sub(r'\[.*?\]', '', message_data)

    return message_data

if "user_input" not in st.session_state:
    st.session_state.user_input = ''

def submit():
    st.session_state.user_input = st.session_state.query
    st.session_state.query = ''

st.title("Pets Avenue AI Chatbot for Diagnosis")

st.text_input("Hi! My name is Aliya! - the extremely smart AI Doctor! and I am here to help diagnose your pet! Please input your pet's symptoms. Be as detailed as possible!", key='query', on_change=submit)

user_input = st.session_state.user_input

st.write("You entered: ", user_input)

print(user_input)

if user_input:
    result = get_assistant_response(user_input)
    st.header("Dr. Aliya's Diagnosis", divider="rainbow")
    st.write(result)