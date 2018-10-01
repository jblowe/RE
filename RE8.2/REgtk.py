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

def make_clickable_button(label, action):
    button = Gtk.Button(label=label)
    button.connect('clicked', action)
    return button

def make_pane(vexpand=False, hexpand=False):
    pane = Gtk.ScrolledWindow()
    pane.set_vexpand(vexpand)
    pane.set_hexpand(hexpand)
    return pane

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
    grid.attach(Gtk.Label(label='Syllable regex:'), 0, 0, 1, 1)
    grid.attach(make_entry(syllable_canon.regex.pattern), 1, 0, 1, 1)
    grid.attach(Gtk.Label(label='Sound classes:'), 0, 1, 1, 1)
    grid.attach(make_entry(str(syllable_canon.sound_classes)), 1, 1, 1, 1)
    grid.attach(Gtk.Label(label='Supra-segmentals'), 0, 2, 1, 1)
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
    pane = make_pane(vexpand=True)
    pane.add(view)
    return pane

def make_lexicons_widget(lexicons):
    notebook = Gtk.Notebook()
    for lexicon in lexicons:
        notebook.append_page(make_lexicon_widget(lexicon.forms),
                             Gtk.Label(label=lexicon.language))
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
                RE.read_context_from_string(row[1]),
                [x.strip() for x in row[2].split(',')], row[3],
                dict(zip(names, ([x.strip() for x in token.split(',')]
                                 for token in row[4:])))))
    return table

def make_correspondence_widget(table):
    pane = make_pane(vexpand=True)
    view, store = make_correspondence_view(table)
    pane.add(view)

    def add_button_clicked(widget):
        columns = view.get_columns()
        row = store.append(len(columns) * [''])
        path = store.get_path(row)
        view.set_cursor(path, columns[0], True)

    def delete_button_clicked(widget):
        store.remove(store.get_iter(view.get_cursor()[0]))

    buttons_box = Gtk.Box(spacing=0)
    buttons_box.add(make_clickable_button('Add correspondence', add_button_clicked))
    buttons_box.add(make_clickable_button('Delete correspondence', delete_button_clicked))
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    box.add(pane)
    box.add(buttons_box)
    return box

def read_parameters_from_widgets(table_widget, canon_widget, name, mels):
    return RE.Parameters(
        read_table_from_widget(table_widget),
        read_syllable_canon_from_widget(canon_widget),
        name,
        mels)

def make_parameter_widget(settings, parameters):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    table_widget = make_correspondence_widget(parameters.table)
    canon_widget = make_syllable_canon_widget(parameters.syllable_canon)
    box.table_widget = table_widget
    box.canon_widget = canon_widget
    box.proto_language_name = parameters.proto_language_name
    box.mels = parameters.mels
    box.add(canon_widget)
    box.add(table_widget)
    
    def save_button_clicked(widget):
        serialize.serialize_correspondence_file(
            os.path.join(
                settings.directory_path,
                settings.proto_languages[parameters.proto_language_name]),
            read_parameters_from_widgets(
                table_widget,
                canon_widget,
                parameters.proto_language_name,
                parameters.mels))

    box.add(make_clickable_button('Save', save_button_clicked))
    return box

def read_parameter_tree_from_widget(notebook_widget):
    return {page.proto_language_name:
            read_parameters_from_widgets(page.table_widget,
                                         page.canon_widget,
                                         page.proto_language_name,
                                         page.mels)
            for page in notebook_widget}

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
                    language,
                    os.path.join(settings.directory_path,
                                 settings.mel_filename)
                    if settings.mel_filename else None)),
            Gtk.Label(label=language))
    return notebook

def make_sets_store(sets=None):
    return Gtk.TreeStore(str, str, str)

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
    sets_view.append_column(Gtk.TreeViewColumn('mel',
                                               Gtk.CellRendererText(),
                                               text=2))
    return sets_view

def make_sets_widget(settings, attested_lexicons, parameter_tree_widget):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    window = make_pane(vexpand=True)
    store = make_sets_store()
    window.add(make_sets_view(store))
    box.add(window)

    def batch_upstream_clicked(widget):
        thread = threading.Thread(target=batch_upstream)
        thread.daemon = True
        thread.start()

    def batch_upstream():
        def store_row(parent, form):
            if isinstance(form, RE.ProtoForm):
                row = store.append(
                    parent=parent,
                    row=['*'+form.glyphs if parent is None
                         else str(form),
                         RE.correspondences_as_ids(form.correspondences),
                         str(form.mel)])
                for supporting_form in form.supporting_forms:
                    store_row(row, supporting_form)
            elif isinstance(form, RE.ModernForm):
                row = store.append(parent=parent,
                                   row=[str(form), '', ''])

        proto_lexicon = RE.upstream_tree(settings.upstream_target,
                                         settings.upstream,
                                         read_parameter_tree_from_widget(parameter_tree_widget),
                                         attested_lexicons)
        Gdk.threads_enter()
        store.clear()
        for form in proto_lexicon.forms:
            store_row(None, form)
        Gdk.threads_leave()

    box.add(make_clickable_button('Batch All Upstream', batch_upstream_clicked))
    return box

def make_pane_container(orientation):
    container = Gtk.Paned()
    container.set_orientation(orientation)
    return container

class REWindow(Gtk.Window):

    def __init__(self, settings):
        Gtk.Window.__init__(self, title='The Reconstruction Engine',
                            default_height=800, default_width=1024)
        attested_lexicons = read.read_attested_lexicons(settings)

        statistics_pane = make_pane(vexpand=True, hexpand=True)
        statistics_view = Gtk.TextView()
        statistics_pane.add(statistics_view)
        self.statistics_buffer = WrappedTextBuffer(statistics_view.get_buffer())

        # layout
        pane_layout = make_pane_container(Gtk.Orientation.HORIZONTAL)
        self.add(pane_layout)
        left_pane = make_pane_container(Gtk.Orientation.VERTICAL)
        left_pane.add(make_lexicons_widget(attested_lexicons.values()))
        pane_layout.add1(left_pane)
        right_pane = make_pane_container(Gtk.Orientation.VERTICAL)
        pane_layout.add2(right_pane)
        parameters_widget = make_parameters_widget(settings)
        right_pane.add1(make_sets_widget(settings, attested_lexicons, parameters_widget))
        right_pane.add2(statistics_pane)

        left_pane.add2(parameters_widget)

def run(settings):
    out = sys.stdout
    win = REWindow(settings)
    sys.stdout = win.statistics_buffer
    win.connect('delete_event', Gtk.main_quit)
    win.show_all()
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
