include(`sfa.m4')dnl
HEAD(SFA-0.1)
<definition>
	<version>3.0</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show vd c all</path>
		</subpath>
		<mode>file</mode>
		DISK_RATE(2, vd, 1, `Virtual', `Virtual Disk Read Latency')
		VD_LATENCY(2, read, Read, 1, `Virtual Disk Write Latency')
		VD_LATENCY(2, write, Write, 1, `Virtual Disk Read IO Size')
		IOSIZE(2, vd, Virtual, read, Read, 1, `Virtual Disk Write IO Size')
		IOSIZE(2, vd, Virtual, write, Write, 1, `')
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show pd c all</path>
		</subpath>
		<mode>file</mode>
		DISK_RATE(2, pd, 1, `Physical', `Physical Disk Read Latency')
		PD_LATENCY(2, read, Read, 1, `Physical Disk Write Latency')
		PD_LATENCY(2, write, Write, 1, `Physical Disk Read IO Size')
		IOSIZE(2, pd, Physical, read, Read, 1, `Physical Disk Write IO Size')
		IOSIZE(2, pd, Physical, write, Write, 1, `')
	</entry>
</definition>
