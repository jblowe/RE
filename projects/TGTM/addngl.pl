use strict;

sub extract_keyterm {
    my ($gl) = @_;
    $gl =~ s/^to //i; # get rid of initial 'to '
    $gl =~ s/\|.*//;  # get rid of everything after vertical bar
    $gl =~ s/ +\((.*?)\)$//; # get rid of text in parenthesis
    $gl =~ s/ *\&lt;(.*)\&gt;//; # get rid of text in angle brackets
    return $gl;
}

sub ngl {
    my ($gl) = @_;
    my @terms;
    $gl =~ s/ *\((.*?)\) *//; # get rid of text in parenthesis
    my @gls = split /, /, $gl;
    for my $glx (@gls) {
        if ($glx =~ m/\*/) {
            while ($glx =~ s/^.*?\*(.+?)\b//) {
                push(@terms, extract_keyterm($1));
            }
        }
        else {
            push(@terms, extract_keyterm($glx));
        }
    }
    return @terms;
}

s/\-<.hw>/<\/hw>/;
s#<hw>( *[=\-])#<prefix>\1</prefix><hw>#;
s#<hw>(.*?)( *[=\-].*?)</hw>#<hw>\1</hw><suffix>\2</suffix>#;

if (m#<gl>(.*?)</gl>#) {
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
