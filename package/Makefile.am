SUBDIRS = .

BUILD_DIRS = RPMS

ORIGIN_COLLECTD_RPMS = $(addprefix ../collectd/RPMS/x86_64/, $(COLLECTD_RPMS))
ORIGIN_DEPENDENCY_RPMS = $(addprefix ../dependency/, $(DEPENDENCY_RPMS))
ORIGIN_GRAFANA_RPMS = $(addprefix ../grafana/RPMS/x86_64/, $(GRAFANA_RPMS))
ORIGIN_XML_DEFINITION_RPMS = $(addprefix ../xml_definition/RPMS/x86_64/, $(XML_DEFINITION_RPMS))
LOCAL_COLLECTD_RPMS = $(addprefix RPMS/, $(COLLECTD_RPMS))
LOCAL_DEPENDENCY_RPMS = $(addprefix RPMS/, $(DEPENDENCY_RPMS))
LOCAL_GRAFANA_RPMS = $(addprefix RPMS/, $(GRAFANA_RPMS))
LOCAL_XML_DEFINITION_RPMS = $(addprefix RPMS/, $(XML_DEFINITION_RPMS))

noinst_DATA = $(BUILD_DIRS) $(LOCAL_DEPENDENCY_RPMS) \
		monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso

# Taking $(addprefix ../dependency/, $@) as dependency won't work.
$(LOCAL_COLLECTD_RPMS): $(ORIGIN_COLLECTD_RPMS)
	cp $(addprefix ../collectd/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_DEPENDENCY_RPMS): $(ORIGIN_DEPENDENCY_RPMS)
	cp $(addprefix ../dependency/, $(notdir $@)) RPMS

$(LOCAL_GRAFANA_RPMS): $(ORIGIN_GRAFANA_RPMS)
	cp $(addprefix ../grafana/RPMS/x86_64/, $(notdir $@)) RPMS

$(LOCAL_XML_DEFINITION_RPMS): $(ORIGIN_XML_DEFINITION_RPMS)
	cp $(addprefix ../xml_definition/RPMS/x86_64/, $(notdir $@)) RPMS

monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso: RPMS monsystem-ddn.repo \
		$(LOCAL_COLLECTD_RPMS) \
		$(LOCAL_DEPENDENCY_RPMS) \
		$(LOCAL_GRAFANA_RPMS) \
		$(LOCAL_XML_DEFINITION_RPMS)
	cp monsystem-ddn.repo RPMS
	createrepo RPMS
	mkisofs -joliet-long -R -o monsystem-ddn.$(MONSYSTEM_PKGVER).el$(DISTRO_RELEASE).x86_64.iso RPMS

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f $(DEPENDENCY_RPMS)
	-rm -f -r $(BUILD_DIRS)
	-rm -f monsystem-ddn.el$(DISTRO_RELEASE).x86_64.iso
