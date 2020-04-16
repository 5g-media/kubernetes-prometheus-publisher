"""
A module that includes a set of utilities.
"""

from datetime import datetime, timedelta
import urllib.parse
from dateutil import tz
from settings import PROMETHEUS_METRICS_LIST, SCHEDULER_SECONDS, PROMETHEUS_POLLING_STEP


def convert_unix_timestamp_to_datetime_str(unix_ts):
    """ Convert a unix timestamp in stringify datetime (UTC)

    Args:
        unix_ts (int): The timestamp in unix

    Returns:
        str: The datetime in str (UTC)

    Example:
        >>> from datetime import datetime
        >>> from utils import convert_unix_timestamp_to_datetime_str
        >>> unix_ts = 1527165350
        >>> dt_str = convert_unix_timestamp_to_datetime_str(unix_ts)
        >>> print(dt_str)
        2018-05-24T12:35:50.000000Z
    """
    timestamp = datetime.utcfromtimestamp(unix_ts)
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def convert_utc_timestamp_in_timezone(utc_timestamp, timezone="GMT"):
    """Convert the UTC timestamp to timezone by given new timezone.

        Args:
            utc_timestamp (object): A utc = datetime.utcnow() object
            timezone (str): A timezone i.e. Europe/Athens

        Returns:
            str: the timestamp in the given timezone considering the UTC timestamp
    """
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(timezone)
    utc = utc_timestamp.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def apply_function_per_metric(metric_type):
    """ Select the proper function the applied in the web service that retrieves the values per pod.

    Args:
        metric_type (str): The type of the metric

    Returns:
        str: the name of the function
    """
    net_metrics = ["container_network_receive_bytes_total",
                   "container_network_receive_errors_total",
                   "container_network_receive_packets_dropped_total",
                   "container_network_receive_packets_total",
                   "container_network_transmit_bytes_total",
                   "container_network_transmit_errors_total",
                   "container_network_transmit_packets_dropped_total",
                   "container_network_transmit_packets_total", ]

    computational_metrics = ["container_cpu_usage_seconds_total",
                             "container_cpu_user_seconds_total",
                             "container_cpu_system_seconds_total ",
                             "container_cpu_cfs_throttled_seconds_total",
                             "container_fs_writes_bytes_total",
                             "container_fs_reads_bytes_total", ]

    if metric_type in net_metrics or metric_type in computational_metrics:
        return "rate"
    return "avg_over_time"


def retrieve_values(query, metric):
    """ Retrieve the values by given metric

    Args:
        query (object): The QueryRange object
        metric (str): The name of the metric

    Returns:
        object: a requests object
    """
    utc_now = datetime.utcnow()

    query = """sum(
      max(kube_pod_labels{label_ow_action!=""}) by (label_ow_action, pod, label_vim_id)
      *
      on(pod)
      group_right(label_ow_action, label_vim_id)
      label_replace(
        sum by (pod_name) (%(metric_function)s(%(metric_name)s{namespace="%(namespace)s"}[1m])), 
        "pod", 
        "$1", 
        "pod_name", 
        "(.+)"
      )
    ) by (pod, label_ow_action, label_vim_id)""" \
            % {"metric_function": apply_function_per_metric(metric), "metric_name": metric,
               "namespace": "default"}

    url_query = urllib.parse.quote(query)
    from_dt = utc_now - timedelta(seconds=int(SCHEDULER_SECONDS))
    from_time = from_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    to_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return query.get(url_query, from_time=from_time, to_time=to_time, step=PROMETHEUS_POLLING_STEP)


def calculate_packet_loss_values(dropped_packets_rate, total_packets_rate):
    """ Calculate the packet loss (percentage)

    Args:
        dropped_packets_rate (float): The rate of dropped packets (packets/sec)
        total_packets_rate (float): The rate of total packets (packets/sec)

    Returns:
        float: The packet loss. Value range: [0 - 100]. Unit is %.
    """
    if float(total_packets_rate) == 0.0:
        return 0.0
    return float(dropped_packets_rate) * 100 / float(total_packets_rate)


def get_unit_by_metric(metric):
    """ Get the unit by given metric

    Args:
        metric (str): The metric name

    Returns:
        str: the unit
    """
    for item in PROMETHEUS_METRICS_LIST:
        if item['name'] == metric:
            return item['unit']
    return ""


def get_type_by_metric(metric):
    """ Get the type by given metric

    Args:
        metric (str): The metric name

    Returns:
        str: the metric's type
    """
    for item in PROMETHEUS_METRICS_LIST:
        if item['name'] == metric:
            return item['type']
    return ""
