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
#Home pc
unshift @INC, "D:/Required/INC";

require "DatabaseFunctions.pl";
require "CgiFunctions.pl";
require "UtilityFunctions.pl";

my $DebugThisAp			   = "0";
my $DebugCgiFunctions 	   = "1";
my $DebugDatabaseFunctions = "1";
my $DebugUtilityFunctions  = "1";

my $ProgramName = "RetrieveBannerAds.cgi";

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
$QueryStringHash{'afl_unique_id'}	= '';
$QueryStringHash{'ad_unique_id'}	= '';
$QueryStringHash{'r'}				= '1';	# rotate			1 = yes, 0 = no
$QueryStringHash{'p'}				= '0';	# popup				1 = yes, 0 = no, -1 = under
$QueryStringHash{'once'}			= '0';	# load only once	1 = yes, 0 = no

my $adv_cookie_name		= "";
my $adv_cookie_password	= "";

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

$SqlStatement = "afl_DeliverBannerAd \'$QueryStringHash{'ad_unique_id'}\', \'$QueryStringHash{'afl_unique_id'}\', \'$ENV{REMOTE_ADDR}\', \'$QueryStringHash{'r'}\'";     

#print "document.write(\"<BR>SQL = ($SqlStatement)<BR>\")\n";

my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
$status = $MSSQL::DBlib::dbh->dbsqlexec();
	
if($DatabaseFunctions::DatabaseError eq "1000" or $DatabaseFunctions::DatabaseError eq "1001")
	{
		&UtilityFunctions::Adv_Print_Framed_Error("", "", $DebugUtilityFunctions, %Map);		
	}
