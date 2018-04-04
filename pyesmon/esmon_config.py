# Copyright (c) 2018 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Console that manages the scheduler
"""
# pylint: disable=too-many-lines
import readline
import logging
import traceback
import sys
import os
import shutil
import yaml

from pyesmon import esmon_install_nodeps
from pyesmon import utils
from pyesmon import time_util
from pyesmon import esmon_common
from pyesmon import lustre


ESMON_CONFIG_LOG_DIR = "/var/log/esmon_config"
CONFIG_FPATH = None
ESMON_SAVED_CONFIG_STRING = None

ESMON_CONFIG_COMMNAD_ADD = "a"
ESMON_CONFIG_COMMNAD_CD = "cd"
ESMON_CONFIG_COMMNAD_EDIT = "e"
ESMON_CONFIG_COMMNAD_HELP = "h"
ESMON_CONFIG_COMMNAD_LS = "ls"
ESMON_CONFIG_COMMNAD_MANUAL = "m"
ESMON_CONFIG_COMMNAD_QUIT = "q"
ESMON_CONFIG_COMMNAD_REMOVE = "rm"
ESMON_CONFIG_COMMNAD_WRITE = "w"


class EsmonConfigCommand(object):
    """
    Config command
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, command, function, arguments=None, need_child=False):
        self.ecc_command = command
        self.ecc_function = function
        self.ecc_need_child = need_child
        self.ecc_arguments = arguments

ESMON_CONFIG_COMMNADS = {}


def esmon_command_add(arg_string):
    """
    Add an intem to the current list
    """
    # pylint: disable=unused-argument
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config
    current_key = current.ewe_key

    if not isinstance(current_config, list):
        console_error('an item can only be added to a list, not to "%s" with '
                      'type "%s"' %
                      (current_key, type(current_config).__name__))
        return -1

    if current_key not in ESMON_INSTALL_CSTRS:
        console_error('illegal configuration: option "%s" is not supported' %
                      (current_key))
        return -1
    current_cstring = ESMON_INSTALL_CSTRS[current_key]
    if current_cstring.ecs_type != ESMON_CONFIG_CSTR_LIST:
        console_error('illegal configuration: option "%s" should not be a '
                      'list' % (current_key))
        return -1

    current_cstring.ecs_item_add(current_config)
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_ADD] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_ADD, esmon_command_add)


def esmon_command_cd(arg_string):
    """
    Print the config in the current directory
    """
    # pylint: disable=global-statement
    ret = 0
    global ESMON_CONFIG_WALK_STACK
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config

    if arg_string == "":
        ESMON_CONFIG_WALK_STACK = [ESMON_CONFIG_ROOT]
        return 0

    args = arg_string.split()
    arg = args[0]

    if arg == "..":
        if length == 1:
            return 0
        else:
            ESMON_CONFIG_WALK_STACK.pop()
    elif (isinstance(current_config, dict) and
          (arg in current_config)):
        child_config = current_config[arg]
        child = EsmonWalkEntry(arg, child_config)
        ESMON_CONFIG_WALK_STACK.append(child)
    elif isinstance(current_config, list):
        ret = esmon_list_cd(current, arg)
    elif str(current_config) == arg:
        console_error('"%s" is not a directory' % arg)
        ret = -1
    else:
        console_error('"%s" is not found' % arg)
        ret = -1
    return ret

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_CD] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_CD, esmon_command_cd,
                       need_child=True)


def esmon_command_edit(arg_string):
    """
    Print the config in the current directory
    """
    # pylint: disable=unused-argument
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config

    if (isinstance(current_config, dict) or
            isinstance(current_config, list)):
        console_error('cannot edit "%s" directly, please edit its children '
                      'instead' %
                      current.ewe_key)
        return -1
    else:
        return esmon_edit(current)
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_EDIT] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_EDIT, esmon_command_edit)


def esmon_command_help(arg_string):
    # pylint: disable=unused-argument
    """
    Print the help string
    """
    print """Command action:
   a         add a new item to current list
   cd $dir   change the current directory to $dir
   e         edit the current configuration
   h         print this menu
   ls [-r]   list config content under current directory
   m         print the manual of this option
   q [-f]    quit without saving changes
   rm        remove the current item from parent
   w         write config file to disk"""

    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_HELP] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_HELP, esmon_command_help)


