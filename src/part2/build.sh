#!/bin/bash

# Script to create docker images for all three servers using the corresponding Dockerfiles
docker build -t frontend-server-img -f frontend.Dockerfile .
docker build -t order-server-img -f order.Dockerfile .
docker build -t catalog-server-img -f catalog.Dockerfile .