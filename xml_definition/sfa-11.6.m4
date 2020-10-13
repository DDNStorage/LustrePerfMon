include(`sfa.m4')dnl
include(`sfa-11-general.m4')dnl
dnl
dnl definition of DISK_RATE_AFTER_11_6
dnl $1: number of INDENT
dnl $2: name of DISK_RATE, vd or pd
dnl $3: is first child of parent ELEMENT
dnl $4: name of DISK_RATE, Virtual or Physical
dnl $5: context end string
define(`DISK_RATE_AFTER_11_6',
        `ELEMENT($1, item,
        `NAME($1 + 1, $2_c_rates, 1)
CONTEXT_SUBTYPE($1 + 1, `$4 Disk Counters:', $5, 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) *\| +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) *\|', 0)
FIELD($1 + 1, 1, disk_index, string, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, disk_index, $2_rate, type=disk_index controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, controller0_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, iops, $2_rate, type=iops controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, controller0_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, KiBps, $2_rate, type=KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, controller0_KiBpIO, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, KiBpIO, $2_rate, type=KiBpIO controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, controller0_Fwd_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, Fwd_iops, $2_rate, type=Fwd_iops controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, controller0_Fwd_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, Fwd_KiBps, $2_rate, type=Fwd_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, controller0_R_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, R_KiBps, $2_rate, type=R_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, controller0_W_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, W_KiBps, $2_rate, type=W_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, controller0_Unmap_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller0, gauge, Unmap_KiBps, $2_rate, type=Unmap_KiBps controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, controller1_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, iops, $2_rate, type=iops controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, controller1_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, KiBps, $2_rate, type=KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, controller1_KiBpIO, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, KiBpIO, $2_rate, type=KiBpIO controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 13, controller1_Fwd_iops, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, Fwd_iops, $2_rate, type=Fwd_iops controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 14, controller1_Fwd_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, Fwd_KiBps, $2_rate, type=Fwd_KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 15, controller1_R_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, R_KiBps, $2_rate, type=R_KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 16, controller1_W_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, W_KiBps, $2_rate, type=W_KiBps controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 17, controller1_Unmap_KiBps, number, ${extra_tag:extrahost}, $2_rate_${content:disk_index}, controller1, gauge, Unmap_KiBps, $2_rate, type=Unmap_KiBps controller=1 disk_index=${content:disk_index}, 0)', $3)')dnl
dnl
dnl
dnl definition of UNMAP
dnl $1: number of INDENT
dnl $2: name of UNMAP, vd or pd
dnl $3: is first child of parent ELEMENT
dnl $4: context end string
define(`UNMAP',
        `ELEMENT($1, item,
        `NAME($1 + 1, $2_unmap, 1)
CONTEXT_SUBTYPE($1 + 1, `  Idx  Unmap Count Unmap Blocks| Unmap Count Unmap Blocks|', $4, 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)\| +([[:digit:]]+) +([[:digit:]]+)\|', 0)
FIELD($1 + 1, 1, disk_index, string, ${extra_tag:extrahost}, $2_unmap_${content:disk_index}, controller0, gauge, disk_index, $2_unmap, type=disk_index controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, controller0_Unmap_Count, number, ${extra_tag:extrahost}, $2_unmap_${content:disk_index}, controller0, derive, count, $2_unmap, type=count controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, controller0_Unmap_Blocks, number, ${extra_tag:extrahost}, $2_unmap_${content:disk_index}, controller0, derive, blocks, $2_unmap, type=blocks controller=0 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, controller1_Unmap_Count, number, ${extra_tag:extrahost}, $2_unmap_${content:disk_index}, controller1, derive, count, $2_unmap, type=count controller=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, controller1_Unmap_Blocks, number, ${extra_tag:extrahost}, $2_unmap_${content:disk_index}, controller1, derive, blocks, $2_unmap, type=blocks controller=1 disk_index=${content:disk_index}, 0)', $3)')dnl
dnl
HEAD(SFA-0.1)
<definition>
	<version>11.0</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show vd c all</path>
		</subpath>
		<mode>file</mode>
		DISK_RATE_AFTER_11_6(2, vd, 1, `Virtual', `Virtual Disk Read Latency')
		VD_LATENCY(2, read, Read, 1, `Virtual Disk Write Latency')
		VD_LATENCY(2, write, Write, 1, `Virtual Disk Read IO Size')
		IOSIZE(2, vd, Virtual, read, Read, 1, `Virtual Disk Write IO Size')
		IOSIZE(2, vd, Virtual, write, Write, 1, `Virtual Disk Qdepth')
		VD_QDEPTH(2, 0, `Virtual Disk Qdepth', 1)
		VD_QDEPTH(2, 1, `', 1)
		UNMAP(2, vd, 1, `')
	</entry>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>show pd c all</path>
		</subpath>
		<mode>file</mode>
		DISK_RATE_AFTER_11_6(2, pd, 1, `Physical', `Physical Disk Read Latency')
		PD_LATENCY(2, read, Read, 1, `Physical Disk Write Latency')
		PD_LATENCY(2, write, Write, 1, `Physical Disk Read IO Size')
		IOSIZE(2, pd, Physical, read, Read, 1, `Physical Disk Write IO Size')
		IOSIZE(2, pd, Physical, write, Write, 1, `')
		UNMAP(2, pd, 1, `')
	</entry>
</definition>
