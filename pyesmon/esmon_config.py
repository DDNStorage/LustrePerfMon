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
import copy
import yaml

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
ESMON_CONFIG_COMMNAD_WRITE_QUIT = "wq"
ESMON_CONFIG_EDIT_QUIT = 1


class EsmonConfigInputStatus(object):
    """
    Input status
    """
    # pylint: disable=too-few-public-methods
    STATUS_COMMAND = "command"
    STATUS_CSTR = "cstr"

    def __init__(self):
        self.ecis_status = None
        self.ecis_candidates = []
        self.ecis_cstr_candidates = []

    def ecis_completer(self, text, state):
        # pylint: disable=global-statement,too-many-branches,unused-argument
        # pylint: disable=too-many-nested-blocks
        """
        The complete function of the input completer
        """
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
                if self.ecis_status == self.STATUS_COMMAND:
                    self.ecis_candidates = sorted(ESMON_CONFIG_COMMNADS.keys())
                else:
                    self.ecis_candidates = sorted(self.ecis_cstr_candidates)
            else:
                try:
                    if self.ecis_status == self.STATUS_COMMAND:
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
                    else:
                        candidates = sorted(self.ecis_cstr_candidates)

                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.ecis_candidates = []
                        for candidate in candidates:
                            if not candidate.startswith(being_completed):
                                continue
                            self.ecis_candidates.append(candidate)
                    else:
                        # matching empty string so use all candidates
                        self.ecis_candidates = candidates
                except (KeyError, IndexError):
                    self.ecis_candidates = []
        try:
            response = self.ecis_candidates[state]
        except IndexError:
            response = None
        return response

ESMON_INPUT_STATUS = EsmonConfigInputStatus()


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
    Add an item to the current list
    """
    # pylint: disable=unused-argument,too-many-locals,too-many-statements,too-many-branches
    # pylint: disable=too-many-return-statements
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config
    current_key = current.ewe_key

    if not isinstance(current_config, list):
        logging.error('an item can only be added to a list, not to "%s" with '
                      'type "%s"', current_key, type(current_config).__name__)
        return -1

    if current_key not in ESMON_INSTALL_CSTRS:
        logging.error('illegal configuration: option "%s" is not supported',
                      current_key)
        return -1

    current_cstring = ESMON_INSTALL_CSTRS[current_key]
    if current_cstring.ecs_type != ESMON_CONFIG_CSTR_LIST:
        logging.error('illegal configuration: option "%s" should not be a '
                      'list', current_key)
        return -1

    print ESMON_CONFIG_ADD_MULTIPLE.ecs_help_info
    prompt = "Press F/f to add only single item, press T/t to add multiple ones: "
    ret, add_multiple = esmon_cstr_input_loop(ESMON_CONFIG_ADD_MULTIPLE,
                                              prompt=prompt)
    if ret == ESMON_CONFIG_EDIT_QUIT:
        return 0

    if add_multiple:
        print "Multiple items will be added."
        print ""

        prompt = "Please input the common prefix of the adding items: "
        ret, prefix = esmon_cstr_input_loop(ESMON_CONFIG_ADD_PREFIX,
                                            prompt=prompt)
        if ret == ESMON_CONFIG_EDIT_QUIT:
            return 0

        print 'The newly addded items will have names like "%s..."' % prefix
        print ""

        print """Start index of the item names is needed. The start index will be included in
the added items."""
        start_cstr = EsmonConfigString("start_index",
                                       ESMON_CONFIG_CSTR_INT,
                                       "")
        prompt = ("Please input the start index, an integer in [%s, %s]: " %
                  (start_cstr.ecs_start, start_cstr.ecs_end))

        ret, start_index = esmon_cstr_input_loop(start_cstr,
                                                 prompt=prompt)
        if ret == ESMON_CONFIG_EDIT_QUIT:
            return 0
        print 'The index of the first item will be "%s".' % (start_index)
        print ""

        print """End index of the item names is needed. The end index will be included in
the added items."""
        end_cstr = EsmonConfigString("end_index",
                                     ESMON_CONFIG_CSTR_INT,
                                     "",
                                     start=start_index)
        prompt = ("Please input the end index, an integer in [%s, %s]: " %
                  (end_cstr.ecs_start, end_cstr.ecs_end))
        ret, end_index = esmon_cstr_input_loop(end_cstr,
                                               prompt=prompt)
        if ret == ESMON_CONFIG_EDIT_QUIT:
            return 0
        print ('The index of the last item will be "%s".' %
               (end_index))
        print ""

        names = ""
        names_filled = ""
        name_index = start_index
        digit_number = len(str(end_index))
        fill_format = "%0" + str(digit_number) + "d"
        number = 0
        while name_index <= end_index:
            name = "%s%d" % (prefix, name_index)
            if names != "":
                names += ", "
            names += name
            name_filled = prefix + fill_format % name_index
            if names_filled != "":
                names_filled += ", "
            names_filled += name_filled
            name_index += 1
            number += 1
            if number >= 3:
                break

        # Add the last item into the output string
        if name_index <= end_index:
            if name_index < end_index:
                names += ", ..."
                names_filled += ", ..."
            name = "%s%d" % (prefix, end_index)
            if names != "":
                names += ", "
            names += name
            name_filled = prefix + fill_format % end_index
            if names_filled != "":
                names_filled += ", "
            names_filled += name_filled

        helpinfo = """Do you want to fill the empty spaces of the names with "0"?
