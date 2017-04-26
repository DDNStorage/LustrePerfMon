dnl Process this file with autoconf to produce a configure script.
AC_INIT([monitor_packager],[m4_esyscmd(./version-gen.sh)])
AC_CONFIG_SRCDIR(./collectd/build.sh)
AC_CONFIG_HEADERS(config.h)

AM_INIT_AUTOMAKE([tar-pax dist-bzip2 foreign])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])
AC_LANG(C)

AC_PREFIX_DEFAULT("/opt/monitor_packager")

#
# Checks for programs.
#
AC_PROG_CC
AC_PROG_CPP
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_MAKE_SET
AM_PROG_CC_C_O
AM_CONDITIONAL(COMPILER_IS_GCC, test "x$GCC" = "xyes")

AC_DISABLE_STATIC
AC_PROG_LIBTOOL
AC_PROG_LEX
AC_PROG_YACC
PKG_PROG_PKG_CONFIG

#
# MB_CHECK_FILE
#
# Check for file existance even when cross compiling
# $1 - file to check
# $2 - do 'yes'
# $3 - do 'no'
#
AC_DEFUN([MB_CHECK_FILE], [
AS_VAR_PUSHDEF([mb_file], [mb_cv_file_$1])dnl
AC_CACHE_CHECK([for $1], mb_file, [
AS_IF([test -r "$1"],
	[AS_VAR_SET(mb_file, [yes])],
	[AS_VAR_SET(mb_file, [no])])
])
AS_IF([test AS_VAR_GET(mb_file) = yes], [$2], [$3])[]dnl
AS_VAR_POPDEF([mb_file])dnl
]) # MB_CHECK_FILE

#
# MB_ARG_REPLACE_PATH(PACKAGE, PATH)
#
AC_DEFUN([MB_ARG_REPLACE_PATH], [
new_configure_args=
eval set -- $ac_configure_args
for arg; do
	case $arg in
		--with-[$1]=*)
			arg=--with-[$1]=[$2] ;;
		*\'*)
			arg=$(printf %s\n ["$arg"] | \
				sed "s/'/'\\\\\\\\''/g") ;;
	esac
	dnl AS_VAR_APPEND([new_configure_args], [" '$arg'"])
	new_configure_args="$new_configure_args '$arg'"
done
ac_configure_args=$new_configure_args
])

#
# __MB_ARG_CANON_PATH
#
# this is the work-horse of the next function
#
AC_DEFUN([__MB_ARG_CANON_PATH], [
	[$3]=$(readlink -f $with_$2)
	MB_ARG_REPLACE_PATH([$1], $[$3])
])

#
# MB_ARG_CANON_PATH
#
# a front-end for the above function that transforms - and . in the
# PACKAGE portion of --with-PACKAGE into _ suitable for variable names
#
AC_DEFUN([MB_ARG_CANON_PATH], [
	__MB_ARG_CANON_PATH([$1], m4_translit([$1], [-.], [__]), [$2])
])

# -------- check for distro version --------
AC_MSG_CHECKING([for distro version])
DISTRO=$(sh detect-distro.sh)
DISTRO_NAME=$(echo $DISTRO | awk -F '-' '{print $1}')
if [[[ "$DISTRO_NAME" != "rhel" ]]]; then
	AC_MSG_ERROR([$DISTRO_NAME is not a supported distro.])
fi
DISTRO_RELEASE=$(echo $DISTRO | awk -F 'rhel-' '{print $2}' | awk -F '.' '{print $1}')
AC_MSG_RESULT([$DISTRO_RELEASE])
AC_SUBST(DISTRO_RELEASE)

# -------- check for package version --------
AC_MSG_CHECKING([for package version])
MONSYSTEM_PKGVER=$(sh ./version-gen.sh)
AC_MSG_RESULT([$MONSYSTEM_PKGVER])
AC_SUBST(MONSYSTEM_PKGVER)

# -------- check whether to only build XML definition rpm --------
AC_MSG_CHECKING([Only build XML rpm])
AC_ARG_ENABLE([xmlonly],
	AC_HELP_STRING([--enable-xmlonly],
		       [only build xml definition rpm]),
	[], [enable_xmlonly="no"])
AC_MSG_RESULT([$enable_xmlonly])
AM_CONDITIONAL([XMLONLY], [test x$enable_xmlonly = xyes])

