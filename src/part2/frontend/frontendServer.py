import socket
import requests
from concurrent.futures import ThreadPoolExecutor
import json
'''
Output format:
GET request: success: {
    "data": {
        "name": "GameStart",
        "price": 15.99,
        "quantity": 100
    }
}
error:
{
    "error": {
        "code": 404,
        "message": "stock not found"
    }
}

POST request:
input:
{
    "name": "GameStart",
    "quantity": 1,
    "type": "sell"
}
output:
{
    "data": {
        "transaction_number": 10
    }
}
error:
{
    "error": {
        "code": 403,
        "message": "Not enough stock"
    }
}

{
    "error": {
        "code": 404,
        "message": "stock not found"
    }
}

'''

# Custom handler for client requests
class clientHandler:

    def __init__(self, address, sock):
        self.address = address
        self.sock = sock
        self.start()

    # Takes http requests from a single client till the client closes the connection
    def start(self):
        while True:
            request = self.sock.recv(1024).decode()
            if not request:
                break
            # Sends the request for further processing.
            response = self.processRequest(request)
            self.sock.sendall(response.encode('utf-8'))
        self.sock.close()

    # Generates a http response with the received response from OrderService or CatalogService
    def generateResponse(self, response):
        body = json.dumps(response)
        response = 'HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}'.format(len(body), body)
        return response

    # Splits the request to see if it is a GET or POST request and accordingly call Catalog or Order server
    def processRequest(self, request):
        req = request.split('\r\n')
        # Extracting the method and API endpoint
        method, endpoint, _ = req[0].split(" ")

        if method == 'GET':
            # Pick the stockname and call CatalogService with the stockname
            stockname = endpoint.split('/')[2]
            response = self.CatalogService(stockname)
            return self.generateResponse(response)

        else:
            '''
            Extracting the start of the body for POST request.Look for the empty string in the dictionary first
            and pick the next index which contains the json body of the request.
            '''

            ind = req.index('')
            orderdict = json.loads(req[ind + 1])
            response = self.OrderService(orderdict)
            return self.generateResponse(response)

    # Function which communicates with OrderServer using HTTP Rest API
    def OrderService(self, orderdict):
        # Creates a http post request for communicating with OrderServer
        order_server_address = 'orderserver'
        order_server_port = 8061
        # Sends a trade request using the exposed API endpoint
        response = requests.post(f"http://{order_server_address}:{order_server_port}/trade", json=orderdict)
        return response.json()

    # Function which communicates with catalogServer using HTTP Rest API
    def CatalogService(self, stockname):
        # Creates a http request for communicating with the CatalogServer
        catalog_server_address = 'catalogserver'
        catalog_server_port = 8103
        # Sends a lookup request using the exposed function by the catalogServer which takes as input the stock name
        response = requests.get(f"http://{catalog_server_address}:{catalog_server_port}/lookup/{stockname}")
        return response.json()


# The class implements functionality of a server which works using a thread per session model
class Httpserver:
    def __init__(self, host, port, pool_size):
        self.host = host
        self.port = port
        self.pool = ThreadPoolExecutor(pool_size)

    # Opens a socket connection and listens to the port and submits the connection to the threadpool
    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f'Listening at port {self.port}')
        while True:
            client_socket, client_address = server_socket.accept()
            self.pool.submit(clientHandler, client_address, client_socket)


if __name__ == '__main__':
    host = 'frontendserver'
    port = 6255
    pool_size = 10
    Httpserver(host, port, pool_size).run()

