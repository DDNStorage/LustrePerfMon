SUBDIRS = .

BUILD_DIRS = BUILD BUILDROOT RPMS SOURCES SPECS SRPMS

M4_DESTINE_FILES = gpfs-3.5.m4 \
	ime-0.1.m4 \
	infiniband-0.1.m4 \
	lustre-1.8.9.m4 \
	lustre-2.1.6.m4 \
	lustre-2.4.2.m4 \
	lustre-2.5.m4 \
	lustre-ieel-2.5.m4 \
	lustre-ieel-2.7.m4 \
	lustre-es4-2.10.m4 \
	sfa-3.0.m4 \
	sfa-11.0.m4


M4_FILES = general.m4 lustre.m4 sfa.m4 $(M4_DESTINE_FILES)

XML_DESTINE_FILES=$(M4_DESTINE_FILES:.m4=.xml)

noinst_DATA = $(BUILD_DIRS) $(XML_DEFINITION_RPM) $(M4_FILES) test_driver.py \
	xml_definition.spec tests

$(XML_DESTINE_FILES): $(M4_FILES)
	m4 $(@:.xml=.m4) > $@.tmp
	xmllint --valid --noout $@.tmp > /dev/null
	if [ "$enable_test" = yes -a "${DISTRO_RELEASE}" != 5 ]; then \
		@PYTHON@ test_driver.py tests/$(basename $@)/preset.xml $@.tmp; \
	else \
		echo "Skip test of $@"; \
	fi
	mv $@.tmp $@

$(XML_DEFINITION_RPM): $(BUILD_DIRS) $(XML_DESTINE_FILES)
	tar czvf xml_definition.tar.gz *.xml collectd.conf.all
	mv xml_definition.tar.gz ./SOURCES
	rpmbuild -ba --define="rev ${XML_DEFINITION_REV}" --define="dist .el${DISTRO_RELEASE}" --define="_topdir $(shell pwd)" xml_definition.spec

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f $(XML_DEFINITION_RPM)
	-rm -f $(XML_DESTINE_FILES)
	-rm -f -r $(BUILD_DIRS)
