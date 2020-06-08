include(`lustre.m4')dnl
HEAD(Lustre-es5_1)
<definition>
	<version>es5_1</version>
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
	LUSTRE2_12_XML_ENTRIES()
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
</definition>