def esmon_command_ls(arg_string):
    """
    Print the config in the current directory
    """
    # pylint: disable=unused-argument
    ret = 0
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config

    if arg_string == "":
        if isinstance(current_config, dict):
            for key in sorted(current_config):
                value = current_config[key]
                value_type = type(value)
                if value_type is dict:
                    print "%s: {...}" % key
                elif value_type is list:
                    print "%s: [...]" % key
                else:
                    print '%s: %s' % (key, value)
        elif isinstance(current_config, list):
            ret = esmon_list_ls(current)
        else:
            print current_config
    elif arg_string == "-r":
        if isinstance(current_config, int) or isinstance(current_config, str):
            print current_config
        else:
            print yaml.dump(current_config, Dumper=EsmonYamlDumper,
                            default_flow_style=False)
    else:
        console_error('unknown argument "%s" of command "%s"' %
                      (arg_string, ESMON_CONFIG_COMMNAD_LS))
    return ret

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_LS] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_LS, esmon_command_ls)


def esmon_command_manual(arg_string):
    # pylint: disable=unused-argument
    """
    Print the help string of current option
    """
    # pylint: disable=unused-argument
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]

    if length == 1:
        # ROOT
        return esmon_command_help("")

    parent = ESMON_CONFIG_WALK_STACK[-2]
    parent_config = parent.ewe_config
    parent_key = parent.ewe_key

    if isinstance(parent_config, list):
        if parent_key not in ESMON_INSTALL_CSTRS:
            console_error('illegal configuration: option "%s" is not supported' %
                          (parent_key))
            return -1
        parent_cstring = ESMON_INSTALL_CSTRS[parent_key]
        print parent_cstring.ecs_item_helpinfo
        return 0

    key = current.ewe_key
    if key not in ESMON_INSTALL_CSTRS:
        console_error('illegal configuration: option "%s" is not supported' %
                      (key))
        return -1

    cstring = ESMON_INSTALL_CSTRS[key]

    print cstring.ecs_help_info
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_MANUAL] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_MANUAL, esmon_command_manual)


def esmon_command_quit(arg_string):
    """
    Quit this program
    """
    # pylint: disable=unused-argument,global-statement
    global ESMON_CONFIG_RUNNING

    config_string = esmon_config_string()
    if arg_string != "-f" and ESMON_SAVED_CONFIG_STRING != config_string:
        console_error("no write since last change (add -f to override)")
        return -1
    ESMON_CONFIG_RUNNING = False
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_QUIT] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_QUIT, esmon_command_quit, arguments=["-f"])


def esmon_command_remove(arg_string):
    """
    remove one or more children
    """
    # pylint: disable=global-statement
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config
    current_key = current.ewe_key

    if arg_string == "":
        console_error('missing operand for "rm" command')
        return -1

    args = arg_string.split()

    if not isinstance(current_config, list):
        console_error('cannot remove any child of current directory "%s", '
                      'because it has "%s" type, not list' %
                      (current_key, type(current_config).__name__))
        return -1

    current_cstring = ESMON_INSTALL_CSTRS[current_key]
    if current_cstring.ecs_type != ESMON_CONFIG_CSTR_LIST:
        console_error('illegal configuration: option "%s" should not be a '
                      'list' % (current_key))
        return -1

    for arg in args:
        child_index = None
        i = 0
        for child in current_config:
            if child[current_cstring.ecs_item_key] == arg:
                child_index = i
                break
            i += 1

        if child_index is None:
            console_error('cannot remove "%s", no such child in current '
                          'directory' % (arg))
            continue
        del current_config[child_index]
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_REMOVE] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_REMOVE, esmon_command_remove, need_child=True)


def esmon_command_write(arg_string):
    """
    Write the config into file
    """
    # pylint: disable=unused-argument,global-statement
    global ESMON_SAVED_CONFIG_STRING
    with open(CONFIG_FPATH, 'w') as yaml_file:
        config_string = esmon_config_string()
        yaml_file.write(config_string)
        ESMON_SAVED_CONFIG_STRING = config_string
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_WRITE] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_WRITE, esmon_command_write)

ESMON_CONFIG_ROOT = None
ESMON_CONFIG_WALK_STACK = []

# Value that can only be True or False
ESMON_CONFIG_CSTR_BOOL = "bool"
# Constant string defined in codes
ESMON_CONFIG_CSTR_CONSTANT = "constant"
# A directory path
ESMON_CONFIG_CSTR_PATH = "path"
ESMON_CONFIG_CSTR_STRING = "str"
# Integer
ESMON_CONFIG_CSTR_INT = "int"
# List
ESMON_CONFIG_CSTR_LIST = "list"
# Dictionary
ESMON_CONFIG_CSTR_DICT = "dict"


class EsmonYamlDumper(yaml.Dumper):
    # pylint: disable=too-many-ancestors
    """
    Provide proper indent
    """
    def increase_indent(self, flow=False, indentless=False):
        return super(EsmonYamlDumper, self).increase_indent(flow, False)


