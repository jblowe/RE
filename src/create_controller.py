import solr
import sys

try:
    core = sys.argv[1]
    host = sys.argv[2]
    query_template = sys.argv[3]
except:
    print('syntax: python %s solar_core hostname query_template' % sys.argv[0])
    print()
    print('e.g     python %s pahma-public https://10.99.1.11 "*:*"' % sys.argv[0])
    print()
    print('or (using a template with a filler and input from stdin):')
    print()
    print('        python %s pahma-public http://localhost:8983 \'objmusno_txt:"%%s"\' < list_of_musnos.txt > found.txt' % sys.argv[0])
    print()
    print('i.e. will read a list of template fillers from stdin, write fillers and counts to stdout')
    sys.exit(1)

try:
    # create a connection to a solr server
    s = solr.SolrConnection(url='%s/solr/%s' % (host, core))
except:
    print('could not open connection to "%s/solr/%s" % (host,core)')

# if a template filler query was specified, try to read stdin for fillers
if ('%s' in query_template):
    for query in sys.stdin.readlines():
        # fill in search and try it.
        filled_in_query = 'something bad happened'
        try:
            filled_in_query = query_template % query.rstrip()
            response = s.query(filled_in_query, rows=0)
            print('%s\t%s' % (filled_in_query + '&wt=csv', response._numFound))
        except:
            print('%s\t%s' % (filled_in_query, "query failed"))

else:
    # just do the one search
    try:
        raw = s.raw_query(q=query_template, wt='csv', rows='00')
        fields = sorted(str(raw).split(','))
        response = s.query(query_template, rows=0)
        print('%s, records found: %s' % (core,response._numFound))

        bl_config = {s: [] for s in 'facet list show sort search'.split(' ')}

        for i, bl_field in enumerate(bl_config):
            for field in fields:
                solr_field = field
                label_field = field.split('_')[0].capitalize()
                if bl_field == 'facet':
                    limit = ', limit: true'
                else:
                    limit = ''
                if '_dt' in solr_field:
                    bl_config[bl_field].append('''
                        config.add_facet_field "%s", :label => "%s", :partial => "blacklight_range_limit/range_limit_panel", :range => {
                              :input_label_range_begin => "from year",
                              :input_label_range_end => "to year"
                        }
                        ''' % (solr_field, label_field))
                else:
                    if bl_field == 'search':
                        bl_config[bl_field].append([solr_field, label_field])
                    else:
                        bl_config[bl_field].append("config.add_%s_field '%s', label: '%s'%s" % (bl_field, solr_field, label_field, limit))

        for section in bl_config:
            print('\n# %s' % section)
            if section == 'search':
                print(
                    "    config.add_search_field 'text', label: 'Any field'")
                print(bl_config[section])
                print('''
                  ].each do |search_field|
                  config.add_search_field(search_field[0]) do |field|
                    field.label = search_field[1]
                    #field.solr_parameters = { :'spellcheck.dictionary' => search_field[0] }
                    field.solr_parameters = {
                      qf: search_field[0],
                      pf: search_field[0],
                      op: 'AND'
                    }
                  end
                end
            ''')
                continue

            for c in bl_config[section]:
                print(c)

        print('''
              end
            end
            ''')

    except:
        raise
        print("could not access %s." % core)