If yes, then the names of newly created items will be: """
        helpinfo += '"%s".\n' % (names_filled)
        helpinfo += 'If not, then the names will be "%s".' % (names)
        print helpinfo
        fill_zero_cstr = EsmonConfigString("fill_zero",
                                           ESMON_CONFIG_CSTR_BOOL,
                                           "")
        prompt = "Press T/t to fill empty space with 0, press F/f not to: "
        ret, fill_zero = esmon_cstr_input_loop(fill_zero_cstr,
                                               prompt=prompt)
        if ret == ESMON_CONFIG_EDIT_QUIT:
            return 0
        if fill_zero:
            print 'The names of newly created items will be "%s"' % names_filled
        else:
            print 'The names of newly created items will be "%s"' % names
        print ""

        name_index = start_index
        while name_index <= end_index:
            if fill_zero:
                name = prefix + fill_format % name_index
            else:
                name = "%s%d" % (prefix, name_index)
            name_index += 1
            number += 1

            ret = esmon_item_add(current_config, current_cstring, name)
            if ret == 0:
                print 'Item with name "%s" is added' % name
    else:
        print "Only a single item will be added."
        print ""
        name_cstr = EsmonConfigString("name",
                                      ESMON_CONFIG_CSTR_STRING,
                                      "")
        prompt = "Please input the name of this item: "
        ret, name = esmon_cstr_input_loop(name_cstr,
                                          prompt=prompt)
        if ret == ESMON_CONFIG_EDIT_QUIT:
            return 0
        ret = esmon_item_add(current_config, current_cstring, name)
        if ret:
            return ret
        print 'Item with name "%s" is added' % name

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
        logging.error('"%s" is not a directory', arg)
        ret = -1
    else:
        logging.error('"%s" is not found', arg)
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
        logging.error('cannot edit "%s" directly, please edit its children '
                      'instead', current.ewe_key)
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
   w         write config file to disk
   wq        write config file to disk and quit"""

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
        logging.error('unknown argument "%s" of command "%s"',
                      arg_string, ESMON_CONFIG_COMMNAD_LS)
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
    current_config = current.ewe_config
    cstring = None

    if length > 1:
        parent = ESMON_CONFIG_WALK_STACK[-2]
        parent_config = parent.ewe_config
        parent_key = parent.ewe_key

        if isinstance(parent_config, list):
            # If current option is an item in a list, print the item help information
            # of the parent. Because the config itself is using the index name as its
            # config string.
            if parent_key not in ESMON_INSTALL_CSTRS:
                logging.error('illegal configuration: option "%s" is not '
                              'supported', parent_key)
                return -1
            cstring = ESMON_INSTALL_CSTRS[parent_key]
            print cstring.ecs_item_helpinfo

    if cstring is None:
        key = current.ewe_key
        if key not in ESMON_INSTALL_CSTRS:
            logging.error('illegal configuration: option "%s" is not '
                          'supported', key)
            return -1
        cstring = ESMON_INSTALL_CSTRS[key]
        print cstring.ecs_help_info

    if isinstance(current_config, list):
        print ""
        print """The listed entries of "ls" are the IDs of each item in this list. Please use
"cd" to enter each entry."""
        return 0

    if cstring.ecs_children is not None:
        print "Following are the children of this option:"
        for child in cstring.ecs_children:
            child_cstring = ESMON_INSTALL_CSTRS[child]
            print ""
            print child
            print child_cstring.ecs_help_info
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
        logging.error("no write since last change (add -f to override)")
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
        logging.error('missing operand for "rm" command')
        return -1

    args = arg_string.split()

    if not isinstance(current_config, list):
        logging.error('cannot remove any child of current directory "%s", '
                      'because it has "%s" type, not list',
                      current_key, type(current_config).__name__)
        return -1

    current_cstring = ESMON_INSTALL_CSTRS[current_key]
    if current_cstring.ecs_type != ESMON_CONFIG_CSTR_LIST:
        logging.error('illegal configuration: option "%s" should not be a '
                      'list', current_key)
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
            logging.error('cannot remove "%s", no such child in current '
                          'directory', arg)
            continue
        del current_config[child_index]
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_REMOVE] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_REMOVE, esmon_command_remove, need_child=True)


def esmon_command_write(arg_string):
    """
    Write the config into file
    """
    # pylint: disable=unused-argument,global-statement,bare-except
    global ESMON_SAVED_CONFIG_STRING
    config_string = esmon_config_string()
    try:
        with open(CONFIG_FPATH, 'w') as yaml_file:
            yaml_file.write(config_string)
    except:
        logging.error("""Failed to save the config file. To avoid data lose, please save the
following config manually:""")
        sys.stdout.write(config_string)
    print "Saved the config to the file."
    ESMON_SAVED_CONFIG_STRING = config_string
    return 0

ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_WRITE] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_WRITE, esmon_command_write)


def esmon_command_write_quit(arg_string):
    """
    Write the config into file and quit
    """
    # pylint: disable=unused-argument,global-statement
    ret = esmon_command_write(arg_string)
    if ret:
        return ret

    ret = esmon_command_quit(arg_string)
    return ret


ESMON_CONFIG_COMMNADS[ESMON_CONFIG_COMMNAD_WRITE_QUIT] = \
    EsmonConfigCommand(ESMON_CONFIG_COMMNAD_WRITE_QUIT,
                       esmon_command_write_quit)


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
# Definition
ESMON_CONFIG_CSTR_DEF = "definition"


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
                 item_child_value=None, item_key=None, children=None, default=None,
                 define_entries=None, mapping_dict=None):
        self.ecs_string = cstring
        # ESMON_CONFIG_CSTR_*
        self.ecs_type = ctype
        self.ecs_help_info = help_info

        # Only valid for ESMON_CONFIG_CSTR_[DICT|LIST]
        self.ecs_children = children

        # If it is ID of a list, then it has no default value
        # ESMON_CONFIG_CSTR_LIST always has default value of []
        self.ecs_default = default

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
        self.ecs_item_child_value = item_child_value
        self.ecs_item_helpinfo = item_helpinfo
        self.ecs_item_key = item_key
        if ctype == ESMON_CONFIG_CSTR_LIST:
            assert item_helpinfo != ""
            assert item_key is not None

        if ctype == ESMON_CONFIG_CSTR_DEF:
            assert define_entries is not None
        else:
            assert define_entries is None
        self.ecs_define_entries = define_entries
        self.ecs_mapping_dict = mapping_dict


ESMON_INSTALL_CSTRS = {}

ESMON_INSTALL_ROOT = \
    EsmonConfigString("/",
                      ESMON_CONFIG_CSTR_DICT,
                      """This is the root of the config.""",
                      children=[esmon_common.CSTR_AGENTS,
                                esmon_common.CSTR_AGENTS_REINSTALL,
                                esmon_common.CSTR_COLLECT_INTERVAL,
                                esmon_common.CSTR_CONTINUOUS_QUERY_INTERVAL,
                                esmon_common.CSTR_ISO_PATH,
                                esmon_common.CSTR_LUSTRE_DEFAULT_VERSION,
                                esmon_common.CSTR_LUSTRE_EXP_MDT,
                                esmon_common.CSTR_LUSTRE_EXP_OST,
                                esmon_common.CSTR_SERVER,
                                esmon_common.CSTR_SSH_HOSTS])

ESMON_INSTALL_CSTRS["/"] = ESMON_INSTALL_ROOT

ESMON_INSTALL_CSTRS[esmon_common.CSTR_CONTINUOUS_QUERY_INTERVAL] = \
    EsmonConfigString(esmon_common.CSTR_CONTINUOUS_QUERY_INTERVAL,
                      ESMON_CONFIG_CSTR_INT,
                      """This option determines the interval of continuous queries. ES PERFMON uses
continuous queries of Influxdb to aggregate data. To calculate the interval
seconds of continuous queries, please multiply this number by the value of
the "collect_interval" option. If this number is "1", the interval of
continous queries would be "collect_interval" seconds. Usually, in order to
downsample the data and reduce performance impact, this value should be
larger than "1".""",
                      start=1,
                      default=4)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_CONTROLLER0_HOST] = \
    EsmonConfigString(esmon_common.CSTR_CONTROLLER0_HOST,
                      ESMON_CONFIG_CSTR_STRING,
                      """This option is the hostname/IP of the controller 0 of this SFA.""",
                      default="controller0_host")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_CONTROLLER1_HOST] = \
    EsmonConfigString(esmon_common.CSTR_CONTROLLER1_HOST,
                      ESMON_CONFIG_CSTR_STRING,
                      """This option is the hostname/IP of the controller 1 of this SFA.""",
                      default="controller1_host")

