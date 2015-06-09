#!/usr/bin/python
import sys
import os
import time
import tempfile
import signal
import getopt
import shutil
import logging
import datetime
from string import Template
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

hostname = os.uname()[1].split('.')[0]
tmp_dir = "/tmp"
PID = ("%d" % (os.getpid()))
mission_dir = (tmp_dir + "/monitor_PID-" +
	       PID + "_" +
	       datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f"))
pid_file = mission_dir + "/" + "collectd.pid"
collectd_conf = mission_dir + "/" + "collectd.conf"
collectd_log = mission_dir + "/" + "collectd.log"
log_file = mission_dir + "/" + "test.log"
xml_path = ""
collectd_interval = 1
exit_on_error = 0
failure_number = 0

def log_setup():
	global logger
	global log_file
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	log_file = logging.FileHandler(log_file)
	logger.addHandler(log_file)
	formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
	log_file.setFormatter(formatter)

	log_stream = logging.StreamHandler(sys.stdout)
	logger.addHandler(log_stream)
	log_stream.setFormatter(formatter)

def environment_setup():
	if mission_dir == "/":
		logger.error("Improper directory '%s' is used" %
			     (mission_dir))
		sys.exit(1)
	if os.path.exists(mission_dir):
		shutil.rmtree(mission_dir, True)
	os.makedirs(mission_dir, 0755)
	log_setup()

def collectd_stop():
	if os.path.exists(pid_file):
		pf = open(pid_file, 'r')
		pid = int(pf.read().strip())
		os.kill(pid, signal.SIGTERM)

def receive_signal(signum, stack):
	collectd_stop()

def failure_record():
	global failure_number
	failure_number += 1
	if exit_on_error == 1:
		collectd_stop()
		sys.exit(1)

usages = [
	"Help messages:",
	"	-h/--help",
	"	--debug print debug log",
	"	--exit_on_error exit if error happens",
	"	--xml_path specify lustre definition xml path",
]
def print_usages(ret):
	for line in usages:
		print line
	sys.exit(ret)

def parse_args():
	global xml_path
	try:
		options, args = getopt.getopt(sys.argv[1:], "hp:i:",
					      ["help", "xml_path=",
					      "exit_on_error", "debug"])
	except getopt.GetoptError:
		print_usages(1)
	for name, value in options:
		if name in ("-h", "--help"):
			print_usages(0)
		if name in ("--exit_on_error"):
			exit_on_error = 1
		if name in ("--xml_path"):
			xml_path = value
			if os.path.isfile(xml_path) == False:
				logger.error("Wrong XML argument '%s'" %
					     (xml_path))
				sys.exit(1)
		if name in ("--debug"):
			logger.setLevel(logging.DEBUG)
	if xml_path == "" :
		logger.error("Please specify xml_path argument")
		sys.exit(1)

environment_setup()
# parse agrs here to make config_head_lines assignment happy.
parse_args()

signal.signal(signal.SIGINT, receive_signal)
signal.signal(signal.SIGTERM, receive_signal)

config_head_lines = [
	"Interval " + str(collectd_interval),
	"LoadPlugin logfile",
	"<Plugin logfile>",
	"	Loglevel info",
	"	File " + '"' + collectd_log + '"',
	"</Plugin>",
	"LoadPlugin rrdtool",
	"<Plugin rrdtool>",
	"	Datadir " + '"' + mission_dir + '"',
	"</Plugin>",
	"LoadPlugin lustre",
	'<Plugin "lustre">',
	"	<Common>",
	"		DefinitionFile " + '"' + xml_path + '"',
	"		Rootpath " + '"' + mission_dir + '"',
	"	</Common>"
]

def is_exe(fpath):
	return (os.path.isfile(fpath) and
		os.access(fpath, os.X_OK))

def which(program):
    fpath, test_name = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return "None"

required_commands = [
	"collectd",
	"rrdtool",
]

def check_commands():
	for command in required_commands:
		logger.debug("Checking whether command '%s' exists" %
			     (command))
		if which(command) == "None":
			logger.error("Command '%s' not found" % (command))
			sys.exit(1)

# this shoud be same for all rrd file?
def parse_rrd(rrdfile):
	dump_file = mission_dir + "/rrd.dump"
	os.system("rrdtool dump %s > %s" % (rrdfile, dump_file))
	per = ET.parse(dump_file)
	p = per.find("/ds")
	for x in p:
		if x.tag == "last_ds":
			break
	if (x.tag != "last_ds"):
		logger.error("The last data point of '%s' is missing" %
			     (rrdfile))
		sys.exit(1)
	num = x.text.strip()
	return num.split('.')[0]

# generate collectd config according to test suite file
def generate_collectd_conf(test_file):
	tree = ET.parse(test_file)
	logger.debug("Generating configure file '%s' for test %s" %
		     (collectd_conf, test_file))
	# Enable all items by parsing XML file
	f = open(collectd_conf, 'w')
	for line in config_head_lines:
		f.write(line + "\n")
	for atype in tree.findall("entry"):
		for btype in atype.findall("item"):
			name = btype.find('name').text
			f.write("\t<Item>\n")
			f.write("\t\tType %s\n" % ('"' + name + '"'))
			f.write("\t</Item>\n")
	f.write("</Plugin>\n")
	f.close()

def generate_proc(test_file):
	tree = ET.parse(test_file)
	for atype in tree.findall("entry"):
		content_path = atype.find('content_path').text
		content_type = atype.find('content_type').text
		content = atype.find('content').text
		content_path = mission_dir + "/" + content_path
		if not os.path.exists(content_path):
			os.makedirs(os.path.dirname(content_path), 0755)
		if content_type == "external":
			shutil.copy2((os.path.dirname(test_file) + "/" +
				      content), content_path)
		else:
			logger.error("Inline data is not supported yet" %
				     (rrdfile))
			sys.exit(1)

def check_collected_result(test_file):
	tree = ET.parse(test_file)
	for atype in tree.findall("entry"):
		for btype in atype.findall("item"):
			data_path = Template(btype.find('data_path').text)
			data_path = data_path.substitute(hostname=hostname)
			data_value = btype.find('data_value').text
			rrdfile = mission_dir + "/" + data_path
			if not os.path.exists(rrdfile):
				logger.info("FAIL: rrdtool file '%s' does "
					    "not exist" % (rrdfile))
				failure_record()
				continue
			content = parse_rrd(rrdfile)
			if content == data_value:
				logger.info("PASS: rrdtool file '%s', "
					    "Got '%s'" %
					    (rrdfile, data_value))
			else:
				logger.info("FAIL: rrdtool file: '%s', "
					    "Got: '%s', Expected '%s'" %
					    (rrdfile, content, data_value))
				failure_record()

def collectd_start():
	command = ("collectd -C %s -P %s" % (collectd_conf, pid_file))
	logger.debug("Starting collectd, command is '%s'" % (command))
	rc = os.system(command)
	if rc != 0:
		logger.error("Failed to start collectd, command is '%s', "
			     "rc = %d" % (command, rc))
		sys.exit(1)

def iterate_all_tests(rootdir):
	for dirName, subdirList, fileList in os.walk(rootdir):
		for test_name in fileList:
			if test_name.endswith(".xml") != True:
				continue
			test_path = dirName + "/" + test_name
			logger.debug("Running test of '%s'" % (test_path))
			generate_collectd_conf(test_path)
			generate_proc(test_path)
			collectd_start()
			# Let's wait for collectd to get the desired metrics.
			time.sleep(collectd_interval * 2 + 3)
			collectd_stop()
			check_collected_result(test_path)

check_commands()
iterate_all_tests(os.getcwd() + "/tests/" + os.path.basename(xml_path))
if (failure_number):
	logger.error("Failed %d test suit(s)" % (failure_number))
	sys.exit(1)