class EsmonConfigString(object):
    """
    Config string
    """
    # pylint: disable=too-few-public-methods,too-many-arguments
    # pylint: disable=too-many-instance-attributes
    def __init__(self, cstring, ctype, help_info, constants=None,
                 start=0, end=65536, item_helpinfo="", allow_none=False,
                 item_add=None, item_key=None):
        self.ecs_string = cstring
        # ESMON_CONFIG_CSTR_*
        self.ecs_type = ctype
        self.ecs_help_info = help_info

        # Only valid for ESMON_CONFIG_CSTR_CONSTANT
        if ctype == ESMON_CONFIG_CSTR_CONSTANT:
            assert constants is not None
        self.ecs_constants = constants

        # Only valid for ESMON_CONFIG_CSTR_PATH
        self.ecs_allow_none = allow_none

        # Only valid for ESMON_CONFIG_CSTR_INT
        self.ecs_start = start
        self.ecs_end = end

        # Only valid for ESMON_CONFIG_CSTR_LIST
        self.ecs_item_helpinfo = item_helpinfo
        self.ecs_item_add = item_add
        self.ecs_item_key = item_key
        if ctype == ESMON_CONFIG_CSTR_LIST:
            assert item_add is not None
            assert item_helpinfo != ""
            assert item_key is not None


ESMON_INSTALL_CSTRS = {}

ESMON_INSTALL_CSTRS[esmon_common.CSTR_CONTINUOUS_QUERY_INTERVAL] = \
    EsmonConfigString(esmon_common.CSTR_CONTINUOUS_QUERY_INTERVAL,
                      ESMON_CONFIG_CSTR_INT,
                      """This option determines the interval of continuous queries. ESMON uses
continuous queries of Influxdb to aggregate data. To calculate the interval
seconds of continuous queries, please multiply this number by the value of
the "collect_interval" option. If this number is "1", the interval of
continous queries would be "collect_interval" seconds. Usually, in order to
downsample the data and reduce performance impact, this value should be
larger than "1".""",
                      start=1)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_CONTROLLER0_HOST] = \
    EsmonConfigString(esmon_common.CSTR_CONTROLLER0_HOST,
                      ESMON_CONFIG_CSTR_STRING,
                      """This option is the hostname/IP of the controller 0 of this SFA.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_CONTROLLER1_HOST] = \
    EsmonConfigString(esmon_common.CSTR_CONTROLLER1_HOST,
                      ESMON_CONFIG_CSTR_STRING,
                      """This option is the hostname/IP of the controller 1 of this SFA.""")

ESMON_HOST_ID_NUM = 0


def esmon_agent_item_add(config_list):
    """
    Add item to agent list
    """
    # pylint: disable=global-statement
    global ESMON_HOST_ID_NUM
    while True:
        host_id = "host_" + str(ESMON_HOST_ID_NUM)
        conflict = False
        for agent in config_list:
            if agent[esmon_common.CSTR_HOST_ID] == host_id:
                conflict = True
                break
        if conflict:
            ESMON_HOST_ID_NUM += 1
        else:
            break

    config_list.append({esmon_common.CSTR_HOST_ID: host_id,
                        esmon_common.CSTR_IME: False,
                        esmon_common.CSTR_INFINIBAND: False,
                        esmon_common.CSTR_LUSTRE_MDS: True,
                        esmon_common.CSTR_LUSTRE_OSS: True,
                        esmon_common.CSTR_SFAS: []})

INFO = "This group of options include the information of this ESMON agent"
ESMON_INSTALL_CSTRS[esmon_common.CSTR_AGENTS] = \
    EsmonConfigString(esmon_common.CSTR_AGENTS,
                      ESMON_CONFIG_CSTR_LIST,
                      """This list includes the information of the ESMON agents.""",
                      item_helpinfo=INFO,
                      item_add=esmon_agent_item_add,
                      item_key=esmon_common.CSTR_HOST_ID)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_AGENTS_REINSTALL] = \
    EsmonConfigString(esmon_common.CSTR_AGENTS_REINSTALL,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to reinstall ESMON agents or not.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_COLLECT_INTERVAL] = \
    EsmonConfigString(esmon_common.CSTR_COLLECT_INTERVAL,
                      ESMON_CONFIG_CSTR_INT,
                      """This option determines the interval seconds to collect datapoint.""",
                      start=1)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_DROP_DATABASE] = \
    EsmonConfigString(esmon_common.CSTR_DROP_DATABASE,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to drop existing ESMON database of Influxdb.
Important: This option should ONLY be set to "True" if the data/metadata in
           ESMON database of Influxdb is not needed any more.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_ENABLE_DISK] = \
    EsmonConfigString(esmon_common.CSTR_ENABLE_DISK,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to collect disk metrics from this agent.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_ERASE_INFLUXDB] = \
    EsmonConfigString(esmon_common.CSTR_ERASE_INFLUXDB,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to erase all data and metadata of Influxdb.
Important: This option should ONLY be set to "True" if the data/metadata of
           Influxdb is not needed any more. When Influxdb is totally
           corrupted, please enable this option to erase and fix. And please
           double check the influxdb_path option is properly configured before
           enabling this option.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_EXP_MDT] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_EXP_MDT,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether ESMON agents collect exp_md_stats_* metrics
from Lustre OST. If there are too many Lustre clients on the system, this
option should be disabled to avoid performance issues.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_EXP_OST] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_EXP_OST,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether ESMON agents collect exp_ost_stats_[read|
write] metrics from Lustre OST or not. If there are too many Lustre clients on
the system, this option should be disabled to avoid performance issues.""")

