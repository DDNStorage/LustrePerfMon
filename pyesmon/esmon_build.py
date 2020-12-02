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
import time
import yaml

# Local libs
from pyesmon import utils
from pyesmon import time_util
from pyesmon import ssh_host
from pyesmon import esmon_common

ESMON_BUILD_CONFIG_FNAME = "esmon_build.conf"
ESMON_BUILD_CONFIG = "/etc/" + ESMON_BUILD_CONFIG_FNAME
DEPENDENT_STRING = "dependent"
COLLECTD_STRING = "collectd"
COLLECT_GIT_STRING = COLLECTD_STRING + ".git"
RPM_STRING = "RPMS"
COPYING_STRING = "copying"
COLLECTD_RPM_NAMES = ["collectd", "collectd-disk", "collectd-filedata",
                      "collectd-ime", "collectd-sensors", "collectd-ssh",
                      "libcollectdclient"]
SERVER_STRING = "server"
ESMON_BUILD_LOG_DIR = "/var/log"


def download_dependent_rpms(host, dependent_dir, distro, target_cpu):
    """
    Download dependent RPMs
    """
    # pylint: disable=too-many-locals,too-many-return-statements
    # pylint: disable=too-many-branches,too-many-statements
    # The yumdb might be broken, so sync
    command = "yumdb sync"
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

    dependent_rpms = esmon_common.ESMON_CLIENT_DEPENDENT_RPMS[:]
    if distro == ssh_host.DISTRO_RHEL7:
        for rpm_name in esmon_common.ESMON_SERVER_DEPENDENT_RPMS:
            if rpm_name not in dependent_rpms:
                dependent_rpms.append(rpm_name)

        for rpm_name in esmon_common.ESMON_INSTALL_DEPENDENT_RPMS:
            if rpm_name not in dependent_rpms:
                dependent_rpms.append(rpm_name)

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

        rpm_fullnames = retval.cr_stdout.split()
        if len(rpm_fullnames) != 1:
            logging.error("got multiple RPMs with query [%s] on host [%s], "
                          "output = [%s]", command, host.sh_hostname,
                          retval.cr_stdout)
            return -1

        rpm_fullname = rpm_fullnames[0]
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
        if target_cpu == "x86_64":
            command = (r"cd %s && yumdownloader -x \*i686 --archlist=x86_64 %s" %
                       (dependent_dir, rpm_name))
        else:
            command = (r"cd %s && yumdownloader %s" %
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
        fpath = dependent_dir + "/" + fname
        logging.debug("found unnecessary file [%s] under directory [%s], "
                      "removing it", fname, dependent_dir)
        ret = host.sh_remove_file(fpath)
        if ret:
            return -1
    return 0


def collectd_build(workspace, build_host, local_host, collectd_git_path,
                   iso_cached_dir, collectd_tarball_name, build_timestamp,
                   distro, distro_number, target_cpu):
    """
    Build Collectd on a host
    """
    # pylint: disable=too-many-return-statements,too-many-arguments
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    local_distro_rpm_dir = ("%s/%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, distro, target_cpu))
    local_collectd_rpm_copying_dir = ("%s/%s" %
                                      (local_distro_rpm_dir, target_cpu))
    local_collectd_rpm_dir = ("%s/%s" %
                              (local_distro_rpm_dir, COLLECTD_STRING))
    host_collectd_git_dir = ("%s/%s" % (workspace, COLLECT_GIT_STRING))
    host_collectd_rpm_dir = ("%s/%s/%s" % (host_collectd_git_dir, RPM_STRING, target_cpu))
    ret = build_host.sh_send_file(collectd_git_path, workspace)
    if ret:
        logging.error("failed to send file [%s] on local host to "
                      "directory [%s] on host [%s]",
                      collectd_git_path, workspace,
                      build_host.sh_hostname)
        return -1

    command = ("cd %s && mkdir -p libltdl/config && sh ./build.sh && "
               "./configure && "
               "make dist-bzip2" %
               (host_collectd_git_dir))
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

    command = ("cd %s && ls collectd-*.tar.bz2" %
               (host_collectd_git_dir))
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

    collectd_tarballs = retval.cr_stdout.split()
    if len(collectd_tarballs) != 1:
        logging.error("unexpected output of Collectd tarball: [%s]",
                      retval.cr_stdout)
        return -1

    collectd_tarball_fname = collectd_tarballs[0]

    if (not collectd_tarball_fname.endswith(".tar.bz2") or
            len(collectd_tarball_fname) <= 8):
        logging.error("unexpected Collectd tarball fname: [%s]",
                      collectd_tarball_fname)
        return -1

    collectd_tarball_current_name = collectd_tarball_fname[:-8]

    command = ("cd %s && tar jxf %s && "
               "mv %s %s && tar cjf %s.tar.bz2 %s" %
               (host_collectd_git_dir, collectd_tarball_fname,
                collectd_tarball_current_name, collectd_tarball_name,
                collectd_tarball_name, collectd_tarball_name))
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

    command = ("cd %s && mkdir {BUILD,RPMS,SOURCES,SRPMS} && "
               "mv %s.tar.bz2 SOURCES" %
               (host_collectd_git_dir, collectd_tarball_name))
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
               '--without gps --without lvm --define "_topdir %s" '
               '--define="rev $(git rev-parse --short HEAD)" '
               '--define="build_timestamp %s" '
               '--define="dist .el%s" '
               'contrib/redhat/collectd.spec' %
               (host_collectd_git_dir, host_collectd_git_dir, build_timestamp, distro_number))
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
                         iso_cached_dir, collectd_version_release, build_timestamp,
                         collectd_tarball_name, distro, target_cpu):
    """
    Check and build Collectd RPMs
    """
    # pylint: disable=too-many-arguments,too-many-return-statements
    # pylint: disable=too-many-statements,too-many-branches,too-many-locals
    local_distro_rpm_dir = ("%s/%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, distro, target_cpu))
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

    if distro == ssh_host.DISTRO_RHEL7:
        distro_number = "7"
    elif distro == ssh_host.DISTRO_RHEL6:
        distro_number = "6"
    else:
        logging.error("unsupported distro [%s]", distro)
        return -1

    found = False
    for collect_rpm_name in COLLECTD_RPM_NAMES:
        collect_rpm_full = ("%s-%s.el%s.%s.rpm" %
                            (collect_rpm_name, collectd_version_release,
                             distro_number, target_cpu))
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
        ret = collectd_build(workspace, build_host, local_host, collectd_git_path,
                             iso_cached_dir, collectd_tarball_name, build_timestamp,
                             distro, distro_number, target_cpu)
        if ret:
            logging.error("failed to build Collectd on host [%s]",
                          local_host.sh_hostname)
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
            collect_rpm_full = ("%s-%s.el%s.%s.rpm" %
                                (collect_rpm_name, collectd_version_release,
                                 distro_number, target_cpu))
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
        collect_rpm_pattern = (r"collectd-\S+-%s.el%s.%s.rpm" %
                               (collectd_version_release, distro_number,
                                target_cpu))
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


def host_build(workspace, build_host, local_host, collectd_git_path,
               iso_cached_dir, collectd_version_release, build_timestamp,
               collectd_tarball_name):
    """
    Build on host
    """
    # pylint: disable=too-many-return-statements,too-many-arguments
    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    distro = build_host.sh_distro()
    if distro is None:
        logging.error("failed to get distro on host [%s]",
                      build_host.sh_hostname)
        return -1

    target_cpu = build_host.sh_target_cpu()
    if target_cpu is None:
        logging.error("failed to get target cpu on host [%s]",
                      build_host.sh_hostname)
        return -1

    local_distro_rpm_dir = ("%s/%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, distro, target_cpu))
    local_dependent_rpm_dir = ("%s/%s" %
                               (local_distro_rpm_dir, DEPENDENT_STRING))
    local_copying_rpm_dir = ("%s/%s" % (local_distro_rpm_dir, COPYING_STRING))
    local_copying_dependent_rpm_dir = ("%s/%s" %
                                       (local_copying_rpm_dir,
                                        DEPENDENT_STRING))
    host_dependent_rpm_dir = ("%s/%s" % (workspace, DEPENDENT_STRING))

    # Update to the latest distro release
    command = "yum update -y"
    retval = build_host.sh_run(command, timeout=1200)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      build_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    # Sometimes yum update install i686 RPMs which cause multiple RPMs for
    # the same name. Uninstall i686 RPMs here.
    target_cpu = build_host.sh_target_cpu()
    if target_cpu is None:
        logging.error("failed to get target cpu on host [%s]",
                      build_host.sh_hostname)
        return -1

    if target_cpu == "x86_64":
        command = "rpm -qa | grep i686"
        retval = build_host.sh_run(command, timeout=600)
        if retval.cr_exit_status == 0:
            command = "rpm -qa | grep i686 | xargs rpm -e"
            retval = build_host.sh_run(command, timeout=600)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              build_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

    command = ("rpm -e zeromq-devel")
    build_host.sh_run(command)

    # The RPMs needed by Collectd building
    # riemann-c-client-devel is not available for RHEL6, but that is fine
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
               "lua-devel byacc ganglia-devel libmicrohttpd-devel "
               "riemann-c-client-devel xfsprogs-devel uthash-devel "
               "qpid-proton-c-devel perl-ExtUtils-Embed -y")
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

    command = "mkdir -p %s" % workspace
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

    ret = collectd_build_check(workspace, build_host, local_host, collectd_git_path,
                               iso_cached_dir, collectd_version_release, build_timestamp,
                               collectd_tarball_name, distro, target_cpu)
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
        ret = build_host.sh_send_file(local_dependent_rpm_dir, workspace)
        if ret:
            logging.error("failed to send cached dependent RPMs from local path "
                          "[%s] to dir [%s] on host [%s]", local_dependent_rpm_dir,
                          local_dependent_rpm_dir, build_host.sh_hostname)
            return -1
    else:
        command = ("mkdir -p %s" % (host_dependent_rpm_dir))
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

    ret = download_dependent_rpms(build_host, host_dependent_rpm_dir, distro,
                                  target_cpu)
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

    ret = build_host.sh_get_file(host_dependent_rpm_dir, local_copying_rpm_dir)
    if ret:
        logging.error("failed to get dependent RPMs from path [%s] on host "
                      "[%s] to local dir [%s]", host_dependent_rpm_dir,
                      build_host.sh_hostname, local_copying_rpm_dir)
        return -1

    command = ("rm -fr %s && mv %s %s && rm -rf %s" %
               (local_dependent_rpm_dir,
                local_copying_dependent_rpm_dir,
                local_dependent_rpm_dir,
                local_copying_rpm_dir))
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


def esmon_download_grafana_plugin(local_host, iso_cached_dir, plugin_name, git_url):
    """
    Download grafana plugin from git
    """
    panel_git_path = iso_cached_dir + "/" + plugin_name
    command = "test -e %s" % panel_git_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = ("git clone %s %s" % (git_url, panel_git_path))
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
        command = ("cd %s && git pull" % panel_git_path)
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

    for filename in esmon_common.GRAFANA_PLUGIN_FILENAMES:
        filepath = "%s/%s" % (panel_git_path, filename)

        command = "test -e %s" % filepath
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


def esmon_download_pie_chart_plugin(local_host, iso_cached_dir):
    """
    Download pie chart plugin
    """
    panel_path = iso_cached_dir + "/" + esmon_common.GRAFANA_PIE_CHART_PANEL
    command = "test -e %s" % panel_path
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        command = "cd %s && wget %s" % (iso_cached_dir, esmon_common.GRAFANA_PIE_CHART_URL)
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

        basename = os.path.basename(esmon_common.GRAFANA_PIE_CHART_URL)
        zip_fpath = iso_cached_dir + "/" + basename

        command = "cd %s && unzip %s" % (iso_cached_dir, zip_fpath)
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

        command = "test -e %s" % panel_path
        retval = local_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to generate dir [%s] after unzip file [%s]",
                          panel_path, zip_fpath)
            return -1

        command = "rm -f %s" % (zip_fpath)
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

    for filename in ["dist/module.js", "README.md", "package.json"]:
        filepath = "%s/%s" % (panel_path, filename)

        command = "test -e %s" % filepath
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


