include(`general.m4')dnl
HEAD(SFA-0.1)
<definition>
	<version>0.1</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show vd c rates</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>vd_c_rates</name>
			<pattern> +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)\| +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)\|</pattern>
			FIELD(4, 1, disk_index, string, vd_rate, ${content:disk_index}, controller0, derive, disk_index, vd_rate, type=disk_index controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 2, controller0_iops, number, vd_rate, ${content:disk_index}, controller0, derive, iops, vd_rate, type=iops controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 3, controller0_KiBps, number, vd_rate, ${content:disk_index}, controller0, derive, KiBps, vd_rate, type=KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 4, controller0_KiBpIO, number, vd_rate, ${content:disk_index}, controller0, derive, KiBps, vd_rate, type=KiBpIO controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 5, controller0_Fwd_iops, number, vd_rate, ${content:disk_index}, controller0, derive, Fwd_iops, vd_rate, type=Fwd_iops controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 6, controller0_Fwd_KiBps, number, vd_rate, ${content:disk_index}, controller0, derive, Fwd_KiBps, vd_rate, type=Fwd_KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 7, controller0_R_KiBps, number, vd_rate, ${content:disk_index}, controller0, derive, R_KiBps, vd_rate, type=R_KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 8, controller0_W_KiBps, number, vd_rate, ${content:disk_index}, controller0, derive, W_KiBps, vd_rate, type=W_KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 9, controller1_iops, number, vd_rate, ${content:disk_index}, controller1, derive, iops, vd_rate, type=iops controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 10, controller1_KiBps, number, vd_rate, ${content:disk_index}, controller1, derive, KiBps, vd_rate, type=KiBps controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 11, controller1_KiBpIO, number, vd_rate, ${content:disk_index}, controller1, derive, KiBpIO, vd_rate, type=KiBpIO controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 12, controller1_Fwd_iops, number, vd_rate, ${content:disk_index}, controller1, derive, Fwd_iops, vd_rate, type=Fwd_iops controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 13, controller1_Fwd_KiBps, number, vd_rate, ${content:disk_index}, controller1, derive, Fwd_KiBps, vd_rate, type=Fwd_KiBps controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 14, controller1_R_KiBps, number, vd_rate, ${content:disk_index}, controller1, derive, R_KiBps, vd_rate, type=R_KiBps controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 15, controller1_W_KiBps, number, vd_rate, ${content:disk_index}, controller1, derive, W_KiBps, vd_rate, type=W_KiBps controller=1 disk_index=${content:disk_index}, 1)
		</item>
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show pd c all</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>pd_c_rates</name>
			<pattern> +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)\| +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)\|</pattern>
			FIELD(4, 1, disk_index, string, pd_rate, ${content:disk_index}, controller0, derive, disk_index, pd_rate, type=disk_index controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 2, controller0_iops, number, pd_rate, ${content:disk_index}, controller0, derive, iops, pd_rate, type=iops controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 3, controller0_KiBps, number, pd_rate, ${content:disk_index}, controller0, derive, KiBps, pd_rate, type=KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 4, controller0_KiBpIO, number, pd_rate, ${content:disk_index}, controller0, derive, KiBps, pd_rate, type=KiBpIO controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 5, controller0_Fwd_iops, number, pd_rate, ${content:disk_index}, controller0, derive, Fwd_iops, pd_rate, type=Fwd_iops controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 6, controller0_Fwd_KiBps, number, pd_rate, ${content:disk_index}, controller0, derive, Fwd_KiBps, pd_rate, type=Fwd_KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 7, controller0_R_KiBps, number, pd_rate, ${content:disk_index}, controller0, derive, R_KiBps, pd_rate, type=R_KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 8, controller0_W_KiBps, number, pd_rate, ${content:disk_index}, controller0, derive, W_KiBps, pd_rate, type=W_KiBps controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 9, controller1_iops, number, pd_rate, ${content:disk_index}, controller1, derive, iops, pd_rate, type=iops controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 10, controller1_KiBps, number, pd_rate, ${content:disk_index}, controller1, derive, KiBps, pd_rate, type=KiBps controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 11, controller1_KiBpIO, number, pd_rate, ${content:disk_index}, controller1, derive, KiBpIO, pd_rate, type=KiBpIO controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 12, controller1_Fwd_iops, number, pd_rate, ${content:disk_index}, controller1, derive, Fwd_iops, pd_rate, type=Fwd_iops controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 13, controller1_Fwd_KiBps, number, pd_rate, ${content:disk_index}, controller1, derive, Fwd_KiBps, pd_rate, type=Fwd_KiBps controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 14, controller1_R_KiBps, number, pd_rate, ${content:disk_index}, controller1, derive, R_KiBps, pd_rate, type=R_KiBps controller=1 disk_index=${content:disk_index}, 1)
			FIELD(4, 15, controller1_W_KiBps, number, pd_rate, ${content:disk_index}, controller1, derive, W_KiBps, pd_rate, type=W_KiBps controller=1 disk_index=${content:disk_index}, 1)
		</item>
		<item>
			<name>pd_read_latency</name>
			CONTEXT(4, ^Physical Disk Read Latency.+
(.+
)*$, 1)
			<pattern> +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)</pattern>
			FIELD(4, 1, disk_index, string, pd_latency, ${content:disk_index}, read, derive, disk_index, pd_latency, type=read time=disk_index disk_index=${content:disk_index}, 1)
			FIELD(4, 2, avg, number, pd_latency, ${content:disk_index}, read, derive, avg, pd_latency, type=read time=avg controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 3, le4ms, number, pd_latency, ${content:disk_index}, read, derive, le4ms, pd_latency, type=read time=le4ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 4, le8ms, number, pd_latency, ${content:disk_index}, read, derive, le8ms, pd_latency, type=read time=le8ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 5, le16ms, number, pd_latency, ${content:disk_index}, read, derive, le16ms, pd_latency, type=read time=le16ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 6, le32ms, number, pd_latency, ${content:disk_index}, read, derive, le32ms, pd_latency, type=read time=le32ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 7, le64ms, number, pd_latency, ${content:disk_index}, read, derive, le64ms, pd_latency, type=read time=le64ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 8, le128ms, number, pd_latency, ${content:disk_index}, read, derive, le128ms, pd_latency, type=read time=le128ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 9, le256ms, number, pd_latency, ${content:disk_index}, read, derive, le256ms, pd_latency, type=read time=le256ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 10, le512ms, number, pd_latency, ${content:disk_index}, read, derive, le512ms, pd_latency, type=read time=le512ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 11, le1s, number, pd_latency, ${content:disk_index}, read, derive, le1s, pd_latency, type=read time=le1s controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 12, le2s, number, pd_latency, ${content:disk_index}, read, derive, le2s, pd_latency, type=read time=le2s controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 13, le4s, number, pd_latency, ${content:disk_index}, read, derive, le4s, pd_latency, type=read time=le4s controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 14, gt4s, number, pd_latency, ${content:disk_index}, read, derive, gt4s, pd_latency, type=read time=gt4s controller=0 disk_index=${content:disk_index}, 1)
		</item>
		<item>
			<name>pd_write_latency</name>
			CONTEXT(4, ^Physical Disk Write Latency.+
(.+
)*$, 1)
			<pattern> +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)</pattern>
			FIELD(4, 1, disk_index, string, pd_latency, ${content:disk_index}, write, derive, disk_index, pd_latency, type=write time=disk_index disk_index=${content:disk_index}, 1)
			FIELD(4, 2, avg, number, pd_latency, ${content:disk_index}, write, derive, avg, pd_latency, type=write time=avg controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 3, le4ms, number, pd_latency, ${content:disk_index}, write, derive, le4ms, pd_latency, type=write time=le4ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 4, le8ms, number, pd_latency, ${content:disk_index}, write, derive, le8ms, pd_latency, type=write time=le8ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 5, le16ms, number, pd_latency, ${content:disk_index}, write, derive, le16ms, pd_latency, type=write time=le16ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 6, le32ms, number, pd_latency, ${content:disk_index}, write, derive, le32ms, pd_latency, type=write time=le32ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 7, le64ms, number, pd_latency, ${content:disk_index}, write, derive, le64ms, pd_latency, type=write time=le64ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 8, le128ms, number, pd_latency, ${content:disk_index}, write, derive, le128ms, pd_latency, type=write time=le128ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 9, le256ms, number, pd_latency, ${content:disk_index}, write, derive, le256ms, pd_latency, type=write time=le256ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 10, le512ms, number, pd_latency, ${content:disk_index}, write, derive, le512ms, pd_latency, type=write time=le512ms controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 11, le1s, number, pd_latency, ${content:disk_index}, write, derive, le1s, pd_latency, type=write time=le1s controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 12, le2s, number, pd_latency, ${content:disk_index}, write, derive, le2s, pd_latency, type=write time=le2s controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 13, le4s, number, pd_latency, ${content:disk_index}, write, derive, le4s, pd_latency, type=write time=le4s controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 14, gt4s, number, pd_latency, ${content:disk_index}, write, derive, gt4s, pd_latency, type=write time=gt4s controller=0 disk_index=${content:disk_index}, 1)
		</item>
		<item>
			<name>pd_read_iosize</name>
			CONTEXT(4, ^Physical Disk Read IO Size.+
(.+
)*$, 1)
			<pattern> +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)</pattern>
			FIELD(4, 1, disk_index, string, pd_iosize, ${content:disk_index}, read, derive, disk_index, pd_iosize, type=read iosize=disk_index disk_index=${content:disk_index}, 1)
			FIELD(4, 2, le4KiB, number, pd_iosize, ${content:disk_index}, read, derive, le4KiB, pd_iosize, type=read iosize=le4KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 3, le8KiB, number, pd_iosize, ${content:disk_index}, read, derive, le4ms, pd_iosize, type=read iosize=le8KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 4, le16KiB, number, pd_iosize, ${content:disk_index}, read, derive, le8ms, pd_iosize, type=read iosize=le16KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 5, le32KiB, number, pd_iosize, ${content:disk_index}, read, derive, le16ms, pd_iosize, type=read iosize=le32KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 6, le64KiB, number, pd_iosize, ${content:disk_index}, read, derive, le32ms, pd_iosize, type=read iosize=le64KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 7, le128KiB, number, pd_iosize, ${content:disk_index}, read, derive, le64ms, pd_iosize, type=read iosize=le128KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 8, le256KiB, number, pd_iosize, ${content:disk_index}, read, derive, le128ms, pd_iosize, type=read iosize=le256KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 9, le512KiB, number, pd_iosize, ${content:disk_index}, read, derive, le256ms, pd_iosize, type=read iosize=le512KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 10, le1MiB, number, pd_iosize, ${content:disk_index}, read, derive, le512ms, pd_iosize, type=read iosize=le1MiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 11, le2MiB, number, pd_iosize, ${content:disk_index}, read, derive, le1s, pd_iosize, type=read iosize=le2MiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 12, le4MiB, number, pd_iosize, ${content:disk_index}, read, derive, le2s, pd_iosize, type=read iosize=le4MiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 13, gt4MiB, number, pd_iosize, ${content:disk_index}, read, derive, le4s, pd_iosize, type=read iosize=gt4MiB controller=0 disk_index=${content:disk_index}, 1)
		</item>
		<item>
			<name>pd_write_iosize</name>
			CONTEXT(4, ^Physical Disk Write IO Size.+
(.+
)*$, 1)
			<pattern> +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)</pattern>
			FIELD(4, 1, disk_index, string, pd_iosize, ${content:disk_index}, write, derive, disk_index, pd_iosize, type=write iosize=disk_index disk_index=${content:disk_index}, 1)
			FIELD(4, 2, le4KiB, number, pd_iosize, ${content:disk_index}, write, derive, le4KiB, pd_iosize, type=write iosize=le4KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 3, le8KiB, number, pd_iosize, ${content:disk_index}, write, derive, le4ms, pd_iosize, type=write iosize=le8KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 4, le16KiB, number, pd_iosize, ${content:disk_index}, write, derive, le8ms, pd_iosize, type=write iosize=le16KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 5, le32KiB, number, pd_iosize, ${content:disk_index}, write, derive, le16ms, pd_iosize, type=write iosize=le32KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 6, le64KiB, number, pd_iosize, ${content:disk_index}, write, derive, le32ms, pd_iosize, type=write iosize=le64KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 7, le128KiB, number, pd_iosize, ${content:disk_index}, write, derive, le64ms, pd_iosize, type=write iosize=le128KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 8, le256KiB, number, pd_iosize, ${content:disk_index}, write, derive, le128ms, pd_iosize, type=write iosize=le256KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 9, le512KiB, number, pd_iosize, ${content:disk_index}, write, derive, le256ms, pd_iosize, type=write iosize=le512KiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 10, le1MiB, number, pd_iosize, ${content:disk_index}, write, derive, le512ms, pd_iosize, type=write iosize=le1MiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 11, le2MiB, number, pd_iosize, ${content:disk_index}, write, derive, le1s, pd_iosize, type=write iosize=le2MiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 12, le4MiB, number, pd_iosize, ${content:disk_index}, write, derive, le2s, pd_iosize, type=write iosize=le4MiB controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 13, gt4MiB, number, pd_iosize, ${content:disk_index}, write, derive, le4s, pd_iosize, type=write iosize=gt4MiB controller=0 disk_index=${content:disk_index}, 1)
		</item>
	</entry>
</definition>
