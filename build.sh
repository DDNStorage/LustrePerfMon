#!/bin/bash
error()
{
    echo $@
    exit 1
}

rpm -e zeromq-devel

yum install libgcrypt-devel libtool-ltdl-devel curl-devel \
    libxml2-devel yajl-devel libdbi-devel libpcap-devel \
    OpenIPMI-devel iptables-devel libvirt-devel \
    libvirt-devel libmemcached-devel mysql-devel libnotify-devel \
    libesmtp-devel postgresql-devel rrdtool-devel \
    lm_sensors-devel net-snmp-devel libcap-devel \
    lvm2-devel libmodbus-devel libmnl-devel iproute-devel \
    hiredis-devel libatasmart-devel protobuf-c-devel \
    mosquitto-devel gtk2-devel openldap-devel \
    zeromq3-devel libssh2-devel rrdtool-devel rrdtool \
    createrepo mkisofs yum-utils redhat-lsb \
    epel-release perl-Regexp-Common python-pep8 pylint lua-devel -y
if [ $? -ne 0 ]; then
    error "failed to install RPMs"
fi

if [ ! -e ../collectd.git ]; then
	git clone git://10.128.7.3/collectd.git ../collectd.git
    if [ $? -ne 0 ]; then
        error "failed to clone collectd"
    fi
else
    pushd ../collectd.git > /dev/null
    git checkout master
    if [ $? -ne 0 ]; then
        error "failed to checkout master branch of collectd"
    fi
    git branch -D master-ddn
    if [ $? -ne 0 ]; then
        error "failed to delete master-ddn branch of collectd"
    fi
    popd
fi
pushd ../collectd.git > /dev/null
git pull
if [ $? -ne 0 ]; then
    error "failed to git pull collectd"
fi
git checkout master-ddn
if [ $? -ne 0 ]; then
    error "failed to checkout master-ddn branch of collectd"
fi
popd

if [ ! -e ../grafana-4.4.1-1.x86_64.rpm ]; then
    pushd ../
    wget --no-check-certificate https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-4.4.1-1.x86_64.rpm
    if [ $? -ne 0 ]; then
        error "failed to download grafana RPM"
    fi
    popd
fi


if [ ! -e ../influxdb-1.3.1.x86_64.rpm ]; then
    pushd ../
    curl -LO  https://dl.influxdata.com/influxdb/releases/influxdb-1.3.1.x86_64.rpm
    if [ $? -ne 0 ]; then
        error "failed to download influxdb RPM"
    fi
    popd
fi

pushd ../
DEPENDENT_RPMS="rpms"
rm -fr $DEPENDENT_RPMS
mkdir $DEPENDENT_RPMS
pushd $DEPENDENT_RPMS

# download dependent RPMs

for rpmname in openpgm yajl zeromq3 fontconfig glibc glibc-common glibc-devel fontpackages-filesystem glibc-headers glibc-static libfontenc libtool-ltdl libtool-ltdl-devel libXfont libyaml openpgm patch python2-filelock python2-pip python-backports python-backports-ssl_match_hostname python-dateutil python-requests python-setuptools python-six python-urllib3 PyYAML rsync urw-fonts xorg-x11-font-utils python-chardet
do
  yumdownloader "$rpmname"
  if [ $? -ne 0 ]; then
    error "failed to download $rpmname RPM"
  fi
done
rm *.i686.rpm -f

git clone https://github.com/Vonage/Grafana_Status_panel.git Grafana_Status_panel
if [ $? -ne 0 ]; then
    error "failed to download grafana status panel"
fi
popd
popd

sh ./autogen.sh
if [ $? -ne 0 ]; then
    error "failed to run autogen.sh"
fi
./configure --with-collectd=../collectd.git --with-grafana=../grafana-4.4.1-1.x86_64.rpm \
    --with-influxdb=../influxdb-1.3.1.x86_64.rpm --with-dependent-rpms=../$DEPENDENT_RPMS
if [ $? -ne 0 ]; then
    error "failed to run configure"
fi
make
if [ $? -ne 0 ]; then
    error "failed to build"
fi
