include(`lustre_xml.m4')dnl
<definition>
	<version>1.8.9</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>/proc/fs/lustre</path>
		</subpath>
		<mode>directory</mode>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>health_check</path>
			</subpath>
			<mode>file</mode>
			<item>
				<name>health</name>
				<pattern>(.+)</pattern>
				FIELD(4, 1, health, string, NA, NA, NA, NA, NA, 1)
			</item>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>version</path>
			</subpath>
			<mode>file</mode>
			<item>
				<name>lustre_version</name>
				<pattern>lustre: ([[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+)</pattern>
				FIELD(4, 1, version, string, NA, NA, NA, NA, NA, 1)
			</item>
			<item>
				<name>kernel_type</name>
				<pattern>kernel: (patchless_client)</pattern>
				FIELD(4, 1, kernel_type, string, NA, NA, NA, NA, NA, 1)
			</item>
			<item>
				<name>build_version</name>
				<pattern>build:  (.+)</pattern>
				FIELD(4, 1, build_version, string, NA, NA, NA, NA, NA, 1)
			</item>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>mds</path>
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
						<path>stats</path>
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
					OST_STATS_ITEM(5, get_page, 1)
					<item>
						<name>ost_stats_get_page_failures</name>
						<pattern>get_page failures +([[:digit:]]+) samples \[num\]</pattern>
						FIELD(6, 1, get_page_failures, number, ${subpath:ost_name}, stats, , derive, get_page_failures, 1)
					</item>
					OST_STATS_ITEM(5, cache_access, 1)
					OST_STATS_ITEM(5, cache_hit, 1)
					OST_STATS_ITEM(5, cache_miss, 1)
					<!-- Following comes from filter_setup()/lprocfs_alloc_obd_stats()/lprocfs_init_ops_stats()
					     Not necessarily available.
					-->
					OST_STATS_ITEM(5, getattr, 1)
					OST_STATS_ITEM(5, setattr, 1)
					OST_STATS_ITEM(5, punch, 1)
					OST_STATS_ITEM(5, sync, 1)
					OST_STATS_ITEM(5, destroy, 1)
					OST_STATS_ITEM(5, create, 1)
					OST_STATS_ITEM(5, statfs, 1)
					OST_STATS_ITEM(5, get_info, 1)
					OST_STATS_ITEM(5, set_info_async, 1)
					OST_STATS_ITEM(5, quotactl, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>brw_stats</path>
					</subpath>
					<mode>file</mode>
					OST_BRW_STATS_ITEM(5, rpc_bulk, ^pages per bulk .+
(.+
)*$, [[:digit:]]+[KM]?, pages, derive, 1)
					OST_BRW_STATS_ITEM(5, page_discontiguous_rpc, ^discontiguous pages .+
(.+
)*$, [[:digit:]]+[KM]?, pages, derive, 1)
					OST_BRW_STATS_ITEM(5, block_discontiguous_rpc, ^discontiguous blocks .+
(.+
)*$, [[:digit:]]+[KM]?, blocks, derive, 1)
					OST_BRW_STATS_ITEM(5, fragmented_io, ^disk fragmented .+
(.+
)*$, [[:digit:]]+[KM]?, fragments, derive, 1)
					OST_BRW_STATS_ITEM(5, io_in_flight, ^disk I/Os .+
(.+
)*$, [[:digit:]]+[KM]?, ios, derive, 1)
					OST_BRW_STATS_ITEM(5, io_time, ^I/O time .+
(.+
)*$, [[:digit:]]+[KM]?, milliseconds, derive, 1)
					OST_BRW_STATS_ITEM(5, io_size, ^disk I/O size .+
(.+
)*$, [[:digit:]]+[KM]?, Bytes, derive, 1)
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>kbytestotal</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>kbytestotal</name>
						<pattern>(.+)</pattern>
						FIELD(6, 1, kbytestotal, number, ${subpath:ost_name}, NA, NA, NA, NA, 1)
					</item>
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>kbytesavail</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>kbytesavail</name>
						<pattern>(.+)</pattern>
						FIELD(6, 1, kbytesavail, number, ${subpath:ost_name}, NA, NA, NA, NA, 1)
					</item>
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>kbytesfree</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>kbytesfree</name>
						<pattern>(.+)</pattern>
						FIELD(6, 1, kbytesfree, number, ${subpath:ost_name}, NA, NA, NA, NA, 1)
					</item>
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>filestotal</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>filestotal</name>
						<pattern>(.+)</pattern>
						FIELD(6, 1, filestotal, number, ${subpath:ost_name}, NA, NA, NA, NA, 1)
					</item>
				</entry>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>filesfree</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>filesfree</name>
						<pattern>(.+)</pattern>
						FIELD(6, 1, filesfree, number, ${subpath:ost_name}, NA, NA, NA, NA, 1)
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
					<path>(^.+-MDT.+$)</path>
					<subpath_field>
						<index>1</index>
						<name>mdc_mdt_name</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>max_rpcs_in_flight</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>max_rpcs_in_flight</name>
						<pattern>(.+)</pattern>
						FIELD(6, 1, max_rpcs_in_flight, number, ${subpath:mdc_mdt_name}, NA, NA, derive, max_rpcs_in_flight, 1)
					</item>
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
					<subpath_type>constant</subpath_type>
					<path>MDS</path>
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
							<path>threads_max</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>mds_threads_max</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_max, number, mds, 
								normal_metadata_ops, NA, derive, threads_max, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_min</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>mds_threads_min</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_min, number, mds, 
								normal_metadata_ops, NA, derive, threads_min, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_started</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>mds_threads_started</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_started, number, mds, 
								normal_metadata_ops, NA, derive, threads_started, 1)
						</item>
					</entry>
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
							<path>threads_max</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_threads_max</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_max, number, ost, 
								normal_data, NA, derive, threads_max, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_min</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_threads_min</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_min, number, ost, 
								normal_data, NA, derive, threads_min, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_started</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_threads_started</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_started, number, ost, 
								normal_data, NA, derive, threads_started, 1)
						</item>
					</entry>
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
							<path>threads_max</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_io_threads_max</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_max, number, ost, 
								bulk_data_IO, NA, derive, threads_max, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_min</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_io_threads_min</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_min, number, ost, 
								bulk_data_IO, NA, derive, threads_min, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_started</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_io_threads_started</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_started, number, ost, 
								bulk_data_IO, NA, derive, threads_started, 1)
						</item>
					</entry>
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
							<path>threads_max</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_create_threads_max</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_max, number, ost, 
								obj_pre-creation_service, NA, derive, threads_max, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_min</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_create_threads_min</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_min, number, ost, 
								obj_pre-creation_service, NA, derive, threads_min, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_started</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ost_create_threads_started</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_started, number, ost, 
								obj_pre-creation_service, NA, derive, threads_started, 1)
						</item>
					</entry>
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
							<path>threads_max</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ldlm_cancel_threads_max</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_max, number, ldlm_service, 
								lock_cancel, NA, derive, threads_max, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_min</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ldlm_cancel_threads_min</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_min, number, ldlm_service, 
								lock_cancel, NA, derive, threads_min, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_started</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ldlm_cancel_threads_started</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_started, number, ldlm_service, 
								lock_cancel, NA, derive, threads_started, 1)
						</item>
					</entry>
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
							<path>threads_max</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ldlm_cbd_threads_max</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_max, number, ldlm_service, 
								lock_grant, NA, derive, threads_max, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_min</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ldlm_cbd_threads_min</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_min, number, ldlm_service, 
								lock_grant, NA, derive, threads_min, 1)
						</item>
					</entry>
					<entry>
						<subpath>
							<subpath_type>constant</subpath_type>
							<path>threads_started</path>
						</subpath>
						<mode>file</mode>
						<item>
							<name>ldlm_cbd_threads_started</name>
							<pattern>(.+)</pattern>
							FIELD(7, 1, threads_started, number, ldlm_service, 
								lock_grant, NA, derive, threads_started, 1)
						</item>
					</entry>
				</entry>
			</entry>
		</entry>
	</entry>
</definition>

