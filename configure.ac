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
COLLECTD_VERSION=$(grep Version $COLLECTD/contrib/redhat/collectd-rhel6.spec | \
	awk '{print $2}' | sed -e "s/%{?rev}/$git_version/g")
AC_MSG_RESULT([$COLLECTD_VERSION])
AC_SUBST(COLLECTD_VERSION)

# -------- check for collectd release --------
AC_MSG_CHECKING([for collectd release])
COLLECTD_RELEASE=$(grep Release $COLLECTD/contrib/redhat/collectd-rhel6.spec | \
	awk '{print $2}' | sed -e "s/%{?dist}//g")
AC_MSG_RESULT([$COLLECTD_RELEASE])
AC_SUBST(COLLECTD_RELEASE)

# -------- check for collectd RPMs --------
AC_MSG_CHECKING([for collectd RPMs])
COLLECTD_RPM_SUBFIX=${COLLECTD_VERSION}-${COLLECTD_RELEASE}.el${DISTRO_RELEASE}.x86_64.rpm
bases="collectd libcollectdclient libcollectdclient-devel"
for base in ${bases}; do
	COLLECTD_RPMS="${COLLECTD_RPMS} ${base}-${COLLECTD_RPM_SUBFIX}"
done
ddn_plugins="gpfs lustre stress zabbix"
# REHL7 does not hace ganglia support yet.
if [[[ "$DISTRO_RELEASE" != "7" ]]]; then
	ddn_plugins="ganglia ${ddn_plugins}"
fi
common_plugins="rrdtool"
plugins="${ddn_plugins} ${common_plugins}"
for plugin in ${plugins}; do
	COLLECTD_RPMS="${COLLECTD_RPMS} collectd-${plugin}-${COLLECTD_RPM_SUBFIX}"
done

AC_MSG_RESULT([$COLLECTD_RPMS])
AC_SUBST(COLLECTD_RPMS)

# -------- check for xml_definition sources --------
AC_MSG_CHECKING([for xml_definition sources])
AC_ARG_WITH([xml_definition],
	AC_HELP_STRING([--with-xml_definition=path],
		       [set path to xml_definition source]),
	[MB_ARG_CANON_PATH([xml_definition], [XML_DEFINITION])],
	[])
AC_MSG_RESULT([$XML_DEFINITION])
AC_SUBST(XML_DEFINITION)

# -------- check for xml_definition --------
MB_CHECK_FILE([$XML_DEFINITION], [],
	[AC_MSG_ERROR([xml_definition source $XML_DEFINITION could not be found.])])

# -------- check for xml_definition version --------
AC_MSG_CHECKING([for xml_definition version])
git_version=$(git --git-dir=$XML_DEFINITION/.git rev-parse --short HEAD)
if [[[ $? -ne 0 ]]]; then
	AC_MSG_ERROR([$XML_DEFINITION is not a git repository.])
fi
XML_DEFINITION_VERSION=$(grep Version $XML_DEFINITION/xml_definition.spec | \
	awk '{print $2}' | sed -e "s/%{?rev}/$git_version/g")
AC_MSG_RESULT([$XML_DEFINITION_VERSION])
AC_SUBST(XML_DEFINITION_VERSION)

# -------- check for xml_definition release --------
AC_MSG_CHECKING([for xml_definition release])
XML_DEFINITION_RELEASE=$(grep Release $XML_DEFINITION/xml_definition.spec | \
	awk '{print $2}' | sed -e "s/%{?dist}//g")
AC_MSG_RESULT([$XML_DEFINITION_RELEASE])
AC_SUBST(XML_DEFINITION_RELEASE)

# -------- check for xml_definition RPMs --------
AC_MSG_CHECKING([for xml_definition RPMs])
XML_DEFINITION_RPMS=xml_definition-${XML_DEFINITION_VERSION}-${XML_DEFINITION_RELEASE}.el${DISTRO_RELEASE}.x86_64.rpm
AC_MSG_RESULT([$XML_DEFINITION_RPMS])
AC_SUBST(XML_DEFINITION_RPMS)

