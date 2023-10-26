''''
This is a test for testing the catalogServer.
GET and POST http requests are sent using the API endpoints of the catalogServer
The returned values are compared and assert is used to check if they are the same
'''
import requests
import json
import socket

# Connect to the catalogServer and send lookup and update requests
def connect():
    catalog_server_address = 'localhost'
    catalog_server_port = 8103
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((catalog_server_address, catalog_server_port))
    #create input and expected outputs for update and lookup
    stocklst =['GameStart','Hellow','FishCo']
    output_lookup = [{"data": {"name": "GameStart","price":2.2,"quantity": 100}},{"error": {"code": 404, "message": "stock not found"}},{"data": {"name": "FishCo","price":1.4,"quantity": 100}}]
    input_trade = [{"name": "GameStart","quantity": -1,"traded":1},{"name": "Mischco","quantity": -2,"traded":2},{"name": "Fishco","quantity":45,"traded":-45}]
    output_trade = [{"data": {"message":"Success"}}, {"data": {"message":"Success"}},{"data": {"message":"Success"}}]
    # Send http get requests using lookup endpoint
    for i in range(3):
        print(f'Input stock: {stocklst[i]}')
        r1 = requests.get(f"http://{catalog_server_address}:{catalog_server_port}/lookup/{stocklst[i]}")
        data = r1.json()
        print('received data :',data)
        print('expected data :', output_lookup[i])
        assert data == output_lookup[i]
    # Send http update requests using trade endpoint
    for i in range(3):
        print(f'Input trade:{input_trade[i]}')
        r1 = requests.post(f"http://{catalog_server_address}:{catalog_server_port}/trade",json = json.dumps(input_trade[i]))
        data = r1.json()
        print('received data :', data)
        print('expected data :', output_trade[i])
        assert data == output_trade[i]





connect()
