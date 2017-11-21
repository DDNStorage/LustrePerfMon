# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for installing virtual machines
"""
# pylint: disable=too-many-lines
import sys
import logging
import traceback
import os
import shutil
import random
import yaml
import filelock

# Local libs
from pyesmon import utils
from pyesmon import time_util
from pyesmon import ssh_host
from pyesmon import esmon_common

ESMON_VIRT_CONFIG_FNAME = "esmon_virt.conf"
ESMON_VIRT_CONFIG = "/etc/" + ESMON_VIRT_CONFIG_FNAME
ESMON_VIRT_LOG_DIR = "/var/log/esmon_virt"
STRING_DISTRO = "distro"
STRING_HOSTNAME = "hostname"
STRING_HOST_IPS = "ips"


def random_mac():
    """
    Generate random MAC address
    """
    mac_parts = [random.randint(0x00, 0x7f),
                 random.randint(0x00, 0xff),
                 random.randint(0x00, 0xff)]
    mac_string = "52:54:00"
    for mac_part in mac_parts:
        mac_string += ":" + ("%02x" % mac_part)
    return mac_string


def vm_is_shut_off(server_host, hostname):
    """
    Check whether vm is shut off
    """
    state = server_host.sh_virsh_dominfo_state(hostname)
    if state is None:
        return False
    elif state == "shut off":
        return True
    return False


def vm_check_shut_off(args):
    """
    Check whether vm is shut off
    """
    server_host = args[0]
    hostname = args[1]
    off = vm_is_shut_off(server_host, hostname)
    if off:
        return 0
    return -1


def vm_delete(server_host, hostname):
    """
    Delete a virtual machine
    """
    existed = True
    active = True
    state = server_host.sh_virsh_dominfo_state(hostname)
    if state is None:
        existed = False
        active = False
    elif state == "shut off":
        active = False

    if active:
        command = ("virsh destroy %s" % hostname)
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    if existed:
        command = ("virsh undefine %s" % hostname)
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    return 0


def vm_clone(workspace, server_host, hostname, network_configs, ips,
             template_hostname, image_dir, distro, internet, disk_number):
    """
    Create virtual machine
    """
    # pylint: disable=too-many-arguments,too-many-locals,too-many-return-statements
    # pylint: disable=too-many-branches,too-many-statements
    host_ip = ips[0]
    ret = vm_delete(server_host, hostname)
    if ret:
        return -1

    command = ("ping -c 1 %s" % host_ip)
    retval = server_host.sh_run(command)
    if retval.cr_exit_status == 0:
        logging.error("IP [%s] already used by a host", host_ip)
        return -1

    command = ("ping -c 1 %s" % hostname)
    retval = server_host.sh_run(command)
    if retval.cr_exit_status == 0:
        logging.error("host [%s] already up", hostname)
        return -1

    active = True
    state = server_host.sh_virsh_dominfo_state(template_hostname)
    if state is None:
        logging.error("template [%s] doesn't exist on host [%s]",
                      template_hostname, server_host.sh_hostname)
        return -1
    elif state == "shut off":
        active = False

    if active:
        command = ("virsh destroy %s" % template_hostname)
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    file_options = ""
    for disk_index in range(disk_number):
        file_options += (" --file %s/%s_%d.img" %
                         (image_dir, hostname, disk_index))

        command = ("rm -f %s/%s_%d.img" %
                   (image_dir, hostname, disk_index))
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    command = ("virt-clone --original %s --name %s%s" %
               (template_hostname, hostname, file_options))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    local_host_dir = workspace + "/" + hostname
    os.mkdir(local_host_dir)
    # net.ifnames=0 biosdevname=0 has been added to grub, so the interface
    # name will always be eth*
    eth_number = 0
    for eth_ip in ips:
        network_config = network_configs[eth_number]
        ifcfg = 'DEVICE="eth%d"\n' % eth_number
        ifcfg += 'IPADDR="%s"\n' % eth_ip
        ifcfg += 'NETMASK="%s"\n' % network_config["netmask"]
        if "gateway" in network_config:
            ifcfg += 'GATEWAY=\"%s"\n' % network_config["gateway"]
        ifcfg += """ONBOOT=yes
