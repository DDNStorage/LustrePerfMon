# Copyright (c) 2018 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Console that manages the scheduler
"""
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


ESMON_CONFIG_LOG_DIR = "/var/log/esmon_config"

ESMON_CONFIG_COMMNAD_HELP = "h"
ESMON_CONFIG_COMMNAD_LS = "ls"
ESMON_CONFIG_COMMNAD_CD = "cd"
ESMON_CONFIG_COMMNAD_EDIT = "e"
ESMON_CONFIG_ROOT = None
ESMON_CONFIG_WALK_STACK = []


class EsmonWalkEntry(object):
    """
    When walking to the subdir, an entry will be allocated
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, key, current_config):
        # The key used to walk to the subdir. For a dict, this is the
        # key of the dict. For a host list, this is usually the host_id
        # For sfas, this is the name value
        self.ewe_key = key
        # The current config walked to
        self.ewe_config = current_config


def console_error(message):
    """
    Print error to console
    """
    print "error: %s" % message


def command_needs_subdir(command):
    """
    If command needs an argument of subdir, return Ture
    """
    if command == ESMON_CONFIG_COMMNAD_CD:
        return True
    return False


def esmon_list_subdirs(current):
    """
    Return a list of the subdirs
    current: the current walk entry
    """
    subdirs = []
    current_config = current.ewe_config
    id_key = esmon_list_id_key(current)
    if id_key is None:
        return None

    for child_config in current_config:
        if id_key not in child_config:
            console_error('illegal configuration, no key "%s" found in '
                          'following config\n: %s' %
                          (id_key,
                           yaml.dump(child_config, default_flow_style=False)))
            return None

        subdirs.append(child_config[id_key])
    return subdirs


def esmon_subdirs():
    """
    Return the names/IDs of subdirs
    """
    # pylint: disable=global-statement,unused-variable
    subdirs = []
    length = len(ESMON_CONFIG_WALK_STACK)
    assert length > 0
    current = ESMON_CONFIG_WALK_STACK[-1]
    current_config = current.ewe_config

    if isinstance(current_config, dict):
        subdirs = []
        for key, value in current_config.iteritems():
            subdirs.append(key)
    elif isinstance(current_config, list):
        subdirs = esmon_list_subdirs(current)
    else:
        subdirs = []

    return subdirs


class EsmonCompleter(object):
    """
    Completer of command
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, options):
        self.ec_options = options
        self.ec_current_candidates = []

    def ec_complete(self, text, state):
        # pylint: disable=unused-argument,too-many-nested-blocks,too-many-branches
        """
        The complete function of the completer
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
                self.ec_current_candidates = sorted(self.ec_options.keys())
            else:
                try:
                    if begin == 0:
                        # first word
                        candidates = self.ec_options.keys()
                    else:
                        # later word
                        first = words[0]
                        candidates = list(self.ec_options[first])
                        needs_subdir = command_needs_subdir(first)
                        if needs_subdir:
                            subdirs = esmon_subdirs()
                            if subdirs is not None:
                                candidates += esmon_subdirs()
                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.ec_current_candidates = []
                        for candidate in candidates:
                            if not candidate.startswith(being_completed):
                                continue
                            self.ec_current_candidates.append(candidate)
                    else:
                        # matching empty string so use all candidates
                        self.ec_current_candidates = candidates
                except (KeyError, IndexError):
                    self.ec_current_candidates = []
        try:
            response = self.ec_current_candidates[state]
        except IndexError:
            response = None
        return response


def esmon_input_init():
    """
    Initialize the input completer
    """
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set editing-mode vi")
    # Register our completer function
    completer = EsmonCompleter({ESMON_CONFIG_COMMNAD_CD: [],
                                ESMON_CONFIG_COMMNAD_EDIT: [],
                                ESMON_CONFIG_COMMNAD_HELP: [],
                                ESMON_CONFIG_COMMNAD_LS: ["-r"]})
    readline.set_completer(completer.ec_complete)


def esmon_input_fini():
    """
    Stop the input completer
    """
    readline.set_completer(None)


def esmon_command_help(arg_string):
    # pylint: disable=unused-argument
    """
    Print the help string
    """
    print """Command action:
   cd $d     change the current directory to $d
   e $f      edit config $f
   h         print this menu
   ls [-r]   list config content under current directory
   q         quit without saving changes
   w         write config file to disk"""

    return 0


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


def esmon_list_id_key(current):
    """
    Return the id_key of a list
    """
    current_config = current.ewe_config
    id_key = None

    if ((current.ewe_key == esmon_common.CSTR_SSH_HOST) or
            (current.ewe_key == esmon_common.CSTR_CLIENT_HOSTS)):
        # Use the values of host IDs as the names
        id_key = esmon_common.CSTR_HOST_ID
    elif current.ewe_key == esmon_common.CSTR_SFAS:
        id_key = esmon_common.CSTR_NAME
    else:
        console_error('illegal configuration: unreconginzed list type in '
                      'following config:\n%s' %
                      (yaml.dump(current_config, default_flow_style=False)))
    return id_key


