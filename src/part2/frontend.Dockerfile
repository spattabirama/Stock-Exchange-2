FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY frontend/frontendServer.py .

ENTRYPOINT ["python3", "frontendServer.py"]