# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for access Influxdb through HTTP API
"""
import logging
import traceback
import requests

class InfluxdbClient(object):
    """
    The :class:`~.InfluxDBClient` object holds information necessary to
    connect to InfluxDB. Requests can be made to InfluxDB directly through
    the client.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, host, database):
        self.ic_hostname = host
        self.ic_database = database

        self.ic_baseurl = "http://%s:8086" % (host)
        self.ic_queryurl = self.ic_baseurl + "/query"
        self.ic_headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        self.ic_session = requests.Session()

    def ic_query(self, query, epoch=None):
        """
        Send a query to InfluxDB.
        :param epoch: response timestamps to be in epoch format either 'h',
            'm', 's', 'ms', 'u', or 'ns',defaults to `None` which is
            RFC3339 UTC format with nanosecond precision
        :type epoch: str
        """
        # pylint: disable=bare-except
        params = {}
        params['q'] = query
        params['db'] = self.ic_database

        if epoch is not None:
            params['epoch'] = epoch

        logging.debug("querying [%s] to [%s]", query, self.ic_queryurl)
        try:
            response = self.ic_session.request(method='GET',
                                               url=self.ic_queryurl,
                                               params=params,
                                               headers=self.ic_headers)
        except:
            logging.error("got exception with query [%s]: %s", query,
                          traceback.format_exc())
            return None

        return response
