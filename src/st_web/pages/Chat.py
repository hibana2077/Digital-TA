
import streamlit as st
import translators as ts
import requests

st.header("Chat")

prompt = st.chat_input("Say something")
if prompt:
    message = st.chat_message("user")
    message.write(prompt)
    message = st.chat_message("assistant")
    message.write("Hello human")
    