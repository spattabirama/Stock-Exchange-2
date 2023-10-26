# Part 1 #

Root folder: part1

## catalog service 
Service to lookup the stockCatalog.csv for stock name and return the response. Also handle the lookup and update requests from the Order service to modify the stockCatalog.csv

Run the catalog server from root folder : python3 backend/catalogServer.py

## order service
Service used to trade stocks and update trades in ordercatalog.csv. 

Run the order server from root folder : python3 backend/OrderServer.py
 
## Frontend Service
The clients will communicate with the front-end service using HTTP based REST APIs. It will forward the requests to order or catalog server based on the type of request from the client.

Type of HTTP requests used.
1.GET /stocks/<stock_name>
2.POST /orders

Run the frontend server from root folder : python3 frontend/server.py

## Client
Once all servers are up and running, execute the client :
The client will randomly select a stock to lookup to the front end server. Based on the quantity, if quantity>0, the client will randomly choose to send another trade request to the frontend based on a probability.

Run the client application from root folder: python3 client/client.py

# Part 2 #

Root folder: part2

The Dockerfiles of all the services are present in the root folder along with the docker compose file and shell script to build the images.

# runninng the shell script to create the images of dockerfiles #

1. Run the script using "bash build.sh" in the same folder as the dockerfiles located

# docker-compose.yml file to bring up and down the services #

1. We can bring up (or tear down) all three microservices using 'docker-compose up'
2. stop the services using 'docker compose down'