# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for building ESMON
"""
import sys
import logging
import traceback
import os
import re
import yaml

# Local libs
from pyesmon import utils
from pyesmon import ssh_host

ESMON_BUILD_CONFIG = "/etc/esmon_build.conf"
ESMON_BUILD_LOG_DIR = "/var/log/esmon_build"


def download_dependent_rpms(host, dependent_dir, distro):
    """
    Download dependent RPMs
    """
    dependent_rpms = ["openpgm", "yajl", "zeromq3", "fontconfig", "glibc",
                      "glibc-common", "glibc-devel", "fontpackages-filesystem",
                      "glibc-headers", "glibc-static", "libfontenc", "libtool",
                      "libtool-ltdl", "libtool-ltdl-devel", "libXfont", "libyaml",
                      "patch", "PyYAML", "rsync", "urw-fonts",
                      "xorg-x11-font-utils", "python-chardet",
                      "lm_sensors-libs", "lm_sensors"]
    if distro == ssh_host.DISTRO_RHEL7:
        python_rpms = ["python2-filelock", "python2-pip",
                       "python-backports",
                       "python-backports-ssl_match_hostname",
                       "python-dateutil", "python-requests",
                       "python-setuptools", "python-six", "python-urllib3",
                       "python-idna"]
        dependent_rpms.extend(python_rpms)

    rpm_dir = dependent_dir + "/RPMS/" + distro
    command = ("mkdir -p %s" % (rpm_dir))
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

    existing_rpm_fnames = os.listdir(rpm_dir)
    for rpm_name in dependent_rpms:
        rpm_pattern = (r"^%s-\d.+\.el7.*\.(x86_64|noarch)\.rpm$" % rpm_name)
        rpm_regular = re.compile(rpm_pattern)
        not_matched = True
        for filename in existing_rpm_fnames[:]:
            match = rpm_regular.match(filename)
            if match:
                existing_rpm_fnames.remove(filename)
                not_matched = False
                logging.debug("matched pattern [%s] with fname [%s]",
                              rpm_pattern, filename)
                break

        if not_matched:
            logging.debug("not find RPM with pattern [%s], downloading",
                          rpm_pattern)

            command = (r"cd %s && yumdownloader -x \*i686 --archlist=x86_64 %s" %
                       (rpm_dir, rpm_name))
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

    # TODO: add more strict check later for all distros
    if distro == ssh_host.DISTRO_RHEL7 and len(existing_rpm_fnames) != 0:
        logging.error("find unknown files under directory [%s]: %s",
                      dependent_dir, existing_rpm_fnames)
        return -1
    return 0


def centos6_build(centos6_host, local_host, collectd_git_path, rpm_dir,
                  rpm_el6_basename, dependent_dir):
    """
    Build on CentOS6 host
    """
    # pylint: disable=too-many-return-statements,too-many-arguments
    distro = centos6_host.sh_distro()
    if distro != ssh_host.DISTRO_RHEL6:
        logging.error("host [%s] is not RHEL6/CentOS6 host",
                      centos6_host.sh_hostname)
        return -1

    command = ("rpm -e zeromq-devel")
    centos6_host.sh_run(command)

    command = ("yum install libgcrypt-devel libtool-ltdl-devel curl-devel "
               "libxml2-devel yajl-devel libdbi-devel libpcap-devel "
               "OpenIPMI-devel iptables-devel libvirt-devel "
               "libvirt-devel libmemcached-devel mysql-devel libnotify-devel "
               "libesmtp-devel postgresql-devel rrdtool-devel "
               "lm_sensors-libs lm_sensors-devel net-snmp-devel libcap-devel "
               "lvm2-devel libmodbus-devel libmnl-devel iproute-devel "
               "hiredis-devel libatasmart-devel protobuf-c-devel "
               "mosquitto-devel gtk2-devel openldap-devel "
               "zeromq3-devel libssh2-devel rrdtool-devel rrdtool "
               "createrepo mkisofs yum-utils redhat-lsb unzip "
               "epel-release perl-Regexp-Common python-pep8 pylint "
               "lua-devel byacc ganglia-devel -y")
    retval = centos6_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      centos6_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    identity = utils.local_strftime(utils.utcnow(), "%Y-%m-%d-%H_%M_%S")
    workspace = ESMON_BUILD_LOG_DIR + "/" + identity
    command = "mkdir -p %s" % workspace
    retval = centos6_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      centos6_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    ret = centos6_host.sh_send_file(collectd_git_path, workspace)
    if ret:
        logging.error("failed to send file [%s] on local host to "
                      "directory [%s] on host [%s]",
                      collectd_git_path, workspace,
                      centos6_host.sh_hostname)
        return -1

    collectd_path = workspace + "/" + "collectd.git"
    command = ("cd %s && mkdir -p libltdl/config && sh ./build.sh && "
               "./configure --enable-write_tsdb --enable-dist --enable-nfs "
               "--disable-java --disable-amqp --disable-gmond --disable-nut "
               "--disable-pinba --disable-ping --disable-varnish "
               "--disable-dpdkstat --disable-turbostat && "
               "make && make dist-bzip2 && "
               "mkdir {BUILD,RPMS,SOURCES,SRPMS} && "
               "mv collectd-*.tar.bz2 SOURCES" % collectd_path)
    retval = centos6_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      centos6_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = ('cd %s && '
               'rpmbuild -ba --with write_tsdb --with nfs --without java '
               '--without amqp --without gmond --without nut --without pinba '
               '--without ping --without varnish --without dpdkstat '
               '--without turbostat --without redis --without write_redis '
               '--define "_topdir %s" '
               '--define="rev $(git rev-parse --short HEAD)" '
               'contrib/redhat/collectd.spec' %
               (collectd_path, collectd_path))
    retval = centos6_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      centos6_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = ("rm %s/%s -fr" % (rpm_dir, rpm_el6_basename))
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

    host_rpm_dir = collectd_path + "/RPMS/x86_64"
    ret = centos6_host.sh_get_file(host_rpm_dir, rpm_dir)
    if ret:
        logging.error("failed to get Collectd RPMs from path [%s] on host "
                      "[%s]", host_rpm_dir, centos6_host.sh_hostname)
        return -1

    command = ("mv %s/x86_64 %s/%s" % (rpm_dir, rpm_dir, rpm_el6_basename))
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

    command = ("rm -rf %s" % workspace)
    retval = centos6_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      centos6_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    ret = download_dependent_rpms(centos6_host, dependent_dir,
                                  ssh_host.DISTRO_RHEL6)
    if ret:
        logging.error("failed to download depdendent RPMs")
        return ret

    return 0


def config_value(config, key):
    """
    Return value of a key in config
    """
    if key not in config:
        return None
    return config[key]


def esmon_do_build(config, config_fpath):
    """
    Build the ISO
    """
    # pylint: disable=too-many-locals,too-many-return-statements
    # pylint: disable=too-many-branches,too-many-statements
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

    centos6_host_config = config_value(config, "centos6_host")
    if hostname is None:
        logging.error("can NOT find [centos6_host] in the config file [%s], "
                      "please correct it", config_fpath)
        return -1

    centos6_host_id = config_value(centos6_host_config, "host_id")
    if centos6_host_id is None:
        logging.error("can NOT find [host_id] in the config of [centos6_host], "
                      "please correct file [%s]", config_fpath)
        return -1

    if centos6_host_id not in hosts:
        logging.error("SSH host with ID [%s] is NOT configured in "
                      "[ssh_hosts], please correct file [%s]",
                      centos6_host_id, config_fpath)
        return -1
    centos6_host = hosts[centos6_host_id]

    local_host = ssh_host.SSHHost("localhost", local=True)
    distro = local_host.sh_distro()
    if distro != ssh_host.DISTRO_RHEL7:
        logging.error("build can only be launched on RHEL7/CentOS7 host")
        return -1

    workspace = os.getcwd()
    dependent_dir = workspace + "/../dependent_dir"
    collectd_git_path = workspace + "/../" + "collectd.git"
    rpm_dir = dependent_dir + "/RPMS"
    command = ("mkdir -p %s" % (rpm_dir))
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
    rpm_el6_basename = ssh_host.DISTRO_RHEL6

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
        command = ("cd %s && git checkout master" %
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

        # The branch might already been deleted, so ignore the return failure
        command = ("cd %s && git branch -D master-ddn" %
                   collectd_git_path)
        retval = local_host.sh_run(command)
        if retval.cr_exit_status:
            logging.warning("failed to run command [%s] on host [%s], "
                            "ret = [%d], stdout = [%s], stderr = [%s]",
                            command,
                            local_host.sh_hostname,
                            retval.cr_exit_status,
                            retval.cr_stdout,
                            retval.cr_stderr)

        command = ("cd %s && git pull && git checkout master-ddn" %
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

    ret = centos6_build(centos6_host, local_host, collectd_git_path,
                        rpm_dir, rpm_el6_basename, dependent_dir)
    if ret:
        logging.error("failed to prepare RPMs of CentOS6 on host [%s]",
                      centos6_host.sh_hostname)
        return -1

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
               "lua-devel byacc -y")
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
        command = ("cd %s/.. && wget --no-check-certificate "
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
        command = ("cd %s/.. && curl -LO https://dl.influxdata.com/influxdb/"
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

    python_library_dict = {}
    name = "certifi-2017.7.27.1.tar.gz"
    url = ("https://pypi.python.org/packages/20/d0/"
           "3f7a84b0c5b89e94abbd073a5f00c7176089f526edb056686751d5064cbd/"
           "certifi-2017.7.27.1.tar.gz#md5=48e8370da8b370a16e223ee9c7b6b063")
    python_library_dict[name] = url

    name = "influxdb-4.1.1.tar.gz"
    url = ("https://pypi.python.org/packages/e1/af/"
           "94faea244de2a73b7a0087637660db2d638edaae58f22d3f0d0d219ad8b7/"
           "influxdb-4.1.1.tar.gz#md5=a59916ef8882b239eb04033775908bd8")
    python_library_dict[name] = url

    name = "six-1.10.0.tar.gz"
    url = ("https://pypi.python.org/packages/b3/b2/"
           "238e2590826bfdd113244a40d9d3eb26918bd798fc187e2360a8367068db/"
           "six-1.10.0.tar.gz#md5=34eed507548117b2ab523ab14b2f8b55")
    python_library_dict[name] = url

    name = "urllib3-1.22.tar.gz"
    url = ("https://pypi.python.org/packages/ee/11/"
           "7c59620aceedcc1ef65e156cc5ce5a24ef87be4107c2b74458464e437a5d/"
           "urllib3-1.22.tar.gz#md5=0da7bed3fe94bf7dc59ae37885cc72f7")
    python_library_dict[name] = url

    name = "pytz-2017.2.tar.gz"
    url = ("https://pypi.python.org/packages/a4/09/"
           "c47e57fc9c7062b4e83b075d418800d322caa87ec0ac21e6308bd3a2d519/"
           "pytz-2017.2.zip#md5=f89bde8a811c8a1a5bac17eaaa94383c")
    python_library_dict[name] = url

    name = "requests-2.18.4.tar.gz"
    url = ("https://pypi.python.org/packages/b0/e1/"
           "eab4fc3752e3d240468a8c0b284607899d2fbfb236a56b7377a329aa8d09/"
           "requests-2.18.4.tar.gz#md5=081412b2ef79bdc48229891af13f4d82")
    python_library_dict[name] = url

    name = "python-dateutil-2.6.1.tar.gz"
    url = ("https://pypi.python.org/packages/54/bb/"
           "f1db86504f7a49e1d9b9301531181b00a1c7325dc85a29160ee3eaa73a54/"
           "python-dateutil-2.6.1.tar.gz#md5=db38f6b4511cefd76014745bb0cc45a4")
    python_library_dict[name] = url

    name = "idna-2.6.tar.gz"
    url = ("https://pypi.python.org/packages/f4/bd/"
           "0467d62790828c23c47fc1dfa1b1f052b24efdf5290f071c7a91d0d82fd3/"
           "idna-2.6.tar.gz#md5=c706e2790b016bd0ed4edd2d4ba4d147")
    python_library_dict[name] = url

    name = "chardet-3.0.4.tar.gz"
    url = ("https://pypi.python.org/packages/fc/bb/"
           "a5768c230f9ddb03acc9ef3f0d4a3cf93462473795d18e9535498c8f929d/"
           "chardet-3.0.4.tar.gz#md5=7dd1ba7f9c77e32351b0a0cfacf4055c")
    python_library_dict[name] = url

    name = "Unidecode-0.04.21.tar.gz"
    url = ("https://pypi.python.org/packages/0e/26/"
           "6a4295c494e381d56bba986893382b5dd5e82e2643fc72e4e49b6c99ce15/"
           "Unidecode-0.04.21.tar.gz#md5=089031ed00637d7078f33dad9d6a3c12")
    python_library_dict[name] = url

    name = "python-slugify-1.2.4.tar.gz"
    url = ("https://pypi.python.org/packages/9f/b0/"
           "2723356c20fb01b0e09f6ee03c0c629f4e30811e7d92ebd15453d648e5f0/"
           "python-slugify-1.2.4.tar.gz#md5=338ab6beafcea746161f07b6173a9031")
    python_library_dict[name] = url

    python_library_name = "python_library"
    python_library_dir = dependent_dir + "/" + python_library_name

    command = ("mkdir -p %s" % (python_library_dir))
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

    python_library_existing_files = os.listdir(python_library_dir)
    for name in python_library_dict.iterkeys():
        if name in python_library_existing_files:
            python_library_existing_files.remove(name)

    for extra_fname in python_library_existing_files:
        logging.warning("find unknown file [%s] under directory [%s], removing",
                        extra_fname, python_library_dir)
        command = ("rm -fr %s/%s" % (python_library_dir, extra_fname))
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

    for name, url in python_library_dict.iteritems():
        path = python_library_dir + "/" + name
        command = "test -e %s" % path
        retval = local_host.sh_run(command)
        if retval.cr_exit_status:
            command = ("cd %s && wget %s" % (python_library_dir, url))
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
    command = "test -e %s/pytz-2017.2.tar.gz" % python_library_dir
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = ("cd %s && unzip pytz-2017.2.zip && "
                   "tar -czf pytz-2017.2.tar.gz pytz-2017.2 && "
                   "rm -fr pytz-2017.2.zip pytz-2017.2" % python_library_dir)
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

    python_library_existing_files = os.listdir(python_library_dir)
    for name in python_library_dict.iterkeys():
        python_library_existing_files.remove(name)

    if len(python_library_existing_files) != 0:
        logging.error("find unknown files under directory [%s]: %s",
                      python_library_dir, python_library_existing_files)
        return -1

    ret = download_dependent_rpms(local_host, dependent_dir,
                                  ssh_host.DISTRO_RHEL7)
    if ret:
        logging.error("failed to install depdendent RPMs")
        return ret

    grafana_status_panel = "Grafana_Status_panel"
    grafana_status_panel_git_path = dependent_dir + "/" + grafana_status_panel
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

    dependent_existing_files = os.listdir(dependent_dir)
    dependent_existing_files.remove(grafana_status_panel)
    dependent_existing_files.remove("RPMS")
    dependent_existing_files.remove(python_library_name)
    for extra_fname in dependent_existing_files:
        logging.warning("find unknown file [%s] under directory [%s], removing",
                        extra_fname, dependent_dir)
        command = ("rm -fr %s/%s" % (dependent_dir, extra_fname))
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

    command = ("cd %s && rm esmon-*.tar.bz2 esmon-*.tar.gz -f && "
               "sh autogen.sh && "
               "./configure --with-collectd=%s --with-grafana=%s "
               "--with-influxdb=%s --with-dependent-rpms=%s && "
               "make" %
               (workspace, collectd_git_path, grafana_rpm_path,
                influxdb_rpm_path, dependent_dir))
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


def esmon_build(config_fpath):
    """
    Build the ISO
    """
    # pylint: disable=bare-except
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

    return esmon_do_build(config, config_fpath)


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
    config_fpath = ESMON_BUILD_CONFIG

    if len(sys.argv) == 2:
        config_fpath = sys.argv[1]
    elif len(sys.argv) > 2:
        usage()
        sys.exit(-1)

    logging.root.setLevel(logging.DEBUG)

    ret = esmon_build(config_fpath)
    if ret:
        logging.error("build failed")
        sys.exit(ret)
    logging.info("Exascaler monistoring system is successfully built")
    sys.exit(0)
