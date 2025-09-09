use strict;

our $has_ngl;

sub extract_keyterm {
    my ($gl) = @_;
    $gl =~ s/^to //i; # get rid of initial 'to '
    $gl =~ s/\|.*//;  # get rid of everything after vertical bar
    $gl =~ s/ +\(+(.*?)\)+$//g; # get rid of text in parenthesis
    $gl =~ s/ *\&lt;(.*)\&gt;//; # get rid of text in angle brackets
    return $gl;
}

sub ngl {
    my ($gl) = @_;
    my @terms;
    $gl =~ s/ *\(+(.*?)\)+ *//g; # get rid of text in parenthesis
    my @gls = split /, +/, $gl;
    for my $glx (@gls) {
        $glx =~ s/\*//g;
        push(@terms, extract_keyterm($glx));
        # handle plurals encoded in lexware
        if ($glx =~ /\|e?s\b/) {
            my $glx2 = $glx;
            $glx2 =~ s/\|(e?s)\b/\1/;
            push(@terms, extract_keyterm($glx2));
        }
    }
    return @terms;
}

s/\-<.hw>/<\/hw>/;
s#<hw>( *[=\-])#<prefix>\1</prefix><hw>#;
s#<hw>(.*?)( *[=\-].*?)</hw>#<hw>\1</hw><suffix>\2</suffix>#;

if (m#<entry#) {
    $has_ngl = 0;
}

if (m#<ngl>(.*?)</ngl>#) {
    $has_ngl = 1;
}

if (m#<gl>(.*?)</gl># && $has_ngl eq 0) {
    my $gl = $1;
    my @terms = ngl($gl);
    if (join('', @terms) ne $gl) {
        foreach my $term (@terms) {
            if ($term) {
                $_ .= "    <ngl>$term</ngl>\n";
            }
        }
    }
}
