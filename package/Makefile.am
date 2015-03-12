SUBDIRS = .

BUILD_DIRS = RPMS

ORIGIN_COLLECTD_RPMS = $(addprefix ../collectd/RPMS/x86_64/, $(COLLECTD_RPMS))
ORIGIN_GRAFANA_RPMS = $(addprefix ../grafana/RPMS/x86_64/, $(GRAFANA_RPMS))
ORIGIN_XML_DEFINITION_RPMS = $(addprefix ../xml_definition/RPMS/x86_64/, $(XML_DEFINITION_RPMS))
ORIGIN_MONTOOLS_RPMS = $(addprefix ../montools/RPMS/x86_64/, $(MONTOOLS_RPMS))
LOCAL_COLLECTD_RPMS = $(addprefix RPMS/, $(COLLECTD_RPMS))
LOCAL_GRAFANA_RPMS = $(addprefix RPMS/, $(GRAFANA_RPMS))
LOCAL_XML_DEFINITION_RPMS = $(addprefix RPMS/, $(XML_DEFINITION_RPMS))
LOCAL_MONTOOLS_RPMS = $(addprefix RPMS/, $(MONTOOLS_RPMS))

noinst_DATA = $(BUILD_DIRS) \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.md5

$(LOCAL_COLLECTD_RPMS): $(ORIGIN_COLLECTD_RPMS)
	cp $(addprefix ../collectd/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_GRAFANA_RPMS): $(ORIGIN_GRAFANA_RPMS)
	cp $(addprefix ../grafana/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_XML_DEFINITION_RPMS): $(ORIGIN_XML_DEFINITION_RPMS)
	cp $(addprefix ../xml_definition/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_MONTOOLS_RPMS): $(ORIGIN_MONTOOLS_RPMS)
	cp $(addprefix ../montools/RPMS/x86_64/, $(notdir $@)) RPMS

monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso: RPMS install.py \
		$(LOCAL_COLLECTD_RPMS) \
		$(LOCAL_GRAFANA_RPMS) \
		$(LOCAL_XML_DEFINITION_RPMS) \
		$(LOCAL_MONTOOLS_RPMS)
	cp install.py RPMS
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
	-rm -f monsystem-ddn.el$(DISTRO_RELEASE).x86_64.iso
