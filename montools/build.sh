#!/bin/sh
TOPDIR=$1
SOURCEDIR=$2
DISTRO_RELEASE=$3
REV=$4

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

if [ "$DISTRO_RELEASE" = "5" ]; then
	DIST=".el5"
elif [ "$DISTRO_RELEASE" = "6" ]; then
	DIST=".el6"
else
	echo "$DISTRO_RELEASE is not supported"
	exit
fi

tar czvf montools.tar.gz *
if [ $? -ne 0 ]; then
	echo "Failed to generate montools.tar.gz"
	exit 1
fi

mv montools.tar.gz $TOPDIR/SOURCES/
if [ $? -ne 0 ]; then
	echo "Failed to move montools.tar.gz"
	exit 1
fi

rpmbuild -ba \
	--define="rev ${REV}" \
	--define="dist ${DIST}" \
	--define="_topdir ${TOPDIR}" \
	$TOPDIR/montools.spec

exit $?
