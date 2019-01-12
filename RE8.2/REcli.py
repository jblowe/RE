import read
import RE
import sys

base_dir = "../RE7/DATA"
# lexicons and parameters
try:
    project = sys.argv[1]
    try:
        settings_type = sys.argv[2]
    except:
        settings_type = 'default'
    try:
        run = sys.argv[3]
    except:
        run = 'default'
except:
    print('no project specified. Try "DEMO93" if you like')
    sys.exit(1)

settings = read.read_settings_file(f'{base_dir}/{project}/{project}.{settings_type}.parameters.xml')

B = RE.batch_all_upstream(settings)
#print_sets(B)
RE.dump_keys(B, f'{base_dir}/{project}/{project}.{run}.keys.txt')
RE.dump_sets(B, f'{base_dir}/{project}/{project}.{run}.sets.txt')
