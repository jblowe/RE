# RE7

A PERL implementation of the Reconstruction Engine, 
which is in turn a "computer implementation of the comparative method"

Runs both from the command line and from the web (i.e. when installed)

To run "in batch" from the command line, try one of the following:

```bash
cd [...]/RE7
# to re-run the DEMO93 data as "run3"
perl -I . rex.pl -o run3 -x DATA/DEMO93  -p default -d DEMO93 -f xxx -t 3 &
# to re-run the Southern and Northern Yi data as "run3"
perl -I . rex.pl -o run3 -x DATA/LOLOISH  -p default -d NYI -f xxx -t 3 &
perl -I . rex.pl -o run3 -x DATA/LOLOISH  -p default -d SYI -f xxx -t 3 &
# to re-run the Polynesian data as "run3"
perl -I . rex.pl -o run3 -x DATA/POLYNESIAN  -p default -d POLYNESIAN -f xxx -t 3
```

From the web:

* Install the script in a directory accessible by the webserver
* Configure CGI scripts to run (e.g. in Apache)
* Visit, e.g.

       http://localhost/~jblowe/RE7/frameset.pl

Set values, click on "Batch Upstream"...

NB: for the larger datasets (e.g. TGTM), it may take a while
(many minutes!) to run the full set.

The code here represents several iterations of the experiment.

Standard PERL modules (you probably will not need to install these):

```
Data::Dumper
Getopt::Std
Time::Local
```

Other Perl modules (you will probably have to install these; use CPAN, of course)

```
Text::Abbrev
XML::Parser
XML::DOM
CGI
CGI::Carp
```

## Installation

There is no particular installation or deployment apparatus. In general:

* Configure your webserver (Apache?) to run PERL CGI scripts.
* Copy the code (e.g. the ```RE7``` directory) to someplace the webserver can access it.
* Ensure that the PERL modules listed above are installed and working.
* Visit the start page (probably something like http://localhost/~jblowe/RE7/frameset.pl)

## Notes

* Only the POLYNESIAN d and DEMO93 (i.e. a small TGTM dataset) are currently working.
