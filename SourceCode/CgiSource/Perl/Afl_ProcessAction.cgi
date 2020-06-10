#!/usr/local/bin/perl -w
use CGI qw/:standard/;

use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

#use strict;

#Begin HTML so errors show up in browser...
#print CGI::header('text/html');
#print "<HTML>\n";

print "Content-type: text/javascript\n\n";

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

my $ProgramName = "Afl_ProcessAction.cgi";

# Determine what libraries to use base on the execution dir...
my $CurrentFilePath = __FILE__;
# Initialize LinkMap Hash variable "Map"...
my %Map = &UtilityFunctions::Load_LinkMap($CurrentFilePath, $DebugUtilityFunctions); 
# Severe Error:  No LinkMap.dat file found -- EXIT --
if($Map{'CONFIG'} eq 'ERROR')
	{
		print "document.write(\"<BR>LinkMap Error.<BR><BR>Contact Site Administrator.<BR>\")\n";
	}
else
	{
		$Map{'PROGRAM_NAME'} = $ProgramName;
	}

my @QueryStringParams;
my %QueryStringHash;

my $SqlStatement = "";

# Load the values passed in into the QueryStringHash...
@QueryStringParams = CGI::param();
%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

$DebugThisAp			= "1" if $QueryStringHash{'test_cgi'} eq "1";
$DebugPrintColorHTML	= "1" if $QueryStringHash{'test_sql'} eq "1";


# this program expects to always receive the ckuid otherwise there is no way to process this aciton...
if($QueryStringHash{'ckuid'})
	{
    	(my $RandomLeft, my $afl_ctl_unique_id, my $site_id, my $afl_account_id, my $RandomRight) = split(/-/, $QueryStringHash{'ckuid'});

		if($DebugThisAp eq "1")
			{
				print "document.write(\"ckuid             = (" . $QueryStringHash{'ckuid'} . ")<BR><BR>\")\n";
				print "document.write(\"Random Left       = (" . $RandomLeft . ")<BR>\")\n";
				print "document.write(\"afl_ctl_unique_id = (" . $afl_ctl_unique_id . ")<BR>\")\n";
				print "document.write(\"site_id           = (" . $site_id . ")<BR>\")\n";
				print "document.write(\"afl_account_id    = (" . $afl_account_id . ")<BR>\")\n";
				print "document.write(\"Random Left       = (" . $RandomRight . ")<BR><BR>\")\n";
			}

		$SqlStatement = "afl_GetPlanActionProcessingInfo \'$afl_ctl_unique_id\'\
														, \'$afl_account_id\'\
														, \'$site_id\'\
														, \'$QueryStringHash{'pluid'}\'\
														"; 

		my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
		$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
		$status = $MSSQL::DBlib::dbh->dbsqlexec();
			
		if($DatabaseFunctions::DatabaseError eq "1025")
			{
				print "document.write(\"<FONT color=\\\"red\\\">ERROR</FONT>: afl_ctl_unique_id (<FONT color=\\\"blue\\\">" . $afl_ctl_unique_id . "</FONT>) not found.<BR>\")\n";
			}
		else
			{
				# Remove the special characters so the string can be printed by JavaScript...
				$SqlStatement =~ s/\'/&quot;/g;
				$SqlStatement =~ s/\n//g;
				$SqlStatement =~ s/\r//g;

				##########################
				# Get ONLY result set...
				##########################
				# dbresults() must be called for each result set...
				$status = $MSSQL::DBlib::dbh->dbresults();
				if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
					{
						my $PlanStoredPorcedure = "";
						if($DebugThisAp eq "1")
							{
								print "document.write(\"<BR>SUCCESS: ($SqlStatement) returned with dbresults status = ($status).<BR>\")\n";
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
											print "document.write(\"<FONT color=\\\"blue\\\">$Key</FONT> <FONT color=\\\"red\\\">$Value</FONT><BR>\")\n";
										}                
									}	

								if($$dataref{stored_proc_name})
									{
										$PlanStoredPorcedure = $$dataref{stored_proc_name} . " \'" . $afl_ctl_unique_id . "\'" . ", \'" . $QueryStringHash{'pluid'} . "\'";
										my $count = 1;
										while($count < 5)
										{
											my $ParmToFind = "cgi_param_" . $count;
											if($$dataref{$ParmToFind})
												{
													if(length($$dataref{$ParmToFind}) > 1)
														{
															$PlanStoredPorcedure = $PlanStoredPorcedure . ", \'" . $QueryStringHash{$$dataref{$ParmToFind}} . "\'";
														}
												}
											$count++;
										}										
									}
							}
						if ($QueryStringHash{'test_sql'} eq "1") 
							{
								$PlanStoredPorcedure = $PlanStoredPorcedure . ", \'" . $QueryStringHash{'test_sql'} . "\'";
							}
						print "document.write(\"SQL = (" . $PlanStoredPorcedure . ")<BR>\")\n" if $DebugThisAp eq "1";
						# Cancel previous database call...
						$status = $MSSQL::DBlib::dbh->dbcancel();
						if($PlanStoredPorcedure !~ m/, \'\',/)
							{
								# Initiate new database call...
								my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, $ProgramName, $PlanStoredPorcedure, $DebugDatabaseFunctions);
								if($return_value eq "1")
									{
										print "document.write(\"SUCCESS:  The action for ckuid = (" . $QueryStringHash{'ckuid'} . ") was processed<BR>\")\n" if $DebugThisAp eq "1";
									}
								else
									{
										print "document.write(\"ERROR:  The action for ckuid = (" . $QueryStringHash{'ckuid'} . ") was NOT processed<BR>\")\n" if $DebugThisAp eq "1";
									}
							}
						else
							{
								print "document.write(\"WARNING:  The action for ckuid = (" . $QueryStringHash{'ckuid'} . ") was NOT processed<BR>Publisher is not set up to process this aciton type.<BR>\")\n" if $DebugThisAp eq "1";
							}

					}# END if($status != FAIL)
				else
					{
						print "document.write(\"<BR>ERROR: $SqlStatement Failed for first result set!<BR>\")\n" if $DebugThisAp eq "1";
						print "document.write(\"<!-- ERROR: $SqlStatement Failed for first result set! -->\")\n";
						$status = $MSSQL::DBlib::dbh->dbcancel();
					}
			}
		}
exit 0;

