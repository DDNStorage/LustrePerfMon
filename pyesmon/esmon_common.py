# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Common library for ESMON
"""
import logging

# Local libs
from pyesmon import utils

ESMON_INSTALL_CONFIG_FNAME = "esmon_install.conf"
RPM_PATTERN_RHEL7 = r"^%s-\d.+(\.el7|).*\.(x86_64|noarch)\.rpm$"
RPM_PATTERN_RHEL6 = r"^%s-\d.+(\.el6|).*\.(x86_64|noarch)\.rpm$"
PATTERN_PYTHON_LIBRARY = r"^%s-\d+\.\d+\.\d+\.tar\.gz$"
DEFAULT_INFLUXDB_PATH = "/esmon/influxdb"

# Config strings

# ESMON_CONFIG_CSTR_PATH can be set to None
ESMON_CONFIG_CSTR_NONE = "None"

# Config used by esmon_install.conf
CSTR_CONTINUOUS_QUERY_INTERVAL = "continuous_query_interval"
CSTR_CONTROLLER0_HOST = "controller0_host"
CSTR_CONTROLLER1_HOST = "controller1_host"
CSTR_CLIENT_HOSTS = "client_hosts"
CSTR_CLIENTS_REINSTALL = "clients_reinstall"
CSTR_COLLECT_INTERVAL = "collect_interval"
CSTR_DROP_DATABASE = "drop_database"
CSTR_ENABLE_DISK = "enable_disk"
CSTR_ERASE_INFLUXDB = "erase_influxdb"
CSTR_HOST_ID = "host_id"
CSTR_HOSTNAME = "hostname"
CSTR_IME = "ime"
CSTR_INFINIBAND = "infiniband"
CSTR_INFLUXDB_PATH = "influxdb_path"
CSTR_ISO_PATH = "iso_path"
CSTR_LUSTRE_EXP_MDT = "lustre_exp_mdt"
CSTR_LUSTRE_EXP_OST = "lustre_exp_ost"
CSTR_LUSTRE_MDS = "lustre_mds"
CSTR_LUSTRE_OSS = "lustre_oss"
CSTR_NAME = "name"
CSTR_REINSTALL = "reinstall"
CSTR_SERVER_HOST = "server_host"
CSTR_SFAS = "sfas"
CSTR_SSH_HOSTS = "ssh_hosts"
CSTR_SSH_IDENTITY_FILE = "ssh_identity_file"

# Config used by esmon_test.conf
CSTR_BACKFS_TYPE = "backfs_type"
CSTR_SKIP_INSTALL_TEST = "skip_install_test"

CSTR_LUSTRES = "lustres"
CSTR_FSNAME = "fsname"
CSTR_MDTS = "mdts"
CSTR_OSTS = "osts"
CSTR_DEVICE = "device"
CSTR_NID = "nid"
CSTR_IS_MGS = "is_mgs"
CSTR_INDEX = "index"
CSTR_LUSTRE_RPM_DIR = "lustre_rpm_dir"
CSTR_E2FSPROGS_RPM_DIR = "e2fsprogs_rpm_dir"
CSTR_LAZY_PREPARE = "lazy_prepare"
CSTR_CLIENTS = "clients"
CSTR_MNT = "mnt"
CSTR_DISTRO = "distro"
CSTR_HOST_IPS = "ips"
CSTR_TEMPLATES = "templates"
CSTR_INTERNET = "internet"
CSTR_RAM_SIZE = "ram_size"
CSTR_DISK_SIZES = "disk_sizes"
CSTR_NETWORK_CONFIGS = "network_configs"
CSTR_ISO = "iso"
CSTR_SERVER_HOST_ID = "server_host_id"
CSTR_IMAGE_DIR = "image_dir"
CSTR_TEMPLATE_HOSTNAME = "template_hostname"
CSTR_IP = "ip"
CSTR_HOSTS = "hosts"
CSTR_CLEANUP = "cleanup"
CSTR_LUSTRE_DEFAULT_VERSION = "lustre_default_version"

GRAFANA_STATUS_PANEL = "Grafana_Status_panel"
GRAFANA_PIECHART_PANEL = "piechart-panel"
GRAFANA_SAVANTLY_HEATMAP_PANEL = "savantly-heatmap-panel"
GRAFANA_PLUGIN_GITS = {}
GRAFANA_PLUGIN_GITS[GRAFANA_STATUS_PANEL] = "https://github.com/Vonage/Grafana_Status_panel.git"
GRAFANA_PLUGIN_GITS[GRAFANA_PIECHART_PANEL] = "https://github.com/grafana/piechart-panel.git"
GRAFANA_PLUGIN_GITS[GRAFANA_SAVANTLY_HEATMAP_PANEL] = ("https://github.com/savantly-net/"
                                                       "grafana-heatmap.git")


def config_value(config, key, mapping_dict=None):
    """
    Return value of a key in config
    """
    if key not in config:
        return None
    value = config[key]
    if mapping_dict is not None and value in mapping_dict:
        value = mapping_dict[value]
    return value


def clone_src_from_git(build_dir, git_url, branch,
                       ssh_identity_file=None):
    """
    Get the soure codes from Git server.
    """
    command = ("rm -fr %s && mkdir -p %s && git init %s" %
               (build_dir, build_dir, build_dir))
    retval = utils.run(command)
    if retval.cr_exit_status != 0:
        logging.error("failed to run command [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command, retval.cr_exit_status, retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = ("cd %s && git config remote.origin.url %s && "
               "GIT_SSH_COMMAND=\"ssh -i /root/.ssh/id_dsa\" "
               "git fetch --tags --progress %s "
               "+refs/heads/*:refs/remotes/origin/* && "
               "git checkout origin/%s -f" %
               (build_dir, git_url, git_url, branch))
    if ssh_identity_file is not None:
        # Git 2.3.0+ has GIT_SSH_COMMAND
        command = ("ssh-agent sh -c 'ssh-add " + ssh_identity_file +
                   " && " + command + "'")

    retval = utils.run(command)
    if retval.cr_exit_status != 0:
        logging.error("failed to run command [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command, retval.cr_exit_status, retval.cr_stdout,
                      retval.cr_stderr)
        return -1
    return 0

# python-requests, PyYAML, python2-filelock, python-slugify, pytz,
# python-dateutil are needed by esmon_install.
# python-chardet and python-urllib3 are needed by python-requests.
# python-backports-ssl_match_hostname and python-six are needed by
# python-urllib3.
# python-backports is needed by python-backports-ssl_match_hostname.
# libyaml is needed by PyYAML.
ESMON_INSTALL_DEPENDENT_RPMS = ["rsync",
                                "python-chardet",
                                "python-backports",
                                "python-backports-ssl_match_hostname",
                                "python-six",
                                "python-urllib3",
                                "libyaml",
                                "PyYAML",
                                "python-requests",
                                "python2-filelock",
                                "python-slugify",
                                "pytz",
                                "python-dateutil"]

# patch is needed to patch /etc/influxdb/influxdb.conf file
# fontconfig and urw-fonts are needed by grafana-*.x86_64.rpm
# fontpackages-filesystem, bitmap-console-fonts(font(:lang=en)) are
# needed by fontconfig
# xorg-x11-font-utils is needed by urw-fonts
# libXfont is needed by xorg-x11-font-utils
# libfontenc is needed by libXfont
ESMON_SERVER_DEPENDENT_RPMS = ["rsync", "patch", "fontpackages-filesystem",
                               "bitmap-console-fonts", "fontconfig",
                               "libfontenc", "libXfont",
                               "xorg-x11-font-utils", "urw-fonts"]


# yajl is needed by collectd
# lm_sensors-libs is needed by collectd-sensors
# zeromq3 is needed by collectd-ssh
# openpgm is needed by zeromq3
ESMON_CLIENT_DEPENDENT_RPMS = ["rsync", "yajl", "lm_sensors-libs", "openpgm", "zeromq3"]
