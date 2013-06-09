#!/bin/sh

# Purpose: Restarts snmpd on Mac OS X

# Author:  Mario Aeby, info@eMeidi.com
# Version: 0.1
# Home:    github.com/emeidi/macosx-memory-snmp

echo "Stopping SNMP daemon ..."
sudo launchctl unload /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist

echo "Starting SNMP daemon ..."
sudo launchctl load -w /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist

exit 0
