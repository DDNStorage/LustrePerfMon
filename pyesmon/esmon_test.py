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
import shutil
import yaml
import filelock

# Local libs
from pyesmon import utils
from pyesmon import esmon_virt
from pyesmon import ssh_host

ESMON_TEST_LOG_DIR = "/var/log/esmon_test"


def config_value(config, key):
    """
    Return value of a key in config
    """
    if key not in config:
        return None
    return config[key]


def esmon_do_test(workspace, config, config_fpath):
    """
    Run the tests
    """
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    vm_host_configs = config_value(config, "vm_hosts")
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
        distro = config_value(vm_host_config, "distro")
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

    installation_server = None
    esmon_server = None
    esmon_clients = []
    for vm_host_config in vm_host_configs:
        hostname = config_value(vm_host_config, "hostname")
        if hostname is None:
            logging.error("no [hostname] is configured for a vm_host, "
                          "please correct file [%s]", config_fpath)
            return -1

        distro = config_value(vm_host_config, "distro")
        if distro is None:
            logging.error("no [distro] is configured for a vm_host, "
                          "please correct file [%s]", config_fpath)
            return -1

        vm_host = ssh_host.SSHHost(hostname)

        if distro == ssh_host.DISTRO_RHEL6:
            logging.info("using [%s] as RHEL6 esmon client", hostname)
            esmon_clients.append(vm_host)
        elif installation_server is None:
            installation_server = vm_host
            logging.info("using [%s] as installation server", hostname)
        elif esmon_server is None:
            esmon_server = vm_host
            logging.info("using [%s] as esmon server", hostname)
        else:
            logging.info("using [%s] as RHEL7 esmon client", hostname)
            esmon_clients.append(vm_host)

    # Check hosts

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
