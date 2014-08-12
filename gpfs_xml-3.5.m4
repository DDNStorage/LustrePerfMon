include(`general_xml.m4')dnl
HEAD(GPFS-3.5)
<definition>
	<version>3.5</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>fs_io_s</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>fs_io_s</name>
			<pattern>_fs_io_s_ _n_ (.+) _nn_ (.+) _rc_ .+ _t_ .+ _tu_ .+ _cl_ (.+) _fs_ (.+) _d_ .+ _br_ (.+) _bw_ (.+) _oc_ (.+) _cc_ (.+) _rdc_ (.+) _wc_ (.+) _dir_ (.+) _iu_ (.+)</pattern>
			FIELD(4, 1, IP, string, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, NA, 1)
			FIELD(4, 2, hostname, string, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, NA, 1)
			FIELD(4, 3, cluster, string, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, NA, 1)
			FIELD(4, 4, filesystem, string, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, NA, 1)
			FIELD(4, 5, bytes_read, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, bytes_read, 1)
			FIELD(4, 6, bytes_write, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, bytes_write, 1)
			FIELD(4, 7, open_count, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, open_count, 1)
			FIELD(4, 8, close_count, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, close_count, 1)
			FIELD(4, 9, read_count, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, read_count, 1)
			FIELD(4, 10, write_count, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, write_count, 1)
			FIELD(4, 11, readdir_count, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, readdir_count, 1)
			FIELD(4, 12, inode_upate_count, number, ${content:cluster}, ${content:filesystem}, ${content:hostname}, derive, inode_upate_count, 1)
		</item>
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>io_s</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>io_s</name>
			<pattern>_io_s_ _n_ (.+) _nn_ (.+) _rc_ .+ _t_ .+ _tu_ .+ _br_ (.+) _bw_ (.+) _oc_ (.+) _cc_ (.+) _rdc_ (.+) _wc_ (.+) _dir_ (.+) _iu_ (.+)</pattern>
			FIELD(4, 1, IP, string, ${content:hostname}, , , derive, NA, 1)
			FIELD(4, 2, hostname, string, ${content:hostname}, , , derive, NA, 1)
			FIELD(4, 3, bytes_read, number, ${content:hostname}, , , derive, bytes_read, 1)
			FIELD(4, 4, bytes_write, number, ${content:hostname}, , , derive, bytes_write, 1)
			FIELD(4, 5, open_count, number, ${content:hostname}, , , derive, open_count, 1)
			FIELD(4, 6, close_count, number, ${content:hostname}, , , derive, close_count, 1)
			FIELD(4, 7, read_count, number, ${content:hostname}, , , derive, read_count, 1)
			FIELD(4, 8, write_count, number, ${content:hostname}, , , derive, write_count, 1)
			FIELD(4, 9, readdir_count, number, ${content:hostname}, , , derive, readdir_count, 1)
			FIELD(4, 10, inode_upate_count, number, ${content:hostname}, , , derive, inode_upate_count, 1)
		</item>
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>rhist on
rhist s</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>rhist_write_size</name>
			<context>^_rhist_ _n_ .+ _nn_ .+ _req_ s _rc_ .+ _t_ .+ _tu_ .+ _k_ w
(_[R|L]_ .+
)*</context>
			<pattern>_R_ (.+) (.+) _NR_ (.+)</pattern>
			FIELD(4, 1, size_minimum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 2, size_maximum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_write, size_${content:size_minimum}_to_${content:size_maximum}, derive, request_number, 1)
		</item>
		<item>
			<name>rhist_write_latency</name>
			<context>^_rhist_ _n_ .+ _nn_ .+ _req_ s _rc_ .+ _t_ .+ _tu_ .+ _k_ w
(_[R|L]_ .+
)*</context>
			<pattern>_L_ (.+) (.+) _NL_ (.+)</pattern>
			FIELD(4, 1, latency_minimum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 2, latency_maximum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_write, latency_${content:latency_minimum}_to_${content:latency_maximum}, derive, request_number, 1)
		</item>
		<item>
			<name>rhist_read_size</name>
			<context>^_rhist_ _n_ .+ _nn_ .+ _req_ s _rc_ .+ _t_ .+ _tu_ .+ _k_ r
(_[R|L]_ .+
)*</context>
			<pattern>_R_ (.+) (.+) _NR_ (.+)</pattern>
			FIELD(4, 1, size_minimum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 2, size_maximum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_read, size_${content:size_minimum}_to_${content:size_maximum}, derive, request_number, 1)
		</item>
		<item>
			<name>rhist_read_latency</name>
			<context>^_rhist_ _n_ .+ _nn_ .+ _req_ s _rc_ .+ _t_ .+ _tu_ .+ _k_ r
(_[R|L]_ .+
)*</context>
			<pattern>_L_ (.+) (.+) _NL_ (.+)</pattern>
			FIELD(4, 1, latency_minimum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 2, latency_maximum, string, ${key:hostname}, , , derive, , 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_read, latency_${content:latency_minimum}_to_${content:latency_maximum}, derive, request_number, 1)
		</item>
	</entry>
</definition>

