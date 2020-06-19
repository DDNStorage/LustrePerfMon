# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for generating collectd config
"""
# pylint: disable=too-many-lines
import collections
import logging

from pyesmon import lustre

COLLECTD_CONFIG_TEST_FNAME = "collectd.conf.test"
COLLECTD_CONFIG_FINAL_FNAME = "collectd.conf.final"
COLLECTD_INTERVAL_TEST = 1
# ES2 of version ddn18 added support for used inode/space in the future
ES2_HAS_USED_INODE_SPACE_SUPPORT = False
# ES4 will add support for used inode/space in the future
ES4_HAS_USED_INODE_SPACE_SUPPORT = True

XML_FNAME_ES2 = "lustre-ieel-2.5_definition.xml"
XML_FNAME_ES3 = "lustre-ieel-2.7_definition.xml"
XML_FNAME_ES4 = "lustre-es4-2.10.xml"
XML_FNAME_2_12 = "lustre-2.12.xml"
XML_FNAME_ES5_1 = "lustre-b_es5_1.m4"
XML_FNAME_2_13 = "lustre-2.13.xml"
XML_FNAME_IME_1_1 = "ime-1.1.xml"
XML_FNAME_IME_1_2 = "ime-1.2.xml"


def lustre_version_xml_fname(lustre_version):
    """
    Return the XML file of this Lustre version
    """
    if lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_ES2:
        xml_fname = XML_FNAME_ES2
    elif lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_ES3:
        xml_fname = XML_FNAME_ES3
    elif lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_ES4:
        xml_fname = XML_FNAME_ES4
    elif lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_2_7:
        xml_fname = XML_FNAME_ES3
    elif lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_2_10:
        xml_fname = XML_FNAME_ES4
    elif lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_2_12:
        xml_fname = XML_FNAME_2_12
    elif lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_ES5_1:
        xml_fname = XML_FNAME_ES5_1
    elif lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_2_13:
        xml_fname = XML_FNAME_2_13
    else:
        logging.error("unsupported Lustre version of [%s]",
                      lustre_version.lv_name)
        return None
    return xml_fname


def support_zfs(xml_fname):
    """
    Whether this XML file supports zfs
    """
    if (xml_fname == XML_FNAME_ES3 or xml_fname == XML_FNAME_ES4 or
            xml_fname == XML_FNAME_2_12 or xml_fname == XML_FNAME_2_13 or
            xml_fname == XML_FNAME_ES5_1):
        return True
    return False


def support_acctgroup_acctproject(lustre_version):
    """
    Whether this Lustre version supports acctgroup and acctproject
    """
    if lustre_version.lv_name == lustre.LUSTRE_VERSION_NAME_ES2:
        return False
    if lustre_version.lv_name in lustre.LUSTER_VERSION_NAMES:
        return True
    return False


class CollectdConfig(object):
    """
    Each collectd config has an object of this type
    """
    # pylint: disable=too-many-public-methods,too-many-instance-attributes
    def __init__(self, esmon_client, collect_internal, job_id_var):
        self.cc_configs = collections.OrderedDict()
        self.cc_plugins = collections.OrderedDict()
        self.cc_filedatas = collections.OrderedDict()
        self.cc_aggregations = collections.OrderedDict()
        self.cc_post_cache_chain_rules = collections.OrderedDict()
        self.cc_sfas = collections.OrderedDict()
        self.cc_checks = []
        self.cc_job_id_var = job_id_var
        self.cc_configs["Interval"] = collect_internal
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
        self.cc_plugin_uptime()
        self.cc_plugin_users()

    def cc_dump(self, fpath):
        """
        Dump the config to file
        """
        # pylint: disable=too-many-statements
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

            if any(self.cc_sfas):
                config = 'LoadPlugin ssh\n'
                fout.write(config)
                template_prefix = """<Plugin "ssh">
    <Common>
        DefinitionFile "/etc/%s"
        Extra_tags "extrahost=%s"
"""
                template_controller0 = """
        <ServerHost>
            HostName "%s"
            UserName "user"
            UserPassword "user"
            SshTerminator "%sRAID[0]$ "
            IpcDir "/tmp"
            #KnownhostsFile "/root/.ssh/known_hosts"
            #PublicKeyfile "/root/.ssh/id_dsa.pub"
            #PrivateKeyfile "/root/.ssh/id_dsa"
            #SshKeyPassphrase "passphrase"
        </ServerHost>
