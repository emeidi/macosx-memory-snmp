#!/usr/bin/python

import sys
import subprocess
import re

if len(sys.argv) != 2:
	print 'Usage: ' + sys.argv[0] + ' [free|wired|active|inactive|used]'
	sys.exit(1)

parameter = sys.argv[1]
#print 'Parameter: ' + parameter
#sys.exit(0)

# Get process info
ps = subprocess.Popen(['ps', '-caxm', '-orss,comm'], stdout=subprocess.PIPE).communicate()[0]
vm = subprocess.Popen(['vm_stat'], stdout=subprocess.PIPE).communicate()[0]

# Iterate processes
processLines = ps.split('\n')
sep = re.compile('[\s]+')
rssTotal = 0 # kB
for row in range(1,len(processLines)):
    rowText = processLines[row].strip()
    rowElements = sep.split(rowText)
    try:
        rss = float(rowElements[0]) * 1024
    except:
        rss = 0 # ignore...
    rssTotal += rss

# Process vm_stat
vmLines = vm.split('\n')
sep = re.compile(':[\s]+')
vmStats = {}
for row in range(1,len(vmLines)-2):
    rowText = vmLines[row].strip()
    rowElements = sep.split(rowText)
    vmStats[(rowElements[0])] = int(rowElements[1].strip('\.')) * 4096

if parameter == 'free':
	#print 'RAW: ' + str(vmStats["Pages free"])
	#print 'MB:  ' + str(vmStats["Pages free"]/1024/1024)
	print str(vmStats["Pages free"])

if parameter == 'wired':
	print str(vmStats["Pages wired down"])

if parameter == 'active':
	print str(vmStats["Pages active"])

if parameter == 'inactive':
	print str(vmStats["Pages inactive"])

if parameter == 'used':
	total = vmStats["Pages wired down"] + vmStats["Pages active"] + vmStats["Pages inactive"]
	print str(total)

sys.exit(0);

print 'Wired Memory:\t\t%d MB' % ( vmStats["Pages wired down"]/1024/1024 )
print 'Active Memory:\t\t%d MB' % ( vmStats["Pages active"]/1024/1024 )
print 'Inactive Memory:\t%d MB' % ( vmStats["Pages inactive"]/1024/1024 )
print 'Free Memory:\t\t%d MB' % ( vmStats["Pages free"]/1024/1024 )
print 'Real Mem Total (ps):\t%.3f MB' % ( rssTotal/1024/1024 )