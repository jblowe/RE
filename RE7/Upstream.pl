#######################################################################
#
#  R E C O N S T R U C T I O N    E N G I N E
#
#  module: Batch Upstream
#
$version = "v6.2 1 Aug 2001" ;
#
# see RE.pl for documentation
########################################################################
# Maintenance record:
#
# v6.0   jbl  3 Nov 1997 First PERL versions
# v6.1   jbl  1 Jun 2001 Modularization!
# v6.2   jbl  1 Aug 2001 Further modularization, fixes
#######################################################################
#use strict;
use XML::Parser;
use XML::DOM;
use Data::Dumper;

require "RE2.pl" ;                     # RE-specific subs
require "RErules.pl";
use Getopt::Std;                      # command line options processing
use Time::Local ;                     # timestamps, etc.

my $version = "v7.0 14 Jun 2014" ;

binmode(STDOUT, 'utf8');

sub Upstream {
  
  ($dir,$prj,$prms,$out,$fmt,$limit) = @_;
  
  Statistics("RE $version");      #gather start of run statistics     
  
  initializePrj($dir,$prj,$prms,$out,$fmt,'log!',$limit) || return;

  open(OUTFILE,">$REoutfile") || die "can't open RE output file '$REoutfile'!";
  binmode(OUTFILE, 'utf8');
    

  %recons    = () ;						#list of reconstructions
  %rflxs     = () ;						#list of words processed
  my @languages = @{ $settings{'Languages'} };
  my $csvdata = $settings{'csvdata'};
  #print "$csvdata\n\n";
  if ($csvdata) {
    LoadCSV("$dir/$csvdata");
    #print scalar @languages;
    foreach $lgabbr (@languages) {
      #print "$lgabbr\n";
      SetupRules($lgabbr) ;
      %wds = %{ $lex{$lgabbr} };
      CreateRcns($lgabbr, %wds) ;			       	#create/update list of recons
      Statistics(qw(LEXICON)) ;				        #add things up
    }
  }
  else {
    #print Dumper(@languages);
    foreach my $lgdata (@languages) {
      ($lgabbr,$fn) = @{ $lgdata };
      if (! -f "$dir/$fn") {
	$fn =  "$prj.$lgabbr.data.xml";
      }
      if (! -f "$dir/$fn") {
	test($fmt,1,sprintf "STAT : [] %-9s",'LEXICON');
	test($fmt,1,"$lgabbr : $prj.$lgabbr.data.xml not found\n") ;	#output a placeholder row
      }
      else {
	LoadLexicon("$dir/$fn");				#create wd list, set up lg parmslgabbr
	SetupRules($lgabbr) ;					#create lg rules for this data
	#print Dumper(%lgrules);
	CreateRcns($lgabbr,%wds) ;				#create/update list of recons
	Statistics(qw(LEXICON)) ;				#add things up
      }
    }
  }
  Statistics(qw(DATA)) ;						#first summarize counts
  DumpRcns($REkeyfile);
  CreateSets() ;							#analyze recons, make sets
  print OUTFILE "<re>\n";
  Multi() ;							#compute overlap
  OutputResults();						#write results
  print OUTFILE "</re>\n";
  Statistics(qw(SET)) ;						#summarize sets
  Statistics(qw(END)) ;						#final run stats
}

sub initializePrj {
    my ($dir, $prj, $prms, $out, $fmt, $log, $limit) = @_ ;
	
    my ($y,$d,$h,$m) = (localtime)[5,7,2,1];
    my $date = sprintf "%s.%s.%s.%s",$y+1900,$d+1,$h,$m;
    $REparmfile = "$dir/$prj.$prms.parameters.xml";
    $RElogfile  = "$dir/$prj.$out.log.txt";
    $REoutfile  = "$dir/$prj.$out.sets.xml";
    $REkeyfile  = "$dir/$prj.$out.keys.txt";
    $REsetfile  = "$dir/$prj.$out.keys.txt";
    OpenLog($RElogfile) if $log;
    Statistics(qw(START));
    
    SetFmt($fmt) ;                       	#set format strings for environment  

    test($fmt,1,"PRE  : [] START    number of words to process from each lexicon: " . ($limit == 0 ? 'unlimited' : $limit) . "\n");
    $limit = 999999 if $limit eq 0;
 
    #print $REparmfile;
    LoadParam($REparmfile);    #read and set parms
    #print %settings;
    $RErulefile = "$dir/".$settings{'correspondences'};
    #LoadSpecial("$file.excl") ;		#forms requiring special handling

    if (! -e $RErulefile) {
      Statistics("ERROR  no rule/correspondence file $RErulefile found!");
      Statistics(qw(END)) ;			
      return 0;
    }

    if ($RErulefile =~ /\.xml/i) {
      LoadTableOfCorr($RErulefile);		#initialize (global) rule list as XML
    }
    elsif ($RErulefile =~ /\.csv/i) {
      LoadTableOfCorrCSV($RErulefile);		#initialize (global) rule list from .csv file
      $settings{"Languages"}       = \@lgnames;
    }

    return 1;
    
}