ESMON_HOST_ID_NUM = 0


def esmon_ssh_host_item_child_value(item_id, child_key):
    """
    Return the default value according to the item_id
    """
    if child_key == esmon_common.CSTR_HOSTNAME:
        return 0, item_id
    return -1, None


def esmon_config_check_add_def(id_value, key_cstring):
    """
    Check the config, if the definition is missing, add one
    """
    root = ESMON_CONFIG_WALK_STACK[0]
    root_config = root.ewe_config

    ret = esmon_config_check(root_config, id_value, esmon_pwd(), key_cstring,
                             silent_on_missing=True)
    if ret == ESMON_DEF_MISSING:
        print ('Defintion of "%s" with value "%s" is not found, adding one' %
               (key_cstring.ecs_string, id_value))
        ret = esmon_config_def_add(root_config, key_cstring, id_value)
        if ret == 0:
            print ('Definition of "%s" with value "%s" is added' %
                   (key_cstring.ecs_string, id_value))
        else:
            return -1
    return 0


def esmon_item_add(config_list, list_cstr, id_value, definition=False):
    """
    Add item to agent list
    definition: whether the item is added for definition
    """
    # pylint: disable=global-statement
    for item_config in config_list:
        if item_config[list_cstr.ecs_item_key] == id_value:
            logging.error('cannot add item with id "%s" because it already '
                          'exists', id_value)
            return -1

    item_config = {}
    key_cstring = None
    for child in list_cstr.ecs_children:
        child_cstr = ESMON_INSTALL_CSTRS[child]
        if child == list_cstr.ecs_item_key:
            item_config[child] = id_value
            key_cstring = child_cstr
        else:
            if child_cstr.ecs_default is None:
                if list_cstr.ecs_item_child_value is not None:
                    ret, value = list_cstr.ecs_item_child_value(id_value, child)
                    if ret:
                        logging.error('fix me: can not generate value of "%s" '
                                      'according to id "%s"',
                                      child, id_value)
                        return -1
                    item_config[child] = value
                else:
                    logging.error('fix me: config "%s" doesnot have default '
                                  'value', child_cstr.ecs_string)
                    return -1
            else:
                item_config[child] = copy.copy(child_cstr.ecs_default)

    if key_cstring is None:
        logging.error('fix me: config "%s" doesnot have child "%s"',
                      list_cstr.ecs_string, list_cstr.ecs_item_key)
        return -1

    ret = 0
    if not definition:
        ret = esmon_config_check_add_def(id_value, key_cstring)

    if ret == 0:
        config_list.append(item_config)

    return ret


LOCALHOST_AGENT = {
    esmon_common.CSTR_HOST_ID: "localhost",
}
INFO = "This group of options include the information of this ES PERFMON agent."
ESMON_INSTALL_CSTRS[esmon_common.CSTR_AGENTS] = \
    EsmonConfigString(esmon_common.CSTR_AGENTS,
                      ESMON_CONFIG_CSTR_LIST,
                      """This list includes the information of the ES PERFMON agents.""",
                      item_helpinfo=INFO,
                      item_key=esmon_common.CSTR_HOST_ID,
                      children=[esmon_common.CSTR_ENABLE_DISK,
                                esmon_common.CSTR_HOST_ID,
                                esmon_common.CSTR_IME,
                                esmon_common.CSTR_INFINIBAND,
                                esmon_common.CSTR_LUSTRE_MDS,
                                esmon_common.CSTR_LUSTRE_OSS,
                                esmon_common.CSTR_SFAS],
                      default=[LOCALHOST_AGENT])

ESMON_INSTALL_CSTRS[esmon_common.CSTR_AGENTS_REINSTALL] = \
    EsmonConfigString(esmon_common.CSTR_AGENTS_REINSTALL,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to reinstall ESMON agents or not.""",
                      default=True)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_COLLECT_INTERVAL] = \
    EsmonConfigString(esmon_common.CSTR_COLLECT_INTERVAL,
                      ESMON_CONFIG_CSTR_INT,
                      """This option determines the interval seconds to collect datapoint.""",
                      start=1,
                      default=60)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_DROP_DATABASE] = \
    EsmonConfigString(esmon_common.CSTR_DROP_DATABASE,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to drop existing ES PERFMON database of
Influxdb.
Important: This option should ONLY be set to "True" if the data/metadata in
           ES PERFMON database of Influxdb is not needed any more.""",
                      default=False)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_ENABLE_DISK] = \
    EsmonConfigString(esmon_common.CSTR_ENABLE_DISK,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to collect disk metrics from this agent.""",
                      default=False)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_ERASE_INFLUXDB] = \
    EsmonConfigString(esmon_common.CSTR_ERASE_INFLUXDB,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to erase all data and metadata of Influxdb.
Important: This option should ONLY be set to "True" if the data/metadata of
           Influxdb is not needed any more. When Influxdb is totally
           corrupted, please enable this option to erase and fix. And please
           double check the influxdb_path option is properly configured before
           enabling this option.""",
                      default=False)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_EXP_MDT] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_EXP_MDT,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether ES PERFMON agents collect exp_md_stats_*
metrics from Lustre MDT. If there are too many Lustre clients on the system,
this option should be disabled to avoid performance issues.""",
                      default=False)

INFO = """This option determines whether ES PERFMON agents collect exp_ost_stats_[read|
write] metrics from Lustre OST or not. If there are too many Lustre clients on
the system, this option should be disabled to avoid performance issues."""

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_EXP_OST] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_EXP_OST,
                      ESMON_CONFIG_CSTR_BOOL,
                      INFO,
                      default=False)

INFO = """This option is the unique name of this controller. This value will be used as
the value of "fqdn" tag for metrics of this SFA. Thus, two SFAs shouldn't have
the same name."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_NAME] = \
    EsmonConfigString(esmon_common.CSTR_NAME,
                      ESMON_CONFIG_CSTR_STRING,
                      INFO)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_HOST_ID] = \
    EsmonConfigString(esmon_common.CSTR_HOST_ID,
                      ESMON_CONFIG_CSTR_DEF,
                      """This option is the ID of the host. The ID of a host is a unique value to
identify the host.""",
                      define_entries=[esmon_common.CSTR_SSH_HOSTS])