INFO = """This option is the unique name of this controller. This value will be used as
the value of "fqdn" tag for metrics of this SFA. Thus, two SFAs shouldn't have
the same name."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_NAME] = \
    EsmonConfigString(esmon_common.CSTR_NAME,
                      ESMON_CONFIG_CSTR_STRING,
                      INFO)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_HOST_ID] = \
    EsmonConfigString(esmon_common.CSTR_HOST_ID,
                      ESMON_CONFIG_CSTR_STRING,
                      """This option is the ID of the host. The ID of a host is a unique value to
identify the host.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_HOSTNAME] = \
    EsmonConfigString(esmon_common.CSTR_HOSTNAME,
                      ESMON_CONFIG_CSTR_STRING,
                      """This option is the hostname or IP of the host. SSH command will use this
hostname/IP to login into the host""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_IME] = \
    EsmonConfigString(esmon_common.CSTR_IME,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to enable IME metrics collection on this
ESMON agent.""")

INFO = """This option determines whether to enable Infiniband metrics collection on this
ESMON agent."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_INFINIBAND] = \
    EsmonConfigString(esmon_common.CSTR_INFINIBAND,
                      ESMON_CONFIG_CSTR_BOOL,
                      INFO)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_INFLUXDB_PATH] = \
    EsmonConfigString(esmon_common.CSTR_INFLUXDB_PATH,
                      ESMON_CONFIG_CSTR_PATH,
                      """This option is Influxdb directory path on ESMON server node.
Important: Please do not put any other files/directries under this directory of
           ESMON server node, because, with "erase_influxdb" option enabled,
           all of the files/directries under that directory will be removed.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_ISO_PATH] = \
    EsmonConfigString(esmon_common.CSTR_ISO_PATH,
                      ESMON_CONFIG_CSTR_PATH,
                      """This option is the path of ESMON ISO.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_MDS] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_MDS,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to enable Lustre MDS metrics collection on
this ESMON agent.""")

INFO = """This option determines whether to enable Lustre OSS metrics collection on this
ESMON agent."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_OSS] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_OSS,
                      ESMON_CONFIG_CSTR_BOOL,
                      INFO)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_REINSTALL] = \
    EsmonConfigString(esmon_common.CSTR_REINSTALL,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to reinstall the ESMON server.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_DEFAULT_VERSION] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_DEFAULT_VERSION,
                      ESMON_CONFIG_CSTR_CONSTANT,
                      """This option determines the default Lustre version to use, if the Lustre
