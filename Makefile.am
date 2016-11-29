if XMLONLY
SUBDIRS = xml_definition
else
SUBDIRS = collectd xml_definition opentsdb_web package .
endif

EXTRA_DIST = version-gen.sh autogen.sh detect-distro.sh

maintainer-clean-local:
	-rm -f -r libltdl
	-rm -f INSTALL
	-rm -f aclocal.m4
