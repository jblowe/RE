# RE.pl
# mise a jour jacobson 15/02/2001

use Text::Abbrev;

# Subroutines for RE
###############################################################################
# Gobals Variables	Description				Setup in		Used in
# ================	===================================	==============		============
# %settings		parameters from the param file		LoadParam
# @rls			rules from the correspondances file	LoadTableOfCorr
# %wds			hash of wordforms for a lg		LoadLexicon		CreateRcns
# @lgnames		names of the languages			LoadTableOfCorr
###############################################################################

########################################################################
# @rules        text array contains RULES element   ParseRules 				(obsolete)
# %classes      hash of macro classes of elements   ParseRules
# %lgrules      rules for a specific language       SetupRules
# %recons       hash of reconstructions             CreateRcns/Sets
# @setlist      list of "pseudo" sets               CreateSets
# %stats        hash of statistics                  Statistics
########################################################################

sub GetCmdLine {
    &getopt("iotln") ;
    $test      = +$opt_t ;
    $limit     = +$opt_n ; #number of forms to process in each lex
    $REinfile  = $opt_i;
    $REoutfile = $opt_o;
    $fmt       = $opt_f;   # format of output : null = XML, h = HTML
    open(REFILE,"<$REinfile") || die "can't open RE file '$REinfile'!";
    if ($REoutfile) {
	open(OUTFILE,">$REoutfile") 
	    || die "can't open RE output file '$REoutfile'!";
    }
    $logopen = 0 ;
    OpenLog($opt_l) ;
    #$_ = <REFILE> ;     # read first line and see if file looks OK...
    #m/^\(RE/ || die 
	#"$REinfile : not an RE SGML instance in ESIS format!";
    #%settings ;    # neat and tidy hash to hold various goodies
    $settings{"Input file"}  = $REinfile ;
    $settings{"Output file"} = $REoutfile ;
}
sub OpenLog {           #do our own logging (sys independent that way)
    ($RElogfile) = @_ ; #NB: don't need a CloseLog for multiple logs...
    if ($RElogfile) {
	open(LOGFILE,">$RElogfile") 
	    || die "can't open RE log file '$RElogfile'!";
	binmode LOGFILE, ":utf8";
        $logopen = 1 ;
        $settings{"Log file"} = $RElogfile ;
    }
}

