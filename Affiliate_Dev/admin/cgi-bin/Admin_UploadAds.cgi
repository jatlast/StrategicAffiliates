#!/usr/local/bin/perl -w
use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

use CGI qw/:standard/;
use strict;

# Add directories to perl environment path...
# Smithers
unshift @INC, "D:/Required/INC/";
# Grimes
unshift @INC, "C:/Required/INC/";

require "DatabaseFunctions.pl";
require "CgiFunctions.pl";
require "UtilityFunctions.pl";

my $DebugThisAp			   = "1";
my $DebugCgiFunctions 	   = "1";
my $DebugDatabaseFunctions = "1";
my $DebugUtilityFunctions  = "1";

my $ProgramName = "Admin_UploadAds.cgi";

my $banner_dot_extension = "";
my $ad_unique_id = "";
my $return_value = 0;

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

		$CGI::POST_MAX=1024 * 10000;  # max 250K posts

		# declare global variables...
		my @QueryStringParams;
		my %QueryStringHash;
		# Load the values passed in into the QueryStringHash...
		@QueryStringParams = CGI::param();
		%QueryStringHash = &CgiFunctions::Load_Query_String_Hash(\@QueryStringParams, \$DebugCgiFunctions);

		if($QueryStringHash{'submit'} eq "Upload Banner")
			{
				if($QueryStringHash{'banner_name_and_path'} eq "")
				{
					# die if no file_name was supplied...
					&UtilityFunctions::Print_Framed_Error("Field 'File Name' must be filled in for this script to work properly.", $DebugUtilityFunctions, %Map);
				}

				# find the file extension...
				$QueryStringHash{'banner_name_and_path'} =~ m/(\.\w+)/;
				$banner_dot_extension = $1;
					
				# check file dot_extension...
				if(&Check_File_Type($banner_dot_extension, $DebugThisAp) eq "-1")
				{
					&UtilityFunctions::Print_Framed_Error("We do not accept pictures of type <FONT color=red>\"" . $banner_dot_extension . "\"</FONT> at this time.<BR>Please choose a new picture to upload.", $DebugUtilityFunctions, %Map);
				}

				my $banner_pixel_width  = "";
				my $banner_pixel_height = "";

				# parse pixel width and length...
				if($QueryStringHash{'width_x_height'})
				{
					($banner_pixel_width, $banner_pixel_height) = split(/x/, $QueryStringHash{'width_x_height'});
				}

				if($DebugThisAp eq "1")
				{
					print "\n\n<!-- ";
					print "DBUSER = ($Map{'DBUSER'})\n";
					print "DBPWD  = ($Map{'DBPWD'})\n";
					print "DBNAME = ($Map{'DBNAME'})\n";
					print "-->\n\n";
				}

				if(
					   $QueryStringHash{'target_url'} !~ m%^http://% 
					and $QueryStringHash{'target_url'} !~ m%^https://% 
					and $QueryStringHash{'target_url'} !~ m%^ftp://% 
					)
				{
					$QueryStringHash{'target_url'} = "http://" . $QueryStringHash{'target_url'};
				}

				##########################################################
				# Remove single quotes for SQL statement...
				##########################################################
				# Remove single quotes from description field...
				if($QueryStringHash{'ad_name'} =~ m/\'/g)
				{
					$QueryStringHash{'ad_name'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from site_name field...
				if($QueryStringHash{'ad_description'} =~ m/\'/g)
				{
					$QueryStringHash{'ad_description'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from site_name field...
				if($QueryStringHash{'alt_text'} =~ m/\'/g)
				{
					$QueryStringHash{'alt_text'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from site_name field...
				if($QueryStringHash{'mouse_over_text'} =~ m/\'/g)
				{
					$QueryStringHash{'mouse_over_text'} =~ s/\'/\'\'/gis;
				}
				##########################################################

				my $SqlStatement = "admin_CreateNewBannerAd \'$QueryStringHash{'afl_unique_id'}\'\
																, \'$QueryStringHash{'ad_type'}\'\
																, \'$banner_dot_extension\'\
																, \'$banner_pixel_width\'\
																, \'$banner_pixel_height\'\
																, \'$QueryStringHash{'ad_name'}\'\
																, \'$QueryStringHash{'ad_description'}\'\
																, \'$QueryStringHash{'target_url'}\'\
																, \'$QueryStringHash{'alt_text'}\'\
																, \'$QueryStringHash{'mouse_over_text'}\'\
																"; 
				my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
				$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
				$status = $MSSQL::DBlib::dbh->dbsqlexec();
					
				if($DatabaseFunctions::DatabaseError eq "1016")
					{
						&UtilityFunctions::Afl_Print_Framed_Error("", "Database Rollback Error.<BR><BR>\n\nPlease try again.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
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
										print "<!-- DbError: ($DatabaseFunctions::DatabaseError) -->\n";
										print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
									}
								my %dataref = ("jason" => "baumbach");
								my $dataref = \%dataref;
								# If in debug mode, print information...
								if($DebugThisAp == 1)
									{
										print "<!-- SQL: $SqlStatement -->\n";
									}
								# Check for global DB error...
								if($DatabaseFunctions::DatabaseError eq "1")
									{
										print "ERROR: ($SqlStatement) Failed!<BR>\n";
									}
								else
									{
										# Prevent infinite loop...
										while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
											{
												# Since there is no global DB error check get 
												# all database fields returned by the query...
												
												$ad_unique_id = $$dataref{ad_unique_id};

												if($DebugThisAp eq "1")
													{
														print "<!-- ad_unique_id = ($ad_unique_id) -->\n";
													}	
											}

										$return_value = &Save_Banner(\$QueryStringHash{'banner_name_and_path'}
																		, \$ad_unique_id
																		, \$banner_dot_extension
																		, \$DebugThisAp
																		, \%Map
																	);
										if($return_value == 1)
											{
                                                print "			<TABLE cellpadding=\"20\" cellspacing=\"0\" align=\"center\">\n";
                                                print "			  <TR>\n";
                                                print "				<TD>\n";
                                                print "					Banner (" . $ad_unique_id . $banner_dot_extension . ") has been successfully added to the database.<BR>Below is how this Banner will appear.\n";
                                                print "				</TD>\n";
                                                print "			  </TR>\n";
                                                print "			  <TR>\n";
                                                print "				<TD>\n";
                                                print "					<script type=\"text/javascript\" src=\"" . $Map{'CGIBIN'} . "/" . $Map{'AFL_RETRIEVE'} . "?auid=" . $ad_unique_id . "&sid=0&acid=0&r=0&p=0\"></script> \n";
                                                print "					<noscript>Please enable JavaScript!!</noscript>\n";
                                                print "				</TD>\n";
                                                print "			  </TR>\n";
												print "			  <TR>\n";
												print "				<TD>\n";
												print "				  <A href=\"" . $Map{'ROOT'} . "/Admin/Admin_UploadAds.html\" class=\"NavText\">Upload Another Ad...</a>\n";
												print "				</TD>\n";
												print "			  </TR>\n";
                                                print "			  <TR>\n";
                                                print "				<TD>\n";
												print "				 <FORM method=\"GET\" action=\"Admin_UploadAds.cgi\">\n";
												print "				   <TABLE width=\"100%\" border=\"0\" cellspacing=\"3\" cellpadding=\"3\">\n";
												print "				     <TR>\n";
												print "				       <TD>\n";
												print "				         <INPUT type=\"hidden\" name=\"ad_unique_id\" value=\"" . $ad_unique_id . "\">\n";
												print "				         <INPUT type=\"hidden\" name=\"ad_type\" value=\"" . $QueryStringHash{'ad_type'} . "\">\n";
												print "				         <INPUT type=\"hidden\" name=\"banner_dot_extension\" value=\"" . $banner_dot_extension . "\">\n";
												print "				         <INPUT type=\"submit\" name=\"submit\" value=\"Delete This Ad\">\n";
												print "				       </TD>\n";
												print "				     </TR>\n";
												print "				   </TABLE>\n";
												print "				 </FORM>\n";
                                                print "				</TD>\n";
                                                print "			  </TR>\n";
                                                print "			</TABLE>\n";
											}
										else
											{
												&UtilityFunctions::Print_Framed_Error("Error handling the file (" . $ad_unique_id . $banner_dot_extension . ").<BR>\n", $DebugUtilityFunctions, %Map);
											}

									}# END else (No db error) 
							}# END if($status != FAIL)
						else
							{
								print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
								&UtilityFunctions::Afl_Print_Framed_Error("", "DB ERROR: Unable to create banner (" . $ad_unique_id . $banner_dot_extension . ").<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
							}
					}
			}
		elsif($QueryStringHash{'submit'} eq "Upload Text Link")
			{
				if(
					   $QueryStringHash{'target_url'} !~ m%^http://% 
					and $QueryStringHash{'target_url'} !~ m%^https://% 
					and $QueryStringHash{'target_url'} !~ m%^ftp://% 
					)
				{
					$QueryStringHash{'target_url'} = "http://" . $QueryStringHash{'target_url'};
				}

				##########################################################
				# Remove single quotes for SQL statement...
				##########################################################
				# Remove single quotes from description field...
				if($QueryStringHash{'text_link_text'} =~ m/\'/g)
				{
					$QueryStringHash{'text_link_text'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from description field...
				if($QueryStringHash{'ad_name'} =~ m/\'/g)
				{
					$QueryStringHash{'ad_name'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from site_name field...
				if($QueryStringHash{'ad_description'} =~ m/\'/g)
				{
					$QueryStringHash{'ad_description'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from site_name field...
				if($QueryStringHash{'alt_text'} =~ m/\'/g)
				{
					$QueryStringHash{'alt_text'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from site_name field...
				if($QueryStringHash{'mouse_over_text'} =~ m/\'/g)
				{
					$QueryStringHash{'mouse_over_text'} =~ s/\'/\'\'/gis;
				}
				##########################################################

				my $SqlStatement = "admin_CreateNewTextLinkAd \'$QueryStringHash{'afl_unique_id'}\'\
																, \'$QueryStringHash{'ad_type'}\'\
																, \'$QueryStringHash{'text_link_text'}\'\
																, \'$QueryStringHash{'ad_name'}\'\
																, \'$QueryStringHash{'ad_description'}\'\
																, \'$QueryStringHash{'target_url'}\'\
																, \'$QueryStringHash{'alt_text'}\'\
																, \'$QueryStringHash{'mouse_over_text'}\'\
																"; 
				my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
				$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
				$status = $MSSQL::DBlib::dbh->dbsqlexec();
					
				if($DatabaseFunctions::DatabaseError eq "1016")
					{
						&UtilityFunctions::Afl_Print_Framed_Error("", "Database Rollback Error.<BR><BR>\n\nPlease try again.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
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
										print "<!-- DbError: ($DatabaseFunctions::DatabaseError) -->\n";
										print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
									}
								my %dataref = ("jason" => "baumbach");
								my $dataref = \%dataref;
								# If in debug mode, print information...
								if($DebugThisAp == 1)
									{
										print "<!-- SQL: $SqlStatement -->\n";
									}
								# Check for global DB error...
								if($DatabaseFunctions::DatabaseError eq "1")
									{
										print "ERROR: ($SqlStatement) Failed!<BR>\n";
									}
								else
									{
										# Prevent infinite loop...
										while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
											{
												# Since there is no global DB error check get 
												# all database fields returned by the query...
												
												$ad_unique_id = $$dataref{ad_unique_id};

												if($DebugThisAp eq "1")
													{
														print "<!-- ad_unique_id = ($ad_unique_id) -->\n";
													}	
											}

										print "			<TABLE cellpadding=\"20\" cellspacing=\"0\" align=\"center\">\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "					Text Link Ad (" . $QueryStringHash{'ad_name'} . ") has been successfully added to the database.<BR>Below is how this Text Link will appear.\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "					<script type=\"text/javascript\" src=\"" . $Map{'CGIBIN'} . "/" . $Map{'AFL_RETRIEVE'} . "?auid=" . $ad_unique_id . "&sid=0&acid=0&r=0&p=0&o=0\"></script> \n";
										print "					<noscript>Please enable JavaScript!!</noscript>\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "				  <A href=\"" . $Map{'ROOT'} . "/Admin/Admin_UploadAds.html\" class=\"NavText\">Upload Another Ad...</a>\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "				 <FORM method=\"GET\" action=\"Admin_UploadAds.cgi\">\n";
										print "				   <TABLE width=\"100%\" border=\"0\" cellspacing=\"3\" cellpadding=\"3\">\n";
										print "				     <TR>\n";
										print "				       <TD>\n";
										print "				         <INPUT type=\"hidden\" name=\"ad_unique_id\" value=\"" . $ad_unique_id . "\">\n";
										print "				         <INPUT type=\"hidden\" name=\"ad_type\" value=\"" . $QueryStringHash{'ad_type'} . "\">\n";
										print "				         <INPUT type=\"submit\" name=\"submit\" value=\"Delete This Ad\">\n";
										print "				       </TD>\n";
										print "				     </TR>\n";
										print "				   </TABLE>\n";
										print "				 </FORM>\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			</TABLE>\n";

									}# END else (No db error) 
							}# END if($status != FAIL)
						else
							{
								print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
								&UtilityFunctions::Afl_Print_Framed_Error("", "DB ERROR: Unable to create Text Link Ad (" . $QueryStringHash{'ad_name'} . ").<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
							}
					}
			}
		elsif($QueryStringHash{'submit'} eq "Upload Interactive HTML")
			{
				##########################################################
				# Remove single quotes for SQL statement...
				##########################################################
				# Remove single quotes from description field...
				if($QueryStringHash{'html_block'} =~ m/\'/g)
				{
					$QueryStringHash{'html_block'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from description field...
				if($QueryStringHash{'ad_name'} =~ m/\'/g)
				{
					$QueryStringHash{'ad_name'} =~ s/\'/\'\'/gis;
				}
				# Remove single quotes from site_name field...
				if($QueryStringHash{'ad_description'} =~ m/\'/g)
				{
					$QueryStringHash{'ad_description'} =~ s/\'/\'\'/gis;
				}
				##########################################################

				my $SqlStatement = "admin_CreateNewInteractiveHtmlAd \'$QueryStringHash{'afl_unique_id'}\'\
																, \'$QueryStringHash{'ad_type'}\'\
																, \'$QueryStringHash{'html_block'}\'\
																, \'$QueryStringHash{'ad_name'}\'\
																, \'$QueryStringHash{'ad_description'}\'\
																"; 
				my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, "$ProgramName");
				$status = $MSSQL::DBlib::dbh->dbcmd($SqlStatement);
				$status = $MSSQL::DBlib::dbh->dbsqlexec();
					
				if($DatabaseFunctions::DatabaseError eq "1016")
					{
						&UtilityFunctions::Afl_Print_Framed_Error("", "Database Rollback Error.<BR><BR>\n\nPlease try again.<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>", $DebugUtilityFunctions, %Map);		
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
										print "<!-- DbError: ($DatabaseFunctions::DatabaseError) -->\n";
										print "<!-- SUCCESS: $SqlStatement returned with dbresults status = ($status). -->\n";
									}
								my %dataref = ("jason" => "baumbach");
								my $dataref = \%dataref;
								# If in debug mode, print information...
								if($DebugThisAp == 1)
									{
										print "<!-- SQL: $SqlStatement -->\n";
									}
								# Check for global DB error...
								if($DatabaseFunctions::DatabaseError eq "1")
									{
										print "ERROR: ($SqlStatement) Failed!<BR>\n";
									}
								else
									{
										# Prevent infinite loop...
										while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
											{
												# Since there is no global DB error check get 
												# all database fields returned by the query...
												
												$ad_unique_id = $$dataref{ad_unique_id};

												if($DebugThisAp eq "1")
													{
														print "<!-- ad_unique_id = ($ad_unique_id) -->\n";
													}	
											}

										print "			<TABLE cellpadding=\"20\" cellspacing=\"0\" align=\"center\">\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "					Interactive HTML Ad (" . $QueryStringHash{'ad_name'} . ") has been successfully added to the database.<BR>Below is how this Interactive HTML Ad will appear.\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "					<script type=\"text/javascript\" src=\"" . $Map{'CGIBIN'} . "/" . $Map{'AFL_RETRIEVE'} . "?auid=" . $ad_unique_id . "&sid=0&acid=0&r=0&p=0\"></script> \n";
										print "					<noscript>Please enable JavaScript!!</noscript>\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "				  <A href=\"" . $Map{'ROOT'} . "/Admin_UploadBannerAd.html\" class=\"NavText\">Upload Another Ad...</a>\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			  <TR>\n";
										print "				<TD>\n";
										print "				 <FORM method=\"GET\" action=\"Admin_UploadAds.cgi\">\n";
										print "				   <TABLE width=\"100%\" border=\"0\" cellspacing=\"3\" cellpadding=\"3\">\n";
										print "				     <TR>\n";
										print "				       <TD>\n";
										print "				         <INPUT type=\"hidden\" name=\"ad_unique_id\" value=\"" . $ad_unique_id . "\">\n";
										print "				         <INPUT type=\"hidden\" name=\"ad_type\" value=\"" . $QueryStringHash{'ad_type'} . "\">\n";
										print "				         <INPUT type=\"submit\" name=\"submit\" value=\"Delete This Ad\">\n";
										print "				       </TD>\n";
										print "				     </TR>\n";
										print "				   </TABLE>\n";
										print "				 </FORM>\n";
										print "				</TD>\n";
										print "			  </TR>\n";
										print "			</TABLE>\n";
									}# END else (No db error) 
							}# END if($status != FAIL)
						else
							{
								print "<!-- Database Error running SQL: \n($SqlStatement)\n -->\n" if $DebugThisAp eq "1";
								&UtilityFunctions::Afl_Print_Framed_Error("", "DB ERROR: Unable to create Interactive HTML Ad (" . $QueryStringHash{'ad_name'} . ").<BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n<BR>\n", $DebugUtilityFunctions, %Map);
							}
					}
			}
		elsif($QueryStringHash{'submit'} eq "Delete This Ad")
			{
				my $return_value = "1";
				if($QueryStringHash{'ad_type'} eq "1")
					{
						$return_value = &UtilityFunctions::Delete_Banner(\$QueryStringHash{'ad_unique_id'}
														, \$QueryStringHash{'banner_dot_extension'}
														, \$DebugThisAp
														, \%Map
													);
					}

				if($return_value eq "1")
					{
						my $SqlStatement = "afl_DeleteAd \'$QueryStringHash{'ad_unique_id'}\'"; 

						my $db_return_value = &DatabaseFunctions::Run_This_Sql_Statement($Map{'DBUSER'}, $Map{'DBPWD'}, $Map{'DBNAME'}, $ProgramName, $SqlStatement, $DebugDatabaseFunctions);
						if($db_return_value eq "1")
							{
								print "			<TABLE cellpadding=\"20\" cellspacing=\"0\" align=\"center\">\n";
								print "			  <TR>\n";
								print "				<TD>\n";
								print "					Ad (" . $QueryStringHash{'ad_unique_id'} . ") has been successfully deleted from the database.\n";
								print "				</TD>\n";
								print "			  </TR>\n";
								print "			  <TR>\n";
								print "				<TD>\n";
								print "				  <A href=\"" . $Map{'ROOT'} . "/Admin/Admin_UploadAds.html\" class=\"NavText\">Upload Another Ad...</a>\n";
								print "				</TD>\n";
								print "			  </TR>\n";
								print "			</TABLE>\n";
							}
						else
							{
								&UtilityFunctions::Afl_Print_Framed_Error("", "ERROR: Unable to delete Banner (" . $QueryStringHash{'ad_unique_id'} . $QueryStringHash{'banner_dot_extension'} . ") from the database.<BR><BR><FONT COLOR=\"#0000FF\">Note: If you think this is incorrect please contact $Map{'EMAIL'}.</FONT><BR>\n<!-- SQL: \n($SqlStatement)\n DbError: \n($DatabaseFunctions::DatabaseError)\n -->\n", $DebugUtilityFunctions, %Map);
							}
					}
				else
					{
						&UtilityFunctions::Print_Framed_Error("Error handling the file (" . $ad_unique_id . $banner_dot_extension . ").<BR>\n", $DebugUtilityFunctions, %Map);
					}

			}
		else
			{
				&UtilityFunctions::Print_Framed_Error("This page is not directly accessable.\n<!-- This should never happen.  submit=($QueryStringHash{'submit'}) -->\n", $DebugUtilityFunctions, %Map);
			}
	}

	

#End HTML...
print "</HTML>\n";
exit 0;

sub Check_File_Type
	{
		my ($file_name, $DebugThisAp) = @_;
		if(
		   $file_name =~ m/\.jpg$/i
		|| $file_name =~ m/\.jpe$/i
		|| $file_name =~ m/\.jpeg$/i
		|| $file_name =~ m/\.gif$/i
#		|| $file_name =~ m/\.pcx$/ 
#		|| $file_name =~ m/\.dcx$/ 
#		|| $file_name =~ m/\.xif$/ 
#		|| $file_name =~ m/\.wif$/ 
#		|| $file_name =~ m/\.tif$/ 
#		|| $file_name =~ m/\.tiff$/ 
#		|| $file_name =~ m/\.jfx$/ 
#		|| $file_name =~ m/\.bmp$/ 
		)
			{
				return "1";
			}
		else
			{
				return "-1"
			}
	}

sub Save_Banner
	{
		my $FileNameAndPath	= shift;
		my $BannerName		= shift;
		my $FileExtension	= shift;
		my $Debug			= shift;
		my $MapHash			= shift;

		my $opened = open (NEWFILE, "> $$MapHash{'BANNER_FOLDER'}" . "$$BannerName" . "$$FileExtension");		
		if($$Debug eq "1")
		{
			print "\n\n<!-- ";
			print "Save_Picture($$FileNameAndPath, $$BannerName, $$FileExtension, $$Debug, $$MapHash{'BANNER_FOLDER'})\n";
			print "Banner Full Path = ($$MapHash{'BANNER_FOLDER'}" . "$$BannerName" . "$$FileExtension" . ")\n";
			print "-->\n\n";
		}
		if ($opened)
			{
				while(read($$FileNameAndPath, my $data, 2048))
					{
						binmode NEWFILE;
						print NEWFILE $data;
					} 
				close (NEWFILE);
				return "1";
			}
		else
			{
				&UtilityFunctions::Print_Framed_Error("Error uploading your picture.\n <!-- Could not open (" . $$MapHash{'BANNER_FOLDER'} . $$BannerName . $$FileExtension . ") Error: ($!) -->\n<BR>\n", $$Debug, %$MapHash);
				return "-1";
			}
	} # End Save_Picture.