# -------- check for grafana sources --------
AC_MSG_CHECKING([for grafana sources])
AC_ARG_WITH([grafana],
	AC_HELP_STRING([--with-grafana=path],
		       [set path to grafana source]),
	[MB_ARG_CANON_PATH([grafana], [GRAFANA])],
	[])
AC_MSG_RESULT([$GRAFANA])
AC_SUBST(GRAFANA)

# -------- check for grafana --------
MB_CHECK_FILE([$GRAFANA], [],
	[AC_MSG_ERROR([grafana source $GRAFANA could not be found.])])

# -------- check for grafana version --------
AC_MSG_CHECKING([for grafana version])
changelog_version=$(grep -e "\# [[:digit:]][[:digit:]]*[.][[:digit:]][[:digit:]]*[.][[:digit:]][[:digit:]]*" \
$GRAFANA/CHANGELOG.md | awk '{print $2}' | head -n 1)

git_version=$(git --git-dir=$GRAFANA/.git rev-parse --short HEAD)
if [[[ $? -ne 0 ]]]; then
	AC_MSG_ERROR([$GRAFANA is not a git repository.])
fi
GRAFANA_VERSION=$(grep Version grafana/grafana.spec | \
	awk '{print $2}' | \
	sed -e "s/%{?brev}/$changelog_version/g" | \
	sed -e "s/%{?rev}/$git_version/g")
AC_MSG_RESULT([$GRAFANA_VERSION])
AC_SUBST(GRAFANA_VERSION)

# -------- check for grafana release --------
AC_MSG_CHECKING([for grafana release])
GRAFANA_RELEASE=$(grep Release grafana/grafana.spec | \
	awk '{print $2}' | sed -e "s/%{?dist}//g")
AC_MSG_RESULT([$GRAFANA_RELEASE])
AC_SUBST(GRAFANA_RELEASE)

# -------- check for grafana RPMs --------
AC_MSG_CHECKING([for grafana RPMs])
GRAFANA_RPMS=grafana-${GRAFANA_VERSION}-${GRAFANA_RELEASE}.el${DISTRO_RELEASE}.x86_64.rpm
AC_MSG_RESULT([$GRAFANA_RPMS])
AC_SUBST(GRAFANA_RPMS)

# -------- check for montools version --------
git_version=$(git rev-parse --short HEAD)
if [[[ $? -ne 0 ]]]; then
	AC_MSG_ERROR([monsystem_package is not a git repository.])
fi

AC_MSG_CHECKING([for montools version])
MONTOOLS_VERSION=$(grep Version montools/montools.spec | \
	awk '{print $2}' | sed -e "s/%{?rev}/$git_version/g")
AC_MSG_RESULT([$MONTOOLS_VERSION])
AC_SUBST(MONTOOLS_VERSION)

# -------- check for montools release --------
AC_MSG_CHECKING([for montools release])
MONTOOLS_RELEASE=$(grep Release montools/montools.spec | \
	awk '{print $2}' | sed -e "s/%{?dist}//g")
AC_MSG_RESULT([$MONTOOLS_RELEASE])
AC_SUBST(MONTOOLS_RELEASE)

# -------- check for montools RPMS --------
AC_MSG_CHECKING([for montools RPMS])
MONTOOLS_RPMS=montools-${MONTOOLS_VERSION}-${MONTOOLS_RELEASE}.el${DISTRO_RELEASE}.x86_64.rpm
AC_MSG_RESULT([$MONTOOLS_RPMS])
AC_SUBST(MONTOOLS_RPMS)

AC_CONFIG_FILES([Makefile collectd/Makefile xml_definition/Makefile
	grafana/Makefile montools/Makefile package/Makefile])
AC_OUTPUT
