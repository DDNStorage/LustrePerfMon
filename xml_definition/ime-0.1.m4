include(`general.m4')dnl
HEAD(IME-3.5)
<definition>
	<version>3.5</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>--nvm-stat</path>
		</subpath>
		<mode>file</mode>
		<item>
			<name>nvm-stat</name>
			<pattern>\| +([[:digit:]]+) +\| +(\S+) +\| +([[:digit:]]+) +\| +([[:digit:]]+)\.[[:digit:]]+ +\| +([[:digit:]]+) +\| +([[:digit:]]+)\.[[:digit:]]+ +\| +([[:digit:]]+) +\| +([[:digit:]]+)\.[[:digit:]]+ +\|.+\|</pattern>
			FIELD(4, 1, ID, string, , , , derive, , NA, NA, 1)
			FIELD(4, 2, name, string, , , , derive, , NA, NA, 1)
			FIELD(4, 3, read_IOs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, derive, read_IOs, ime_nvm_IOs, host=${key:hostname} rw=read device=${content:ID}, 1)
			FIELD(4, 4, read_MBs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, derive, read_MBs, ime_nvm_MBs, host=${key:hostname} rw=read device=${content:ID}, 1)
			FIELD(4, 5, write_IOs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, derive, write_IOs, ime_nvm_IOs, host=${key:hostname} rw=write device=${content:ID}, 1)
			FIELD(4, 6, write_MBs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, derive, write_MBs, ime_nvm_MBs, host=${key:hostname} rw=write device=${content:ID}, 1)
			FIELD(4, 7, unmap_IOs, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, derive, unmap_IOs, ime_nvm_IOs, host=${key:hostname} rw=unmap device=${content:ID}, 1)
			FIELD(4, 8, free, number, ime_${key:hostname}, nvm-stat, device_${content:ID}, derive, free, ime_nvm_free, host=${key:hostname} device=${content:ID}, 1)
		</item>
	</entry>
</definition>