BOOTPROTO="static"
TYPE=Ethernet
IPV6INIT=no
NM_CONTROLLED=no
"""

        ifcfg_fname = "ifcfg-eth%d" % eth_number
        ifcfg_fpath = local_host_dir + "/" + ifcfg_fname
        with open(ifcfg_fpath, "wt") as fout:
            fout.write(ifcfg)

        host_ifcfg_fpath = workspace + "/" + ifcfg_fname
        ret = server_host.sh_send_file(ifcfg_fpath, workspace)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          ifcfg_fpath, workspace,
                          server_host.sh_hostname)
            return -1

        ret = server_host.sh_run("which virt-copy-in")
        if ret.cr_exit_status != 0:
            command = ("yum install libguestfs-tools-c -y")
            retval = server_host.sh_run(command)
            if retval.cr_exit_status:
                logging.error("failed to run command [%s] on host [%s], "
                              "ret = [%d], stdout = [%s], stderr = [%s]",
                              command,
                              server_host.sh_hostname,
                              retval.cr_exit_status,
                              retval.cr_stdout,
                              retval.cr_stderr)
                return -1

        command = ("virt-copy-in -d %s %s "
                   "/etc/sysconfig/network-scripts" % (hostname, host_ifcfg_fpath))
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
        eth_number += 1

    host_rules_fpath = workspace + "/70-persistent-net.rules"
    command = ("> %s" % host_rules_fpath)
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = ("virt-copy-in -d %s %s "
               "/etc/udev/rules.d" % (hostname, host_rules_fpath))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    if distro == ssh_host.DISTRO_RHEL6:
        network_string = 'NETWORKING=yes\n'
        network_string += 'HOSTNAME=%s\n' % hostname
        network_fname = "network"
        network_fpath = local_host_dir + "/" + network_fname
        with open(network_fpath, "wt") as fout:
            fout.write(network_string)

        host_network_fpath = workspace + "/" + network_fname
        ret = server_host.sh_send_file(network_fpath, workspace)
        if ret:
            logging.error("failed to send file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          network_fpath, workspace,
                          server_host.sh_hostname)
            return -1

        command = ("virt-copy-in -d %s %s "
                   "/etc/sysconfig" % (hostname, host_network_fpath))
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1
    else:
        host_hostname_fpath = workspace + "/hostname"
        command = ("echo %s > %s" % (hostname, host_hostname_fpath))
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        command = ("virt-copy-in -d %s %s "
                   "/etc" % (hostname, host_hostname_fpath))
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    command = ("virsh start %s" % hostname)
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    # Remove the record in known_hosts, otherwise ssh will fail
    command = ('sed -i "/%s /d" /root/.ssh/known_hosts' % (host_ip))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    # Remove the record in known_hosts, otherwise ssh will fail
    command = ('sed -i "/%s /d" /root/.ssh/known_hosts' % (hostname))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    vm_host = ssh_host.SSHHost(host_ip)
    ret = vm_host.sh_wait_up()
    if ret:
        logging.error("failed to wait host [%s] up",
                      host_ip)
        return -1

    ret = vm_check(hostname, host_ip, distro, internet)
    if ret:
        return -1
    return 0


def vm_check(hostname, host_ip, distro, internet):
    """
    Check whether virtual machine is up and fine
    """
    # pylint: disable=too-many-return-statements
    vm_host = ssh_host.SSHHost(host_ip)
    command = "hostname"
    retval = vm_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      host_ip,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    current_hostname = retval.cr_stdout.strip()
    if current_hostname != hostname:
        logging.error("wrong host name of the virtual machine [%s], expected "
                      "[%s], got [%s]", host_ip, hostname, current_hostname)
        return -1

    vm_host = ssh_host.SSHHost(hostname)
    command = "hostname"
    retval = vm_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    current_hostname = retval.cr_stdout.strip()
    if current_hostname != hostname:
        logging.error("wrong host name of the virtual machine [%s], expected "
                      "[%s], got [%s]", hostname, hostname, current_hostname)
        return -1

    if vm_host.sh_distro() != distro:
        logging.error("wrong distro of the virtual machine [%s], expected "
                      "[%s], got [%s]", hostname, distro, vm_host.sh_distro())
        return -1

    if internet:
        if vm_host.sh_check_internet():
            logging.error("virtual machine [%s] can not access Internet",
                          hostname)
            return -1
    return 0


def vm_start(workspace, server_host, hostname, network_configs, ips,
             template_hostname, image_dir, distro, internet, disk_number):
    """
    Start virtual machine, if vm is bad, clone it
    """
    # pylint: disable=too-many-arguments
    host_ip = ips[0]
    ret = vm_check(hostname, host_ip, distro, internet)
    if ret == 0:
        return 0

    if vm_is_shut_off(server_host, hostname):
        command = ("virsh start %s" % (hostname))
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    vm_host = ssh_host.SSHHost(hostname)
    ret = vm_host.sh_wait_up()
    if ret == 0:
        ret = vm_check(hostname, host_ip, distro, internet)
        if ret == 0:
            return 0

    ret = vm_clone(workspace, server_host, hostname, network_configs, ips,
                   template_hostname, image_dir, distro, internet, disk_number)
    if ret:
        logging.error("failed to create virtual machine [%s] based on "
                      "template [%s]", hostname, template_hostname)
        return -1
    return 0


def vm_install(workspace, server_host, iso_path, hostname,
               internet, network_configs, image_dir, distro,
               ram_size, disk_sizes):
    """
    Install virtual machine from ISO
    """
    # pylint: disable=too-many-arguments,too-many-locals
    # pylint: disable=too-many-return-statements,too-many-statements
    # pylint: disable=too-many-branches
    ret = vm_delete(server_host, hostname)
    if ret:
        return -1

    network_config = network_configs[0]
    host_ip = network_config["ip"]
    command = ("ping -c 1 %s" % host_ip)
    retval = server_host.sh_run(command)
    if retval.cr_exit_status == 0:
        logging.error("IP [%s] is already used by a host", host_ip)
        return -1

    command = ("ping -c 1 %s" % hostname)
    retval = server_host.sh_run(command)
    if retval.cr_exit_status == 0:
        logging.error("host [%s] is already up", hostname)
        return -1

    mnt_path = "/mnt/" + utils.random_word(8)
    command = ("mkdir -p %s && mount -o loop %s %s" %
               (mnt_path, iso_path, mnt_path))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    ks_config = """# Kickstart file automatically generated by ESMON.
