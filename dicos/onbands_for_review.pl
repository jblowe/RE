# SIMPLE version for no subentries or modes -�- OMITS entire article including HEADBAND IF NO MATCH!!!
# BUG REJECT DOES NOT WORK ON HEADBANDS, on other bands it can strand an unmatched subentry
# onbands10.pl 23.07.03
# @onbands is the list of band names that cause an entry to be output
# $onpat can be specified (regular expression or literal string)
# @bands is the list of bands that will be output (headbands and subheadbands of matched entries always are output) 
# if no @bands or @notbands are specified, only headwords are output (not onbands)
# $onpat can be a regular expression or literal string
# $allbands = 1 means all bands are copied to output
# NOTE in output, all sub-hw bands are included whether the subentry contain onbands or not
# BUG: when reject is set, all dot bands are output

@onbands=qw(hw hdr hwdial hwold);	#(get rid of -X, -old)
#define ONE of the following 3 (bands, notbands, allbands) as non-null
#@notbands=qw(compX dfbotX dfeX dffX dfnX encX ilX impX nagX nbiX phrX synX varX dffold dfnold dfeold phrold stedt);
@bands=qw(all anton cf comp cons dfbot dfe dff dfn dfzoo dial emp enc etym gram hist il imp mmnag morph nag nb nbbot niv phon phr pron ps rajdfn rajnag ris syn var voir xr);
#$allbands = "1";
$onpat="";
#$reject= 1;

$line = $bandname = $bandcontent = $band = "";
@buffer = ();
$inputlineno = 0;
if (not @onbands) {die "must specify onbands";}
if (not $onpat) {$onpat = ".*";}
$matchflag = 0;

while (!$EOF) {
	($line = &readline) || ($line = " "); 
	if ($line =~ /^\s*$/) { 
		next;
	}
	chomp $line;
	&bandparse($line);

# if new entry or EOF, print completed entry if ... ; empty buffer
	if (($dots eq ".") || $EOF) {
		if (($matchflag && !$reject) || (!$matchflag && $reject)){
			print "\n";
			for $zork (@buffer) {
				print "$zork\n";
			}

		}
		$matchflag = 0;
		@buffer = ();

	}
	
# if onband, onpat, set matchflag	
	for my $name (@onbands){
		if ($name eq $bandname) {
			if ($bandcontent =~ /$onpat/) {
				$matchflag = 1;
				last;
			}
		}
	}


# if bands, buffer it                              
# if (sub)entry, buffer it
	if ($dots) {
		push @buffer, $line;
	}elsif ($allbands) {
		push @buffer, $line;
	}elsif (@bands) { 
		for $name (@bands){
			if ($name eq $bandname) {
				push @buffer, $line;
				last;
			}
		}
	
	}elsif (@notbands) {
		for $name (@notbands){
			if ($name eq $bandname) {
				$nopush = 1;
				last;
			}
		}
		unless ($nopush) {
			push @buffer, $line;
		}
		$nopush = 0;		

	}
}
#print "$inputlineno lines read";
#print @faultybands;

sub readline {
	my $line = "";
	if (defined ($line = <STDIN>)){$inputlineno++;}else{$EOF = 1;}
	return $line;
}

sub bandparse {
	our $dots = $band = $bandname = $bandcontent = "";
	my $line = shift;
	if ( $line =~ /^(\.*)(\d*)([^\s]+)\s*(([^\s].*$)|$)/ ) {
		$dots = $1;
		$mode = $2;
		$bandname = $3;
		$bandcontent = $4;
		$band = "$dots$bandname\t$bandcontent";
	}else{
		push @faultybands, "$inputlineno\n";
	}
}






