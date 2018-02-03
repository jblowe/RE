#use strict;


sub getAllData {
  my ($node) = @_;
  my $result = "";
    
  my $myType = $node->getNodeType();
  if ($myType == 3) {
    my $data = $node->getData;
    $result = "$data";
  } else {
    my $elt = $node->getChildNodes();
    my $n = $elt->getLength;
    for (my $i=0; $i<$n; $i++) {
      $item =$elt->item($i);
      my $data = &getAllData($item);
      $result = "$result$data";
    }
  }
  $result;
}

sub LoadTableOfCorrCSV {                         #make "canonical form" of rules
  my ($fn) = @_;
  my ($i,$j,$k,$r,@h,$q,@c,@d,@x,$z) ; #i.e. L1 x > L2 y rules
  my($nameClasse, $clef, $valeur);
  
  #initialisations
  #%classes = ();
  #$nameClasse = "";
  #$dlm = '\\\011';
  $dlm = "\t";
  
  if (open(CORRS,"<$fn")) {
    test($fmt,1,"RLS  : [] CSV correspondence file:\n");
    test($fmt,1,"RLS  : [] $fn\n");
  }
  else {
    test($fmt,1,"RLS  : [] failed to open CSV correspondence file:\n");
    test($fmt,1,"RLS  : [] $fn\n");
    return;
  }

  binmode CORRS, ":utf8";
  my @rules = <CORRS>;
  chomp @rules;

  test($fmt,5,scalar @rules . " data lines in csv file\n");

  @rules = grep { s/[\r\n]+//g; $_  } @rules;
  @rules = grep { /^[^#]/ } @rules;


  @header = split($dlm,$rules[0]) ;
  $startlg = 5 ;
  $endlg   = @header - 1;
  @lgnames  =  @header[$startlg .. $endlg] ;


  test($fmt,5,"\nTable of Correspondence column headers\n");
  foreach $c (@header) {
    $n++;
    test($fmt,5,$n . ' = ' . $c . "\n");
  }

  my $i = 0 ;
  for $r (@rules) {
    @h = split($dlm,$r) ;
    next if $h[2] eq 'Type';
    #print $r . "\n";
    $k++ ;
    for $i ($startlg .. $endlg) {
      @c = split /[=,]/,$h[$i] ;
      for $z (@c) {       # expand ToC cells (e.g. i=e or a,o)
	@d = split /,/,$h[2] ;
	for $q (@d) {   # expand syllable slots (e.g. R,V)
	  $j++ ;
	  @x = ($j-1,@h[0..1],$q,$header[3],@h[3..4],$header[$i],$z) ;
	  push @rls, [ @x ];
	  #test($fmt,6,(join "\t", @x) . "\n" );
	}
      }
    }
  }
  test($fmt,1,sprintf $fmtstr[5],$j,$k );
  ($test >= 3) && &OutputRules ;
  #test($fmt,1,"LEX  : [] Run stats         Lg    Forms Recns  Fail \n" );
  #test($fmt,1,"LEX  : [] =========  ==========   ===== ===== ===== \n" );
}
# Transforme les lignes de la table de correspondances en règles
# nb règles = nbFormesParLangues * typeSyllabiques. A quoi sert l'*' dans les @rls?
sub LoadTableOfCorr {
  my ($fn) = @_ ;
  
  @rls = ();
  @lgnames  =  ();
  
  %langues = ();	
  my $parser = new XML::DOM::Parser;
  my $doc = $parser->parsefile($fn);
  if ($doc) {
    test($fmt,1,"RLS  : [] XML correspondence file:\n");
    test($fmt,1,"RLS  : [] $fn\n");
  }
  else {
    test($fmt,1,"RLS  : [] failed to open XML correspondence file:\n");
    test($fmt,1,"RLS  : [] $fn\n");
    return;
  }
  my $root = $doc->getDocumentElement;
  my $nbRule = 0;
  my $nbCorr = 0;
  for $parameters ($root->getElementsByTagName ("parameters")) {
    for $parm ($parameters->getElementsByTagName ("*")) {
      my $tag = $parm->getNodeName;
      my $name = $parm->getAttribute("name");
      if ($tag =~ /class/i) {
	my $class = $parm->getAttribute("name");
	$settings{$class} = $parm->getAttribute("value");
      }
      elsif ($tag =~ /canon/i) {
	$settings{SYLLABLE} = $parm->getAttribute("value");
	$settings{SYLLABLE} && ($syllcanon = "^".$settings{SYLLABLE}."\$") ;
      }
    }
  }
  for $corr ($root->getElementsByTagName ("corr")) {
    $nbCorr++;
    my $num 	= $corr->getAttribute("num");
    my $level 	= $corr->getAttribute("level");
    for $protoElt ($corr->getElementsByTagName ("proto")) {
      my $proto   	= getAllData($protoElt);
      my @syllabes    = split /,/,$protoElt->getAttribute ("syll");
      my $context 	= $protoElt->getAttribute("context");
      for $modernElt ($corr->getElementsByTagName ("modern")) {
	my $lang = $modernElt->getAttribute("dialecte");
	if (!$langues{$lang}) {
	  $langues{$lang} = $n;
	}
	for $modern ($modernElt->getElementsByTagName ("seg")) {
	  for $syllabe (@syllabes) {
	    my @mseg = split /[=,]+/, getAllData($modern);
	    for $m (@mseg) {
	      @x = ($nbRule++, $num, $level, $syllabe, '*', $proto, $context, $lang, $m);
	      push @rls, [ @x ];
	    }
	  }
	}
      }
    }
  }
  @lgnames = keys(%langues);
  # pour afficher les statistiques (provisoire)
  test($fmt,1,sprintf $fmtstr[5],$nbRule,$nbCorr, $fmt );
  ($test >= 3) && &OutputRules ;
  test($fmt,1,"LEX  : [] Run stats         Lg    Forms Recns  Fail\n", $fmt );
  test($fmt,1,"LEX  : [] =========  ==========   ===== ===== =====\n", $fmt );
}

sub SetupRules {
  my ($lgabbr) = @_;
  my ($i,$n);
  %lgrules = () ;              #clean out the global rule list
  @colnames =  qw(ID Corr Chron Slot PLg Anc Con Lg Out);
  %colhash  =  map {$_, $i++} @colnames ;
  #print $test, " xxx ",$lgabbr,'xxx';
  my @lgrls = grep {$$_[7] =~ m/$lgabbr/} @rls  ;
  #print "\nlgrls",scalar @lgrls;
  #pick out rules for this lg
  for my $rules (@lgrls) {
    #print join ",",@{$rules}; print "\n";
    push @{ $lgrules{@$rules[8]} }, [ @$rules[0],@$rules[1] ];
    #print Dumper( $lgrules{@$rules[8]} );
    #make hash pointing to list of rules
    #and corrs for each constituent in lg
  }
  #print Dumper(%lgrules);
  ($test >= 5) ? do {
    test($fmt,5,sprintf $fmtstr[7],@colnames );
    #print 'rules ',scalar @rls,' ',scalar @lgrls,"\n";
    grep {
      $i++;
      (test($fmt,5,sprintf $fmtstr[7], @$_ ), $fmt) } @lgrls ; } : "" ;
}

sub Tokenize {
  my ($s,$w,$a,$b,$d,$id) = @_ ;
  my ($x,$i,$c,$r,$y,@x,$g,$h,$k,$m) ;
  #print "$d :: $syllcanon\n";
  if (!$s) {                        # base case for recursion
    if ($d =~ /$syllcanon/) {       # if a "good" syllable...
      $rcx++ ;
      push @{ $recons{$b} },$id ; # add ptr to ListOfRcns
      $rcnlist{$b} = $w ; # save form for output later!
      test($fmt,4,sprintf $fmtstr[3],$rcx,$w,$a,$b,$d,(join " ",(@{ $recons{$b} }))) ;
    }
  }
  else {
    for $i (1 .. length $s) {      # for each initial substring of
      $s =~ /(.{$i})(.*)$/ ;     # the "rest" of this form...
      $c = $1 ; $r = $2 ; @x = () ; # on your marks, get set...
      @x = @{ $lgrules{$c} } ;   # if init. substr is in the ToC
      # test @x here for Panini!
      foreach $y (@x) {          # pass it down the line...
	$g = @$y[0] ;          # rule number
	$h = @$y[1] ;          # corr row number
	$k = $rls[$g][5];      # output of rule(usually protolg)
	$m = $rls[$g][3];      # syll slot
	#print  $r,"$w$k","$a$g.","$b$h.","$d$m",$id,"\n" ;
	Tokenize($r,"$w$k","$a$g.","$b$h.","$d$m",$id) ;
      } 
    }  
  }
}


sub HTMLParms {
    ($dir,$prj,$prms,$out,$fmt,$limit) = @_;
    print "<h3>" . $REparmfile . "</h3>";

    my @parms =  qw(title correspondences SYLLABLE fuzzy spec trace csvdata);
    print '<table style="width: initial" cellspace="1" id="settings" class="tablesorter"><thead>';
    print SGMLtag(qw(tr),'<th width="150px">' . join("<th>",qw(Parameter Value)));
    print "</thead><tbody>";
    for my $setting (@parms) {
      if ($settings{$setting}) {
	print  SGMLtag(qw(tr),"<td>$setting" . "<td>" . $settings{$setting}) ;
      }
      else {
	print  SGMLtag(qw(tr),"<td>$setting" . "<td>*** not specified ***") ;
      }
    }
    print "</tbody></table>\n";

    my @languages = @{ $settings{'Languages'} };
    my $csvdata = $settings{'csvdata'};
    if ($csvdata) {
      print "<h3>CSV Data</h3>";
    }
    else {
      print "<h3>XML Data</h3>";
    }
    print '<table style="width: initial;" cellspace="1" id="languaages" class="tablesorter"><thead>';
    print SGMLtag(qw(tr),'<th width="150px">' . join("<th>",qw(Language File/column Count)));
    print "</thead><tbody>";
    
    if ($csvdata) {
      my $i = 0;
      LoadCSV("$dir/$csvdata");
      #print scalar @languages;
      foreach $lgabbr (@languages) {
	$i++;
	#print "$lgabbr\n";
	SetupRules($lgabbr) ;
	%wds = %{ $lex{$lgabbr} };
	my $items = scalar keys %wds;
	print  SGMLtag(qw(tr),"<td>$lgabbr" . "<td>$i" . "<td>$items") ;
      }
    }
    else {
      foreach my $lgdata (@languages) {
	($lgabbr,$fn) = @{ $lgdata };
	if (! -f "$dir/$fn") {
	  $fn =  "$prj.$lgabbr.data.xml";
	}
	if (! -f "$dir/$fn") {
	  test($fmt,1,"$lgabbr : $prj.$lgabbr.data.xml not found\n") ;	#output a placeholder row
	}
	else {
	  LoadLexicon("$dir/$fn");				#create wd list, set up lg parmslgabbr
	  SetupRules($lgabbr) ;					#create lg rules for this data
	}
	my $items = scalar keys %wds;
	print  SGMLtag(qw(tr),"<td>$lgabbr" . "<td>$dir/$fn" . "<td>$items") ;
      }
    }
    print "</tbody></table>\n";
    print <<SCRIPT
    <script>
           \$('#settings').tablesorter({
            });
    </script>
SCRIPT

}

sub HTMLRules {
    $nrules = 0 ;
    print "<h3>" . $RErulefile . "</h3><hr/>";
    @colnames =  qw(ID Corr Chron Slot PLg Anc Con Lg Out);

    print '<table style="width: initial;" cellspace="1" id="rules" class="tablesorter"><thead>';
    print SGMLtag(qw(tr),'<th>' . join("<th>",@colnames));
    print "</thead><tbody>";

    for my $r (@rls) {
	$nrules++ ; 
	print  SGMLtag(qw(tr),'<td>' . join("<td>",@{$r})) ;
    }
    print "</tbody></table>\n";
    print <<SCRIPT
    <script>
           \$('#rules').tablesorter({
            });
    </script>
SCRIPT

}


sub HTMLCorrs {
  
  my $corrs;
  my $lgnames;

  if ($RErulefile =~ /xml/i) {
    ($corrs, $lgnames) = getXMLcorrs($RErulefile);
  }
  elsif ($RErulefile =~ /csv/i) {
    ($corrs, $lgnames) = getCSVcorrs($RErulefile);
  }
  else {
    print "<h3>Couldn't parse file $RErulefile</h3>";
  }

  $nrules = 0 ;
  print "<h3>" . $RErulefile . "</h3>";
  my @colnames =  qw(ID Corr Chron Slot PLg Anc Context);
  
  print '<table style="width: initial;" cellspace="1" id="corrs" class="tablesorter"><thead>';
  print SGMLtag(qw(tr),'<th>' . join("<th>",@colnames) . '<th>' . join("<th>",@{$lgnames}));
  print "</thead><tbody>";
  
  foreach my $r (@{$corrs}) {
    $nrules++ ; 
    print  SGMLtag(qw(tr),'<td>' . join("<td>",@{$r})) ;
  }
  print "</tbody></table>\n";
  print <<SCRIPT
    <script>
           \$('#corrs').tablesorter({
            });
    </script>
SCRIPT
    
}

sub getXMLcorrs {
  my ($fn) = @_ ;
  
  my @rls = ();
  my @lgnames  =  ();
  
  %langues = ();	
  my $parser = new XML::DOM::Parser;
  my $doc = $parser->parsefile($fn);
  my $root = $doc->getDocumentElement;
  my $nbRule = 0;
  my $nbCorr = 0;
  for $parameters ($root->getElementsByTagName ("parameters")) {
    for $parm ($parameters->getElementsByTagName ("*")) {
      my $tag = $parm->getNodeName;
      my $name = $parm->getAttribute("name");
      if ($tag =~ /class/i) {
	my $class = $parm->getAttribute("name");
	$settings{$class} = $parm->getAttribute("value");
      }
      elsif ($tag =~ /canon/i) {
	$settings{SYLLABLE} = $parm->getAttribute("value");
	$settings{SYLLABLE} && ($syllcanon = "^".$settings{SYLLABLE}."\$") ;
      }
    }
  }
  for $corr ($root->getElementsByTagName ("corr")) {
    $nbCorr++;
    my $num 	= $corr->getAttribute("num");
    my $level 	= $corr->getAttribute("level");
    for $protoElt ($corr->getElementsByTagName ("proto")) {
      my $proto   	= getAllData($protoElt);
      my $syllabes      = $protoElt->getAttribute ("syll");
      my $context 	= $protoElt->getAttribute("context");
      my @x = ($nbCorr, $num, $level, $syllabes, '*', $proto, $context);
      for $modernElt ($corr->getElementsByTagName ("modern")) {
	my $lang = $modernElt->getAttribute("dialecte");
	if (!$langues{$lang}) {
	  $langues{$lang} = $n;
	}
	my @segs;
	for $modern ($modernElt->getElementsByTagName ("seg")) {
	    push @segs, getAllData($modern);
	}
	push @x, join('; ',@segs);
      }
      push @rls,[ @x ];
    }
  }
  @lgnames = keys(%langues);

  return \@rls, \@lgnames ;

}


sub getCSVcorrs {
  my ($fn) = @_ ;
  
  my @rls = ();
  my @lgnames  =  ();
  my @header;
  my $plg;
  
  %langues = ();
  open CORRS, "<$fn";
  binmode(CORRS, 'utf8');
  my $nbRule = 0;
  my $nbCorr = 0;
  while (<CORRS>) {
    next if /^#/;
    chomp;
    $nbCorr++;
    if ($nbCorr == 1) {
      @header = split /\t/;
      $plg = @header[3];
      next;
    }
    my @x = split /\t/;
    # oops...have to stick protolg name into row...
    splice(@x,4,0,$plg);
    push @rls,[ $nbCorr - 1, @x ];
  }
  @lgnames = splice(@header,5);

  close CORRS;

  return \@rls, \@lgnames ;

}

sub OutputRules {
    $nrules = 0 ;
    if (!$REoutfile) {
	test($fmt,1,"RLS  : [] No output file supplied; no RULES written.",$fmt);
	return ;
    }
    my ($r) ;
    test($fmt,3,"RLS  : [] Writing rules... \n", $fmt );
    printf OUTFILE "<RULES>\n";
    for $r (@rls) {
	$nrules++ ; 
	printf OUTFILE SGMLtag(qw(RULE),(join " ",@{$r})) ;
    }
    printf OUTFILE "</RULES>\n";
}
##---------------------------> test if a letter match with a context
sub TstCx { 
    my($fait, $context) = @_;
    my($reponse);
    
    $reponse = 1;				     #context => true
    if ($context){
		$reponse = 0;			     # false
		if ($fait =~ /^($context)$/) {
			$reponse = 1;		     # => true
		}
    }
    $reponse;
}
##------------------------> recuperation du contexte gauche
sub gLCx { 
    my($numRegle) = @_;
    my($context, $pos, $avant);
    
    $avant = "";
    if ($numRegle >= 0) {
		$context = $rls[$numRegle][6]; ## cherche la regle testee
		$context =~s/^[\/\*]*//;       ## supprime '*' et '/'
		if (($pos = index($context, "_")) != -1) {
			$avant = substr($context, 0, $pos);
		}
		$avant = &replaceMacro($avant);
		$avant =~ s/\,/\|/g;
    }
    $avant;
}
##--------------------------------> recuperation du contexte droite
sub gRCx { 
    my($numRegle) = @_;
    my($context, $pos, $apres);
	
    
    $apres = "";
    if ($numRegle >= 0) {
		$context = $rls[$numRegle][6]; ## cherche la regle testee
		$context =~s/^[\/\*]*//;       ## supprime les '*' et '/'

		if (($pos = index($context, "_")) != -1) {
			$apres = substr($context, $pos+1,length($context));
		}
		$apres = &replaceMacro($apres);
		$apres =~ s/\,/\|/g;
    }
    $apres;
}
##--------------------------> recuperation la lettre
sub getLetter { 
    my($numRegle) = @_;
    my $lettre;
    if ($numRegle) {
	$lettre = $rls[$numRegle][5];
    }
    $lettre;
}
##--------------------------> recuperation des toutes les regles
sub getRules { 
    my($lettre) = @_;
#print "lettre ",$lettre,"\n";
    my @tableaDeRegles, %baseDeRegles, $num, $regle;
    
    @tableaDeRegles = ();	#initialisations
    %baseDeRegles = ();
    
    @tableaDeRegles  = @{$lgrules{$lettre}};
    foreach $regle (@tableaDeRegles) {
	$num++;
	$baseDeRegles{"regle$num"} = @$regle[0];
    }
    %baseDeRegles ;
}
sub PopPush { 
    my (@resultats) = @_;
    my $numRegle, $size;
    
    $numRegle = "-1";
    if (($size = @resultats) > 0){
		$numRegle = pop(@resultats);
		push(@resultats, $numRegle);
    }
    $numRegle;
}
sub computeSpecificite { 
    my ($numRegle) = @_;
    my $result = 0;
    if (gLCx($numRegle)) {
		$result++;
    }
    if (gRCx($numRegle)) {
		$result++;
    }
    $result;
}
sub replaceMacro { 
    my($s) = @_;
    my($clef, $valeur);
    
    while(($clef, $valeur) = each(%classes)) {
		$s   =~s/$clef/$valeur/;
    }
    $s;
}

1;
