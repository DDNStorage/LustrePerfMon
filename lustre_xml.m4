dnl
dnl The m4 file to automatically generate lustre definition file
dnl Authors: Li Xi <lixi at ddn.com>
dnl
dnl
include(`general_xml.m4')dnl
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
dnl $2: name of MD_STATS_ITEM
dnl $3: is first child of parent ELEMENT
define(`MD_STATS_ITEM',
	`ELEMENT($1, item, 
	`NAME($1 + 1, md_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples .+', 0)
FIELD($1 + 1, 1, $2, number, ${subpath:mdt_name}, md_stats, , derive, $2, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM
dnl $3: type of item 
dnl $4: is first child of parent ELEMENT
define(`OST_STATS_ITEM',
        `ELEMENT($1, item,
        `NAME($1 + 1, ost_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\]', 0)
FIELD($1 + 1, 1, $2, number, ${subpath:ost_name}, stats, , derive, $2, 0)', $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_IO_STATS_ITEM
dnl $3: type of item
dnl $4: is first child of parent ELEMENT
define(`OST_IO_STATS_ITEM',
        `ELEMENT($1, item,
        `NAME($1 + 1, ost_io_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\] +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ost_io, stats, derive, $2_samples, 0)
FIELD($1 + 1, 2, $2, number, ${key:hostname}, ost_io, stats, gauge, $2_min, 0)
FIELD($1 + 1, 3, $2, number, ${key:hostname}, ost_io, stats, gauge, $2_max, 0)
FIELD($1 + 1, 4, $2, number, ${key:hostname}, ost_io, stats, derive, $2_sum, 0)
FIELD($1 + 1, 5, $2, number, ${key:hostname}, ost_io, stats, derive, $2_sum_square, 0)
', $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_BRW_STATS_ITEM
dnl $3: context regular expression
dnl $4: start pattern of item
dnl $5: first field name
dnl $6: is first child of parent ELEMENT
define(`OST_BRW_STATS_ITEM',
        `ELEMENT($1, item,
        `NAME($1 + 1, ost_brw_stats_$2, 1)
CONTEXT($1 + 1, $3, 0)
PATTERN($1 + 1, `^($4):[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+\|[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+).*', 0)
FIELD($1 + 1, 1, $5, string, ${subpath:ost_name}, brw_stats, $2_${content:$5}_$5, , $5, 0)
FIELD($1 + 1, 2, read_sample, number, ${subpath:ost_name}, brw_stats, $2_${content:$5}_$5, derive, read_sample, 0)
FIELD($1 + 1, 3, read_percentage, number, ${subpath:ost_name}, brw_stats, $2_${content:$5}_$5, gauge, read_percentage, 0)
FIELD($1 + 1, 4, read_cum, number, ${subpath:ost_name}, brw_stats, $2_${content:$5}_$5, gauge, read_cum, 0)
FIELD($1 + 1, 5, write_sample, number, ${subpath:ost_name}, brw_stats, $2_${content:$5}_$5, derive, write_sample, 0)
FIELD($1 + 1, 6, write_percentage, number, ${subpath:ost_name}, brw_stats, $2_${content:$5}_$5, gauge, write_percentage, 0)
FIELD($1 + 1, 7, write_cum, number, ${subpath:ost_name}, brw_stats, $2_${content:$5}_$5, gauge, write_cum, 0)
', $6)')dnl
dnl ', $6)')dnl