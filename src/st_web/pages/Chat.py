'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-05-05 14:01:07
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-05-06 21:26:03
FilePath: \Digital-TA\src\st_web\pages\Chat.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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
    