# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for installing ESMON
"""
# pylint: disable=too-many-lines
import sys
import logging
import traceback
import os
import shutil
import httplib
import json
import requests
import yaml
import filelock
import influxdb
import slugify

# Local libs
from pyesmon import utils
from pyesmon import ssh_host
from pyesmon import collectd

ESMON_CONFIG_FNAME = "esmon.conf"
ESMON_CONFIG = "/etc/" + ESMON_CONFIG_FNAME
ESMON_INSTALL_LOG_DIR = "/var/log/esmon_install"
INFLUXDB_CONFIG_FPATH = "/etc/influxdb/influxdb.conf"
ESMON_INFLUXDB_CONFIG_DIFF = "influxdb.conf.diff"
GRAFANA_DATASOURCE_NAME = "esmon_datasource"
INFLUXDB_DATABASE_NAME = "esmon_database"
INFLUXDB_CQ_PREFIX = "cq_"
INFLUXDB_CQ_MEASUREMENT_PREFIX = "cqm_"
GRAFANA_DASHBOARD_DIR = "dashboards"
GRAFANA_STATUS_PANEL = "Grafana_Status_panel"
GRAFANA_PLUGIN_DIR = "/var/lib/grafana/plugins"
GRAFANA_DASHBOARDS = {}
GRAFANA_DASHBOARDS["Lustre Statistics"] = "lustre_statistics.json"
GRAFANA_DASHBOARDS["Server Statistics"] = "server_statistics.json"

def grafana_dashboard_check(name, dashboard):
    """
    Check whether the dashboard is legal or not
    """
    if dashboard["id"] is not None:
        logging.error("dashabord [%s] is invalid, expected [id] to be "
                      "[null], but got [%s]",
                      name, dashboard["id"])
        return -1
    if dashboard["title"] != name:
        logging.error("dashabord [%s] is invalid, expected [title] to be "
                      "[%s], but got [%s]",
                      name, name, dashboard["title"])
        return -1
    return 0


class EsmonServer(object):
    """
    ESMON server host has an object of this type
    """
    def __init__(self, host, workspace):
        self.es_host = host
        self.es_workspace = workspace
        self.es_rpm_basename = "RPMS"
        self.es_rpm_dir = self.es_workspace + "/" + self.es_rpm_basename
        self.es_grafana_failure = False
        hostname = host.sh_hostname
        self.es_influxdb_client = influxdb.InfluxDBClient(host=hostname,
                                                          database=INFLUXDB_DATABASE_NAME)

    def es_firewall_open_ports(self):
        """
        Open necessary ports in the firewall
        """
        ret = self.es_host.sh_rpm_query("firewalld")
        if ret:
            logging.debug("firewalld is not installed on host [%s], "
                          "skipping opening ports", self.es_host.sh_hostname)
            return 0

        command = ("firewall-cmd --state")
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("firewall is already closed on host [%s], skipping "
                          "opening ports", self.es_host.sh_hostname)
            return 0

        ports = [3000, 4242, 8086, 8088, 25826]
        for port in ports:
            command = ("firewall-cmd --zone=public --add-port=%d/tcp "
                       "--permanent" % port)
            retval = self.es_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.es_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        command = ("firewall-cmd --reload")
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def es_dependent_rpms_install(self):
        """
        Install dependent RPMs
        """
        dependent_rpms = ["yajl", "openpgm", "zeromq3", "glibc", "patch",
                          "fontpackages-filesystem", "libfontenc", "libtool-ltdl",
                          "libtool", "fontconfig", "libXfont", "rsync",
                          "xorg-x11-font-utils", "urw-fonts"]
        for dependent_rpm in dependent_rpms:
            ret = self.es_host.sh_rpm_query(dependent_rpm)
            if ret:
                command = ("cd %s && rpm -ivh %s*.rpm" %
                           (self.es_rpm_dir, dependent_rpm))
                retval = self.es_host.sh_run(command)
                if retval.cr_exit_status:
                    if "already installed" not in retval.cr_stderr:
                        logging.error("failed to run command [%s] on host [%s], "
                                      "ret = [%d], stdout = [%s], stderr = [%s]",
                                      command,
                                      self.es_host.sh_hostname,
                                      retval.cr_exit_status,
                                      retval.cr_stdout,
                                      retval.cr_stderr)
                        return -1
        return 0

    def es_influxdb_uninstall(self):
        """
        uninstall influxdb
        """
        ret = self.es_host.sh_rpm_query("influxdb")
        if ret:
            return 0

        command = ("service influxdb stop")
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        command = ("service influxdb status")
        ret = self.es_host.sh_wait_update(command, expect_exit_status=3)
        if ret:
            logging.error("failed to drop database of collectd")
            return -1

        command = "rpm -e --nodeps influxdb"
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def es_influxdb_reinstall(self, erase_influxdb, drop_database):
        """
        Reinstall influxdb RPM
        """
        # pylint: disable=too-many-return-statements,too-many-statements
        # pylint: disable=too-many-branches
        ret = self.es_influxdb_uninstall()
        if ret:
            return ret

        if erase_influxdb:
            command = ('rm /var/lib/influxdb -fr')
            retval = self.es_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.es_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        command = ("cd %s && rpm -ivh influxdb-*.rpm" %
                   (self.es_rpm_dir))
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        config_diff = self.es_rpm_dir + "/" + ESMON_INFLUXDB_CONFIG_DIFF
        command = ("patch -i %s %s" % (config_diff, INFLUXDB_CONFIG_FPATH))
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        command = ("service influxdb start")
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        command = ("service influxdb status")
        ret = self.es_host.sh_wait_update(command, expect_exit_status=0)
        if ret:
            logging.error("failed to wait until influxdb starts")
            return -1

        # Somehow the restart command won't be waited until finished, so wait
        # here
        need_wait = True
        if drop_database:
            command = ('influx -execute "DROP DATABASE %s"' % INFLUXDB_DATABASE_NAME)
            ret = self.es_host.sh_wait_update(command, expect_exit_status=0)
            if ret:
                logging.error("failed to drop database of ESMON")
                return -1
            need_wait = False

        command = ('influx -execute "CREATE DATABASE %s"' % INFLUXDB_DATABASE_NAME)
        if need_wait:
            ret = self.es_host.sh_wait_update(command, expect_exit_status=0)
            if ret:
                logging.error("failed to create database of ESMON")
                return -1
        else:
            retval = self.es_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.es_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1
        return 0

    def es_grafana_url(self, api_path):
        """
        Return full Grafana URL
        """
        return ("http://admin:admin@" + self.es_host.sh_hostname + ":3000" +
                api_path)

    def es_grafana_try_connect(self, args):
        # pylint: disable=bare-except,unused-argument
        """
        Check whether we can connect to Grafana
        """
        url = self.es_grafana_url("")
        try:
            response = requests.get(url)
        except:
            logging.debug("not able to connect to [%s]: %s", url,
                          traceback.format_exc())
            return -1
        if response.status_code != httplib.OK:
            logging.debug("got grafana status [%d] when acessing grafana url "
                          "[%s]", response.status_code, url)
            self.es_grafana_failure = True
            return 0
        return 0

    def es_grafana_influxdb_add(self):
        """
        Add influxdb source to grafana
        """
        # pylint: disable=bare-except
        influxdb_url = "http://%s:8086" % self.es_host.sh_hostname
        data = {
            "name": GRAFANA_DATASOURCE_NAME,
            "isDefault": True,
            "type": "influxdb",
            "url": influxdb_url,
            "access": "proxy",
            "database": INFLUXDB_DATABASE_NAME,
            "basicAuth": False,
        }

        headers = {"Content-type": "application/json",
                   "Accept": "application/json"}

        url = self.es_grafana_url("/api/datasources")
        try:
            response = requests.post(url, json=data, headers=headers)
        except:
            logging.error("not able to create data source through [%s]: %s",
                          url, traceback.format_exc())
            return -1
        if response.status_code != httplib.OK:
            logging.error("got grafana status [%d] when creating datasource",
                          response.status_code)
            return -1
        return 0


    def es_grafana_influxdb_delete(self):
        """
        Delete influxdb source from grafana
        """
        # pylint: disable=bare-except
        headers = {"Content-type": "application/json",
                   "Accept": "application/json"}

        url = self.es_grafana_url("/api/datasources/name/%s" %
                                  GRAFANA_DATASOURCE_NAME)
        try:
            response = requests.delete(url, headers=headers)
        except:
            logging.error("not able to delete data source through [%s]: %s",
                          url, traceback.format_exc())
            return -1
        if response.status_code != httplib.OK:
            logging.error("got grafana status [%d] when deleting datasource",
                          response.status_code)
            return -1
        return 0


    def es_grafana_has_influxdb(self):
        """
        Get influxdb datasource of grafana
        Return 1 if has influxdb datasource, return 0 if not, return -1 if
        error
        """
        # pylint: disable=bare-except
        headers = {"Content-type": "application/json",
                   "Accept": "application/json"}

        url = self.es_grafana_url("/api/datasources/name/%s" %
                                  GRAFANA_DATASOURCE_NAME)
        try:
            response = requests.get(url, headers=headers)
        except:
            logging.error("not able to get data source through [%s]: %s",
                          url, traceback.format_exc())
            return -1
        if response.status_code == httplib.OK:
            return 1
        elif response.status_code == httplib.NOT_FOUND:
            return 0
        logging.error("got grafana status [%d] when get datasource of influxdb",
                      response.status_code)
        return -1

    def es_grafana_datasources(self):
        """
        Get all datasources of grafana
        """
        # pylint: disable=bare-except
        headers = {"Content-type": "application/json",
                   "Accept": "application/json"}

        url = self.es_grafana_url("/api/datasources")
        try:
            response = requests.get(url, headers=headers)
        except:
            logging.error("not able to get data sources through [%s]: %s",
                          url, traceback.format_exc())
            return -1
        if response.status_code != httplib.OK:
            logging.error("got grafana status [%d]", response.status_code)
            return -1
        return 0

    def es_grafana_dashboard_add(self, mnt_path, name, fname):
        """
        Add dashboard of grafana
        """
        # pylint: disable=bare-except
        dashboard_json_fpath = (mnt_path + "/" + GRAFANA_DASHBOARD_DIR +
                                "/" + fname)
        with open(dashboard_json_fpath) as json_file:
            dashboard = json.load(json_file)

        ret = grafana_dashboard_check(name, dashboard)
        if ret:
            return ret

        data = {
            "dashboard": dashboard,
            "overwrite": False,
        }

        headers = {"Content-type": "application/json",
                   "Accept": "application/json"}

        url = self.es_grafana_url("/api/dashboards/db")
        try:
            response = requests.post(url, json=data, headers=headers)
        except:
            logging.error("not able to add bashboard through [%s]: %s",
                          url, traceback.format_exc())
            return -1
        if response.status_code != httplib.OK:
            logging.error("got grafana status [%d] when adding dashbard [%s]",
                          response.status_code, name)
            return -1
        return 0

    def es_grafana_dashboard_delete(self, name):
        """
        Delete bashboard from grafana
        """
        # pylint: disable=bare-except
        headers = {"Content-type": "application/json",
                   "Accept": "application/json"}

        url = self.es_grafana_url("/api/dashboards/db/%s" %
                                  slugify.slugify(name))
        try:
            response = requests.delete(url, headers=headers)
        except:
            logging.error("not able to delete dashboard through [%s]: %s",
                          url, traceback.format_exc())
            return -1
        if response.status_code != httplib.OK:
            logging.error("got grafana status [%d] when deleting dashboard",
                          response.status_code)
            return -1
        return 0

    def es_grafana_has_dashboard(self, name):
        """
        Check whether grafana has dashboard
        Return 1 if has dashboard, return 0 if not, return -1 if error
        """
        # pylint: disable=bare-except
        headers = {"Content-type": "application/json",
                   "Accept": "application/json"}

        url = self.es_grafana_url("/api/dashboards/db/%s" %
                                  slugify.slugify(name))
        try:
            response = requests.get(url, headers=headers)
        except:
            logging.error("not able to get dashboard through [%s]: %s",
                          url, traceback.format_exc())
            return -1
        if response.status_code == httplib.OK:
            return 1
        elif response.status_code == httplib.NOT_FOUND:
            return 0
        logging.error("got grafana status [%d] when get dashboard",
                      response.status_code)
        return -1

    def es_grafana_change_logo(self):
        """
        Change the logo of grafana
        """
        command = ("/bin/cp -f %s/DDN-Storage-RedBG.svg "
                   "/usr/share/grafana/public/img/grafana_icon.svg" %
                   (self.es_rpm_dir))
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        command = ("/bin/cp -f %s/DDN-Storage-RedBG.png "
                   "/usr/share/grafana/public/img/fav32.png" %
                   (self.es_rpm_dir))
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def es_grafana_install_plugin(self):
        """
        Install grafana status plugin
        """
        plugin_dir = GRAFANA_PLUGIN_DIR + "/" + GRAFANA_STATUS_PANEL
        command = ("rm -fr %s" % (plugin_dir))
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        new_plugin_dir = self.es_rpm_dir + "/" + GRAFANA_STATUS_PANEL
        command = ("cp -a %s %s" % (new_plugin_dir, GRAFANA_PLUGIN_DIR))
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def es_grafana_reinstall(self, mnt_path):
        """
        Reinstall grafana RPM
        """
        # pylint: disable=too-many-return-statements,too-many-branches
        ret = self.es_host.sh_rpm_query("grafana")
        if ret == 0:
            command = "rpm -e --nodeps grafana"
            retval = self.es_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.es_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        command = ("cd %s && rpm -ivh grafana-*.rpm" %
                   (self.es_rpm_dir))
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        command = ("service grafana-server restart")
        retval = self.es_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.es_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        ret = utils.wait_condition(self.es_grafana_try_connect, [])
        if ret:
            logging.error("cannot connect to grafana")
            return ret
        if self.es_grafana_failure:
            return -1

        ret = self.es_grafana_has_influxdb()
        if ret < 0:
            return -1
        elif ret == 1:
            ret = self.es_grafana_influxdb_delete()
            if ret:
                return ret

        ret = self.es_grafana_influxdb_add()
        if ret:
            return ret

        for name, fname in GRAFANA_DASHBOARDS.iteritems():
            ret = self.es_grafana_has_dashboard(name)
            if ret < 0:
                return -1
            elif ret == 1:
                ret = self.es_grafana_dashboard_delete(name)
                if ret:
                    return ret

            ret = self.es_grafana_dashboard_add(mnt_path, name, fname)
            if ret:
                return ret

        ret = self.es_grafana_change_logo()
        if ret:
            return ret

        ret = self.es_grafana_install_plugin()
        if ret:
            return ret
        return 0

    def es_reinstall(self, erase_influxdb, drop_database, mnt_path):
        """
        Reinstall RPMs
        """

        ret = self.es_dependent_rpms_install()
        if ret:
            logging.error("failed to install dependent RPMs to server")
            return -1

        ret = self.es_firewall_open_ports()
        if ret:
            logging.error("failed to export ports of ESMON server, later"
                          "operations mght faill")
            return -1

        ret = self.es_influxdb_reinstall(erase_influxdb, drop_database)
        if ret:
            logging.error("failed to reinstall influxdb on host [%s]",
                          self.es_host.sh_hostname)
            return -1

        ret = self.es_grafana_reinstall(mnt_path)
        if ret:
            logging.error("failed to reinstall grafana on host [%s]",
                          self.es_host.sh_hostname)
            return -1
        return 0

    def es_influxdb_cq_create(self, measurement, groups, interval="1m"):
        """
        Create continuous query in influxdb
        """
        # pylint: disable=bare-except
        cq_query = INFLUXDB_CQ_PREFIX + measurement
        cq_measurement = INFLUXDB_CQ_MEASUREMENT_PREFIX + measurement
        group_string = ""
        for group in groups:
            group_string += ', "%s"' % group
        query = ('CREATE CONTINUOUS QUERY %s ON "%s"\n'
                 '  BEGIN SELECT sum("value") INTO "%s" '
                 '      FROM "%s" GROUP BY time(%s)%s\n'
                 'END;' %
                 (cq_query, INFLUXDB_DATABASE_NAME, cq_measurement,
                  measurement, interval, group_string))
        client = self.es_influxdb_client
        try:
            client.query(query)
        except:
            logging.error("failed to create continuous query with query [%s]",
                          query)
            return -1
        return 0


class EsmonClient(object):
    """
    Each client ESMON host has an object of this type
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(self, host, workspace, esmon_server, lustre_oss=False,
                 lustre_mds=False, ime=False):
        self.ec_host = host
        self.ec_workspace = workspace
        self.ec_rpm_basename = "RPMS"
        self.ec_rpm_dir = self.ec_workspace + "/" + self.ec_rpm_basename
        self.ec_esmon_server = esmon_server
        config = collectd.CollectdConfig(self)
        config.cc_configs["Interval"] = collectd.COLLECTD_INTERVAL_TEST
        if lustre_oss or lustre_mds:
            config.cc_plugin_lustre(lustre_oss=lustre_oss,
                                    lustre_mds=lustre_mds)
        if ime:
            config.cc_plugin_ime()
        self.ec_collectd_config_test = config

        config = collectd.CollectdConfig(self)
        config.cc_configs["Interval"] = collectd.COLLECTD_INTERVAL_FINAL
        if lustre_oss or lustre_mds:
            config.cc_plugin_lustre(lustre_oss=lustre_oss,
                                    lustre_mds=lustre_mds)
        if ime:
            config.cc_plugin_ime()
        self.ec_collectd_config_final = config

        self.ec_influxdb_update_time = None

    def ec_check(self):
        """
        Sanity check of the host
        """
        # The client might has problem to access ESMON server, find the problem
        # as early as possible.
        command = ("ping -c 1 %s" % self.ec_esmon_server.es_host.sh_hostname)
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def ec_dependent_rpms_install(self):
        """
        Install dependent RPMs
        """
        dependent_rpms = ["yajl", "openpgm", "zeromq3", "glibc", "patch",
                          "fontpackages-filesystem", "libfontenc", "libtool-ltdl",
                          "libtool", "fontconfig", "libXfont", "rsync",
                          "xorg-x11-font-utils", "urw-fonts",
                          "lm_sensors-libs"]
        for dependent_rpm in dependent_rpms:
            ret = self.ec_host.sh_rpm_query(dependent_rpm)
            if ret:
                command = ("cd %s && rpm -ivh %s*.rpm" %
                           (self.ec_rpm_dir, dependent_rpm))
                retval = self.ec_host.sh_run(command)
                if retval.cr_exit_status:
                    if "already installed" not in retval.cr_stderr:
                        logging.error("failed to run command [%s] on host [%s], "
                                      "ret = [%d], stdout = [%s], stderr = [%s]",
                                      command,
                                      self.ec_host.sh_hostname,
                                      retval.cr_exit_status,
                                      retval.cr_stdout,
                                      retval.cr_stderr)
                        return -1
        return 0

    def ec_rpm_uninstall(self, rpm_name):
        """
        Uninstall a RPM
        """
        command = ("rpm -qa | grep %s" % rpm_name)
        retval = self.ec_host.sh_run(command)
        uninstall = True
        if retval.cr_exit_status == 1 and retval.cr_stdout == "":
            uninstall = False
        elif retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        if uninstall:
            command = ("rpm -qa | grep %s | xargs rpm -e --nodeps" % rpm_name)
            retval = self.ec_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.ec_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1
        return 0

    def ec_rpm_reinstall(self, rpm_name):
        """
        Reinstall a RPM
        """
        ret = self.ec_rpm_uninstall(rpm_name)
        if ret:
            logging.error("failed to reinstall collectd RPM")
            return -1

        command = ("cd %s && rpm -ivh %s*.rpm" %
                   (self.ec_rpm_dir, rpm_name))
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def ec_collectd_reinstall(self):
        """
        Reinstall collectd RPM
        """
        ret = self.ec_dependent_rpms_install()
        if ret:
            logging.error("failed to install dependent RPMs")
            return -1

        ret = self.ec_rpm_uninstall("collectd")
        if ret:
            logging.error("failed to uninstall collectd RPMs")
            return -1

        ret = self.ec_collectd_install()
        if ret:
            logging.error("failed to install collectd RPMs")
            return -1

        ret = self.ec_rpm_reinstall("xml_definition")
        if ret:
            logging.error("failed to reinstall collectd RPM")
            return -1

        return 0

    def ec_collectd_install(self):
        """
        Install collectd RPM
        """
        command = ("cd %s && rpm -ivh collectd-*.rpm libcollectdclient-*.rpm" %
                   (self.ec_rpm_dir))
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    def ec_collectd_send_config(self, test_config):
        """
        Send collectd config to client
        """
        fpath = self.ec_workspace + "/"
        if test_config:
            fpath += collectd.COLLECTD_CONFIG_TEST_FNAME
            config = self.ec_collectd_config_test
        else:
            fpath += collectd.COLLECTD_CONFIG_FINAL_FNAME
            config = self.ec_collectd_config_final
        fpath += "." + self.ec_host.sh_hostname

        config.cc_dump(fpath)

        etc_path = "/etc/collectd.conf"
        ret = self.ec_host.sh_send_file(fpath, etc_path)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          fpath, etc_path,
                          self.ec_host.sh_hostname)
            return -1

        return 0

    def ec_send_rpms(self, mnt_path):
        """
        send RPMs to client
        """
        command = ("mkdir -p %s" % (self.ec_workspace))
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        ret = self.ec_host.sh_send_file(mnt_path,
                                        self.ec_workspace)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          mnt_path, self.ec_workspace,
                          self.ec_host.sh_hostname)
            return -1

        basename = os.path.basename(mnt_path)
        command = ("cd %s && mv %s %s" %
                   (self.ec_workspace, basename,
                    self.ec_rpm_basename))
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def ec_collectd_start(self):
        """
        Start collectd
        """
        command = ("service collectd start")
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def ec_collectd_stop(self):
        """
        Stop collectd
        """
        command = ("service collectd stop")
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def ec_collectd_restart(self):
        """
        Stop collectd
        """
        command = ("service collectd restart")
        retval = self.ec_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.ec_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def _ec_influxdb_measurement_check(self, args):
        # pylint: disable=bare-except,unused-argument
        """
        Check whether we can connect to Grafana
        """
        measurement_name = args[0]
        query = ('SELECT * FROM "%s" '
                 'WHERE fqdn = \'%s\' ORDER BY time DESC LIMIT 1;' %
                 (measurement_name, self.ec_host.sh_hostname))
        client = self.ec_esmon_server.es_influxdb_client
        try:
            result = client.query(query, epoch="s")
        except:
            logging.debug("got exception with query [%s]", query)
            return -1
        points = list(result.get_points())
        if len(points) != 1:
            logging.debug("got multiple points with query [%s]: %s", query,
                          points)
            return -1
        point = points[0]
        timestamp = int(point["time"])
        if self.ec_influxdb_update_time is None:
            self.ec_influxdb_update_time = timestamp
        elif timestamp > self.ec_influxdb_update_time:
            return 0
        logging.debug("timestamp [%d] is not updated with query [%s]",
                      timestamp, query)
        return -1

    def ec_influxdb_measurement_check(self, measurement_name):
        """
        Check whether influxdb has datapoint
        """
        ret = utils.wait_condition(self._ec_influxdb_measurement_check,
                                   [measurement_name])
        if ret:
            logging.error("failed to check measurement [%s]", measurement_name)
        return ret


