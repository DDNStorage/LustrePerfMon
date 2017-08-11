#!/usr/bin/python
# Copyright DataDirect Networks, Li Xi <lixi@ddn.com>, Jul 2015
"""This script gets the topn result of openTSDB"""
import sys
import os
import signal
import getopt
import shutil
import logging
import subprocess
import re
import time
import inspect
import urllib2
import stat
import datetime

TMP_DIR = "/tmp"
LOG_FILENAME = TMP_DIR + "/" + "topn.log"
LOGGER = logging.getLogger()
REPLAY = False
SEEK = False
HISTORY = False
INTERVAL_SEC = 60
START_DATE = datetime.datetime.today()
END_DATE = None
METRIC_NAME = ""
TAG_NAME = ""
QUERY_FILE = TMP_DIR + "/" + "topn_" + str(os.getpid()) + ".query"


def log_setup():
    """Setup the log, should be called as earlier as possible"""
    LOGGER.setLevel(logging.DEBUG)

    log_file = logging.FileHandler(LOG_FILENAME)
    LOGGER.addHandler(log_file)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(formatter)
    LOGGER.info("======== TopN started ========")
    LOGGER.info("Query data saved to %s", QUERY_FILE)


def run_command(command, dump_debug=True):
    """ Run shell command """
    if dump_debug:
        LOGGER.debug("Starting command '%s'", command)
    process = subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    ret = process.wait()
    stdout = ""
    for line in process.stdout.readlines():
        stdout = stdout + line
    stderr = ""
    for line in process.stderr.readlines():
        stderr = stderr + line
    if dump_debug:
        LOGGER.debug("Ended command '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
    return ret, stdout, stderr


def signal_hander(signum, frame):
    LOGGER.info("======== TopN ended ========")
    raise SystemExit()


class Datapoint:
    def __init__(self, metric_name, line):
        pattern = ("%s ([0-9]+) (\S+) {(.+)}" % (METRIC_NAME))
        matched = re.match(pattern, line)
        if not matched:
            LOGGER.error("'%s' not matches '%s'", line, pattern)
            raise RuntimeError()
        self.line = line
        self.time = int(matched.group(1))
        self.value = float(matched.group(2))
        pattern = r"([a-zA-Z0-9_]+)=([a-zA-Z0-9_\.]+)"
        self.tags = {}
        tag_string = matched.group(3)
        for matched in re.finditer(pattern, tag_string):
            self.tags[matched.group(1)] = matched.group(2)


def right_align(in_str, length):
    if len(in_str) > length:
        LOGGER.error("String '%s' longer than %d", in_str, length)
        return in_str
    out_str = ""
    for i in range(0, (length - len(in_str))):
        out_str += " "
    out_str += in_str
    return out_str


def getTerminalSize():
    import os
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            import os
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])


def print_to_console(lines, console_width, console_height):
    if (console_width < 3 or console_height < 1):
        return -1
    line_number = 0
    for line in lines.splitlines():
        if line_number + 1 == console_height:
            sys.stdout.write('...')
            sys.stdout.flush()
            break
        if len(line) > console_width:
            print line[:console_width - 3] + "..."
        else:
            print line
        line_number += 1


def usage(command):
    """ Dump help of usage. """
    sys.stderr.write("Usage: %s [-e|end <time>] [-h|help] [-i|interval] "
                     "[-m|metric] [-r|replay] [-s|start <time>] [-S|seek]"
                     "[-t|tag]\n" % command)
    sys.stderr.flush()


def datetime_parse_duration(duration_string):
    # Parses a human-readable duration (e.g, "10m", "3h", "14d") into seconds.
    # Formats supported:
    # ms: milliseconds
    # s: seconds
    # m: minutes
    # h: hours
    # d: days
    # w: weeks
    # n: month (30 days)
    # y: years (365 days)
    if len(duration_string) <= 2 or duration_string[-2] != 'm':
        number = float(duration_string[:-1])
        unit = duration_string[-1]
        multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 3600 * 24,
                      'w': 3600 * 24 * 7, 'n': 3600 * 24 * 30,
                      'y': 3600 * 24 * 365}
        return number * multiplier[unit]
    else:
        number = float(duration_string[:-2])
        return number / 1000.0


