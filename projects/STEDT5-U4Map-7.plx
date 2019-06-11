#!/usr/bin/perl -w
BEGIN { $^W = 1 }
use strict;
use utf8;

binmode(STDOUT, 'utf8');

##############################################
# This  program  converts  Mac STEDTFont 5.1 #
# text files to UTF-8. Run it in a directory #
# of files and convert each file.txt in that #
# directory to file.u8, silently overwriting #
# any pre-existing file.u8 in that directory #
# (you might want to be careful about that). #
##############################################
# The STEDT Project  and  the author make no #
# expressed or implied warranty of any kind, #
# and  assume  no  liability  for  errors or #
# omissions.   No  liability is  assumed for #
# incidental  and  consequential  damages in #
# connection with  or arising out of the use #
# of the information  or  programs contained #
# in or accompanying this file. Caveat Utor! #
##############################################
# Richard Cook  rscook@socrates.berkeley.edu #
# Dominic Yu                                 #
##############################################
# Written with MacPerl 5.6.1r2  (2003-09-09) #
# Updated for  Perl    5.8.1    (2004-09-17) #
# Improvements for diacritics   (2007-08-26) #
##############################################

warn "x"x64,"\n";
warn "Started: ", scalar localtime(), " ...\n";
warn sprintf "Perl %vd\n", $^V;
warn "-"x64,"\n";
warn "Remapping Mac STEDT Font 5.1 text files to Unicode 4.0 ...\n";

##################################
###GET LIST OF FILES TO CONVERT###
#opendir(DIR, ':')
my ($dir) = @ARGV;
opendir(DIR, $dir)
    or die "cannot open : $dir";
my @files = map {"$dir/$_"} readdir(DIR);
closedir(DIR);
die "Died: No files in current directory to convert! (why not add some?)\n"
    unless @files;
my %files;
warn "-"x64,"\n";
my $tif = @files;
warn "The following $tif infiles in the current directory will be converted\n";
warn "to UTF-8 (INFILE => OUTFILE):\n";
warn "-"x64,"\n";
my $n;
for my $infile (@files){
    $n++;
    my $outfile = $infile;
    $outfile .= '.u8';
    $files{$infile}=$outfile;
    warn "$n:  $infile => $outfile\n";
}

############################################
###LOAD THE MAPS FROM THE DATA LIST BELOW###
warn "-"x64,"\n";
warn "Building the maps ...\n";

my (%char, %diac, %skip, %hash, %all, $linecount, $seq);
while (<DATA>){
    next if /^#|^$/;
    $linecount++;
    chomp;
    my @t = split(/\t/,$_,-1);
    @t == 5
        or die "Died! corrupt STED2U-map, line: $.\n";

    $seq = $t[0]
        unless defined $seq;
    $t[0] == $seq
        or die "Died! $t[0] == $seq ??\n";

    $t[1] = chr hex $t[1];

    chr $t[0] eq $t[1]
        or die "Died! $t[0] eq $t[1] ??\n";

    exists $all{$t[1]}
        or
    exists $hash{$t[1]}
        or
    exists $char{$t[1]}
        or
    exists $diac{$t[1]}
        and die "Non-unique keys! $_\n";

	$all{$t[1]}=$t[2];

    if($t[4] == 0){# these base chars *don't* remap
        $skip{$t[1]}=$t[2];
    }
    elsif($t[4] == 1){# diacritics
        $diac{$t[1]}=$t[2];
        $hash{$t[1]}=$t[2];
    }
    elsif($t[4] == 2){# these base chars *do* remap
        $char{$t[1]}=$t[2];
        $hash{$t[1]}=$t[2];
    }
    else{
        die "bad `Combining' value $t[4]: $_\n";
    }
    $seq++;
}
my $all = scalar keys %all;

warn "STEDTFont 5.1 Unicode 4.0 Scalar Values all loaded.\n";
warn "Total of $all characters in the comprehensive Map.\n";

###############
###MAP STATS###
warn "-"x64,"\n";
warn "Verifying map counts ...\n\n";