else
	{
		##########################
		# Get ONLY result set...
		##########################
		# dbresults() must be called for each result set...
		$status = $MSSQL::DBlib::dbh->dbresults();
		if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
			{
				if($DebugThisAp eq "1")
					{
						print "document.write(\"<BR>SUCCESS: $SqlStatement returned with dbresults status = ($status).<BR>\")\n";
					}
				elsif($DatabaseFunctions::DatabaseError eq "1016")
					{
						print "document.write(\"<BR>Retrieval Failure.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \nROLLBACK ($DatabaseFunctions::DatabaseError)\n -->\n<BR>\")\n";
					}
				my %dataref = ("jason" => "baumbach");
				my $dataref = \%dataref;
				# Check for global DB error...
				if($DatabaseFunctions::DatabaseError eq "1")
					{
						print "document.write(\"<BR>Retrieval Failure.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \nROLLBACK ($DatabaseFunctions::DatabaseError)\n -->\n<BR>\")\n";
					}
				else
					{
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								# Since there is no global DB error check get 
								# all database fields returned by the query...
									
								my $ad_unique_id					= $$dataref{ad_unique_id};
								my $dot_extension					= $$dataref{dot_extension};
								my $which_site						= $$dataref{which_site};
								my $pixel_width						= $$dataref{pixel_width};
								my $pixel_height					= $$dataref{pixel_height};
								my $target_url						= $$dataref{target_url};
								my $alt_text						= $$dataref{alt_text};
								my $status_text						= $$dataref{status_text};
								my $afl_click_through_log_unique_id	= $$dataref{afl_click_through_log_unique_id};
									
								if($DebugThisAp eq "1")
									{
										print "document.write(\"<BR>ad_unique_id                    = ($ad_unique_id)<BR>\")\n";
										print "document.write(\"<BR>dot_extension                   = ($dot_extension)<BR>\")\n";
										print "document.write(\"<BR>which_site                      = ($which_site)<BR>\")\n";
										print "document.write(\"<BR>pixel_width                     = ($pixel_width)<BR>\")\n";
										print "document.write(\"<BR>pixel_height                    = ($pixel_height)<BR>\")\n";
										print "document.write(\"<BR>target_url                      = ($target_url)<BR>\")\n";
										print "document.write(\"<BR>alt_text                        = ($alt_text)<BR>\")\n";
										print "document.write(\"<BR>status_text                     = ($status_text)<BR>\")\n";
										print "document.write(\"<BR>afl_click_through_log_unique_id = ($afl_click_through_log_unique_id)<BR>\")\n";
									}
								if($QueryStringHash{'p'} eq "0")
								{
									print "document.write(\"		<TABLE bgcolor=\\\"$table_bgcolor\\\" border=\\\"$table_border_size\\\" cellpadding=\\\"3\\\" cellspacing=\\\"0\\\" width=\\\"$pixel_width\\\" height=\\\"$pixel_height\\\">\")\n";
									print "document.write(\"		  <TR>\")\n";
									print "document.write(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$status_text';return true\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true\\\" onclick=\\\"location.href='$Map{'AFL_CGIBIN'}/ProcessBannerClick.cgi?afl_url=$target_url&amp;afl_unique_id=$afl_click_through_log_unique_id&amp;afl_ip_address=$ENV{REMOTE_ADDR}'\\\">\")\n";
									print "document.write(\"			  <A href=\\\"$Map{'ADV_CGIBIN'}/ProcessBannerClick.cgi?afl_url=$target_url&amp;afl_unique_id=$afl_click_through_log_unique_id&amp;afl_ip_address=$ENV{REMOTE_ADDR}\\\" onmouseover=\\\"window.status='$status_text';return true\\\" onmouseout=\\\"window.status='';return true\\\"></A>\")\n";
									print "document.write(\"			  <IMG src=http://www.netlovematch.com/affiliates/banners/" . $ad_unique_id . $dot_extension . " width=$pixel_width height=$pixel_height border=0>\")\n";
									print "document.write(\"			</TD>\")\n";
									print "document.write(\"		  </TR>\")\n";
									print "document.write(\"		</TABLE>\")\n";
								}
								elsif($QueryStringHash{'p'} eq "1")
								{
#									print "var myWindow = window.open('pop up', 'popup', 'toolbar=no, location=no, scrollbars=no, resizable=no, width=" . ($pixel_width+20) . ", height=" . ($pixel_height+20) . "')\n";
									&Print_Pop_UP_Management_JS($ad_unique_id, $QueryStringHash{'once'}, $pixel_width, $pixel_height);

									print "myWindow.document.writeln(\"<HTML>\")\n";
									print "myWindow.document.writeln(\"  <HEAD>\")\n";
									print "myWindow.document.writeln(\"    <TITLE>\")\n";
									print "myWindow.document.writeln(\"		 $status_text\")\n";
									print "myWindow.document.writeln(\"    </TITLE>\")\n";
									print "myWindow.document.writeln(\"  </HEAD>\")\n";
									print "myWindow.document.writeln(\"  <BODY>\")\n";

									print "myWindow.document.writeln(\"		<TABLE bgcolor=\\\"$table_bgcolor\\\" border=\\\"$table_border_size\\\" cellpadding=\\\"3\\\" cellspacing=\\\"0\\\" width=\\\"$pixel_width\\\" height=\\\"$pixel_height\\\">\")\n";
									print "myWindow.document.writeln(\"		  <TR>\")\n";
									print "myWindow.document.writeln(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$status_text';return true\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true\\\" onclick=\\\"location.href='$Map{'AFL_CGIBIN'}/ProcessBannerClick.cgi?afl_url=$target_url&amp;afl_unique_id=$afl_click_through_log_unique_id&amp;afl_ip_address=$ENV{REMOTE_ADDR}'\\\">\")\n";
									print "myWindow.document.writeln(\"			  <A href=\\\"$Map{'ADV_CGIBIN'}/ProcessBannerClick.cgi?afl_url=$target_url&amp;afl_unique_id=$afl_click_through_log_unique_id&amp;afl_ip_address=$ENV{REMOTE_ADDR}\\\" onmouseover=\\\"window.status='$status_text';return true\\\" onmouseout=\\\"window.status='';return true\\\"></A>\")\n";
									print "myWindow.document.writeln(\"			  <IMG src=http://www.netlovematch.com/affiliates/banners/" . $ad_unique_id . $dot_extension . " width=$pixel_width height=$pixel_height border=0>\")\n";
									print "myWindow.document.writeln(\"			</TD>\")\n";
									print "myWindow.document.writeln(\"		  </TR>\")\n";
									print "myWindow.document.writeln(\"		</TABLE>\")\n";
									print "myWindow.document.writeln(\"  </BODY>\")\n";
									print "myWindow.document.writeln(\"</HTML>\")\n";
									print "myWindow.focus()\n";

								}
								elsif($QueryStringHash{'p'} eq "-1")
								{
									#print "var myWindow = window.open('popunder', 'popunder', 'toolbar=no, location=no, scrollbars=no, resizable=no, width=" . ($pixel_width+20) . ", height=" . ($pixel_height+20) . "')\n";
									&Print_Pop_UP_Management_JS($ad_unique_id, $QueryStringHash{'once'}, $pixel_width, $pixel_height);

									print "myWindow.document.writeln(\"<HTML>\")\n";
									print "myWindow.document.writeln(\"  <HEAD>\")\n";
									print "myWindow.document.writeln(\"    <TITLE>\")\n";
									print "myWindow.document.writeln(\"		 $status_text\")\n";
									print "myWindow.document.writeln(\"    </TITLE>\")\n";
									print "myWindow.document.writeln(\"  </HEAD>\")\n";
									print "myWindow.document.writeln(\"  <BODY>\")\n";

									print "myWindow.document.writeln(\"		<TABLE bgcolor=\\\"$table_bgcolor\\\" border=\\\"$table_border_size\\\" cellpadding=\\\"3\\\" cellspacing=\\\"0\\\" width=\\\"$pixel_width\\\" height=\\\"$pixel_height\\\">\")\n";
									print "myWindow.document.writeln(\"		  <TR>\")\n";
									print "myWindow.document.writeln(\"			<TD align=\\\"left\\\" nowrap onmouseover=\\\"this.style.cursor='hand';window.status='$status_text';return true\\\" onmouseout=\\\"this.style.cursor='auto';window.status='';return true\\\" onclick=\\\"location.href='$Map{'AFL_CGIBIN'}/ProcessBannerClick.cgi?afl_url=$target_url&amp;afl_unique_id=$afl_click_through_log_unique_id&amp;afl_ip_address=$ENV{REMOTE_ADDR}'\\\">\")\n";
									print "myWindow.document.writeln(\"			  <A href=\\\"$Map{'ADV_CGIBIN'}/ProcessBannerClick.cgi?afl_url=$target_url&amp;afl_unique_id=$afl_click_through_log_unique_id&amp;afl_ip_address=$ENV{REMOTE_ADDR}\\\" onmouseover=\\\"window.status='$status_text';return true\\\" onmouseout=\\\"window.status='';return true\\\"></A>\")\n";
									print "myWindow.document.writeln(\"			  <IMG src=http://www.netlovematch.com/affiliates/banners/" . $ad_unique_id . $dot_extension . " width=$pixel_width height=$pixel_height border=0>\")\n";
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
					}# END else (No db error) 
			}# END if($status != FAIL)
		else
			{
				print "document.write(\"<BR>ERROR: $SqlStatement Failed for first result set!<BR>\")\n";
				$status = $MSSQL::DBlib::dbh->dbcancel();
			}
	}


sub Print_Pop_UP_Management_JS
{
	my ($window_name, $load_only_once, $pixel_width, $pixel_height) = @_;

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
	print "document.write(\"var winfeatures=\\\"width=" . ($pixel_width+20) . ", height=" . ($pixel_height+20) . ",scrollbars=0,resizable=0,toolbar=0,location=0,menubar=0,status=1,directories=0\\\";\")\n";
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
	print "document.write(\"loadpopunder();\")\n";
	print "document.write(\"document.cookie=\\\"popunder=yes\\\";\")\n";
	print "document.write(\"}\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"function loadpopunder(){\")\n";
	print "document.write(\"myWindow=window.open(popunder,\\\"\\\",winfeatures);\")\n";
	print "document.write(\"myWindow.blur();\")\n";
	print "document.write(\"window.focus();\")\n";
	print "document.write(\"}\")\n";
#	print "document.write(\"\")\n";
	print "document.write(\"if (once_per_session==0)\")\n";
	print "document.write(\"loadpopunder();\")\n";
	print "document.write(\"else\")\n";
	print "document.write(\"loadornot();\")\n";
	print "document.write(\"</script>\")\n";
}
exit 0;