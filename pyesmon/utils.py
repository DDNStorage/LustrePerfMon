# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Misc utility library
"""

from __future__ import print_function
import os
import time
import signal
import subprocess
import StringIO
import select
import logging
import logging.handlers
import datetime
import threading
import traceback
import sys
import random
import string
import dateutil.tz

LOG_INFO_FNAME = "info.log"
LOGGING_HANLDERS = {}


def eprint(*args, **kwargs):
    """
    Print to stderr
    """
    print(*args, file=sys.stderr, **kwargs)


def read_one_line(filename):
    """
    Open file and read one line
    """
    return open(filename, 'r').readline().rstrip('\n')


def pid_is_alive(pid):
    """
    True if process pid exists and is not yet stuck in Zombie state.
    Zombies are impossible to move between cgroups, etc.
    pid can be integer, or text of integer.
    """
    path = '/proc/%s/stat' % pid

    try:
        stat = read_one_line(path)
    except IOError:
        if not os.path.exists(path):
            # file went away
            return False
        raise

    return stat.split()[2] != 'Z'


def signal_pid(pid, sig):
    """
    Sends a signal to a process id. Returns True if the process terminated
    successfully, False otherwise.
    """
    # pylint: disable=unused-variable
    try:
        os.kill(pid, sig)
    except OSError:
        # The process may have died before we could kill it.
        pass

    for i in range(5):
        if not pid_is_alive(pid):
            return True
        time.sleep(1)

    # The process is still alive
    return False


def nuke_subprocess(subproc):
    """
    Kill the subprocess
    """
    # check if the subprocess is still alive, first
    if subproc.poll() is not None:
        return subproc.poll()

    # the process has not terminated within timeout,
    # kill it via an escalating series of signals.
    signal_queue = [signal.SIGTERM, signal.SIGKILL]
    for sig in signal_queue:
        signal_pid(subproc.pid, sig)
        if subproc.poll() is not None:
            return subproc.poll()


class CommandResult(object):
    """
    All command will return a command result of this class
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, stdout="", stderr="",
                 exit_status=None, duration=0):
        self.cr_exit_status = exit_status
        self.cr_stdout = stdout
        self.cr_stderr = stderr
        self.cr_duration = duration


