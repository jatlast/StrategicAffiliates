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


print CGI::header('text/html');
print "<HTML>\n";
#print "Content-type: text/javascript\n\n";

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

my $opened = open (NEWFILE, "> C:/Temp/temp.txt");		
if ($opened)
	{
	if($QueryStringHash{'stamp'})
		{
			print NEWFILE "Stamp = (" . $QueryStringHash{'stamp'} . ")\n";
			#print "Stamp = (" . $QueryStringHash{'stamp'} . ")";

		}
	else
		{
			print NEWFILE "No Stamp\n";
		}
		close (NEWFILE);
	}

#my $query = new CGI;
#print $query->header(-cookie=>'cookie=value');


exit 0;
