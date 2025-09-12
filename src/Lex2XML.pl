# Convert lexware file to XML
#
# jbl 9/9/97
#
use strict;

my $doctype = "lexicon";
my ($infile, $outfile, $logfile, $dialect) = @ARGV;
open(CVT, $infile) || die "no input file!";
open(OUT, ">$outfile") || die "no output file!";
open(LOG, ">$logfile") || die "log file!";
print OUT '<?xml version="1.0" encoding="utf-8"?>';
print OUT "\n<$doctype dialecte=\"$dialect\">";

my $inmode = 0;
my $insub = 0;
my $lines = 0;
my $n = 0;
my %taglist;
my $currmode;

sub brackets {
    my ($tag, $data) = @_;
    # handle [[[... conventions
    if ($data =~ /\[/ && $data !~ /\]/) {
        my $depth = 1;
        while ($data =~ /\[/) {
            #print "1 $data\n";
            $data =~ s/\w*\[+([^\[<]+)/<srcxcr$depth>\1<\/srcxcr$depth>/ && ($taglist{'srcxcr'}++);
            $depth++;
        }
        $data =~ s/^\s+|\s+$//g;
        $data =~ s/>\s+/>/g;
        $data =~ s/\s+</</g;
        #print "2 $data\n";
        my ($field, $rest) = $data =~ /^(.*?)(<srcxcr.*)/;
        $field =~ s/^\s+|\s+$//g;
        #print "3 $field = $rest\n";
        return "\n<$tag>$field</$tag>\n$rest";
    }
    else {
        if ($data ne '') {
            return "\n<$tag>$data</$tag>";
        }
    }
}

while (<CVT>) {
    chomp;
    s/\r//g;
    $lines++;
    #while (!$_) {$_ = <> ; chop};
    s/&/&amp;/g;
    s/</&lt;/g;
    s/>/&gt;/g;

    if (/^\*/) {
        print OUT "\n<comment>$_</comment>";
        $taglist{'comment'}++;
        next;
    }

    if (s/^(\d+)//) {
        my $mode_level = $1;
        my ($tag, $data) = /^([^ \t]+)[ \t]*(.*)$/;
        #warn "$tag $data === $_\n";
        if ($currmode eq $mode_level) {
            print OUT brackets($tag, $data);
            $taglist{'mode'}++;
        }
        else {
            $currmode = $mode_level;
            if ($inmode == 1) {print OUT "\n</mode>";}
            print OUT "\n<mode level=\"$mode_level\">";
            $inmode = 1;
            print OUT brackets($tag, $data);
            $taglist{'mode'}++;
        }
        next;
    }
    else {
        if (s/^(\.+)//) {
            if ($1 eq '.') {
                my $currmode;
                $n++;
                if ($inmode == 1) {print OUT "\n</mode>";}
                if ($insub == 1) {print OUT "\n</sub>";}
                if ($n > 1) {print OUT "\n</entry>";}
                print OUT "\n<entry id=\"$dialect.$n\">";
                $taglist{'entry'}++;
                $inmode = 0;
                $insub = 0;
            }
            else {
                my $a = length($1);
                if ($inmode == 1) {print OUT "\n</mode>";}
                $inmode = 0;
                if ($insub == 1) {print OUT "\n</sub>";}
                print OUT "\n<sub level=\"$a\">";
                $taglist{'sub'}++;
                $insub = 1;
            }
        }
        if (/^([^ \t]+)[ \t]*(.*)$/) {
            if ($inmode == 1) {print OUT "\n</mode>";}
            $inmode = 0;
            print OUT brackets($1, $2);
            $taglist{$1}++;
        }
        else {
            print OUT "<extra>$_</extra>";
            $taglist{'extra'}++;
        }
    }
}
print OUT "\n</entry>";
print OUT "\n<\/$doctype>\n";

print LOG "input: $infile\n";
print LOG "dialect: $dialect\n";
print LOG "*** Tag statistics\n";

my $tottags = 0;
foreach my $k (sort keys %taglist) {
    $tottags += $taglist{$k};
    #$tlist = "$tlist&$k";
    printf LOG "%s\t%d\n", $k, $taglist{$k};
}
print LOG "\nNo. of Lines: $lines";
print LOG "\nNo. of tags:  $tottags\n";