# -------- check whether to enable XML test --------
AC_MSG_CHECKING([whether to enable XML test])
AC_ARG_ENABLE([test],
	AC_HELP_STRING([--disable-test],
		       [disable test]),
	[], [enable_test="yes"])
AC_MSG_RESULT([$enable_test])

if [[[ $enable_xmlonly == 'no' ]]]; then
	# -------- check for collectd sources --------
	AC_MSG_CHECKING([for collectd sources])
	AC_ARG_WITH([collectd],
		AC_HELP_STRING([--with-collectd=path],
			       [set path to collectd source]),
		[MB_ARG_CANON_PATH([collectd], [COLLECTD])],
		[])
	AC_MSG_RESULT([$COLLECTD])
	AC_SUBST(COLLECTD)

	# -------- check for collectd --------
	MB_CHECK_FILE([$COLLECTD], [],
		[AC_MSG_ERROR([Collectd source $COLLECTD could not be found.])])

	# -------- check for collectd version --------
	AC_MSG_CHECKING([for collectd version])
	git_version=$(git --git-dir=$COLLECTD/.git rev-parse --short HEAD)
	if [[[ $? -ne 0 ]]]; then
		AC_MSG_ERROR([$COLLECTD is not a git repository.])
	fi
	COLLECTD_VERSION=$(grep Version $COLLECTD/contrib/redhat/collectd.spec | \
		grep -v \# | awk '{print $2}' | sed -e "s/%{?rev}/$git_version/g")
	AC_MSG_RESULT([$COLLECTD_VERSION])
	AC_SUBST(COLLECTD_VERSION)

	# -------- check for collectd release --------
	AC_MSG_CHECKING([for collectd release])
	COLLECTD_RELEASE=$(grep Release $COLLECTD/contrib/redhat/collectd.spec | \
		grep -v \# | awk '{print $2}' | sed -e "s/%{?dist}//g")
	AC_MSG_RESULT([$COLLECTD_RELEASE])
	AC_SUBST(COLLECTD_RELEASE)

	# -------- check for collectd RPMs --------
	AC_MSG_CHECKING([for collectd RPMs])
	COLLECTD_RPM_SUBFIX=${COLLECTD_VERSION}-${COLLECTD_RELEASE}.el${DISTRO_RELEASE}.x86_64.rpm
	bases="collectd libcollectdclient libcollectdclient-devel"
	for base in ${bases}; do
		COLLECTD_RPMS="${COLLECTD_RPMS} ${base}-${COLLECTD_RPM_SUBFIX}"
	done
	ddn_plugins="gpfs ime filedata stress zabbix ssh"
	# REHL7 does not hace ganglia support yet.
	if [[[ "$DISTRO_RELEASE" != "7" ]]]; then
		ddn_plugins="ganglia ${ddn_plugins}"
		common_plugins="rrdtool"
	fi
	plugins="${ddn_plugins} ${common_plugins}"
	for plugin in ${plugins}; do
		COLLECTD_RPMS="${COLLECTD_RPMS} collectd-${plugin}-${COLLECTD_RPM_SUBFIX}"
	done

	AC_MSG_RESULT([$COLLECTD_RPMS])
	AC_SUBST(COLLECTD_RPMS)

	# -------- check for grafana RPM --------
	AC_MSG_CHECKING([for grafana RPM])
	AC_ARG_WITH([grafana],
		AC_HELP_STRING([--with-grafana=path],
			       [set path to grafana RPM]),
		[MB_ARG_CANON_PATH([grafana], [GRAFANA_RPM_PATH])],
		[])
	AC_MSG_RESULT([$GRAFANA_RPM_PATH])
	AC_SUBST(GRAFANA_RPM_PATH)

	# -------- check for grafana --------
	MB_CHECK_FILE([$GRAFANA_RPM_PATH], [],
		[AC_MSG_ERROR([grafana RPM file $GRAFANA_RPM_PATH could not be found.])])

	# -------- check for opentsdb_web version --------
	AC_MSG_CHECKING([for opentsdb_web version])
	OPENTSDB_WEB_REV=$(git rev-parse --short HEAD)
	if [[[ $? -ne 0 ]]]; then
		AC_MSG_ERROR([monsystem_package is not a git repository.])
	fi
	AC_SUBST(OPENTSDB_WEB_REV)

	OPENTSDB_WEB_VERSION=$(grep Version opentsdb_web/opentsdb_web.spec | \
		awk '{print $2}' | sed -e "s/%{?rev}/${OPENTSDB_WEB_REV}/g")
	AC_MSG_RESULT([$OPENTSDB_WEB_VERSION])
	AC_SUBST(OPENTSDB_WEB_VERSION)

	# -------- check for opentsdb_web release --------
	AC_MSG_CHECKING([for opentsdb_web release])
	OPENTSDB_WEB_RELEASE=$(grep Release opentsdb_web/opentsdb_web.spec | \
		awk '{print $2}' | sed -e "s/%{?dist}//g")
	AC_MSG_RESULT([$OPENTSDB_WEB_RELEASE])
	AC_SUBST(OPENTSDB_WEB_RELEASE)

	# -------- check for opentsdb_web RPMs --------
	AC_MSG_CHECKING([for opentsdb_web RPMs])
	OPENTSDB_WEB_RPMS=opentsdb_web-${OPENTSDB_WEB_VERSION}-${OPENTSDB_WEB_RELEASE}.el${DISTRO_RELEASE}.x86_64.rpm
	AC_MSG_RESULT([$OPENTSDB_WEB_RPMS])
	AC_SUBST(OPENTSDB_WEB_RPMS)
fi

# -------- check for xml_definition version --------
AC_MSG_CHECKING([for xml_definition version])
XML_DEFINITION_REV=$(git rev-parse --short HEAD)
if [[[ $? -ne 0 ]]]; then
	AC_MSG_ERROR([monsystem_package is not a git repository.])
fi
AC_SUBST(XML_DEFINITION_REV)

XML_DEFINITION_VERSION=$(grep Version xml_definition/xml_definition.spec | \
	awk '{print $2}' | sed -e "s/%{?rev}/${XML_DEFINITION_REV}/g")
AC_MSG_RESULT([$XML_DEFINITION_VERSION])
AC_SUBST(XML_DEFINITION_VERSION)

# -------- check for xml_definition release --------
AC_MSG_CHECKING([for xml_definition release])
XML_DEFINITION_RELEASE=$(grep Release xml_definition/xml_definition.spec | \
	awk '{print $2}' | sed -e "s/%{?dist}//g")
AC_MSG_RESULT([$XML_DEFINITION_RELEASE])
AC_SUBST(XML_DEFINITION_RELEASE)

# -------- check for xml_definition RPMs --------
AC_MSG_CHECKING([for xml_definition RPMs])
XML_DEFINITION_RPMS=xml_definition-${XML_DEFINITION_VERSION}-${XML_DEFINITION_RELEASE}.noarch.rpm
AC_MSG_RESULT([$XML_DEFINITION_RPMS])
AC_SUBST(XML_DEFINITION_RPMS)

# ------- check for python --------
AC_CHECK_PROGS([PYTHON], [python], [])
if test "x$PYTHON" = "x"; then
	AC_MSG_ERROR([Python is needed for test of xml_definition. Install python.])
fi

# ------- check for pep8 --------
AC_CHECK_PROGS([PEP8], [pep8], [])
if test "x$PEP8" = "x"; then
	AC_MSG_ERROR([pep8 is needed to check python coding style. Install pep8.])
fi

# ------- check for pylint --------
AC_CHECK_PROGS([PYLINT], [pylint], [])
if test "x$PYLINT" = "x"; then
	AC_MSG_ERROR([pylint is needed to check python coding style. Install pylint.])
fi

# ------- check for ElementTree of python --------
AC_MSG_CHECKING([for ElementTree of python])
if [[[ "${DISTRO_RELEASE}" != "5" ]]]; then
	$PYTHON -c "import xml.etree.ElementTree";
	if [[[ $? -ne 0 ]]]; then
		AC_MSG_ERROR([ElementTree is need for test of xml files.])
		AC_MSG_RESULT([no])
	fi
	AC_MSG_RESULT([yes])
else
	AC_MSG_RESULT([skipped])
fi


AC_CONFIG_FILES([Makefile collectd/Makefile xml_definition/Makefile
	package/Makefile opentsdb_web/Makefile])
AC_OUTPUT
