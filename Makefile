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

rpm:
	git clean -d -x -f
	make all
	tar czvf xml_definition.tar.gz *.xml collectd.conf.all
	mkdir {BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
	mv xml_definition.tar.gz ./SOURCES/
	rpmbuild -ba --define="rev $(shell git rev-parse --short HEAD)" \
		--define="_topdir $(shell pwd)" \
		xml_definition.spec

clean:
	rm *.xml check_xml -f
	rm -fr {BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
	rm xml_definition.tar.gz -f
