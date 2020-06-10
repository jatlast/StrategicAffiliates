#!/usr/local/bin/perl -w

# For CGI functionality
use CGI qw/:standard/;
# For database access
use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

use strict;

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

my $DebugPrintColorHTML	   = "0";


my $ProgramName = "Afl_ProcessClick.cgi";

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

my @QueryStringParams;
my %QueryStringHash;

# make sure the query string hash contains the variable names required...
$QueryStringHash{'ctluid'}	= "0";		# afl_ctl_unique_id		"click_through_log unique_id"
$QueryStringHash{'lnum'}	= "0";		# link_clicked_number	Only really used for Embeded HTML

# Load the values passed in into the QueryStringHash...
@QueryStringParams = CGI::param();
%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

my $SqlStatement = "afl_ProcessClick \'$QueryStringHash{'ctluid'}\', \'$QueryStringHash{'lnum'}\', \'$ENV{REMOTE_ADDR}\'";     

my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
$status = $MSSQL::DBlib::dbh->dbsqlexec();
	
if($DatabaseFunctions::DatabaseError eq "1016")
	{
		#Rollback error
		# These 2 line need to be romoved for the program to be able to redirect properly...
		#Begin HTML so errors show up in browser...
		print CGI::header('text/html');
		print "<HTML>\n";
		&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to automatically redirect.<BR>Please use the Back Button below to try again.\n<!-- SQL: \n($SqlStatement)\n DbError: ROLLBACK ($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
	}
elsif($DatabaseFunctions::DatabaseError eq "1021")
	{
		# unable to process click ERROR
		# These 2 line need to be romoved for the program to be able to redirect properly...
		#Begin HTML so errors show up in browser...
		print CGI::header('text/html');
		print "<HTML>\n";
		&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to automatically redirect.<BR>Please use the Back Button below to try again.\n<!-- SQL: \n($SqlStatement)\n DbError: ($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
	}
else
	{
		##########################
		# Get ONLY result set...
		##########################
		# dbresults() must be called for each result set...
		$status = $MSSQL::DBlib::dbh->dbresults();
		if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
			{
				if($DebugThisAp eq "1")
					{
						print "<BR>SUCCESS: ($SqlStatement) returned with dbresults status = ($status).<BR>\n";
					}
				my %dataref = ("jason" => "baumbach");
				my $dataref = \%dataref;
				# Prevent infinite loop...
				while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
					{
						# Since there is no global DB error check get 
						# all database fields returned by the query...
							
						if($DebugPrintColorHTML eq "1")
							{
								while( (my $Key, my $Value) = each(%$dataref) )
								{
									print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n";
								}                
							}	

						# if the database does not return a target url this program will be unable to redirect the user.
						my $redirect_url = "";
						if($$dataref{redirect_program_url} =~ m/^http/g)
							{
								# Start with the affiliate's redirect url...
								$redirect_url = $$dataref{redirect_program_url};

								if($$dataref{target_url} =~ m/^http/g)
									{
										# since there is a target_url in the DB this means it is an ad and needs to go where the ad points...
										$redirect_url = $redirect_url . "?turl=" . $$dataref{target_url} . "&";
									}
								elsif($QueryStringHash{'turl'})
									{
										# since there was a 'turl' passed in as a query param it is a dynamic html and needs to go here the GET points...
										$redirect_url = $redirect_url . "?turl=" . $QueryStringHash{'turl'} . "&";
									}
								else
									{
										# since there is no target just append the '?' for the rest of the params...
										$redirect_url = $redirect_url . "?";
									}
							}
						else
							{
								if($$dataref{target_url} =~ m/^http/g)
									{
										# since there is a target_url in the DB this means it is an ad and needs to go where the ad points...
										$redirect_url = $$dataref{target_url} . "?";
									}
								elsif($QueryStringHash{'turl'})
									{
										# since there was a 'turl' passed in as a query param it is a dynamic html and needs to go here the GET points...
										$redirect_url = $QueryStringHash{'turl'} . "?";
									}
								else
									{
										&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to automatically redirect.<BR>Please use the Back Button below to try again.\n<!-- URL: \n($redirect_url)\n DbError: \n -->\n<BR>", $DebugUtilityFunctions, %Map);		
									}
							}

							my $randum_number_1 = int(rand 10000);
							my $randum_number_2 = int(rand 10000);
							# Create an ctlid - click_through_log_id composite ( random-ctluid-sid-acid-random )
							$redirect_url = $redirect_url . "ckuid=" . $randum_number_1 . "-" . $QueryStringHash{'ctluid'} . "-" . $$dataref{site_id} . "-" . $$dataref{afl_account_id}. "-" . $randum_number_2;

							# Cookie Time out in days...
							if($$dataref{referral_period_in_days})
								{
									$redirect_url = $redirect_url . "&to=" . $$dataref{referral_period_in_days};
								}
							else
								{
									# Time Out of "0" means never time out so we will set it to expire in a little over 2 years...
									$redirect_url = $redirect_url . "&to=800";
								}

							# append all unknown cgi parameters to the end of the query string to pass them to the affiliates redirect script...
							while( (my $Value, my $Key) = sort each(%QueryStringHash) )
								{
									if(
											$Key ne "ctluid"
										and $Key ne "acid"
										and $Key ne "sid"
										and $Key ne "lnum"
										and $Key ne "turl"
									  )
										{
										   print "<!-- $Key = ($Value) -->\n" if $DebugThisAp eq "1";
										   $redirect_url = $redirect_url . "&" . $Key . "=" . $Value;
										}
								}       

						if($redirect_url =~ m/http/g)
							{
								print "<HEAD>\n";
								print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
								print " <!--\n";
								print "  window.location = \"$redirect_url\"\n";
								print " //-->\n";
								print " </SCRIPT> \n";
								print " <NOSCRIPT>\n";
								print "  Unable to automatically redirect because JavaScript is disabled.<BR>\n";
								print "  Click this link to proceed to <A href=\"$redirect_url\">$$dataref{target_url}</A>\n";
								print " <NOSCRIPT> \n";
								print "</HEAD>\n";
								print "Redirect URL = ($redirect_url)\n" if $DebugThisAp eq "1";
							}
						else
							{
								# These 2 line need to be romoved for the program to be able to redirect properly...
								#Begin HTML so errors show up in browser...
								&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to automatically redirect.<BR>Please use the Back Button below to try again.\n<!-- URL: \n($redirect_url)\n DbError: \n -->\n<BR>", $DebugUtilityFunctions, %Map);		
							}
					}
			}# END if($status != FAIL)
		else
			{
				$status = $MSSQL::DBlib::dbh->dbcancel();
				&UtilityFunctions::Adv_Print_Framed_Error("", "Unable to automatically redirect.<BR>Please use the Back Button below to try again.\n<!-- SQL: \n($SqlStatement)\n DbError: \n -->\n<BR>", $DebugUtilityFunctions, %Map);		
			}
	}

exit 0;