ESMON_INSTALL_CSTRS[esmon_common.CSTR_HOSTNAME] = \
    EsmonConfigString(esmon_common.CSTR_HOSTNAME,
                      ESMON_CONFIG_CSTR_STRING,
                      """This option is the hostname or IP of the host. "ssh" command will use this
hostname/IP to login into the host. If the host is the ES PERFMON server, this
hostname/IP will be used as the server host in the write_tsdb plugin of
ES PERFMON agent.""")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_IME] = \
    EsmonConfigString(esmon_common.CSTR_IME,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to enable IME metrics collection on this
ES PERFMON agent.""",
                      default=False)

INFO = """This option determines whether to enable Infiniband metrics collection on this
ES PERFMON agent."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_INFINIBAND] = \
    EsmonConfigString(esmon_common.CSTR_INFINIBAND,
                      ESMON_CONFIG_CSTR_BOOL,
                      INFO,
                      default=False)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_INFLUXDB_PATH] = \
    EsmonConfigString(esmon_common.CSTR_INFLUXDB_PATH,
                      ESMON_CONFIG_CSTR_PATH,
                      """This option is Influxdb directory path on ES PERFMON server node.
Important: Please do not put any other files/directries under this directory of
           ES PERFMON server node, because, with "erase_influxdb" option
           enabled, all of the files/directries under that directory will be
           removed.""",
                      default="/esmon/influxdb")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_ISO_PATH] = \
    EsmonConfigString(esmon_common.CSTR_ISO_PATH,
                      ESMON_CONFIG_CSTR_PATH,
                      """This option is the path of ES PERFMON ISO.""",
                      default="/root/esmon.iso")

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LOCAL_HOST] = \
    EsmonConfigString(esmon_common.CSTR_LOCAL_HOST,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether this host is local host.""",
                      default=False)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_MDS] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_MDS,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to enable Lustre MDS metrics collection on
this ES PERFMON agent.""",
                      default=True)

INFO = """This option determines whether to enable Lustre OSS metrics collection on this
ES PERFMON agent."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_OSS] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_OSS,
                      ESMON_CONFIG_CSTR_BOOL,
                      INFO,
                      default=True)

ESMON_INSTALL_CSTRS[esmon_common.CSTR_REINSTALL] = \
    EsmonConfigString(esmon_common.CSTR_REINSTALL,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to reinstall the ES PERFMON server.""",
                      default=True)

MAPPING_DICT = {lustre.LUSTRE_VERSION_NAME_ERROR: None}
ESMON_INSTALL_CSTRS[esmon_common.CSTR_LUSTRE_DEFAULT_VERSION] = \
    EsmonConfigString(esmon_common.CSTR_LUSTRE_DEFAULT_VERSION,
                      ESMON_CONFIG_CSTR_CONSTANT,
                      """This option determines the default Lustre version to use, if the Lustre
RPMs installed on the ES PERFMON agent is not with the supported version.""",
                      constants=lustre.LUSTER_VERSION_NAMES,
                      default="es3",
                      mapping_dict=MAPPING_DICT)

INFO = """This group of options include the information about the ES PERFMON server."""
SERVER_DEFAULT = {
    esmon_common.CSTR_HOST_ID: "localhost"
}
ESMON_INSTALL_CSTRS[esmon_common.CSTR_SERVER] = \
    EsmonConfigString(esmon_common.CSTR_SERVER,
                      ESMON_CONFIG_CSTR_DICT,
                      INFO,
                      children=[esmon_common.CSTR_DROP_DATABASE,
                                esmon_common.CSTR_ERASE_INFLUXDB,
                                esmon_common.CSTR_HOST_ID,
                                esmon_common.CSTR_INFLUXDB_PATH,
                                esmon_common.CSTR_REINSTALL],
                      default=SERVER_DEFAULT)

ESMON_SFA_NAME_NUM = 0


INFO = "This group of options include the information of this SFA on the ES PERFMON agent."
ESMON_INSTALL_CSTRS[esmon_common.CSTR_SFAS] = \
    EsmonConfigString(esmon_common.CSTR_SFAS,
                      ESMON_CONFIG_CSTR_LIST,
                      """This list includes the information of SFAs on this ES PERFMON agent.""",
                      item_helpinfo=INFO,
                      item_key=esmon_common.CSTR_NAME,
                      children=[esmon_common.CSTR_CONTROLLER0_HOST,
                                esmon_common.CSTR_CONTROLLER1_HOST,
                                esmon_common.CSTR_NAME],
                      default=[])

LOCALHOST_SSH_HOST = {
    esmon_common.CSTR_HOST_ID: "localhost",
    esmon_common.CSTR_HOSTNAME: "localhost",
    esmon_common.CSTR_LOCAL_HOST: True,
}

INFO = """This is the information about how to login into this host using SSH connection."""
ESMON_INSTALL_CSTRS[esmon_common.CSTR_SSH_HOSTS] = \
    EsmonConfigString(esmon_common.CSTR_SSH_HOSTS,
                      ESMON_CONFIG_CSTR_LIST,
                      """This list includes the informations about how to login into the hosts using
SSH connections.""",
                      item_helpinfo=INFO,
                      item_key=esmon_common.CSTR_HOST_ID,
                      item_child_value=esmon_ssh_host_item_child_value,
                      children=[esmon_common.CSTR_HOST_ID,
                                esmon_common.CSTR_HOSTNAME,
                                esmon_common.CSTR_SSH_IDENTITY_FILE,
                                esmon_common.CSTR_LOCAL_HOST],
                      default=[LOCALHOST_SSH_HOST])

MAPPING_DICT = {esmon_common.ESMON_CONFIG_CSTR_NONE: None}

ESMON_INSTALL_CSTRS[esmon_common.CSTR_SSH_IDENTITY_FILE] = \
    EsmonConfigString(esmon_common.CSTR_SSH_IDENTITY_FILE,
                      ESMON_CONFIG_CSTR_PATH,
                      """This option is the SSH key file used when using SSH command to login into
the host. If the default SSH identity file works, this option can be set to\n\"""" +
                      esmon_common.ESMON_CONFIG_CSTR_NONE + '".',
                      allow_none=True,
                      default=esmon_common.ESMON_CONFIG_CSTR_NONE,
                      mapping_dict=MAPPING_DICT)

ESMON_TEST_CSTRS = ESMON_INSTALL_CSTRS.copy()

ESMON_TEST_CSTRS[esmon_common.CSTR_BACKFS_TYPE] = \
    EsmonConfigString(esmon_common.CSTR_BACKFS_TYPE,
                      ESMON_CONFIG_CSTR_CONSTANT,
                      """This option determines which backend file system to use for Lustre.""",
                      constants=lustre.LUSTRE_BACKEND_FILESYSTEMS)

