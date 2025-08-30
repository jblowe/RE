import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib
import RE
import read
import threading
import sys
import serialize
import os
import load_hooks
from argparser import args


settings = Gtk.Settings.get_default()
settings.set_property("gtk-xft-dpi", 112 * 1024)

class WrappedTextBuffer():
    def __init__(self, buffer):
        self.buffer = buffer
    def write(self, string):
        Gdk.threads_enter()
        self.buffer.insert(self.buffer.get_end_iter(),
                           string, len(string))
        Gdk.threads_leave()
    def flush(self):
        pass

def make_clickable_button(label, action):
    button = Gtk.Button(label=label)
    button.connect('clicked', action)
    return button

def make_pane(vexpand=False, hexpand=False):
    pane = Gtk.ScrolledWindow()
    pane.set_vexpand(vexpand)
    pane.set_hexpand(hexpand)
    return pane

def make_labeled_entry(entry, label='Insert text here'):
    box = Gtk.Box()
    label = Gtk.Label(label='Syllable regex:')
    box.add(label)
    box.add(entry)
    return box

def make_expander(widget, label='Insert text here'):
    expander = Gtk.Expander(label=label)
    expander.add(widget)
    return expander

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

def tab_key_press_handler(view, event):
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

def make_entry(text):
    entry = Gtk.Entry()
    entry.set_text(text)
    return entry

# given a sound classes object, construct a widget that allows users
# to specify a dictionary.
def make_sound_classes_widget(sound_classes):
    store = Gtk.ListStore(*([str, str]))
    for (sound_class, constituents) in sound_classes.items():
        store.append([sound_class,
                      ', '.join(constituents)])
    return make_sheet(['Class', 'Constituents'], store, name='Sound Classes'), store

def make_syllable_canon_widget(syllable_canon):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    widget = make_expander(box, label="Syllable canon")
    widget.regex_entry = make_entry(syllable_canon.regex.pattern)
    sound_class_widget, sound_class_store = make_sound_classes_widget(syllable_canon.sound_classes)
    widget.sound_class_store = sound_class_store
    widget.supra_segmental_entry = make_entry(','.join(syllable_canon.supra_segmentals))
    widget.context_match_type_entry = make_entry(syllable_canon.context_match_type)
    box.add(make_labeled_entry(widget.regex_entry, 'Syllable regex:'))
    box.add(make_labeled_entry(widget.supra_segmental_entry, 'Supra-segmentals:'))
    box.add(make_labeled_entry(widget.context_match_type_entry, 'Context match type'))
    box.add(sound_class_widget)
    return widget

def read_syllable_canon_from_widget(widget):
    sound_classes = {row[0]: [x.strip() for x in row[1].split(',')]
                     for row in widget.sound_class_store}
    return RE.SyllableCanon(
        sound_classes,
        widget.regex_entry.get_text(),
        [x.strip() for x in widget.supra_segmental_entry.get_text().split(',')],
        widget.context_match_type_entry.get_text()
    )

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

def read_table_from_widget(widget, rule_widget):
    view = widget.view
    names = [col.get_title() for col in view.get_columns()][4:]
    table = RE.TableOfCorrespondences('', names)
    for row in view.get_model():
        table.add_correspondence(
            RE.Correspondence(
                row[0],
                RE.read_context_from_string(row[1]),
                [x.strip() for x in row[2].split(',')], row[3],
                dict(zip(names, ([x.strip() for x in token.split(',')]
                                 for token in row[4:])))))
    for row in rule_widget.view.get_model():
        table.add_rule(
            RE.Rule(
                row[0],
                RE.read_context_from_string(row[1]),
                row[2].strip(),
                row[3].strip(),
                [x.strip() for x in row[4].split(',')],
                int(row[5])))
    return table

