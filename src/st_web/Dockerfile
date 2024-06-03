FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip curl wget

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN pip3 install -U pip

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN uv pip install -r requirements.txt

COPY . /app

EXPOSE 80

CMD ["python3", "-m", "streamlit", "run", "Home.py", "--server.port", "80", "--server.enableCORS", "false","--server.enableXsrfProtection", "false"]