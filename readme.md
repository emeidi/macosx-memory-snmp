Purpose
=======
You are monitoring one or several computers running Mac OS X on your local network using cacti — but the Memory Usage graph is empty? No wonder: Apple does not provide /proc/meminfo where net-snmp usually would derive this information from.

In order to remedy this situation, I borrowed two scripts available online, modified and integrated them into my setup.

Using the `memory.py` script, I can insert information from running `vm_stat` on the local computer (ie. the computer to be monitored by cacti) into SNMP.

Using `check_snmp_extend.py` - or actually rather the wrapper script `mac_memory.sh` - I can query the SNMP servers on all my Macs for the memory attributes provided by `memory.py` and pass this information to cacti.

Installation Instructions
=========================

On the Mac you want to monitor using SNMP
-----------------------------------------
1. Copy `memory.py` to a convenient location on your Mac, e.g. /usr/local/bin
1. Make `memory.py` readable and executable for the SNMP user
1. Add all lines starting with `exec` in snmpd.conf to /etc/snmp/snmpd.conf
  * Adjust path to `memory.py` according to the location of the script defined in first step
1. Restart snmpd daemon using `restart-snmp.sh`

If you want to check whether SNMP returns memory information, execute the following command on the Mac you want to monitor:

```bash
snmpwalk -v 1 -c public localhost .1.3.6.1.4.1.2021.8.1
UCD-SNMP-MIB::extIndex.1 = INTEGER: 1
UCD-SNMP-MIB::extIndex.2 = INTEGER: 2
UCD-SNMP-MIB::extIndex.3 = INTEGER: 3
UCD-SNMP-MIB::extIndex.4 = INTEGER: 4
UCD-SNMP-MIB::extIndex.5 = INTEGER: 5
UCD-SNMP-MIB::extNames.1 = STRING: memory_free
UCD-SNMP-MIB::extNames.2 = STRING: memory_wired
UCD-SNMP-MIB::extNames.3 = STRING: memory_active
UCD-SNMP-MIB::extNames.4 = STRING: memory_inactive
UCD-SNMP-MIB::extNames.5 = STRING: memory_used
UCD-SNMP-MIB::extCommand.1 = STRING: /usr/bin/python
UCD-SNMP-MIB::extCommand.2 = STRING: /usr/bin/python
UCD-SNMP-MIB::extCommand.3 = STRING: /usr/bin/python
UCD-SNMP-MIB::extCommand.4 = STRING: /usr/bin/python
UCD-SNMP-MIB::extCommand.5 = STRING: /usr/bin/python
UCD-SNMP-MIB::extResult.1 = INTEGER: 0
UCD-SNMP-MIB::extResult.2 = INTEGER: 0
UCD-SNMP-MIB::extResult.3 = INTEGER: 0
UCD-SNMP-MIB::extResult.4 = INTEGER: 0
UCD-SNMP-MIB::extResult.5 = INTEGER: 0
UCD-SNMP-MIB::extOutput.1 = STRING: 7727325184
UCD-SNMP-MIB::extOutput.2 = STRING: 2521927680
UCD-SNMP-MIB::extOutput.3 = STRING: 2995613696
UCD-SNMP-MIB::extOutput.4 = STRING: 2286985216
UCD-SNMP-MIB::extOutput.5 = STRING: 7804522496
UCD-SNMP-MIB::extErrFix.1 = INTEGER: noError(0)
UCD-SNMP-MIB::extErrFix.2 = INTEGER: noError(0)
UCD-SNMP-MIB::extErrFix.3 = INTEGER: noError(0)
UCD-SNMP-MIB::extErrFix.4 = INTEGER: noError(0)
UCD-SNMP-MIB::extErrFix.5 = INTEGER: noError(0)
UCD-SNMP-MIB::extErrFixCmd.1 = STRING: 
UCD-SNMP-MIB::extErrFixCmd.2 = STRING: 
UCD-SNMP-MIB::extErrFixCmd.3 = STRING: 
UCD-SNMP-MIB::extErrFixCmd.4 = STRING: 
UCD-SNMP-MIB::extErrFixCmd.5 = STRING:
```

On the cacti server
-------------------
1. Copy `mac_memory.sh` and `check_snmp_extend.py` to <cacti>/resourcess/scripts

In the cacti web interface
--------------------------
1. Import `cacti_graph_template_mac_os_x_-_memory_usage_-_graph_template.xml`
1. Add the graph template `Mac OS X - Memory Usage - Graph Template` to an existing device
1. Enjoy!

![alt text](https://raw.github.com/emeidi/macosx-memory-snmp/master/mac_memory_usage.png "Example Memory Usage")