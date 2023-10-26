import random
import json
import time
import socket


# Initiating stock name list and probability value
stock_names = ['GameStart', 'FishCo', 'BoarCo', 'MehirCo']
prob = 0.7


# Takes http response and returns the json body of the response
def decode_http_response(response):
    req = response.decode().split('\r\n')
    ind = req.index('')
    orderdict = json.loads(req[ind + 1])
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
    port = 6255
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    t1 = time.perf_counter()
    for i in range(1000):
        # Randomly choose a stock
        stockName = random.choice(stock_names)
        # Generate a http lookup request
        lookup_request = f"GET /stocks/{stockName} HTTP/1.1\r\nHost: {host}\r\n"
        # Send the http request over a socket
        client_socket.send(lookup_request.encode())
        # Receive the lookup response
        client_socket.recv(4096)
    print(time.perf_counter()-t1)


connect()