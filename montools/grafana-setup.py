#!/usr/bin/python
import os
import shutil
import sys
import stat
import re
import socket
import fcntl
import struct


GRAFANA_DIR="/usr/local/grafana"
GRAFANA_CONF_DIR="/usr/local/grafana/src"
GRAFANA_CONF_VHOST="/etc/httpd/conf.d/grafana.conf"
GRAFANA_CONF_VHOST_BACKUP="/etc/httpd/conf.d/grafana.conf.back"
lport=9100
graphite_port=8000
elasticsearch_port=9200
debug = 0
graphite_url = ""
elasticsearch_url = ""

def __add_grafana_vhost(port, docroot):
	conf_fp = open(GRAFANA_CONF_VHOST, 'w+')

	conf_fp.truncate(0)
	conf_fp.write("<VirtualHost *:%s>\n" %port)
	conf_fp.write("DocumentRoot %s\n" %docroot)
	conf_fp.write("</VirtualHost>\n")
	conf_fp.write("Listen %s\n" %port)

def add_grafana_vhost():
	global lport
	print "Enter the grafana listen port(default is %s): " %lport,
	line = sys.stdin.readline()
	line = line.rstrip('\n')
	if len(line) > 0:
		lport = line

	doc_root = GRAFANA_CONF_DIR
	__add_grafana_vhost(lport, doc_root)

def remove_grafana_vhost():
	os.rename(GRAFANA_CONF_VHOST, GRAFANA_CONF_VHOST_BACKUP)

def get_my_ip():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def conf_change_settings(conf_file, context, content):
	tmp_file = conf_file + ".back"
	dst_fp = open(tmp_file, 'w')
	with open(conf_file, 'r') as src_fp:
		for line in src_fp:
			if line.find(context) >= 0:
				dst_fp.write(line)
				dst_fp.write(content)
				continue
			dst_fp.write(line)
	src_fp.close()
	dst_fp.close()
	os.rename(tmp_file, conf_file)

def config_elasticsearch_url():
	global elasticsearch_url
	using_ip = get_my_ip()
	default_url = "http://%s:%s" %(using_ip, elasticsearch_port)
	print "Enter the elasticsearch url(default is: '%s'): " %default_url,
	elasticsearch_url = sys.stdin.readline()
	elasticsearch_url = elasticsearch_url.rstrip('\n')
	if len(elasticsearch_url) == 0:
		elasticsearch_url = default_url

def config_graphite_url():
	global graphite_url
	using_ip = get_my_ip()
	default_url = "http://%s:%s" %(using_ip, graphite_port)
	print "Enter the graphite url(default is: '%s'): " %default_url,
	graphite_url = sys.stdin.readline()
	graphite_url = graphite_url.rstrip('\n')
	if len(graphite_url) == 0:
		graphite_url = default_url

def config_js():
	cur_dir = os.getcwd()
	dst_dir = GRAFANA_CONF_DIR
	os.chdir(dst_dir)
	shutil.copy("config.sample.js", "config.js")

	global graphite_url
	global elasticsearch_url
	content = ""
	content = content + "    datasources: {\n"
	content = content + "      graphite: {\n"
	content = content + "        type: 'graphite',\n"
	content = content + "        url: \"" + graphite_url + "\",\n"
	content = content + "      },\n"
	content = content + "      elasticsearch: {\n"
	content = content + "        type: 'elasticsearch',\n"
	content = content + "        url: \"" + elasticsearch_url + "\",\n"
	content = content + "        index: 'grafana-dash',\n"
	content = content + "        grafanaDB: true,\n"
	content = content + "      }\n"
	content = content + "    },"

	conf_file = GRAFANA_CONF_DIR + "/config.js"
	conf_change_settings(conf_file, "return new Settings", content)

	os.chdir(cur_dir)


def uninstall():
	os.system("service httpd stop")
	conf_file = GRAFANA_CONF_DIR + "/config.js"
	conf_file_backup = GRAFANA_CONF_DIR + "/config.js.backup"
	os.rename(conf_file, conf_file_backup)
	remove_grafana_vhost()
	os.system("service httpd start")

ALL_STEPS=4
def install():
	os.system("/etc/init.d/httpd stop")
	print "(1/%s) =============== Config config.js file  ===============" %ALL_STEPS
	config_graphite_url()
	add_grafana_vhost()
	print "(2/%s) =============== Enable elasticsearch  ===============" %ALL_STEPS
	config_elasticsearch_url()
	print "(3/%s) =============== Reconfig config.js ===============" %ALL_STEPS
	config_js()
	os.system("chkconfig --add elasticsearch")
	os.system("service elasticsearch restart")
	os.system("service httpd restart")


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Please use: python setup.py install or " \
		      "python setup.py uninstall"
		exit()
	if sys.argv[1] == "install":
		install()
	elif sys.argv[1] == "uninstall":
		uninstall()
	else:
		print "Please use: python setup.py install or " \
		      "python setup.py uninstall"




