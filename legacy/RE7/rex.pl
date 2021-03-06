#######################################################################
#
#  R E C O N S T R U C T I O N    E N G I N E
#
#  module: Batch Upstream
#
$version = "v6.0 10 Nov 1997" ;
#
# see RE.pl for documentation
########################################################################
# Maintenance record:
#
# v6.0   jbl  3 Nov 97  First PERL versions
# v7.0   jbl 06 Jun 14  First revisions
#
# perl rex.pl -o run2 -x DATA/DEMO93  -p default -d DEMO93 -f xxx -t 3
#
#######################################################################
require "Upstream.pl" ;               # RE-specific subs
use Getopt::Std;                      # command line options processing
use Time::Local ;                     # timestamps, etc.


#######################################################################
# Get ready to run
#######################################################################
getopt("pdtnoxf", \%opts) ;
my $prms      = $opts{'p'};
my $prj       = $opts{'d'};
my $limit     = int($opts{'n'}); #number of forms to process in each lex
my $run       = $opts{'o'};
my $dir       = $opts{'x'};
my $f         = $opts{'f'};

$test         = int($opts{'t'}) ;

print "test =  $opts{'t'} $test \n";

#foreach $o (keys %opts) {
#  print "$o " . $opts{$o} . "\n";
#}

Upstream($dir,$prj,$prms,$run,'',$limit);
