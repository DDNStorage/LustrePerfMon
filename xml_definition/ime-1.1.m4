include(`general.m4')dnl
HEAD(IME-3.5)
<definition>
	<version>3.5</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>--nvm-stat --bfs</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>nvm-stat</name>
			<pattern>\| +([[:digit:]]+) +\| +(\S+) +\| +([[:digit:]]+) +\| +([[:digit:]]+)\.[[:digit:]]+ +\| +([[:digit:]]+) +\| +([[:digit:]]+)\.[[:digit:]]+ +\| +([[:digit:]]+) +\| +([[:digit:]]+)\.[[:digit:]]+ +\|.+\|</pattern>
			FIELD(4, 1, ID, string, , , , gauge, , NA, NA, 1)
			FIELD(4, 2, name, string, , , , gauge, , NA, NA, 1)
			FIELD(4, 3, read_IOs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, gauge, read_IOs, ime_nvm_read_IOs, host=${key:hostname} rw=read device=${content:ID}, 1)
			FIELD(4, 4, read_MBs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, gauge, read_MBs, ime_nvm_read_MBs, host=${key:hostname} rw=read device=${content:ID}, 1)
			FIELD(4, 5, write_IOs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, gauge, write_IOs, ime_nvm_write_IOs, host=${key:hostname} rw=write device=${content:ID}, 1)
			FIELD(4, 6, write_MBs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, gauge, write_MBs, ime_nvm_write_MBs, host=${key:hostname} rw=write device=${content:ID}, 1)
			FIELD(4, 7, unmap_IOs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, gauge, unmap_IOs, ime_nvm_unmap_IOs, host=${key:hostname} rw=unmap device=${content:ID}, 1)
			FIELD(4, 8, free, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, gauge, free, ime_nvm_free, host=${key:hostname} device=${content:ID}, 1)
		</item>
		<item>
			<name>bfs-stat</name>
                        <pattern>Read bytes: +([[:digit:]]+)+
Write bytes: +([[:digit:]]+)+
Reads: +([[:digit:]]+)+
Writes: +([[:digit:]]+)+
Opens: +([[:digit:]]+)+
Closes: +([[:digit:]]+)+
fsync: +([[:digit:]]+)+
fstat: +([[:digit:]]+)+
ftruncate: +([[:digit:]]+)+
ns_multi: +([[:digit:]]+)+
open errors: +([[:digit:]]+)+
close errors: +([[:digit:]]+)+
read errors: +([[:digit:]]+)+
write errors: +([[:digit:]]+)+
fsync errors: +([[:digit:]]+)+
fstat errors: +([[:digit:]]+)+
ftruncate errors: +([[:digit:]]+)
ns_multi errors: +([[:digit:]]+)</pattern>
			FIELD(4, 1, Read_bytes, number, ime_${key:hostname}, bfs-stat, , derive, Read_bytes, ime_bfs_read_bytes, , 1)
			FIELD(4, 2, Write_bytes, number, ime_${key:hostname}, bfs-stat, , derive, Write_bytes, ime_bfs_write_bytes, , 1)
			FIELD(4, 3, Reads, number, ime_${key:hostname}, bfs-stat, , derive, Reads, ime_bfs_reads, , 1)
			FIELD(4, 4, Writes, number, ime_${key:hostname}, bfs-stat, , derive, Writes, ime_bfs_writes, , 1)
			FIELD(4, 5, Opens, number, ime_${key:hostname}, bfs-stat, , derive, Opens, ime_bfs_opens, , 1)
			FIELD(4, 6, Closes, number, ime_${key:hostname}, bfs-stat, , derive, Closes, ime_bfs_closes, , 1)
			FIELD(4, 7, fsync, number, ime_${key:hostname}, bfs-stat, , derive, fsync, ime_bfs_fsync, , 1)
			FIELD(4, 8, fstat, number, ime_${key:hostname}, bfs-stat, , derive, fstat, ime_bfs_fstat, , 1)
			FIELD(4, 9, ftruncate, number, ime_${key:hostname}, bfs-stat, , derive, ftruncate, ime_bfs_ftruncate, , 1)
			FIELD(4, 10, ns_multi, number, ime_${key:hostname}, bfs-stat, , derive, ns_multi, ime_bfs_ns_multi, , 1)
			FIELD(4, 11, open_errors, number, ime_${key:hostname}, bfs-stat, , derive, open_errors, ime_bfs_open_errors, , 1)
			FIELD(4, 12, close_errors, number, ime_${key:hostname}, bfs-stat, , derive, close_errors, ime_bfs_close_errors, , 1)
			FIELD(4, 13, read_errors, number, ime_${key:hostname}, bfs-stat, , derive, read_errors, ime_bfs_read_errors, , 1)
			FIELD(4, 14, write_errors, number, ime_${key:hostname}, bfs-stat, , derive, write_errors, ime_bfs_write_errors, , 1)
			FIELD(4, 15, fsync_errors, number, ime_${key:hostname}, bfs-stat, , derive, fsync_errors, ime_bfs_fsync_errors, , 1)
			FIELD(4, 16, fstat_errors, number, ime_${key:hostname}, bfs-stat, , derive, fstat_errors, ime_bfs_fstat_errors, , 1)
			FIELD(4, 17, ftruncate_errors, number, ime_${key:hostname}, bfs-stat, , derive, ftruncate_errors, ime_bfs_ftruncate_errors, , 1)
			FIELD(4, 18, ns_multi_errors, number, ime_${key:hostname}, bfs-stat, , derive, ns_multi_errors, ime_bfs_ns_multi_errors, , 1)
		</item>
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>--frgbs | grep '[0-9]'</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>UM-stat</name>
			<pattern>\s+MinFreeSpaceRatio   = +([[:digit:]]+)+\s+FlushThresholdRatio = +([[:digit:]]+)+\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+).[[:digit:]]+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|\s+([[:digit:]]+)+ \|</pattern>

			FIELD(4, 1, MinFreeSpaceRatio, number, ime_${key:hostname}, UM-stat, , gauge, MinFreeSpaceRatio, ime_UM_MinFreeSpaceRatio, , 1)
			FIELD(4, 2, FlushThresholdRatio, number, ime_${key:hostname}, UM-stat, , gauge, FlushThresholdRatio, ime_UM_FlushThresholdRatio, , 1)
			FIELD(4, 3, Cap_InUse, number, ime_${key:hostname}, UM-stat, , gauge, Cap_InUse, ime_Cap_InUse, , 1)
			FIELD(4, 4, Cap_Total, number, ime_${key:hostname}, UM-stat, , gauge, Cap_Total, ime_Cap_Total, , 1)
			FIELD(4, 5, Cap_PCT_Free, number, ime_${key:hostname}, UM-stat, , gauge, Cap_PCT_Free, ime_PCT_Free, , 1)
			FIELD(4, 6, DM_PrestageQueued, number, ime_${key:hostname}, UM-stat, , gauge, DM_PrestageQueued, ime_DM_PrestageQueued, , 1)
			FIELD(4, 7, DM_SyncQueued, number, ime_${key:hostname}, UM-stat, , gauge, DM_SyncQueued, ime_DM_SyncQueued, , 1)
			FIELD(4, 8, DM_Clean, number, ime_${key:hostname}, UM-stat, , gauge, DM_Clean, ime_DM_Clean, , 1)
			FIELD(4, 9, DM_Pinned, number, ime_${key:hostname}, UM-stat, , gauge, DM_Pinned, ime_DM_Pinned, , 1)
			FIELD(4, 10, FBS_FullDirty, number, ime_${key:hostname}, UM-stat, , gauge, FBS_FullDirty, ime_FBS_FullDirty, , 1)
			FIELD(4, 11, FBS_PartialDirty, number, ime_${key:hostname}, UM-stat, , gauge, FBS_PartialDirty, ime_FBS_PartialDirty, , 1)
			FIELD(4, 12, FBS_FullClean, number, ime_${key:hostname}, UM-stat, , gauge, FBS_FullClean, ime_FBS_FullClean, , 1)
			FIELD(4, 13, FBS_PartialClean, number, ime_${key:hostname}, UM-stat, , gauge, FBS_PartialClean, ime_FBS_PartialClean, , 1)
			FIELD(4, 14, FBS_Pinned, number, ime_${key:hostname}, UM-stat, , gauge, FBS_Pinned, ime_FBS_pinned, , 1)
		</item>
	</entry>
</definition>

