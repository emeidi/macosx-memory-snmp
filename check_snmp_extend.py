#!/usr/bin/python
#-*- coding: utf-8 -*-

# Original Author: tntteam@free.fr

# As of version .2 Nick Anderson <nick@cmdln.org> 
# cloned the script and maintains a git repository. 
# Patches Welcome!
# https://github.com/nickanderson/check_snmp_extend

###################################################
#
# IMPORT
#
###################################################

from sys import exit
from sys import argv
import commands, signal
from optparse import OptionParser




###################################################
#
# Initial values
#
###################################################

overall_status = -1

ok=0
unknown=1
warning=2
critical=3

state = {
	ok			: "OK",
	unknown		: "UNKNOWN",
	warning		: "WARNING",
	critical	: "CRITICAL"
}

state_nagios = {
	"OK"		:	0,
	"WARNING"	:	1,
	"CRITICAL"	:	2,
	"UNKNOWN"	:	3
}
state_nagios_text = {
	0	: "OK",
	1	: "WARNING",
	2	: "CRITICAL",
	3	: "UNKNOWN"
}

exit_codes = {
	0	:	state_nagios["OK"],
	1	:	state_nagios["UNKNOWN"],
	2	:	state_nagios["WARNING"],
	3	:	state_nagios["CRITICAL"]
}

summary=""
long_output=""
perfdata=""
ok_count=0
not_ok_count=0


###################################################
#
# Timeout()
#       Timeout a function (src : http://programming-guides.com/python/timeout-a-function)
###################################################
class TimeoutException(Exception):
    pass

def timeout():
	def timeout_function(f):
		def f2(*args):
			def timeout_handler(signum, frame):
				raise TimeoutException()

			old_handler = signal.signal(signal.SIGALRM, timeout_handler)
			signal.alarm(options.timeout) # triger alarm in timeout_time seconds
			try:
				retval = f()
			except TimeoutException:
				error("TIMEOUT")
			finally:
				signal.signal(signal.SIGALRM, old_handler)
				signal.alarm(0)
			return retval
		return f2
	return timeout_function

	
def clean_line_result(text):
	ret = ['', '']
	
	text2=text.split('=',1)
	#plugin name :
	ret[0]=text2[0].split('.',1)[1].replace('"','').strip()
	#return code removing the ending \n:
	ret[1]=int(text2[1].rstrip('\n'))
	return ret
	
def clean_line_output(text):
	ret = ['', '', '', '']
	
	text2=text.split('=',1)
	#plugin name :
	ret[0]=text2[0].split('.',1)[1].replace('"','').strip()
	#return (code, text, etc.) removing the ending \n
	text3=text2[1].rstrip('\n')
	#return summary
	ret[1]=text3.split('|',1)[0].split('\n')[0].strip()
	#return perfdata
	try:
		ret[2]=text3.split('|',1)[1].split('\n')[0].strip()
		try: #more perfdata (nagios syntax guide says it's correct -_-)
			ret[2]="%s %s" % (ret[2], text3.split('|',2)[2].strip())
		except IndexError:
			pass
	except IndexError:
			pass
	#return long output
	try: #split on | left side because we can have perfdata after long output
		ret[3]=text3.split('\n')[1].split('|')[0].strip()
	except IndexError:
		pass

	return ret

