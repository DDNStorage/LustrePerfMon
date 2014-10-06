include(`lustre_xml.m4')dnl
HEAD(Lustre-ieel-2.5)
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
					SUBPATH(5, constant, exports, 1)
					MODE(5, directory, 1)
					<entry>
						ONE_FIELD_SUBPATH(6, regular_expression, (.+@.+), mdt_exp_name, 1)
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
						FIELD(6, 1, job_id, string, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, job_id, 1)
						FIELD(6, 2, open, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, open, 1)
						FIELD(6, 3, close, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, close, 1)
						FIELD(6, 4, mknod, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, mknod, 1)
						FIELD(6, 5, link, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, link, 1)
						FIELD(6, 6, unlink, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, unlink, 1)
						FIELD(6, 7, mkdir, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, mkdir, 1)
						FIELD(6, 8, rmdir, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, rmdir, 1)
						FIELD(6, 9, rename, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, rename, 1)
						FIELD(6, 10, getattr, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, getattr, 1)
						FIELD(6, 11, setattr, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, setattr, 1)
						FIELD(6, 12, getxattr, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, getxattr, 1)
						FIELD(6, 13, setxattr, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, setxattr, 1)
						FIELD(6, 14, statfs, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, statfs, 1)
						FIELD(6, 15, sync, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, sync, 1)
						FIELD(6, 16, samedir_rename, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, samedir_rename, 1)
						FIELD(6, 17, crossdir_rename, number, ${key:hostname}, ${subpath:mdt_name}, jobstat_${content:job_id}, derive, crossdir_rename, 1)
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
					SUBPATH(5, constant, exports, 1)
					MODE(5, directory, 1)
					<entry>
						ONE_FIELD_SUBPATH(6, regular_expression, (.+@.+), ost_exp_name, 1)
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
  read: +\{ samples: +([[:digit:]]+).+, sum: +([[:digit:]]+).+
  write: +\{ samples: +([[:digit:]]+).+, sum: +([[:digit:]]+).+
  setattr: +\{ samples: +([[:digit:]]+).+
  punch: +\{ samples: +([[:digit:]]+).+
  sync: +\{ samples: +([[:digit:]]+).+</pattern>
						FIELD(6, 1, job_id, string, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, job_id, 1)
						FIELD(6, 2, read_samples, number, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, read_samples, 1)
						FIELD(6, 3, read_bytes, number, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, read_bytes, 1)
						FIELD(6, 4, write_samples, number, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, write_samples, 1)
						FIELD(6, 5, write_bytes, number, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, write_bytes, 1)
						FIELD(6, 6, setattr, number, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, setattr, 1)
						FIELD(6, 7, punch, number, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, pubch, 1)
						FIELD(6, 8, sync, number, ${key:hostname}, ${subpath:ost_name}, jobstat_${content:job_id}, derive, sync, 1)
					</item>
				</entry>
				FILES_KBYTES_INFO_ENTRIES(4, ost, ${subpath:ost_name}, 1)
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
				CONSTANT_FILE_ENTRY(4, max_rpcs_in_flight, max_rpcs_in_flight, (.+), number,
					${key:hostname}, ${subpath:mdc_mdt_name}, mdc_rpcs, gauge, max_rpcs_in_flight, 1)
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
					THREAD_INFO_ENTRIES(5, mds, mds, normal_metadata_ops, gauge, 1)
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
						OST_IO_STATS_ITEM(6, req_waittime, usec, 1)
						OST_IO_STATS_ITEM(6, req_qdepth, reqs, 1)
						OST_IO_STATS_ITEM(6, req_active, reqs, 1)
						OST_IO_STATS_ITEM(6, req_timeout, sec, 1)
						OST_IO_STATS_ITEM(6, reqbuf_avail, bufs, 1)
						OST_IO_STATS_ITEM(6, ost_read, usec, 1)
						OST_IO_STATS_ITEM(6, ost_write, usec, 1)
						OST_IO_STATS_ITEM(6, ost_punch, usec, 1)
					</entry>
					THREAD_INFO_ENTRIES(5, ost_io, ost, bulk_data_IO, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ost_create</path>
					</subpath>
					<mode>directory</mode>
					THREAD_INFO_ENTRIES(5, ost_create, ost, obj_pre-creation_service, gauge, 1)
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
					THREAD_INFO_ENTRIES(5, ldlm_cancel, ldlm_service, lock_cancel, gauge, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>ldlm_cbd</path>
					</subpath>
					<mode>directory</mode>
					THREAD_INFO_ENTRIES(5, ldlm_cbd, ldlm_service, lock_grant, gauge, 1)
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
				FILES_KBYTES_INFO_ENTRIES(4, mdt, ${subpath:lod_mdt_name}, 1)
			</entry>
		</entry>
	</entry>
</definition>

