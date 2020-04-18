#!/bin/bash

mv kubernetes-prometheus-publisher/ k8s-prometheus-publisher/
find ./k8s-prometheus-publisher -type d -exec chmod -R 755 {} \;
find ./k8s-prometheus-publisher -type f -exec chmod 664 {} \;
chmod a+x ./k8s-prometheus-publisher/deployment/run.sh ./k8s-prometheus-publisher/deployment/clean.sh
cp ./k8s-prometheus-publisher/deployment/Dockerfile .
sudo docker build --no-cache -t k8s-prometheus-publisher .
source k8s-prometheus-publisher/deployment/clean.sh