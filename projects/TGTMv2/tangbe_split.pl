$T="⁰¹²³⁴⁵⁶'";
$V="aeioøuɔəɛɨʌʔʱː̃";
$C="bcdɖghjklmnŋɲpqrsʃʈtvwxyz";

/([⁰¹²³⁴⁵⁶']+)([bcdɖghjklmnŋɲpqrsʃʈtvwxyz]+)?([aeioøuɔəɛɨʌʔʱː̃]+)([bcdɖghjklmnŋɲpqrsʃʈtvwxyz]+)/ && print "syll\t$1\t$2\t$3\t$4\n";
# s/\b$T+$C+$V+$C/\1\t\2\t\3\t/;

