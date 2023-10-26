import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
import csv

# Initial order path and locks
order_path = 'backend/files/ordercatalog.csv'
transactionlock = threading.Lock()
writelock = threading.Lock()

class orderService:

    # self.count is the transaction number which is incremented whenever a transaction is successful
    #The count is assigned to 0 before the server starts
    def __init__(self):
        self.count = 0

    # Sends a lookup request to catalog server,update request to catalog server,updates ordercatalog.csv and returns response to the front end

    def trade(self, new_order):
        catalog_server_address = socket.gethostname()
        catalog_server_port = 8103
        # Extract the stock name and generate a get request
        stockname = new_order['name']
        response_get = requests.get(f"http://{catalog_server_address}:{catalog_server_port}/lookup/{stockname}")
        lookup_dict = response_get.json()
        # If the stock doesn't exist send the error message
        if 'error' in lookup_dict:
            return lookup_dict
        # Extract the leftover quantity for the given stock
        available_qty = lookup_dict['data']['quantity']
        # Pick the quantity and type of transaction from the input order
        quantity = new_order['quantity']
        type = new_order['type']
        # The quantity to reduce or increase depending on buy or sell request
        reduced_quantity = quantity
        if type == 'buy':
                # Checks if the current volume is greater than the given quantity
                if available_qty >= quantity:
                    # Updating the reduced quantity to pass to the catalog server
                    reduced_quantity = -quantity
                else:
                    return {"error": {"code": 403, "message": 'Not enough stock'}}
        # Generate a post request to be sent to the catalog server
        update_order = json.dumps({'name':stockname,'quantity':reduced_quantity,'traded':quantity})
        res = requests.post(f"http://{catalog_server_address}:{catalog_server_port}/update",json=update_order)
        update_res = res.json()
        # If the update was successful
        if update_res['data']['message'] == 'Success':
            # Apply transaction lock and increment transaction number and write to csv
            with transactionlock:
                self.count += 1
                # Write the updated row into the csv
                row = [self.count, new_order['name'], new_order['quantity'], new_order['type']]
                with writelock:
                    with open(order_path, 'a') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(row)
                reply = {"data": {"transaction_number": self.count}}
                return reply
        else:
            return {"error": {"code": 405, "message": "Unknown error,retry"}}

# This class inherits from BaseHTTPRequestHandler and overrides do_POST method for handling requests
class OrderRequestHandler(BaseHTTPRequestHandler):

    # Modifies the stock and return output as a json object
    def do_POST(self):

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        params = json.loads(body.decode('utf-8'))
        # Extract the API endpoint and call trade() function
        if self.path.startswith('/trade'):
            response = orderobj.trade(params)
            # Sends the error code depending on whether there is an error message or not
            if 'error' in response:
                self.send_response(response['error']['code'])
            else:
                self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    # Create an object of orderService()
    orderobj = orderService()
    # Bind the host to the port
    host = socket.gethostname()
    port = 8061
    server_address = (f"{host}", port)
    print(f'Order server up on port {port}')
    # Create an object of HTTPServer class
    httpobj = HTTPServer(server_address, OrderRequestHandler)
    httpobj.serve_forever()

