import os, time

# nb: we are trying to get the directory above the directory this file is in
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_version():
    try:
        with os.popen("/usr/bin/git describe --always") as f:
            version = f.read().strip()
        if version == '':  # try alternate location for git (this is the usual Mac location)
            with os.popen("/usr/local/bin/git describe --always") as f:
                version = f.read().strip()
    except:
        version = 'Unknown'
    return version


def add_time_and_version():
    return 'code and data version: %s, updated: %s' % (get_version(), time.strftime("%b %d %Y %H:%M:%S", time.localtime()))


def data_files(project):
    project_dir = os.path.join(BASE_DIR, 'projects', project)
    filelist = [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
    # filelist = [f for f in filelist if '.xml' in f]
    to_display = []
    for type in 'data correspondences parameters mel sets'.split(' '):
        to_display.append((type, [f for f in filelist if f'{type}.xml' in f]))
    return to_display, BASE_DIR


def file_content(file_path):
    # file_path contains the project and filename, e.g. TGTM/TGTM.mel.xml
    project = file_path.split('/')[0]
    file_path = os.path.join(BASE_DIR, 'projects', file_path)
    xslt_path = determine_file_type(file_path)
    xslt_path = os.path.join(BASE_DIR, 'styles', xslt_path)
    try:
        data = xml2html(file_path, xslt_path)
    except:
        data = '<span style="color: red">Problem handling this file, sorry!</span>'
    # f = open(file_path,'r')
    # data = f.read()
    # f.close()
    return data, project


def xml2html(xml_filename, xsl_filename):
    import lxml.etree as ET

    dom = ET.parse(xml_filename)
    xslt = ET.parse(xsl_filename)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return newdom


def determine_file_type(file_path):
    if 'correspondences.xml' in file_path:
        return 'toc2html.xsl'
    elif 'data.xml' in file_path:
        return 'lexicon2html.xsl'
    elif 'parameters.xml' in file_path:
        return 'params2html.xsl'
    elif 'sets.xml' in file_path:
        return 'sets2html.xsl'
    elif 'mel.xml' in file_path:
        return 'mel2html.xsl'


VERSION = get_version()
