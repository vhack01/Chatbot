from langchain_core.messages import AIMessage
import streamlit as st
from backend import stream, retrive_all_conversations
from langchain_core.messages import HumanMessage
from util import generate_thread_id

#************ utility functions ************

def init():
    if "chat_history" not in st.session_state:
        st.session_state['active_thread_id'] = generate_thread_id()
        st.session_state['chat_history'] = {**retrive_all_conversations(), st.session_state['active_thread_id'] : []}

def load_messages(thread_id):
    st.title('Ask me anything...')
    if thread_id:
        message_history = chat_history.get(thread_id, [])

        for message in message_history:
            with st.chat_message(message['role']):
                st.text(message['content'])    

def load_threads():
    for thread_id in chat_history:
        if st.button(thread_id):
            st.session_state['active_thread_id'] = thread_id
            st.rerun()

#************ Session setup ************
    
init()
chat_history = st.session_state['chat_history']
active_thread_id = st.session_state['active_thread_id']

#********* Show message history *********

load_messages(active_thread_id)

#************ Sidebar ************
with st.sidebar:
    st.title("Chatbot Janta Party")

    if st.button("New Chat"):
        active_thread_id = generate_thread_id()
        chat_history[active_thread_id] = []
        st.session_state['active_thread_id'] = active_thread_id
        st.rerun()

    st.markdown('---')
    st.subheader("Recent Chats")

    load_threads()
        

#************ User Input ************

def get_ai_message(stream_generator):
    for chunk, metadata in stream_generator:
        if isinstance(chunk, AIMessage) and chunk.content:
            yield chunk.content

user_input = st.chat_input("Ask something")

if user_input:
    
    chat_history[active_thread_id].append({'role': 'user', "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)

    config = {'configurable': {'thread_id': active_thread_id}}

    stream_generator = stream({'messages': [HumanMessage(content=user_input)]}, config=config)
    
    with st.chat_message('assistant'):
        ai_message = st.write_stream(get_ai_message(stream_generator))
        chat_history[active_thread_id].append({'role': 'assistant', "content": ai_message})
    


