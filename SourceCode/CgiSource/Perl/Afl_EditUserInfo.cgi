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

my $ProgramName = "Afl_EditUserInfo.cgi";

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

				if($QueryStringHash{'submit'} eq "Delete")
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_DeleteUserInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'unique_id'}\'\
																		"; 

						my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, $ProgramName, $SqlStatement, $DebugDatabaseFunctions);
						if($return_value eq "1")
							{
								# Update Cookie info...
								print "<HEAD>\n";
								print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
								print "    <!--\n";
								print "		window.location = \"" . $Map{'CGIBIN'} . "/Afl_AccountDetails.cgi\"\n";
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
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your User Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				elsif($QueryStringHash{'submit'} eq "Save")
					{
						##########################################################
						# Remove single quotes for SQL statement...
						##########################################################
						# Remove single quotes from description field...
						if($QueryStringHash{'name'} =~ m/\'/g)
						{
							$QueryStringHash{'name'} =~ s/\'/\'\'/gis;
						}
						if($QueryStringHash{'title'} =~ m/\'/g)
						{
							$QueryStringHash{'title'} =~ s/\'/\'\'/gis;
						}
						if($QueryStringHash{'password_question'} =~ m/\'/g)
						{
							$QueryStringHash{'password_question'} =~ s/\'/\'\'/gis;
						}
						# Remove single quotes from site_name field...
						if($QueryStringHash{'password_answer'} =~ m/\'/g)
						{
							$QueryStringHash{'password_answer'} =~ s/\'/\'\'/gis;
						}
						##########################################################

						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_UpdateUserInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'email'}\'\
																		, \'$QueryStringHash{'password'}\'\
																		, \'$QueryStringHash{'name'}\'\
																		, \'$QueryStringHash{'title'}\'\
																		, \'$QueryStringHash{'phone'}\'\
																		, \'$QueryStringHash{'account_type'}\'\
																		, \'$QueryStringHash{'password_question'}\'\
																		, \'$QueryStringHash{'password_answer'}\'\
																		, \'$QueryStringHash{'receive_promo_mail'}\'\
																		"; 
						if($QueryStringHash{'unique_id'})
						{
							# afl_sub_user_info table...
							$SqlStatement = $SqlStatement . ", \'$QueryStringHash{'unique_id'}\'"; 
						}

						my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, $ProgramName, $SqlStatement, $DebugDatabaseFunctions);
						if($return_value eq "1")
							{
								# Update Cookie info...
								print "<HEAD>\n";
								print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
								print "    <!--\n";

								if(!$QueryStringHash{'unique_id'})
								{
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
									print "            document.cookie=\"afl_cookie_id=" . $afl_account_id . "; expires=\" + Then.toGMTString() + \"; path=/\"\n";
									print "            document.cookie=\"afl_cookie_password=" . $QueryStringHash{'password'} . "; expires=\" + Then.toGMTString() + \"; path=/\"\n";
									print "            document.cookie=\"afl_cookie_email=" . $QueryStringHash{'email'} . "; expires=\" + Then.toGMTString() + \"; path=/\"\n";
								}
								
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
						elsif($DatabaseFunctions::DatabaseError eq "1015")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "Email address (<FONT COLOR=\"#8B0000\">" . $QueryStringHash{'email'} . "</FONT>) is not unique.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						elsif($DatabaseFunctions::DatabaseError eq "1022")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">ERROR: Access denied for user ($afl_cookie_email)</FONT><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						elsif($DatabaseFunctions::DatabaseError eq "1023")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">ERROR: Incorrect email (" . $QueryStringHash{'email'} . ") or password.</FONT><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						else
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your User Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				elsif($QueryStringHash{'submit'} eq "Create")
					{
						##########################################################
						# Remove single quotes for SQL statement...
						##########################################################
						# Remove single quotes from description field...
						if($QueryStringHash{'name'} =~ m/\'/g)
						{
							$QueryStringHash{'name'} =~ s/\'/\'\'/gis;
						}
						if($QueryStringHash{'title'} =~ m/\'/g)
						{
							$QueryStringHash{'title'} =~ s/\'/\'\'/gis;
						}
						if($QueryStringHash{'password_question'} =~ m/\'/g)
						{
							$QueryStringHash{'password_question'} =~ s/\'/\'\'/gis;
						}
						# Remove single quotes from site_name field...
						if($QueryStringHash{'password_answer'} =~ m/\'/g)
						{
							$QueryStringHash{'password_answer'} =~ s/\'/\'\'/gis;
						}
						##########################################################
						my $SqlStatement = "afl_CreateNewUserInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'email'}\'\
																		, \'$QueryStringHash{'password'}\'\
																		, \'$QueryStringHash{'name'}\'\
																		, \'$QueryStringHash{'title'}\'\
																		, \'$QueryStringHash{'phone'}\'\
																		, \'$QueryStringHash{'account_type'}\'\
																		, \'$QueryStringHash{'password_question'}\'\
																		, \'$QueryStringHash{'password_answer'}\'\
																		, \'$QueryStringHash{'receive_promo_mail'}\'\
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
						elsif($DatabaseFunctions::DatabaseError eq "1015")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "Email address (<FONT COLOR=\"#8B0000\">" . $QueryStringHash{'email'} . "</FONT>) is not unique.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						elsif($DatabaseFunctions::DatabaseError eq "1022")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">ERROR: Access denied for user ($afl_cookie_email)</FONT><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						elsif($DatabaseFunctions::DatabaseError eq "1023")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">ERROR: Incorrect email (" . $QueryStringHash{'email'} . ") or password.</FONT><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						else
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your User Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				if($QueryStringHash{'submit'} eq "Add")
					{
							print "<head>\n";
							print "<title>Edit Payment Information</title>\n";
							print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n";
							print "<link href=\"" . $Map{'ROOT'} . "/css/" . $Map{'STYLE_SHEET'} . "\" rel=\"stylesheet\" type=\"text/css\">\n";
							print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/MyFunctions.js\"></SCRIPT>\n";
							print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/Afl_EditUserInfo.js\"></SCRIPT>\n";
							print "</head>\n";
							print "<body bgcolor=\"eeeeee\">\n";
							print "<table width=\"700\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\" bgcolor=\"#999999\">\n";
							print "  <tr>\n";
							print "    <td><table width=\"700\" border=\"0\" cellpadding=\"3\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
							print "        <form name=\"UserInfoForm\" method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\" onsubmit=\"return check_Afl_EditUserInfoForm(this);\">\n";
							print "          <tr> \n";
							print "            <td colspan=\"3\" class=\"BlackTextLarge3Bold\"><strong>&nbsp;Edit User Information</strong></td>\n";
							print "          </tr>\n";
							print "          <tr> \n";
							print "            <td colspan=\"3\"><IMG src=\"" . $Map{'ROOT'} . "/images/blackSpacer.gif\" width=\"100%\" height=\"2\"></td>\n";
							print "          </tr>\n";
							print "          <tr> \n";
							print "            <td colspan=\"3\"><font color=\"red\">&nbsp;</font>&nbsp;</td>\n";
							print "          </tr>\n";
							print "          <tr> \n";

							print "            <tr class=\"BG2Text2\"> \n";
							print "              <td>Name</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "              <td> <input type=\"text\" name=\"name\" maxlength=\"60\" size=\"20\" value=\"\" class=\"formFieldStatic\"> \n";
							print "              </td>\n";
							print "            </tr>\n";
							print "            <tr class=\"BlackTextMedium\"> \n";
							print "              <td>Title</td>\n";
							print "              <td>&nbsp;</td>\n";
							print "              <td> <input type=\"text\" name=\"title\" maxlength=\"30\" size=\"20\" value=\"\" class=\"formFieldStatic\"> \n";
							print "              </td>\n";
							print "            </tr>\n";
							print "            <tr class=\"BG2Text2\"> \n";
							print "              <td>Email</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "              <td> <input type=\"text\" name=\"email\" maxlength=\"50\" size=\"20\" value=\"\" class=\"formFieldStatic\"> \n";
							print "              </td>\n";
							print "            </tr>\n";
							print "            <tr class=\"BG2Text2\"> \n";
							print "              <td>&nbsp;</td>\n";
							print "              <td>&nbsp;</td>\n";
							print "                <TD class=\"AlignLeft\">\n";
							print "                  If you change your email address it will have to be verified.\n";
							print "                </TD>\n";
							print "            </TR>\n";
							print "            <tr class=\"BlackTextMedium\"> \n";
							print "              <td>Phone</td>\n";
							print "              <td>&nbsp;</td>\n";
							print "              <td> <input type=\"text\" name=\"phone\" maxlength=\"30\" size=\"20\" value=\"\" class=\"formFieldStatic\"> \n";
							print "              </td>\n";
							print "            </tr>\n";
							print "            <tr class=\"BG2Text2\"> \n";
							print "              <td>Password</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "              <td> <input type=\"password\" name=\"password\" maxlength=\"40\" size=\"20\" value=\"\" class=\"formFieldStatic\"> \n";
							print "              </td>\n";
							print "            </tr>\n";
							print "            <tr class=\"BlackTextMedium\"> \n";
							print "              <td>Re-type Password</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "              <td><input type=\"password\" name=\"verify_password\" maxlength=\"40\" size=\"20\" class=\"formFieldStatic\"> \n";
							print "              </td>\n";
							print "            </tr>\n";
							print "            <tr class=\"BG2Text2\"> \n";
							print "              <td>I.D. Question</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "                <TD valign=\"middle\">\n";
							print "                  <SELECT name=\"password_question\">\n";
							print "                    <OPTION value=\"-1\" SELECTED>\n";
							print "                      Select...\n";
							print "                    </OPTION>\n";
							print "                    <OPTION value=\"Pet's name\">\n";
							print "                      Pet's name\n";
							print "                    </OPTION>\n";
							print "                    <OPTION value=\"Favorite color\">\n";
							print "                      Favorite color\n";
							print "                    </OPTION>\n";
							print "                    <OPTION value=\"Mother's maiden name\">\n";
							print "                      Mother's maiden name\n";
							print "                    </OPTION>\n";
							print "                    <OPTION value=\"City of Birth\">\n";
							print "                      City of Birth\n";
							print "                    </OPTION>\n";
							print "                  </SELECT>\n";
							print "                </TD>\n";
							print "            </tr>\n";
							print "            <tr class=\"BlackTextMedium\"> \n";
							print "              <td>I.D. Answer</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "              <td><input type=\"text\" name=\"password_answer\" value=\"\" size=\"13\" maxlength=\"32\" class=\"formFieldStatic\"> \n";
							print "            </tr>\n";
							print "              <TR>\n";
							print "              <td>&nbsp;</td>\n";
							print "              <td>&nbsp;</td>\n";
							print "                <TD class=\"AlignLeft\">\n";
							print "                  I.D. Question and Password will be verified if you lose your password.\n";
							print "                </TD>\n";
							print "              </TR>\n";
							print "            <tr class=\"BG2Text2\"> \n";
							print "              <td>User Type</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "              <td> <select name=\"account_type\" class=\"dropDown\">\n";
							my @account_type	  = ("-1", "0", "1", "2");
							foreach my $account_type (@account_type) 
								{
									if($account_type eq "-1") 
										{
											print "                              <OPTION value=\"-1\" SELECTED>\n";
											print "                                Select...\n";
										}
									elsif($account_type eq "0") 
										{
										# user may not select...
										}
									elsif($account_type eq "1") 
										{
											print "                              <OPTION value=\"1\">\n";
											print "                                Operator - May only change account settings\n";
										}
									elsif($account_type eq "2") 
										{
											print "                              <OPTION value=\"2\">\n";
											print "                                Analyzer - May only view reporting\n";
										}
									else
										{
											print "                              <OPTION value=\"-1\">\n";
											print "                                Select......\n";
										}
									print "                              </OPTION>\n";
								}

							print "                </select> </td>\n";
							print "            </tr>\n";
							
                            print "            <TR>\n";
							print "              <td>&nbsp;</td>\n";
                            print "              <TD valign=\"top\" class=\"AlignRight\">\n";
                            print "                <FONT color=\"red\">*</FONT><INPUT type=\"checkbox\" name=\"receive_promo_mail\" value=\"1\">\n";
                            print "              </TD>\n";
                            print "              <TD class=\"BlackTextMedium\">\n";
                            print "					Send me news about NetLoveMatch.com and partner promotions via email.\n";
                            print "					<BR>\n";
                            print "					(If selected this address will receive account information / feature announcement emails when necessary.) \n";
                            print "              </TD>\n";
                            print "            </TR>\n";
							
							print "            <tr class=\"BlackTextMedium\"> \n";
							print "              <td>&nbsp;</td>\n";
							print "              <td><FONT color=\"red\">*</FONT></td>\n";
							print "              <td>Required Fields</td>\n";
							print "            </tr>\n";

							print "            <td colspan=\"3\" align=\"center\"> <table cellspacing=\"0\" cellpadding=\"0\">\n";
							print "                <tr> \n";
							print "                  <td> <table cellspacing=\"0\" cellpadding=\"1\" width=\"10\" border=\"0\">\n";
							print "                      <tr> \n";
							print "                        <td> <input name=\"submit\" type=\"submit\" class=\"buttonDefault\" value=\"Create\"> \n";
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
					else
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_GetUserInfo \'$afl_cookie_email\', \'$afl_cookie_password\'"; 

						if($QueryStringHash{'unique_id'})
						{
							# afl_sub_user_info table...
							$SqlStatement = $SqlStatement . ", \'$QueryStringHash{'unique_id'}\'"; 
						}


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
                                                print "<link href=\"" . $Map{'ROOT'} . "/css/sa.css\" rel=\"stylesheet\" type=\"text/css\">\n";
												print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/MyFunctions.js\"></SCRIPT>\n";
												print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/Afl_EditUserInfo.js\"></SCRIPT>\n";
                                                print "</head>\n";
                                                print "<body bgcolor=\"eeeeee\">\n";
                                                print "<table width=\"700\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\" bgcolor=\"#999999\">\n";
                                                print "  <tr>\n";
                                                print "    <td><table width=\"700\" border=\"0\" cellpadding=\"3\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
                                                print "        <form name=\"UserInfoForm\" method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\" onsubmit=\"return check_Afl_EditUserInfoForm(this);\">\n";
                                                print "          <tr> \n";
												if($QueryStringHash{'unique_id'})
												{
	                                                print "            <input type=\"hidden\" name=\"unique_id\" value=\"" . $QueryStringHash{'unique_id'} . "\"> \n";
												}
                                                print "            <td colspan=\"3\" class=\"BlackTextLarge3Bold\"><strong>&nbsp;Edit User Information</strong></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><IMG src=\"" . $Map{'ROOT'} . "/images/blackSpacer.gif\" width=\"100%\" height=\"2\"></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><font color=\"red\">&nbsp;</font>&nbsp;</td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";

                                                print "            <tr class=\"BG2Text2\"> \n";
                                                print "              <td>Name</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "              <td> <input type=\"text\" name=\"name\" maxlength=\"60\" size=\"20\" value=\"" . $$dataref{name} . "\" class=\"formFieldStatic\"> \n";
                                                print "              </td>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BlackTextMedium\"> \n";
                                                print "              <td>Title</td>\n";
                                                print "              <td>&nbsp;</td>\n";
                                                print "              <td> <input type=\"text\" name=\"title\" maxlength=\"30\" size=\"20\" value=\"" . $$dataref{title} . "\" class=\"formFieldStatic\"> \n";
                                                print "              </td>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BG2Text2\"> \n";
                                                print "              <td>Email</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "              <td> <input type=\"text\" name=\"email\" maxlength=\"50\" size=\"20\" value=\"" . $$dataref{email} . "\" class=\"formFieldStatic\"> \n";
                                                print "              </td>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BG2Text2\"> \n";
                                                print "              <td>&nbsp;</td>\n";
                                                print "              <td>&nbsp;</td>\n";
                                                print "                <TD class=\"AlignLeft\">\n";
                                                print "                  If you change your email address it will have to be verified.\n";
                                                print "                </TD>\n";
                                                print "            </TR>\n";
                                                print "            <tr class=\"BlackTextMedium\"> \n";
                                                print "              <td>Phone</td>\n";
                                                print "              <td>&nbsp;</td>\n";
                                                print "              <td> <input type=\"text\" name=\"phone\" maxlength=\"30\" size=\"20\" value=\"" . $$dataref{phone} . "\" class=\"formFieldStatic\"> \n";
                                                print "              </td>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BG2Text2\"> \n";
                                                print "              <td>Password</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "              <td> <input type=\"password\" name=\"password\" maxlength=\"40\" size=\"20\" value=\"" . $$dataref{password} . "\" class=\"formFieldStatic\"> \n";
                                                print "              </td>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BlackTextMedium\"> \n";
                                                print "              <td>Re-type Password</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "              <td><input type=\"password\" name=\"verify_password\" maxlength=\"40\" size=\"20\" class=\"formFieldStatic\"> \n";
                                                print "              </td>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BG2Text2\"> \n";
                                                print "              <td>I.D. Question</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "                <TD valign=\"middle\">\n";
                                                print "                  <SELECT name=\"password_question\">\n";
                                                print "                    <OPTION value=\"" . $$dataref{password_question} . "\">\n";
												if($$dataref{password_question} =~ m/\'\'/g)
												{
													$$dataref{password_question} =~ s/\'\'/\'/gis;
												}
                                                print "                      " . $$dataref{password_question} . "\n";
                                                print "                    </OPTION>\n";
                                                print "                    <OPTION value=\"Pet's name\">\n";
                                                print "                      Pet's name\n";
                                                print "                    </OPTION>\n";
                                                print "                    <OPTION value=\"Favorite color\">\n";
                                                print "                      Favorite color\n";
                                                print "                    </OPTION>\n";
                                                print "                    <OPTION value=\"Mother's maiden name\">\n";
                                                print "                      Mother's maiden name\n";
                                                print "                    </OPTION>\n";
                                                print "                    <OPTION value=\"City of Birth\">\n";
                                                print "                      City of Birth\n";
                                                print "                    </OPTION>\n";
                                                print "                  </SELECT>\n";
                                                print "                </TD>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BlackTextMedium\"> \n";
                                                print "              <td>I.D. Answer</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "              <td><input type=\"text\" name=\"password_answer\" value=\"" . $$dataref{password_answer} . "\" size=\"13\" maxlength=\"32\" class=\"formFieldStatic\"> \n";
                                                print "            </tr>\n";
                                                print "              <TR>\n";
                                                print "              <td>&nbsp;</td>\n";
                                                print "              <td>&nbsp;</td>\n";
                                                print "                <TD class=\"AlignLeft\">\n";
                                                print "                  I.D. Question and Password will be verified if you lose your password.\n";
                                                print "                </TD>\n";
                                                print "              </TR>\n";
                                                print "            <tr class=\"BG2Text2\"> \n";
                                                print "              <td>User Type</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "              <td> <select name=\"account_type\" class=\"dropDown\">\n";
												my @account_type	  = ("-1", "0", "1", "2");
												foreach my $account_type (@account_type) 
													{
														if($account_type eq "-1") 
															{
															if($$dataref{account_type} eq $account_type) 
																{
																	print "                              <OPTION value=\"-1\" SELECTED>\n";
																	print "                                Select...\n";
																}
															}
														elsif($account_type eq "0") 
															{
															if($$dataref{account_type} eq $account_type) 
																{
																	print "                              <OPTION value=\"0\" SELECTED>\n";
																	print "                                Admin - User has full control of the system\n";
																	last;
																}
															}
														elsif($account_type eq "1") 
															{
															if($$dataref{account_type} eq $account_type) 
																{
																	print "                              <OPTION value=\"1\" SELECTED>\n";
																	print "                                Operator - May only change account settings\n";
																}
															else
																{
																	print "                              <OPTION value=\"1\">\n";
																	print "                                Operator - May only change account settings\n";
																}
															}
														elsif($account_type eq "2") 
															{
															if($$dataref{account_type} eq $account_type) 
																{
																	print "                              <OPTION value=\"2\" SELECTED>\n";
																	print "                                Analyzer - May only view reporting\n";
																}
															else
																{
																	print "                              <OPTION value=\"2\">\n";
																	print "                                Analyzer - May only view reporting\n";
																}
															}
														else
															{
																print "                              <OPTION value=\"-1\">\n";
																print "                                Select......\n";
															}
														print "                              </OPTION>\n";
													}

												print "                </select> </td>\n";
                                                print "            </tr>\n";
                                                print "            <tr class=\"BlackTextMedium\"> \n";
                                                print "              <td>&nbsp;</td>\n";
                                                print "              <td><FONT color=\"red\">*</FONT></td>\n";
                                                print "              <td>Required Fields</td>\n";
                                                print "            </tr>\n";

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
												
												if(!$QueryStringHash{'unique_id'})
												{
													print "			<tr>\n";
													print "			  <td class=\"BlackTextMedium\" colspan=\"3\">\n";
													print "				<font color=\"red\">Note</font>: \n";
													print "				The email address you assign to any user must be unique and cannot be assigned to any other user in this or any other account. The Admin role may be reassigned to another user with an Operator or Analyzer role if you first use the edit function to assign a new email address to the Operator or Analyzer. You may then edit the Admin email address. Do not delete a user if you plan to use the assigned email address for any other role. \n";
													print "			  </td>\n";
													print "			</tr>\n";
												}
												
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
										&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to edit User info for ($afl_cookie_email).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
									}
							}
					}
			}
	}
#End HTML...
print "</HTML>\n";

sub Print_User_Category_Options
{
	(my $PrimaryCategory, my $CommaSeperatedList, my $Debug, my %Map) = @_;

	my @SplitArray;
	my $index = 0;
	my $count = 0;
	my $ArraySize = 0;

	if($CommaSeperatedList =~ m/,/g)
		{
			(@SplitArray) = split (/,/, $CommaSeperatedList );
		}
	else
		{
			push(@SplitArray, $CommaSeperatedList);
		}


	$ArraySize = scalar $#SplitArray + 1;

	print "<!-- CommaSeperatedList = ($CommaSeperatedList) -->\n" if $Debug eq '1';
	print "<!-- SplitArray         = (@SplitArray) -->\n" if $Debug eq '1';
	print "<!-- ArraySize          = ($ArraySize) -->\n" if $Debug eq '1';


	my $SqlStatement = "SELECT * FROM afl_website_categories ORDER BY category ASC";
	my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "DatabaseFunctions.pl");
	$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
	$status = $MSSQL::DBlib::dbh->dbsqlexec();
		
	##########################
	# Get ONLY result set...
	##########################
	# dbresults() must be called for each result set...
	$status = $MSSQL::DBlib::dbh->dbresults();
	if($status != FAIL)
		{
			print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n" if $Debug eq '1';
			my %dataref = ("jason" => "baumbach");
			my $dataref = \%dataref;
			# If in debug mode, print information...
			print "<!-- SQL: $SqlStatement -->\n" if $Debug eq '1';
			# Prevent infinite loop...
			my $previous_category = "";
			while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
				{
					# Since there is no global DB error check get 
					# all database fields returned by the query...
					
					$index = 0;
					my $found = "No";
					$SplitArray[$index] =~ s/^\s//g;
					while($index < $ArraySize)
					{
						print "<!-- " . $$dataref{unique_id} . " = (" . $SplitArray[$index] . ") -->\n" if $Debug eq '1';
						if ($SplitArray[$index++] eq $$dataref{unique_id})
							{
								$found = "Yes";
							}
					}


					if ($PrimaryCategory eq $$dataref{unique_id})
						{
							if ($previous_category ne $$dataref{category}) 
								{
									print "                          <input type=\"radio\" name=\"primary_category\" value=\"" . $$dataref{unique_id} . "\" checked><span class=\"BlackTextLargeBold\">" . $$dataref{category} . "</span><br>\n";
								}
							print "                          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"checkbox\" name=\"secondary_categories\" value=\"" . $$dataref{unique_id} . "\">" . $$dataref{sub_category} . "<br>\n";
						}
					else
						{
							if ($previous_category ne $$dataref{category}) 
								{
									print "                          <input type=\"radio\" name=\"primary_category\" value=\"" . $$dataref{unique_id} . "\"><span class=\"BlackTextLargeBold\">" . $$dataref{category} . "</span><br>\n";
								}
							if ($found eq "Yes") 
								{
									print "                          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"checkbox\" name=\"secondary_categories\" value=\"" . $$dataref{unique_id} . "\" checked>" . $$dataref{sub_category} . "<br>\n";
								}
							else
								{
									print "                          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"checkbox\" name=\"secondary_categories\" value=\"" . $$dataref{unique_id} . "\">" . $$dataref{sub_category} . "<br>\n";
								}
						}

					if ($count++ eq 62) 
						{
                            print "                        </td><td class=\"AlignTop\">";
						}

					$previous_category = $$dataref{category};
				}
				}# END else (No db error) 
			else
				{
					print "ERROR ($DatabaseFunctions::DatabaseError): $SqlStatement Failed for first result set!\n";
					$status = $MSSQL::DBlib::dbh->dbcancel();
				}
}


exit 0;

#                                <a href="#" onClick="alert('Sorry, The Superuser cannot be deleted!\n\nThe email address you assign to any user must be unique to this or any other account. You may reassign an email address to the Superuser role by first changing the email address of the user to whom the email address was first assigned. You may then reassign this email address to the Superuser role.')">Delete</a>
