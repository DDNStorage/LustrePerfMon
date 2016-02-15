SUBDIRS = .

BUILD_DIRS = BUILD BUILDROOT RPMS SOURCES SPECS SRPMS

OPENTSDB_WEB_FILES=angular.min.js bubble.html \
	index.html topn.js opentsdb.js pie.html bar.html \
	table.html

noinst_DATA = $(BUILD_DIRS) $(OPENTSDB_WEB_RPMS) $(OPENTSDB_WEB_FILES) \
	opentsdb_web.spec

$(OPENTSDB_WEB_RPMS): $(OPENTSDB_WEB_FILES)
	tar czvf opentsdb_web.tar.gz $(OPENTSDB_WEB_FILES)
	mv opentsdb_web.tar.gz ./SOURCES
	rpmbuild -ba --define="rev ${OPENTSDB_WEB_REV}" --define="dist .el${DISTRO_RELEASE}" --define="_topdir $(shell pwd)" opentsdb_web.spec

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f $(OPENTSDB_WEB_RPMS)
	-rm -f -r $(BUILD_DIRS)
