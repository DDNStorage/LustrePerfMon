SUBDIRS = .

BUILD_DIRS = BUILD BUILDROOT RPMS SOURCES SPECS SRPMS

EXTRA_DIST = build.sh
LOCAL_MONTOOLS_RPMS = $(addprefix RPMS/x86_64/, $(MONTOOLS_RPMS))

noinst_DATA = $(BUILD_DIRS) $(LOCAL_MONTOOLS_RPMS)

montools-$(MONTOOLS_VERSION):
	mkdir montools-$(MONTOOLS_VERSION)
	cp graphite-setup.py montools-$(MONTOOLS_VERSION) -a
	cp grafana-setup.py montools-$(MONTOOLS_VERSION) -a

$(LOCAL_MONTOOLS_RPMS): montools-$(MONTOOLS_VERSION)
	sh build.sh $(shell pwd) $(shell pwd)/montools-$(MONTOOLS_VERSION) $(DISTRO_RELEASE)

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f -r montools-$(MONTOOLS_VERSION)
	-rm -f -r $(BUILD_DIRS)
