# Convert lexware file to XML
#
# jbl 9/9/97
#
$doctype = "lexicon";
($infile, $outfile, $logfile, $dialect) = @ARGV;
open(CVT, $infile) || die "no input file!";
open(OUT, ">$outfile") || die "no output file!";
open(LOG, ">$logfile") || die "log file!";
print OUT '<?xml version="1.0" encoding="utf-8"?>';
print OUT "\n<$doctype dialecte=\"$dialect\">";

my $inmode = 0;
my $insub = 0;

while (<CVT>) {
    chop;
    $lines++;
    #while (!$_) {$_ = <> ; chop};
    s/</&lt;/g;
    s/>/&gt;/g;

    if (/^\*/) {
        print OUT "\n<comment>$_</comment>";
        $taglist{'comment'}++;
        next;
    }

    # handle [[[... conventions
    $depth = 1;
    while (/\[/) {
        s/\w*\[+([^\[<]+)/<srcxcr$depth>\1<\/srcxcr$depth>/ && ($taglist{srcxcr}++);
        $depth++;
    }
    my $rest = '';
    my $field = '';
    if (/<srcxcr/) {
        # ($field, $rest) = /^(\W*?)\w*(<srcxcr.*)/;
        ($field, $rest) = /^(.*?)\w*(<srcxcr.*)/;
        $_ = $field;
    }
    if (s/^(\d+)//) {
        my $mode_level = $1;
        my ($tag, $data) = /^([^ \t]+)[ \t]*(.*)$/;
        #warn "$tag $data === $_\n";
        if ($currmode eq $mode_level) {
            print OUT "\n<$tag>$data</$tag>";
            $taglist{'mode'}++;
        }
        else {
            $currmode = $mode_level;
            if ($inmode == 1) {print OUT "\n</mode>";}
            print OUT "\n<mode level=\"$mode_level\">";
            $inmode = 1;
            print OUT "\n<$tag>$data</$tag>";
            $taglist{'mode'}++;
        }
        next;
    }
    else {
        if (s/^(\.+)//) {
            if ($1 eq "\.") {
                $n++;
                if ($inmode == 1) {print OUT "\n</mode>";}
                if ($insub == 1) {print OUT "\n</sub>";}
                if ($n > 1) {print OUT "\n</entry>";}
                print OUT "\n<entry id=\"$dialect.$n\">";
                if ($rest ne '') {
                    print OUT "\n$rest";
                    $rest = '';
                }
                $taglist{'entry'}++;
                $inmode = 0;
                $insub = 0;
            }
            else {
                $a = length($1);
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
            print OUT "\n<$1>$2</$1>";
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
foreach $k (sort keys %taglist) {
    $tottags += $taglist{$k};
    $tlist = "$tlist&$k";
    printf LOG "%s\t%d\n", $k, $taglist{$k};
}
print LOG "\nNo. of Lines: $lines";
print LOG "\nNo. of tags:  $tottags\n";


