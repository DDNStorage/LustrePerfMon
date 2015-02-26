#!/usr/bin/python
import sys
import os
import signal
import getopt
import shutil
import logging
import datetime
import subprocess
import re
import time
import inspect
import urllib2
import stat
import datetime

tmp_dir = "/tmp"
log_filename = tmp_dir + "/" + "install_DDN_monitor.log"
# Whether to cleanup yum cache before trying to install RPMs
cleanup_yum_cache = False
update_rpms_anyway = False

def log_setup():
	global logger
	global log_filename
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	log_file = logging.FileHandler(log_filename)
	logger.addHandler(log_file)
	formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
	log_file.setLevel(logging.DEBUG)
	log_file.setFormatter(formatter)

	log_stream = logging.StreamHandler(sys.stdout)
	log_stream.setLevel(logging.INFO)
	logger.addHandler(log_stream)

def run_command(command, dump_debug = True):
	p = subprocess.Popen(command,
			     shell = True,
			     stdout = subprocess.PIPE,
			     stderr = subprocess.PIPE)
	rc = p.wait()
	stdout=""
	for line in p.stdout.readlines():
		stdout = stdout + line;
	stderr=""
	for line in p.stderr.readlines():
		stderr = stderr + line;
	if (dump_debug):
		logger.debug("Run command '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
	return rc, stdout, stderr

def yum_repolist(repo):
	command = "yum repolist " + repo
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', rc = %d" %
			     (command, stdout, rc))
		return None
	lines = stdout.split("\n")
	if (len(lines) < 2):
		logger.error("Output '%s' of command '%s' is unexpected" %
			     (stdout, command))
		return None
	last_line = lines[-2]
	pattern = r"repolist: (\d+)"
	matched = re.match(pattern, last_line)
	if not matched:
		logger.error("Output '%s' does not match pattern '%s'" %
			     (last_line, pattern))
		return None
	return matched.group(1)

def cleanup_and_exit(rc, failure = "some unexpected failure", advices = []):
	logger.error("Aborting because of %s" % failure)
	logger.error("Please check log '%s' for more information" % log_filename)
	if (advices):
		logger.error("Before trying again, please make sure:")
		for advice in advices:
			logger.error("\t* %s", advice)
	sys.exit(rc)

def signal_hander(signum, stack):
	if (signum == signal.SIGINT):
		logger.error("Aborting because of keyboard interrupt")
	elif (signum == signal.SIGTERM):
		logger.error("Aborting because of being killed")
	else:
		logger.error("Aborting because %d" % signum)
	logger.error("Please check log '%s' for more information" % log_filename)
	raise SystemExit()

class step():
	def __init__(self, name, func):
		self.name = name
		self.func = func

def create_repo():
	advices = ["Current user has enough authority",
		   "Yum environment is is properly configured",
		   "Yum repository of CentOS/Redhat base is properly configured",
		   "DDN Monitoring System ISO is unbroken"]

	ddn_monsystem_repo_path = "/etc/yum.repos.d/monsystem-ddn.repo"
	repo_file = "[monsystem-ddn]\n" \
		    "name=Monitor system of DDN\n" \
		    "baseurl=file://"
	repo_file += os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	repo_file += "\n" \
		     "failovermethod=priority\n" \
		     "enabled=1\n" \
		     "gpgcheck=0\n"
	logger.debug("Repository file: '%s'" % (repo_file))
	repo_fd = open(ddn_monsystem_repo_path, "w")
	line = repo_fd.write(repo_file)
	repo_fd.close()

	# Cleanup possible wrong cache of repository data
	if (cleanup_yum_cache):
		command = "yum clean all"
		rc, stdout, stderr = run_command(command)
		if rc != 0:
			logger.error("Failed to run '%s', stdout = '%s', "
				     "rc = %d" % (command, stdout, rc))
			cleanup_and_exit(rc, "yum failure", advices)

	repo = "monsystem-ddn"
	repolist = yum_repolist(repo)
	if not repolist:
		logger.error("Failed to get repolist for '%s'" % (repo))
		cleanup_and_exit(-1, "yum failure", advices)
	if repolist == "0":
		logger.error("Repository '%s' is missing " % (repo))
		cleanup_and_exit(-1, "missing monsystem-ddn repositoy", advices)

