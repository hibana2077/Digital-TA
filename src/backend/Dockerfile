FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip curl wget

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8081

# CMD ["python3", "main.py"]
CMD ["ls", "-la"]