SUBDIRS = .

BUILD_DIRS = RPMS

ORIGIN_COLLECTD_RPMS = $(addprefix ../collectd/RPMS/x86_64/, $(COLLECTD_RPMS))
GRAFANA_RPM = $(notdir $(GRAFANA_RPM_PATH))
ORIGIN_XML_DEFINITION_RPMS = $(addprefix ../xml_definition/RPMS/x86_64/, $(XML_DEFINITION_RPMS))
ORIGIN_OPENTSDB_WEB_RPMS = $(addprefix ../opentsdb_web/RPMS/x86_64/, $(OPENTSDB_WEB_RPMS))
LOCAL_COLLECTD_RPMS = $(addprefix RPMS/, $(COLLECTD_RPMS))
LOCAL_GRAFANA_RPMS = $(addprefix RPMS/, $(GRAFANA_RPM))
LOCAL_XML_DEFINITION_RPMS = $(addprefix RPMS/, $(XML_DEFINITION_RPMS))
LOCAL_OPENTSDB_WEB_RPMS = $(addprefix RPMS/, $(OPENTSDB_WEB_RPMS))

noinst_DATA = $(BUILD_DIRS) \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5

$(LOCAL_COLLECTD_RPMS): $(ORIGIN_COLLECTD_RPMS)
	cp $(addprefix ../collectd/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_GRAFANA_RPMS): $(GRAFANA_RPM_PATH)
	cp $(GRAFANA_RPM_PATH) RPMS

$(LOCAL_XML_DEFINITION_RPMS): $(ORIGIN_XML_DEFINITION_RPMS)
	cp $(addprefix ../xml_definition/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_OPENTSDB_WEB_RPMS): $(ORIGIN_OPENTSDB_WEB_RPMS)
	cp $(addprefix ../opentsdb_web/RPMS/x86_64/, $(notdir $@)) RPMS

monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso: RPMS install.py \
		$(LOCAL_COLLECTD_RPMS) \
		$(LOCAL_GRAFANA_RPMS) \
		$(LOCAL_XML_DEFINITION_RPMS) \
		$(LOCAL_OPENTSDB_WEB_RPMS) \
		topn.py
	rm -f monsystem-ddn.*.iso
	rm -f monsystem-ddn.*.md5
	@PEP8@ install.py
	cp install.py RPMS
	cp topn.py RPMS
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