def config_value(config, key):
    """
    Return value of a key in config
    """
    if key not in config:
        return None
    return config[key]


def esmon_do_install(workspace, config, config_fpath, mnt_path):
    """
    Start to install with the ISO mounted
    """
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches,bare-except, too-many-locals
    # pylint: disable=too-many-statements
    host_configs = config_value(config, "ssh_hosts")
    if host_configs is None:
        logging.error("can NOT find [ssh_hosts] in the config file, "
                      "please correct file [%s]", config_fpath)
        return -1

    hosts = {}
    for host_config in host_configs:
        host_id = host_config["host_id"]
        if host_id is None:
            logging.error("can NOT find [host_id] in the config of a "
                          "SSH host, please correct file [%s]",
                          config_fpath)
            return -1

        hostname = config_value(host_config, "hostname")
        if hostname is None:
            logging.error("can NOT find [hostname] in the config of SSH host "
                          "with ID [%s], please correct file [%s]",
                          host_id, config_fpath)
            return -1

        ssh_identity_file = config_value(host_config, "ssh_identity_file")

        if host_id in hosts:
            logging.error("multiple SSH hosts with the same ID [%s], please "
                          "correct file [%s]", host_id, config_fpath)
            return -1
        host = ssh_host.SSHHost(hostname, ssh_identity_file)
        hosts[host_id] = host

    server_host_config = config_value(config, "server_host")
    if hostname is None:
        logging.error("can NOT find [server_host] in the config file [%s], "
                      "please it", config_fpath)
        return -1

    host_id = config_value(server_host_config, "host_id")
    if host_id is None:
        logging.error("can NOT find [host_id] in the config of [server_host], "
                      "please correct file [%s]", config_fpath)
        return -1

    erase_influxdb = config_value(server_host_config, "erase_influxdb")
    if erase_influxdb is None:
        erase_influxdb = False
    logging.info("Influxdb will %sbe erased according to the config",
                 "" if erase_influxdb else "NOT ")

    drop_database = config_value(server_host_config, "drop_database")
    if drop_database is None:
        drop_database = False
    logging.info("database [%s] of Influxdb will %sbe dropped "
                 "according to the config", INFLUXDB_DATABASE_NAME,
                 "" if drop_database else "NOT ")

    if host_id not in hosts:
        logging.error("SSH host with ID [%s] is NOT configured in "
                      "[ssh_hosts], please correct file [%s]",
                      host_id, config_fpath)
        return -1

    host = hosts[host_id]
    esmon_server = EsmonServer(host, workspace)
    esmon_server_client = EsmonClient(host, workspace, esmon_server)
    ret = esmon_server_client.ec_check()
    if ret:
        logging.error("checking of ESMON server [%s] failed, please fix the "
                      "problem", esmon_server_client.ec_host.sh_hostname)
        return -1

    client_host_configs = config_value(config, "client_hosts")
    if client_host_configs is None:
        logging.error("can NOT find [client_hosts] in the config file, "
                      "please correct file [%s]", config_fpath)
        return -1

    esmon_clients = {}
    for client_host_config in client_host_configs:
        host_id = config_value(client_host_config, "host_id")
        if host_id is None:
            logging.error("can NOT find [host_id] in the config of a "
                          "ESMON client host, please correct file [%s]",
                          config_fpath)
            return -1

        if host_id not in hosts:
            logging.error("ESMON client with ID [%s] is NOT configured in "
                          "[ssh_hosts], please correct file [%s]",
                          host_id, config_fpath)
            return -1

        enabled_plugins = "memory, CPU, df(/), load, sensors"

        host = hosts[host_id]
        lustre_oss = config_value(client_host_config, "lustre_oss")
        if lustre_oss is None:
            lustre_oss = False
        if lustre_oss:
            enabled_plugins += ", Lustre OSS"

        lustre_mds = config_value(client_host_config, "lustre_mds")
        if lustre_mds is None:
            lustre_mds = False
        if lustre_mds:
            enabled_plugins += ", Lustre MDS"

        ime = config_value(client_host_config, "ime")
        if ime is None:
            ime = False
        if ime:
            enabled_plugins += ", DDN IME"

        logging.info("support for metrics of [%s] will be enabled on ESMON "
                     "client [%s] according to the config",
                     enabled_plugins, host.sh_hostname)

        esmon_client = EsmonClient(host, workspace, esmon_server,
                                   lustre_oss=lustre_oss,
                                   lustre_mds=lustre_mds, ime=ime)
        esmon_clients[host_id] = esmon_client
        ret = esmon_client.ec_check()
        if ret:
            logging.error("checking of ESMON client [%s] failed, please fix "
                          "the problem",
                          esmon_client.ec_host.sh_hostname)
            return -1

    ret = esmon_server_client.ec_send_rpms(mnt_path)
    if ret:
        logging.error("failed to send file [%s] on local host to "
                      "directory [%s] on host [%s]",
                      mnt_path, esmon_server_client.ec_workspace,
                      esmon_server_client.ec_host.sh_hostname)
        return -1

    ret = esmon_server.es_reinstall(erase_influxdb, drop_database, mnt_path)
    if ret:
        logging.error("failed to reinstall esmon server on host [%s]",
                      esmon_server.es_host.sh_hostname)
        return -1

    ret = esmon_server.es_influxdb_cq_create("mdt_jobstats_samples",
                                             ["job_id", "optype"])
    if ret:
        return -1

    ret = esmon_server.es_influxdb_cq_create("ost_jobstats_samples",
                                             ["job_id", "optype"])
    if ret:
        return -1

    ret = esmon_server.es_influxdb_cq_create("ost_brw_stats_rpc_bulk_samples",
                                             ["size", "field"])
    if ret:
        return -1

    ret = esmon_server.es_influxdb_cq_create("ost_stats_bytes",
                                             ["optype"])
    if ret:
        return -1

    ret = esmon_server.es_influxdb_cq_create("md_stats",
                                             ["optype"])
    if ret:
        return -1

    ret = esmon_server.es_influxdb_cq_create("mdt_acctuser_samples",
                                             ["user_id", "optype"])
    if ret:
        return -1

    ret = esmon_server.es_influxdb_cq_create("ost_acctuser_samples",
                                             ["user_id", "optype"])
    if ret:
        return -1

    ret = esmon_server.es_influxdb_cq_create("ost_kbytesinfo_used",
                                             ["user_id", "optype"],
                                             interval="10m")
    if ret:
        return -1

    for esmon_client in esmon_clients.values():
        if esmon_server.es_host.sh_hostname != esmon_client.ec_host.sh_hostname:
            ret = esmon_client.ec_send_rpms(mnt_path)
            if ret:
                logging.error("failed to send file [%s] on local host to "
                              "directory [%s] on host [%s]",
                              mnt_path, esmon_client.ec_workspace,
                              esmon_client.ec_host.sh_hostname)
                return -1

        ret = esmon_client.ec_collectd_reinstall()
        if ret:
            logging.error("failed to install esmon client on host [%s]",
                          esmon_client.ec_host.sh_hostname)
            return -1

        ret = esmon_client.ec_collectd_send_config(True)
        if ret:
            logging.error("failed to send test config to esmon client on host [%s]",
                          esmon_client.ec_host.sh_hostname)
            return -1

        ret = esmon_client.ec_collectd_start()
        if ret:
            logging.error("failed to start esmon client on host [%s]",
                          esmon_client.ec_host.sh_hostname)
            return -1

    for esmon_client in esmon_clients.values():
        ret = esmon_client.ec_collectd_config_test.cc_check()
        if ret:
            logging.error("influx doesn't have expected datapoints from host [%s]",
                          esmon_client.ec_host.sh_hostname)
            return -1

    for esmon_client in esmon_clients.values():
        ret = esmon_client.ec_collectd_send_config(False)
        if ret:
            logging.error("failed to send final config to esmon client on host [%s]",
                          esmon_client.ec_host.sh_hostname)
            return -1

        ret = esmon_client.ec_collectd_restart()
        if ret:
            logging.error("failed to start esmon client on host [%s]",
                          esmon_client.ec_host.sh_hostname)
            return -1
    return ret

