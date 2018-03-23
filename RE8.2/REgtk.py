import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib
import RE
import read
import threading
import sys
import serialize
import os

class WrappedTextBuffer():
    def __init__(self, buffer):
        self.buffer = buffer
    def write(self, string):
        Gdk.threads_enter()
        self.buffer.insert(self.buffer.get_end_iter(),
                           string, len(string))
        Gdk.threads_leave()

def make_correspondence_row(correspondence, names):
    return [correspondence.id,
            RE.context_as_string(correspondence.context),
            ','.join(correspondence.syllable_types),
            correspondence.proto_form] + \
            [', '.join(v)
             for v in (correspondence.daughter_forms.get(name)
                       for name in names)]

def make_correspondence_store(table):
    store = Gtk.ListStore(*([str, str, str, str] +
                            len(table.daughter_languages) * [str]))
    for c in table.correspondences:
        store.append(make_correspondence_row(c, table.daughter_languages))
    return store

def make_correspondence_view(table):
    store = make_correspondence_store(table)
    def key_press_handler(view, event):
        if Gdk.keyval_name(event.keyval) == 'Tab':
            path, column = view.get_cursor()
            columns = view.get_columns()
            index = columns.index(column)
            next_column = columns[index + 1
                                  if index + 1 < len(columns)
                                  else 0]
            # timeout needed to save cell contents
            GLib.timeout_add(50, view.set_cursor,
                             path, next_column, True)
    treeview = Gtk.TreeView.new_with_model(store)
    treeview.connect('key-press-event', key_press_handler)
    def store_edit_text(i):
        def f(widget, path, text):
            store[path][i] = text
        return f
    for i, column_title in enumerate(['ID', 'Context', 'Syllable Type', '*']
                                     + table.daughter_languages):
        cell = Gtk.CellRendererText()
        cell.set_property('editable', True)
        cell.connect('edited', store_edit_text(i))
        column = Gtk.TreeViewColumn(column_title, cell, text=i)
        column.set_sort_column_id(i)
        treeview.append_column(column)
    return treeview, store

def make_entry(text):
    entry = Gtk.Entry()
    entry.set_text(text)
    return entry

def make_syllable_canon_widget(syllable_canon):
    grid = Gtk.Grid()
    grid.attach(Gtk.Label('Syllable regex:'), 0, 0, 1, 1)
    grid.attach(make_entry(syllable_canon.regex.pattern), 1, 0, 1, 1)
    grid.attach(Gtk.Label('Sound classes:'), 0, 1, 1, 1)
    grid.attach(make_entry(str(syllable_canon.sound_classes)), 1, 1, 1, 1)
    grid.attach(Gtk.Label('Supra-segmentals'), 0, 2, 1, 1)
    grid.attach(make_entry(','.join(syllable_canon.supra_segmentals)),
                1, 2, 1, 1)
    return grid

def read_syllable_canon_from_widget(widget):
    children = widget.get_children()
    return RE.SyllableCanon(
        eval(children[2].get_text()),
        children[4].get_text(),
        [x.strip() for x in children[0].get_text().split(',')])

def make_lexicon_widget(words):
    store = Gtk.ListStore(str, str)
    for form in words:
        store.append([form.glyphs, form.gloss])
    view = Gtk.TreeView.new_with_model(store)
    for i, column_title in enumerate(['Form', 'Gloss']):
        cell = Gtk.CellRendererText()
        cell.set_property('editable', True)
        column = Gtk.TreeViewColumn(column_title, cell, text=i)
        column.set_sort_column_id(i)
        view.append_column(column)
    pane = Gtk.ScrolledWindow()
    pane.set_vexpand(True)
    pane.add(view)
    return pane

def make_lexicons_widget(lexicons):
    notebook = Gtk.Notebook()
    for lexicon in lexicons:
        notebook.append_page(make_lexicon_widget(lexicon.forms),
                             Gtk.Label(lexicon.language))
    return notebook

