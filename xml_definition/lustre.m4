dnl
dnl The m4 file to automatically generate lustre definition file
dnl Authors: Li Xi <lixi at ddn.com>
dnl
dnl
include(`general.m4')dnl
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
dnl $13: is first child of parent definition
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
dnl $8: is first child of parent definition
define(`MDC_MDT_CONSTANT_FILE_ENTRY',
`CONSTANT_FILE_ENTRY($1, $2, $2, $3, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}-${subpath:mdc_tag}, $4, $5, $6, $7,
fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index} mdc_tag=${subpath:mdc_tag}, $8)')dnl
dnl
dnl $1: number of INDENT
dnl $2: item name prefix
dnl $3: plugin OPTION
dnl $4: plugin_instance OPTION
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`THREAD_INFO_ENTRIES',
`CONSTANT_FILE_ENTRY($1, threads_max, $2_threads_max, (.+), number, ${key:hostname}, $3, $4, $5, threads_max, $2_thread_max, , 1)
CONSTANT_FILE_ENTRY($1, threads_min, $2_threads_min, (.+), number, ${key:hostname}, $3, $4, $5, threads_min, $2_thread_min, , 0)
CONSTANT_FILE_ENTRY($1, threads_started, $2_threads_started, (.+), number, ${key:hostname}, $3, $4, $5, threads_started, $2_thread_started, , 0)')dnl
dnl
dnl $1: number of INDENT
dnl $2: "mdt" or "ost"
dnl $3: plugin OPTION
dnl $4: is first child of parent definition
define(`FILES_KBYTES_INFO_ENTRIES',
`CONSTANT_FILE_ENTRY($1, filestotal, $2_filestotal, (.+), number, ${key:hostname}, $3, filesinfo, gauge, filestotal, $2_filesinfo_total, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 1)
CONSTANT_FILE_ENTRY($1, filesfree, $2_filesfree, (.+), number, ${key:hostname}, $3, filesinfo, gauge, filesfree, $2_filesinfo_free, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)
CONSTANT_FILE_ENTRY($1, kbytestotal, $2_kbytestotal, (.+), number, ${key:hostname}, $3, kbytesinfo, gauge, kbytestotal, $2_kbytesinfo_total, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)
CONSTANT_FILE_ENTRY($1, kbytesfree, $2_kbytesfree, (.+), number, ${key:hostname}, $3, kbytesinfo, gauge, kbytesfree, $2_kbytesinfo_free, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)
CONSTANT_FILE_ENTRY($1, kbytesavail, $2_kbytesavail, (.+), number, ${key:hostname}, $3, kbytesinfo, gauge, kbytesavail, $2_kbytesinfo_avail, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)')dnl
dnl
dnl $1: number of INDENT
dnl $2: "mdt" or "ost"
dnl $3: plugin OPTION
dnl $4: is first child of parent definition
define(`LDLM_LOCK_INFO_ENTRIES',
`CONSTANT_FILE_ENTRY($1, lock_count, $2_lock_count, (.+), number, ${key:hostname}, $3, locksinfo, gauge, lock_count, $2_lock_count, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 1)
CONSTANT_FILE_ENTRY($1, lock_timeouts, $2_lock_timeouts, (.+), number, ${key:hostname}, $3, locksinfo, gauge, lock_timeouts, $2_lock_timeouts, fs_name=${subpath:fs_name} $2_index=${subpath:$2_index}, 0)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of RECOVERY_STATUS_ITEM
dnl $3: "mdt" or "ost"
dnl $4: match pattern RegEx str
dnl $5: type of item
dnl $6: is first child of parent definition
define(`RECOVERY_STATUS_ITEM',
	`ELEMENT($1, item, 
	`NAME($1 + 1, $3_recovery_status_$2, 1)
PATTERN($1 + 1, `$2: +$4', 0)
FIELD($1 + 1, 1, $2, $5, ${key:hostname}, ${subpath:fs_name}-${subpath:$3_index}, $3_recovery_status, gauge, $2, $3_recovery_status, optype=$2 fs_name=${subpath:fs_name} $3_index=${subpath:$3_index}, 0)', $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of RECOVERY_STATUS_CONNECTED_ITEM
dnl $3: "mdt" or "ost"
dnl $4: is first child of parent definition
define(`RECOVERY_STATUS_CONNECTED_ITEM',
	`ELEMENT($1, item, 
	`NAME($1 + 1, $3_recovery_status_$2, 1)
PATTERN($1 + 1, `$2: +([[:digit:]]+)\/([[:digit:]]+)', 0)
FIELD($1 + 1, 1, connected_clients, number, ${key:hostname}, ${subpath:fs_name}-${subpath:$3_index}, $3_recovery_status, gauge, connected_clients, $3_recovery_status, optype=connected_clients fs_name=${subpath:fs_name} $3_index=${subpath:$3_index}, 0)
FIELD($1 + 1, 2, recoverable_clients, number, ${key:hostname}, ${subpath:fs_name}-${subpath:$3_index}, $3_recovery_status, gauge, recoverable_clients, $3_recovery_status, optype=recoverable_clients fs_name=${subpath:fs_name} $3_index=${subpath:$3_index}, 0)', $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of MD_STATS_ITEM
dnl $3: is first child of parent definition
define(`MD_STATS_ITEM',
	`ELEMENT($1, item, 
	`NAME($1 + 1, md_stats_$2, 1)
PATTERN($1 + 1, `^$2 +([[:digit:]]+) samples .+', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}, md_stats, derive, $2, md_stats, optype=$2 fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of MD_STATS_ITEM_V2
dnl $3: is first child of parent definition
define(`MD_STATS_ITEM_V2',
	`ELEMENT($1, item, 
	`NAME($1 + 1, md_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[usecs\] ([[:digit:]]+) ([[:digit:]]+) ([[:digit:]]+) ([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}, md_stats, derive, $2, md_stats, optype=$2 fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 2, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}, md_stats_min, derive, $2, md_stats_min, optype=$2 fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 3, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}, md_stats_max, derive, $2, md_stats_max, optype=$2 fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 4, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}, md_stats_sum, derive, $2, md_stats_sum, optype=$2 fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 5, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:mdt_index}, md_stats_sumsq, derive, $2, md_stats_sumsq, optype=$2 fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_MD_STATS_ITEM
dnl $3: is first child of parent definition
define(`EXPORT_MD_STATS_ITEM',
	`ELEMENT($1, item,
	`NAME($1 + 1, exp_md_stats_$2, 1)
PATTERN($1 + 1, `^$2 +([[:digit:]]+) samples .+', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:mdt_exp_client}-${subpath:mdt_exp_type}_${subpath:fs_name}-${subpath:mdt_index}, stats, derive, $2, exp_md_stats, optype=$2 exp_client=${subpath:mdt_exp_client} exp_type=${subpath:mdt_exp_type} fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_MD_STATS_ITEM_V2
dnl $3: is first child of parent definition
define(`EXPORT_MD_STATS_ITEM_V2',
	`ELEMENT($1, item,
	`NAME($1 + 1, exp_md_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[usecs\] +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:mdt_exp_client}-${subpath:mdt_exp_type}_${subpath:fs_name}-${subpath:mdt_index}, stats, derive, $2, exp_md_stats, optype=$2 exp_client=${subpath:mdt_exp_client} exp_type=${subpath:mdt_exp_type} fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 2, $2, number, ${key:hostname}, ${subpath:mdt_exp_client}-${subpath:mdt_exp_type}_${subpath:fs_name}-${subpath:mdt_index}, stats, derive, $2, exp_md_stats_min_latency, optype=$2 exp_client=${subpath:mdt_exp_client} exp_type=${subpath:mdt_exp_type} fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 3, $2, number, ${key:hostname}, ${subpath:mdt_exp_client}-${subpath:mdt_exp_type}_${subpath:fs_name}-${subpath:mdt_index}, stats, derive, $2, exp_md_stats_max_latency, optype=$2 exp_client=${subpath:mdt_exp_client} exp_type=${subpath:mdt_exp_type} fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 4, $2, number, ${key:hostname}, ${subpath:mdt_exp_client}-${subpath:mdt_exp_type}_${subpath:fs_name}-${subpath:mdt_index}, stats, derive, $2, exp_md_stats_sum_latency, optype=$2 exp_client=${subpath:mdt_exp_client} exp_type=${subpath:mdt_exp_type} fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)
FIELD($1 + 1, 5, $2, number, ${key:hostname}, ${subpath:mdt_exp_client}-${subpath:mdt_exp_type}_${subpath:fs_name}-${subpath:mdt_index}, stats, derive, $2, exp_md_stats_sumsq_latency, optype=$2 exp_client=${subpath:mdt_exp_client} exp_type=${subpath:mdt_exp_type} fs_name=${subpath:fs_name} mdt_index=${subpath:mdt_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM_PREFIX
dnl $3: prefix of the regular expression
dnl $4: type of item
dnl $5: is first child of parent definition
define(`OST_STATS_ITEM_PREFIX',
	`ELEMENT($1, item,
	`NAME($1 + 1, ost_stats_$2, 1)
PATTERN($1 + 1, `$3 +([[:digit:]]+) samples \[$4\]', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, ost_stats_samples, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $5)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM
dnl $3: type of item
dnl $4: is first child of parent definition
define(`OST_STATS_ITEM_V2',
	`ELEMENT($1, item,
	`NAME($1 + 1, ost_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\] +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, ost_stats_samples, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 2, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, ost_stats_min_latency, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 3, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, ost_stats_max_latency, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 4, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, ost_stats_sum_latency, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 5, $2, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, ost_stats_sumsq_latency, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
', $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM
dnl $3: type of item 
dnl $4: is first child of parent definition
define(`OST_STATS_ITEM',
	`OST_STATS_ITEM_PREFIX($1, $2, $2, $3, $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_OST_STATS_ITEM
dnl $3: type of item
dnl $4: is first child of parent definition
define(`EXPORT_OST_STATS_ITEM',
	`ELEMENT($1, item,
	    `NAME($1 + 1, exp_ost_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\]', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, exp_ost_stats_samples, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $4)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_OST_STATS_ITEM
dnl $3: type of item
dnl $4: is first child of parent definition
define(`EXPORT_OST_STATS_ITEM_V2',
	`ELEMENT($1, item,
	    `NAME($1 + 1, exp_ost_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\] +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, exp_ost_stats_samples, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 2, $2, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, exp_ost_stats_min_latency, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 3, $2, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, exp_ost_stats_max_latency, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 4, $2, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, exp_ost_stats_sum_latency, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 5, $2, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2, exp_ost_stats_sumsq_latency, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $4)')dnl
dnl $1: number of INDENT
dnl $2: name of OST_STATS_ITEM_RW
dnl $3: is first child of parent definition
define(`OST_STATS_ITEM_RW',
	`ELEMENT($1, item,
	`NAME($1 + 1, ost_stats_$2, 1)
PATTERN($1 + 1, `$2_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2_samples, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_samples, ost_stats_samples, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 2, $2_bytes, number, ${key:hostname}, ${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_bytes, ost_stats_bytes, optype=$2 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXPORT_OST_STATS_ITEM_RW
dnl $3: is first child of parent definition
define(`EXPORT_OST_STATS_ITEM_RW',
	`ELEMENT($1, item,
	`NAME($1 + 1, exp_ost_stats_$2, 1)
PATTERN($1 + 1, `$2_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $2_samples, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_samples, exp_ost_stats_samples, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)
FIELD($1 + 1, 2, $2_bytes, number, ${key:hostname}, ${subpath:ost_exp_client}-${subpath:ost_exp_type}_${subpath:fs_name}-${subpath:ost_index}, stats, derive, $2_bytes, exp_ost_stats_bytes, optype=$2 exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type} fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: additional items
dnl $3: is first child of parent definition
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
dnl $3: is first child of parent definition
define(`EXPORT_OST_STATS_ENTRY_V2',
	`ELEMENT($1, entry,
	`SUBPATH($1 + 1, constant, stats, 1)
MODE($1 + 1, file, 0)
EXPORT_OST_STATS_ITEM_RW($1 + 1, read, 0)
EXPORT_OST_STATS_ITEM_RW($1 + 1, write, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, getattr, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, setattr, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, punch, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, sync, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, destroy, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, create, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, statfs, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, get_info, usecs, 0)
EXPORT_OST_STATS_ITEM_V2($1 + 1, set_info_async, usecs, 0)
$2', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: additional items
dnl $3: is first child of parent definition
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
EXPORT_MD_STATS_ITEM($1 + 1, samedir_rename, 0)
EXPORT_MD_STATS_ITEM($1 + 1, crossdir_rename, 0)
$2', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: additional items
dnl $3: is first child of parent definition
define(`EXPORT_MD_STATS_ENTRY_V2',
	`ELEMENT($1, entry,
	`SUBPATH($1 + 1, constant, stats, 1)
MODE($1 + 1, file, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, open, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, close, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, mknod, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, link, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, unlink, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, mkdir, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, rmdir, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, rename, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, getattr, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, setattr, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, getxattr, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, setxattr, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, statfs, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, sync, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, samedir_rename, 0)
EXPORT_MD_STATS_ITEM_V2($1 + 1, crossdir_rename, 0)
$2', $3)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of SERVICE_STATS_ITEM
dnl $3: type of item
dnl $4: unit of the item
dnl $5: is first child of parent definition
define(`SERVICE_STATS_ITEM',
	`ELEMENT($1, item,
	`NAME($1 + 1, $2_stats_$3, 1)
PATTERN($1 + 1, `$3 +([[:digit:]]+) samples \[$4\] +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, $3, number, ${key:hostname}, $2, stats, gauge, $3_samples, $2_stats_$3_samples, , 0)
FIELD($1 + 1, 2, $3, number, ${key:hostname}, $2, stats, gauge, $3_min, $2_stats_$3_min, , 0)
FIELD($1 + 1, 3, $3, number, ${key:hostname}, $2, stats, gauge, $3_max, $2_stats_$3_max, , 0)
FIELD($1 + 1, 4, $3, number, ${key:hostname}, $2, stats, gauge, $3_sum, $2_stats_$3_sum, , 0)
FIELD($1 + 1, 5, $3, number, ${key:hostname}, $2, stats, gauge, $3_sum_square, $2_stats_$3_sum_square, , 0)
', $5)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of SERVICE_STATS_MEAN
dnl $3: type of item
dnl $4: unit of the stat, not used currently
define(`SERVICE_STATS_MEAN',
	`MATH_ENTRY($1, $2_stats_$3_sum, /, $2_stats_$3_samples, $2_stats_$3_mean, $3_mean, 1)
MATH_ENTRY($1, $2_stats_$3_sum_square, /, $2_stats_$3_samples, $2_stats_$3_mean_square, $3_mean_square, 0)')dnl
dnl
dnl $1: number of INDENT
dnl $2: type of item
dnl $3: unit of the stat, not used currently
define(`CLIENT_STATS_MEAN',
	`MATH_ENTRY($1, client_stats_$2_sum, /, client_stats_$2_samples, client_stats_$2_mean, $2_mean, 1)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: plugin OPTION
dnl $6: plugin_instance OPTION
dnl $7: type OPTION
dnl $8: type_instance OPTION
dnl $9: tsdb_name OPTION
dnl $10: tsdb_index OPTION
dnl $11: size of the field
dnl $12: is first child of parent definition
define(`OST_BRW_STATS_FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, $5, 0)
OPTION($1 + 1, plugin_instance, $6, 0)
OPTION($1 + 1, type, $7, 0)
OPTION($1 + 1, type_instance, $8, 0)
OPTION($1 + 1, tsdb_name, $9, 0)
OPTION($1 + 1, tsdb_tags, field=$3 $10 size=$11, 0)', $12)')dnl
dnl
define(`OST_COMMON_INDEX',
`fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}')dnl
dnl
define(`OST_COMMON_PLUGIN',
`${subpath:fs_name}-${subpath:ost_index}')dnl
dnl
define(`EXP_COMMON_INDEX',
`exp_client=${subpath:ost_exp_client} exp_type=${subpath:ost_exp_type}')dnl
dnl
define(`EXP_COMMON_PLUGIN',
`${subpath:ost_exp_client}-${subpath:ost_exp_type}')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of OST_BRW_STATS_ITEM
dnl $3: context regular expression
dnl $4: start pattern of item
dnl $5: first field name
dnl $6: is first child of parent definition
define(`OST_BRW_STATS_ITEM',
	`ELEMENT($1, item,
	`NAME($1 + 1, ost_brw_stats_$2, 1)
CONTEXT($1 + 1, $3, 0)
PATTERN($1 + 1, `^($4):[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+\|[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+).*', 0)
OST_BRW_STATS_FIELD($1 + 1, 1, $5, string, OST_COMMON_PLUGIN, brw_stats_$2_${content:$5}_$5, , $5, ost_brw_stats_$2_string, OST_COMMON_INDEX, ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 2, read_sample, number, OST_COMMON_PLUGIN, brw_stats_$2_${content:$5}_$5, derive, read_sample, ost_brw_stats_$2_samples, OST_COMMON_INDEX, ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 3, read_percentage, number, OST_COMMON_PLUGIN, brw_stats_$2_${content:$5}_$5, gauge, read_percentage, ost_brw_stats_$2_percentage, OST_COMMON_INDEX, ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 4, read_cum, number, OST_COMMON_PLUGIN, brw_stats_$2_${content:$5}_$5, gauge, read_cum, ost_brw_stats_$2_cum, OST_COMMON_INDEX, ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 5, write_sample, number, OST_COMMON_PLUGIN, brw_stats_$2_${content:$5}_$5, derive, write_sample, ost_brw_stats_$2_samples, OST_COMMON_INDEX, ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 6, write_percentage, number, OST_COMMON_PLUGIN, brw_stats_$2_${content:$5}_$5, gauge, write_percentage, ost_brw_stats_$2_percentage, OST_COMMON_INDEX, ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 7, write_cum, number, OST_COMMON_PLUGIN, brw_stats_$2_${content:$5}_$5, gauge, write_cum, ost_brw_stats_$2_cum, OST_COMMON_INDEX, ${content:$5}_$5, 0)', $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of EXP_OST_BRW_STATS_ITEM
dnl $3: context regular expression
dnl $4: start pattern of item
dnl $5: first field name
dnl $6: is first child of parent definition
define(`EXP_OST_BRW_STATS_ITEM',
	`ELEMENT($1, item,
	`NAME($1 + 1, exp_ost_brw_stats_$2, 1)
CONTEXT($1 + 1, $3, 0)
PATTERN($1 + 1, `^($4):[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+\|[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+)[[:blank:]]+([[:digit:]]+).*', 0)
OST_BRW_STATS_FIELD($1 + 1, 1, $5, string, EXP_COMMON_PLUGIN()-OST_COMMON_PLUGIN(), brw_stats_$2_${content:$5}_$5, , $5, exp_ost_brw_stats_$2_string, EXP_COMMON_INDEX() OST_COMMON_INDEX(), ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 2, read_sample, number, EXP_COMMON_PLUGIN()-OST_COMMON_PLUGIN(), brw_stats_$2_${content:$5}_$5, derive, read_sample, exp_ost_brw_stats_$2_samples, EXP_COMMON_INDEX() OST_COMMON_INDEX(), ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 3, read_percentage, number, EXP_COMMON_PLUGIN()-OST_COMMON_PLUGIN(), brw_stats_$2_${content:$5}_$5, gauge, read_percentage, exp_ost_brw_stats_$2_percentage, EXP_COMMON_INDEX() OST_COMMON_INDEX(), ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 4, read_cum, number, EXP_COMMON_PLUGIN()-OST_COMMON_PLUGIN(), brw_stats_$2_${content:$5}_$5, gauge, read_cum, exp_ost_brw_stats_$2_cum, EXP_COMMON_INDEX() OST_COMMON_INDEX(), ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 5, write_sample, number, EXP_COMMON_PLUGIN()-OST_COMMON_PLUGIN(), brw_stats_$2_${content:$5}_$5, derive, write_sample, exp_ost_brw_stats_$2_samples, EXP_COMMON_INDEX() OST_COMMON_INDEX(), ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 6, write_percentage, number, EXP_COMMON_PLUGIN()-OST_COMMON_PLUGIN(), brw_stats_$2_${content:$5}_$5, gauge, write_percentage, exp_ost_brw_stats_$2_percentage, EXP_COMMON_INDEX() OST_COMMON_INDEX(), ${content:$5}_$5, 0)
OST_BRW_STATS_FIELD($1 + 1, 7, write_cum, number, EXP_COMMON_PLUGIN()-OST_COMMON_PLUGIN(), brw_stats_$2_${content:$5}_$5, gauge, write_cum, exp_ost_brw_stats_$2_cum, EXP_COMMON_INDEX() OST_COMMON_INDEX(), ${content:$5}_$5, 0)', $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: "mdt" or "ost"
dnl $7: "samples" or "bytes"
dnl $8: is first child of parent definition
define(`JOBSTAT_FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
FIRST_VALUE($1 + 1, 0, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, ${subpath:fs_name}-${subpath:$6_index}, 0)
OPTION($1 + 1, plugin_instance, jobstat_${content:job_id}, 0)
OPTION($1 + 1, type, $5, 0)
OPTION($1 + 1, type_instance, $3, 0)
OPTION($1 + 1, tsdb_name, $6_jobstats_$7, 0)
OPTION($1 + 1, tsdb_tags, optype=$3 fs_name=${subpath:fs_name} $6_index=${subpath:$6_index} job_id=${content:job_id}, 0)', $8)')dnl
dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: "mdt" or "ost"
dnl $7: "samples" or "bytes"
dnl $8: is first child of parent definition
dnl $9: type of latency
define(`JOBSTAT_FIELD_V2',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
FIRST_VALUE($1 + 1, 0, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, ${subpath:fs_name}-${subpath:$6_index}, 0)
OPTION($1 + 1, plugin_instance, jobstat_${content:job_id}, 0)
OPTION($1 + 1, type, $5, 0)
OPTION($1 + 1, type_instance, $3, 0)
OPTION($1 + 1, tsdb_name, $6_jobstats_$9, 0)
OPTION($1 + 1, tsdb_tags, optype=$3 fs_name=${subpath:fs_name} $6_index=${subpath:$6_index} job_id=${content:job_id}, 0)', $8)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`OST_JOBSTAT_FIELD',
	`JOBSTAT_FIELD($1, $2, $3, $4, $5, ost, samples, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`OST_JOBSTAT_FIELD_BYTES',
	`JOBSTAT_FIELD($1, $2, $3, $4, $5, ost, bytes, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: ost or mdt
dnl $7: is first child of parent definition
define(`JOBSTAT_FIELD_META_OPERATIONS',
	`JOBSTAT_FIELD($1, $2, $3, $4, $5, $6, samples, $7)
	 JOBSTAT_FIELD_V2($1, eval(`$2 + 1'), $3, $4, $5, $6, $3, $7, min)
	 JOBSTAT_FIELD_V2($1, eval(`$2 + 2'), $3, $4, $5, $6, $3, $7, max)
	 JOBSTAT_FIELD_V2($1, eval(`$2 + 3'), $3, $4, $5, $6, $3, $7, sum)
	 JOBSTAT_FIELD_V2($1, eval(`$2 + 4'), $3, $4, $5, $6, $3, $7, sumsq)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`MDT_JOBSTAT_FIELD',
	`JOBSTAT_FIELD($1, $2, $3, $4, $5, mdt, samples, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: "mdt" or "ost"
dnl $7: "samples" or "kbytes"
dnl $8: "user", "group" or "project"
dnl $9: is first child of parent definition
define(`ACCTQUOTA_FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, ${subpath:fs_name}-${subpath:$6_index}, 0)
OPTION($1 + 1, plugin_instance, acct$8_${content:id}, 0)
OPTION($1 + 1, type, $5, 0)
OPTION($1 + 1, type_instance, $3, 0)
OPTION($1 + 1, tsdb_name, $6_acct$8_$7, 0)
OPTION($1 + 1, tsdb_tags, optype=$3 fs_name=${subpath:fs_name} $6_index=${subpath:$6_index} $8_id=${content:id}, 0)', $9)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`MDT_ACCTUSER_FIELD',
	`ACCTQUOTA_FIELD($1, $2, $3, $4, $5, mdt, samples, user, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`OST_ACCTUSER_FIELD',
	`ACCTQUOTA_FIELD($1, $2, $3, $4, $5, ost, samples, user, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`MDT_ACCTGROUP_FIELD',
	`ACCTQUOTA_FIELD($1, $2, $3, $4, $5, mdt, samples, group, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`OST_ACCTGROUP_FIELD',
	`ACCTQUOTA_FIELD($1, $2, $3, $4, $5, ost, samples, group, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`MDT_ACCTPROJECT_FIELD',
	`ACCTQUOTA_FIELD($1, $2, $3, $4, $5, mdt, samples, project, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
dnl $6: is first child of parent definition
define(`OST_ACCTPROJECT_FIELD',
	`ACCTQUOTA_FIELD($1, $2, $3, $4, $5, ost, samples, project, $6)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
define(`LDLM_STATS_FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, ${subpath:fs_name}-${subpath:ost_index}, 0)
OPTION($1 + 1, plugin_instance, ldlm_stats_$3, 0)
OPTION($1 + 1, type, $5, 0)
OPTION($1 + 1, type_instance, $3, 0)
OPTION($1 + 1, tsdb_name, ldlm_stats, 0)
OPTION($1 + 1, tsdb_tags, optype=$3 fs_name=${subpath:fs_name} ost_index=${subpath:ost_index}, 0)', 1)')dnl
dnl
dnl $1: number of INDENT
dnl $2: index of FIELD
dnl $3: name of FIELD
dnl $4: type of FIELD
dnl $5: type OPTION
define(`CLIENT_STATS_FIELD',
	`ELEMENT($1, field,
	`INDEX($1 + 1, $2, 1)
NAME($1 + 1, $3, 0)
TYPE($1 + 1, $4, 0)
OPTION($1 + 1, host, ${key:hostname}, 0)
OPTION($1 + 1, plugin, ${subpath:fs_name}-${subpath:client_uuid}, 0)
OPTION($1 + 1, plugin_instance, client_stats, 0)
OPTION($1 + 1, type, $5, 0)
OPTION($1 + 1, type_instance, $3, 0)
OPTION($1 + 1, tsdb_name, client_stats_$3, 0)
OPTION($1 + 1, tsdb_tags, fs_name=${subpath:fs_name} client_uuid=${subpath:client_uuid}, 0)', 0)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of CLIENT_STATS_ITEM
dnl $3: unit of ITEM
define(`CLIENT_STATS_ITEM_FOUR',
	`ELEMENT($1, item,
	`NAME($1 + 1, client_stats_$2, 1)
PATTERN($1 + 1, `$2 +([[:digit:]]+) samples \[$3\] ([[:digit:]]+) ([[:digit:]]+) ([[:digit:]]+)', 0)
CLIENT_STATS_FIELD($1 + 1, 1, $2_samples, number, gauge)
CLIENT_STATS_FIELD($1 + 1, 2, $2_min, number, gauge)
CLIENT_STATS_FIELD($1 + 1, 3, $2_max, number, gauge)
CLIENT_STATS_FIELD($1 + 1, 4, $2_sum, number, gauge)
', 1)')dnl
dnl
dnl $1: number of INDENT
dnl $2: name of CLIENT_STATS_ITEM
dnl $3: unit of ITEM
define(`CLIENT_STATS_ITEM_ONE',
	`ELEMENT($1, item,
	`NAME($1 + 1, client_stats_$2, 1)
PATTERN($1 + 1, `^$2 +([[:digit:]]+) samples \[$3\]', 0)
CLIENT_STATS_FIELD($1 + 1, 1, $2_samples, number, gauge)
', 1)')dnl
dnl
define(`LUSTRE2_12_XML_ENTRIES',
`
	MATH_ENTRY(1, mdt_filesinfo_total, -, mdt_filesinfo_free, mdt_filesinfo_used, filesused, 1)
	MATH_ENTRY(1, mdt_kbytesinfo_total, -, mdt_kbytesinfo_free, mdt_kbytesinfo_used, kbytesused, 1)
	MATH_ENTRY(1, ost_filesinfo_total, -, ost_filesinfo_free, ost_filesinfo_used, filesused, 1)
	MATH_ENTRY(1, ost_kbytesinfo_total, -, ost_kbytesinfo_free, ost_kbytesinfo_used, kbytesused, 1)
	SERVICE_STATS_MEAN(1, mdt, req_waittime, usec)
	SERVICE_STATS_MEAN(1, mdt, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, mdt, req_active, reqs)
	SERVICE_STATS_MEAN(1, mdt, req_timeout, sec)
	SERVICE_STATS_MEAN(1, mdt, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, mdt, ldlm_ibits_enqueue, reqs)
	SERVICE_STATS_MEAN(1, mdt, mds_getattr, usec)
	SERVICE_STATS_MEAN(1, mdt, mds_connect, usec)
	SERVICE_STATS_MEAN(1, mdt, mds_get_root, usec)
	SERVICE_STATS_MEAN(1, mdt, mds_statfs, usec)
	SERVICE_STATS_MEAN(1, mdt, mds_getxattr, usec)
	SERVICE_STATS_MEAN(1, mdt, obd_ping, usec)
	SERVICE_STATS_MEAN(1, mdt_readpage, req_waittime, usec)
	SERVICE_STATS_MEAN(1, mdt_readpage, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, mdt_readpage, req_active, reqs)
	SERVICE_STATS_MEAN(1, mdt_readpage, req_timeout, sec)
	SERVICE_STATS_MEAN(1, mdt_readpage, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, mdt_readpage, mds_close, usec)
	SERVICE_STATS_MEAN(1, mdt_readpage, mds_readpage, usec)
	SERVICE_STATS_MEAN(1, mdt_setattr, req_waittime, usec)
	SERVICE_STATS_MEAN(1, mdt_setattr, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, mdt_setattr, req_active, reqs)
	SERVICE_STATS_MEAN(1, mdt_setattr, req_timeout, sec)
	SERVICE_STATS_MEAN(1, mdt_setattr, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, mdt_fld, req_waittime, usec)
	SERVICE_STATS_MEAN(1, mdt_fld, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, mdt_fld, req_active, reqs)
	SERVICE_STATS_MEAN(1, mdt_fld, req_timeout, sec)
	SERVICE_STATS_MEAN(1, mdt_fld, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, mdt_out, req_waittime, usec)
	SERVICE_STATS_MEAN(1, mdt_out, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, mdt_out, req_active, reqs)
	SERVICE_STATS_MEAN(1, mdt_out, req_timeout, sec)
	SERVICE_STATS_MEAN(1, mdt_out, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, mdt_seqm, req_waittime, usec)
	SERVICE_STATS_MEAN(1, mdt_seqm, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, mdt_seqm, req_active, reqs)
	SERVICE_STATS_MEAN(1, mdt_seqm, req_timeout, sec)
	SERVICE_STATS_MEAN(1, mdt_seqm, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, mdt_seqs, req_waittime, usec)
	SERVICE_STATS_MEAN(1, mdt_seqs, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, mdt_seqs, req_active, reqs)
	SERVICE_STATS_MEAN(1, mdt_seqs, req_timeout, sec)
	SERVICE_STATS_MEAN(1, mdt_seqs, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, ost, req_waittime, usec)
	SERVICE_STATS_MEAN(1, ost, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, ost, req_active, reqs)
	SERVICE_STATS_MEAN(1, ost, req_timeout, sec)
	SERVICE_STATS_MEAN(1, ost, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, ost_io, req_waittime, usec)
	SERVICE_STATS_MEAN(1, ost_io, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, ost_io, req_active, reqs)
	SERVICE_STATS_MEAN(1, ost_io, req_timeout, sec)
	SERVICE_STATS_MEAN(1, ost_io, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, ost_io, ost_read, usec)
	SERVICE_STATS_MEAN(1, ost_io, ost_write, usec)
	SERVICE_STATS_MEAN(1, ost_io, ost_punch, usec)
	SERVICE_STATS_MEAN(1, ost_create, req_waittime, usec)
	SERVICE_STATS_MEAN(1, ost_create, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, ost_create, req_active, reqs)
	SERVICE_STATS_MEAN(1, ost_create, req_timeout, sec)
	SERVICE_STATS_MEAN(1, ost_create, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, ost_seq, req_waittime, usec)
	SERVICE_STATS_MEAN(1, ost_seq, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, ost_seq, req_active, reqs)
	SERVICE_STATS_MEAN(1, ost_seq, req_timeout, sec)
	SERVICE_STATS_MEAN(1, ost_seq, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, ldlm_canceld, req_waittime, usec)
	SERVICE_STATS_MEAN(1, ldlm_canceld, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, ldlm_canceld, req_active, reqs)
	SERVICE_STATS_MEAN(1, ldlm_canceld, req_timeout, sec)
	SERVICE_STATS_MEAN(1, ldlm_canceld, reqbuf_avail, bufs)
	SERVICE_STATS_MEAN(1, ldlm_cbd, req_waittime, usec)
	SERVICE_STATS_MEAN(1, ldlm_cbd, req_qdepth, reqs)
	SERVICE_STATS_MEAN(1, ldlm_cbd, req_active, reqs)
	SERVICE_STATS_MEAN(1, ldlm_cbd, req_timeout, sec)
	SERVICE_STATS_MEAN(1, ldlm_cbd, reqbuf_avail, bufs)
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>/proc/fs/lustre</path>
		</subpath>
		<mode>directory</mode>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>osd-ldiskfs</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+)-(MDT[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>fs_name</name>
					</subpath_field>
					<subpath_field>
						<index>2</index>
						<name>mdt_index</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				FILES_KBYTES_INFO_ENTRIES(4, mdt, ${subpath:fs_name}-${subpath:mdt_index}, 1)
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>quota_slave</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						SUBPATH(6, constant, acct_user, 1)
						MODE(6, file, 1)
						<item>
							<name>mdt_acctuser</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							MDT_ACCTUSER_FIELD(7, 1, id, string, gauge, 1)
							MDT_ACCTUSER_FIELD(7, 2, usage_inodes, number, gauge, 1)
							MDT_ACCTUSER_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_group, 1)
						MODE(6, file, 1)
						<item>
							<name>mdt_acctgroup</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							MDT_ACCTGROUP_FIELD(7, 1, id, string, gauge, 1)
							MDT_ACCTGROUP_FIELD(7, 2, usage_inodes, number, gauge, 1)
							MDT_ACCTGROUP_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_project, 1)
						MODE(6, file, 1)
						<item>
							<name>mdt_acctproject</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							MDT_ACCTPROJECT_FIELD(7, 1, id, string, gauge, 1)
							MDT_ACCTPROJECT_FIELD(7, 2, usage_inodes, number, gauge, 1)
							MDT_ACCTPROJECT_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
				</entry>
			</entry>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+)-(OST[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>fs_name</name>
					</subpath_field>
					<subpath_field>
						<index>2</index>
						<name>ost_index</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				FILES_KBYTES_INFO_ENTRIES(4, ost, ${subpath:fs_name}-${subpath:ost_index}, 1)
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>brw_stats</path>
					</subpath>
					<mode>file</mode>
					OST_BRW_STATS_ITEM(5, rpc_bulk, ^pages per bulk .+
(.+
)*$, [[:digit:]]+[KM]?, pages, 1)
					OST_BRW_STATS_ITEM(5, page_discontiguous_rpc, ^discontiguous pages .+
(.+
)*$, [[:digit:]]+[KM]?, pages, 1)
					OST_BRW_STATS_ITEM(5, block_discontiguous_rpc, ^discontiguous blocks .+
(.+
)*$, [[:digit:]]+[KM]?, blocks, 1)
					OST_BRW_STATS_ITEM(5, fragmented_io, ^disk fragmented .+
(.+
)*$, [[:digit:]]+[KM]?, fragments, 1)
					OST_BRW_STATS_ITEM(5, io_in_flight, ^disk I/Os .+
(.+
)*$, [[:digit:]]+[KM]?, ios, 1)
					OST_BRW_STATS_ITEM(5, io_time, ^I/O time .+
(.+
)*$, [[:digit:]]+[KM]?, milliseconds, 1)
					OST_BRW_STATS_ITEM(5, io_size, ^disk I/O size .+
(.+
)*$, [[:digit:]]+[KM]?, Bytes, 1)
				</entry>
				<entry>
					SUBPATH(5, constant, quota_slave, 1)
					MODE(5, directory, 1)
					<entry>
						SUBPATH(6, constant, acct_user, 1)
						MODE(6, file, 1)
						<item>
							<name>ost_acctuser</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							OST_ACCTUSER_FIELD(7, 1, id, string, gauge, 1)
							OST_ACCTUSER_FIELD(7, 2, usage_inodes, number, gauge, 1)
							OST_ACCTUSER_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_group, 1)
						MODE(6, file, 1)
						<item>
							<name>ost_acctgroup</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							OST_ACCTGROUP_FIELD(7, 1, id, string, gauge, 1)
							OST_ACCTGROUP_FIELD(7, 2, usage_inodes, number, gauge, 1)
							OST_ACCTGROUP_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_project, 1)
						MODE(6, file, 1)
						<item>
							<name>ost_acctproject</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							OST_ACCTPROJECT_FIELD(7, 1, id, string, gauge, 1)
							OST_ACCTPROJECT_FIELD(7, 2, usage_inodes, number, gauge, 1)
							OST_ACCTPROJECT_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>osd-zfs</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+)-(MDT[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>fs_name</name>
					</subpath_field>
					<subpath_field>
						<index>2</index>
						<name>mdt_index</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>quota_slave</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						SUBPATH(6, constant, acct_user, 1)
						MODE(6, file, 1)
						<item>
							<name>zfs_mdt_acctuser</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							MDT_ACCTUSER_FIELD(7, 1, id, string, gauge, 1)
							MDT_ACCTUSER_FIELD(7, 2, usage_inodes, number, gauge, 1)
							MDT_ACCTUSER_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_group, 1)
						MODE(6, file, 1)
						<item>
							<name>zfs_mdt_acctgroup</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							MDT_ACCTGROUP_FIELD(7, 1, id, string, gauge, 1)
							MDT_ACCTGROUP_FIELD(7, 2, usage_inodes, number, gauge, 1)
							MDT_ACCTGROUP_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_project, 1)
						MODE(6, file, 1)
						<item>
							<name>zfs_mdt_acctproject</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							MDT_ACCTPROJECT_FIELD(7, 1, id, string, gauge, 1)
							MDT_ACCTPROJECT_FIELD(7, 2, usage_inodes, number, gauge, 1)
							MDT_ACCTPROJECT_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
				</entry>
			</entry>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+)-(OST[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>fs_name</name>
					</subpath_field>
					<subpath_field>
						<index>2</index>
						<name>ost_index</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					SUBPATH(5, constant, quota_slave, 1)
					MODE(5, directory, 1)
					<entry>
						SUBPATH(6, constant, acct_user, 1)
						MODE(6, file, 1)
						<item>
							<name>zfs_ost_acctuser</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							OST_ACCTUSER_FIELD(7, 1, id, string, gauge, 1)
							OST_ACCTUSER_FIELD(7, 2, usage_inodes, number, gauge, 1)
							OST_ACCTUSER_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_group, 1)
						MODE(6, file, 1)
						<item>
							<name>zfs_ost_acctgroup</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							OST_ACCTGROUP_FIELD(7, 1, id, string, gauge, 1)
							OST_ACCTGROUP_FIELD(7, 2, usage_inodes, number, gauge, 1)
							OST_ACCTGROUP_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
					<entry>
						SUBPATH(6, constant, acct_project, 1)
						MODE(6, file, 1)
						<item>
							<name>zfs_ost_acctproject</name>
							<pattern>- +id: +(.+)
  usage: +\{ inodes: +([[:digit:]]+), kbytes: +([[:digit:]]+).+</pattern>
							OST_ACCTPROJECT_FIELD(7, 1, id, string, gauge, 1)
							OST_ACCTPROJECT_FIELD(7, 2, usage_inodes, number, gauge, 1)
							OST_ACCTPROJECT_FIELD(7, 3, usage_kbytes, number, gauge, 1)
						</item>
					</entry>
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>mdt</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+)-(MDT[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>fs_name</name>
					</subpath_field>
					<subpath_field>
						<index>2</index>
						<name>mdt_index</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>recovery_status</path>
					</subpath>
					<mode>file</mode>
					RECOVERY_STATUS_ITEM(5, recovery_start, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, recovery_duration, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_CONNECTED_ITEM(5, completed_clients, mdt, 1)
					RECOVERY_STATUS_ITEM(5, replayed_requests, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, last_transno, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, time_remaining, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_CONNECTED_ITEM(5, connected_clients, mdt, 1)
					RECOVERY_STATUS_ITEM(5, req_replay_clients, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, lock_replay_clients, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, evicted_clients, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, queued_requests, mdt, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, next_transno, mdt, ([[:digit:]]+), number, 1)
				</entry>
				<entry>
					<!-- mds_stats_counter_init() -->
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>md_stats</path>
					</subpath>
					<mode>file</mode>
					MD_STATS_ITEM(5, open, 1)
					MD_STATS_ITEM(5, close, 1)
					MD_STATS_ITEM(5, mknod, 1)
					MD_STATS_ITEM(5, link, 1)
					MD_STATS_ITEM(5, unlink, 1)
					MD_STATS_ITEM(5, mkdir, 1)
					MD_STATS_ITEM(5, rmdir, 1)
					MD_STATS_ITEM(5, rename, 1)
					MD_STATS_ITEM(5, getattr, 1)
					MD_STATS_ITEM(5, setattr, 1)
					MD_STATS_ITEM(5, getxattr, 1)
					MD_STATS_ITEM(5, setxattr, 1)
					MD_STATS_ITEM(5, statfs, 1)
					MD_STATS_ITEM(5, sync, 1)
				</entry>
				<entry>
					SUBPATH(5, constant, exports, 1)
					MODE(5, directory, 1)
					<entry>
						TWO_FIELD_SUBPATH(6, regular_expression, (.+)@(.+), mdt_exp_client, mdt_exp_type, 1)
						MODE(6, directory, 1)
						EXPORT_MD_STATS_ENTRY(6, , 1)
					</entry>
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>job_stats</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>mdt_jobstats</name>
						<pattern>- +job_id: +(.+)
 +snapshot_time: +.+
  open: +\{ samples: +([[:digit:]]+).+
  close: +\{ samples: +([[:digit:]]+).+
  mknod: +\{ samples: +([[:digit:]]+).+
  link: +\{ samples: +([[:digit:]]+).+
  unlink: +\{ samples: +([[:digit:]]+).+
  mkdir: +\{ samples: +([[:digit:]]+).+
  rmdir: +\{ samples: +([[:digit:]]+).+
  rename: +\{ samples: +([[:digit:]]+).+
  getattr: +\{ samples: +([[:digit:]]+).+
  setattr: +\{ samples: +([[:digit:]]+).+
  getxattr: +\{ samples: +([[:digit:]]+).+
  setxattr: +\{ samples: +([[:digit:]]+).+
  statfs: +\{ samples: +([[:digit:]]+).+
  sync: +\{ samples: +([[:digit:]]+).+
  samedir_rename: +\{ samples: +([[:digit:]]+).+
  crossdir_rename: +\{ samples: +([[:digit:]]+).+</pattern>
						MDT_JOBSTAT_FIELD(6, 1, job_id, string, derive, 1)
						MDT_JOBSTAT_FIELD(6, 2, open, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 3, close, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 4, mknod, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 5, link, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 6, unlink, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 7, mkdir, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 8, rmdir, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 9, rename, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 10, getattr, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 11, setattr, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 12, getxattr, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 13, setxattr, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 14, statfs, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 15, sync, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 16, samedir_rename, number, derive, 1)
						MDT_JOBSTAT_FIELD(6, 17, crossdir_rename, number, derive, 1)
					</item>
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>obdfilter</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+)-(OST[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>fs_name</name>
					</subpath_field>
					<subpath_field>
						<index>2</index>
						<name>ost_index</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>recovery_status</path>
					</subpath>
					<mode>file</mode>
					RECOVERY_STATUS_ITEM(5, recovery_start, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, recovery_duration, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_CONNECTED_ITEM(5, completed_clients, ost, 1)
					RECOVERY_STATUS_ITEM(5, replayed_requests, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, last_transno, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, time_remaining, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_CONNECTED_ITEM(5, connected_clients, ost, 1)
					RECOVERY_STATUS_ITEM(5, req_replay_clients, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, lock_replay_clients, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, evicted_clients, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, queued_requests, ost, ([[:digit:]]+), number, 1)
					RECOVERY_STATUS_ITEM(5, next_transno, ost, ([[:digit:]]+), number, 1)
				</entry>
				<entry>
					<!-- filter_setup().
					     There are a lot of counter, only defined part of them here
					-->
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>stats</path>
					</subpath>
					<mode>file</mode>
					OST_STATS_ITEM_RW(5, read, 1)
					OST_STATS_ITEM_RW(5, write, 1)
					OST_STATS_ITEM(5, getattr, reqs, 1)
					OST_STATS_ITEM(5, setattr, reqs, 1)
					OST_STATS_ITEM(5, punch, reqs, 1)
					OST_STATS_ITEM(5, sync, reqs, 1)
					OST_STATS_ITEM(5, destroy, reqs, 1)
					OST_STATS_ITEM(5, create, reqs, 1)
					OST_STATS_ITEM(5, statfs, reqs, 1)
					OST_STATS_ITEM(5, get_info, reqs, 1)
					OST_STATS_ITEM(5, set_info_async, reqs, 1)
					OST_STATS_ITEM(5, quotactl, reqs, 1)
				</entry>
				<entry>
					SUBPATH(5, constant, exports, 1)
					MODE(5, directory, 1)
					<entry>
						TWO_FIELD_SUBPATH(6, regular_expression, (.+)@(.+), ost_exp_client, ost_exp_type, 1)
						MODE(6, directory, 1)
						EXPORT_OST_STATS_ENTRY(6, , 1)
					</entry>
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>job_stats</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>ost_jobstats</name>
						<pattern>- +job_id: +(.+)
 +snapshot_time: +.+
  read_bytes: +\{ samples: +([[:digit:]]+), unit: bytes, min: *([[:digit:]]+), max: *([[:digit:]]+), sum: *([[:digit:]]+) }
  write_bytes: +\{ samples: +([[:digit:]]+), unit: bytes, min: *([[:digit:]]+), max: *([[:digit:]]+), sum: *([[:digit:]]+) }
  getattr: +\{ samples: +([[:digit:]]+).+
  setattr: +\{ samples: +([[:digit:]]+).+
  punch: +\{ samples: +([[:digit:]]+).+
  sync: +\{ samples: +([[:digit:]]+).+
  destroy: +\{ samples: +([[:digit:]]+).+
  create: +\{ samples: +([[:digit:]]+).+
  statfs: +\{ samples: +([[:digit:]]+).+
  get_info: +\{ samples: +([[:digit:]]+).+
  set_info: +\{ samples: +([[:digit:]]+).+
  quotactl: +\{ samples: +([[:digit:]]+).+</pattern>
						OST_JOBSTAT_FIELD(6, 1, job_id, string, derive, 1)
						OST_JOBSTAT_FIELD(6, 2, read_samples, number, derive, 1)
						OST_JOBSTAT_FIELD_BYTES(6, 3, min_read_bytes, number, derive, 1)
						OST_JOBSTAT_FIELD_BYTES(6, 4, max_read_bytes, number, derive, 1)
						OST_JOBSTAT_FIELD_BYTES(6, 5, sum_read_bytes, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 6, write_samples, number, derive, 1)
						OST_JOBSTAT_FIELD_BYTES(6, 7, min_write_bytes, number, derive, 1)
						OST_JOBSTAT_FIELD_BYTES(6, 8, max_write_bytes, number, derive, 1)
						OST_JOBSTAT_FIELD_BYTES(6, 9, sum_write_bytes, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 10, getattr, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 11, setattr, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 12, punch, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 13, sync, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 14, destroy, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 15, create, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 16, statfs, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 17, get_info, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 18, set_info, number, derive, 1)
						OST_JOBSTAT_FIELD(6, 19, quotactl, number, derive, 1)
					</item>
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>mdc</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+)-(MDT.)+-(mdc.+)$</path>
					<subpath_field>
						<index>1</index>
						<name>fs_name</name>
					</subpath_field>
					<subpath_field>
						<index>2</index>
						<name>mdt_index</name>
					</subpath_field>
					<subpath_field>
						<index>3</index>
						<name>mdc_tag</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				MDC_MDT_CONSTANT_FILE_ENTRY(4, max_rpcs_in_flight, (.+), mdc_rpcs, gauge, max_rpcs_in_flight, max_rpcs_in_flight, 1)
			</entry>
		</entry>
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>/sys/fs/lustre</path>
		</subpath>
		<mode>directory</mode>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>ldlm</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>constant</subpath_type>
					<path>namespaces</path>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>regular_expression</subpath_type>
						<path>^filter-(.+)-(OST[0-9a-fA-F]+)_UUID$</path>
						<subpath_field>
							<index>1</index>
							<name>fs_name</name>
						</subpath_field>
						<subpath_field>
							<index>2</index>
							<name>ost_index</name>
						</subpath_field>
					</subpath>
					<mode>directory</mode>
					LDLM_LOCK_INFO_ENTRIES(5, ost, ${subpath:fs_name}-${subpath:ost_index}, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>regular_expression</subpath_type>
						<path>^mdt-(.+)-(MDT[0-9a-fA-F]+)_UUID$</path>
						<subpath_field>
							<index>1</index>
							<name>fs_name</name>
						</subpath_field>
						<subpath_field>
							<index>2</index>
							<name>mdt_index</name>
						</subpath_field>
					</subpath>
					<mode>directory</mode>
					LDLM_LOCK_INFO_ENTRIES(5, mdt, ${subpath:fs_name}-${subpath:mdt_index}, 1)
				</entry>
			</entry>
		</entry>
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>/sys/kernel/debug/lustre</path>
		</subpath>
		<mode>directory</mode>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>mds</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>constant</subpath_type>
					<path>MDS</path>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>mdt</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, mdt, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, mdt, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, mdt, reqbuf_avail, bufs, 1)
						SERVICE_STATS_ITEM(6, mdt, ldlm_ibits_enqueue, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt, mds_getattr, usec, 1)
						SERVICE_STATS_ITEM(6, mdt, mds_connect, usec, 1)
						SERVICE_STATS_ITEM(6, mdt, mds_get_root, usec, 1)
						SERVICE_STATS_ITEM(6, mdt, mds_statfs, usec, 1)
						SERVICE_STATS_ITEM(6, mdt, mds_getxattr, usec, 1)
						SERVICE_STATS_ITEM(6, mdt, obd_ping, usec, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, mds, mds, normal_metadata_ops, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>mdt_readpage</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, mdt_readpage, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, mdt_readpage, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_readpage, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_readpage, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, mdt_readpage, reqbuf_avail, bufs, 1)
						SERVICE_STATS_ITEM(6, mdt_readpage, mds_close, usec, 1)
						SERVICE_STATS_ITEM(6, mdt_readpage, mds_readpage, usec, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, mds, mds, readpage, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>mdt_setattr</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, mdt_setattr, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, mdt_setattr, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_setattr, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_setattr, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, mdt_setattr, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, mds, mds, setattr_service, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>mdt_fld</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, mdt_fld, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, mdt_fld, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_fld, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_fld, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, mdt_fld, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, mds, mds, fld_service, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>mdt_out</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, mdt_out, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, mdt_out, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_out, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_out, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, mdt_out, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, mds, mds, metadata_out_service, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>mdt_seqm</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, mdt_seqm, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, mdt_seqm, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_seqm, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_seqm, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, mdt_seqm, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, mds, mds, metadata_seqm_service, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>mdt_seqs</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, mdt_seqs, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, mdt_seqs, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_seqs, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, mdt_seqs, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, mdt_seqs, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, mds, mds, metadata_seqs_service, gauge, 1)
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>ost</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>constant</subpath_type>
					<path>OSS</path>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ost</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, ost, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, ost, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, ost, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, ost, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, ost, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, ost, ost, normal_data, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ost_io</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, ost_io, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, ost_io, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, ost_io, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, ost_io, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, ost_io, reqbuf_avail, bufs, 1)
						SERVICE_STATS_ITEM(6, ost_io, ost_read, usec, 1)
						SERVICE_STATS_ITEM(6, ost_io, ost_write, usec, 1)
						SERVICE_STATS_ITEM(6, ost_io, ost_punch, usec, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, ost_io, ost, bulk_data_IO, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ost_create</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, ost_create, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, ost_create, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, ost_create, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, ost_create, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, ost_create, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, ost_create, ost, obj_pre-creation_service, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ost_seq</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, ost_seq, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, ost_seq, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, ost_seq, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, ost_seq, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, ost_seq, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, ost_seq, ost, seq_service, gauge, 1)
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>ldlm</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>constant</subpath_type>
					<path>services</path>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ldlm_canceld</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, ldlm_canceld, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, ldlm_canceld, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, ldlm_canceld, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, ldlm_canceld, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, ldlm_canceld, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, ldlm_cancel, ldlm_service, lock_cancel, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ldlm_cbd</path>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>stats</path>
						</subpath>
						<mode>file</mode>
						<write_after_read>0</write_after_read>
						SERVICE_STATS_ITEM(6, ldlm_cbd, req_waittime, usec, 1)
						SERVICE_STATS_ITEM(6, ldlm_cbd, req_qdepth, reqs, 1)
						SERVICE_STATS_ITEM(6, ldlm_cbd, req_active, reqs, 1)
						SERVICE_STATS_ITEM(6, ldlm_cbd, req_timeout, sec, 1)
						SERVICE_STATS_ITEM(6, ldlm_cbd, reqbuf_avail, bufs, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, ldlm_cbd, ldlm_service, lock_grant, gauge, 1)
				</entry>
			</entry>
			<entry>
				<subpath>
					<subpath_type>constant</subpath_type>
					<path>namespaces</path>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>regular_expression</subpath_type>
						<path>^filter-(.+)-(OST[0-9a-fA-F]+)_UUID$</path>
						<subpath_field>
							<index>1</index>
							<name>fs_name</name>
						</subpath_field>
						<subpath_field>
							<index>2</index>
							<name>ost_index</name>
						</subpath_field>
					</subpath>
					<mode>directory</mode>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>pool</path>
						</subpath>
						<mode>directory</mode>
						<entry>
							<!-- ldlm_stats_counter_init() -->
							<subpath>
								<subpath_type>constant</subpath_type>
								<path>stats</path>
							</subpath>
							<mode>file</mode>
							<item>
								<name>ost_ldlm_stats</name>
								<pattern>snapshot_time             +([[:digit:]]+).+
granted                   +[[:digit:]]+ samples \[locks\] +([[:digit:]]+).+
grant                     +[[:digit:]]+ samples \[locks\] +([[:digit:]]+).+
cancel                    +[[:digit:]]+ samples \[locks\] +([[:digit:]]+).+
grant_rate                +[[:digit:]]+ samples \[locks\/s\] +([[:digit:]]+).+
cancel_rate               +[[:digit:]]+ samples \[locks\/s\] +([[:digit:]]+).+
grant_plan                +[[:digit:]]+ samples \[locks\/s\] +([[:digit:]]+).+
slv                       +[[:digit:]]+ samples \[slv\] +([[:digit:]]+).+
recalc_freed              +[[:digit:]]+ samples \[locks\] +([[:digit:]]+).+
recalc_timing             +[[:digit:]]+ samples \[sec\] +([[:digit:]]+).+</pattern>
								LDLM_STATS_FIELD(8, 1, snapshot_time, number, gauge)
								LDLM_STATS_FIELD(8, 2, granted, number, gauge)
								LDLM_STATS_FIELD(8, 3, grant, number, gauge)
								LDLM_STATS_FIELD(8, 4, cancel, number, gauge)
								LDLM_STATS_FIELD(8, 5, grant_rate, number, gauge)
								LDLM_STATS_FIELD(8, 6, cancel_rate, number, gauge)
								LDLM_STATS_FIELD(8, 7, grant_plan, number, gauge)
								LDLM_STATS_FIELD(8, 8, slv, number, gauge)
								LDLM_STATS_FIELD(8, 9, recalc_freed, number, gauge)
								LDLM_STATS_FIELD(8, 10, recalc_timing, number, gauge)
							</item>
						</entry>
					</entry>
				</entry>
			</entry>
		</entry>
	</entry>
')dnl
