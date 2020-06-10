#!/usr/local/bin/perl -w

use strict;

package GraphingFunctions;

use MSSQL::DBlib;
use MSSQL::DBlib::Const::General;
use MSSQL::DBlib::Const::Datatypes;

use GD::Graph::mixed;
use GD::Graph::colour;
use GD::Graph::Data;

sub Create_And_Return_Graph_Location
{

	my $SqlStatement	= shift;
	my $GraphType		= shift;
	my $GraphTitle		= shift;
	my $LegendArray		= shift;
	my $Width			= shift;
	my $Height			= shift;
	my $GraphPath		= shift;
	my $GraphName		= shift;
	my $Debug			= shift;
	my $MapHash			= shift;

	if($$GraphType eq "bars")
		{
			use GD::Graph::bars;
		}
	elsif($$GraphType eq "lines")
		{
			use GD::Graph::lines;
		}
	elsif($$GraphType eq "linespoints")
		{
			use GD::Graph::linespoints;
		}
	else
		{
			print "<!-- GRAPH ERROR:  Unrecognized graph type of ($$GraphType) -->";
			return "graph_error.jpg";
		}

	my $DebugPrintColorHTML	   = "1";

	my @ColorsArray = ($$MapHash{'GRAPH_COLOR_1'}
						, $$MapHash{'GRAPH_COLOR_2'}
						, $$MapHash{'GRAPH_COLOR_3'}
						, $$MapHash{'GRAPH_COLOR_4'}
						, $$MapHash{'GRAPH_COLOR_5'}
						, $$MapHash{'GRAPH_COLOR_6'}
						);

	my @TimeLineArray;
	my @DataSet_1_Array;
	my @DataSet_2_Array;
	my @DataSet_3_Array;
	my @DataSet_4_Array;
	my @DataSet_5_Array;
	my @DataSet_6_Array;

	my $ArrayItemCount = 1;

	for(my $i=0; $i<$ArrayItemCount; $i++)
		{
			push (@TimeLineArray, 0);
			push (@DataSet_1_Array, 0);
			push (@DataSet_2_Array, 0);
			push (@DataSet_3_Array, 0);
			push (@DataSet_4_Array, 0);
			push (@DataSet_5_Array, 0);
			push (@DataSet_6_Array, 0);
		}

	my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($$MapHash{'DBUSER'}, $$MapHash{'DBPWD'}, $$MapHash{'DBNAME'}, "GraphingFunctions");
	#my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin("persian", "citrix", $$MapHash{'DBNAME'}, "GraphingFunctions");
	$status = $MSSQL::DBlib::dbh->dbcmd($$SqlStatement);
	$status = $MSSQL::DBlib::dbh->dbsqlexec();

	##########################
	# result set...
	##########################
	# dbresults() must be called for each result set...
	$status = $MSSQL::DBlib::dbh->dbresults();
	if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
		{
			if($$Debug eq "1")
				{
					print "<!-- SUCCESS: $$SqlStatement returned with dbresults status = ($status). -->\n";
				}
			my %dataref = ("jason" => "baumbach");
			my $dataref = \%dataref;

			my $index = 0;
			# Prevent infinite loop...
			while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
				{

					$TimeLineArray[$index]	= $$dataref{loop_date};

					$DataSet_1_Array[$index] = $$dataref{DataSet_1};
					$DataSet_2_Array[$index] = $$dataref{DataSet_2};
					$DataSet_3_Array[$index] = $$dataref{DataSet_3};
					$DataSet_4_Array[$index] = $$dataref{DataSet_4};
					$DataSet_5_Array[$index] = $$dataref{DataSet_5};
					$DataSet_6_Array[$index] = $$dataref{DataSet_6};

					$index++;

					if($$Debug eq "1")
						{
							while( (my $Key, my $Value) = each(%$dataref) )
							{
								print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
								print "<!-- $Key = ($Value) -->\n";
							}                
						}	

				}
		}# END if($status != FAIL)
	else
		{
			print "ERROR: $SqlStatement Failed for first result set!\n";
			$status = $MSSQL::DBlib::dbh->dbcancel();
		}
		
	my $FileExtension = ".png";
	my $FileName = $$GraphName . $FileExtension;

	#print "File name: $FileName\n";

	my $datavalues = GD::Graph::Data->new([
	[ @TimeLineArray ]
	, [ @DataSet_1_Array]
	, [ @DataSet_2_Array]
	, [ @DataSet_3_Array]
	, [ @DataSet_4_Array]
	, [ @DataSet_5_Array]
	, [ @DataSet_6_Array]
	]);

	# Create our graph object
	my $graph;
	if($$GraphType eq "bars")
		{
			$graph = GD::Graph::bars->new($$Width, $$Height);
		}
	elsif($$GraphType eq "lines")
		{
			$graph = GD::Graph::lines->new($$Width, $$Height);
		}
	elsif($$GraphType eq "linespoints")
		{
			$graph = GD::Graph::linespoints->new($$Width, $$Height);
		}
	#$graph->set_x_axis_font(gdLargFont, 18);

	#my @NewMemberArray_Sorted = sort(@NewMemberArray);

	# Set useful variables such as our axis labels, title, 
	# coloring, etc
	$graph->set(
	title => "$$GraphTitle"
	, x_label => "Date"
	, y_label => "Number"
	#  , y_max_value => pop(@NewMemberArray_Sorted)
	, bar_spacing => $$MapHash{'GRAPH_BAR_SPACING'}
	, x_label_position => 1/2
	, x_labels_vertical => 1
	, shadow_depth => $$MapHash{'GRAPH_SHADOW_DEPTH'}
	, transparent => 1
	, cumulate => $$MapHash{'GRAPH_CUMULATE'}
	, x_long_ticks => $$MapHash{'GRAPH_X_LONG_TICKS'}
	, y_long_ticks => $$MapHash{'GRAPH_Y_LONG_TICKS'}
	, labelclr => $$MapHash{'GRAPH_LABELS_COLOR'}
	, legendclr => $$MapHash{'GRAPH_LEGEND_COLOR'}
	, textclr => $$MapHash{'GRAPH_TEXT_COLOR'}
	, dclrs => \@ColorsArray
	);

	$graph->set_legend(@$LegendArray);

	# Actually plot the data
	$graph->plot($datavalues) or die $graph->error;

	# Output the image as a PNG
	open(OUTPUT, ">$$GraphPath/$FileName") or print "Can't open $FileName: $!\n";
	binmode OUTPUT;
	print OUTPUT $graph->gd->png();
	close(OUTPUT);

	return "$FileName";

	exit 0;
}


