"""
Definition of the settings
"""

import os

DEBUG = int(os.environ.get("DEBUG", 0))
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

# =================================
# KAFKA SETTINGS
# =================================
KAFKA_SERVER = "{}:{}".format(os.environ.get("KAFKA_IP", "192.168.1.175"),
                              os.environ.get("KAFKA_PORT", "9092"))
KAFKA_CLIENT_ID = 'kubernetes-prometheus-publisher'
KAFKA_API_VERSION = (1, 1, 0)
KAFKA_KUBERNETES_TOPIC = os.environ.get("KAFKA_KUBERNETES_TOPIC", "nfvi.ncsrd.kubernetes")

# =================================
# PROMETHEUS SETTINGS
# =================================
PROMETHEUS = {"HOST": os.environ.get("PROMETHEUS_HOST", "10.100.176.57"),
              "PORT": os.environ.get("PROMETHEUS_PORT", 31078)}
PROMETHEUS_POLLING_STEP = os.environ.get("PROMETHEUS_POLLING_STEP", '20s')
PROMETHEUS_METRICS_LIST = [
    {"name": "container_fs_inodes_free", "type": "gauge", "unit": ""},
    {"name": "container_fs_io_current", "type": "gauge", "unit": "iops"},
    {"name": "container_fs_usage_bytes", "type": "gauge", "unit": "bytes"},
    {"name": "container_fs_writes_bytes_total", "type": "counter", "unit": "bytes"},
    {"name": "container_fs_reads_bytes_total", "type": "counter", "unit": "bytes"},
    {"name": "container_cpu_load_average_10s", "type": "gauge", "unit": "seconds"},
    {"name": "container_cpu_system_seconds_total", "type": "counter", "unit": "seconds"},
    {"name": "container_cpu_usage_seconds_total", "type": "counter", "unit": "seconds"},
    {"name": "container_cpu_cfs_throttled_seconds_total", "type": "counter", "unit": "seconds"},
    {"name": "container_memory_usage_bytes", "type": "gauge", "unit": "bytes"},
    {"name": "container_memory_working_set_bytes", "type": "gauge", "unit": "bytes"},
    {"name": "container_memory_max_usage_bytes", "type": "gauge", "unit": "bytes"},
    {"name": "container_memory_swap", "type": "gauge", "unit": "bytes"},
    {"name": "container_network_receive_bytes_total", "type": "counter", "unit": "bytes"},
    {"name": "container_network_receive_errors_total", "type": "counter", "unit": ""},
    {"name": "container_network_receive_packets_dropped_total", "type": "counter", "unit": ""},
    {"name": "container_network_receive_packets_total", "type": "counter", "unit": "packets"},
    {"name": "container_network_transmit_bytes_total", "type": "counter", "unit": "bytes"},
    {"name": "container_network_transmit_errors_total", "type": "counter", "unit": ""},
    {"name": "container_network_transmit_packets_dropped_total", "type": "counter", "unit": ""},
    {"name": "container_network_transmit_packets_total", "type": "counter", "unit": ""},
    {"name": "container_network_tcp_usage_total", "type": "gauge", "unit": ""},
    {"name": "container_network_udp_usage_total", "type": "gauge", "unit": ""},
    {"name": "container_spec_memory_reservation_limit_bytes", "type": "gauge", "unit": "bytes"},
    {"name": "container_network_receive_packet_loss_percentage", "type": "counter", "unit": "%"},
    {"name": "container_network_transmit_packet_loss_percentage", "type": "counter", "unit": "%"}
]

# =================================
# SCHEDULER SETTINGS
# =================================
SCHEDULER_SECONDS = os.environ.get("SCHEDULER_SECONDS", 20)  # seconds

# ==================================
# LOGGING SETTINGS
# ==================================
# See more: https://docs.python.org/3.5/library/logging.config.html
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': "[%(asctime)s] - [%(name)s:%(lineno)s] - [%(levelname)s] %(message)s",
        },
        'simple': {
            'class': 'logging.Formatter',
            'format': '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
        },
        'publisher': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "{}/logs/publisher.log".format(PROJECT_ROOT),
            'mode': 'w',
            'formatter': 'detailed',
            'level': 'DEBUG' if DEBUG else 'INFO',
            'maxBytes': 1024 * 1024,
            'backupCount': 5,
        },
        'errors': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "{}/logs/error.log".format(PROJECT_ROOT),
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'detailed',
            'maxBytes': 1024 * 1024,
            'backupCount': 5,
        },
    },
    'loggers': {
        'publisher': {
            'level': 'DEBUG',
            'handlers': ['publisher']
        },
        'errors': {
            'handlers': ['errors']
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
}