def esmon_download_grafana_plugins(local_host, iso_cached_dir):
    """
    Download grafana plugin
    """
    for plugin_name, git_url in esmon_common.GRAFANA_PLUGIN_GITS.iteritems():
        ret = esmon_download_grafana_plugin(local_host, iso_cached_dir, plugin_name, git_url)
        if ret:
            logging.error("failed to clone Grafana plugin [%s] from url [%s]",
                          plugin_name, git_url)
            return -1

    ret = esmon_download_pie_chart_plugin(local_host, iso_cached_dir)
    if ret:
        logging.error("failed to download Grafana Piechart plugin")
        return -1
    return 0


def parse_host_configs(config, config_fpath, hosts):
    """
    Parse the host_configs
    """
    host_configs = esmon_common.config_value(config, "ssh_hosts")
    if host_configs is None:
        logging.info("can NOT find [ssh_hosts] in the config file [%s]",
                     config_fpath)
        return 0

    for host_config in host_configs:
        host_id = host_config["host_id"]
        if host_id is None:
            logging.error("can NOT find [host_id] in the config of a "
                          "SSH host, please correct file [%s]",
                          config_fpath)
            return -1

        hostname = esmon_common.config_value(host_config, "hostname")
        if hostname is None:
            logging.error("can NOT find [hostname] in the config of SSH host "
                          "with ID [%s], please correct file [%s]",
                          host_id, config_fpath)
            return -1

        mapping_dict = {esmon_common.ESMON_CONFIG_CSTR_NONE: None}
        ssh_identity_file = esmon_common.config_value(host_config,
                                                      esmon_common.CSTR_SSH_IDENTITY_FILE,
                                                      mapping_dict=mapping_dict)

        if host_id in hosts:
            logging.error("multiple SSH hosts with the same ID [%s], please "
                          "correct file [%s]", host_id, config_fpath)
            return -1
        host = ssh_host.SSHHost(hostname, ssh_identity_file)
        hosts[host_id] = host
    return 0


