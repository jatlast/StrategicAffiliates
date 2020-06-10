#!/usr/local/bin/perl -w
use CGI qw/:standard/;

use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

#use strict;

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

my $ProgramName = "ManageEmailVerification.cgi";

#Begin HTML so errors show up in browser...
print CGI::header('text/html');
print "<HTML>\n";

# Determine what libraries to use base on the execution dir...
my $CurrentFilePath = __FILE__;
# Initialize LinkMap Hash variable "Map"...
my %Map = &UtilityFunctions::Load_LinkMap($CurrentFilePath, $DebugUtilityFunctions); 

# Severe Error:  No LinkMap.dat file found -- EXIT --
if($Map{'CONFIG'} eq 'ERROR')
	{
		&UtilityFunctions::Print_Error("LinkMap Error.<BR><BR>Contact Site Administrator.", $DebugUtilityFunctions, %Map);
	}
else
	{
		$Map{'PROGRAM_NAME'} = $ProgramName;
		print "<!-- $Map{'SYSTEM'} -->\n" if $DebugThisAp eq "1";
	}

# Possible values:
#	Email_Me_My_Verification_Code
#	Verify_My_Email_Address
#	Change_My_Email_Address

my @QueryStringParams;
my %QueryStringHash;

my $afl_cookie_id		= "";
my $afl_cookie_email	= "";
my $afl_cookie_password	= "";
my $is_email_verified	= "";

# Load the values passed in into the QueryStringHash...
@QueryStringParams = CGI::param();
%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

# user_name and password are only passed if the user is verifying her email address using the link supplied to her via email...
if ( $QueryStringHash{'user_name'} eq "" or $QueryStringHash{'email'} eq "" or $QueryStringHash{'password'} eq "" )
	{
		# Since the user is not using the link supplied check the cookies for user session authentication...
		$afl_cookie_id		 = &CgiFunctions::Get_Cookie_Value("afl_cookie_id"		, $DebugCgiFunctions);
		$afl_cookie_email	 = &CgiFunctions::Get_Cookie_Value("afl_cookie_email"	, $DebugCgiFunctions);
		$afl_cookie_password = &CgiFunctions::Get_Cookie_Value("afl_cookie_password", $DebugCgiFunctions);

		if ($afl_cookie_email eq "" or $afl_cookie_password eq "") 
			{
				# Die if the user is not logged in...
				&UtilityFunctions::Afl_Print_Framed_Error("", "You must be logged in to view this page.", $DebugUtilityFunctions, %Map);
			}
		else
			{
				# Since the user session is authentic set the user_name and password variables with the same info as the cookies just to be thorough...
				$QueryStringHash{'unique_id'} = $afl_cookie_id;
				$QueryStringHash{'email'}	  = $afl_cookie_email;
				$QueryStringHash{'password'}  = $afl_cookie_password;
			}
	}
