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
dnl $11: tsdb_name OPTION
dnl $12: tsdb_tags OPTION
dnl $13: is first child of parent ELEMENT
define(`CONSTANT_FILE_ENTRY',
	`ELEMENT($1, entry,
SUBPATH($1+1, constant, $2, 1)
MODE($1+1, file, 0)
ONE_FIELD_ITEM($1+1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 0), $13)')dnl
dnl
dnl $1: number of INDENT
dnl $2: path of entry, used as field name
dnl $3: item pattern
dnl $4: plugin_instance OPTION
dnl $5: type OPTION
dnl $6: type_instance OPTION
dnl $7: tsdb_name OPTION
dnl $8: is first child of parent ELEMENT
define(`MDC_MDT_CONSTANT_FILE_ENTRY',
`CONSTANT_FILE_ENTRY($1, $2, $2, $3, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}-${subpath:mdc_tag}, $4, $5, $6, $7, 
fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index} mdc_tag=${subpath:mdc_tag}, $8)')dnl
dnl
dnl $1: number of INDENT
dnl $2: item name prefix
dnl $3: plugin OPTION
dnl $4: plugin_instance OPTION
dnl $5: type OPTION
dnl $6: is first child of parent ELEMENT
define(`THREAD_INFO_ENTRIES',
`CONSTANT_FILE_ENTRY($1, threads_max, $2_threads_max, (.+), number, ${key:hostname}, $3, $4, $5, threads_max, $2_thread_max, NA, 1)
CONSTANT_FILE_ENTRY($1, threads_min, $2_threads_min, (.+), number, ${key:hostname}, $3, $4, $5, threads_min, $2_thread_min, NA, 0)
CONSTANT_FILE_ENTRY($1, threads_started, $2_threads_started, (.+), number, ${key:hostname}, $3, $4, $5, threads_started, $2_thread_started, NA, 0)')dnl
dnl
dnl $1: number of INDENT
dnl $2: "mdt" or "ost"
dnl $3: plugin OPTION
dnl $4: is first child of parent ELEMENT
define(`FILES_KBYTES_INFO_ENTRIES',
`CONSTANT_FILE_ENTRY($1, filestotal, $2_filestotal, (.+), number, ${key:hostname}, $3, filesinfo, gauge, filestotal, $2_filesinfo_total, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 1)
CONSTANT_FILE_ENTRY($1, filesfree, $2_filesfree, (.+), number, ${key:hostname}, $3, filesinfo, gauge, filesfree, $2_filesinfo_free, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)
CONSTANT_FILE_ENTRY($1, kbytestotal, $2_kbytestotal, (.+), number, ${key:hostname}, $3, kbytesinfo, gauge, kbytestotal, $2_kbytesinfo_total, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)
CONSTANT_FILE_ENTRY($1, kbytesfree, $2_kbytesfree, (.+), number, ${key:hostname}, $3, kbytesinfo, gauge, kbytesfree, $2_kbytesinfo_free, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)
CONSTANT_FILE_ENTRY($1, kbytesavail, $2_kbytesavail, (.+), number, ${key:hostname}, $3, kbytesinfo, gauge, kbytesavail, $2_kbytesinfo_avail, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of MD_STATS_ITEM
dnl $3: is first child of parent ELEMENT
define(`MD_STATS_ITEM',
	`ELEMENT($1, item, 
	`NAME($1 + 1, md_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples .+', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}, md_stats, derive, $2, md_stats, optype=$2 fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_MD_STATS_ITEM
dnl $3: is first child of parent ELEMENT
define(`EXPORT_MD_STATS_ITEM',
	`ELEMENT($1, item,
	`NAME($1 + 1, exp_md_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples .+', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:mdt_exp_client}-${subpath:mdt_exp_type}_${subpath:fs_name}-${subpath:mdt_index}, stats, derive, $2, exp_md_stats, optype=$2 exp_client=${subpath:mdt_exp_client} exp_type=${subpath:mdt_exp_type} fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM_PREFIX
dnl $3: prefix of the regular expression
dnl $4: type of item 
dnl $5: is first child of parent ELEMENT
define(`OST_STATS_ITEM_PREFIX',
        `ELEMENT($1, item,
        `NAME($1 + 1, ost_stats_$2, 1)
PATTERN($1 + 1, `$3 +([[:digit:]]+) samples \[$4\]', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, ost_stats_samples, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $5)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM
dnl $3: type of item 
dnl $4: is first child of parent ELEMENT
define(`OST_STATS_ITEM',
        `OST_STATS_ITEM_PREFIX($1, $2, $2, $3, $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_OST_STATS_ITEM
dnl $3: type of item
dnl $4: is first child of parent ELEMENT
define(`EXPORT_OST_STATS_ITEM',
        `ELEMENT($1, item,
        `NAME($1 + 1, exp_ost_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\]', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, exp_ost_stats_samples, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM_RW
dnl $3: is first child of parent ELEMENT
define(`OST_STATS_ITEM_RW',
        `ELEMENT($1, item,
        `NAME($1 + 1, ost_stats_$2, 1)
PATTERN($1 + 1, `$2_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2_samples, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_samples, ost_stats_samples, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 2, $2_bytes, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_bytes, ost_stats_bytes, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_OST_STATS_ITEM_RW
dnl $3: is first child of parent ELEMENT
define(`EXPORT_OST_STATS_ITEM_RW',
        `ELEMENT($1, item,
        `NAME($1 + 1, exp_ost_stats_$2, 1)
PATTERN($1 + 1, `$2_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2_samples, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_samples, exp_ost_stats_samples, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 2, $2_bytes, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_bytes, exp_ost_stats_bytes, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: additional items
dnl $3: is first child of parent ELEMENT
define(`EXPORT_OST_STATS_ENTRY',
        `ELEMENT($1, entry,
        `SUBPATH($1 + 1, constant, stats, 1)
MODE($1 + 1, file, 0)
EXPORT_OST_STATS_ITEM_RW($1 + 1, read, 0)
EXPORT_OST_STATS_ITEM_RW($1 + 1, write, 0)
EXPORT_OST_STATS_ITEM($1 + 1, getattr, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, setattr, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, punch, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, sync, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, destroy, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, create, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, statfs, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, get_info, reqs, 0)
EXPORT_OST_STATS_ITEM($1 + 1, set_info_async, reqs, 0)
$2', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: additional items
dnl $3: is first child of parent ELEMENT
define(`EXPORT_MD_STATS_ENTRY',
        `ELEMENT($1, entry,
        `SUBPATH($1 + 1, constant, stats, 1)
MODE($1 + 1, file, 0)
EXPORT_MD_STATS_ITEM($1 + 1, open, 0)
EXPORT_MD_STATS_ITEM($1 + 1, close, 0)
EXPORT_MD_STATS_ITEM($1 + 1, mknod, 0)
EXPORT_MD_STATS_ITEM($1 + 1, link, 0)
EXPORT_MD_STATS_ITEM($1 + 1, unlink, 0)
EXPORT_MD_STATS_ITEM($1 + 1, mkdir, 0)
EXPORT_MD_STATS_ITEM($1 + 1, rmdir, 0)
EXPORT_MD_STATS_ITEM($1 + 1, rename, 0)
EXPORT_MD_STATS_ITEM($1 + 1, getattr, 0)
EXPORT_MD_STATS_ITEM($1 + 1, setattr, 0)
EXPORT_MD_STATS_ITEM($1 + 1, getxattr, 0)
EXPORT_MD_STATS_ITEM($1 + 1, setxattr, 0)
EXPORT_MD_STATS_ITEM($1 + 1, statfs, 0)
EXPORT_MD_STATS_ITEM($1 + 1, sync, 0)
$2', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_IO_STATS_ITEM
dnl $3: type of item
dnl $4: is first child of parent ELEMENT
define(`OST_IO_STATS_ITEM',
        `ELEMENT($1, item,
        `NAME($1 + 1, ost_io_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\] +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ost_io, stats, derive, $2_samples, ost_io_stats_$3_samples, optype=$2, 0)
FIELD($1 + 1, 2, $2, number, ${key:hostname}, ost_io, stats, gauge, $2_min, ost_io_stats_$3_min, optype=$2, 0)
FIELD($1 + 1, 3, $2, number, ${key:hostname}, ost_io, stats, gauge, $2_max, ost_io_stats_$3_max, optype=$2, 0)
FIELD($1 + 1, 4, $2, number, ${key:hostname}, ost_io, stats, derive, $2_sum, ost_io_stats_$3_sum, optype=$2, 0)
FIELD($1 + 1, 5, $2, number, ${key:hostname}, ost_io, stats, derive, $2_sum_square, ost_io_stats_$3_sum_square, optype=$2, 0)
', $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: plugin_instance OPTION
dnl $6: type OPTION
dnl $7: type_instance OPTION
dnl $8: name of OST_BRW_STATS_ITEM
dnl $9: size of the field
dnl $10: "samples" or "percentage" or "cum"
dnl $11: is first child of parent ELEMENT
define(`OST_BRW_STATS_FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, ${subpath:fs_name}-${subpath:ost_index}, 0)
OPTION($1 + 1, plugin_instance, $5, 0)
OPTION($1 + 1, type, $6, 0)
OPTION($1 + 1, type_instance, $7, 0)
OPTION($1 + 1, tsdb_name, ost_brw_stats_$8_$10, 0)
OPTION($1 + 1, tsdb_tags, field=$3 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index} size=$9, 0)', $11)')dnl
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
OST_BRW_STATS_FIELD($1 + 1, 1, $5, string, brw_stats_$2_${content:$5}_$5, , $5, $2, ${content:$5}_$5, string, 0)
OST_BRW_STATS_FIELD($1 + 1, 2, read_sample, number, brw_stats_$2_${content:$5}_$5, derive, read_sample, $2, ${content:$5}_$5, samples, 0)
OST_BRW_STATS_FIELD($1 + 1, 3, read_percentage, number, brw_stats_$2_${content:$5}_$5, gauge, read_percentage, $2, ${content:$5}_$5, percentage, 0)
OST_BRW_STATS_FIELD($1 + 1, 4, read_cum, number, brw_stats_$2_${content:$5}_$5, gauge, read_cum, $2, ${content:$5}_$5, cum, 0)
OST_BRW_STATS_FIELD($1 + 1, 5, write_sample, number, brw_stats_$2_${content:$5}_$5, derive, write_sample, $2, ${content:$5}_$5, samples, 0)
OST_BRW_STATS_FIELD($1 + 1, 6, write_percentage, number, brw_stats_$2_${content:$5}_$5, gauge, write_percentage, $2, ${content:$5}_$5, percentage, 0)
OST_BRW_STATS_FIELD($1 + 1, 7, write_cum, number, brw_stats_$2_${content:$5}_$5, gauge, write_cum, $2, ${content:$5}_$5, cum, 0)', $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: "mdt" or "ost"
dnl $7: "samples" or "bytes"
dnl $8: is first child of parent ELEMENT
define(`JOBSTAT_FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, ${subpath:fs_name}-${subpath:$6_index}, 0)
OPTION($1 + 1, plugin_instance, jobstat_${content:job_id}, 0)
OPTION($1 + 1, type, $5, 0)
OPTION($1 + 1, type_instance, $3, 0)
OPTION($1 + 1, tsdb_name, $6_jobstats_$7, 0)
OPTION($1 + 1, tsdb_tags, optype=$3 fs_name=${subpath:fs_name} $6_index=${subpath:$6_index} job_id=${content:job_id}, 0)', $8)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent ELEMENT
define(`OST_JOBSTAT_FIELD',
	`JOBSTAT_FIELD($1, $2, $3, $4, $5, ost, samples, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent ELEMENT
define(`OST_JOBSTAT_FIELD_BYTES',
	`JOBSTAT_FIELD($1, $2, $3, $4, $5, ost, bytes, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent ELEMENT
define(`MDT_JOBSTAT_FIELD',
	`JOBSTAT_FIELD($1, $2, $3, $4, $5, mdt, samples, $6)')dnl
