# Convert lexware file to XML
#
# jbl 9/9/97
#
# usage: perl Lex2XML.pl infile outfile logfile dialect
#
# Lexware conventions handled:
#   .band     starts a new entry; its element gets headword="true"
#   ..band    starts a subentry (<sub>); deeper levels (...) are treated as ..
#   Nband     band in mode (sense) N; consecutive bands with the same N are
#             grouped in <mode level="N">
#   *text     comment
#   lines starting with whitespace continue the preceding band
#
# Within band content:
#   [[ text   (two or more '[') becomes <xcr n="1">text</xcr>, numbered in
#             order of occurrence, and stays inside the band; a single '['
#             is left alone
#   <text>    becomes <tbr>text</tbr>; an unmatched '<' or '>' is left as
#             text and reported on STDERR
#
use strict;
use warnings;

my $doctype = "lexicon";
my ($infile, $outfile, $logfile, $dialect) = @ARGV;
open(CVT, '<', $infile) || die "no input file!";
open(OUT, '>', $outfile) || die "no output file!";
open(LOG, '>', $logfile) || die "log file!";
print OUT '<?xml version="1.0" encoding="utf-8"?>';
print OUT "\n<$doctype dialecte=\"$dialect\">";

my $inmode = 0;
my $insub = 0;
my $lines = 0;
my $n = 0;
my %taglist;
my $currmode = '';
my $hdr = 0;
my $unmatched = 0;

sub escape {
    my ($s) = @_;
    $s =~ s/&/&amp;/g;
    $s =~ s/</&lt;/g;
    $s =~ s/>/&gt;/g;
    return $s;
}

# escape a piece of band text, turning each <...> pair into <tbr>...</tbr>
sub tbr {
    my ($text, $lineno, $tag) = @_;
    my $out = '';
    foreach my $piece (split /(<[^<>]*>)/, $text) {
        if ($piece =~ /^<([^<>]*)>$/) {
            $out .= '<tbr>' . escape($1) . '</tbr>';
            $taglist{'tbr'}++;
        }
        else {
            if ($piece =~ /[<>]/) {
                warn "$infile:$lineno: unmatched '<' or '>' in $tag: $text\n";
                $unmatched++;
            }
            $out .= escape($piece);
        }
    }
    return $out;
}

# render one band as an XML element; the band that starts an entry (a
# single ".") gets headword="true"
sub band {
    my ($tag, $data, $lineno, $headword) = @_;
    $data =~ s/^\s+|\s+$//g;
    return '' if $data eq '';
    my ($field, @xcrs) = split /\s*\[{2,}\s*/, $data, -1;
    my $content = tbr($field, $lineno, $tag);
    my $i = 0;
    foreach my $x (@xcrs) {
        $i++;
        $content .= "<xcr n=\"$i\">" . tbr($x, $lineno, $tag) . "</xcr>";
        $taglist{'xcr'}++;
    }
    my $attr = $headword ? q( headword="true") : q();
    return "\n<$tag$attr>$content</$tag>";
}

sub close_mode {
    if ($inmode == 1) {print OUT "\n</mode>";}
    $inmode = 0;
    $currmode = '';
}

# read the file into logical lines, joining continuation lines (lines
# that start with whitespace) to the band they continue
my @logical;
while (<CVT>) {
    chomp;
    s/\r//g;
    $lines++;
    next if (/^\s*$/);
    if (/^[ \t]/ && @logical && $logical[-1][0] !~ /^\*/) {
        s/^\s+|\s+$//g;
        $logical[-1][0] =~ s/\s+$//;
        $logical[-1][0] .= " $_";
        $taglist{'continuation'}++;
        next;
    }
    push @logical, [$_, $lines];
}

foreach my $l (@logical) {
    my ($line, $lineno) = @$l;
    $_ = $line;

    if (/^\*/) {
        print OUT "\n<comment>" . escape($_) . "</comment>";
        $taglist{'comment'}++;
        next;
    }

    if (s/^(\d+)//) {
        my $mode_level = $1;
        my ($tag, $data) = /^([^ \t]+)[ \t]*(.*)$/;
        if ($currmode ne $mode_level) {
            close_mode();
            $currmode = $mode_level;
            print OUT "\n<mode level=\"$mode_level\">";
            $inmode = 1;
        }
        print OUT band($tag, $data, $lineno);
        $taglist{'mode'}++;
        next;
    }

    my $headword = 0;
    if (s/^(\.+)//) {
        if ($1 eq '.') {
            $headword = 1;
            $n++;
            close_mode();
            if ($insub == 1) {print OUT "\n</sub>";}
            $insub = 0;
            if ($n > 1 && $hdr == 0) {print OUT "\n</entry>"}
            # hack just for tamang dictionary
            if (/^hdr/) {
                s/hdr\s+//;
                print OUT "\n<hdr>" . tbr($_, $lineno, 'hdr') . "</hdr>";
                $hdr = 1;
                next;
            }
            $hdr = 0;
            print OUT "\n<entry id=\"$dialect.$n\">";
            $taglist{'entry'}++;
        }
        else {
            close_mode();
            if ($insub == 1) {print OUT "\n</sub>";}
            print OUT "\n<sub>";
            $taglist{'sub'}++;
            $insub = 1;
        }
    }
    if (/^([^ \t]+)[ \t]*(.*)$/) {
        close_mode();
        print OUT band($1, $2, $lineno, $headword);
        $taglist{$1}++;
    }
}
close_mode();
if ($insub == 1) {print OUT "\n</sub>";}
print OUT "\n</entry>";
print OUT "\n</$doctype>\n";

print LOG "input: $infile\n";
print LOG "dialect: $dialect\n";
print LOG "*** Tag statistics\n";

my $tottags = 0;
foreach my $k (sort keys %taglist) {
    $tottags += $taglist{$k};
    printf LOG "%s\t%d\n", $k, $taglist{$k};
}
print LOG "\nNo. of Lines: $lines";
print LOG "\nNo. of tags:  $tottags\n";
print LOG "Unmatched < or >: $unmatched\n";
