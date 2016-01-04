/*
 * Copyright (C) 2016, DataDirect Networks, Inc.
 *
 *
 * Author: Li Xi <lixi@ddn.com>
 */

function positive_interger_valid(string) {
  if (string == "" || isNaN(string))
    return false
  var i = parseInt(string);
  if (i <= 0)
    return false
  return true
}

function nonnegative_interger_valid(string) {
  if (string == "" || isNaN(string))
    return false
  var i = parseInt(string);
  if (i < 0)
    return false
  return true
}

function datetime_unit_valid(unit){
  if (unit.length == 2) {
    if (unit == "ms")
      return true;
    else
      return false;
  } else if (unit.length == 1) {
    if (unit == "s" || unit == "m" || unit == "h" || unit == "d" ||
        unit == "w" || unit == "n"  || unit == "y")
      return true;
    else
      return false;
  } else {
    return false;
  }
}

function datetime_duration_valid(duration_string) {
  /**
   * Check whether a string is human-readable duration
   * (e.g, "10m", "3h", "14d").
   * Formats supported:
   * ms: milliseconds
   * s: seconds
   * m: minutes
   * h: hours
   * d: days
   * w: weeks
   * n: month (30 days)
   * y: years (365 days)
   */
  if (duration_string.length < 2) {
    /* Should have a unit */
    return false;
  } else if (duration_string.length == 2 ||
  	     (duration_string.slice(-2) != "ms")) {
    return positive_interger_valid(duration_string.slice(0, -1)) &&
           datetime_unit_valid(duration_string.slice(-1));
  } else {
    return positive_interger_valid(duration_string.slice(0, -2));
  }
}

function year_valid(year_string) {
  if (year_string.length != 4) {
    return false;
  }
  return positive_interger_valid(year_string); 
}

function month_valid(month_string) {
  if (month_string.length != 2 ||
      isNaN(month_string)) {
    return false;
  }
  var month = parseInt(month_string);
  if (month < 1 || month > 12) {
    return false;
  }
  return true;
}

function day_valid(day_string) {
  if (day_string.length != 2 ||
      isNaN(day_string)) {
    return false;
  }
  var day = parseInt(day_string);
  /* Simple check, not considering leap month and so on */
  if (day < 1 || day > 31) {
    return false;
  }
  return true;
}

function hour_valid(hour_string) {
  if (hour_string.length != 2 ||
      isNaN(hour_string)) {
    return false;
  }
  var hour = parseInt(hour_string);
  /* Simple check, not considering leap month and so on */
  if (hour < 0 || hour > 23) {
    return false;
  }
  return true;
}

function minite_second_valid(minute_string) {
  if (minute_string.length != 2 ||
      isNaN(minute_string)) {
    return false;
  }
  var minute = parseInt(minute_string);
  /* Simple check, not considering leap month and so on */
  if (minute < 0 || minute > 59) {
    return false;
  }
  return true;
}

function absolute_date_valid(datetime_string) {
  switch (datetime_string.length) {
  case 19:
    if (datetime_string.slice(16, 17) != ":")
      return false;
    var second = datetime_string.slice(17, 19);
    if (!minite_second_valid(second))
      return false;
  case 16:
    if (datetime_string.slice(10, 11) != "-" &&
        datetime_string.slice(10, 11) != " ")
      return false;
    if (datetime_string.slice(13, 14) != ":")
      return false;
    var hour = datetime_string.slice(11, 13);
    if (!hour_valid(hour))
      return false;
    var minute = datetime_string.slice(14, 16);
    if (!minite_second_valid(hour))
      return false;
  case 10:
    if (datetime_string.slice(4, 5) != "/" ||
        datetime_string.slice(7, 8) != "/")
      return false;
    var year = datetime_string.slice(0, 4);
    var month = datetime_string.slice(5, 7);
    var day = datetime_string.slice(8, 10);
    return year_valid(year) && month_valid(month) && day_valid(day);
    break;
  default:
    return false;
  }
}

