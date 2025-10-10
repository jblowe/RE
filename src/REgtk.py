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
import projects
import checkpoint
from datetime import datetime
import xml.etree.ElementTree as ET

class ProjectManagerDialog(Gtk.Dialog):
    """Dialog to choose a project."""
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Select Project", parent=parent, flags=0)
        self.set_default_size(600, 380)

        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button("Open", Gtk.ResponseType.OK)

        content = self.get_content_area()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=10)
        content.add(vbox)

        # Top explanatory label
        label = Gtk.Label(label="Choose a project to open from the projects directory:")
        label.set_halign(Gtk.Align.START)
        vbox.pack_start(label, False, False, 0)

        # Tree/List of projects
        self.store = Gtk.ListStore(str)  # project_name
        self.tree = Gtk.TreeView(model=self.store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Project", renderer, text=0)
        self.tree.append_column(column)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.add(self.tree)
        vbox.pack_start(scroller, True, True, 0)

        # Controls: mel/fuzzy/recon
        controls = Gtk.Box(spacing=8)
        self.mel_combo = Gtk.ComboBoxText()
        controls.pack_start(make_labeled_entry(self.mel_combo, 'mel:'), False, False, 0)

        self.recon_combo = Gtk.ComboBoxText()
        controls.pack_start(make_labeled_entry(self.recon_combo, 'recon:'), False, False, 0)

        self.fuzzy_check = Gtk.CheckButton(label='fuzzy')
        self.fuzzy_check.set_active(False)
        controls.pack_start(self.fuzzy_check, False, False, 0)

        vbox.pack_start(controls, False, False, 0)

        # Update mel/recon choices when a project is selected
        self.tree.get_selection().connect("changed", self.on_project_selection_changed)

        # Fill store with project names
        for name in projects.projects:
            self.store.append([name])

        # Select first row by default
        if len(self.store) > 0:
            first_path = self.store.get_path(self.store.get_iter_first())
            self.tree.set_cursor(first_path)

        self.show_all()

    def on_project_selection_changed(self, selection):
        model, iter_ = selection.get_selected()
        if iter_ is None:
            return
        project = model.get_value(iter_, 0)
        parameters_file = os.path.join(projects.projects[project],
                                       f'{project}.master.parameters.xml')
        self.mel_combo.remove_all()
        self.recon_combo.remove_all()
        try:
            recons = []
            mels = ['None']
            for setting in ET.parse(parameters_file).getroot():
                match setting.tag:
                    case 'reconstruction':
                        recons.append(setting.attrib['name'])
                    case 'mel':
                        mels.append(setting.attrib['name'])
            for mel in mels:
                self.mel_combo.append_text(mel)
            for recon in recons:
                self.recon_combo.append_text(recon)
            if mels:
                self.mel_combo.set_active(0)
            self.recon_combo.set_active(0)
        except Exception as e:
            print("Could not parse mel/recon options from", project_file, e)


    def get_selected(self):
        sel = self.tree.get_selection()
        model, iter_ = sel.get_selected()
        if iter_ is None:
            return None
        project = model.get_value(iter_, 0)
        # read controls
        mel = self.mel_combo.get_active_text()
        recon = self.recon_combo.get_active_text()
        fuzzy = self.fuzzy_check.get_active()
        return {
            'project': project,
            'mel': mel,
            'fuzzy': fuzzy,
            'recon': recon
        }

class WrappedTextBuffer():
    def __init__(self, buffer):
        self.buffer = buffer
    def write(self, string):
        GObject.idle_add(lambda string: self.buffer.insert(self.buffer.get_end_iter(),
                                                      string, len(string)),
                         string,
                         priority=GObject.PRIORITY_DEFAULT)
    def flush(self):
        pass

class Pane(Gtk.ScrolledWindow):
    def __init__(self, vexpand=False, hexpand=False):
        super().__init__()
        self.set_vexpand(vexpand)
        self.set_hexpand(hexpand)

def make_clickable_button(label, action):
    button = Gtk.Button(label=label)
    button.connect('clicked', action)
    return button

def make_labeled_entry(entry, label='Insert text here'):
    box = Gtk.Box()
    label = Gtk.Label(label=label)
    box.add(label)
    box.add(entry)
    return box

def make_expander(widget, label='Insert text here'):
    expander = Gtk.Expander(label=label)
    expander.add(widget)
    return expander

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

class Entry(Gtk.Entry):
    def __init__(self, initial, status_bar):
        super().__init__(hexpand=True)
        self.set_text(initial)
        self.connect("changed", lambda entry: status_bar.set_dirty(True))

class EnumerationWidget(Gtk.Box):
    def __init__(self, states, initial_state, on_toggle=lambda: None):
        super().__init__()
        self.state = initial_state
        self.on_toggle = on_toggle
        first_button = None
        for state in states:
            if first_button:
                button = Gtk.RadioButton.new_from_widget(first_button)
            else:
                button = Gtk.RadioButton.new_with_label_from_widget(None, state)
                first_button = button
            button.set_label(state)
            button.connect("toggled", self.on_button_toggled, state)
            if initial_state == state:
                button.set_active(True)
            self.pack_start(button, False, False, 0)

    def on_button_toggled(self, button, state):
        if button.get_active():
            if self.state != state:
                self.on_toggle()
            self.state = state

    def get_state(self):
        return self.state

class ContextMatchTypeEntry(EnumerationWidget):
    def __init__(self, initial_state, status_bar):
        super().__init__(['constituent', 'glyphs'], initial_state,
                         on_toggle = lambda: status_bar.set_dirty(True))

class SyllableCanonWidget(Gtk.Expander):
    def __init__(self, syllable_canon, status_bar):
        super().__init__(label='Syllable Canon')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)
        self.regex_entry = Entry(syllable_canon.regex.pattern, status_bar)
        self.sound_class_widget = SoundClassSheet(syllable_canon.sound_classes, status_bar)
        self.supra_segmental_entry = Entry(','.join(syllable_canon.supra_segmentals), status_bar)
        self.context_match_type_entry = ContextMatchTypeEntry(syllable_canon.context_match_type, status_bar)
        box.add(make_labeled_entry(self.regex_entry, 'Syllable regex:'))
        box.add(make_labeled_entry(self.supra_segmental_entry, 'Supra-segmentals:'))
        box.add(make_labeled_entry(self.context_match_type_entry, 'Context match type'))
        box.add(self.sound_class_widget)

    def syllable_canon(self):
        return RE.SyllableCanon(
            self.sound_class_widget.sound_classes(),
            self.regex_entry.get_text(),
            [x.strip() for x in self.supra_segmental_entry.get_text().split(',')],
            self.context_match_type_entry.get_state()
        )

