# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for generating collectd config
"""
import collections

COLLECTD_CONFIG_TEMPLATE_FNAME = "collectd.conf.template"
COLLECTD_CONFIG_TEST_FNAME = "collectd.conf.test"
COLLECTD_CONFIG_FINAL_FNAME = "collectd.conf.final"
COLLECTD_INTERVAL_TEST = 1
COLLECTD_INTERVAL_FINAL = 60

class CollectdConfig(object):
    """
    Each collectd config has an object of this type
    """
    def __init__(self, esmon_client):
        self.cc_configs = collections.OrderedDict()
        self.cc_plugins = collections.OrderedDict()
        self.cc_aggregations = collections.OrderedDict()
        self.cc_post_cache_chain_rules = collections.OrderedDict()
        self.cc_checks = []
        self.cc_configs["Interval"] = COLLECTD_INTERVAL_FINAL
        self.cc_configs["WriteQueueLimitHigh"] = 1000000
        self.cc_configs["WriteQueueLimitLow"] = 800000
        self.cc_plugin_syslog("err")
        self.cc_plugin_memory()
        self.cc_plugin_cpu()
        self.cc_esmon_client = esmon_client
        self.cc_plugin_write_tsdb()
        self.cc_plugin_df()
        self.cc_plugin_load()
        self.cc_plugin_sensors()
        self.cc_plugin_disk()
        self.cc_plugin_uptime()
        self.cc_plugin_users()

    def cc_dump(self, fpath):
        """
        Dump the config to file
        """
        with open(fpath, "wt") as fout:
            fout.write("# Collectd config file generated automatcially by "
                       "ESMON\n# Please contact DDN Storage for information "
                       "and support\n\n")
            for config_name, config in self.cc_configs.iteritems():
                text = '%s %s\n' % (config_name, config)
                fout.write(text)
            fout.write("\n")

            if any(self.cc_aggregations):
                config = """LoadPlugin aggregation
<Plugin "aggregation">
"""
                fout.write(config)
                for config in self.cc_aggregations.values():
                    fout.write(config)
                config = """
</Plugin>

"""
                fout.write(config)

            if any(self.cc_post_cache_chain_rules):
                config = """LoadPlugin match_regex
PostCacheChain "PostCache"
# Don't send "cpu-X" stats
<Chain "PostCache">
"""
                fout.write(config)
                for config in self.cc_post_cache_chain_rules.values():
                    fout.write(config)
                config = """
    Target "write"
</Chain>

"""
                fout.write(config)

            for plugin_name, plugin_config in self.cc_plugins.iteritems():
                text = 'LoadPlugin %s\n' % plugin_name
                text += plugin_config + '\n'
                fout.write(text)

    def cc_check(self):
        """
        Check the config to file
        """
        for check in self.cc_checks:
            ret = check()
            if ret:
                return ret
        return 0

    def cc_plugin_syslog(self, log_level):
        """
        Config the syslog plugin
        """
        if log_level != "err" and log_level != "info" and log_level != "debug":
            return -1
        config = ('<Plugin "syslog">\n'
                  '    LogLevel %s\n'
                  '</Plugin>\n' % log_level)
        self.cc_plugins["syslog"] = config
        return 0

    def cc_plugin_memory_check(self):
        """
        Check the memory plugin
        """
        return self.cc_esmon_client.ec_influxdb_measurement_check("memory.buffered.memory")

    def cc_plugin_memory(self):
        """
        Config the memory plugin
        """
        self.cc_plugins["memory"] = ""
        if self.cc_plugin_memory_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_memory_check)
        return 0

    def cc_plugin_write_tsdb(self):
        """
        Config the write TSDB plugin
        """
        host = self.cc_esmon_client.ec_esmon_server.es_host.sh_hostname
        config = ('<Plugin "write_tsdb">\n'
                  '    <Node>\n'
                  '        Host "%s"\n'
                  '        Port "4242"\n'
                  '        DeriveRate true\n'
                  '    </Node>\n'
                  '</Plugin>\n' % host)
        self.cc_plugins["write_tsdb"] = config
        return 0

    def cc_plugin_cpu_check(self):
        """
        Check the CPU plugin
        """
        client = self.cc_esmon_client
        measurement = "aggregation.cpu-average.cpu.system"
        return client.ec_influxdb_measurement_check(measurement)

    def cc_plugin_cpu(self):
        """
        Config the cpu plugin
        """
        self.cc_aggregations["cpu"] = """    <Aggregation>
        Plugin "cpu"
        Type "cpu"
        GroupBy "Host"
        GroupBy "TypeInstance"
        CalculateAverage true
    </Aggregation>
