if XMLONLY
SUBDIRS = xml_definition
else
SUBDIRS = xml_definition opentsdb_web .
endif

DISTRO_RHEL6 = rhel6
DISTRO_RHEL7 = rhel7
ISO_PATH = ISO
ISO_RPM = $(ISO_PATH)/RPMS
ISO_RPM_RHEL7 = $(ISO_RPM)/$(DISTRO_RHEL7)
ISO_RPM_RHEL7_SERVER = $(ISO_RPM_RHEL7)/server

EXTRA_DIST = autogen.sh detect-distro.sh esmon.spec esmon_build \
	esmon_build.conf esmon_config esmon_install esmon_install.conf \
	esmon_influxdb esmon_test esmon_test.conf esmon_virt \
	esmon_virt.conf pyesmon/*.py man1/* version-gen.sh 

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

doc/ESMON_User_Manual_Raw_en.pdf: doc/ESMON_User_Manual_Raw_en.md doc/pic
	cd doc && pandoc --template=ddntemplate.latex --toc ESMON_User_Manual_Raw_en.md -o ESMON_User_Manual_Raw_en.pdf

esmon-$(MONSYSTEM_PKGVER).x86_64.iso: \
		doc/ESMON_User_Manual_Raw_en.pdf $(ESMON_RPM)
	rm $(ISO_PATH) -fr
	rm -f esmon-*.iso
	rm -f esmon-*.md5
	cp -a $(CACHED_ISO_PATH) $(ISO_PATH)
	cp $(XML_DEFINITION_RPM_PATH) $(ISO_RPM)
	cp $(ESMON_RPM) $(ISO_RPM_RHEL7)
	cp influxdb.conf.diff $(ISO_PATH)
	cp -a dashboards $(ISO_PATH)
	cp -a $(CACHED_ISO_PATH)/Grafana_Status_panel $(ISO_PATH)
	cp DDN-Storage-RedBG.svg $(ISO_PATH)
	cp DDN-Storage-RedBG.png $(ISO_PATH)
	cp doc/ESMON_User_Manual_Raw_en.pdf $(ISO_PATH)
	mkisofs -joliet-long -R -o esmon-$(MONSYSTEM_PKGVER).x86_64.iso $(ISO_PATH)

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