ESMON_TEST_CSTRS[esmon_common.CSTR_SKIP_INSTALL_TEST] = \
    EsmonConfigString(esmon_common.CSTR_SKIP_INSTALL_TEST,
                      ESMON_CONFIG_CSTR_BOOL,
                      """This option determines whether to skip ES PERFMON install test or not. When
this option is enabled, it is assumed that the ES PERFMON has already been
installed on the current system. If ES PERFMON has not been installed properly, the
following tests might fail.""")

ESMON_TEST_CSTRS[esmon_common.CSTR_ESMON_VIRT] = \
    EsmonConfigString(esmon_common.CSTR_ESMON_VIRT,
                      ESMON_CONFIG_CSTR_PATH,
                      """This option is the config file path of esmon_virt. The config file will be
read by esmon_virt command to install virtual machines.""")

ESMON_CONFIG_RUNNING = True

INFO = """Multiple items with the same name prefix can be added using the same template,
e.g. OSS01, OSS02, ..., OSS099, or OSS1, OSS2, ..., OSS99."""
ESMON_CONFIG_ADD_MULTIPLE = EsmonConfigString("whether_multiple",
                                              ESMON_CONFIG_CSTR_BOOL,
                                              INFO)

ESMON_CONFIG_ADD_PREFIX = EsmonConfigString("prefix",
                                            ESMON_CONFIG_CSTR_STRING,
                                            "")


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
            logging.error('illegal configuration: no option "%s" found in '
                          'following config:\n %s', id_key,
                          yaml.dump(current_config, Dumper=EsmonYamlDumper,
                                    default_flow_style=False))
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


def esmon_input_init():
    """
    Initialize the input completer
    """
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set editing-mode vi")
    readline.set_completer(ESMON_INPUT_STATUS.ecis_completer)


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
        logging.error('illegal configuration: option "%s" is not supported',
                      current_key)
        return None

    current_cstring = ESMON_INSTALL_CSTRS[current_key]
    if current_cstring.ecs_type != ESMON_CONFIG_CSTR_LIST:
        logging.error('illegal configuration: option "%s" should not be a '
                      'list', current_key)
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
            logging.error('illegal configuration: no option "%s" found in '
                          'following config:\n %s', item_key,
                          yaml.dump(child_config, Dumper=EsmonYamlDumper,
                                    default_flow_style=False))
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
            logging.error('illegal configuration: no option "%s" found in '
                          'following config:\n%s', id_key,
                          yaml.dump(current_config, Dumper=EsmonYamlDumper,
                                    default_flow_style=False))
            return -1

        id_value = child_config[id_key]
        if arg == id_value:
            if matched_child_config is not None:
                logging.error('illegal configuration: multiple children with '
                              'value "%s" for key "%s" in following config:\n %s',
                              id_value, id_key,
                              yaml.dump(current_config, Dumper=EsmonYamlDumper,
                                        default_flow_style=False))
                return -1
            matched_child_config = child_config

    if matched_child_config is None:
        logging.error('no child found with value "%s" for key "%s"',
                      arg, id_key)
        return -1

    child = EsmonWalkEntry(arg, matched_child_config)
    ESMON_CONFIG_WALK_STACK.append(child)

    return 0


def esmon_edit(current):
    """
    Edit a value
    """
    # pylint: disable=too-many-return-statements
    key = current.ewe_key
    current_config = current.ewe_config
    if isinstance(current_config, bool):
        cstring_types = [ESMON_CONFIG_CSTR_BOOL]
    elif isinstance(current_config, str):
        cstring_types = [ESMON_CONFIG_CSTR_CONSTANT,
                         ESMON_CONFIG_CSTR_PATH,
                         ESMON_CONFIG_CSTR_STRING,
                         ESMON_CONFIG_CSTR_DEF]
    elif isinstance(current_config, int):
        cstring_types = [ESMON_CONFIG_CSTR_INT]
    else:
        logging.error('unsupported type of config value "%s"',
                      current_config)
        return -1
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0

    if length <= 1:
        logging.error('illegal configuration: ROOT should not be editable')
        return -1

    parent = ESMON_CONFIG_WALK_STACK[-2]
    parent_config = parent.ewe_config

    if key not in ESMON_INSTALL_CSTRS:
        logging.error('illegal configuration: option "%s" is not supported',
                      key)
        return -1

    cstring = ESMON_INSTALL_CSTRS[key]
    if cstring.ecs_type not in cstring_types:
        logging.error('illegal configuration: the type of option "%s" is not '
                      '"%s", it might be "%s"',
                      key, cstring.ecs_type, cstring_types)
        return -1

    print cstring.ecs_help_info, "\n"
    print 'Current value: "%s"' % current_config

    ret, value = esmon_cstr_input_loop(cstring)
    if ret == ESMON_CONFIG_EDIT_QUIT or value == current_config:
        print 'Keep it as "%s"' % current_config
        return 0

    ret = esmon_config_check_add_def(value, cstring)
    if ret:
        return -1

    # If changing the item key of the grandparent, then update the
    # key in the stack for a correct path
    if length > 2:
        grandparent = ESMON_CONFIG_WALK_STACK[-3]
        grandparent_key = grandparent.ewe_key

        if grandparent_key not in ESMON_INSTALL_CSTRS:
            logging.error('illegal configuration: option "%s" is not supported',
                          grandparent_key)
            return -1
        grandparent_cstr = ESMON_INSTALL_CSTRS[grandparent_key]
        if ((grandparent_cstr.ecs_type == ESMON_CONFIG_CSTR_LIST) and
                (grandparent_cstr.ecs_item_key == key)):
            parent.ewe_key = value

    parent_config[key] = value
    current.ewe_config = value
    print 'Changed it to "%s"' % value
    return 0


