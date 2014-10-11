SUBDIRS = .

BUILD_DIRS = BUILD BUILDROOT RPMS SOURCES SPECS SRPMS

EXTRA_DIST = build.sh
LOCAL_COLLECTD_RPMS = $(addprefix RPMS/x86_64/, $(COLLECTD_RPMS))

noinst_DATA = $(BUILD_DIRS) $(LOCAL_COLLECTD_RPMS)

collectd-$(COLLECTD_VERSION):
	cp $(COLLECTD) collectd-$(COLLECTD_VERSION) -a

$(LOCAL_COLLECTD_RPMS): collectd-$(COLLECTD_VERSION)
	sh build.sh $(shell pwd) $(shell pwd)/collectd-$(COLLECTD_VERSION) $(DISTRO_RELEASE)

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f -r collectd-$(COLLECTD_VERSION)
	-rm -f -r $(BUILD_DIRS)
