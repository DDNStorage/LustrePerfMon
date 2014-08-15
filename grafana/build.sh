#!/bin/sh
TOPDIR=$1
SOURCEDIR=$2
BREV=$3
REV=$4
DIST=$5

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

if [ "$BREV" = "" ]; then
	BREV=$(grep -e "\# [[:digit:]][[:digit:]]*[.][[:digit:]][[:digit:]]*[.][[:digit:]][[:digit:]]*" \
CHANGELOG.md | awk '{print $2}' | head -n 1)
fi

tar czvf grafana.tar.gz *
if [ $? -ne 0 ]; then
	echo "Failed to generate grafana.tar.gz"
	exit 1
fi

mv grafana.tar.gz $TOPDIR/SOURCES/
if [ $? -ne 0 ]; then
	echo "Failed to move grafana.tar.gz"
	exit 1
fi

rpmbuild -ba \
	--define="brev ${BREV}" \
	--define="rev ${REV}" \
	--define="dist ${DIST}" \
	--define="_topdir ${TOPDIR}" \
	$TOPDIR/grafana.spec

exit $?