RPMs installed on the ESMON client is not with the supported version.""",
                      constants=lustre.LUSTER_VERSION_NAMES)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_SERVER] = \
    EsmonConfigString(esmon_common.CSTR_SERVER,
                      ESMON_CONFIG_CSTR_DICT,
                      """This group of options includes the information about the ESMON server.""")

ESMON_SFA_NAME_NUM = 0


def esmon_sfa_item_add(config_list):
    """
    Add item to SFA list
    """
    # pylint: disable=global-statement
    global ESMON_SFA_NAME_NUM
    while True:
        name = "sfa_" + ESMON_SFA_NAME_NUM
        conflict = False
        for agent in config_list:
            if agent[esmon_common.CSTR_NAME] == name:
                conflict = True
                break
        if conflict:
            ESMON_SFA_NAME_NUM += 1
        else:
            break

    controller0 = name + "_controller0_host"
    controller1 = name + "_controller1_host"
    config_list.append({esmon_common.CSTR_NAME: name,
                        esmon_common.CSTR_CONTROLLER0_HOST: controller0,
                        esmon_common.CSTR_CONTROLLER1_HOST: controller1})

INFO = "This group of options include the information of this SFA on the ESMON agent"
ESMON_INSTALL_CSTRS[esmon_common.CSTR_SFAS] = \
    EsmonConfigString(esmon_common.CSTR_SFAS,
                      ESMON_CONFIG_CSTR_LIST,
                      """This list includes the information of SFAs on this ESMON agent.""",
                      item_helpinfo=INFO,
                      item_add=esmon_sfa_item_add,
                      item_key=esmon_common.CSTR_NAME)


def esmon_ssh_host_item_add(config_list):
    """
    Add item into ssh_hosts
    """
    # pylint: disable=global-statement
    global ESMON_HOST_ID_NUM
    while True:
        host_id = "host_" + str(ESMON_HOST_ID_NUM)
        conflict = False
        for host in config_list:
            if host[esmon_common.CSTR_HOST_ID] == host_id:
                conflict = True
                break
        if conflict:
            ESMON_HOST_ID_NUM += 1
        else:
            break

    config_list.append({esmon_common.CSTR_HOST_ID: host_id,
                        esmon_common.CSTR_HOSTNAME: False,
                        esmon_common.CSTR_SSH_IDENTITY_FILE: "None"})


INFO = """This is the information about how to login into this host using SSH connection."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_SSH_HOSTS] = \
    EsmonConfigString(esmon_common.CSTR_SSH_HOSTS,
                      ESMON_CONFIG_CSTR_LIST,
                      """This list includes the informations about how to login into the hosts using
SSH connections.""",
                      item_helpinfo=INFO,
                      item_add=esmon_ssh_host_item_add,
                      item_key=esmon_common.CSTR_HOST_ID)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_SSH_IDENTITY_FILE] = \
    EsmonConfigString(esmon_common.CSTR_SSH_IDENTITY_FILE,
                      ESMON_CONFIG_CSTR_PATH,
                      """This option is the SSH key file used when using SSH command to login into
the host. If the default SSH identity file works, this option can be set to\n\"""" +
                      esmon_common.ESMON_CONFIG_CSTR_NONE + '".',
                      allow_none=True)

ESMON_TEST_CSTRS = ESMON_INSTALL_CSTRS.copy()

ESMON_TEST_CSTRS[esmon_common.CSTR_BACKFS_TYPE] = \
    EsmonConfigString(esmon_common.CSTR_BACKFS_TYPE,
                      ESMON_CONFIG_CSTR_CONSTANT,
                      """This option determines which backend file system to use for Lustre.""",
                      constants=lustre.LUSTRE_BACKEND_FILESYSTEMS)

ESMON_TEST_CSTRS[esmon_common.CSTR_SKIP_INSTALL_TEST] = \
    EsmonConfigString(esmon_common.CSTR_SKIP_INSTALL_TEST,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to skip ESMON install test or not. When
this option is enabled, it is assumed that the ESMON has already been
installed on the current system. If ESMON has not been installed properly, the
following tests might fail.""")

ESMON_CONFIG_CANDIDATES = []
ESMON_CONFIG_RUNNING = True


class EsmonWalkEntry(object):
    """
    When walking to the subdir, an entry will be allocated
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, key, current_config):
        # The key used to walk to the subdir. For an item of dict, this is the
        # key of the dict. For a host config, this is usually the host_id. For
        # a sfa config, this is the name value
        self.ewe_key = key
        # The current config walked to
        self.ewe_config = current_config


def console_error(message):
    """
    Print error to console
    """
    print "error: %s" % message


def command_needs_child(command):
    """
    If command needs an argument of subdir, return Ture
    """
    if command == ESMON_CONFIG_COMMNAD_CD:
        return True
    return False


def esmon_list_children(current):
    """
    Return a list of the children
    current: the current walk entry
    """
    children = []
    current_config = current.ewe_config
    id_key = esmon_list_item_key(current)
    if id_key is None:
        return None

    for child_config in current_config:
        if id_key not in child_config:
            console_error('illegal configuration: no option "%s" found in '
                          'following config:\n %s' %
                          (id_key,
                           yaml.dump(current_config, Dumper=EsmonYamlDumper,
                                     default_flow_style=False)))
            return None

        children.append(child_config[id_key])
    return children


def esmon_children():
    """
    Return the names/IDs of children
    """
    # pylint: disable=global-statement,unused-variable
    children = []
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config

    if isinstance(current_config, dict):
        children = []
        for key, value in current_config.iteritems():
            children.append(key)
    elif isinstance(current_config, list):
        children = esmon_list_children(current)
    else:
        children = []

    return children


