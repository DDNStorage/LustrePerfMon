if XMLONLY
SUBDIRS = xml_definition
else
SUBDIRS = collectd xml_definition opentsdb_web .
endif

DISTRO_RHEL6 = rhel6
DISTRO_RHEL7 = rhel7

EXTRA_DIST = version-gen.sh autogen.sh detect-distro.sh esmon.spec \
	esmon_install esmon_install.conf esmon_build.conf pyesmon/*.py man1/*

XML_DEFINITION_RPM_PATH = $(addprefix xml_definition/RPMS/noarch/, $(XML_DEFINITION_RPM))
OPENTSDB_WEB_RPM_PATH = $(addprefix opentsdb_web/RPMS/x86_64/, $(OPENTSDB_WEB_RPM))
ESMON_RPM = ./build/RPMS/x86_64/esmon-$(MONSYSTEM_PKGVER)-$(ESMON_RELEASE).el$(DISTRO_RELEASE).x86_64.rpm

noinst_DATA = esmon-$(MONSYSTEM_PKGVER).x86_64.iso \
	esmon-$(MONSYSTEM_PKGVER).x86_64.md5

build_dir = `pwd`/build

$(ESMON_RPM): esmon.spec dist
	mkdir -p $(build_dir)/BUILD $(build_dir)/SPECS $(build_dir)/SRPMS $(build_dir)/RPMS \
		&& rpmbuild $(rpmbuild_opt) --define="_topdir $(build_dir)" \
			--define="_prefix $(prefix)" -tb $(distdir).tar.gz \
			--define="dist .el${DISTRO_RELEASE}" \
		&& echo "RPM successfully generated in $(build_dir)/RPMS"

esmon-$(MONSYSTEM_PKGVER).x86_64.iso: \
		$(ESMON_RPM)
	rm BUILD_ISO -fr
	rm -f esmon-*.iso
	rm -f esmon-*.md5
	mkdir -p BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp collectd/RPMS/x86_64/* BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp $(GRAFANA_RPM_PATH) BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp $(INFLUXDB_RPM_PATH) BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp $(XML_DEFINITION_RPM_PATH) BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp $(ESMON_RPM) BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp $(DEPENDENT_RPMS_PATH)/RPMS/$(DISTRO_RHEL7)/*.rpm \
		BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp $(OPENTSDB_WEB_RPM_PATH) BUILD_ISO/RPMS/$(DISTRO_RHEL7)
	cp -a $(DEPENDENT_RPMS_PATH)/RPMS/$(DISTRO_RHEL6) BUILD_ISO/RPMS
	cp $(XML_DEFINITION_RPM_PATH) BUILD_ISO/RPMS/$(DISTRO_RHEL6)
	cp influxdb.conf.diff BUILD_ISO
	cp -a dashboards BUILD_ISO
	cp installesmon.sh BUILD_ISO
	cp -a $(DEPENDENT_RPMS_PATH)/Grafana_Status_panel BUILD_ISO
	cp -a $(DEPENDENT_RPMS_PATH)/python_library BUILD_ISO
	cp DDN-Storage-RedBG.svg BUILD_ISO
	cp DDN-Storage-RedBG.png BUILD_ISO
	mkisofs -joliet-long -R -o esmon-$(MONSYSTEM_PKGVER).x86_64.iso BUILD_ISO

esmon-$(MONSYSTEM_PKGVER).x86_64.md5: \
		esmon-$(MONSYSTEM_PKGVER).x86_64.iso
	md5sum esmon-$(MONSYSTEM_PKGVER).x86_64.iso \
		> esmon-$(MONSYSTEM_PKGVER).x86_64.md5

clean-local:
	-rm -f -r $(BUILD_DIRS)
	-rm -f esmon-*.iso
	-rm -f esmon-*.md5

maintainer-clean-local:
	-rm -f -r libltdl
	-rm -f INSTALL
	-rm -f aclocal.m4
