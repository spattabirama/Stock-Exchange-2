import http.client
import requests
import random
import json
import time
import socket



prob = 0.7
stock_names = ['GameStart','FishCo','BoarCo','MehirCo']

# Takes http response and returns the json body of the response
def decode_http_response(response):
    print(response)
    req = response.decode().split('\r\n')
    ind = req.index('')
    orderdict = (json.loads(req[ind + 1]))
    return orderdict

# Takes the stockName and creates values for trade request
def create_trade_request(stockName):
    trade_req = dict()
    trade_req['name'] = stockName
    trade_req['quantity'] = random.randint(1,10)
    trade_req['type'] = random.choice(['buy','sell'])
    return trade_req

# Connect to the frontendserver and sends get and post requests
def connect():
    host = socket.gethostname()
    port = 6261
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    t1 = time.perf_counter()
    for i in range(1000):
        # Randomly choose a stock
        stockName = random.choice(stock_names)
        # Create body for trade request
        content = json.dumps(create_trade_request(stockName))
        # Create a trade request
        trade_request = f"POST /orders HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(content)}\r\nContent-Type: application/json\r\n\r\n{content}"
        # Send trade request through the socket
        client_socket.send(trade_request.encode())
        # Receive trade response
        trade_response = client_socket.recv(4096)
        #Extract the json body of the response
        decode_http_response(trade_response)


    print(time.perf_counter()-t1)


connect()
