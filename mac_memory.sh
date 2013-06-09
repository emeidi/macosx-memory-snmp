#!/bin/sh

# Purpose: Calls check_snmp_extend.py for a selected host and retrieves memory attributes injected into SNMP by the script memory.py running on the host

# Author:  Mario Aeby, info@eMeidi.com
# Version: 0.1
# github.com/emeidi/macosx-memory-snmp

PYTHON=`which python`
SCRIPT="check_snmp_extend.py"
DEBUG=0

if [ ! -e "$PYTHON" ]
then
	echo "File '$PYTHON' is not executable"
	exit 1
fi

if [ $# -lt 1 ]
then
	echo "Usage: $0 <hostname>"
	exit 1
fi

HOSTNAME="$1"
[ $DEBUG -eq 1 ] && echo "Hostname: $HOSTNAME"

# Make sure the python script is called with an absolute path
SCRIPT="`dirname $0`/$SCRIPT"

ATTRIBS="memory_free memory_wired memory_active memory_inactive memory_used"
for ATTRIB in $ATTRIBS
do
	CMD="$PYTHON $SCRIPT -H $HOSTNAME -e $ATTRIB"
	[ $DEBUG -eq 1 ] && echo "Running command: $CMD"
	
	RETVAL=`$CMD`
	echo -n "$ATTRIB:$RETVAL "
done

echo ""

exit 0