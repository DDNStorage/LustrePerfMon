# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Time utility library
"""
import datetime
import dateutil.tz


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
