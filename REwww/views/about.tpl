<p>
One of the inspirations for this effort is work done in the 1990's and published as:
</p>
<p>
Lowe, John and Martine Mazaudon. <i>The reconstruction engine: a computer implementation of the comparative method</i>, Association for
Computational Linguistics Special Issue in Computational Phonology 20.3 (September 1994) pp. 381-417.
</p>
<p>
"The Reconstruction
Engine (RE) models the comparative method for establishing genetic
affiliation among a group of languages.  The program is a research tool
designed to aid the linguist in evaluating specific hypotheses, by calculating
the consequences of a set of postulated sound changes (proposed by the
linguist) on complete lexicons of several languages.  It divides the lexicons
into a phonologically regular part, and a part which deviates from the sound
laws.  RE is bi-directional: given words in modern languages, it can propose
cognate sets (with reconstructions); given reconstructions, it can project the
modern forms which would result from regular changes.  RE operates either
interactively, allowing word-by-word evaluation of hypothesized sound changes
and semantic shifts, or in a 'batch' mode, processing entire multilingual
lexicons <i>en masse</i>."
</p>
<p>HTML: <a href="http://linguistics.berkeley.edu/~jblowe/REWWW/RE.html">http://linguistics.berkeley.edu/~jblowe/REWWW/RE.html</a></p>
<p>PDF: <a href="https://dl.acm.org/citation.cfm?id=204920">https://dl.acm.org/citation.cfm?id=204920</a></p>
<p>
RE was first written as a SPITBOL program in the late 1980's, inspired by
an initial experiment and code written by <a href="http://www.montler.net/lexware/">Robert Hsu</a>.
Later attempts to
re-write the program in more current frameworks (i.e. PERL and Java) date from the mid-90's 
to the early 21st century.
</p>
<p>
The current implementation is written in Python, and this web interface uses the
<a href="https://bottlepy.org">Bottle</a>
web microframework and the
<a href="https://getbootstrap.com">Bootstrap</a> CSS framework.
</p>
<p>
The code and data are available in <a href="https://github.com/jblowe/RE">GitHub</a>.
</p>