###################################################
#				
# check_snmp_extend()
#	check all SNMP extend
###################################################
def check_snmp_extend():
	global overall_status, ok_count, not_ok_count
	
	output_table={}
	
	timeoutstr="Timeout: No Response from " + options.host
	noexecstr="::nsExtendResult = No Such Instance currently exists at this OID"
        if options.snmp_version == '3':
		snmp_request="snmpwalk -v%s -u %s -l %s -a %s -A %s -x %s -X %s -OQ %s 'NET-SNMP-EXTEND-MIB::nsExtendResult'" % (options.snmp_version, options.snmp_user, options.snmp_seclevel, options.snmp_authproto, options.snmp_authpass, options.snmp_privproto, options.snmp_privpass, options.host)
	else:
		snmp_request="snmpwalk -v%s -c %s -OQ %s 'NET-SNMP-EXTEND-MIB::nsExtendResult'" % (options.snmp_version, options.community, options.host)
	
	results=commands.getoutput(snmp_request).split("NET-SNMP-EXTEND-MIB")
	if options.debug:
		debug("snmp request: %s" % (snmp_request))
		debug(results)
	
	if results[0] == timeoutstr:
		error("No response from: %s. Maybe community is not good ?" % (options.host) )
	if results[1] == noexecstr:
		error("No extend snmp found for this server: %s." % (options.host) )
	
	if options.snmp_version == '3':
		snmp_request="snmpwalk -v%s -u %s -l %s -a %s -A %s -x %s -X %s -OQ %s 'NET-SNMP-EXTEND-MIB::nsExtendOutputFull'" % (options.snmp_version, options.snmp_user, options.snmp_seclevel, options.snmp_authproto, options.snmp_authpass, options.snmp_privproto, options.snmp_privpass, options.host)
	else:
		snmp_request="snmpwalk -v%s -c %s -OQ %s 'NET-SNMP-EXTEND-MIB::nsExtendOutputFull'" % (options.snmp_version, options.community, options.host)

	outputs=commands.getoutput(snmp_request).split("NET-SNMP-EXTEND-MIB")
	if options.debug:
		debug("snmp request: %s" % (snmp_request))
		debug(outputs)

	if results[0] == timeoutstr:
		error("No response from: %s. Maybe community is not good ?" % (options.host) )
	if results[1] == noexecstr:
		error("No extend snmp found for this server: %s." % (options.host) )	
		
	for i in range(1,len(results)): #skip 0 as it's empty because of split
		cleaned_result=clean_line_result(results[i])
		
		plugin_name=cleaned_result[0]
		plugin_return_code=int(cleaned_result[1])
		if not plugin_name in output_table :
			output_table[plugin_name]={
				"Name"			:	"",
				"Result"		:	unknown,
				"Summary"		:	"",
				"Perfdata"		:	"",
				"LongOutput"	:	""
			}
		
		#output_table[plugin_name]["Name"]=plugin_name
		output_table[plugin_name]["Result"]=plugin_return_code
	
	for i in range(1,len(outputs)): #skip 0 as it's empty because of split
		cleaned_output=clean_line_output(outputs[i])
		
		plugin_name=cleaned_output[0]
		plugin_return_summary=cleaned_output[1]
		plugin_return_perfdata=cleaned_output[2]
		plugin_return_long_output=cleaned_output[3]
		
		if not plugin_name in output_table :
			output_table[plugin_name]={
				"Name"			:	"",
				"Result"		:	unknown,
				"Summary"		:	"",
				"Perfdata"		:	"",
				"LongOutput"	:	""
			}
			
		#output_table[plugin_name]["Name"]=plugin_name
		output_table[plugin_name]["Summary"]=plugin_return_summary
		output_table[plugin_name]["Perfdata"]=plugin_return_perfdata
		output_table[plugin_name]["LongOutput"]=plugin_return_long_output
	
		
	
	for snmp_extend in output_table.items():
	
		#stupid nagios rules, unknown return code is > critical ...
		#so a dirty method is applied here to avoid this
		if snmp_extend[1]["Result"]==state_nagios["OK"]:
			overall_status = max(overall_status,ok)
		elif snmp_extend[1]["Result"]==state_nagios["WARNING"]:
			overall_status = max(overall_status,warning)
		elif snmp_extend[1]["Result"]==state_nagios["CRITICAL"]:
			overall_status = max(overall_status,critical)
		else:
			overall_status = max(overall_status,unknown)
			
		if options.output_complete_summary:
			add_summary("%s=%s, " % (snmp_extend[0],snmp_extend[1]["Summary"]) )
		else:
			add_summary("%s=%s, " % (snmp_extend[0],state_nagios_text[snmp_extend[1]["Result"]]) )
		
		if snmp_extend[1]["Perfdata"] != "" and options.output_perfdata:
			add_perfdata("%s" % (snmp_extend[1]["Perfdata"]) )
	
		if snmp_extend[1]["LongOutput"] != "" and options.output_longoutput:
			add_long_output("%s=%s, " % (snmp_extend[0], snmp_extend[1]["LongOutput"]) )
	
		if snmp_extend[1]["Result"] > ok:
			not_ok_count+=1
		else:
			ok_count+=1
		
		if options.debug:
			debug("extend name: %s, summary: %s, perfdata: %s, longoutput: %s" % (snmp_extend[0], snmp_extend[1]["Summary"], snmp_extend[1]["Perfdata"], snmp_extend[1]["LongOutput"]) )

	
		
