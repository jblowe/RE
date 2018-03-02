import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib
import RE
import read
import threading
import sys
import serialize

class WrappedTextBuffer():
    def __init__(self, buffer):
        self.buffer = buffer
    def write(self, string):
        Gdk.threads_enter()
        self.buffer.insert(self.buffer.get_end_iter(),
                           string, len(string))
        Gdk.threads_leave()

def make_correspondence_row(correspondence, names):
    return [correspondence.id, str(correspondence.context),
            correspondence.syllable_type, correspondence.proto_form] + \
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
        treeview.append_column(column)
    return treeview, store

def read_view_into_table(view):
    model = view.get_model()
    names = [col.get_title() for col in view.get_columns()][4:]
    table = RE.TableOfCorrespondences('', names)
    for row in model:
        table.add_correspondence(
            RE.Correspondence(
                row[0], eval(row[1]), row[2], row[3],
                dict(zip(names, ([x.strip() for x in token.split(',')]
                                 for token in row[4:])))))
    return table

def make_sets_store(sets=None):
    return Gtk.TreeStore(str, str)

def make_sets_view(model):
    sets_view = Gtk.TreeView.new_with_model(model)
    recon_column = Gtk.TreeViewColumn('Reconstructions',
                                      Gtk.CellRendererText(),
                                      text=0)
    recon_column.set_resizable(True)
    sets_view.append_column(recon_column)
    sets_view.append_column(Gtk.TreeViewColumn('Ids',
                                               Gtk.CellRendererText(),
                                               text=1))
    return sets_view

def make_syllable_canon_widget(syllable_canon):
    grid = Gtk.Grid()
    regex_entry = Gtk.Entry()
    regex_entry.set_text(syllable_canon.regex.pattern)
    grid.attach(Gtk.Label('Syllable regex:'), 0, 0, 1, 1)
    grid.attach(regex_entry, 1, 0, 1, 1)
    sound_classes_entry = Gtk.Entry()
    sound_classes_entry.set_text(str(syllable_canon.sound_classes))
    grid.attach(Gtk.Label('Sound classes:'), 0, 1, 1, 1)
    grid.attach(sound_classes_entry, 1, 1, 1, 1)
    return grid

def read_syllable_canon_from_widget(widget):
    children = widget.get_children()
    return RE.SyllableCanon(eval(children[0].get_text()),
                            children[2].get_text())

def make_lexicon_widget(words):
    store = Gtk.ListStore(str, str)
    for form in words:
        store.append([form.form, form.gloss])
    view = Gtk.TreeView.new_with_model(store)
    for i, column_title in enumerate(['Form', 'Gloss']):
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, cell, text=i)
        view.append_column(column)
    pane = Gtk.ScrolledWindow()
    pane.set_vexpand(True)
    pane.add(view)
    return pane

def make_lexicons_widget(lexicons):
    notebook = Gtk.Notebook()
    for language, words in lexicons:
        notebook.append_page(make_lexicon_widget(words),
                             Gtk.Label(language))
    return notebook

# make 1 box containing 5 input entries
class REWindow(Gtk.Window):

    def __init__(self, lexicons, params):
        Gtk.Window.__init__(self, title='The Reconstruction Engine',
                            default_height=800, default_width=1024)

        correspondence_pane = Gtk.ScrolledWindow()
        correspondence_pane.set_vexpand(True)
        self.correspondence_view, self.table_store = \
            make_correspondence_view(params.table)
        correspondence_pane.add(self.correspondence_view)

        sets_pane = Gtk.ScrolledWindow()
        sets_pane.set_vexpand(True)
        self.upstream_store = make_sets_store()
        sets_pane.add(make_sets_view(self.upstream_store))

        upstream_button = Gtk.Button(label='Batch Upstream')
        upstream_button.connect('clicked', self.batch_upstream_press)

        add_table_row_button = Gtk.Button(label='Add correspondence')
        add_table_row_button.connect('clicked',
                                     self.on_add_row_button_clicked)

        delete_table_row_button = Gtk.Button(label='Delete correspondence')
        delete_table_row_button.connect('clicked',
                                        self.on_delete_row_button_clicked)

        save_button = Gtk.Button(label='Save')
        save_button.connect('clicked', self.on_save_button_clicked)

        statistics_pane = Gtk.ScrolledWindow()
        statistics_pane.set_hexpand(True)
        statistics_pane.set_vexpand(True)
        statistics_view = Gtk.TextView()
        statistics_pane.add(statistics_view)
        self.statistics_buffer = WrappedTextBuffer(statistics_view.get_buffer())

        # layour
        self.pane_layout = Gtk.Paned()
        self.pane_layout.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.add(self.pane_layout)
        left_pane = Gtk.Paned()
        left_pane.set_orientation(Gtk.Orientation.VERTICAL)
        self.syllable_canon_widget = \
            make_syllable_canon_widget(params.syllable_canon)
        top_left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top_left_box.add(self.syllable_canon_widget)
        top_left_box.add(make_lexicons_widget(lexicons))
        left_pane.add(top_left_box)
        self.pane_layout.add1(left_pane)
        right_pane = Gtk.Paned()
        right_pane.set_orientation(Gtk.Orientation.VERTICAL)
        self.pane_layout.add2(right_pane)
        right_pane.add1(sets_pane)
        right_pane.add2(statistics_pane)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        buttons_box = Gtk.Box(spacing=0)
        box.add(correspondence_pane)
        buttons_box.add(add_table_row_button)
        buttons_box.add(delete_table_row_button)
        buttons_box.add(upstream_button)
        buttons_box.add(save_button)
        box.add(buttons_box)
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

    def on_add_row_button_clicked(self, widget):
        columns = self.correspondence_view.get_columns()
        row = self.table_store.append(len(columns) * [''])
        path = self.table_store.get_path(row)
        self.correspondence_view.set_cursor(path, columns[0], True)

    def on_delete_row_button_clicked(self, widget):
        self.table_store.remove(self.table_store.get_iter(
            self.correspondence_view.get_cursor()[0]))

    def on_save_button_clicked(self, widget):
        serialize.serialize_correspondence_file(f'{base_dir}/{project}/{settings.correspondence_file}',
            RE.Parameters(read_view_into_table(
                self.correspondence_view),
                          read_syllable_canon_from_widget(
                              self.syllable_canon_widget)))

def run(lexicons, params):
    out = sys.stdout
    win = REWindow(lexicons, params)
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
    lexicons = list(read.read_lexicons(settings.upstream, base_dir, project))
    params = read.read_correspondence_file(f'{base_dir}/{project}/{settings.correspondence_file}', project, settings.upstream)
    run(lexicons, params)