def read_table_from_widget(widget):
    view = widget.get_children()[0].get_children()[0]
    model = view.get_model()
    names = [col.get_title() for col in view.get_columns()][4:]
    table = RE.TableOfCorrespondences('', names)
    for row in model:
        table.add_correspondence(
            RE.Correspondence(
                row[0],
                ((None, None) if row[1] == '' else
                 tuple(None if x == '' else
                       [y.strip() for y in x.split(',')]
                       for x in row[1].split('_'))),
                [x.strip() for x in row[2].split(',')], row[3],
                dict(zip(names, ([x.strip() for x in token.split(',')]
                                 for token in row[4:])))))
    return table

def make_correspondence_widget(table):
    pane = Gtk.ScrolledWindow()
    pane.set_vexpand(True)
    view, store = make_correspondence_view(table)
    pane.add(view)

    def add_button_clicked(widget):
        columns = view.get_columns()
        row = store.append(len(columns) * [''])
        path = store.get_path(row)
        view.set_cursor(path, columns[0], True)

    def delete_button_clicked(widget):
        store.remove(store.get_iter(view.get_cursor()[0]))

    add_button = Gtk.Button(label='Add correspondence')
    add_button.connect('clicked', add_button_clicked)
    delete_button = Gtk.Button(label='Delete correspondence')
    delete_button.connect('clicked', delete_button_clicked)
    buttons_box = Gtk.Box(spacing=0)
    buttons_box.add(add_button)
    buttons_box.add(delete_button)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    box.add(pane)
    box.add(buttons_box)
    return box

def make_parameter_widget(settings, parameters):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    table_widget = make_correspondence_widget(parameters.table)
    canon_widget = make_syllable_canon_widget(parameters.syllable_canon)
    box.add(canon_widget)
    box.add(table_widget)
    
    def save_button_clicked(widget):
        table = read_table_from_widget(table_widget)
        serialize.serialize_correspondence_file(
            os.path.join(
                settings.directory_path,
                settings.proto_languages[parameters.proto_language_name]),
            RE.Parameters(
                table,
                read_syllable_canon_from_widget(canon_widget),
                parameters.proto_language_name))

    save_button = Gtk.Button(label='Save')
    save_button.connect('clicked', save_button_clicked)
    box.add(save_button)
    
    return box

def make_parameters_widget(settings):
    notebook = Gtk.Notebook()
    for (language, correspondence_filename) in settings.proto_languages.items():
        notebook.append_page(
            make_parameter_widget(
                settings,
                read.read_correspondence_file(
                    os.path.join(settings.directory_path,
                                 correspondence_filename),
                    language,
                    settings.upstream[language],
                    language)),
            Gtk.Label(language))
    return notebook

def make_sets_store(sets=None):
    return Gtk.TreeStore(str, str)

def make_sets_view(model):
    sets_view = Gtk.TreeView.new_with_model(model)
    recon_column = Gtk.TreeViewColumn('Reconstructions',
                                      Gtk.CellRendererText(),
                                      text=0)
    recon_column.set_sort_column_id(0)
    recon_column.set_resizable(True)
    sets_view.append_column(recon_column)
    sets_view.append_column(Gtk.TreeViewColumn('Ids',
                                               Gtk.CellRendererText(),
                                               text=1))
    return sets_view

def make_sets_widget(settings):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    window = Gtk.ScrolledWindow()
    window.set_vexpand(True)
    store = make_sets_store()
    window.add(make_sets_view(store))
    box.add(window)

    def batch_upstream_clicked(widget):
        threading.Thread(target=lambda: batch_upstream()).start()

    def batch_upstream():
        def store_row(parent, form):
            if isinstance(form, RE.ProtoForm):
                row = store.append(
                    parent=parent,
                    row=['*'+form.glyphs if parent is None
                         else str(form),
                         RE.correspondences_as_ids(form.correspondences)])
                for supporting_form in form.supporting_forms:
                    store_row(row, supporting_form)
            elif isinstance(form, RE.ModernForm):
                row = store.append(parent=parent,
                                   row=[str(form), ''])

        proto_lexicon = RE.batch_all_upstream(settings)
        Gdk.threads_enter()
        store.clear()
        for form in proto_lexicon.forms:
            store_row(None, form)
        Gdk.threads_leave()

    upstream_button = Gtk.Button(label='Batch All Upstream')
    upstream_button.connect('clicked', batch_upstream_clicked)
    box.add(upstream_button)
    return box

