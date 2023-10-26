FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY backend/orderServer.py .

ENTRYPOINT ["python3", "orderServer.py"]