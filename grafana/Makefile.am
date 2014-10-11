SUBDIRS = .

BUILD_DIRS = BUILD BUILDROOT RPMS SOURCES SPECS SRPMS

EXTRA_DIST = build.sh
LOCAL_GRAFANA_RPMS = $(addprefix RPMS/x86_64/, $(GRAFANA_RPMS))

noinst_DATA = $(BUILD_DIRS) $(LOCAL_GRAFANA_RPMS)

grafana-$(GRAFANA_VERSION):
	cp $(GRAFANA) grafana-$(GRAFANA_VERSION) -a

$(LOCAL_GRAFANA_RPMS): grafana-$(GRAFANA_VERSION)
	sh build.sh $(shell pwd) $(shell pwd)/grafana-$(GRAFANA_VERSION) $(DISTRO_RELEASE)

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f -r grafana-$(GRAFANA_VERSION)
	-rm -f -r $(BUILD_DIRS)
