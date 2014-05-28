all: lustre-1.8.9.xml lustre-2.5.xml lustre-2.4.2.xml check_xml test

lustre-1.8.9.xml: lustre_xml-1.8.9.m4 lustre_xml.m4
	m4 lustre_xml-1.8.9.m4 > lustre-1.8.9.xml

lustre-2.5.xml: lustre_xml-2.5.m4 lustre_xml.m4
	m4 lustre_xml-2.5.m4 > lustre-2.5.xml

lustre-2.4.2.xml: lustre_xml-2.4.2.m4 lustre_xml.m4
	m4 lustre_xml-2.4.2.m4 > lustre-2.4.2.xml

check_xml: check_xml.c
	gcc -Wall -Werror -I/usr/include/libxml2 -lxml2 check_xml.c -o check_xml

test:	lustre-1.8.9.xml check_xml
	./check_xml lustre-1.8.9.xml > /tmp/check.log
	./check_xml lustre-2.5.xml > /tmp/check.log
	./check_xml lustre-2.4.2.xml > /tmp/check.log

clean:
	rm *.xml check_xml -f
