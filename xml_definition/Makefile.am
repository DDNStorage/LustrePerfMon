SUBDIRS = .

BUILD_DIRS = BUILD BUILDROOT RPMS SOURCES SPECS SRPMS

EXTRA_DIST = build.sh
LOCAL_XML_DEFINITION_RPMS = $(addprefix RPMS/x86_64/, $(XML_DEFINITION_RPMS))

noinst_DATA = $(BUILD_DIRS) $(LOCAL_XML_DEFINITION_RPMS)

xml_definition-$(XML_DEFINITION_VERSION):
	cp $(XML_DEFINITION) xml_definition-$(XML_DEFINITION_VERSION) -a

$(LOCAL_XML_DEFINITION_RPMS): xml_definition-$(XML_DEFINITION_VERSION)
	sh build.sh $(shell pwd) $(shell pwd)/xml_definition-$(XML_DEFINITION_VERSION)

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f -r xml_definition-$(XML_DEFINITION_VERSION)
	-rm -f -r $(BUILD_DIRS)