class LexiconWidget(Pane):
    def __init__(self, words):
        super().__init__(vexpand=True)
        self.store = Gtk.ListStore(str, str)
        for form in words:
            self.store.append([form.glyphs, form.gloss])
        view = Gtk.TreeView.new_with_model(self.store)
        for i, column_title in enumerate(['Form', 'Gloss']):
            cell = Gtk.CellRendererText()
            cell.set_property('editable', True)
            column = Gtk.TreeViewColumn(column_title, cell, text=i)
            column.set_sort_column_id(i)
            view.append_column(column)
        self.add(view)

class LexiconsWidget(Gtk.Notebook):
    def __init__(self, lexicons):
        super().__init__()
        for lexicon in lexicons:
            self.append_page(LexiconWidget(lexicon.forms),
                             Gtk.Label(label=lexicon.language))

# A sheet is an expandable editable spreadsheet which has Add and
# Delete buttons to add or remove rows.
class Sheet(Gtk.Expander):
    def __init__(self, column_names, store, name, status_bar):
        super().__init__(label=name)
        view = Gtk.TreeView.new_with_model(store)
        self.status_bar = status_bar
        def store_edit_text(i):
            def f(widget, path, text):
                if store[path][i] != text:
                    self.status_bar.set_dirty(True)
                    store[path][i] = text
            return f
        for i, column_title in enumerate(column_names):
            cell = Gtk.CellRendererText()
            cell.set_property('editable', True)
            cell.connect('edited', store_edit_text(i))
            column = Gtk.TreeViewColumn(column_title, cell, text=i)
            column.set_sort_column_id(i)
            view.append_column(column)
        pane = Pane(vexpand=True)
        pane.add(view)

        buttons_box = Gtk.Box(spacing=0)
        buttons_box.add(make_clickable_button('Add', self.add_button_clicked))
        buttons_box.add(make_clickable_button('Delete', self.delete_button_clicked))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.add(pane)
        box.add(buttons_box)
        pane.set_vexpand(False)
        self.add(box)
        self.store = store
        self.view = view
        # we need to manually expand and unexpand the pane to trick layout
        # into working right.
        def action(widget, spec):
            pane.set_vexpand(widget.get_expanded())
        self.connect('notify::expanded', action)

    def add_button_clicked(self, widget):
        columns = self.view.get_columns()
        row = self.store.append(len(columns) * [''])
        path = self.store.get_path(row)
        self.view.set_cursor(path, columns[0], True)
        self.status_bar.set_dirty(True)

    def delete_button_clicked(self, widget):
        self.store.remove(self.store.get_iter(self.view.get_cursor()[0]))
        self.status_bar.set_dirty(True)

