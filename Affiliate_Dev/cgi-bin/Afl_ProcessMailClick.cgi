#!/usr/local/bin/perl -w
use CGI qw/:standard/;

use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

#use strict;

# Add directories to perl environment path...
# Smithers
unshift @INC, "D:/Required/INC/";
# Grimes
unshift @INC, "C:/Required/INC/";

require "DatabaseFunctions.pl";
require "CgiFunctions.pl";
require "UtilityFunctions.pl";

my $DebugThisAp			   = "0";
my $DebugCgiFunctions 	   = "0";
my $DebugDatabaseFunctions = "0";
my $DebugUtilityFunctions  = "0";

if($DebugThisAp eq "1"
	or $DebugCgiFunctions eq "1"
	or $DebugDatabaseFunctions eq "1"
	or $DebugUtilityFunctions eq "1"
	)
	{
		print CGI::header('text/html');
		print "<HTML>\n";
	}


my $ProgramName = "ProcessMailClick.cgi";

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

my @QueryStringParams;
my %QueryStringHash;

# Load the values passed in into the QueryStringHash...
@QueryStringParams = CGI::param();
%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);


# Since the url is not kept in tact we must regenerate it...
my $processed_url = $QueryStringHash{'pmc_url'};
while( (my $Key, my $Value) = each(%QueryStringHash) )
{
	if($Key ne "pmc_id" 
		and $Key ne "pmc_respondent" 
		and $Key ne "pmc_url" 
		and $Key ne "pmc_ip_address"
		and $Key ne "pmc_stamp"
		)
	{
		print "<!-- $Key = ($Value) -->\n" if $DebugThisAp eq "1";
		$Value =~ s/ /+/g;
		if ($processed_url =~ m/\?$/) 
			{
				$processed_url = $processed_url . "$Key=$Value";
			}
		else
			{
				$processed_url = $processed_url . "&$Key=$Value";
			}
	}
}       
$processed_url =~ s/\'/%27/g;
$processed_url =~ s/om_//g;

$QueryStringHash{'pmc_respondent'} =~ s/\'/%27/g;

print "<!-- processed_url = ($processed_url) -->\n" if $DebugThisAp eq "1";

my $SqlStatement = "mail_ProcessMailClick \'$QueryStringHash{'pmc_id'}\', \'$QueryStringHash{'pmc_respondent'}\', \'$ENV{REMOTE_ADDR}\',  \'$processed_url\'";     

my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER_MAILING_LIST'}, $Map{'DBPWD_MAILING_LIST'}, $Map{'DBNAME'}, $ProgramName, $SqlStatement, $DebugDatabaseFunctions);

# No matter what the database returns this program should redirect the user to the passed in url...
if($processed_url ne "")
	{
		my $query = new CGI;
		my $referrer_url = $query->referer();

		if($referrer_url !~ m%^http://www.OneMonkey.com%gi
			and $referrer_url !~ m%^http://10.10.10.5:1800%gi
			and $referrer_url !~ m%^http://65.37.145.203%gi
			and $referrer_url ne ""
			)
			{
				print CGI::header('text/html');
				print "<HTML>\n";
				print "<BODY>\n";
				print "<!-- Ofending Referrer URL = ($referrer_url)-->\n";
				print "<SCRIPT LANGUAGE=JavaScript>\n";
				print "<!--\n";
				print "			document.write(\"<H2>This window has an external domain that will cause problems while viewing our pages.<BR>A new window should have been opened.</H2>\")\n";
				print "			window.open(\'$processed_url\')\n";
				print "	// -->\n";
				print "</SCRIPT>\n";

				print "<H3>If a new window did not open please copy and past the link below into your browser's Address Bar:</H3><H4><FONT color=\"red\">$processed_url</FONT><H4>\n";

				print "<NOSCRIPT>\n";
				print "<H3>To avoid this problem in the future please enable JavaScript</H3>\n";
				print "</NOSCRIPT>\n";

				print "</BODY>\n";
				print "</HTML>\n";
			}
		else
			{
				print $query->redirect($processed_url);
			}
	}
