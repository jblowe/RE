import toolbox
import sys

filename = sys.argv[1]

for mkr, text in toolbox.read_toolbox_file(open(filename)):
    if text is not None:
        if mkr == '\\pnv':
            print('')
        print('Marker: {0!r:<8}Text: {1!r}'.format(mkr, text))
