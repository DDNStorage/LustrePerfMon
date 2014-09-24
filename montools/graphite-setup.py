#!/usr/bin/python
import os
import shutil
import sys
import stat

lport=8000
debug = 0

def file_add_exec(path):
	st = os.stat(path)
	os.chmod(path, st.st_mode | stat.S_IEXEC)

def config_local_setting(setting_conf):
	graphitedb = "/var/lib/graphite-web/graphite.db"
	dst_conf = "/etc/graphite-web/local_settings.py"
	dst_fp = open(dst_conf, 'w')
	uncomment = 0
	with open(setting_conf, 'r') as src_fp:
		for line in src_fp:
			if line[0:6] == "#DEBUG" and debug:
				dst_fp.write(line[1:])
				continue

			if line[0:10] == "#DATABASES":
				uncomment = 1
			if uncomment:
				if line[0] == '#':
					if line.find("'NAME'") > 0:
						idx = line.index(':')
						newline = line[1:idx+1] + " '" \
							  + graphitedb + "',\n"
						dst_fp.write(newline)
					else:
						dst_fp.write(line[1:])
				if line[0:2] == "#}":
					uncomment = 0
			else:
				dst_fp.write(line)

	print setting_conf

def clear_database_config():
	local_setting = "/etc/graphite-web/local_settings.py.back"
	if os.path.exists(local_setting):
		os.rename(local_setting, "/etc/graphite-web/local_settings.py")

def config_database():
	os.rename("/etc/graphite-web/local_settings.py",
		  "/etc/graphite-web/local_settings.py.back")
	setting_conf = "/etc/graphite-web/local_settings.py.back"
	config_local_setting(setting_conf)
	sync_db = "python \
		  /usr/lib/python2.6/site-packages/graphite/manage.py syncdb"
	os.system(sync_db)

def enable_grafana(fp):
	print "Do you want to enable Grafana(yes/no, default is yes): ",
	line = sys.stdin.readline()
	line = line.rstrip('\n')
	if line == "no":
		print "Grafana is disabled"
		return

	print "Enable the Grafana"
	fp.write('Header set Access-Control-Allow-Origin "*"\n')
	fp.write('Header set Access-Control-Allow-Methods "GET, OPTIONS"\n')
	fp.write('Header set Access-Control-Allow-Headers ' \
		 '"origin, authorization, accept"\n')

def add_vhost_to_apache(vhost_conf, port):
	dst_conf = "/etc/httpd/conf.d/graphite-web.conf"
	dst_fp = open(dst_conf, 'w')
	with open(vhost_conf, 'r') as src_fp:
		for line in src_fp:
			if line.find("Listen") == 0:
				continue

			if line.find("<VirtualHost ") == 0:
				listen = "Listen " + str(lport) + "\n"
				line = "<VirtualHost *:" + str(lport) + ">\n"
				dst_fp.write(listen)
				dst_fp.write(line)
				enable_grafana(dst_fp)
				continue
			if line.find("Header set Access-Control-Allow-Origin") == 0 \
			   or line.find("Header set Access-Control-Allow-Methods") == 0 \
			   or line.find("Header set Access-Control-Allow-Headers") == 0 :
				continue
			dst_fp.write(line)
	src_fp.close()
	dst_fp.close()

def clear_apache_config():
	if os.path.exists("/etc/httpd/conf.d/graphite-web.conf.back"):
		os.rename("/etc/httpd/conf.d/graphite-web.conf.back",
			  "/etc/httpd/conf.d/graphite-web.conf")
		os.system("service httpd start")

def config_apache():
	global lport
	print "Enter the Graphite listen port(default is %d): " %lport,
	line = sys.stdin.readline()
	line = line.rstrip('\n')
	if len(line) > 0:
		lport = line

	os.rename("/etc/httpd/conf.d/graphite-web.conf",
		  "/etc/httpd/conf.d/graphite-web.conf.back")
	vhost_conf = "/etc/httpd/conf.d/graphite-web.conf.back"
	add_vhost_to_apache(vhost_conf, lport)

def uninstall():
	print "=============== STEP1: clear database config ==============="
	clear_database_config()
	print "=============== STEP2: clear apache config ==============="
	clear_apache_config()

def disable_selinux_in_config():
	selinux_conf = "/etc/selinux/config"
	new_conf = "/etc/selinux/config.new"

	new_fp = open(new_conf, 'w')
	with open(selinux_conf, 'r') as src_fp:
		for line in src_fp:
			line = line.strip()
			mylist=line.split('=')
			if mylist[0] == 'SELINUX' \
			   and len(mylist) == 2 \
			   and mylist[1] != 'disabled':
				line = "SELINUX=disabled"
			new_fp.write(line)
			new_fp.write('\n')
	src_fp.close()
	new_fp.close()

	os.rename(new_conf, selinux_conf)

def disable_selinux():
	print "Disable the Selinux(yes/no, default is yes):",
	line = sys.stdin.readline()
	line = line.rstrip('\n')
	if line == "yes" or len(line) == 0:
		os.system("setenforce 0")
		disable_selinux_in_config()
	else:
		print "Warning: Do not disable the Selinux, " \
		      "please config it to make the httpd available"

def disable_iptables():
	print "Disable the iptables(yes/no, default is yes):",
	line = sys.stdin.readline()
	line = line.rstrip('\n')
	if line == "yes" or len(line) == 0:
		print "Diable the iptables now"
		os.system("service iptables stop")
		os.system("chkconfig iptables off")
	else:
		print "Warning: Do not disable the iptables, " \
		      "please config it to make the httpd available"

def prepare_installation():
	disable_selinux()
	disable_iptables()

def install():
	prepare_installation()
	print "============ STEP1: Config graphite apache ==============="
	config_apache()
	print "============ STEP2: Config graphite database ==============="
	config_database()

	print "============ STEP4: Add permission to 'Apache' of: "\
	      "/var/lib/graphite-web/graphite.db =============="
	chown_cmd = "chown -R apache:apache /var/lib/graphite-web/graphite.db"
	os.system(chown_cmd)
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




