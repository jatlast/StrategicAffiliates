#!/usr/local/bin/perl -w

# For CGI functionality
use CGI qw/:standard/;
#use CGI::Cookie;
# For Automated web access
use LWP::UserAgent;
use HTTP::Request;
use HTTP::Response;

#use strict;

# Add directories to perl environment path...
# Smithers
unshift @INC, "D:/Required/INC/";
# Grimes
unshift @INC, "C:/Required/INC/";

require "CgiFunctions.pl";
require "UtilityFunctions.pl";

my $DebugThisAp			   = "0";
my $DebugCgiFunctions 	   = "0";
my $DebugUtilityFunctions  = "0";

my $ProgramName = "Stamp.cgi";


#print CGI::header('text/html');
#print "<HTML>\n";
print "Content-type: text/javascript\n\n";

# Determine what libraries to use base on the execution dir...
my $CurrentFilePath = __FILE__;
# Initialize LinkMap Hash variable "Map"...
my %Map = &UtilityFunctions::Load_LinkMap($CurrentFilePath, $DebugUtilityFunctions); 
# Severe Error:  No LinkMap.dat file found -- EXIT --
if($Map{'CONFIG'} eq 'ERROR')
	{
		&UtilityFunctions::Print_Error("LinkMap Error.<BR><BR>Contact Site Administrator.", $DebugUtilityFunctions, %Map);
	}
else
	{
		$Map{'PROGRAM_NAME'} = $ProgramName;
	}

	print "document.write(\"<script language=\\\"javascript\\\">\")\n";
	print "document.write(\"function getArgs() {\")\n";
	print "document.write(\"	var args = new Object();\")\n";
#	print "document.write(\"	// Get Query String\")\n";
	print "document.write(\"	var query = location.search.substring(1);\")\n";
#	print "document.write(\"	// Split query at the comma\")\n";
	print "document.write(\"	var pairs = query.split(\\\"&\\\");\")\n";
#	print "document.write(\"	// Begin loop through the querystring\")\n";
	print "document.write(\"	for(var i = 0; i < pairs.length; i++) {\")\n";
#	print "document.write(\"		// Look for name=value\")\n";
	print "document.write(\"		var pos = pairs[i].indexOf('='); \")\n";
#	print "document.write(\"		// if not found, skip to next\")\n";
	print "document.write(\"		if (pos == -1) continue; \")\n";
#	print "document.write(\"		// Extract the name\")\n";
	print "document.write(\"		var argname = pairs[i].substring(0,pos); \")\n";
	print "document.write(\"		\")\n";
#	print "document.write(\"		// Extract the value\")\n";
	print "document.write(\"		var value = pairs[i].substring(pos+1); \")\n";
#	print "document.write(\"		// Store as a property\")\n";
	print "document.write(\"		args[argname] = unescape(value); \")\n";
	print "document.write(\"	}\")\n";
	print "document.write(\"	return args;\")\n";
	print "document.write(\"}\")\n";


	print "document.write(\"var args = getArgs();\")\n";
	# Start -- if the "ckuid" exists in the url set the cookie...
	print "document.write(\"if (args.ckuid){\")\n";

	print "document.write(\"var ckuid_value = args.ckuid;\")\n";
	print "document.write(\"var cookie_time_out = args.to;\")\n";

	# debugging alert statement with the ckuid value passed in...
#	print "document.write(\"alert(ckuid_value);\")\n";

	print "document.write(\"if (cookie_time_out > 0){\")\n";
	print "document.write(\"  var Then = new Date();\")\n";
	print "document.write(\"  Then.setTime(Then.getTime() + 60 * 60 * 1000 * 24 * cookie_time_out);\")\n";
	print "document.write(\"  document.cookie=\\\"ckuid=\\\" + ckuid_value + \\\"; expires=\\\" + Then.toGMTString() + \\\"; path=/\\\";\")\n";
	print "document.write(\"}\")\n";
	print "document.write(\"else{\")\n";# don't expire for 2 years...
	print "document.write(\"  Then.setTime(Then.getTime() + 60 * 60 * 1000 * 24 * 800);\")\n";
	print "document.write(\"  document.cookie=\\\"ckuid=\\\" + ckuid_value + \\\"; expires=\\\" + Then.toGMTString() + \\\"; path=/\\\";\")\n";
	print "document.write(\"}\")\n";

	# End -- if the "ckuid" exists in the url set the cookie...
	print "document.write(\"}\")\n";

#	print "document.write(\"document.write(\\\"<IMG src=$Map{'AFL_CGIBIN'}/GetStamp.cgi?stamp=\\\" + ckuid + \\\" width=1 height=1 border=0>\\\");\")\n";
	print "document.write(\"</script>\")\n";

