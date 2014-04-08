include(`lustre_xml.m4')dnl
<definition>
	<version>1.8.9</version>
	<entry>
		<subpath>
			<subpath_type>constant</subpath_type>
			<path>/proc/fs/lustre</path>
		</subpath>
		<mode>directory</mode>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>health_check</path>
			</subpath>
			<mode>file</mode>
			<item>
				<name>health</name>
				<pattern>(.+)</pattern>
				FIELD(4, 1, health, string, NA, NA, NA, NA, NA, 1)
			</item>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>version</path>
			</subpath>
			<mode>file</mode>
			<item>
				<name>lustre_version</name>
				<pattern>lustre: ([[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+)</pattern>
				FIELD(4, 1, version, string, NA, NA, NA, NA, NA, 1)
			</item>
			<item>
				<name>kernel_type</name>
				<pattern>kernel: (patchless_client)</pattern>
				FIELD(4, 1, kernel_type, string, NA, NA, NA, NA, NA, 1)
			</item>
			<item>
				<name>build_version</name>
				<pattern>build:  (.+)</pattern>
				FIELD(4, 1, build_version, string, NA, NA, NA, NA, NA, 1)
			</item>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>mds</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+-MDT[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>mdt_name</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					<!-- mds_stats_counter_init() -->
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>stats</path>
					</subpath>
					<mode>file</mode>
					MD_STATS_ITEM(5, open, 1)
					MD_STATS_ITEM(5, close, 1)
					MD_STATS_ITEM(5, mknod, 1)
					MD_STATS_ITEM(5, link, 1)
					MD_STATS_ITEM(5, unlink, 1)
					MD_STATS_ITEM(5, mkdir, 1)
					MD_STATS_ITEM(5, rmdir, 1)
					MD_STATS_ITEM(5, rename, 1)
					MD_STATS_ITEM(5, getattr, 1)
					MD_STATS_ITEM(5, setattr, 1)
					MD_STATS_ITEM(5, getxattr, 1)
					MD_STATS_ITEM(5, setxattr, 1)
					MD_STATS_ITEM(5, statfs, 1)
					MD_STATS_ITEM(5, sync, 1)
				</entry>
			</entry>
		</entry>
		<entry>
			<subpath>
				<subpath_type>constant</subpath_type>
				<path>obdfilter</path>
			</subpath>
			<mode>directory</mode>
			<entry>
				<subpath>
					<subpath_type>regular_expression</subpath_type>
					<path>(^.+-OST[0-9a-fA-F]+$)</path>
					<subpath_field>
						<index>1</index>
						<name>ost_name</name>
					</subpath_field>
				</subpath>
				<mode>directory</mode>
				<entry>
					<!-- filter_setup().
					     There are a lot of counter, only defined part of them here
					-->
					<subpath>
						<subpath_type>constant</subpath_type>
						<path>stats</path>
					</subpath>
					<mode>file</mode>
					<item>
						<name>ost_stats_read</name>
						<pattern>read_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)</pattern>
						<field>
							<index>1</index>
							<name>read_samples</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>read_samples</string>
							</option>
						</field>
						<field>
							<index>2</index>
							<name>read_bytes</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>read_bytes</string>
							</option>
						</field>
					</item>
					<item>
						<name>ost_stats_write</name>
						<pattern>write_bytes +([[:digit:]]+) samples \[bytes\] [[:digit:]]+ [[:digit:]]+ ([[:digit:]]+)</pattern>
						<field>
							<index>1</index>
							<name>write_samples</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>write_samples</string>
							</option>
						</field>
						<field>
							<index>2</index>
							<name>write_bytes</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>write_bytes</string>
							</option>
						</field>
					</item>
					<item>
						<name>ost_stats_get_page</name>
						<pattern>get_page +([[:digit:]]+) samples \[usec\]</pattern>
						<field>
							<index>1</index>
							<name>get_page</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>get_page</string>
							</option>
						</field>
					</item>
					<item>
						<name>ost_stats_get_page_failures</name>
						<pattern>get_page failures +([[:digit:]]+) samples \[num\]</pattern>
						<field>
							<index>1</index>
							<name>get_page_failures</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>get_page_failures</string>
							</option>
						</field>
					</item>
					<item>
						<name>ost_stats_cache_access</name>
						<pattern>cache_access +([[:digit:]]+) samples \[pages\]</pattern>
						<field>
							<index>1</index>
							<name>cache_access</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>cache_access</string>
							</option>
						</field>
					</item>
					<item>
						<name>ost_stats_cache_hit</name>
						<pattern>cache_hit +([[:digit:]]+) samples \[pages\]</pattern>
						<field>
							<index>1</index>
							<name>cache_hit</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>cache_hit</string>
							</option>
						</field>
					</item>
					<item>
						<name>ost_stats_cache_miss</name>
						<pattern>cache_miss +([[:digit:]]+) samples \[pages\]</pattern>
						<field>
							<index>1</index>
							<name>cache_miss</name>
							<type>number</type>
							<option>
								<name>host</name>
								<string>${subpath:ost_name}</string>
							</option>
							<option>
								<name>plugin</name>
								<string>stats</string>
							</option>
							<option>
								<name>plugin_instance</name>
								<string></string>
							</option>
							<option>
								<name>type</name>
								<string>derive</string>
							</option>
							<option>
								<name>type_instance</name>
								<string>cache_miss</string>
							</option>
						</field>
					</item>
					<!-- Following comes from filter_setup()/lprocfs_alloc_obd_stats()/lprocfs_init_ops_stats()
					     Not necessarily available.
					-->
					OST_STATS_ITEM(5, getattr, 1)
					OST_STATS_ITEM(5, setattr, 1)
					OST_STATS_ITEM(5, punch, 1)
					OST_STATS_ITEM(5, sync, 1)
					OST_STATS_ITEM(5, destroy, 1)
					OST_STATS_ITEM(5, create, 1)
					OST_STATS_ITEM(5, statfs, 1)
					OST_STATS_ITEM(5, get_info, 1)
					OST_STATS_ITEM(5, set_info_async, 1)
					OST_STATS_ITEM(5, quotactl, 1)
				</entry>
			</entry>
		</entry>
	</entry>
</definition>

