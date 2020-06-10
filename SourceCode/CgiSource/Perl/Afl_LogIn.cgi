#!/usr/local/bin/perl -w

use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

#use strict;
use CGI qw/:standard/;

# Add directories to perl environment path...
# Smithers
unshift @INC, "D:/Required/INC/";
# Grimes
unshift @INC, "C:/Required/INC/";

require "DatabaseFunctions.pl";
require "CgiFunctions.pl";
require "SendMailFunctions.pl";
require "UtilityFunctions.pl";

my $DebugThisAp			   = "1";
my $DebugCgiFunctions 	   = "1";
my $DebugDatabaseFunctions = "1";
my $DebugUtilityFunctions  = "1";
my $DebugMailSendFunctions = "1";

my $ProgramName = "Afl_Login.cgi";

my $count = 0;

#Begin HTML so errors show up in browser...
print CGI::header('text/html');
print "<HTML>\n";

# Determine what libraries to use base on the execution dir...
my $CurrentFilePath = __FILE__;
# Initialize LinkMap Hash variable "Map"...
my %Map = &UtilityFunctions::Load_LinkMap($CurrentFilePath, 1); 

# Severe Error:  No LinkMap.dat file found -- EXIT --
if($Map{'CONFIG'} eq 'ERROR')
	{
		&UtilityFunctions::Print_Error("LinkMap Error.<BR><BR>Contact Site Administrator.", $DebugUtilityFunctions, %Map);
	}
else
	{
		$Map{'PROGRAM_NAME'} = $ProgramName;
		print "<!-- $Map{'CONFIG'} -->\n" if $DebugThisAp eq "1";

		# declare global variables...
		my @QueryStringParams;
		my %QueryStringHash;
		# Load the values passed in into the QueryStringHash...
		@QueryStringParams = CGI::param();
		%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

		if ($QueryStringHash{'submit'} eq "Login")
			{
				my $afl_account_id	= "";
				my $password		= "";
				my $email			= "";
				
				my $SqlStatement = "afl_LogIn \'$QueryStringHash{'email'}\', \'$QueryStringHash{'password'}\'"; 
				my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
				$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
				$status = $MSSQL::DBlib::dbh->dbsqlexec();
					
				if($DatabaseFunctions::DatabaseError eq "1000" or $DatabaseFunctions::DatabaseError eq "1001")
					{
						&UtilityFunctions::Afl_Print_Framed_Error($QueryStringHash{'email'}, "Email ($QueryStringHash{'email'}) and password did not match.<BR><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);		
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
										print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
									}
								my %dataref = ("jason" => "baumbach");
								my $dataref = \%dataref;
								# If in debug mode, print information...
								if($DebugThisAp == 1)
									{
										print "<!-- SQL: $SqlStatement -->\n";
									}
								# Check for global DB error...
								if($DatabaseFunctions::DatabaseError eq "1")
									{
										print "ERROR: ($SqlStatement) Failed!<BR>\n";
									}
								else
									{
										# Prevent infinite loop...
										while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
											{
												# Since there is no global DB error check get 
												# all database fields returned by the query...
													
												$afl_account_id	= $$dataref{afl_account_id};
												$password		= $$dataref{password};
												$email			= $$dataref{email};

												if($DebugThisAp eq "1")
													{
														print "<!-- afl_account_id = ($afl_account_id) -->\n";
														print "<!-- password       = ($password) -->\n";
														print "<!-- email          = ($email) -->\n";
													}

												# Update Cookie info...
												print "<HEAD>\n";
												print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
												print "    <!--\n";
												
												# Delete Existing Cookies...
												print "		if (document.cookie != \"\") \n";
												print "		{\n";
												print "		    expireDate = new Date;\n";
												print "		    expireDate.setDate(expireDate.getDate()-2);\n";
												print "			                          \n";
												print "		    Cookie1 = document.cookie.split(\";\");\n";
												print "		    for (i=0; i<Cookie1.length; i++) \n";
												print "		   {\n";
												print "		       cookieName = Cookie1[i].split(\"=\")[0];\n";
												print "		       document.cookie = cookieName + \"=; expires=\" + expireDate.toGMTString() + \"; path=/\";\n";
												print "		   }\n";
												print "		}\n";
												
												# Create New Cookies...
												print "            var Then = new Date()\n";
												print "            Then.setTime(Then.getTime() + 60 * 60 * 1000)\n";
												print "            document.cookie=\"afl_cookie_id=$afl_account_id; expires=\" + Then.toGMTString() + \"; path=/\"\n";
												print "            document.cookie=\"afl_cookie_password=$password; expires=\" + Then.toGMTString() + \"; path=/\"\n";
												print "            document.cookie=\"afl_cookie_email=$email; expires=\" + Then.toGMTString() + \"; path=/\"\n";

												print "		window.location = \"Afl_AccountDetails.cgi\"\n";

												print "    //-->\n";
												print " </SCRIPT> \n";
												print "</HEAD>\n";
												
											}
									}# END else (No db error) 
							}# END if($status != FAIL)
						else
							{
								print "ERROR: $SqlStatement Failed for first result set!\n";
								$status = $MSSQL::DBlib::dbh->dbcancel();
							}
					}
			}
		else
			{
				&UtilityFunctions::Afl_Print_Framed_Error($QueryStringHash{'email'}, "Improperly formed URL.  The url is missing \";submit=\".\n<!-- ERROR: submit = ($QueryStringHash{'submit'}) --><BR><BR>\n\nPlease try again.<BR><BR>", $DebugUtilityFunctions, %Map);		
			}
	}

#End HTML...
print "</HTML>\n";
exit 0;
