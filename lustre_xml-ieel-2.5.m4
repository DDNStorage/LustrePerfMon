include(`lustre_xml.m4')dnl
<definition>
	<version>2.5.52</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>/proc/fs/lustre</path>
		</subpath>
		<mode>directory</mode>
		CONSTANT_FILE_ENTRY(2, health_check, lustre_health, (.+), string, NA, NA, NA, NA, NA, 1)
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>version</path>
			</subpath>
			<mode>file</mode>
			ONE_FIELD_ITEM(3, lustre_version, lustre_version, 
			lustre: ([[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+), string, NA, NA, NA, NA, NA, 1)
			ONE_FIELD_ITEM(3, kernel_type, kernel_type, kernel: (patchless_client), string, NA, NA, NA, NA, NA, 1)
			ONE_FIELD_ITEM(3, build_version, build_version, build:  (.+), string, NA, NA, NA, NA, NA, 1)
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
					<path>(^.+-MDT[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>mdt_name</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
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
						FIELD(6, 1, job_id, string, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, job_id, 1)
						FIELD(6, 2, open, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, open, 1)
						FIELD(6, 3, close, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, close, 1)
						FIELD(6, 4, mknod, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, mknod, 1)
						FIELD(6, 5, link, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, link, 1)
						FIELD(6, 6, unlink, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, unlink, 1)
						FIELD(6, 7, mkdir, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, mkdir, 1)
						FIELD(6, 8, rmdir, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, rmdir, 1)
						FIELD(6, 9, rename, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, rename, 1)
						FIELD(6, 10, getattr, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, getattr, 1)
						FIELD(6, 11, setattr, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, setattr, 1)
						FIELD(6, 12, getxattr, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, getxattr, 1)
						FIELD(6, 13, setxattr, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, setxattr, 1)
						FIELD(6, 14, statfs, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, statfs, 1)
						FIELD(6, 15, sync, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, sync, 1)
						FIELD(6, 16, samedir_rename, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, samedir_rename, 1)
						FIELD(6, 17, crossdir_rename, number, ${subpath:mdt_name}, jobstat, ${content:job_id}, derive, crossdir_rename, 1)
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
					<path>(^.+-OST[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>ost_name</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					<!-- filter_setup().
					     There are a lot of counter, only defined part of them here
					-->
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>stats</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>ost_stats_read</name>
						<pattern>read_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)</pattern>
						FIELD(6, 1, read_samples, number, ${subpath:ost_name}, stats, , derive, read_samples, 1)
						FIELD(6, 2, read_bytes, number, ${subpath:ost_name}, stats, , derive, read_bytes, 1)
					</item>
					<item>
						<name>ost_stats_write</name>
						<pattern>write_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)</pattern>
						FIELD(6, 1, write_samples, number, ${subpath:ost_name}, stats, , derive, write_samples, 1)
						FIELD(6, 2, write_bytes, number, ${subpath:ost_name}, stats, , derive, write_bytes, 1)
					</item>
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
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>job_stats</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>ost_jobstats</name>
						<pattern>- +job_id: +(.+)
 +snapshot_time: +.+
  read: +\{ samples: +([[:digit:]]+).+, sum: +([[:digit:]]+).+
  write: +\{ samples: +([[:digit:]]+).+, sum: +([[:digit:]]+).+
  setattr: +\{ samples: +([[:digit:]]+).+
  punch: +\{ samples: +([[:digit:]]+).+
  sync: +\{ samples: +([[:digit:]]+).+</pattern>
						FIELD(6, 1, job_id, string, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, job_id, 1)
						FIELD(6, 2, read_samples, number, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, read_samples, 1)
						FIELD(6, 3, read_bytes, number, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, read_bytes, 1)
						FIELD(6, 4, write_samples, number, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, write_samples, 1)
						FIELD(6, 5, write_bytes, number, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, write_bytes, 1)
						FIELD(6, 6, setattr, number, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, setattr, 1)
						FIELD(6, 7, punch, number, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, pubch, 1)
						FIELD(6, 8, sync, number, ${subpath:ost_name}, jobstat, ${content:job_id}, derive, sync, 1)
					</item>
				</entry>
				CONSTANT_FILE_ENTRY(4, filestotal, ost_filestotal, (.+), 
					number, ${subpath:ost_name}, filesinfo, , gauge, filestotal, 1)
				CONSTANT_FILE_ENTRY(4, filesfree, ost_filesfree, (.+), 
					number, ${subpath:ost_name}, filesinfo, , gauge, filesfree, 1)
				CONSTANT_FILE_ENTRY(4, kbytestotal, ost_kbytestotal, (.+), 
					number, ${subpath:ost_name}, kbytesinfo, , gauge, kbytestotal, 1)
				CONSTANT_FILE_ENTRY(4, kbytesfree, ost_kbytesfree, (.+), 
					number, ${subpath:ost_name}, kbytesinfo, , gauge, kbytesfree, 1)
				CONSTANT_FILE_ENTRY(4, kbytesavail, ost_kbytesavail, (.+), 
					number, ${subpath:ost_name}, kbytesinfo, , gauge, kbytesavail, 1)
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
					<path>(^.+-MDT.+-mdc).+$</path>
					<subpath_field>
						<index>1</index>
						<name>mdc_mdt_name</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				CONSTANT_FILE_ENTRY(4, max_rpcs_in_flight, max_rpcs_in_flight, (.+), 
					number, ${subpath:mdc_mdt_name}, mdc_rpcs, , gauge, max_rpcs_in_flight, 1)
			</entry>
		</entry>
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
					CONSTANT_FILE_ENTRY(5, threads_max, mds_threads_max, (.+), 
						number, mds, normal_metadata_ops, , gauge, threads_max, 1)
					CONSTANT_FILE_ENTRY(5, threads_min, mds_threads_min, (.+), 
						number, mds, normal_metadata_ops, , gauge, threads_min, 1)
					CONSTANT_FILE_ENTRY(5, threads_started, mds_threads_started, (.+), 
						number, mds, normal_metadata_ops, , gauge, threads_started, 1)
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
					CONSTANT_FILE_ENTRY(5, threads_max, ost_threads_max, (.+), 
						number, ost, normal_data, , gauge, threads_max, 1)
					CONSTANT_FILE_ENTRY(5, threads_min, ost_threads_min, (.+), 
						number, ost, normal_data, , gauge, threads_min, 1)
					CONSTANT_FILE_ENTRY(5, threads_started, ost_threads_started, (.+), 
						number, ost, normal_data, , gauge, threads_started, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ost_io</path>
					</subpath>
					<mode>directory</mode>
					CONSTANT_FILE_ENTRY(5, threads_max, ost_io_threads_max, (.+), 
						number, ost, bulk_data_IO, , gauge, threads_max, 1)
					CONSTANT_FILE_ENTRY(5, threads_min, ost_io_threads_min, (.+), 
						number, ost, bulk_data_IO, , gauge, threads_min, 1)
					CONSTANT_FILE_ENTRY(5, threads_started, ost_io_threads_started, (.+), 
						number, ost, bulk_data_IO, , gauge, threads_started, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ost_create</path>
					</subpath>
					<mode>directory</mode>
					CONSTANT_FILE_ENTRY(5, threads_max, ost_create_threads_max, (.+), 
						number, ost, obj_pre-creation_service, , gauge, threads_max, 1)
					CONSTANT_FILE_ENTRY(5, threads_min, ost_create_threads_min, (.+), 
						number, ost, obj_pre-creation_service, , gauge, threads_min, 1)
					CONSTANT_FILE_ENTRY(5, threads_started, ost_create_threads_started, (.+), 
						number, ost, obj_pre-creation_service, , gauge, threads_started, 1)
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
					CONSTANT_FILE_ENTRY(5, threads_max, ldlm_cancel_threads_max, (.+), 
						number, ldlm_service, lock_cancel, , gauge, threads_max, 1)
					CONSTANT_FILE_ENTRY(5, threads_min, ldlm_cancel_threads_min, (.+), 
						number, ldlm_service, lock_cancel, , gauge, threads_min, 1)
					CONSTANT_FILE_ENTRY(5, threads_started, ldlm_cancel_threads_started, (.+), 
						number, ldlm_service, lock_cancel, , gauge, threads_started, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ldlm_cbd</path>
					</subpath>
					<mode>directory</mode>
					CONSTANT_FILE_ENTRY(5, threads_max, ldlm_cbd_threads_max, (.+), 
						number, ldlm_service, lock_grant, , gauge, threads_max, 1)
					CONSTANT_FILE_ENTRY(5, threads_min, ldlm_cbd_threads_min, (.+), 
						number, ldlm_service, lock_grant, , gauge, threads_min, 1)
					CONSTANT_FILE_ENTRY(5, threads_started, ldlm_cbd_threads_started, (.+), 
						number, ldlm_service, lock_grant, , gauge, threads_started, 1)
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>lod</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+-MDT[0-9a-fA-F]+)-mdtlov</path>
					<subpath_field>
						<index>1</index>
						<name>lod_mdt_name</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				CONSTANT_FILE_ENTRY(4, filestotal, mdt_filestotal, (.+), 
					number, ${subpath:lod_mdt_name}, filesinfo, , gauge, filestotal, 1)
				CONSTANT_FILE_ENTRY(4, filesfree, mdt_filesfree, (.+), 
					number, ${subpath:lod_mdt_name}, filesinfo, , gauge, filesfree, 1)
				CONSTANT_FILE_ENTRY(4, kbytestotal, mdt_kbytestotal, (.+), 
					number, ${subpath:lod_mdt_name}, kbytesinfo, , gauge, kbytestotal, 1)
				CONSTANT_FILE_ENTRY(4, kbytesfree, mdt_kbytesfree, (.+), 
					number, ${subpath:lod_mdt_name}, kbytesinfo, , gauge, kbytesfree, 1)
				CONSTANT_FILE_ENTRY(4, kbytesavail, mdt_kbytesavail, (.+), 
					number, ${subpath:lod_mdt_name}, kbytesinfo, , gauge, kbytesavail, 1)
			</entry>
		</entry>
	</entry>
</definition>