# A sheet is an expandable editable spreadsheet which has Add and
# Delete buttons to add or remove rows.
def make_sheet(column_names, store, name='Insert name here'):
    view = Gtk.TreeView.new_with_model(store)
    view.connect('key-press-event', tab_key_press_handler)
    def store_edit_text(i):
        def f(widget, path, text):
            store[path][i] = text
        return f
    for i, column_title in enumerate(column_names):
        cell = Gtk.CellRendererText()
        cell.set_property('editable', True)
        cell.connect('edited', store_edit_text(i))
        column = Gtk.TreeViewColumn(column_title, cell, text=i)
        column.set_sort_column_id(i)
        view.append_column(column)
    pane = make_pane(vexpand=True)
    pane.add(view)

    def add_button_clicked(widget):
        columns = view.get_columns()
        row = store.append(len(columns) * [''])
        path = store.get_path(row)
        view.set_cursor(path, columns[0], True)

    def delete_button_clicked(widget):
        store.remove(store.get_iter(view.get_cursor()[0]))

    buttons_box = Gtk.Box(spacing=0)
    buttons_box.add(make_clickable_button('Add', add_button_clicked))
    buttons_box.add(make_clickable_button('Delete', delete_button_clicked))
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    box.add(pane)
    box.add(buttons_box)
    pane.set_vexpand(False)
    expander = make_expander(box, name)
    expander.view = view
    # we need to manually expand and unexpand the pane to trick layout
    # into working right.
    def action(widget, spec):
        pane.set_vexpand(widget.get_expanded())
    expander.connect('notify::expanded', action)
    return expander

def make_correspondence_widget(table):
    store = make_correspondence_store(table)
    return make_sheet(['ID', 'Context', 'Syllable Type', '*'] + table.daughter_languages,
                      store, 'Correspondences')

def make_rule_widget(table):
    store = Gtk.ListStore(*([str, str, str, str, str, str]))
    for rule in table.rules:
        store.append([rule.id,
                      RE.context_as_string(rule.context),
                      rule.input,
                      rule.outcome,
                      ', '.join(rule.languages),
                      str(rule.stage)])
    return make_sheet(['RID', 'Context', 'Input', 'Outcome', 'Languages', 'Stage'], store, 'Rules')

def read_parameters_from_widgets(table_widget, rule_widget, canon_widget, name, mels):
    return RE.Parameters(
        read_table_from_widget(table_widget, rule_widget),
        read_syllable_canon_from_widget(canon_widget),
        name,
        mels)

def make_parameter_widget(settings, parameters):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.table_widget = make_correspondence_widget(parameters.table)
    box.rule_widget = make_rule_widget(parameters.table)
    box.canon_widget = make_syllable_canon_widget(parameters.syllable_canon)
    box.proto_language_name = parameters.proto_language_name
    box.mels = parameters.mels
    box.add(box.canon_widget)
    box.add(box.table_widget)
    box.add(box.rule_widget)

    def save_button_clicked(widget):
        serialize.serialize_correspondence_file(
            os.path.join(
                settings.directory_path,
                settings.proto_languages[parameters.proto_language_name]),
            read_parameters_from_widgets(
                box.table_widget,
                box.rule_widget,
                box.canon_widget,
                parameters.proto_language_name,
                parameters.mels))

    box.add(make_clickable_button('Save', save_button_clicked))
    return box

def read_parameter_tree_from_widget(notebook_widget):
    return {page.proto_language_name:
            read_parameters_from_widgets(page.table_widget,
                                         page.rule_widget,
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
                    settings.mel_filename)),
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

def make_sets_widget(settings, attested_lexicons, parameter_tree_widget, statistics_buffer):
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
        out = sys.stdout
        sys.stdout = statistics_buffer
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
            elif isinstance(form, RE.Stage0Form):
                row = store.append(parent=parent,
                                   row=[str(form), '', ''])
                ids = None
                for (stage, rules_applied) in form.history:
                    if ids:
                        store.append(parent=row,
                                     row=['> *' + stage,
                                          f' by applying {ids}',
                                          ''])
                    ids = ','.join([rule.id for rule in rules_applied])
                store.append(parent=row,
                             row=['> ' + str(form.modern),
                                  f' by applying {ids}',
                                  ''])

        proto_lexicon = RE.upstream_tree(settings.upstream_target,
                                         settings.upstream,
                                         read_parameter_tree_from_widget(parameter_tree_widget),
                                         attested_lexicons,
                                         # HACK
                                         False)
        def update_model():
            store.clear()
            for form in proto_lexicon.forms:
                store_row(None, form)
        sys.stdout = out
        GLib.idle_add(update_model)

    box.add(make_clickable_button('Batch All Upstream', batch_upstream_clicked))
    return box

