# pylint: disable=too-many-lines
"""

Install python RPMs for esmon_install to work properly first
"""
# Local libs
import logging
import re
import sys
from pyesmon import ssh_host
from pyesmon import esmon_install_common
from pyesmon import utils
from pyesmon import esmon_common


def iso_path_in_config(local_host):
    """
    Return the ISO path in the config file
    """
    local_host = ssh_host.SSHHost("localhost", local=True)
    command = (r"grep -v ^\# /etc/esmon_install.conf | "
               "grep ^iso_path: | awk '{print $2}'")

    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on localhost, "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return None

    lines = retval.cr_stdout.splitlines()
    if len(lines) != 1:
        logging.error("unexpected iso path in config file: %s", lines)
        return None
    return lines[0]


class EsmonInstallServer(object):
    """
    ESMON server host has an object of this type
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self, host, iso_dir):
        self.eis_host = host
        self.eis_iso_dir = iso_dir
        self.eis_rpm_dir = (iso_dir + "/" + "RPMS/" +
                            ssh_host.DISTRO_RHEL7)
        self.eis_rpm_dependent_dir = self.eis_rpm_dir + "/dependent"
        self.eis_rpm_dependent_fnames = None

    def eis_rpm_install(self, name):
        """
        Install a RPM in the ISO given the name of the RPM
        """
        if self.eis_rpm_dependent_fnames is None:
            command = "ls %s" % self.eis_rpm_dependent_dir
            retval = self.eis_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              self.eis_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1
            self.eis_rpm_dependent_fnames = retval.cr_stdout.split()

        rpm_dir = self.eis_rpm_dependent_dir
        rpm_pattern = (esmon_common.RPM_PATTERN_RHEL7 % name)
        rpm_regular = re.compile(rpm_pattern)
        matched_fname = None
        for filename in self.eis_rpm_dependent_fnames[:]:
            match = rpm_regular.match(filename)
            if match:
                matched_fname = filename
                logging.debug("matched pattern [%s] with fname [%s]",
                              rpm_pattern, filename)
                break
        if matched_fname is None:
            logging.error("failed to find RPM with pattern [%s] under "
                          "directory [%s] of host [%s]", rpm_pattern,
                          rpm_dir, self.eis_host.sh_hostname)
            return -1

        command = ("cd %s && rpm -ivh %s" %
                   (rpm_dir, matched_fname))
        retval = self.eis_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          self.eis_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        return 0


def dependency_find(local_host):
    """
    Find missing pylibs
    """
    missing_dependencies = []
    for dependent_rpm in esmon_common.ESMON_INSTALL_DEPENDENT_RPMS:
        ret = local_host.sh_rpm_query(dependent_rpm)
        if ret == 0:
            continue
        missing_dependencies.append(dependent_rpm)

    return missing_dependencies


def dependency_do_install(local_host, mnt_path):
    """
    Install the pylibs
    """
    missing_dependencies = dependency_find(local_host)
    esmon_installer = EsmonInstallServer(local_host, mnt_path)
    for i, dependent_rpm in enumerate(missing_dependencies):
        ret = esmon_installer.eis_rpm_install(dependent_rpm)
        if ret:
            logging.error("failed to install rpm [%s] on host [%s] "
                          "still missing RPMS: %s", dependent_rpm,
                          local_host .sh_hostname, missing_dependencies[i:])
            return -1
    return 0


def dependency_install(local_host):
    """
    Install the missing pylib
    """
    iso_path = iso_path_in_config(local_host)
    if iso_path is None:
        iso_path = esmon_install_common.find_iso_path_in_cwd(local_host)
        if iso_path is None:
            logging.error("failed to find ESMON ISO %s under currect "
                          "directory")
            return -1
        logging.info("no [iso_path] is configured, use [%s] under current "
                     "directory", iso_path)

    mnt_path = "/mnt/" + utils.random_word(8)
    command = ("mkdir -p %s && mount -o loop %s %s" %
               (mnt_path, iso_path, mnt_path))
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

    ret = dependency_do_install(local_host, mnt_path)
    if ret:
        logging.error("failed to install dependent libraries on local host")
        return ret

    command = ("umount %s" % (mnt_path))
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      local_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        ret = -1

    command = ("rmdir %s" % (mnt_path))
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      local_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        ret = -1
    return ret


def usage():
    """
    Print usage string
    """
    utils.eprint("Usage: %s [-h|--help]" %
                 sys.argv[0])
    utils.eprint("To install EXASCaler Performance Monitoring System, "
                 "please run command \"%s\"." % (sys.argv[0]))
    utils.eprint("To change the configuration, please edit "
                 "file \"%s\"." % (esmon_common.ESMON_INSTALL_CONFIG))


def main():
    """
    Install Exascaler monitoring
    """
    # pylint: disable=unused-variable,too-many-branches
    argc = len(sys.argv)
    if argc == 2:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            usage()
            sys.exit(0)
        else:
            utils.eprint("Unkown options \"%s\"" % sys.argv[1])
            usage()
            sys.exit(-1)
    elif argc > 2:
        utils.eprint("too many options")
        usage()
        sys.exit(-1)

    local_host = ssh_host.SSHHost("localhost", local=True)
    missing_dependencies = dependency_find(local_host)
    if len(missing_dependencies):
        ret = dependency_install(local_host)
        if ret:
            sys.exit(-1)
    from pyesmon import esmon_install_nodeps
    esmon_install_nodeps.main()
