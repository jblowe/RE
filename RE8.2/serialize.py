import xml.etree.ElementTree as ET

def serialize_correspondence_file(filename, parameters):
    root = ET.Element('tableOfCorr')
    params = ET.SubElement(root, 'parameters')
    syllable_canon = parameters.syllable_canon
    for cover, values in syllable_canon.sound_classes.items():
        ET.SubElement(params, 'class', name=cover, value=values)
    ET.SubElement(params, 'canon', name='syllabe',
                  value=syllable_canon.regex.pattern)
    for correspondence in parameters.table.correspondences:
        corr = ET.SubElement(root, 'corr', num=correspondence.id)
        ET.SubElement(corr, 'proto',
                      contextL=correspondence.context[0] or '',
                      contextR=correspondence.context[1] or '',
                      syll=correspondence.syllable_type).text = \
            correspondence.proto_form
        for language, forms in correspondence.daughter_forms.items():
            modern = ET.SubElement(corr, 'modern', dialecte=language)
            for form in forms:
                ET.SubElement(modern, 'seg').text = form
    ET.ElementTree(root).write(filename, encoding='UTF-8')