def esmon_install_locked(workspace, config_fpath):
    """
    Start to install holding the confiure lock
    """
    # pylint: disable=too-many-branches,bare-except, too-many-locals
    # pylint: disable=too-many-statements
    config_fd = open(config_fpath)
    ret = 0
    try:
        config = yaml.load(config_fd)
    except:
        logging.error("not able to load [%s] as yaml file: %s", config_fpath,
                      traceback.format_exc())
        ret = -1
    config_fd.close()
    if ret:
        return -1

    iso_path = config["iso_path"]
    mnt_path = "/mnt/" + utils.random_word(8)

    local_host = ssh_host.SSHHost("localhost", local=True)
    command = ("mkdir -p %s && mount -o loop %s %s" %
               (mnt_path, iso_path, mnt_path))
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      local_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    try:
        ret = esmon_do_install(workspace, config, config_fpath, mnt_path)
    except:
        ret = -1
        logging.error("exception: %s", traceback.format_exc())

    command = ("umount %s" % (mnt_path))
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      local_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        ret = -1

    command = ("rmdir %s" % (mnt_path))
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      local_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1
    return ret


def esmon_install(workspace, config_fpath):
    """
    Start to install
    """
    # pylint: disable=bare-except
    lock_file = config_fpath + ".lock"
    lock = filelock.FileLock(lock_file)
    try:
        with lock.acquire(timeout=0):
            try:
                ret = esmon_install_locked(workspace, config_fpath)
            except:
                ret = -1
                logging.error("exception: %s", traceback.format_exc())
            lock.release()
    except filelock.Timeout:
        ret = -1
        logging.error("someone else is holding lock of file [%s], aborting "
                      "to prevent conflicts", lock_file)
    return ret


