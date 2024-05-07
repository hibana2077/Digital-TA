'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-05-06 23:44:15
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-05-07 09:38:31
FilePath: \Digital-TA\src\st_web\pages\Embeddings.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import streamlit as st
import requests
import os

st.header("Embeddings")

# show the embeddings


# show the files that have been uploaded
st.subheader("Uploaded Files")
response = requests.get("http://localhost:8081/test/file_count")
if response.status_code == 200 and response.json()["file_count"] > 0:
    files = response.json()["file_names"]
    for file in files:
        st.write(file)
else:
    st.write("No files have been uploaded yet.")