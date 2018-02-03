#!/usr/bin/perl
####!/opt/local/bin/perl
####!/usr/local/bin/perl
#use strict;

use CGI qw(-utf8);
use CGI::Carp qw/fatalsToBrowser/;
require "RE2.pl" ;                     # RE-specific subs
require "RErules.pl";
require "Upstream.pl" ;

my $query = new CGI;

binmode STDOUT, ":utf8";

print $query->header(-charset => 'UTF-8');
my $version = "v7.0 14 Jun 2014" ;
my $TITLE = "Reconstruction Engine v7.0";
my $HEADER="T H E &nbsp; &nbsp; R E C O N S T R U C T I O N&nbsp; &nbsp; &nbsp;E N G I N E";

# We use the path information to distinguish between calls
# to the script to:
# (1) create the frameset
# (2) create the query form
# (3) create the query response

my $path_info = $query->path_info;
my $script_name = $query->script_name ;

# If no path information is provided, then we create 
# a side-by-side frame set
if (!$path_info) {
    &print_frameset;
    #exit 0;
}
else {
  # If we get here, then we either create the query form
  # or we create the response.
  #&print_html_header;
  &print_test     if $path_info=~/test/;
  &print_header   if $path_info=~/header/;
  &print_query    if $path_info=~/query/;
  &print_response if $path_info=~/response/;
  &print_resp2    if $path_info=~/second/;
  #&print_end;
}

# Create the frameset
sub print_frameset {
  $script_name = $query->script_name;
  #print $query->start_html($TITLE);
  print <<EOF;
<html>
<frameset rows="48px,*" frameborder="no" framespacing="0px">
<frame src="$script_name/header" scrolling="no" marginheight="0" marginwidth="0">
<frameset cols='200px,*' frameborder="no" framespacing="0px" >
<frame src="$script_name/query" name="query" noresize="false" scrolling="no" marginheight="0" marginwidth="0">
<frame src="$script_name/response" name="response" marginheight="0" marginwidth="10" scrolling="auto">
</frameset>
</frameset>
</html>
EOF
  ;

  $x = <<EOF2
<frameset cols="20%,80%">
<frame src="$script_name/query" name="query">
<frame src="$script_name/response" name="response">
</frameset>
EOF2
  ;
  #print $query->end_html();
}

sub print_test {
    #print $query->start_html($TITLE);
    print "$path_info eq $script_name<br>";
    foreach $k (keys %{$query}) {
      print $k . " " . $query{$k} . "<br>"; 
    }
    print $query->param , "<br>";

}

sub print_end {
    print '<P><hr><span style="font-size:8pt">' . scalar localtime . '</span><hr>';
    print $query->end_html;
}


sub print_header {
  print '<div style="background-color: lightgray; height:45px;padding: 10px;">';
  print '<div style="float: left;"><span style="font-weight: bold; vertical-align:top">' . $HEADER . '</span></div>';
  print '<div style="font-size:8pt;float: right;"><span>' . $version . "<br/>" . scalar localtime . '</span></div>';
  print '</div>';
}

sub print_query {
  #$script_name = $query->script_name;
  print '<div style="background-color: lightblue;padding: 10px;">';

  print '<P><a href="../DOCS/REintro.html" target="response">Documentation</a>';
  
  print $query->start_form(-action=>"$script_name/response",-TARGET=>"response");
  
  my @projects = qw(DEMO93 TGTM TGTM2/TGTM INDOEUROPEAN POLYNESIAN LOLOISH/NYI LOLOISH/SYI) ;

  #print join "<br/>",@projects;

  
  print "<P><EM>Select a project to work on:</EM><BR>";
  print $query->popup_menu(-name=>'project',
  			   -values=> [ @projects ],
  			  );

  print "<P><EM>Parameter set to use:</EM><BR>";
  @parameterfiles = [ qw(default simplified leadingedge) ];
  print $query->popup_menu(-name=>'parameters',
			   -values=> @parameterfiles 
				    );
  
  print "<P><EM>Experiment name (i.e. name for this run):</EM><BR>";
  print $query->textfield(-name =>'run', -size=>20, -default=> 'run1');

  print "<P><EM>Number to process:</EM><BR>";
  print $query->textfield(-name =>'limit', -size=>10, -default=> '0');


  print "<P><EM>Level of Detail:</EM><BR>";
  print $query->popup_menu(-name=>'detail',
			   -values=> ( [1 .. 5] ),
			   -labels=>{
				     1=>'Minimum: statistics only',
				     2=>'Rules, wordforms, parameters',
				     3=>'+ reconstructions (compact)',
				     4=>'+ reconstruction and set details',
				     5=>'Maximum'
				    }
				    );
  
  print "<P><EM>Activity:</EM><BR>";
  my @cmds = ("Interactive Upstream/Downstream","Batch Upstream","Review SETS","Review RULES","Review CORRESPONDENCES","Review PARAMETERS","Review PREVIOUS RUN STATISTICS","Upload" );
  for (@cmds) { print $query->submit('Action',$_),"<BR>" } ;
  
  print "<P>",$query->reset;
  print $query->end_form;
  print '</div>';
}

