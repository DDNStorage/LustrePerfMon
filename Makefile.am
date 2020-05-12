if XMLONLY
SUBDIRS = xml_definition
else
SUBDIRS = xml_definition .
endif

ISO_PATH = ISO
ISO_RPM = $(ISO_PATH)/RPMS
ISO_RPM_DISTRO_CPU = $(ISO_RPM)/rhel$(DISTRO_RELEASE)/$(target_cpu)

EXTRA_DIST = autogen.sh detect-distro.sh esmon.spec esmon_build \
	esmon_build.conf esmon_config esmon_install esmon_install.conf \
	esmon_influxdb esmon_test esmon_virt example_configs \
	pyesmon/*.py man1/* version-gen.sh .pylintrc pyesmon/.pylintrc

XML_DEFINITION_RPM_PATH = $(addprefix xml_definition/RPMS/noarch/, $(XML_DEFINITION_RPM))
ESMON_RPM = ./build/RPMS/$(target_cpu)/esmon-$(MONSYSTEM_PKGVER)-$(ESMON_RELEASE).el$(DISTRO_RELEASE).$(target_cpu).rpm

noinst_DATA = esmon-$(MONSYSTEM_PKGVER).$(target_cpu).iso \
	esmon-$(MONSYSTEM_PKGVER).$(target_cpu).md5

build_dir = `pwd`/build

$(ESMON_RPM): esmon.spec dist
	mkdir -p $(build_dir)/BUILD $(build_dir)/SPECS $(build_dir)/SRPMS $(build_dir)/RPMS \
		&& rpmbuild $(rpmbuild_opt) --define="_topdir $(build_dir)" \
			--define="_prefix $(prefix)" -tb $(distdir).tar.gz \
			--define="dist .el${DISTRO_RELEASE}" \
		&& echo "RPM successfully generated in $(build_dir)/RPMS"

doc/ESMON_User_Manual_Raw_en.pdf: doc/ESMON_User_Manual_Raw_en.md doc/pic
	cd doc && pandoc --template=ddntemplate.latex --toc ESMON_User_Manual_Raw_en.md -o ESMON_User_Manual_Raw_en.pdf

esmon-$(MONSYSTEM_PKGVER).$(target_cpu).iso: \
	$(ESMON_RPM)
	rm $(ISO_PATH) -fr
	rm -f esmon-*.iso
	rm -f esmon-*.md5
	cp -a $(CACHED_ISO_PATH) $(ISO_PATH)
	cp doc/*.docx $(ISO_PATH)
	cp $(XML_DEFINITION_RPM_PATH) $(ISO_RPM)
	cp $(ESMON_RPM) $(ISO_RPM_DISTRO_CPU)
	cp influxdb/influxdb.conf.diff $(ISO_PATH)
	cp -a dashboards $(ISO_PATH)
	cp DDN-Storage-RedBG.svg $(ISO_PATH)
	cp DDN-Storage-RedBG.png $(ISO_PATH)
	mkisofs -joliet-long -R -o esmon-$(MONSYSTEM_PKGVER).$(target_cpu).iso $(ISO_PATH)

esmon-$(MONSYSTEM_PKGVER).$(target_cpu).md5: \
		esmon-$(MONSYSTEM_PKGVER).$(target_cpu).iso
	md5sum esmon-$(MONSYSTEM_PKGVER).$(target_cpu).iso \
		> esmon-$(MONSYSTEM_PKGVER).$(target_cpu).md5

clean-local:
	-rm -f -r $(BUILD_DIRS)
	-rm -f esmon-*.iso
	-rm -f esmon-*.md5

maintainer-clean-local:
	-rm -f -r libltdl
	-rm -f INSTALL
	-rm -f aclocal.m4
