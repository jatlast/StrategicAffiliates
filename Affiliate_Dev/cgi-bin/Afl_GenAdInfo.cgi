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

my $ProgramName = "Afl_GenAdInfo.cgi";

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

				# Update login_info table to change the user's email address...
				my $SqlStatement = "afl_GetAdInfo \'$afl_cookie_email\', \'$afl_cookie_password\', \'$QueryStringHash{'ad_unique_id'}\'"; 

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
										print "<title>View Ad Info</title>\n";
										print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n";
										print "<SCRIPT language=\"javascript\" src=\"" . $Map{'ROOT'} . "/JavaScript/MyFunctions.js\"></SCRIPT>\n";
										print "<link href=\"" . $Map{'ROOT'} . "/css/" . $Map{'STYLE_SHEET'} . "\" rel=\"stylesheet\" type=\"text/css\">\n";
										print "</head>\n";
										print "<body bgcolor=\"eeeeee\">\n";

										print "      <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\n";
										print "        <TR>\n";
										print "          <TD align=\"center\">\n";
										print "            &nbsp;\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "      </TABLE>\n";
										print "      <TABLE width=\"90%\" border=\"0\" align=\"center\" cellpadding=\"3\" cellspacing=\"1\" bgcolor=\"#FFFFFF\">\n";
										print "        <TR>\n";
										print "          <TD colspan=\"2\" class=\"BlackTextMedium\">\n";
										print "            <STRONG>Ad Detail</STRONG>\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR bgcolor=\"#ffffff\">\n";
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
										print "        <TR class=\"BG2Text2\">\n";
										print "          <TD>\n";
										print "            Link Status\n";
										print "          </TD>\n";
										print "          <TD>\n";
										print "            " . $$dataref{is_ad_active} . "\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BlackTextMedium\">\n";
										print "          <TD>\n";
										print "            Link ID / Name\n";
										print "          </TD>\n";
										print "          <TD>\n";
										print "            " . $$dataref{ad_unique_id} . " / " . $$dataref{ad_name} . "\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BG2Text2\">\n";
										print "          <TD>\n";
										print "            Link Type / Size\n";
										print "          </TD>\n";
										print "          <TD>\n";
										# Banners....
										if($$dataref{ad_type} eq "1")
											{
												print "            Banner / " . $$dataref{banner_pixel_width} . " x " . $$dataref{banner_pixel_height} . "\n";
											}
										# Text Link....
										elsif($$dataref{ad_type} eq "2")
											{
												print "            Text Link / N/A\n";
											}
										# Splash....
										elsif($$dataref{ad_type} eq "3")
											{
												print "            HTML Table for Start Page / N/A\n";
											}
										# HTML Mail....
										elsif($$dataref{ad_type} eq "4")
											{
												print "            Emailable HTML / N/A\n";
											}
										# Unknown....
										else
											{
												print "            N/A / N/A\n";
											}

										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BlackTextMedium\">\n";
										print "          <TD>\n";
										print "            Description\n";
										print "          </TD>\n";
										print "          <TD>\n";
										print "            " . $$dataref{ad_description} . "\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BG2Text2\">\n";
										print "          <TD>\n";
										print "            Destination\n";
										print "          </TD>\n";
										print "          <TD>\n";
										# Banner Ad or Text Link....
										if($$dataref{ad_type} eq "1" or $$dataref{ad_type} eq "2")
											{
												print "            <A href=\"" . $$dataref{target_url} . "\" target=\"_blank\">View Destination Page</A>&nbsp;\n";
											}
										else
											{
												print "            N/A\n";
											}
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BlackTextMedium\">\n";
										print "          <TD>\n";
										print "            3 Month EPC\n";
										print "          </TD>\n";
										print "          <TD>\n";
										print "            N/A\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BG2Text2\">\n";
										print "          <TD>\n";
										print "            7 Day EPC\n";
										print "          </TD>\n";
										print "          <TD>\n";
										print "            N/A\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BlackTextMedium\">\n";
										print "          <TD>\n";
										print "            Advertiser\n";
										print "          </TD>\n";
										print "          <TD>\n";
										print "            <A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAffiliateProgramInfo.cgi?afl_unique_id=" . $$dataref{afl_unique_id} . "',900,850);\" class=\"NavText\">" . $$dataref{display_name} . "</a>\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR class=\"BG2Text2\">\n";
										print "          <TD>\n";
										print "            Category\n";
										print "          </TD>\n";
										print "          <TD>\n";
										print "            " . $$dataref{site_category} . "\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "        <TR>\n";
										print "          <TD align=\"center\" colspan=\"2\" bgcolor=\"#ffffff\">\n";
										print "            <TABLE cellspacing=\"0\" cellpadding=\"0\">\n";
										# If Ad is Active....
										if($$dataref{is_ad_active} !~ m/Not Active/)
											{
												print "              <TR>\n";
												print "                <TD>\n";
												print "                  <TABLE cellspacing=\"0\" cellpadding=\"1\" width=\"10\" border=\"0\">\n";
												print "                    <TR>\n";
												print "                      <TD>\n";
												print "                        <FORM action=\"" . $Map{'CGIBIN'} . "/Afl_GenAdHtmlInfo.cgi\" method=\"post\">\n";
												print "                          <INPUT type=\"hidden\" name=\"ad_unique_id\" value=\"" . $$dataref{ad_unique_id} . "\"> \n";
												print "                          <TABLE>\n";
												print "                            <TR>\n";
												print "                              <TD>\n";
												print "                                <INPUT type=\"submit\" value=\"Get HTML\" name=\"submit2\">\n";
												print "                              </TD>\n";
												print "                            </TR>\n";
												print "                          </TABLE>\n";
												print "                        </FORM>\n";
												print "                      </TD>\n";
												print "                      <TD>\n";
												print "                        &nbsp;\n";
												print "                      </TD>\n";
												print "                    </TR>\n";
												print "                  </TABLE>\n";
												print "                </TD>\n";
												print "              </TR>\n";
											}

										print "              <TR bgcolor=\"#ffffff\">\n";
										print "                <TD colspan=\"2\" align=\"center\">\n";
										print "                  <FORM>\n";
										print "                  </FORM>\n";
										print "                  <TABLE cellspacing=\"0\" cellpadding=\"1\" width=\"10\" border=\"0\">\n";
										print "                    <TR>\n";
										print "                      <TD>\n";
                                        print "                        <input class=\"buttonDefault\" onClick=\"window.close();\" type=\"button\" name=\"button2\" value=\"Close\" /> \n";
										print "                      </TD>\n";
										print "                    </TR>\n";
										print "                  </TABLE>\n";
										print "                </TD>\n";
										print "              </TR>\n";
										print "            </TABLE>\n";
										print "          </TD>\n";
										print "        </TR>\n";
										print "      </TABLE>\n";
										
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