my %warn = (
    Char => scalar keys %char,
    Diac => scalar keys %diac,
    Skip => scalar keys %skip,
    Hash => scalar keys %hash,
);

my $z;
for my $w (sort keys %warn){
    my $warn = sprintf "Total of %03d Keys in the %s hash", $warn{$w}, $w;
    $warn = $warn . " (sum of above, these all get remapped)" 
        if $w eq "Hash";
    $warn = $warn . " (these don't get remapped)" 
        if $w eq "Skip";
    warn "$warn.\n";
    $z += $warn{$w} 
        unless $w eq "Hash";
}

if($linecount == $z && $linecount == $all){
    warn "Total of $linecount Map DATA lines is all of Char, Diac, & Skip.\n\n";
}
else{
    die "ebod?! linecount=>$linecount,  z=>$z, all=>$all\n";
}

my $c = join("", sort keys %char);
my $d = join("", sort keys %diac);
my $s = join("", sort keys %skip);
my $h = join("", sort keys %hash);

my $cx = join("", map {sprintf "0x%X ", ord $_} sort keys %char);
my $dx = join("", map {sprintf "0x%X ", ord $_} sort keys %diac);
my $hx = join("", map {sprintf "0x%X ", ord $_} sort keys %hash);

warn "STEDTFont 5.1 characters to remap:\n\n";
warn "    Total of $warn{Char} base characters:\n[$cx].\n\n";
warn "    Total of $warn{Diac} prestruck diacritics:\n[$dx].\n\n";
warn "    Total of $warn{Hash} characters (base+diacritic) get remapped:\n[$hx].\n\n";
warn "STEDTFont 5.1 base characters unchanged:\n\n";
warn "    Total of $warn{Skip} chars in STEDTFont skipclass:\n[$s].\n\n";

warn "All map counts verified.\n";

#########################
###MAKE THE CONVERSION###
warn "-"x64,"\n";
warn "Beginning file conversion to UTF-8 ...\n\n";

# Some 7-bit control characters < 0x20 <SPACE> should probably
# not be in a Mac STEDTFont text file, and might be stripped 
# if they occur, except for 0x09 <TAB>, 0x0A <LF>, 0x0D <CR>.
# Some applications might export other 7-bit controls in  
# plain text to preserve certain info, e.g. FileMaker uses 
# 0x0B <VT> for line breaks within a cell. Also, (the one
# control > 0x20 <SPACE>) 0x7F <DELETE> is unused in STEDTFont.
# We leave these controls in the data if they occur, but warn you
# in case they are evidence of some problem with the infile.

my $ctrl = '[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]';

# high diacritics from STEDTFont, must be ordered last in utf8

my $hd = '[\x9f\xff\xfc\xce\xe1\xab\xcf]';

