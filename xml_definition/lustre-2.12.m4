include(`lustre.m4')dnl
HEAD(Lustre-es4-2.10)
<definition>
	<version>2.10</version>
	MATH_ENTRY(1, mdt_filesinfo_total, -, mdt_filesinfo_free, mdt_filesinfo_used, filesused, 1)
	MATH_ENTRY(1, mdt_kbytesinfo_total, -, mdt_kbytesinfo_free, mdt_kbytesinfo_used, kbytesused, 1)
	MATH_ENTRY(1, ost_filesinfo_total, -, ost_filesinfo_free, ost_filesinfo_used, filesused, 1)
	MATH_ENTRY(1, ost_kbytesinfo_total, -, ost_kbytesinfo_free, ost_kbytesinfo_used, kbytesused, 1)
	CLIENT_STATS_MEAN(1, read, usec)
	CLIENT_STATS_MEAN(1, write, usec)
	CLIENT_STATS_MEAN(1, open, usec)
	CLIENT_STATS_MEAN(1, close, usec)
	CLIENT_STATS_MEAN(1, mmap, usec)
	CLIENT_STATS_MEAN(1, page_fault, usec)
	CLIENT_STATS_MEAN(1, page_mkwrite, usec)
	CLIENT_STATS_MEAN(1, seek, usec)
	CLIENT_STATS_MEAN(1, fsync, usec)
	CLIENT_STATS_MEAN(1, readdir, usec)
	CLIENT_STATS_MEAN(1, setattr, usec)
	CLIENT_STATS_MEAN(1, truncate, usec)
	CLIENT_STATS_MEAN(1, flock, usec)
	CLIENT_STATS_MEAN(1, getattr, usec)
	CLIENT_STATS_MEAN(1, fallocate, usec)
	CLIENT_STATS_MEAN(1, create, usec)
	CLIENT_STATS_MEAN(1, link, usec)
	CLIENT_STATS_MEAN(1, unlink, usec)
	CLIENT_STATS_MEAN(1, symlink, usec)
	CLIENT_STATS_MEAN(1, mkdir, usec)
	CLIENT_STATS_MEAN(1, rmdir, usec)
	CLIENT_STATS_MEAN(1, mknod, usec)
	CLIENT_STATS_MEAN(1, rename, usec)
	CLIENT_STATS_MEAN(1, statfs, usec)
	CLIENT_STATS_MEAN(1, setxattr, usec)
	CLIENT_STATS_MEAN(1, getxattr, usec)
	CLIENT_STATS_MEAN(1, listxattr, usec)
	CLIENT_STATS_MEAN(1, removexattr, usec)
	CLIENT_STATS_MEAN(1, inode_permission, usec)
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
			<path>/sys/kernel/debug/lustre/llite</path>
		</subpath>
		<mode>directory</mode>
		<entry>
			<subpath>
				<subpath_type>regular_expression</subpath_type>
				<path>(^.+)-([0-9a-fA-F]+$)</path>
				<subpath_field>
					<index>1</index>
					<name>fs_name</name>
				</subpath_field>
				<subpath_field>
					<index>2</index>
					<name>client_uuid</name>
				</subpath_field>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>constant</subpath_type>
					<path>stats</path>
				</subpath>
				<mode>file</mode>
				<write_after_read>0</write_after_read>
				CLIENT_STATS_ITEM_FOUR(4, read_bytes, bytes)
				CLIENT_STATS_ITEM_FOUR(4, write_bytes, bytes)
				CLIENT_STATS_ITEM_FOUR(4, read, usec)
				CLIENT_STATS_ITEM_FOUR(4, write, usec)
				CLIENT_STATS_ITEM_ONE(4, ioctl, reqs)
				CLIENT_STATS_ITEM_FOUR(4, open, usec)
				CLIENT_STATS_ITEM_FOUR(4, close, usec)
				CLIENT_STATS_ITEM_FOUR(4, mmap, usec)
				CLIENT_STATS_ITEM_FOUR(4, page_fault, usec)
				CLIENT_STATS_ITEM_FOUR(4, page_mkwrite, usec)
				CLIENT_STATS_ITEM_FOUR(4, seek, usec)
				CLIENT_STATS_ITEM_FOUR(4, fsync, usec)
				CLIENT_STATS_ITEM_FOUR(4, readdir, usec)
				CLIENT_STATS_ITEM_FOUR(4, setattr, usec)
				CLIENT_STATS_ITEM_FOUR(4, truncate, usec)
				CLIENT_STATS_ITEM_FOUR(4, flock, usec)
				CLIENT_STATS_ITEM_FOUR(4, getattr, usec)
				CLIENT_STATS_ITEM_FOUR(4, fallocate, usec)
				CLIENT_STATS_ITEM_FOUR(4, create, usec)
				CLIENT_STATS_ITEM_FOUR(4, link, usec)
				CLIENT_STATS_ITEM_FOUR(4, unlink, usec)
				CLIENT_STATS_ITEM_FOUR(4, symlink, usec)
				CLIENT_STATS_ITEM_FOUR(4, mkdir, usec)
				CLIENT_STATS_ITEM_FOUR(4, rmdir, usec)
				CLIENT_STATS_ITEM_FOUR(4, mknod, usec)
				CLIENT_STATS_ITEM_FOUR(4, rename, usec)
				CLIENT_STATS_ITEM_FOUR(4, statfs, usec)
				CLIENT_STATS_ITEM_FOUR(4, setxattr, usec)
				CLIENT_STATS_ITEM_FOUR(4, getxattr, usec)
				CLIENT_STATS_ITEM_ONE(4, getxattr_hits, reqs)
				CLIENT_STATS_ITEM_FOUR(4, listxattr, usec)
				CLIENT_STATS_ITEM_FOUR(4, removexattr, usec)
				CLIENT_STATS_ITEM_FOUR(4, inode_permission, usec)
			</entry>
		</entry>
	</entry>
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
</definition>