else
	{
		# Since the user is verifying using the link set the cookie variables just to be thorough...
		$afl_cookie_id			= "0";
		$afl_cookie_email		= $QueryStringHash{'email'};
		$afl_cookie_password	= $QueryStringHash{'password'};

		# Since the url is not kept in tact we must regenerate it...
#		my $processed_url = $QueryStringHash{'pmc_url'};

		my $processed_url = $Map{'CGIBIN'} . "/" . $ProgramName . "?";
		while( (my $Key, my $Value) = each(%QueryStringHash) )
		{
			print "<!-- $Key = ($Value) -->\n" if $DebugThisAp eq "1";
			$Value =~ s/ /+/g;
			if ($processed_url =~ m/\?$/) 
				{
					$processed_url = $processed_url . "$Key=$Value";
				}
			else
				{
					$processed_url = $processed_url . "&$Key=$Value";
				}
		}       
		$processed_url =~ s/\'/%27/g;

		print "<!-- processed_url = ($processed_url) -->\n" if $DebugThisAp eq "1";

		# No matter what the database returns this program should redirect the user to the passed in url...
		if($processed_url ne "")
			{
				my $query = new CGI;
				my $referrer_url = $query->referer();

				if($referrer_url !~ m%^$Map{'CGIBIN'}%gi
					and $referrer_url ne ""
					)
					{
						print "<BODY>\n";
						print "<!-- Ofending Referrer URL = ($referrer_url)-->\n";
						print "<SCRIPT LANGUAGE=JavaScript>\n";
						print "<!--\n";
						print "			document.write(\"<H2>This window has an external domain that will cause problems while viewing our pages.<BR>A new window should have been opened.</H2>\")\n";
						print "			window.open(\'$processed_url\')\n";
						print "	// -->\n";
						print "</SCRIPT>\n";
				
						print "<!-- External processed_url = ($processed_url) -->\n" if $DebugThisAp eq "1";

						print "<H3>If a new window did not open please copy and past the link below into your browser's Address Bar:</H3><H4><FONT color=\"red\">$processed_url</FONT><H4>\n";

						print "<NOSCRIPT>\n";
						print "<H3>To avoid this problem in the future please enable JavaScript</H3>\n";
						print "</NOSCRIPT>\n";

						print "</BODY>\n";
						print "</HTML>\n";
						exit 0;
					}
				else
					{
						print "<!-- Internal processed_url = ($processed_url) -->\n" if $DebugThisAp eq "1";
#						print $query->redirect($processed_url);
					}
			}
		else
			{
				print "<!-- This should never happen:  No processed_url = ($processed_url) -->\n" if $DebugThisAp eq "1";
			}
	}

# Generate the unique email verification code...
(my $sec, my $min, my $hour, my $mday, my $mon, my $year, my $wday, my $yday, my $isdst) = localtime(time);
# use parsed date to create unique verification code...
# verification code has the folling format m[m]-d[d]-yyyy-h[h]-m[m]-s[s]
my $UniqueVerificationCode = ($mon+1) . $mday . ($year+1900) . "-" . $hour . $min . $sec;

