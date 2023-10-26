import socket
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import threading
import time
import csv
'''
- Implemented a catalogservice class which initially loads data from the file,defines lookup and trade functions
and also periodically backs up data to the file
- Used HTTP server which uses an inbuilt threadpool to submit incoming requests.
- Implemented http request handler which takes get and post requests from the server and forwards them to the appropriate functions 
in catalog service class.
- The threaded server sends response to the frontendServer or OrderServer depending on where the request came from.
'''

stock_path = 'backend/files/stockCatalog.csv'
class stockValues:
    def __init__(self, quantity,volume,price):
        self.quantity = quantity
        self.volume = volume
        self.price = price

# Added locks for stock catalog and for writing to csv
cataloglock = threading.Lock()
orderlock = threading.Lock()

class catalogService:

    def __init__(self):
        self.catalog = dict()
        self.load()
        #Separate thread to back data periodically
        th = threading.Thread(target=self.backup_data)
        th.start()

    # Backs data to the file periodically
    def backup_data(self):
        while True:
            time.sleep(3)
            # Lock to access the catalog and update the csv file
            with cataloglock:
                lst =[]
                lst.append(['Stockname','Quantity','Volume_traded','Price'])
                for name in self.catalog:
                    lst.append([name,self.catalog[name].quantity,self.catalog[name].volume,self.catalog[name].price])
                with orderlock:
                    with open(stock_path, 'w') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerows(lst)


    # Loads data from the file at startup and saves it in a dictionary
    def load(self):
            f = open(stock_path, 'r')
            next(f)
            for line in f:
                name, values = line.split(",")[0], line.split(",")[1:]
                self.catalog[name] = stockValues(int(values[0]),int(values[1]),float(values[2].strip()))
            print('Succesfully loaded data')

    # The function looks up for the stock from stock_catalog and returns the stockname ,price and quantity

    def lookup(self, stockname):
        # Apply catalog lock to access the catalog
        with cataloglock:
            # stock does not exist
            if stockname not in self.catalog:
                res = {"error": {"code": 404, "message": "stock not found"}}
                return res
            # retrieve stock from the catalog
            quantity,price = self.catalog[stockname].quantity, self.catalog[stockname].price
            res = {"data": {"name": stockname, "price": price, "quantity": quantity}}
            return res

    # The function changes the stock volume depending on a buy or sell transaction and returns an output in the form of a dictionary

    def trade(self, values_dict):
        stockname = values_dict['name']
        qty = values_dict['quantity']
        traded_vol = values_dict['traded']
       #Update stock quantity and volume
        with cataloglock:
                self.catalog[stockname].quantity += qty
                self.catalog[stockname].volume += traded_vol
                res = {"data": {"message":"Success"}}
                return res

# A custom request handler which inherits from the BaseHTTPRequestHandler
class CatalogRequestHandler(BaseHTTPRequestHandler):
    #Overrides do_GET and do_POST functions to call lookup and trade respectively
    def do_GET(self):
        # Extracts the method name and calls the lookup function
        params = self.path.split('/')[1:]
        #If the endpoint is correct
        if self.path.startswith('/lookup'):
            response = catalogobj.lookup(params[1])
            if 'error' in response:
                self.send_response(response['error']['code'])
            else:
                self.send_response(200)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        #If the endpoint is wrong send an error message
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": {"code": 408, "message": 'Wrong endpoint'}}).encode('utf-8'))

    # Modifies the stock and returns output as a json object

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
         # Extracts the method name and calls the trade function
        params = json.loads(body.decode('utf-8'))
        if self.path.startswith('/update'):
            response = catalogobj.trade(json.loads(params))
            # Sends back response code depending on whether an error or success
            if 'error' in response:
                self.send_response(response['error']['code'])
            else:
                self.send_response(200)

            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
          #If the endpoint is wrong send an error message
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": {"code": 408, "message": 'Wrong endpoint'}}).encode('utf-8'))


if __name__ == '__main__':
    #   An object of catalogService is created
    catalogobj = catalogService()
    #   Server address and port number for catalogserver
    host = socket.gethostname()
    port = 8103
    server_address =(f"{host}",port)
    print(f'Catlog server listening on port {port}')
    # Create an object of http server
    httpobj = HTTPServer(server_address,CatalogRequestHandler)
    httpobj.serve_forever()