def esmon_completer(text, state):
    # pylint: disable=global-statement,too-many-branches,unused-argument
    # pylint: disable=too-many-nested-blocks
    """
    The complete function of the input completer
    """
    global ESMON_CONFIG_CANDIDATES
    response = None
    if state == 0:
        # This is the first time for this text,
        # so build a match list.
        origline = readline.get_line_buffer()
        begin = readline.get_begidx()
        end = readline.get_endidx()
        being_completed = origline[begin:end]
        words = origline.split()
        if not words:
            ESMON_CONFIG_CANDIDATES = sorted(ESMON_CONFIG_COMMNADS.keys())
        else:
            try:
                if begin == 0:
                    # first word
                    candidates = ESMON_CONFIG_COMMNADS.keys()
                else:
                    # later word
                    first = words[0]
                    config_command = ESMON_CONFIG_COMMNADS[first]
                    if config_command.ecc_arguments is not None:
                        candidates = list(config_command.ecc_arguments)
                    else:
                        candidates = []
                    if config_command.ecc_need_child:
                        subdirs = esmon_children()
                        if subdirs is not None:
                            candidates += subdirs

                if being_completed:
                    # match options with portion of input
                    # being completed
                    ESMON_CONFIG_CANDIDATES = []
                    for candidate in candidates:
                        if not candidate.startswith(being_completed):
                            continue
                        ESMON_CONFIG_CANDIDATES.append(candidate)
                else:
                    # matching empty string so use all candidates
                    ESMON_CONFIG_CANDIDATES = candidates
            except (KeyError, IndexError):
                ESMON_CONFIG_CANDIDATES = []
    try:
        response = ESMON_CONFIG_CANDIDATES[state]
    except IndexError:
        response = None
    return response


def esmon_input_init():
    """
    Initialize the input completer
    """
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set editing-mode vi")
    readline.set_completer(esmon_completer)


def esmon_input_fini():
    """
    Stop the input completer
    """
    readline.set_completer(None)


def esmon_pwd():
    """
    Print the config in the current directory
    """
    # pylint: disable=unused-argument
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0

    if length == 1:
        path = "/"
    else:
        path = ""
        for walk in ESMON_CONFIG_WALK_STACK[1:]:
            path += "/" + walk.ewe_key

    return path


def esmon_list_item_key(current):
    """
    Return the item key of a list
    """
    current_key = current.ewe_key

    if current_key not in ESMON_INSTALL_CSTRS:
        console_error('illegal configuration: option "%s" is not supported' %
                      (current_key))
        return None

    current_cstring = ESMON_INSTALL_CSTRS[current_key]
    if current_cstring.ecs_type != ESMON_CONFIG_CSTR_LIST:
        console_error('illegal configuration: option "%s" should not be a '
                      'list' % (current_key))
        return None

    return current_cstring.ecs_item_key


def esmon_list_ls(current):
    """
    Print a list of the config
    current: the current walk entry
    """
    current_config = current.ewe_config
    item_key = esmon_list_item_key(current)
    if item_key is None:
        return -1

    id_values = []
    for child_config in current_config:
        if item_key not in child_config:
            console_error('illegal configuration: no option "%s" found in '
                          'following config:\n %s' %
                          (item_key,
                           yaml.dump(child_config, Dumper=EsmonYamlDumper,
                                     default_flow_style=False)))
            return -1

        id_value = child_config[item_key]
        id_values.append(id_value)

    for id_value in sorted(id_values):
        print "%s: {%s: %s, ...}" % (id_value, item_key, id_value)
    return 0


def esmon_list_cd(current, arg):
    """
    Change to a subdir of current path
    """
    current_config = current.ewe_config
    matched_child_config = None
    id_key = esmon_list_item_key(current)
    if id_key is None:
        return -1

    for child_config in current_config:
        if id_key not in child_config:
            console_error('illegal configuration: no option "%s" found in '
                          'following config:\n%s' %
                          (id_key,
                           yaml.dump(current_config, Dumper=EsmonYamlDumper,
                                     default_flow_style=False)))
            return -1

        id_value = child_config[id_key]
        if arg == id_value:
            if matched_child_config is not None:
                console_error('illegal configuration: multiple children with '
                              'value "%s" for key "%s" in following config:\n %s' %
                              (id_value, id_key,
                               yaml.dump(current_config, Dumper=EsmonYamlDumper,
                                         default_flow_style=False)))
                return -1
            matched_child_config = child_config

    if matched_child_config is None:
        console_error('no child found with value "%s" for key "%s"' %
                      (arg, id_key))
        return -1

    child = EsmonWalkEntry(arg, matched_child_config)
    ESMON_CONFIG_WALK_STACK.append(child)

    return 0