if ($QueryStringHash{'submit'} eq "Email_Me_My_Verification_Code") 
	{
		my $email_verification_code = "";
		my $SqlStatement = "afl_GetEmailVerificationInfo \'$QueryStringHash{'email'}\', \'$QueryStringHash{'password'}\'"; 
		my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
		$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
		$status = $MSSQL::DBlib::dbh->dbsqlexec();
			
		##########################
		# Get ONLY result set...
		##########################
		# dbresults() must be called for each result set...
		$status = $MSSQL::DBlib::dbh->dbresults();
		if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
			{
				&UtilityFunctions::Afl_Print_HTML_Top(\1, \$ProgramName, \$DebugUtilityFunctions, \%Map);
				if($DebugThisAp eq "1")
					{
						print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
					}
				my %dataref = ("jason" => "baumbach");
				my $dataref = \%dataref;
				# If in debug mode, print information...
				if($DebugThisAp eq '1')
					{
						print "<!-- SQL: $SqlStatement -->\n";
					}
				# Prevent infinite loop...
				while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
					{
						# Since there is no global DB error check get 
						# all database fields returned by the query...
							
						$is_email_verified = $$dataref{is_email_verified};
						$email_verification_code = $$dataref{email_verification_code};
						if($email_verification_code){$email_verification_code =~ s/\s//g}
						else{$email_verification_code = "";}
							
						if($DebugThisAp eq "1")
							{
								print "<!-- email_verification_code = ($email_verification_code) -->\n";
								print "<!-- is_email_verified       = ($is_email_verified) -->\n";
							}
					}

				my $return_value = &SendMailFunctions::Email_The_Verification_Code_To_User($QueryStringHash{'email'}, $QueryStringHash{'password'}, $QueryStringHash{'email'}, $email_verification_code, $DebugThisAp, %Map);
				if($return_value eq "1")
					{
						# Print HTML Body...
						my $StatementOfSuccess = "			<BR><BR><FONT face=\"Helvetica,Arial\">Your Email Verification Code has been sent to <FONT color=\"blue\">$QueryStringHash{'email'}</FONT>.</FONT><BR>\n";
						$StatementOfSuccess .= "				<UL>\n";
						$StatementOfSuccess .= "					<LI><FONT face=\"Helvetica,Arial\">Please check for your verification code which has been sent to <FONT color=\"blue\">$QueryStringHash{'email'}</FONT></FONT>\n";
						$StatementOfSuccess .= "					<LI><FONT face=\"Helvetica,Arial\">Once you receive your verification code you can either follow one of the 4 procedures detailed in the email or</FONT>\n";
						$StatementOfSuccess .= "					<LI><FONT face=\"Helvetica,Arial\">Verify your email address with the email verificaiton code that was sent to you by following the directions below for &#147;Option 1&#147;</FONT>\n";
						$StatementOfSuccess .= "				</UL><BR><BR>\n";
						# Print HTML Body...
						&Print_Email_Verification_Options_HTML($StatementOfSuccess, $DebugThisAp, %Map);
						&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
					}
				else
					{
						print "<!-- Unable To Send Mail -->\n" if $DebugThisAp eq "1";
						# Print HTML Body...
						my $StatementOfSuccess = "			<FONT face=\"Helvetica,Arial\" color=\"red\">Sorry, the system was unable to send the verification code to $QueryStringHash{'email'}.<BR><BR>Please try again.</FONT><BR><BR>\n";
						# Print HTML Body...
						&Print_Email_Verification_Options_HTML($StatementOfSuccess, $DebugThisAp, %Map);
						&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
					}
			}# END if($status != FAIL)
		else
			{
				print "ERROR: $SqlStatement Failed for first result set!\n";
				$status = $MSSQL::DBlib::dbh->dbcancel();
				&UtilityFunctions::Afl_Print_Framed_Error("", "ERROR: Unable to send verification code to $QueryStringHash{'email'}.  Make sure this is your correct email address.<BR>Please be sure you entered the correct Email Verification Code.<BR>\n", $DebugUtilityFunctions, %Map);
			}
	}
elsif ($QueryStringHash{'submit'} eq "Verify_My_Email_Address")
	{
		# Update login_info table to change the user's email address...
		my $SqlStatement = "afl_VerifyEmailAddress \'$QueryStringHash{'email'}\', \'$QueryStringHash{'password'}\', \'$QueryStringHash{'email_verification_code'}\'";
		
		my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
		$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
		$status = $MSSQL::DBlib::dbh->dbsqlexec();
		if($DatabaseFunctions::DatabaseError eq "1000" or $DatabaseFunctions::DatabaseError eq "1001")
			{
				$status = $MSSQL::DBlib::dbh->dbcancel();
				print "<!-- Unable to update Email Verification Status -->\n" if $DebugThisAp eq "1";
				&UtilityFunctions::Afl_Print_Framed_Error("", "ERROR: Unable to verify that $QueryStringHash{'email'} is your correct email address.<BR>Please be sure you entered the correct Email Verification Code.<BR>\n", $DebugUtilityFunctions, %Map);
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
						&UtilityFunctions::Afl_Print_HTML_Top(\1, \$ProgramName, \$DebugUtilityFunctions, \%Map);
						if($DebugThisAp eq "1")
							{
								print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
							}
						my %dataref = ("jason" => "baumbach");
						my $dataref = \%dataref;
						# If in debug mode, print information...
						if($DebugThisAp == 1)
							{
								print "<!-- SQL: $SqlStatement -->\n";
							}
						my $affiliate_tracking_id	= "";
						my $plan_unique_id			= "";
						my $profile_score			= "";
						my $credit_publisher		= "";
						# Prevent infinite loop...
						while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
							{
								$affiliate_tracking_id	= $$dataref{affiliate_tracking_id};
								$plan_unique_id			= $$dataref{plan_unique_id};
								$profile_score			= $$dataref{profile_score};
								$credit_publisher		= $$dataref{credit_publisher};

								if($DebugThisAp eq "1")
									{
										print "<!-- affiliate_tracking_id = ($affiliate_tracking_id) -->\n";
										print "<!-- plan_unique_id        = ($plan_unique_id) -->\n";
										print "<!-- profile_score	      = ($profile_score) -->\n";
										print "<!-- credit_publisher      = ($credit_publisher) -->\n";
									}
							}

						print "<!-- Updated Email Verification Status -->\n" if $DebugThisAp eq "1";
						# Print HTML Body...

						if($plan_unique_id ne "" and $profile_score ne "" and $credit_publisher ne "")
							{
								print "<SCRIPT type=\"text/javascript\" src=\"$Map{'CGIBIN'}/Afl_ProcessAction.cgi?ckuid=$affiliate_tracking_id&pluid=$plan_unique_id&pfsc=$profile_score&crpub=$credit_publisher\"></SCRIPT>\n";					
							} 
						else
							{
								print "<!-- no afl action initiated for ckuid ($affiliate_tracking_id) -->\n";
							}

						print "			<BR>\n";
						print "			<BR>\n";
						print "			<SPAN class=\"BlackTextMedium\">Your email address <FONT color=\"blue\">$QueryStringHash{'email'}</FONT> has been successfully verified.</SPAN><BR>\n";
						print "				<UL>\n";
						print "					<LI><SPAN class=\"BlackTextMedium\"><A class=\"NavText\" href=\"$Map{'ROOT'}/Afl_LogIn.html\">Click Here To Log In...</A></SPAN>\n";
						print "					<LI><SPAN class=\"BlackTextMedium\">If you are already logged in you may use the navigation links on the top of this page.</SPAN>\n";
						print "				</UL><BR><BR>\n";
						# Print HTML Bottom...
						&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
						
					}# END if($status != FAIL)
				else
					{
						$status = $MSSQL::DBlib::dbh->dbcancel();
						print "<!-- Unable to update Email Verification Status -->\n" if $DebugThisAp eq "1";
						&UtilityFunctions::Afl_Print_Framed_Error("", "ERROR: Unable to verify that $QueryStringHash{'email'} is your correct email address.<BR>Please be sure you entered the correct Email Verification Code.<BR>\n", $DebugUtilityFunctions, %Map);
					}
			}
	}