"""
        self.cc_post_cache_chain_rules["cpu"] = """    <Rule>
        <Match regex>
            Plugin "^cpu$"
            PluginInstance "^[0-9]+$"
        </Match>
        <Target write>
            Plugin "aggregation"
        </Target>
        Target stop
    </Rule>
"""
        self.cc_plugins["cpu"] = ""
        if self.cc_plugin_cpu_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_cpu_check)
        return 0

    def cc_plugin_lustre(self, lustre_oss=False, lustre_mds=False):
        """
        Config the Lustre plugin
        """
        config = """<Plugin "filedata">
    <Common>
        DefinitionFile "/etc/lustre-ieel-2.7_definition.xml"
    </Common>
"""
        if lustre_oss:
            config += """
    # OST stats
    <Item>
        Type "ost_acctuser"
        Query_interval 10
    </Item>
    <Item>
        Type "ost_kbytestotal"
        Query_interval 10
    </Item>
    <Item>
        Type "ost_kbytesfree"
        Query_interval 10
    </Item>
    <Item>
        Type "ost_kbytesused"
        Query_interval 10
    </Item>
    <Item>
        Type "ost_filesused"
        Query_interval 10
    </Item>
    <Item>
        Type "ost_stats_write"
    </Item>
    <Item>
        Type "ost_stats_read"
    </Item>
    <Item>
        Type "ost_brw_stats_rpc_bulk"
    </Item>
    <Item>
        Type "ost_jobstats"
#        <Rule>
#            Field "job_id"
#            Match "[[:digit:]]+"
#        </Rule>
    </Item>
#   <ItemType>
#       Type "ost_jobstats"
#       <ExtendedParse>
#           # Parse the field job_id
#           Field "job_id"
#           # Match the pattern
#           Pattern "u([[:digit:]]+)[.]g([[:digit:]]+)[.]j([[:digit:]]+)"
#           <ExtendedField>
#               Index 1
#               Name slurm_job_uid
#           </ExtendedField>
#           <ExtendedField>
#               Index 2
#               Name slurm_job_gid
#           </ExtendedField>
#           <ExtendedField>
#               Index 3
#               Name slurm_job_id
#           </ExtendedField>
#       </ExtendedParse>
#       TsdbTags "slurm_job_uid=${extendfield:slurm_job_uid} slurm_job_gid=${extendfield:slurm_job_gid} slurm_job_id=${extendfield:slurm_job_id}"
#   </ItemType>
"""
        if lustre_mds:
            config += """
    # MDT stats
    <Item>
        Type "mdt_acctuser"
        Query_interval 10
    </Item>
    <Item>
        Type "mdt_filestotal"
        Query_interval 10
    </Item>
    <Item>
        Type "mdt_filesfree"
        Query_interval 10
    </Item>
    <Item>
        Type "mdt_filesused"
        Query_interval 10
    </Item>
    <Item>
        Type "md_stats_open"
    </Item>
    <Item>
        Type "md_stats_close"
    </Item>
    <Item>
        Type "md_stats_mknod"
    </Item>
    <Item>
        Type "md_stats_unlink"
    </Item>
    <Item>
        Type "md_stats_mkdir"
    </Item>
    <Item>
        Type "md_stats_rmdir"
    </Item>
    <Item>
        Type "md_stats_rename"
    </Item>
    <Item>
        Type "md_stats_getattr"
    </Item>
    <Item>
        Type "md_stats_setattr"
    </Item>
    <Item>
        Type "md_stats_getxattr"
    </Item>
    <Item>
        Type "md_stats_setxattr"
    </Item>
    <Item>
        Type "md_stats_statfs"
    </Item>
    <Item>
        Type "md_stats_sync"
    </Item>
    <Item>
        Type "mdt_jobstats"
