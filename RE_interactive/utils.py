import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def data_files(project):
    project_dir = os.path.join(BASE_DIR, 'RE7', 'DATA', project)
    filelist = [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
    #filelist = [f for f in filelist if '.xml' in f]
    to_display = []
    for type in 'data correspondences parameters sets'.split(' '):
        to_display.append((type, [f for f in filelist if f'{type}.xml' in f]))
    return to_display, BASE_DIR


def file_content(filename):
    file_path = os.path.join(BASE_DIR, 'RE7', 'DATA', filename)
    xslt_path = determine_file_type(file_path)
    xslt_path = os.path.join(BASE_DIR, 'RE7', 'styles', xslt_path)
    data = xml2html(file_path, xslt_path)
    project = filename.split('/')[0]
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
