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

my $ProgramName = "Afl_EditWebsiteInfo.cgi";

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
				my @QueryStringParams = CGI::param();
				my %QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

				if($QueryStringHash{'submit'} eq "Delete")
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_DeleteWebsiteInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'site_id'}\'\
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
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your Website Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				elsif($QueryStringHash{'submit'} eq "Save")
					{
						my @secondary_categories = CGI::param('secondary_categories');
						my $index = 0;
						foreach my $secondary_category (@secondary_categories) 
							{
								my $database_column_name = "secondary_category_" . ($index + 1);
								$QueryStringHash{$database_column_name} = @secondary_categories[$index];
								$index++;
								print "<!-- database_column_name = ($database_column_name) -->\n" if $DebugThisAp eq "1";
							}
						
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
						##########################################################

						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_UpdateWebsiteInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'site_id'}\'\
																		, \'$QueryStringHash{'site_name'}\'\
																		, \'$QueryStringHash{'site_url'}\'\
																		, \'$QueryStringHash{'site_description'}\'\
																		, \'$QueryStringHash{'primary_category'}\'\
																		, \'$QueryStringHash{'secondary_category_1'}\'\
																		, \'$QueryStringHash{'secondary_category_2'}\'\
																		, \'$QueryStringHash{'secondary_category_3'}\'\
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
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your Website Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				elsif($QueryStringHash{'submit'} eq "Create")
					{
						my @secondary_categories = CGI::param('secondary_categories');
						my $index = 0;
						foreach my $secondary_category (@secondary_categories) 
							{
								my $database_column_name = "secondary_category_" . ($index + 1);
								$QueryStringHash{$database_column_name} = @secondary_categories[$index++];
								print "<!-- database_column_name = ($database_column_name) -->\n" if $DebugThisAp eq "1";
							}
						
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
						##########################################################

						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_CreateNewWebsiteInfo \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'site_name'}\'\
																		, \'$QueryStringHash{'site_url'}\'\
																		, \'$QueryStringHash{'site_description'}\'\
																		, \'$QueryStringHash{'primary_category'}\'\
																		, \'$QueryStringHash{'secondary_category_1'}\'\
																		, \'$QueryStringHash{'secondary_category_2'}\'\
																		, \'$QueryStringHash{'secondary_category_3'}\'\
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
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your Website Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				if($QueryStringHash{'submit'} eq "Add")
					{
							print "<head>\n";
							print "<title>Edit Payment Information</title>\n";
							print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n";
							print "<link href=\"" . $Map{'ROOT'} . "/css/" . $Map{'STYLE_SHEET'} . "\" rel=\"stylesheet\" type=\"text/css\">\n";
							print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/MyFunctions.js\"></SCRIPT>\n";
							print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/Afl_EditWebsiteInfo.js\"></SCRIPT>\n";
							print "</head>\n";
							print "<body bgcolor=\"eeeeee\">\n";
							print "<table width=\"700\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\" bgcolor=\"#999999\">\n";
							print "  <tr>\n";
							print "    <td><table width=\"700\" border=\"0\" cellpadding=\"3\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
							print "        <form name=\"WebsiteInfoForm\" method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\" onsubmit=\"return check_Afl_EditWebsiteInfoForm(this);\">\n";
							print "          <tr> \n";
							print "            <td colspan=\"3\" class=\"BlackTextLarge3Bold\"><strong>&nbsp;Edit Website Information</strong></td>\n";
							print "          </tr>\n";
							print "          <tr> \n";
							print "            <td colspan=\"3\"><IMG src=\"" . $Map{'ROOT'} . "/images/blackSpacer.gif\" width=\"100%\" height=\"2\"></td>\n";
							print "          </tr>\n";
							print "          <tr> \n";
							print "            <td colspan=\"3\"><font color=\"red\">&nbsp;</font>&nbsp;</td>\n";
							print "          </tr>\n";
							print "          <tr> \n";

							print "          <tr class=\"BlackTextMedium\"> \n";
							print "            <td>Site Name</td>\n";
							print "            <td> \n";
							print "              <input class=\"formFieldStatic\" type=\"text\" name=\"site_name\" size=\"40\" maxlength=\"60\" value=\"\"> \n";
							print "            </td>\n";
							print "          </tr>\n";
							print "          <tr class=\"BG2Text2\"> \n";
							print "            <td>Site URL</td>\n";
							print "            <td> \n";
							print "              <input class=\"formFieldStatic\" type=\"text\" name=\"site_url\" size=\"40\" maxlength=\"125\" value=\"\"> \n";
							print "            </td>\n";
							print "          </tr>\n";
							print "          <tr class=\"BlackTextMedium\"> \n";
							print "            <td>Description<br>\n";
							print "              Describe your site in 1500 characters or less. </td>\n";
							print "            <td> \n";
							print "              <textarea class=\"textArea\" name=\"site_description\" cols=\"40\" rows=\"4\" onblur=\" return CheckLength(this.value)\"></textarea> \n";
							print "            </td>\n";
							print "          </tr>\n";
							print "          <tr class=\"BG2Text2\"> \n";
							print "            <td height=\"1260\" colspan=\"2\"> \n";
							print "              <p>&nbsp;\n";
							print "              <p><span class=\"BlackTextLargeBold\">Site Categories</span> \n";
							print "              <table width=\"80%\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\">\n";
							print "                <tr> \n";
							print "                  <td width=\"597\"> <table border=\"0\" width=\"100%\" cellpadding=\"3\" cellspacing=\"0\">\n";
							print "                      <tr> \n";
							print "                        <td colspan=\"2\"> \n";
							print "                          <p><span class=\"BlackTextMedium\">Select 1 primary category \n";
							print "                            (with radio button on left side,) and... check up \n";
							print "                            to 3 general categories for your site (on right side.) \n";
							print "                            </span><br>\n";
							print "                            <br>\n";
							print "                            <span class=\"BlackTextSmall\">Information used to match \n";
							print "                            your program with the most profitable partners. </span></p>\n";
							print "                          </td>\n";
							print "                      </tr>\n";
							print "                      <tr> \n";
							print "                        <td class=\"AlignTop\">";

							&Print_Website_Category_Options("", "", $DebugThisAp, %Map);
					
							print "                        </td>\n";
							print "                      </tr>\n";

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
						my $SqlStatement = "afl_GetWebsiteInfo \'$afl_cookie_email\', \'$afl_cookie_password\', \'$QueryStringHash{'site_id'}\'"; 

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
												print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/Afl_EditWebsiteInfo.js\"></SCRIPT>\n";
                                                print "</head>\n";
                                                print "<body bgcolor=\"eeeeee\">\n";
                                                print "<table width=\"700\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\" bgcolor=\"#999999\">\n";
                                                print "  <tr>\n";
                                                print "    <td><table width=\"700\" border=\"0\" cellpadding=\"3\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
                                                print "        <form name=\"WebsiteInfoForm\" method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\" onsubmit=\"return check_Afl_EditWebsiteInfoForm(this);\">\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\" class=\"BlackTextLarge3Bold\"><strong>&nbsp;Edit Website Information</strong></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><IMG src=\"" . $Map{'ROOT'} . "/images/blackSpacer.gif\" width=\"100%\" height=\"2\"></td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";
                                                print "            <td colspan=\"3\"><font color=\"red\">&nbsp;</font>&nbsp;</td>\n";
                                                print "          </tr>\n";
                                                print "          <tr> \n";

                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td>Site ID</td>\n";
                                                print "            <td>" . $$dataref{site_id} . "</td>\n";
                                                print "            <input type=\"hidden\" name=\"site_id\" value=\"" . $$dataref{site_id} . "\"> \n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>Site Name</td>\n";
                                                print "            <td> \n";
                                                print "              <input class=\"formFieldStatic\" type=\"text\" name=\"site_name\" size=\"40\" maxlength=\"60\" value=\"" . $$dataref{site_name} . "\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td>Site URL</td>\n";
                                                print "            <td> \n";
                                                print "              <input class=\"formFieldStatic\" type=\"text\" name=\"site_url\" size=\"40\" maxlength=\"125\" value=\"" . $$dataref{site_url} . "\"> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BlackTextMedium\"> \n";
                                                print "            <td>Description<br>\n";
                                                print "              Describe your site in 1500 characters or less. </td>\n";
                                                print "            <td> \n";
                                                print "              <textarea class=\"textArea\" name=\"site_description\" cols=\"40\" rows=\"4\" onblur=\" return CheckLength(this.value)\">" . $$dataref{site_description} . "</textarea> \n";
                                                print "            </td>\n";
                                                print "          </tr>\n";
                                                print "          <tr class=\"BG2Text2\"> \n";
                                                print "            <td height=\"1260\" colspan=\"2\"> \n";
                                                print "              <p>&nbsp;\n";
                                                print "              <p><span class=\"BlackTextLargeBold\">Site Categories</span> \n";
                                                print "              <table width=\"80%\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\">\n";
                                                print "                <tr> \n";
                                                print "                  <td width=\"597\"> <table border=\"0\" width=\"100%\" cellpadding=\"3\" cellspacing=\"0\">\n";
                                                print "                      <tr> \n";
                                                print "                        <td colspan=\"2\"> \n";
                                                print "                          <p><span class=\"BlackTextMedium\">Select 1 primary category \n";
                                                print "                            (with radio button on left side,) and... check up \n";
                                                print "                            to 3 general categories for your site (on right side.) \n";
                                                print "                            </span><br>\n";
                                                print "                            <br>\n";
                                                print "                            <span class=\"BlackTextSmall\">Information used to match \n";
                                                print "                            your program with the most profitable partners. </span></p>\n";
                                                print "                          </td>\n";
                                                print "                      </tr>\n";
                                                print "                      <tr> \n";
                                                print "                        <td class=\"AlignTop\">";

												my $CSV = "";
												if($$dataref{secondary_category_1})
												{
													$CSV = $CSV . $$dataref{secondary_category_1};
												}
												if($$dataref{secondary_category_2})
												{
													$CSV = $CSV . "," . $$dataref{secondary_category_2};
												}
												if($$dataref{secondary_category_3})
												{
													$CSV = $CSV . "," . $$dataref{secondary_category_3};
												}
												&Print_Website_Category_Options($$dataref{primary_category}, $CSV, $DebugThisAp, %Map);
										
                                                print "                        </td>\n";
                                                print "                      </tr>\n";

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
										&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to edit website info for ($afl_cookie_email).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
									}
							}
					}
			}
	}
#End HTML...
print "</HTML>\n";

sub Print_Website_Category_Options
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
							if ($found eq "Yes") 
								{
									print "                          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"checkbox\" name=\"secondary_categories\" value=\"" . $$dataref{unique_id} . "\" checked>" . $$dataref{sub_category} . "<br>\n";
								}
							else
								{
									print "                          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"checkbox\" name=\"secondary_categories\" value=\"" . $$dataref{unique_id} . "\">" . $$dataref{sub_category} . "<br>\n";
								}
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
