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

my $DebugPrintColorHTML	   = "0";

my $ProgramName = "Afl_AccountDetails.cgi";

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


if ($afl_cookie_email eq "" or $afl_cookie_password eq "") 
	{
		# Die if the user is not logged in...
		&UtilityFunctions::Afl_Print_Framed_Error("", "You must be logged in to view this page.", $DebugUtilityFunctions, %Map);
	}
else
	{
		# Account ID and Account Type of the current user who is logged in 
		#   used to determine website behaviour...
		my $afl_account_id			 = "";
		my $login_account_type		 = "";

		# Update login_info table to change the user's email address...
		my $SqlStatement = "afl_GenAccountInfo \'$afl_cookie_email\', \'$afl_cookie_password\'"; 

		my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
		$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
		$status = $MSSQL::DBlib::dbh->dbsqlexec();
			
		if($DatabaseFunctions::DatabaseError eq "1000" or $DatabaseFunctions::DatabaseError eq "1001")
			{
				&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "Email ($afl_cookie_email) and password did not match.<BR><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);		
			}
		elsif($DatabaseFunctions::DatabaseError eq "1016")
			{
				&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "Database Rollback Error.<BR><BR>\n\nPlease try again.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
			}
		else
			{
				&UtilityFunctions::Afl_Print_HTML_Top(\1, \$ProgramName, \$DebugUtilityFunctions, \%Map);
				##########################
				# Get FIRST result set...
				# Affiliate ID and User Type...
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
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								# Since there is no global DB error check get 
								# all database fields returned by the query...
								
								$afl_account_id		= $$dataref{afl_account_id};
								$login_account_type	= $$dataref{login_account_type};

								if($DebugThisAp eq "1")
									{
										while( (my $Key, my $Value) = each(%$dataref) )
										{
											print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
											print "<!-- $Key = ($Value) -->\n";
										}                
									}	

							}
					}
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
				##########################
				# Get SECOND result set...
				# Affiliate ID and User Type...
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
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								if($DebugThisAp eq "1")
									{
										while( (my $Key, my $Value) = each(%$dataref) )
										{
											print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
											print "<!-- $Key = ($Value) -->\n";
										}                
									}	
								print "      <TABLE width=\"98%\" border=\"0\" cellspacing=\"0\" cellpadding=\"3\">\n";
								print "        <TR> \n";
								print "          <TD width=\"49%\">&nbsp; </TD>\n";
								print "          <TD width=\"51%\">&nbsp; </TD>\n";
								print "        </TR>\n";
								print "        <TR> \n";
								print "          <TD> <TABLE width=\"98%\" border=\"0\" cellspacing=\"1\" cellpadding=\"0\" bgcolor=\"#999999\">\n";
								print "              <TR> \n";
								print "                <TD width=\"497\"> <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
								print "                    <TR> \n";
								print "                      <TD width=\"602\"> <TABLE width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"3\">\n";
								print "                          <TR> \n";
								print "                            <TD class=\"RedTextLargeBold\"> Contact Information \n";
								print "                            </TD>\n";

								print "                            <TD width=\"50%\" align=\"right\">";
								print "<input type=\"button\"";
								if($login_account_type ne "0")
								{
									print " disabled ";
								}
								print "value=\"Edit\" name=\"SubmitContactInfo\" onclick=\"OpenWindow('" . $Map{'CGIBIN'} . "/Afl_EditContactInfo.cgi',480,740)\">\n";
								print "                            </TD>\n";

								print "                          </TR>\n";
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> Name </TD>\n";
								print "                            <TD> " . $$dataref{name} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD> Address </TD>\n";
								print "                            <TD> " . $$dataref{address_1} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> Address 2 </TD>\n";
								print "                            <TD> " . $$dataref{address_2} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD> City </TD>\n";
								print "                            <TD> " . $$dataref{city} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> State/Province </TD>\n";
								print "                            <TD> " . $$dataref{state} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD> Postal Code </TD>\n";
								print "                            <TD> " . $$dataref{zip} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> Country </TD>\n";
								print "                            <TD> " . $$dataref{country} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD> Phone </TD>\n";
								print "                            <TD> " . $$dataref{phone} . " </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> Fax </TD>\n";
								print "                            <TD> " . $$dataref{fax} . " </TD>\n";
								print "                          </TR>\n";
								print "                        </TABLE></TD>\n";
								print "                    </TR>\n";
								print "                  </TABLE></TD>\n";
								print "              </TR>\n";
								print "            </TABLE></TD>\n";
							}
					}
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
				##########################
				# Get THIRD result set...
				# Affiliate ID and User Type...
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
						# Check for global DB error...
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								if($DebugThisAp eq "1")
									{
										while( (my $Key, my $Value) = each(%$dataref) )
										{
											print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
											print "<!-- $Key = ($Value) -->\n";
										}                
									}	
								print "          <TD valign=\"top\"> <TABLE width=\"100%\" border=\"0\" cellspacing=\"1\" cellpadding=\"0\" bgcolor=\"#999999\">\n";
								print "              <TR> \n";
								print "                <TD width=\"497\"> <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
								print "                    <TR> \n";
								print "                      <TD width=\"602\"> <TABLE width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"3\">\n";
								print "                          <TR> \n";
								print "                            <TD class=\"RedTextLargeBold\"> Payment Information \n";
								print "                            </TD>\n";

								print "                            <TD width=\"50%\" align=\"right\">";
								print "<input type=\"button\"";
								if($login_account_type ne "0")
								{
									print " disabled ";
								}
								print "value=\"Edit\" name=\"SubmitPaymentInfo\" onclick=\"OpenWindow('" . $Map{'CGIBIN'} . "/Afl_EditPaymentInfo.cgi',550,755)\">\n";
								print "                            </TD>\n";

								print "                          </TR>\n";

								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> Minimum Payment Amount </TD>\n";
								print "                            <TD> \$" . $$dataref{minimum_payment} . " USD </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD> Payment Method </TD>\n";
								print "                            <TD> " . $$dataref{payment_method} . " </TD>\n";
								print "                          </TR>\n";
								if($$dataref{payment_method} eq "Check")		# Check
								{
									print "                          <TR class=\"BG2Text2\"> \n";
									print "                            <TD> Payee name </TD>\n";
									print "                            <TD> " . $$dataref{pay_to_the_order_of} . " </TD>\n";
									print "                          </TR>\n";
								}
								elsif($$dataref{payment_method} eq "Direct Deposit")	# Direct Deposit
								{
									print "                          <TR class=\"BG2Text2\"> \n";
									print "                            <TD> Payee name </TD>\n";
									print "                            <TD> " . $$dataref{name_on_bank_account} . " </TD>\n";
									print "                          </TR>\n";
									print "                          <TR class=\"BlackTextMedium\"> \n";
									print "                            <TD> SS# or Fed tax ID# </TD>\n";
									print "                            <TD> " . $$dataref{social_security_or_tax_id} . " </TD>\n";
									print "                          </TR>\n";
									print "                          <TR class=\"BG2Text2\"> \n";
									print "                            <TD> Bank Name </TD>\n";
									print "                            <TD> " . $$dataref{bank_name} . " </TD>\n";
									print "                          </TR>\n";
									print "                          <TR class=\"BlackTextMedium\"> \n";
									print "                            <TD> Account Type </TD>\n";
									print "                            <TD> " . $$dataref{bank_account_type} . " </TD>\n";
									print "                          </TR>\n";
									print "                          <TR class=\"BG2Text2\"> \n";
									print "                            <TD> Account Number </TD>\n";
									print "                            <TD> " . $$dataref{bank_account_number} . " </TR>\n";
									print "                          <TR class=\"BlackTextMedium\"> \n";
									print "                            <TD> Routing Number </TD>\n";
									print "                            <TD> " . $$dataref{bank_routing_number} . " </TD>\n";
									print "                          </TR>\n";
								}
								else							# Unknown
								{
									print "                          <TR class=\"BG2Text2\"> \n";
									print "                            <TD> Payee name </TD>\n";
									print "                            <TD> Unknown </TD>\n";
									print "                          </TR>\n";
								}

								print "                        </TABLE></TD>\n";
								print "                    </TR>\n";
								print "                  </TABLE></TD>\n";
								print "              </TR>\n";
								print "            </TABLE></TD>\n";
								print "        </TR>\n";
								print "        <TR> \n";
								print "          <TD>&nbsp; </TD>\n";
								print "          <TD>&nbsp; </TD>\n";
								print "        </TR>\n";
							}
					}
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
				##########################
				# Get FOURTH result set...
				# Affiliate ID and User Type...
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
						print "        <TR> \n";
						print "          <TD colspan=\"2\"> <TABLE width=\"100%\" border=\"0\" cellspacing=\"1\" cellpadding=\"0\" bgcolor=\"#999999\">\n";
						print "              <TR> \n";
						print "                <TD width=\"100%\"> <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
						print "                    <TR> \n";
						print "                      <TD width=\"100%\"> <TABLE width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"3\">\n";
						print "                          <TR> \n";
						print "                            <TD colspan=\"3\" class=\"RedTextLargeBold\"> User Settings \n";
						print "                            </TD>\n";

						print "                            <TD colspan=\"3\" align=\"right\">";
						print "<input type=\"button\"";
						if($login_account_type ne "0")
						{
							print " disabled ";
						}
						print "value=\"Add\" name=\"SubmitUserInfo\" onclick=\"OpenWindow('" . $Map{'CGIBIN'} . "/Afl_EditUserInfo.cgi?submit=Add',550,755)\"> \n";
						print "                            </TD>\n";

						print "                          </TR>\n";
						print "                          <TR class=\"BlackTextLargeBold\"> \n";
						print "                            <TD> Name </TD>\n";
						print "                            <TD> Status </TD>\n";
						print "                            <TD> Title </TD>\n";
						print "                            <TD> Email </TD>\n";
						print "                            <TD> Phone </TD>\n";
						print "                            <TD> Actions </TD>\n";
						print "                          </TR>\n";
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								if($DebugThisAp eq "1")
									{
										while( (my $Key, my $Value) = each(%$dataref) )
										{
											print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
											print "<!-- $Key = ($Value) -->\n";
										}                
									}	
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> " . $$dataref{name} . " </TD>\n";
								print "                            <TD> " . $$dataref{account_type} . " </TD>\n";
								print "                            <TD> " . $$dataref{title} . " </TD>\n";
								print "                            <TD> " . $$dataref{email} . " </TD>\n";
								print "                            <TD> " . $$dataref{phone} . " </TD>\n";

								print "                            <TD>";
								if($login_account_type eq "0")
								{
									print "                             <A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_EditUserInfo.cgi',570,755)\" class=\"NavText\">Edit</A>\n";
#									print "                             <A href=\"Javascript:confirmDelete('/account_CJ.html')\" class=\"NavText\">Delete</A> \n";
								}
								else
								{
									print "								<A href=\"\" onClick=\"alert('You do not have permission to edit company information!'); return false;\" class=\"NavText\">Edit</A>, \n";
									print "                             <A href=\"\" onClick=\"alert('You do not have permission to edit company information!'); return false;\" class=\"NavText\">Delete</A> \n";
								}
								print "                            </TD>\n";

								print "                          </TR>\n";
							}
					}
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
				##########################
				# Get FIFTH result set...
				# Affiliate ID and User Type...
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
						my $count = 0;
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								if($DebugThisAp eq "1")
									{
										while( (my $Key, my $Value) = each(%$dataref) )
										{
											print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
											print "<!-- $Key = ($Value) -->\n";
										}                
									}	
								if($count++ % 2 eq 0)
									{
										print "                          <TR class=\"BlackTextMedium\"> \n";
									}
								else
									{
										print "                          <TR class=\"BG2Text2\"> \n";
									}

								print "                            <TD> " . $$dataref{name} . " </TD>\n";
								print "                            <TD> " . $$dataref{account_type} . " </TD>\n";
								print "                            <TD> " . $$dataref{title} . " </TD>\n";
								print "                            <TD> " . $$dataref{email} . " </TD>\n";
								print "                            <TD> " . $$dataref{phone} . " </TD>\n";

								print "                            <TD>";
								if($login_account_type eq "0")
								{
									print "                             <A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_EditUserInfo.cgi?unique_id=" . $$dataref{unique_id} . "',570,755)\" class=\"NavText\">Edit</A>, \n";
									print "                             <A href=\"Javascript:confirmDelete('" . $Map{'CGIBIN'} . "/Afl_EditUserInfo.cgi?submit=Delete&unique_id=" . $$dataref{unique_id} . "')\" class=\"NavText\">Delete</A> \n";
								}
								else
								{
									print "								<A href=\"\" onClick=\"alert('You do not have permission to edit company information!'); return false;\" class=\"NavText\">Edit</A>, \n";
									print "                             <A href=\"\" onClick=\"alert('You do not have permission to edit company information!'); return false;\" class=\"NavText\">Delete</A> \n";
								}
								print "                            </TD>\n";

								print "                          </TR>\n";
							}
						print "                        </TABLE></TD>\n";
						print "                    </TR>\n";
						print "                  </TABLE></TD>\n";
						print "              </TR>\n";
						print "            </TABLE></TD>\n";
						print "        </TR>\n";
						print "        <TR> \n";
						print "          <TD colspan=\"2\">&nbsp; </TD>\n";
						print "        </TR>\n";
					}
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
				##########################
				# Get LAST result set...
				# Affiliate ID and User Type...
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
						print "        <TR> \n";
						print "          <TD colspan=\"2\"> <TABLE width=\"100%\" border=\"0\" cellspacing=\"1\" cellpadding=\"0\" bgcolor=\"#999999\">\n";
						print "              <TR> \n";
						print "                <TD width=\"100%\"> <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
						print "                    <TR> \n";
						print "                      <TD width=\"100%\"> <TABLE width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"3\">\n";
						print "                          <TR> \n";
						print "                            <TD nowrap colspan=\"2\" align=\"left\" class=\"RedTextLargeBold\"> \n";
						print "                              Website Settings </TD>\n";

						print "                            <TD nowrap align=\"right\">";
						print "<input type=\"button\"";
						if($login_account_type ne "0")
						{
							print " disabled ";
						}
						print "value=\"Add\" name=\"SubmitWebAdd\" onclick=\"OpenWindow('" . $Map{'CGIBIN'} . "/Afl_EditWebsiteInfo.cgi?submit=Add',800,740)\"> \n";
						print "                            </TD>\n";
						print "                          </TR>\n";
						my %dataref = ("jason" => "baumbach");
						my $dataref = \%dataref;
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								if($DebugThisAp eq "1")
									{
										while( (my $Key, my $Value) = each(%$dataref) )
										{
											print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
											print "<!-- $Key = ($Value) -->\n";
										}                
									}	
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> Name </TD>\n";
								print "                            <TD> " . $$dataref{site_name} . " </TD>\n";
								print "                            <TD>";
								if($login_account_type eq "0")
								{
									print "                             <A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_EditWebsiteInfo.cgi?site_id=" . $$dataref{site_id} . "',800,740)\" class=\"NavText\">Edit</A>, \n";
									print "                             <A href=\"Javascript:confirmDelete('" . $Map{'CGIBIN'} . "/Afl_EditWebsiteInfo.cgi?submit=Delete&site_id=" . $$dataref{site_id} . "')\" class=\"NavText\">Delete</A> \n";
								}
								else
								{
									print "								<A href=\"\" onClick=\"alert('You do not have permission to edit company information!'); return false;\" class=\"NavText\">Edit</A>, \n";
									print "                             <A href=\"\" onClick=\"alert('You do not have permission to edit company information!'); return false;\" class=\"NavText\">Delete</A> \n";
								}
								print "                            </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD> PID </TD>\n";
								print "                            <TD> " . $$dataref{site_id} . " </TD>\n";
								print "                            <TD>&nbsp; </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> URL </TD>\n";
								print "                            <TD> " . $$dataref{site_url} . " </TD>\n";
								print "                            <TD>&nbsp; </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD> Description </TD>\n";
								print "                            <TD> " . $$dataref{site_description} . " </TD>\n";
								print "                            <TD>&nbsp; </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BG2Text2\"> \n";
								print "                            <TD> Category </TD>\n";
								print "                            <TD> " . $$dataref{site_category} . " -> " . $$dataref{site_sub_category} . " </TD>\n";
								print "                            <TD>&nbsp; </TD>\n";
								print "                          </TR>\n";
								print "                          <TR class=\"BlackTextMedium\"> \n";
								print "                            <TD>&nbsp; </TD>\n";
								print "                            <TD>&nbsp; </TD>\n";
								print "                            <TD>&nbsp; </TD>\n";
								print "                          </TR>\n";
							}
						print "                        </TABLE></TD>\n";
						print "                    </TR>\n";
						print "                  </TABLE></TD>\n";
						print "              </TR>\n";
						print "            </TABLE></TD>\n";
						print "        </TR>\n";
						print "        <TR> \n";
						print "          <TD>&nbsp; </TD>\n";
						print "          <TD>&nbsp; </TD>\n";
						print "        </TR>\n";
						print "      </TABLE>\n";
					}
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
			}
		&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
	}
#End HTML...
print "</HTML>\n";
exit 0;