elsif ($QueryStringHash{'submit'} eq "Change_My_Email_Address")
	{
		&UtilityFunctions::Afl_Print_HTML_Top(\1, \$ProgramName, \$DebugUtilityFunctions, \%Map);
		my $email_verification_code = $UniqueVerificationCode;
		# Update login_info table to change the user's email address...
		my $SqlStatement = "afl_ChangeEmailAddress \'$QueryStringHash{'email'}\', \'$QueryStringHash{'password'}\', \'$QueryStringHash{'new_email'}\', \'$email_verification_code\'"; 
		my $return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, 'UploadPicture.cgi', $SqlStatement, $DebugDatabaseFunctions);
		if($return_value eq "1")
			{
				print "<!-- Updated Email Address -->\n" if $DebugThisAp eq "1";
				print " <SCRIPT type=\"text/javascript\" language=\"javascript\">\n";
				print "    <!--\n";
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
				
				print "     var Then = new Date()\n";
				print "     Then.setTime(Then.getTime() + 60 * 60 * 1000)\n";
				print "     document.cookie=\"afl_cookie_id=$afl_cookie_id; expires=\" + Then.toGMTString() + \"; path=/\"\n";
				print "     document.cookie=\"afl_cookie_email=$QueryStringHash{'new_email'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";
				print "     document.cookie=\"afl_cookie_password=$QueryStringHash{'password'}; expires=\" + Then.toGMTString() + \"; path=/\"\n";
				print "    //-->\n";
				print " </SCRIPT> \n";

				#Since the email change was successful change the email that will be displayed on the form...
				$QueryStringHash{'email'} = $QueryStringHash{'new_email'};

				$return_value = &SendMailFunctions::Email_The_Verification_Code_To_User($QueryStringHash{'email'}, $QueryStringHash{'password'}, $QueryStringHash{'new_email'}, $email_verification_code, $DebugThisAp, %Map);
				if($return_value eq "1")
					{
						print "<!-- Sent User Mail to ($QueryStringHash{'new_email'}) -->\n" if $DebugThisAp eq "1";
						# Print HTML Body...
						my $StatementOfSuccess = "			<BR><BR><SPAN class=\"BlackTextMedium\">Your email address has been changed to <FONT color=\"blue\">$QueryStringHash{'new_email'}</FONT>.</SPAN><BR>\n";
						$StatementOfSuccess .= "				<UL>\n";
						$StatementOfSuccess .= "					<LI><SPAN class=\"BlackTextMedium\">Please check for your verification code which has been sent to <FONT color=\"blue\">$QueryStringHash{'new_email'}</FONT></SPAN>\n";
						$StatementOfSuccess .= "					<LI><SPAN class=\"BlackTextMedium\">Once you receive your verification code you can either follow one of the 4 procedures detailed in the email or</SPAN>\n";
						$StatementOfSuccess .= "					<LI><SPAN class=\"BlackTextMedium\">Verify your email address with the email verificaiton code that was sent to you by following the directions below for &#147;Option 1&#147;</SPAN>\n";
						$StatementOfSuccess .= "				</UL><BR><BR>\n";
						&Print_Email_Verification_Options_HTML($StatementOfSuccess, $DebugThisAp, %Map);
						# Print HTML Body...

					}
				else
					{
						print "<!-- Unable To Send Mail -->\n" if $DebugThisAp eq "1";
						my $StatementOfSuccess = "			<SPAN class=\"RedTextLargeBold\">Sorry, the system was unable to send the verification code to $QueryStringHash{'new_email'}.<BR><BR>Please try again.</SPAN><BR><BR>\n";
						# Print HTML Body...
						&Print_Email_Verification_Options_HTML($StatementOfSuccess, $DebugThisAp, %Map);
					}
			}
		else
			{
				print "<!-- Unable to Update Email Address -->\n" if $DebugThisAp eq "1";
				my $StatementOfSuccess = "			<SPAN class=\"BlackTextMedium\">Sorry, the system was unable to to update your email address from $QueryStringHash{'email'} to $QueryStringHash{'new_email'}.<BR><BR>Please try again.</SPAN><BR><BR>\n";
				# Print HTML Body...
				&Print_Email_Verification_Options_HTML($StatementOfSuccess, $DebugThisAp, %Map);
			}
		&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
	}