def esmon_edit(current):
    """
    Edit a value
    """
    key = current.ewe_key
    current_config = current.ewe_config
    if isinstance(current_config, bool):
        cstring_types = [ESMON_CONFIG_CSTR_BOOL]
    elif isinstance(current_config, str):
        cstring_types = [ESMON_CONFIG_CSTR_CONSTANT,
                         ESMON_CONFIG_CSTR_PATH,
                         ESMON_CONFIG_CSTR_STRING]
    elif isinstance(current_config, int):
        cstring_types = [ESMON_CONFIG_CSTR_INT]
    else:
        console_error('unsupported type of config value "%s"' %
                      (current_config))
        return -1
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0

    if length <= 1:
        console_error('illegal configuration: option with boolen type "%s"'
                      'should NOT be the ROOT' % (key))
        return -1

    parent = ESMON_CONFIG_WALK_STACK[-2]
    parent_config = parent.ewe_config

    if key not in ESMON_INSTALL_CSTRS:
        console_error('illegal configuration: option "%s" is not supported' %
                      (key))
        return -1

    cstring = ESMON_INSTALL_CSTRS[key]
    if cstring.ecs_type not in cstring_types:
        console_error('illegal configuration: the type of option "%s" is not '
                      '"%s", it might be "%s"' %
                      (key, cstring.ecs_type, cstring_types))
        return -1

    print cstring.ecs_help_info, "\n"
    print 'Current value: "%s"' % current_config

    value = esmon_edit_loop(current_config, cstring)
    parent_config[key] = value
    current.ewe_config = value
    return 0


def esmon_edit_loop(default, cstring):
    """
    Loop until allowed string is inputed
    """
    # pylint: disable=too-many-branches,redefined-variable-type,bare-except
    # pylint: disable=too-many-statements
    value = default

    if cstring.ecs_type == ESMON_CONFIG_CSTR_BOOL:
        prompt = 'To set it to True/False, press t/f: '
    elif cstring.ecs_type == ESMON_CONFIG_CSTR_CONSTANT:
        if len(cstring.ecs_constants) == 1:
            prompt = 'The supported value is: '
        else:
            prompt = 'The supported values are: '
        value_string = ""
        for supported_value in cstring.ecs_constants:
            if value_string != "":
                value_string += ", "
            value_string += '"%s"' % supported_value
        prompt += value_string + ".\n"
        prompt += 'Please select one of the supported values: '
    elif cstring.ecs_type == ESMON_CONFIG_CSTR_PATH:
        prompt = 'Please input the new path: '
    elif cstring.ecs_type == ESMON_CONFIG_CSTR_STRING:
        prompt = 'Please input the new value (a string): '
    elif cstring.ecs_type == ESMON_CONFIG_CSTR_INT:
        prompt = ('Please input the new integer of [%s-%s]: ' %
                  (cstring.ecs_start, cstring.ecs_end))
    else:
        console_error('unknown type "%s"' % cstring.ecs_type)

    value = None
    while ESMON_CONFIG_RUNNING:
        cmd_line = raw_input(prompt)
        cmd_line = cmd_line.strip()
        if len(cmd_line) == 0:
            continue

        if cstring.ecs_type == ESMON_CONFIG_CSTR_BOOL:
            if cmd_line == 'T' or cmd_line == 't':
                value = True
            elif cmd_line == 'F' or cmd_line == 'f':
                value = False
            else:
                console_error('"%s" is neither "t" nor "f"' % cmd_line)
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_CONSTANT:
            for supported_value in cstring.ecs_constants:
                if cmd_line == supported_value:
                    value = cmd_line
                    break
            if value is None:
                console_error('"%s" is not supported value' % cmd_line)
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_PATH:
            if len(cmd_line) <= 1:
                console_error('path "%s" is too short' % cmd_line)
            elif cstring.ecs_allow_none and cmd_line == esmon_common.ESMON_CONFIG_CSTR_NONE:
                value = esmon_common.ESMON_CONFIG_CSTR_NONE
            elif cmd_line[0] != '/':
                console_error('"%s" is not absolute path' % cmd_line)
            else:
                value = cmd_line
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_STRING:
            value = cmd_line
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_INT:
            try:
                value = int(cmd_line)
                if value < cstring.ecs_start or value > cstring.ecs_end:
                    console_error('"%s" is out of range [%s-%s]' %
                                  (value, cstring.ecs_start, cstring.ecs_end))
                    value = None
            except:
                console_error('"%s" is not an integer' % cmd_line)
        else:
            console_error('unknown type "%s"' % cstring.ecs_type)

        if value is not None:
            break

    if value == default:
        print 'Keep it as "%s"' % value
    else:
        print 'Changed it to "%s"' % value
    return value


