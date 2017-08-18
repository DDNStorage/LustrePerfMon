#! /bin/sh
# This script to prepare the installation
cd "$(dirname "$0")"
rpm -ivh python*.rpm
yum remove esmon
rpm -ivh libyaml*.rpm
rpm -ivh Py*.rpm
rpm -ivh esmon*.rpm
if [ $? -ne 0 ];then
  echo "ESMON package install failed"
  exit -1
fi
echo "ESMON package has been installed"
echo "Please set your servers' information into /etc/esmon.conf"
echo "And please make sure you can access all these server by ssh with keyfile"
echo "Then please run /opt/monitor_packager/bin/esmon_install to continue"
