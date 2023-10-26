
import requests
import socket
'''
This is a test for testing the orderServer.
POST http requests are sent using the API endpoints of the orderServer
The returned values are compared and assert is used to check if they are the same
'''
# Connect to the order server and send trade requests
def connect():
    order_server_address = 'localhost'
    order_server_port = 8061
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((order_server_address, order_server_port))
    input_trade = [{"name": "GameStart","quantity": 2,"type":'sell'},{"name": "MehirCo","quantity": 123,"type":'buy'},{"name": "FishCo","quantity":45,"type":'sell'},{"name": "Hellow","quantity": 2,"type":'sell'}]
    output_trade = [{"data": {"transaction_number": 1}}, {"error": {"code": 403, "message": 'Not enough stock'}},{"data": {"transaction_number": 2}},{"error": {"code": 404, "message": "stock not found"}}]

    #Trade requests are sent by using values from input_trade and the output is compared with expected output_trade
    for i in range(4):
        print(f'Input trade : {input_trade[i]}')
        r1 = requests.post(f"http://{order_server_address}:{order_server_port}/trade",json = input_trade[i])
        data = r1.json()
        print('received_output',data)
        print('expected_output',output_trade[i])
        assert data == output_trade[i]



connect()
