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
require "UtilityFunctions.pl";
require "GraphingFunctions.pl";

my $DebugThisAp				= "0";
my $DebugCgiFunctions 		= "0";
my $DebugDatabaseFunctions	= "0";
my $DebugUtilityFunctions	= "0";
my $DebugGraphingFunctionss = "1";

my $DebugPrintColorHTML	   = "0";

my $ProgramName = "Afl_Statistics.cgi";

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
		# Load the values passed in into the QueryStringHash...
		my @QueryStringParams = CGI::param();
		my %QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

		if(!$QueryStringHash{'range_name'})
			{
				$QueryStringHash{'range_name'} = "";
			}

		# Update login_info table to change the user's email address...
		my $SqlStatement = "afl_GetAdvertiserStatsByAccountId \'$afl_cookie_email\', \'$afl_cookie_password\', \'$QueryStringHash{'range_name'}\'"; 

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
				##########################
				# dbresults() must be called for each result set...
				$status = $MSSQL::DBlib::dbh->dbresults();
				if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
					{
						if($DebugThisAp eq "1")
							{
								print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
							}
						my %dataref = ("jason" => "baumbach");
						my $dataref = \%dataref;

						my @advertiser;
						my @start_date;
						my @end_date;
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								# Since there is no global DB error check get 
								# all database fields returned by the query...

								push (@range_name, $$dataref{range_name});
								push (@start_date, $$dataref{start_date});
								push (@end_date, $$dataref{end_date});
								
								if($DebugThisAp eq "1")
									{
										while( (my $Key, my $Value) = each(%$dataref) )
										{
											print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
											print "<!-- $Key = ($Value) -->\n";
										}                
									}	
							}

						print "                   <TABLE width=\"100%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" bgcolor=\"#E5E5E5\">\n";
						print "                        <TR bgcolor=\"#FFFFFF\">\n";
						print "                          <TD>\n";
						print "                            &nbsp;\n";
						print "                          </TD>\n";
						print "                        </TR>\n";
						print "                        <TR>\n";
						print "                          <TD>\n";
						print "                            <TABLE width=\"100%\" border=\"0\" cellpadding=\"8\" cellspacing=\"1\">\n";
						print "                              <TR bgcolor=\"#FFFFFF\">\n";
						print "                                <TD colspan=\"12\" class=\"BlackTextLargeBold\">\n";
                        print "									<form method=\"post\" action=\"" . $Map{'CGIBIN'} . "/" . $ProgramName . "\">\n";
						print "                                  Select a report range <SELECT name=\"range_name\" id=\"range_name\">\n";
						foreach my $range_name (@range_name) 
						{
							if ($range_name eq $QueryStringHash{'range_name'}) 
								{
									print "                <OPTION value=\"$range_name\" SELECTED>\n";
									print "                  $range_name\n";
									print "                  </OPTION>\n";
								}
							else
								{
									print "                <OPTION value=\"$range_name\">\n";
									print "                  $range_name\n";
									print "                  </OPTION>\n";
								}
						}        
						print "                                  </SELECT>\n";
						print "								<input name=\"generate\" type=\"submit\" class=\"buttonDefault\" value=\"Generate\";>\n";
						print "                                </TD>\n";
						print "							  </TR>\n";
						print "							  </form>\n";

						

					}# END if($status != FAIL)
				else
					{
						print "ERROR: $SqlStatement Failed for first result set!\n";
						$status = $MSSQL::DBlib::dbh->dbcancel();
					}

				##########################
				# Get SECOND result set...
				# Affiliate ID and User Type...
				##########################
				# dbresults() must be called for each result set...
				$status = $MSSQL::DBlib::dbh->dbresults();
				if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
					{
						print "                              <TR bgcolor=\"#FFFFFF\">\n";
						print "                                <TD colspan=\"12\" class=\"BlackTextLargeBold\">\n";
						print "                                  &nbsp;\n";
						print "                                </TD>\n";
						print "                              </TR>\n";
						print "                              <TR bgcolor=\"#FFFFFF\">\n";
						print "                                <TD class=\"BG1Text1\">\n";
						print "                                  Advertiser\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  Revenue\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  Leads\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  Leads Commission\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  Sales\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  Sales Commission\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  Clicks\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  Impressions\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  CTR\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  CR\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  EPM\n";
						print "                                </TD>\n";
						print "                                <TD class=\"BlackTextMedium\">\n";
						print "                                  EPC\n";
						print "                                </TD>\n";
						print "                              </TR>\n";

						if($DebugThisAp eq "1")
							{
								print "<!-- DbError: ($DatabaseFunctions::DatabaseError) -->\n";
								print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
							}
						my %dataref = ("jason" => "baumbach");
						my $dataref = \%dataref;
						my $class = "BG2Text2";
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
										$class = "BG2Text2";
									}
								else
									{
										$class = "BlackTextMedium";
									}

								print "                              <TR bgcolor=\"#FFFFFF\">\n";
								print "                                <TD class=\"$class\">\n";
								if($$dataref{advertiser} eq 'Totals')
									{
										print "                                 " . $$dataref{advertiser} . "\n";
									}
								else
									{
										print "									<A href=\"javascript:OpenWindow('" . $Map{'CGIBIN'} . "/Afl_GenAffiliateProgramInfo.cgi?afl_unique_id=" . $$dataref{afl_unique_id} . "',555,750);\" class=\"NavText\">" . $$dataref{advertiser} . "</a>\n";
									}
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  \$" . $$dataref{total_revenue} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{leads} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  \$" . $$dataref{leads_commission} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{sales} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  \$" . $$dataref{sales_commission} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{clicks} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{impressions} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{click_through_ratio} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{conversion_ratio} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{earnings_per_thousand_imp} . "\n";
								print "                                </TD>\n";
								print "                                <TD class=\"$class\">\n";
								print "                                  " . $$dataref{earnings_per_hundred_clicks} . "\n";
								print "                                </TD>\n";
								print "                              </TR>\n";
							}
						print "                            </TABLE>\n";
						print "                          </TD>\n";
						print "                        </TR>\n";
						print "                      </TABLE>\n";

						my $SqlStatement_LeadsGraph	= "afl_GraphActionsAllByAccountId \'$afl_cookie_email\', \'$afl_cookie_password\', 'leads', '1', \'$QueryStringHash{'range_name'}\'";
						my @LegendArray_Leads = ("Total Actions", "New Males", "New Females");
						my $GraphPath		= $Map{'BANNER_FOLDER'};
						my $GraphName_Leads	= $afl_cookie_email . "_" . $QueryStringHash{'range_name'} . "_" . "Leads";
						$GraphName_Leads =~ s/\W/_/gi;
						my $Width_Leads		= "375";
						my $Height_Leads	= "300";

						my $GraphImage_Leads = &GraphingFunctions::Create_And_Return_MixedGraph_Location(\$SqlStatement_LeadsGraph
																										, \'3'
																										, \'Leads'
																										, \@LegendArray_Leads
																										, \$Width_Leads
																										, \$Height_Leads
																										, \$GraphPath
																										, \$GraphName_Leads
																										, \"1"
																										, \%Map
																										);

						my $SqlStatement_SalesGraph	= "afl_GraphActionsAllByAccountId \'$afl_cookie_email\', \'$afl_cookie_password\', 'sales', '1', \'$QueryStringHash{'range_name'}\'";
						my @LegendArray_Sales = ("Total Actions", "1 Month", "3 Month", "6 Month", "12 Month", "Lifetime");
						my $GraphName_Sales	= $afl_cookie_email . "_" . $QueryStringHash{'range_name'} . "_" . "Sales";
						$GraphName_Sales =~ s/\W/_/gi;
						my $Width_Sales		= "375";
						my $Height_Sales	= "300";

						my $GraphImage_Sales = &GraphingFunctions::Create_And_Return_MixedGraph_Location(\$SqlStatement_SalesGraph
																										, \'6'
																										, \'Sales'
																										, \@LegendArray_Sales
																										, \$Width_Sales
																										, \$Height_Sales
																										, \$GraphPath
																										, \$GraphName_Sales
																										, \"1"
																										, \%Map
																										);

						print "                      <TABLE width=\"800\">\n";
						print "                        <TR bgcolor=\"#FFFFFF\">\n";
						print "                          <TD>\n";
						print "                            &nbsp;\n";
						print "                          </TD>\n";
						print "                        </TR>\n";
						print "                        <TR bgcolor=\"#FFFFFF\">\n";
						print "                             <TD width=\"33%\">\n";
						print "								<IMG src=\"/Banners/$GraphImage_Leads\" width=\"$Width_Leads\" height=\"$Height_Leads\">\n";
						print "                            </TD>\n";
						print "                             <TD width=\"34%\">\n";
						print "								&nbsp;";
						print "                            </TD>\n";
						print "                             <TD width=\"33%\">\n";
						print "								<IMG src=\"/Banners/$GraphImage_Sales\" width=\"$Width_Sales\" height=\"$Height_Sales\">\n";
						print "                           </TD>\n";
						print "                        </TR>\n";
						print "                        <TR>\n";
						print "                          <TD>\n";
						print "                            &nbsp;\n";
						print "                          </TD>\n";
						print "                        </TR>\n";
						print "                      </TABLE>\n";

						&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
					}
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error($afl_cookie_email, "DB ERROR: Unable to create account for ($QueryStringHash{'email'}).<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
					}
			}
	}
#End HTML...
print "</HTML>\n";
exit 0;
