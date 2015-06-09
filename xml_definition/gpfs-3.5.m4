include(`general.m4')dnl
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
			FIELD(4, 1, IP, string, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, NA, host_ip, cluster=${content:cluster} fs_name=${content:filesystem}, 1)
			FIELD(4, 2, hostname, string, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, NA, hostname, cluster=${content:cluster} fs_name=${content:filesystem}, 1)
			FIELD(4, 3, cluster, string, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, NA, cluster, fs_name=${content:filesystem}, 1)
			FIELD(4, 4, filesystem, string, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, NA, fs_name, cluster=${content:cluster}, 1)
			FIELD(4, 5, bytes_read, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, bytes_read, fs_io_bytes, optype=read fs_name=${content:filesystem} cluster=${content:cluster}, 1)
			FIELD(4, 6, bytes_write, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, bytes_write, fs_io_bytes, optype=write fs_name=${content:filesystem} cluster=${content:cluster}, 1)
			FIELD(4, 7, open_count, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, open_count, fs_io_count, optype=open fs_name=${content:filesystem} cluster=${content:cluster}, 1)
			FIELD(4, 8, close_count, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, close_count, fs_io_count, optype=close fs_name=${content:filesystem} cluster=${content:cluster}, 1)
			FIELD(4, 9, read_count, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, read_count, fs_io_count, optype=read fs_name=${content:filesystem} cluster=${content:cluster}, 1)
			FIELD(4, 10, write_count, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, write_count, fs_io_count, optype=write fs_name=${content:filesystem} cluster=${content:cluster}, 1)
			FIELD(4, 11, readdir_count, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, readdir_count, fs_io_count, optype=readdir fs_name=${content:filesystem} cluster=${content:cluster}, 1)
			FIELD(4, 12, inode_upate_count, number, ${key:hostname}, ${content:cluster}, ${content:filesystem}, derive, inode_upate_count, fs_io_count, optype=inode_update fs_name=${content:filesystem} cluster=${content:cluster}, 1)
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
			FIELD(4, 1, IP, string, ${key:hostname}, , , derive, NA, host_ip, , 1)
			FIELD(4, 2, hostname, string, ${key:hostname}, , , derive, NA, hostname, , 1)
			FIELD(4, 3, bytes_read, number, ${key:hostname}, , , derive, bytes_read, io_bytes, optype=read, 1)
			FIELD(4, 4, bytes_write, number, ${key:hostname}, , , derive, bytes_write, io_bytes, optype=write, 1)
			FIELD(4, 5, open_count, number, ${key:hostname}, , , derive, open_count, io_count, optype=open, 1)
			FIELD(4, 6, close_count, number, ${key:hostname}, , , derive, close_count, io_count, optype=close, 1)
			FIELD(4, 7, read_count, number, ${key:hostname}, , , derive, read_count, io_count, optype=read, 1)
			FIELD(4, 8, write_count, number, ${key:hostname}, , , derive, write_count, io_count, optype=write, 1)
			FIELD(4, 9, readdir_count, number, ${key:hostname}, , , derive, readdir_count, io_count, optype=readdir, 1)
			FIELD(4, 10, inode_upate_count, number, ${key:hostname}, , , derive, inode_upate_count, io_count, optype=inode_update, 1)
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
			FIELD(4, 1, size_minimum, string, ${key:hostname}, , , derive, , minimum_size, optype=write, 1)
			FIELD(4, 2, size_maximum, string, ${key:hostname}, , , derive, , maximum_size, optype=write, 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_write, size_${content:size_minimum}_to_${content:size_maximum}, derive, request_number, rhist_request_size_number, optype=write extent=${content:size_minimum}_to_${content:size_maximum}, 1)
		</item>
		<item>
			<name>rhist_write_latency</name>
			<context>^_rhist_ _n_ .+ _nn_ .+ _req_ s _rc_ .+ _t_ .+ _tu_ .+ _k_ w
(_[R|L]_ .+
)*</context>
			<pattern>_L_ (.+) (.+) _NL_ (.+)</pattern>
			FIELD(4, 1, latency_minimum, string, ${key:hostname}, , , derive, , minimum_latency, optype=write, 1)
			FIELD(4, 2, latency_maximum, string, ${key:hostname}, , , derive, , maximum_latency, optype=write, 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_write, latency_${content:latency_minimum}_to_${content:latency_maximum}, derive, request_number, rhist_request_latency_number, optype=write extent=${content:latency_minimum}_to_${content:latency_maximum}, 1)
		</item>
		<item>
			<name>rhist_read_size</name>
			<context>^_rhist_ _n_ .+ _nn_ .+ _req_ s _rc_ .+ _t_ .+ _tu_ .+ _k_ r
(_[R|L]_ .+
)*</context>
			<pattern>_R_ (.+) (.+) _NR_ (.+)</pattern>
			FIELD(4, 1, size_minimum, string, ${key:hostname}, , , derive, , minimum_size, optype=read, 1)
			FIELD(4, 2, size_maximum, string, ${key:hostname}, , , derive, , maximum_size, optype=read, 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_read, size_${content:size_minimum}_to_${content:size_maximum}, derive, request_number, rhist_request_size_number, optype=read extent=${content:size_minimum}_to_${content:size_maximum}, 1)
		</item>
		<item>
			<name>rhist_read_latency</name>
			<context>^_rhist_ _n_ .+ _nn_ .+ _req_ s _rc_ .+ _t_ .+ _tu_ .+ _k_ r
(_[R|L]_ .+
)*</context>
			<pattern>_L_ (.+) (.+) _NL_ (.+)</pattern>
			FIELD(4, 1, latency_minimum, string, ${key:hostname}, , , derive, , minimum_latency, optype=read, 1)
			FIELD(4, 2, latency_maximum, string, ${key:hostname}, , , derive, , maximum_latency, optype=read, 1)
			FIELD(4, 3, request_number, number, ${key:hostname}, gpfs_rhlist_read, latency_${content:latency_minimum}_to_${content:latency_maximum}, derive, request_number, rhist_request_latency_number, optype=read extent=${content:latency_minimum}_to_${content:latency_maximum}, 1)
		</item>
	</entry>
</definition>