install
reboot
cdrom
lang en_US.UTF-8
keyboard us
"""
    ks_config += """rootpw password
firewall --disabled
authconfig --enableshadow --passalgo=sha512
selinux --disabled
timezone --utc Asia/Shanghai
bootloader --location=mbr --driveorder=sda --append="crashkernel=auto net.ifnames=0 biosdevname=0"
zerombr
clearpart --all --initlabel
part / --fstype=ext4 --grow --size=500 --ondisk=sda --asprimary
repo --name="Media" --baseurl=file:///mnt/source --cost=100
%packages
@Core
%end
%post --log=/var/log/anaconda/post-install.log
#!/bin/bash
# Configure hostname, somehow virt-install --name doesn't work
"""
    if distro == ssh_host.DISTRO_RHEL6:
        ks_config += 'echo NETWORKING=yes > /etc/sysconfig/network\n'
        ks_config += ('echo HOSTNAME=%s >> /etc/sysconfig/network\n' %
                      (hostname))
    elif distro == ssh_host.DISTRO_RHEL7:
        ks_config += "echo %s > /etc/hostname\n" % (hostname)
    else:
        logging.error("wrong distro [%s]", distro)
        return -1
    ks_config += "# Configure network\n"
    eth_number = 0
    ens_number = 3
    for network_config in network_configs:
        # net.ifnames=0 biosdevname=0 will be added to GRUB_CMDLINE_LINUX, so the
        # interface name will always be eth*
        ks_config += "# Network eth%d\n" % eth_number
        ks_config += ("rm -f /etc/sysconfig/network-scripts/ifcfg-ens%d\n" %
                      ens_number)
        ks_config += ("cat << EOF > /etc/sysconfig/network-scripts/ifcfg-eth%d\n" %
                      eth_number)
        ks_config += "DEVICE=eth%d\n" % eth_number
        ks_config += 'IPADDR="%s"\n' % network_config["ip"]
        ks_config += 'NETMASK="%s"\n' % network_config["netmask"]
        if "gateway" in network_config:
            ks_config += 'GATEWAY=\"%s"\n' % network_config["gateway"]
        ks_config += """ONBOOT=yes