sub Create_And_Return_MixedGraph_Location
{
	my $SqlStatement	= shift;
	my $NumberOfColumns	= shift;
	my $GraphTitle		= shift;
	my $LegendArray		= shift;
	my $Width			= shift;
	my $Height			= shift;
	my $GraphPath		= shift;
	my $GraphName		= shift;
	my $Debug			= shift;
	my $MapHash			= shift;

	my $DebugPrintColorHTML	   = "0";
	my $index = 0;

	my @ColorsArray = ($$MapHash{'GRAPH_COLOR_1'}
						, $$MapHash{'GRAPH_COLOR_2'}
						, $$MapHash{'GRAPH_COLOR_3'}
						, $$MapHash{'GRAPH_COLOR_4'}
						, $$MapHash{'GRAPH_COLOR_5'}
						, $$MapHash{'GRAPH_COLOR_6'}
						);

	my @TimeLineArray;
	my @DataSet_1_Array;
	my @DataSet_2_Array;
	my @DataSet_3_Array;
	my @DataSet_4_Array;
	my @DataSet_5_Array;
	my @DataSet_6_Array;

	my $ArrayItemCount = 1;

	for(my $i=0; $i<$ArrayItemCount; $i++)
		{
			push (@TimeLineArray, 0);
			push (@DataSet_1_Array, 0);
			push (@DataSet_2_Array, 0);
			push (@DataSet_3_Array, 0);
			push (@DataSet_4_Array, 0);
			push (@DataSet_5_Array, 0);
			push (@DataSet_6_Array, 0);
		}

	my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin($$MapHash{'DBUSER'}, $$MapHash{'DBPWD'}, $$MapHash{'DBNAME'}, "GraphingFunctions");
	#my $status = $MSSQL::DBlib::dbh = MSSQL::DBlib->dblogin("persian", "citrix", $$MapHash{'DBNAME'}, "GraphingFunctions");
	$status = $MSSQL::DBlib::dbh->dbcmd($$SqlStatement);
	$status = $MSSQL::DBlib::dbh->dbsqlexec();

	##########################
	# result set...
	##########################
	# dbresults() must be called for each result set...
	$status = $MSSQL::DBlib::dbh->dbresults();
	if($status != FAIL && $DatabaseFunctions::DatabaseError ne "1")
		{
			if($$Debug eq "1")
				{
					print "<!-- SUCCESS: $$SqlStatement returned with dbresults status = ($status). -->\n";
				}
			my %dataref = ("jason" => "baumbach");
			my $dataref = \%dataref;

			# Prevent infinite loop...
			while ($MSSQL::DBlib::dbh->dbnextrow2($dataref, 1) != NO_MORE_ROWS) 
				{

					if($$dataref{loop_date})
						{
							$TimeLineArray[$index]	= $$dataref{loop_date};
						}
					else
						{
							$TimeLineArray[$index]	= 0;
						}

					if($$dataref{DataSet_1})
						{
							$DataSet_1_Array[$index] = $$dataref{DataSet_1};
						}
					else
						{
							$DataSet_1_Array[$index] = 0;
						}

					if($$dataref{DataSet_2})
						{
							$DataSet_2_Array[$index] = $$dataref{DataSet_2};
						}
					else
						{
							$DataSet_2_Array[$index] = 0;
						}

					if($$dataref{DataSet_3})
						{
							$DataSet_3_Array[$index] = $$dataref{DataSet_3};
						}
					else
						{
							$DataSet_3_Array[$index] = 0;
						}

					if($$dataref{DataSet_4})
						{
							$DataSet_4_Array[$index] = $$dataref{DataSet_4};
						}
					else
						{
							$DataSet_4_Array[$index] = 0;
						}

					if($$dataref{DataSet_5})
						{
							$DataSet_5_Array[$index] = $$dataref{DataSet_5};
						}
					else
						{
							$DataSet_5_Array[$index] = 0;
						}

					if($$dataref{DataSet_6})
						{
							$DataSet_6_Array[$index] = $$dataref{DataSet_6};
						}
					else
						{
							$DataSet_6_Array[$index] = 0;
						}

					$index++;

					if($$Debug eq "1")
						{
							while( (my $Key, my $Value) = each(%$dataref) )
							{
								print "<FONT color=\"blue\">$Key</FONT> <FONT color=\"red\">$Value</FONT><BR>\n" if $DebugPrintColorHTML eq "1";
								print "<!-- $Key = ($Value) -->\n";
							}                
						}	
				}
		}# END if($status != FAIL)
	else
		{
			print "ERROR: $SqlStatement Failed for first result set!\n";
			$status = $MSSQL::DBlib::dbh->dbcancel();
		}

	if($index == 0)
		{
			print "<!-- No Data -->";
#			return "graph_type_no_data.jpg";
		}	

	my $FileExtension = ".png";
	my $FileName = $$GraphName . $FileExtension;
	my $datavalues;

	if($$NumberOfColumns eq "2")
		{
			$datavalues = GD::Graph::Data->new([
												[ @TimeLineArray ]
												, [ @DataSet_1_Array]
												, [ @DataSet_2_Array]
												]);
		}
	elsif($$NumberOfColumns eq "3")
		{
			$datavalues = GD::Graph::Data->new([
												[ @TimeLineArray ]
												, [ @DataSet_1_Array]
												, [ @DataSet_2_Array]
												, [ @DataSet_3_Array]
												]);
		}
	elsif($$NumberOfColumns eq "4")
		{
			$datavalues = GD::Graph::Data->new([
												[ @TimeLineArray ]
												, [ @DataSet_1_Array]
												, [ @DataSet_2_Array]
												, [ @DataSet_3_Array]
												, [ @DataSet_4_Array]
												]);
		}
	elsif($$NumberOfColumns eq "5")
		{
			$datavalues = GD::Graph::Data->new([
												[ @TimeLineArray ]
												, [ @DataSet_1_Array]
												, [ @DataSet_2_Array]
												, [ @DataSet_3_Array]
												, [ @DataSet_4_Array]
												, [ @DataSet_5_Array]
												]);
		}
	elsif($$NumberOfColumns eq "6")
		{
			$datavalues = GD::Graph::Data->new([
												[ @TimeLineArray ]
												, [ @DataSet_1_Array]
												, [ @DataSet_2_Array]
												, [ @DataSet_3_Array]
												, [ @DataSet_4_Array]
												, [ @DataSet_5_Array]
												, [ @DataSet_6_Array]
												]);
		}
	else
		{
			print "<!--GRAPH ERROR:  Unrecognized NumberOfColumns = ($$NumberOfColumns) -->";
			return "graph_error.jpg";
		}

	# Create our graph object
	my $graph = GD::Graph::mixed->new($$Width, $$Height);
	#$graph->set_x_axis_font(gdLargFont, 18);

	#my @NewMemberArray_Sorted = sort(@NewMemberArray);

	# Set useful variables such as our axis labels, title, 
	# coloring, etc
	$graph->set(
	title => "$$GraphTitle"
	, x_label => "Date"
	, y1_label => "Total Actions"
	, y2_label => "Event"
	, types => [qw(bars lines)]
	#  , y_max_value => pop(@NewMemberArray_Sorted)
	, bar_spacing => $$MapHash{'GRAPH_BAR_SPACING'}
	, x_label_position => 1/2
	, x_labels_vertical => 1
	, shadow_depth => $$MapHash{'GRAPH_SHADOW_DEPTH'}
	, transparent => 1
	, cumulate => $$MapHash{'GRAPH_CUMULATE'}
	, x_long_ticks => $$MapHash{'GRAPH_X_LONG_TICKS'}
	, y_long_ticks => $$MapHash{'GRAPH_Y_LONG_TICKS'}
	, labelclr => $$MapHash{'GRAPH_LABELS_COLOR'}
	, legendclr => $$MapHash{'GRAPH_LEGEND_COLOR'}
	, textclr => $$MapHash{'GRAPH_TEXT_COLOR'}
	, dclrs => \@ColorsArray
	, line_width => 5
	, x_min_value => 0
	, y_min_value => 0
	, zero_axis_only => 0
	);

	$graph->set_legend(@$LegendArray);
#	$graph->set_legend('Total Actions (Left)', 'New Males (Right)');

	# Actually plot the data
	$graph->plot($datavalues) or die $graph->error;

	# Output the image as a PNG
	open(OUTPUT, ">$$GraphPath/$FileName") or print "Can't open $FileName: $!\n";
	binmode OUTPUT;
	print OUTPUT $graph->gd->png();
	close(OUTPUT);

	return "$FileName";

	exit 0;
}