def influxdb_build(current_dir, local_host, config, iso_cached_dir,
                   target_cpu, influxdb_rpm_fname,
                   local_server_rpm_dir):
    """
    Build the RPM of influxdb
    """
    # pylint: disable=too-many-return-statements,too-many-arguments
    influxdb_git_path = current_dir + "/../" + "influxdb.git"
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

    influxdb_git_url = esmon_common.config_value(config, "influxdb_git_url")
    if influxdb_git_url is None:
        influxdb_git_url = "https://github.com/influxdata/influxdb.git"
        logging.info("can NOT find [influxdb_git_url] in the config, "
                     "use default value [%s]", influxdb_git_url)

    influxdb_git_branch = esmon_common.config_value(config, "influxdb_git_branch")
    if influxdb_git_branch is None:
        influxdb_git_branch = "1.8"
        logging.info("can NOT find [influxdb_git_branch] in the config, "
                     "use default value [%s]", influxdb_git_branch)

    ret = esmon_common.clone_src_from_git(influxdb_git_path, influxdb_git_url,
                                          influxdb_git_branch)
    if ret:
        logging.error("failed to clone influxdb branch [%s] from [%s] to "
                      "directory [%s]", influxdb_git_branch,
                      influxdb_git_url, influxdb_git_path)
        return -1

    command = ("cd %s && git apply %s/influxdb/influxdb_1.8.patch" %
               (influxdb_git_path, current_dir))
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

    command = ("cd %s && ./build.py" %
               (influxdb_git_path))
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

    command = ("cd %s/man && make" %
               (influxdb_git_path))
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

    command = ("cd %s && mkdir BUILD BUILDROOT RPMS SOURCES SPECS SRPMS" %
               (influxdb_git_path))
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

    command = ("cp %s/influxdb/influxdb.spec %s/influxdb/influxdb.conf %s" %
               (current_dir, current_dir, influxdb_git_path))
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

    command = ("cd %s && tar czvf influxdb.tar.gz build influxdb.conf "
               "scripts/influxdb.service scripts/logrotate man/*.1" %
               (influxdb_git_path))
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

    command = ("cd %s && mv influxdb.tar.gz SOURCES" %
               (influxdb_git_path))
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

    command = ('cd %s && rpmbuild -ba --define="_topdir %s" influxdb.spec' %
               (influxdb_git_path, influxdb_git_path))
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

    rpm_file = ("%s/RPMS/%s/%s" %
                (influxdb_git_path, target_cpu, influxdb_rpm_fname))

    command = ("cp %s %s" % (rpm_file, local_server_rpm_dir))
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


