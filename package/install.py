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
graphite_url = ""

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

def create_repo(repo_name, repo_file):
	repo_path = "/etc/yum.repos.d/" + repo_name + ".repo"
	logger.debug("Repository file: '%s'" % (repo_file))
	repo_fd = open(repo_path, "w")
	line = repo_fd.write(repo_file)
	repo_fd.close()

	repolist = yum_repolist(repo_name)
	if not repolist:
		logger.error("Failed to get repolist for '%s'" % (repo_name))
		return -1
	if repolist == "0":
		logger.error("Repository '%s' is missing " % (repo_name))
		return -1
	return 0

def create_repos():
	advices = ["Current user has enough authority",
		   "Yum environment is is properly configured",
		   "Yum repository of CentOS/Redhat base is properly configured",
		   "DDN Monitoring System ISO is unbroken"]

	repo_name = "monsystem-ddn"
	repo_file = "[monsystem-ddn]\n" \
		    "name=Monitor system of DDN\n" \
		    "baseurl=file://"
	repo_file += os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	repo_file += "\n" \
		     "failovermethod=priority\n" \
		     "enabled=1\n" \
		     "gpgcheck=0\n"
	rc = create_repo(repo_name, repo_file)
	if (rc):
		logger.error("Failed to create repo '%s'" % (repo_name))
		cleanup_and_exit(rc, "yum failure", advices)

	repo_name = "elasticsearch-1.5"
	repo_file = "[elasticsearch-1.5]\n" \
		    "name=Elasticsearch repository for 1.5.x packages\n" \
		    "baseurl=http://packages.elastic.co/elasticsearch/1.5/centos\n" \
		    "gpgcheck=1\n" \
		    "gpgkey=http://packages.elastic.co/GPG-KEY-elasticsearch\n" \
		    "enabled=1"
	rc = create_repo(repo_name, repo_file)
	if (rc):
		logger.error("Failed to create repo '%s'" % (repo_name))
		cleanup_and_exit(rc, "yum failure", advices)

	# Cleanup possible wrong cache of repository data
	if (cleanup_yum_cache):
		command = "yum clean all"
		rc, stdout, stderr = run_command(command)
		if rc != 0:
			logger.error("Failed to run '%s', stdout = '%s', "
				     "rc = %d" % (command, stdout, rc))
			cleanup_and_exit(rc, "yum failure", advices)

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
				  "solve dependency? [Y/n]: ")
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

	install_rpms = ["collectd-ganglia",
			"collectd-gpfs",
			"collectd-lustre",
			"collectd-rrdtool",
			"collectd-ssh",
			"collectd-stress",
			"collectd-zabbix",
			"xml_definition",
			"elasticsearch",
			"grafana",
			"python-carbon",
			"java-1.7.0"]
	for rpm_name in install_rpms:
		command = ("yum install %s -y" % rpm_name)
		rc, stdout, stderr = run_command(command)
		if rc != 0:
			logger.error("Failed to run '%s', stdout = '%s', "
				     "stderr = '%s', rc = %d" %
				     (command, stdout, stderr, rc))
			cleanup_and_exit(-1, "yum failure", advices)

def check_url(url):
	logging.debug("Access '%s' to check URL" % (url))
	try:
		pagehandle = urllib2.urlopen(url)
	except Exception,e:
		logger.error("Failed to open URL '%s' because of '%s'" %
			     (url, e))
		return -1
	htmlSource = pagehandle.read()
	pagehandle.close()
	return 0

class watched_log():
	def __init__(self, log_name):
		self.log_name = log_name
		try:
			self.start_size = os.stat(log_name)[stat.ST_SIZE]
		except OSError:
			self.start_size = 0
	def get_new(self):
		try:
			end_size = os.stat(self.log_name)[stat.ST_SIZE]
		except OSError:
			end_size = 0
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

