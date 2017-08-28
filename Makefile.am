if XMLONLY
SUBDIRS = xml_definition
else
SUBDIRS = collectd xml_definition opentsdb_web .
endif

EXTRA_DIST = version-gen.sh autogen.sh detect-distro.sh esmon.spec \
	esmon_install esmon.conf pyesmon/*.py man1/*

ORIGIN_COLLECTD_RPMS = $(addprefix collectd/RPMS/x86_64/, $(COLLECTD_RPMS))
GRAFANA_RPM = $(notdir $(GRAFANA_RPM_PATH))
INFLUXDB_RPM = $(notdir $(INFLUXDB_RPM_PATH))
ORIGIN_XML_DEFINITION_RPM = $(addprefix xml_definition/RPMS/noarch/, $(XML_DEFINITION_RPM))
ORIGIN_OPENTSDB_WEB_RPMS = $(addprefix opentsdb_web/RPMS/x86_64/, $(OPENTSDB_WEB_RPMS))
LOCAL_COLLECTD_RPMS = $(addprefix RPMS/, $(COLLECTD_RPMS))
LOCAL_GRAFANA_RPMS = $(addprefix RPMS/, $(GRAFANA_RPM))
LOCAL_INFLUXDB_RPMS = $(addprefix RPMS/, $(INFLUXDB_RPM))
LOCAL_XML_DEFINITION_RPM = $(addprefix RPMS/, $(XML_DEFINITION_RPM))
LOCAL_OPENTSDB_WEB_RPMS = $(addprefix RPMS/, $(OPENTSDB_WEB_RPMS))
ESMON_RPM = ./build/RPMS/x86_64/esmon-$(MONSYSTEM_PKGVER)-$(ESMON_RELEASE).el$(DISTRO_RELEASE).x86_64.rpm

noinst_DATA = BUILD_ISO \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5

build_dir = `pwd`/build

$(ESMON_RPM): esmon.spec dist
	mkdir -p $(build_dir)/BUILD $(build_dir)/SPECS $(build_dir)/SRPMS $(build_dir)/RPMS \
		&& rpmbuild $(rpmbuild_opt) --define="_topdir $(build_dir)" \
			--define="_prefix $(prefix)" -tb $(distdir).tar.gz \
			--define="dist .el${DISTRO_RELEASE}" \
		&& echo "RPM successfully generated in $(build_dir)/RPMS"

$(LOCAL_COLLECTD_RPMS): $(ORIGIN_COLLECTD_RPMS)
	cp $(addprefix collectd/RPMS/x86_64/, $(notdir $@)) BUILD_ISO

$(LOCAL_GRAFANA_RPMS): $(GRAFANA_RPM_PATH)
	cp $(GRAFANA_RPM_PATH) BUILD_ISO

$(LOCAL_INFLUXDB_RPMS): $(INFLUXDB_RPM_PATH)
	cp $(INFLUXDB_RPM_PATH) BUILD_ISO

$(LOCAL_XML_DEFINITION_RPM): $(ORIGIN_XML_DEFINITION_RPM)
	cp $(addprefix xml_definition/RPMS/noarch/, $(notdir $@)) BUILD_ISO

$(LOCAL_OPENTSDB_WEB_RPMS): $(ORIGIN_OPENTSDB_WEB_RPMS)
	cp $(addprefix opentsdb_web/RPMS/x86_64/, $(notdir $@)) BUILD_ISO

monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso: CLEAN_BUILD_ISO \
		$(ESMON_RPM) \
		$(LOCAL_COLLECTD_RPMS) \
		$(LOCAL_GRAFANA_RPMS) \
		$(LOCAL_INFLUXDB_RPMS) \
		$(LOCAL_XML_DEFINITION_RPM) \
		$(LOCAL_OPENTSDB_WEB_RPMS) \
		influxdb.conf.diff
	rm -f monsystem-ddn.*.iso
	rm -f monsystem-ddn.*.md5
	cp influxdb.conf.diff BUILD_ISO
	cp -a dashboards BUILD_ISO
	cp installesmon.sh BUILD_ISO
	cp -a $(DEPENDENT_RPMS_PATH)/* BUILD_ISO
	cp DDN-Storage-RedBG.svg BUILD_ISO
	cp DDN-Storage-RedBG.png BUILD_ISO
	cp $(ESMON_RPM) BUILD_ISO
	createrepo BUILD_ISO
	mkisofs -joliet-long -R -o monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso BUILD_ISO

monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5: \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso
	md5sum monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso \
		> monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5

CLEAN_BUILD_ISO:
	rm BUILD_ISO -fr
	mkdir BUILD_ISO

clean-local:
	-rm -f -r $(BUILD_DIRS)
	-rm -f monsystem-ddn.*.iso
	-rm -f monsystem-ddn.*.md5

maintainer-clean-local:
	-rm -f -r libltdl
	-rm -f INSTALL
	-rm -f aclocal.m4