# Scripts that are to be include with other scripts must end with "1;"
1;

#				my $count = 1;
#				my $count_1 = 0;
#				my $count_2 = 0;
#				my $count_3 = 0;
#				my $count_4 = 0;
#				my $count_5 = 0;
#				my $count_6 = 0;
#				my $count_7 = 0;
#				while( (my $Key, my $Value) = each(%$dataref) )
#				{
#					if($count % 7 == 0)
#						{
#							$DataSet_6_Array[$count_7+$index] = $Value;
#							print "<!-- 7 = $count -->" if $$Debug eq "1";
#							$count_7++;
#						}
#					elsif($count % 6 == 0)
#						{
#							$DataSet_5_Array[$count_6+$index] = $Value;
#							print "<!-- 6 = $count -->" if $$Debug eq "1";
#							$count_6++;
#						}
#					elsif($count % 5 == 0)
#						{
#							$DataSet_4_Array[$count_5+$index] = $Value;
#							print "<!-- 5 = $count -->" if $$Debug eq "1";
#							$count_5++;
#						}
#					elsif($count % 4 == 0)
#						{
#							$TimeLineArray[$count_4+$index] = $Value;
#							print "<!-- 4 = $count -->" if $$Debug eq "1";
#							$count_4++;
#						}
#					elsif($count % 3 == 0)
#						{
#							$DataSet_3_Array[$count_3+$index] = $Value;
#							print "<!-- 3 = $count -->" if $$Debug eq "1";
#							$count_3++;
#						}
#					elsif($count % 2 == 0)
#						{
#							$DataSet_2_Array[$count_2+$index] = $Value;
#							print "<!-- 2 = $count -->" if $$Debug eq "1";
#							$count_2++;
#						}
#					elsif($count % 1 eq 0)
#						{
#							$DataSet_1_Array[$count_1+$index] = $Value;
#							print "<!-- 1 = $count -->" if $$Debug eq "1";
#							$count_1++;
#						}
#					print "<!-- $Key = ($Value) -->\n" if $$Debug eq "1";
#					$count++;
#				}        