BOOTPROTO="static"
TYPE=Ethernet
IPV6INIT=no
NM_CONTROLLED=no
EOF
"""
        eth_number += 1
        ens_number += 1

    ks_config += "%end\n"
    local_host_dir = workspace + "/" + hostname
    os.mkdir(local_host_dir)
    ks_fname = "%s.ks" % hostname
    ks_fpath = local_host_dir + "/" + ks_fname
    with open(ks_fpath, "wt") as fout:
        fout.write(ks_config)

    host_ks_fpath = workspace + "/" + ks_fname
    ret = server_host.sh_send_file(ks_fpath, workspace)
    if ret:
        logging.error("failed to send file [%s] on local host to "
                      "directory [%s] on host [%s]",
                      ks_fpath, workspace,
                      server_host.sh_hostname)
        return -1

    command = ("virt-install --vcpus=1 --os-type=linux "
               "--hvm --connect=qemu:///system "
               "--accelerate --serial pty -v --nographics --noautoconsole --wait=-1 ")
    command += "--ram=%s " % ram_size
    for network_config in network_configs:
        command += ("--network=%s " % (network_config["virt_install_option"]))
    command += ("--name=%s " % (hostname))
    command += ("--initrd-inject=%s " % (host_ks_fpath))
    disk_index = 0
    for disk_size in disk_sizes:
        command += ("--disk path=%s/%s_%d.img,size=%s " %
                    (image_dir, hostname, disk_index, disk_size))
        disk_index += 1
    command += ("--location %s " % (mnt_path))
    command += ("--disk=%s,device=cdrom,perms=ro " % (iso_path))
    command += ("--extra-args='console=tty0 console=ttyS0,115200n8 "
                "ks=file:/%s'" % (ks_fname))

    if distro == ssh_host.DISTRO_RHEL6:
        install_timeout = 300
    elif distro == ssh_host.DISTRO_RHEL7:
        install_timeout = 600

    retval = server_host.sh_run(command, timeout=install_timeout)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    ret = server_host.sh_run("which sshpass")
    if ret.cr_exit_status != 0:
        command = ("yum install sshpass -y")
        retval = server_host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          server_host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

    # Remove the record in known_hosts, otherwise ssh will fail
    command = ('sed -i "/%s /d" /root/.ssh/known_hosts' % (host_ip))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    # When virt-install finished, the virtual machine starts to reboot
    # so wait a little bit here until the host is up. Need
    # StrictHostKeyChecking=no, otherwise exit code will be 6 (ENOENT)
    expect_stdout = hostname + "\n"
    command = ("sshpass -p password ssh -o StrictHostKeyChecking=no "
               "root@%s hostname" % (host_ip))
    ret = server_host.sh_wait_update(command, expect_exit_status=0,
                                     expect_stdout=expect_stdout)
    if ret:
        logging.error("failed to wait host [%s] up", hostname)
        return -1

    command = ("sshpass -p password ssh root@%s "
               "\"mkdir /root/.ssh && chmod 600 /root/.ssh\"" % (host_ip))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = ("sshpass -p password scp /root/.ssh/* root@%s:/root/.ssh" % (host_ip))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    vm_host = ssh_host.SSHHost(host_ip)
    command = "> /root/.ssh/known_hosts"
    retval = vm_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      vm_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    command = "hostname"
    retval = vm_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      vm_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    if internet:
        ret = vm_host.sh_enable_dns()
        if ret:
            logging.error("failed to enable dns on host [%s]")
            return -1

    real_hostname = retval.cr_stdout.strip()
    if real_hostname != hostname:
        logging.error("wrong hostname, expected [%s], got [%s]",
                      hostname, real_hostname)
        return -1

    # Do not check the return status, because the connection could be stopped
    command = "init 0"
    vm_host.sh_run(command)

    command = ("umount %s" % (mnt_path))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        ret = -1

    command = ("rmdir %s" % (mnt_path))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    # Need to wait until VM shut off, otherwise "virsh change-media" won't
    # change the XML file
    ret = utils.wait_condition(vm_check_shut_off, [server_host, hostname])
    if ret:
        logging.error("failed when waiting host [%s] on [%s] shut off",
                      hostname, server_host.sh_hostname)
        return ret

    # Find the CDROM device
    command = ("virsh domblklist %s --details | grep cdrom | "
               "awk '{print $3}'" % (hostname))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1
    cdroms = retval.cr_stdout.splitlines()
    if len(cdroms) != 1:
        logging.error("unexpected cdroms: [%s]",
                      retval.cr_stdout)
        return -1
    cdrom = cdroms[0]

    command = ("virsh change-media %s %s --eject" % (hostname, cdrom))
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    return 0


def esmon_vm_install(workspace, config, config_fpath):
    """
    Start to test with ESMON
    """
    # pylint: disable=too-many-return-statements,too-many-locals
    # pylint: disable=too-many-branches,too-many-statements
    server_host_config = esmon_common.config_value(config, "server_host")
    if server_host_config is None:
        logging.error("no [server_host] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    server_host = ssh_host.SSHHost("localhost", local=True)

    image_dir = esmon_common.config_value(server_host_config, "image_dir")
    if image_dir is None:
        logging.error("no [image_dir] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel6_template_hostname = esmon_common.config_value(server_host_config,
                                                        "rhel6_template_hostname")
    if rhel6_template_hostname is None:
        logging.error("no [rhel6_template_hostname] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel6_template_reinstall = esmon_common.config_value(server_host_config,
                                                         "rhel6_template_reinstall")
    if rhel6_template_reinstall is None:
        logging.error("no [rhel6_template_reinstall] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    internet = esmon_common.config_value(server_host_config,
                                         "internet")
    if internet is None:
        internet = False
        logging.debug("no [internet] is configured, disable internet")

    ram_size = esmon_common.config_value(server_host_config, "ram_size")
    if ram_size is None:
        logging.error("no [ram_size] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    disk_sizes = esmon_common.config_value(server_host_config, "disk_sizes")
    if disk_sizes is None:
        logging.error("no [disk_sizes] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel6_network_configs = esmon_common.config_value(server_host_config,
                                                      "rhel6_network_configs")
    if rhel6_network_configs is None:
        logging.error("no [rhel6_network_configs] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel6_iso = esmon_common.config_value(server_host_config, "rhel6_iso")
    if rhel6_iso is None:
        logging.error("no [rhel6_iso] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    command = "mkdir -p %s" % workspace
    retval = server_host.sh_run(command)
    if retval.cr_exit_status:
        logging.error("failed to run command [%s] on host [%s], "
                      "ret = [%d], stdout = [%s], stderr = [%s]",
                      command,
                      server_host.sh_hostname,
                      retval.cr_exit_status,
                      retval.cr_stdout,
                      retval.cr_stderr)
        return -1

    if rhel6_template_reinstall:
        ret = vm_install(workspace, server_host, rhel6_iso,
                         rhel6_template_hostname, internet,
                         rhel6_network_configs, image_dir,
                         ssh_host.DISTRO_RHEL6, ram_size,
                         disk_sizes)
        if ret:
            logging.error("failed to create virtual machine template [%s]",
                          rhel6_template_hostname)
            return -1

    rhel7_template_hostname = esmon_common.config_value(server_host_config,
                                                        "rhel7_template_hostname")
    if rhel7_template_hostname is None:
        logging.error("no [rhel7_template_hostname] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel7_template_reinstall = esmon_common.config_value(server_host_config,
                                                         "rhel7_template_reinstall")
    if rhel7_template_reinstall is None:
        logging.error("no [rhel7_template_reinstall] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel7_network_configs = esmon_common.config_value(server_host_config,
                                                      "rhel7_network_configs")
    if rhel7_network_configs is None:
        logging.error("no [rhel7_network_configs] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    rhel7_iso = esmon_common.config_value(server_host_config, "rhel7_iso")
    if rhel7_iso is None:
        logging.error("no [rhel7_iso] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    if rhel7_template_reinstall:
        ret = vm_install(workspace, server_host, rhel7_iso,
                         rhel7_template_hostname, internet,
                         rhel7_network_configs, image_dir,
                         ssh_host.DISTRO_RHEL7, ram_size,
                         disk_sizes)
        if ret:
            logging.error("failed to create virtual machine template [%s]",
                          rhel7_template_hostname)
            return -1

    vm_host_configs = esmon_common.config_value(config, "vm_hosts")
    if vm_host_configs is None:
        logging.error("no [vm_hosts] is configured, "
                      "please correct file [%s]", config_fpath)
        return -1

    hosts = []
    hosts_string = """127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