def influxdb_build_check(current_dir, local_host, config, iso_cached_dir,
                         distro, target_cpu, server_rpms):
    """
    Check and build influxdb RPM
    """
    # pylint: disable=too-many-arguments,too-many-return-statements
    # pylint: disable=too-many-statements,too-many-branches,too-many-locals
    local_distro_rpm_dir = ("%s/%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, distro, target_cpu))
    local_server_rpm_dir = ("%s/%s" %
                            (local_distro_rpm_dir, SERVER_STRING))
    command = ("mkdir -p %s && ls %s" %
               (local_server_rpm_dir, local_server_rpm_dir))
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
    rpm_server_fnames = retval.cr_stdout.split()
    influxdb_rpm_fname = ("influxdb-1.8.0-1.%s.rpm" % (target_cpu))

    if influxdb_rpm_fname in rpm_server_fnames:
        logging.info("RPM [%s] is already cached in directory [%s], not building "
                     "Influxdb", influxdb_rpm_fname, local_server_rpm_dir)
        server_rpms[influxdb_rpm_fname] = influxdb_rpm_fname
        return 0

    ret = influxdb_build(current_dir, local_host, config, iso_cached_dir,
                         target_cpu, influxdb_rpm_fname,
                         local_server_rpm_dir)
    if ret:
        logging.error("failed to build Influxdb")
        return -1

    # The url will not be used anyway.
    server_rpms[influxdb_rpm_fname] = influxdb_rpm_fname
    return 0


def esmon_do_build(current_dir, relative_workspace, config, config_fpath):
    """
    Build the ISO
    """
    # pylint: disable=too-many-locals,too-many-return-statements
    # pylint: disable=too-many-branches,too-many-statements
    hosts = {}
    if parse_host_configs(config, config_fpath, hosts):
        logging.error("failed to parse host configs")
        return -1

    centos6_host_config = esmon_common.config_value(config, "centos6_host")
    if centos6_host_config is None:
        logging.info("can NOT find [centos6_host] in the config file [%s], "
                     "diableing CentOS6 support", config_fpath)
        centos6_host = None
    else:
        centos6_host_id = esmon_common.config_value(centos6_host_config, "host_id")
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

    target_cpu = local_host.sh_target_cpu()
    if target_cpu is None:
        logging.error("failed to get target cpu on local_host [%s]",
                      local_host.sh_hostname)
        return -1

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

    collectd_git_url = esmon_common.config_value(config, "collectd_git_url")
    if collectd_git_url is None:
        collectd_git_url = "https://github.com/DDNStorage/collectd.git"
        logging.info("can NOT find [collectd_git_url] in the config, "
                     "use default value [%s]", collectd_git_url)

    collectd_git_branch = esmon_common.config_value(config, "collectd_git_branch")
    if collectd_git_branch is None:
        collectd_git_branch = "master-ddn"
        logging.info("can NOT find [collectd_git_branch] in the config, "
                     "use default value [%s]", collectd_git_branch)

    ret = esmon_common.clone_src_from_git(collectd_git_path, collectd_git_url,
                                          collectd_git_branch)
    if ret:
        logging.error("failed to clone Collectd branch [%s] from [%s] to "
                      "directory [%s]", collectd_git_branch,
                      collectd_git_url, collectd_git_path)
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
               r"grep -v \# | awk '{print $2}'" %
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

    build_timestamp = os.environ.get('TIMESTAMP', str(int(time.time())))
    collectd_version_string = retval.cr_stdout.strip()
    collectd_version = collectd_version_string.replace('%{?build_timestamp}', build_timestamp)
    collectd_tarball_name = "collectd-" + collectd_version

    command = (r"cd %s && grep Release contrib/redhat/collectd.spec | "
               r"grep -v \# | awk '{print $2}'" %
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
    collectd_release_string = collectd_release_string.replace('%{?rev}', collectd_git_version)
    collectd_release = collectd_release_string.replace('%{?dist}', '')
    collectd_version_release = collectd_version + "-" + collectd_release

    if centos6_host is not None:
        centos6_workspace = ESMON_BUILD_LOG_DIR + "/" + relative_workspace
        ret = host_build(centos6_workspace, centos6_host, local_host, collectd_git_path,
                         iso_cached_dir, collectd_version_release, build_timestamp,
                         collectd_tarball_name)
        if ret:
            logging.error("failed to prepare RPMs of CentOS6 on host [%s]",
                          centos6_host.sh_hostname)
            return -1

    # The build host of CentOS7 could potentially be another host, not local
    # host
    local_workspace = current_dir + "/" + relative_workspace
    ret = host_build(local_workspace, local_host, local_host, collectd_git_path,
                     iso_cached_dir, collectd_version_release, build_timestamp,
                     collectd_tarball_name)
    if ret:
        logging.error("failed to prepare RPMs of CentOS7 on local host")
        return -1

    local_distro_rpm_dir = ("%s/%s/%s/%s" %
                            (iso_cached_dir, RPM_STRING, distro, target_cpu))
    local_server_rpm_dir = ("%s/%s" %
                            (local_distro_rpm_dir, SERVER_STRING))

    command = ("mkdir -p %s" % local_server_rpm_dir)
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

    server_rpms = {}
    influxdb_rpm = esmon_common.config_value(config, "influxdb_rpm")
    if influxdb_rpm is not None:
        name = os.path.basename(influxdb_rpm)

        command = ("cp %s %s" % (influxdb_rpm, local_server_rpm_dir))
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
        # The URL will not be used actually
        server_rpms[name] = influxdb_rpm
    if target_cpu == "x86_64":
        name = "grafana-6.0.2-1.x86_64.rpm"
        url = ("https://dl.grafana.com/oss/release/" + name)
        server_rpms[name] = url

        if influxdb_rpm is None:
            name = "influxdb-1.7.4.x86_64.rpm"
            url = ("https://dl.influxdata.com/influxdb/releases/" + name)
            server_rpms[name] = url
    elif target_cpu == "aarch64":
        name = "grafana-6.7.3-1.aarch64.rpm"
        url = ("https://dl.grafana.com/oss/release/" + name)
        server_rpms[name] = url

        ret = influxdb_build_check(current_dir, local_host, config, iso_cached_dir,
                                   distro, target_cpu, server_rpms)
        if ret:
            logging.error("failed to build influxdb")
            return -1
    else:
        logging.error("unsupported CPU type [%s]", target_cpu)
        return -1

    for name, url in server_rpms.iteritems():
        fpath = ("%s/%s" % (local_server_rpm_dir, name))
        command = "test -e %s" % fpath
        retval = local_host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("file [%s] doesn't exist, downloading it", fpath)
            command = ("cd %s && wget --no-check-certificate %s" %
                       (local_server_rpm_dir, url))
            retval = local_host.sh_run(command, timeout=3600)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              local_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

    server_existing_files = os.listdir(local_server_rpm_dir)
    for server_rpm in server_rpms.iterkeys():
        server_existing_files.remove(server_rpm)
    for extra_fname in server_existing_files:
        logging.warning("find unknown file [%s] under directory [%s], removing",
                        extra_fname, local_server_rpm_dir)
        command = ("rm -fr %s/%s" % (local_server_rpm_dir, extra_fname))
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

    ret = esmon_download_grafana_plugins(local_host, iso_cached_dir)
    if ret:
        logging.error("failed to download Grafana plugins")
        return -1

    dependent_existing_files = os.listdir(iso_cached_dir)
    for panel_name in esmon_common.GRAFANA_PLUGINS:
        dependent_existing_files.remove(panel_name)
    dependent_existing_files.remove("RPMS")
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
               "./configure --with-cached-iso=%s && "
               "make" %
               (current_dir, iso_cached_dir))
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

    if centos6_host is not None:
        command = ("rm -fr %s" % (centos6_workspace))
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


def esmon_build(current_dir, relative_workspace, config_fpath):
    """
    Build the ISO. If config_fpath is None, then use default config
    """
    # pylint: disable=bare-except
    if config_fpath is None:
        config = None
    else:
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

    return esmon_do_build(current_dir, relative_workspace, config, config_fpath)


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

    identity = time_util.local_strftime(time_util.utcnow(), "%Y-%m-%d-%H_%M_%S")

    current_dir = os.getcwd()
    build_log_dir = "build_esmon"
    relative_workspace = build_log_dir + "/" + identity

    local_workspace = current_dir + "/" + relative_workspace
    local_log_dir = current_dir + "/" + build_log_dir
    if not os.path.exists(local_log_dir):
        os.mkdir(local_log_dir)
    elif not os.path.isdir(local_log_dir):
        logging.error("[%s] is not a directory", local_log_dir)
        sys.exit(-1)

    if not os.path.exists(local_workspace):
        os.mkdir(local_workspace)
    elif not os.path.isdir(local_workspace):
        logging.error("[%s] is not a directory", local_workspace)
        sys.exit(-1)

    config_fpath_exists = os.path.exists(config_fpath)
    if not config_fpath_exists:
        config_fpath = None
        print("Started building Exascaler monitoring system using default config, "
              "please check [%s] for more log" %
              (local_workspace))
    else:
        print("Started building Exascaler monitoring system using config [%s], "
              "please check [%s] for more log" %
              (config_fpath, local_workspace))
    utils.configure_logging(local_workspace)

    console_handler = utils.LOGGING_HANLDERS["console"]
    console_handler.setLevel(logging.DEBUG)

    if config_fpath_exists:
        save_fpath = local_workspace + "/" + ESMON_BUILD_CONFIG_FNAME
        logging.debug("copying config file from [%s] to [%s]", config_fpath,
                      save_fpath)
        shutil.copyfile(config_fpath, save_fpath)

    ret = esmon_build(current_dir, relative_workspace, config_fpath)
    if ret:
        logging.error("build failed")
        sys.exit(ret)
    logging.info("Exascaler monistoring system is successfully built")
    sys.exit(0)
