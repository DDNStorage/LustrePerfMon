# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for installing virtual machines
"""
# pylint: disable=too-many-lines
import sys
import logging
import traceback
import os
import re
import shutil
import yaml
import filelock

# Local libs
from pyesmon import utils
from pyesmon import esmon_common
from pyesmon import esmon_virt
from pyesmon import esmon_install
from pyesmon import ssh_host
from pyesmon import watched_io

ESMON_TEST_LOG_DIR = "/var/log/esmon_test"


def generate_client_host_config(host_id):
    """
    Generate the client host config of ESMON installation
    """
    client_host = {}
    client_host[esmon_install.HOST_ID_STRING] = host_id
    client_host[esmon_install.LUSTRE_OSS_STRING] = host_id
    client_host[esmon_install.LUSTRE_MDS_STRING] = host_id
    client_host[esmon_install.IME_STRING] = host_id
    return client_host


def generate_server_host_config(host_id):
    """
    Generate the server host config of ESMON installation
    """
    server_host = {}
    server_host[esmon_install.HOST_ID_STRING] = host_id
    server_host[esmon_install.DROP_DATABASE_STRING] = False
    server_host[esmon_install.ERASE_INFLUXDB_STRING] = False
    return server_host


class EsmonInstallServer(object):
    """
    ESMON server host has an object of this type
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self, workspace, host, iso_dir):
        self.eis_host = host
        self.eis_iso_dir = iso_dir
        self.eis_rpm_dir = (iso_dir + "/" + "RPMS/" +
                            ssh_host.DISTRO_RHEL7)
        self.eis_rpm_dependent_dir = self.eis_rpm_dir + "/dependent"
        self.eis_rpm_dependent_fnames = None
        self.eis_workspace = workspace

    def eis_rpm_install(self, name):
        """
        Install a RPM in the ISO given the name of the RPM
        """
        if self.eis_rpm_dependent_fnames is None:
            command = "ls %s" % self.eis_rpm_dependent_dir
            retval = self.eis_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.eis_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1
            self.eis_rpm_dependent_fnames = retval.cr_stdout.split()

        rpm_dir = self.eis_rpm_dependent_dir
        rpm_pattern = (esmon_common.RPM_PATTERN_RHEL7 % name)
        rpm_regular = re.compile(rpm_pattern)
        matched_fname = None
        for filename in self.eis_rpm_dependent_fnames[:]:
            match = rpm_regular.match(filename)
            if match:
                matched_fname = filename
                logging.debug("matched pattern [%s] with fname [%s]",
                              rpm_pattern, filename)
                break
        if matched_fname is None:
            logging.error("failed to find RPM with pattern [%s] under "
                          "directory [%s] of host [%s]", rpm_pattern,
                          rpm_dir, self.eis_host.sh_hostname)
            return -1

        command = ("cd %s && rpm -ivh %s" %
                   (rpm_dir, matched_fname))
        retval = self.eis_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.eis_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0


def esmon_do_test_install(workspace, install_server, mnt_path):
    """
    Run the install test
    """
    # pylint: disable=too-many-return-statements
    esmon_installer = EsmonInstallServer(workspace, install_server, mnt_path)

    command = ("rpm -e esmon")
    retval = install_server.sh_run(command)
    if retval.cr_exit_status:
        logging.debug("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      install_server.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)

    command = ("rpm -ivh %s/RPMS/rhel7/esmon-*.el7.x86_64.rpm" %
               (mnt_path))
    retval = install_server.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      install_server.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    for dependent_rpm in esmon_common.ESMON_INSTALL_DEPENDENT_RPMS:
        ret = install_server.sh_rpm_query(dependent_rpm)
        if ret == 0:
            continue
        ret = esmon_installer.eis_rpm_install(dependent_rpm)
        if ret:
            logging.error("failed to install rpm [%s] on host [%s]",
                          dependent_rpm, install_server.sh_hostname)
            return -1

    install_config_fpath = (workspace + "/" +
                            esmon_common.ESMON_INSTALL_CONFIG_FNAME)
    ret = install_server.sh_send_file(install_config_fpath, "/etc")
    if ret:
        logging.error("failed to send file [%s] on local host to "
                      "directory [/etc] on host [%s]",
                      install_config_fpath, install_server.sh_hostname)
        return -1

    args = {}
    args["hostname"] = install_server.sh_hostname
    stdout_file = (workspace + "/" + "esmon_install.stdout")
    stderr_file = (workspace + "/" + "esmon_install.stderr")
    stdout_fd = watched_io.watched_io_open(stdout_file,
                                           watched_io.log_watcher_debug, args)
    stderr_fd = watched_io.watched_io_open(stderr_file,
                                           watched_io.log_watcher_debug, args)
    command = "esmon_install"
    retval = install_server.sh_run(command, stdout_tee=stdout_fd,
                                   stderr_tee=stderr_fd, return_stdout=False,
                                   return_stderr=False, timeout=None, flush_tee=True)
    stdout_fd.close()
    stderr_fd.close()

    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d]",
                      command,
                      install_server.sh_hostname,
                      retval.cr_exit_status)
        return -1
    return 0