class REWindow(Gtk.Window):

    def __init__(self, settings):
        Gtk.Window.__init__(self, title='The Reconstruction Engine',
                            default_height=800, default_width=1024)
        sets_pane = Gtk.ScrolledWindow()
        sets_pane.set_vexpand(True)
        self.upstream_store = make_sets_store()
        sets_pane.add(make_sets_view(self.upstream_store))

        upstream_button = Gtk.Button(label='Batch Upstream')
        upstream_button.connect('clicked', self.batch_upstream_press)

        statistics_pane = Gtk.ScrolledWindow()
        statistics_pane.set_hexpand(True)
        statistics_pane.set_vexpand(True)
        statistics_view = Gtk.TextView()
        statistics_pane.add(statistics_view)
        self.statistics_buffer = WrappedTextBuffer(statistics_view.get_buffer())

        # layout
        self.pane_layout = Gtk.Paned()
        self.pane_layout.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.add(self.pane_layout)
        left_pane = Gtk.Paned()
        left_pane.set_orientation(Gtk.Orientation.VERTICAL)
        top_left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top_left_box.add(make_lexicons_widget(
            [read.read_lexicon(
                os.path.join(settings.directory_path,
                             settings.attested[language]))
             for language in settings.attested.keys()]))
        left_pane.add(top_left_box)
        self.pane_layout.add1(left_pane)
        right_pane = Gtk.Paned()
        right_pane.set_orientation(Gtk.Orientation.VERTICAL)
        self.pane_layout.add2(right_pane)
        # right_pane.add1(sets_pane)
        right_pane.add1(make_sets_widget(settings))
        right_pane.add2(statistics_pane)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.add(make_parameters_widget(settings))
        self.add(box)
        left_pane.add2(box)

    def batch_upstream_press(self, widget):
        threading.Thread(target=lambda: self.batch_upstream()).start()

    def batch_upstream(self):
        params = RE.Parameters(read_view_into_table(
            self.correspondence_view),
                               read_syllable_canon_from_widget(
                                   self.syllable_canon_widget))
        sets, statistics = RE.batch_upstream(lexicons, params)
        Gdk.threads_enter()
        self.upstream_store.clear()
        for (cs, supporting_forms) in sets:
            proto = RE.correspondences_as_proto_form_string(cs)
            ids = RE.correspondences_as_ids(cs)
            parent = self.upstream_store.append(parent=None,
                                                row=['*' + proto, ids])
            for supporting_form in supporting_forms:
                self.upstream_store.append(parent=parent,
                                           row=[str(supporting_form), ''])
        Gdk.threads_leave()

def run(settings):
    out = sys.stdout
    win = REWindow(settings)
    sys.stdout = win.statistics_buffer
    win.connect('delete_event', Gtk.main_quit)
    win.show_all()
    GObject.threads_init()
    Gdk.threads_init()
    Gtk.main()
    sys.stdout = out

if __name__ == "__main__":

    base_dir = "../RE7/DATA"
    # lexicons and parameters
    try:
        project = sys.argv[1]
        try:
            settings_type = sys.argv[2]
        except:
            settings_type = 'default'
    except:
        print('no project specified. Try "DEMO93" if you like')
        sys.exit(1)

    settings = read.read_settings_file(f'{base_dir}/{project}/{project}.{settings_type}.parameters.xml')
    # lexicons = list(read.read_lexicons(settings.upstream, base_dir, project))
    # params = read.read_correspondence_file(f'{base_dir}/{project}/{settings.correspondence_file}', project, settings.upstream)
    run(settings)
