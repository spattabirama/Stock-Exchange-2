import random
import json
import time
import socket
'''
This is a test for testing the frontendServer.
GET and POST http requests are sent using the API endpoints of the frontendServer
The returned values are compared and assert is used to check if they are the same
'''



prob = 0.5

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

stocklst = ['GameStart', 'Hellow', 'FishCo']
output_lookup = [{"data": {"name": "GameStart","price":2.2,"quantity": 100}},{"error": {"code": 404, "message": "stock not found"}},{"data": {"name": "FishCo","price":1.4,"quantity": 100}}]
input_trade = [{"name": "GameStart","quantity": 105,"type":'buy'},{},{"name": "Fishco","quantity":45,"type":'sell'}]
output_trade = [{"error": {"code": 403, "message": 'Not enough stock'}}, {},{"data": {"transaction_number":1}}]

# Connect to the frontendserver and sends get and post requests
def connect():
    host = 'localhost'
    port = 6260
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    t1 = time.perf_counter()
    for i in range(4):
        # Pick the stock
        stockName = stocklst[i]
        # Generate a http lookup request
        lookup_request = f"GET /stocks/{stockName} HTTP/1.1\r\nHost: {host}\r\n"
        # Send the http request over a socket
        client_socket.send(lookup_request.encode())
        #Receive the lookup response
        lookup_response = client_socket.recv(4096)
        #Decode the response
        output = decode_http_response(lookup_response)
        print('stockname',stockName)
        print('lookup_output ',output)
        print('expected_output',output_lookup[i])
        assert output== output_lookup[i]
        ans = random.randint(0, 1)
        # Check if the stock exists
        if 'error' in output:
            print(output)
        # If the generated probability is less than the current probability,send a trade request
        elif ans <= prob:
            # Create body for trade request
                content = json.dumps(create_trade_request(stockName,))
                print('trade request :',content)
                # Create a trade request
                trade_request = f"POST /orders HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(content)}\r\nContent-Type: application/json\r\n\r\n{content}"
                # Send trade request through the socket
                client_socket.send(trade_request.encode())
                # Receive trade response
                trade_response = client_socket.recv(4096)
                #Extract the json body of the response
                trade_output = decode_http_response(trade_response)
                print('trade_output',trade_output)
                print('expected_output',output_trade[i])
                assert trade_output == output_trade[i]


    print(time.perf_counter()-t1)


connect()