def esmon_cstr_input_loop(cstring, prompt=None):
    """
    Loop until allowed string is inputed
    """
    # pylint: disable=too-many-branches,redefined-variable-type,bare-except
    # pylint: disable=too-many-statements
    ESMON_INPUT_STATUS.ecis_status = ESMON_INPUT_STATUS.STATUS_CSTR
    if prompt is None:
        if cstring.ecs_type == ESMON_CONFIG_CSTR_BOOL:
            prompt = 'To set it to True/False, press t/f: '
            ESMON_INPUT_STATUS.ecis_cstr_candidates = ["t", "f"]
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_CONSTANT:
            if len(cstring.ecs_constants) == 1:
                prompt = 'The supported value is: '
            else:
                prompt = 'The supported values are: '
            value_string = ""
            ESMON_INPUT_STATUS.ecis_cstr_candidates = []
            for supported_value in cstring.ecs_constants:
                if value_string != "":
                    value_string += ", "
                value_string += '"%s"' % supported_value
                ESMON_INPUT_STATUS.ecis_cstr_candidates.append(supported_value)
            prompt += value_string + ".\n"
            prompt += 'Please select one of the supported values: '
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_PATH:
            prompt = 'Please input the new path: '
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_STRING:
            prompt = 'Please input the new value (a string): '
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_INT:
            prompt = ('Please input an integer in [%s-%s]: ' %
                      (cstring.ecs_start, cstring.ecs_end))
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_DEF:
            prompt = 'Please input the new value (a string): '
        else:
            logging.error('unknown type "%s"', cstring.ecs_type)

    value = None
    ret = 0
    while ESMON_CONFIG_RUNNING:
        try:
            cmd_line = raw_input(prompt)
        except (KeyboardInterrupt, EOFError):
            ret = ESMON_CONFIG_EDIT_QUIT
            print ""
            break

        cmd_line = cmd_line.strip()
        if len(cmd_line) == 0:
            continue

        if cstring.ecs_type == ESMON_CONFIG_CSTR_BOOL:
            if cmd_line == 'T' or cmd_line == 't':
                value = True
            elif cmd_line == 'F' or cmd_line == 'f':
                value = False
            else:
                logging.error('"%s" is neither "t" nor "f"', cmd_line)
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_CONSTANT:
            for supported_value in cstring.ecs_constants:
                if cmd_line == supported_value:
                    value = cmd_line
                    break
            if value is None:
                logging.error('"%s" is not supported value', cmd_line)
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_PATH:
            if len(cmd_line) <= 1:
                logging.error('path "%s" is too short', cmd_line)
            elif cstring.ecs_allow_none and cmd_line == esmon_common.ESMON_CONFIG_CSTR_NONE:
                value = esmon_common.ESMON_CONFIG_CSTR_NONE
            elif cmd_line[0] != '/':
                logging.error('"%s" is not absolute path', cmd_line)
            else:
                value = cmd_line
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_STRING:
            value = cmd_line
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_INT:
            try:
                value = int(cmd_line)
                if value < cstring.ecs_start or value > cstring.ecs_end:
                    logging.error('"%s" is out of range [%s-%s]', value,
                                  cstring.ecs_start, cstring.ecs_end)
                    value = None
            except:
                logging.error('"%s" is not an integer', cmd_line)
        elif cstring.ecs_type == ESMON_CONFIG_CSTR_DEF:
            value = cmd_line
        else:
            logging.error('unknown type "%s"', cstring.ecs_type)

        if value is not None:
            break

    return ret, value


def esmon_config_guide(cstring, section):
    """
    Return the guide of this cstring
    """
    if section == "":
        guide_string = ""
    else:
        guide_string = "# " + section
        if "." not in section:
            guide_string += "."
        guide_string += " " + cstring.ecs_string + "\n# "
        guide_string += cstring.ecs_help_info.replace("\n", "\n# ")
        if cstring.ecs_default is not None:
            guide_string += "\n# Default value: %s" % cstring.ecs_default
        guide_string += "\n#\n"
    if cstring.ecs_children is None:
        return guide_string
    child_index = 1
    for child_string in cstring.ecs_children:
        child_cstr = ESMON_INSTALL_CSTRS[child_string]
        if section == "":
            child_section = str(child_index)
        else:
            child_section = section + "." + str(child_index)
        child_index += 1
        guide_string += esmon_config_guide(child_cstr, child_section)
    return guide_string