"""
                template_controller1 = """
        <ServerHost>
            HostName "%s"
            UserName "user"
            UserPassword "user"
            SshTerminator "%sRAID[1]$ "
            IpcDir "/tmp"
            #KnownhostsFile "/root/.ssh/known_hosts"
            #PublicKeyfile "/root/.ssh/id_dsa.pub"
            #PrivateKeyfile "/root/.ssh/id_dsa"
            #SshKeyPassphrase "passphrase"
        </ServerHost>
"""
                template_postfix = """
    </Common>
    <Item>
        Type "vd_c_rates"
    </Item>
    <Item>
        Type "vd_read_latency"
    </Item>
    <Item>
        Type "vd_write_latency"
    </Item>
    <Item>
        Type "vd_read_iosize"
    </Item>
    <Item>
        Type "vd_write_iosize"
    </Item>
    <Item>
        Type "pd_c_rates"
    </Item>
    <Item>
        Type "pd_read_latency"
    </Item>
    <Item>
        Type "pd_write_latency"
    </Item>
    <Item>
        Type "pd_read_iosize"
    </Item>
    <Item>
        Type "pd_write_iosize"
    </Item>
</Plugin>

"""
                for sfa in self.cc_sfas.values():
                    if sfa.esfa_subsystem_name == "":
                        name = ""
                    else:
                        name = sfa.esfa_subsystem_name + " "

                    controller0 = sfa.esfa_index2controller(controller0=True)
                    controller1 = sfa.esfa_index2controller(controller0=False)
                    config = (template_prefix % (sfa.esfa_xml_fname,
                                                 sfa.esfa_name))
                    if controller0 is not None:
                        config = config + (template_controller0 %
                                           (controller0, name))
                    if controller1 is not None:
                        config = config + (template_controller1 %
                                           (controller1, name))
                    config = config + template_postfix
                    fout.write(config)

            if any(self.cc_filedatas):
                config = """LoadPlugin filedata
