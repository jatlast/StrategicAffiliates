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

my $ProgramName = "Afl_GenAdHtmlInfo.cgi";

my $count = 0;

my @site_name_array;
my @site_id_array;

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

				# Update login_info table to change the user's email address...
				my $SqlStatement = "afl_GetAdHtmlInfo \'$afl_cookie_email\', \'$afl_cookie_password\', \'$QueryStringHash{'ad_unique_id'}\'"; 

				if($QueryStringHash{'site_id'})
					{
						$SqlStatement = $SqlStatement . ", \'$QueryStringHash{'site_id'}\'"; 
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
								my $count = 0;
								# Prevent infinite loop...
								while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
									{
										# Since there is no global DB error check get 
										# all database fields returned by the query...

										$site_name_array[$count]	= $$dataref{site_name};
										$site_id_array[$count]		= $$dataref{site_id};
										$count++;
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
										print "<head>\n";
										print "<title>View Ad Info</title>\n";
										print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n";
										print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/MyFunctions.js\"></SCRIPT>\n";
										print "<link href=\"" . $Map{'ROOT'} . "/css/" . $Map{'STYLE_SHEET'} . "\" rel=\"stylesheet\" type=\"text/css\">\n";
										print "</head>\n";
										print "<body bgcolor=\"eeeeee\">\n";

                                        print "    <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\n";
                                        print "      <TR>\n";
                                        print "        <TD align=\"center\">\n";
                                        print "          &nbsp;\n";
                                        print "        </TD>\n";
                                        print "      </TR>\n";
                                        print "    </TABLE>\n";
                                        print "      <TABLE width=\"90%\" class=\"default\" border=\"0\" align=\"center\" cellpadding=\"3\" cellspacing=\"0\" bgcolor=\"#FFFFFF\">\n";
                                        print "        <TR>\n";
                                        print "          <TD class=\"BlackTextMedium\" colspan=\"2\">\n";
                                        print "            Get Link HTML\n";
                                        print "          </TD>\n";
                                        print "        </TR>\n";
                                        print "        <TR>\n";
										# Banners....
										if($$dataref{ad_type} eq "1")
											{
												print "          <td colspan=\"2\" bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">";
												print "				<img src=\"" . $Map{'ROOT'} . "/Banners/" . $$dataref{ad_unique_id} . $$dataref{banner_dot_extension} . "\" width=\"" . $$dataref{banner_pixel_width} . "\" height=\"" . $$dataref{banner_pixel_height} . "\"><BR>" . $$dataref{banner_pixel_width} . " x " . $$dataref{banner_pixel_height} . " Banner Ad</a>";
												print "			 </td>\n";
											}
										# Text Link....
										elsif($$dataref{ad_type} eq "2")
											{
												print "          <td colspan=\"2\" bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{text_link_text} . "<BR>Text Link</td>\n";
											}
										# Splash....
										elsif($$dataref{ad_type} eq "3")
											{
												print "          <td colspan=\"2\" bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{html_block} . "<BR>HTML Table for Start Page</td>\n";
											}
										# HTML Mail....
										elsif($$dataref{ad_type} eq "4")
											{
												print "          <td colspan=\"2\" bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{html_block} . "<BR>Emailable HTML</td>\n";
											}
										# Unknown....
										else
											{
												print "          <td colspan=\"2\" bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">&nbsp;</td>\n";
											}
                                        print "        </TR>\n";
                                        print "    <FORM action=\"" . $Map{'CGIBIN'} . "/Afl_GenAdHtmlInfo.cgi\" method=\"post\" name=\"GetHtmlForm\">\n";
                                        print "      <INPUT type=\"hidden\" name=\"ad_unique_id\" value=\"" . $$dataref{ad_unique_id} . "\"> \n";
                                        print "        <TR>\n";
                                        print "          <TD class=\"BG2Text2\">\n";
                                        print "            The tracking code is for\n";
                                        print "          </TD>\n";
                                        print "          <TD class=\"BG2Text2\">\n";
                                        print "            <SELECT name=\"site_id\" onchange=\"form.submit();return false;\">\n";
										my $count = 0;
										foreach my $site_name (@site_name_array) 
											{
												print "              <OPTION value=\"" . $site_id_array[$count] . "\">\n";
												print "                " . $site_name . "\n";
												print "              </OPTION>\n";
												$count++;
											}

                                        print "            </SELECT>\n";
                                        print "          </TD>\n";
                                        print "        </TR>\n";
										# Set window behavior for clicks
										print "        <TR>\n";
										print "          <TD class=\"BlackTextMedium\">\n";
										print "            Set click target window.\n";
										print "          </TD>\n";
										print "          <TD class=\"BlackTextMedium\">\n";

										if($QueryStringHash{'click_target'})
											{
												if($QueryStringHash{'click_target'} eq "1")
													{
														print "            <INPUT type=\"radio\" name=\"click_target\" value=\"1\" checked onclick=\"form.submit();return false;\">Same Window\n";
													}
												else
													{
														print "            <INPUT type=\"radio\" name=\"click_target\" value=\"1\" onclick=\"form.submit();return false;\">Same Window\n";
													}
												if($QueryStringHash{'click_target'} eq "2")
													{
														print "            <INPUT type=\"radio\" name=\"click_target\" value=\"2\" checked onclick=\"form.submit();return false;\">New Window\n";
													}
												else
													{
														print "            <INPUT type=\"radio\" name=\"click_target\" value=\"2\" onclick=\"form.submit();return false;\">New Window\n";
													}
												# Banner Ad or Text Link....
												if($$dataref{ad_type} eq "1" and $QueryStringHash{'up_or_under'})
													{
													if($QueryStringHash{'click_target'} eq "-1")
														{
															print "            <INPUT type=\"radio\" name=\"click_target\" value=\"-1\" checked onclick=\"form.submit();return false;\">Parent Window\n";
														}
													else
														{
															print "            <INPUT type=\"radio\" name=\"click_target\" value=\"-1\" onclick=\"form.submit();return false;\">Parent Window\n";
														}
													}
											}
										else
											{
													# Banner Ad or Text Link....
													if($$dataref{ad_type} eq "1" and $QueryStringHash{'up_or_under'})
														{
															print "            <INPUT type=\"radio\" name=\"click_target\" value=\"1\" onclick=\"form.submit();return false;\">Same Window\n";
															print "            <INPUT type=\"radio\" name=\"click_target\" value=\"2\" checked onclick=\"form.submit();return false;\">New Window\n";
															print "            <INPUT type=\"radio\" name=\"click_target\" value=\"-1\" onclick=\"form.submit();return false;\">Parent Window\n";
														}
													else
														{
															print "            <INPUT type=\"radio\" name=\"click_target\" value=\"1\" onclick=\"form.submit();return false;\">Same Window\n";
															print "            <INPUT type=\"radio\" name=\"click_target\" value=\"2\" onclick=\"form.submit();return false;\">New Window\n";
														}
											}

										print "			<BR><FONT color=\"red\">Choose where you want the user's window to open when they click an ad..</FONT>\n";
										print "          </TD>\n";
										print "        </TR>\n";
										# Banner Ad or Text Link....
										if($$dataref{ad_type} eq "1")
											{
												print "        <TR>\n";
												print "          <TD class=\"BG2Text2\">\n";
												print "            Set ad to open in a new browser window?\n";
												print "          </TD>\n";
												print "          <TD class=\"BG2Text2\">\n";

												if($QueryStringHash{'up_or_under'})
													{
														if($QueryStringHash{'up_or_under'} eq "1")
															{
																print "            <INPUT type=\"radio\" name=\"up_or_under\" value=\"1\" checked onclick=\"form.submit();return false;\">Pop Up\n";
															}
														else
															{
																print "            <INPUT type=\"radio\" name=\"up_or_under\" value=\"1\" onclick=\"form.submit();return false;\">Pop Up\n";
															}
														if($QueryStringHash{'up_or_under'} eq "-1")
															{
																print "            <INPUT type=\"radio\" name=\"up_or_under\" value=\"-1\" checked onclick=\"form.submit();return false;\">Pop Under\n";
															}
														else
															{
																print "            <INPUT type=\"radio\" name=\"up_or_under\" value=\"-1\" onclick=\"form.submit();return false;\">Pop Under\n";
															}
													}
												else
													{
															print "            <INPUT type=\"radio\" name=\"up_or_under\" value=\"1\" onclick=\"form.submit();return false;\">Pop Up\n";
															print "            <INPUT type=\"radio\" name=\"up_or_under\" value=\"-1\" onclick=\"form.submit();return false;\">Pop Under\n";
													}

												print "			<BR><FONT color=\"red\">Choose <i>only</i> if you want your ad to pop up or pop under.</FONT>\n";
												print "          </TD>\n";
												print "        </TR>\n";
												print "        <TR>\n";
												print "          <TD class=\"BlackTextMedium\">\n";
												print "           Set ad to Pop Up/Under only once?\n";
												print "          </TD>\n";
												print "          <TD class=\"BlackTextMedium\">\n";
												if($QueryStringHash{'only_once'})
													{
														if($QueryStringHash{'only_once'} eq "1")
															{
																print "            <INPUT type=\"checkbox\" name=\"only_once\" value=\"1\" checked onclick=\"form.submit();return false;\">Yes\n";
															}
														else
															{
																print "            <INPUT type=\"checkbox\" name=\"only_once\" value=\"1\" onclick=\"form.submit();return false;\">Yes\n";
															}
													}
												else
														{
														print "            <INPUT type=\"checkbox\" name=\"only_once\" value=\"1\" onclick=\"form.submit();return false;\">Yes\n";
													}

												print "          </TD>\n";
												print "        </TR>\n";


											}
										# Banners or Text Links...
										if($$dataref{ad_type} eq "1" or $$dataref{ad_type} eq "2")
											{
												print "        <TR>\n";
												print "          <TD class=\"BG2Text2\">\n";
												print "            Set ad to rotate?\n";
												print "          </TD>\n";
												print "          <TD class=\"BG2Text2\">\n";
												if($QueryStringHash{'rotate'})
													{
														if($QueryStringHash{'rotate'} eq "1")
															{
																print "            <INPUT type=\"checkbox\" name=\"rotate\" value=\"1\" checked onclick=\"form.submit();return false;\">Yes\n";
															}
														else
															{
																print "            <INPUT type=\"checkbox\" name=\"rotate\" value=\"1\" onclick=\"form.submit();return false;\">Yes\n";
															}
													}
												else
													{
														print "            <INPUT type=\"checkbox\" name=\"rotate\" value=\"1\" onclick=\"form.submit();return false;\">Yes\n";
													}

												print "          </TD>\n";
												print "        </TR>\n";
											}
										# Dynamic pages...
										if($$dataref{ad_type} eq "3" or $$dataref{ad_type} eq "4")
											{
												print "        <TR>\n";
												print "          <TD class=\"BG2Text2\">\n";
												print "            Your Site ID:\n";
												print "          </TD>\n";
												print "          <TD class=\"BG2Text2\">\n";
											}
										else
											{
												print "        <TR>\n";
												print "          <TD class=\"BlackTextMedium\">\n";
												print "            Your Site ID:\n";
												print "          </TD>\n";
												print "          <TD class=\"BlackTextMedium\">\n";
											}
                                        print "            " . $site_id_array[0] . "\n";
                                        print "          </TD>\n";
                                        print "        </TR>\n";
										# Dynamic pages...
										if($$dataref{ad_type} eq "3" or $$dataref{ad_type} eq "4")
											{
												print "        <TR>\n";
												print "          <TD class=\"BlackTextMedium\">\n";
		                                        print "            Ad ID:\n";
												print "          </TD>\n";
												print "          <TD class=\"BlackTextMedium\">\n";
											}
										else
											{
												print "        <TR>\n";
												print "          <TD class=\"BG2Text2\">\n";
		                                        print "            Ad ID:\n";
												print "          </TD>\n";
												print "          <TD class=\"BG2Text2\">\n";
											}
                                        print "            " . $$dataref{ad_unique_id} . "\n";
                                        print "          </TD>\n";
                                        print "        </TR>\n";
										# Dynamic pages...
										if($$dataref{ad_type} eq "3" or $$dataref{ad_type} eq "4")
											{
												print "        <TR>\n";
												print "          <TD class=\"BG2Text2\" colspan=\"2\">\n";
											}
										else
											{
												print "        <TR>\n";
												print "          <TD class=\"BlackTextMedium\" colspan=\"2\">\n";
											}
                                        print "            Copy and paste the following HTML code into your web pages.\n";
                                        print "            <BR>\n";
                                        print "             <TEXTAREA name=\"textfield\" cols=\"70\" rows=\"10\" wrap=\"on\" class=\"textArea\">";

                                        print "&lt;script type=\"text/javascript\" src=\"" . $Map{'CGIBIN'} . "/" . $Map{'AFL_RETRIEVE'} . "?auid=" . $$dataref{ad_unique_id} . "&sid=" . $site_id_array[0] . "&acid=" . $$dataref{afl_account_id};

										if($QueryStringHash{'rotate'})
											{
												if($QueryStringHash{'rotate'} eq "1")
													{
														print "&r=1";
													}
												else
													{
														print "&r=0";
													}
											}
										else
											{
												print "&r=0";
											}

										if($QueryStringHash{'up_or_under'})
											{
												print "&p=" . $QueryStringHash{'up_or_under'} . "";
											}
										else
											{	
												# default values is NO popup/under...
												print "&p=0";
											}

										if($QueryStringHash{'only_once'})
											{
												print "&o=" . $QueryStringHash{'only_once'} . "\"";
											}
										else
											{
												print "&o=0";
											}

										if($QueryStringHash{'click_target'})
											{
												print "&w=" . $QueryStringHash{'click_target'} . "\"";
											}
										else
											{
												print "&w=1\"";
											}

                                        print "&gt;&lt;/script&gt;\n";
										print "&lt;noscript&gt;&lt;FONT color=\"#FF0000\"&gt;Please enable JavaScript!!&lt;/FONT&gt;&lt;IMG src=\"" . $Map{'CGIBIN'} . "/" . $Map{'AFL_RETRIEVE'} . "?auid=" . $$dataref{ad_unique_id} . "&sid=" . $site_id_array[0] . "&acid=" . $$dataref{afl_account_id} . "&js=0\" width=\"1\" height=\"1\" border=\"0\">&lt;/noscript&gt;";

										print "</TEXTAREA>\n";
                                        print "          </TD>\n";
                                        print "        </TR>\n";
                                        print "        <TR>\n";
                                        print "          <TD class=\"BG2Text2\" colspan=\"2\">\n";
                                        print "            <FONT color=\"red\">NOTE</FONT>: You must include all the above html in your links. Any missing html will prevent the link from tracking properly and result in a loss of commissions.\n";
                                        print "          </TD>\n";
                                        print "        </TR>\n";
                                        print "        <TR>\n";
                                        print "          <TD colspan=\"2\" align=\"center\">\n";
                                        print "            <TABLE cellspacing=\"0\" cellpadding=\"1\" width=\"10\" border=\"0\">\n";
                                        print "              <TR>\n";
                                        print "                <TD>\n";
                                        print "                  <INPUT type=\"button\" value=\"Highlight All\" onclick=\"javascript:this.form.textfield.focus();this.form.textfield.select()\">\n";
                                        print "                </TD>\n";
										print "                <TD>\n";
										print "					 <input type=\"button\" value=\"Clear Form\" onclick=\"javascript:window.location.replace('" . $Map{'CGIBIN'} . "/Afl_GenAdHtmlInfo.cgi?ad_unique_id=" . $$dataref{ad_unique_id} . "')\">\n";
										print "                </TD>\n";
                                        print "              </TR>\n";
                                        print "              <TR>\n";
	                                    print "					<TD colspan=\"2\" align=\"center\">\n";
                                        print "                  <INPUT type=\"button\" value=\"Close\" name=\"as_action\" onclick=\"window.close()\">\n";
                                        print "                </TD>\n";
                                        print "              </TR>\n";

                                        print "            </TABLE>\n";
                                        print "          </TD>\n";
                                        print "        </TR>\n";
                                        print "      </TABLE>\n";
                                        print "    </FORM>\n";
                                        										
									}
							}
						else
							{
								$status = $MSSQL::DBlib::dbh->dbcancel();
								print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to view ad info for ($afl_cookie_email).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
							}
					}
			}
	}
#End HTML...
print "</HTML>\n";
exit 0;