def make_correspondence_row(correspondence, names):
    return [correspondence.id,
            RE.context_as_string(correspondence.context),
            ','.join(correspondence.syllable_types),
            correspondence.proto_form] + \
            [', '.join(v)
             for v in (correspondence.daughter_forms.get(name)
                       for name in names)]

class CorrespondenceSheet(Sheet):
    def __init__(self, table, status_bar):
        store = Gtk.ListStore(*([str, str, str, str] +
                                len(table.daughter_languages) * [str]))
        for c in table.correspondences:
            store.append(make_correspondence_row(c, table.daughter_languages))
        self.names = table.daughter_languages
        super().__init__(['ID', 'Context', 'Syllable Type', '*'] + table.daughter_languages,
                         store,
                         'Correspondences',
                         status_bar)

    def fill(self, table):
        for row in self.store:
            table.add_correspondence(
                RE.Correspondence(
                    row[0],
                    RE.read_context_from_string(row[1]),
                    [x.strip() for x in row[2].split(',')], row[3],
                    dict(zip(self.names, ([x.strip() for x in token.split(',')]
                                          for token in row[4:])))))

class RuleSheet(Sheet):
    def __init__(self, table, status_bar):
        store = Gtk.ListStore(*([str, str, str, str, str, str]))
        for rule in table.rules:
            store.append([rule.id,
                          RE.context_as_string(rule.context),
                          rule.input,
                          ', '.join(rule.outcome),
                          ', '.join(rule.languages),
                          str(rule.stage)])
        super().__init__(['RID', 'Context', 'Input', 'Outcome', 'Languages', 'Stage'],
                         store, 'Rules', status_bar)

    def fill(self, table):
        for row in self.store:
            table.add_rule(
                RE.Rule(
                    row[0],
                    RE.read_context_from_string(row[1]),
                    row[2].strip(),
                    [x.strip() for x in row[3].split(',')],
                    [x.strip() for x in row[4].split(',')],
                    int(row[5])))

# given a sound classes object, construct a widget that allows users
# to specify a dictionary.
class SoundClassSheet(Sheet):
    def __init__(self, sound_classes, status_bar):
        store = Gtk.ListStore(*([str, str]))
        for (sound_class, constituents) in sound_classes.items():
            store.append([sound_class,
                          ', '.join(constituents)])
        super().__init__(['Class', 'Constituents'],
                         store, 'Sound Classes', status_bar)

    def sound_classes(self):
        return {row[0]: [x.strip() for x in row[1].split(',')]
                for row in self.store}

class ParameterWidget(Gtk.Box):
    def __init__(self, parameters, status_bar):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.correspondence_sheet = CorrespondenceSheet(parameters.table, status_bar)
        self.rule_sheet = RuleSheet(parameters.table, status_bar)
        self.canon_widget = SyllableCanonWidget(parameters.syllable_canon, status_bar)
        self.proto_language_name = parameters.proto_language_name
        self.mels = parameters.mels
        self.add(self.canon_widget)
        self.add(self.correspondence_sheet)
        self.add(self.rule_sheet)

    def parameters(self):
        names = self.correspondence_sheet.names
        table = RE.TableOfCorrespondences('', names)
        self.correspondence_sheet.fill(table)
        self.rule_sheet.fill(table)
        return RE.Parameters(
            table,
            self.canon_widget.syllable_canon(),
            self.proto_language_name,
            self.mels)

