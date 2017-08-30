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
    createrepo mkisofs yum-utils redhat-lsb unzip \
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

DEPENDENT_RPMS="../rpms"
PYLIBS_DIR=$DEPENDENT_RPMS"/pylibs"
rm -fr $DEPENDENT_RPMS

mkdir -p $PYLIBS_DIR
pushd $PYLIBS_DIR
# download python libs from pipy
#python - certifi
if [ ! -e ../rtifi-2017.7.27.1.tar.gz ]; then
    wget https://pypi.python.org/packages/20/d0/3f7a84b0c5b89e94abbd073a5f00c7176089f526edb056686751d5064cbd/certifi-2017.7.27.1.tar.gz#md5=48e8370da8b370a16e223ee9c7b6b063
    if [ $? -ne 0 ]; then
        error "failed to download python - certifi package"
    fi
fi

#python - influxdb
if [ ! -e ../influxdb-4.1.1.tar.gz ]; then
    wget https://pypi.python.org/packages/e1/af/94faea244de2a73b7a0087637660db2d638edaae58f22d3f0d0d219ad8b7/influxdb-4.1.1.tar.gz#md5=a59916ef8882b239eb04033775908bd8
    if [ $? -ne 0 ]; then
        error "failed to download python - influxdb package"
    fi
fi

#python - six
if [ ! -e ../six-1.10.0.tar.gz ]; then
    wget https://pypi.python.org/packages/b3/b2/238e2590826bfdd113244a40d9d3eb26918bd798fc187e2360a8367068db/six-1.10.0.tar.gz#md5=34eed507548117b2ab523ab14b2f8b55
    if [ $? -ne 0 ]; then
        error "failed to download python - six package"
    fi
fi

#python - urllib3
if [ ! -e ../urllib3-1.22.tar.gz ]; then
    wget https://pypi.python.org/packages/ee/11/7c59620aceedcc1ef65e156cc5ce5a24ef87be4107c2b74458464e437a5d/urllib3-1.22.tar.gz#md5=0da7bed3fe94bf7dc59ae37885cc72f7
    if [ $? -ne 0 ]; then
        error "failed to download python - urllib3 package"
    fi
fi


#python - pytz
if [ ! -e ../pytz-2017.2.tar.gz ]; then
    wget https://pypi.python.org/packages/a4/09/c47e57fc9c7062b4e83b075d418800d322caa87ec0ac21e6308bd3a2d519/pytz-2017.2.zip#md5=f89bde8a811c8a1a5bac17eaaa94383c
    if [ $? -ne 0 ]; then
        error "failed to download python - pytz package"
    fi
    unzip pytz-2017.2.zip
    tar -cf pytz-2017.2.tar.gz pytz-2017.2
    rm -f pytz-2017.2.zip
fi

#python - requests
if [ ! -e ../requests-2.18.4.tar.gz ]; then
    wget https://pypi.python.org/packages/b0/e1/eab4fc3752e3d240468a8c0b284607899d2fbfb236a56b7377a329aa8d09/requests-2.18.4.tar.gz#md5=081412b2ef79bdc48229891af13f4d82
    if [ $? -ne 0 ]; then
        error "failed to download python - requests package"
    fi
fi

#python - dateutils
if [ ! -e ../python-dateutil-2.6.1.tar.gz ]; then
    wget https://pypi.python.org/packages/54/bb/f1db86504f7a49e1d9b9301531181b00a1c7325dc85a29160ee3eaa73a54/python-dateutil-2.6.1.tar.gz#md5=db38f6b4511cefd76014745bb0cc45a4
    if [ $? -ne 0 ]; then
        error "failed to download python - dateutil package"
    fi
fi

#python - idna
if [ ! -e ../idna-2.6.tar.gz ]; then
    wget https://pypi.python.org/packages/f4/bd/0467d62790828c23c47fc1dfa1b1f052b24efdf5290f071c7a91d0d82fd3/idna-2.6.tar.gz#md5=c706e2790b016bd0ed4edd2d4ba4d147
    if [ $? -ne 0 ]; then
        error "failed to download python - idna package"
    fi
fi

#python - chardet
if [ ! -e ../chardet-3.0.4.tar.gz ]; then
    wget https://pypi.python.org/packages/fc/bb/a5768c230f9ddb03acc9ef3f0d4a3cf93462473795d18e9535498c8f929d/chardet-3.0.4.tar.gz#md5=7dd1ba7f9c77e32351b0a0cfacf4055c
    if [ $? -ne 0 ]; then
        error "failed to download python - chardet package"
    fi
fi
popd

#python - Unidecode
if [ ! -e ../Unidecode-0.04.21.tar.gz ]; then
    wget https://pypi.python.org/packages/0e/26/6a4295c494e381d56bba986893382b5dd5e82e2643fc72e4e49b6c99ce15/Unidecode-0.04.21.tar.gz#md5=089031ed00637d7078f33dad9d6a3c12
    if [ $? -ne 0 ]; then
        error "failed to download python - Unidecode package"
    fi
fi
popd

#python - slugify
if [ ! -e ../python-slugify-1.2.4.tar.gz ]; then
    wget https://pypi.python.org/packages/9f/b0/2723356c20fb01b0e09f6ee03c0c629f4e30811e7d92ebd15453d648e5f0/python-slugify-1.2.4.tar.gz#md5=338ab6beafcea746161f07b6173a9031
    if [ $? -ne 0 ]; then
        error "failed to download python - slugify package"
    fi
fi
popd

pushd $DEPENDENT_RPMS
# download dependent RPMs
for rpmname in openpgm yajl zeromq3 fontconfig glibc glibc-common \
               glibc-devel fontpackages-filesystem glibc-headers glibc-static \
               libfontenc libtool libtool-ltdl libtool-ltdl-devel libXfont libyaml \
               openpgm patch python2-filelock python2-pip python-backports \
               python-backports-ssl_match_hostname python-dateutil \
               python-requests python-setuptools python-six python-urllib3 \
               PyYAML rsync urw-fonts xorg-x11-font-utils python-chardet \
               python-idna lm_sensors-libs lm_sensors
do
    yumdownloader -x \*i686 --archlist=x86_64 "$rpmname"
    if [ $? -ne 0 ]; then
        error "failed to download $rpmname RPM"
    fi
done

git clone https://github.com/Vonage/Grafana_Status_panel.git Grafana_Status_panel
if [ $? -ne 0 ]; then
    error "failed to download grafana status panel"
fi
popd

rm esmon-*.tar.bz2 esmon-*.tar.gz -f

sh ./autogen.sh
if [ $? -ne 0 ]; then
    error "failed to run autogen.sh"
fi
./configure --with-collectd=../collectd.git --with-grafana=../grafana-4.4.1-1.x86_64.rpm \
    --with-influxdb=../influxdb-1.3.1.x86_64.rpm --with-dependent-rpms=$DEPENDENT_RPMS
if [ $? -ne 0 ]; then
    error "failed to run configure"
fi
make
if [ $? -ne 0 ]; then
    error "failed to build"
fi