function datetime_valid(datetime_string) {
  /**
   * Relative: 5m-ago, 1h-ago, etc.
   * Absolute human readable dates:
   * "yyyy/MM/dd-HH:mm:ss"
   * "yyyy/MM/dd HH:mm:ss"
   * "yyyy/MM/dd-HH:mm"
   * "yyyy/MM/dd HH:mm"
   * "yyyy/MM/dd"
   * Unix Timestamp in seconds or milliseconds:
   * 1355961600
   * 1355961600000
   * 1355961600.000
   */
  if (datetime_string.slice(-4) == "-ago") {
    return datetime_duration_valid(datetime_string.slice(0, -4));
  } else if (datetime_string.indexOf("/") != -1 ||
  	     datetime_string.indexOf(":") != -1) {
    return absolute_date_valid(datetime_string);
  } else if (datetime_string.length == 10 ||
  	     datetime_string.length == 13) {
    return positive_interger_valid(datetime_string);
  } else if (datetime_string.length == 14 &&
  	     datetime_string.slice(10, 11) == '.') {
    console.log(datetime_string.slice(0, 10));
    console.log(datetime_string.slice(11, 14));
    return positive_interger_valid(datetime_string.slice(0, 10)) && 
           nonnegative_interger_valid(datetime_string.slice(11, 14));
  }
  return false;
}

function topn_valid(topn_string) {
  return positive_interger_valid(topn_string);
}

function metric_valid(metric_string) {
  if (metric_string == "")
    return false;
  return true;
}

function tags_valid(query_tags_string) {
  if (query_tags_string == "")
    return false;
  tag_array = query_tags_string.split(",");
  for (var i = 0; i < tag_array.length; i++) {
    key_value = tag_array[i].split("=");
    if (key_value.length != 2)
      return false;
    else if (key_value[0] == "" || key_value[1] == "")
      return false;
  }
  return true;
}

function opentsdb_url_valid(opentsdb_url_string) {
  if (opentsdb_url_string.slice(0, 7) != "http://" &&
      opentsdb_url_string.slice(0, 8) != "http://")
    return false;
  return true;
}

function flush_interval_valid(flush_interval_string) {
  return nonnegative_interger_valid(flush_interval_string);
}

var default_start = "1m-ago"
var default_topn = "10";
var default_metric = "ost_jobstats_samples";
var default_tags = "optype=write_samples";
var default_flush_interval = "3";

function get_valid_start(start_string) {
  start = start_string;
  start = start.replace(/%2F/g, "/");
  start = start.replace(/\+/g, " ");
  start = start.replace(/%3A/g, ":");
  if (!datetime_valid(start)) {
    alert("Invalid start time \"" + start + "\" use \"" + default_start +
          "\" instead");
    start = default_start;
  }
  return start;
}

function get_valid_topn(topn_string) {
  topn = topn_string;
  if (!topn_valid(topn)) {
    alert("Invalid topn \"" + topn + "\" use \"" + default_topn +
          "\" instead");
    topn = default_topn;
  }
  return topn;
}

function get_valid_metric(metric_string) {
  metric = metric_string;
  if (!metric_valid(metric)) {
    alert("Invalid metric \"" + metric + "\" use \"" + default_metric +
          "\" instead");
    metric = default_metric;
  }

  return metric;
}

function get_valid_tags(tags_string) {
  query_tags = tags_string;
  query_tags = query_tags.replace(/%3D/g,"=");
  query_tags = query_tags.replace(/%2C/g,",");
  if (!tags_valid(query_tags)) {
    alert("Invalid tags \"" + query_tags + "\" use \"" + default_tags +
          "\" instead");
    query_tags = default_tags;
  }

  return query_tags;
}

function get_valid_opentsdb_url(opentsdb_url_string) {
  opentsdb_url = opentsdb_url_string;
  opentsdb_url = opentsdb_url.replace(/%3A/g,":");
  opentsdb_url = opentsdb_url.replace(/%2F/g,"/");
  if (!opentsdb_url_valid(opentsdb_url)) {
    default_opentsdb_url = top.window.location.protocol + "//" +
                           top.window.location.hostname + ":4242";
    alert("Invalid openTSDB URL \"" + opentsdb_url + "\" use \"" +
          default_opentsdb_url + "\" instead");
    opentsdb_url = default_opentsdb_url;
  }
  return opentsdb_url;
}

function get_valid_flush_interval(flush_interval_string) {
  flush_interval = flush_interval_string;
  if (!flush_interval_valid(flush_interval)) {
    alert("Invalid flush interval \"" + flush_interval + "\" use \"" +
          default_flush_interval + "\" instead");
    flush_interval = default_flush_interval;
  }
  return flush_interval;
}
