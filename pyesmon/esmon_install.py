"""
Library for installing ESMON
"""

import sys
import logging
import traceback
import os
import shutil
import yaml
import filelock

# Local libs
from pyesmon import utils
from pyesmon import ssh_host

ESMON_CONFIG_FNAME = "esmon.conf"
ESMON_CONFIG = "/etc/" + ESMON_CONFIG_FNAME
ESMON_INSTALL_LOG_DIR = "/var/log/esmon_install"
INFLUXDB_CONFIG_FPATH = "/etc/influxdb/influxdb.conf"
ESMON_INFLUXDB_CONFIG_DIFF = "influxdb.conf.diff"
COLLECTD_CONFIG_FNAME = "collectd.conf.esmon"

class EsmonServer(object):
    """
    ESMON server host has an object of this type
    """
    def __init__(self, host, workspace):
        self.es_host = host
        self.es_workspace = workspace
        self.es_rpm_basename = "RPMS"
        self.es_rpm_dir = self.es_workspace + "/" + self.es_rpm_basename

    def es_influxdb_reinstall(self):
        """
        Install influxdb RPM
        """
        ret = self.es_host.sh_rpm_query("influxdb")
        if ret == 0:
            command = "rpm -e influxdb"
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

        command = ("cd %s && rpm -ivh influxdb-*" %
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

        command = ('influx -execute "CREATE DATABASE collectd"')
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

    def es_send_rpms(self, mnt_path):
        """
        send RPMs to server
        """
        command = ("mkdir -p %s" % (self.es_workspace))
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

        ret = self.es_host.sh_send_file(mnt_path,
                                        self.es_workspace)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          mnt_path, self.es_workspace,
                          self.es_host.sh_hostname)
            return -1

        basename = os.path.basename(mnt_path)
        command = ("cd %s && mv %s %s" %
                   (self.es_workspace, basename,
                    self.es_rpm_basename))
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

class EsmonClient(object):
    """
    Each client ESMON host has an object of this type
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(self, host, workspace):
        self.ec_host = host
        self.ec_workspace = workspace
        self.ec_rpm_basename = "RPMS"
        self.ec_rpm_dir = self.ec_workspace + "/" + self.ec_rpm_basename

    def ec_dependent_rpms_install(self):
        """
        Install dependent RPMs
        """
        dependent_rpms = ["yajl", "openpgm", "zeromq3"]
        for dependent_rpm in dependent_rpms:
            ret = self.ec_host.sh_rpm_query(dependent_rpm)
            if ret:
                command = ("cd %s && rpm -ivh %s*.rpm" %
                           (self.ec_rpm_dir, dependent_rpm))
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
            command = ("rpm -qa | grep %s | xargs rpm -e" % rpm_name)
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
        command = ("cd %s && rpm -ivh collectd-* libcollectdclient-*" %
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

        collectd_config_fpath = self.ec_workspace + "/collectd.conf"
        etc_path = "/etc"
        ret = self.ec_host.sh_send_file(collectd_config_fpath,
                                        etc_path)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          collectd_config_fpath, etc_path,
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

def generate_collectd_config(mnt_path, workspace, esmon_server):
    """
    Generate collectd config
    """
    server_hostname = esmon_server.es_host.sh_hostname
    template_fpath = mnt_path + "/" + COLLECTD_CONFIG_FNAME
    collectd_config_fpath = workspace + "/collectd.conf"
    with open(template_fpath, "rt") as fin:
        with open(collectd_config_fpath, "wt") as fout:
            for line in fin:
                fout.write(line.replace('${esmon:server_host}',
                                        server_hostname))


def esmon_install_locked(workspace, config_fpath):
    """
    Start to install holding the confiure lock
    """
    # pylint: disable=global-statement,too-many-return-statements
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

    host_configs = config["ssh_hosts"]
    hosts = {}
    for host_config in host_configs:
        hostname = host_config["hostname"]
        host_id = host_config["host_id"]
        if "ssh_identity_file" in host_config:
            ssh_identity_file = host_config["ssh_identity_file"]
        else:
            ssh_identity_file = None
        if host_id in hosts:
            logging.error("multiple hosts with the same ID [%s]", host_id)
            return -1
        host = ssh_host.SSHHost(hostname, ssh_identity_file)
        hosts[host_id] = host

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

    server_host_config = config["server_host"]
    host_id = server_host_config["host_id"]
    if host_id not in hosts:
        logging.error("no host with ID [%s] is configured", host_id)
        return -1
    host = hosts[host_id]
    esmon_server = EsmonServer(host, workspace)

    ret = esmon_server.es_send_rpms(mnt_path)
    if ret:
        logging.error("failed to send file [%s] on local host to "
                      "directory [%s] on host [%s]",
                      mnt_path, esmon_server.es_workspace,
                      esmon_server.es_host.sh_hostname)
        return -1

    ret = esmon_server.es_influxdb_reinstall()
    if ret:
        logging.error("failed to install esmon server on host [%s]",
                      esmon_server.es_host.sh_hostname)
        return -1

    generate_collectd_config(mnt_path, workspace, esmon_server)

    client_host_configs = config["client_hosts"]
    esmon_clients = {}
    for client_host_config in client_host_configs:
        host_id = client_host_config["host_id"]

        if host_id not in hosts:
            logging.error("no host with ID [%s] is configured", host_id)
            return -1
        host = hosts[host_id]
        esmon_client = EsmonClient(host, workspace)
        esmon_clients[host_id] = esmon_client

    for esmon_client in esmon_clients.values():
        if esmon_server.es_host.sh_hostname != esmon_client.ec_host.sh_hostname:
            ret = esmon_client.ec_send_rpms(mnt_path)
            if ret:
                logging.error("failed to send file [%s] on local host to "
                              "directory [%s] on host [%s]",
                              mnt_path, esmon_client.ec_workspace,
                              esmon_client.ec_host.sh_hostname)
                break

        ret = esmon_client.ec_collectd_reinstall()
        if ret:
            logging.error("failed to install esmon client on host [%s]",
                          esmon_client.ec_host.sh_hostname)
            break

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
        return -1

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
        logging.error("installation failed, please check [%s] for more log",
                      workspace)
        sys.exit(ret)
    logging.info("Exascaler monistoring system is installed, please check [%s] "
                 "for more log", workspace)
    sys.exit(0)