class ParameterTreeWidget(Gtk.Notebook):
    def __init__(self, initial_parameter_tree, status_bar):
        super().__init__()
        for (language, parameters) in initial_parameter_tree.items():
            self.append_page(ParameterWidget(parameters, status_bar),
                             Gtk.Label(label=language))

    def parameter_tree(self):
        return {parameter_widget.proto_language_name:
                parameter_widget.parameters()
                for parameter_widget in self}

class SetsWidget(Gtk.Box):
    def __init__(self, on_batch_clicked):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.window = Pane(vexpand=True)

        self.store = Gtk.TreeStore(str, str, str)
        self.view = Gtk.TreeView.new_with_model(self.store)
        recon_column = Gtk.TreeViewColumn('Reconstructions',
                                          Gtk.CellRendererText(),
                                          text=0)
        recon_column.set_sort_column_id(0)
        recon_column.set_resizable(True)
        self.view.append_column(recon_column)
        self.view.append_column(Gtk.TreeViewColumn("Ids",
                                                   Gtk.CellRendererText(), text=1))
        self.view.append_column(Gtk.TreeViewColumn("mel",
                                                   Gtk.CellRendererText(), text=2))
        self.window.add(self.view)
        self.add(self.window)

        button = make_clickable_button("Batch All Upstream", lambda w: on_batch_clicked())
        self.add(button)

        # For scroll-to-form support
        self.form_row_map = {}

    def populate(self, proto_lexicon):
        """Populate this store with forms."""
        self.store.clear()
        self.form_row_map.clear()

        def store_row(parent, form):
            if isinstance(form, RE.ProtoForm):
                row = self.store.append(
                    parent=parent,
                    row=['*' + form.glyphs if parent is None else str(form),
                         RE.correspondences_as_ids(form.correspondences),
                         str(form.mel)])
                for supporting_form in form.supporting_forms:
                    store_row(row, supporting_form)
            elif isinstance(form, RE.ModernForm):
                row = self.store.append(parent=parent, row=[str(form), '', ''])
            elif isinstance(form, RE.Stage0Form):
                row = self.store.append(parent=parent, row=[str(form), '', ''])
                ids = None
                for (stage, rules_applied) in form.history:
                    if ids:
                        self.store.append(parent=row,
                                          row=["> *" + stage,
                                               f" by applying {ids}",
                                               ""])
                    ids = ",".join([rule.id for rule in rules_applied])
                self.store.append(parent=row,
                                  row=["> " + str(form.modern),
                                       f" by applying {ids}",
                                       ""])
            self.form_row_map[form] = row

        for form in proto_lexicon.forms:
            store_row(None, form)

    def scroll_to_form(self, form):
        """Scroll and select the row with the given form."""
        iter_ = self.form_row_map.get(form)
        if iter_:
            path = self.view.get_model().get_path(iter_)
            self.view.expand_to_path(path)
            self.view.scroll_to_cell(path, None, True, 0.5, 0.0)
            self.view.set_cursor(path)
            return True
        return False

class LogWidget(Pane):
    def __init__(self):
        super().__init__(vexpand=True, hexpand=True)
        text_view = Gtk.TextView()
        self.add(text_view)
        self.log_buffer = WrappedTextBuffer(text_view.get_buffer())

    def get_buffer(self):
        return self.log_buffer

class FailedParsesWidget(Pane):
    def __init__(self):
        super().__init__(vexpand=True, hexpand=True)
        self.store = Gtk.ListStore(str, str, str)

        view = Gtk.TreeView.new_with_model(self.store)
        for i, column_title in enumerate(['Language', 'Form', 'Gloss']):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, cell, text=i)
            column.set_sort_column_id(i)
            view.append_column(column)
        self.add(view)

    def populate(self, failed_parses):
        self.store.clear()
        for failed_parse in failed_parses:
            self.store.append([
                failed_parse.language,
                failed_parse.glyphs,
                failed_parse.gloss if isinstance(failed_parse, (RE.Stage0Form, RE.ModernForm)) else ''
            ])