"""
                fout.write(config)
                for config in self.cc_filedatas.values():
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
        name = "memory.buffered.memory"
        return self.cc_esmon_client.ec_influxdb_measurement_check(name)

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

    def cc_plugin_lustre(self, lustre_version, lustre_oss=False,
                         lustre_mds=False, lustre_client=False,
                         lustre_exp_ost=False, lustre_exp_mdt=False):
        # pylint: disable=too-many-arguments,too-many-branches
        """
        Config the Lustre plugin
        """
        xml_fname = lustre_version_xml_fname(lustre_version)
        if xml_fname is None:
            return -1

        enable_zfs = support_zfs(xml_fname)

        config = """<Plugin "filedata">
    <Common>
        DefinitionFile "/etc/"""
        config += xml_fname + '"'
        config += """
    </Common>
"""
        config += """
    <Item>
        Type "ldlm_canceld_stats_req_waittime"
    </Item>
    <Item>
        Type "ldlm_canceld_stats_req_qdepth"
    </Item>
    <Item>
        Type "ldlm_canceld_stats_req_active"
    </Item>
    <Item>
        Type "ldlm_canceld_stats_req_timeout"
    </Item>
    <Item>
        Type "ldlm_canceld_stats_reqbuf_avail"
    </Item>

    <Item>
        Type "ldlm_cbd_stats_req_waittime"
    </Item>
    <Item>
        Type "ldlm_cbd_stats_req_qdepth"
    </Item>
    <Item>
        Type "ldlm_cbd_stats_req_active"
    </Item>
    <Item>
        Type "ldlm_cbd_stats_req_timeout"
    </Item>
    <Item>
        Type "ldlm_cbd_stats_reqbuf_avail"
    </Item>
"""
        if lustre_oss:
            config += """
    # OST stats
    <Item>
        Type "ost_acctuser"
    </Item>"""
            if enable_zfs:
                config += """
    <Item>
        Type "zfs_ost_acctuser"
    </Item>"""
            if support_acctgroup_acctproject(lustre_version):
                config += """
    <Item>
        Type "ost_acctgroup"
    </Item>
    <Item>
        Type "ost_acctproject"
    </Item>"""
                if enable_zfs:
                    config += """
    <Item>
        Type "zfs_ost_acctgroup"
    </Item>
    <Item>
        Type "zfs_ost_acctproject"
    </Item>
"""
            config += """
    <Item>
        Type "ost_brw_stats_rpc_bulk"
    </Item>
    <Item>
        Type "ost_brw_stats_page_discontiguous_rpc"
    </Item>
    <Item>
        Type "ost_brw_stats_block_discontiguous_rpc"
    </Item>
    <Item>
        Type "ost_brw_stats_fragmented_io"
    </Item>
    <Item>
        Type "ost_brw_stats_io_in_flight"
    </Item>
    <Item>
        Type "ost_brw_stats_io_time"
    </Item>
    <Item>
        Type "ost_brw_stats_io_size"
    </Item>

    <Item>
        Type "ost_stats_write"
    </Item>
    <Item>
        Type "ost_stats_read"
    </Item>
    <Item>
        Type "ost_stats_statfs"
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

    <Item>
        Type "ost_kbytestotal"
    </Item>
    <Item>
        Type "ost_kbytesfree"
    </Item>
    <Item>
        Type "ost_filestotal"
    </Item>
    <Item>
        Type "ost_filesfree"
    </Item>"""
            config += """

    # Items of ost_threads_* are not enabled

    # Items of ost_io_stats_* are not enabled because in order to get meaningful
    # value, need to, for example:
    # ost_io_stats_usec_sum / ost_io_stats_usec_samples

    # Items of ost_io_threads_* are not enabled

    # Item ost_ldlm_stats is not enabled, because min/max/sum/stddev is not so
    # useful for none-rate metrics.

    <Item>
        Type "ost_stats_req_waittime"
    </Item>
    <Item>
        Type "ost_stats_req_qdepth"
    </Item>
    <Item>
        Type "ost_stats_req_active"
    </Item>
    <Item>
        Type "ost_stats_req_timeout"
    </Item>
    <Item>
        Type "ost_stats_reqbuf_avail"
    </Item>

    <Item>
        Type "ost_io_stats_req_waittime"
    </Item>
    <Item>
        Type "ost_io_stats_req_qdepth"
    </Item>
    <Item>
        Type "ost_io_stats_req_active"
    </Item>
    <Item>
        Type "ost_io_stats_req_timeout"
    </Item>
    <Item>
        Type "ost_io_stats_reqbuf_avail"
    </Item>
    <Item>
        Type "ost_io_stats_ost_read"
    </Item>
    <Item>
        Type "ost_io_stats_ost_write"
    </Item>
    <Item>
        Type "ost_io_stats_ost_punch"
    </Item>

    <Item>
        Type "ost_create_stats_req_waittime"
    </Item>
    <Item>
        Type "ost_create_stats_req_qdepth"
    </Item>
    <Item>
        Type "ost_create_stats_req_active"
    </Item>
    <Item>
        Type "ost_create_stats_req_timeout"
    </Item>
    <Item>
        Type "ost_create_stats_reqbuf_avail"
    </Item>

    # Currently do not enable:
    # ost_seq_stats_[req_waittime|req_qdepth|req_active|req_timeout|reqbuf_avail]

    <Item>
        Type "ost_lock_count"
    </Item>
    <Item>
        Type "ost_lock_timeouts"
    </Item>

    # Currently do not enable:
    # ost_recovery_status_[recovery_start|recovery_duration|replayed_requests|
    # last_transno|time_remaining|req_replay_clients|lock_replay_clients|
    # queued_requests|next_transno]
    #
    # Whenever enabling completed_clients or connected_clients, need to enable
    # them both, because when recovery under different status (COMPLETE|RECOVERING),
    # /proc prints the same variables but with different leading words:
    #
    # When status is COMPLETE:
    #
    # completed_clients: $finished_clients/$recoverable_clients
    #
    # When status is RECOVERING:
    #
    # connected_clients: $finished_clients/$recoverable_clients
    #
    # evicted_clients will be printed only during RECOVERING, thus is a good sign
    # to show that recovery is in process.
    #
    <Item>
        Type "ost_recovery_status_completed_clients"
    </Item>
    <Item>
        Type "ost_recovery_status_connected_clients"
    </Item>
    <Item>
        Type "ost_recovery_status_evicted_clients"
    </Item>
"""
            if self.cc_job_id_var == lustre.JOB_ID_PROCNAME_UID:
                config += """
    <ItemType>
        Type "ost_jobstats"
        <ExtendedParse>
            # Parse the field job_id
            Field "job_id"
            # Match the pattern
            Pattern "(.+)[.]([[:digit:]]+)"
            <ExtendedField>
                Index 1
                Name procname
            </ExtendedField>
            <ExtendedField>
                Index 2
                Name uid
            </ExtendedField>
        </ExtendedParse>
        TsdbTags "procname=${extendfield:procname} uid=${extendfield:uid}"
    </ItemType>
"""
        if lustre_exp_ost:
            config += """
    <Item>
        Type "exp_ost_stats_read"
    </Item>
    <Item>
        Type "exp_ost_stats_write"
    </Item>
    # The other exp_ost_stats_* items are not enabled here
"""
        if lustre_client:
            config += """
    # Client stats
    <Item>
        Type "client_stats_read"
    </Item>
    <Item>
        Type "client_stats_write"
    </Item>
    <Item>
        Type "client_stats_read_bytes"
    </Item>
    <Item>
        Type "client_stats_write_bytes"
    </Item>
    <Item>
        Type "client_stats_ioctl"
    </Item>
    <Item>
        Type "client_stats_open"
    </Item>
    <Item>
        Type "client_stats_close"
    </Item>
    <Item>
        Type "client_stats_mmap"
    </Item>
    <Item>
        Type "client_stats_page_fault"
    </Item>
    <Item>
        Type "client_stats_page_mkwrite"
    </Item>
    <Item>
        Type "client_stats_seek"
    </Item>
    <Item>
        Type "client_stats_fsync"
    </Item>
    <Item>
        Type "client_stats_readdir"
    </Item>
    <Item>
        Type "client_stats_setattr"
    </Item>
    <Item>
        Type "client_stats_truncate"
    </Item>
    <Item>
        Type "client_stats_flock"
    </Item>
    <Item>
        Type "client_stats_getattr"
    </Item>
    <Item>
        Type "client_stats_fallocate"
    </Item>
    <Item>
        Type "client_stats_create"
    </Item>
    <Item>
        Type "client_stats_open"
    </Item>
    <Item>
        Type "client_stats_link"
    </Item>
    <Item>
        Type "client_stats_unlink"
    </Item>
    <Item>
        Type "client_stats_symlink"
    </Item>
    <Item>
        Type "client_stats_mkdir"
    </Item>
    <Item>
        Type "client_stats_rmdir"
    </Item>
    <Item>
        Type "client_stats_mknod"
    </Item>
    <Item>
        Type "client_stats_rename"
    </Item>
    <Item>
        Type "client_stats_statfs"
    </Item>
    <Item>
        Type "client_stats_setxattr"
    </Item>
    <Item>
        Type "client_stats_getxattr"
    </Item>
    <Item>
        Type "client_stats_getxattr_hits"
    </Item>
    <Item>
        Type "client_stats_listxattr"
    </Item>
    <Item>
        Type "client_stats_removexattr"
    </Item>
    <Item>
        Type "client_stats_inode_permission"
    </Item>
"""
        if lustre_mds:
            config += """
    # MDT stats
    <Item>
        Type "mdt_acctuser"
    </Item>"""
            if enable_zfs:
                config += """
    <Item>
        Type "zfs_mdt_acctuser"
    </Item>"""
            if support_acctgroup_acctproject(lustre_version):
                config += """
    <Item>
        Type "mdt_acctgroup"
    </Item>
    <Item>
        Type "mdt_acctproject"
    </Item>"""
                if enable_zfs:
                    config += """
    <Item>
        Type "zfs_mdt_acctgroup"
    </Item>
    <Item>
        Type "zfs_mdt_acctproject"
    </Item>"""
            config += """
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

    <Item>
        Type "mdt_filestotal"
    </Item>
    <Item>
        Type "mdt_filesfree"
    </Item>"""

            if self.cc_job_id_var == lustre.JOB_ID_PROCNAME_UID:
                config += """
    <ItemType>
        Type "mdt_jobstats"
        <ExtendedParse>
            # Parse the field job_id
            Field "job_id"
            # Match the pattern
            Pattern "(.+)[.]([[:digit:]]+)"
            <ExtendedField>
                Index 1
                Name procname
            </ExtendedField>
            <ExtendedField>
                Index 2
                Name uid
            </ExtendedField>
        </ExtendedParse>
        TsdbTags "procname=${extendfield:procname} uid=${extendfield:uid}"
    </ItemType>
"""

        config += """
    <Item>
        Type "mdt_stats_req_waittime"
    </Item>
    <Item>
        Type "mdt_stats_req_qdepth"
    </Item>
    <Item>
        Type "mdt_stats_req_active"
    </Item>
    <Item>
        Type "mdt_stats_req_timeout"
    </Item>
    <Item>
        Type "mdt_stats_reqbuf_avail"
    </Item>
    <Item>
        Type "mdt_stats_ldlm_ibits_enqueue"
    </Item>
    <Item>
        Type "mdt_stats_mds_getattr"
    </Item>
    <Item>
        Type "mdt_stats_mds_connect"
    </Item>
    <Item>
        Type "mdt_stats_mds_get_root"
    </Item>
    <Item>
        Type "mdt_stats_mds_statfs"
    </Item>
    <Item>
        Type "mdt_stats_mds_getxattr"
    </Item>
    <Item>
        Type "mdt_stats_obd_ping"
    </Item>

    <Item>
        Type "mdt_readpage_stats_req_waittime"
    </Item>
    <Item>
        Type "mdt_readpage_stats_req_qdepth"
    </Item>
    <Item>
        Type "mdt_readpage_stats_req_active"
    </Item>
    <Item>
        Type "mdt_readpage_stats_req_timeout"
    </Item>
    <Item>
        Type "mdt_readpage_stats_reqbuf_avail"
    </Item>
    <Item>
        Type "mdt_readpage_stats_mds_close"
    </Item>
    <Item>
        Type "mdt_readpage_stats_mds_readpage"
    </Item>

    # Currently do not enable:
    # mdt_setattr_stats_[req_waittime|req_qdepth|req_active|req_timeout|
    # reqbuf_avail], because Lustre doesn't use it yet.

    <Item>
        Type "mdt_lock_count"
    </Item>
    <Item>
        Type "mdt_lock_timeouts"
    </Item>

    # Currently do not enable:
    # mdt_recovery_status_[recovery_start|recovery_duration|replayed_requests|
    # last_transno|time_remaining|req_replay_clients|lock_replay_clients|
    # queued_requests|next_transno]
    #
    # Whenever enabling completed_clients or connected_clients, need to enable
    # them both, because when recovery under different status (COMPLETE|RECOVERING),
    # /proc prints the same variables but with different leading words:
    #
    # When status is COMPLETE:
    #
    # completed_clients: $finished_clients/$recoverable_clients
    #
    # When status is RECOVERING:
    #
    # connected_clients: $finished_clients/$recoverable_clients
    #
    # evicted_clients will be printed only during RECOVERING, thus is a good sign
    # to show that recovery is in process.
    #
    <Item>
        Type "mdt_recovery_status_completed_clients"
    </Item>
    <Item>
        Type "mdt_recovery_status_connected_clients"
    </Item>
    <Item>
        Type "mdt_recovery_status_evicted_clients"
    </Item>
"""

        if lustre_exp_mdt:
            config += """
    <Item>
        Type "exp_md_stats_open"
    </Item>
    <Item>
        Type "exp_md_stats_close"
    </Item>
    <Item>
        Type "exp_md_stats_mknod"
    </Item>
    <Item>
        Type "exp_md_stats_link"
    </Item>
    <Item>
        Type "exp_md_stats_unlink"
    </Item>
    <Item>
        Type "exp_md_stats_mkdir"
    </Item>
    <Item>
        Type "exp_md_stats_rmdir"
    </Item>
    <Item>
        Type "exp_md_stats_rename"
    </Item>
    <Item>
        Type "exp_md_stats_getattr"
    </Item>
    <Item>
        Type "exp_md_stats_setattr"
    </Item>
    <Item>
        Type "exp_md_stats_getxattr"
    </Item>
    <Item>
        Type "exp_md_stats_setxattr"
    </Item>
    <Item>
        Type "exp_md_stats_statfs"
    </Item>
    <Item>
        Type "exp_md_stats_sync"
    </Item>
"""

        # Client support, e.g. max_rpcs_in_flight of mdc could be added
        config += "</Plugin>\n\n"
        self.cc_filedatas["lustre"] = config
        client = self.cc_esmon_client
        rpm_name = "collectd-filedata"
        if rpm_name not in client.ec_needed_collectd_rpms:
            client.ec_needed_collectd_rpms.append(rpm_name)
        return 0

    def cc_plugin_ime(self, ime_version):
        """
        Config the IME plugin
        """
        ime_config_file = "ime-%s.xml" % ime_version
        if ime_config_file != XML_FNAME_IME_1_1 and ime_config_file != XML_FNAME_IME_1_2:
            logging.error("unsupported IME version [%s]",
                          ime_version)
            return -1

        self.cc_plugins["ime"] = ("""<Plugin "ime">
    <Common>
        DefinitionFile "/etc/%s"
    </Common>
    <Item>
        Type "nvm-stat"
    </Item>
    <Item>
        Type "bfs-stat"
    </Item>
    <Item>
        Type "UM-stat"
    </Item>
</Plugin>

""" % (ime_config_file))
        client = self.cc_esmon_client
        rpm_name = "collectd-ime"
        if rpm_name not in client.ec_needed_collectd_rpms:
            client.ec_needed_collectd_rpms.append(rpm_name)
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
        host = client.ec_host
        measurement = "aggregation.sensors-max.temperature"

        command = "sensors | grep temp"
        retval = host.sh_run(command)
        if retval.cr_exit_status:
            logging.debug("failed to run command [%s] on host [%s], there "
                          "might be no sensor, skip checking measurement "
                          "[%s]",
                          command,
                          host.sh_hostname,
                          measurement)
            return 0
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

        client = self.cc_esmon_client
        rpm_name = "collectd-sensors"
        if rpm_name not in client.ec_needed_collectd_rpms:
            client.ec_needed_collectd_rpms.append(rpm_name)
        return 0

    def cc_plugin_disk(self):
        """
        Config the disk plugin
        """
        self.cc_plugins["disk"] = ""

        client = self.cc_esmon_client
        rpm_name = "collectd-disk"
        if rpm_name not in client.ec_needed_collectd_rpms:
            client.ec_needed_collectd_rpms.append(rpm_name)
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

    def cc_plugin_sfa_check(self):
        """
        Check the SFA plugin
        """
        client = self.cc_esmon_client
        measurement = "vd_rate"

        for sfa in self.cc_sfas.values():
            fqdn = sfa.esfa_name

            ret = client.ec_influxdb_measurement_check(measurement, fqdn=fqdn)
            if ret:
                return ret
        return 0

    def cc_plugin_sfa(self, sfa):
        """
        Add SFA configuration
        """
        name = sfa.esfa_name
        self.cc_sfas[name] = sfa
        if self.cc_plugin_sfa_check not in self.cc_checks:
            self.cc_checks.append(self.cc_plugin_sfa_check)

        rpm_name = "collectd-ssh"
        client = self.cc_esmon_client
        if rpm_name not in client.ec_needed_collectd_rpms:
            client.ec_needed_collectd_rpms.append(rpm_name)
        return 0

    def cc_plugin_infiniband(self):
        """
        Add IB configuration
        """
        config = """<Plugin "filedata">
    <Common>
        DefinitionFile "/etc/infiniband-0.1_definition.xml"
    </Common>
    <Item>
        Type "excessive_buffer_overrun_errors"
    </Item>
    <Item>
        Type "link_downed"
    </Item>
    <Item>
        Type "link_error_recovery"
    </Item>
    <Item>
        Type "local_link_integrity_errors"
    </Item>
    <Item>
        Type "port_rcv_constraint_errors"
    </Item>
    <Item>
        Type "port_rcv_data"
    </Item>
    <Item>
        Type "port_rcv_errors"
    </Item>
    <Item>
        Type "port_rcv_packets"
    </Item>
    <Item>
        Type "port_rcv_remote_physical_errors"
    </Item>
    <Item>
        Type "port_xmit_constraint_errors"
    </Item>
    <Item>
        Type "port_xmit_data"
    </Item>
    <Item>
        Type "port_xmit_discards"
    </Item>
    <Item>
        Type "port_xmit_packets"
    </Item>
    <Item>
        Type "symbol_error"
    </Item>
    <Item>
        Type "VL15_dropped"
    </Item>
    <Item>
        Type "port_rcv_switch_relay_errors"
    </Item>
</Plugin>

"""
        self.cc_filedatas["infiniband"] = config
        client = self.cc_esmon_client
        rpm_name = "collectd-filedata"
        if rpm_name not in client.ec_needed_collectd_rpms:
            client.ec_needed_collectd_rpms.append(rpm_name)
