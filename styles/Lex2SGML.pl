# Convert lexware file to XML
#
# jbl 9/9/97
#
$doctype = "LEXICON";
($infile,$DTDfile) = @ARGV ;
open(CVT,$infile)  || die "no input file!" ;
open(DTD,">$DTDfile") || die "DTD file!";
print "\n<$doctype>\n";

while (<CVT>) {
	chop ;
	$lines++ ;
	#while (!$_) {$_ = <> ; chop};
        s/</&lt;/g;
        s/>/&gt;/g;
        s/ \[\[/<srcxcr>/ && ($taglist{srcxcr}++ );
        if (s/^(\.+)//) {
		if ($1 eq "\.") 
			{ $n++ ; print "\n<entry n=$n>" ; }
		else {
                        $a = length($1) ;
                        print "\n<sub level=\"$a\">" ;
		}
	}
        if (s/^(\d+)//) {
                if ($currmode eq $1) {}
                else {
                        $currmode = $1 ;
                        print "\n<mode level=\"$1\">" ;
                        }
                }
        if (/^([^ \t]+)[ \t]*(.*)$/) {
		print "\n<$1>$2";
		$taglist{$1}++ ;
		}
	else {
		print "$_" ;
		}
}
print "\n<\/$doctype>\n";
print DTD "<!DOCTYPE $doctype [\n";
#print DTD "<!ENTITY % ISOlat1 PUBLIC \"ISO 8879:1986//ENTITIES Added Latin 1//EN\">\n";
#print DTD "%ISOlat1;\n" ;
print DTD "<!ELEMENT $doctype o o (ENTRY)+>\n";
print DTD "<!ELEMENT ENTRY - o ANY -(ENTRY)>\n";
print DTD "<!ELEMENT SUB   - o ANY -(SUB)>\n";
print DTD "<!ELEMENT MODE  - o ANY -(MODE)>\n";
#print DTD "<!ELEMENT ENTRY - o +(SUB$tlist)>\n";
#print DTD "<!ELEMENT SUB   - o +(SUB$tlist)>\n";
print DTD "<!ATTLIST ENTRY N      CDATA #IMPLIED>\n";
print DTD "<!ATTLIST (SUB|MODE)   LEVEL CDATA #IMPLIED>\n";
foreach $k (sort keys %taglist) {
        print DTD "<!ELEMENT $k - o (#PCDATA)>\n" ;
	}
print DTD "]>\n";
print DTD "\n<!--\n\n*** Tag statistics\n";
foreach $k (sort keys %taglist) {
	$tottags += $taglist{$k} ;
	$tlist = "$tlist&$k" ;
      printf DTD "%s\t%d\n",$k,$taglist{$k} ;
	}
print DTD "\nNo. of Lines: $lines";
print DTD "\nNo. of tags:  $tottags\n";  
print DTD "-->\n" ;


