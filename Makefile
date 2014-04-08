all: lustre-1.8.9.xml check_xml

lustre-1.8.9.xml: lustre_xml-1.8.9.m4 lustre_xml.m4
	m4 lustre_xml-1.8.9.m4 > lustre-1.8.9.xml

check_xml: check_xml.c
	gcc -Wall -Werror -I/usr/include/libxml2 -lxml2 check_xml.c -o check_xml

test:	lustre-1.8.9.xml check_xml
	./check_xml lustre-1.8.9.xml

clean:
	rm *.xml check_xml -f
