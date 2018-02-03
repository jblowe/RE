sub SetOpts {
    my (@preamble) = @_ ;
    $delim      =  "#" ;             #not used at the moment...
    $syllcanon  =  "^(C*V+C*)+\$" ;  #default syllable canon
    SetFmt() ;                       #set format strings for environment
    #interactive and www commands...
    %cmd = abbrev @clist = 
    qw(quit batch convert upstream downstream lg sets set testset help syll log corr rule element);
    
    for (@preamble) {
	($t,$d) = @$_;
	if ($t =~ /^class:(.*)/) {
		$classes{$1} = $d;
	}
	$settings{$t} = $d ;
	test(4,sprintf "   setting: %-15s = %s\n",$t,$d );
    }
    $settings{SYLLABLE} && ($syllcanon = "^".$settings{SYLLABLE}."\$") ;
    test(1,"PRE  : [] " . $settings{TITLE}. "\n");
    $limit && (test(1,"PRE  : [] limit is " . $limit . 
		    " words from each lexicon.\n"));
    $settings{"Reconstructions"} = 0 ;
    $settings{"Forms Processed"} = 0 ;
    $settings{"Isolates"}        = 0 ;
    $settings{"No Recons"}       = 0 ;
    test(2,"SYLL : [] CANON = " . $syllcanon . "\n");
}
