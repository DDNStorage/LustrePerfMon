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

tmp_dir = "/tmp"
log_filename = tmp_dir + "/" + "install_DDN_monitor.log"

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

def run_command(command):
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
	logger.debug("Run command '%s', stdout = '%s', stderr = '%s', rc = %d" %
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

def cleanup_and_exit(rc, failure = "some unexpected failure"):
	logger.error("Aborting because of %s" % failure)
	logger.error("Please check log '%s' for more information" % log_filename)
	logger.error("Before trying again, please make sure:")
	logger.error("\t* Current user has enough authority;")
	logger.error("\t* Yum environment is is properly configured;")
	logger.error("\t* Yum repository of CentOS/Redhat base is properly "
		     "configured;")
	logger.error("\t* DDN Monitoring System is unbroken.")
	sys.exit(rc)

log_setup()

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
	command = "yum clean all"
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', rc = %d" %
			     (command, stdout, rc))
		cleanup_and_exit(rc, "yum failure")

	repo = "monsystem-ddn"
	repolist = yum_repolist(repo)
	if not repolist:
		logger.error("Failed to get repolist for '%s'" % (repo))
		cleanup_and_exit(-1, "yum failure")
	if repolist == "0":
		logger.error("Repository '%s' is missing " % (repo))
		cleanup_and_exit(-1, "missing monsystem-ddn repositoy")

def install_rpms():
	command = "yum install montools grafana elasticsearch -y"
	rc, stdout, stderr = run_command(command)
	if rc != 0:
		logger.error("Failed to run '%s', stdout = '%s', rc = %d" %
			     (command, stdout, rc))
		cleanup_and_exit(-1, "yum failure")

signal.signal(signal.SIGINT, signal_hander)
signal.signal(signal.SIGTERM, signal_hander)

logger.info("Installing DDN Monsystem")

steps = []
steps.append(step("Create DDN Monsystem repository", create_repo))
steps.append(step("Install DDN Monsystem RPM", install_rpms))
current_step = 0
for tmp_step in steps:
	current_step += 1
	logger.info("====== Step %d/%d started: %s ======" % (current_step, len(steps), tmp_step.name))
	tmp_step.func()
	logger.info("====== Step %d/%d finished: %s ======" % (current_step, len(steps), tmp_step.name))

logger.info("Installation finished")
