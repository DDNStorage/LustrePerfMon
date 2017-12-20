# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for access Influxdb through HTTP API
"""
import logging
import traceback
import sys
import httplib
import requests

from pyesmon import time_util
from pyesmon import utils


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


def esmon_influxdb_query(influx_server, influx_database,
                         query_string):
    """
    Query influxdb server
    """
    client = InfluxdbClient(influx_server, influx_database)
    response = client.ic_query(query_string, epoch="s")
    if response is None:
        logging.debug("failed to query influxdb [%s] on server [%s] with query [%s] ",
                      influx_database, influx_server, query_string)
        return -1

    if response.status_code != httplib.OK:
        logging.debug("got InfluxDB status [%d]", response.status_code)
        return -1

    print response.json()
    return 0


def usage():
    """
    Print usage string
    """
    utils.eprint("Usage: %s influx_server influx_databse query_string" %
                 sys.argv[0])


def main():
    """
    Test Exascaler monitoring
    """
    reload(sys)
    sys.setdefaultencoding("utf-8")

    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)
    influx_server = sys.argv[1]
    influx_database = sys.argv[2]
    query_string = sys.argv[3]

    identity = time_util.local_strftime(time_util.utcnow(), "%Y-%m-%d-%H_%M_%S")

    print("Querying influxdb [%s] on server [%s] with query [%s] " %
          (influx_database, influx_server, query_string))
    utils.configure_logging()

    console_handler = utils.LOGGING_HANLDERS["console"]
    console_handler.setLevel(logging.DEBUG)

    ret = esmon_influxdb_query(influx_server, influx_database,
                               query_string)
    if ret:
        logging.error("Influxdb query failed")
        sys.exit(ret)
    sys.exit(0)