else
	{
		# These 2 line need to be romoved for the program to be able to redirect properly...
		#Begin HTML so errors show up in browser...
		print CGI::header('text/html');
		print "<HTML>\n";
		&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to automatically redirect.<BR>Please use this link to continue: <A href=\"$processed_url\">$QueryStringHash{'pmc_url'}</A>\n<!-- SQL: \n($SqlStatement)\n DbError: \nROLLBACK ($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
	}
exit 0;


######### The old way of intercepting DB Errors...
#if($return_value eq "1" and $DatabaseFunctions::DatabaseError eq "0")
#	{
#		my $query = new CGI;
#		print $query->redirect($processed_url);
#	}
#elsif($DatabaseFunctions::DatabaseError eq "1016" or $DatabaseFunctions::DatabaseError eq "1021")
#	{
#		# These 2 line need to be romoved for the program to be able to redirect properly...
#		#Begin HTML so errors show up in browser...
#		print CGI::header('text/html');
#		print "<HTML>\n";
#		&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to process click.<BR>Please use this link to continue: <A href=\"$QueryStringHash{'om_url'}\">$QueryStringHash{'om_url'}</A>\n<!-- SQL: \n($SqlStatement)\n DbError: \nROLLBACK ($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
#	}
#else
#	{
#		# These 2 line need to be romoved for the program to be able to redirect properly...
#		#Begin HTML so errors show up in browser...
#		print CGI::header('text/html');
#		print "<HTML>\n";
#		&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to process click.<BR>Please use this link to continue: <A href=\"$QueryStringHash{'om_url'}\">$QueryStringHash{'om_url'}</A>\n<!-- SQL: \n($SqlStatement)\n DbError: \nROLLBACK ($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
#	}


#		print "<SCRIPT LANGUAGE=JavaScript>\n";
#		print "<!--\n";
#		print "	document.write(window.location.href + \"<BR>\") \n";
#		print "	document.write(document.referrer  + \"<BR>\") \n";
#		print "	// Get URL...\n";
#		print "	var oldURL = new String()\n";
#		print "\n";
#		print "	oldURL = document.referrer\n";
#		print "// Hotmail\n";
#		print "//oldURL = \"http://216.33.240.250/cgi-bin/linkrd?_lang=EN&lah=958e1b64b226d6fb3cb27ea5e7dabd17&lat=1038048231&hm___action=http%3a%2f%2f65%2e37%2e145%2e203%2fcgi%2dbin%2fProcessMailClick%2ecgi%3fpmc_url%3dhttp%3a%2f%2fwww%2eonemonkey%2ecom%2fJS_Test_File%2ehtml%26pmc_id%3d459%26pmc_respondent%3djatlast%40hotmail%2ecom\"\n";
#		print "// Yahoo Mail\n";
#		print "//oldURL = \"http://us.f208.mail.yahoo.com/ym/ShowLetter?MsgId=6751_389351_24421_1152_4718_0_346&YY=76532&inc=25&order=down&sort=date&pos=0&view=a&head=b&box=Inbox\"\n";
#		print "\n";
#		print "	var referrer_root = new String();\n";
#		print "	referrer_root = oldURL.substring(oldURL.indexOf(\"http://\", 0) + 7\n";
#		print "									, oldURL.indexOf(\"/\", 7)\n";
#		print "									)\n";
#		print "\n";
#		print "	document.write(\"<BR>Root = (\" + referrer_root + \")<BR>\")\n";
#		print "\n";
#		print "	if (referrer_root == \"www.onemonkey.com\" \n";
#		print "		|| referrer_root == \"10.10.10.5:1800\" \n";
#		print "		|| referrer_root == \"65.37.145.203\"\n";
#		print "		)\n";
#		print "		{\n";
#		print "			document.write(\"<BR>Referrer Root = (\" + referrer_root + \")<BR>\")\n";
#		print "		}\n";
#		print "	else\n";
#		print "		{\n";
#		print "			document.write(\"<BR>Needs Redirect = (\" + referrer_root + \")<BR>\")\n";
#		print "			//window.open(\'$processed_url\')\n";
#		print "		}\n";
#		print "\n";
#		print "	// -->\n";
#		print "</SCRIPT>\n";
#
#
#
#
#
#
#
#
#
