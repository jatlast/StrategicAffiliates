#!/usr/local/bin/perl -w
use strict;

my $key;

print "Content-type: text/html\n\n";
print "<HTML>\n";
print "<BODY>\n";
print "<tt>\n";

foreach $key (sort keys(%ENV))
{
	print "<FONT color=red>$key</FONT> = $ENV{$key}<p>";
}

print "</tt>\n";
print "</BODY>\n";
print "</HTML>\n";