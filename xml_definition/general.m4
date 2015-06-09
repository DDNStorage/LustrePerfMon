dnl
dnl The m4 file to automatically generate definition file
dnl Authors: Li Xi <lixi at ddn.com>
dnl
dnl
define(`FOR',
	`ifelse($#, 0, ``$0'',
	`ifelse(eval($2 <= $3), 1,
	`pushdef(`$1', $2)$4`'popdef(`$1')$0(`$1', incr($2), $3, `$4')')')')dnl
dnl
dnl $1: number of indent
define(`INDENT', `FOR(`x', 1, $1, `	')')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of ELEMENT
dnl $3: content of ELEMENT
dnl $4: is first child of parent element
define(`ELEMENT',
	`ifelse(eval($4 == 0), 1, INDENT($1))<$2>
INDENT($1 + 1)$3
INDENT($1)</$2>')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of ELEMENT
dnl $3: content of ELEMENT
dnl $4: is first child of parent element
define(`ELEMENT_ONELINE',
        `ifelse(eval($4 == 0), 1, INDENT($1))<$2>$3</$2>')dnl
dnl
dnl $1: number of INDENT
dnl $2: value of NAME
dnl $3: is first child of parent ELEMENT
define(`SUBPATH_TYPE',
	`ELEMENT_ONELINE($1, subpath_type, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: value of NAME
dnl $3: is first child of parent ELEMENT
define(`PATH',
	`ELEMENT_ONELINE($1, path, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: value of NAME
dnl $3: is first child of parent ELEMENT
define(`NAME',
	`ELEMENT_ONELINE($1, name, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: value of MODE
dnl $3: is first child of parent ELEMENT
define(`MODE',
	`ELEMENT_ONELINE($1, mode, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: value of STRING
dnl $3: is first child of parent ELEMENT
define(`STRING',
	`ELEMENT_ONELINE($1, string, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OPTION
dnl $3: string of OPTION
dnl $4: is first child of parent ELEMENT
define(`OPTION',
	`ELEMENT($1, option,
	`NAME($1 + 1, $2, 1)
STRING($1 + 1, $3, 0)',
	$4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: valiue of INDEX
dnl $3: is first child of parent ELEMENT
define(`INDEX',
	`ELEMENT_ONELINE($1, index, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: valiue of TYPE
dnl $3: is first child of parent ELEMENT
define(`TYPE',
	`ELEMENT_ONELINE($1, type, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: host OPTION
dnl $6: plugin OPTION
dnl $7: plugin_instance OPTION
dnl $8: type OPTION
dnl $9: type_instance OPTION
dnl $10: tsdb_name OPTION
dnl $11: tsdb_tags OPTION
dnl $12: is first child of parent ELEMENT
define(`FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
OPTION($1 + 1, host, $5, 0)
OPTION($1 + 1, plugin, $6, 0)
OPTION($1 + 1, plugin_instance, $7, 0)
OPTION($1 + 1, type, $8, 0)
OPTION($1 + 1, type_instance, $9, 0)
OPTION($1 + 1, tsdb_name, $10, 0)
OPTION($1 + 1, tsdb_tags, $11, 0)', $12)')dnl
dnl
dnl $1: number of INDENT
dnl $2: value of PATTERN
dnl $3: is first child of parent ELEMENT
define(`PATTERN',
        `ELEMENT_ONELINE($1, pattern, $2, $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of field
dnl $3: name of field
dnl $4: is first child of parent ELEMENT
define(`SUBPATH_FIELD',
	`ELEMENT($1, subpath_field,
INDEX($1+1, $2, 1)
NAME($1+1, $3, 0), $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: type of subpath
dnl $3: path value of entry
dnl $4: is first child of parent ELEMENT
define(`SUBPATH',
	`ELEMENT($1, subpath,
SUBPATH_TYPE($1+1, $2, 1)
PATH($1+1, $3, 0), $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: type of subpath
dnl $3: path value of entry
dnl $4: name of the field
dnl $5: is first child of parent ELEMENT
define(`ONE_FIELD_SUBPATH',
	`ELEMENT($1, subpath,
SUBPATH_TYPE($1+1, $2, 1)
PATH($1+1, $3, 0)
SUBPATH_FIELD($1+1, 1, $4, 0), $5)')dnl
dnl
dnl $1: number of INDENT
dnl $2: type of subpath
dnl $3: path value of entry
dnl $4: first name of the field
dnl $5: second name of the field
dnl $6: is first child of parent ELEMENT
define(`TWO_FIELD_SUBPATH',
	`ELEMENT($1, subpath,
SUBPATH_TYPE($1+1, $2, 1)
PATH($1+1, $3, 0)
SUBPATH_FIELD($1+1, 1, $4, 0)
SUBPATH_FIELD($1+1, 2, $5, 0), $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of field
dnl $3: name of item
dnl $4: pattern of item
dnl $5: type of field
dnl $6: host OPTION
dnl $7: plugin OPTION
dnl $8: plugin_instance OPTION
dnl $9: type OPTION
dnl $10: type_instance OPTION
dnl $11: tsdb_name OPTION
dnl $12: tsdb_tags OPTION
dnl $13: is first child of parent ELEMENT
define(`ONE_FIELD_ITEM',
	`ELEMENT($1, item,
NAME($1+1, $3, 1)
PATTERN($1+1, $4, 0)
FIELD($1+1, 1, $2, $5, $6, $7, $8, $9, $10, $11, $12, 0), $13)')dnl
dnl
dnl $1: number of INDENT
dnl $2: path of entry, name of field use this value
dnl $3: item name
dnl $4: item pattern
dnl $5: field type
dnl $6: host OPTION
dnl $7: plugin OPTION
dnl $8: plugin_instance OPTION
dnl $9: type OPTION
dnl $10: type_instance OPTION
dnl $11: is first child of parent ELEMENT
define(`CONSTANT_FILE_ENTRY',
	`ELEMENT($1, entry,
SUBPATH($1+1, constant, $2, 1)
MODE($1+1, file, 0)
ONE_FIELD_ITEM($1+1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 0), $11)')dnl
dnl
dnl $1: number of INDENT
dnl $2: value of CONTEXT
dnl $3: is first child of parent ELEMENT
define(`CONTEXT',
	`ELEMENT_ONELINE($1, context, $2, $3)')dnl
dnl
dnl $1: RELEASE name of the XML file
define(`HEAD',
	``<?xml version="1.0"?>

<!-- XML definition file for $1 -->
<!-- Copyright (c) 2014, DataDirect Networks, Inc. -->
<!-- Authors: Li Xi <lixi at ddn.com> -->
<!-- This file is automatically generated, do NOT edit this file directly -->

<!DOCTYPE definition [
	<!ELEMENT definition     (version,entry+)>
	<!ELEMENT version        (#PCDATA)>

	<!ELEMENT entry          (subpath,mode,item*,entry*)>
	<!ELEMENT mode           (#PCDATA)>

	<!ELEMENT subpath        (subpath_type,path,subpath_field*)>
	<!ELEMENT subpath_type   (#PCDATA)>
	<!ELEMENT path           (#PCDATA)>

	<!ELEMENT subpath_field  (index,name)>
	<!ELEMENT index          (#PCDATA)>
	<!ELEMENT name           (#PCDATA)>

	<!ELEMENT item           (name,context?,pattern,field+)>
	<!ELEMENT pattern        (#PCDATA)>
	<!ELEMENT context        (#PCDATA)>

	<!ELEMENT field          (index,name,type,option+)>
	<!ELEMENT type           (#PCDATA)>

	<!ELEMENT option         (name,string)>
	<!ELEMENT string         (#PCDATA)>
]>
'')dnl