"""
    for vm_host_config in vm_host_configs:
        hostname = esmon_common.config_value(vm_host_config, STRING_HOSTNAME)
        if hostname is None:
            logging.error("no [hostname] is configured for a vm_host, "
                          "please correct file [%s]", config_fpath)
            return -1

        ips = esmon_common.config_value(vm_host_config, STRING_HOST_IPS)
        if ips is None:
            logging.error("no [%s] is configured for a vm_host, "
                          "please correct file [%s]", STRING_HOST_IPS,
                          config_fpath)
            return -1

        distro = esmon_common.config_value(vm_host_config, STRING_DISTRO)
        if distro is None:
            logging.error("no [distro] is configured for a vm_host, "
                          "please correct file [%s]", config_fpath)
            return -1

        if distro == ssh_host.DISTRO_RHEL6:
            template_hostname = rhel6_template_hostname
            network_configs = rhel6_network_configs
        elif distro == ssh_host.DISTRO_RHEL7:
            template_hostname = rhel7_template_hostname
            network_configs = rhel7_network_configs
        else:
            logging.error("invalid distro [%s] is configured for a vm_host, "
                          "please correct file [%s]", distro, config_fpath)
            return -1

        reinstall = esmon_common.config_value(vm_host_config, "reinstall")
        if reinstall is None:
            reinstall = False

        if not reinstall:
            ret = vm_start(workspace, server_host, hostname, network_configs,
                           ips, template_hostname, image_dir, distro, internet,
                           len(disk_sizes))
            if ret:
                logging.error("virtual machine [%s] can't be started",
                              hostname)
                return -1
        else:
            ret = vm_clone(workspace, server_host, hostname, network_configs,
                           ips, template_hostname, image_dir, distro, internet,
                           len(disk_sizes))
            if ret:
                logging.error("failed to create virtual machine [%s] based on "
                              "template [%s]", hostname, rhel7_template_hostname)
                return -1

        host_ip = ips[0]
        vm_host = ssh_host.SSHHost(hostname)
        hosts_string += ("%s %s\n" % (host_ip, hostname))
        hosts.append(vm_host)

    hosts_fpath = workspace + "/hosts"
    with open(hosts_fpath, "wt") as hosts_file:
        hosts_file.write(hosts_string)

    for host in hosts:
        ret = host.sh_enable_dns()
        if ret:
            logging.error("failed to enable dns on host [%s]",
                          host.sh_hostname)
            return -1

        command = "yum install rsync -y"
        retval = host.sh_run(command)
        if retval.cr_exit_status:
            logging.error("failed to run command [%s] on host [%s], "
                          "ret = [%d], stdout = [%s], stderr = [%s]",
                          command,
                          host.sh_hostname,
                          retval.cr_exit_status,
                          retval.cr_stdout,
                          retval.cr_stderr)
            return -1

        ret = host.sh_send_file(hosts_fpath, "/etc")
        if ret:
            logging.error("failed to send hosts file [%s] on local host to "
                          "directory [%s] on host [%s]",
                          hosts_fpath, workspace,
                          host.sh_hostname)
            return -1

    return 0


def esmon_virt_locked(workspace, config_fpath):
    """
    Start to test holding the confiure lock
    """
    # pylint: disable=too-many-branches,bare-except,too-many-locals
    # pylint: disable=too-many-statements
    config_fd = open(config_fpath)
    ret = 0
    try:
        config = yaml.load(config_fd)
    except:
        logging.error("not able to load [%s] as yaml file: %s", config_fpath,
                      traceback.format_exc())
        ret = -1
    config_fd.close()
    if ret:
        return -1

    try:
        ret = esmon_vm_install(workspace, config, config_fpath)
    except:
        ret = -1
        logging.error("exception: %s", traceback.format_exc())

    return ret


def esmon_virt(workspace, config_fpath):
    """
    Start to install virtual machines
    """
    # pylint: disable=bare-except
    lock_file = config_fpath + ".lock"
    lock = filelock.FileLock(lock_file)
    try:
        with lock.acquire(timeout=0):
            try:
                ret = esmon_virt_locked(workspace, config_fpath)
            except:
                ret = -1
                logging.error("exception: %s", traceback.format_exc())
            lock.release()
    except filelock.Timeout:
        ret = -1
        logging.error("someone else is holding lock of file [%s], aborting "
                      "to prevent conflicts", lock_file)
    return ret


def usage():
    """
    Print usage string
    """
    utils.eprint("Usage: %s <config_file>" %
                 sys.argv[0])


def main():
    """
    Install virtual machines
    """
    # pylint: disable=unused-variable
    reload(sys)
    sys.setdefaultencoding("utf-8")
    config_fpath = ESMON_VIRT_CONFIG

    if len(sys.argv) == 2:
        config_fpath = sys.argv[1]
    elif len(sys.argv) > 2:
        usage()
        sys.exit(-1)

    identity = time_util.local_strftime(time_util.utcnow(), "%Y-%m-%d-%H_%M_%S")
    workspace = ESMON_VIRT_LOG_DIR + "/" + identity

    if not os.path.exists(ESMON_VIRT_LOG_DIR):
        os.mkdir(ESMON_VIRT_LOG_DIR)
    elif not os.path.isdir(ESMON_VIRT_LOG_DIR):
        logging.error("[%s] is not a directory", ESMON_VIRT_LOG_DIR)
        sys.exit(-1)

    if not os.path.exists(workspace):
        os.mkdir(workspace)
    elif not os.path.isdir(workspace):
        logging.error("[%s] is not a directory", workspace)
        sys.exit(-1)

    print("Started installing virtual machines using config [%s], "
          "please check [%s] for more log" %
          (config_fpath, workspace))
    utils.configure_logging(workspace)

    console_handler = utils.LOGGING_HANLDERS["console"]
    console_handler.setLevel(logging.DEBUG)

    save_fpath = workspace + "/" + ESMON_VIRT_CONFIG_FNAME
    logging.debug("copying config file from [%s] to [%s]", config_fpath,
                  save_fpath)
    shutil.copyfile(config_fpath, save_fpath)
    ret = esmon_virt(workspace, config_fpath)
    if ret:
        logging.error("installation failed, please check [%s] for more log\n",
                      workspace)
        sys.exit(ret)
    logging.info("Installed the virtual machines, please check [%s] "
                 "for more log", workspace)
    sys.exit(0)
