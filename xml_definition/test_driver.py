#!/usr/bin/python2
from os import path
import glob
import logging
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

class Collectd:
	def __init__(self, conf, pid):
		self.pid = pid
		subprocess.check_call(["collectd", "-C", conf, "-P", self.pid],
				      stdout = sys.stdout.fileno(),
				      stderr = sys.stderr.fileno())

	def stop(self):
		os.kill(int(open(self.pid, 'r').read().strip()), signal.SIGTERM)

def parse_rrd(rrd):
	tree = ET.fromstring(
		subprocess.check_output(["rrdtool", "dump", rrd],
					stderr = sys.stderr.fileno()))

	return tree.find("ds").find("last_ds").text.strip().split('.')[0]

def check_result(logger, dmission, tests):
	failures = 0
	missings = 0
	successes = 0

	for test in tests.findall("test"):
		test_path = test.find("path").text
		test_pattern = test.find("pattern").text
		failed = False
		succeeded = False

		for rrd in glob.iglob(path.join(dmission, test_path)):
			content = parse_rrd(rrd)
			match = re.match(test_pattern, content)
			if match == None or match.end(0) != len(content):
				logger.info("FAIL: rrdtool file: '%s', Got: '%s', Expected '%s'" %
					    (rrd, content, test_pattern))
				failed = True
			elif not failed:
				succeeded = True

		if succeeded:
			successes += 1
		elif failed:
			failures += 1
		else:
			logger.info("MISSING: rrdtool file '%s' does not exist" %
				    test_path)
			missings += 1

	return failures, missings, successes

def generate_test_names(tests):
	for test in tests.findall("test"):
		yield test.find("name").text

def iterate_preset(preset):
	for child in preset:
		if child.tag == "definition":
			definition = child.text
		elif child.tag == "content":
			content = child.text
		elif child.tag == "tests":
			tests = child.text

	return (definition, content, tests)

def mkconf(conf, interval, host, log, data, definition, root, types):
	file = open(conf, 'w')

	file.write("""Interval %d
Hostname "%s"

LoadPlugin logfile
<Plugin logfile>
	Loglevel info
	File "%s"
</Plugin>

LoadPlugin rrdtool
<Plugin rrdtool>
Datadir "%s"
</Plugin>

LoadPlugin filedata
<Plugin filedata>
	<Common>
		DefinitionFile "%s"
		Rootpath "%s"
	</Common>
""" % (interval, host, log, data, definition, root))

	for type in types:
		file.write("""	<Item>
		Type "%s"
	</Item>
""" % type)

	file.write("</Plugin>\n")
	file.close()

def parse_inputs():
	level = None
	preset = None
	preset_directory = None
	definition = None
	content = None
	tests = None

	for arg in sys.argv[1:]:
		if arg == "DEBUG":
			level = logging.DEBUG
		elif arg == "INFO":
			level = logging.INFO
		elif arg == "WARNING":
			level = logging.WARNING
		elif arg == "ERROR":
			level = logging.ERROR
		elif arg == "CRITICAL":
			level = logging.CRITICAL
		elif os.path.isdir(arg):
			content = arg
		else:
			root = ET.parse(arg).getroot()
			if root.tag == "preset":
				preset = root
				preset_directory = path.dirname(arg)
			elif root.tag == "definition":
				definition = arg
			elif root.tag == "tests":
				tests = root

	if preset != None:
		preset_definition, preset_content, preset_tests = \
			iterate_preset(preset)

		if definition == None:
			definition = \
				path.join(preset_directory, preset_definition)

		if content == None:
			content = path.join(preset_directory, preset_content)

		if tests == None:
			tests = ET.parse(
				path.join(preset_directory, preset_tests)
			).getroot()

	return (level, definition, content, tests)

def print_usage():
	print """usage:
	%s LOGLEVEL PRESET [CONTENT] [DEFINITION] [TESTS]
	%s LOGLEVEL CONTENT DEFINITION TESTS

LOGLEVEL:   DEBUG, INFO, WARNING, ERROR or CRITICAL
PRESET:     preset of content, definition, and tests
CONTENT:    virtual root directory
DEFINITION: filedata definition
TESTS:      XML containing test cases

The order of arguments does not matter.""" % (sys.argv[0], sys.argv[0])

def run():
	host = "collection"
	interval = 1

	def receive_signal(signum, stack):
		collectd.stop()

	logger = logging.getLogger()
	logger.addHandler(logging.StreamHandler())

	try:
		level, definition, content, tests = parse_inputs()
	except:
		print_usage()
		raise

	if level != None:
		logger.setLevel(level)

	if definition == None or content == None or tests == None:
		print_usage()

	dtemp = tempfile.mkdtemp()
	logger.info("working in %s", dtemp)
	logger.info("investigate and then delete the directory after running tests")

	pid = path.join(dtemp, "collectd.pid")
	conf = path.join(dtemp, "collectd.conf")
	log = path.join(dtemp, "collectd.log")

	mkconf(conf, interval, host, log, dtemp,
	       definition, path.abspath(content), generate_test_names(tests))

	signal.signal(signal.SIGINT, receive_signal)
	signal.signal(signal.SIGTERM, receive_signal)
	collectd = Collectd(conf, pid)

	# Let's wait for collectd to get the desired metrics.
	time.sleep(interval * 2 + 3)
	collectd.stop()
	failures, missings, successes = check_result(logger, dtemp, tests)

	logger.error("total %d, failed: %d, missing: %d, success: %d" %
		     (failures + missings + successes,
                      failures, missings, successes))
	if failures or missings:
		sys.exit(1)

run()