###################################################
#				
# check_this_snmp_extend()
#	check this SNMP extend (options.extend_name)
###################################################
def check_this_snmp_extend():
	global overall_status
	
	output_table={}
	
	timeoutstr="Timeout: No Response from " + options.host
	noexecstr="No Such Instance currently exists at this OID"

	if options.snmp_version == '3':
		snmp_request="snmpwalk -v%s -u %s -l %s -a %s -A %s -x %s -X %s -OQv %s 'NET-SNMP-EXTEND-MIB::nsExtendResult.\"%s\"'" % (options.snmp_version, options.snmp_user, options.snmp_seclevel, options.snmp_authproto, options.snmp_authpass, options.snmp_privproto, options.snmp_privpass, options.host, options.extend_name)
	else:
		snmp_request="snmpwalk -v%s -c %s -OQv %s 'NET-SNMP-EXTEND-MIB::nsExtendResult.\"%s\"'" % (options.snmp_version, options.community, options.host, options.extend_name)

	result=commands.getoutput(snmp_request)
	if options.debug:
		debug("snmp request: %s" % (snmp_request))
		debug(result)
	
	if result == noexecstr:
		error("This extend module is not found for this server: %s" %(options.extend_name) )
	if result == timeoutstr:
		error("No response from: %s. Maybe community is not good ?" % (options.host) )
		
	if options.snmp_version == '3':
		snmp_request="snmpwalk -v%s -u %s -l %s -a %s -A %s -x %s -X %s -OQv %s 'NET-SNMP-EXTEND-MIB::nsExtendOutputFull.\"%s\"'" % (options.snmp_version, options.snmp_user, options.snmp_seclevel, options.snmp_authproto, options.snmp_authpass, options.snmp_privproto, options.snmp_privpass, options.host, options.extend_name)
	else:
		snmp_request="snmpwalk -v%s -c %s -OQv %s 'NET-SNMP-EXTEND-MIB::nsExtendOutputFull.\"%s\"'" % (options.snmp_version, options.community, options.host, options.extend_name)

	output=commands.getoutput(snmp_request)
	if options.debug:
		debug("snmp request: %s" % (snmp_request))
		debug(output)
	
	if result == noexecstr:
		error("This extend module is not found for this server: %s" %(options.extend_name) )
	if result == timeoutstr:
		error("No response from: %s. Maybe community is not good ?" % (options.host) )
		
	overall_status = int(result)

	
	add_summary(output)


