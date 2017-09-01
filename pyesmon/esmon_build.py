# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for building ESMON
"""
import sys
import logging
import os
import re

# Local libs
from pyesmon import utils
from pyesmon import ssh_host


def usage():
    """
    Print usage string
    """
    utils.eprint("Usage: %s" %
                 sys.argv[0])

def build():
    """
    Build the ISO
    """
    # pylint: disable=too-many-locals,too-many-return-statements
    # pylint: disable=too-many-branches,too-many-statements
    local_host = ssh_host.SSHHost("localhost", local=True)
    command = ("rpm -e zeromq-devel")
    local_host.sh_run(command)

    command = ("yum install libgcrypt-devel libtool-ltdl-devel curl-devel "
               "libxml2-devel yajl-devel libdbi-devel libpcap-devel "
               "OpenIPMI-devel iptables-devel libvirt-devel "
               "libvirt-devel libmemcached-devel mysql-devel libnotify-devel "
               "libesmtp-devel postgresql-devel rrdtool-devel "
               "lm_sensors-devel net-snmp-devel libcap-devel "
               "lvm2-devel libmodbus-devel libmnl-devel iproute-devel "
               "hiredis-devel libatasmart-devel protobuf-c-devel "
               "mosquitto-devel gtk2-devel openldap-devel "
               "zeromq3-devel libssh2-devel rrdtool-devel rrdtool "
               "createrepo mkisofs yum-utils redhat-lsb unzip "
               "epel-release perl-Regexp-Common python-pep8 pylint "
               "lua-devel -y")
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

    workspace = os.getcwd()
    collectd_git_path = workspace + "/../" + "collectd.git"
    command = "test -e %s" % collectd_git_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = "git clone git://10.128.7.3/collectd.git %s" % collectd_git_path
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
    else:
        command = ("cd %s && git checkout master && "
                   "git branch -D master-ddn && "
                   "git pull && git checkout master-ddn" %
                   collectd_git_path)
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

    grafana_rpm_path = workspace + "/../" + "grafana-4.4.1-1.x86_64.rpm"
    command = "test -e %s" % grafana_rpm_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = ("cd %s && wget --no-check-certificate "
                   "https://s3-us-west-2.amazonaws.com/grafana-releases"
                   "/release/grafana-4.4.1-1.x86_64.rpm" % workspace)
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

    influxdb_rpm_path = workspace + "/../" + "influxdb-1.3.1.x86_64.rpm"
    command = "test -e %s" % influxdb_rpm_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = ("cd %s && curl -LO https://dl.influxdata.com/influxdb/"
                   "releases/influxdb-1.3.1.x86_64.rpm" % workspace)
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

    python_libs = {}
    name = "certifi-2017.7.27.1.tar.gz"
    url = ("https://pypi.python.org/packages/20/d0/"
           "3f7a84b0c5b89e94abbd073a5f00c7176089f526edb056686751d5064cbd/"
           "certifi-2017.7.27.1.tar.gz#md5=48e8370da8b370a16e223ee9c7b6b063")
    python_libs[name] = url

    name = "influxdb-4.1.1.tar.gz"
    url = ("https://pypi.python.org/packages/e1/af/"
           "94faea244de2a73b7a0087637660db2d638edaae58f22d3f0d0d219ad8b7/"
           "influxdb-4.1.1.tar.gz#md5=a59916ef8882b239eb04033775908bd8")
    python_libs[name] = url

    name = "six-1.10.0.tar.gz"
    url = ("https://pypi.python.org/packages/b3/b2/"
           "238e2590826bfdd113244a40d9d3eb26918bd798fc187e2360a8367068db/"
           "six-1.10.0.tar.gz#md5=34eed507548117b2ab523ab14b2f8b55")
    python_libs[name] = url

    name = "urllib3-1.22.tar.gz"
    url = ("https://pypi.python.org/packages/ee/11/"
           "7c59620aceedcc1ef65e156cc5ce5a24ef87be4107c2b74458464e437a5d/"
           "urllib3-1.22.tar.gz#md5=0da7bed3fe94bf7dc59ae37885cc72f7")
    python_libs[name] = url

    name = "pytz-2017.2.tar.gz"
    url = ("https://pypi.python.org/packages/a4/09/"
           "c47e57fc9c7062b4e83b075d418800d322caa87ec0ac21e6308bd3a2d519/"
           "pytz-2017.2.zip#md5=f89bde8a811c8a1a5bac17eaaa94383c")
    python_libs[name] = url

    name = "requests-2.18.4.tar.gz"
    url = ("https://pypi.python.org/packages/b0/e1/"
           "eab4fc3752e3d240468a8c0b284607899d2fbfb236a56b7377a329aa8d09/"
           "requests-2.18.4.tar.gz#md5=081412b2ef79bdc48229891af13f4d82")
    python_libs[name] = url

    name = "python-dateutil-2.6.1.tar.gz"
    url = ("https://pypi.python.org/packages/54/bb/"
           "f1db86504f7a49e1d9b9301531181b00a1c7325dc85a29160ee3eaa73a54/"
           "python-dateutil-2.6.1.tar.gz#md5=db38f6b4511cefd76014745bb0cc45a4")
    python_libs[name] = url

    name = "idna-2.6.tar.gz"
    url = ("https://pypi.python.org/packages/f4/bd/"
           "0467d62790828c23c47fc1dfa1b1f052b24efdf5290f071c7a91d0d82fd3/"
           "idna-2.6.tar.gz#md5=c706e2790b016bd0ed4edd2d4ba4d147")
    python_libs[name] = url

    name = "chardet-3.0.4.tar.gz"
    url = ("https://pypi.python.org/packages/fc/bb/"
           "a5768c230f9ddb03acc9ef3f0d4a3cf93462473795d18e9535498c8f929d/"
           "chardet-3.0.4.tar.gz#md5=7dd1ba7f9c77e32351b0a0cfacf4055c")
    python_libs[name] = url

    name = "Unidecode-0.04.21.tar.gz"
    url = ("https://pypi.python.org/packages/0e/26/"
           "6a4295c494e381d56bba986893382b5dd5e82e2643fc72e4e49b6c99ce15/"
           "Unidecode-0.04.21.tar.gz#md5=089031ed00637d7078f33dad9d6a3c12")
    python_libs[name] = url

    name = "python-slugify-1.2.4.tar.gz"
    url = ("https://pypi.python.org/packages/9f/b0/"
           "2723356c20fb01b0e09f6ee03c0c629f4e30811e7d92ebd15453d648e5f0/"
           "python-slugify-1.2.4.tar.gz#md5=338ab6beafcea746161f07b6173a9031")
    python_libs[name] = url

    dependent_rpm_dir = workspace + "/../rpms"
    pylibs_name = "pylibs"
    pylibs_dir = dependent_rpm_dir + "/" + pylibs_name

    command = ("mkdir -p %s" % (pylibs_dir))
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

    for name, url in python_libs.iteritems():
        path = pylibs_dir + "/" + name
        command = "test -e %s" % path
        retval = local_host.sh_run(command)
        if retval.cr_exit_status:
            command = ("cd %s && wget %s" % (pylibs_dir, url))
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

    # Special handling for pytz
    command = "test -e %s/pytz-2017.2.tar.gz" % pylibs_dir
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = ("cd %s && unzip pytz-2017.2.zip && "
                   "tar -cf pytz-2017.2.tar.gz && "
                   "rm -fr pytz-2017.2.zip pytz-2017.2" % pylibs_dir)
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

    pylib_files = os.listdir(pylibs_dir)
    for name in python_libs.iterkeys():
        pylib_files.remove(name)

    if len(pylib_files) != 0:
        logging.error("find unknown files under directory [%s]: %s",
                      pylibs_dir, pylib_files)
        return -1

    dependent_rpms = ["openpgm", "yajl", "zeromq3", "fontconfig", "glibc",
                      "glibc-common", "glibc-devel", "fontpackages-filesystem",
                      "glibc-headers", "glibc-static", "libfontenc", "libtool",
                      "libtool-ltdl", "libtool-ltdl-devel", "libXfont", "libyaml",
                      "openpgm", "patch", "python2-filelock", "python2-pip",
                      "python-backports", "python-backports-ssl_match_hostname",
                      "python-dateutil", "python-requests", "python-setuptools",
                      "python-six", "python-urllib3", "PyYAML", "rsync", "urw-fonts",
                      "xorg-x11-font-utils", "python-chardet", "python-idna",
                      "lm_sensors-libs", "lm_sensors"]

    dependent_files = os.listdir(dependent_rpm_dir)
    dependent_files.remove(pylibs_name)

    for rpm_name in dependent_rpms:
        #rpm_pattern = (r"^%s.+\.(x86_64|noarch)\.rpm$" % rpm_name)
        rpm_pattern = (r"^%s-\d.+\.el7.*\.(x86_64|noarch)\.rpm$" % rpm_name)
        rpm_regular = re.compile(rpm_pattern)
        not_matched = True
        for filename in dependent_files[:]:
            match = rpm_regular.match(filename)
            if match:
                dependent_files.remove(filename)
                not_matched = False
                logging.debug("matched pattern [%s] with fname [%s]",
                              rpm_pattern, filename)
                break

        if not_matched:
            logging.debug("not find RPM with pattern [%s], downloading",
                          rpm_pattern)

            command = (r"cd %s && yumdownloader -x \*i686 --archlist=x86_64 %s" %
                       (dependent_rpm_dir, rpm_name))
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

    grafana_status_panel = "Grafana_Status_panel"
    grafana_status_panel_git_path = dependent_rpm_dir + "/" + grafana_status_panel
    command = "test -e %s" % grafana_status_panel_git_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = ("git clone https://github.com/Vonage/"
                   "Grafana_Status_panel.git %s" %
                   grafana_status_panel_git_path)
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
    else:
        command = ("cd %s && git pull" % grafana_status_panel_git_path)
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

    dependent_files.remove(grafana_status_panel)
    if len(dependent_files) != 0:
        logging.error("find unknown files under directory [%s]: %s",
                      dependent_rpm_dir, dependent_files)
        return -1

    command = ("cd %s && rm esmon-*.tar.bz2 esmon-*.tar.gz -f && "
               "sh autogen.sh && "
               "./configure --with-collectd=%s --with-grafana=%s "
               "--with-influxdb=%s --with-dependent-rpms=%s && "
               "make" %
               (workspace, collectd_git_path, grafana_rpm_path,
                influxdb_rpm_path, dependent_rpm_dir))
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

    return 0


def main():
    """
    Install Exascaler monitoring
    """
    reload(sys)
    sys.setdefaultencoding("utf-8")

    if len(sys.argv) != 1:
        usage()
        sys.exit(-1)

    logging.root.setLevel(logging.DEBUG)

    ret = build()

    sys.exit(ret)