def esmon_config_string():
    """
    Return the current configuration string
    """
    root = ESMON_CONFIG_WALK_STACK[0]
    root_config = root.ewe_config
    simplifed_config = copy.deepcopy(root_config)
    config_string = """#
# Configuration file of ESPerfMon from DDN
#
# This file is automatically generated by esmon_config command. To update this
# file, please run esmon_config command.
#
# Configuration Guide:
#
"""
    config_string += esmon_config_guide(ESMON_INSTALL_ROOT, "")
    simplify_list = []
    ret = esmon_config_check(simplifed_config, simplifed_config, "/",
                             ESMON_INSTALL_ROOT,
                             simplify=simplify_list)
    if ret:
        logging.error('fix me: failed to simplify config, skip simplifying')
        config_string += yaml.dump(root_config, Dumper=EsmonYamlDumper,
                                   default_flow_style=False)
    else:
        config_string += yaml.dump(simplifed_config, Dumper=EsmonYamlDumper,
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
        logging.error('command "%s" is not found', command)
        return -1

    config_command = ESMON_CONFIG_COMMNADS[command]

    ret = -1
    try:
        ret = config_command.ecc_function(arg_string)
    except Exception, err:
        logging.error('failed to run command "%s", exception: %s, %s',
                      cmd_line, err, traceback.format_exc())
        return -1

    return ret


def esmon_command_input_loop():
    """
    Loop and excute the command
    """
    while ESMON_CONFIG_RUNNING:
        ESMON_INPUT_STATUS.ecis_status = ESMON_INPUT_STATUS.STATUS_COMMAND
        try:
            cmd_line = raw_input('[%s]$ (h for help): ' % esmon_pwd())
        except (KeyboardInterrupt, EOFError):
            print ""
            print "Type q to exit"
            continue

        cmd_line = cmd_line.strip()
        if len(cmd_line) == 0:
            continue
        esmon_command(cmd_line)

ESMON_DEF_MISSING = -2


def esmon_config_bool_check(config, path, cstr):
    """
    Check whether the bool config is legal or not
    """
    # pylint: disable=unused-argument
    if not isinstance(config, bool):
        logging.error('illegal configuration: config "%s" is not bool',
                      path)
        return -1

    return 0


def esmon_config_dict_check(root_config, config, path, cstr,
                            simplify=None, silent_on_missing=False):
    """
    Check whether the dict config is legal or not
    """
    # pylint: disable=too-many-branches,too-many-arguments
    if not isinstance(config, dict):
        logging.error('illegal configuration: config "%s" is not dictionary',
                      path)
        return -1

    child_names = cstr.ecs_children
    for expected_child in child_names:
        if expected_child not in config:
            assert expected_child in ESMON_INSTALL_CSTRS
            child_cstr = ESMON_INSTALL_CSTRS[expected_child]
            if child_cstr.ecs_default is None:
                logging.error('illegal configuration: config "%s" doesnot have '
                              'expected child [%s]', path, expected_child)
                return -1
            elif simplify is None:
                config[expected_child] = copy.copy(child_cstr.ecs_default)

    for child_name, child_config in config.items():
        if child_name not in child_names:
            logging.error('illegal configuration: config "%s" should not have '
                          'child [%s]', path, child_name)
            return -1
        if child_name not in ESMON_INSTALL_CSTRS:
            logging.error('illegal configuration: child [%s] is not a valid '
                          'option name', child_name)
            return -1
        child_cstr = ESMON_INSTALL_CSTRS[child_name]
        if path == "/":
            child_path = "/" + child_name
        else:
            child_path = path + "/" + child_name
        ret = esmon_config_check(root_config, child_config, child_path, child_cstr,
                                 simplify=simplify,
                                 silent_on_missing=silent_on_missing)
        if ret:
            return ret

        if simplify is not None:
            if child_cstr.ecs_type == ESMON_CONFIG_CSTR_LIST:
                if len(child_config) == 0:
                    if child_name in simplify:
                        del config[child_name]
                    else:
                        simplify.append(child_name)
                    logging.debug("simplified %s/%s", path, child_name)
            elif child_cstr.ecs_default is not None:
                if child_config == child_cstr.ecs_default:
                    if child_name in simplify:
                        del config[child_name]
                    else:
                        simplify.append(child_name)
                    logging.debug("simplified %s/%s", path, child_name)
    return 0


def esmon_config_int_check(config, path, cstr):
    """
    Check whether the int config is legal or not
    """
    # pylint: disable=unused-argument
    if not isinstance(config, int):
        logging.error('illegal configuration: config "%s" is not integer',
                      path)
        return -1

    if (config < cstr.ecs_start or
            config > cstr.ecs_end):
        logging.error('"%s" is out of range [%s-%s]',
                      config, cstr.ecs_start,
                      cstr.ecs_end)
        return -1

    return 0


def esmon_config_string_check(config, path, cstr):
    """
    Check whether the string config is legal or not
    """
    # pylint: disable=unused-argument
    if not isinstance(config, str):
        logging.error('illegal configuration: config "%s" is not string',
                      path)
        return -1
    return 0


def esmon_config_path_check(config, path, cstr):
    """
    Check whether the path config is legal or not
    """
    if not isinstance(config, str):
        logging.error('illegal configuration: config "%s" is not string',
                      path)
        return -1

    if len(config) <= 1:
        logging.error('illegal configuration: path "%s" is too short',
                      config)
    elif (cstr.ecs_allow_none and
          config == esmon_common.ESMON_CONFIG_CSTR_NONE):
        pass
    elif config[0] != '/':
        logging.error('illegal configuration: path "%s" is not absolute '
                      'path', config)
    return 0


def esmon_config_constant_check(config, path, cstr):
    """
    Check whether the constant config is legal or not
    """
    if not isinstance(config, str):
        logging.error('illegal configuration: config "%s" is not string',
                      path)
        return -1

    found = False
    for supported_value in cstr.ecs_constants:
        if config == supported_value:
            found = True
            break
    if not found:
        logging.error('"%s" is not supported value for constant "%s"',
                      config, cstr.ecs_string)
        return -1

    return 0


def esmon_config_list_check(root_config, config, path, cstr,
                            simplify=None, silent_on_missing=False):
    """
    Check whether the list config is legal or not
    """
    # pylint: disable=too-many-return-statements,too-many-branches
    # pylint: disable=too-many-nested-blocks,too-many-locals
    # pylint: disable=too-many-arguments
    if not isinstance(config, list):
        logging.error('illegal configuration: config "%s" is not list',
                      path)
        return -1

    item_key = cstr.ecs_item_key
    grandson_names = cstr.ecs_children
    for child_config in config:
        if not isinstance(child_config, dict):
            logging.error('illegal configuration: a child of config "%s" '
                          'is not dictionary', path)
            return -1

        if item_key not in child_config:
            logging.error('illegal configuration: a child of config "%s" '
                          'has no key "%s"', path, item_key)
            return -1

        child_name = child_config[item_key]
        if path == "/":
            child_path = "/" + child_name
        else:
            child_path = path + "/" + child_name

        for expected_grandon in grandson_names:
            if expected_grandon not in child_config:
                assert expected_grandon in ESMON_INSTALL_CSTRS
                grandson_cstr = ESMON_INSTALL_CSTRS[expected_grandon]
                if grandson_cstr.ecs_default is None:
                    logging.error('illegal configuration: config "%s" doesnot have '
                                  'expected child [%s]', child_path, expected_grandon)
                    return -1
                elif simplify is None:
                    child_config[expected_grandon] = copy.copy(grandson_cstr.ecs_default)

        for grandson_name, grandson_config in child_config.items():
            if grandson_name not in grandson_names:
                logging.error('illegal configuration: config "%s" should not '
                              'have child [%s]', child_path, grandson_name)
                return -1
            if grandson_name not in ESMON_INSTALL_CSTRS:
                logging.error('illegal configuration: child [%s] is not a '
                              'valid option name', grandson_name)
                return -1
            grandson_cstr = ESMON_INSTALL_CSTRS[grandson_name]
            grandson_path = child_path + "/" + grandson_name
            ret = esmon_config_check(root_config, grandson_config, grandson_path,
                                     grandson_cstr, simplify=simplify,
                                     silent_on_missing=silent_on_missing)
            if ret:
                return ret

            if simplify is not None:
                if grandson_cstr.ecs_type == ESMON_CONFIG_CSTR_LIST:
                    if len(grandson_config) == 0:
                        if grandson_name in simplify:
                            del child_config[grandson_name]
                        else:
                            simplify.append(grandson_name)
                        logging.debug("simplified %s", grandson_path)
                elif grandson_cstr.ecs_type == ESMON_CONFIG_CSTR_DICT:
                    assert grandson_cstr.ecs_default is None
                elif grandson_cstr.ecs_default is not None:
                    if grandson_config == grandson_cstr.ecs_default:
                        if grandson_name in simplify:
                            del child_config[grandson_name]
                        else:
                            simplify.append(grandson_name)
                        logging.debug("simplified %s", grandson_path)
    return 0


def esmon_config_def_parent(root_config, cstr):
    """
    Give a cstring of definition, return config and path of its parent
    """
    parent_config = root_config
    parent_path = "/"
    parent_cstr = ESMON_INSTALL_ROOT
    for entry in cstr.ecs_define_entries:
        if not isinstance(parent_config, dict):
            logging.error('illegal configuration: config "%s" is not a dictionary',
                          parent_path)
            return -1, None, None, None
        if entry not in parent_config:
            logging.error('illegal configuration: config "%s" has no child "%s"',
                          parent_path, entry)
            return -1, None, None, None

        if entry not in parent_cstr.ecs_children:
            logging.error('fix me: cstring "%s" has no child "%s"',
                          parent_path, entry)
            return -1, None, None, None

        if entry not in ESMON_INSTALL_CSTRS:
            logging.error('fix me: "%s" is not supported cstring',
                          entry)
            return -1, None, None, None

        parent_config = parent_config[entry]
        if parent_path != "/":
            parent_path += "/"
        parent_path += entry
        parent_cstr = ESMON_INSTALL_CSTRS[entry]

    if not isinstance(parent_config, list):
        logging.error('illegal configuration: config "%s" is not a list',
                      parent_path)
        return -1, None, None, None

    return 0, parent_config, parent_path, parent_cstr


def esmon_config_def_check(root_config, config, path, cstr,
                           silent_on_missing=False):
    """
    Check whether the definition config is legal or not
    """
    # pylint: disable=too-many-return-statements,unused-variable
    if not isinstance(config, str):
        logging.error('illegal configuration: config "%s" is not a string',
                      path)
        return -1

    ret, parent_config, parent_path, parent_cstr = \
        esmon_config_def_parent(root_config, cstr)
    if ret:
        return -1

    # Skip the definition check
    if path.startswith(parent_path):
        return 0

    found = False
    for definition in parent_config:
        if not isinstance(definition, dict):
            logging.error('illegal configuration: a item of list "%s" is not '
                          'a dictionary', path)
            return -1
        if cstr.ecs_string not in definition:
            logging.error('illegal configuration: a item of list "%s" has '
                          'no "%s" option', path, cstr.ecs_string)
            return -1
        value = definition[cstr.ecs_string]
        if value == config:
            found = True
    if not found:
        if not silent_on_missing:
            logging.error('illegal configuration: definition of "%s" can not '
                          'be found in list "%s"', config, parent_path)
        return ESMON_DEF_MISSING

    return 0


def esmon_config_def_add(root_config, cstr, new_value):
    """
    Add the definition config
    """
    # pylint: disable=too-many-return-statements,unused-variable
    ret, parent_config, parent_path, parent_cstr = \
        esmon_config_def_parent(root_config, cstr)
    if ret:
        return -1

    ret = esmon_item_add(parent_config, parent_cstr, new_value, definition=True)
    return ret


def esmon_config_check(root_config, config, path, cstr,
                       simplify=None, silent_on_missing=False):
    """
    Check whether the config is legal or not
    """
    # pylint: disable=too-many-return-statements,too-many-branches
    # pylint: disable=too-many-arguments
    logging.debug("checking %s", path)
    if cstr.ecs_type == ESMON_CONFIG_CSTR_DICT:
        ret = esmon_config_dict_check(root_config, config, path, cstr,
                                      simplify=simplify,
                                      silent_on_missing=silent_on_missing)
        if ret:
            return -1
    elif cstr.ecs_type == ESMON_CONFIG_CSTR_LIST:
        ret = esmon_config_list_check(root_config, config, path,
                                      cstr,
                                      simplify=simplify,
                                      silent_on_missing=silent_on_missing)
        if ret:
            return -1
    elif cstr.ecs_type == ESMON_CONFIG_CSTR_STRING:
        ret = esmon_config_string_check(config, path,
                                        cstr)
        if ret:
            return -1
    elif cstr.ecs_type == ESMON_CONFIG_CSTR_INT:
        ret = esmon_config_int_check(config, path,
                                     cstr)
        if ret:
            return -1
    elif cstr.ecs_type == ESMON_CONFIG_CSTR_CONSTANT:
        ret = esmon_config_constant_check(config, path,
                                          cstr)
        if ret:
            return -1
    elif cstr.ecs_type == ESMON_CONFIG_CSTR_PATH:
        ret = esmon_config_path_check(config, path,
                                      cstr)
        if ret:
            return -1
    elif cstr.ecs_type == ESMON_CONFIG_CSTR_BOOL:
        ret = esmon_config_bool_check(config, path,
                                      cstr)
        if ret:
            return -1
    elif cstr.ecs_type == ESMON_CONFIG_CSTR_DEF:
        ret = esmon_config_def_check(root_config, config, path,
                                     cstr,
                                     silent_on_missing=silent_on_missing)
        if ret:
            return ret
    else:
        logging.error('unsupported option type "%s" of config "%s"',
                      cstr.ecs_type, path)
        return -1

    return 0


def esmon_scratch_dict(cstring):
    """
    Return the scratch config of a dictionary
    """
    config = {}
    for child in cstring.ecs_children:
        child_cstr = ESMON_INSTALL_CSTRS[child]
        if child_cstr.ecs_default is None:
            config[child] = esmon_scratch_dict(child_cstr)
        else:
            config[child] = copy.copy(child_cstr.ecs_default)
    return config


def esmon_config(workspace):
    """
    Start to config the file
    """
    # pylint: disable=too-many-branches,bare-except,too-many-locals
    # pylint: disable=global-statement
    global ESMON_CONFIG_ROOT, ESMON_CONFIG_WALK_STACK, ESMON_SAVED_CONFIG_STRING
    save_fpath = workspace + "/" + esmon_common.ESMON_INSTALL_CONFIG_FNAME

    create_reason = None
    if os.path.exists(CONFIG_FPATH):
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
        if config is None:
            create_reason = 'File "%s" is an empty config.' % CONFIG_FPATH
    else:
        create_reason = 'File "%s" doesnot exist.' % CONFIG_FPATH

    if create_reason is not None:
        ESMON_SAVED_CONFIG_STRING = ""
        print create_reason
        prompt = "Press T/t to create it from scratch, press F/f to quit: "
        create_cstring = EsmonConfigString("create",
                                           ESMON_CONFIG_CSTR_BOOL,
                                           "")
        ret, create_new = esmon_cstr_input_loop(create_cstring,
                                                prompt=prompt)
        if ret == ESMON_CONFIG_EDIT_QUIT or not create_new:
            return 0

        open(CONFIG_FPATH, 'a').close()
        config = esmon_scratch_dict(ESMON_INSTALL_ROOT)

    ESMON_CONFIG_ROOT = EsmonWalkEntry("/", config)
    ESMON_CONFIG_WALK_STACK = [ESMON_CONFIG_ROOT]

    ret = esmon_config_check(config, config, "/", ESMON_INSTALL_ROOT)
    if ret:
        return -1

    esmon_input_init()
    esmon_command_input_loop()
    esmon_input_fini()
    return 0


def install_config_value(config, key):
    """
    Return the config value
    """
    if key not in ESMON_INSTALL_CSTRS:
        logging.error("invalid config option [%s]", key)
        return -1, None

    cstring = ESMON_INSTALL_CSTRS[key]
    if key not in config:
        if cstring.ecs_default is None:
            logging.error("config option [%s] is not configured and has no "
                          "default value", key)
            return -1, None
        value = cstring.ecs_default
        logging.debug("config option [%s] is not configured and use "
                      "default value [%s]", key, cstring.ecs_default)
    else:
        value = config[key]

    mapping_dict = cstring.ecs_mapping_dict
    if mapping_dict is not None and value in mapping_dict:
        value = mapping_dict[value]
    return 0, value


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
    CONFIG_FPATH = esmon_common.ESMON_INSTALL_CONFIG

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

    utils.configure_logging(workspace, simple_console=True)

    ret = esmon_config(workspace)
    if ret:
        logging.error("config failed, please check [%s] for more log",
                      workspace)
        sys.exit(ret)
    logging.info("Please check [%s] for the ES PERFMON configuration "
                 "and [%s] for more log",
                 CONFIG_FPATH, workspace)
    sys.exit(0)