def esmon_test_install(workspace, install_server, host_iso_path):
    """
    Run the install test
    """
    # pylint: disable=bare-except
    mnt_path = "/mnt/" + utils.random_word(8)

    command = ("mkdir -p %s && mount -o loop %s %s" %
               (mnt_path, host_iso_path, mnt_path))
    retval = install_server.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      install_server.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    try:
        ret = esmon_do_test_install(workspace, install_server, mnt_path)
    except:
        ret = -1
        logging.error("exception: %s", traceback.format_exc())

    command = ("umount %s" % (mnt_path))
    retval = install_server.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      install_server.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        ret = -1

    command = ("rmdir %s" % (mnt_path))
    retval = install_server.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      install_server.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1
    return ret


def esmon_do_test(workspace, config, config_fpath):
    """
    Run the tests
    """
    # pylint: disable=too-many-return-statements,too-many-locals
    # pylint: disable=too-many-branches,too-many-statements
    vm_host_configs = esmon_common.config_value(config, "vm_hosts")
    if vm_host_configs is None:
        logging.error("no [vm_hosts] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    if len(vm_host_configs) < 4:
        logging.error("[vm_hosts] has less than four hosts, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel7_number = 0
    for vm_host_config in vm_host_configs:
        distro = esmon_common.config_value(vm_host_config, "distro")
        if distro is None:
            logging.error("no [distro] is configured for a vm_host, "
                          "please correct file [%s]", config_fpath)
            return -1

        if distro == ssh_host.DISTRO_RHEL7:
            rhel7_number += 1

    if rhel7_number < 2:
        logging.error("less than two hosts vith distro [rhel7] is configured "
                      "as installation server and ESMON server, please "
                      "correct file [%s]", config_fpath)
        return -1

    ret = esmon_virt.esmon_vm_install(workspace, config, config_fpath)
    if ret:
        logging.error("failed to install the virtual machines")
        return -1

    local_host = ssh_host.SSHHost("localhost", local=True)

    hosts = []
    install_server = None
    server_host_config = None
    client_host_configs = []
    ssh_host_configs = []
    hosts_string = """127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
"""
    for vm_host_config in vm_host_configs:
        hostname = esmon_common.config_value(vm_host_config, esmon_virt.STRING_HOSTNAME)
        if hostname is None:
            logging.error("no [%s] is configured for a vm_host, "
                          "please correct file [%s]",
                          esmon_virt.STRING_HOSTNAME, config_fpath)
            return -1

        distro = esmon_common.config_value(vm_host_config, esmon_virt.STRING_DISTRO)
        if distro is None:
            logging.error("no [%s] is configured for a vm_host, "
                          "please correct file [%s]", esmon_virt.STRING_DISTRO,
                          config_fpath)
            return -1

        host_ip = esmon_common.config_value(vm_host_config, esmon_virt.STRING_HOST_IP)
        if host_ip is None:
            logging.error("no [%s] is configured for a vm_host, "
                          "please correct file [%s]",
                          esmon_virt.STRING_HOST_IP, config_fpath)
            return -1

        # Remove the record in known_hosts, otherwise ssh will fail
        command = ('sed -i "/%s /d" /root/.ssh/known_hosts' % (host_ip))
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

        # Remove the record in known_hosts, otherwise ssh will fail
        command = ('sed -i "/%s /d" /root/.ssh/known_hosts' % (hostname))
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

        vm_host = ssh_host.SSHHost(hostname)
        command = "> /root/.ssh/known_hosts"
        retval = vm_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          vm_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        hosts_string += ("%s %s\n" % (host_ip, hostname))
        hosts.append(vm_host)
        ssh_host_config = {}
        ssh_host_config[esmon_install.HOST_ID_STRING] = hostname
        ssh_host_config[esmon_install.HOSTNAME_STRING] = hostname
        ssh_host_configs.append(ssh_host_config)

        if distro == ssh_host.DISTRO_RHEL6:
            client_host_configs.append(generate_client_host_config(hostname))
            logging.info("using [%s] as a RHEL6 esmon client", hostname)
        elif install_server is None:
            install_server = vm_host
            logging.info("using [%s] as the installation server", hostname)
        elif server_host_config is None:
            server_host_config = generate_server_host_config(hostname)
            logging.info("using [%s] as the esmon server", hostname)
        else:
            logging.info("using [%s] as a RHEL7 esmon client", hostname)
            client_host_configs.append(generate_client_host_config(hostname))

    command = "ls esmon-*.iso"
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

    current_dir = os.getcwd()
    iso_names = retval.cr_stdout.split()
    if len(iso_names) != 1:
        logging.info("found unexpected ISOs [%s] under currect directory [%s]",
                     iso_names, current_dir)
        return -1

    iso_name = iso_names[0]
    iso_path = current_dir + "/" + iso_name

    command = "mkdir -p %s" % workspace
    retval = install_server.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      install_server.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    hosts_fpath = workspace + "/hosts"
    with open(hosts_fpath, "wt") as hosts_file:
        hosts_file.write(hosts_string)

    for host in hosts:
        ret = host.sh_enable_dns()
        if ret:
            logging.error("failed to enable dns on host [%s]",
                          host.sh_hostname)
            return -1

        command = "yum install rsync -y"
        retval = host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        ret = host.sh_send_file(hosts_fpath, "/etc")
        if ret:
            logging.error("failed to send hosts file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          hosts_fpath, workspace,
                          host.sh_hostname)
            return -1

    ret = install_server.sh_send_file(iso_path, workspace)
    if ret:
        logging.error("failed to send ESMON ISO [%s] on local host to "
                      "directory [%s] on host [%s]",
                      iso_path, workspace,
                      install_server.sh_hostname)
        return -1

    host_iso_path = workspace + "/" + iso_name
    install_config = {}
    install_config[esmon_install.ISO_PATH_STRING] = host_iso_path
    install_config[esmon_install.SSH_HOST_STRING] = ssh_host_configs
    install_config[esmon_install.CLIENT_HOSTS_STRING] = client_host_configs
    install_config[esmon_install.SERVER_HOST_STRING] = server_host_config
    install_config_string = yaml.dump(install_config, default_flow_style=False)
    install_config_fpath = workspace + "/" + esmon_common.ESMON_INSTALL_CONFIG_FNAME
    with open(install_config_fpath, "wt") as install_config_file:
        install_config_file.write(install_config_string)

    ret = esmon_test_install(workspace, install_server, host_iso_path)
    if ret:
        return -1

    return 0


def esmon_test_locked(workspace, config_fpath):
    """
    Start to test holding the confiure lock
    """
    # pylint: disable=too-many-branches,bare-except,too-many-locals
    # pylint: disable=too-many-statements
    save_fpath = workspace + "/" + esmon_virt.ESMON_VIRT_CONFIG_FNAME
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

    try:
        ret = esmon_do_test(workspace, config, config_fpath)
    except:
        ret = -1
        logging.error("exception: %s", traceback.format_exc())

    return ret


def esmon_test(workspace, config_fpath):
    """
    Start to test
    """
    # pylint: disable=bare-except
    lock_file = config_fpath + ".lock"
    lock = filelock.FileLock(lock_file)
    try:
        with lock.acquire(timeout=0):
            try:
                ret = esmon_test_locked(workspace, config_fpath)
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
    Test Exascaler monitoring
    """
    # pylint: disable=unused-variable
    reload(sys)
    sys.setdefaultencoding("utf-8")
    config_fpath = esmon_virt.ESMON_VIRT_CONFIG

    if len(sys.argv) == 2:
        config_fpath = sys.argv[1]
    elif len(sys.argv) > 2:
        usage()
        sys.exit(-1)

    identity = utils.local_strftime(utils.utcnow(), "%Y-%m-%d-%H_%M_%S")
    workspace = ESMON_TEST_LOG_DIR + "/" + identity

    if not os.path.exists(ESMON_TEST_LOG_DIR):
        os.mkdir(ESMON_TEST_LOG_DIR)
    elif not os.path.isdir(ESMON_TEST_LOG_DIR):
        logging.error("[%s] is not a directory", ESMON_TEST_LOG_DIR)
        sys.exit(-1)

    if not os.path.exists(workspace):
        os.mkdir(workspace)
    elif not os.path.isdir(workspace):
        logging.error("[%s] is not a directory", workspace)
        sys.exit(-1)

    print("Started testing ESMON using config [%s], "
          "please check [%s] for more log" %
          (config_fpath, workspace))
    utils.configure_logging(workspace)

    console_handler = utils.LOGGING_HANLDERS["console"]
    console_handler.setLevel(logging.DEBUG)

    ret = esmon_test(workspace, config_fpath)
    if ret:
        logging.error("test failed, please check [%s] for more log\n",
                      workspace)
        sys.exit(ret)
    logging.info("Passed the ESMON tests, please check [%s] "
                 "for more log", workspace)
    sys.exit(0)
