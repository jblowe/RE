import read
import sys

# insert list of language names here
languages = []
table = read.read_csv_correspondences(sys.argv[0], 'placeholder', languages)

RE.Parameters(table,
              RE.SyllableCanon({}, 'placeholder', []),
              'placeholder', None).serialize('converted.xml')
