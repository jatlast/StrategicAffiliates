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

my $ProgramName = "Afl_Home.cgi";

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

# Since the user is not using the link supplied check the cookies for user session authentication...
my $afl_cookie_id		= &CgiFunctions::Get_Cookie_Value("afl_cookie_id"		, $DebugCgiFunctions);
my $afl_cookie_email	= &CgiFunctions::Get_Cookie_Value("afl_cookie_email"	, $DebugCgiFunctions);
my $afl_cookie_password	= &CgiFunctions::Get_Cookie_Value("afl_cookie_password"	, $DebugCgiFunctions);


if ($afl_cookie_id eq "" or $afl_cookie_password eq "") 
	{
		# Die if the user is not logged in...
		&UtilityFunctions::Afl_Print_Framed_Error("", "You must be logged in to view this page.", $DebugUtilityFunctions, %Map);
	}
else
	{

		my $affiliate_of			= "";
		my $program_type			= "";
		my $password				= "";
		my $email					= "";
		my $creation_date			= "";
		my $last_login				= "";
		my $email_verification_code = "";
		my $is_email_verified		= "";
		my $receive_promo_mail		= "";
		my $password_question		= "";
		my $password_answer			= "";
		my $web_site_name			= "";
		my $web_site_url			= "";
		my $web_site_description	= "";
		my $web_site_topic			= "";
		my $first_name				= "";
		my $last_name				= "";
		my $organizaiton_name		= "";
		my $address_1				= "";
		my $address_2				= "";
		my $city					= "";
		my $state					= "";
		my $zip						= "";
		my $country					= "";
		my $phone					= "";
		my $fax						= "";
		my $social_security_number	= "";
		my $tax_id_number	  		= "";
		my $pay_to_the_order_of		= "";
		my $bank_name				= "";
		my $bank_ABA_code			= "";
		my $bank_account_number		= "";
		my $agree_to_policies		= "";

		# Update login_info table to change the user's email address...
		my $SqlStatement = "afl_GenHome \'$afl_cookie_id\', \'$afl_cookie_password\'"; 

		my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
		$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
		$status = $MSSQL::DBlib::dbh->dbsqlexec();
			
		if($DatabaseFunctions::DatabaseError eq "1016")
			{
				&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_id, "Database Rollback Error.<BR><BR>\n\nPlease try again.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
			}
		else
			{
				&UtilityFunctions::Afl_Print_HTML_Top(\1, \$ProgramName, \$DebugUtilityFunctions, \%Map);
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
										
										$affiliate_of			= $$dataref{affiliate_of};
										$program_type			= $$dataref{program_type};
										$password				= $$dataref{password};
										$email					= $$dataref{email};
										$creation_date			= $$dataref{creation_date};
										$last_login				= $$dataref{last_login};
										$email_verification_code= $$dataref{email_verification_code};
										$is_email_verified		= $$dataref{is_email_verified};
										$receive_promo_mail		= $$dataref{receive_promo_mail};
										$password_question		= $$dataref{password_question};
										$password_answer		= $$dataref{password_answer};
										$web_site_name			= $$dataref{web_site_name};
										$web_site_url			= $$dataref{web_site_url};
										$web_site_description	= $$dataref{web_site_description};
										$web_site_topic			= $$dataref{web_site_topic};
										$first_name				= $$dataref{first_name};
										$last_name				= $$dataref{last_name};
										$organizaiton_name		= $$dataref{organizaiton_name};
										$address_1				= $$dataref{address_1};
										$address_2				= $$dataref{address_2};
										$city					= $$dataref{city};
										$state					= $$dataref{state};
										$zip					= $$dataref{zip};
										$country				= $$dataref{country};
										$phone					= $$dataref{phone};
										$fax					= $$dataref{fax};
										$social_security_number	= $$dataref{social_security_number};
										$tax_id_number	  		= $$dataref{tax_id_number};
										$pay_to_the_order_of	= $$dataref{pay_to_the_order_of};
										$bank_name				= $$dataref{bank_name};
										$bank_ABA_code			= $$dataref{bank_ABA_code};
										$bank_account_number	= $$dataref{bank_account_number};
										$agree_to_policies		= $$dataref{agree_to_policies};

										if($DebugThisAp eq "1")
											{
												print "<!-- affiliate_of            = ($affiliate_of) -->\n";
												print "<!-- program_type            = ($program_type) -->\n";
												print "<!-- password                = ($password) -->\n";
												print "<!-- email                   = ($email) -->\n";
												print "<!-- creation_date           = ($creation_date) -->\n";
												print "<!-- last_login              = ($last_login) -->\n";
												print "<!-- email_verification_code = ($email_verification_code) -->\n";
												print "<!-- is_email_verified       = ($is_email_verified) -->\n";
												print "<!-- receive_promo_mail      = ($receive_promo_mail) -->\n";
												print "<!-- password_question       = ($password_question) -->\n";
												print "<!-- password_answer         = ($password_answer) -->\n";
												print "<!-- web_site_name           = ($web_site_name) -->\n";
												print "<!-- web_site_url            = ($web_site_url) -->\n";
												print "<!-- web_site_description    = ($web_site_description) -->\n";
												print "<!-- web_site_topic          = ($web_site_topic) -->\n";
												print "<!-- first_name              = ($first_name) -->\n";
												print "<!-- last_name               = ($last_name) -->\n";
												print "<!-- organizaiton_name       = ($organizaiton_name) -->\n";
												print "<!-- address_1               = ($address_1) -->\n";
												print "<!-- address_2               = ($address_2) -->\n";
												print "<!-- city                    = ($city) -->\n";
												print "<!-- state                   = ($state) -->\n";
												print "<!-- zip                     = ($zip) -->\n";
												print "<!-- country                 = ($country) -->\n";
												print "<!-- phone                   = ($phone) -->\n";
												print "<!-- fax                     = ($fax) -->\n";
												print "<!-- social_security_number  = ($social_security_number) -->\n";
												print "<!-- tax_id_number           = ($tax_id_number) -->\n";
												print "<!-- pay_to_the_order_of     = ($pay_to_the_order_of) -->\n";
												print "<!-- bank_name               = ($bank_name) -->\n";
												print "<!-- bank_ABA_code           = ($bank_ABA_code) -->\n";
												print "<!-- bank_account_number     = ($bank_account_number) -->\n";
												print "<!-- agree_to_policies       = ($agree_to_policies) -->\n";
											}	
									}
								print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
								print "    <!--\n";
								print "            var Then = new Date()\n";
								print "            Then.setTime(Then.getTime() + 60 * 60 * 1000)\n";
								print "            document.cookie=\"afl_cookie_id=$afl_cookie_id; expires=\" + Then.toGMTString() + \"; path=/\"\n";
								print "            document.cookie=\"afl_cookie_email=$afl_cookie_email; expires=\" + Then.toGMTString() + \"; path=/\"\n";
								print "            document.cookie=\"afl_cookie_password=$afl_cookie_password; expires=\" + Then.toGMTString() + \"; path=/\"\n";
								print "    //-->\n";
								print " </SCRIPT> \n";
							}# END else (No db error) 
						}# END if($status != FAIL)
				else
					{
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error("", "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
			}
		&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
	}
#End HTML...
print "</HTML>\n";
exit 0;
