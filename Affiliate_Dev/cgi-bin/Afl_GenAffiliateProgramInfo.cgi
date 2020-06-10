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

my $ProgramName = "Afl_GenAffiliateProgramInfo.cgi";

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

				if($QueryStringHash{'submit'} eq "Activate Program")
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_AddRelatedAffiliateProgram \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'afl_unique_id'}\'\
																		, \'$QueryStringHash{'receive_email'}\'\
																		"; 
						my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, $ProgramName, $SqlStatement, $DebugDatabaseFunctions);
						if($return_value eq "1")
							{
								# Update Cookie info...
								print "<HEAD>\n";
								print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
								print "    <!--\n";
								print "		opener.document.location.reload();\n";
								print "		window.location = \"" . $ProgramName . "?afl_unique_id=" . $QueryStringHash{'afl_unique_id'} . "\"\n";
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
						elsif($DatabaseFunctions::DatabaseError eq "1024")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">ERROR: You must deactivate an existing program before activating a new program.</FONT><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						else
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to save your Payment Information Canges.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				elsif($QueryStringHash{'submit'} eq "Deactivate Program")
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_RemoveRelatedAffiliateProgram \'$afl_cookie_email\'\
																		, \'$afl_cookie_password\'\
																		, \'$QueryStringHash{'afl_unique_id'}\'\
																		"; 
						my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, $ProgramName, $SqlStatement, $DebugDatabaseFunctions);
						if($return_value eq "1")
							{
								# Update Cookie info...
								print "<HEAD>\n";
								print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
								print "    <!--\n";
								print "		opener.document.location.reload();\n";
								print "		window.location = \"" . $ProgramName . "?afl_unique_id=" . $QueryStringHash{'afl_unique_id'} . "\"\n";
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
						elsif($DatabaseFunctions::DatabaseError eq "1024")
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "<FONT COLOR=\"#8B0000\">ERROR: You must deactivate an existing program before activating a new program.</FONT><BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n", $DebugUtilityFunctions, %Map);
							}
						else
							{
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "ERROR: Unable to Deactivate Program.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				else
					{
						# Update login_info table to change the user's email address...
						my $SqlStatement = "afl_GetAffiliateProgramInfo \'$afl_cookie_email\', \'$afl_cookie_password\', \'$QueryStringHash{'afl_unique_id'}\'"; 

						my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "GenAffiliateInfo");
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
								my $AffiliateUniqueID = "";
								my $activation_date = "";
								my $receive_email = "";
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
												$AffiliateUniqueID	= $$dataref{unique_id};
												$activation_date	= $$dataref{activation_date};
												$receive_email		= $$dataref{receive_email};
												if($DebugThisAp eq "1")
													{
														while( (my $Key, my $Value) = each(%$dataref) )
														{
															print "<FONT color=\"blue\">$Key</FONT> " if $DebugPrintColorHTML eq "1";
															if($Value)
																{
																	print "<FONT color=\"red\">$Value</FONT>\n" if $DebugPrintColorHTML eq "1";
																}
															else
																{
																	print "<BR>\n" if $DebugPrintColorHTML eq "1";
																}
															print "<!-- $Key = ";
															if($Value)
																{
																	print "($Value)";
																}
															print " -->\n";
														}                
													}	
												print "  <HEAD>\n";
												print "    <TITLE>\n";
												print "      " . $$dataref{site_url} . " Affiliate program\n";
												print "    </TITLE>\n";
												print "    <META http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n";
												print "    <LINK href=\"" . $Map{'ROOT'} . "/css/" . $Map{'STYLE_SHEET'} . "\" rel=\"stylesheet\" type=\"text/css\">\n";
												print "</HEAD>\n";
												print "  <BODY bgcolor=\"eeeeee\">\n";
												print "<table width=\"700\" border=\"0\" cellpadding=\"4\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
												print "	<form name=\"AffiliatePlan\" method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\">\n";
												print "	<input type=\"hidden\" name=\"afl_unique_id\" value=\"" . $AffiliateUniqueID . "\">\n";
												print "    <tr> \n";
												print "      <td colspan=\"2\"> <img src=\"" . $$dataref{banner_url} . "\"></td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td width=\"88%\"> <span class=\"BlackTextLargeBold\">Country:</span> <span class=\"BlackTextMedium\">" . $$dataref{country} . "</span> </td>\n";
												print "      <td width=\"12%\" rowspan=\"6\"> \n";
												print "		<p>&nbsp;</p>\n";
												print "        <p>&nbsp;</p>\n";
												print "        <p>&nbsp;</p>\n";
												print "	  </td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td class=\"BlackTextLargeBold\"> URL: <a href=\"" . $$dataref{site_url} . "\" class=\"NavText\">" . $$dataref{site_url} . "</a> \n";
												print "      </td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td> <span class=\"BlackTextLargeBold\">Joined Network:</span> <span class=\"BlackTextMedium\">" . $$dataref{creation_date} . "</span> </td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td> <span class=\"BlackTextLargeBold\">Category:</span> <span class=\"BlackTextMedium\">" . $$dataref{site_category} . "</span> </td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td>&nbsp;</td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td height=\"172\" class=\"AlignTop\"> <span class=\"BlackTextLargeBold\">Description:</span>" . $$dataref{plan_descriptions} . "</td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td colspan=\"2\">&nbsp;</td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td colspan=\"2\" align=\"center\" class=\"BlackTextLargeBold\">\n";
												if($activation_date !~ m/1900/)
													{
														print "	  Status: <span class=\"RedTextMedium\">Active</span> | Start Date: <span class=\"BlackTextMedium\">" . $$dataref{activation_date} . "</span>\n";
													}
												else
													{
														print "	  Status: <span class=\"RedTextMedium\">Not Active</span> | Start Date: <span class=\"BlackTextMedium\">N/A</span>\n";
													}
												print "	  </td>\n";
												print "    </tr>\n";
												print "    <tr> \n";
												print "      <td colspan=\"2\">&nbsp;</td>\n";
												print "    </tr>\n";
											}
									}
								else
									{
										$status = $MSSQL::DBlib::dbh->dbcancel();
										print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
										&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to edit User info for ($afl_cookie_email).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
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
								my $program_count = 1;
								while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
									{
										if($DebugThisAp eq "1")
											{
												while( (my $Key, my $Value) = each(%$dataref) )
												{
													print "<FONT color=\"blue\">$Key</FONT> " if $DebugPrintColorHTML eq "1";
													if($Value)
														{
															print "<FONT color=\"red\">$Value</FONT>\n" if $DebugPrintColorHTML eq "1";
														}
													else
														{
															print "<BR>\n" if $DebugPrintColorHTML eq "1";
														}
													print "<!-- $Key = ";
													if($Value)
														{
															print "($Value)";
														}
													print " -->\n";
												}                
											}	

												print "    <!-- aflpp (" . $$dataref{unique_id} . ") --> \n";
												print "    <tr> \n";
												print "      <td colspan=\"2\" align=\"center\"> <table width=\"100%\" border=\"0\" cellpadding=\"1\" cellspacing=\"0\">\n";
												print "          <tr> \n";
												print "            <td align=\"center\"> <TABLE width=\"500\" border=\"0\" cellpadding=\"0\" cellspacing=\"1\" bgcolor=\"#999999\">\n";
												print "                <TR> \n";
												print "                  <TD> <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
												print "                      <TR> \n";
												print "                        <TD width=\"602\"> <table width=\"100%\" border=\"0\" cellpadding=\"3\" cellspacing=\"3\">\n";
												print "                            <tr> \n";
												print "                              <td nowrap class=\"BlackTextLargeBold\">&nbsp;</td>\n";
												print "                              <td class=\"BlackTextMedium\">&nbsp;</td>\n";
												print "                            </tr>\n";
												print "                            <tr> \n";
												if($$dataref{action_type} eq "1")
													{
														print "                              <td nowrap class=\"BlackTextLargeBold\">$program_count. Action: <span class=\"RedTextMedium\">Sale</span></td>\n";
													}
												else
													{
														print "                              <td nowrap class=\"BlackTextLargeBold\">$program_count. Action: <span class=\"RedTextMedium\">Lead</span></td>\n";
													}
												print "                              <td class=\"BlackTextMedium\">" . $$dataref{action_name} . "</td>\n";
												print "                            </tr>\n";
												print "                            <tr> \n";
												print "                              <td class=\"BlackTextMedium\">Action Referral Period</td>\n";
												print "                              <td class=\"BlackTextMedium\">" . $$dataref{referral_period_in_days} . " day(s)</td>\n";
												print "                            </tr>\n";
												print "                            <tr> \n";
												print "                              <td class=\"BlackTextMedium\">Action Criteria </td>\n";
												print "                              <td class=\"BlackTextMedium\">" . $$dataref{action_description} . "</td>\n";
												print "                            </tr>\n";
												print "                            <tr> \n";
												print "                              <td class=\"BlackTextMedium\">Occurrences</td>\n";
												print "                              <td class=\"BlackTextMedium\">" . $$dataref{referral_occurences} . "</td>\n";
												print "                            </tr>\n";
												print "                            <tr> \n";
												print "                              <td class=\"BlackTextMedium\">Commission</td>\n";
												if($$dataref{commission_by_percentage} eq "1")
													{
														print "                              <td class=\"BlackTextMedium\">" . ($$dataref{commission} * 100) . "\%</td>\n";
													}
												else
													{
														print "                              <td class=\"BlackTextMedium\">\$" . $$dataref{commission} . "</td>\n";
													}
												print "                            </tr>\n";
												# Incentive programs if offered...
												if($$dataref{incentive_by_actions})
													{
														my $count = 1;
														while($count < 5)
														{
															my $IncentiveThreshold	= "incentive_threshold_"	. $count;
															my $IncentivePercent	= "incentive_percent_"		. $count;
															if($$dataref{$IncentiveThreshold} and $$dataref{$IncentivePercent})
																{
																	# The incentives are based on the number of actions...
																	if($$dataref{incentive_by_actions} eq 1)
																		{
																			print "                        <TR>\n";
																			print "                          <TD class=\"BlackTextMedium\">\n";
																			print "                            Performance Incentive $count.\n";
																			print "                          </TD>\n";
																			print "                          <TD class=\"BlackTextMedium\">\n";
																			print "                            For <SPAN class=\"BlackTextLargeBold\">Number of Actions</SPAN> greater than <SPAN class=\"BlackTextLargeBold\">" . $$dataref{$IncentiveThreshold} . "</SPAN> increase commission by <SPAN class=\"BlackTextLargeBold\">" . ($$dataref{$IncentivePercent} * 100) . "</SPAN>\%\n";
																			print "                          </TD>\n";
																			print "                        </TR>\n";
																		}
																	# The incentives are based on the number of actions...
																	elsif($$dataref{incentive_by_actions} eq 0)
																		{
																			print "                        <TR>\n";
																			print "                          <TD class=\"BlackTextMedium\">\n";
																			print "                            Performance Incentive $count.\n";
																			print "                          </TD>\n";
																			print "                          <TD class=\"BlackTextMedium\">\n";
																			print "                            For <SPAN class=\"BlackTextLargeBold\">Total Sales Dollars</SPAN> equal to or greater than <SPAN class=\"BlackTextLargeBold\">\$" . $$dataref{$IncentiveThreshold} . "</SPAN> increase commission by <SPAN class=\"BlackTextLargeBold\">" . ($$dataref{$IncentivePercent} * 100) . "\%</SPAN>\n";
																			print "                          </TD>\n";
																			print "                        </TR>\n";
																		}
																}
															$count++;
														}										
													}
												print "                            <tr> \n";
												print "                              <td>&nbsp;</td>\n";
												print "                              <td>&nbsp;</td>\n";
												print "                            </tr>\n";
												print "                          </table>\n";
												print "						</TD>\n";
												print "                      </TR>\n";
												print "                    </TABLE>\n";
												print "				  </TD>\n";
												print "                </TR>\n";
												print "              </TABLE>\n";
												print "			</td>\n";
												print "        </tr>\n";
												print "        <tr> \n";
												print "          <td>&nbsp;</td>\n";
												print "        </tr>\n";
												print "       </table> \n";
										$program_count++;
									}
									print "     <tr>\n";
									print "      <td colspan=\"2\" align=\"center\"> <TABLE width=\"500\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" bgcolor=\"#999999\">\n";
									print "          <TR> \n";
									print "            <TD height=\"54\"> <TABLE width=\"100%\" border=\"0\" cellpadding=\"2\" cellspacing=\"1\">\n";
									print "                <TR> \n";
									print "                  <TD width=\"115\" bgcolor=\"#FFFFFF\" class=\"BlackTextMedium\">Receive Email</TD>\n";
									if($receive_email eq "1")
										{
											print "                  <TD width=\"374\" bgcolor=\"#FFFFFF\"><input checked type=\"checkbox\" name=\"receive_email\" value=\"1\"></TD>\n";
										}
									else
										{
											print "                  <TD width=\"374\" bgcolor=\"#FFFFFF\"><input type=\"checkbox\" name=\"receive_email\" value=\"1\"></TD>\n";
										}
									print "                </TR>\n";
									print "                <TR bgcolor=\"#FFFFFF\"> \n";
									print "                  <TD colspan=\"2\" class=\"BlackTextMedium\">Please note that you \n";
									print "                    should check the box above to receive email notification &amp; \n";
									print "                    reminders of account activities &amp; events.</TD>\n";
									print "                </TR>\n";
									print "              </TABLE></TD>\n";
									print "          </TR>\n";
									print "        </TABLE> \n";
									print "    <tr> \n";
									print "      <td height=\"48\" colspan=\"2\" align=\"center\"> \n";
									if($activation_date !~ m/1900/)
										{
											print "        <input type=\"submit\" name=\"submit\" value=\"Deactivate Program\">\n";
										}
									else
										{
											print "        <input type=\"submit\" name=\"submit\" value=\"Activate Program\">\n";
										}
									print "	  </td>\n";
									print "   </tr>\n";
									print "    <tr valign=\"bottom\"> \n";
									print "      <td height=\"118\" colspan=\"2\" align=\"center\"> \n";
									print "        <p> \n";
									print "          <input onClick=\"window.close();\" type=\"button\" name=\"button2\" value=\"Close Window\">\n";
									print "        </p> \n";
									print "	  </td>\n";
									print "   </tr>\n";
									print "  </form>\n";
									print "</table>\n";
							}
						else
							{
								$status = $MSSQL::DBlib::dbh->dbcancel();
								print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
							}
						}
					}
			}
	}
#End HTML...
print "</HTML>\n";


exit 0;

#                                <a href="#" onClick="alert('Sorry, The Superuser cannot be deleted!\n\nThe email address you assign to any user must be unique to this or any other account. You may reassign an email address to the Superuser role by first changing the email address of the user to whom the email address was first assigned. You may then reassign this email address to the Superuser role.')">Delete</a>