def esmon_list_ls(current):
    """
    Print a list of the config
    current: the current walk entry
    """
    current_config = current.ewe_config
    id_key = esmon_list_id_key(current)
    if id_key is None:
        return -1

    for child_config in current_config:
        if id_key not in child_config:
            console_error('illegal configuration, no key "%s" found in '
                          'following config\n: %s' %
                          (id_key,
                           yaml.dump(child_config, default_flow_style=False)))
            return -1

        id_value = child_config[id_key]

        print "%s: {%s: %s, ...}" % (id_value, id_key, id_value)
    return 0


def esmon_list_cd(current, arg_string):
    """
    Change to a subdir of current path
    """
    current_config = current.ewe_config
    matched_child_config = None
    id_key = esmon_list_id_key(current)
    if id_key is None:
        return -1

    for child_config in current_config:
        if id_key not in child_config:
            console_error('illegal configuration: no key "%s" found in '
                          'following config:\n%s' %
                          (id_key,
                           yaml.dump(child_config, default_flow_style=False)))
            return -1

        id_value = child_config[id_key]
        if arg_string == id_value:
            if matched_child_config is not None:
                console_error('illegal configuration: multiple children with '
                              'value "%s" for key "%s" in following config\n: %s' %
                              (id_value, id_key,
                               yaml.dump(current_config, default_flow_style=False)))
                return -1
            matched_child_config = child_config

    if matched_child_config is None:
        console_error('no child found with value "%s" for key "%s"' %
                      (id_value, id_key))
        return -1

    child = EsmonWalkEntry(arg_string, matched_child_config)
    ESMON_CONFIG_WALK_STACK.append(child)

    return 0


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
            for key, value in current_config.iteritems():
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
            print yaml.dump(current_config, default_flow_style=False)
    else:
        console_error('unknown argument "%s" of command "%s"' %
                      (arg_string, ESMON_CONFIG_COMMNAD_LS))
    return ret


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
    elif arg_string == "..":
        if length == 1:
            return 0
        else:
            ESMON_CONFIG_WALK_STACK.pop()
    elif (isinstance(current_config, dict) and
          (arg_string in current_config)):
        child_config = current_config[arg_string]
        child = EsmonWalkEntry(arg_string, child_config)
        ESMON_CONFIG_WALK_STACK.append(child)
    elif isinstance(current_config, list):
        ret = esmon_list_cd(current, arg_string)
    else:
        console_error('failed to change to subdir "%s"' % arg_string)
    return ret


def esmon_command_edit(arg_string):
    """
    Print the config in the current directory
    """
    # pylint: disable=unused-argument
    return 0


def esmon_command(cmd_line):
    """
    Run a command in the console
    """
    # pylint: disable=broad-except
    functions = {ESMON_CONFIG_COMMNAD_CD: esmon_command_cd,
                 ESMON_CONFIG_COMMNAD_EDIT: esmon_command_edit,
                 ESMON_CONFIG_COMMNAD_HELP: esmon_command_help,
                 ESMON_CONFIG_COMMNAD_LS: esmon_command_ls}
    if ' ' in cmd_line:
        command, arg_string = cmd_line.split(' ', 1)
    else:
        command = cmd_line
        arg_string = ""

    arg_string = arg_string.strip()

    try:
        func = functions[command]
    except (KeyError, IndexError), err:
        func = None

    # Run system command
    if func is not None:
        try:
            ret = func(arg_string)
        except Exception, err:
            console_error('failed to run command "%s", exception: %s, %s' %
                          (cmd_line, err, traceback.format_exc()))
            return -1
    else:
        console_error('command "%s" is not found' % command)
        ret = -1
    return ret


def esmon_input_loop():
    """
    Loop and excute the command
    """
    while True:
        cmd_line = raw_input('[%s]$ (h for help): ' % esmon_pwd())
        cmd_line = cmd_line.strip()
        if cmd_line == 'q' or cmd_line == 'quit':
            break
        if len(cmd_line) == 0:
            continue
        esmon_command(cmd_line)


def esmon_config(workspace, config_fpath):
    """
    Start to config the file
    """
    # pylint: disable=too-many-branches,bare-except,too-many-locals
    # pylint: disable=global-statement
    global ESMON_CONFIG_ROOT, ESMON_CONFIG_WALK_STACK
    save_fpath = workspace + "/" + esmon_common.ESMON_INSTALL_CONFIG_FNAME
    logging.debug("copying config file from [%s] to [%s]", config_fpath,
                  save_fpath)
    shutil.copyfile(config_fpath, save_fpath)

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

    ESMON_CONFIG_ROOT = EsmonWalkEntry("", config)
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
    reload(sys)
    sys.setdefaultencoding("utf-8")
    config_fpath = esmon_install_nodeps.ESMON_INSTALL_CONFIG

    if len(sys.argv) == 2:
        config_fpath = sys.argv[1]
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

    ret = esmon_config(workspace, config_fpath)
    if ret:
        logging.error("config failed, please check [%s] for more log",
                      workspace)
        sys.exit(ret)
    logging.info("Please check [%s] for the ESMON configuration"
                 "and [%s] for more log",
                 config_fpath, workspace)
    sys.exit(0)
