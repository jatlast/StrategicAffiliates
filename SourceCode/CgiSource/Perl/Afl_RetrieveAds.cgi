#!/usr/local/bin/perl -w
use CGI qw/:standard/;

use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

#use strict;

#Begin HTML so errors show up in browser...
#print CGI::header('text/html');
#print "<HTML>\n";

print "Content-type: text/javascript\n\n";

# Add directories to perl environment path...
# Smithers
unshift @INC, "D:/Required/INC/";
# Grimes
unshift @INC, "C:/Required/INC/";

require "DatabaseFunctions.pl";
require "CgiFunctions.pl";
require "UtilityFunctions.pl";

my $DebugThisAp			   = "0";
my $DebugCgiFunctions 	   = "0";
my $DebugDatabaseFunctions = "0";
my $DebugUtilityFunctions  = "0";

my $DebugPrintColorHTML	   = "0";

my $ProgramName = "Afl_RetrieveAds.cgi";

# Determine what libraries to use base on the execution dir...
my $CurrentFilePath = __FILE__;
# Initialize LinkMap Hash variable "Map"...
my %Map = &UtilityFunctions::Load_LinkMap($CurrentFilePath, $DebugUtilityFunctions); 
# Severe Error:  No LinkMap.dat file found -- EXIT --
if($Map{'CONFIG'} eq 'ERROR')
	{
		print "document.write(\"<BR>LinkMap Error.<BR><BR>Contact Site Administrator.<BR>\")\n";
	}
else
	{
		$Map{'PROGRAM_NAME'} = $ProgramName;
	}
# Test URL...
# http://www.netlovematch.com/affiliates/RetrieveBannerAds.cgi?afl_unique_id=1&ad_unique_id=100&r=0&p=0
# http://10.10.10.5:1901/cgi-bin/RetrieveBannerAds.cgi?afl_unique_id=1&ad_unique_id=100&r=0&p=0

my @QueryStringParams;
my %QueryStringHash;

# make sure the query string hash contains the variable names required...
$QueryStringHash{'aflid'}	= '0';	# afl_uinque_id
$QueryStringHash{'auid'}	= '0';	# ad_unique_id
$QueryStringHash{'sid'}		= '0';	# site_id
$QueryStringHash{'acid'}	= '0';	# afl_account_id
#$QueryStringHash{'ip'}		= '';	# ip_address
#$QueryStringHash{'lnum'}	= '1';	# link number		1 = link one or only link
$QueryStringHash{'r'}		= '1';	# rotate			1 = yes | 0 = no
$QueryStringHash{'p'}		= '0';	# popup				1 = yes | 0 = no | -1 = under
$QueryStringHash{'o'}		= '0';	# load only once	1 = yes | 0 = no
$QueryStringHash{'w'}		= '1';	# window to open in	2 = new | 1 = same | -1 = parent
$QueryStringHash{'js'}		= '1';	# is_js_enabled		1 = yes | 0 = no

my $SqlStatement		= "";

my $font_face	    	= "";
my $table_bgcolor    	= "#FFFFFF";
my $table_border_size	= "0";
my $local_bgcolor    	= "#FFFFFF";

my $unique_id    		= "";
my $test_mode		  	= "";

# Load the values passed in into the QueryStringHash...
@QueryStringParams = CGI::param();
%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

# Check for popunder cookie variable..
my $show_once_cookie = &CgiFunctions::Get_Cookie_Value($QueryStringHash{'auid'}, $DebugCgiFunctions);
#print "document.write(\"<BR>cookie show_once_cookie = $show_once_cookie.<BR>\")\n";

# when "js" = 0 the user has JavaScript disabled...
if($QueryStringHash{'js'} eq "0")
	{
		$SqlStatement = "afl_LogUndeliverableAd \'$QueryStringHash{'auid'}\'\
														, \'$QueryStringHash{'acid'}\'\
														, \'$QueryStringHash{'sid'}\'\
														, \'$ENV{REMOTE_ADDR}\'\
														"; 
		# Update the last_sent field of the current result set...
			my $SqlErrorVal = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName", $SqlStatement, $DebugDatabaseFunctions);
			if($SqlErrorVal eq "1")
				{
						# since this part of the cgi should only run from a WebBug there is no debugging possible
				}
			else
				{
						# since this part of the cgi should only run from a WebBug there is no debugging possible
				}
	}