#       <Rule>
#           Field "job_id"
#           Match "[[:digit:]]+"
#       </Rule>
    </Item>
#   <ItemType>
#       Type "mdt_jobstats"
#       <ExtendedParse>
#           # Parse the field job_id
#           Field "job_id"
#           # Match the pattern
#           Pattern "u([[:digit:]]+)[.]g([[:digit:]]+)[.]j([[:digit:]]+)"
#           <ExtendedField>
#               Index 1
#               Name slurm_job_uid
#           </ExtendedField>
#           <ExtendedField>
#               Index 2
#               Name slurm_job_gid
#           </ExtendedField>
#           <ExtendedField>
#               Index 3
#               Name slurm_job_id
#           </ExtendedField>
#       </ExtendedParse>
#       TsdbTags "slurm_job_uid=${extendfield:slurm_job_uid} slurm_job_gid=${extendfield:slurm_job_gid} slurm_job_id=${extendfield:slurm_job_id}"
#   </ItemType>
"""
        config += "</Plugin>\n\n"
        self.cc_plugins["filedata"] = config
        return 0

    def cc_plugin_ime(self):
        """
        Config the IME plugin
        """
        self.cc_plugins["ime"] = """<Plugin "ime">
    <Common>
        DefinitionFile "/etc/ime-0.1_definition.xml"
    </Common>
    <Item>
        Type "nvm-stat"
    </Item>
    <Item>
        Type "bfs-stat"
    </Item>
</Plugin>

"""
        return 0

    def cc_plugin_df_check(self):
        """
        Check the df plugin
        """
        client = self.cc_esmon_client
        measurement = "df.root.df_complex.free"
        return client.ec_influxdb_measurement_check(measurement)

    def cc_plugin_df(self):
        """
        Config the df plugin on /
        """
        self.cc_plugins["df"] = """<Plugin "df">
    MountPoint "/"
</Plugin>

"""
        if self.cc_plugin_df_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_df_check)
        return 0

    def cc_plugin_load_check(self):
        """
        Check the load plugin
        """
        client = self.cc_esmon_client
        measurement = "load.load.shortterm"
        return client.ec_influxdb_measurement_check(measurement)

    def cc_plugin_load(self):
        """
        Config the load plugin
        """
        self.cc_plugins["load"] = ""
        if self.cc_plugin_load_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_load_check)
        return 0

    def cc_plugin_sensors_check(self):
        """
        Check the sensors plugin
        """
        client = self.cc_esmon_client
        measurement = "aggregation.sensors-max.temperature"
        return client.ec_influxdb_measurement_check(measurement)

    def cc_plugin_sensors(self):
        """
        Config the sensors plugin
        """
        self.cc_aggregations["sensors"] = """    <Aggregation>
        Plugin "sensors"
        Type "temperature"
        GroupBy "Host"
        CalculateMaximum true
    </Aggregation>
"""
        self.cc_post_cache_chain_rules["sensors"] = """    <Rule>
        <Match regex>
            Plugin "^sensors$"
            Type "^temperature$"
        </Match>
        <Target write>
            Plugin "aggregation"
        </Target>
    </Rule>
"""
        self.cc_plugins["sensors"] = ""
        if self.cc_plugin_sensors_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_sensors_check)
        return 0

    def cc_plugin_disk(self):
        """
        Config the disk plugin
        """
        self.cc_plugins["disk"] = ""
        return 0

    def cc_plugin_uptime_check(self):
        """
        Check the uptime plugin
        """
        client = self.cc_esmon_client
        measurement = "uptime.uptime"
        return client.ec_influxdb_measurement_check(measurement)

    def cc_plugin_uptime(self):
        """
        Config the uptime plugin
        """
        self.cc_plugins["uptime"] = ""
        if self.cc_plugin_uptime_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_uptime_check)
        return 0

    def cc_plugin_users_check(self):
        """
        Check the users plugin
        """
        client = self.cc_esmon_client
        measurement = "users.users"
        return client.ec_influxdb_measurement_check(measurement)

    def cc_plugin_users(self):
        """
        Config the users plugin
        """
        self.cc_plugins["users"] = ""
        if self.cc_plugin_users_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_users_check)
        return 0
