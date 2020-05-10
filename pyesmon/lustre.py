# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for Lustre file system management
"""
# pylint: disable=too-many-lines
import logging
import os
import re

from pyesmon import utils
from pyesmon import ssh_host

# The directory path that has Lustre test script
LUSTRE_TEST_SCRIPT_DIR = "/usr/lib64/lustre/tests"

ZFS = "zfs"
LDISKFS = "ldiskfs"
JOB_ID_PROCNAME_UID = "procname_uid"
JOB_ID_UNKNOWN = "unknown"

LUSTRE_BACKEND_FILESYSTEMS = [LDISKFS, ZFS]


def lustre_string2index(index_string):
    """
    Transfer string to index number, e.g.
    "000e" -> 14
    """
    index_number = int(index_string, 16)
    if index_number > 0xffff:
        return -1, ""
    return 0, index_number


def lustre_index2string(index_number):
    """
    Transfer number to index string, e.g.
    14 -> "000e"
    """
    if index_number > 0xffff:
        return -1, ""
    index_string = "%04x" % index_number
    return 0, index_string


def lustre_ost_index2string(index_number):
    """
    Transfer number to OST index string, e.g.
    14 -> "OST000e"
    """
    if index_number > 0xffff:
        return -1, ""
    index_string = "OST%04x" % index_number
    return 0, index_string


def lustre_mdt_index2string(index_number):
    """
    Transfer number to MDT index string, e.g.
    14 -> "MDT000e"
    """
    if index_number > 0xffff:
        return -1, ""
    index_string = "MDT%04x" % index_number
    return 0, index_string


class LustreFilesystem(object):
    """
    Information about Lustre file system
    """
    # pylint: disable=too-few-public-methods
    # mgs_nid: 10.0.0.1@tcp
    def __init__(self, fsname):
        self.lf_fsname = fsname
        self.lf_mgs_nid = None
        self.lf_mgs = None
        self.lf_osts = {}
        self.lf_mdts = {}
        self.lf_clients = {}

    def lf_ost_add(self, ost_index, ost):
        """
        Add OST into this file system
        """
        if ost_index in self.lf_osts:
            return -1
        self.lf_osts[ost_index] = ost
        return 0

    def lf_mdt_add(self, mdt_index, mdt):
        """
        Add MDT into this file system
        """
        if mdt_index in self.lf_mdts:
            return -1
        if mdt.lmdt_is_mgs:
            if self.lf_mgs is not None:
                return -1
            self.lf_mgs = mdt
        self.lf_mdts[mdt_index] = mdt
        return 0

    def lf_format(self):
        """
        Format the whole file system
        """
        if self.lf_mgs_nid is None:
            logging.error("the MGS nid of Lustre file system [%s] is not "
                          "configured, not able to format", self.lf_fsname)
            return -1

        for mdt_index, mdt in self.lf_mdts.iteritems():
            ret = mdt.lmdt_format()
            if ret:
                logging.error("failed to format MDT [%d] of Lustre file "
                              "system [%s]", mdt_index, self.lf_fsname)
                return -1

        for ost_index, ost in self.lf_osts.iteritems():
            ret = ost.lost_format()
            if ret:
                logging.error("failed to format OST [%d] of Lustre file "
                              "system [%s]", ost_index, self.lf_fsname)
                return -1
        return 0

    def lf_mount(self):
        """
        Mount the whole file system
        """
        for mdt_index, mdt in self.lf_mdts.iteritems():
            ret = mdt.lmdt_mount()
            if ret:
                logging.error("failed to mount MDT [%d] of Lustre file "
                              "system [%s]", mdt_index, self.lf_fsname)
                return -1

        for ost_index, ost in self.lf_osts.iteritems():
            ret = ost.lost_mount()
            if ret:
                logging.error("failed to mount OST [%d] of Lustre file "
                              "system [%s]", ost_index, self.lf_fsname)
                return -1

        for client_index, client in self.lf_clients.iteritems():
            ret = client.lc_mount()
            if ret:
                logging.error("failed to mount client [%d] of Lustre file "
                              "system [%s]", client_index, self.lf_fsname)
                return -1
        return 0

    def lf_umount(self):
        """
        Umount the whole file system
        """
        for client_index, client in self.lf_clients.iteritems():
            ret = client.lc_umount()
            if ret:
                logging.error("failed to umount client [%d] of Lustre file "
                              "system [%s]", client_index, self.lf_fsname)
                return -1

        for mdt_index, mdt in self.lf_mdts.iteritems():
            ret = mdt.lmdt_umount()
            if ret:
                logging.error("failed to umount MDT [%d] of Lustre file "
                              "system [%s]", mdt_index, self.lf_fsname)
                return -1

        for ost_index, ost in self.lf_osts.iteritems():
            ret = ost.lost_umount()
            if ret:
                logging.error("failed to umount OST [%d] of Lustre file "
                              "system [%s]", ost_index, self.lf_fsname)
                return -1
        return 0

    def lf_conf_param(self, command):
        """
        Config param on the MGS
        """
        if self.lf_mgs is None:
            logging.error("no MGS is known for Lustre file system [%s]",
                          self.lf_fsname)
            return -1

        host = self.lf_mgs.lmdt_host
        command = ("lctl conf_param %s.%s" %
                   (self.lf_fsname, command))
        retval = host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1


class LustreMDT(object):
    """
    Lustre MDT service
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    # index: 0, 1, etc.
    def __init__(self, lustre_fs, index, host, device, mnt,
                 is_mgs=False, backfs_type=LDISKFS):
        # pylint: disable=too-many-arguments
        self.lmdt_lustre_fs = lustre_fs
        self.lmdt_index = index
        self.lmdt_host = host
        self.lmdt_mnt = mnt
        self.lmdt_device = device
        self.lmdt_is_mgs = is_mgs
        self.lmdt_backfs_type = backfs_type
        if backfs_type == ZFS:
            self.lmdt_zfs_pool = "pool_%s_mdt_%s" % (lustre_fs.lf_fsname, index)
            self.lmdt_zfs_fsname = "fs_mdt_%s" % index
        else:
            self.lmdt_zfs_pool = None
            self.lmdt_zfs_fsname = None

        ret, index_string = lustre_mdt_index2string(index)
        if ret:
            reason = ("invalid MDT index [%s]" % (index))
            logging.error(reason)
            raise Exception(reason)
        self.lmdt_index_string = index_string

        ret = host.lsh_mdt_add(lustre_fs.lf_fsname, index, self)
        if ret:
            reason = ("MDT [%s:%d] already exists in host [%s]" %
                      (lustre_fs.lf_fsname, index, host.sh_hostname))
            logging.error(reason)
            raise Exception(reason)

        ret = lustre_fs.lf_mdt_add(index, self)
        if ret:
            reason = ("MDT [%d] already exists in file system [%s]" %
                      (index, lustre_fs.lf_fsname))
            logging.error(reason)
            raise Exception(reason)
        lustre_fs.lf_mdts[index] = self

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

        if self.lmdt_backfs_type == ZFS:
            command += (" --backfstype zfs %s/%s %s" %
                        (self.lmdt_zfs_pool,
                         self.lmdt_zfs_fsname,
                         self.lmdt_device))

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

    def lmdt_mount(self):
        """
        Mount this MDT
        """
        if self.lmdt_backfs_type == ZFS:
            command = ("mkdir -p %s && mount -t lustre %s/%s %s" %
                       (self.lmdt_mnt, self.lmdt_zfs_pool,
                        self.lmdt_zfs_fsname, self.lmdt_mnt))
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

        command = ("mkdir -p %s && mount -t lustre %s %s" %
                   (self.lmdt_mnt, self.lmdt_device, self.lmdt_mnt))
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

    def lmdt_umount(self):
        """
        Umount this MDT
        """
        command = ("umount %s" % (self.lmdt_mnt))
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
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    # index: 0, 1, etc.
    def __init__(self, lustre_fs, index, host, device, mnt,
                 backfs_type=LDISKFS):
        # pylint: disable=too-many-arguments
        self.lost_lustre_fs = lustre_fs
        self.lost_index = index
        self.lost_host = host
        self.lost_device = device
        self.lost_mnt = mnt
        self.lost_backfs_type = backfs_type
        if self.lost_backfs_type == ZFS:
            self.lost_zfs_pool = "pool_%s_ost_%s" % (lustre_fs.lf_fsname, index)
            self.lost_zfs_fsname = "fs_ost_%s" % index
        else:
            self.lost_zfs_pool = None
            self.lost_zfs_fsname = None

        ret, index_string = lustre_ost_index2string(index)
        if ret:
            reason = ("invalid OST index [%s]" % (index))
            logging.error(reason)
            raise Exception(reason)
        self.lost_index_string = index_string

        ret = host.lsh_ost_add(lustre_fs.lf_fsname, index, self)
        if ret:
            reason = ("OST [%s:%d] already exists in host [%s]" %
                      (lustre_fs.lf_fsname, index, host.sh_hostname))
            logging.error(reason)
            raise Exception(reason)

        ret = lustre_fs.lf_ost_add(index, self)
        if ret:
            reason = ("OST [%d] already exists in file system [%s]" %
                      (index, lustre_fs.lf_fsname))
            logging.error(reason)
            raise Exception(reason)
        lustre_fs.lf_osts[index] = self

    def lost_format(self):
        """
        Format this OST
        """
        if self.lost_backfs_type == ZFS:
            command = ("mkfs.lustre --fsname %s --backfstype zfs --ost "
                       "--reformat --mgsnode=%s --index=%s %s/%s %s" %
                       (self.lost_lustre_fs.lf_fsname,
                        self.lost_lustre_fs.lf_mgs_nid,
                        self.lost_index,
                        self.lost_zfs_pool,
                        self.lost_zfs_fsname,
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
        command = ("mkfs.lustre --fsname %s --ost "
                   "--reformat --mgsnode=%s --index=%s %s" %
                   (self.lost_lustre_fs.lf_fsname,
                    self.lost_lustre_fs.lf_mgs_nid,
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

    def lost_mount(self):
        """
        Mount this OST
        """
        if self.lost_backfs_type == ZFS:
            command = ("mkdir -p %s && mount -t lustre %s/%s %s" %
                       (self.lost_mnt, self.lost_zfs_pool,
                        self.lost_zfs_fsname, self.lost_mnt))
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

        command = ("mkdir -p %s && mount -t lustre %s %s" %
                   (self.lost_mnt, self.lost_device, self.lost_mnt))
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

    def lost_umount(self):
        """
        Umount this OST
        """
        command = ("umount %s" % (self.lost_mnt))
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


class LustreClient(object):
    """
    Lustre client
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, lustre_fs, host, mnt):
        # pylint: disable=too-many-arguments
        self.lc_lustre_fs = lustre_fs
        self.lc_host = host
        self.lc_mnt = mnt
        index = ("%s:%s" % (host.sh_hostname, mnt))
        if index in lustre_fs.lf_clients:
            reason = ("client [%d] already exists in file system [%s]",
                      (index, lustre_fs.lf_fsname))
            raise Exception(reason)
        lustre_fs.lf_clients[index] = self

    def lc_mount(self):
        """
        Mount this client
        """
        command = ("mkdir -p %s && mount -t lustre %s:/%s %s" %
                   (self.lc_mnt, self.lc_lustre_fs.lf_mgs_nid,
                    self.lc_lustre_fs.lf_fsname, self.lc_mnt))
        retval = self.lc_host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.lc_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def lc_umount(self):
        """
        Umount this client
        """
        command = ("umount %s" % (self.lc_mnt))
        retval = self.lc_host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.lc_host.sh_hostname,
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
    def __init__(self, name, rpm_patterns,
                 kernel_major_version):
        # pylint: disable=too-few-public-methods,too-many-arguments
        self.lv_name = name
        self.lv_rpm_patterns = rpm_patterns
        self.lv_kernel_major_version = kernel_major_version

RPM_KERNEL = "kernel"
RPM_KERNEL_FIRMWARE = "kernel-firmware"
RPM_LUSTRE = "lustre"
RPM_IOKIT = "iokit"

# Following three RPMs only in EXAScaler3
RPM_KMOD_COMMON = "kmod_common"
RPM_LUSTER_SERVER = "lustre_server"
RPM_KMOD_LDISKFS = "kmod_ldiskfs"

RPM_KMOD = "kmod"
RPM_OSD_LDISKFS = "osd_ldiskfs"
RPM_OSD_LDISKFS_MOUNT = "osd_ldiskfs_mount"
RPM_OSD_ZFS = "osd_zfs"
RPM_OSD_ZFS_MOUNT = "osd_zfs_mount"
RPM_TESTS = "tests"
RPM_TESTS_KMOD = "tests_kmod"
RPM_MLNX_OFA = "mlnx_ofa"
RPM_MLNX_KMOD = "mlnx_ofa_modules"

LUSTRE_ZFS_RPM_TYPES = [RPM_OSD_ZFS, RPM_OSD_ZFS_MOUNT]

# The order should be proper for the dependency of RPMs
LUSTRE_RPM_TYPES = [RPM_KMOD_COMMON,  # Only in EXAScaler3
                    RPM_KMOD,
                    RPM_OSD_LDISKFS_MOUNT,
                    RPM_KMOD_LDISKFS,  # Only in EXAScaler3
                    RPM_OSD_LDISKFS,
                    RPM_OSD_ZFS_MOUNT,
                    RPM_OSD_ZFS,
                    RPM_LUSTRE,
                    RPM_LUSTER_SERVER,  # Only in EXAScaler3
                    RPM_IOKIT,
                    RPM_TESTS_KMOD,
                    RPM_TESTS]

ES2_PATTERNS = {
    RPM_KERNEL: r"^(kernel-2.+\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.5.+\.rpm)$",
    RPM_IOKIT: r"^(lustre-iokit-2\.5.+\.rpm)$",
    RPM_KMOD: r"^(lustre-modules-2\.5.+\.rpm)$",
    RPM_OSD_LDISKFS: r"^(lustre-osd-ldiskfs-2\.5.+\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.5.+\.rpm)$",
    RPM_OSD_ZFS: r"^(lustre-osd-zfs-2\.5.+\.rpm)$",
    RPM_OSD_ZFS_MOUNT: r"^(lustre-osd-zfs-mount-2\.5.+\.rpm)$",
    RPM_TESTS: r"^(lustre-tests-2\.5.+\.rpm)$",
    RPM_MLNX_OFA: r"^(mlnx-ofa_kernel-\d.+\.rpm)$",
    RPM_MLNX_KMOD: r"^(mlnx-ofa_kernel-modules-\d.+\.rpm)$"}

LUSTRE_VERSION_NAME_ES2 = "es2"

LUSTRE_VERSION_ES2 = LustreVersion(LUSTRE_VERSION_NAME_ES2,
                                   ES2_PATTERNS,  # rpm_patterns
                                   "2")  # kernel_major_version

ES3_PATTERNS = {
    RPM_KERNEL: r"^(kernel-lustre-3.+\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.7.+\.rpm)$",
    RPM_LUSTER_SERVER: r"^(lustre-server-2\.7.+\.rpm)$",
    RPM_IOKIT: r"^(lustre-iokit-2\.7.+\.rpm)$",
    RPM_KMOD_COMMON: r"^(kmod-lustre-common-2\.7.+\.rpm)$",
    RPM_KMOD: r"^(kmod-lustre-el7\.\d-2\.7.+\.rpm)$",
    RPM_KMOD_LDISKFS: r"^(kmod-lustre-el7\.\d-ldiskfs-2\.7.+\.rpm)$",
    RPM_OSD_LDISKFS: r"^(kmod-lustre-el7\.\d-osd-ldiskfs-2\.7.+\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.7.+\.rpm)$",
    RPM_TESTS: r"^(lustre-tests-2\.7.+\.rpm)$",
    RPM_MLNX_OFA: r"^(mlnx-ofa_kernel-\d.+\.rpm)$",
    RPM_MLNX_KMOD: r"^(kmod-mlnx-ofa_kernel-el7\.\d-lustre-3.+\.rpm)$"}

LUSTRE_VERSION_NAME_ES3 = "es3"

ES3_HAS_DEPENDENCY_PROBLEM = True

LUSTRE_VERSION_ES3 = LustreVersion(LUSTRE_VERSION_NAME_ES3,
                                   ES3_PATTERNS,  # rpm_patterns
                                   "3")  # kernel_major_version

ES4_PATTERNS = {
    RPM_KERNEL: r"^(kernel-3.+\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.10\.\d+_ddn.+\.rpm)$",
    RPM_IOKIT: r"^(lustre-iokit-2\.10\.\d+_ddn.+\.rpm)$",
    RPM_KMOD: r"^(kmod-lustre-2\.10\.\d+_ddn.+\.rpm)$",
    RPM_OSD_LDISKFS: r"^(kmod-lustre-osd-ldiskfs-2\.10\.\d+_ddn.+\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.10.+\.rpm)$",
    RPM_OSD_ZFS: r"^(kmod-lustre-osd-zfs-2\.10\.\d+_ddn.+\.rpm)$",
    RPM_OSD_ZFS_MOUNT: r"^(lustre-osd-zfs-mount-2\.10\.\d+_ddn.+\.rpm)$",
    RPM_TESTS: r"^(lustre-tests-2\.10\.\d+_ddn.+\.rpm)$",
    RPM_TESTS_KMOD: r"^(kmod-lustre-tests-2\.10\.\d+_ddn.+\.rpm)$",
}

LUSTRE_VERSION_NAME_ES4 = "es4"

LUSTRE_VERSION_ES4 = LustreVersion(LUSTRE_VERSION_NAME_ES4,
                                   ES4_PATTERNS,  # rpm_patterns
                                   "3")  # kernel_major_version

LUSTRE_VERSION_NAME_2_10 = "2.10"

B2_10_PATTERNS = {
    RPM_KERNEL: r"^(kernel-3.+\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.10.+\.rpm)$",
    RPM_IOKIT: r"^(lustre-iokit-2\.10.+\.rpm)$",
    RPM_KMOD: r"^(kmod-lustre-2\.10.+\.rpm)$",
    RPM_OSD_LDISKFS: r"^(kmod-lustre-osd-ldiskfs-2\.10.+\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.10.+\.rpm)$",
    RPM_OSD_ZFS: r"^(kmod-lustre-osd-zfs-2\.10.+\.rpm)$",
    RPM_OSD_ZFS_MOUNT: r"^(lustre-osd-zfs-mount-2\.10.+\.rpm)$",
    RPM_TESTS: r"^(lustre-tests-2\.10.+\.rpm)$",
    RPM_TESTS_KMOD: r"^(kmod-lustre-tests-2\.10.+\.rpm)$",
}

LUSTRE_VERSION_2_10 = LustreVersion(LUSTRE_VERSION_NAME_2_10,
                                    ES4_PATTERNS,  # rpm_patterns
                                    "3")  # kernel_major_version


B2_7_PATTERNS = {
    RPM_KERNEL: r"^(kernel-3.+\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.7.+\.rpm)$",
    RPM_IOKIT: r"^(lustre-iokit-2\.7.+\.rpm)$",
    RPM_KMOD: r"^(lustre-modules-2\.7.+\.rpm)$",
    RPM_OSD_LDISKFS: r"^(lustre-osd-ldiskfs-2\.7.+\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.7.+\.rpm)$",
    RPM_OSD_ZFS: r"^(lustre-osd-zfs-2\.7.+\.rpm)$",
    RPM_OSD_ZFS_MOUNT: r"^(lustre-osd-zfs-mount-2\.7.+\.rpm)$",
    RPM_TESTS: r"^(lustre-tests-2\.7.+\.rpm)$",
    RPM_MLNX_OFA: r"^(mlnx-ofa_kernel-\d.+\.rpm)$",
    RPM_MLNX_KMOD: r"^(mlnx-ofa_kernel-modules-\d.+\.rpm)$"}

LUSTRE_VERSION_NAME_2_7 = "2.7"

LUSTRE_VERSION_2_7 = LustreVersion(LUSTRE_VERSION_NAME_2_7,
                                   B2_7_PATTERNS,  # rpm_patterns
                                   "3")  # kernel_major_version


B2_12_PATTERNS = {
    RPM_KERNEL: r"^(kernel-3.+\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.12.+\.rpm)$",
    RPM_KMOD: r"^(kmod-lustre-2\.12.+\.rpm)$",
    RPM_OSD_LDISKFS: r"^(kmod-lustre-osd-ldiskfs-2\.12.+\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.12.+\.rpm)$",
    RPM_OSD_ZFS: r"^(kmod-lustre-osd-zfs-2\.12.+\.rpm)$",
    RPM_OSD_ZFS_MOUNT: r"^(lustre-osd-zfs-mount-2\.12.+\.rpm)$"}

LUSTRE_VERSION_NAME_2_12 = "2.12"

LUSTRE_VERSION_2_12 = LustreVersion(LUSTRE_VERSION_NAME_2_12,
                                    B2_12_PATTERNS,  # rpm_patterns
                                    "3")  # kernel_major_version
B2_13_PATTERNS = {
    RPM_KERNEL: r"^(kernel-3.+\.rpm)$",
    RPM_LUSTRE: r"^(lustre-2\.13.+\.rpm)$",
    RPM_KMOD: r"^(kmod-lustre-2\.13.+\.rpm)$",
    RPM_OSD_LDISKFS: r"^(kmod-lustre-osd-ldiskfs-2\.13.+\.rpm)$",
    RPM_OSD_LDISKFS_MOUNT: r"^(lustre-osd-ldiskfs-mount-2\.13.+\.rpm)$",
    RPM_OSD_ZFS: r"^(kmod-lustre-osd-zfs-2\.13.+\.rpm)$",
    RPM_OSD_ZFS_MOUNT: r"^(lustre-osd-zfs-mount-2\.13.+\.rpm)$"}

LUSTRE_VERSION_NAME_2_13 = "2.13"

LUSTRE_VERSION_2_13 = LustreVersion(LUSTRE_VERSION_NAME_2_13,
                                    B2_13_PATTERNS,  # rpm_patterns
                                    "3")  # kernel_major_version

LUSTER_VERSIONS = [LUSTRE_VERSION_ES2, LUSTRE_VERSION_ES3, LUSTRE_VERSION_ES4,
                   LUSTRE_VERSION_2_7, LUSTRE_VERSION_2_10, LUSTRE_VERSION_2_12,
                   LUSTRE_VERSION_2_13]

LUSTRE_VERSION_NAME_ERROR = "error"

LUSTER_VERSION_NAMES = [LUSTRE_VERSION_NAME_ES2, LUSTRE_VERSION_NAME_ES3,
                        LUSTRE_VERSION_NAME_ES4, LUSTRE_VERSION_NAME_2_7,
                        LUSTRE_VERSION_NAME_2_10, LUSTRE_VERSION_NAME_2_12,
                        LUSTRE_VERSION_NAME_2_13, LUSTRE_VERSION_NAME_ERROR]


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
                    logging.error("RPM [%s] can be matched to both type [%s] "
                                  "and [%s]", value, rpm_type, key)
                    return -1

                if rpm_name is not None and rpm_name != value:
                    logging.error("RPM [%s] can be matched as both name [%s] "
                                  "and [%s]", value, rpm_name, value)
                    return -1

                rpm_type = key
                rpm_name = value
                matched = True
                logging.debug("match of key [%s]: [%s] by data [%s]",
                              key, value, data)
        if matched:
            matched_versions.append(version)

    if len(matched_versions) != 0:
        if rpm_type in rpm_dict:
            logging.error("multiple match of RPM type [%s], both from [%s] "
                          "and [%s]", rpm_type, rpm_name, rpm_dict[rpm_type])
            return -1
        for version in possible_versions[:]:
            if version not in matched_versions:
                possible_versions.remove(version)
        rpm_dict[rpm_type] = rpm_name

    return 0


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
        self.lr_zfs_support = True

    def lr_prepare(self):
        """
        Prepare the RPMs
        """
        rpm_files = os.listdir(self.lr_rpm_dir)

        possible_versions = LUSTER_VERSIONS[:]
        for rpm_file in rpm_files:
            logging.debug("found file [%s] in directory [%s]",
                          rpm_file, self.lr_rpm_dir)
            ret = match_rpm_patterns(rpm_file, self.lr_rpm_names,
                                     possible_versions)
            if ret:
                logging.error("failed to match pattern for file [%s]",
                              rpm_file)
                return -1

        if len(possible_versions) != 1:
            logging.info("the possible RPM version is [%d], "
                         "using the first matched one [%s]",
                         len(possible_versions), possible_versions[0])
        self.lr_lustre_version = possible_versions[0]

        for key in self.lr_lustre_version.lv_rpm_patterns.keys():
            if key not in self.lr_rpm_names:
                if key in LUSTRE_ZFS_RPM_TYPES:
                    logging.info("disabling ZFS support, because no RPM [%s] "
                                 "found", key)
                    self.lr_zfs_support = False
                else:
                    logging.error("failed to get RPM name of [%s]", key)
                    return -1

        if self.lr_zfs_support:
            for key in LUSTRE_ZFS_RPM_TYPES:
                if key not in self.lr_rpm_names:
                    logging.info("disabling ZFS support, because no [%s] "
                                 "defined in RPM patterns", key)
                    self.lr_zfs_support = False
                    break

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


def failure_caused_by_ksym(retval):
    """
    Check whether the kmod RPM installation failed because of dependency
    on ksym
    """
    lines = retval.cr_stderr.split('\n')
    if len(lines) < 1:
        logging.debug("line number doesn't match: [%d]", len(lines))
        return False
    if lines[0] != "error: Failed dependencies:":
        logging.debug("first line doesn't match: [%s]", lines[0])
        return False
    ksym_pattern = r"^.+ksym.+ is needed by .+$"
    for line in lines[1:]:
        if line == "":
            continue
        matched = re.match(ksym_pattern, line, re.M)
        if not matched:
            logging.debug("line doesn't match: [%s]", line)
            return False
    return True


def lustre_client_id(fsname, mnt):
    """
    Return the Lustre client ID
    """
    return "%s:%s" % (fsname, mnt)


def lustre_ost_id(fsname, ost_index):
    """
    Return the Lustre client ID
    """
    return "%s:%s" % (fsname, ost_index)


def lustre_mdt_id(fsname, mdt_index):
    """
    Return the Lustre client ID
    """
    return "%s:%s" % (fsname, mdt_index)


class LustreServerHost(ssh_host.SSHHost):
    # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    Each host being used to run Lustre tests has an object of this
    """
    def __init__(self, hostname, identity_file=None, local=False, host_id=None):
        super(LustreServerHost, self).__init__(hostname,
                                               identity_file=identity_file,
                                               local=local,
                                               host_id=host_id)
        # key: $fsname:$mnt, value: LustreClient object
        self.lsh_clients = {}
        # Key: $fsname:$ost_index, value: LustreOST object
        self.lsh_osts = {}
        # Key: $fsname:$mdt_index, value: LustreMDT object
        self.lsh_mdts = {}
        self.lsh_cached_has_fuser = None
        self.lsh_fuser_install_failed = False

    def lsh_has_fuser(self):
        """
        Check whether host has fuser
        """
        # pylint: disable=too-many-return-statements,too-many-branches
        if self.lsh_cached_has_fuser is not None:
            return self.lsh_cached_has_fuser

        ret = self.sh_run("which fuser")
        if ret.cr_exit_status != 0:
            self.lsh_cached_has_fuser = False
        else:
            self.lsh_cached_has_fuser = True
        return self.lsh_cached_has_fuser

    def lsh_fuser_kill(self, fpath):
        """
        Run "fuser -km" to a fpath
        """
        if not self.lsh_has_fuser() and not self.lsh_fuser_install_failed:
            logging.debug("host [%s] doesnot have fuser, trying to install",
                          self.sh_hostname)
            ret = self.sh_run("yum install psmisc -y")
            if ret.cr_exit_status:
                logging.error("failed to install fuser")
                self.lsh_fuser_install_failed = True
                return -1
            self.sh_cached_has_rsync = True

        command = ("fuser -km %s" % (fpath))
        retval = self.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0

    def lsh_ost_add(self, fsname, ost_index, ost):
        """
        Add OST into this host
        """
        ost_id = lustre_ost_id(fsname, ost_index)
        if ost_id in self.lsh_osts:
            return -1
        self.lsh_osts[ost_id] = ost
        return 0

    def lsh_mdt_add(self, fsname, mdt_index, mdt):
        """
        Add MDT into this host
        """
        mdt_id = lustre_mdt_id(fsname, mdt_index)
        if mdt_id in self.lsh_mdts:
            return -1
        self.lsh_mdts[mdt_id] = mdt
        return 0

    def lsh_client_add(self, fsname, mnt, client):
        """
        Add MDT into this host
        """
        client_id = lustre_client_id(fsname, mnt)
        if client_id in self.lsh_clients:
            return -1
        self.lsh_clients[client_id] = client
        return 0

    def lsh_lustre_device_label(self, device):
        """
        Run e2label on a lustre device
        """
        if device[0] == '/':
            # Likely Ext4 device
            command = ("e2label %s" % device)
        else:
            command = ("zfs get -o value -H lustre:svname %s" % device)
        retval = self.sh_run(command)
        if retval.cr_exit_status != 0:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command, self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1, None
        return 0, retval.cr_stdout.strip()

    def lsh_lustre_detect_services(self, clients, osts, mdts, add_found=False):
        """
        Detect mounted Lustre services (MDT/OST/clients) from the host
        """
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        server_pattern = (r"^(?P<device>\S+) (?P<mount_point>\S+) lustre .+$")
        server_regular = re.compile(server_pattern)

        client_pattern = (r"^.+:/(?P<fsname>\S+) (?P<mount_point>\S+) lustre .+$")
        client_regular = re.compile(client_pattern)

        ost_pattern = (r"^(?P<fsname>\S+)-OST(?P<index_string>[0-9a-f]{4})$")
        ost_regular = re.compile(ost_pattern)

        mdt_pattern = (r"^(?P<fsname>\S+)-MDT(?P<index_string>[0-9a-f]{4})$")
        mdt_regular = re.compile(mdt_pattern)

        # Detect Lustre services
        command = ("cat /proc/mounts")
        retval = self.sh_run(command)
        if retval.cr_exit_status != 0:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command, self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        for line in retval.cr_stdout.splitlines():
            logging.debug("checking line [%s]", line)
            match = server_regular.match(line)
            if not match:
                continue

            device = match.group("device")
            mount_point = match.group("mount_point")

            match = client_regular.match(line)
            if match:
                fsname = match.group("fsname")
                client_id = lustre_client_id(fsname, mount_point)
                if client_id in self.lsh_clients:
                    client = self.lsh_clients[client_id]
                else:
                    lustre_fs = LustreFilesystem(fsname)
                    client = LustreClient(lustre_fs, self, mount_point)
                    if add_found:
                        self.lsh_client_add(fsname, mount_point, client)
                clients[client_id] = client
                logging.debug("client [%s] mounted on dir [%s] of host [%s]",
                              fsname, mount_point, self.sh_hostname)
                continue

            ret, label = self.lsh_lustre_device_label(device)
            if ret:
                logging.error("failed to get the label of device [%s] on "
                              "host [%s]", device, self.sh_hostname)
                return -1

            match = ost_regular.match(label)
            if match:
                fsname = match.group("fsname")
                index_string = match.group("index_string")
                ret, ost_index = lustre_string2index(index_string)
                if ret:
                    logging.error("invalid label [%s] of device [%s] on "
                                  "host [%s]", label, device, self.sh_hostname)
                    return -1
                ost_id = lustre_ost_id(fsname, ost_index)
                if ost_id in self.lsh_osts:
                    ost = self.lsh_osts[ost_id]
                else:
                    lustre_fs = LustreFilesystem(fsname)
                    ost = LustreOST(lustre_fs, ost_index, self, device, mount_point)
                    if add_found:
                        self.lsh_ost_add(fsname, ost_index, ost)
                osts[ost_id] = ost
                logging.debug("OST [%s] mounted on dir [%s] of host [%s]",
                              fsname, mount_point, self.sh_hostname)
                continue

            match = mdt_regular.match(label)
            if match:
                fsname = match.group("fsname")
                index_string = match.group("index_string")
                ret, mdt_index = lustre_string2index(index_string)
                if ret:
                    logging.error("invalid label [%s] of device [%s] on "
                                  "host [%s]", label, device, self.sh_hostname)
                    return -1
                mdt_id = lustre_mdt_id(fsname, mdt_index)
                if mdt_id in self.lsh_mdts:
                    mdt = self.lsh_mdts[mdt_id]
                else:
                    lustre_fs = LustreFilesystem(fsname)
                    mdt = LustreMDT(lustre_fs, mdt_index, self, device, mount_point)
                    if add_found:
                        self.lsh_mdt_add(fsname, mdt_index, mdt)
                mdts[mdt_id] = mdt
                logging.debug("MDT [%s] mounted on dir [%s] of host [%s]",
                              fsname, mount_point, self.sh_hostname)
                continue
            logging.error("unable to detect service mounted on dir [%s] of "
                          "host [%s]", mount_point, self.sh_hostname)
            return -1

        return 0

    def lsh_lustre_umount_services(self, client_only=False):
        """
        Umount Lustre OSTs/MDTs/clients on the host
        """
        # pylint: disable=too-many-return-statements
        clients = {}
        osts = {}
        mdts = {}
        ret = self.lsh_lustre_detect_services(clients, osts, mdts)
        if ret:
            logging.error("failed to detect Lustre services on host [%s]",
                          self.sh_hostname)
            return -1

        for client in clients.values():
            command = ("umount %s" % client.lc_mnt)
            retval = self.sh_run(command)
            if retval.cr_exit_status:
                logging.debug("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
            else:
                continue

            # Kill the user of Lustre client so that umount won't be stopped
            ret = self.lsh_fuser_kill(client.lc_mnt)
            if ret:
                logging.error("failed to kill processes using [%s]", client.lc_mnt)
                return -1

            command = ("umount %s" % client.lc_mnt)
            retval = self.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        if client_only:
            return 0

        for mdt in mdts.values():
            command = ("umount %s" % mdt.lmdt_mnt)
            retval = self.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        for ost in osts.values():
            command = ("umount %s" % ost.lost_mnt)
            retval = self.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1
        return 0

    def lsh_lustre_uninstall(self):
        # pylint: disable=too-many-return-statements,too-many-branches
            # pylint: disable=too-many-statements
        """
        Uninstall Lustre RPMs
        """
        logging.info("uninstalling Lustre RPMs on host [%s]", self.sh_hostname)

        ret = self.sh_run("rpm --rebuilddb")
        if ret.cr_exit_status != 0:
            logging.error("failed to run 'rpm --rebuilddb' on host "
                          "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                          self.sh_hostname, ret.cr_exit_status,
                          ret.cr_stdout, ret.cr_stderr)
            return -1

        logging.info("killing all processes that run yum commands"
                     "on host [%s]",
                     self.sh_hostname)
        ret = self.sh_run("ps aux | grep -v grep | grep yum | "
                          "awk '{print $2}'")
        if ret.cr_exit_status != 0:
            logging.error("failed to kill yum processes on host "
                          "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                          self.sh_hostname, ret.cr_exit_status,
                          ret.cr_stdout, ret.cr_stderr)
            return -1

        for pid in ret.cr_stdout.splitlines():
            logging.info("killing pid [%s] on host [%s]",
                         pid, self.sh_hostname)
            ret = self.sh_run("kill -9 %s" % pid)
            if ret.cr_exit_status != 0:
                logging.error("failed to kill pid [%s] on host "
                              "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                              pid, self.sh_hostname, ret.cr_exit_status,
                              ret.cr_stdout, ret.cr_stderr)
                return -1

        logging.info("running yum-complete-transaction in case of broken yum "
                     "on host [%s]", self.sh_hostname)
        ret = self.sh_run("which yum-complete-transaction")
        if ret.cr_exit_status != 0:
            ret = self.sh_run("yum install yum-utils -y")
            if ret.cr_exit_status != 0:
                logging.error("failed to install yum-utils on host "
                              "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                              self.sh_hostname, ret.cr_exit_status,
                              ret.cr_stdout, ret.cr_stderr)
                return -1

        ret = self.sh_run("yum-complete-transaction")
        if ret.cr_exit_status != 0:
            logging.error("failed to run yum-complete-transaction on host "
                          "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                          self.sh_hostname, ret.cr_exit_status,
                          ret.cr_stdout, ret.cr_stderr)
            return -1

        logging.info("installing backup kernel in case something bad happens "
                     "to Luster kernel on host [%s]", self.sh_hostname)
        ret = self.sh_run("package-cleanup --oldkernels --count=2 -y")
        if ret.cr_exit_status != 0:
            logging.error("failed to cleanup old kernels on host [%s], "
                          "ret = %d, stdout = [%s], stderr = [%s]",
                          self.sh_hostname, ret.cr_exit_status,
                          ret.cr_stdout, ret.cr_stderr)
            return -1

        ret = self.sh_run("yum install kernel -y", timeout=1800)
        if ret.cr_exit_status != 0:
            logging.error("failed to install backup kernel on host [%s], "
                          "ret = %d, stdout = [%s], stderr = [%s]",
                          self.sh_hostname, ret.cr_exit_status,
                          ret.cr_stdout, ret.cr_stderr)
            return -1

        logging.info("uninstalling Lustre RPMs on host [%s]",
                     self.sh_hostname)
        ret = self.sh_rpm_find_and_uninstall("grep lustre")
        if ret != 0:
            logging.error("failed to uninstall Lustre RPMs on host "
                          "[%s]", self.sh_hostname)
            return -1

        zfs_rpms = ["libnvpair1", "libuutil1", "libzfs2", "libzpool2",
                    "kmod-spl", "kmod-zfs", "spl", "zfs"]
        rpm_string = ""
        for zfs_rpm in zfs_rpms:
            retval = self.sh_run("rpm -qi %s" % zfs_rpm)
            if retval.cr_exit_status == 0:
                if rpm_string != "":
                    rpm_string += " "
                rpm_string += zfs_rpm

        if rpm_string != "":
            retval = self.sh_run("rpm -e %s" % rpm_string)
            if retval.cr_exit_status != 0:
                logging.error("failed to uninstall ZFS RPMs on host "
                              "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                              self.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        logging.info("uninstalled RPMs on host [%s]", self.sh_hostname)
        return 0

    def lsh_lustre_utils_install(self):
        # pylint: disable=too-many-return-statements,too-many-branches
        """
        Install other util RPMs required by running Lustre tests
        """
        logging.info("installing requested utils of Lustre on host [%s]",
                     self.sh_hostname)

        # attr, bc, dbench: lustre test RPM
        # lsof: mlnx-ofa_kernel and mlnx-ofa_kernel-modules RPM
        # net-snmp-libs, net-snmp-agent-libs: lustre RPM
        # pciutils: ?
        # pdsh: lustre test RPM
        # procps: ?
        # sg3_utils: ?
        # nfs, nfs-utils: LATEST itself.
        dependent_rpms = ["attr", "bc", "dbench", "bzip2", "lsof",
                          "net-snmp-libs", "pciutils", "pdsh", "procps",
                          "sg3_utils", "nfs-utils", "sysstat"]

        distro = self.sh_distro()
        if distro == ssh_host.DISTRO_RHEL7:
            dependent_rpms += ["net-snmp-agent-libs"]
        elif distro == ssh_host.DISTRO_RHEL6:
            pass
        else:
            logging.error("unsupported distro of host [%s]",
                          self.sh_hostname)
            return -1

        retval = self.sh_run("rpm -qa | grep epel-release")
        if retval.cr_exit_status != 0:
            retval = self.sh_run("yum install epel-release -y")
            if retval.cr_exit_status != 0:
                logging.error("failed to install EPEL RPM on host [%s]",
                              self.sh_hostname)
                return -1

        command = "yum install -y"
        for rpm in dependent_rpms:
            command += " " + rpm

        retval = self.sh_run(command)
        if retval.cr_exit_status != 0:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        host_key_config = "StrictHostKeyChecking no"
        retval = self.sh_run(r"grep StrictHostKeyChecking /etc/ssh/ssh_config "
                             r"| grep -v \#")
        if retval.cr_exit_status != 0:
            retval = self.sh_run("echo '%s' >> /etc/ssh/ssh_config" %
                                 host_key_config)
            if retval.cr_exit_status != 0:
                logging.error("failed to change ssh config on host [%s]",
                              self.sh_hostname)
                return -1
        elif retval.cr_stdout != host_key_config + "\n":
            logging.error("unexpected StrictHostKeyChecking config on host "
                          "[%s], expected [%s], got [%s]",
                          self.sh_hostname, host_key_config, retval.cr_stdout)
            return -1

        # RHEL6 doesn't has perl-File-Path in yum by default
        if distro == ssh_host.DISTRO_RHEL7:
            # perl-File-Path is reqired by lustre-iokit
            retval = self.sh_run("yum install perl-File-Path -y")
            if retval.cr_exit_status != 0:
                logging.error("failed to install perl-File-Path on host [%s]",
                              self.sh_hostname)
                return -1

        logging.info("installed requested utils of Lustre on host [%s]",
                     self.sh_hostname)
        return 0

    def lsh_install_e2fsprogs(self, workspace, e2fsprogs_dir):
        """
        Install e2fsprogs RPMs for Lustre
        """
        # pylint: disable=too-many-return-statements
        command = ("mkdir -p %s" % workspace)
        retval = self.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        basename = os.path.basename(e2fsprogs_dir)
        host_copying_rpm_dir = workspace + "/" + basename
        host_e2fsprogs_rpm_dir = workspace + "/" + "e2fsprogs_rpms"

        ret = self.sh_send_file(e2fsprogs_dir, workspace)
        if ret:
            logging.error("failed to send Lustre RPMs [%s] on local host to "
                          "directory [%s] on host [%s]",
                          e2fsprogs_dir, workspace,
                          self.sh_hostname)
            return -1

        command = ("mv %s %s" % (host_copying_rpm_dir, host_e2fsprogs_rpm_dir))
        retval = self.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        retval = self.sh_run(r"rpm -qp %s/`ls %s | grep '.rpm$' | grep "
                             r"'^e2fsprogs-[0-9]' | head -1` "
                             r"--queryformat '%%{version} %%{url}'" %
                             (host_e2fsprogs_rpm_dir, host_e2fsprogs_rpm_dir))
        if retval.cr_exit_status != 0:
            logging.error("no e2fsprogs rpms is provided under "
                          "directory [%s] on host [%s]",
                          host_e2fsprogs_rpm_dir, self.sh_hostname)
            return -1

        info = retval.cr_stdout.strip().split(" ")
        pattern = re.compile(r'hpdd.intel|whamcloud')
        if ('wc' not in info[0]) or (not re.search(pattern, info[1])):
            logging.error("e2fsprogs rpms provided under directory [%s] on "
                          "host [%s] don't have proper version, expected it"
                          "comes from hpdd.intel or whamcloud",
                          host_e2fsprogs_rpm_dir, self.sh_hostname)
            return -1
        rpm_version = info[0]

        need_install = False
        retval = self.sh_run("rpm -q e2fsprogs "
                             "--queryformat '%{version} %{url}'")
        if retval.cr_exit_status != 0:
            need_install = True
        else:
            info = retval.cr_stdout.strip().split(" ")
            pattern = re.compile(r'hpdd.intel|whamcloud')
            if ('wc' not in info[0]) or (not re.search(pattern, info[1])):
                need_install = True

            current_version = info[0]
            if rpm_version != current_version:
                need_install = True

        if not need_install:
            logging.info("e2fsprogs RPMs under [%s] on host [%s] is already "
                         "installed", host_e2fsprogs_rpm_dir, self.sh_hostname)
            return 0

        logging.info("installing e2fsprogs RPMs under [%s] on host [%s]",
                     host_e2fsprogs_rpm_dir, self.sh_hostname)
        retval = self.sh_run("rpm -Uvh %s/*.rpm" % host_e2fsprogs_rpm_dir)
        if retval.cr_exit_status != 0:
            logging.error("failed to install RPMs under [%s] of e2fsprogs on "
                          "host [%s], ret = %d, stdout = [%s], stderr = [%s]",
                          host_e2fsprogs_rpm_dir, self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout, retval.cr_stderr)
            return -1

        logging.info("installed e2fsprogs RPMs under [%s] on host [%s]",
                     host_e2fsprogs_rpm_dir, self.sh_hostname)
        return 0

    def lsh_lustre_install(self, workspace, lustre_rpms, e2fsprogs_rpm_dir):
        """
        Install Lustre RPMs on a host
        """
        # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements
        command = ("mkdir -p %s" % workspace)
        retval = self.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        basename = os.path.basename(lustre_rpms.lr_rpm_dir)
        host_copying_rpm_dir = workspace + "/" + basename
        host_lustre_rpm_dir = workspace + "/" + "lustre_rpms"

        ret = self.sh_send_file(lustre_rpms.lr_rpm_dir, workspace)
        if ret:
            logging.error("failed to send Lustre RPMs [%s] on local host to "
                          "directory [%s] on host [%s]",
                          lustre_rpms.lr_rpm_dir, workspace,
                          self.sh_hostname)
            return -1

        command = ("mv %s %s" % (host_copying_rpm_dir, host_lustre_rpm_dir))
        retval = self.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        if self.lsh_lustre_utils_install() != 0:
            logging.error("failed to install requested utils of Lustre on host [%s]",
                          self.sh_hostname)
            return -1

        # always update dracut-kernel first
        logging.info("installing dracut-kernel RPM on host [%s]",
                     self.sh_hostname)
        retval = self.sh_run("yum update dracut-kernel -y")
        if retval.cr_exit_status != 0:
            logging.error("failed to install dracut-kernel RPM on "
                          "host [%s], ret = %d, stdout = [%s], stderr = [%s]",
                          self.sh_hostname, retval.cr_exit_status,
                          retval.cr_stdout, retval.cr_stderr)
            return -1

        logging.info("installing kernel RPM on host [%s]",
                     self.sh_hostname)
        if RPM_KERNEL_FIRMWARE in lustre_rpms.lr_rpm_names:
            rpm_name = lustre_rpms.lr_rpm_names[RPM_KERNEL_FIRMWARE]
            retval = self.sh_run("rpm -ivh --force %s/%s" %
                                 (host_lustre_rpm_dir, rpm_name),
                                 timeout=ssh_host.LONGEST_TIME_RPM_INSTALL)
            if retval.cr_exit_status != 0:
                logging.error("failed to install kernel RPM on host [%s], "
                              "ret = %d, stdout = [%s], stderr = [%s]",
                              self.sh_hostname, retval.cr_exit_status,
                              retval.cr_stdout, retval.cr_stderr)
                return -1

        rpm_name = lustre_rpms.lr_rpm_names[RPM_KERNEL]
        retval = self.sh_run("rpm -ivh --force %s/%s" %
                             (host_lustre_rpm_dir, rpm_name),
                             timeout=ssh_host.LONGEST_TIME_RPM_INSTALL)
        if retval.cr_exit_status != 0:
            logging.error("failed to install kernel RPM on host [%s], "
                          "ret = %d, stdout = [%s], stderr = [%s]",
                          self.sh_hostname, retval.cr_exit_status,
                          retval.cr_stdout, retval.cr_stderr)
            return -1

        if self.sh_distro() == ssh_host.DISTRO_RHEL6:
            # Since the VM might not have more than 8G memory, crashkernel=auto
            # won't save any memory for Kdump
            logging.info("changing boot argument of crashkernel on host [%s]",
                         self.sh_hostname)
            retval = self.sh_run("sed -i 's/crashkernel=auto/"
                                 "crashkernel=128M/g' /boot/grub/grub.conf")
            if retval.cr_exit_status != 0:
                logging.error("failed to change boot argument of crashkernel "
                              "on host [%s], ret = %d, stdout = [%s], "
                              "stderr = [%s]",
                              self.sh_hostname, retval.cr_exit_status,
                              retval.cr_stdout, retval.cr_stderr)
                return -1
        else:
            # Somehow crashkernel=auto doen't work for RHEL7 sometimes
            logging.info("changing boot argument of crashkernel on host [%s]",
                         self.sh_hostname)
            retval = self.sh_run("sed -i 's/crashkernel=auto/"
                                 "crashkernel=128M/g' /boot/grub2/grub.cfg")
            if retval.cr_exit_status != 0:
                logging.error("failed to change boot argument of crashkernel "
                              "on host [%s], ret = %d, stdout = [%s], "
                              "stderr = [%s]",
                              self.sh_hostname, retval.cr_exit_status,
                              retval.cr_stdout, retval.cr_stderr)
                return -1

        # install ofed if necessary
        logging.info("installing OFED RPM on host [%s]", self.sh_hostname)
        retval = self.sh_run("ls %s | grep mlnx-ofa_kernel" %
                             host_lustre_rpm_dir)

        if retval.cr_exit_status == 0:
            logging.info("installing OFED RPM on host [%s]",
                         self.sh_hostname)
            retval = self.sh_run("rpm -ivh --force "
                                 "%s/mlnx-ofa_kernel*.rpm" %
                                 host_lustre_rpm_dir)
            if retval.cr_exit_status != 0:
                retval = self.sh_run("yum localinstall -y --nogpgcheck "
                                     "%s/mlnx-ofa_kernel*.rpm" %
                                     host_lustre_rpm_dir)
                if retval.cr_exit_status != 0:
                    logging.error("failed to install OFED RPM on host [%s], "
                                  "ret = %d, stdout = [%s], stderr = [%s]",
                                  self.sh_hostname, retval.cr_exit_status,
                                  retval.cr_stdout, retval.cr_stderr)
                    return -1

        # install e2fsprogs-wc if necessary
        if self.lsh_install_e2fsprogs(workspace, e2fsprogs_rpm_dir):
            return -1

        # Remove any files under the test directory to avoid FID problem
        logging.info("removing directory [%s] on host [%s]",
                     LUSTRE_TEST_SCRIPT_DIR, self.sh_hostname)
        retval = self.sh_run("rm %s -fr" % LUSTRE_TEST_SCRIPT_DIR)
        if retval.cr_exit_status != 0:
            logging.error("failed to remove [%s] on host "
                          "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                          LUSTRE_TEST_SCRIPT_DIR, self.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        logging.info("installing ZFS RPMs on host [%s]", self.sh_hostname)
        if lustre_rpms.lr_zfs_support:
            install_timeout = ssh_host.LONGEST_SIMPLE_COMMAND_TIME * 2
            version = lustre_rpms.lr_lustre_version
            kernel_major_version = version.lv_kernel_major_version
            retval = self.sh_run("cd %s && rpm -ivh libnvpair1-* libuutil1-* "
                                 "libzfs2-0* libzpool2-0* kmod-spl-%s* "
                                 "kmod-zfs-%s* spl-0* zfs-0*" %
                                 (host_lustre_rpm_dir, kernel_major_version,
                                  kernel_major_version),
                                 timeout=install_timeout)
            if retval.cr_exit_status != 0:
                logging.error("failed to install ZFS RPMs on host "
                              "[%s], ret = %d, stdout = [%s], stderr = [%s]",
                              self.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        logging.info("installing RPMs on host [%s]", self.sh_hostname)
        for rpm_type in LUSTRE_RPM_TYPES:
            if rpm_type not in lustre_rpms.lr_rpm_names:
                continue
            install_timeout = ssh_host.LONGEST_SIMPLE_COMMAND_TIME * 2
            retval = self.sh_run("rpm -ivh --force %s/%s" %
                                 (host_lustre_rpm_dir,
                                  lustre_rpms.lr_rpm_names[rpm_type]),
                                 timeout=install_timeout)
            if retval.cr_exit_status != 0:
                if (failure_caused_by_ksym(retval) or
                        (lustre_rpms.lr_lustre_version.lv_name == LUSTRE_VERSION_NAME_ES3 and
                         ES3_HAS_DEPENDENCY_PROBLEM)):
                    retval = self.sh_run("rpm -ivh --force --nodeps %s/%s" %
                                         (host_lustre_rpm_dir,
                                          lustre_rpms.lr_rpm_names[rpm_type]),
                                         timeout=install_timeout)
                    if retval.cr_exit_status == 0:
                        continue

                retval = self.sh_run("yum localinstall -y --nogpgcheck %s/%s" %
                                     (host_lustre_rpm_dir,
                                      lustre_rpms.lr_rpm_names[rpm_type]),
                                     timeout=install_timeout)
                if retval.cr_exit_status != 0:
                    logging.error("failed to install [%s] RPM on host [%s], "
                                  "ret = %d, stdout = [%s], stderr = [%s]",
                                  rpm_type, self.sh_hostname,
                                  retval.cr_exit_status, retval.cr_stdout,
                                  retval.cr_stderr)
                    return -1

        logging.info("installed RPMs under [%s] on host [%s]",
                     host_lustre_rpm_dir, self.sh_hostname)

        return 0

    def lsh_lustre_reinstall(self, workspace, lustre_rpms, e2fsprogs_rpm_dir):
        """
        Reinstall Lustre RPMs
        """
        logging.info("reinstalling Lustre RPMs on host [%s]", self.sh_hostname)

        ret = self.lsh_lustre_uninstall()
        if ret:
            logging.error("failed to uninstall Lustre RPMs on host [%s]",
                          self.sh_hostname)
            return -1

        ret = self.lsh_lustre_install(workspace, lustre_rpms, e2fsprogs_rpm_dir)
        if ret != 0:
            logging.error("failed to install RPMs on host [%s]",
                          self.sh_hostname)
            return -1

        logging.info("reinstalled Lustre RPMs on host [%s]", self.sh_hostname)
        return 0

    def sh_can_skip_install(self, lustre_rpms):
        """
        Check whether the install of Lustre RPMs could be skipped
        """
        for rpm_type in LUSTRE_RPM_TYPES:
            if rpm_type not in lustre_rpms.lr_rpm_names:
                continue
            if (rpm_type in LUSTRE_ZFS_RPM_TYPES and
                    (not lustre_rpms.lr_zfs_support)):
                continue
            rpm_name = lustre_rpms.lr_rpm_names[rpm_type]
            logging.debug("checking whether RPM [%s] is installed on "
                          "host [%s]", rpm_name, self.sh_hostname)
            name, ext = os.path.splitext(rpm_name)
            if ext != ".rpm":
                logging.debug("RPM [%s] does not have .rpm subfix,"
                              "go on anyway", rpm_name)
            retval = self.sh_run("rpm -qi %s" % name)
            if retval.cr_exit_status != 0:
                logging.info("RPM [%s] is not installed on host [%s], "
                             "will not skip install",
                             rpm_name, self.sh_hostname)
                return False
        return True

    def lsh_lustre_check_clean(self, kernel_version):
        """
        Check whether the host is clean for running Lustre
        """
        logging.info("checking for Lustre on host [%s]", self.sh_hostname)
        # Check whether kernel is installed kernel
        if not self.sh_is_up():
            logging.error("host [%s] is not up", self.sh_hostname)
            return -1

        if kernel_version != self.sh_get_kernel_ver():
            logging.error("host [%s] has a wrong kernel version, expected "
                          "[%s], got [%s]", self.sh_hostname, kernel_version,
                          self.sh_get_kernel_ver())
            return -1

        # Run some fundamental command to check Lustre is installed correctly
        check_commands = ["lustre_rmmod", "modprobe lustre"]
        for command in check_commands:
            retval = self.sh_run(command)
            if retval.cr_exit_status != 0:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1
        logging.info("host [%s] is clean to run Lustre",
                     self.sh_hostname)
        return 0

    def lsh_lustre_prepare(self, workspace, lustre_rpms, e2fsprogs_rpm_dir,
                           lazy_prepare=False):
        """
        Prepare the host for running Lustre
        """
        logging.info("starting preparing host [%s] for Lustre", self.sh_hostname)
        if lazy_prepare and self.sh_can_skip_install(lustre_rpms):
            logging.info("skipping installation of Lustre RPMs on host [%s]",
                         self.sh_hostname)
        else:
            ret = self.lsh_lustre_reinstall(workspace, lustre_rpms,
                                            e2fsprogs_rpm_dir)
            if ret:
                logging.error("failed to reinstall Lustre RPMs on host [%s]",
                              self.sh_hostname)
                return -1

        need_reboot = False
        ret = self.lsh_lustre_umount_services()
        if ret:
            logging.info("failed to umount Lustre clients, reboot is needed")
            need_reboot = True

        if lazy_prepare and not need_reboot:
            ret = self.lsh_lustre_check_clean(lustre_rpms.lr_kernel_version)
            if ret:
                logging.debug("host [%s] need a reboot to change the kernel "
                              "or cleanup the status of Lustre",
                              self.sh_hostname)
                need_reboot = True

        if need_reboot:
            ret = self.sh_kernel_set_default(lustre_rpms.lr_kernel_version)
            if ret:
                logging.error("failed to set default kernel of host [%s] to [%s]",
                              self.sh_hostname, lustre_rpms.lr_kernel_version)
                return -1

            ret = self.sh_reboot()
            if ret:
                logging.error("failed to reboot host [%s]", self.sh_hostname)
                return -1

            ret = self.lsh_lustre_check_clean(lustre_rpms.lr_kernel_version)
            if ret:
                logging.error("failed to check Lustre status after reboot on host [%s]",
                              self.sh_hostname)
                return -1

        logging.info("prepared host [%s] for Lustre", self.sh_hostname)
        return 0