def usage():
    """
    Print usage string
    """
    utils.eprint("Usage: %s <config_file>" %
                 sys.argv[0])


def main():
    """
    Install Exascaler monitoring
    """
    # pylint: disable=unused-variable
    reload(sys)
    sys.setdefaultencoding("utf-8")
    config_fpath = ESMON_CONFIG

    if len(sys.argv) == 2:
        config_fpath = sys.argv[1]
    elif len(sys.argv) > 2:
        usage()
        sys.exit(-1)

    identity = utils.local_strftime(utils.utcnow(), "%Y-%m-%d-%H_%M_%S")
    workspace = ESMON_INSTALL_LOG_DIR + "/" + identity

    if not os.path.exists(ESMON_INSTALL_LOG_DIR):
        os.mkdir(ESMON_INSTALL_LOG_DIR)
    elif not os.path.isdir(ESMON_INSTALL_LOG_DIR):
        logging.error("[%s] is not a directory", ESMON_INSTALL_LOG_DIR)
        sys.exit(-1)

    if not os.path.exists(workspace):
        os.mkdir(workspace)
    elif not os.path.isdir(workspace):
        logging.error("[%s] is not a directory", workspace)
        sys.exit(-1)

    print("Started installing Exascaler monitoring system using config [%s], "
          "please check [%s] for more log" %
          (config_fpath, workspace))
    utils.configure_logging(workspace)

    save_fpath = workspace + "/" + ESMON_CONFIG_FNAME
    logging.debug("copying config file from [%s] to [%s]", config_fpath,
                  save_fpath)
    shutil.copyfile(config_fpath, save_fpath)
    ret = esmon_install(workspace, config_fpath)
    if ret:
        logging.error("installation failed, please check [%s] for more log\n",
                      workspace)
        sys.exit(ret)
    logging.info("Exascaler monistoring system is installed, please check [%s] "
                 "for more log", workspace)
    sys.exit(0)