class CorrespondenceIndexWidget(Gtk.Box):
    def __init__(self, on_form_clicked, languages):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.store = Gtk.TreeStore(str, int, object)
        # str = correspondence text
        # int = visible_refs (updated after filter)
        # object = form target (None for parent rows)
        self.store = Gtk.TreeStore(str, int, object)
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self._filter_func)
        self.enum = EnumerationWidget(['any'] + languages, 'any',
                                      lambda: self.apply_filter())
        self.sorted = Gtk.TreeModelSort(model=self.filter)
        view = Gtk.TreeView.new_with_model(self.sorted)

        # Cell renderers
        def correspondence_cell_fun(column, cell, model, iter_, data=None):
            target = model.get_value(iter_, 2)
            text = model.get_value(iter_, 0)
            # highlight children as a link
            if target:
                cell.set_property("markup", f'<span foreground="blue" underline="single">{text}</span>')
            else:
                cell.set_property("text", text)

        def ref_cell_fun(column, cell, model, iter_, data=None):
            target = model.get_value(iter_, 2)   # "link target" object for children
            refs = model.get_value(iter_, 1)     # # of references column
            if target is None:                   # parent row
                cell.set_property("text", str(refs))
            else:                                # child row
                cell.set_property("text", "")    # blank out children

        for i, column_title in enumerate(['Correspondence', '# of references']):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, cell, text=i)
            column.set_sort_column_id(i)
            if i == 0:
                column.set_cell_data_func(cell, correspondence_cell_fun)
            if i == 1:
                column.set_cell_data_func(cell, ref_cell_fun)
            view.append_column(column)

        def on_button_press(view, event):
            if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:  # left click
                # Convert click coordinates to tree path
                x = int(event.x)
                y = int(event.y)
                pthinfo = view.get_path_at_pos(x, y)
                if pthinfo is not None:
                    path, col, cellx, celly = pthinfo
                    model = view.get_model()
                    iter_ = model.get_iter(path)
                    target = model.get_value(iter_, 2)
                    if target is not None:
                        # child row with hyperlink target
                        on_form_clicked(target)
                        return True  # stop further handling
            return False

        # ---------- Cursor change on hover ----------
        def on_motion_notify(view, event):
            x = int(event.x)
            y = int(event.y)
            pthinfo = view.get_path_at_pos(x, y)
            window = view.get_window()
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                model = view.get_model()
                iter_ = model.get_iter(path)
                target = model.get_value(iter_, 2)
                if target is not None:  # child row
                    window.set_cursor(Gdk.Cursor.new(Gdk.CursorType.HAND2))
                    return False
                window.set_cursor(None)  # reset
            return False

        view.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        view.connect("button-press-event", on_button_press)
        view.connect("motion-notify-event", on_motion_notify)
        pane = Pane(vexpand=True, hexpand=True)
        pane.add(view)
        self.pack_start(make_labeled_entry(self.enum, 'With support from:'),
                        False, False, 0)
        self.add(pane)

    # filter forms by support
    def _filter_func(self, model, iter_, data=None):
        selected_lang = self.enum.get_state()
        if selected_lang == 'any':
            return True
        # parent rows (correspondence) are always visible
        if model.get_value(iter_, 2) is None:
            return True
        # child rows (forms) are visible if they match selected language
        form = model.get_value(iter_, 2)
        return selected_lang in (support.language
                                 for support in form.attested_support)

    def update_visible_counts(self):
        parent = self.filter.get_iter_first()
        while parent:
            if self.filter[parent][2] is None:  # parent row
                # count children still visible under filter
                count = 0
                child = self.filter.iter_children(parent)
                while child:
                    count += 1
                    child = self.filter.iter_next(child)
                child_iter = self.filter.convert_iter_to_child_iter(parent)
                if child_iter:
                    self.store[child_iter][1] = count
            parent = self.filter.iter_next(parent)

    def apply_filter(self):
        self.filter.refilter()
        self.update_visible_counts()

    def populate(self, correspondence_index):
        self.store.clear()
        for (correspondence, forms) in correspondence_index.items():
            row = self.store.append(parent=None, row=[str(correspondence), len(forms), None])
            for form in forms:
                self.store.append(parent=row, row=[str(form), None, form])
        self.update_visible_counts()