sub LoadCSV {
  my ($fn) = @_ ;
  %lex   = ();
  $dlm = "\t";
  
  open(LEXICON,"<$fn") || die "could not open $fn";
  binmode LEXICON, ":utf8";
  my @lexicon = <LEXICON>;

  @lexicon = grep { s/[\r\n]+//g } @lexicon;

  #print scalar @lexicon;

  $rows = 0;
  $forms = 0;
  
  foreach $l (@lexicon) {
    next if $l =~ /^#/; # skip comments;
    next if $l =~/^S/;  # skip blank lines;
    $rows++;
    if ($rows eq 1) { #  first line (header)
      @lexheader = split($dlm,$l) ;
      %colhash  =  map {$_, $i++} @lexheader ;

      test($fmt,5,"\nData Matrix column headers\n");
      foreach $c (sort keys %colhash) {
	test($fmt,5,$colhash{$c}. ' = ' . $c . "\n");
      }
      next;
    }
    $forms++;
    #print $l,"\n";
    @entry = split($dlm,$l) ;
    
    my ($wd,$gls,$id);			# default values for tags
    $id = $colhash{'id'} ? $entry[$colhash{'id'}] : 0;
    if (!$id) { $id = $mkid++;}
    $gls = $entry[$colhash{'gloss'}];
    $itemid = 0;
    for $lgabbr (@lgnames) {
      $itemid++;
      $wd = $entry[$colhash{$lgabbr}];
      test($fmt,7,$colhash{$lgabbr}-1 . ". ($id.$itemid) " . $lgabbr . ': ' . $wd . " '$gls'\n");
      push @{ $lex{$lgabbr}{$wd}  }, "$id.$itemid" ;
      $arts{"$id.$itemid"} = [ $lgabbr,$wd,$gls ]; # to do: chercher les doublons !
      #print "arts{ $id.$itemid } = [ $lgabbr,$wd,$gls ]\n";
    }
    #print sprintf "%s %s %s %s\n",$lgabbr,$wd,$gls,$id;
  }
  Statistics(qw(INPUT)) ;
  
  return 1 ;
}
# QUESTIONS: a quoi sert $arts
# $arts ==> article [lgabbr, forme, glose] pour rechercher les doublons
sub LoadLexicon {
  my ($fn) = @_ ;
  %wds   = ();			# hash of wordforms to process
  $forms = 0;
  
  my $parser = new XML::DOM::Parser;
  my $doc = $parser->parsefile($fn);
  my $root = $doc->getDocumentElement;
  for $lexicon ($doc->getElementsByTagName ("lexicon")) {
    #$lgabbr = $lexicon->getAttribute("dialecte");
    for $entry ($lexicon->getElementsByTagName ("entry")) {
      $forms++;
      my ($wd,$gls,$id);			# default values for tags
      # $id = $entry->getAttribute("id");
      $id = $entry->getAttribute("N");
      for $elt ($entry->getElementsByTagName ("*")) {
	my $tagname = $elt->getNodeName;
	my $value = getAllData($elt);
	if ($tagname =~ /hw/i) {
	  $wd = $value;
	} elsif ($tagname =~ /(gl|dfe)/i) {
	  $gls = $value;
	} elsif ($tagname =~ /id/i) {
	  $id = $value;
	}
      }
      if (!$id) { $id = $mkid++;}
      push @{ $wds{$wd}  }, $id ;
      $arts{$id} = [ $lgabbr,$wd,$gls ]; # to do: chercher les doublons !
      #print sprintf "%s %s %s %s\n",$lgabbr,$wd,$gls,$id;
    }
    #Statistics(qw(INPUT)) ;
  }
  $doc->dispose;
  return 1 ;
}

# Je n'ai pas compris comment marche $syllcanon (semble etre une variable globale)
sub LoadParam {
  my ($fn) = @_ ;
  %settings = ();
  
  my $parser = new XML::DOM::Parser;
  my $doc = $parser->parsefile($fn);
  my $root = $doc->getDocumentElement;
  for $elt ($doc->getElementsByTagName("action")) {
    my $name = $elt->getAttribute("name");
    if ($name =~ /upstream/i) {
      my $from = $elt->getAttribute("from");
      my $to = $elt->getAttribute("to");
      my $file = $elt->getAttribute("file");
      push @languages,[$from,$file];
      #print "from",$from;
      #print "\n",join ",",@languages;
    }
  }
  for $elt ($doc->getElementsByTagName("param")) {
    my $name = $elt->getAttribute("name");
    $settings{$name} = $elt->getAttribute("value");
  }

  $syllcanon  =  "^(C*V+C*)+\$" ;  #default syllable canon
  $settings{SYLLABLE} && ($syllcanon = "^".$settings{SYLLABLE}."\$") ;
  $settings{"Reconstructions"} = 0 ;
  $settings{"Forms Processed"} = 0 ;
  $settings{"Isolates"}        = 0 ;
  $settings{"No Recons"}       = 0 ;
  $settings{"Languages"}       = \@languages;
  test($fmt,1,"PRE  : [] " . $settings{"TITLE"}. "\n");
}

sub CreateRcns {
  my ($lgabbr,%wds) = @_;
  
  test($fmt,3,"RCN  : [] Reconstructing forms for lexicon: $lgabbr\n" );
  $wrds = 0 ;                # forms processed
  $rcns = 0 ;                # reconstructions generated
  $fail = 0 ;                # forms which fail to reconstruction
  
  for (sort keys %wds) {
    if (($limit && $wrds < $limit) || (!$limit))  {
      s/^[-\s]+//; # get rid of whitespace and hyphens
      s/[,-= ].*//; # only take first syll or so
      s/[\(\)]//g; # get rid of parens
      if ($_ ne '') {
	$wrds++;
	$idno++;
	GenerateRcns($_,$idno,$lgabbr,[ @{$wds{$_}} ]); #gen. forms & add to list
      }
    }
  }
  Accumulate("Forms processed",$wrds);
  Accumulate("Reconstructions",$rcns);
  Accumulate("No Recons",      $fail);
}

sub GenerateRcns {
    my ($w,$id,$lgabbr,@ptr) = @_ ;

    #print "($w,$id)\n";
    $rcx = 0 ;                      #counts recons for *this* form
    
    #print "gen: $id,$lgabbr,$w\n";
    test($fmt,4,sprintf $fmtstr[1],$id,$lgabbr,$w);
    if ($special{$id} eq "skip") {
	    push @{ $recons{"SKIPPED"} },$id ;
	    $rflxs{$id} =  [ @ptr ];    #for each form, save ptr to orgnl
    }
    else {
	Tokenize($w,"","","","",$id);
	$rcns += $rcx ;
	test($fmt,4,sprintf $fmtstr[4],$rcx,$lgabbr,$w,$id);
	$rflxs{$id} =  [ @ptr ];    #for each form, save ptr to orgnl
	if ($rcx == 0) {
	    push @{ $recons{"FAILED.$lgabbr"} },$id ;
	    $fail++ ;
	}
    }
}
sub GenerateByRule {
    my ($w,$id,@ptr) = @_ ;
    $rcx = 0 ;                      #counts recons for *this* form
    #test($fmt,4,sprintf $fmtstr[1],$id,$lgabbr,Chr2Dis($w));
    if ($special{$id} eq "skip") {
	    push @{ $recons{"SKIPPED"} },$id ;
	    $rflxs{$id} =  [ @ptr ];    #for each form, save ptr to orgnl
    }
    else {
	Tokenize($w,$id,(),0);
	$rcns += $rcx ;
	#test($fmt,4,sprintf $fmtstr[4],$rcx,$lgabbr,Chr2Dis($w),$id);
	$rflxs{$id} =  [ @ptr ];    #for each form, save ptr to orgnl
	if ($rcx == 0) {
	    push @{ $recons{"FAILED.$lgabbr"} },$id ;
	    $fail++ ;
	}
    }
}
sub CreateSets {                   #compare sets, merge subsets, etc.
    local @rawsets = () ;          #local so SubSets, etc. can see it...
    @nonce  = () ;                 #global but prbbly doesnt have to be
    test($fmt,7,"SET  : [] Studying sets ...\n" );
    my @xsets = keys %recons ;
    @rawsets  = grep((@{$recons{$_}} >  1),@xsets) ; #sets w/ 2+ supports
    @nonce    = grep((@{$recons{$_}} == 1),@xsets) ; #recons w/ only 1 sf
    #($test== 6) && &DumpSets(@rawsets);
    &SubSets ;                        #reconcile sets
    $NRawSets = scalar @rawsets ;
    $NSets    = scalar @sets;
    Accumulate("Sets created",  scalar @rawsets );
    Accumulate("Sets retained", scalar @sets );
}
sub SubSets {                         #find all sets which are subsets
    my ($r, $i, $j, $c, $z, %mark, @l, @x, @int) ; #     of other sets
    $i = 0 ;
    for ($i = 0 ; $i < ($max = @rawsets) ; $i++)  {
	$r = $rawsets[$i] ;
	if ($r ne "DEL") {
	    @l = @{ $recons{$r} } ;
	    for ($j = 0 ; $j < $max ; $j++)  {
		$z = @rawsets[$j] ;
		if ($z ne "DEL" && $i != $j) {
		    @x = @{ $recons{$z} } ;   
		    %mark = () ;
		    grep($mark{$_}++,@l);     # compute set intersexn
		    @int = grep($mark{$_},@x); # < camel book...
		    $c = scalar @int ;        # compare # of elements...
		    if ($c == scalar @l) {    # @l = subset of curr. set
			#print "$i/$r: ",(join " ",@l),
			#" : subset of  ","$j/$z: ",(join " ",@x),"\n" ;
			$rawsets[$i] = "DEL" ;# so zap it...
		    }
		    elsif ($c == scalar @x) { # curr. set = subset of @l
			#print "$j/$z: ",(join " ",@x),
			#" : subset of  ","$i/$r: ",(join " ",@l),"\n" ;
			$rawsets[$j] = "DEL" ;# so zap it...
		    }
		}
	    }
	} 
    }
    @sets = grep $_ ne "DEL",@rawsets ;
    #($test== 6) && &DumpSets(@sets);
}
sub DumpSets {
    my (@sets) = @_ ;
    my ($r, $i, $x, $a, $b) ;
    #test($fmt,6,sprintf $fmtstr[17],scalar @sets . " set(s) retained";
    #for $r (@sets) {
    for ($i = 0 ; $i < ($max = @sets) ; $i++)  {
	$r = $sets[$i] ;
	print "$r $i xxx\n";
	grep { 
	    for $a (@{ $rflxs{$_}}) {
		for $b (@{$a}) {
		    test($fmt,6, $i."\t".$r."\t". $rcnlist{$r}."\t".
			join("\t",@{ $arts{$b}}) . "\n");
		}
	    }
	}
	@{ $recons{$r} } ;
    }
}
sub DumpRcns {
    my ($fn) = @_ ;
    my $lgn = $langues{$lgabbr};
    my ($r, $i, $x, $a, $b) ;
    open(RCNFILE,">$fn") || Statistics("$fn not opened");
    binmode(RCNFILE, 'utf8');
    foreach $r (sort keys %recons)  {
	$i++;
	grep { 
	    for $a (@{ $rflxs{$_}}) {
		for $b (@{$a}) {
		    print RCNFILE $r."\t". $rcnlist{$r}."\t".
			$b . "\t" . join("\t",@{ $arts{$b}}) . "\n";
		}
	    }
	}
	@{ $recons{$r} } ;
    }
    close(RCNFILE);
}
sub LoadRcns {
    #my ($fn) = @_ ;
    #open(RCNFILE,"<$fn") || Statistics("$fn not opened");
    while (<>)  {
	chomp;
	my ($ana,$r,$id,$lg,$rfx,$gls) = split "\t";
	$arts{$id} = [ $lg,$rfx,$gls ];
	push @{ $rflxs{$ana}  }, "$lg.$id" ;
	push @{ $wds{$rfx}    }, "$lg$id" ;
	push @{ $recons{$ana} }, "$lg.$id" ;
	$rcnlist{$ana} = $r ;
    }
    close(RCNFILE);
}
##------------------------------------------> Tokenization
sub syllchk {
    return (@_[0] =~ /$syllcanon/) ? "OK" : "Failed<br>";
}

sub Statistics {
    my ($type) = @_ ;
    #print "type $type, test $test\n";
    test($fmt,1,sprintf "STAT : [] %-9s",$type );
    if ($type =~ /^START/) {
	test($fmt,1,"parameters: $REparmfile");
	#test($fmt,1,sprintf "STAT : [] %-9s",$type );
	}
    elsif ($type =~ /^END/) {
	test($fmt,3, sprintf "test() was called %d times\n",$tcnt );
	test($fmt,1, "*****" );
	}
    elsif ($type =~ /^DATA/) {
	test($fmt,1, sprintf "%s %s %6s",
	$settings{"Forms processed"} . " forms,",
	$settings{"Reconstructions"} . " recons,",
	$settings{"No Recons"} .       " no rc" );
	}
    elsif ($type =~ /^SET/) {
	test($fmt,1, sprintf "%s %s %6s",
	$settings{"Sets created"} .  " raw sets,",
	$settings{"Sets retained"} . " merged sets,",
	$settings{"Isolates"} .      " isolates");
	}
    elsif ($type =~ /^LEXICON/) {
	($test >= 1) && test($fmt,1, 
	    "$lgabbr : $wrds words, $rcns recons, $fail failed") ;
	($test == 2) && test($fmt,2, 
	    sprintf "%12s  %6d%6d%6d",$lgabbr,$wrds,$rcns,$fail)  ;
	}
    elsif ($type =~ /^INPUT/) {
	($test >= 1) && test($fmt,1, 
	    "$lgabbr : $forms words") ;
	($test >= 2) && test($fmt,2, 
	    sprintf "%12s  %6d%6d%6d",$lgabbr,$wrds,$rcns,$fail)  ;
	}
    else {
      #test($fmt,1,$type );
    }
    test($fmt,1,"\n") ;
}
sub Accumulate {
    ($key,$val) = @_ ;
    $settings{$key} += $val ;
}
sub OutputResults {
    $nsets = 0 ;
    if (!$REoutfile) {
	test($fmt,1,"OUT  : [] No -o <file> supplied; no SETS written. \n" );
	return ;
    }
    my ($rcn,$a) ;
    test($fmt,3,"OUT  : [] Writing output... \n" );
    print OUTFILE "<sets>\n";
    %isolates = %rflxs ;
    for $rcn (@sets) {
	print OUTFILE PrintSet($rcn) ;
    }
    print OUTFILE "</sets>\n";
    for $rcn (@sets) {
	LineWise($rcn) ;
    }
    print OUTFILE "<isolates>\n";
    #print join " ",keys %isolates;
    for $iso (keys %isolates) {
	for $a (@{$isolates{$iso}}) {
	    for $b (@{$a}) {
		$isocnt++;
		print OUTFILE  SGMLtag(qw(rfx),
		       sprintf("<lg>%s</lg><lx>%s</lx><gl>%s</gl>",@{ $arts{$b}}) . 
		       SGMLtag(qw(rn),$iso) . 
     		       SGMLtag(qw(hn),$b)) ;
		#print OUTFILE PrintIsolate($rcn) ;
	    }
	}
    }
    print OUTFILE "</isolates>\n";
    Accumulate("Isolates", $isocnt );
}
sub PrintSet {
    my ($rcn) = @_ ;
    my ($res) ;
    $nsets++ ; 
    $res .= SGMLtag(qw(id),$nsets) ;
    $res .= SGMLtag(qw(rcn),$rcn) ;
    $res .= SGMLtag(qw(pfm),$rcnlist{$rcn});
    $res .= SGMLtag(qw(ref),(join " ",@{ $recons{$rcn} })) ;
    $res .= "<sf>\n";
    grep { 
	for $a (@{ $rflxs{$_}}) {
	    delete $isolates{$_} ; #if it's in a set it can't be an isolate...
	    for $b (@{$a}) {
		$res .= SGMLtag(qw(rfx),
			sprintf("<lg>%s</lg><lx>%s</lx><gl>%s</gl>",@{ $arts{$b}}). 
			SGMLtag(qw(rn),$_) . 
			SGMLtag(qw(hn),$b)) ;
	    }
	}
    }
    @{ $recons{$rcn} } ;
    $res .= "</sf>\n";
    SGMLtag(qw(set),$res);
}
sub Multi {                  # Compute set membership for reflexes...
    $nsets = 0 ;
    my ($rcn,$res,$a,@m,%mark) ;
    #test($fmt,3,"SET  : [] Computing overlap... \n" ;
    $res .= "<archive>\n";
    for $rcn (@sets) {       # for each set
	$nsets++ ; 
	grep {push @{$mark{$_}},$rcn} @{ $recons{$rcn} } ;
    }
    @m = grep { $a = @{$mark{$_} }; if ($a>1) {push @m,$_}} keys %mark ;
    #test($fmt,5, (sprintf  $fmtstr[6]);
    grep {
	#test($fmt,5,sprintf $fmtstr[2],($_ ." in sets ".
				   #join(", ",@{ $mark{$_} }) . "\n") ; 
	$res .= "<overlap><ref>$_</ref><set>" .
	    join(" ",@{ $mark{$_} }) . "</set></overlap>\n" ; 
	grep LineWise($_), @{ $mark{$_} };
    } @m;
    #test($fmt,5, (sprintf  $fmtstr[8]);
    $res .= "</archive>\n";
    printf OUTFILE $res ;
}
sub LineWise {
    my ($analysis) = @_ ;
    my ($a,$b,%tmp) ;
    grep { 
	for $a (@{ $rflxs{$_}}) {
	    for $b (@{$a}) {
		#$tmp{@{$arts{$b}}[0]}  = sprintf "%s",@{$arts{$b}}[1];
		$tmp{@{$arts{$b}}[0]} = 
		 sprintf $fmtstr[10],@{$arts{$b}}[1..2];
		 #sprintf $fmtstr[10],@{$arts{$b}}[1],$_,$b;
	    }
	}
    }
    @{ $recons{$analysis} } ;
    test($fmt,5, (sprintf  $fmtstr[9],$analysis,map($tmp{$_},@lgnames)));
}
sub SGMLtag {
    my $endtag ;
    ($endtag = @_[0]) =~ s/(.*) */\1/ ;
    return "<@_[0]>" . @_[1] . "</$endtag>\n" ;
}
sub test { 

    my ($fmt,$tv,$tp) = @_ ;
    #$tp =~ s/\n//g;
    #print "<br>TEST: *** fmt,test,tv,'logopen',tp\n";
    #print "<br>    : *** $fmt,$test,$tv,'$logopen',$tp";
    $tcnt++ ;
    ($test >= $tv) && do {
        my $t = localtime time;
        $t =~ s/.{4}(.*)$/$1/ ;
        $tp =~ s/\[\]/\[$t\]/;
        #$tp =~ s/\n/<br>/g ;
        #print $fmt .'<br/>';
        #print $tp;
        #$tp .= "\n" unless ($tp =~ /\n/);
        $logopen && print LOGFILE $tp unless $fmt eq 'quiet';
        if ($fmt eq "h") {
            $tp =~ s/\n/<br>/g ;
            #print $fmt . " " . $tp;
            print $tp;
        }
    }
}
sub SetFmt {
  my ($fmt) = @_;

    if ($fmt eq "h") {
	$fs = "<FONT FACE='STEDT'><B>";
	$fe = "</B></FONT>";
	# stedt fontification temporarily disabled...
	$fs = "<B>";
	$fe = "</B>";
	@fmtstr = (
	"",
	"<H4>(%d) %s $fs%s$fe</H4><TABLE BORDER=1 CELLPADDING=0>" .
	"<TR><TH>No.<TH>Recon<TH>Corrs.<TH>Rules<TH>Syllable<TH>RefNo",
        "<TR><TD COLSPAN=9><FONT SIZE=+2>%s</FONT>",
	"<TR><TD>%d<TD>$fs%s$fe<TD>%s<TD>%s<TD>%s<TD>%s",
	"</TABLE>", #<H4> %d reconstruction produced for: %s $fs%s$fe [%s]</H4>",
	"RLS  : [] %d basic rules from %d ROWS.<P>", #5
	"<H4>%s for %s = /%s/:</H4><TABLE BORDER=1 CELLPADDING=0>",
	"<TR>" . ("<TD>%s" x 5) . ("<TD>$fs%s$fe" x 2) . "<TD>%s<TD>$fs%s$fe\n",
	"</TABLE>",                            #8
	"<TR>" . ("<TD>%s&nbsp;" x 9) . "\n",  #9
        "$fs%s$fe<br><FONT SIZE=-1>%s</FONT>", #10
	"<TR><TD>%d<TD>%d<TD>%s<TD>$fs%s$fe<TD>",  #11
        "<TD>$fs%s$fe",                        #12
	"<TR><TD COLSPAN=4>delete rule: %s contexte %s non satisfait\n",  #13
	"<TR><TD COLSPAN=4>rules OK: %s analyse letter %s \n",  #14
        "<TR>" . "<TD>%s" x 2 . "<TD>%s",      #15
	"<TABLE BORDER=1 CELLPADDING=0>",      #16
	"<H4>%s</H4>",
		   ) ;
	$tr = "<TR>" ;
	$td = "<TD>";
	}
    else {
	@fmtstr = (
	"",
	"\n[%d] %s '%s'\n",                    #1
	"",                                    #2
	" %8s: %-15s %-15s %-15s %-8s : %s\n", #3
	"\n", #  %d reconstructions produced for: %s %s [%s]\n",
	"RLS  : [] %d diachronic rules from %d correspondence rows.\n",
	"\n%d rules and %d constituents for language %s\n\n",
	"%4d %5s %4s %4s  ".("%-10s"x6)."\n",    #7
	"",                                    #8
	#"%-10s "x9 . "\n",                    #9
	"\t%s"x9 . "\n",                       #9
	#"%s:%s",                              #10
	"%s",                                  #10
        "%6d %9d : %8s %9s %s\n",              #11
        "%s",                                  #12
	"delete rule: %s contexte %s non satisfait\n",  #13
	"rules OK: %s analyse letter %s\n",    #14
	"%-12s%8d%8d\n",                       #15
        "",                                    #16
	"$s",
		   ) ;
	$tr = "\n";
	}
}

1;
