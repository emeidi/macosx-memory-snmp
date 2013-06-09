#!/bin/sh

echo "Stopping SNMP daemon ..."
sudo launchctl unload /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist

echo "Starting SNMP daemon ..."
sudo launchctl load -w /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist

exit 0