def accel_str(label):
    if label == None:
        return None
    """Return the right modifier string for this platform."""
    if sys.platform == "darwin":
        return label.replace("<Ctrl>", "<Meta>")  # Command key on Mac
    else:
        return label

class CheckpointDialog(Gtk.FileChooserDialog):
    def __init__(self, parent, action_type="save", default_dir=None):
        action = Gtk.FileChooserAction.SAVE if action_type == "save" else Gtk.FileChooserAction.OPEN
        title = "Create Checkpoint" if action_type == "save" else "Load Checkpoint"

        super().__init__(title=title, parent=parent, action=action)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE if action_type == "save" else Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.set_default_size(800, 400)
        self._add_filters()
        self.set_current_folder(f'../projects/{parent.project}/')

        if action_type == "save":
            suggested_name = f"{parent.project}.{datetime.now():%Y-%m-%d_%H-%M-%S}.rechk"
            self.set_current_name(suggested_name)

    def _add_filters(self):
        filter_chk = Gtk.FileFilter()
        filter_chk.set_name("RE Checkpoint Files (*.rechk)")
        filter_chk.add_pattern("*.rechk")
        self.add_filter(filter_chk)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("All Files")
        filter_any.add_pattern("*")
        self.add_filter(filter_any)

class REMenuBar(Gtk.MenuBar):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self._build_menus()

    def _add_item(self, menu, label, callback_or_submenu, accel=None):
        item = Gtk.MenuItem(label=label)

        if isinstance(callback_or_submenu, list):
            submenu = Gtk.Menu()
            for sublabel, subcb in callback_or_submenu:
                self._add_item(submenu, sublabel, subcb)
            item.set_submenu(submenu)
        elif callback_or_submenu:
            item.connect("activate", callback_or_submenu)

        # Assign keyboard shortcut if provided
        if accel:
            key, mod = Gtk.accelerator_parse(accel)
            item.add_accelerator(
                "activate", self.window.accel_group, key, mod, Gtk.AccelFlags.VISIBLE
            )

        menu.append(item)
        return item

    def _build_menus(self):
        menus = {
            "File": [
                ("Open Project...", self.window.open_project, None),
                ("Save Project", self.window.save_project, "<Ctrl>S"),
                ("—", None, None),
                ("Create Checkpoint...", self.window.create_checkpoint, None),
                ("Load Checkpoint...", self.window.load_checkpoint, None),
                ("Compare...", self.window.compare, None),
                ("—", None, None),
                ("Quit", Gtk.main_quit, None),
            ],
            "View": [
                ("Zoom In", self.window.zoom_in, "<Ctrl>plus"),
                ("Zoom Out", self.window.zoom_out, "<Ctrl>minus"),
                ("Reset Zoom", self.window.zoom_reset, None),
            ],
        }

        for menu_name, items in menus.items():
            menu = Gtk.Menu()
            menu_item = Gtk.MenuItem(label=menu_name)
            menu_item.set_submenu(menu)
            self.append(menu_item)

            for label, callback, accel in items:
                if label == "—":
                    menu.append(Gtk.SeparatorMenuItem())
                    continue
                self._add_item(menu, label, callback, accel_str(accel))

def make_pane_container(orientation):
    container = Gtk.Paned()
    container.set_orientation(orientation)
    return container

