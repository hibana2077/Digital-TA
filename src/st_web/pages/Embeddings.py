
import streamlit as st
import requests
import os

st.header("Embeddings")

# show the embeddings


# show the files that have been uploaded
st.subheader("Uploaded Files")
response = requests.get("http://localhost:8081/file_count")
if response.status_code == 200 and response.json()["file_count"] > 0:
    files = response.json()["file_names"]
    for file in files:
        st.write(file)
else:
    st.write("No files have been uploaded yet.")