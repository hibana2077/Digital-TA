from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
import streamlit as st
import translators as ts
import requests
import os

# _ = ts.preaccelerate_and_speedtest(timeout=1.5)
OLLAMA_SERVER = os.getenv("OLLAMA_SERVER", "http://localhost:11434")
BACKEND_SERVER = os.getenv("BACKEND_SERVER", "http://localhost:8081")
TRANSLATOR_PROVIDER = os.getenv("TRANSLATOR_PROVIDER", "google")
EXTRACT_PROMPT = PromptTemplate.from_template(
    "You are an Top algorithm, you need to according to user input extract information from the content. user input: {user_input}, content: {content}"
)


def get_all_embeddings() -> list:
    response = requests.get(f"{BACKEND_SERVER}/embedding_count")
    if response.status_code == 200:
        return response.json()["embedding_names"]
    else:
        return []

def embeddings_search(user_input: str, embedding_name: str) -> dict:
    response = requests.get(f"{BACKEND_SERVER}/embed_query", params={"user_input": user_input, "embedding_name": embedding_name})
    if response.status_code == 200:
        return response.json()
    else:
        return {"embeddings": [], "time": 0}

def init_chat_history() -> ChatPromptTemplate:
    if 'chat_history' not in st.session_state:
        template = ChatPromptTemplate.from_messages([
            ('system', "You are an AI Teaching Assistant, you need to help students with their questions based on the content of the textbooks."),
        ])
        st.session_state['chat_history'] = template
    else:
        template = st.session_state['chat_history']
    return template

header_col, embeddings_select_col = st.columns([0.7,0.3])

with header_col:
    st.header("Chat")

with embeddings_select_col:
    embeddings = get_all_embeddings()
    embeddings_select = st.selectbox("Select an embedding", embeddings, index=None)

chat_tmp = init_chat_history()
llm = ChatOllama(model="llama2", base_url=OLLAMA_SERVER)
user_input = st.chat_input("You can start a conversation with the AI Teaching Assistant here.")
chain = chat_tmp | llm | StrOutputParser()

if user_input:
    if embeddings_select != "":
        with st.status("Searching for book content..."):
            embeddings_search_result = embeddings_search(user_input, embeddings_select)

        with st.status("Extracting information..."):
            extracted_info = ""
            for embedding in embeddings_search_result["results"]:
                # embedding is dict with keys: "page_content", "metadata"
                # metadata is dict with keys: "page", "source"
                extract_template = EXTRACT_PROMPT.format(user_input=user_input, content=embedding["page_content"])
                extract_chain = extract_template | llm | StrOutputParser()
                extract_response = extract_chain.invoke({})
                extracted_info += f"Page {embedding['metadata']['page']}: {extract_response}\n"
            
        with st.status("Digital TA Thinking..."):
            chat_tmp.append(SystemMessage(f"Extracted information from the content: {extracted_info}"))
            chat_tmp.append(HumanMessage(ts.translate_text(user_input, translator=TRANSLATOR_PROVIDER, to_language="en")))
            response = chain.invoke({})
            chat_tmp.append(AIMessage(response))
            st.session_state['chat_history'] = chat_tmp

for message in st.session_state['chat_history'].messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(ts.translate_text(message.content, translator=TRANSLATOR_PROVIDER, to_language="zh-TW"))
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(ts.translate_text(message.content, translator=TRANSLATOR_PROVIDER, to_language="zh-TW"))
    