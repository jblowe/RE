# RE
The Reconstruction Engine, a computer implementation of the comparative method

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

* Only the Polynesiand and DEMO93 (i.e. a small TGTM dataset) are currently working.
