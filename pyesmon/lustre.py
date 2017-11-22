# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for Lustre file system management
"""
import logging
import os
import re

from pyesmon import utils

class LustreFilesystem(object):
    """
    Information about Lustre file system
    """
    # pylint: disable=too-few-public-methods
    # mgs_nid: 10.0.0.1@tcp
    def __init__(self, fsname, mgs_nid):
        self.lf_fsname = fsname
        self.lf_mgs_nid = mgs_nid


class LustreMDT(object):
    """
    Lustre MDT service
    """
    # pylint: disable=too-few-public-methods
    # index: 0, 1, etc.
    def __init__(self, lustre_fs, index, host, device,
                 is_mgs=False):
        # pylint: disable=too-many-arguments
        self.lmdt_lustre_fs = lustre_fs
        self.lmdt_index = index
        self.lmdt_host = host
        self.lmdt_device = device
        self.lmdt_is_mgs = is_mgs

    def lmdt_format(self):
        """
        Format this MDT
        """
        command = ("mkfs.lustre --fsname %s --mdt "
                   "--reformat --mgsnode=%s --index=%s" %
                   (self.lmdt_lustre_fs.lf_fsname,
                    self.lmdt_lustre_fs.lf_mgs_nid,
                    self.lmdt_index))

        if self.lmdt_is_mgs:
            command += " --mgs"
        command += " " + self.lmdt_device

        retval = self.lmdt_host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.lmdt_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        return 0


class LustreOST(object):
    """
    Lustre OST service
    """
    # pylint: disable=too-few-public-methods
    # index: 0, 1, etc.
    def __init__(self, lustre_fs, index, host, device):
        # pylint: disable=too-many-arguments
        self.lost_lustre_fs = lustre_fs
        self.lost_index = index
        self.lost_host = host
        self.lost_device = device

    def lost_format(self):
        """
        Format this OST
        """
        command = ("mkfs.lustre --fsname %s --ost "
                   "--reformat --mgsnode=%s --index=%s %s" %
                   (self.lost_lustre_fs.li_fsname,
                    self.lost_lustre_fs.li_mgs_nid,
                    self.lost_index,
                    self.lost_device))

        retval = self.lost_host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.lost_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        return 0


class LustreVersion(object):
    """
    RPM version of Lustre
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self, name, rpm_git_pattern, rpm_patterns):
        # pylint: disable=too-few-public-methods,too-many-arguments
        self.lv_name = name
        self.lv_rpm_git_pattern = rpm_git_pattern
        self.lv_rpm_patterns = rpm_patterns

RPM_KERNEL = "kernel"
RPM_KERNEL_FIRMWARE = "kernel-firmware"
RPM_LUSTRE = "lustre"
RPM_IOKIT = "iokit"
RPM_KMOD = "kmod"
RPM_OSD_LDISKFS = "osd_ldiskfs"
RPM_OSD_LDISKFS_MOUNT = "osd_ldiskfs_mount"
RPM_OSD_ZFS = "osd_zfs"
RPM_OSD_ZFS_MOUNT = "osd_zfs_mount"
RPM_TESTS = "tests"
RPM_TESTS_KMOD = "tests_kmod"
RPM_MLNX_OFA = "mlnx_ofa"
RPM_MLNX_KMOD = "mlnx_ofa_modules"

ES3_PATTERNS = {
    RPM_KERNEL: r"^(kernel-3.+\.x86_64\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.7.+\.x86_64\.rpm)$",
    RPM_IOKIT: r"^(lustre-iokit-2\.7.+\.x86_64\.rpm)$",
    RPM_KMOD: r"^(lustre-modules-2\.7.+\.x86_64\.rpm)$",
    RPM_OSD_LDISKFS: r"^(lustre-osd-ldiskfs-2\.7.+\.x86_64\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.7.+\.x86_64\.rpm)$",
    RPM_OSD_ZFS: r"^(lustre-osd-zfs-2\.7.+\.x86_64\.rpm)$",
    RPM_OSD_ZFS_MOUNT: r"^(lustre-osd-zfs-mount-2\.7.+\.x86_64\.rpm)$",
    RPM_TESTS: r"^(lustre-tests-2\.7.+\.x86_64\.rpm)$",
    RPM_MLNX_OFA: r"^(mlnx-ofa_kernel-3.+\.x86_64\.rpm)$",
    RPM_MLNX_KMOD: r"^(mlnx-ofa_kernel-modules-3.+\.x86_64\.rpm)$"}


