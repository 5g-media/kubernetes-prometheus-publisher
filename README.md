# *Kubernetes-prometheus-publisher* service

## Introduction
This service is responsible to:
- retrieve monitoring data related to a Kubernetes cluster using the Prometheus API,
- publish the monitoring data by given k8s container in the pub/sub broker (Apache Kafka)

Actually, this service feeds the [MAPE](https://github.com/5g-media/mape) with monitoring data.

## Requirements
- Python vrs 3.5+
- The Apache Kafka (vrs 1.1.0) broker must be accessible from the service
- The Prometheus API (vrs 2.2.1) must be accessible from the service

## Configuration
Check the `settings.py` file:
 - *KAFKA_SERVER*: defines the kafka bus *host* and *port*.
 - *KAFKA_CLIENT_ID*: The default value is 'kubernetes-prometheus-publisher'.
 - *KAFKA_KUBERNETES_TOPIC*: defines the topic in which you want to send the messages. The default topic name is `nfvi.ncsrd.kubernetes`.
 - *PROMETHEUS*: defines the host port of the Prometheus service as a dict.
 - *PROMETHEUS_POLLING_STEP*: defines the polling step in Prometheus API. Default value is '30s'.
 - *PROMETHEUS_METRICS_LIST*: defines the list of metrics that we are interested in
 - *SCHEDULER_SECONDS*: defines how frequent the publisher is running to collect the values of the metrics. Default value is 30 seconds.
 - LOGGING: declares the logging (files, paths, backups, max length)

## Installation/Deployment

To build the docker image, copy the bash script included in the `bash_scripts/` folder in the parent folder of the project and then, run:
```bash
   chmod +x build_docker_image.sh
   ./build_docker_image.sh
```

Considering the docker image is available, you can deploy the service as a docker container using the below command:
```bash
$ sudo docker run -p 80:3333 --name k8s-prometheus-publisher --restart always \
  -e DEBUG=1 \
  -e KAFKA_IP="192.168.1.175" \
  -e KAFKA_PORT="9092" \
  -e KAFKA_KUBERNETES_TOPIC="nfvi.ncsrd2.kubernetes" \
  -e PROMETHEUS_HOST="192.168.1.107" \
  -e PROMETHEUS_PORT="31078" \
  -e PROMETHEUS_POLLING_STEP="45s" \
  -e SCHEDULER_SECONDS=30 \
  -dit k8s-prometheus-publisher
$ rm Dockerfile
```
The name of the docker image and container is:  *k8s-prometheus-publisher*.


## Usage
After the installation/deployment of this service, it collects the
values of predefined set of metrics (as these defined in the
`settings.py` file) every `X` minutes and send them in the topic
`nfvi.ncsrd.kubernetes`.

An indicative structure of each message is:
```json
{
    "container_id": "959a1de912ce454a9a1de912ce654ae9",
    "metric_type": "container_cpu_system_seconds_total",
    "data": [
        {
            "type": "counter",
            "name": "container_cpu_system_seconds_total",
            "timestamp": "2019-02-13T10:14:32.897000Z",
            "unit": "seconds",
            "value": "0.21000000000000016"
        },
        {
            "type": "counter",
            "name": "container_cpu_system_seconds_total",
            "timestamp": "2019-02-13T10:15:02.897000Z",
            "unit": "seconds",
            "value": "0.21000000000000016"
        },
        {
            "type": "counter",
            "name": "container_cpu_system_seconds_total",
            "timestamp": "2019-02-13T10:15:32.897000Z",
            "unit": "seconds",
            "value": "0.21000000000000016"
        }
    ]
}
```


## Tests

The entrypoint of the service is the `worker.py` file.

Therefore, you can type the below command to test it without the usage of the docker service after the installation of the needed packages (`pip3 install -r requirements.txt`):
```bash
$ python3 daemon.py
```

## Authors
- Singular Logic

## Acknowledgements
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement *No 761699*. The dissemination of results herein reflects only the author’s view and the European Commission is not responsible for any use that may be made 
of the information it contains.

## License
[Apache 2.0](LICENSE.md)