# ONLY DELIVER AD IF IT HAS NOT BEEN SHOWN BEFORE...
elsif($show_once_cookie ne "yes" and $QueryStringHash{'o'} ne "1")
	{

	$SqlStatement = "afl_DeliverAd \'$QueryStringHash{'auid'}\'\
													, \'$QueryStringHash{'acid'}\'\
													, \'$QueryStringHash{'sid'}\'\
													, \'$QueryStringHash{'r'}\'\
													, \'$ENV{REMOTE_ADDR}\'\
													"; 

	my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
	$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
	$status = $MSSQL::DBlib::dbh->dbsqlexec();
		
	if($DatabaseFunctions::DatabaseError eq "1000" or $DatabaseFunctions::DatabaseError eq "1001")
		{
			&UtilityFunctions::Adv_Print_Framed_Error("", "", $DebugUtilityFunctions, %Map);		
		}
	else
		{
			# Remove the special characters so the string can be printed by JavaScript...
			$SqlStatement =~ s/\'/&quot;/g;
			$SqlStatement =~ s/\n//g;
			$SqlStatement =~ s/\r//g;

			##########################
			# Get ONLY result set...
			##########################
			# dbresults() must be called for each result set...
			$status = $MSSQL::DBlib::dbh->dbresults();
			if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
				{
					if($DebugThisAp eq "1")
						{
							print "document.write(\"<BR>SUCCESS: ($SqlStatement) returned with dbresults status = ($status).<BR>\")\n";
						}
					elsif($DatabaseFunctions::DatabaseError eq "1016")
						{
							print "document.write(\"<BR>Retrieval Failure.<BR>SQL: ($SqlStatement)<BR> DbError: ROLLBACK ($DatabaseFunctions::DatabaseError)<BR>\")\n";
						}
					my %dataref = ("jason" => "baumbach");
					my $dataref = \%dataref;
					# Check for global DB error...
					if($DatabaseFunctions::DatabaseError eq "1")
						{
							print "document.write(\"SQL: ($SqlStatement)<BR> DbError: ($DatabaseFunctions::DatabaseError)<BR>\")\n";
						}
					else
						{
							# Prevent infinite loop...
							while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
								{
									# Since there is no global DB error check get 
									# all database fields returned by the query...
										
									if($DebugPrintColorHTML eq "1")
										{
											while( (my $Key, my $Value) = each(%$dataref) )
											{
												my $Value_To_JS = $Value;
												$Value_To_JS =~ s/\n//g;
												$Value_To_JS =~ s/\r//g;
												$Value_To_JS =~ s/\"/&quot;/g;
												$Value_To_JS =~ s/\'/&quot;/g;
												print "document.write(\"<FONT color=\\\"blue\\\">$Key</FONT> <FONT color=\\\"red\\\">$Value_To_JS</FONT><BR>\")\n";
											}                
										}	

									my $click_window_target = "_blank"; # _blank = New.
									if($QueryStringHash{'w'} eq "1")
										{
											$click_window_target = "_self"; # Same
										}
									elsif($QueryStringHash{'w'} eq "2")
										{
											$click_window_target = "_blank"; # New
										}
									elsif($QueryStringHash{'w'} eq "-1")
										{
											$click_window_target = "_parent"; # parent
										}

									# Banners...
									if($$dataref{ad_type} eq "1")
										{
											print "document.write(\"<BR>ad_type = ($$dataref{ad_type})<BR>\")\n" if $DebugThisAp eq "1";
											if($QueryStringHash{'p'} eq "0")
												{
													print "document.write(\"		<TABLE bgcolor=\\\"$table_bgcolor\\\" border=\\\"$table_border_size\\\" cellpadding=\\\"3\\\" cellspacing=\\\"0\\\" width=\\\"$$dataref{banner_pixel_width}\\\" height=\\\"$$dataref{banner_pixel_height}\\\">\")\n";
													print "document.write(\"		  <TR>\")\n";
													if ($click_window_target eq "_blank")
														{
															# Open in New Window
															print "document.write(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$$dataref{mouse_over_text}'; return true;\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true;\\\" onclick=\\\"window.open('$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1','','scrollbars=1,resizable=1,toolbar=1,location=1,menubar=1,status=1,directories=1');\\\">\")\n";
															print "document.write(\"			  <A href=\\\"#\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true;\\\" onmouseout=\\\"window.status='';return true;\\\">\")\n";
														}
													else
														{
															# Open in Same Window
															print "document.write(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$$dataref{mouse_over_text}'; return true;\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true;\\\" onclick=\\\"location.href='$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1';\\\">\")\n";
															print "document.write(\"			  <A href=\\\"$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true;\\\" onmouseout=\\\"window.status='';return true;\\\">\")\n";
														}
													print "document.write(\"			  <IMG alt=\\\"$$dataref{alt_text}\\\" src=\\\"$Map{'AFL_ROOT'}/banners/$$dataref{ad_unique_id}$$dataref{banner_dot_extension}\\\" width=$$dataref{banner_pixel_width} height=$$dataref{banner_pixel_height} border=0></A>\")\n";
													print "document.write(\"			</TD>\")\n";
													print "document.write(\"		  </TR>\")\n";
													print "document.write(\"		</TABLE>\")\n";
												}
											elsif($QueryStringHash{'p'} eq "1")
												{
													if($click_window_target eq "_self")
														{
															$click_window_target = "_parent"; # parent
														}
				#									print "var myWindow = window.open('pop up', 'popup', 'toolbar=no, location=no, scrollbars=no, resizable=no, width=($$dataref{banner_pixel_width}+20), height=($$dataref{banner_pixel_height}+20)')\n";
													&Print_Pop_UP_Management_JS($$dataref{ad_unique_id}, $QueryStringHash{'o'}, $$dataref{banner_pixel_width}, $$dataref{banner_pixel_height});

													print "myWindow.document.writeln(\"<HTML>\")\n";
													print "myWindow.document.writeln(\"  <HEAD>\")\n";
													print "myWindow.document.writeln(\"    <TITLE>\")\n";
													print "myWindow.document.writeln(\"		$$dataref{mouse_over_text}\")\n";
													print "myWindow.document.writeln(\"    </TITLE>\")\n";
													print "myWindow.document.writeln(\"  </HEAD>\")\n";
													print "myWindow.document.writeln(\"  <BODY>\")\n";

													print "myWindow.document.writeln(\"		<TABLE bgcolor=\\\"$table_bgcolor\\\" border=\\\"$table_border_size\\\" cellpadding=\\\"3\\\" cellspacing=\\\"0\\\" width=\\\"$$dataref{banner_pixel_width}\\\" height=\\\"$$dataref{banner_pixel_height}\\\">\")\n";
													print "myWindow.document.writeln(\"		  <TR>\")\n";

													if ($click_window_target eq "_blank")
														{
															# Open in New Window
															print "myWindow.document.writeln(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true\\\" onclick=\\\"window.open('$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1','','scrollbars=1,resizable=1,toolbar=1,location=1,menubar=1,status=1,directories=1');\\\">\")\n";
															print "myWindow.document.writeln(\"			  <A href=\\\"#\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"window.status='';return true\\\">\")\n";
														}
													else
														{
															# Open in Parent Window
															print "myWindow.document.writeln(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true\\\" onclick=\\\"opener.document.location='$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1';\\\">\")\n";
															print "myWindow.document.writeln(\"			  <A href=\\\"#\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"window.status='';return true\\\">\")\n";
														}

													print "myWindow.document.writeln(\"			  <IMG alt=\\\"$$dataref{alt_text}\\\" src=\\\"$Map{'AFL_ROOT'}/banners/$$dataref{ad_unique_id}$$dataref{banner_dot_extension}\\\" width=$$dataref{banner_pixel_width} height=$$dataref{banner_pixel_height} border=0></A>\")\n";
													print "myWindow.document.writeln(\"			</TD>\")\n";
													print "myWindow.document.writeln(\"		  </TR>\")\n";
													print "myWindow.document.writeln(\"		</TABLE>\")\n";
													print "myWindow.document.writeln(\"  </BODY>\")\n";
													print "myWindow.document.writeln(\"</HTML>\")\n";
													print "myWindow.focus()\n";

												}
											elsif($QueryStringHash{'p'} eq "-1")
												{
													if($click_window_target eq "_self")
														{
															$click_window_target = "_parent"; # parent
														}
													#print "var myWindow = window.open('popunder', 'popunder', 'toolbar=no, location=no, scrollbars=no, resizable=no, width=($$dataref{banner_pixel_width}+20), height=($$dataref{banner_pixel_height}+20)')\n";
													&Print_Pop_UP_Management_JS($$dataref{ad_unique_id}, $QueryStringHash{'o'}, $$dataref{banner_pixel_width}, $$dataref{banner_pixel_height});

													print "myWindow.document.writeln(\"<HTML>\")\n";
													print "myWindow.document.writeln(\"  <HEAD>\")\n";
													print "myWindow.document.writeln(\"    <TITLE>\")\n";
													print "myWindow.document.writeln(\"		$$dataref{mouse_over_text}\")\n";
													print "myWindow.document.writeln(\"    </TITLE>\")\n";
													print "myWindow.document.writeln(\"  </HEAD>\")\n";
													print "myWindow.document.writeln(\"  <BODY>\")\n";

													print "myWindow.document.writeln(\"		<TABLE bgcolor=\\\"$table_bgcolor\\\" border=\\\"$table_border_size\\\" cellpadding=\\\"3\\\" cellspacing=\\\"0\\\" width=\\\"$$dataref{banner_pixel_width}\\\" height=\\\"$$dataref{banner_pixel_height}\\\">\")\n";
													print "myWindow.document.writeln(\"		  <TR>\")\n";

													if ($click_window_target eq "_blank")
														{
															# Open in New Window
															print "myWindow.document.writeln(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true\\\" onclick=\\\"window.open('$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1','','scrollbars=1,resizable=1,toolbar=1,location=1,menubar=1,status=1,directories=1');\\\">\")\n";
															print "myWindow.document.writeln(\"			  <A href=\\\"#\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"window.status='';return true\\\">\")\n";
														}
													else
														{
															# Open in Parent Window
															print "myWindow.document.writeln(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true\\\" onclick=\\\"opener.document.location='$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1';\\\">\")\n";
															print "myWindow.document.writeln(\"			  <A href=\\\"#\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"window.status='';return true\\\">\")\n";
														}

													print "myWindow.document.writeln(\"			  <IMG alt=\\\"$$dataref{alt_text}\\\" src=\\\"$Map{'AFL_ROOT'}/banners/$$dataref{ad_unique_id}$$dataref{banner_dot_extension}\\\" width=$$dataref{banner_pixel_width} height=$$dataref{banner_pixel_height} border=0></A>\")\n";
													print "myWindow.document.writeln(\"			</TD>\")\n";
													print "myWindow.document.writeln(\"		  </TR>\")\n";
													print "myWindow.document.writeln(\"		</TABLE>\")\n";
													print "myWindow.document.writeln(\"  </BODY>\")\n";
													print "myWindow.document.writeln(\"</HTML>\")\n";

													print "document.focus()\n";
												}
											else
												{
													print "myWindow.document.writeln(\"<BR>ERROR<BR>\")\n";
												}
										}
									# Text Links
									elsif($$dataref{ad_type} eq "2")
										{
											if ($click_window_target ne "_blank")
												{
													# Open in New Window
													print "document.write(\"<A title=\\\"$$dataref{alt_text}\\\" href=\\\"$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1;\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"window.status='';return true\\\">$$dataref{text_link_text}</A>\")\n";
												}
											else
												{
													# Open in Same Window
													print "document.write(\"<A title=\\\"$$dataref{alt_text}\\\" href=\\\"#\\\" onclick=\\\"window.open('$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=1','','scrollbars=1,resizable=1,toolbar=1,location=1,menubar=1,status=1,directories=1');\\\" onmouseover=\\\"window.status='$$dataref{mouse_over_text}';return true\\\" onmouseout=\\\"window.status='';return true\\\">$$dataref{text_link_text}</A>\")\n";
												}
											print "document.write(\"<BR>ad_type = ($$dataref{ad_type})<BR>\")\n" if $DebugThisAp eq "1";
										}
									# Interactive HTML
									elsif($$dataref{ad_type} eq "3")
										{
											print "document.write(\"<BR>ad_type = ($$dataref{ad_type})<BR>\")\n" if $DebugThisAp eq "1";
	#										my $HTML_To_JS = $$dataref{html_block};

											my $NumberOfFoundLinks		= 1;
											my @html_block_line_array = split(/\r\n/, $$dataref{html_block});
											foreach my $CurrentLine (@html_block_line_array) 
												{
													if($CurrentLine =~ m%<A href="http://.*?"%gis
														#or $CurrentLine =~ m%"location.href='http://.*?'"%gis
														or $CurrentLine =~ m%<form method="GET" action=".*?">%gis
														or $CurrentLine =~ m%<form method="POST" action=".*?">%gis
														)
													{
														print "document.write(\"Found link ($NumberOfFoundLinks)<BR>\")\n" if $DebugThisAp eq "1";
														$CurrentLine =~ s%<form method="POST" action="(.*?)">%<form method="GET" action="$Map{'CGIBIN'}/Afl_ProcessClick.cgi" target="$click_window_target"><input type="hidden" name="turl" value="$1"><input type="hidden" name="ctluid" value="$$dataref{afl_ctl_unique_id}"><input type="hidden" name="lnum" value="$NumberOfFoundLinks">%gis;
														$CurrentLine =~ s%<form method="GET" action="(.*?)">%<form method="GET" action="$Map{'CGIBIN'}/Afl_ProcessClick.cgi" target="$click_window_target"><input type="hidden" name="turl" value="$1"><input type="hidden" name="ctluid" value="$$dataref{afl_ctl_unique_id}"><input type="hidden" name="lnum" value="$NumberOfFoundLinks">%gis;
														$CurrentLine =~ s%<A href="(.*?)"%<A href="$Map{'CGIBIN'}/Afl_ProcessClick.cgi?turl=$1&amp;ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=$NumberOfFoundLinks" target="$click_window_target"%gis;
														#$CurrentLine =~ s%"location.href='http://(.*?)'"%"location.href='$Map{'CGIBIN'}/Afl_ProcessClick.cgi?ctluid=$$dataref{afl_ctl_unique_id}&amp;lnum=$NumberOfFoundLinks'"%gis;
														$NumberOfFoundLinks++;
													}
												$CurrentLine =~ s/"/\\\"/g;
												print "document.write(\"$CurrentLine\")\n";
												}
										}
									# Interactive HTML For Email...
									elsif($$dataref{ad_type} eq "4")
										{
											print "document.write(\"<BR>ad_type = ($$dataref{ad_type})<BR>\")\n" if $DebugThisAp eq "1";
											my $HTML_To_JS = $$dataref{html_block};

											my $NumberOfFoundLinks = 0;
											my @html_block_line_array = split(/\r\n/, $$dataref{html_block});
											foreach my $CurrentLine (@html_block_line_array) 
												{
													if($CurrentLine =~ m%<A href="http://.*?"%gis
														or $CurrentLine =~ m%"location.href='http://.*?'"%gis
														or $CurrentLine =~ m%<form method="GET" action=".*?">%gis
														)
													{
	#													print "document.write(\"Found link ($NumberOfFoundLinks++)<BR>\")\n";
														# Add a random number (pmc_stamp) to try and fool spam detectors...
														#my $pmc_stamp = time;
														#$_ =~ s%<A href="http://(.*?)"%<A href="$$MapHash{'ADV_CGIBIN'}/ProcessMailClick.cgi?pmc_url=http://$1&pmc_id=$$mail_sent_unique_id&pmc_respondent=$$email_address&pmc_stamp=$pmc_stamp"%gis;
														#$_ =~ s%"location.href='http://(.*?)'"%"location.href='$$MapHash{'ADV_CGIBIN'}/ProcessMailClick.cgi?pmc_url=http://$1&pmc_id=$$mail_sent_unique_id&pmc_respondent=$$email_address&pmc_stamp=$pmc_stamp'"%gis;
														#$_ =~ s%<form method="GET" action="(.*?)">%<form method="GET" action="$$MapHash{'ADV_CGIBIN'}/ProcessMailClick.cgi"><input type="hidden" name="pmc_url" value="$1?"><input type="hidden" name="pmc_id" value="$$mail_sent_unique_id"><input type="hidden" name="pmc_respondent" value="$$email_address"><input type="hidden" name="pmc_stamp" value="$pmc_stamp">%gis;
													}
													else
													{	
	#													$CurrentLine =~ s/"/\\\"/g;
	#													print "document.write(\"Link # ($NumberOfFoundLinks)<BR>\")\n";
	#													print "document.write(\"<SPAN class=BlackTextLarge>$CurrentLine<SPAN><BR>\")\n";
													}
	#												$NumberOfFoundLinks++;
												}

											$HTML_To_JS =~ s/\n//g;
											$HTML_To_JS =~ s/\r//g;
											$HTML_To_JS =~ s/"/\\\"/g;
											print "document.write(\"$HTML_To_JS\")\n";
										}
									else
										{
										}

								}
						}# END else (No db error) 
				}# END if($status != FAIL)
			else
				{
					print "document.write(\"<BR>ERROR: $SqlStatement Failed for first result set!<BR>\")\n";
					$status = $MSSQL::DBlib::dbh->dbcancel();
				}
		}

	}
