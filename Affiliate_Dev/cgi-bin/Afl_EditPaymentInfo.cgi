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

my $ProgramName = "Afl_EditPaymentInfo.cgi";

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
				# Load the values passed in into the QueryStringHash...
				@QueryStringParams = CGI::param();
				%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

				if($QueryStringHash{'submit'} eq "Save")
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_UpdatePaymentInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'minimum_payment'}\'\
																		, \'$QueryStringHash{'payment_method'}\'\
																		, \'$QueryStringHash{'direct_deposit_country'}\'\
																		, \'$QueryStringHash{'pay_to_the_order_of'}\'\
																		, \'$QueryStringHash{'social_security_or_tax_id'}\'\
																		, \'$QueryStringHash{'bank_name'}\'\
																		, \'$QueryStringHash{'name_on_bank_account'}\'\
																		, \'$QueryStringHash{'bank_account_type'}\'\
																		, \'$QueryStringHash{'bank_account_number'}\'\
																		, \'$QueryStringHash{'bank_routing_number'}\'\
																		"; 
						my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, $ProgramName, $SqlStatement, $DebugDatabaseFunctions);
						if($return_value eq "1")
							{
								# Update Cookie info...
								print "<HEAD>\n";
								print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
								print "    <!--\n";
								print "		opener.document.location.reload();\n";
								print "		window.close();\n";
								print "    //-->\n";
								print " </SCRIPT> \n";
								print "</HEAD>\n";
							}
						elsif($DatabaseFunctions::DatabaseError eq "1000" or $DatabaseFunctions::DatabaseError eq "1001")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "Email ($afl_cookie_email) and password did not match.<BR><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);		
							}
						elsif($DatabaseFunctions::DatabaseError eq "1012")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">You must first <A href=\"$Map{'CGIBIN'}/ManageEmailVerification.cgi\">verify your email address</A> before becoming a premium member.</FONT><BR><A href=\"$Map{'CGIBIN'}/ManageEmailVerification.cgi\">click here to verify email...</A><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						elsif($DatabaseFunctions::DatabaseError eq "1022")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">ERROR: Access denied for user ($afl_cookie_email)</FONT><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						else
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your Payment Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				else
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_GetPaymentInfo \'$afl_cookie_email\', \'$afl_cookie_password\'"; 

						my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
						$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
						$status = $MSSQL::DBlib::dbh->dbsqlexec();
							
						if($DatabaseFunctions::DatabaseError eq "1022")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Access Denied.<BR><BR>\n\nUser ($afl_cookie_email) does not have permission to edit this data.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
							}
						elsif($DatabaseFunctions::DatabaseError eq "1000" or $DatabaseFunctions::DatabaseError eq "1001")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "Email ($afl_cookie_email) and password did not match.<BR><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);		
							}
						else
							{
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
												if($DebugThisAp eq "1")
													{
														while( (my $Key, my $Value) = each(%$dataref) )
														{
															print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
															print "<!-- $Key = ($Value) -->\n";
														}                
													}	
                                                print "<head>\n";
                                                print "<title>Edit Payment Information</title>\n";
                                                print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n";
                                                print "<link href=\"" . $Map{'ROOT'} . "/css/" . $Map{'STYLE_SHEET'} . "\" rel=\"stylesheet\" type=\"text/css\">\n";
												print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/MyFunctions.js\"></SCRIPT>\n";
												print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/Afl_EditPaymentInfo.js\"></SCRIPT>\n";
                                                print "</head>\n";
                                                print "<body bgcolor=\"eeeeee\">\n";
                                                print "<table width=\"700\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\" bgcolor=\"#999999\">\n";
                                                print "  <tr>\n";
                                                print "    <td><table width=\"700\" border=\"0\" cellpadding=\"3\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
                                                print "        <form method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\" onsubmit=\"return check_Afl_EditPaymentInfoForm(this);\">\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\" class=\"BlackTextLarge3Bold\"><strong>&nbsp;Edit Payment Information</strong></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><IMG src=\"" . $Map{'ROOT'} . "/images/blackSpacer.gif\" width=\"100%\" height=\"2\"></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><font color=\"red\">&nbsp;</font>&nbsp;</td>\n";
                                                print "          </tr>\n";
                                                print "		  <TR>\n";
                                                print "			<TD class=\"AlignRight\">\n";
                                                print "			  Tax ID (SSN/EIN):\n";
                                                print "			</TD>\n";
                                                print "			<TD>\n";
                                                print "			  <INPUT name=\"social_security_or_tax_id\" value=\"" . $$dataref{social_security_or_tax_id} . "\" size=\"20\" maxlength=\"11\">\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "          <TR> \n";
                                                print "            <TD class=\"AlignRight\">Minimum Payment Amount:</TD>\n";
                                                print "            <TD class=\"AlignLeft\"> <select name=\"minimum_payment\" class=\"dropDown\">\n";

												my @minimum_payment	  = ("-1", "25", "50", "75", "100", "250");
												foreach my $minimum_payment (@minimum_payment) 
													{
														if($$dataref{minimum_payment} eq $minimum_payment and $$dataref{minimum_payment} eq "-1") 
															{
																print "                              <OPTION value=\"-1\" SELECTED>\n";
																print "                                Select...\n";
															}
														elsif($$dataref{minimum_payment} eq $minimum_payment) 
															{
																print "                              <OPTION value=\"" . $$dataref{minimum_payment} . "\" SELECTED>\n";
																print "                                " . $$dataref{minimum_payment} . "\n";
															}
														elsif($minimum_payment eq "-1") 
															{
																print "                              <OPTION value=\"-1\">\n";
																print "                                Select...\n";
															}
														else
															{
																print "                              <OPTION value=\"$minimum_payment\">\n";
																print "                                $minimum_payment\n";
															}
														print "                              </OPTION>\n";
													}

                                                print "              </select>";
												print "			   </TD>\n";
                                                print "          </TR>\n";
                                                print "          <TR class=\"BG2Text2\"> \n";
                                                print "			<TD colspan=\"2\" class=\"AlignLeft\">\n";
                                                print "			  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<FONT color=\"red\">*</FONT>";
												if($$dataref{payment_method} eq "1")
												{
													print "<input type=\"radio\" name=\"payment_method\" value=\"1\" checked=\"checked\">";
												}
												else
												{
													print "<input type=\"radio\" name=\"payment_method\" value=\"1\"";
												}
												print "<SPAN class=\"BlackTextLargeBold\">Payment By Direct Deposit (Choose an option)</SPAN>\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD colspan=\"2\" class=\"AlignCenter\">\n";
												if($$dataref{direct_deposit_country} eq "223")
												{
													print "				<input type=\"radio\" name=\"direct_deposit_country\" value=\"223\" checked=\"checked\">\n";
													print "				  <SPAN class=\"paragraph_red\">US Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"38\">\n";
													print "				  <SPAN class=\"paragraph_red\">Canada Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"83\">\n";
													print "				<SPAN class=\"paragraph_red\">UK Direct Deposit </SPAN>\n";
												}
												elsif($$dataref{direct_deposit_country} eq "38")
												{
													print "				<input type=\"radio\" name=\"direct_deposit_country\" value=\"223\">\n";
													print "				  <SPAN class=\"paragraph_red\">US Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"38\" checked=\"checked\">\n";
													print "				  <SPAN class=\"paragraph_red\">Canada Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"83\">\n";
													print "				<SPAN class=\"paragraph_red\">UK Direct Deposit </SPAN>\n";
												}
												elsif($$dataref{direct_deposit_country} eq "83")
												{
													print "				<input type=\"radio\" name=\"direct_deposit_country\" value=\"223\">\n";
													print "				  <SPAN class=\"paragraph_red\">US Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"38\">\n";
													print "				  <SPAN class=\"paragraph_red\">Canada Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"83\" checked=\"checked\">\n";
													print "				<SPAN class=\"paragraph_red\">UK Direct Deposit </SPAN>\n";
												}
												else
												{
													print "				<input type=\"radio\" name=\"direct_deposit_country\" value=\"223\">\n";
													print "				  <SPAN class=\"paragraph_red\">US Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"38\">\n";
													print "				  <SPAN class=\"paragraph_red\">Canada Direct Deposit </SPAN>\n";
													print "					<input type=\"radio\" name=\"direct_deposit_country\" value=\"83\">\n";
													print "				<SPAN class=\"paragraph_red\">UK Direct Deposit </SPAN>\n";
												}

                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD width=\"297\" height=\"28\" class=\"AlignRight\">\n";
                                                print "			  <P>\n";
                                                print "				 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<SPAN class=\"paragraph_red\">Bank name:</SPAN>\n";
                                                print "			  </P>\n";
                                                print "			</TD>\n";
                                                print "			<TD width=\"483\" height=\"28\" class=\"bank_name\">\n";
                                                print "			  <P>\n";
                                                print "				 <INPUT name=\"bank_name\" value=\"" . $$dataref{bank_name} . "\" size=\"20\" maxlength=\"32\">\n";
                                                print "			  </P>\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD height=\"27\" class=\"AlignRight\">\n";
                                                print "			  <FONT color=\"red\">*</FONT>Account Type:\n";
                                                print "			</TD>\n";
                                                print "			<TD valign=\"middle\">\n";
                                                print "			  <SELECT name=\"bank_account_type\">\n";
												if($$dataref{bank_account_type} eq "Checking")
												{
													print "				<OPTION SELECTED value=\"Checking\">\n";
													print "				  Checking\n";
													print "				</OPTION>\n";
													print "				<OPTION value=\"Savings\">\n";
													print "				  Savings\n";
													print "				</OPTION>\n";
												}
												elsif($$dataref{bank_account_type} eq "Savings")
												{
													print "				<OPTION value=\"Checking\">\n";
													print "				  Checking\n";
													print "				</OPTION>\n";
													print "				<OPTION SELECTED value=\"Savings\">\n";
													print "				  Savings\n";
													print "				</OPTION>\n";
												}
												else
												{
													print "				<OPTION value=\"Checking\">\n";
													print "				  Checking\n";
													print "				</OPTION>\n";
													print "				<OPTION value=\"Savings\">\n";
													print "				  Savings\n";
													print "				</OPTION>\n";
												}
                                                print "			  </SELECT>\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD width=\"297\" height=\"28\" class=\"AlignRight\">\n";
                                                print "			  <P>\n";
                                                print "				 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<SPAN class=\"paragraph_red\">Name on Account:</SPAN>\n";
                                                print "			  </P>\n";
                                                print "			</TD>\n";
                                                print "			<TD width=\"483\" height=\"28\">\n";
                                                print "			  <P>\n";
                                                print "				 <INPUT name=\"name_on_bank_account\" value=\"" . $$dataref{name_on_bank_account} . "\"size=\"20\" maxlength=\"64\">\n";
                                                print "			  </P>\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD height=\"22\" class=\"AlignRight\">\n";
                                                print "			  Account number:\n";
                                                print "			</TD>\n";
                                                print "			<TD height=\"22\" class=\"BlackTextMedium\">\n";
                                                print "			  <INPUT name=\"bank_account_number\" value=\"" . $$dataref{bank_account_number} . "\"size=\"20\" maxlength=\"10\">\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD>&nbsp;\n";
                                                print "			  \n";
                                                print "			</TD>\n";
                                                print "			<TD height=\"27\" class=\"AlignLeft\">\n";
                                                print "			  Typically a 10 digit number at the right side of your account number printed on your personal checks.\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD width=\"297\" height=\"28\" class=\"AlignRight\">\n";
                                                print "			  <P>\n";
                                                print "				 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Routing number:\n";
                                                print "			  </P>\n";
                                                print "			</TD>\n";
                                                print "			<TD width=\"483\" height=\"28\" class=\"BlackTextMedium\">\n";
                                                print "			  <P>\n";
                                                print "				 <INPUT name=\"bank_routing_number\" value=\"" . $$dataref{bank_routing_number} . "\"size=\"20\" maxlength=\"9\">\n";
                                                print "			  </P>\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD>&nbsp;\n";
                                                print "			  \n";
                                                print "			</TD>\n";
                                                print "			<TD height=\"27\" class=\"AlignLeft\">\n";
                                                print "			  Find your 9 digit routing number at the bottom left of your account's checks\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "          <TR class=\"BG2Text2\"> \n";
                                                print "			<TD colspan=\"2\" class=\"AlignLeft\">\n";
                                                print "			  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<FONT color=\"red\">*</FONT>";
												if($$dataref{payment_method} eq "2")
												{
													print "<input type=\"radio\" name=\"payment_method\" value=\"2\" checked=\"checked\">";
												}
												else
												{
													print "<input type=\"radio\" name=\"payment_method\" value=\"2\"";
												}
												print "<SPAN class=\"BlackTextLargeBold\">Payment by Check:</SPAN>\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "		  <TR>\n";
                                                print "			<TD width=\"297\" height=\"27\" class=\"AlignRight\">\n";
                                                print "			  <SPAN class=\"paragraph_red\">Checks payable to:</SPAN>\n";
                                                print "			</TD>\n";
                                                print "			<TD width=\"483\" height=\"27\" class=\"BlackTextMedium\">\n";
                                                print "			  <INPUT name=\"pay_to_the_order_of\" value=\"" . $$dataref{pay_to_the_order_of} . "\"size=\"20\" maxlength=\"64\">\n";
                                                print "			</TD>\n";
                                                print "		  </TR>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\" align=\"center\"> <table cellspacing=\"0\" cellpadding=\"0\">\n";
                                                print "                <tr> \n";
                                                print "                  <td> <table cellspacing=\"0\" cellpadding=\"1\" width=\"10\" border=\"0\">\n";
                                                print "                      <tr> \n";
                                                print "                        <td> <input name=\"submit\" type=\"submit\" class=\"buttonDefault\" value=\"Save\"> \n";
                                                print "                        </td>\n";
                                                print "                      </tr>\n";
                                                print "                    </table></td>\n";
                                                print "                  <td>&nbsp;&nbsp; </td>\n";
                                                print "                  <td> <table cellspacing=\"0\" cellpadding=\"1\" width=\"10\" border=\"0\">\n";
                                                print "                      <tr> \n";
                                                print "                        <td> <input class=\"buttonDefault\" onClick=\"window.close();\" type=\"button\" name=\"button2\" value=\"Cancel\" /> \n";
                                                print "                        </td>\n";
                                                print "                      </tr>\n";
                                                print "                    </table></td>\n";
                                                print "                </tr>\n";
                                                print "              </table></td>\n";
                                                print "          </tr>\n";
                                                print "        </form>\n";
                                                print "      </table></td>\n";
                                                print "  </tr>\n";
                                                print "</table>\n";
                                                print "<p>&nbsp;</p>\n";
                                                print "</body>\n";
                                                
											}
									}
								else
									{
										$status = $MSSQL::DBlib::dbh->dbcancel();
										print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
										&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to edit payment info for ($afl_cookie_email).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
									}
							}
					}
			}
	}
#End HTML...
print "</HTML>\n";
exit 0;
