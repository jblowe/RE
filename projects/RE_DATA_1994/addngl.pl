use strict;

sub extract_keyterm {
    my ($gl) = @_;
    $gl =~ s/^to //i;
    $gl =~ s/\|.*//;
    $gl =~ s/ +\((.*?)\)$//;
    $gl =~ s/\)$//;
    $gl =~ s/ *\&lt;(.*)\&gt;//;
    return $gl;
}

sub ngl {
    my ($gl) = @_;
    my @terms;
    my @gls = split /, /, $gl;
    for my $glx (@gls) {
        if ($glx =~ m/\*/) {
            while ($glx =~ s/^.*?\*([^\*]+)//) {
                push(@terms, extract_keyterm($1));
            }
        }
        else {
            push(@terms, extract_keyterm($glx));
        }
    }
    return @terms;
}

if (m#<gl>(.*?)</gl>#) {
    my $gl = $1;
    my @terms = ngl($gl);
    if (join('', @terms) ne $gl) {
        foreach my $term (@terms) {
            $_ .= "    <ngl>$term</ngl>\n";
        }
    }
}