def service_check_status(name):
	command = ("service %s status" % (name))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.debug("Failed to run '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
	return rc == 0

def service_stop(name):
	command = ("service %s stop" % (name))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.debug("Failed to run '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
		return rc

	return rc

def service_start(name):
	command = ("service %s status" % (name))
	rc, stdout, stderr = run_command(command)
	if rc == 0:
		return 0

	command = ("service %s start" % (name))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.debug("Failed to run '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
		return rc

	rc = wait_condition(timeout, service_check_status, name)
	if rc != 0:
		logger.error("Status of service '%s' is not OK" % (name))
	return rc

def service_restart(name, timeout = 3):
	command = ("service %s restart" % (name))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
		return rc

	rc = wait_condition(timeout, service_check_status, name)
	if rc != 0:
		logger.error("Status of service '%s' is not OK" % (name))
	return rc

def service_startup_on(name):
	command = ("chkconfig %s on" % (name))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
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

# Replace origin string with dest
# dest could be a string which includes '${origin}'
# All '${origin}' will be replace by origin data
# TODO: add escape way for ${XXX}
def replace_string(origin, dest):
	new_data = ""
	last_end = 0
	pattern = "\${([^}]+)}"
	const_origin = "origin"
	for matched in re.finditer(pattern, dest, re.S|re.M):
		new_data += dest[last_end:matched.start(0)]
		if (matched.group(1) == const_origin):
			new_data += origin
		else:
			new_data += matched.group(0)
		last_end = matched.end(0)
	new_data += dest[last_end:]
	return new_data

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
			new_data += replace_string(matched.group(i),
				replacer.replace_strings[i - 1])
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
	# re.s: Makes a period (dot) match any character, including a newline.
	# re.M: Makes $ match the end of a line (not just the end of the
	#       string) and makes ^ match the start of any line (not just the
	#       start of the string).
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
		logger.debug("File '%s' has not been updated for database "
			     "configure before" % (file_name))
		if (only_check):
			return -1
		backup_file(file_name)
		logger.debug("Trying to update file '%s'" % (file_name))
		# The block of database should be lines started with #
		# This is strict so as to avoid other blocks ended with #}
		block_pattern = "#DATABASES = {\n(#[^\n]+\n)+#}\n"
		replacers = []
		replacers.append(replacer_class("^(#)", [""]))
		replacers.append(replacer_class("'NAME': '([^\n]+)',\n",
						[graphite_db]))
		replacers.append(replacer_class("('PORT': '')",
						["'PORT': '',\n        'TIMEOUT': 20"]))
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
		logger.debug("File '%s' has been updated for database "
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
	logger.debug("Creating Graphite database")
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

	logger.debug("Synd db")
	command = ("python %s syncdb" % (manage_fname))
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', "
			     "stderr = '%s', rc = %d" %
			     (command, stdout, stderr, rc))
		return rc
	logger.debug("Created Graphite database")
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

	st = os.stat(graphite_db)
	os.chmod(graphite_db, st.st_mode | stat.S_IWGRP | stat.S_IWOTH)

	service_name = "httpd"
	rc = service_restart(service_name)
	if (rc):
		logger.error("Failed to start service '%s'" %
			     (service_name))
		cleanup_and_exit(-1, "httpd failure", advices)

	httpd_error_log = "/var/log/httpd/error_log"
	httpd_graphite_access_log = "/var/log/httpd/graphite-web-access.log"
	httpd_graphite_error_log = "/var/log/httpd/graphite-web-error.log"
	graphite_exception_log = "/var/log/graphite-web/exception.log"
	graphite_info_log = "/var/log/graphite-web/info.log"
	logs = []
	logs.append(watched_log(httpd_error_log))
	logs.append(watched_log(httpd_graphite_access_log))
	logs.append(watched_log(httpd_graphite_error_log))
	logs.append(watched_log(graphite_exception_log))
	logs.append(watched_log(graphite_info_log))

	url_start = "http://"
	default_graphite_url = "http://localhost"
	prompt_message = ("Please input Graphite URL"
			  "('%s' by default): " % default_graphite_url)
	global graphite_url
	graphite_url = raw_input(prompt_message)
	if (graphite_url == ""):
		graphite_url = default_graphite_url
	elif ((len(graphite_url) < len(url_start)) or
	      (graphite_url[0:len(url_start)] != url_start)):
	      	graphite_url = url_start + graphite_url

	logger.info("Checking Graphite URL '%s'" % (graphite_url))
	rc = check_url(graphite_url)
	if rc != 0:
		logger.error("Graphite is not running correctly")
		for log in logs:
			messages = log.get_new()
			if (messages):
				logger.debug("Log '%s': '%s'" %
					     (log.log_name, messages))
		cleanup_and_exit(-1, "httpd failure", advices)

def comment_collectd_config(file_name, only_check = False):
	file = open(file_name, "r")
	data = file.read()
	file.close()

	block_pattern = "^[^#|\n][^\n]*\n"
	matched = re.search(block_pattern, data, re.S|re.M)
	if not matched:
		logger.debug("File '%s' has already been commented" %
			     (file_name))
		return 0

	if (only_check):
		return -1

	logger.info("File '%s' has some uncommented lines, commenting them" %
		    (file_name))

	backup_file(file_name)
	replacers = []
	replacers.append(replacer_class("^([^\n]+)\n", ["#${origin}"]))
	new_data = replace_block(data, block_pattern,
				 replacers)
	file = open(file_name, "w")
	file.write(new_data)
	file.close()

	return comment_collectd_config(file_name, True)

def check_update(condition_data):
	filename = condition_data[0]
	fomer_mtime = condition_data[1]
	if (not os.path.exists(filename)):
		logger.debug("File '%s' does not exist" % (filename))
		return False

	current_mtime = os.stat(filename)[stat.ST_MTIME]
	if (fomer_mtime == current_mtime):
		logger.debug("File '%s' is not updated, mtime '%s/%s'" %
			     (filename, fomer_mtime, current_mtime))
		return False

	logger.debug("File '%s' is updated, mtime '%s/%s'" %
		     (filename, fomer_mtime, current_mtime))
	return True

def wait_condition(timeout, condition_fn, condition_data):
	wait_time = 0
	while (not condition_fn(condition_data)):
		wait_time += 1
		if (wait_time > timeout):
			return -1
		time.sleep(1)
	return 0

def config_collectd():
	advices = []
	collectd_conf = "/etc/collectd.conf"
	collectd_log_file = "/var/log/collectd.log"
	edit_signature = "\n## Added by script of DDN Monitoring System\n"
	collectd_append = edit_signature
	interval = 1
	collectd_append += ("Interval     %d\n" % interval)
	collectd_append += """LoadPlugin logfile
LoadPlugin write_graphite
LoadPlugin cpu

<Plugin logfile>
  LogLevel err
"""

	collectd_append += ('  File "%s"\n' % collectd_log_file)
	collectd_append += """  Timestamp true
  PrintSeverity true
</Plugin>

<Plugin write_graphite>
  <Carbon>
    Host "localhost"
    Port "2003"
    Prefix "collectd."
    Protocol "tcp"
  </Carbon>
</Plugin>
"""

	file = open(collectd_conf, "r")
	data = file.read()
	file.close()

	matched = re.search(edit_signature, data)
	if not matched:
		logger.info("File '%s' has not been edited by DDN Monsystem "
			    "before, updating it", (collectd_conf))
		rc = comment_collectd_config(collectd_conf)
		if (rc):
			logger.error("Failed to edit Collectd settings")
			cleanup_and_exit(-1, "Collectd setting failure", advices)

		config_file = open(collectd_conf,'a')
		config_file.write(collectd_append)
		config_file.close()
	else:
		logger.info("File '%s' has already been edited by DDN "
			    "Monsystem before", (collectd_conf))

	system_log_file = "/var/log/messages"
	system_log = watched_log(system_log_file)
	collectd_log = watched_log(collectd_log_file)
	logs = []
	logs.append(system_log)
	logs.append(collectd_log)

	service_name = "carbon-aggregator"
	rc = service_restart(service_name)
	if (rc):
		logger.error("Failed to start service '%s'" %
			     (service_name))
		cleanup_and_exit(-1, "Collectd failure", advices)

	service_name = "carbon-cache"
	rc = service_restart(service_name)
	if (rc):
		logger.error("Failed to start service '%s'" %
			     (service_name))
		cleanup_and_exit(-1, "Collectd failure", advices)

	hostname = os.uname()[1]
	cabon_directory = "/var/lib/carbon/whisper/collectd"
	cpu_idle_file = (cabon_directory + "/" + hostname + "/" +
			 "cpu-0/cpu-idle.wsp")
	if (os.path.exists(cpu_idle_file)):
		fomer_mtime = os.stat(cpu_idle_file)[stat.ST_MTIME]
	else:
		fomer_mtime = "0"

	service_name = "collectd"
	rc = service_restart(service_name)
	if (rc):
		logger.error("Failed to start service '%s'" %
			     (service_name))
		for log in logs:
			messages = log.get_new()
			if (messages):
				logger.debug("Log '%s': '%s'" %
					     (log.log_name, messages))
		cleanup_and_exit(-1, "Collectd failure", advices)

	arguments = [cpu_idle_file, fomer_mtime]
	timeout = 20
	rc = wait_condition(timeout, check_update, arguments)
	if (rc):
		logger.error("File '%s' has not been updated for %d seconds" %
			     (cpu_idle_file, timeout))
		cleanup_and_exit(-1, "Collectd failure", advices)

	# Check whether there is any error messages in Collectd log
	pattern = "error"
	messages = collectd_log.get_new()
	if (messages):
		matched = re.search(pattern, messages)
		if (matched):
			logger.info("The collectd log file '%s' has some "
				    "error messages, please check whether "
				    "there is any  problem" %
				    (collectd_log_file))
			logger.debug("Log '%s': '%s'" %
				     (collectd_log.log_name, messages))

def config_grafana():
	advices = []
	grafana_httpd_conf_filename = "/etc/httpd/conf.d/grafana.conf"
	edit_signature = "\n## Added by script of DDN Monitoring System\n"
	grafana_document_root = "/usr/local/grafana/src"
	grafana_js_conf_filename = grafana_document_root + "/config.js"
	grafana_js_conf_sample_filename = grafana_document_root + "/config.sample.js"
	global graphite_url
	elasticsearch_url = "http://localhost:9200"
	grafana_js_edit_signature = "\n    // Added by script of DDN Monitoring System\n"
	grafana_js_conf = grafana_js_edit_signature
	grafana_js_conf += "    datasources: {\n"
	grafana_js_conf += "      graphite: {\n"
	grafana_js_conf += "        type: 'graphite',\n"
	grafana_js_conf += "        url: \"" + graphite_url + "\",\n"
	grafana_js_conf += "      },\n"
	grafana_js_conf += "      elasticsearch: {\n"
	grafana_js_conf += "        type: 'elasticsearch',\n"
	grafana_js_conf += "        url: \"" + elasticsearch_url + "\",\n"
	grafana_js_conf += "        index: 'grafana-dash',\n"
	grafana_js_conf += "        grafanaDB: true,\n"
	grafana_js_conf += "      }\n"
	grafana_js_conf += "    },"
	grafana_port = "8000"
	grafana_httpd_conf = edit_signature
	grafana_httpd_conf += ("<VirtualHost *:%s>\n" % grafana_port)
	grafana_httpd_conf += ("DocumentRoot %s\n" % grafana_document_root)
	grafana_httpd_conf += ("</VirtualHost>\n")
	grafana_httpd_conf += ("Listen %s\n" % grafana_port)

	need_write = True
	if (os.path.exists(grafana_httpd_conf_filename)):
		config_file = open(grafana_httpd_conf_filename, "r")
		data = config_file.read()
		config_file.close()

		matched = re.search(edit_signature, data)
		if not matched:
			logger.info("File '%s' has not been edited by DDN "
				    "Monsystem before",
				    (grafana_httpd_conf_filename))
			backup_file(grafana_httpd_conf_filename)
		else:
			logger.info("File '%s' has already been edited by DDN "
				    "Monsystem before",
				    (grafana_httpd_conf_filename))
			need_write = False
	if (need_write):
		logger.info("Writing file '%s'", (grafana_httpd_conf_filename))
		config_file = open(grafana_httpd_conf_filename, 'w')
		config_file.write(grafana_httpd_conf)
		config_file.close()

	need_write = True
	if (os.path.exists(grafana_js_conf_filename)):
		config_file = open(grafana_js_conf_filename, "r")
		data = config_file.read()
		config_file.close()

		matched = re.search(grafana_js_edit_signature, data)
		if not matched:
			logger.info("File '%s' has not been edited by DDN "
				    "Monsystem before",
				    (grafana_js_conf_filename))
			backup_file(grafana_js_conf_filename)
		else:
			logger.info("File '%s' has already been edited by DDN "
				    "Monsystem before",
				    (grafana_js_conf_filename))
			need_write = False

	if (need_write):
		shutil.copy2(grafana_js_conf_sample_filename,
			     grafana_js_conf_filename)

		config_file = open(grafana_js_conf_filename, "r")
		data = config_file.read()
		config_file.close()

		block_pattern = "  return new Settings\({\n.+  }\);\n"
		replacers = []
		replacers.append(replacer_class("(return new Settings\({)",
						["${origin}\n" +
						 grafana_js_conf]))
		new_data = replace_block(data, block_pattern,
					 replacers)
		config_file = open(grafana_js_conf_filename, "w")
		config_file.write(new_data)
		config_file.close()

	service_name = "httpd"
	rc = service_restart(service_name)
	if (rc):
		logger.error("Failed to start service '%s'" %
			     (service_name))
		cleanup_and_exit(-1, "httpd failure", advices)

	service_name = "elasticsearch"
	rc = service_restart(service_name)
	if (rc):
		logger.error("Failed to start service '%s'" %
			     (service_name))
		cleanup_and_exit(-1, "httpd failure", advices)

	httpd_error_log = "/var/log/httpd/error_log"
	logs = []
	logs.append(watched_log(httpd_error_log))

	url_start = "http://"
	default_grafana_url = "http://localhost:8000"
	prompt_message = ("Please input grafana URL"
			  "('%s' by default): " % default_grafana_url)
	global grafana_url
	grafana_url = raw_input(prompt_message)
	if (grafana_url == ""):
		grafana_url = default_grafana_url
	elif ((len(grafana_url) < len(url_start)) or
	      (grafana_url[0:len(url_start)] != url_start)):
	      	grafana_url = url_start + grafana_url

	logger.info("Checking Grafana URL '%s'" % (grafana_url))
	rc = check_url(grafana_url)
	if rc != 0:
		logger.error("Grafana is not running correctly")
		for log in logs:
			messages = log.get_new()
			if (messages):
				logger.debug("Log '%s': '%s'" %
					     (log.log_name, messages))
		cleanup_and_exit(-1, "httpd failure", advices)

	for log in logs:
		messages = log.get_new()
		if (messages):
			logger.error("Log '%s': '%s'" %
				     (log.log_name, messages))

def config_startup():
	advices = []
	services = ["httpd", "collectd", "carbon-aggregator", "carbon-cache",
		    "elasticsearch"]
	for service in services:
		rc = service_startup_on(service)
		if (rc):
			logger.error("Failed to set service '%s' startup on" %
				     (service))
			cleanup_and_exit(-1, "Service startup failure",
					 advices)

log_setup()

try:
	opts, args = getopt.getopt(sys.argv[1:], "u",["update"])
except getopt.GetoptError:
	logger.error("Wrong arguments, should be: sys.argv[0] [-u]")
	print 'sys.argv[0] [-u]'
	sys.exit(2)
for opt, arg in opts:
	if opt == '-u':
		update_rpms_anyway = True
		logger.debug("Upadate RPMs anyway")

signal.signal(signal.SIGINT, signal_hander)
signal.signal(signal.SIGTERM, signal_hander)

logger.info("Installing DDN Monsystem")

steps = []
steps.append(step("Create DDN Monsystem repositories", create_repos))
steps.append(step("Install DDN Monsystem RPMs", install_rpms))
steps.append(step("Configure Graphite", config_graphite))
steps.append(step("Configure Collectd", config_collectd))
steps.append(step("Configure Grafana", config_grafana))
steps.append(step("Configure service startup", config_startup))
current_step = 0
for tmp_step in steps:
	current_step += 1
	logger.info("====== Step %d/%d started: %s ======" % (current_step, len(steps), tmp_step.name))
	tmp_step.func()
	logger.info("====== Step %d/%d finished: %s ======" % (current_step, len(steps), tmp_step.name))
logger.info("Installation finished")
