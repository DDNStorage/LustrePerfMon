if XMLONLY
SUBDIRS = xml_definition
else
SUBDIRS = collectd xml_definition opentsdb_web .
endif

EXTRA_DIST = version-gen.sh autogen.sh detect-distro.sh esmon.spec \
	esmon_install esmon.conf pyesmon/*.py man1/*

BUILD_DIRS = RPMS

ORIGIN_COLLECTD_RPMS = $(addprefix collectd/RPMS/x86_64/, $(COLLECTD_RPMS))
GRAFANA_RPM = $(notdir $(GRAFANA_RPM_PATH))
INFLUXDB_RPM = $(notdir $(INFLUXDB_RPM_PATH))
ORIGIN_XML_DEFINITION_RPMS = $(addprefix xml_definition/RPMS/noarch/, $(XML_DEFINITION_RPMS))
ORIGIN_OPENTSDB_WEB_RPMS = $(addprefix opentsdb_web/RPMS/x86_64/, $(OPENTSDB_WEB_RPMS))
LOCAL_COLLECTD_RPMS = $(addprefix RPMS/, $(COLLECTD_RPMS))
LOCAL_GRAFANA_RPMS = $(addprefix RPMS/, $(GRAFANA_RPM))
LOCAL_INFLUXDB_RPMS = $(addprefix RPMS/, $(INFLUXDB_RPM))
LOCAL_XML_DEFINITION_RPMS = $(addprefix RPMS/, $(XML_DEFINITION_RPMS))
LOCAL_OPENTSDB_WEB_RPMS = $(addprefix RPMS/, $(OPENTSDB_WEB_RPMS))
ESMON_RPM = ./build/RPMS/x86_64/esmon-$(MONSYSTEM_PKGVER)-$(ESMON_RELEASE).el$(DISTRO_RELEASE).x86_64.rpm

noinst_DATA = $(BUILD_DIRS) \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5

build_dir = `pwd`/build

$(ESMON_RPM): esmon.spec dist
	mkdir -p $(build_dir)/BUILD $(build_dir)/SPECS $(build_dir)/SRPMS $(build_dir)/RPMS \
		&& rpmbuild $(rpmbuild_opt) --define="_topdir $(build_dir)" \
			--define="_prefix $(prefix)" -tb $(distdir).tar.gz \
		&& echo "RPM successfully generated in $(build_dir)/RPMS"

$(LOCAL_COLLECTD_RPMS): $(ORIGIN_COLLECTD_RPMS)
	cp $(addprefix collectd/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_GRAFANA_RPMS): $(GRAFANA_RPM_PATH)
	cp $(GRAFANA_RPM_PATH) RPMS

$(LOCAL_INFLUXDB_RPMS): $(INFLUXDB_RPM_PATH)
	cp $(INFLUXDB_RPM_PATH) RPMS

$(LOCAL_XML_DEFINITION_RPMS): $(ORIGIN_XML_DEFINITION_RPMS)
	cp $(addprefix xml_definition/RPMS/noarch/, $(notdir $@)) RPMS

$(LOCAL_OPENTSDB_WEB_RPMS): $(ORIGIN_OPENTSDB_WEB_RPMS)
	cp $(addprefix opentsdb_web/RPMS/x86_64/, $(notdir $@)) RPMS

monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso: RPMS \
		$(ESMON_RPM) \
		$(LOCAL_COLLECTD_RPMS) \
		$(LOCAL_GRAFANA_RPMS) \
		$(LOCAL_INFLUXDB_RPMS) \
		$(LOCAL_XML_DEFINITION_RPMS) \
		$(LOCAL_OPENTSDB_WEB_RPMS) \
		collectd.conf.ddnmon influxdb.conf.ddnmon grafana-ddnmon.json
	rm -f monsystem-ddn.*.iso
	rm -f monsystem-ddn.*.md5
	cp $(ESMON_RPM) RPMS
	createrepo RPMS
	mkisofs -joliet-long -R -o monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso RPMS

monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5: \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso
	md5sum monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso \
		> monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f -r $(BUILD_DIRS)
	-rm -f monsystem-ddn.*.iso
	-rm -f monsystem-ddn.*.md5

maintainer-clean-local:
	-rm -f -r libltdl
	-rm -f INSTALL
	-rm -f aclocal.m4