sub print_response {

    unless ($query->param) {
	print "<b>Some Intro Material here...</b>";
	return;
    }

    print <<HERE
<html><head>
    <link rel="stylesheet" type="text/css" href="../css/tablesorter.css"/>
    <script type="text/javascript" src="../js/jquery-1.10.0.min.js"></script>
    <script type="text/javascript" src="../js/jquery-ui-1.10.3.custom.min.js"></script>
    <script type="text/javascript" src="../js/jquery.tablesorter.js"></script>
</head>
HERE
;

    my ($project) = $query->param("project");
    my ($run)     = $query->param("run");
    my ($limit)   = $query->param("limit");
    $test    = $query->param("detail");
    my ($action)  = $query->param("Action");
    $fmt       = "h" ; 
    my $prms      = "default";

    REwww($project,$prms,$run,$fmt,$limit,$action);
    #REwww($project,$prms,$run,$fmt,$limit,$action,$test);

    &print_end;
}
sub print_resp2 {
    #print "<H2>Frameset Result2</H2>\n";

    unless ($query->param) {
	print "<b>No query submitted yet.</b>";
	return;
    }
    my ($file)   = $query->param("file");
    my ($action) = $query->param("Action");
    $fmt      = "h" ; 
    
    $file && REwww($file,$action);

    my $term;
    my ($lgabbr) = $query->param("lgabbr");
    my ($corr)   = $query->param("corrcol");
    my ($rule)   = $query->param("rulecol");
    my ($val)    = $query->param("val");
    my ($act)    = $query->param("Act");
    if ($act =~ /corr/) {
	$term = $corr ;
    }
    elsif ($act =~ /element/ ) {
	$term = $rule ;
    }
    elsif ($act =~ /rule/ ) {
	$term = $lgabbr ;
    }
    if ($act) {
	&$act() ;
    }   
}


#jacobson le 26 mars 2001
sub do_downstream {
    my ($corrfile, $paramfile) = @_ ;
    
    print "<h4>Upstream $corrfile $paramfile</h4>";
    print $query->start_form(-target=>'result',
			     -method=>POST,
			     -action=>'fn.pl'
			     );
    $query->param('what', 'do_upstream');			#pour changer la valeur
    print $query->hidden(-name=>'what', -value=>'do_upstream');
    print $query->hidden(-name=>'corrfile', -default=>$corrfile);
    print $query->hidden(-name=>'paramfile', -default=>$paramfile);
    $fmt = "h" ;
    &initializePrj($corrfile, $paramfile);
    print "<script language=\"javascript\" src=\"/RE/clavier.js\"></script>";
    print &clavier();
    print "<table>\n";

    foreach $lgabbr (@lgnames) {
	print $tr,$td,$lgabbr,$td,
	$query->textfield(-name =>$lgabbr, -size=>15, -style=>$UFONTS, -onFocus=>'myFocus(this)');
    }
    print "</table>\n<P>";
    print "<b>Canon</b><br>",
    $query->textfield(-name =>'canon', -size=>25, -default=>$syllcanon);
    print "<P>";
    print $query->submit('run1','Intersection') . "<BR>";
    print $query->submit('run2','Summary') . "<BR>";
    print $query->submit('run3','Analysis');
    print $query->end_form();
}

