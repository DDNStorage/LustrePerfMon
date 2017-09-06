# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for building ESMON
"""
# pylint: disable=too-many-lines
import sys
import logging
import traceback
import os
import re
import shutil
import yaml

# Local libs
from pyesmon import utils
from pyesmon import ssh_host

ESMON_BUILD_CONFIG_FNAME = "esmon_build.conf"
ESMON_BUILD_CONFIG = "/etc/" + ESMON_BUILD_CONFIG_FNAME
ESMON_BUILD_LOG_DIR = "/var/log/esmon_build"
DEPENDENT_STRING = "dependent"
COLLECTD_STRING = "collectd"
COLLECT_GIT_STRING = COLLECTD_STRING + ".git"
X86_64_STRING = "x86_64"
RPM_STRING = "RPMS"
RPM_PATH_STRING = RPM_STRING + "/" + X86_64_STRING
COPYING_STRING = "copying"
COLLECTD_RPM_NAMES = ["collectd", "collectd-disk", "collectd-filedata",
                      "collectd-ime", "collectd-sensors", "collectd-ssh",
                      "libcollectdclient"]

def download_dependent_rpms(host, dependent_dir):
    """
    Download dependent RPMs
    """
    # pylint: disable=too-many-locals,too-many-return-statements
    # pylint: disable=too-many-branches
    dependent_rpms = ["openpgm", "yajl", "zeromq3", "fontconfig", "glibc",
                      "glibc-common", "glibc-devel", "fontpackages-filesystem",
                      "glibc-headers", "glibc-static", "libfontenc", "libtool",
                      "libtool-ltdl", "libtool-ltdl-devel", "libXfont", "libyaml",
                      "patch", "PyYAML", "rsync", "urw-fonts",
                      "xorg-x11-font-utils", "python-chardet",
                      "lm_sensors-libs"]

    command = ("ls %s" % (dependent_dir))
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
    existing_rpm_fnames = retval.cr_stdout.split()

    command = "yum install -y"
    for rpm_name in dependent_rpms:
        command += " " + rpm_name

    # Install the RPM to get the fullname and checksum in db
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

    for rpm_name in dependent_rpms:
        command = "rpm -q %s" % rpm_name
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

        rpm_fullname = retval.cr_stdout.strip()
        sha256sum = host.sh_yumdb_sha256(rpm_fullname)
        if sha256sum is None:
            logging.error("failed to get sha256 of RPM [%s] on host [%s]",
                          rpm_fullname, host.sh_hostname)
            return -1

        rpm_filename = rpm_fullname + ".rpm"
        fpath = dependent_dir + "/" + rpm_filename
        found = False
        for filename in existing_rpm_fnames[:]:
            if filename == rpm_filename:
                file_sha256sum = host.sh_sha256sum(fpath)
                if sha256sum != file_sha256sum:
                    logging.debug("found RPM [%s] with wrong sha256sum, "
                                  "deleting it", fpath)
                    ret = host.sh_remove_file(fpath)
                    if ret:
                        return -1
                    break

                logging.debug("found RPM [%s] with correct sha256sum", fpath)
                existing_rpm_fnames.remove(filename)
                found = True
                break

        if found:
            continue

        logging.debug("downloading RPM [%s] on host [%s]", fpath,
                      host.sh_hostname)

        command = (r"cd %s && yumdownloader -x \*i686 --archlist=x86_64 %s" %
                   (dependent_dir, rpm_name))
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

        # Don't trust yumdownloader, check again
        file_sha256sum = host.sh_sha256sum(fpath)
        if sha256sum != file_sha256sum:
            logging.error("downloaded RPM [%s] on host [%s] with wrong "
                          "sha256sum, expected [%s], got [%s]", fpath,
                          host.sh_hostname, sha256sum, file_sha256sum)
            return -1

    for fname in existing_rpm_fnames:
        logging.debug("found unnecessary file [%s] under directory [%s], "
                      "removing it", fname, dependent_dir)
        ret = host.sh_remove_file(fpath)
        if ret:
            return -1
    return 0


def collectd_build(workspace, build_host, local_host, collectd_git_path,
                   iso_cached_dir, distro):
    """
    Build Collectd on CentOS6 host
    """
    # pylint: disable=too-many-return-statements,too-many-arguments
    local_distro_rpm_dir = ("%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, distro))
    local_collectd_rpm_copying_dir = ("%s/%s" %
                                      (local_distro_rpm_dir, X86_64_STRING))
    local_collectd_rpm_dir = ("%s/%s" %
                              (local_distro_rpm_dir, COLLECTD_STRING))
    host_collectd_git_dir = ("%s/%s" % (workspace, COLLECT_GIT_STRING))
    host_collectd_rpm_dir = ("%s/%s" % (host_collectd_git_dir, RPM_PATH_STRING))
    ret = build_host.sh_send_file(collectd_git_path, workspace)
    if ret:
        logging.error("failed to send file [%s] on local host to "
                      "directory [%s] on host [%s]",
                      collectd_git_path, workspace,
                      build_host.sh_hostname)
        return -1

    command = ("cd %s && mkdir -p libltdl/config && sh ./build.sh && "
               "./configure --enable-write_tsdb --enable-dist --enable-nfs "
               "--disable-java --disable-amqp --disable-gmond --disable-nut "
               "--disable-pinba --disable-ping --disable-varnish "
               "--disable-dpdkstat --disable-turbostat && "
               "make && make dist-bzip2 && "
               "mkdir {BUILD,RPMS,SOURCES,SRPMS} && "
               "mv collectd-*.tar.bz2 SOURCES" % host_collectd_git_dir)
    retval = build_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      build_host.sh_hostname,
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
               (host_collectd_git_dir, host_collectd_git_dir))
    retval = build_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      build_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = ("mkdir -p %s" % (local_distro_rpm_dir))
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

    command = ("rm %s -fr" % (local_collectd_rpm_dir))
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

    ret = build_host.sh_get_file(host_collectd_rpm_dir, local_distro_rpm_dir)
    if ret:
        logging.error("failed to get Collectd RPMs from path [%s] on host "
                      "[%s] to local dir [%s]", host_collectd_rpm_dir,
                      build_host.sh_hostname, local_distro_rpm_dir)
        return -1

    command = ("mv %s %s" % (local_collectd_rpm_copying_dir, local_collectd_rpm_dir))
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

def collectd_build_check(workspace, build_host, local_host, collectd_git_path,
                         iso_cached_dir, collectd_version_release,
                         distro):
    """
    Check and build Collectd RPMs
    """
    # pylint: disable=too-many-arguments,too-many-return-statements
    # pylint: disable=too-many-statements,too-many-branches,too-many-locals
    local_distro_rpm_dir = ("%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, distro))
    local_collectd_rpm_dir = ("%s/%s" %
                              (local_distro_rpm_dir, COLLECTD_STRING))
    command = ("mkdir -p %s && ls %s" %
               (local_collectd_rpm_dir, local_collectd_rpm_dir))
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
    rpm_collectd_fnames = retval.cr_stdout.split()

    if distro == ssh_host.DISTRO_RHEL6:
        distro_number = "6"
    elif distro == ssh_host.DISTRO_RHEL7:
        distro_number = "7"
    else:
        return -1

    found = False
    for collect_rpm_name in COLLECTD_RPM_NAMES:
        collect_rpm_full = ("%s-%s.el%s.x86_64.rpm" %
                            (collect_rpm_name, collectd_version_release,
                             distro_number))
        found = False
        for rpm_collectd_fname in rpm_collectd_fnames[:]:
            if collect_rpm_full == rpm_collectd_fname:
                found = True
                rpm_collectd_fnames.remove(rpm_collectd_fname)
                logging.debug("RPM [%s/%s] already cached",
                              local_collectd_rpm_dir, collect_rpm_full)
                break

        if not found:
            logging.debug("RPM [%s] not cached in directory [%s], building "
                          "Collectd", collect_rpm_full, local_collectd_rpm_dir)
            break

    if not found:
        ret = collectd_build(workspace, build_host, local_host,
                             collectd_git_path, iso_cached_dir, distro)
        if ret:
            logging.error("failed to build Collectd on host [%s]",
                          build_host.sh_hostname)
            return -1

        # Don't trust the build, check RPMs again
        command = ("ls %s" % (local_collectd_rpm_dir))
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
        rpm_collectd_fnames = retval.cr_stdout.split()

        for collect_rpm_name in COLLECTD_RPM_NAMES:
            collect_rpm_full = ("%s-%s.el%s.x86_64.rpm" %
                                (collect_rpm_name, collectd_version_release,
                                 distro_number))
            found = False
            for rpm_collectd_fname in rpm_collectd_fnames[:]:
                if collect_rpm_full == rpm_collectd_fname:
                    found = True
                    rpm_collectd_fnames.remove(rpm_collectd_fname)
                    logging.debug("RPM [%s/%s] already cached",
                                  local_collectd_rpm_dir, collect_rpm_full)
                    break

            if not found:
                logging.error("RPM [%s] not found in directory [%s] after "
                              "building Collectd", collect_rpm_full,
                              local_collectd_rpm_dir)
                return -1
    else:
        collect_rpm_pattern = (r"collectd-\S+-%s.el6.x86_64.rpm" %
                               (collectd_version_release))
        collect_rpm_regular = re.compile(collect_rpm_pattern)
        for rpm_collectd_fname in rpm_collectd_fnames[:]:
            match = collect_rpm_regular.match(rpm_collectd_fname)
            if not match:
                fpath = ("%s/%s" %
                         (local_collectd_rpm_dir, rpm_collectd_fname))
                logging.debug("found a file [%s] not matched with pattern "
                              "[%s], removing it", fpath,
                              collect_rpm_pattern)

                command = ("rm -f %s" % (fpath))
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

def centos6_build(workspace, centos6_host, local_host, collectd_git_path,
                  iso_cached_dir, collectd_version_release):
    """
    Build on CentOS6 host
    """
    # pylint: disable=too-many-return-statements,too-many-arguments
    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    local_distro_rpm_dir = ("%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, ssh_host.DISTRO_RHEL6))
    local_dependent_rpm_dir = ("%s/%s" %
                               (local_distro_rpm_dir, DEPENDENT_STRING))
    local_copying_rpm_dir = ("%s/%s" % (local_distro_rpm_dir, COPYING_STRING))
    local_copying_dependent_rpm_dir = ("%s/%s" %
                                       (local_copying_rpm_dir,
                                        DEPENDENT_STRING))
    host_dependent_rpm_dir = ("%s/%s" % (workspace, DEPENDENT_STRING))

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

    ret = collectd_build_check(workspace, centos6_host, local_host,
                               collectd_git_path, iso_cached_dir,
                               collectd_version_release,
                               ssh_host.DISTRO_RHEL6)
    if ret:
        return -1

    dependent_rpm_cached = False
    command = ("test -e %s" % (local_dependent_rpm_dir))
    retval = local_host.sh_run(command)
    if retval.cr_exit_status == 0:
        command = ("test -d %s" % (local_dependent_rpm_dir))
        retval = local_host.sh_run(command)
        if retval.cr_exit_status != 0:
            command = ("rm -f %s" % (local_dependent_rpm_dir))
            retval = local_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("path [%s] is not a directory and can't be "
                              "deleted", local_dependent_rpm_dir)
                return -1
        else:
            dependent_rpm_cached = True

    if dependent_rpm_cached:
        ret = centos6_host.sh_send_file(local_dependent_rpm_dir, workspace)
        if ret:
            logging.error("failed to send cached dependent RPMs from local path "
                          "[%s] to dir [%s] on host [%s]", local_dependent_rpm_dir,
                          local_dependent_rpm_dir, centos6_host.sh_hostname)
            return -1
    else:
        command = ("mkdir -p %s" % (host_dependent_rpm_dir))
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

    ret = download_dependent_rpms(centos6_host, host_dependent_rpm_dir)
    if ret:
        logging.error("failed to download depdendent RPMs")
        return ret

    command = ("rm -fr %s && mkdir -p %s" %
               (local_copying_rpm_dir, local_copying_rpm_dir))
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

    ret = centos6_host.sh_get_file(host_dependent_rpm_dir, local_copying_rpm_dir)
    if ret:
        logging.error("failed to get dependent RPMs from path [%s] on host "
                      "[%s] to local dir [%s]", host_dependent_rpm_dir,
                      centos6_host.sh_hostname, local_copying_rpm_dir)
        return -1

    command = ("rm -fr %s && mv %s %s && rm -rf %s" %
               (local_dependent_rpm_dir,
                local_copying_dependent_rpm_dir,
                local_dependent_rpm_dir,
                local_copying_rpm_dir))
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

    return 0


def config_value(config, key):
    """
    Return value of a key in config
    """
    if key not in config:
        return None
    return config[key]


def esmon_do_build(workspace, config, config_fpath):
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

    current_dir = os.getcwd()
    iso_cached_dir = current_dir + "/../iso_cached_dir"
    collectd_git_path = current_dir + "/../" + "collectd.git"
    rpm_dir = iso_cached_dir + "/RPMS"
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

    command = "test -e %s" % collectd_git_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        collectd_git_url = config_value(config, "collectd_git_url")
        if collectd_git_url is None:
            logging.error("can NOT find [collectd_git_url] in the config, "
                          "please correct file [%s]", config_fpath)
            return -1

        command = "git clone %s %s" % (collectd_git_url, collectd_git_path)
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

        command = ("cd %s && git pull" %
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

    command = ("cd %s && git checkout master-ddn" %
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

    command = ("cd %s && git rev-parse --short HEAD" %
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
    collectd_git_version = retval.cr_stdout.strip()

    command = (r"cd %s && grep Version contrib/redhat/collectd.spec | "
               r"grep -v \# | awk '{print $2}'"  %
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
    collectd_version_string = retval.cr_stdout.strip()
    collectd_version = collectd_version_string.replace('%{?rev}', collectd_git_version)

    command = (r"cd %s && grep Release contrib/redhat/collectd.spec | "
               r"grep -v \# | awk '{print $2}'"  %
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
    collectd_release_string = retval.cr_stdout.strip()
    collectd_release = collectd_release_string.replace('%{?dist}', '')
    collectd_version_release = collectd_version + "-" + collectd_release

    ret = centos6_build(workspace, centos6_host, local_host, collectd_git_path,
                        iso_cached_dir, collectd_version_release)
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

    grafana_rpm_path = current_dir + "/../" + "grafana-4.4.1-1.x86_64.rpm"
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

    influxdb_rpm_path = current_dir + "/../" + "influxdb-1.3.1.x86_64.rpm"
    command = "test -e %s" % influxdb_rpm_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = ("cd %s/.. && curl -LO https://dl.influxdata.com/influxdb/"
                   "releases/influxdb-1.3.1.x86_64.rpm" % current_dir)
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
    python_library_dir = iso_cached_dir + "/" + python_library_name

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

    local_distro_rpm_dir = ("%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, ssh_host.DISTRO_RHEL7))
    local_dependent_rpm_dir = ("%s/%s" %
                               (local_distro_rpm_dir, DEPENDENT_STRING))
    ret = download_dependent_rpms(local_host, local_dependent_rpm_dir)
    if ret:
        logging.error("failed to install depdendent RPMs")
        return ret

    grafana_status_panel = "Grafana_Status_panel"
    grafana_status_panel_git_path = iso_cached_dir + "/" + grafana_status_panel
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

    dependent_existing_files = os.listdir(iso_cached_dir)
    dependent_existing_files.remove(grafana_status_panel)
    dependent_existing_files.remove("RPMS")
    dependent_existing_files.remove(python_library_name)
    for extra_fname in dependent_existing_files:
        logging.warning("find unknown file [%s] under directory [%s], removing",
                        extra_fname, iso_cached_dir)
        command = ("rm -fr %s/%s" % (iso_cached_dir, extra_fname))
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
               (current_dir, collectd_git_path, grafana_rpm_path,
                influxdb_rpm_path, iso_cached_dir))
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


def esmon_build(workspace, config_fpath):
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

    return esmon_do_build(workspace, config, config_fpath)


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

    identity = utils.local_strftime(utils.utcnow(), "%Y-%m-%d-%H_%M_%S")
    workspace = ESMON_BUILD_LOG_DIR + "/" + identity

    if not os.path.exists(ESMON_BUILD_LOG_DIR):
        os.mkdir(ESMON_BUILD_LOG_DIR)
    elif not os.path.isdir(ESMON_BUILD_LOG_DIR):
        logging.error("[%s] is not a directory", ESMON_BUILD_LOG_DIR)
        sys.exit(-1)

    if not os.path.exists(workspace):
        os.mkdir(workspace)
    elif not os.path.isdir(workspace):
        logging.error("[%s] is not a directory", workspace)
        sys.exit(-1)

    print("Started building Exascaler monitoring system using config [%s], "
          "please check [%s] for more log" %
          (config_fpath, workspace))
    utils.configure_logging(workspace)

    console_handler = utils.LOGGING_HANLDERS["console"]
    console_handler.setLevel(logging.DEBUG)

    save_fpath = workspace + "/" + ESMON_BUILD_CONFIG_FNAME
    logging.debug("copying config file from [%s] to [%s]", config_fpath,
                  save_fpath)
    shutil.copyfile(config_fpath, save_fpath)

    ret = esmon_build(workspace, config_fpath)
    if ret:
        logging.error("build failed")
        sys.exit(ret)
    logging.info("Exascaler monistoring system is successfully built")
    sys.exit(0)
