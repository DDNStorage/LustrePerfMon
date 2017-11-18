"""

Install python RPMs for esmon_install to work properly first
"""
# Local libs
import os
import logging


def find_iso_path_in_cwd(local_host):
    """
    Find ESMON iso path in current work directory
    """
    command = "ls esmon-*.iso"
    retval = local_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      local_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return None

    current_dir = os.getcwd()
    iso_names = retval.cr_stdout.split()
    if len(iso_names) != 1:
        logging.error("found unexpected ISOs %s under currect directory [%s]",
                      iso_names, current_dir)
        return None

    iso_name = iso_names[0]
    iso_path = current_dir + "/" + iso_name
    return iso_path