for my $f (sort keys %files){

    next if -d $f;

    open IF, "< $f" 
        or die "cannot open `$f': $!";
    warn "Reading text file `$f' ...\n";
    open OF, "> $files{$f}" 
        or die "cannot create `$files{$f}': $!";
    warn "Writing text file `$files{$f}' ...\n";

    binmode(OF, 'utf8');

    my %frq; my $warned=0;
    while (<IF>){

        if (/$ctrl/ && $warned < 1){
            warn "Check for improper controls in file `$f':\n $_";
            $warned++;
        }
        # mark controls (see above)
        #$_ =~ s/($ctrl)/"{".sprintf("%0#4X",ord $1)."}"/ego;

        for my $c (split(//,$_)){
            next if $c =~ /^$|\t|\n/;
            $frq{$c}++;
        }

	# handle legacy lexware accented characters
	#s/\\'(.)/\1\x{0300}/g; # accent acute
	#s/\\`(.)/\1\x{0301}/g; # accent grave
	#s/\\^(.)/\1\x{0302}/g; # circonflex

        #my @t = split(/\t/,$_,-1);
        # if your infile is tab-separated with mixed encodings
        # then you'll want to specify the field to convert ...

		# remove all duplicate diacritics (typos)
		1 while (s/([\Q$d\E])\1/$1/go);
		
		# high diacs must be ordered after
		s/([\Q$d\E]+)/join '', sort diacritically split('', $1)/goe
			if (/$hd/o);
	
        # interpose a space between diac and line-end or tab
        $_ =~ s/([\Q$d\E])(\t|$)/$1 $2/go;

        # then, any post-diac non-diac is base; reorder them
        $_ =~ s/([\Q$d\E]+)([^\Q$d\E])/$2$1/go;

        # remap to USV('s) to UTF-8
        $_ =~ s/([\Q$h\E])/ul($hash{$1})/ego;

        # note that 0x84 and 0x96 both have 1-to-2 mappings which
        # could be handled with 0x84 => U+0221, 0x96 => U+0236 instead ...

		# now fix diacritic issues
		# 1. dotless i is no longer needed for diacritics
		#    fixing this will help with character appearance
		#    and possibly searching/sorting text
		# 2. diacritics after spaces should be converted
		#    to the corresponding non-combining forms,
		#    again to solve display issues
		#    (we don't do diaereses and tilde, but their use
		#     with spaces seems rare enough to be safe ignoring)
		s/ı(̱)?([̄́̃̀̈̌̂̆])/i$1$2/g; # dotless i + diacritics
		s/ ̄/ˉ/g; # macron, modifier letter
		s/ ́/ˊ/g; # acute
		s/ ̀/ˋ/g; # grave
		s/ ̌/ˇ/g; # caron
		s/ ̂/ˆ/g; # circumflex
		s/ ̱/ˍ/g; # low macron, modifier letter

        # get rid of ctrl-z
        s/\cZ//g;

        print OF;

    }
    warn "line count for `$f': $. .\n";

    close IF 
        or die "trouble closing `$f': $!";
    close OF 
        or die "trouble closing `$files{$f}': $!";

    warn "Finished converting `$f'.\n\n";

    my $types = scalar keys %frq;
    warn "Frequencies for $types character types occurring in `$f':\n";
    for my $f (sort {$frq{$b} <=> $frq{$a} 
                               or
                           $a cmp $b} keys %frq){
		next if $f =~ /^$/;
        my $g = $f;
        $g = "" if $g =~ /$ctrl/o;
		$g = $all{$f} if exists $all{$f};
        printf "%#X\t% 6d\t=> %s\n", ord $f, $frq{$f}, $g;
    }
    warn "-"x64,"\n";
}
my $pl = $tif == 1 ? "" : "s";
my $ar = "no";
$ar = "the" if $tif > 0;
$ar = "all" if $tif > 2;
my $time = time() - $^T;
my $sex = $time  == 1 ? "" : "s"; 
warn "Finished converting $ar $tif file$pl in a total of $time second$sex.\n";

#################
###SUBROUTINES###

##################################
############# SUB UL #############
##################################
###### convert USV to chars ######
###### see column 2 of DATA ######
##################################

sub ul {
    join '', map {chr hex} ($_[0] =~ /\[U\+([0-9A-Fa-f]{1,6})\]/g);
}

# a sorting routine for diacritics
# orders high diacs after regular diacs

sub diacritically {
	$a =~ /$hd/o <=> $b =~ /$hd/o
}


#####################################
#MAPPING DATA STEDTFONT5 <=> UNICODE4

__DATA__
#DEC	HEX	USV	UNAME	COMB
032	20	[U+0020]	SPACE	0
033	21	[U+0021]	EXCLAMATION MARK	0
034	22	[U+0022]	QUOTATION MARK	0
035	23	[U+0023]	NUMBER SIGN	0
036	24	[U+1D4A]	MODIFIER LETTER SMALL SCHWA	2
037	25	[U+0279]	LATIN SMALL LETTER TURNED R	2
038	26	[U+2AA4]	GREATER-THAN OVERLAPPING LESS-THAN	2
039	27	[U+0027]	APOSTROPHE	0
040	28	[U+0028]	LEFT PARENTHESIS	0
041	29	[U+0029]	RIGHT PARENTHESIS	0
042	2A	[U+002A]	ASTERISK	0
043	2B	[U+002B]	PLUS SIGN	0
044	2C	[U+002C]	COMMA	0
045	2D	[U+002D]	HYPHEN-MINUS	0
046	2E	[U+002E]	FULL STOP	0
047	2F	[U+002F]	SOLIDUS	0
048	30	[U+0030]	DIGIT ZERO	0
049	31	[U+0031]	DIGIT ONE	0
050	32	[U+0032]	DIGIT TWO	0
051	33	[U+0033]	DIGIT THREE	0
052	34	[U+0034]	DIGIT FOUR	0
053	35	[U+0035]	DIGIT FIVE	0
054	36	[U+0036]	DIGIT SIX	0
055	37	[U+0037]	DIGIT SEVEN	0
056	38	[U+0038]	DIGIT EIGHT	0
057	39	[U+0039]	DIGIT NINE	0
058	3A	[U+003A]	COLON	0
059	3B	[U+003B]	SEMICOLON	0
060	3C	[U+003C]	LESS-THAN SIGN	0
061	3D	[U+003D]	EQUALS SIGN	0
062	3E	[U+003E]	GREATER-THAN SIGN	0
063	3F	[U+003F]	QUESTION MARK	0
064	40	[U+032A]	COMBINING BRIDGE BELOW	1
065	41	[U+0041]	LATIN CAPITAL LETTER A	0
066	42	[U+0042]	LATIN CAPITAL LETTER B	0
067	43	[U+0043]	LATIN CAPITAL LETTER C	0
068	44	[U+0044]	LATIN CAPITAL LETTER D	0
069	45	[U+0045]	LATIN CAPITAL LETTER E	0
070	46	[U+0046]	LATIN CAPITAL LETTER F	0
071	47	[U+0047]	LATIN CAPITAL LETTER G	0
072	48	[U+0048]	LATIN CAPITAL LETTER H	0
073	49	[U+0049]	LATIN CAPITAL LETTER I	0
074	4A	[U+004A]	LATIN CAPITAL LETTER J	0
075	4B	[U+004B]	LATIN CAPITAL LETTER K	0
076	4C	[U+004C]	LATIN CAPITAL LETTER L	0
077	4D	[U+004D]	LATIN CAPITAL LETTER M	0
078	4E	[U+004E]	LATIN CAPITAL LETTER N	0
079	4F	[U+004F]	LATIN CAPITAL LETTER O	0
080	50	[U+0050]	LATIN CAPITAL LETTER P	0
081	51	[U+0051]	LATIN CAPITAL LETTER Q	0
082	52	[U+0052]	LATIN CAPITAL LETTER R	0
083	53	[U+0053]	LATIN CAPITAL LETTER S	0
084	54	[U+0054]	LATIN CAPITAL LETTER T	0
085	55	[U+0055]	LATIN CAPITAL LETTER U	0
086	56	[U+0056]	LATIN CAPITAL LETTER V	0
087	57	[U+0057]	LATIN CAPITAL LETTER W	0
088	58	[U+0058]	LATIN CAPITAL LETTER X	0
089	59	[U+0059]	LATIN CAPITAL LETTER Y	0
090	5A	[U+005A]	LATIN CAPITAL LETTER Z	0
091	5B	[U+005B]	LEFT SQUARE BRACKET	0
092	5C	[U+0300]	COMBINING GRAVE ACCENT	1
093	5D	[U+005D]	RIGHT SQUARE BRACKET	0
094	5E	[U+027E]	LATIN SMALL LETTER R WITH FISHHOOK	2
095	5F	[U+0331]	COMBINING MACRON BELOW	1
096	60	[U+00D0]	LATIN CAPITAL LETTER ETH	2
097	61	[U+0061]	LATIN SMALL LETTER A	0
098	62	[U+0062]	LATIN SMALL LETTER B	0
099	63	[U+0063]	LATIN SMALL LETTER C	0
100	64	[U+0064]	LATIN SMALL LETTER D	0
101	65	[U+0065]	LATIN SMALL LETTER E	0
102	66	[U+0066]	LATIN SMALL LETTER F	0
103	67	[U+0067]	LATIN SMALL LETTER G	0
104	68	[U+0068]	LATIN SMALL LETTER H	0
105	69	[U+0069]	LATIN SMALL LETTER I	0
106	6A	[U+006A]	LATIN SMALL LETTER J	0
107	6B	[U+006B]	LATIN SMALL LETTER K	0
108	6C	[U+006C]	LATIN SMALL LETTER L	0
109	6D	[U+006D]	LATIN SMALL LETTER M	0
110	6E	[U+006E]	LATIN SMALL LETTER N	0
111	6F	[U+006F]	LATIN SMALL LETTER O	0
112	70	[U+0070]	LATIN SMALL LETTER P	0
113	71	[U+0071]	LATIN SMALL LETTER Q	0
114	72	[U+0072]	LATIN SMALL LETTER R	0
115	73	[U+0073]	LATIN SMALL LETTER S	0
116	74	[U+0074]	LATIN SMALL LETTER T	0
117	75	[U+0075]	LATIN SMALL LETTER U	0
118	76	[U+0076]	LATIN SMALL LETTER V	0
119	77	[U+0077]	LATIN SMALL LETTER W	0
120	78	[U+0078]	LATIN SMALL LETTER X	0
121	79	[U+0079]	LATIN SMALL LETTER Y	0
122	7A	[U+007A]	LATIN SMALL LETTER Z	0
123	7B	[U+007B]	LEFT CURLY BRACKET	0
124	7C	[U+0301]	COMBINING ACUTE ACCENT	1
125	7D	[U+007D]	RIGHT CURLY BRACKET	0
126	7E	[U+0303]	COMBINING TILDE	1
127	7F	[U+007F]	DELETE	0
128	80	[U+00BB]	RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK	2
129	81	[U+0252]	LATIN SMALL LETTER TURNED ALPHA	2
130	82	[U+025F]	LATIN SMALL LETTER DOTLESS J WITH STROKE	2
131	83	[U+0307]	COMBINING DOT ABOVE	1
132	84	[U+0064][U+0311]	<LATIN SMALL LETTER D, COMBINING INVERTED BREVE>	2
133	85	[U+02B7]	MODIFIER LETTER SMALL W	2
134	86	[U+0335]	COMBINING SHORT STROKE OVERLAY	1
135	87	[U+00E6]	LATIN SMALL LETTER AE	2
136	88	[U+02C7]	CARON	2
137	89	[U+02C6]	MODIFIER LETTER CIRCUMFLEX ACCENT	2
138	8A	[U+00AB]	LEFT-POINTING DOUBLE ANGLE QUOTATION MARK	2
139	8B	[U+033E]	COMBINING VERTICAL TILDE	1
140	8C	[U+0251]	LATIN SMALL LETTER ALPHA	2
141	8D	[U+00E7]	LATIN SMALL LETTER C WITH CEDILLA	2
142	8E	[U+0323]	COMBINING DOT BELOW	1
143	8F	[U+1D07]	LATIN LETTER SMALL CAPITAL E	2
144	90	[U+24D2]	CIRCLED LATIN SMALL LETTER C	2
145	91	[U+0250]	LATIN SMALL LETTER TURNED A	2
146	92	[U+031B]	COMBINING HORN	1
147	93	[U+1D2E]	MODIFIER LETTER CAPITAL B	2
148	94	[U+0131]	LATIN SMALL LETTER DOTLESS I	2
149	95	[U+0268]	LATIN SMALL LETTER I WITH STROKE	2
150	96	[U+0074][U+0311]	<LATIN SMALL LETTER T, COMBINING INVERTED BREVE>	2
151	97	[U+0153]	LATIN SMALL LIGATURE OE	2
152	98	[U+0275]	LATIN SMALL LETTER BARRED O	2
153	99	[U+00B7]	MIDDLE DOT	2
154	9A	[U+00F8]	LATIN SMALL LETTER O WITH STROKE	2
155	9B	[U+00D8]	LATIN CAPITAL LETTER O WITH STROKE	2
156	9C	[U+24B8]	CIRCLED LATIN CAPITAL LETTER C	2
157	9D	[U+1D2C]	MODIFIER LETTER CAPITAL A	2
158	9E	[U+24C8]	CIRCLED LATIN CAPITAL LETTER S	2
159	9F	[U+0303]	COMBINING TILDE	1
160	A0	[U+0236]	LATIN SMALL LETTER T WITH CURL	2
161	A1	[U+02F0]	MODIFIER LETTER LOW UP ARROWHEAD	2
162	A2	[U+2074]	SUPERSCRIPT FOUR	2
163	A3	[U+00B3]	SUPERSCRIPT THREE	2
164	A4	[U+2076]	SUPERSCRIPT SIX	2
165	A5	[U+2078]	SUPERSCRIPT EIGHT	2
166	A6	[U+2077]	SUPERSCRIPT SEVEN	2
167	A7	[U+0329]	COMBINING VERTICAL LINE BELOW	1
168	A8	[U+0282]	LATIN SMALL LETTER S WITH HOOK	2
169	A9	[U+0263]	LATIN SMALL LETTER GAMMA	2
170	AA	[U+00B2]	SUPERSCRIPT TWO	2
171	AB	[U+0309]	COMBINING HOOK ABOVE	1
172	AC	[U+02EF]	MODIFIER LETTER LOW DOWN ARROWHEAD	2
173	AD	[U+25E6]	WHITE BULLET	2
174	AE	[U+02BB]	MODIFIER LETTER TURNED COMMA	2
175	AF	[U+028C]	LATIN SMALL LETTER TURNED V	2
176	B0	[U+2075]	SUPERSCRIPT FIVE	2
177	B1	[U+007E]	TILDE	2
178	B2	[U+0235]	LATIN SMALL LETTER N WITH CURL	2
179	B3	[U+014B]	LATIN SMALL LETTER ENG	2
180	B4	[U+0285]	LATIN SMALL LETTER SQUAT REVERSED ESH	2
181	B5	[U+0271]	LATIN SMALL LETTER M WITH HOOK	2
182	B6	[U+0221]	LATIN SMALL LETTER D WITH CURL	2
183	B7	[U+026F]	LATIN SMALL LETTER TURNED M	2
184	B8	[U+03B2]	GREEK SMALL LETTER BETA	2
185	B9	[U+0278]	LATIN SMALL LETTER PHI	2
186	BA	[U+0253]	LATIN SMALL LETTER B WITH HOOK	2
187	BB	[U+2079]	SUPERSCRIPT NINE	2
188	BC	[U+2070]	SUPERSCRIPT ZERO	2
189	BD	[U+027F]	LATIN SMALL LETTER REVERSED R WITH FISHHOOK	2
190	BE	[U+02B0]	MODIFIER LETTER SMALL H	2
191	BF	[U+0254]	LATIN SMALL LETTER OPEN O	2
192	C0	[U+0266]	LATIN SMALL LETTER H WITH HOOK	2
193	C1	[U+00B9]	SUPERSCRIPT ONE	2
194	C2	[U+026C]	LATIN SMALL LETTER L WITH BELT	2
195	C3	[U+24C1]	CIRCLED LATIN CAPITAL LETTER L	2
196	C4	[U+03B8]	GREEK SMALL LETTER THETA	2
197	C5	[U+03C7]	GREEK SMALL LETTER CHI	2
198	C6	[U+0283]	LATIN SMALL LETTER ESH	2
199	C7	[U+030C]	COMBINING CARON	1
200	C8	[U+0302]	COMBINING CIRCUMFLEX ACCENT	1
201	C9	[U+221A]	SQUARE ROOT	2
202	CA	[U+00A0]	NO-BREAK SPACE	2
203	CB	[U+1D00]	LATIN LETTER SMALL CAPITAL A	2
204	CC	[U+026E]	LATIN SMALL LETTER LEZH	2
205	CD	[U+007C]	VERTICAL LINE	2
206	CE	[U+0300]	COMBINING GRAVE ACCENT	1
207	CF	[U+0309]	COMBINING HOOK ABOVE	1
208	D0	[U+0328]	COMBINING OGONEK	1
209	D1	[U+0304]	COMBINING MACRON	1
210	D2	[U+032F]	COMBINING INVERTED BREVE BELOW	1
211	D3	[U+0306]	COMBINING BREVE	1
212	D4	[U+0325]	COMBINING RING BELOW	1
213	D5	[U+030A]	COMBINING RING ABOVE	1
214	D6	[U+0294]	LATIN LETTER GLOTTAL STOP	2
215	D7	[U+24CB]	CIRCLED LATIN CAPITAL LETTER V	2
216	D8	[U+028F]	LATIN LETTER SMALL CAPITAL Y	2
217	D9	[U+0308]	COMBINING DIAERESIS	1
218	DA	[U+02B1]	MODIFIER LETTER SMALL H WITH HOOK	2
219	DB	[U+0346]	COMBINING BRIDGE ABOVE	1
220	DC	[U+027D]	LATIN SMALL LETTER R WITH TAIL	2
221	DD	[U+025A]	LATIN SMALL LETTER SCHWA WITH HOOK	2
222	DE	[U+02B4]	MODIFIER LETTER SMALL TURNED R	2
223	DF	[U+02BC]	MODIFIER LETTER APOSTROPHE	2
224	E0	[U+0280]	LATIN LETTER SMALL CAPITAL R	2
225	E1	[U+0301]	COMBINING ACUTE ACCENT	1
226	E2	[U+0234]	LATIN SMALL LETTER L WITH CURL	2
227	E3	[U+028B]	LATIN SMALL LETTER V WITH HOOK	2
228	E4	[U+025B]	LATIN SMALL LETTER OPEN E	2
229	E5	[U+0290]	LATIN SMALL LETTER Z WITH RETROFLEX HOOK	2
230	E6	[U+0288]	LATIN SMALL LETTER T WITH RETROFLEX HOOK	2
231	E7	[U+0309]	COMBINING HOOK ABOVE	1
232	E8	[U+1D1C]	LATIN LETTER SMALL CAPITAL U	2
233	E9	[U+026A]	LATIN LETTER SMALL CAPITAL I	2
234	EA	[U+02CC]	MODIFIER LETTER LOW VERTICAL LINE	2
235	EB	[U+0256]	LATIN SMALL LETTER D WITH TAIL	2
236	EC	[U+00F0]	LATIN SMALL LETTER ETH	2
237	ED	[U+0264]	LATIN SMALL LETTER RAMS HORN	2
238	EE	[U+1D34]	MODIFIER LETTER CAPITAL H	2
239	EF	[U+0292]	LATIN SMALL LETTER EZH	2
240	F0	[U+0291]	LATIN SMALL LETTER Z WITH CURL	2
241	F1	[U+1D38]	MODIFIER LETTER CAPITAL L	2
242	F2	[U+02D0]	MODIFIER LETTER TRIANGULAR COLON	2
243	F3	[U+0265]	LATIN SMALL LETTER TURNED H	2
244	F4	[U+0281]	LATIN LETTER SMALL CAPITAL INVERTED R	2
245	F5	[U+0111]	LATIN SMALL LETTER D WITH STROKE	2
246	F6	[U+0274]	LATIN LETTER SMALL CAPITAL N	2
247	F7	[U+1D39]	MODIFIER LETTER CAPITAL M	2
248	F8	[U+0272]	LATIN SMALL LETTER N WITH LEFT HOOK	2
249	F9	[U+0273]	LATIN SMALL LETTER N WITH RETROFLEX HOOK	2
250	FA	[U+0259]	LATIN SMALL LETTER SCHWA	2
251	FB	[U+0255]	LATIN SMALL LETTER C WITH CURL	2
252	FC	[U+0300]	COMBINING GRAVE ACCENT	1
253	FD	[U+21AD]	LEFT RIGHT WAVE ARROW	2
254	FE	[U+21AE]	LEFT RIGHT ARROW WITH STROKE	2
255	FF	[U+0301]	COMBINING ACUTE ACCENT	1
#END
