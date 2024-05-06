'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-05-06 21:09:40
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-05-06 23:55:55
FilePath: \Digital-TA\src\backend\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import time
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

embeddings = OllamaEmbeddings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test/embeddings")
def test_embeddings(text: str):
    time_start = time.time()
    embeddings_list = embeddings.embed_query(text)
    time_end = time.time()
    return {"embeddings": embeddings_list, "time": time_end - time_start,"model_name":embeddings.model}

@app.get("/test/file_count")
def test_file_count():
    directory = "files"  # 設定要檢查的資料夾名稱
    if os.path.exists(directory):
        files = os.listdir(directory)  # 獲取資料夾中的所有檔案名稱
        return {"file_count": len(files), "file_names": files}
    else:
        return {"file_count": 0, "message": "No such directory."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"files/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    return JSONResponse(status_code=200, content={"message": "File uploaded successfully", "file_path": file_location})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081) # In docker need to change to 0.0.0.0