###################################################
# parse_options()
#   parse comandline options, set default values
#   and arguments, construct help
###################################################
def parse_options():
    help_epilog="""
    
    HOW TO ADD A SNMP EXEC (EXTEND) :
	edit /etc/snmp/snmpd.conf
	add a line like this :
	
	extend yesterday /bin/date --date=yesterday
	(This should output the current date -1 day)
	
	Then restart your snmpd daemon (service snmpd restart)
	
	Call this plugin like this to check this snmp extend :
	%prog --host localhost --snmp-version 2c --community public --extend-name yesterday
	This should output :
	Mon Mar 28 11:12:24 CEST 2011
	(well, you won't get this specific date, but output will be similar...)

    """
	
    class MyParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog
    
    parser = MyParser(usage="usage: %prog [options]", epilog=help_epilog,
            version="%prog 0.5") 

    parser.add_option("-d", "--debug", dest="debug",
            action="store_true", default=False,
            help="Enable debug output")

    parser.add_option("-L", "--output-longoutput", dest="output_longoutput",
            action="store_true", default=False,
            help="Long output format")

    parser.add_option("-p", "--output-perfdata", dest="output_perfdata",
            action="store_true", default=False,
            help="Output performance data")

    parser.add_option("-s", "--output-complete-summary",
            dest="output_complete_summary",
            action="store_true", default=False,
            help="Output complete summary")

    parser.add_option("-v", "--snmp-version", dest="snmp_version",
            default=1,
            help="SNMP Version")

    parser.add_option("-c", "--community", dest="community",
            default="public",
            help="Community string [default: public]")

    parser.add_option("-H", "--host", dest="host",
            default="localhost",
            help="Host [default: localhost]")

    parser.add_option("-e", "--extend-name", dest="extend_name",
            default="ALL",
            help="SNMP extend name [default: ALL]")

    parser.add_option("-t", "--timeout", dest="timeout",
            default=10,
            help="Timeout [default: 10]")
    
    parser.add_option("-u", "--user", dest="snmp_user",
            help="SNMP username (v3 only)")
    
    parser.add_option("-l", "--seclevel", dest="snmp_seclevel",
            help="SNMP Seclevel (noAuthNoPriv|authNoPriv|authPriv, v3 only)")

    parser.add_option("-a", "--authproto", dest="snmp_authproto",
            help="SNMP Authentication protocol (MD5 or SHA, v3 only)")
    
    parser.add_option("-A", "--authpass", dest="snmp_authpass",
            help="SNMP Authentication password (v3 only)")

    parser.add_option("-x", "--privproto", dest="snmp_privproto",
            help="SNMP privacy protocol (DES or AES, v3 only)")

    parser.add_option("-X", "--privpass", dest="snmp_privpass",
            help="SNMP privacy password (v3 only)")
    

    global options
    global args
    (options, args) = parser.parse_args()

###################################################
#				
# error(text, exitcode)	
#	print error text
###################################################
def error(errortext, exit_code=unknown):
	print "* Error: %s" % errortext
	#print_help()
	#:print "* Error: %s" % errortext
	exit(exit_codes[exit_code])

###################################################
#				
# debug(text)	
#	print debug text
###################################################
def debug( debugtext ):
	print	debugtext

###################################################
#				
# add_perfdata(text)	
#	append text to perfdata
###################################################
def add_perfdata(text):
	global perfdata
	perfdata = perfdata + text + " "

###################################################
#				
# add_summary(text)	
#	append text to summary
###################################################
def add_summary(text):
	global summary
	summary = summary + text
	
###################################################
#				
# add_long_output(text)	
#	append text to long output
###################################################
def add_long_output(text):
	global long_output
	long_output = long_output + text

###################################################
#				
# main()	
#	main
###################################################
def main():
	parse_options()

	do_the_main_stuff()

	end()

###################################################
#
# do_the_main_stuff()
#       Exported from main() to get advantages of timeout function
###################################################
@timeout()
def do_the_main_stuff():
	if options.extend_name == 'ALL':
		check_snmp_extend()
	else:
		check_this_snmp_extend()


###################################################
#				
# end()	
#	print the output infos and exit with the correct nagios output code
###################################################
def end():
	global overall_status
	
	if overall_status < 0 or overall_status > 3:
		overall_status = unknown
	
	if options.extend_name == 'ALL':
		message = "%s - ok objects: %s, not ok objects: %s - %s" % (state[overall_status], ok_count, not_ok_count, summary)
		if perfdata != "" and options.output_perfdata:
			message = "%s | %s" % (message, perfdata)
		if long_output != "" and options.output_longoutput:
			message = "%s \n %s" % (message, long_output)
		exit_code = exit_codes[overall_status]
	else:
		message = "%s" % (summary)
		exit_code = overall_status
	print message
	
	exit(exit_code)
	
###################################################
#
# __main__
#	call to main()
###################################################
if __name__ == '__main__':
	main()

