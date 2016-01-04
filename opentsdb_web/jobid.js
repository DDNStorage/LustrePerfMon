/*
 * Copyright (C) 2016, DataDirect Networks, Inc.
 *
 *
 * Author: Li Xi <lixi@ddn.com>
 */

var start = default_start;
var topn = default_topn;
var metric = default_metric;
var query_tags = default_tags;
var opentsdb_url = "http://ddnlab.imwork.net:4242";
var flush_interval = default_flush_interval;
var show_func = function() {
  alert("No show function defined");
};

function check_all() {
  var flush_obj = document.getElementById("flush");
  var start_obj = document.getElementById("start");
  var topn_obj = document.getElementById("topn");
  var metric_obj = document.getElementById("metric");
  var tags_obj = document.getElementById("tags");
  var opentsdb_url_obj = document.getElementById("opentsdb_url");
  var flush_interval_obj = document.getElementById("flush_interval");
  var all_passed = true;

  start = start_obj.value;
  if (!datetime_valid(start)) {
    all_passed = false;
    start_obj.style.background = "yellow";
  } else {
    start_obj.style.background = "white";
  }

  topn = topn_obj.value;
  if (!topn_valid(topn)) {
    all_passed = false;
    topn_obj.style.background = "yellow";
  } else {
    topn_obj.style.background = "white";
  }

  metric = metric_obj.value;
  if (!metric_valid(metric)) {
    all_passed = false;
    metric_obj.style.background = "yellow";
  } else {
    metric_obj.style.background = "white";
  }

  query_tags = tags_obj.value;
  if (!tags_valid(query_tags)) {
    all_passed = false;
    tags_obj.style.background = "yellow";
  } else {
    tags_obj.style.background = "white";
  }

  opentsdb_url = opentsdb_url_obj.value;
  if (!opentsdb_url_valid(opentsdb_url)) {
    all_passed = false;
    opentsdb_url_obj.style.background = "yellow";
  } else {
    opentsdb_url_obj.style.background = "white";
  }

  flush_interval = flush_interval_obj.value;
  if (!flush_interval_valid(flush_interval)) {
    all_passed = false;
    flush_interval_obj.style.background = "yellow";
  } else {
    flush_interval_obj.style.background = "white";
    var interval = parseInt(flush_interval);
    if (interval > 0)
      window.setInterval('submit_form();', interval * 1000);
  }

  if (all_passed)
    flush_obj.disabled = false;
  else
    flush_obj.disabled = true;
  return all_passed;
}

function submit_form()
{
  var focusedElement = document.activeElement;
  if (focusedElement.id != "start" &&
      focusedElement.id != "opentsdb_url" &&
      focusedElement.id != "topn" &&
      focusedElement.id != "metric" &&
      focusedElement.id != "tags" &&
      focusedElement.id != "flush_interval" &&
      check_all())
    document.input.submit();
}

function set_values()
{
  var flush_obj = document.getElementById("flush");
  var start_obj = document.getElementById("start");
  var topn_obj = document.getElementById("topn");
  var metric_obj = document.getElementById("metric");
  var tags_obj = document.getElementById("tags");
  var opentsdb_url_obj = document.getElementById("opentsdb_url");
  var flush_interval_obj = document.getElementById("flush_interval");

  start_obj.value = start;
  topn_obj.value = topn;
  metric_obj.value = metric;
  tags_obj.value = query_tags;
  opentsdb_url_obj.value = opentsdb_url;
  flush_interval_obj.value = flush_interval;
  var interval = parseInt(flush_interval);
  if (interval > 0)
    window.setInterval('submit_form();', interval * 1000);
  flush_obj.focus();
}

function jobid_control($scope, $http)
{
  var url = top.window.location.href;
  var arg_hash = [];
  var args = url.split("?");
  var str = args[1];
  if (str == null)
    str = "start=" + default_start + "&topn=" + default_topn;
  args = str.split("&");
  for(var i = 0; i < args.length; i++) {
    str = args[i];
    var arg = str.split("=");
    switch (arg[0]) {
    case "start":
      start = get_valid_start(arg[1]);
      break;
    case "topn":
      topn = get_valid_topn(arg[1]);
      break;
    case "metric":
      metric = get_valid_metric(arg[1]);
      break;
    case "tags":
      query_tags = get_valid_tags(arg[1]);
      break;
    case "opentsdb_url":
      opentsdb_url = get_valid_opentsdb_url(arg[1]);
      break;
    case "flush_interval":
      flush_interval = get_valid_flush_interval(arg[1]);
      break;
    default:
      alert("Unknown option: \"" + arg[0] + "=\"" + arg[1]);
      break;
    }
  }
  set_values();

  var options = {
    method: 'GET',
    url: opentsdb_url + '/api/query/gexp' + '?start=' +
         start + '&exp=highestCurrent(sum:rate:' + metric + '{' + query_tags +
         ',job_id=*},' + topn + ')'
  };

  $http(options).success(function(response) {
    show_func(response);
  }).error(function(response) {
    $scope.error = response.error;
  });
}

document.write("<form name='input' method='get'>");
document.write("OpenTSDB URL:<input type='text' name='opentsdb_url' id='opentsdb_url' oninput='check_all();'/>");
document.write("Start Time:<input type='text' name='start' id='start' oninput='check_all();'/>");
document.write("Topn Number:<input type='text' name='topn' id='topn' oninput='check_all();'/>");
document.write("Metric Name:<input type='text' name='metric' id='metric' oninput='check_all();'/>");
document.write("Tags Expression:<input type='text' name='tags' id='tags' oninput='check_all();'/>");
document.write("Flush Interval:<input type='text' name='flush_interval' id='flush_interval' oninput='check_all();'/>");
document.write("<input type='submit' value='Flush' id = 'flush'/>");
document.write("</form>");
document.write("<div ng-app='myApp' ng-controller='customersCtrl'/>");