def make_pane_container(orientation):
    container = Gtk.Paned()
    container.set_orientation(orientation)
    return container

def make_open_dialog_window(window):
    def add_filters(dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
    def activate(widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=window, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        add_filters(dialog)
        response = dialog.run()
        print('what')
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()
    return activate

def make_RE_menu_bar(window):
    menu_bar = Gtk.MenuBar()

    file_menu_item = Gtk.MenuItem(label="File")
    menu_bar.append(file_menu_item)
    file_menu = Gtk.Menu()
    file_menu_item.set_submenu(file_menu)

    open_menu = Gtk.MenuItem(label="New Experiment")
    file_menu.add(open_menu)
    open_menu.connect('activate', make_open_dialog_window(window))

    open_menu = Gtk.MenuItem(label="Open Experiment...")
    file_menu.add(open_menu)
    open_menu.connect('activate', make_open_dialog_window(window))

    save_menu = Gtk.MenuItem(label="Save All Parameters")
    file_menu.add(save_menu)
    save_menu.connect('activate', make_open_dialog_window(window))

    save_menu = Gtk.MenuItem(label="Save All Parameters As...")
    file_menu.add(save_menu)
    save_menu.connect('activate', make_open_dialog_window(window))

    save_menu = Gtk.MenuItem(label="Save Run...")
    file_menu.add(save_menu)
    save_menu.connect('activate', make_open_dialog_window(window))

    save_run_menu = Gtk.MenuItem(label="Compare Runs...")
    file_menu.add(save_run_menu)
    save_menu.connect('activate', make_open_dialog_window(window))

    quit_menu = Gtk.MenuItem(label="Quit")
    file_menu.add(quit_menu)
    quit_menu.connect('activate', quit)

    edit_menu_item = Gtk.MenuItem(label="Edit")
    menu_bar.append(edit_menu_item)

    view_menu_item = Gtk.MenuItem(label="View")
    menu_bar.append(view_menu_item)

    return menu_bar

class REWindow(Gtk.Window):

    def __init__(self, settings, attested_lexicons):
        Gtk.Window.__init__(self, title='The Reconstruction Engine',
                            default_height=800, default_width=1400)

        statistics_pane = make_pane(vexpand=True, hexpand=True)
        statistics_view = Gtk.TextView()
        statistics_pane.add(statistics_view)
        statistics_buffer = WrappedTextBuffer(statistics_view.get_buffer())

        menu_bar = make_RE_menu_bar(self)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menu_bar, False, False, 0)

        # layout
        pane_layout = make_pane_container(Gtk.Orientation.HORIZONTAL)
        box.pack_start(pane_layout, True, True, 0)
        left_pane = make_pane_container(Gtk.Orientation.VERTICAL)
        left_pane.add(make_lexicons_widget(attested_lexicons.values()))
        pane_layout.add1(left_pane)
        right_pane = make_pane_container(Gtk.Orientation.VERTICAL)
        pane_layout.add2(right_pane)
        parameters_widget = make_parameters_widget(settings)
        right_pane.add1(make_sets_widget(settings, attested_lexicons, parameters_widget, statistics_buffer))
        right_pane.add2(statistics_pane)

        left_pane.add2(parameters_widget)

        self.add(box)

def run(settings, attested_lexicons):
    win = REWindow(settings, attested_lexicons)
    win.connect('delete_event', Gtk.main_quit)
    win.show_all()
    Gdk.threads_init()
    Gtk.main()

if __name__ == "__main__":
    settings = read.read_settings_file(f'../projects/{args.project}/{args.project}.master.parameters.xml',
                                       mel=args.mel,
                                       recon=args.recon)
    load_hooks.load_hook(args.project, args, settings)
    # HACK: The statement above and the statement below are no longer
    # independent due to fuzzying in TGTM...
    attested_lexicons = read.read_attested_lexicons(settings)
    run(settings, attested_lexicons)
