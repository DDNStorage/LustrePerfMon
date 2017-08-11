# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com

"""
Library for daemon process
"""
import logging

SHUTTING_DOWN = False
EXIT_REASON = "unkown reason"

def signal_handler(signum, frame):
    """
    Singal hander
    """
    # pylint: disable=unused-argument,global-statement
    global SHUTTING_DOWN, EXIT_REASON
    SHUTTING_DOWN = True
    EXIT_REASON = "got signal %d" % signum
    logging.error("exiting because %s", EXIT_REASON)
