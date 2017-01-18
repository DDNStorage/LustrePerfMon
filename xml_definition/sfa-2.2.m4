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
FIELD($1 + 1, 1, disk_index, string, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, disk_index, $2_rate, type=disk_index controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, controller0_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, iops, $2_rate, type=iops controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, controller0_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, KiBps, $2_rate, type=KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, controller0_KiBpIO, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, KiBpIO, $2_rate, type=KiBpIO controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, controller0_Fwd_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, Fwd_iops, $2_rate, type=Fwd_iops controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, controller0_Fwd_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, Fwd_KiBps, $2_rate, type=Fwd_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, controller0_R_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, R_KiBps, $2_rate, type=R_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, controller0_W_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, W_KiBps, $2_rate, type=W_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, controller1_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, iops, $2_rate, type=iops controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, controller1_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, KiBps, $2_rate, type=KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, controller1_KiBpIO, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, KiBpIO, $2_rate, type=KiBpIO controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, controller1_Fwd_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, Fwd_iops, $2_rate, type=Fwd_iops controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, controller1_Fwd_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, Fwd_KiBps, $2_rate, type=Fwd_KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 14, controller1_R_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, R_KiBps, $2_rate, type=R_KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 15, controller1_W_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, W_KiBps, $2_rate, type=W_KiBps controller=1 disk_index=${content:disk_index}, 0)', $3)')dnl
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
)*', 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, disk_index, string, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, disk_index, pd_latency, type=$2 latency=disk_index disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, avg, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, avg, pd_latency, type=$2 latency=avg disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, le4ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le4ms, pd_latency, type=$2 latency=le4ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, le8ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le8ms, pd_latency, type=$2 latency=le8ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, le16ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le16ms, pd_latency, type=$2 latency=le16ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, le32ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le32ms, pd_latency, type=$2 latency=le32ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, le64ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le64ms, pd_latency, type=$2 latency=le64ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, le128ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le128ms, pd_latency, type=$2 latency=le128ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, le256ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le256ms, pd_latency, type=$2 latency=le256ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, le512ms, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le512ms, pd_latency, type=$2 latency=le512ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, le1s, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le1s, pd_latency, type=$2 latency=le1s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, le2s, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le2s, pd_latency, type=$2 latency=le2s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, le4s, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, le4s, pd_latency, type=$2 latency=le4s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 14, gt4s, number, ${extra_tag:extrahost}, pd_latency_${content:disk_index}, $2, gauge, gt4s, pd_latency, type=$2 latency=gt4s disk_index=${content:disk_index}, 0)', $4)')dnl
dnl
dnl definition of IOSIZE
dnl $1: number of INDENT
dnl $2: name of DISK_RATE, vd or pd
dnl $3: name of DISK_RATE, Virtual or Physical
dnl $4: type of IOSIZE, read or write
dnl $5: Type of IOSIZE, Read or Write
dnl $6: is first child of parent ELEMENT
define(`IOSIZE',
        `ELEMENT($1, item,
        `NAME($1 + 1, $2_$4_iosize, 1)
CONTEXT($1 + 1, `^$3 Disk $5 IO Size.+
(.+
)*', 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, disk_index, string, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, disk_index, $2_iosize, type=$4 iosize=disk_index disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, le4KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le4KiB, $2_iosize, type=$4 iosize=le4KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, le8KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le8KiB, $2_iosize, type=$4 iosize=le8KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, le16KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le16KiB, $2_iosize, type=$4 iosize=le16KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, le32KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le32KiB, $2_iosize, type=$4 iosize=le32KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, le64KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le64KiB, $2_iosize, type=$4 iosize=le64KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, le128KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le128KiB, $2_iosize, type=$4 iosize=le128KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, le256KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le256KiB, $2_iosize, type=$4 iosize=le256KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, le512KiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le512KiB, $2_iosize, type=$4 iosize=le512KiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, le1MiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le1MiB, $2_iosize, type=$4 iosize=le1MiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, le2MiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le2MiB, $2_iosize, type=$4 iosize=le2MiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, le4MiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, le4MiB, $2_iosize, type=$4 iosize=le4MiB disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, gt4MiB, number, ${extra_tag:extrahost}, $2_iosize_${content:disk_index}, $4, gauge, gt4MiB, $2_iosize, type=$4 iosize=gt4MiB disk_index=${content:disk_index}, 0)', $6)')dnl
dnl
dnl definition of VD_LATENCY
dnl $1: number of INDENT
dnl $2: type of VD_LATENCY, read or write
dnl $3: Type of VD_LATENCY, Read or Write
dnl $4: is first child of parent ELEMENT
define(`VD_LATENCY',
        `ELEMENT($1, item,
        `NAME($1 + 1, vd_$2_latency, 1)
CONTEXT($1 + 1, `^Virtual Disk $3 Latency.+
(.+
)*', 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, disk_index, string, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, disk_index, vd_latency, type=$2 latency=disk_index disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, avg, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, avg, vd_latency, type=$2 latency=avg disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, le16ms, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le16ms, vd_latency, type=$2 latency=le16ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, le32ms, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le32ms, vd_latency, type=$2 latency=le32ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, le64ms, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le64ms, vd_latency, type=$2 latency=le64ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, le128ms, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le128ms, vd_latency, type=$2 latency=le128ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, le256ms, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le256ms, vd_latency, type=$2 latency=le256ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, le512ms, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le512ms, vd_latency, type=$2 latency=le512ms disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, le1s, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le1s, vd_latency, type=$2 latency=le1s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, le2s, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le2s, vd_latency, type=$2 latency=le2s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, le4s, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le4s, vd_latency, type=$2 latency=le4s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, le8s, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le8s, vd_latency, type=$2 latency=le8s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, le16s, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, le16s, vd_latency, type=$2 latency=le16s disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 14, gt16s, number, ${extra_tag:extrahost}, vd_latency_${content:disk_index}, $2, gauge, gt16s, vd_latency, type=$2 latency=gt16s disk_index=${content:disk_index}, 0)', $4)')dnl
dnl
HEAD(SFA-0.1)
<definition>
	<version>0.1</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show vd c all</path>
		</subpath>
		<mode>file</mode>
		DISK_RATE(2, vd, 1)
		VD_LATENCY(2, read, Read, 1)
		VD_LATENCY(2, write, Write, 1)
		IOSIZE(2, vd, Virtual, read, Read, 1)
		IOSIZE(2, vd, Virtual, write, Write, 1)
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
		IOSIZE(2, pd, Physical, read, Read, 1)
		IOSIZE(2, pd, Physical, write, Write, 1)
	</entry>
</definition>
