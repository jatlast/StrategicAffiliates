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

my $ProgramName = "Afl_CreateLogin.cgi";

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
	}

my $afl_unique_id	= "";
my $return_value	= "";

# declare global variables...
my @QueryStringParams;
my %QueryStringHash;
# Load the values passed in into the QueryStringHash...
@QueryStringParams = CGI::param();
%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

# Generate the unique email verification code...
(my $sec, my $min, my $hour, my $mday, my $mon, my $year, my $wday, my $yday, my $isdst) = localtime(time);
# use parsed date to create unique verification code...
# verification code has the folling format m[m]-d[d]-yyyy-h[h]-m[m]-s[s]
my $UniqueVerificationCode = ($mon+1) . $mday . ($year+1900) . "-" . $hour . $min . $sec;

##########################################################
# Remove single quotes for SQL statement...
##########################################################
# Remove single quotes from description field...
if($QueryStringHash{'site_description'} =~ m/\'/g)
{
	$QueryStringHash{'site_description'} =~ s/\'/\'\'/gis;
}
# Remove single quotes from site_name field...
if($QueryStringHash{'site_name'} =~ m/\'/g)
{
	$QueryStringHash{'site_name'} =~ s/\'/\'\'/gis;
}
# Remove single quotes from password_answer field...
if($QueryStringHash{'password_answer'} =~ m/\'/g)
{
	$QueryStringHash{'password_answer'} =~ s/\'/\'\'/gis;
}

# Remove single quotes from organizaiton_name field...
if($QueryStringHash{'organizaiton_name'} =~ m/\'/g)
{
	$QueryStringHash{'organizaiton_name'} =~ s/\'/\'\'/gis;
}

# Remove single quotes from pay_to_the_order_of field...
if($QueryStringHash{'pay_to_the_order_of'} =~ m/\'/g)
{
	$QueryStringHash{'pay_to_the_order_of'} =~ s/\'/\'\'/gis;
}

# Remove single quotes from bank_name field...
if($QueryStringHash{'bank_name'} =~ m/\'/g)
{
	$QueryStringHash{'bank_name'} =~ s/\'/\'\'/gis;
}
##########################################################

if(!$QueryStringHash{'receive_promo_mail'})
{
	$QueryStringHash{'receive_promo_mail'} = 0;
}

if(!$QueryStringHash{'accepted_terms'})
{
	$QueryStringHash{'accepted_terms'} = 0;
}

# Update login_info table to change the user's email address...
my $SqlStatement = "afl_CreateNewAffiliateProfile \'$QueryStringHash{'site_name'}\'\
												, \'$QueryStringHash{'site_url'}\'\
												, \'$QueryStringHash{'site_description'}\'\
												, $QueryStringHash{'primary_category'}\
												, \'$QueryStringHash{'name'}\'\
												, \'$QueryStringHash{'email'}\'\
												, \'$QueryStringHash{'password'}\'\
												, \'$QueryStringHash{'password_question'}\'\
												, \'$QueryStringHash{'password_answer'}\'\
												, \'$UniqueVerificationCode\'\
												, \'$QueryStringHash{'address_1'}\'\
												, \'$QueryStringHash{'address_2'}\'\
												, \'$QueryStringHash{'city'}\'\
												, $QueryStringHash{'state'}\
												, \'$QueryStringHash{'zip'}\'\
												, $QueryStringHash{'country'}\
												, \'$QueryStringHash{'phone'}\'\
												, \'$QueryStringHash{'fax'}\'\
												, \'$QueryStringHash{'social_security_or_tax_id'}\'\
												, $QueryStringHash{'payment_method'}\
												, $QueryStringHash{'direct_deposit_country'}\
												, \'$QueryStringHash{'bank_name'}\'\
												, \'$QueryStringHash{'account_type'}\'\
												, \'$QueryStringHash{'name_on_bank_account'}\'\
												, \'$QueryStringHash{'bank_account_number'}\'\
												, \'$QueryStringHash{'bank_routing_number'}\'\
												, \'$QueryStringHash{'pay_to_the_order_of'}\'\
												, $QueryStringHash{'receive_promo_mail'}\
												, $QueryStringHash{'accepted_terms'}\
												"; 

my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
$status = $MSSQL::DBlib::dbh->dbsqlexec();
	
if($DatabaseFunctions::DatabaseError eq "1015")
	{
		&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "Email address (<FONT COLOR=\"#8B0000\">" . $QueryStringHash{'email'} . "</FONT>) is not unique.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
	}
elsif($DatabaseFunctions::DatabaseError eq "1016")
	{
		&UtilityFunctions::Afl_Print_Framed_Error("", "Database Rollback Error.<BR><BR>\n\nPlease try again.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
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
						print "<!-- DbError: ($DatabaseFunctions::DatabaseError) -->\n";
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
								
								$afl_unique_id = $$dataref{afl_unique_id};

								if($DebugThisAp eq "1")
									{
										print "<!-- afl_unique_id = ($afl_unique_id) -->\n";
									}	
							}

						print "<!-- Created Host ($afl_unique_id) -->\n" if $DebugThisAp eq "1";
						# Set login information cookies...
						print "<HEAD>\n";
						print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
						print "    <!--\n";
						print "            var Then = new Date()\n";
						print "            Then.setTime(Then.getTime() + 60 * 60 * 1000)\n";
						print "            document.cookie=\"afl_cookie_id=$afl_unique_id; expires=\" + Then.toGMTString() + \"; path=/\"\n";
						print "            document.cookie=\"afl_cookie_email=$QueryStringHash{'email'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";
						print "            document.cookie=\"afl_cookie_password=$QueryStringHash{'password'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";
						print "    //-->\n";
						print " </SCRIPT> \n";
						print "</HEAD>\n";

						# Send User Email Verification Code...
						$return_value = &SendMailFunctions::Email_The_Verification_Code_To_User($QueryStringHash{'email'}, $QueryStringHash{'password'}, $QueryStringHash{'email'}, $UniqueVerificationCode, $DebugThisAp, %Map);
						if($return_value == 1)
							{
								print "<!-- Sent ($QueryStringHash{'email'}) Verification Code Mail -->\n" if $DebugThisAp eq "1";
								print "			<FONT face=\"Helvetica,Arial\">Sent verification mail to <FONT color=\"blue\">$QueryStringHash{'email'}</FONT> successfully.</FONT><BR>\n" if $DebugThisAp eq "1";
								# Send Host Welcome Mail...
								$return_value = &SendMailFunctions::Afl_Email_The_Publisher_Welcome_Message_To_User($afl_unique_id, $QueryStringHash{'email'}, $QueryStringHash{'password'}, $UniqueVerificationCode, $DebugThisAp, %Map);
								if($return_value == 1)
									{
										print "<!-- Sent ($QueryStringHash{'email'}) Host Welcome Mail -->\n" if $DebugThisAp eq "1";
										print "			<FONT face=\"Helvetica,Arial\">Sent host welcome mail to <FONT color=\"blue\">$QueryStringHash{'email'}</FONT> successfully.</FONT><BR>\n" if $DebugThisAp eq "1";
									}
								else
									{
										print "<!-- Unable To Send Mail To ($QueryStringHash{'email'})-->\n" if $DebugThisAp eq "1";
										print "			<FONT face=\"Helvetica,Arial\">Unable to send host welcome mail to <FONT color=\"blue\">$QueryStringHash{'email'}</FONT>.</FONT><BR>\n" if $DebugThisAp eq "1";
									}
							}
						else
							{
								print "<!-- Unable To Send Mail To ($QueryStringHash{'email'})-->\n" if $DebugThisAp eq "1";
								print "			<FONT face=\"Helvetica,Arial\">Unable to send verification mail to <FONT color=\"blue\">$QueryStringHash{'email'}</FONT>.</FONT><BR>\n" if $DebugThisAp eq "1";
							}

						print "<SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
						print "	  <!--\n";
						print "		window.location = \"Afl_AccountDetails.cgi\"\n";
						print "  //-->\n";
						print "</SCRIPT>\n";
					}# END else (No db error) 
				}# END if($status != FAIL)
		else
			{
				print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
				&UtilityFunctions::Afl_Print_Framed_Error("", "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
			}
	}

#End HTML...
print "</HTML>\n";
exit 0;