def rpm_erase(rpm_name, prompt_depend = True):
	command = ("rpm -e %s" % rpm_name)
	rc, stdout, stderr = run_command(command)
	if (rc == 0):
		return 0

	uninstalled = ("error: package %s is not installed" % rpm_name)
	if (stderr[:len(uninstalled)] == uninstalled):
		logger.debug("RPM '%s' is not installed, skipping" %
			     (rpm_name))
		return 0

	dependency_error = "error: Failed dependencies:\n"
	if (stderr[:len(dependency_error)] != dependency_error):
		logger.error("Command '%s' failed because of unknown error, "
			     "stdout = '%s', stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
		return -1

	depend_rpms = []
	for line in stderr[len(dependency_error):].splitlines(True):
		pattern = r".+ is needed by \(installed\) (.+)\n$"
		matched = re.match(pattern, line)
		if not matched:
			logger.error("Do not understand dependency '%s', ignoring", (line))
			continue
		depend_rpms.append(matched.group(1))

	logger.info("Can't uninstall RPM '%s' directly "
		    "because it is needed by following RPM(s):" %
		    (rpm_name))
	for depend_rpm in depend_rpms:
		logger.info("	%s", depend_rpm)
	if (prompt_depend):
		prompt_message = ("Uninstall these RPMs to "
				  "solve dependency? [Y/n]:")
		uninstall = raw_input(prompt_message)
		if (uninstall != "" and
		    (uninstall[0] == "N" or
		     uninstall[0] == "n")):
		    	logger.info("Abort uninstallation of RPM '%s' "
		    		    "because of user's command" %
				    (rpm_name))
			return -1

	# Got permission to erase depend RPMs
	for depend_rpm in depend_rpms:
		rc = rpm_erase(depend_rpm, prompt_depend)
		if (rc):
			logger.error("Failed to uninstall RPM '%s'" %
				     (depend_rpm))
			return rc

	# All depend RPMs should have been uninstalled, try uninstall again
	command = ("rpm -e %s" % rpm_name)
	rc, stdout, stderr = run_command(command)
	if (rc):
		logger.error("Command '%s' failed, "
			     "stdout = '%s', stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
	return rc

def install_rpms():
	advices = ["Current user has enough authority",
		   "Yum environment is is properly configured",
		   "Yum repository of CentOS/Redhat base is properly configured",
		   "DDN Monitoring System ISO is unbroken"]

	# Erase existing collectd RPMs so as to update them
	erase_rpms = ["collectd", "libcollectdclient", "xml_definition"]
	if (update_rpms_anyway):
		for rpm_name in erase_rpms:
			rc = rpm_erase(rpm_name, True)
			if rc != 0:
				logger.error("Failed to uninstall RPM '%s'" %
					     (rpm_name))
				cleanup_and_exit(-1, "RPM failure", advices)

	install_rpms = ["collectd-lustre",
			"collectd-gpfs",
			"collectd-stress",
			"collectd-ganglia",
			"collectd-zabbix",
			"collectd-rrdtool",
			"xml_definition",
			"grafana",
			"montools",
			"elasticsearch"]
	for rpm_name in install_rpms:
		command = ("yum install %s -y" % rpm_name)
		rc, stdout, stderr = run_command(command)
		if rc != 0:
			logger.error("Failed to run '%s', stdout = '%s', rc = %d" %
				     (command, stdout, rc))
			cleanup_and_exit(-1, "yum failure", advices)

def check_graphite(url):
	logging.debug("Access '%s' to check Graphite website" % (url))
	try:
		pagehandle = urllib2.urlopen(url)
	except Exception,e:
		logger.error("Failed to open website '%s' because of '%s'" %
			     (url, e))
		return -1
	htmlSource = pagehandle.read()
	pagehandle.close()
	return 0

class watched_log():
	def __init__(self, log_name):
		self.log_name = log_name
		self.start_size = os.stat(log_name)[stat.ST_SIZE]
	def get_new(self):
		end_size = os.stat(self.log_name)[stat.ST_SIZE]
		if (end_size < self.start_size):
			self.start_size = end_size
			logger.debug("Log '%s' has been truncated" %
				     (self.log_name))
		elif (end_size == self.start_size):
			logger.debug("Log '%s' has not updated" %
				     (self.log_name))
			return None
		file = open(self.log_name, 'r')
		file.seek(self.start_size)
		messages = ""
		for line in file.readlines():
			messages += line
		file.close()
		return messages

def start_service(name):
	command = ("service %s status" % (name))
	rc, stdout, stderr = run_command(command)
	if rc == 0:
		return 0

	command = ("service %s start" % (name))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', "
			     "rc = %d" % (command, stdout, rc))
		return rc

	command = ("service %s status" % (name))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', "
			     "rc = %d" % (command, stdout, rc))
		return rc
	return rc