sub Print_Pop_UP_Management_JS
{
	my ($window_name, $load_only_once, $banner_pixel_width, $banner_pixel_height) = @_;

	print "document.write(\"<script language=\\\"javascript\\\">\")\n";
#	print "document.write(\"//Pop-under window- By JavaScript Kit\")\n";
#	print "document.write(\"//Credit notice must stay intact for use\")\n";
#	print "document.write(\"//Visit http://javascriptkit.com for this script\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"//specify page to pop-under\")\n";
	print "document.write(\"var popunder=\\\"$window_name\\\";\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"//specify popunder window features\")\n";
#	print "document.write(\"//set 1 to enable a particular feature, 0 to disable\")\n";
	print "document.write(\"var winfeatures=\\\"width=" . ($banner_pixel_width+20) . ", height=" . ($banner_pixel_height+20) . ",scrollbars=0,resizable=0,toolbar=0,location=0,menubar=0,status=1,directories=0\\\";\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"//Pop-under only once per browser session? (0=no, 1=yes)\")\n";
#	print "document.write(\"//Specifying 0 will cause popunder to load every time page is loaded\")\n";
	print "document.write(\"var once_per_session=$load_only_once;\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"///No editing beyond here required/////\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"function get_cookie(Name) {\")\n";
	print "document.write(\"  var search = Name + \\\"=\\\";\")\n";
	print "document.write(\"  var returnvalue = \\\"\\\";\")\n";
	print "document.write(\"  if (document.cookie.length > 0) {\")\n";
	print "document.write(\"    offset = document.cookie.indexOf(search);\")\n";
	print "document.write(\"    if (offset != -1) {\")\n";
	print "document.write(\"      offset += search.length;\")\n";
#	print "document.write(\"      // set index of beginning of value\")\n";
	print "document.write(\"      end = document.cookie.indexOf(\\\";\\\", offset);\")\n";
#	print "document.write(\"      // set index of end of cookie value\")\n";
	print "document.write(\"      if (end == -1)\")\n";
	print "document.write(\"         end = document.cookie.length;\")\n";
	print "document.write(\"      returnvalue=unescape(document.cookie.substring(offset, end));\")\n";
	print "document.write(\"      }\")\n";
	print "document.write(\"   }\")\n";
	print "document.write(\"  return returnvalue;\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"function loadornot(){\")\n";
	print "document.write(\"if (get_cookie('$window_name')==''){\")\n";
	print "document.write(\"var Then = new Date();\")\n";
	print "document.write(\"Then.setTime(Then.getTime() + 60 * 60 * 1000);\")\n";
#	print "document.write(\"Then.setTime(Then.getTime() + 1000);\")\n";
#	print "document.write(\"alert(\\\"Then = \\\" + Then.toGMTString());\")\n";
#	print "document.write(\"alert(Then.toGMTString());\")\n";
	print "document.write(\"document.cookie=\\\"$window_name=yes; expires=\\\" + Then.toGMTString() + \\\"; path=/\\\";\")\n";
	print "document.write(\"loadpopunder();\")\n";
	print "document.write(\"}\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"function loadpopunder(){\")\n";
	print "document.write(\"myWindow=window.open(popunder,\\\"\\\",winfeatures);\")\n";
	print "document.write(\"myWindow.blur();\")\n";
	print "document.write(\"window.focus();\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"if (once_per_session==0){\")\n";
	print "document.write(\"loadpopunder();\")\n";
	print "document.write(\"}else{\")\n";
	print "document.write(\"loadornot();}\")\n";
	print "document.write(\"</script>\")\n";
}
exit 0;

sub tesm
{
	my ($window_name, $load_only_once, $banner_pixel_width, $banner_pixel_height) = @_;

	print "document.write(\"<script language=\\\"javascript\\\">\")\n";
#	print "document.write(\"//Pop-under window- By JavaScript Kit\")\n";
#	print "document.write(\"//Credit notice must stay intact for use\")\n";
#	print "document.write(\"//Visit http://javascriptkit.com for this script\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"//specify page to pop-under\")\n";
	print "document.write(\"var popunder=\\\"$window_name\\\";\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"//specify popunder window features\")\n";
#	print "document.write(\"//set 1 to enable a particular feature, 0 to disable\")\n";
	print "document.write(\"var winfeatures=\\\"width=" . ($banner_pixel_width+20) . ", height=" . ($banner_pixel_height+20) . ",scrollbars=0,resizable=0,toolbar=0,location=0,menubar=0,status=1,directories=0\\\";\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"//Pop-under only once per browser session? (0=no, 1=yes)\")\n";
#	print "document.write(\"//Specifying 0 will cause popunder to load every time page is loaded\")\n";
	print "document.write(\"var once_per_session=$load_only_once;\")\n";
#	print "document.write(\"\")\n";
#	print "document.write(\"///No editing beyond here required/////\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"function get_cookie(Name) {\")\n";
	print "document.write(\"  var search = Name + \\\"=\\\";\")\n";
	print "document.write(\"  var returnvalue = \\\"\\\";\")\n";
	print "document.write(\"  if (document.cookie.length > 0) {\")\n";
	print "document.write(\"    offset = document.cookie.indexOf(search);\")\n";
	print "document.write(\"    if (offset != -1) {\")\n";
	print "document.write(\"      offset += search.length;\")\n";
#	print "document.write(\"      // set index of beginning of value\")\n";
	print "document.write(\"      end = document.cookie.indexOf(\\\";\\\", offset);\")\n";
#	print "document.write(\"      // set index of end of cookie value\")\n";
	print "document.write(\"      if (end == -1)\")\n";
	print "document.write(\"         end = document.cookie.length;\")\n";
	print "document.write(\"      returnvalue=unescape(document.cookie.substring(offset, end));\")\n";
	print "document.write(\"      }\")\n";
	print "document.write(\"   }\")\n";
	print "document.write(\"  return returnvalue;\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"function loadornot(){\")\n";
	print "document.write(\"if (get_cookie('popunder')==''){\")\n";
	print "document.write(\"var Then = new Date();\")\n";
	print "document.write(\"Then.setTime(Then.getTime() + 60 * 60 * 1000);\")\n";
#	print "document.write(\"Then.setTime(Then.getTime() + 1000);\")\n";
#	print "document.write(\"alert(\\\"Then = \\\" + Then.toGMTString());\")\n";
#	print "document.write(\"alert(Then.toGMTString());\")\n";
	print "document.write(\"document.cookie=\\\"popunder=yes; expires=\\\" + Then.toGMTString() + \\\"; path=/\\\";\")\n";
	print "document.write(\"loadpopunder();\")\n";
	print "document.write(\"}\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"function loadpopunder(){\")\n";
	print "document.write(\"myWindow=window.open(popunder,\\\"\\\",winfeatures);\")\n";
	print "document.write(\"myWindow.blur();\")\n";
	print "document.write(\"window.focus();\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"if (once_per_session==0){\")\n";
	print "document.write(\"loadpopunder();\")\n";
	print "document.write(\"}else{\")\n";
	print "document.write(\"loadornot();}\")\n";
	print "document.write(\"</script>\")\n";

												if ($ENV{'HTTP_USER_AGENT'} =~ /MSIE/)
													{
#														print "<p>Your browser is <b>Internet Explorer!</b></p>\n";
													}
												elsif ($ENV{'HTTP_USER_AGENT'} =~ /Mozilla/)
													{
#														print "<p>Your browser is <b>Netscape!</b></p>\n";
													}

}

