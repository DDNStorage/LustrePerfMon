#!/usr/bin/python
"""This script installs DDN monitoring system"""
import sys
import os
import signal
import getopt
import shutil
import logging
import subprocess
import re
import time
import inspect
import urllib2
import stat
import datetime

TMP_DIR = "/tmp"
LOG_FILENAME = TMP_DIR + "/" + "install_DDN_monitor.log"
# Whether to cleanup yum cache before trying to install RPMs
UPDATE_RPMS_ANYWAY = False
GRAPHITE_URL = ""
BASE_REPOSITORY = ""
EPEL_REPOSITORY = ""
ELASTICSEARCH_RPM = ""
LOGGER = logging.getLogger()


def log_setup():
    """Setup the log, should be called as earlier as possible"""
    LOGGER.setLevel(logging.DEBUG)

    log_file = logging.FileHandler(LOG_FILENAME)
    LOGGER.addHandler(log_file)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(formatter)

    log_stream = logging.StreamHandler(sys.stdout)
    log_stream.setLevel(logging.INFO)
    LOGGER.addHandler(log_stream)


def run_command(command, dump_debug=True):
    """ Run shell command """
    process = subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    ret = process.wait()
    stdout = ""
    for line in process.stdout.readlines():
        stdout = stdout + line
    stderr = ""
    for line in process.stderr.readlines():
        stderr = stderr + line
    if dump_debug:
        LOGGER.debug("Run command '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
    return ret, stdout, stderr


def yum_repository():
    """ Get the repository list by runing 'yum repolist' command.
        A list of repositories will be returned. """
    command = "yum repolist"
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.error("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
        return None

    pattern = r"repo id +repo name +status\n(.+)\nrepolist: .+\n"
    matched = re.search(pattern, stdout, re.S | re.M)
    if not matched:
        LOGGER.error("Output '%s' does not match pattern '%s'", stdout,
                     pattern)
        return None
    lines = matched.group(1).split("\n")
    return lines


def cleanup_and_exit(ret, failure="some unexpected failure", advices=None):
    """ Print out some messages and exit. """
    LOGGER.error("Aborting because of %s", failure)
    LOGGER.error("Please check log '%s' for more information", LOG_FILENAME)
    if not advices is None:
        LOGGER.error("Before trying again, please make sure:")
        for advice in advices:
            LOGGER.error("\t* %s", advice)
    sys.exit(ret)


def signal_hander(signum):
    """ Signal hander that print proper messages when existing. """
    if signum == signal.SIGINT:
        LOGGER.error("Aborting because of keyboard interrupt")
    elif signum == signal.SIGTERM:
        LOGGER.error("Aborting because of being killed")
    else:
        LOGGER.error("Aborting because %d", signum)
    LOGGER.error("Please check log '%s' for more information", LOG_FILENAME)
    raise SystemExit()


def write_file(path, content):
    """ Write content to a file. """
    LOGGER.debug("Writing file '%s': '%s'", path, content)
    newfile = open(path, "w")
    newfile.write(content)
    newfile.close()
    return 0


def create_repo_monsystem(repo_list):
    """ Create yum repository of DDN monitoring system. """
    repo_name = "monsystem-ddn"
    repo_path = "/etc/yum.repos.d/monsystem-ddn.repo"
    found = False
    for repo in repo_list:
        if cmp(repo[0:len(repo_name)], repo_name) == 0:
            found = True
            break
    if found is True:
        LOGGER.debug("Found repository '%s' skiping creation of it",
                     repo_name)
    else:
        repo_content = "[monsystem-ddn]\n" \
                       "name=Monitor system of DDN\n" \
                       "baseurl=file://"
        repo_content += os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        repo_content += "\n" \
                        "failovermethod=priority\n" \
                        "enabled=1\n" \
                        "gpgcheck=0\n"
        ret = write_file(repo_path, repo_content)
        if ret:
            return ret
    return 0


def create_repo_elasticsearch(repo_list):
    """ Create yum repository of elasticsearch. """
    if ELASTICSEARCH_RPM == "":
        repo_name = "elasticsearch-1.5"
        repo_path = "/etc/yum.repos.d/elasticsearch-1.5-ddn.repo"
        found = False
        for repo in repo_list:
            if cmp(repo[0:len(repo_name)], repo_name) == 0:
                found = True
                break
        if found is True:
            LOGGER.debug("Found repository '%s' skiping creation of it",
                         repo_name)
        else:
            repo_content = ("[elasticsearch-1.5]\n"
                            "name=Elasticsearch repository for 1.5.x "
                            "packages\n"
                            "baseurl=http://packages.elastic.co/elasticsearch/"
                            "1.5/centos\n"
                            "gpgcheck=1\n"
                            "gpgkey=http://packages.elastic.co/"
                            "GPG-KEY-elasticsearch\n"
                            "enabled=1")
            ret = write_file(repo_path, repo_content)
            if ret:
                return ret
    return 0


def create_repo_base(repo_list):
    """ Create yum repository of CentOS-base. """
    if BASE_REPOSITORY != "":
        repo_name = "base"
        found = False
        for repo in repo_list:
            if cmp(repo[0:len(repo_name)], repo_name) == 0:
                found = True
                break
        repo_path = "/etc/yum.repos.d/CentOS-base-ddn.repo"
        if found is True and not os.path.exists(repo_path):
            advices = ["Current CentOS base repository is removed"]
            LOGGER.error("Found repository '%s', please remove it to use "
                         "local repository", repo_name)
            cleanup_and_exit(-1, "yum failure", advices)
        else:
            repo_content = ("[base]\n"
                            "name=CentOS-$releasever - Base\n"
                            "baseurl=file://%s\n"
                            "gpgcheck=1\n"
                            "enabled=1\n"
                            "gpgkey=file://%s/RPM-GPG-KEY-CentOS-6" %
                            (BASE_REPOSITORY, BASE_REPOSITORY))
            ret = write_file(repo_path, repo_content)
            if ret:
                return ret
    return 0


def create_repo_epel(repo_list):
    """ Create yum repository of EPEL. """
    if EPEL_REPOSITORY != "":
        repo_name = "epel"

        found = False
        for repo in repo_list:
            if cmp(repo[0:len(repo_name)], repo_name) == 0:
                found = True
                break
        repo_path = "/etc/yum.repos.d/epel-ddn.repo"
        if found and not os.path.exists(repo_path):
            advices = ["Current EPEL repository is removed"]
            LOGGER.error("Found repository '%s', please remove it "
                         "to use local repository", repo_name)
            cleanup_and_exit(-1, "yum failure", advices)
        else:
            repo_content = ("[epel]\n"
                            "name=Extra Packages for Enterprise Linux 6 - "
                            "$basearch\n"
                            "baseurl=file://%s\n"
                            "gpgcheck=0\n"
                            "enabled=1\n" %
                            (EPEL_REPOSITORY))
            ret = write_file(repo_path, repo_content)
            if ret:
                return ret
    return 0


def create_repos():
    """ Create yum repositories. """
    advices = ["Current user has enough authority",
               "Yum environment is is properly configured",
               "Yum repository of CentOS/Redhat base is properly configured",
               "DDN Monitoring System ISO is unbroken"]

    repo_list = yum_repository()
    if repo_list is None:
        LOGGER.error("Failed to check repolist")
        cleanup_and_exit(-1, "yum failure", advices)

    ret = create_repo_monsystem(repo_list)
    if ret:
        LOGGER.error("Failed to create repository of DDN monitorings system")
        cleanup_and_exit(ret, "yum failure", advices)

    ret = create_repo_elasticsearch(repo_list)
    if ret:
        LOGGER.error("Failed to create repository of elasticsearch")
        cleanup_and_exit(ret, "yum failure", advices)

    ret = create_repo_base(repo_list)
    if ret:
        LOGGER.error("Failed to create repository of CentOS-base")
        cleanup_and_exit(ret, "yum failure", advices)

    ret = create_repo_epel(repo_list)
    if ret:
        LOGGER.error("Failed to create repository of EPEL")
        cleanup_and_exit(ret, "yum failure", advices)

    # Cleanup possible wrong cache of repository data
    command = "yum clean all"
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.error("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
        cleanup_and_exit(ret, "yum failure", advices)


def rpm_erase(rpm_name, prompt_depend=True):
    """ Erase the given RPM, erase the RPMs depends on the given RPM too if
    necessary. """
    command = ("rpm -e %s" % rpm_name)
    ret, stdout, stderr = run_command(command)
    if ret == 0:
        return 0

    uninstalled = ("error: package %s is not installed" % rpm_name)
    if stderr[:len(uninstalled)] == uninstalled:
        LOGGER.debug("RPM '%s' is not installed, skipping", rpm_name)
        return 0

    dependency_error = "error: Failed dependencies:\n"
    if stderr[:len(dependency_error)] != dependency_error:
        LOGGER.error("Command '%s' failed because of unknown error, "
                     "stdout = '%s', stderr = '%s', ret = %d", command,
                     stdout, stderr, ret)
        return -1

    depend_rpms = []
    for line in stderr[len(dependency_error):].splitlines(True):
        pattern = r".+ is needed by \(installed\) (.+)\n$"
        matched = re.match(pattern, line)
        if not matched:
            LOGGER.error("Do not understand dependency '%s', ignoring", line)
            continue
        depend_rpms.append(matched.group(1))

    LOGGER.info("Can't uninstall RPM '%s' directly because it is needed by "
                "following RPM(s):", rpm_name)
    for depend_rpm in depend_rpms:
        LOGGER.info("    %s", depend_rpm)
    if prompt_depend:
        prompt_message = ("Uninstall these RPMs to "
                          "solve dependency? [Y/n]: ")
        uninstall = raw_input(prompt_message)
        if uninstall != "" and (uninstall[0] == "N" or uninstall[0] == "n"):
            LOGGER.info("Abort uninstallation of RPM '%s' because of user's "
                        "command", rpm_name)
            return -1

    # Got permission to erase depend RPMs
    for depend_rpm in depend_rpms:
        ret = rpm_erase(depend_rpm, prompt_depend)
        if ret:
            LOGGER.error("Failed to uninstall RPM '%s'", depend_rpm)
            return ret

    # All depend RPMs should have been uninstalled, try uninstall again
    command = ("rpm -e %s" % rpm_name)
    ret, stdout, stderr = run_command(command)
    if ret:
        LOGGER.error("Command '%s' failed, stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
    return ret


def install_rpms():
    """ Install RPMs either through YUM or RPM. """
    advices = ["Current user has enough authority",
               "Yum environment is is properly configured",
               "Yum repository of CentOS/Redhat base is properly configured",
               "DDN Monitoring System ISO is unbroken"]

    # Erase existing collectd RPMs so as to update them
    rpms = ["collectd", "libcollectdclient", "xml_definition"]
    if UPDATE_RPMS_ANYWAY:
        for rpm_name in rpms:
            ret = rpm_erase(rpm_name, True)
            if ret != 0:
                LOGGER.error("Failed to uninstall RPM '%s'", rpm_name)
                cleanup_and_exit(-1, "RPM failure", advices)

    rpms = ["ganglia",
            "collectd-ganglia",
            "collectd-gpfs",
            "collectd-lustre",
            "collectd-rrdtool",
            "collectd-ssh",
            "collectd-stress",
            "collectd-zabbix",
            "xml_definition",
            "grafana",
            "python-carbon",
            "java-1.7.0"]
    if ELASTICSEARCH_RPM == "":
        rpms.append("elasticsearch")
    else:
        command = ("rpm -qi elasticsearch")
        ret, stdout, stderr = run_command(command)
        if ret != 0:
            LOGGER.debug("elasticsearch RPM is not installed, installing")
            command = ("rpm -ivh %s" % (ELASTICSEARCH_RPM))
            ret, stdout, stderr = run_command(command)
            if ret != 0:
                LOGGER.error("Failed to run '%s', stdout = '%s', "
                             "stderr = '%s', ret = %d", command, stdout,
                             stderr, ret)
                cleanup_and_exit(ret, "rpm failure", advices)
    for rpm_name in rpms:
        command = ("yum install %s -y" % rpm_name)
        ret, stdout, stderr = run_command(command)
        if ret != 0:
            LOGGER.error("Failed to run '%s', stdout = '%s', stderr = '%s', "
                         "ret = %d", command, stdout, stderr, ret)
            cleanup_and_exit(-1, "yum failure", advices)


def check_url(url):
    """ Check whether URL is accessable. """
    logging.debug("Access '%s' to check URL", url)
    try:
        pagehandle = urllib2.urlopen(url)
    except Exception, error:
        LOGGER.error("Failed to open URL '%s' because of '%s'", url, error)
        return -1
    html_source = pagehandle.read()
    LOGGER.debug("URL '%s': '%s'", url, html_source)
    pagehandle.close()
    return 0


class WatchedLog(object):
    """ Watch and get the updates of a log file. """
    def __init__(self, log_name):
        self.log_name = log_name
        try:
            self.start_size = os.stat(log_name)[stat.ST_SIZE]
        except OSError:
            self.start_size = 0

    def get_new(self):
        """ Return new log since last dump. """
        try:
            end_size = os.stat(self.log_name)[stat.ST_SIZE]
        except OSError:
            end_size = 0
        if end_size < self.start_size:
            self.start_size = end_size
            LOGGER.debug("Log '%s' has been truncated", self.log_name)
        elif end_size == self.start_size:
            LOGGER.debug("Log '%s' has not updated", self.log_name)
            return None
        log_file = open(self.log_name, 'r')
        log_file.seek(self.start_size)
        messages = ""
        for line in log_file.readlines():
            messages += line
        log_file.close()
        return messages


def service_check_status(name):
    """ Check the status of a serivce. """
    command = ("service %s status" % (name))
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.debug("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
    return ret == 0


def service_stop(name):
    """ Stop a service. """
    command = ("service %s stop" % (name))
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.debug("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
        return ret

    return ret


def service_start(name):
    """ Start a service. """
    command = ("service %s status" % (name))
    ret, stdout, stderr = run_command(command)
    if ret == 0:
        return 0

    command = ("service %s start" % (name))
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.debug("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
        return ret

    timeout = 20
    ret = wait_condition(timeout, service_check_status, name)
    if ret != 0:
        LOGGER.error("Status of service '%s' is not OK", name)
    return ret


def service_restart(name, timeout=10):
    """ Restart a service. """
    command = ("service %s restart" % (name))
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.error("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
        return ret

    ret = wait_condition(timeout, service_check_status, name)
    if ret != 0:
        LOGGER.error("Status of service '%s' is not OK", name)
    return ret


def service_startup_on(name):
    """ Enable the startup of a service. """
    command = ("chkconfig %s on" % (name))
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.error("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
        return ret
    return ret


def backup_file(src):
    """ Backuo file to a name with a timestamp. """
    dst = src
    dst += datetime.datetime.now().strftime("_%Y-%m-%d_%H:%M:%S.%f")
    shutil.copy2(src, dst)
    LOGGER.error("File '%s' has been backuped as '%s'", src, dst)


class Replacer(object):
    """ Replace class. """
    def __init__(self, pattern, replace_strings):
        self.pattern = pattern
        self.replace_strings = replace_strings


def replace_string(origin, dest):
    """ Replace origin string with dest. dest could be a string which includes
        '${origin}. All '${origin}' will be replace by origin data.
        TODO: add escape way for ${XXX}. """
    new_data = ""
    last_end = 0
    pattern = r"\${([^}]+)}"
    const_origin = "origin"
    for matched in re.finditer(pattern, dest, re.S | re.M):
        new_data += dest[last_end:matched.start(0)]
        if matched.group(1) == const_origin:
            new_data += origin
        else:
            new_data += matched.group(0)
        last_end = matched.end(0)
    new_data += dest[last_end:]
    return new_data


def replace_pattern(data, replacer):
    """ Replace the pattern in a string. """
    new_data = ""
    last_end = 0
    # re.s: Makes a period (dot) match any character, including a newline.
    # re.M: Makes $ match the end of a line (not just the end of the
    #       string) and makes ^ match the start of any line (not just the
    #       start of the string).
    for matched in re.finditer(replacer.pattern, data, re.S | re.M):
        groups = matched.groups()
        group_num = len(groups)
        if group_num != len(replacer.replace_strings):
            LOGGER.error("Pattern '%s' conflicts with replace strings '%s', "
                         "ignored", replacer.pattern,
                         replacer.replace_strings)
            continue

        new_data += data[last_end:matched.start(0)]
        last_end = matched.start(0)
        for i in range(1, group_num + 1):
            LOGGER.debug("Replace [%d, %d] of '%s' with '%s'",
                         matched.start(i), matched.end(i), data,
                         replacer.replace_strings[i - 1])
            new_data += data[last_end:matched.start(i)]
            new_data += replace_string(matched.group(i),
                                       replacer.replace_strings[i - 1])
            last_end = matched.end(i)
    new_data += data[last_end:]
    return new_data


def replace_patterns(data, replacers):
    """ Replace patterns in a string. """
    new_data = data
    for replacer in replacers:
        new_data = replace_pattern(new_data, replacer)
    LOGGER.debug("String '%s' has been replace to '%s'", data, new_data)
    return new_data


def replace_block(data, block_pattern, replacers=None):
    """ Replace patterns in a matched block of a string. """
    new_data = ""
    last_end = 0
    # re.s: Makes a period (dot) match any character, including a newline.
    # re.M: Makes $ match the end of a line (not just the end of the
    #       string) and makes ^ match the start of any line (not just the
    #       start of the string).
    for matched in re.finditer(block_pattern, data, re.S | re.M):
        new_data += data[last_end:matched.start(0)]
        new_data += replace_patterns(matched.group(0), replacers)
        last_end = matched.end(0)
    new_data += data[last_end:]

    return new_data


def match_block(data, block_start, block_end, pattern):
    """ Find a regular expression in a block, and returns a re.MatchObject
        TODO: Replace block start/end with regular expression too
        TODO: Do not need to split into lines before matching block """
    started = False
    for line in data.splitlines(True):
        if line == block_start:
            started = True
            matched = re.search(pattern, line)
            if matched:
                return matched
        elif started:
            matched = re.search(pattern, line)
            if matched:
                return matched
            if line == block_end:
                started = False
    if started:
        LOGGER.error("Block '%s ... %s' starts but never end', error ignored",
                     block_start, block_end)

    return None


def edit_graphite_config(file_name, graphite_db, only_check=False):
    """ Edit Graphite configure file. """
    config_file = open(file_name, "r")
    data = config_file.read()
    config_file.close()

    # First of all check whether config file has been edited correctly
    block_start = "DATABASES = {\n"
    block_end = "}\n"
    matched = match_block(data, block_start, block_end,
                          "'NAME': '(.+)',")
    if not matched:
        LOGGER.debug("File '%s' has not been updated for database configure "
                     "before", (file_name))
        if only_check:
            return -1
        backup_file(file_name)
        LOGGER.debug("Trying to update file '%s'", file_name)
        # The block of database should be lines started with #
        # This is strict so as to avoid other blocks ended with #}
        block_pattern = "#DATABASES = {\n(#[^\n]+\n)+#}\n"
        replacers = []
        replacers.append(Replacer("^(#)", [""]))
        replacers.append(Replacer("'NAME': '([^\n]+)',\n",
                                  [graphite_db]))
        timeout_string = "'PORT': '',\n        'TIMEOUT': 20"
        replacers.append(Replacer("('PORT': '')",
                                  [timeout_string]))
        new_data = replace_block(data, block_pattern,
                                 replacers)
        config_file = open(file_name, "w")
        config_file.write(new_data)
        config_file.close()
        ret = edit_graphite_config(file_name, graphite_db, True)
        if ret:
            LOGGER.error("Failed to update file '%s' correctly", file_name)
            return -1
    elif matched.group(1) != graphite_db:
        LOGGER.info("File '%s' has been updated before, but Graphite DB is "
                    "'%s' not '%s' ", file_name, matched.group(1),
                    graphite_db)
        if only_check:
            return -1
        backup_file(file_name)
        LOGGER.info("Trying to correct database configure of '%s'", file_name)
        ret = edit_graphite_config(file_name, graphite_db, True)
        if ret:
            LOGGER.error("Failed to correct database configure "
                         "of '%s'", file_name)
            return -1
    # Do not print verbose message when check finds no error
    if not only_check:
        LOGGER.debug("File '%s' has been updated for database "
                     "configure", file_name)
    return 0


def rpm_file_list(rpm_name):
    """ Get the file list of a RPM. """
    command = ("rpm -ql %s" % rpm_name)
    ret, stdout, stderr = run_command(command, False)
    if ret != 0:
        LOGGER.error("Failed to get file list of RPM '%s', stdout = '%s', "
                     "stderr = '%s', ret = %d", stdout, stderr, ret, rpm_name)
        return ret, None
    return ret, stdout.splitlines(False)


def create_graphite_database():
    """ Create Graphite database. """
    LOGGER.debug("Creating Graphite database")
    rpm_name = "graphite-web"
    ret, file_list = rpm_file_list(rpm_name)
    if ret:
        return ret
    desired_fname = "graphite/manage.py"
    manage_fname = ""
    for filename in file_list:
        if filename[-len(desired_fname):] == desired_fname:
            manage_fname = filename
    if manage_fname == "":
        LOGGER.error("Failed to find file '%s' in RPM '%s'", desired_fname,
                     rpm_name)
        return -1

    LOGGER.debug("Synd db")
    command = ("python %s syncdb" % (manage_fname))
    ret, stdout, stderr = run_command(command)
    if ret != 0:
        LOGGER.error("Failed to run '%s', stdout = '%s', stderr = '%s', "
                     "ret = %d", command, stdout, stderr, ret)
        return ret
    LOGGER.debug("Created Graphite database")
    return 0


def config_graphite():
    """ Configure Graphite. """
    advices = ["Httpd is properly configured"]

    graphite_db = "/var/lib/graphite-web/graphite.db"
    graphite_conf = "/etc/graphite-web/local_settings.py"

    ret = edit_graphite_config(graphite_conf, graphite_db)
    if ret:
        LOGGER.error("Failed to edit Graphite settings")
        cleanup_and_exit(-1, "Graphite setting failure", advices)

    ret = create_graphite_database()
    if ret:
        LOGGER.error("Failed to create Graphite database")
        cleanup_and_exit(-1, "Graphite database failure", advices)

    db_stat = os.stat(graphite_db)
    os.chmod(graphite_db, db_stat.st_mode | stat.S_IWGRP | stat.S_IWOTH)

    service_name = "httpd"
    ret = service_restart(service_name)
    if ret:
        LOGGER.error("Failed to start service '%s'", service_name)
        cleanup_and_exit(-1, "httpd failure", advices)

    httpd_error_log = "/var/log/httpd/error_log"
    httpd_graphite_access_log = "/var/log/httpd/graphite-web-access.log"
    httpd_graphite_error_log = "/var/log/httpd/graphite-web-error.log"
    graphite_exception_log = "/var/log/graphite-web/exception.log"
    graphite_info_log = "/var/log/graphite-web/info.log"
    logs = []
    logs.append(WatchedLog(httpd_error_log))
    logs.append(WatchedLog(httpd_graphite_access_log))
    logs.append(WatchedLog(httpd_graphite_error_log))
    logs.append(WatchedLog(graphite_exception_log))
    logs.append(WatchedLog(graphite_info_log))

    url_start = "http://"
    default_graohite_url = "http://localhost"
    prompt_message = ("Please input Graphite URL"
                      "('%s' by default): " % default_graohite_url)
    global GRAPHITE_URL
    GRAPHITE_URL = raw_input(prompt_message)
    if GRAPHITE_URL == "":
        GRAPHITE_URL = default_graohite_url
    elif ((len(GRAPHITE_URL) < len(url_start)) or
          (GRAPHITE_URL[0:len(url_start)] != url_start)):
        GRAPHITE_URL = url_start + GRAPHITE_URL

    LOGGER.info("Checking Graphite URL '%s'", GRAPHITE_URL)
    ret = check_url(GRAPHITE_URL)
    if ret != 0:
        LOGGER.error("Graphite is not running correctly")
        for log in logs:
            messages = log.get_new()
            if messages:
                LOGGER.debug("Log '%s': '%s'", log.log_name, messages)
        cleanup_and_exit(-1, "httpd failure", advices)


def comment_collectd_config(file_name, only_check=False):
    """ Commet all the lines in a collect configure file. """
    config_file = open(file_name, "r")
    data = config_file.read()
    config_file.close()

    block_pattern = "^[^#|\n][^\n]*\n"
    matched = re.search(block_pattern, data, re.S | re.M)
    if not matched:
        LOGGER.debug("File '%s' has already been commented", file_name)
        return 0

    if only_check:
        return -1

    LOGGER.info("File '%s' has some uncommented lines, commenting them",
                file_name)

    backup_file(file_name)
    replacers = []
    replacers.append(Replacer("^([^\n]+)\n", ["#${origin}"]))
    new_data = replace_block(data, block_pattern,
                             replacers)
    config_file = open(file_name, "w")
    config_file.write(new_data)
    config_file.close()

    return comment_collectd_config(file_name, True)


def check_update(condition_data):
    """ Check whether a file is updated. """
    filename = condition_data[0]
    fomer_mtime = condition_data[1]
    if not os.path.exists(filename):
        LOGGER.debug("File '%s' does not exist", filename)
        return False

    current_mtime = os.stat(filename)[stat.ST_MTIME]
    if fomer_mtime == current_mtime:
        LOGGER.debug("File '%s' is not updated, mtime '%s/%s'", filename,
                     fomer_mtime, current_mtime)
        return False

    LOGGER.debug("File '%s' is updated, mtime '%s/%s'", filename, fomer_mtime,
                 current_mtime)
    return True


def wait_condition(timeout, condition_fn, condition_data):
    """ Wait until condition becomes true or time runs out. """
    wait_time = 0
    while not condition_fn(condition_data):
        wait_time += 1
        if wait_time > timeout:
            return -1
        time.sleep(1)
    return 0


def config_collectd():
    """ Configure Collectd. """
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

    config_file = open(collectd_conf, "r")
    data = config_file.read()
    config_file.close()

    matched = re.search(edit_signature, data)
    if not matched:
        LOGGER.info("File '%s' has not been edited by DDN Monsystem "
                    "before, updating it", (collectd_conf))
        ret = comment_collectd_config(collectd_conf)
        if ret:
            LOGGER.error("Failed to edit Collectd settings")
            cleanup_and_exit(-1, "Collectd setting failure", advices)

        config_file = open(collectd_conf, 'a')
        config_file.write(collectd_append)
        config_file.close()
    else:
        LOGGER.info("File '%s' has already been edited by DDN "
                    "Monsystem before", (collectd_conf))

    system_log_file = "/var/log/messages"
    system_log = WatchedLog(system_log_file)
    collectd_log = WatchedLog(collectd_log_file)
    logs = []
    logs.append(system_log)
    logs.append(collectd_log)

    service_name = "carbon-aggregator"
    ret = service_restart(service_name)
    if ret:
        LOGGER.error("Failed to start service '%s'", service_name)
        cleanup_and_exit(-1, "Collectd failure", advices)

    service_name = "carbon-cache"
    ret = service_restart(service_name)
    if ret:
        LOGGER.error("Failed to start service '%s'", service_name)
        cleanup_and_exit(-1, "Collectd failure", advices)

    hostname = os.uname()[1]
    cabon_directory = "/var/lib/carbon/whisper/collectd"
    cpu_idle_file = (cabon_directory + "/" + hostname + "/" +
                     "cpu-0/cpu-idle.wsp")
    if os.path.exists(cpu_idle_file):
        fomer_mtime = os.stat(cpu_idle_file)[stat.ST_MTIME]
    else:
        fomer_mtime = "0"

    service_name = "collectd"
    ret = service_restart(service_name)
    if ret:
        LOGGER.error("Failed to start service '%s'", service_name)
        for log in logs:
            messages = log.get_new()
            if messages:
                LOGGER.debug("Log '%s': '%s'", log.log_name, messages)
        cleanup_and_exit(-1, "Collectd failure", advices)

    arguments = [cpu_idle_file, fomer_mtime]
    timeout = 20
    ret = wait_condition(timeout, check_update, arguments)
    if ret:
        LOGGER.error("File '%s' has not been updated for %d seconds",
                     cpu_idle_file, timeout)
        cleanup_and_exit(-1, "Collectd failure", advices)

    # Check whether there is any error messages in Collectd log
    pattern = "error"
    messages = collectd_log.get_new()
    if messages:
        matched = re.search(pattern, messages)
        if matched:
            LOGGER.info("The collectd log file '%s' has some "
                        "error messages, please check whether "
                        "there is any  problem", collectd_log_file)
            LOGGER.debug("Log '%s': '%s'", collectd_log.log_name, messages)


def config_grafana():
    """ Configure Grafana. """
    advices = []
    grafana_httpd_conf_filename = "/etc/httpd/conf.d/grafana.conf"
    edit_signature = "\n## Added by script of DDN Monitoring System\n"
    grafana_document_root = "/usr/local/grafana/src"
    grafana_js_conf_filename = grafana_document_root + "/config.js"
    grafana_js_conf_sample_filename = (grafana_document_root +
                                       "/config.sample.js")
    global GRAPHITE_URL
    elasticsearch_url = "http://localhost:9200"
    grafana_js_edit_signature = ("\n    // Added by script of DDN Monitoring "
                                 "System\n")
    grafana_js_conf = grafana_js_edit_signature
    grafana_js_conf += "    datasources: {\n"
    grafana_js_conf += "      graphite: {\n"
    grafana_js_conf += "        type: 'graphite',\n"
    grafana_js_conf += "        url: \"" + GRAPHITE_URL + "\",\n"
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
    if os.path.exists(grafana_httpd_conf_filename):
        config_file = open(grafana_httpd_conf_filename, "r")
        data = config_file.read()
        config_file.close()

        matched = re.search(edit_signature, data)
        if not matched:
            LOGGER.info("File '%s' has not been edited by DDN Monsystem "
                        "before", grafana_httpd_conf_filename)
            backup_file(grafana_httpd_conf_filename)
        else:
            LOGGER.info("File '%s' has already been edited by DDN Monsystem "
                        "before", grafana_httpd_conf_filename)
            need_write = False
    if need_write:
        LOGGER.info("Writing file '%s'", (grafana_httpd_conf_filename))
        config_file = open(grafana_httpd_conf_filename, 'w')
        config_file.write(grafana_httpd_conf)
        config_file.close()

    need_write = True
    if os.path.exists(grafana_js_conf_filename):
        config_file = open(grafana_js_conf_filename, "r")
        data = config_file.read()
        config_file.close()

        matched = re.search(grafana_js_edit_signature, data)
        if not matched:
            LOGGER.info("File '%s' has not been edited by DDN Monsystem "
                        "before", grafana_js_conf_filename)
            backup_file(grafana_js_conf_filename)
        else:
            LOGGER.info("File '%s' has already been edited by DDN Monsystem "
                        "before", grafana_js_conf_filename)
            need_write = False

    if need_write:
        shutil.copy2(grafana_js_conf_sample_filename,
                     grafana_js_conf_filename)

        config_file = open(grafana_js_conf_filename, "r")
        data = config_file.read()
        config_file.close()

        block_pattern = r"  return new Settings\({\n.+  }\);\n"
        replacers = []
        replacers.append(Replacer(r"(return new Settings\({)",
                                  [r"${origin}\n" + grafana_js_conf]))
        new_data = replace_block(data, block_pattern, replacers)
        config_file = open(grafana_js_conf_filename, "w")
        config_file.write(new_data)
        config_file.close()

    service_name = "httpd"
    ret = service_restart(service_name)
    if ret:
        LOGGER.error("Failed to start service '%s'", service_name)
        cleanup_and_exit(-1, "httpd failure", advices)

    service_name = "elasticsearch"
    ret = service_restart(service_name)
    if ret:
        LOGGER.error("Failed to start service '%s'", service_name)
        cleanup_and_exit(-1, "httpd failure", advices)

    httpd_error_log = "/var/log/httpd/error_log"
    logs = []
    logs.append(WatchedLog(httpd_error_log))

    url_start = "http://"
    default_grafana_url = "http://localhost:8000"
    prompt_message = ("Please input grafana URL ('%s' by default): " %
                      default_grafana_url)
    grafana_url = raw_input(prompt_message)
    if grafana_url == "":
        grafana_url = default_grafana_url
    elif ((len(grafana_url) < len(url_start)) or
          (grafana_url[0:len(url_start)] != url_start)):
        grafana_url = url_start + grafana_url

    LOGGER.info("Checking Grafana URL '%s'", grafana_url)
    ret = check_url(grafana_url)
    if ret != 0:
        LOGGER.error("Grafana is not running correctly")
        for log in logs:
            messages = log.get_new()
            if messages:
                LOGGER.debug("Log '%s': '%s'", log.log_name, messages)
        cleanup_and_exit(-1, "httpd failure", advices)

    for log in logs:
        messages = log.get_new()
        if messages:
            LOGGER.error("Log '%s': '%s'", log.log_name, messages)


def config_startup():
    """ Configure startup of services. """
    advices = []
    services = ["httpd", "collectd", "carbon-aggregator", "carbon-cache",
                "elasticsearch"]
    for service in services:
        ret = service_startup_on(service)
        if ret:
            LOGGER.error("Failed to set service '%s' startup on", service)
            cleanup_and_exit(-1, "Service startup failure", advices)


def usage(command):
    """ Dump help of usage. """
    LOGGER.error("Usage: %s [-u|update] [-h|help]\n"
                 "    --base_repo=BASE_REPO\n"
                 "    --epel_repo=EPEL_REPO\n"
                 "    --ELASTICSEARCH_RPM=RPM", command)


class Step(object):
    """ Installation step. """
    def __init__(self):
        self.steps = []

    def add_step(self, name, func):
        """ Add a step. """
        self.steps.append([name, func])

    def run(self):
        """ Run all steps. """
        current_step = 0
        for name, func in self.steps:
            current_step += 1
            LOGGER.info("====== Step %d/%d started: %s ======", current_step,
                        len(self.steps), name)
            ret = func()
            if ret:
                LOGGER.info("====== Step %d/%d failed: %s ======",
                            current_step, len(self.steps), name)
                return ret
            LOGGER.info("====== Step %d/%d finished: %s ======", current_step,
                        len(self.steps), name)
        return ret


def main(argv):
    """ Main function. """
    global UPDATE_RPMS_ANYWAY
    global BASE_REPOSITORY
    global EPEL_REPOSITORY
    global ELASTICSEARCH_RPM

    try:
        opts, args = getopt.getopt(argv[1:], "uh",
                                   ["update",
                                    "help",
                                    "base_repo=",
                                    "epel_repo=",
                                    "elasticsearch_rpm="])
    except getopt.GetoptError:
        LOGGER.error("Failed to parse options %s", argv)
        usage(argv[0])
        return 2
    for opt, arg in opts:
        if opt in ("-u", "--update"):
            UPDATE_RPMS_ANYWAY = True
            LOGGER.debug("Upadate RPMs anyway")
        elif opt in ("-h", "--help"):
            usage(argv[0])
            return 0
        elif opt == "--base_repo":
            BASE_REPOSITORY = arg
            LOGGER.debug("Use local base repository '%s'", BASE_REPOSITORY)
        elif opt == "--epel_repo":
            EPEL_REPOSITORY = arg
            LOGGER.debug("Use local epel repository '%s'", EPEL_REPOSITORY)
        elif opt == "--elasticsearch_rpm":
            ELASTICSEARCH_RPM = arg
            LOGGER.debug("Use local elasticsearch rpm '%s'", ELASTICSEARCH_RPM)
        else:
            LOGGER.error("Unkown option '%s'", opt)

    signal.signal(signal.SIGINT, signal_hander)
    signal.signal(signal.SIGTERM, signal_hander)

    LOGGER.info("Installing DDN Monsystem")

    step = Step()
    step.add_step("Create DDN Monsystem repositories", create_repos)
    step.add_step("Install DDN Monsystem RPMs", install_rpms)
    step.add_step("Configure Graphite", config_graphite)
    step.add_step("Configure Collectd", config_collectd)
    step.add_step("Configure Grafana", config_grafana)
    step.add_step("Configure service startup", config_startup)
    ret = step.run()
    if ret:
        LOGGER.error("Installation failed")
        return ret

    LOGGER.info("Installation finished")
    return 0

if __name__ == '__main__':
    log_setup()
    sys.exit(main(sys.argv))
