#!/usr/local/bin/perl -w

# For CGI functionality
use CGI qw/:standard/;
# For Automated web access
use LWP::UserAgent;
use HTTP::Request;
use HTTP::Response;

use strict;

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

my $ProgramName = "Redirect.cgi";

print CGI::header('text/html');
print "<HTML>\n";

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

# Load the values passed in into the QueryStringHash...
my @QueryStringParams = CGI::param();
my %QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

# Since the url is not kept in tact we must regenerate it...
if($QueryStringHash{'turl'})
	{
		print "<HEAD>\n";
		print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
		print "    <!--\n";
		print "         var Then = new Date()\n";
		print "         Then.setTime(Then.getTime() + 60 * 60 * 1000)\n";

		if($QueryStringHash{'user_name'})
			{
				print "         document.cookie=\"cookie_name=$QueryStringHash{'user_name'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";

			}
		if($QueryStringHash{'password'})
			{
				print "         document.cookie=\"cookie_password=$QueryStringHash{'password'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";

			}

		if($QueryStringHash{'to'} gt "0")
			{
				# 1000 milliseconds x 60 seconds x 60 minutes x 24 hours x # days
				print "         Then.setTime(Then.getTime() + 1000 * 60 * 60 * 24 * $QueryStringHash{'to'})\n";
				print "         document.cookie=\"ckuid=$QueryStringHash{'ckuid'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";
			}
		else
			{
				# don't expire for 2 years...
				print "         Then.setTime(Then.getTime() + 1000 * 60 * 60 * 24 * 800)\n";
				print "         document.cookie=\"ckuid=$QueryStringHash{'ckuid'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";
			}

		print "			window.location = \"$QueryStringHash{'turl'}\"\n";

		print "    //-->\n";
		print " </SCRIPT> \n";
		print "Redirect URL = ($QueryStringHash{'turl'})\n" if $DebugThisAp eq "1";
		print "</HEAD>\n";
	}
else
	{
		# These 2 line need to be romoved for the program to be able to redirect properly...
		#Begin HTML so errors show up in browser...
		&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to automatically redirect.<BR>Please use the back button below and try again.\n<BR>", $DebugUtilityFunctions, %Map);		
	}
exit 0;
