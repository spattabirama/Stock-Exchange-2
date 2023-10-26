from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import requests
import json
import csv

'''
- Implemented a order service class which sends request and updates to catalog server, and exports the transaction details to a csv
- Implemented a HTTP server to submit incoming requests and inherits from the BaseHTTPServer
- Implemented http request handler which takes get and post requests from the server and forwards them to the appropriate functions 
in catalog service class.
- The threaded server sends response to the frontendServer
'''

order_path = '/app/data/ordercatalog.csv'

# Creates locks for synchronization
transactionlock = threading.Lock()
writelock = threading.Lock()


class orderService:
    # self.count is the transaction number which is incremented whenever a transaction is successful
    def __init__(self):
        self.catalog = dict()
        self.count = 0


    # Sends a lookup request to catalog server, update request to catalog server, updates ordercatalog.csv, and returns response to the front end
    def trade(self, new_order):
        catalog_server_address = 'catalogserver'
        catalog_server_port = 8103

        # Extract the stock name and generate a get request
        stockname = new_order['name']
        response_get = requests.get(f"http://{catalog_server_address}:{catalog_server_port}/lookup/{stockname}")
        lookup_dict = response_get.json()

        # Condition to handle unavailability of a stock
        if 'error' in lookup_dict:
            return lookup_dict

        # Extract the leftover quantity for the given stock
        available_qty = lookup_dict['data']['quantity']
        # Pick the quantity and type of transaction from the input order
        quantity = new_order['quantity']
        type = new_order['type']

        # The quantity to reduce or increase
        reduced_quantity = quantity
        if type == 'buy':
                # Checks if the current volume is greater than the given quantity
                if available_qty >= quantity:
                    # Passing actual value to the catalog server
                    reduced_quantity = -quantity
                else:
                    return {"error": {"code": 403, "message": 'Not enough stock'}}

        # Generate a post request to be sent to the catalog server
        update_order = json.dumps({'name':stockname,'quantity':reduced_quantity,'traded':quantity})
        requests.post(f"http://{catalog_server_address}:{catalog_server_port}/trade",json=update_order)

        # Update transaction number write to csv
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


# A custom request handler which inherits from the BaseHTTPRequestHandler
# Overrides do_POST method for handling requests
class OrderRequestHandler(BaseHTTPRequestHandler):
    # Modifies the stock and return output as a json object
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        params = json.loads(body.decode('utf-8'))

        if self.path.startswith('/trade'):
            response = orderobj.trade(params)
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))



if __name__ == '__main__':
    # An object of orderService is created
    orderobj = orderService()
    # Server address and port number for orderserver
    host = 'orderserver'
    port = 8061
    server_address = (f"{host}", port)
    print(f'Order server up on port {port}')
    # Creates an object for the custom server
    httpobj = HTTPServer(server_address, OrderRequestHandler)
    httpobj.serve_forever()