else
	{
		my $SqlStatement = "afl_GetEmailVerificationInfo \'$QueryStringHash{'email'}\', \'$QueryStringHash{'password'}\'"; 
		my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
		$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
		$status = $MSSQL::DBlib::dbh->dbsqlexec();
			
		my $email = "";
		##########################
		# Get ONLY result set...
		##########################
		# dbresults() must be called for each result set...
		$status = $MSSQL::DBlib::dbh->dbresults();
		if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
			{
				&UtilityFunctions::Afl_Print_HTML_Top(\1, \$ProgramName, \$DebugUtilityFunctions, \%Map);
				if($DebugThisAp eq "1")
					{
						print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
					}
				my %dataref = ("jason" => "baumbach");
				my $dataref = \%dataref;
				# If in debug mode, print information...
				if($DebugThisAp == 1)
					{
						print "<!-- SQL: $SqlStatement -->\n";
					}
				# Prevent infinite loop...
				while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
					{
						# Since there is no global DB error check get 
						# all database fields returned by the query...
							
						$email = $$dataref{email};
						if($email){$email =~ s/\s//g}
						else{$email = "";}
							
						$is_email_verified = $$dataref{is_email_verified};
						if($is_email_verified){$is_email_verified =~ s/\s//g}
						else{$is_email_verified = "";}
							
						if($DebugThisAp eq "1")
							{
								print "<!-- email             = ($email) -->\n";
								print "<!-- is_email_verified = ($is_email_verified) -->\n";
							}
					}
				# Print HTML Body...
				my $StatementOfSuccess = "";
				&Print_Email_Verification_Options_HTML($StatementOfSuccess, $DebugThisAp, %Map);
				# Print HTML Bottom...
				&UtilityFunctions::Afl_Print_HTML_Bottom(\$ProgramName, \$DebugUtilityFunctions, \%Map);
			}# END if($status != FAIL)
		else
			{
				$status = $MSSQL::DBlib::dbh->dbcancel();
				print "<!-- ERROR: $SqlStatement Failed for first result set! -->\n" if $DebugThisAp eq "1";
				&UtilityFunctions::Afl_Print_Framed_Error("", "You must be logged in to view this page.", $DebugUtilityFunctions, %Map);
			}
	}

print "</HTML>\n";
 


sub Print_Email_Verification_Options_HTML
	{
		(my $Statement, my $Debug, my %Map) = @_;

		print "      <BR>\n";
		print "      <CENTER>\n";
		print "      <TABLE border=\"1\" cellspacing=\"0\" width=\"80%\" cellpadding=\"5\">\n";
		print "          <TD align=\"middle\" width=\"100%\" bgcolor=\"#FFFFFF\">\n";
		print "           <DIV align=\"left\">\n";
		print "             $Statement\n";
		print "           </DIV>\n";
		if($is_email_verified eq '1')
			{
				print "          <FONT size=\"2\" face=\"Helvetica,Arial\">Your email address (<STRONG>$QueryStringHash{'email'}</STRONG>) has been verified.<BR><BR>If you change this email address you will have to verify the new address in order to regain access to all the features of $Map{'WHICH_CONNECTIONS'}.com</FONT> \n";
			}
		else
			{
				print "          <FONT size=\"2\" face=\"Helvetica,Arial\">Your email address (<STRONG>$QueryStringHash{'email'}</STRONG>) has <FONT color=\" color=\"#8B0000\"\">NOT</FONT> been verified.<BR><BR>To access the features of $Map{'WHICH_CONNECTIONS'}.com you must first verify that you have access to the above email address.</FONT> \n";
			}
		print "		  <HR>\n";
		print "          <FONT size=\"3\" face=\"Helvetica,Arial\" color=\"Blue\"><STRONG>Email Verification Options...</STRONG></FONT> \n";
		print "          <HR>\n";
		print "          <TABLE border=\"0\" width=\"50%\" cellpadding=\"5\">\n";
		print "            <TR>\n";
		print "              <TD height=\"54\">\n";
		print "				<FONT face=\"arial,helvetica\" color=\"#990000\"><STRONG><FONT color=\"Blue\">Option 1:</FONT><BR>Enter Your Email Verification Number...</STRONG></FONT>\n";
		print "				<BR>\n";
		print "				  <OL>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">If you do not have an Email Verification Code follow the &#147;Option 2&#147; directions below.</FONT>\n";
		print "					</LI>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">If you have already received your Email Verification Code please enter it below.</FONT>\n";
		print "					</LI>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">Press the &#147;Verify_My_Email_Address&#148; button to verify your email address.</FONT>\n";
		print "					</LI>\n";
		print "				  </OL>\n";
		print "<!--\n";
		print "				  <CENTER>\n";
		print "					<FONT face=\"Arial, Helvetica, sans-serif\" size=\"-1\" color=\"800000\">(Alternatively: Follow the link provided in your confirmation email to automatically activate your account.)</FONT>\n";
		print "				  </CENTER>\n";
		print "-->\n";
		print "				<FORM onsubmit=\"return checkFormOne(this)\" action=\"ManageEmailVerification.cgi\" method=\"POST\">\n";
		print "					<TABLE>\n";
		print "					  <TBODY>\n";
		print "		              <!-- email -->\n";
		print "					  <TR>\n";
		print "						<TD align=\"right\">\n";
		print "						  <P>\n";
		print "							 <FONT size=\"-1\" face=\"Arial, Helvetica, sans-serif\">Email:</FONT>\n";
		print "						  </P>\n";
		print "						</TD>\n";
		print "						<TD align=\"left\">\n";
		print "						  <P>\n";
		print "							 <INPUT type=\"hidden\" name=\"email\" value=\"$QueryStringHash{'email'}\">\n";
		print "							 <FONT face=\"Arial, Helvetica, sans-serif\"><STRONG>$QueryStringHash{'email'}</STRONG></FONT>\n";
		print "						  </P>\n";
		print "						</TD>\n";
		print "					  </TR>\n";
		print "					  <!--    verification_code -->\n";
		print "					  <TR>\n";
		print "						<TD align=\"right\">\n";
		print "						  <FONT size=\"-1\" face=\"Arial, Helvetica, sans-serif\">Verification Code:</FONT>\n";
		print "						</TD>\n";
		print "						<TD align=\"left\">\n";
		print "						  <FONT face=\"Arial, Helvetica, sans-serif\"> <INPUT name=\"email_verification_code\" size=\"20\"> <FONT color=\"#FF0000\" size=\"-1\">Number emailed to you.</FONT></FONT>\n";
		print "						</TD>\n";
		print "					  </TR>\n";
		print "						<TR>\n";
		print "						  <TD>\n";
		print "							&nbsp;\n";
		print "						  </TD>\n";
		print "						  <TD>\n";
		print "							<FONT face=\"geneva,arial\" size=\"-4\"><INPUT type=\"submit\" value=\"Verify_My_Email_Address\" name=\"submit\"></FONT>\n";
		print "						  </TD>\n";
		print "						</TR>\n";
		print "					  </TBODY>\n";
		print "					</TABLE>\n";
		print "				</FORM>\n";
		print "              </TD>\n";
		print "            </TR>\n";
		print "          </TABLE>\n";
		print "		  <HR>\n";
		print "          <TABLE border=\"0\" width=\"50%\" cellpadding=\"5\">\n";
		print "            <TR>\n";
		print "              <TD height=\"54\">\n";
		print "				<FONT face=\"arial,helvetica\" color=\"#990000\"><STRONG><FONT color=\"Blue\">Option 2:</FONT><BR>Receive Your Verification Number...</STRONG></FONT>\n";
		print "				<BR>\n";
		print "				  <OL>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">If the Email Address below is not correct follow the directions for &#147;Option 3&#148; to change your existing email address.</FONT>\n";
		print "					</LI>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">If the Email Address below is correct press the &#147;Email_Me_My_Verification_Code&#148; button to send a Verification Code to your current email address.</FONT>\n";
		print "					</LI>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">Once you receive your Verification Code use it to complete &#147;Option 1&#147; above.</FONT>\n";
		print "					</LI>\n";
		print "				  </OL>\n";
		print "				<FORM action=\"ManageEmailVerification.cgi\" method=\"POST\">\n";
		print "					<TABLE>\n";
		print "					  <TBODY>\n";
		print "						<TR>\n";
		print "						  <TD align=\"right\">\n";
		print "							<FONT face=\"geneva,arial\" size=\"-4\">Email Address:</FONT>\n";
		print "						  </TD>\n";
		print "						  <TD>\n";
		print "							 <INPUT type=\"hidden\" name=\"email\" value=\"$QueryStringHash{'email'}\">\n";
		print "							 <FONT face=\"Arial, Helvetica, sans-serif\"><STRONG>$QueryStringHash{'email'}</STRONG></FONT>\n";
		print "						  </TD>\n";
		print "						</TR>\n";
		print "						<TR>\n";
		print "						  <TD>\n";
		print "							&nbsp;\n";
		print "						  </TD>\n";
		print "						  <TD>\n";
		print "							<FONT face=\"geneva,arial\" size=\"-4\"><INPUT type=\"submit\" value=\"Email_Me_My_Verification_Code\" name=\"submit\"></FONT>\n";
		print "						  </TD>\n";
		print "						</TR>\n";
		print "			            <TR>\n";
		print "						  <TD>\n";
		print "							&nbsp;\n";
		print "						  </TD>\n";
		print "						  <TD>\n";
		print "								<FONT face=\"Arial, Helvetica, sans-serif\" size=\"-1\" color=\"800000\">(You should receive your email verification code within 5 minutes.)</FONT>\n";
		print "						  </TD>\n";
		print "						</TR>\n";
		print "					  </TBODY>\n";
		print "					</TABLE>\n";
		print "				</FORM>\n";
		print "              </TD>\n";
		print "            </TR>\n";
		print "          </TABLE>\n";
		print "          <HR>\n";
		print "          <TABLE border=\"0\" width=\"50%\" cellpadding=\"5\">\n";
		print "            <TR>\n";
		print "              <TD height=\"54\">\n";
		print "				<FONT face=\"arial,helvetica\" color=\"#990000\"><STRONG><FONT color=\"Blue\">Option 3:</FONT><BR>Change Your Email Address...</STRONG></FONT>\n";
		print "				<BR>\n";
		print "				  <OL>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">Enter your new email address.</FONT>\n";
		print "					</LI>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">Press the &#147;Change_My_Email_Address&#148; button to change your email address.</FONT>\n";
		print "					</LI>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">Once you change your email address you will have to following the directions for &#147;Option 2&#147; above to receive your new Email Verification Code.</FONT>\n";
		print "					</LI>\n";
		print "					<LI>\n";
		print "					  <FONT size=\"1\" color=\"800000\" face=\"Helvetica,Arial\">Once you receive your Email Verification Code you will hve to follow the directions for &#147;Option 1&#147; above to verify your new email address.</FONT>\n";
		print "					</LI>\n";
		print "				  </OL>\n";
		print "				<FORM onsubmit=\"return checkFormTwo(this)\" action=\"ManageEmailVerification.cgi\" method=\"POST\">\n";
		print "					<TABLE>\n";
		print "					  <TBODY>\n";
		print "						<TR>\n";
		print "						  <TD align=\"right\">\n";
		print "							<FONT face=\"geneva,arial\" size=\"-4\">Current Email Address:</FONT>\n";
		print "						  </TD>\n";
		print "						  <TD>\n";
		print "							 <INPUT type=\"hidden\" name=\"email\" value=\"$QueryStringHash{'email'}\"><FONT face=\"Arial, Helvetica, sans-serif\"><STRONG>$QueryStringHash{'email'}</STRONG></FONT>\n";
		print "						  </TD>\n";
		print "						</TR>\n";
		print "						<TR>\n";
		print "						  <TD align=\"right\">\n";
		print "							<FONT face=\"geneva,arial\" size=\"-4\">New Email Address:</FONT>\n";
		print "						  </TD>\n";
		print "						  <TD>\n";
		print "							<INPUT size=\"32\" name=\"new_email\">\n";
		print "						  </TD>\n";
		print "						</TR>\n";
		print "						<TR>\n";
		print "						  <TD>\n";
		print "							&nbsp;\n";
		print "						  </TD>\n";
		print "						  <TD>\n";
		print "							<FONT face=\"geneva,arial\" size=\"-4\"><INPUT type=\"submit\" value=\"Change_My_Email_Address\" name=\"submit\"></FONT>\n";
		print "						  </TD>\n";
		print "						</TR>\n";
		print "					  </TBODY>\n";
		print "					</TABLE>\n";
		print "				</FORM>\n";
		print "              </TD>\n";
		print "            </TR>\n";
		print "          </TABLE>\n";
		print "			<SCRIPT language=\"javascript\" src=\"$Map{'ROOT'}/JavaScript/ManageEmailVerification.js\"></SCRIPT>\n";
		print "          <HR>\n";
		print "          </TD>\n";
		print "      </TABLE>\n";
		print "      </CENTER>\n";
	}

exit 0;