class CommandJob(object):
    """
    Each running of a command has an object of this class
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, command, timeout=None, stdout_tee=None,
                 stderr_tee=None, stdin=None, return_stdout=True,
                 return_stderr=True, quit_func=None,
                 flush_tee=False):
        # pylint: disable=too-many-arguments
        self.cj_command = command
        self.cj_result = CommandResult()
        self.cj_timeout = timeout
        self.cj_stdout_tee = stdout_tee
        self.cj_stderr_tee = stderr_tee
        self.cj_quit_func = quit_func
        # allow for easy stdin input by string, we'll let subprocess create
        # a pipe for stdin input and we'll write to it in the wait loop
        if isinstance(stdin, basestring):
            self.cj_string_stdin = stdin
            self.cj_stdin = subprocess.PIPE
        else:
            self.cj_string_stdin = None
            self.cj_stdin = None
        if return_stdout:
            self.cj_stdout_file = StringIO.StringIO()
        if return_stderr:
            self.cj_stderr_file = StringIO.StringIO()
        self.cj_started = False
        self.cj_killed = False
        self.cj_start_time = None
        self.cj_stop_time = None
        self.cj_max_stop_time = None
        self.cj_subprocess = None
        self.cj_return_stdout = return_stdout
        self.cj_return_stderr = return_stderr
        self.cj_flush_tee = flush_tee

    def cj_run_start(self):
        """
        Start to run the command
        """
        if self.cj_started:
            return -1

        self.cj_started = True
        self.cj_start_time = time.time()
        if self.cj_timeout:
            self.cj_max_stop_time = self.cj_timeout + self.cj_start_time
        shell = '/bin/bash'
        self.cj_subprocess = subprocess.Popen(self.cj_command,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              shell=True,
                                              executable=shell,
                                              stdin=self.cj_stdin)
        return 0

    def cj_run_stop(self):
        """
        Stop the job even when it is running
        """
        self.cj_kill()
        self.cj_post_exit()
        return self.cj_result

    def cj_post_exit(self):
        """
        After exit, process the outputs and calculate the duration
        """
        self.cj_process_output(is_stdout=True, final_read=True)
        self.cj_process_output(is_stdout=False, final_read=True)
        if self.cj_stdout_tee:
            self.cj_stdout_tee.flush()
        if self.cj_stderr_tee:
            self.cj_stderr_tee.flush()
        self.cj_subprocess.stdout.close()
        self.cj_subprocess.stderr.close()
        self.cj_stop_time = time.time()
        if self.cj_return_stdout:
            self.cj_result.cr_stdout = self.cj_stdout_file.getvalue()
        if self.cj_return_stderr:
            self.cj_result.cr_stderr = self.cj_stderr_file.getvalue()
        self.cj_result.cr_duration = self.cj_stop_time - self.cj_start_time
        logging.debug("command [%s] finished, "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      self.cj_command,
                      self.cj_result.cr_exit_status,
                      self.cj_result.cr_stdout,
                      self.cj_result.cr_stderr)

    def cj_run(self):
        """
        Run the command, wait until it exits and return the results
        """
        # Do not allow run for more than twice currently
        if self.cj_started:
            return self.cj_result

        ret = self.cj_run_start()
        if ret:
            self.cj_result.cr_exit_status = ret
            logging.debug("command [%s] failed to start, "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          self.cj_command,
                          self.cj_result.cr_exit_status,
                          self.cj_result.cr_stdout,
                          self.cj_result.cr_stderr)

        self.cj_wait_for_command()
        self.cj_post_exit()
        return self.cj_result

    def cj_process_output(self, is_stdout=True, final_read=False):
        """
        Process the stdout or stderr
        """
        buf = None
        if is_stdout:
            pipe = self.cj_subprocess.stdout
            if self.cj_return_stdout:
                buf = self.cj_stdout_file
            tee = self.cj_stdout_tee
        else:
            pipe = self.cj_subprocess.stderr
            if self.cj_return_stderr:
                buf = self.cj_stderr_file
            tee = self.cj_stderr_tee

        if final_read:
            # read in all the data we can from pipe and then stop
            tmp_data = []
            while select.select([pipe], [], [], 0)[0]:
                tmp_data.append(os.read(pipe.fileno(), 1024))
                if len(tmp_data[-1]) == 0:
                    break
            data = "".join(tmp_data)
        else:
            # perform a single read
            data = os.read(pipe.fileno(), 1024)
        if buf is not None:
            buf.write(data)
        if tee:
            tee.write(data)

    def cj_kill(self):
        """
        Kill the job
        """
        nuke_subprocess(self.cj_subprocess)
        self.cj_result.cr_exit_status = self.cj_subprocess.poll()
        self.cj_killed = True

    def cj_wait_for_command(self):
        """
        Wait until the command exits
        """
        # pylint: disable=too-many-branches
        read_list = []
        write_list = []
        reverse_dict = {}

        read_list.append(self.cj_subprocess.stdout)
        read_list.append(self.cj_subprocess.stderr)
        reverse_dict[self.cj_subprocess.stdout] = True
        reverse_dict[self.cj_subprocess.stderr] = False

        if self.cj_string_stdin is not None:
            write_list.append(self.cj_subprocess.stdin)

        if self.cj_timeout:
            time_left = self.cj_max_stop_time - time.time()
        else:
            time_left = None  # so that select never times out

        while not self.cj_timeout or time_left > 0:
            # select will return when we may write to stdin or when there is
            # stdout/stderr output we can read (including when it is
            # EOF, that is the process has terminated).
            # To check for processes which terminate without producing any
            # output, a 1 second timeout is used in select.
            read_ready, write_ready, _ = select.select(read_list, write_list,
                                                       [], 1)

            # os.read() has to be used instead of
            # subproc.stdout.read() which will otherwise block
            for file_obj in read_ready:
                is_stdout = reverse_dict[file_obj]
                self.cj_process_output(is_stdout)
                if self.cj_flush_tee:
                    if is_stdout:
                        self.cj_stdout_tee.flush()
                    else:
                        self.cj_stderr_tee.flush()

            for file_obj in write_ready:
                # we can write PIPE_BUF bytes without blocking
                # POSIX requires PIPE_BUF is >= 512
                file_obj.write(self.cj_string_stdin[:512])
                self.cj_string_stdin = self.cj_string_stdin[512:]
                # no more input data, close stdin, remove it from the select
                # set
                if not self.cj_string_stdin:
                    file_obj.close()
                    write_list.remove(file_obj)

            self.cj_result.cr_exit_status = self.cj_subprocess.poll()
            if self.cj_result.cr_exit_status is not None:
                return

            if self.cj_timeout:
                time_left = self.cj_max_stop_time - time.time()

            if self.cj_quit_func is not None and self.cj_quit_func():
                break

        # Kill process if timeout
        self.cj_kill()
        return


def run(command, timeout=None, stdout_tee=None, stderr_tee=None, stdin=None,
        return_stdout=True, return_stderr=True, quit_func=None,
        flush_tee=False):
    """
    Run a command
    """
    # pylint: disable=too-many-arguments
    job = CommandJob(command, timeout=timeout, stdout_tee=stdout_tee,
                     stderr_tee=stderr_tee, stdin=stdin,
                     return_stdout=return_stdout, return_stderr=return_stderr,
                     quit_func=quit_func, flush_tee=flush_tee)
    return job.cj_run()


def configure_logging(resultsdir):
    """
    Configure the logging levels
    """
    default_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] "
                                          "[%(filename)s:%(lineno)s] "
                                          "%(message)s",
                                          "%Y/%m/%d-%H:%M:%S")

    debug_handler = logging.FileHandler(resultsdir + "/debug.log")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(default_formatter)

    info_handler = logging.FileHandler(resultsdir + "/" + LOG_INFO_FNAME)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(default_formatter)

    warning_handler = logging.FileHandler(resultsdir + "/warning.log")
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(default_formatter)

    error_handler = logging.FileHandler(resultsdir + "/error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(default_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(default_formatter)

    logging.root.handlers = []
    logging.root.setLevel(logging.DEBUG)
    logging.root.addHandler(debug_handler)
    logging.root.addHandler(info_handler)
    logging.root.addHandler(console_handler)
    logging.root.addHandler(warning_handler)
    logging.root.addHandler(error_handler)

    LOGGING_HANLDERS["debug"] = debug_handler
    LOGGING_HANLDERS["console"] = console_handler
    LOGGING_HANLDERS["warning"] = warning_handler
    LOGGING_HANLDERS["error"] = error_handler


def utcnow():
    """
    Get the current UTC time which has the time zone info.
    """
    return datetime.datetime.now(dateutil.tz.tzutc())


def local_strftime(utc_datetime, fmt):
    """
    Return a string representing the date of timezone from the datetime of
    local timezone
    """
    local_datetime = utc_datetime.astimezone(dateutil.tz.tzlocal())
    return local_datetime.strftime(fmt)


def thread_start(target, args):
    """
    Wrap the target function and start a thread to run it
    """
    def target_wrap(*args, **kwargs):
        """
        Wrap the target function
        """
        # pylint: disable=bare-except
        ret = None
        try:
            ret = target(*args, **kwargs)
        except:
            logging.error("exception when running thread: [%s]",
                          traceback.format_exc())
        return ret

    run_thread = threading.Thread(target=target_wrap,
                                  args=args)
    run_thread.setDaemon(True)
    run_thread.start()
    return run_thread


def random_word(length):
    """
    Return random lowercase word with given length
    """
    return ''.join(random.choice(string.lowercase) for i in range(length))


def which(program):
    """
    Return the full path of (shell) commands.
    """
    # pylint: disable=unused-variable
    def is_exe(fpath):
        """
        Whether the fpath is an executable file
        """
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def wait_condition(condition_func, args, timeout=90, sleep_interval=1):
    # pylint: disable=too-many-arguments
    """
    Wait until the condition_func returns 0
    """
    waited = 0
    while True:
        ret = condition_func(args)
        if ret:
            if waited < timeout:
                waited += sleep_interval
                time.sleep(sleep_interval)
                continue
            logging.error("timeout when waiting condition")
            return -1
        return 0
    return -1
