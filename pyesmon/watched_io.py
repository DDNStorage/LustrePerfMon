# Copyright (c) 2016 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Wathed IO is an file IO which will call callbacks when reading/writing from/to
the file
"""

import io
import os
import logging
import traceback

# local libs
from pyesmon import utils


def watched_io_open(fname, func, args):
    """Open watched IO file.
    Codes copied from io.py
    """
    if not isinstance(fname, (basestring, int)):
        raise TypeError("invalid file: %r" % fname)
    mode = "w"
    raw = io.FileIO(fname, mode)
    buffering = io.DEFAULT_BUFFER_SIZE
    try:
        blksize = os.fstat(raw.fileno()).st_blksize
    except (os.error, AttributeError):
        pass
    else:
        if blksize > 1:
            buffering = blksize
    buffer_writer = io.BufferedWriter(raw, buffering)
    text = WatchedIO(buffer_writer, fname, func, args)
    return text


class WatchedIO(io.TextIOWrapper):
    """
    WatchedIO object
    The func will be called when writting to the file
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, buffered_io, fname, func, args):
        super(WatchedIO, self).__init__(buffered_io)
        self.wi_check_time = utils.utcnow()
        self.wi_func = func
        self.wi_args = args
        self.wi_fname = fname

    def write(self, data):
        """
        Need unicode() otherwise will hit problem:
        TypeError: can't write str to text stream
        And also, even the encoding should be utf-8
        there will be some error, so need to ignore it.
        """
        #pylint: disable=bare-except
        self.wi_check_time = utils.utcnow()
        data = unicode(data, encoding='utf-8', errors='ignore')
        try:
            super(WatchedIO, self).write(data)
        except:
            logging.error("failed to write the file [%s]: %s",
                          self.wi_fname, traceback.format_exc())
        self.wi_func(self.wi_args, data)


def log_watcher_debug(args, new_log):
    """
    Watch log dump to logging.debug
    """
    if len(new_log) == 0:
        return
    logging.debug("log from host [%s]: [%s]",
                  args["hostname"], new_log)


def log_watcher_info(args, new_log):
    """
    Watch log dump to logging.info
    """
    if len(new_log) == 0:
        return
    logging.info("log from host [%s]: [%s]",
                 args["hostname"], new_log)


def log_watcher_error(args, new_log):
    """
    Watch log dump to logging.error
    """
    if len(new_log) == 0:
        return
    logging.error("log from host [%s]: [%s]",
                  args["hostname"], new_log)
