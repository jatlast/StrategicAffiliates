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

my $ProgramName = "Afl_GenAffiliateChoices.cgi";

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
		my $SqlStatement = "afl_GenAffiliateChoices \'$afl_cookie_email\', \'$afl_cookie_password\'"; 

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
						print "      <table width=\"100%\" border=\"1\" cellpadding=\"3\" cellspacing=\"0\" bordercolor=\"#999999\">\n";
						print "        <tr> \n";
						print "          <td bgcolor=\"white\" class=\"AlignCenter\">Advertiser</td>\n";
						print "          <td bgcolor=\"white\" class=\"AlignCenter\">3 Month EPC</td>\n";
						print "          <td bgcolor=\"white\" class=\"AlignCenter\">7 Day EPC</td>\n";
						print "          <td bgcolor=\"white\" class=\"AlignCenter\">Sale | Lead</td>\n";
						print "          <td bgcolor=\"white\" class=\"AlignCenter\">Status</td>\n";
						print "          <td bgcolor=\"white\" class=\"AlignCenter\">Category</td>\n";
						print "        </tr>\n";
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
								if($count++ % 2 eq 0)
									{
										$bg_color = "lightgrey";
									}
								else
									{
										$bg_color = "white";
									}
								print "        <tr> \n";
								print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">";
								print "				<p><A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAffiliateProgramInfo.cgi?afl_unique_id=" . $$dataref{unique_id} . "',555,750);\" class=\"NavText\">";
								if($$dataref{banner_url_150x40} ne "" and $$dataref{banner_url_150x40} ne " ")
									{
										print "				<img src=\"" . $$dataref{banner_url_150x40} . "\" border=\"0\" width=\"150\" height=\"40\">";
									}
								print "				<BR>" . $$dataref{display_name} . "";
								print "				</a></p>\n";
								print "			 </td>\n";
								print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">N/A</td>\n";
								print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">N/A</td>\n";
								
								# Sale Range...
								print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignLeft\">\n";
								if($$dataref{sales})
									{
											print "				Sale: <A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAffiliateProgramInfo.cgi?afl_unique_id=" . $$dataref{unique_id} . "',555,750);\" class=\"NavText\">" . $$dataref{sales} . "</a><BR>\n";
									}
								else
									{
											print "&nbsp;<BR>";
									}
								# Lead Range...
								if($$dataref{leads})
									{
										print "				Lead: <A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAffiliateProgramInfo.cgi?afl_unique_id=" . $$dataref{unique_id} . "',555,750);\" class=\"NavText\">" . $$dataref{leads} . "</a><BR>\n";
									}
								else
									{
										print "&nbsp;<BR>";
									}
								# Incentive...
								print "			<SPAN class=\"RedTextMedium\">" . $$dataref{plus_incentives} . "</SPAN><BR>\n";
								print "			</td>\n";
								print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">\n";
								if($$dataref{relationship_status} eq "Active")
									{
										print "				" . $$dataref{relationship_status} . "\n";
									}
								else
									{
										print "				<A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAffiliateProgramInfo.cgi?afl_unique_id=" . $$dataref{unique_id} . "',555,750);\" class=\"NavText\">" . $$dataref{relationship_status} . "</a>\n";
									}
								print "			</td>\n";
								print "          <td bgcolor=\"" . $bg_color . "\" class=\"AlignCenter\">" . $$dataref{site_category} . "</td>\n";
								print "        </tr>\n";
							}
							print "      </table>\n";
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
