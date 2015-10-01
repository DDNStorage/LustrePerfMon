include(`general.m4')dnl
dnl
dnl definition of DISK_RATE
dnl $1: number of INDENT
dnl $2: name of DISK_RATE
dnl $3: is first child of parent ELEMENT
define(`DISK_RATE',
        `ELEMENT($1, item,
        `NAME($1 + 1, $2_c_rates, 1)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)\| +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)\|', 0)
FIELD($1 + 1, 1, disk_index, string, $2_rate, ${content:disk_index}, controller0, derive, disk_index, $2_rate, type=disk_index controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, controller0_iops, number, $2_rate, ${content:disk_index}, controller0, derive, iops, $2_rate, type=iops controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, controller0_KiBps, number, $2_rate, ${content:disk_index}, controller0, derive, KiBps, $2_rate, type=KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, controller0_KiBpIO, number, $2_rate, ${content:disk_index}, controller0, derive, KiBpIO, $2_rate, type=KiBpIO controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, controller0_Fwd_iops, number, $2_rate, ${content:disk_index}, controller0, derive, Fwd_iops, $2_rate, type=Fwd_iops controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, controller0_Fwd_KiBps, number, $2_rate, ${content:disk_index}, controller0, derive, Fwd_KiBps, $2_rate, type=Fwd_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, controller0_R_KiBps, number, $2_rate, ${content:disk_index}, controller0, derive, R_KiBps, $2_rate, type=R_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, controller0_W_KiBps, number, $2_rate, ${content:disk_index}, controller0, derive, W_KiBps, $2_rate, type=W_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, controller1_iops, number, $2_rate, ${content:disk_index}, controller1, derive, iops, $2_rate, type=iops controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, controller1_KiBps, number, $2_rate, ${content:disk_index}, controller1, derive, KiBps, $2_rate, type=KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, controller1_KiBpIO, number, $2_rate, ${content:disk_index}, controller1, derive, KiBpIO, $2_rate, type=KiBpIO controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, controller1_Fwd_iops, number, $2_rate, ${content:disk_index}, controller1, derive, Fwd_iops, $2_rate, type=Fwd_iops controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, controller1_Fwd_KiBps, number, $2_rate, ${content:disk_index}, controller1, derive, Fwd_KiBps, $2_rate, type=Fwd_KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 14, controller1_R_KiBps, number, $2_rate, ${content:disk_index}, controller1, derive, R_KiBps, $2_rate, type=R_KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 15, controller1_W_KiBps, number, $2_rate, ${content:disk_index}, controller1, derive, W_KiBps, $2_rate, type=W_KiBps controller=1 disk_index=${content:disk_index}, 0)', $3)')dnl
dnl
dnl definition of PD_LATENCY
dnl $1: number of INDENT
dnl $2: type of PD_LATENCY, read or write
dnl $3: Type of PD_LATENCY, Read or Write
dnl $4: is first child of parent ELEMENT
define(`PD_LATENCY',
        `ELEMENT($1, item,
        `NAME($1 + 1, pd_$2_latency, 1)
CONTEXT($1 + 1, `^Physical Disk $3 Latency.+
(.+
)*$', 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, disk_index, string, pd_latency, ${content:disk_index}, $2, derive, disk_index, pd_latency, type=$2 time=disk_index disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, avg, number, pd_latency, ${content:disk_index}, $2, derive, avg, pd_latency, type=$2 time=avg disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, le4ms, number, pd_latency, ${content:disk_index}, $2, derive, le4ms, pd_latency, type=$2 time=le4ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, le8ms, number, pd_latency, ${content:disk_index}, $2, derive, le8ms, pd_latency, type=$2 time=le8ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, le16ms, number, pd_latency, ${content:disk_index}, $2, derive, le16ms, pd_latency, type=$2 time=le16ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, le32ms, number, pd_latency, ${content:disk_index}, $2, derive, le32ms, pd_latency, type=$2 time=le32ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, le64ms, number, pd_latency, ${content:disk_index}, $2, derive, le64ms, pd_latency, type=$2 time=le64ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, le128ms, number, pd_latency, ${content:disk_index}, $2, derive, le128ms, pd_latency, type=$2 time=le128ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, le256ms, number, pd_latency, ${content:disk_index}, $2, derive, le256ms, pd_latency, type=$2 time=le256ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, le512ms, number, pd_latency, ${content:disk_index}, $2, derive, le512ms, pd_latency, type=$2 time=le512ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, le1s, number, pd_latency, ${content:disk_index}, $2, derive, le1s, pd_latency, type=$2 time=le1s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, le2s, number, pd_latency, ${content:disk_index}, $2, derive, le2s, pd_latency, type=$2 time=le2s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, le4s, number, pd_latency, ${content:disk_index}, $2, derive, le4s, pd_latency, type=$2 time=le4s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 14, gt4s, number, pd_latency, ${content:disk_index}, $2, derive, gt4s, pd_latency, type=$2 time=gt4s disk_index=${content:disk_index}, 0)', $4)')dnl
dnl
dnl definition of PD_IOSIZE
dnl $1: number of INDENT
dnl $2: type of PD_IOSIZE, read or write
dnl $3: Type of PD_IOSIZE, Read or Write
dnl $4: is first child of parent ELEMENT
define(`PD_IOSIZE',
        `ELEMENT($1, item,
        `NAME($1 + 1, pd_$2_iosize, 1)
CONTEXT($1 + 1, `^Physical Disk $3 IO Size.+
(.+
)*$', 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, disk_index, string, pd_iosize, ${content:disk_index}, $2, derive, disk_index, pd_iosize, type=$2 iosize=disk_index disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, le4KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le4KiB, pd_iosize, type=$2 iosize=le4KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, le8KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le8KiB, pd_iosize, type=$2 iosize=le8KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, le16KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le16KiB, pd_iosize, type=$2 iosize=le16KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, le32KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le32KiB, pd_iosize, type=$2 iosize=le32KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, le64KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le64KiB, pd_iosize, type=$2 iosize=le64KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, le128KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le128KiB, pd_iosize, type=$2 iosize=le128KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, le256KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le256KiB, pd_iosize, type=$2 iosize=le256KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, le512KiB, number, pd_iosize, ${content:disk_index}, $2, derive, le512KiB, pd_iosize, type=$2 iosize=le512KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, le1MiB, number, pd_iosize, ${content:disk_index}, $2, derive, le1MiB, pd_iosize, type=$2 iosize=le1MiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, le2MiB, number, pd_iosize, ${content:disk_index}, $2, derive, le2MiB, pd_iosize, type=$2 iosize=le2MiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, le4MiB, number, pd_iosize, ${content:disk_index}, $2, derive, le4MiB, pd_iosize, type=$2 iosize=le4MiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, gt4MiB, number, pd_iosize, ${content:disk_index}, $2, derive, gt4MiB, pd_iosize, type=$2 iosize=gt4MiB disk_index=${content:disk_index}, 0)', $4)')dnl
dnl
HEAD(SFA-0.1)
<definition>
	<version>0.1</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show vd c rates</path>
		</subpath>
		<mode>file</mode>
		DISK_RATE(2, vd, 1)
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show pd c all</path>
		</subpath>
		<mode>file</mode>
		DISK_RATE(2, pd, 1)
		PD_LATENCY(2, read, Read, 1)
		PD_LATENCY(2, write, Write, 1)
		PD_IOSIZE(2, read, Read, 1)
		PD_IOSIZE(2, write, Write, 1)
	</entry>
</definition>