sub do_upstream {
    ($dir,$project,$prms,$run,$fmt,$limit) = @_;
    print "<h4>Upstream</h4>";
    #print $query->start_form(-target=>'result');
    print $query->start_form(
			     -target=>'response',
			     -method=>POST,
			     #-action=>'reconstruct'
			     );
    print $query->hidden(-name=>'dir', -default=>$dir);
    print $query->hidden(-name=>'project', -default=>$project);
    print $query->hidden(-name=>'prms', -default=>$prms);
    print $query->hidden(-name=>'run', -default=>$run);


    $fmt = "x" ;
    initializePrj($dir,$project,$prms,$run,$fmt,'',$limit) || die "could not initialize downstream parameters";
    $fmt = "h" ;

    print "<table>\n";
    print SGMLtag(qw(tr),'<th>' . join('<th>',qw(Language Form)));
   
    foreach $lgabbr (@lgnames) {
      print  SGMLtag(qw(tr),"<td>$lgabbr" . "<td>" . $query->textfield(-name =>$lgabbr, -size=>15)) ;
    }
    print "</table>\n<P>";
    print $query->submit('Action','Compute') . "<BR>";
    print $query->submit('Action','Demonstrate!') . "<BR>";
    print $query->submit('Action','Details!');
    print $query->end_form();
}
sub reconstruct {
    ($dir,$project,$prms,$run,$fmt,$limit) = @_;
    do_upstream($dir,$project,$prms,$run,$fmt,$limit);
    # get lgs...
    $itemid = 0;
    for $lgabbr (@lgnames) {
      $itemid++;
      $id++;
      $wd =$query->param($lgabbr);
      $gls = '';
      #push @{ $lex{$lgabbr}{$wd}  }, "$id.$itemid" ;
      $arts{"$id.$itemid"} = [ $lgabbr,$wd,$gls ];
      my %wds ;
      $wds{$wd}  = "$id.$itemid" ;
      #print "<li>$lgabbr: $wd :: $id.$itemid</li>";
      #print "<br>calling setuprules";
      if ($wd) {
      $test = 1;
      SetupRules($lgabbr) ;
      $test = 7;
      CreateRcns($lgabbr,%wds) ;				#create/update list of recons
      Statistics(qw(LEXICON)) ;				        #add things up
      }
    }
    Statistics(qw(DATA)) ;				        #first summarize counts
    CreateSets() ;
    print "<h4>$NSets set(s) saved (of $NRawSets).</h4>";
    $test = 7;
    DumpSets(@sets);
    print "<h4>Overlapping sets</h4>";
    Multi() ;                        
}
#######################################################################
# Get ready to run: open input file, read preamble and rules
#######################################################################

