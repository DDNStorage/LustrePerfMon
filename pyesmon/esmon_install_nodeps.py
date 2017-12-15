# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for installing ESMON, assuming all python library is installed
"""
# pylint: disable=too-many-lines
import sys
import logging
import traceback
import os
import shutil
import httplib
import re
import json

# Local libs
from pyesmon import utils
from pyesmon import time_util
from pyesmon import ssh_host
from pyesmon import collectd
from pyesmon import esmon_common
from pyesmon import esmon_influxdb
from pyesmon import esmon_install_common
import requests
import yaml
import filelock
import slugify


ESMON_INSTALL_CONFIG = "/etc/" + esmon_common.ESMON_INSTALL_CONFIG_FNAME
ESMON_INSTALL_LOG_DIR = "/var/log/esmon_install"
INFLUXDB_CONFIG_FPATH = "/etc/influxdb/influxdb.conf"
INFLUXDB_CONFIG_DIFF = "influxdb.conf.diff"
GRAFANA_DATASOURCE_NAME = "esmon_datasource"
INFLUXDB_DATABASE_NAME = "esmon_database"
INFLUXDB_CQ_PREFIX = "cq_"
INFLUXDB_CQ_MEASUREMENT_PREFIX = "cqm_"
GRAFANA_DASHBOARD_DIR = "dashboards"
GRAFANA_PLUGIN_DIR = "/var/lib/grafana/plugins"
GRAFANA_DASHBOARDS = {}
GRAFANA_DASHBOARDS["Cluster Status"] = "cluster_status.json"
GRAFANA_DASHBOARDS["Lustre Statistics"] = "lustre_statistics.json"
GRAFANA_DASHBOARDS["Lustre OST"] = "lustre_ost.json"
GRAFANA_DASHBOARDS["Server Statistics"] = "server_statistics.json"
GRAFANA_DASHBOARDS["SFA Physical Disk"] = "SFA_physical_disk.json"
GRAFANA_DASHBOARDS["SFA Virtual Disk"] = "SFA_virtual_disk.json"
RPM_STRING = "RPMS"
DEPENDENT_STRING = "dependent"
COLLECTD_STRING = "collectd"
RPM_TYPE_COLLECTD = COLLECTD_STRING
RPM_TYPE_DEPENDENT = DEPENDENT_STRING
SERVER_STRING = "server"
RPM_TYPE_SERVER = SERVER_STRING
RPM_TYPE_XML = "xml"


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
    # pylint: disable=too-many-public-methods,too-many-instance-attributes
    def __init__(self, host, workspace, collect_interval):
        self.es_host = host
        self.es_workspace = workspace
        self.es_iso_dir = workspace + "/ISO"
        self.es_rpm_dir = (self.es_iso_dir + "/" + "RPMS/" +
                           ssh_host.DISTRO_RHEL7)
        self.es_grafana_failure = False
        hostname = host.sh_hostname
        self.es_influxdb_client = esmon_influxdb.InfluxdbClient(hostname,
                                                                INFLUXDB_DATABASE_NAME)
        self.es_client = EsmonClient(host, workspace, self, collect_interval)
        self.es_collect_interval = collect_interval

    def es_check(self):
        """
        Check whether this host is proper for a ESMON server
        """
        distro = self.es_host.sh_distro()
        if distro != ssh_host.DISTRO_RHEL7:
            logging.error("ESMON server should be RHEL7/CentOS7 host, but got "
                          "[%s]", distro)
            return -1

        ret = self.es_client.ec_check()
        if ret:
            logging.error("checking of ESMON server [%s] failed, please fix "
                          "the problem",
                          self.es_host.sh_hostname)
            return -1
        return 0

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
        for dependent_rpm in esmon_common.ESMON_SERVER_DEPENDENT_RPMS:
            ret = self.es_host.sh_rpm_query(dependent_rpm)
            if ret == 0:
                continue
            ret = self.es_client.ec_rpm_install(dependent_rpm,
                                                RPM_TYPE_DEPENDENT)
            if ret:
                logging.error("failed to install dependent RPM on ESMON "
                              "server [%s]", self.es_host.sh_hostname)
                return ret
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
            logging.error("failed to drop Influx database of ESMON")
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

        ret = self.es_client.ec_rpm_install("influxdb", RPM_TYPE_SERVER)
        if ret:
            logging.error("failed to install Influxdb RPM on ESMON "
                          "server [%s]", self.es_host.sh_hostname)
            return ret

        config_diff = self.es_iso_dir + "/" + INFLUXDB_CONFIG_DIFF
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

        command = ("chkconfig influxdb on")
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

    def es_grafana_dashboard_add(self, name, dashboard):
        """
        Add dashboard of grafana
        """
        # pylint: disable=bare-except
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
                                  slugify.slugify(name.decode('unicode-escape')))
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
                                  slugify.slugify(name.decode('unicode-escape')))
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

    def es_grafana_dashboard_replace(self, name, dashboard):
        """
        Replace a bashboard in grafana
        """
        ret = self.es_grafana_has_dashboard(name)
        if ret < 0:
            return -1
        elif ret == 1:
            ret = self.es_grafana_dashboard_delete(name)
            if ret:
                return ret

        ret = self.es_grafana_dashboard_add(name, dashboard)
        return ret

    def es_grafana_change_logo(self):
        """
        Change the logo of grafana
        """
        command = ("/bin/cp -f %s/DDN-Storage-RedBG.svg "
                   "/usr/share/grafana/public/img/grafana_icon.svg" %
                   (self.es_iso_dir))
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
                   (self.es_iso_dir))
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

    def es_grafana_install_plugin(self, panel_name):
        """
        Install a grafana plugin
        """
        plugin_dir = GRAFANA_PLUGIN_DIR + "/" + panel_name
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

        new_plugin_dir = self.es_iso_dir + "/" + panel_name
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

    def es_grafana_install_plugins(self):
        """
        Install grafana plugins
        """
        for plugin in esmon_common.GRAFANA_PLUGIN_GITS.iterkeys():
            ret = self.es_grafana_install_plugin(plugin)
            if ret:
                logging.error("failed to install grafana plugin [%s]", plugin)
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

        ret = self.es_client.ec_rpm_install("grafana", RPM_TYPE_SERVER)
        if ret:
            logging.error("failed to install Influxdb RPM on ESMON "
                          "server [%s]", self.es_host.sh_hostname)
            return ret

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

        command = ("chkconfig grafana-server on")
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

        collect_interval = str(self.es_collect_interval)
        for name, fname in GRAFANA_DASHBOARDS.iteritems():
            dashboard_template_fpath = (mnt_path + "/" + GRAFANA_DASHBOARD_DIR +
                                        "/" + fname + ".template")
            if os.path.isfile(dashboard_template_fpath):
                dashboard_json_fpath = (self.es_workspace + "/" + fname)
                lines = open(dashboard_template_fpath).readlines()
                json_file = open(dashboard_json_fpath, 'w')
                for line in lines:
                    json_file.write(line.replace('$COLLECT_INTERVAL', collect_interval))
                json_file.close()
            else:
                dashboard_json_fpath = (mnt_path + "/" + GRAFANA_DASHBOARD_DIR +
                                        "/" + fname)

            with open(dashboard_json_fpath) as json_file:
                dashboard = json.load(json_file)

            ret = self.es_grafana_dashboard_replace(name, dashboard)
            if ret:
                return ret

        ret = self.es_grafana_change_logo()
        if ret:
            return ret

        ret = self.es_grafana_install_plugins()
        if ret:
            return ret
        return 0

    def es_reinstall(self, erase_influxdb, drop_database, mnt_path):
        """
        Reinstall RPMs
        """
        # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements
        ret = self.es_client.ec_send_iso_files(mnt_path)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          mnt_path, self.es_workspace,
                          self.es_host.sh_hostname)
            return -1

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

        cq_time = self.es_collect_interval
        ret = self.es_influxdb_cq_create("mdt_acctuser_samples",
                                         ["fs_name", "optype", "user_id", ],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("mdt_acctgroup_samples",
                                         ["fs_name", "group_id", "optype", ],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("mdt_acctproject_samples",
                                         ["fs_name", "optype", "project_id"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_acctuser_samples",
                                         ["fs_name", "optype", "user_id", ],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_acctgroup_samples",
                                         ["fs_name", "optype", "group_id"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_acctproject_samples",
                                         ["fs_name", "optype", "project_id"],
                                         cq_time)
        if ret:
            return -1

        # Shows summarized client metadata operations
        ret = self.es_influxdb_cq_create("exp_md_stats",
                                         ["exp_client", "fs_name"],
                                         cq_time)
        if ret:
            return -1

        # Shows summarized job metadata operations
        ret = self.es_influxdb_cq_create("mdt_jobstats_samples",
                                         ["fs_name", "job_id"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_stats_bytes",
                                         ["fs_name", "optype", "ost_index"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_stats_bytes",
                                         ["fs_name", "ost_index"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_stats_bytes",
                                         ["fs_name", "optype"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_kbytesinfo_used",
                                         ["fs_name", "optype"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_brw_stats_page_discontiguous_rpc_samples",
                                         ["field", "fs_name", "size"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_brw_stats_block_discontiguous_rpc_samples",
                                         ["field", "fs_name", "size"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_brw_stats_fragmented_io_samples",
                                         ["field", "fs_name", "size"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_brw_stats_io_in_flight_samples",
                                         ["field", "fs_name", "size"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_brw_stats_io_time_samples",
                                         ["field", "fs_name", "size"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_brw_stats_io_size_samples",
                                         ["field", "fs_name", "size"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_jobstats_samples",
                                         ["fs_name", "job_id", "optype"],
                                         cq_time)
        if ret:
            return -1

        where = "WHERE optype = 'sum_read_bytes' OR optype = 'sum_write_bytes'"
        ret = self.es_influxdb_cq_create("ost_jobstats_samples",
                                         ["fs_name", "job_id"],
                                         cq_time,
                                         where=where)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_brw_stats_rpc_bulk_samples",
                                         ["field", "fs_name", "size"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("exp_ost_stats_bytes",
                                         ["fs_name", "exp_client", "optype"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("md_stats",
                                         ["fs_name"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("md_stats",
                                         ["fs_name", "mdt_index"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("md_stats",
                                         ["fs_name", "optype"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("mdt_filesinfo_free",
                                         ["fs_name"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("mdt_filesinfo_used",
                                         ["fs_name"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_kbytesinfo_free",
                                         ["fs_name"],
                                         cq_time)
        if ret:
            return -1

        ret = self.es_influxdb_cq_create("ost_kbytesinfo_used",
                                         ["fs_name"],
                                         cq_time)
        if ret:
            return -1

        return 0

    def _es_influxdb_cq_create(self, measurement, groups, interval, where=""):
        """
        Create continuous query in influxdb
        """
        # pylint: disable=bare-except
        cq_query = INFLUXDB_CQ_PREFIX + measurement
        group_string = ""
        cq_measurement = INFLUXDB_CQ_MEASUREMENT_PREFIX + measurement
        for group in groups:
            group_string += ', "%s"' % group
            cq_query += "_%s" % group
            cq_measurement += "-%s" % group

        query = ('CREATE CONTINUOUS QUERY %s ON "%s" \n'
                 'BEGIN SELECT sum("value") INTO "%s" \n'
                 '    FROM "%s" %s GROUP BY time(%ss)%s \n'
                 'END;' %
                 (cq_query, INFLUXDB_DATABASE_NAME, cq_measurement,
                  measurement, where, interval, group_string))
        response = self.es_influxdb_client.ic_query(query)
        if response is None:
            logging.error("failed to create continuous query with query [%s]",
                          query)
            return -1

        if response.status_code != httplib.OK:
            logging.error("got InfluxDB status [%d] when creating "
                          "continuous query with query [%s]",
                          response.status_code, query)
            return -1
        return 0

    def es_influxdb_cq_delete(self, measurement, groups):
        """
        Delete continuous query in influxdb
        """
        # pylint: disable=bare-except
        cq_query = INFLUXDB_CQ_PREFIX + measurement
        for group in groups:
            cq_query += "_%s" % group
        query = ('DROP CONTINUOUS QUERY %s ON "%s";' %
                 (cq_query, INFLUXDB_DATABASE_NAME))
        response = self.es_influxdb_client.ic_query(query)
        if response is None:
            logging.error("failed to drop continuous query with query [%s]",
                          query)
            return -1

        if response.status_code != httplib.OK:
            logging.error("got InfluxDB status [%d] when droping "
                          "continuous query with query [%s]",
                          response.status_code, query)
            return -1
        return 0

    def es_influxdb_cq_create(self, measurement, groups, interval, where=""):
        """
        Create continuous query in influxdb, delete one first if necesary
        """
        # Sort the groups so that we will get a unique cq name for the same groups
        groups.sort()
        ret = self._es_influxdb_cq_create(measurement, groups, interval, where=where)
        if ret == 0:
            return 0

        ret = self.es_influxdb_cq_delete(measurement, groups)
        if ret:
            return ret

        ret = self._es_influxdb_cq_create(measurement, groups, interval, where=where)
        if ret:
            logging.error("failed to create continuous query for measurement [%s]",
                          measurement)
        return ret


class EsmonClient(object):
    """
    Each client ESMON host has an object of this type
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(self, host, workspace, esmon_server, collect_interval,
                 lustre_oss=False, lustre_mds=False, ime=False,
                 infiniband=False, sfas=None, enabled_plugins=""):
        self.ec_host = host
        self.ec_workspace = workspace
        self.ec_iso_basename = "ISO"
        self.ec_iso_dir = self.ec_workspace + "/" + self.ec_iso_basename
        self.ec_esmon_server = esmon_server
        self.ec_needed_collectd_rpms = ["libcollectdclient", "collectd"]
        self.ec_enabled_plugins = enabled_plugins
        config = collectd.CollectdConfig(self, collect_interval)
        config.cc_configs["Interval"] = collectd.COLLECTD_INTERVAL_TEST
        if lustre_oss or lustre_mds:
            config.cc_plugin_lustre(lustre_oss=lustre_oss,
                                    lustre_mds=lustre_mds)
        if ime:
            config.cc_plugin_ime()
        if sfas is not None:
            for sfa in sfas:
                config.cc_plugin_sfa(sfa)
        if infiniband:
            config.cc_plugin_infiniband()
        self.ec_collectd_config_test = config

        config = collectd.CollectdConfig(self, collect_interval)
        if lustre_oss or lustre_mds:
            config.cc_plugin_lustre(lustre_oss=lustre_oss,
                                    lustre_mds=lustre_mds)
        if ime:
            config.cc_plugin_ime()
        if sfas is not None:
            for sfa in sfas:
                config.cc_plugin_sfa(sfa)
        if infiniband:
            config.cc_plugin_infiniband()
        self.ec_collectd_config_final = config

        self.ec_influxdb_update_time = None
        self.ec_distro = None
        self.ec_rpm_pattern = None
        self.ec_rpm_dependent_dir = None
        self.ec_rpm_collectd_dir = None
        self.ec_rpm_dir = None
        self.ec_rpm_dependent_fnames = None
        self.ec_rpm_collectd_fnames = None
        self.ec_rpm_fnames = None
        self.ec_rpm_server_dir = None
        self.ec_rpm_server_fnames = None

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

        distro = self.ec_host.sh_distro()
        self.ec_distro = distro
        if distro == ssh_host.DISTRO_RHEL6:
            self.ec_rpm_pattern = esmon_common.RPM_PATTERN_RHEL6
        elif distro == ssh_host.DISTRO_RHEL7:
            self.ec_rpm_pattern = esmon_common.RPM_PATTERN_RHEL7
        else:
            logging.error("distro of host [%s] is not RHEL6/CentOS6 or "
                          "RHEL7/CentOS7", self.ec_host.sh_hostname)
            return -1
        self.ec_rpm_dir = ("%s/%s" %
                           (self.ec_iso_dir, RPM_STRING))
        rpm_distro_dir = ("%s/%s" %
                          (self.ec_rpm_dir, distro))
        self.ec_rpm_dependent_dir = ("%s/%s" %
                                     (rpm_distro_dir, DEPENDENT_STRING))
        self.ec_rpm_collectd_dir = ("%s/%s" %
                                    (rpm_distro_dir, COLLECTD_STRING))
        self.ec_rpm_server_dir = ("%s/%s" %
                                  (rpm_distro_dir, SERVER_STRING))
        return 0

    def ec_dependent_rpms_install(self):
        """
        Install dependent RPMs
        """
        existing_rpms = self.ec_rpm_dependent_fnames[:]
        logging.debug("find following RPMs: %s", existing_rpms)

        # lm_sensors-libs might be installed with different version. So remove
        # it if lm_sensors is not installed
        ret = self.ec_host.sh_rpm_query("lm_sensors")
        if ret:
            ret = self.ec_host.sh_rpm_query("lm_sensors-libs")
            if ret == 0:
                command = "rpm -e lm_sensors-libs --nodeps"
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

        for dependent_rpm in esmon_common.ESMON_CLIENT_DEPENDENT_RPMS:
            ret = self.ec_host.sh_rpm_query(dependent_rpm)
            if ret:
                ret = self.ec_rpm_install(dependent_rpm, RPM_TYPE_DEPENDENT)
                if ret:
                    logging.error("failed to install RPM [%s] on ESMON client "
                                  "[%s]", dependent_rpm,
                                  self.ec_host.sh_hostname)
                    return ret
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

    def ec_rpm_reinstall(self, rpm_name, rpm_type):
        """
        Reinstall a RPM
        """
        ret = self.ec_rpm_uninstall(rpm_name)
        if ret:
            logging.error("failed to reinstall collectd RPM")
            return -1

        ret = self.ec_rpm_install(rpm_name, rpm_type)
        if ret:
            logging.error("failed to install RPM [%s] on ESMON client "
                          "[%s]", rpm_name, self.ec_host.sh_hostname)
            return ret
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

        ret = self.ec_rpm_reinstall("xml_definition", RPM_TYPE_XML)
        if ret:
            logging.error("failed to reinstall XML definition RPM")
            return -1

        return 0

    def ec_rpm_install(self, name, rpm_type):
        """
        Install a RPM in the ISO given the name of the RPM
        """
        if rpm_type == RPM_TYPE_XML:
            rpm_dir = self.ec_rpm_dir
            fnames = self.ec_rpm_fnames
        elif rpm_type == RPM_TYPE_COLLECTD:
            rpm_dir = self.ec_rpm_collectd_dir
            fnames = self.ec_rpm_collectd_fnames
        elif rpm_type == RPM_TYPE_DEPENDENT:
            rpm_dir = self.ec_rpm_dependent_dir
            fnames = self.ec_rpm_dependent_fnames
        elif rpm_type == RPM_TYPE_SERVER:
            rpm_dir = self.ec_rpm_server_dir
            fnames = self.ec_rpm_server_fnames
        else:
            logging.error("unexpected RPM type [%s]", rpm_type)
            return -1

        rpm_pattern = (self.ec_rpm_pattern % name)
        rpm_regular = re.compile(rpm_pattern)
        matched_fname = None
        for filename in fnames[:]:
            match = rpm_regular.match(filename)
            if match:
                matched_fname = filename
                logging.debug("matched pattern [%s] with fname [%s]",
                              rpm_pattern, filename)
                break
        if matched_fname is None:
            logging.error("failed to find RPM with pattern [%s] under "
                          "directory [%s] of host [%s]", rpm_pattern,
                          rpm_dir, self.ec_host.sh_hostname)
            return -1

        command = ("cd %s && rpm -ivh %s" %
                   (rpm_dir, matched_fname))
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

    def ec_collectd_install(self):
        """
        Install collectd RPMs
        """
        for rpm_name in self.ec_needed_collectd_rpms:
            ret = self.ec_rpm_install(rpm_name, RPM_TYPE_COLLECTD)
            if ret:
                logging.error("failed to install RPM [%s] on ESMON client "
                              "[%s]", rpm_name, self.ec_host.sh_hostname)
                return ret
        return 0

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

    def ec_send_iso_files(self, mnt_path, no_copy=False):
        """
        send RPMs to client
        """
        # pylint: disable=too-many-return-statements
        if not no_copy:
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

            ret = self.ec_host.sh_send_file(mnt_path, self.ec_workspace)
            if ret:
                logging.error("failed to send file [%s] on local host to "
                              "directory [%s] on host [%s]",
                              mnt_path, self.ec_workspace,
                              self.ec_host.sh_hostname)
                return -1

            basename = os.path.basename(mnt_path)
            command = ("cd %s && mv %s %s" %
                       (self.ec_workspace, basename,
                        self.ec_iso_basename))
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

        command = "ls %s" % self.ec_rpm_dependent_dir
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
        self.ec_rpm_dependent_fnames = retval.cr_stdout.split()

        command = "ls %s" % self.ec_rpm_dir
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
        self.ec_rpm_fnames = retval.cr_stdout.split()

        command = "ls %s" % self.ec_rpm_collectd_dir
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
        self.ec_rpm_collectd_fnames = retval.cr_stdout.split()

        if self.ec_host.sh_distro() == ssh_host.DISTRO_RHEL6:
            self.ec_rpm_server_fnames = []
            return 0

        command = "ls %s" % self.ec_rpm_server_dir
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
        self.ec_rpm_server_fnames = retval.cr_stdout.split()
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

        # The start might return 0 even failure happened, so check again
        command = ("service collectd status")
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

        command = ("chkconfig collectd on")
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
        # pylint: disable=bare-except,unused-argument,too-many-return-statements
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Check whether the datapoint is recieved by InfluxDB
        """
        measurement_name = args[0]
        tags = args[1]
        tag_string = ""
        for key, value in tags.iteritems():
            if tag_string != "":
                tag_string += " AND"
            else:
                tag_string = " WHERE"
            tag_string += (" %s = '%s'" % (key, value))
        query = ('SELECT * FROM "%s"%s ORDER BY time DESC LIMIT 1;' %
                 (measurement_name, tag_string))
        client = self.ec_esmon_server.es_influxdb_client

        response = client.ic_query(query, epoch="s")
        if response is None:
            logging.debug("failed to drop continuous query with query [%s]",
                          query)
            return -1

        if response.status_code != httplib.OK:
            logging.debug("got InfluxDB status [%d] with query [%s]",
                          response.status_code, query)
            return -1

        data = response.json()
        json_string = json.dumps(data, indent=4, separators=(',', ': '))
        logging.debug("data: [%s]", json_string)
        if "results" not in data:
            logging.debug("got wrong InfluxDB data [%s], no [results]", json_string)
            return -1
        results = data["results"]

        if len(results) != 1:
            logging.debug("got wrong InfluxDB data [%s], [results] is not a "
                          "array with only one element", json_string)
            return -1
        result = results[0]

        if "series" not in result:
            logging.debug("got wrong InfluxDB data [%s], no [series] in one "
                          "of the result", json_string)
            return -1

        series = result["series"]
        if len(series) != 1:
            logging.debug("got wrong InfluxDB data [%s], [series] is not a "
                          "array with only one element", json_string)
            return -1
        serie = series[0]

        if "columns" not in serie:
            logging.debug("got wrong InfluxDB data [%s], no [columns] in one "
                          "of the series", json_string)
            return -1
        columns = serie["columns"]

        if "values" not in serie:
            logging.debug("got wrong InfluxDB data [%s], no [values] in one "
                          "of the series", json_string)
            return -1
        serie_values = serie["values"]

        if len(serie_values) != 1:
            logging.debug("got wrong InfluxDB data [%s], [values] is not a "
                          "array with only one element", json_string)
            return -1
        value = serie_values[0]

        time_index = -1
        i = 0
        for column in columns:
            if column == "time":
                time_index = i
                break
            i += 1

        if time_index == -1:
            logging.debug("got wrong InfluxDB data [%s], no [time] in "
                          "the columns", json_string)
            return -1

        timestamp = int(value[time_index])

        if self.ec_influxdb_update_time is None:
            self.ec_influxdb_update_time = timestamp
        elif timestamp > self.ec_influxdb_update_time:
            return 0
        logging.debug("timestamp [%d] is not updated with query [%s]",
                      timestamp, query)
        return -1

    def ec_influxdb_measurement_check(self, measurement_name, **tags):
        """
        Check whether influxdb has datapoint
        """
        if "fqdn" not in tags:
            tags["fqdn"] = self.ec_host.sh_hostname
        ret = utils.wait_condition(self._ec_influxdb_measurement_check,
                                   [measurement_name, tags])
        if ret:
            logging.error("failed to check measurement [%s]", measurement_name)
        return ret

    def ec_reinstall(self, mnt_path, no_copy=False):
        """
        Reinstall the ESMON client
        """
        # pylint: disable=too-many-return-statements
        ret = self.ec_send_iso_files(mnt_path, no_copy=no_copy)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          mnt_path, self.ec_workspace,
                          self.ec_host.sh_hostname)
            return -1

        ret = self.ec_host.sh_disable_selinux()
        if ret:
            logging.error("failed to disable SELinux on host [%s]",
                          self.ec_host.sh_hostname)
            return -1

        ret = self.ec_collectd_reinstall()
        if ret:
            logging.error("failed to install esmon client on host [%s]",
                          self.ec_host.sh_hostname)
            return -1

        ret = self.ec_collectd_send_config(True)
        if ret:
            logging.error("failed to send test config to esmon client on host [%s]",
                          self.ec_host.sh_hostname)
            return -1

        ret = self.ec_collectd_start()
        if ret:
            logging.error("failed to start esmon client on host [%s]",
                          self.ec_host.sh_hostname)
            return -1

        ret = self.ec_collectd_config_test.cc_check()
        if ret:
            logging.error("Influxdb doesn't have expected datapoints from "
                          "host [%s]", self.ec_host.sh_hostname)
            return -1

        ret = self.ec_collectd_send_config(False)
        if ret:
            logging.error("failed to send final config to esmon client on host [%s]",
                          self.ec_host.sh_hostname)
            return -1

        ret = self.ec_collectd_restart()
        if ret:
            logging.error("failed to start esmon client on host [%s]",
                          self.ec_host.sh_hostname)
            return -1

        return 0


def esmon_install_parse_config(workspace, config, config_fpath):
    """
    Start to install with the ISO mounted
    """
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches,bare-except, too-many-locals
    # pylint: disable=too-many-statements
    esmon_clients = {}
    esmon_server = None

    host_configs = esmon_common.config_value(config, esmon_common.CSTR_SSH_HOST)
    if host_configs is None:
        logging.error("can NOT find [ssh_hosts] in the config file, "
                      "please correct file [%s]", config_fpath)
        return -1, esmon_server, esmon_clients

    hosts = {}
    for host_config in host_configs:
        host_id = host_config[esmon_common.CSTR_HOST_ID]
        if host_id is None:
            logging.error("can NOT find [host_id] in the config of a "
                          "SSH host, please correct file [%s]",
                          config_fpath)
            return -1, esmon_server, esmon_clients

        hostname = esmon_common.config_value(host_config, esmon_common.CSTR_HOSTNAME)
        if hostname is None:
            logging.error("can NOT find [hostname] in the config of SSH host "
                          "with ID [%s], please correct file [%s]",
                          host_id, config_fpath)
            return -1, esmon_server, esmon_clients

        ssh_identity_file = esmon_common.config_value(host_config, "ssh_identity_file")

        if host_id in hosts:
            logging.error("multiple SSH hosts with the same ID [%s], please "
                          "correct file [%s]", host_id, config_fpath)
            return -1, esmon_server, esmon_clients
        host = ssh_host.SSHHost(hostname, identity_file=ssh_identity_file,
                                host_id=host_id)
        hosts[host_id] = host

    server_host_config = esmon_common.config_value(config, esmon_common.CSTR_SERVER_HOST)
    if server_host_config is None:
        logging.error("can NOT find [server_host] in the config file [%s], "
                      "please correct it", config_fpath)
        return -1, esmon_server, esmon_clients

    host_id = esmon_common.config_value(server_host_config, esmon_common.CSTR_HOST_ID)
    if host_id is None:
        logging.error("can NOT find [host_id] in the config of [server_host], "
                      "please correct file [%s]", config_fpath)
        return -1, esmon_server, esmon_clients

    if host_id not in hosts:
        logging.error("SSH host with ID [%s] is NOT configured in "
                      "[ssh_hosts], please correct file [%s]",
                      host_id, config_fpath)
        return -1, esmon_server, esmon_clients

    collect_interval = esmon_common.config_value(config,
                                                 esmon_common.CSTR_COLLECT_INTERVAL)
    if collect_interval is None:
        logging.error("[%s] is not configured, please correct file [%s]",
                      esmon_common.CSTR_COLLECT_INTERVAL, config_fpath)
        return -1

    host = hosts[host_id]
    esmon_server = EsmonServer(host, workspace, collect_interval)
    ret = esmon_server.es_check()
    if ret:
        logging.error("checking of ESMON server [%s] failed, please fix the "
                      "problem", esmon_server.es_host.sh_hostname)
        return -1, esmon_server, esmon_clients

    client_host_configs = esmon_common.config_value(config, esmon_common.CSTR_CLIENT_HOSTS)
    if client_host_configs is None:
        logging.error("can NOT find [%s] in the config file, "
                      "please correct file [%s]",
                      esmon_common.CSTR_CLIENT_HOSTS, config_fpath)
        return -1, esmon_server, esmon_clients

    for client_host_config in client_host_configs:
        host_id = esmon_common.config_value(client_host_config, esmon_common.CSTR_HOST_ID)
        if host_id is None:
            logging.error("can NOT find [%s] in the config of a "
                          "ESMON client host, please correct file [%s]",
                          esmon_common.CSTR_HOST_ID, config_fpath)
            return -1, esmon_server, esmon_clients

        if host_id not in hosts:
            logging.error("ESMON client with ID [%s] is NOT configured in "
                          "[ssh_hosts], please correct file [%s]",
                          host_id, config_fpath)
            return -1, esmon_server, esmon_clients

        enabled_plugins = ("memory, CPU, df(/), load, sensors, disk, uptime, "
                           "users")

        host = hosts[host_id]
        lustre_oss = esmon_common.config_value(client_host_config, esmon_common.CSTR_LUSTRE_OSS)
        if lustre_oss is None:
            lustre_oss = False
        if lustre_oss:
            enabled_plugins += ", Lustre OSS"

        lustre_mds = esmon_common.config_value(client_host_config, esmon_common.CSTR_LUSTRE_MDS)
        if lustre_mds is None:
            lustre_mds = False
        if lustre_mds:
            enabled_plugins += ", Lustre MDS"

        ime = esmon_common.config_value(client_host_config, esmon_common.CSTR_IME)
        if ime is None:
            ime = False
        if ime:
            enabled_plugins += ", DDN IME"

        infiniband = esmon_common.config_value(client_host_config, esmon_common.CSTR_INFINIBAND)
        if infiniband is None:
            infiniband = False
        if infiniband:
            enabled_plugins += ", IB"

        sfas = esmon_common.config_value(client_host_config, esmon_common.CSTR_SFAS)
        sfa_names = []
        sfa_hosts = []
        if sfas is not None:
            for sfa in sfas:
                name = esmon_common.config_value(sfa, esmon_common.CSTR_NAME)
                if name is None:
                    logging.error("can NOT find [%s] in the SFA config of a "
                                  "ESMON client host, please correct file "
                                  "[%s]", esmon_common.CSTR_NAME, config_fpath)
                    return -1, esmon_server, esmon_clients

                if name in sfa_names:
                    logging.error("multiple SFAs with the same name [%s], "
                                  "please correct file [%s]", name,
                                  config_fpath)
                    return -1, esmon_server, esmon_clients
                sfa_names.append(name)

                controller0_host = esmon_common.config_value(sfa,
                                                             esmon_common.CSTR_CONTROLLER0_HOST)
                if controller0_host is None:
                    logging.error("can NOT find [%s] in the SFA "
                                  "config of a ESMON client host, please "
                                  "correct file [%s]",
                                  esmon_common.CSTR_CONTROLLER0_HOST, config_fpath)
                    return -1, esmon_server, esmon_clients

                if controller0_host in sfa_hosts:
                    logging.error("multiple SFAs with the same controller "
                                  "host [%s], please correct file [%s]",
                                  controller0_host,
                                  config_fpath)
                    return -1, esmon_server, esmon_clients
                sfa_hosts.append(controller0_host)

                controller1_host = esmon_common.config_value(sfa,
                                                             esmon_common.CSTR_CONTROLLER1_HOST)
                if controller1_host is None:
                    logging.error("can NOT find [%s] in the SFA "
                                  "config of a ESMON client host, please "
                                  "correct file [%s]",
                                  esmon_common.CSTR_CONTROLLER1_HOST, config_fpath)
                    return -1, esmon_server, esmon_clients

                if controller1_host in sfa_hosts:
                    logging.error("multiple SFAs with the same controller "
                                  "host [%s], please correct file [%s]",
                                  controller1_host,
                                  config_fpath)
                    return -1, esmon_server, esmon_clients
                sfa_hosts.append(controller1_host)
            enabled_plugins += ", SFA"

        esmon_client = EsmonClient(host, workspace, esmon_server, collect_interval,
                                   lustre_oss=lustre_oss,
                                   lustre_mds=lustre_mds, ime=ime,
                                   infiniband=infiniband,
                                   sfas=sfas,
                                   enabled_plugins=enabled_plugins)
        esmon_clients[host_id] = esmon_client
        ret = esmon_client.ec_check()
        if ret:
            logging.error("checking of ESMON client [%s] failed, please fix "
                          "the problem",
                          esmon_client.ec_host.sh_hostname)
            return -1, esmon_server, esmon_clients

    return 0, esmon_server, esmon_clients


def esmon_do_install(workspace, config, config_fpath, mnt_path):
    """
    Start to install with the ISO mounted
    """
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches,bare-except, too-many-locals
    # pylint: disable=too-many-statements
    ret, esmon_server, esmon_clients = esmon_install_parse_config(workspace, config, config_fpath)
    if ret:
        logging.error("failed to parse config [%s]", config_fpath)
        return -1

    clients_reinstall = esmon_common.config_value(config,
                                                  esmon_common.CSTR_CLIENTS_REINSTALL)
    if clients_reinstall is None:
        logging.info("[%s] is not configured in file [%s], use True as default",
                     esmon_common.CSTR_CLIENTS_REINSTALL, config_fpath)
        clients_reinstall = True

    server_host_config = esmon_common.config_value(config, esmon_common.CSTR_SERVER_HOST)
    if server_host_config is None:
        logging.error("can NOT find [server_host] in the config file [%s], "
                      "please correct it", config_fpath)
        return -1

    erase_influxdb = esmon_common.config_value(server_host_config, esmon_common.CSTR_ERASE_INFLUXDB)
    if erase_influxdb is None:
        logging.info("[%s] is not configured in file [%s], use False as default",
                     esmon_common.CSTR_ERASE_INFLUXDB, config_fpath)
        erase_influxdb = False

    drop_database = esmon_common.config_value(server_host_config, esmon_common.CSTR_DROP_DATABASE)
    if drop_database is None:
        logging.info("[%s] is not configured in file [%s], use False as default",
                     esmon_common.CSTR_DROP_DATABASE, config_fpath)
        drop_database = False

    server_reinstall = esmon_common.config_value(server_host_config,
                                                 esmon_common.CSTR_REINSTALL)
    if server_reinstall is None:
        logging.info("[%s] is not configured in file [%s], use True as default",
                     esmon_common.CSTR_REINSTALL, config_fpath)
        server_reinstall = True

    if not server_reinstall:
        logging.info("ESMON server won't be reinstalled according to the "
                     "config")
    else:
        logging.info("Influxdb will %sbe erased according to the config",
                     "" if erase_influxdb else "NOT ")
        logging.info("database [%s] of Influxdb will %sbe dropped "
                     "according to the config", INFLUXDB_DATABASE_NAME,
                     "" if drop_database else "NOT ")

    if clients_reinstall:
        for esmon_client in esmon_clients.values():
            logging.info("support for metrics of [%s] will be enabled on "
                         "ESMON client [%s] according to the config",
                         esmon_client.ec_enabled_plugins,
                         esmon_client.ec_host.sh_hostname)

    if server_reinstall:
        ret = esmon_server.es_reinstall(erase_influxdb, drop_database, mnt_path)
        if ret:
            logging.error("failed to reinstall ESMON server on host [%s]",
                          esmon_server.es_host.sh_hostname)
            return -1

    if clients_reinstall:
        for esmon_client in esmon_clients.values():
            no_copy = (esmon_server.es_host.sh_hostname ==
                       esmon_client.ec_host.sh_hostname)
            if not server_reinstall:
                no_copy = False
            ret = esmon_client.ec_reinstall(mnt_path, no_copy=no_copy)
            if ret:
                logging.error("failed to reinstall ESMON client on host [%s]",
                              esmon_client.ec_host.sh_hostname)
                return -1
    else:
        logging.info("ESMON clients won't be reinstalled according to the "
                     "config, restarting ESMON client instead")
        for esmon_client in esmon_clients.values():
            ret = esmon_client.ec_collectd_restart()
            if ret:
                logging.error("failed to start esmon client on host [%s]",
                              esmon_client.ec_host.sh_hostname)
                return -1
    return 0


def esmon_mount_and_install(workspace, config, config_fpath):
    """
    Mount the ISO and install the ESMON system
    """
    # pylint: disable=bare-except,global-statement
    local_host = ssh_host.SSHHost("localhost", local=True)
    iso_path = esmon_common.config_value(config, esmon_common.CSTR_ISO_PATH)
    if iso_path is None:
        iso_path = esmon_install_common.find_iso_path_in_cwd(local_host)
        if iso_path is None:
            logging.error("failed to find ESMON ISO %s under currect "
                          "directory")
            return -1
        logging.info("no [iso_path] is configured, use [%s] under current "
                     "directory", iso_path)

    mnt_path = "/mnt/" + utils.random_word(8)

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


def esmon_install_locked(workspace, config_fpath):
    """
    Start to install holding the confiure lock
    """
    # pylint: disable=too-many-branches,bare-except,too-many-locals
    # pylint: disable=too-many-statements
    save_fpath = workspace + "/" + esmon_common.ESMON_INSTALL_CONFIG_FNAME
    logging.debug("copying config file from [%s] to [%s]", config_fpath,
                  save_fpath)
    shutil.copyfile(config_fpath, save_fpath)

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

    return esmon_mount_and_install(workspace, config, config_fpath)


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
    config_fpath = ESMON_INSTALL_CONFIG

    if len(sys.argv) == 2:
        config_fpath = sys.argv[1]
    elif len(sys.argv) > 2:
        usage()
        sys.exit(-1)

    identity = time_util.local_strftime(time_util.utcnow(), "%Y-%m-%d-%H_%M_%S")
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

    ret = esmon_install(workspace, config_fpath)
    if ret:
        logging.error("installation failed, please check [%s] for more log\n",
                      workspace)
        sys.exit(ret)
    logging.info("Exascaler monistoring system is installed, please check [%s] "
                 "for more log", workspace)
    sys.exit(0)
