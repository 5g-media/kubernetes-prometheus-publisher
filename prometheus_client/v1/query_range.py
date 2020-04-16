"""
Module that implements the QueryRange requests in Prometheus API
"""

import logging.config

import urllib3

from httpclient.client import Client
from settings import PROMETHEUS, LOGGING

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger("publisher")


class QueryRange(object):
    """QueryRange Class.

    Attributes:
        bearer_token (str, optional): The Prometheus Authorization Token (if any)

    Methods:
        get(query, from_time, to_time, step): perform a query_range request in Prometheus API
    """

    def __init__(self, token=None):
        """Class Constructor."""
        self.__client = Client(verify_ssl_cert=False)
        self.bearer_token = token

    def get(self, query, from_time, to_time, step=14):
        """ Perform a query_range request in Prometheus API (PromQL)

        Args:
            query (str): The query
            from_time (str): The start datetime
            to_time (str): The end datetime
            step (int): The used step in the query. Default value is 14 secs.

        Returns:
            object: A list of NSs as a requests object
        """
        endpoint = 'http://{}:{}/api/v1/query_range'.format(PROMETHEUS.get('HOST'),
                                                            PROMETHEUS.get('PORT'))
        headers = {"Accept": "application/json"}
        endpoint += "?query={}&start={}&end={}&step={}".format(query, from_time, to_time, step)
        logger.debug("Prometheus web service: {}".format(endpoint))
        response = self.__client.get(url=endpoint, headers=headers)
        return response
