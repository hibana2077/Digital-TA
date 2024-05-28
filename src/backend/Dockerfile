FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip curl wget

RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8081

CMD ["ollama","pull","llama2","&&","python3", "app.py"]