#!/bin/sh
TOPDIR=$1
SOURCEDIR=$2
REV=$3
DIST=$4

creat_dir()
{
	local NEWDIR=$1
	if [ ! -e $NEWDIR ]; then
		mkdir -p $NEWDIR
		if [ $? -ne 0 ]; then
			echo "Faled to create $NEWDIR"
			exit 1
		fi
	fi

	if [ ! -d $NEWDIR ]; then
		echo "$NEWDIR is not a directory"
		exit 1
	fi
	return 0
}

if [ "$TOPDIR" = "" ]; then
	echo "The path of top directory is missing"
	exit 1
fi

DIRNAME=$(dirname $TOPDIR)
if [ "$DIRNAME" = "." ];then
	echo "$TOPDIR is not absolute path"
	exit 1
fi

if [ "$SOURCEDIR" = "" ]; then
	echo "The path of collectd source code directory is missing"
	exit 1
fi

DIRNAME=$(dirname $SOURCEDIR)
if [ "$DIRNAME" = "." ];then
	echo "$SOURCEDIR is not absolute path"
	exit 1
fi

creat_dir $TOPDIR/BUILD
creat_dir $TOPDIR/BUILDROOT
creat_dir $TOPDIR/RPMS
creat_dir $TOPDIR/SOURCES
creat_dir $TOPDIR/SPECS
creat_dir $TOPDIR/SRPMS

cd $SOURCEDIR
if [ "$REV" = "" ]; then
	REV=$(git rev-parse --short HEAD)
fi

sh ./build.sh
if [ $? -ne 0 ]; then
	echo "Failed to run build.sh"
	exit 1
fi

./configure --enable-dist
if [ $? -ne 0 ]; then
	echo "Failed to configure"
	exit 1
fi

make dist-bzip2
if [ $? -ne 0 ]; then
	echo "Failed to make dist-bzip2"
	exit 1
fi

mv collectd-*.tar.bz2 $TOPDIR/SOURCES/
if [ $? -ne 0 ]; then
	echo "Failed to move collectd-*.tar.bz2"
	exit 1
fi

rpmbuild -ba --without java --without amqp --without nut \
	--without pinba --without ping --without varnish \
	--define="rev ${REV}" \
	--define="dist ${DIST}" \
	--define="_topdir ${TOPDIR}" \
	$SOURCEDIR/contrib/redhat/collectd-rhel6.spec

exit $?