sub REwww {
  
  ($project,$prms,$run,$fmt,$limit,$ccmd) = @_ ;

  $limit = $limit + 0;

  my $file;
  my @lgnames;
  my @header;
  my @colnames;
  
  #$prms      = "params";
  #$prj       = $prj;
  #out        = $out;
  my $dir = `pwd`;
  chomp $dir;
  if ($project =~ /\//) { # if the project has a slash in it...
    my ($d,$p) = split '/',$project;
    $dir = "$dir/DATA/$d";
    $project = $p;
  }
  else {
    $dir = "$dir/DATA/$project";
  }

  print "<h2>$ccmd</h2>\n";

  #print $file,$ccmd;
  # -o run2 -x DATA/DEMO93  -p params -d DEMO93 -f xxx -t 3
  
#######################################################################
# process command
#######################################################################
  if    ($ccmd =~ /Compute/) {
    reconstruct($dir,$project,$prms,$run,$fmt,$limit);
  }
  elsif ($ccmd =~ /Batch Upstream/) {

    #my $limit     = 99999 ; #number of forms to process in each lex
    #print "starting ...<br>";
    &Upstream($dir,$project,$prms,$run,$fmt,$limit) ;
    #print "done ...<br>";
    print "<h3>$project.$run.log.txt</h3>\n";
    close LOGFILE;
    open LOGFILE,"<$dir/$project.$run.log.txt"  || die "can't open RE log file '$project.$run.log.txt'!";
    binmode LOGFILE, ":utf8";
    print '<PRE>';
    my @L = <LOGFILE>;
    print @L;
    print '</PRE>';
    
  }
  elsif ($ccmd =~ /Interactive Upstream\/Downstream/) {
    do_upstream($dir,$project,$prms,$run,$fmt,$limit);
  }
  elsif ($ccmd =~ /Downstream/) {
    do_downstream($dir,$project,$prms,$run,$fmt,$limit);
  }
  elsif ($ccmd =~ /Review SETS/) {
    print "<h3>$project.$run.sets.xml</h3><hr/>";
    my $cmd = "/usr/bin/xsltproc styles/sets2html.xsl $dir/$project.$run.sets.xml > $dir/$project.$run.sets.html";
    #print $cmd ."<br>";
    $result = system($cmd) & 127 ;
    open SETS,"< $dir/$project.$run.sets.html"  || die "can't open RE sets file '$project.$run.sets.html'!";
    binmode SETS, ":utf8";
    my @L = <SETS>;
    print @L;
    close SETS;
    system("rm $dir/$project.$run.sets.html");
    #print $query->redirect("../DATA/$project/$project.$run.sets.html");
  }
  elsif ($ccmd =~ /Review PREVIOUS RUN STATISTICS/) {
    initializePrj($dir,$project,$prms,$run,$fmt,'',$limit) || return;
    print "<h3>$project.$run.log.txt</h3><hr/>";
    open RUN,"< $dir/$project.$run.log.txt"  || die "can't open RE sets file '$project.$run.log.txt'!";
    binmode RUN, ":utf8";
    print '<PRE>';
    my @L = <RUN>;
    print @L;
    print '</PRE>';
    close RUN;
  }
  elsif ($ccmd =~ /Review RULES/) {
    initializePrj($dir,$project,$prms,$run,'quiet','',$limit) || die "could not initialize!";
    &HTMLRules();
  }
  elsif ($ccmd =~ /Review CORRESPONDENCES/) {
    initializePrj($dir,$project,$prms,$run,$fmt,'',$limit) ||  die "could not initialize!";
    &HTMLCorrs();
  }
  elsif ($ccmd =~ /Review PARAMETERS/) {
    initializePrj($dir,$project,$prms,$run,$fmt,'',$limit) ||  die "could not initialize!";
    &HTMLParms($dir,$project,$prms,$run,$fmt,$limit) ;
  }
  elsif ($ccmd =~ /Search RULES/) {
    print 
      $query->h4("Review and test rules for $file"),
      $query->h5($version) ,
      $query->start_form,
      $query->br;
    
    print 
      "<TABLE BORDER=1>",
	"<TR>",
	    "<TD>",
	    $query->submit('Act',qw(rule)),"<BR>\n",
	    "<TD>",
	    "Language to which rules apply?",
	    $query->br,
	    $query->popup_menu(-name=>'lgabbr',
		       -values=> [ @lgnames ],
			       ),
	    "<TD ROWSPAN=4>",
	    "value to search for?",
	    $query->br,
	    $query->textfield("val"),
	    "<TR>",
	    "<TD>",
	    $query->submit('Act',qw(corr)),"<BR>\n",
	    "<TD>",
	    "Correspondence column?",
	    $query->br,
	    $query->popup_menu(-name=>'corrcol',
		       -values=> [ @header ],
			       ),
	    "<TR>",
	    "<TD>",
	    $query->submit('Act',qw(element)),"<BR>\n",
	    "<TD>",
	    "Rule column to search?",
	    $query->br,
	    $query->popup_menu(-name=>'rulecol',
		       -values=> [ @colnames ],
			       ),
	    "<TR>",
	    "<TD>",
	    $query->reset,
	    "</TABLE>",
	    $query->endform,
	    $query->hr;
    }
    else  {
	print "$ccmd: not recognized.\n" ;
    }
}
