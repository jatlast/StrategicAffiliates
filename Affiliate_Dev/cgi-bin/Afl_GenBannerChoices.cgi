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

my $ProgramName = "Afl_GenBannerChoices.cgi";

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
		my $banner_count = "";

		# Update login_info table to change the user's email address...
		my $SqlStatement = "afl_GenBannerChoices \'$afl_cookie_email\', \'$afl_cookie_password\'"; 

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
				##########################
				# Get FIRST result set...
				# Affiliate ID and User Type...
				##########################
				# dbresults() must be called for each result set...
				$status = $MSSQL::DBlib::dbh->dbresults();
				if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
					{
						&UtilityFunctions::Afl_Print_HTML_Top(\1, \$ProgramName, \$DebugUtilityFunctions, \%Map);
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
								
								$banner_count = $$dataref{banner_count};

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
				if($banner_count > 0)
					{
						print "      <table width=\"100%\" border=\"1\" cellpadding=\"3\" cellspacing=\"0\" bordercolor=\"#999999\">\n";
						print "        <tr> \n";
						print "          <td colspan=\"6\" bgcolor=\"white\" class=\"BlackTextLargeBold\"><BR>You currently have " . $banner_count . " banner(s) to chose from.<BR></td>\n";
						print "        </tr>\n";
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
								my $count = 0;
								my $bg_color = "";
								# Prevent infinite loop...
								print "        <tr> \n";
								print "          <td bgcolor=\"white\" class=\"AlignCenter\">Link</td>\n";
								print "          <td bgcolor=\"white\" class=\"AlignCenter\">CTR</td>\n";
								print "          <td bgcolor=\"white\" class=\"AlignCenter\">Link ID</td>\n";
								print "          <td bgcolor=\"white\" class=\"AlignCenter\">Advertiser Home</td>\n";
								print "          <td bgcolor=\"white\" class=\"AlignCenter\">Status</td>\n";
								print "          <td bgcolor=\"white\" class=\"AlignCenter\">Get HTML</td>\n";
								print "        </tr>\n";
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
												$bg_color = "lightgrey";
											}
										else
											{
												$bg_color = "white";
											}
										print "        <tr> \n";
										# Banners....
										if($$dataref{ad_type} eq "1")
											{
												print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">";
												print "				<img src=\"" . $Map{'ROOT'} . "/Banners/" . $$dataref{ad_unique_id} . $$dataref{banner_dot_extension} . "\" width=\"" . $$dataref{banner_pixel_width} . "\" height=\"" . $$dataref{banner_pixel_height} . "\"><BR><A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAdInfo.cgi?ad_unique_id=" . $$dataref{ad_unique_id} . "',900,850);\" class=\"NavText\">" . $$dataref{banner_pixel_width} . " x " . $$dataref{banner_pixel_height} . " Banner Ad</a>";
												print "			 </td>\n";
											}
										# Text Link....
										elsif($$dataref{ad_type} eq "2")
											{
												print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{text_link_text} . "<BR><A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAdInfo.cgi?ad_unique_id=" . $$dataref{ad_unique_id} . "',900,850);\" class=\"NavText\">Text Link</a></td>\n";
											}
										# Splash....
										elsif($$dataref{ad_type} eq "3")
											{
												print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{html_block} . "<BR><A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAdInfo.cgi?ad_unique_id=" . $$dataref{ad_unique_id} . "',900,850);\" class=\"NavText\">HTML Table for Start Page</a></td>\n";
											}
										# HTML Mail....
										elsif($$dataref{ad_type} eq "4")
											{
												print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{html_block} . "<BR><A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAdInfo.cgi?ad_unique_id=" . $$dataref{ad_unique_id} . "',900,850);\" class=\"NavText\">Emailable HTML</a></td>\n";
											}
										# Unknown....
										else
											{
												print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">&nbsp;</td>\n";
											}
										if($$dataref{click_through_rate} > 0)
											{
												print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{click_through_rate} . "</td>\n";
											}
										else
											{
												print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">N/A</td>\n";
											}
										
										print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{ad_unique_id} . "</td>\n";
										print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\"><A href=\"javascript:OpenWindow('" . $$dataref{site_url} . "',900,850);\" class=\"NavText\">" . $$dataref{display_name} . "</a></td>\n";
										print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">\n";
										print "				<A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAffiliateProgramInfo.cgi?afl_unique_id=" . $$dataref{afl_unique_id} . "',555,750);\" class=\"NavText\">" . $$dataref{relationship_status} . "</a>\n";
										print "			</td>\n";

										print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\"><A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAdHtmlInfo.cgi?ad_unique_id=" . $$dataref{ad_unique_id} . "',555,750);\" class=\"NavText\">Get HTML</A></td>\n";
										print "        </tr>\n";

									}

									print "        <tr> \n";
									print "          <td colspan=\"5\">\n";
									print "				&nbsp;\n";
									print "          </td>\n";
									print "        </tr>\n";
									print "      </table>\n";
									&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
							}
						else
							{
								$status = $MSSQL::DBlib::dbh->dbcancel();
								print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
								&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
							}
					}	
				else
					{
						print "      <table width=\"100%\" border=\"1\" cellpadding=\"3\" cellspacing=\"0\" bordercolor=\"#999999\">\n";
						print "        <tr> \n";
						print "          <td>";
						print "				&nbsp;";
						print "			 </td>\n";
						print "        </tr>\n";
						print "        <tr> \n";
						print "          <td bgcolor=\"white\" class=\"BlackTextLargeBold\">";
						print "				In order to get banner ads you must first <A href=\"" . $Map{'CGIBIN'} . "/Afl_GenAffiliateChoices.cgi\" class=\"NavText\">activate one or more affiliate programs...</A>";
						print "			 </td>\n";
						print "        </tr>\n";
						print "        <tr> \n";
						print "          <td>";
						print "				&nbsp;";
						print "			 </td>\n";
						print "        </tr>\n";
						print "      </table>\n";
						&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
					}
			}
	}
#End HTML...
print "</HTML>\n";
exit 0;