def backup_file(src):
	dst = src
	dst += datetime.datetime.now().strftime("_%Y-%m-%d_%H:%M:%S.%f")
	shutil.copy2(src, dst)
	logger.error("File '%s' has been backuped as '%s'" % (src, dst))

class replacer_class():
	def __init__(self, pattern, replace_strings):
		self.pattern = pattern
		self.replace_strings = replace_strings

def replace_pattern(data, replacer):
	new_data = ""
	last_end = 0
	# re.s: Makes a period (dot) match any character, including a newline.
	# re.M: Makes $ match the end of a line (not just the end of the
	#       string) and makes ^ match the start of any line (not just the
	#       start of the string).
	for matched in re.finditer(replacer.pattern, data, re.S|re.M):
		groups = matched.groups()
		group_num = len(groups)
		if (group_num !=
		    len(replacer.replace_strings)):
			logger.error("Pattern '%s' conflicts with "
				     "replace strings '%s', ignored" %
				     (replacer.pattern,
				      replacer.replace_strings))
			continue

		new_data += data[last_end:matched.start(0)]
		last_end = matched.start(0)
		for i in range(1, group_num + 1):
			logger.debug("Replace [%d, %d] of '%s' with '%s'" %
				     (matched.start(i), matched.end(i),
				      data,
				      replacer.replace_strings[i - 1]))
			new_data += data[last_end:matched.start(i)]
			new_data += replacer.replace_strings[i - 1]
			last_end = matched.end(i)
	new_data += data[last_end:]
	return new_data

def replace_patterns(data, replacers):
	new_data = data
	for replacer in replacers:
		new_data = replace_pattern(new_data, replacer)
	logger.debug("String '%s' has been replace to '%s'" %
		     (data, new_data))
	return new_data

# Replace a regular expression in a block
def replace_block(data, block_pattern, replacers = []):
	new_data = ""
	last_end = 0
	for matched in re.finditer(block_pattern, data, re.S|re.M):
		new_data += data[last_end:matched.start(0)]
		new_data += replace_patterns(matched.group(0), replacers)
		last_end = matched.end(0)
	new_data += data[last_end:]

	return new_data

# TODO: Replace block start/end with regular expression too
# TODO: Do not need to split into lines before matching block
# Find a regular expression in a block
# Returns a re.MatchObject
def match_block(data, block_start, block_end, pattern):
	started = False
	for line in data.splitlines(True):
		if (line == block_start):
			started = True
			matched = re.search(pattern, line)
			if matched:
				return matched
		elif (started):
			matched = re.search(pattern, line)
			if matched:
				return matched
			if (line == block_end):
				started = False
	if (started):
		logger.error("Block '%s ... %s' starts but never end', "
			     "error ignored" % (block_start, block_end))

	return None

