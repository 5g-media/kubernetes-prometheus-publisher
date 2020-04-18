# *Kubernetes-prometheus-publisher* service

## Introduction
This service is responsible to:
- retrieve monitoring data related to the containers/pods that are running in a Kubernetes cluster using the Prometheus API,
- publish the monitoring data by given Kubernetes containers/pods in the publish/subscribe broker (Apache Kafka)

Actually, this service feeds the [MAPE](https://github.com/5g-media/mape) with monitoring data.

## Requirements
- Python 3.5+
- Docker engine
- The Apache Kafka broker must be accessible from the service
- The Prometheus API must be accessible from the service

The required python packages are depicted in the `requirements.txt` file. 

## Configuration

A variety of variables are defined in the `settings.py`  file. The configuration that is used in the deployment phase (either as `ENV` variables or via an `.env` file in case of docker-compose) includes:

| **Setting** | **Description** |
| --- | --- |
| DEBUG | Run the service on debug mode or not. By default, debug is disabled. |
| KAFKA_IP | The host of the Service Platform Virtualization publish/subscribe broker. |
| KAFKA_PORT | The port of the Service Platform Virtualization publish/subscribe broker. By default, port is 9092. |
| KAFKA_KUBERNETES_TOPIC | The publish/subscribe broker topic name where the monitoring data are published. By default, the topic name is `"nfvi.ncsrd.kubernetes"`. | 
| PROMETHEUS_HOST | The host of the Prometheus API hosted in the Kubernetes cluster. | 
| PROMETHEUS_PORT | The port of the Prometheus API hosted in the Kubernetes cluster. | 
| PROMETHEUS_POLLING_STEP | Describes the polling step in Prometheus API. Default value is `20s`. | 
| SCHEDULER_SECONDS | How frequent the publisher collects the monitoring data through the Prometheus API and publishes them in the pub/sub broker. Default value is `20` seconds. | 

## Installation/Deployment

To build the docker image, copy the bash script included in the `bash_scripts/` folder in the parent folder of the project and then, run:
```bash
    cd $HOME
    # clone repository
    cp ./kubernetes-prometheus-publisher/bash_scripts/build_docker_image.sh .
    chmod +x build_docker_image.sh
    ./build_docker_image.sh
```

Check the available docker images using:
```bash
    docker images
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
  -e PROMETHEUS_POLLING_STEP="20s" \
  -e SCHEDULER_SECONDS=20 \
  -dit k8s-prometheus-publisher
```

Check the running docker containers:
```bash
    docker ps -a
```
The name of the docker image and container is:  *k8s-prometheus-publisher*.


## Usage

After the installation/deployment of this service, it collects the
values of predefined set of metrics (as these defined in the
`settings.py` file) every `X` seconds and send them in the topic
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

Considering that the service is running as a supervisor task, you can check its status either by typing in your browser `http://{host}` and using as username/password the admin/admin, or inspecting the `supervisorctl` inside the docker container.


## Tests

The entrypoint of the service is the `worker.py` file.

Therefore, you can type the below command to test it without the usage of the docker service after the installation of the needed packages (`pip3 install -r requirements.txt`):
```bash
$ python3 daemon.py
```

## Authors
- Singular Logic <pathanasoulis@ep.singularlogic.eu>

## Acknowledgements
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement [No 761699](http://www.5gmedia.eu/). The dissemination of results herein reflects only the author’s view and the European Commission is not responsible for any use that may be made 
of the information it contains.

## License
[Apache 2.0](LICENSE.md)