def datetime_parse(datetime_string):
    # Relative: 5m-ago, 1h-ago, etc.
    # Absolute human readable dates:
    # "yyyy/MM/dd-HH:mm:ss"
    # "yyyy/MM/dd HH:mm:ss"
    # "yyyy/MM/dd-HH:mm"
    # "yyyy/MM/dd HH:mm"
    # "yyyy/MM/dd"
    # Unix Timestamp in seconds or milliseconds:
    # 1355961600
    # 1355961600000
    # 1355961600.000
    if datetime_string.endswith("-ago"):
        try:
            interval = datetime_parse_duration(datetime_string[:-4])
        except:
            return None
        second = time.time() - interval
        return datetime.datetime.fromtimestamp(second)

    if "/" in datetime_string or ":" in datetime_string:
        length = len(datetime_string)
        if length == 10:
            try:
                return datetime.datetime.strptime(datetime_string, "%Y/%m/%d")
            except:
                return None
        elif length == 16:
            if "-" in datetime_string:
                try:
                    return datetime.datetime.strptime(datetime_string,
                                                      "%Y/%m/%d-%H:%M")
                except:
                    return None
            else:
                try:
                    return datetime.datetime.strptime(datetime_string,
                                                      "%Y/%m/%d %H:%M")
                except:
                    return None
        elif length == 19:
            if "-" in datetime_string:
                try:
                    return datetime.datetime.strptime(datetime_string,
                                                      "%Y/%m/%d-%H:%M:%S")
                except:
                    return None
            else:
                try:
                    return datetime.datetime.strptime(datetime_string,
                                                      "%Y/%m/%d %H:%M:%S")
                except:
                    return None
        else:
            LOGGER.error("Wrong time format: %s", datetime_string)
            return None
    else:
        if "." in datetime_string:
            if (datetime_string[10] != '.' or len(datetime_string) != 14):
                LOGGER.error("Wrong time format: %s", datetime_string)
                return None
            try:
                second = float(datetime_string)
            except:
                return None
            return datetime.datetime.fromtimestamp(second)
        else:
            if (len(datetime_string) > 10 and len(datetime_string) != 13):
                LOGGER.error("Wrong time format: %s", datetime_string)
                return None
            try:
                second = float(datetime_string)
            except:
                return None
            if len(datetime_string) == 13:
                second = second / 1000.0
            return datetime.datetime.fromtimestamp(second)


