import read
import RE
import sys

base_dir = "../RE7/DATA"
# lexicons and parameters
if len(sys.argv) != 4:
    print('need project and 2 parameter sets to compare results of')
    sys.exit(1)
try:
    project = sys.argv[1]
    parameters1 = sys.argv[2]
    parameters2 = sys.argv[3]
    try:
        run = sys.argv[4]
    except:
        run = 'default'

except:
    print('no project specified. Try "DEMO93" if you like')

settings1 = read.read_settings_file(f'{base_dir}/{project}/{parameters1}')
settings2 = read.read_settings_file(f'{base_dir}/{project}/{parameters2}')

B1 = RE.batch_all_upstream(settings1)
B2 = RE.batch_all_upstream(settings2)
#print_sets(B)
RE.analyze_sets(B1, B2, f'{base_dir}/{project}/{project}.{run}.analysis.txt')
