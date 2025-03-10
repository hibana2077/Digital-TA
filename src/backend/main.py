'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-05-06 21:09:40
LastEditors: hibana2077 hibana2077@gmaill.com
LastEditTime: 2024-06-13 15:49:11
FilePath: \Digital-TA\src\backend\main.py
Description: Here is the main file for the FastAPI server.
'''
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama.embeddings import OllamaEmbeddings
from contextlib import asynccontextmanager
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import redis
import os
import time
import uvicorn
import requests
from fastapi.middleware.cors import CORSMiddleware

ollama_server = os.getenv("OLLAMA_SERVER", "http://localhost:11434")
redis_server = os.getenv("REDIS_SERVER", "localhost")
redis_port = os.getenv("REDIS_PORT", 6379)
HOST = os.getenv("HOST", "127.0.0.1")

counter_db = redis.Redis(host=redis_server, port=redis_port, db=0) # string
user_rec_db = redis.Redis(host=redis_server, port=redis_port, db=1) # hash
question_str_db = redis.Redis(host=redis_server, port=redis_port, db=2) # list

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # pull model from ollama
    _ = requests.post(f"{ollama_server}/api/pull", json={"name": "nomic-embed-text"})


@app.get("/")
def read_root():
    """
    A function that handles the root endpoint.

    Returns:
        dict: A dictionary with the message "Hello: World".
    """
    return {"Hello": "World"}

@app.get("/test/embeddings")
def test_embeddings(text: str):
    time_start = time.time()
    embeddings = OllamaEmbeddings(base_url=ollama_server, model='nomic-embed-text')
    embeddings_list = embeddings.embed_query(text)
    time_end = time.time()
    return {"embeddings": embeddings_list, "time": time_end - time_start,"model_name":embeddings.model}

@app.get("/embedding_count")
def test_embedding_count():
    directory = "embeddings"
    if os.path.exists(directory):
        files = os.listdir(directory)
        return {"embedding_count": len(files), "embedding_names": files}
    else:
        return {"embedding_count": 0, "embedding_names": []}

@app.get("/file_count")
def test_file_count():
    """
    Get the count and names of files in a directory.

    Returns:
        dict: A dictionary containing the file count and file names.
            - file_count (int): The number of files in the directory.
            - file_names (list): A list of file names in the directory.

            If the directory does not exist, the dictionary will also contain:
            - message (str): A message indicating that the directory does not exist.
    """
    directory = "files"  # 設定要檢查的資料夾名稱
    if os.path.exists(directory):
        files = os.listdir(directory)  # 獲取資料夾中的所有檔案名稱
        return {"file_count": len(files), "file_names": files}
    else:
        return {"file_count": 0, "message": "No such directory."}

@app.get("/status/mertics")
def get_status_mertics():
    """
    Retrieves the status metrics.

    Returns:
        dict: A dictionary containing the textbook count, subject count, and dialogue count.
    """
    return {"textbook_count": 3, "subject_count": 2, "dialogue_count": 86}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
        """
        Uploads a file to the server.

        Parameters:
        - file: The file to be uploaded.

        Returns:
        - JSONResponse: A JSON response indicating the status of the upload.
            - message: A message indicating whether the file was uploaded successfully.
            - file_path: The path where the file is saved on the server.
        """
        file_location = f"files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb+") as file_object:
                file_object.write(await file.read())
        return JSONResponse(status_code=200, content={"message": "File uploaded successfully", "file_path": file_location})

@app.post("/create_embeddings")
async def create_embeddings(data: dict):
    file_name: str = data["file_name"]
    embedding_name: str = data["embedding_name"]
    auth_password: str = data["auth_password"]
    if auth_password == "admin":
        time_start = time.time()
        embeddings = OllamaEmbeddings(model='nomic-embed-text', base_url=ollama_server)
        loader = PyPDFLoader("files/" + file_name)
        pages = loader.load_and_split()
        vectorstore = FAISS.from_documents(pages, embeddings)
        vectorstore.save_local("embeddings/" + embedding_name)
        time_end = time.time()
        return {"message": "Embeddings created successfully", "time": time_end - time_start}
    else:
        return {"message": "Authentication failed"}

@app.post("/embed_query")
async def embed_query(data: dict):
    ts = time.time()
    embedding_name: str = data["embedding_name"]
    user_input: str = str(data["user_input"])
    embeddings = OllamaEmbeddings(model='nomic-embed-text', base_url=ollama_server)
    # load the embeddings
    vectorstore = FAISS.load_local("embeddings/" + embedding_name,embeddings,allow_dangerous_deserialization=True)
    # do similarity search
    results = vectorstore.similarity_search(user_input)
    return {"results": results, "time": time.time() - ts}

@app.post("/user_rec")
async def user_rec(data: dict):
    ts = time.time()
    embedding_name: str = data["embedding_name"]
    student_id: str = data["student_id"]
    question_str: str = data["question_str"]
    # save user input to redis
    # name -> student_id, value -> {embedding_name: embedding_name, conversation_times: 1}
    # check if student_id exists
    key = f"{student_id}:{embedding_name}"
    if user_rec_db.hexists(key, "conversation_times"):
        user_rec_db.hincrby(key, "conversation_times", 1)
        question_str_db_id = user_rec_db.hget(key, "question_str_id")
        question_str_db.rpush(question_str_db_id, question_str)
    else:
        question_str_id = counter_db.incr("question_str_id")
        user_rec_db.hset(key, "conversation_times", 1)
        user_rec_db.hset(key, "question_str_id", question_str_id)
        question_str_db.rpush(question_str_id, question_str)
    # return the updated user_rec
    info = user_rec_db.hgetall(student_id)
    return {"user_rec": info, "time": time.time() - ts}

@app.get("/user_rec")
async def get_user_rec(data: dict):
    ts = time.time()
    student_id: str = data["student_id"]
    embedding_name: str = data["embedding_name"]

    # 使用 student_id:embedding_name 作為鍵檢索
    key = f"{student_id}:{embedding_name}"
    if not user_rec_db.exists(key):
        return {"error": "No record found", "time": time.time() - ts}

    # 獲取相關數據
    question_str_id = user_rec_db.hget(key, "question_str_id")
    questions = question_str_db.lrange(question_str_id, 0, -1)
    return {"questions": questions, "time": time.time() - ts}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=8081) # In docker need to change to 0.0.0.0