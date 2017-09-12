# DDN Exascaler Monitoring System Manual

## Definitions

+ **ESMON**: Abbreviation for *DDN Exascaler Monitoring System*.
+ **DDN Exascaler**: *DDN Exascaler* is software stack developed by *DDN* to overcome the toughest storage and data management challenges in extreme, data-intensive environments.
+ **Installation Server**: The server on which the installation process is triggered.

- **Monitoring Server**: The server on which the database (*Influxdb*) and web server (*Grafana*) of the monitoring system will run.
- **Monitoring Client(s):**  The servers from which the monitor system will collect metrics from. The metrics includes information about CPU, memory, Lustre, SFA storage, etc. A *Collectd* daemon will run on each monitoring client.
- **DDN IME**: *DDN’s Infinite Memory Engine (IME)* is a flash-native, software-defined, storage cache that streamlines application IO, eliminating system bottlenecks.
- **Lustre**: The *Lustre* file system is an open-source, parallel file system that supports many requirements of leadership class HPC simulation environments.

## Requirements

###Installation Server

- OS distribution: CenOS7/RHEL7
- Free disk space: > 500 MB. The *installation server* will save all installation logs to */var/log/esmon_install* directory, which requires some free disk space.
- Network:  The *installation server* be able to start SSH connections to the *monitoring server* and *monitoring clients* without  password prompt
- *ESMON* ISO image :  The *installation server* should posses the *ESMON* ISO image.

###Monitoring Server

- OS distribution: CenOS7/RHEL7
- Free disk space:  > 5G. *Influxdb* will be running on this server. More disk space is required to keep more data into *Influxdb* 
- Network: SSHD should be running on the *monitoring server* and it should be able to be connected by *installation server* without prompting for password.

###Monitoring Client

- OS distribution: CenOS7/RHEL7 or CentOS6/RHEL6
- Free disk space:  > 200M. The *installation server* will save necessary RPMs in directory */var/log/esmon_install*, which requires some free disk space.
- Network: SSHD should be running on the *monitoring client* and it should be able to be connected by *installation server* without prompting for password.

## Installation

###1. Prepare the *Installation Server*

1. Grab the *ESMON* ISO image file to the *installation server*, e.g. /ISOs/esmon.iso.

2.    Mount the *ESMON* ISO image:

      ```shell
      # mount -o loop /ISOs/esmon.iso /media
      ```


3.    Start the install script:

      ```shell
      # cd /media && sh ./installesmon.sh
      Updating / installing...
      esmon-0.1.g16e2e3c-7.el7              ########################################
      ******************************************************************************
      *              ESMON package has been installed                              *
      *Please set your servers' information into /etc/esmon_install.conf           *
      *And please make sure you can access all these server by ssh with keyfile    *
      *Then please run /usr/bin/esmon_install to continue                          *
      ******************************************************************************
      ```

### 2. Edit the Configuration File

The configuration file */etc/esmon_install.conf* includes all the necessary information for installation. Following is an example:

```yaml
iso_path: /work/ISOs/esmon.iso             # ISO path to ESMON
ssh_hosts:                                 # Array of hosts
  - host_id: Monitoring-Server             # ID of this SSH host
    hostname: Monitoring-Server            # The host name
    ssh_identity_file: /root/.ssh/id_rsa   # The SSH key to connect to the host
  - host_id: Monitoring-Client1
    hostname: Monitoring-Client1
    ssh_identity_file: /root/.ssh/id_rsa
  - host_id: Monitoring-Client2
    hostname: Monitoring-Client2
    ssh_identity_file: /root/.ssh/id_rsa
client_hosts:                              # Array of client hosts of ESMON
  - host_id: Monitoring-Client1            # Host ID
    lustre_oss: true                       # Whether enable Lustre OSS monitoring
    lustre_mds: true                       # Whether enable Lustre MDS monitoring
    ime: false                             # Whether enable IME monitoring
  - host_id: Monitoring-Client2
    lustre_oss: false
    lustre_mds: true
    ime: false 
server_host:
    host_id: Monitoring-Server # Server host ID of ESMON
    drop_database: true        # Whether to drop existing ESMON database in Influxdb
    erase_influxdb: true       # Whether to erase all data/metadata of Influxdb
```

**iso_path** is the path where *ESMON* ISO image is saved

**ssh_hosts** includes the information of how to login to the hosts using SSH connections. **host_id** is the unique ID of the host. Two hosts shouldn't share a same **host_id**. **hostname** is the host name to use when connecting to the host using SSH. **host_id** and **hostname** could be different for a host, because there could multiple ways to connect to the same host. **ssh_identity_file** is the SSH key file used when connecting to the host. **ssh_identity_file** could be omitted if the default SSH identity file works. All the monitoring server* and *monitoring client*s should be included in the **ssh_hosts**.

**client_hosts** includes all of the hosts that *ESMON* client packages should be installed and configured. **lustre_oss ** defines whether to enable metric collection of Lustre OSS. **lustre_mds** defines whether to enable metric collection of Lustre MDS. **ime** defines whether to enable metric collection of *DDN IME*.

**host_id** in **server_host** is the host ID that *ESMON* server packages should be installed and configured. If **erase_influxdb** is true, all of the data and metadata of *Influxdb* will be erased completely. And if **drop_database** is true, the database of ESMON in *Influxdb* will be dropped. **erase_influxdb** and
**drop_database** should only be when the data in *Influxdb* is not needed any more. By enabling **erage_influxdb**, some corruption problems of *Influxdb* could be fixed.

### 3. Start the Installation on the Cluster

After the */etc/esmon_install.conf* file has been updated correctly on the *installation server*, following command could be run to start the installation on the cluster:

```shell
# esmon_install
```

 If the *ESMON* is installed successfully on the system,  following messages will be printed:

```
[2017/09/11-13:08:26][INFO] [esmon_install.py:1695] Exascaler monistoring system is installed, please check [/var/log/esmon_install/2017-09-11-13_07_01] for more log
```

All the logs which are useful for debugging are saved under */var/log/esmon_install* directory of the *installation server*.

### 4. Access the Monitoring Web Page

The *Grafana* service is started on the *monitoring server* automatically. The default HTTP port is 3000, and default user and group is admin.

## Troubleshooting

*/var/log/esmon_install/[installing_date]* directory on the *installation server* gathers all the logs that is useful for debugging. If a failure happens, some error messages will be printed to file */var/log/esmon_install/[installing_date]/error.log*. The first error message usually contains the information about the cause of failure.