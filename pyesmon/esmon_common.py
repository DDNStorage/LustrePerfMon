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

def config_value(config, key):
    """
    Return value of a key in config
    """
    if key not in config:
        return None
    return config[key]


def clone_src_from_git(build_dir, git_url, branch,
                       ssh_identity_file=None):
    """
    Get the Lustre soure codes from Git server.
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

# python-requests, PyYAML, python2-filelock, python-slugify are needed by esmon_install.
# python-chardet and python-urllib3 are needed by python-requests.
# python-backports-ssl_match_hostname and python-six are needed by python-urllib3.
# python-backports is needed by python-backports-ssl_match_hostname.
# libyaml is needed by PyYAML
# python-setuptools is needed by all python libaries that needs to be setuped in
# ESMON_INSTALL_PYTHON_LIBS
ESMON_INSTALL_DEPENDENT_RPMS = ["python-chardet", 
                                "python-backports",
                                "python-backports-ssl_match_hostname", "python-six",
                                "python-urllib3",
                                "libyaml",
                                "PyYAML",
                                "python-requests",
                                "python2-filelock",
                                "python-slugify",
                                "python-setuptools"]

ESMON_INSTALL_PYTHON_LIBS = ["influxdb"]

# patch is needed to patch /etc/influxdb/influxdb.conf file
# fontconfig and urw-fonts are needed by grafana-4.4.1-1.x86_64.rpm
# fontpackages-filesystem, bitmap-console-fonts(font(:lang=en)) are
# needed by fontconfig
ESMON_SERVER_DEPENDENT_RPMS = ["patch", "fontpackages-filesystem",
                               "bitmap-console-fonts", "fontconfig", "urw-fonts"]

ESMON_CLIENT_DEPENDENT_RPMS = ["openpgm", "yajl", "zeromq3", "fontconfig", "glibc",
                               "glibc-common", "glibc-devel", "fontpackages-filesystem",
                               "glibc-headers", "glibc-static", "libfontenc", "libtool",
                               "libtool-ltdl", "libtool-ltdl-devel", "libXfont", "libyaml",
                               "patch", "PyYAML", "rsync", "urw-fonts",
                               "xorg-x11-font-utils", "python-chardet",
                               "lm_sensors-libs"]
