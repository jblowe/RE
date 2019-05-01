#!/usr/bin/perl
# make a release (i.e. a named sequential tag..)
# ./make-release.pl <tag-prefix> "commit comment"
# e.g. ./make-release.pl "a few fixes and enhancements"

use strict;

if (`git status -s | wc -l` != 0) {
    print "repo needs to clean: no uncommitted changes or untracked files!\n\n";
    print system('git status -s');
    die "\nexiting...\n";
}

if (`git fetch --dry-run 2>&1 | wc -l` != 0) {
    print "repo is not up to date! please update it (e.g. git pull)!\n\n";
    print system('git fetch --dry-run');
    die "\nexiting...\n";
}

if (scalar @ARGV != 1)  {
  die "Need just one arguments: \"comment (can be empty)\"\n";
}

my ($MSG) = @ARGV;

# or die("needs to be executed within the RE repo!");
    
my @tags = `git tag --list`;
if ($#tags < 0) {
   print "can't find any tags\n";
   exit(1);
}

my (@parts, $revision, $version_number, $last_revision, $last_version_number, $revision);

foreach my $tag (sort @tags) {
    @parts = split(/\./, $tag);
    $revision = pop(@parts);
    $version_number = join('.', @parts);

    if ($revision > $last_revision) {
        $last_revision = $revision;
        $last_version_number = $version_number;
    }
}

$last_revision++;
my $version_number = "$last_version_number.$last_revision";
my $tag_message = "Release tag for $version_number.";
$tag_message .= ' ' . $MSG if $MSG;

print "verifying code is current and using master branch...\n";
#system "git pull -v";
#system "git checkout master";
print "updating CHANGELOG.txt...\n";
system "echo 'CHANGELOG for RE' > CHANGELOG.txt";
system "echo  >> CHANGELOG.txt";
system "echo 'OK, it is not a *real* change log, but a list of changes resulting from git log' >> CHANGELOG.txt";
system "echo 'with some human annotation after the fact.' >> CHANGELOG.txt";
system "echo  >> CHANGELOG.txt";
system "echo 'This is version $version_number' >> CHANGELOG.txt";
#system "echo '$version_number' > VERSION";
system "date >> CHANGELOG.txt ; echo >> CHANGELOG.txt";
system "git log --pretty=format:\"%h%x09%an%x09%ad%x09%s\" >> CHANGELOG.txt";
system "cp CHANGELOG.txt ..; rm CHANGELOG.txt";
#system "git commit -a -m 'revise change log and VERSION file for version $version_number'";
#system "git add ../CHANGELOG.txt"; #system "git commit -m 'revised change log for version $version_number'";
#system "git push -v" ;
print  "git tag -a $version_number -m '$tag_message'\n";
#system "git tag -a $version_number -m '$tag_message'";
#system "git push --tags";