def esmon_config_string():
    """
    Return the current configuration string
    """
    root = ESMON_CONFIG_WALK_STACK[0]
    root_config = root.ewe_config
    config_string = """#
# Configuration file of ESPerfMon from DDN
#
# This file is automatically generated by esmon_config command. To update this
# file, please run esmon_config command.
#
# Configuration Guide:
#
"""
    for config_name in sorted(ESMON_INSTALL_CSTRS):
        config = ESMON_INSTALL_CSTRS[config_name]
        config_string += "# " + config_name + ":\n# "
        config_string += config.ecs_help_info.replace("\n", "\n# ")
        config_string += "\n#\n"
    config_string += yaml.dump(root_config, Dumper=EsmonYamlDumper,
                               default_flow_style=False)
    return config_string


def esmon_command(cmd_line):
    """
    Run a command in the console
    """
    # pylint: disable=broad-except
    if ' ' in cmd_line:
        command, arg_string = cmd_line.split(' ', 1)
    else:
        command = cmd_line
        arg_string = ""

    arg_string = arg_string.strip()

    if command not in ESMON_CONFIG_COMMNADS:
        console_error('command "%s" is not found' % command)
        return -1

    config_command = ESMON_CONFIG_COMMNADS[command]

    ret = -1
    try:
        ret = config_command.ecc_function(arg_string)
    except Exception, err:
        console_error('failed to run command "%s", exception: %s, %s' %
                      (cmd_line, err, traceback.format_exc()))
        return -1

    return ret


def esmon_input_loop():
    """
    Loop and excute the command
    """
    while ESMON_CONFIG_RUNNING:
        cmd_line = raw_input('[%s]$ (h for help): ' % esmon_pwd())
        cmd_line = cmd_line.strip()
        if len(cmd_line) == 0:
            continue
        esmon_command(cmd_line)


def esmon_config(workspace):
    """
    Start to config the file
    """
    # pylint: disable=too-many-branches,bare-except,too-many-locals
    # pylint: disable=global-statement
    global ESMON_CONFIG_ROOT, ESMON_CONFIG_WALK_STACK, ESMON_SAVED_CONFIG_STRING
    save_fpath = workspace + "/" + esmon_common.ESMON_INSTALL_CONFIG_FNAME
    logging.debug("copying config file from [%s] to [%s]", CONFIG_FPATH,
                  save_fpath)
    shutil.copyfile(CONFIG_FPATH, save_fpath)

    config_fd = open(CONFIG_FPATH)
    ret = 0
    try:
        config = yaml.load(config_fd)
    except:
        logging.error("not able to load [%s] as yaml file: %s", CONFIG_FPATH,
                      traceback.format_exc())
        ret = -1
    config_fd.seek(0)
    ESMON_SAVED_CONFIG_STRING = config_fd.read()
    config_fd.close()
    if ret:
        return -1

    ESMON_CONFIG_ROOT = EsmonWalkEntry("/", config)
    ESMON_CONFIG_WALK_STACK = [ESMON_CONFIG_ROOT]

    esmon_input_init()
    esmon_input_loop()
    esmon_input_fini()
    return 0


def usage():
    """
    Print usage string
    """
    utils.eprint("Usage: %s <config_file>" %
                 sys.argv[0])


def main():
    """
    Config ESMON
    """
    # pylint: disable=global-statement
    global CONFIG_FPATH
    reload(sys)
    sys.setdefaultencoding("utf-8")
    CONFIG_FPATH = esmon_install_nodeps.ESMON_INSTALL_CONFIG

    if len(sys.argv) == 2:
        CONFIG_FPATH = sys.argv[1]
    elif len(sys.argv) > 2:
        usage()
        sys.exit(-1)

    identity = time_util.local_strftime(time_util.utcnow(), "%Y-%m-%d-%H_%M_%S")
    workspace = ESMON_CONFIG_LOG_DIR + "/" + identity

    if not os.path.exists(ESMON_CONFIG_LOG_DIR):
        os.mkdir(ESMON_CONFIG_LOG_DIR)
    elif not os.path.isdir(ESMON_CONFIG_LOG_DIR):
        logging.error("[%s] is not a directory", ESMON_CONFIG_LOG_DIR)
        sys.exit(-1)

    if not os.path.exists(workspace):
        os.mkdir(workspace)
    elif not os.path.isdir(workspace):
        logging.error("[%s] is not a directory", workspace)
        sys.exit(-1)

    utils.configure_logging(workspace)

    ret = esmon_config(workspace)
    if ret:
        logging.error("config failed, please check [%s] for more log",
                      workspace)
        sys.exit(ret)
    logging.info("Please check [%s] for the ESMON configuration "
                 "and [%s] for more log",
                 CONFIG_FPATH, workspace)
    sys.exit(0)