def main(argv):
    """ Main function. """
    global START_DATE
    global REPLAY
    global SEEK
    global METRIC_NAME
    global TAG_NAME
    global INTERVAL_SEC
    global HISTORY

    try:
        opts, args = getopt.getopt(argv[1:], "e:hi:m:rs:St:",
                                   ["end",
                                    "help",
                                    "metric",
                                    "replay",
                                    "start",
                                    "seek",
                                    "tag",
                                    "interval"])
    except getopt.GetoptError:
        sys.stderr.write("Failed to parse options %s\n" % argv)
        usage(argv[0])
        return 2
    for opt, arg in opts:
        if opt in ("-e", "--end"):
            END_DATE = datetime_parse(arg)
            if END_DATE is None:
                sys.stderr.write("Invalid end date '%s'\n" % arg)
                return 2
        elif opt in ("-h", "--help"):
            usage(argv[0])
            return 0
        elif opt in ("-m", "--metric"):
            METRIC_NAME = arg
        elif opt in ("-r", "--replay"):
            LOGGER.debug("Replay history")
            REPLAY = True
        elif opt in ("-s", "--start"):
            LOGGER.debug("Time start from %s", arg)
            START_DATE = datetime_parse(arg)
            if START_DATE is None:
                sys.stderr.write("Invalid start date '%s'\n" % arg)
                return 2
            HISTORY = True
        elif opt in ("-S", "--seek"):
            LOGGER.debug("Seek to the first valid data")
            SEEK = True
        elif opt in ("-t", "--tag"):
            TAG_NAME = arg
        elif opt in ("-i", "--interval"):
            INTERVAL_SEC = int(arg)
        else:
            sys.stderr.write("Unkown option '%s'\n" % opt)
            return 2

    if METRIC_NAME == "":
        sys.stderr.write("Please give metric name\n")
        usage(argv[0])
        return 2

    START_DATE = datetime.datetime.fromtimestamp(
        int(time.mktime(START_DATE.timetuple()))
        / INTERVAL_SEC * INTERVAL_SEC)

    if END_DATE is not None:
        END_DATE = datetime.datetime.fromtimestamp(
            int(time.mktime(END_DATE.timetuple()))
            / INTERVAL_SEC * INTERVAL_SEC)
        if END_DATE - START_DATE < datetime.timedelta(seconds=1):
            sys.stderr.write("End time is not larger enough than start "
                             "time\n")
            usage(argv[0])
            return 2

    signal.signal(signal.SIGINT, signal_hander)
    signal.signal(signal.SIGTERM, signal_hander)

    date = START_DATE
    sys.stdout.write("Initializing...\n")
    wakeup_time = time.time()
    start_ms = int(time.mktime(START_DATE.timetuple())) * 1000
    end_ms = None
    if END_DATE is not None:
        end_ms = int(time.mktime(END_DATE.timetuple())) * 1000
    while True:
        aggregate_query = ""
        if TAG_NAME != "":
            aggregate_query = ("%s=*" % TAG_NAME)
        current_ms = int(time.mktime(date.timetuple())) * 1000
        if end_ms is not None and current_ms > end_ms:
            break
        command = ("tsdb query %d sum rate downsample %d "
                   "sum %s %s | "
                   "sort -k2 -n > %s" %
                   (current_ms, INTERVAL_SEC * 1000, METRIC_NAME,
                    aggregate_query, QUERY_FILE))
        ret, stdout, stderr = run_command(command)
        if ret:
            return ret

        log_file = open(QUERY_FILE, 'r')
        last_datapoint = None
        first_datapoint = None
        for line in log_file.readlines():
            if first_datapoint is None:
                first_datapoint = Datapoint(METRIC_NAME, line)
            last_datapoint = Datapoint(METRIC_NAME, line)
        log_file.close()
        if last_datapoint is not None and last_datapoint.time <= current_ms:
            continue
        if ((REPLAY and SEEK and
             (first_datapoint is not None) and
             (first_datapoint.time > current_ms))):
            SEEK = False
            current_ms = first_datapoint.time

        while True:
            datapoints = []
            log_file = open(QUERY_FILE, 'r')
            for line in log_file.readlines():
                pattern = ("%s ([0-9]+)" % (METRIC_NAME))
                matched = re.match(pattern, line)
                if not matched:
                    LOGGER.error("'%s' not matches '%s'", line, pattern)
                    continue
                tmp_ms = (int)(matched.group(1))
                if tmp_ms > current_ms:
                    break
                if tmp_ms < current_ms:
                    continue
                new_datapoint = Datapoint(METRIC_NAME, line)
                # Ignore the negative datapoints
                if new_datapoint.value > 0:
                    datapoints.append(new_datapoint)
            log_file.close()
            datapoints.sort(reverse=True,
                            key=lambda datapoint: datapoint.value)

            line = ("Time: %s    %d(s)    Interval: %d(s)" %
                    (date.strftime("%Y/%m/%d-%H:%M:%S"), current_ms / 1000,
                     INTERVAL_SEC))
            console_data = line + "\n"
            LOGGER.info("%s", line)
            tag_lens = {}
            value_len = len("rate")
            for datapoint in datapoints:
                value_string = ("%.2f" % datapoint.value)
                if (value_len < len(value_string)):
                    value_len = len(value_string)
                for (key, value) in datapoint.tags.items():
                    tag_found = False
                    for (tag_name, tag_len) in tag_lens.items():
                        if cmp(key, tag_name) == 0:
                            if tag_len < len(value):
                                tag_lens[key] = len(value)
                            tag_found = True
                            break
                    if not tag_found:
                        tag_lens[key] = max(len(key), len(value))

            seperator = " | "
            head = ""
            head += right_align("rate", value_len)
            head += seperator

            for (key, value) in tag_lens.items():
                head += right_align(key, value)
                head += seperator
            console_data += head + "\n"
            LOGGER.info("%s", head)
            for datapoint in datapoints:
                tmp = ("%.2f" % datapoint.value)
                line = right_align(tmp, value_len)
                line += seperator
                for (key, value) in tag_lens.items():
                    if key in datapoint.tags:
                        line += right_align(datapoint.tags[key], value)
                    else:
                        line += right_align("-", value)
                    line += seperator
                console_data += line + "\n"
                LOGGER.info("%s", line)

            former_width = 0
            former_height = 0

            timedelta = time.time() - wakeup_time
            sleep_timedelta = float(INTERVAL_SEC) - timedelta
            if (sleep_timedelta < 0):
                LOGGER.error("Query time takes too long (%f seconds)!",
                             timedelta)
                sleep_timedelta = 0.0

            LOGGER.info("Starting to sleep for %f seconds", sleep_timedelta)
            if REPLAY or not HISTORY:
                (width, height) = getTerminalSize()
                os.system('clear')
                print_to_console(console_data, width, height)
                (former_width, former_height) = (width, height)
                for i in range(0, int(sleep_timedelta)):
                    (width, height) = getTerminalSize()
                    if width != former_width or height != former_height:
                        os.system('clear')
                        print_to_console(console_data, width, height)
                        (former_width, former_height) = (width, height)
                    time.sleep(1)
                time.sleep(sleep_timedelta - int(sleep_timedelta))
                wakeup_time = time.time()
                LOGGER.info("Waked up from sleep for %f seconds",
                            sleep_timedelta)
            else:
                print console_data
            date = date + datetime.timedelta(seconds=INTERVAL_SEC)
            current_ms = current_ms + 1000 * INTERVAL_SEC
            if end_ms is not None and current_ms > end_ms:
                break
            # Try to query again if no datapoint or datapoin is too old
            if last_datapoint is None or last_datapoint.time <= current_ms:
                break


if __name__ == '__main__':
    log_setup()
    sys.exit(main(sys.argv))
