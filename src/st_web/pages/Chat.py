from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
import streamlit as st
import translators as ts
import requests
import os

# _ = ts.preaccelerate_and_speedtest(timeout=1.5)
OLLAMA_SERVER = os.getenv("OLLAMA_SERVER", "http://localhost:11434")
TRANSLATOR_PROVIDER = os.getenv("TRANSLATOR_PROVIDER", "google")

st.header("Chat")

def init_chat_history() -> ChatPromptTemplate:
    if 'chat_history' not in st.session_state:
        template = ChatPromptTemplate.from_messages([
            ('system', "You are an AI Teaching Assistant, you need to help students with their questions based on the content of the textbooks."),
        ])
        st.session_state['chat_history'] = template
    else:
        template = st.session_state['chat_history']
    return template

chat_tmp = init_chat_history()
llm = ChatOllama(model="llama2", base_url=OLLAMA_SERVER)
user_input = st.chat_input("You can start a conversation with the AI Teaching Assistant here.")
chain = chat_tmp | llm | StrOutputParser()

if user_input:
    with st.status("Thinking..."):
        chat_tmp.append(HumanMessage(ts.translate_text(user_input, translator=TRANSLATOR_PROVIDER, to_language="en")))
        response = chain.invoke({})
        chat_tmp.append(AIMessage(response))
        st.session_state['chat_history'] = chat_tmp

if len(st.session_state['chat_history'].messages) == 1:
    st.html("<p align='center'><h3>Start a conversation with the AI Teaching Assistant!</h3></p>")

for message in st.session_state['chat_history'].messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(ts.translate_text(message.content, translator=TRANSLATOR_PROVIDER, to_language="zh-TW"))
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(ts.translate_text(message.content, translator=TRANSLATOR_PROVIDER, to_language="zh-TW"))
    