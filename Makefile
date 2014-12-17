all: lustre-1.8.9.xml lustre-2.5.xml lustre-ieel-2.5.xml lustre-2.4.2.xml \
	lustre-2.1.6.xml check_xml test gpfs-3.5.xml

lustre-1.8.9.xml: lustre_xml-1.8.9.m4 lustre_xml.m4 general_xml.m4
	m4 lustre_xml-1.8.9.m4 > lustre-1.8.9.xml

lustre-2.5.xml: lustre_xml-2.5.m4 lustre_xml.m4 general_xml.m4
	m4 lustre_xml-2.5.m4 > lustre-2.5.xml

lustre-ieel-2.5.xml: lustre_xml-ieel-2.5.m4 lustre_xml.m4 general_xml.m4
	m4 lustre_xml-ieel-2.5.m4 > lustre-ieel-2.5.xml

lustre-2.4.2.xml: lustre_xml-2.4.2.m4 lustre_xml.m4 general_xml.m4
	m4 lustre_xml-2.4.2.m4 > lustre-2.4.2.xml

lustre-2.1.6.xml: lustre_xml-2.1.6.m4 lustre_xml.m4 general_xml.m4
	m4 lustre_xml-2.1.6.m4 > lustre-2.1.6.xml

gpfs-3.5.xml: gpfs_xml-3.5.m4 general_xml.m4
	m4 gpfs_xml-3.5.m4 > gpfs-3.5.xml

check_xml: check_xml.c
	gcc -Wall -Werror -I/usr/include/libxml2 -lxml2 check_xml.c -o check_xml

test:	lustre-1.8.9.xml lustre-2.5.xml lustre-ieel-2.5.xml lustre-2.4.2.xml \
	lustre-2.1.6.xml gpfs-3.5.xml check_xml
	./check_xml lustre-1.8.9.xml > /tmp/check.log
	./check_xml lustre-2.5.xml > /tmp/check.log
	./check_xml lustre-ieel-2.5.xml > /tmp/check.log
	./check_xml lustre-2.4.2.xml > /tmp/check.log
	./check_xml lustre-2.1.6.xml > /tmp/check.log
	./check_xml gpfs-3.5.xml > /tmp/check.log
	python test_driver.py --xml_path lustre-1.8.9.xml --exit_on_error
	python test_driver.py --xml_path lustre-2.5.xml --exit_on_error
	python test_driver.py --xml_path lustre-ieel-2.5.xml --exit_on_error
	python test_driver.py --xml_path lustre-2.4.2.xml --exit_on_error
	python test_driver.py --xml_path lustre-2.1.6.xml --exit_on_error
	python test_driver.py --xml_path gpfs-3.5.xml --exit_on_error

rpm:
	git clean -d -x -f
	make all
	tar czvf xml_definition.tar.gz *.xml collectd.conf.all
	mkdir {BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
	mv xml_definition.tar.gz ./SOURCES/
	rpmbuild -ba --define="rev $(shell git rev-parse --short HEAD)" \
		--define="_topdir $(shell pwd)" \
		xml_definition.spec

last_commit: lustre-1.8.9.git.xml lustre-2.5.git.xml lustre-ieel-2.5.git.xml \
	     lustre-2.4.2.git.xml lustre-2.1.6.git.xml gpfs-3.5.git.xml

check_version:
	GIT_VERSION=`git log -1 --format=%H`; \
	CURRENT_VERSION=`cat current_version`; \
	if [ "$$GIT_VERSION" != "$$CURRENT_VERSION" ]; then \
		echo $$GIT_VERSION > current_version; \
	fi

current_version: check_version
	echo "";

lustre-1.8.9.git.xml: current_version
	git stash >/dev/null 2>&1
	m4 lustre_xml-1.8.9.m4 > lustre-1.8.9.git.xml
	git stash pop >/dev/null 2>&1

lustre-2.1.6.git.xml: current_version
	git stash >/dev/null 2>&1
	m4 lustre_xml-2.1.6.m4 > lustre-2.1.6.git.xml
	git stash pop >/dev/null 2>&1

lustre-2.4.2.git.xml: current_version
	git stash >/dev/null 2>&1
	m4 lustre_xml-2.4.2.m4 > lustre-2.4.2.git.xml
	git stash pop >/dev/null 2>&1

lustre-2.5.git.xml: current_version
	git stash >/dev/null 2>&1
	m4 lustre_xml-2.5.m4 > lustre-2.5.git.xml
	git stash pop >/dev/null 2>&1

lustre-ieel-2.5.git.xml: current_version
	git stash >/dev/null 2>&1
	m4 lustre_xml-ieel-2.5.m4 > lustre-ieel-2.5.git.xml
	git stash pop >/dev/null 2>&1

gpfs-3.5.git.xml: current_version
	git stash >/dev/null 2>&1
	m4 gpfs_xml-3.5.m4 > gpfs-3.5.git.xml
	git stash pop >/dev/null 2>&1

define diff_func
	@diff $(1) $(2) > $(1).change 2>&1; \
	if [ $$? -ne 0 ];then \
		echo "$(1) has changed from last commit, please check \
		     $(1).change for detail"; \
	fi
endef

git_diff: all last_commit
	$(call diff_func, lustre-1.8.9.xml, lustre-1.8.9.git.xml)
	$(call diff_func, lustre-2.1.6.xml, lustre-2.1.6.git.xml)
	$(call diff_func, lustre-2.4.2.xml, lustre-2.4.2.git.xml)
	$(call diff_func, lustre-2.5.xml, lustre-2.5.git.xml)
	$(call diff_func, lustre-ieel-2.5.xml, lustre-ieel-2.5.git.xml)
	$(call diff_func, gpfs-3.5.xml, gpfs-3.5.git.xml)

clean:
	rm *.xml *.xml.last *.xml.change check_xml -f
	rm -fr {BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
	rm xml_definition.tar.gz -f
