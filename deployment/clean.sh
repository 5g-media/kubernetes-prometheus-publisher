#!/bin/bash

if sudo docker ps | grep -q 'k8s-prometheus-publisher'; then
    # Gracefully stop supervisor
    sudo docker exec -i k8s-prometheus-publisher service supervisor stop && \
    sudo docker stop k8s-prometheus-publisher && \
    sudo docker rm -f k8s-prometheus-publisher
fi
