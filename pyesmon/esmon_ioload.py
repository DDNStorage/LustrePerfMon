# Copyright (c) 2018 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: Qian Yingjin qian@ddn.com
"""
Library for Loading the Lustre file system for
monitoring.
"""
import sys
import logging
import os
import traceback
import shutil
import time
import yaml
import filelock

# Local libs
from pyesmon import utils
from pyesmon import time_util
from pyesmon import esmon_common
from pyesmon import ssh_host
from pyesmon import lustre

ESMON_TEST_LOG_DIR = "/var/log/esmon_test"
ESMON_TEST_CONFIG_FNAME = "esmon_test.conf"
ESMON_TEST_CONFIG = "/etc/" + ESMON_TEST_CONFIG_FNAME


def esmon_write_thread(client, stripe_num):
    """
    The thread doing write IO.
    """
    fpath = ("%s/%s_write" % (client.lc_mnt, client.lc_host.sh_hostname))
    command = ("lfs setstripe -c %s %s" % (stripe_num, fpath))
    retval = client.lc_host.sh_run(command)
    if retval.cr_exit_status:
        logging.debug("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      client.lc_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    while True:
        command = ("dd if=/dev/zero of=%s bs=1M count=4096" % (fpath))
        retval = client.lc_host.sh_run(command)
        if retval.cr_exit_status != 0:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command, client.lc_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
    return 0


def esmon_read_thread(client, stripe_num):
    """
    The thread doing read IO.
    """
    fpath = ("%s/%s_read" % (client.lc_mnt, client.lc_host.sh_hostname))
    command = ("lfs setstripe -c %s %s" % (stripe_num, fpath))
    retval = client.lc_host.sh_run(command)
    if retval.cr_exit_status:
        logging.debug("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      client.lc_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = ("dd if=/dev/zero of=%s bs=1M count=4096" % (fpath))
    retval = client.lc_host.sh_run(command)
    if retval.cr_exit_status:
        logging.debug("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      client.lc_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    while True:
        command = ("dd if=%s of=/dev/zero bs=1M count=4096" % (fpath))
        retval = client.lc_host.sh_run(command)
        if retval.cr_exit_status != 0:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command, client.lc_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
    return 0


def esmon_mdtest_thread(client, number):
    """
    The thread doing mdtest.
    """
    while True:
        command = ("mdtest -c -n %d -d %s" % (number, client.lc_mnt))
        retval = client.lc_host.sh_run(command)
        if retval.cr_exit_status != 0:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command, client.lc_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
    return 0


def esmon_remove_allfiles(client):
    """
    Test of remove all files
    """
    command = ("rm -rf %s/*" % (client.lc_mnt))
    retval = client.lc_host.sh_run(command)
    if retval.cr_exit_status:
        logging.debug("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      client.lc_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1
    return 0


def esmon_launch_ioload_daemon(lustre_fs):
    """
    Launch IO laod daemon.
    """
    # pylint: disable=unused-variable
    clinum = len(lustre_fs.lf_clients)
    if clinum < 3:
        logging.error("Need 3 Lustre clients at least to perform I/O "
                      "loading test")

    ostnum = len(lustre_fs.lf_osts)
    count = 0
    for client_index, client in lustre_fs.lf_clients.iteritems():
        if count == 0:
            ret = esmon_remove_allfiles(client)
            if ret:
                return ret
            utils.thread_start(esmon_write_thread, (client, ostnum))
        elif count == 1:
            utils.thread_start(esmon_read_thread, (client, ostnum))
        elif count == 2:
            utils.thread_start(esmon_mdtest_thread, (client, 10000))
        else:
            break
        count = count + 1

    return 0


def esmon_io_loading(workspace, config, confpath):
    """
    Start the I/O
    """
    # pylint: disable=too-many-locals,unused-argument,too-many-return-statements
    # pylint: disable=too-many-branches,too-many-statements
    ssh_host_configs = esmon_common.config_value(config, esmon_common.CSTR_SSH_HOST)
    if ssh_host_configs is None:
        logging.error("can NOT find [%s] in the config file, "
                      "please correct file [%s]",
                      esmon_common.CSTR_SSH_HOST, confpath)
        return -1

    hosts = {}
    for host_config in ssh_host_configs:
        host_id = host_config["host_id"]
        if host_id is None:
            logging.error("can NOT find [host_id] in the config of a "
                          "SSH host, please correct file [%s]",
                          confpath)
            return -1

        hostname = esmon_common.config_value(host_config, "hostname")
        if hostname is None:
            logging.error("can NOT find [hostname] in the config of SSH host "
                          "with ID [%s], please correct file [%s]",
                          host_id, confpath)
            return -1

        ssh_identity_file = esmon_common.config_value(host_config, "ssh_identity_file")

        if host_id in hosts:
            logging.error("multiple SSH hosts with the same ID [%s], please "
                          "correct file [%s]", host_id, confpath)
            return -1
        host = ssh_host.SSHHost(hostname, ssh_identity_file)
        hosts[host_id] = host

    # Parse the Lustre client configuration.
    lustre_configs = esmon_common.config_value(config, esmon_common.CSTR_LUSTRES)
    if lustre_configs is None:
        logging.error("no [%s] is configured, please correct file [%s]",
                      esmon_common.CSTR_LUSTRES, confpath)
        return -1

    for lustre_config in lustre_configs:
        # Parse general configs of Lustre file system
        fsname = esmon_common.config_value(lustre_config, esmon_common.CSTR_FSNAME)
        if fsname is None:
            logging.error("no [%s] is configured, please correct file [%s]",
                          esmon_common.CSTR_FSNAME, confpath)
            return -1

        lazy_prepare = esmon_common.config_value(lustre_config, esmon_common.CSTR_LAZY_PREPARE)
        if lazy_prepare is None:
            lazy_prepare = False
            logging.info("no [%s] is configured for fs [%s], using default value false",
                         esmon_common.CSTR_LAZY_PREPARE, fsname)
            return -1

        lustre_fs = lustre.LustreFilesystem(fsname)
        lustre_hosts = {}

        # Parse OST configs
        ost_configs = esmon_common.config_value(lustre_config, esmon_common.CSTR_OSTS)
        if ost_configs is None:
            logging.error("no [%s] is configured, please correct file [%s]",
                          esmon_common.CSTR_OSTS, confpath)
            return -1

        for ost_config in ost_configs:
            ost_index = esmon_common.config_value(ost_config, esmon_common.CSTR_INDEX)
            if ost_index is None:
                logging.error("no [%s] is configured, please correct file [%s]",
                              esmon_common.CSTR_INDEX, confpath)
                return -1

            host_id = esmon_common.config_value(ost_config, esmon_common.CSTR_HOST_ID)
            if host_id is None:
                logging.error("no [%s] is configured, please correct file [%s]",
                              esmon_common.CSTR_HOST_ID, confpath)
                return -1

            if host_id not in hosts:
                logging.error("no host with ID [%s] is configured in hosts, "
                              "please correct file [%s]",
                              host_id, confpath)
                return -1

            device = esmon_common.config_value(ost_config, esmon_common.CSTR_DEVICE)
            if device is None:
                logging.error("no [%s] is configured, please correct file [%s]",
                              esmon_common.CSTR_DEVICE, confpath)
                return -1

            host = hosts[host_id]
            lustre_host = lustre.LustreServerHost(host.sh_hostname,
                                                  identity_file=host.sh_identity_file,
                                                  local=host.sh_local,
                                                  host_id=host_id)

            if host_id not in lustre_hosts:
                lustre_hosts[host_id] = lustre_host

            mnt = "/mnt/%s_ost_%s" % (fsname, ost_index)
            lustre.LustreOST(lustre_fs, ost_index, lustre_host, device, mnt)

        # Parse client configs
        client_configs = esmon_common.config_value(lustre_config,
                                                   esmon_common.CSTR_CLIENTS)
        if client_configs is None:
            logging.error("no [%s] is configured, please correct file [%s]",
                          esmon_common.CSTR_CLIENTS, confpath)
            return -1

        for client_config in client_configs:
            host_id = esmon_common.config_value(client_config, esmon_common.CSTR_HOST_ID)
            if host_id is None:
                logging.error("no [%s] is configured, please correct file [%s]",
                              esmon_common.CSTR_HOST_ID, confpath)
                return -1

            if host_id not in hosts:
                logging.error("no host with [%s] is configured in hosts, "
                              "please correct file [%s]",
                              host_id, confpath)
                return -1

            mnt = esmon_common.config_value(client_config, esmon_common.CSTR_MNT)
            if mnt is None:
                logging.error("no [%s] is configured, please correct file [%s]",
                              esmon_common.CSTR_MNT, confpath)
                return -1

            host = hosts[host_id]
            lustre_host = lustre.LustreServerHost(host.sh_hostname,
                                                  identity_file=host.sh_identity_file,
                                                  local=host.sh_local,
                                                  host_id=host_id)

            if host_id not in lustre_hosts:
                lustre_hosts[host_id] = lustre_host
            lustre.LustreClient(lustre_fs, host, mnt)

        ret = esmon_launch_ioload_daemon(lustre_fs)
        if ret:
            return ret

    return 0


def esmon_ioload_locked(workspace, confpath):
    """
    Start to generate I/O load with configure lock.
    """
    # pylint: disable=bare-except
    save_fpath = workspace + "/" + ESMON_TEST_CONFIG_FNAME
    logging.debug("copying config file from [%s] to [%s]", confpath,
                  save_fpath)
    shutil.copyfile(confpath, save_fpath)

    config_fd = open(confpath)
    ret = 0
    try:
        config = yaml.load(config_fd)
    except:
        logging.error("not able to load [%s] as yaml file: %s", confpath,
                      traceback.format_exc())
        ret = -1
    config_fd.close()
    if ret:
        return -1

    try:
        ret = esmon_io_loading(workspace, config, confpath)
    except:
        ret = -1
        logging.error("exception: %s", traceback.format_exc())

    return ret


def esmon_ioload(workspace, confpath):
    """
    Start I/O loading
    """
    # pylint: disable=bare-except
    lock_file = confpath + ".lock"
    lock = filelock.FileLock(lock_file)
    try:
        with lock.acquire(timeout=0):
            try:
                ret = esmon_ioload_locked(workspace, confpath)
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
    Generate I/O load for the Lustre file system
    """
    confpath = ESMON_TEST_CONFIG

    if len(sys.argv) == 2:
        confpath = sys.argv[1]
    elif len(sys.argv) > 2:
        usage()
        sys.exit(-1)

    identity = time_util.local_strftime(time_util.utcnow(), "%Y-%m-%d-%H_%M_%S")
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

    print("Started I/O load testing for ESMON using config [%s], "
          "please check [%s] for more log" %
          (confpath, workspace))
    utils.configure_logging(workspace)

    console_handler = utils.LOGGING_HANLDERS["console"]
    console_handler.setLevel(logging.DEBUG)

    ret = esmon_ioload(workspace, confpath)
    if ret:
        logging.error("test failed, please check [%s] for more log\n",
                      workspace)
        sys.exit(ret)

    while True:
        time.sleep(10)

    logging.info("Finished I/O load testing, please check [%s] "
                 "for more log", workspace)
    sys.exit(0)
