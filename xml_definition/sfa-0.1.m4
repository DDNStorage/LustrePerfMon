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
			FIELD(4, 1, disk_index, number, controller0, ${content:disk_index}, , derive, NA, disk_index, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 2, controller0_iops, number, controller0, ${content:disk_index}, , derive, NA, iops, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 3, controller0_KiBps, number, controller0, ${content:disk_index}, , derive, NA, KiBps, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 4, controller0_KiBpIO, number, controller0, ${content:disk_index}, , derive, NA, KiBpIO, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 5, controller0_Fwd_iops, number, controller0, ${content:disk_index}, , derive, NA, Fwd_iops, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 6, controller0_Fwd_KiBps, number, controller0, ${content:disk_index}, , derive, NA, Fwd_KiBps, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 7, controller0_R_KiBps, number, controller0, ${content:disk_index}, , derive, NA, R_KiBps, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 8, controller0_W_KiBps, number, controller0, ${content:disk_index}, , derive, NA, W_KiBps, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 9, controller1_iops, number, controller1, ${content:disk_index}, , derive, NA, iops, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 10, controller1_KiBps, number, controller1, ${content:disk_index}, , derive, NA, KiBps, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 11, controller1_KiBpIO, number, controller1, ${content:disk_index}, , derive, NA, KiBpIO, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 12, controller1_Fwd_iops, number, controller1, ${content:disk_index}, , derive, NA, Fwd_iops, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 13, controller1_Fwd_KiBps, number, controller1, ${content:disk_index}, , derive, NA, Fwd_KiBps, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 14, controller1_R_KiBps, number, controller1, ${content:disk_index}, , derive, NA, R_KiBps, controller=0 disk_index=${content:disk_index}, 1)
			FIELD(4, 15, controller1_W_KiBps, number, controller1, ${content:disk_index}, , derive, NA, W_KiBps, controller=0 disk_index=${content:disk_index}, 1)
		</item>
	</entry>
</definition>