exit 0;

if(0)
{
	print "document.write(\"<script language=\\\"javascript\\\">\")\n";
	print "document.write(\"function getArgs() {\")\n";
	print "document.write(\"	var args = new Object();\")\n";
#	print "document.write(\"	// Get Query String\")\n";
	print "document.write(\"	var query = location.search.substring(1);\")\n";
#	print "document.write(\"	// Split query at the comma\")\n";
	print "document.write(\"	var pairs = query.split(\\\"&\\\");\")\n";
#	print "document.write(\"	// Begin loop through the querystring\")\n";
	print "document.write(\"	for(var i = 0; i < pairs.length; i++) {\")\n";
#	print "document.write(\"		// Look for name=value\")\n";
	print "document.write(\"		var pos = pairs[i].indexOf('='); \")\n";
#	print "document.write(\"		// if not found, skip to next\")\n";
	print "document.write(\"		if (pos == -1) continue; \")\n";
#	print "document.write(\"		// Extract the name\")\n";
	print "document.write(\"		var argname = pairs[i].substring(0,pos); \")\n";
	print "document.write(\"		\")\n";
#	print "document.write(\"		// Extract the value\")\n";
	print "document.write(\"		var value = pairs[i].substring(pos+1); \")\n";
#	print "document.write(\"		// Store as a property\")\n";
	print "document.write(\"		args[argname] = unescape(value); \")\n";
	print "document.write(\"	}\")\n";
	print "document.write(\"	return args;\")\n";
	print "document.write(\"}\")\n";


	print "document.write(\"var args = getArgs();\")\n";
	# Start -- if the "ckuid" exists in the url set the cookie...
	print "document.write(\"if (args.ckuid){\")\n";

	print "document.write(\"var ckuid_value = args.ckuid;\")\n";
	print "document.write(\"var ckuid;\")\n";

	# debugging alert statement with the ckuid value passed in...
#	print "document.write(\"alert(ckuid_value);\")\n";

	print "document.write(\"if (get_cookie('ckuid')!=''){\")\n";
	print "document.write(\"ckuid = get_cookie('ckuid');\")\n";
	print "document.write(\"}\")\n";
	print "document.write(\"else{\")\n";
	print "document.write(\"var Then = new Date();\")\n";
	print "document.write(\"Then.setTime(Then.getTime() + 60 * 60 * 1000);\")\n";
#	print "document.write(\"document.cookie=\\\"ckuid=$random_num; expires=\\\" + Then.toGMTString() + \\\"; path=/\\\";\")\n";
	print "document.write(\"document.cookie=\\\"ckuid=\\\" + ckuid_value + \\\"; expires=\\\" + Then.toGMTString() + \\\"; path=/\\\";\")\n";
	print "document.write(\"}\")\n";

	print "document.write(\"if (get_cookie('ckuid')!=''){\")\n";
	print "document.write(\"ckuid = get_cookie('ckuid');\")\n";
	print "document.write(\"}\")\n";
	print "document.write(\"else{\")\n";
	print "document.write(\"alert(\\\"Unable to set cookie\\\");\")\n";
	print "document.write(\"}\")\n";

	print "document.write(\"function get_cookie(Name) {\")\n";
	print "document.write(\"  var search = Name + \\\"=\\\";\")\n";
	print "document.write(\"  var returnvalue = \\\"\\\";\")\n";
	print "document.write(\"  if (document.cookie.length > 0) {\")\n";
	print "document.write(\"    offset = document.cookie.indexOf(search);\")\n";
	print "document.write(\"    if (offset != -1) {\")\n";
	print "document.write(\"      offset += search.length;\")\n";
#	print "document.write(\"      // set index of beginning of value\")\n";
	print "document.write(\"      end = document.cookie.indexOf(\\\";\\\", offset);\")\n";
#	print "document.write(\"      // set index of end of cookie value\")\n";
	print "document.write(\"      if (end == -1)\")\n";
	print "document.write(\"         end = document.cookie.length;\")\n";
	print "document.write(\"      returnvalue=unescape(document.cookie.substring(offset, end));\")\n";
	print "document.write(\"      }\")\n";
	print "document.write(\"   }\")\n";
	print "document.write(\"  return returnvalue;\")\n";
	print "document.write(\"}\")\n";

	# End -- if the "ckuid" exists in the url set the cookie...
	print "document.write(\"}\")\n";

#	print "document.write(\"document.write(\\\"<IMG src=$Map{'AFL_CGIBIN'}/GetStamp.cgi?stamp=\\\" + ckuid + \\\" width=1 height=1 border=0>\\\");\")\n";
	print "document.write(\"</script>\")\n";
}
