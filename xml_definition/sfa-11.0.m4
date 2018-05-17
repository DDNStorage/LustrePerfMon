include(`sfa.m4')dnl
dnl
dnl definition of VD_QDEPTH
dnl $1: number of INDENT
dnl $2: controller index, 0 or 1
dnl $3: context end string
dnl $4: is first child of parent ELEMENT
define(`VD_QDEPTH',
        `ELEMENT($1, item,
        `NAME($1 + 1, vd_qdepth_controller_$2, 1)
CONTEXT_SUBTYPE($1 + 1, `Virtual Disk Qdepth', $3, 0)
PATTERN($1 + 1, `^ +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+) +([[:digit:]]+)', 0)
FIELD($1 + 1, 1, disk_index, string, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, disk_index, vd_qdepth, controller=$2 qdepth=disk_index disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 2, 1, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 1, vd_qdepth, controller=$2 qdepth=1 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 3, 2, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 2, vd_qdepth, controller=$2 qdepth=2 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 4, 3to4, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 3to4, vd_qdepth, controller=$2 qdepth=3to4 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 5, 5to8, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 5to8, vd_qdepth, controller=$2 qdepth=5to8 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 6, 9to16, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 9to16, vd_qdepth, controller=$2 qdepth=9to16 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 7, 17to32, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 17to32, vd_qdepth, controller=$2 qdepth=17to32 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 8, 33to64, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 33to64, vd_qdepth, controller=$2 qdepth=33to64 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 9, 65to128, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 65to128, vd_qdepth, controller=$2 qdepth=65to128 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 10, 129to256, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 129to256, vd_qdepth, controller=$2 qdepth=129to256 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 11, 257to512, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, 257to512, vd_qdepth, controller=$2 qdepth=257to512 disk_index=${content:disk_index}, 0)
FIELD($1 + 1, 12, gt512, number, ${extra_tag:extrahost}, vd_qdepth_${content:disk_index}, $2, gauge, gt512, vd_qdepth, controller=$2 qdepth=gt512 disk_index=${content:disk_index}, 0)', $4)')dnl
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
		DISK_RATE(2, vd, 1, `Virtual', `Virtual Disk Read Latency')
		VD_LATENCY(2, read, Read, 1, `Virtual Disk Write Latency')
		VD_LATENCY(2, write, Write, 1, `Virtual Disk Read IO Size')
		IOSIZE(2, vd, Virtual, read, Read, 1, `Virtual Disk Write IO Size')
		IOSIZE(2, vd, Virtual, write, Write, 1, `Virtual Disk Qdepth')
		VD_QDEPTH(2, 0, `Virtual Disk Qdepth', 1)
		VD_QDEPTH(2, 1, `', 1)
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
