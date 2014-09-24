#!/bin/sh

ALL_STEPS=5
CURRENT_STEP=1
DDN_MON_REPOSITORY_PATH=/etc/yum.repos.d/monsystem-ddn.repo
echo "==============DDN Monsystem Instllation======================="
echo "($CURRENT_STEP/$ALL_STEPS). Mount system ISO on mount point '/media/CentOS':"
echo -n "Please enter the system ISO full path(press 'enter' if already mounted):"
isopath=
read isopath
if [ ! -z $isopath ];then
	mkdir -p /media/CentOS
	mount -o loop $isopath /media/CentOS
	rc = $?
	if [ $rc -ne 0 ];then
		echo "mount $isopath on /media/CentOS failed, exit"
		exit $rc
	fi
fi

CURRENT_STEP=2
echo "($CURRENT_STEP/$ALL_STEPS). Create DDN Monsystem repository:"
echo -n "Please enter the full path of mount point of monsystem-ddn.iso:"
read DDN_MON_PATH
if [ -d $DDN_MON_PATH -a -f "$DDN_MON_PATH/install.sh" ]; then
	echo -e "[monsystem-ddn]\n"\
"name=Monitor system of DDN\n"\
"baseurl=file://${DDN_MON_PATH}\n"\
"failovermethod=priority\n"\
"enabled=1\n"\
"gpgcheck=0\n" > $DDN_MON_REPOSITORY_PATH
else
	echo "Wrong path: $DDN_MON_PATH, exit"
	exit -1
fi

CURRENT_STEP=3
echo "($CURRENT_STEP/$ALL_STEPS). Install DDN Monsystem:"
yum install montools
rc = $?
if [ $rc -ne 0 ];then
	echo "Install montools failed, exit"
	exit $rc
fi

CURRENT_STEP=4
echo "($CURRENT_STEP/$ALL_STEPS). Config graphite:"
python /usr/local/montools/bin/graphite-setup install

CURRENT_STEP=5
echo "($CURRENT_STEP/$ALL_STEPS). Install and config grafana?"
echo -n "Install grafana?(yes/no, default is yes):"
read ins_grafana
if [ "$ins_grafana" == "yes" -o  -z "$ins_grafana" ];then
	yum install grafana elasticsearch
	python /usr/local/montools/bin/grafana-setup install
else
	echo "Enter: ${ins_grafana}, grafana not installed"
fi

echo "==============DDN Monsystem Instllation Finished======================="