class StatusBar(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=5)
        css = b"""
        .dirty {
            color: red;
            font-weight: bold;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Left-aligned label
        self.message_label = Gtk.Label(label="No project loaded.")
        self.message_label.set_halign(Gtk.Align.START)
        self.message_label.set_hexpand(True)  # take all space
        self.pack_start(self.message_label, True, True, 0)

        # Right-aligned dirty flag
        self.dirty_label = Gtk.Label(label="")
        self.dirty_label.set_halign(Gtk.Align.END)
        self.pack_start(self.dirty_label, False, False, 0)

        self.show_all()

    def set_message(self, text):
        self.message_label.set_text(text)

    def set_dirty(self, is_dirty):
        if is_dirty:
            self.dirty_label.set_text("● Unsaved changes")
            self.dirty_label.get_style_context().add_class("dirty")
        else:
            self.dirty_label.set_text("")
            self.dirty_label.get_style_context().remove_class("dirty")

class REWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='The Reconstruction Engine',
                            default_height=800, default_width=1400)
        # Track zoom state
        self.zoom_level = 1.0

        # Keyboard shortcuts
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        # -----------------------------
        # Menu
        # -----------------------------
        menu_bar = REMenuBar(self)

        # -----------------------------
        # Main layout
        # -----------------------------
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menu_bar, False, False, 0)

        # status bar
        self.status_bar = StatusBar()

        # layout
        pane_layout = make_pane_container(Gtk.Orientation.HORIZONTAL)
        box.pack_start(pane_layout, True, True, 0)
        self.left_pane = make_pane_container(Gtk.Orientation.VERTICAL)
        pane_layout.add1(self.left_pane)
        self.right_pane = make_pane_container(Gtk.Orientation.VERTICAL)
        pane_layout.add2(self.right_pane)
        self.add(box)
        box.pack_end(self.status_bar, False, False, 0)  # add at bottom of window
        self.show_all()
        self.open_project()

    def on_batch_all_upstream(self):
        """Run the batch process in a thread."""
        thread = threading.Thread(target=self._batch_upstream)
        thread.daemon = True
        thread.start()

    def _batch_upstream(self):
        def update_model():
            self.sets_widget.populate(proto_lexicon)
            statistics = proto_lexicon.statistics
            # KLUDGE: fix the api around isolates
            self.isolates_widget.populate(RE.Lexicon(proto_lexicon.language,
                                                     RE.extract_isolates(proto_lexicon),
                                                     statistics))
            self.failed_parses_widget.populate(statistics.failed_parses)
            self.correspondence_index_widget.populate(statistics.correspondence_index)
        out = sys.stdout
        sys.stdout = self.log_widget.get_buffer()
        try:
            proto_lexicon = RE.upstream_tree(
                self.settings.upstream_target,
                self.settings.upstream,
                self.parameters_widget.parameter_tree(),
                self.attested_lexicons,
                False,
            )
            GLib.idle_add(update_model)
        finally:
            sys.stdout = out

    # --------- Zoom handling (DPI-based) ---------
    def _apply_zoom(self):
        dpi_value = int(112 * self.zoom_level) * 1024
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-xft-dpi", dpi_value)

    def zoom_in(self, widget):
        self.zoom_level *= 1.2
        self._apply_zoom()

    def zoom_out(self, widget):
        self.zoom_level /= 1.2
        self._apply_zoom()

    def zoom_reset(self, widget):
        self.zoom_level = 1.0
        self._apply_zoom()

    def clear_widgets(self):
        for child in self.left_pane.get_children():
            self.left_pane.remove(child)
        for child in self.right_pane.get_children():
            self.right_pane.remove(child)

    # Load lexicons and parameters into widgets.
    def load(self, attested_lexicons, initial_parameter_tree):
        # Clear old widgets.
        self.clear_widgets()
        self.status_bar.set_dirty(False)
        self.attested_lexicons = attested_lexicons

        # Input widgets
        self.lexicons_widget = LexiconsWidget(attested_lexicons.values())
        self.parameters_widget = ParameterTreeWidget(initial_parameter_tree, self.status_bar)

        # Output widgets
        self.sets_widget = SetsWidget(self.on_batch_all_upstream)
        self.log_widget = LogWidget()
        self.isolates_widget = SetsWidget(lambda w: None)
        self.failed_parses_widget = FailedParsesWidget()
        self.correspondence_index_widget = CorrespondenceIndexWidget(
            self.sets_widget.scroll_to_form,
            [lexicon.language for lexicon in attested_lexicons.values()])

        # -----------------------------
        # Stack-based statistics pane
        # -----------------------------
        self.statistics_stack = Gtk.Stack()
        self.statistics_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.statistics_stack.set_transition_duration(200)

        self.statistics_stack.add_titled(self.log_widget, "log", "Log")
        self.statistics_stack.add_titled(self.isolates_widget,
                                         "isolates", "Isolates")
        self.statistics_stack.add_titled(self.failed_parses_widget,
                                         "failed", "Failed Parses")
        self.statistics_stack.add_titled(self.correspondence_index_widget,
                                         "index", "Correspondence index")
        # StackSwitcher to switch between views
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.statistics_stack)

        # Add new widgets to layout
        self.left_pane.add(self.lexicons_widget)
        self.right_pane.add1(self.sets_widget)
        stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        stats_box.pack_start(stack_switcher, False, False, 0)
        stats_box.pack_start(self.statistics_stack, True, True, 0)
        self.right_pane.add2(stats_box)  # add the stack here

        self.left_pane.add2(self.parameters_widget)

        self.show_all()

    # Initially load widgets from a settings file.
    def open_from_settings(self, settings):
        attested_lexicons = read.read_attested_lexicons(settings)

        self.settings = settings

        initial_parameter_tree = {language:
                                  read.read_correspondence_file(
                                      os.path.join(settings.directory_path,
                                                   correspondence_filename),
                                      language,
                                      settings.upstream[language],
                                      language,
                                      settings.mel_filename)
                                  for (language, correspondence_filename)
                                  in settings.proto_languages.items()
                                  }
        self.load(attested_lexicons, initial_parameter_tree)

    def open_project(self, widget=None):
        """Show the ProjectManagerDialog and load the selected project."""
        dialog = ProjectManagerDialog(self)
        response = dialog.run()
        selection = None
        if response == Gtk.ResponseType.OK:
            selection = dialog.get_selected()
        dialog.destroy()

        if selection is None:
            return

        project = selection['project']
        self.project = project
        parameters_file = os.path.join(projects.projects[project],
                                       f'{project}.master.parameters.xml')
        mel = None if selection['mel'] == 'None' else selection['mel']
        settings = read.read_settings_file(parameters_file,
                                           mel=mel,
                                           fuzzy=selection['fuzzy'],
                                           recon=selection['recon'])
        # dummy an arg object for load hooks. FIXME
        dummy.mel = mel
        dummy.fuzzy = selection['fuzzy']
        dummy.recon = selection['recon']
        load_hooks.load_hook(projects.projects[project], dummy, settings)
        self.status_bar.set_message(f'Opened project {project} from projects directory.')
        self.open_from_settings(settings)

    def create_checkpoint(self, widget):
        dialog = CheckpointDialog(self, action_type="save")
        if dialog.run() == Gtk.ResponseType.OK:
            checkpoint_path = dialog.get_filename()
            print(f"Creating checkpoint at: {checkpoint_path}")
            checkpoint_data = checkpoint.CheckpointData(self.attested_lexicons,
                                                        self.parameters_widget.parameter_tree())
            checkpoint.save_checkpoint_to_path(checkpoint_path, checkpoint_data)
            self.status_bar.set_message(f'Created checkpoint: {checkpoint_path}')
            self.status_bar.set_dirty(False)
        dialog.destroy()

    def load_checkpoint(self, widget):
        dialog = CheckpointDialog(self, action_type="load")
        if dialog.run() == Gtk.ResponseType.OK:
            checkpoint_path = dialog.get_filename()
            print(f"Loading checkpoint from: {checkpoint_path}")
            checkpoint_data = checkpoint.load_checkpoint_from_path(checkpoint_path)
            self.load(checkpoint_data.lexicons, checkpoint_data.parameter_tree)
            self.status_bar.set_message(f'Loaded from checkpoint: {checkpoint_path}')
        dialog.destroy()

    def compare(self, widget):
        pass

    def save_project(self, widget):
        for (proto_language_name, parameters) in self.parameters_widget.parameter_tree().items():
            serialize.serialize_correspondence_file(
                os.path.join(
                    self.settings.directory_path,
                    self.settings.proto_languages[proto_language_name]),
                parameters)
        self.status_bar.set_message(f'Saved project {self.project} into projects directory.')
        self.status_bar.set_dirty(False)

# HACK make load hooks happy
class dummy:
    pass

if __name__ == "__main__":
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-xft-dpi", 112 * 1024)

    win = REWindow()
    win.connect('delete_event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
