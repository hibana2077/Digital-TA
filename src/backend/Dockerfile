FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip curl wget

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN uv pip install -r requirements.txt

COPY . /app

EXPOSE 8081

CMD ["python3", "main.py"]