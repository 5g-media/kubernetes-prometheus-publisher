FROM ubuntu:16.04
MAINTAINER Athanasoulis Panagiotis
LABEL version="1.0"

ENV DEBUG=$DEBUG
ENV KAFKA_IP=$KAFKA_IP
ENV KAFKA_PORT=$KAFKA_PORT
ENV KAFKA_KUBERNETES_TOPIC=$KAFKA_KUBERNETES_TOPIC
ENV PROMETHEUS_HOST=$PROMETHEUS_HOST
ENV PROMETHEUS_PORT=$PROMETHEUS_PORT
ENV PROMETHEUS_POLLING_STEP=$PROMETHEUS_POLLING_STEP
ENV SCHEDULER_SECONDS=$SCHEDULER_SECONDS

RUN pwd
RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get -y install python3-dev python3-setuptools python3-pip supervisor vim \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/k8s-prometheus-publisher

COPY k8s-prometheus-publisher /opt/k8s-prometheus-publisher
RUN ls -la /opt/k8s-prometheus-publisher

RUN pip3 install -r /opt/k8s-prometheus-publisher/requirements.txt \
 && cp /opt/k8s-prometheus-publisher/deployment/k8s-prometheus-publisher.conf /etc/supervisor/conf.d/k8s-prometheus-publisher.conf \
 && rm -rf /etc/supervisor/supervisord.conf \
 && cp /opt/k8s-prometheus-publisher/deployment/supervisor/supervisord.conf /etc/supervisor/supervisord.conf \
 && chmod +x /opt/k8s-prometheus-publisher/deployment/run.sh

EXPOSE 3333

ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/opt/k8s-prometheus-publisher/deployment/run.sh"]