def edit_graphite_config(file_name, graphite_db, only_check = False):
	file = open(file_name, "r")
	data = file.read()
	file.close()

	# First of all check whether config file has been edited correctly
	block_start = "DATABASES = {\n"
	block_end = "}\n"
	matched = match_block(data, block_start, block_end,
			      "'NAME': '(.+)',")
	if (not matched):
		logger.info("File '%s' has not been updated for database "
			    "configure before" % (file_name))
		if (only_check):
			return -1
		backup_file(file_name)
		logger.info("Trying to update file '%s'" % (file_name))
		# The block of database should be lines started with #
		# This is strict so as to avoid other blocks ended with #}
		block_pattern = "#DATABASES = {\n(#[^\n]+\n)+#}\n"
		replacers = []
		replacers.append(replacer_class("^(#)", [""]))
		replacers.append(replacer_class("'NAME': '([^\n]+)',\n",
						[graphite_db]))
		new_data = replace_block(data, block_pattern,
					 replacers)
		file = open(file_name, "w")
		file.write(new_data)
		file.close()
		rc = edit_graphite_config(file_name, graphite_db, True)
		if (rc):
			logger.error("Failed to update file '%s' correctly" %
				     (file_name))
			return -1
	elif (matched.group(1) != graphite_db):
		logger.info("File '%s' has been updated before, "
			    "but Graphite DB is '%s' not '%s' " %
			    (file_name, matched.group(1), graphite_db))
		if (only_check):
			return -1
		backup_file(file_name)
		logger.info("Trying to correct database configure of '%s'" %
			    (file_name))
		rc = edit_graphite_config(file_name, graphite_db, True)
		if (rc):
			logger.error("Failed to correct database configure "
				     "of '%s'" % (file_name))
			return -1
	# Do not print verbose message when check finds no error
	if (not only_check):
		logger.info("File '%s' has been updated for database "
			    "configure" % (file_name))
	return 0

def rpm_file_list(rpm_name):
	command = ("rpm -ql %s" % rpm_name)
	rc, stdout, stderr = run_command(command, False)
	if rc != 0:
		logger.error("Failed to get file list of RPM '%s'" %
			     (rpm_name))
		return rc, None
	return rc, stdout.splitlines(False)

def create_graphite_database():
	rpm_name = "graphite-web"
	rc, file_list = rpm_file_list(rpm_name)
	if (rc):
		return rc
	desired_fname = "graphite/manage.py"
	manage_fname = ""
	for filename in file_list:
		if filename[-len(desired_fname):] == desired_fname:
			manage_fname = filename
	if manage_fname == "":
		logger.error("Failed to find file '%s' in RPM '%s'" %
			     (desired_fname, rpm_name))
		return -1

	command = ("python %s syncdb" % (manage_fname))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
		return rc
	return 0

def config_graphite():
	advices = ["Httpd is properly configured"]

	graphite_db = "/var/lib/graphite-web/graphite.db"
	graphite_conf = "/etc/graphite-web/local_settings.py"
	rc = edit_graphite_config(graphite_conf, graphite_db)
	if (rc):
		logger.error("Failed to edit Graphite settings")
		cleanup_and_exit(-1, "Graphite setting failure", advices)

	rc = create_graphite_database()
	if (rc):
		logger.error("Failed to create Graphite database")
		cleanup_and_exit(-1, "Graphite database failure", advices)

	service_name = "httpd"
	rc = start_service(service_name)
	if (rc):
		logger.error("Failed to start service '%s'" %
			     (service_name))
		cleanup_and_exit(-1, "httpd failure", advices)

	httpd_graphite_access_log = "/var/log/httpd/graphite-web-access.log"
	httpd_graphite_error_log = "/var/log/httpd/graphite-web-error.log"
	graphite_exception_log = "/var/log/graphite-web/exception.log"
	graphite_info_log = "/var/log/graphite-web/info.log"
	logs = []
	logs.append(watched_log(httpd_graphite_access_log))
	logs.append(watched_log(httpd_graphite_error_log))
	logs.append(watched_log(graphite_exception_log))
	logs.append(watched_log(graphite_info_log))

	rc = check_graphite("http://localhost")
	if rc != 0:
		logger.error("Graphite is not running correctly")
		for log in logs:
			messages = log.get_new()
			if (messages):
				logger.debug("Log '%s': '%s'" %
					     (log.log_name, messages))
		cleanup_and_exit(-1, "httpd failure", advices)

log_setup()

signal.signal(signal.SIGINT, signal_hander)
signal.signal(signal.SIGTERM, signal_hander)

logger.info("Installing DDN Monsystem")

steps = []
steps.append(step("Create DDN Monsystem repository", create_repo))
steps.append(step("Install DDN Monsystem RPMs", install_rpms))
steps.append(step("Configure Graphite", config_graphite))
current_step = 0
for tmp_step in steps:
	current_step += 1
	logger.info("====== Step %d/%d started: %s ======" % (current_step, len(steps), tmp_step.name))
	tmp_step.func()
	logger.info("====== Step %d/%d finished: %s ======" % (current_step, len(steps), tmp_step.name))
logger.info("Installation finished")
