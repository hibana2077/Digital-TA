FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip curl wget

RUN curl -fsSL https://ollama.com/install.sh | sh

# This is aa new thing , github copilot does not know about this 哈!
RUN ollama pull llama2

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8081

CMD ["python3", "app.py"]