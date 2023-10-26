FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY backend/catalogServer.py .

ENTRYPOINT ["python3", "catalogServer.py"]