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

my $ProgramName = "Afl_EditContactInfo.cgi";

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
						my $SqlStatement = "afl_UpdateContactInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'name'}\'\
																		, \'$QueryStringHash{'address_1'}\'\
																		, \'$QueryStringHash{'address_2'}\'\
																		, \'$QueryStringHash{'city'}\'\
																		, \'$QueryStringHash{'state'}\'\
																		, \'$QueryStringHash{'zip'}\'\
																		, \'$QueryStringHash{'country'}\'\
																		, \'$QueryStringHash{'phone'}\'\
																		, \'$QueryStringHash{'fax'}\'\
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
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your Contact Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				else
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_GetContactInfo \'$afl_cookie_email\', \'$afl_cookie_password\'"; 

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
                                                print "<title>Edit Contact Information</title>\n";
                                                print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n";
                                                print "<link href=\"" . $Map{'ROOT'} . "/css/" . $Map{'STYLE_SHEET'} . "\" rel=\"stylesheet\" type=\"text/css\">\n";
												print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/MyFunctions.js\"></SCRIPT>\n";
												print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/Afl_EditContactInfo.js\"></SCRIPT>\n";
                                                print "</head>\n";
                                                print "<body bgcolor=\"eeeeee\">\n";
                                                print "<table width=\"700\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\" bgcolor=\"#999999\">\n";
                                                print "  <tr>\n";
                                                print "    <td><table width=\"700\" border=\"0\" cellpadding=\"3\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
                                                print "        <form method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\" onsubmit=\"return check_Afl_EditContactInfoForm(this);\">\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\" class=\"BlackTextLarge3Bold\"><strong>&nbsp;Edit Contact Information</strong></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><IMG src=\"" . $Map{'ROOT'} . "/images/blackSpacer.gif\" width=\"100%\" height=\"2\"></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><font color=\"red\">&nbsp;</font>&nbsp;</td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td>Account #</td>\n";
                                                print "            <td>&nbsp;</td>\n";
                                                print "            <td><strong>" . $$dataref{afl_account_id} . "</strong></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>Name</td>\n";
                                                print "            <td>*</td>\n";
                                                print "            <td> <input type=\"text\" name=\"name\" maxlength=\"96\" size=\"50\" value=\"" . $$dataref{name} . "\" class=\"formFieldStatic\"></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td>Address</td>\n";
                                                print "            <td>*</td>\n";
                                                print "            <td> <input type=\"text\" name=\"address_1\" maxlength=\"64\" size=\"50\" value=\"" . $$dataref{address_1} . "\" class=\"formFieldStatic\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>Address 2</td>\n";
                                                print "            <td>&nbsp;</td>\n";
                                                print "            <td> <input type=\"text\" name=\"address_2\" maxlength=\"32\" size=\"50\" value=\"" . $$dataref{address_2} . "\" class=\"formFieldStatic\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td>City</td>\n";
                                                print "            <td>*</td>\n";
                                                print "            <td> <input type=\"text\" name=\"city\" maxlength=\"32\" size=\"20\" value=\"" . $$dataref{city} . "\" class=\"formFieldStatic\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";

												# state ...
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>State/Province</td>\n";
                                                print "            <td>&nbsp;</td>\n";
                                                print "            <td> <select name=\"state\" >\n";

												&DatabaseFunctions::Print_Lookup_Table_Options('state', '', $$dataref{state}, '', '1', $DebugThisAp, %Map);
												print "                 </SELECT>\n";

                                                print "            </td>\n";
												# zip...
                                                print "          </tr>\n";
                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td>Zip Code</td>\n";
                                                print "            <td>*</td>\n";
                                                print "            <td> <input type=\"text\" name=\"zip\" maxlength=\"10\" size=\"12\" value=\"" . $$dataref{zip} . "\" class=\"formFieldStatic\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";

												# country...
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>Country</td>\n";
                                                print "            <td>&nbsp;</td>\n";
                                                print "            <td> <select name=\"country\" >\n";

												&DatabaseFunctions::Print_Lookup_Table_Options('country', '', $$dataref{country}, '', '1', $DebugThisAp, %Map);
												print "                 </SELECT>\n";

                                                print "            </td>\n";
                                                print "          </tr>\n";


                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td>Phone</td>\n";
                                                print "            <td>*</td>\n";
                                                print "            <td> <input type=\"text\" name=\"phone\" maxlength=\"20\" size=\"30\" value=\"" . $$dataref{phone} . "\" class=\"formFieldStatic\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>Fax</td>\n";
                                                print "            <td>&nbsp;</td>\n";
                                                print "            <td> <input type=\"text\" name=\"fax\" maxlength=\"20\" size=\"30\" value=\"" . $$dataref{fax} . "\" class=\"formFieldStatic\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>&nbsp;</td>\n";
                                                print "            <td>*</td>\n";
                                                print "            <td>Required fields</td>\n";
                                                print "          </tr>\n";
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
										&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to edit account info for ($afl_cookie_email).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
									}
							}
					}
			}
	}
#End HTML...
print "</HTML>\n";
exit 0;
