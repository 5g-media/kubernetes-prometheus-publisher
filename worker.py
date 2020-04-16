"""
This module operates as the entry-point of this project.
"""

import json
import logging.config
import time
import schedule
from kafka import KafkaProducer
from kafka.errors import KafkaError
from prometheus_client.v1 import query_range
from settings import LOGGING, SCHEDULER_SECONDS, PROMETHEUS_METRICS_LIST, KAFKA_API_VERSION, \
    KAFKA_SERVER, KAFKA_KUBERNETES_TOPIC
from utils import convert_unix_timestamp_to_datetime_str, retrieve_values, \
    calculate_packet_loss_values

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("publisher")
error_logger = logging.getLogger("errors")


def main():
    """main process"""
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER,
                             api_version=KAFKA_API_VERSION,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    prom_ql = query_range.QueryRange(token=None)

    # Keep metrics for the packet loss calculation
    tx_rx_metrics = {}

    for metric in PROMETHEUS_METRICS_LIST:
        try:
            # Load the values for the requested metric for any running container
            # having the label 'vim_id'
            response = retrieve_values(prom_ql, metric['name'])
            if response.status_code != 200:
                error_logger.error("GET {} - {}".format(response.url, response.text))
                continue

            response_body = response.json()
            result_type = response_body['data'].get('resultType')
            if result_type != "matrix":
                logger.warning("The `resultType` is not the matrix. It is `{}`".format(result_type))

            # The response of the `query_range` request returns the result type (`matrix`) and
            # a list of results. Each object in results list includes one or more values of the
            # requested metric per container ID; actually, the `label_vim_id` key reflects
            # the container ID.
            for result in response_body['data'].get('result', []):
                metric_values = []
                osm_container_id = result.get('metric', {}).get('label_vim_id', None)
                # Skip process if the container is not relevant with OSM
                if osm_container_id is None:
                    continue

                # Add an empty dict for an OSM container
                if osm_container_id not in tx_rx_metrics.keys():
                    tx_rx_metrics[osm_container_id] = {}

                # Keep all the values for the requested metric by given container ID in a list.
                values_len = len(result['values'])
                if values_len:
                    latest_value = result['values'][values_len - 1]
                    metric_values.append(
                        {"timestamp": convert_unix_timestamp_to_datetime_str(latest_value[0]),
                         "unit": metric['unit'], "type": metric['type'], "name": metric['name'],
                         "value": latest_value[1]})

                    # Save temporary a set of useful metrics for the packet loss calculation
                    if metric["name"] in ["container_network_receive_packets_dropped_total",
                                          "container_network_receive_packets_total",
                                          "container_network_transmit_packets_dropped_total",
                                          "container_network_transmit_packets_total"]:
                        tx_rx_metrics[osm_container_id][metric["name"]] = latest_value[1]
                        proper_tm = convert_unix_timestamp_to_datetime_str(latest_value[0])
                        tx_rx_metrics[osm_container_id]['timestamp'] = proper_tm

                    # Push the metric values in batch per container ID
                    payload = {"container_id": osm_container_id, "type": metric['type'],
                               "data": metric_values}
                    logger.debug("Generic metrics: {}".format(payload))
                    publish_metrics(producer, payload)
        except Exception as ex:
            error_logger.exception(ex)

    # The tx_rx_metrics keeps the required metrics for the calculation of the
    # packet loss in each container. Indicative sample:
    # --------------------
    # {
    #   "bfbcd872d6b64adcbcd872d6b64adcf1": {
    #     "timestamp": "2019-04-24T07:56:34.158000Z",
    #     "container_network_receive_packets_dropped_total": "0",
    #     "container_network_transmit_packets_dropped_total": "0",
    #     "container_network_transmit_packets_total": "15.5",
    #     "container_network_receive_packets_total": "36"
    #   },
    #   "c7a07d28d38746c6a07d28d38746c630": {
    #     "timestamp": "2019-04-24T07:56:34.158000Z",
    #     "container_network_receive_packets_dropped_total": "0",
    #     "container_network_transmit_packets_dropped_total": "0",
    #     "container_network_transmit_packets_total": "16.875",
    #     "container_network_receive_packets_total": "37.25"
    #   }
    # }
    for container in tx_rx_metrics.keys():
        # Packet loss in RX
        try:
            container_network_receive_packet_loss_percentage = calculate_packet_loss_values(
                tx_rx_metrics[container].get('container_network_receive_packets_dropped_total'),
                tx_rx_metrics[container].get('container_network_receive_packets_total'))
            rx_payload = {"container_id": container,
                          "type": 'container_network_receive_packet_loss_percentage',
                          "data": [{"timestamp": tx_rx_metrics[container]["timestamp"],
                                    "unit": "%", "type": "counter",
                                    "name": "container_network_receive_packet_loss_percentage",
                                    "value": container_network_receive_packet_loss_percentage}]}
            logger.debug("rx_packet_loss: {}".format(rx_payload))
            publish_metrics(producer, rx_payload)
        except TypeError as ex:
            error_logger.error(ex)

        # Packet loss in TX
        try:
            container_network_transmit_packet_loss_percentage = calculate_packet_loss_values(
                tx_rx_metrics[container].get('container_network_transmit_packets_dropped_total'),
                tx_rx_metrics[container].get('container_network_transmit_packets_total'))
            tx_payload = {"container_id": container,
                          "type": 'container_network_transmit_packet_loss_percentage',
                          "data": [{"timestamp": tx_rx_metrics[container]["timestamp"],
                                    "unit": "%", "type": "counter",
                                    "name": "container_network_transmit_packet_loss_percentage",
                                    "value": container_network_transmit_packet_loss_percentage}]}
            logger.debug("tx_packet_loss: {}".format(tx_payload))
            publish_metrics(producer, tx_payload)
        except TypeError as ex:
            error_logger.error(ex)

    # Close producer
    producer.close()


def publish_metrics(producer, payload):
    """ Publish the payload in kafka bus

    Args:
        producer (iterator): The kafka iterator
        payload (dict): The message to be published

    Returns:
        None
    """
    request = producer.send(KAFKA_KUBERNETES_TOPIC, payload)
    try:
        request.get(timeout=3)
    except KafkaError as ex:
        error_logger.error(ex)


if __name__ == '__main__':
    # Retrieve the data every X seconds
    schedule.every(int(SCHEDULER_SECONDS)).seconds.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