LUSTRE_VERSION_ES3 = LustreVersion("es3",
                                   r".+\.x86_64_g(.+)\.x86_64\.rpm$",
                                   ES3_PATTERNS)


LUSTER_VERSIONS = [LUSTRE_VERSION_ES3]


def match_rpm_patterns(data, rpm_dict, possible_versions):
    """
    Match a rpm pattern
    """
    matched_versions = []
    rpm_type = None
    rpm_name = None
    for version in possible_versions:
        patterns = version.lv_rpm_patterns
        matched = False
        for key in patterns.keys():
            match = re.search(patterns[key], data)
            if match:
                value = match.group(1)
                if rpm_type is not None and rpm_type != key:
                    reason = ("RPM [%s] can be matched to both type [%s] "
                              "and [%s]" % (value, rpm_type, key))
                    logging.error(reason)
                    raise Exception(reason)

                if rpm_name is not None and rpm_name != value:
                    reason = ("RPM [%s] can be matched as both name [%s] "
                              "and [%s]" % (value, rpm_name, value))
                    logging.error(reason)
                    raise Exception(reason)

                rpm_type = key
                rpm_name = value
                matched = True
                logging.debug("match of key [%s]: [%s] by data [%s]",
                              key, value, data)
        if matched:
            matched_versions.append(version)

    if len(matched_versions) != 0:
        if rpm_type in rpm_dict:
            reason = ("Multiple match of RPM type [%s], both from [%s] "
                      "and [%s]" %
                      (rpm_type, rpm_name, rpm_dict[rpm_type]))
            logging.error(reason)
            raise Exception(reason)
        for version in possible_versions[:]:
            if version not in matched_versions:
                possible_versions.remove(version)
        rpm_dict[rpm_type] = rpm_name


class LustreRPMs(object):
    """
    Lustre OST service
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, lustre_rpm_dir):
        self.lr_rpm_dir = lustre_rpm_dir
        self.lr_rpm_names = {}
        self.lr_lustre_version = None
        self.lr_kernel_version = None

    def lr_prepare(self):
        """
        Prepare the RPMs
        """
        rpm_files = os.listdir(self.lr_rpm_dir)

        possible_versions = LUSTER_VERSIONS[:]
        for rpm_file in rpm_files:
            logging.debug("found file [%s] in directory [%s]",
                          rpm_file, self.lr_rpm_dir)
            match_rpm_patterns(rpm_file, self.lr_rpm_names,
                               possible_versions)

        if len(possible_versions) != 1:
            logging.error("The possible RPM version is %d, should be 1",
                          len(possible_versions))
            return -1
        self.lr_lustre_version = possible_versions[0]

        for key in self.lr_lustre_version.lv_rpm_patterns.keys():
            if key not in self.lr_rpm_names:
                logging.error("failed to get RPM name of [%s]", key)
                return -1

        kernel_rpm_name = self.lr_rpm_names[RPM_KERNEL]
        kernel_rpm_path = (self.lr_rpm_dir + '/' + kernel_rpm_name)
        command = ("rpm -qpl %s | grep /lib/modules |"
                   "sed 1q | awk -F '/' '{print $4}'" %
                   kernel_rpm_path)
        retval = utils.run(command)
        if retval.cr_exit_status != 0:
            logging.error("failed to get run command [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          retval.cr_exit_status, retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        self.lr_kernel_version = retval.cr_stdout.strip()
        return 0


def install_lustre_rpms(workspace, host, lustre_rpms):
    """
    Install Lustre RPMs on a host
    """
    command = ("mkdir -p %s" % workspace)
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

    basename = os.path.basename(lustre_rpms.lr_rpm_dir)
    host_copying_rpm_dir = workspace + "/" + basename
    host_lustre_rpm_dir = workspace + "/" + "lustre_rpms"

    ret = host.sh_send_file(lustre_rpms.lr_rpm_dir, workspace)
    if ret:
        logging.error("failed to send Lustre RPMs [%s] on local host to "
                      "directory [%s] on host [%s]",
                      lustre_rpms.lr_rpm_dir, host_lustre_rpm_dir,
                      host.sh_hostname)
        return -1

    command = ("mv %s %s" % (host_copying_rpm_dir, host_lustre_rpm_dir))
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

    command = ("uptime")
    retval_before = host.sh_run(command)
    host.sh_reboot()
    retval_after = host.sh_run(command)
    logging.info("uptime of host [%s] before reboot [%s], after [%s]",
                  host.sh_hostname, retval_before.cr_stdout, retval_after.cr_stdout)
    return 0
