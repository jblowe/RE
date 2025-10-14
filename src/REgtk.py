import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib, Pango
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
import traceback

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

        self.fuzzy_combo = Gtk.ComboBoxText()
        controls.pack_start(make_labeled_entry(self.fuzzy_combo, 'fuzzy:'), False, False, 0)

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
        self.fuzzy_combo.remove_all()
        try:
            recons = []
            mels = ['None']
            fuzzies = ['None']
            for setting in ET.parse(parameters_file).getroot():
                match setting.tag:
                    case 'reconstruction':
                        recons.append(setting.attrib['name'])
                    case 'mel':
                        mels.append(setting.attrib['name'])
                    case 'fuzzy':
                        fuzzies.append(setting.attrib['name'])
            for mel in mels:
                self.mel_combo.append_text(mel)
            for recon in recons:
                self.recon_combo.append_text(recon)
            for fuzzy in fuzzies:
                self.fuzzy_combo.append_text(fuzzy)
            if mels:
                self.mel_combo.set_active(0)
            self.recon_combo.set_active(0)
        except Exception as e:
            print("Could not parse mel/recon/fuzzy options from", project_file, e)


    def get_selected(self):
        sel = self.tree.get_selection()
        model, iter_ = sel.get_selected()
        if iter_ is None:
            return None
        project = model.get_value(iter_, 0)
        # read controls
        mel = self.mel_combo.get_active_text()
        recon = self.recon_combo.get_active_text()
        fuzzy = self.fuzzy_combo.get_active_text()
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
        GLib.idle_add(lambda string: self.buffer.insert(self.buffer.get_end_iter(),
                                                   string, len(string)),
                      string,
                      priority=GLib.PRIORITY_DEFAULT)
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
        self.connect("changed", lambda entry: status_bar.add_dirty('entry'))

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
                         on_toggle = lambda: status_bar.add_dirty('context_match'))

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
    def __init__(self, lexicon):
        super().__init__(vexpand=True)
        self.store = Gtk.ListStore(str, str, str)
        self.language = lexicon.language
        for form in lexicon.forms:
            self.store.append([form.glyphs, form.gloss, form.id])
        view = Gtk.TreeView.new_with_model(self.store)

        view.set_search_equal_func(all_columns_search_func, None)
        view.set_search_column(0)

        for i, column_title in enumerate(['Form', 'Gloss']):
            cell = Gtk.CellRendererText()
            cell.set_property('editable', True)
            column = Gtk.TreeViewColumn(column_title, cell, text=i)
            column.set_resizable(True)
            column.set_sort_column_id(i)
            view.append_column(column)
        self.add(view)

    def lexicon(self):
        language = self.language
        return RE.Lexicon(language,
                          [RE.ModernForm(language, row[0], row[1], row[2])
                           for row in self.store],
                          None)

class LexiconsWidget(Gtk.Notebook):
    def __init__(self, lexicons):
        super().__init__()
        for lexicon in lexicons:
            self.append_page(LexiconWidget(lexicon),
                             Gtk.Label(label=lexicon.language))

    def lexicons(self):
        return {lexicon_widget.language:
                lexicon_widget.lexicon()
                for lexicon_widget in self}


# A search function that searches over all columns for matches.
def all_columns_search_func(model, column, key, iter_, data):
    key = key.lower()
    values = [model.get_value(iter_, i)
              for i in range(model.get_n_columns())]
    return not any(key in (str(v) or "").lower() for v in values)

# A sheet is an editable spreadsheet which has Add and Delete buttons
# to add or remove rows.
class Sheet(Gtk.Box):
    def __init__(self, column_names, store, name,
                 on_change: lambda: None,
                 search_func=all_columns_search_func):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        view = Gtk.TreeView.new_with_model(store)
        view.connect('key-press-event', tab_key_press_handler)
        view.set_search_equal_func(search_func, None)
        view.set_search_column(0)
        self.on_change = on_change
        def store_edit_text(i):
            def f(widget, path, text):
                if store[path][i] != text:
                    self.on_change()
                    store[path][i] = text
            return f
        for i, column_title in enumerate(column_names):
            cell = Gtk.CellRendererText()
            cell.set_property('editable', True)
            cell.connect('edited', store_edit_text(i))
            column = Gtk.TreeViewColumn(column_title, cell, text=i)
            column.set_resizable(True)
            column.set_sort_column_id(i)
            view.append_column(column)
        pane = Pane(vexpand=True)
        pane.add(view)
        self.buttons_box = Gtk.Box(spacing=0)
        self.buttons_box.add(make_clickable_button('Add', self.add_button_clicked))
        self.buttons_box.add(make_clickable_button('Delete', self.delete_button_clicked))
        self.add(pane)
        hscroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                             vscrollbar_policy=Gtk.PolicyType.NEVER)
        hscroll.add(self.buttons_box)
        self.add(hscroll)
        self.store = store
        self.view = view
        self.pane = pane

    def add_button_clicked(self, widget):
        columns = self.view.get_columns()
        row = self.store.append(self.store.get_n_columns() * [''])
        path = self.store.get_path(row)
        self.view.set_cursor(path, columns[0], True)
        self.on_change()

    def delete_button_clicked(self, widget):
        self.store.remove(self.store.get_iter(self.view.get_cursor()[0]))
        self.on_change()

    def scroll_to_row_matching(self, predicate):
        """Scroll to the first row for which predicate(model_row) is True."""
        treeview = self.view
        model = treeview.get_model()

        for row in model:
            if predicate(row):
                path = model.get_path(row.iter)
                treeview.scroll_to_cell(path, None, True, 0.5, 0.0)
                treeview.set_cursor(path)
                return True
        return False

class ExpandableSheet(Gtk.Expander):
    def __init__(self, column_names, store, name, on_change=lambda: None):
        super().__init__(label=name)
        sheet = Sheet(column_names, store, name, on_change=on_change)
        self.add(sheet)
        self.store = sheet.store
        sheet.pane.set_vexpand(False)
        self.sheet = sheet

        # we need to manually expand and unexpand the pane to trick layout
        # into working right.
        def action(widget, spec):
            sheet.pane.set_vexpand(widget.get_expanded())

        self.connect('notify::expanded', action)

    def scroll_to_row_matching(self, predicate):
        self.set_expanded(True)
        self.sheet.scroll_to_row_matching(predicate)

class DisableableRowsMixin:
    def setup_disableable_rows(self, sheet, enabled_index):
        """Attach the context menu and styling behavior to the given TreeView."""
        self.enabled_index = enabled_index
        view = sheet.view
        store = sheet.store

        # Attach cell data functions
        for i, column in enumerate(view.get_columns()):
            renderers = column.get_cells()
            if renderers:
                renderer = renderers[0]
                column.set_cell_data_func(renderer, self._style_row, i)

        # Attach right-click menu
        def on_right_click(view, event):
            if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
                pthinfo = view.get_path_at_pos(int(event.x), int(event.y))
                if pthinfo is None:
                    return False
                path, col, cellx, celly = pthinfo
                model = view.get_model()
                iter_ = model.get_iter(path)
                enabled = model.get_value(iter_, self.enabled_index)

                menu = Gtk.Menu()
                label = "Disable row" if enabled else "Enable row"
                item = Gtk.MenuItem(label=label)

                def toggle(_):
                    model.set_value(iter_, self.enabled_index, not enabled)
                    view.queue_draw()

                item.connect("activate", toggle)
                menu.append(item)
                menu.show_all()
                menu.popup(None, None, None, None, event.button, event.time)
                return True
            return False

        def toggle_selected_row(_widget):
            """Enable or disable the currently selected row."""
            selection = self.sheet.view.get_selection()
            model, iter_ = selection.get_selected()
            if iter_ is None:
                return
            enabled = model.get_value(iter_, self.enabled_index)
            model.set_value(iter_, self.enabled_index, not enabled)
            self.sheet.view.queue_draw()
            toggle_row_button.set_label("Disable Row" if not enabled else "Enable Row")
            update_bulk_buttons()

        def on_selection_changed(selection):
            """Update the toggle button label when the selected row changes."""
            model, iter_ = selection.get_selected()
            if iter_ is None:
                toggle_row_button.set_label("Toggle Row")
                toggle_row_button.set_sensitive(False)
                return
            enabled = model.get_value(iter_, self.enabled_index)
            toggle_row_button.set_sensitive(True)
            toggle_row_button.set_label("Disable Row" if enabled else "Enable Row")

        def enable_all_rows(_widget):
            for row in self.sheet.store:
                row[self.enabled_index] = True
            self.sheet.view.queue_draw()

        def disable_all_rows(_widget):
            for row in self.sheet.store:
                row[self.enabled_index] = False
            self.sheet.view.queue_draw()

        def update_bulk_buttons(*args):
            """Update the enable/disable all buttons to reflect table state."""
            any_disabled = any(not row[self.enabled_index] for row in self.sheet.store)
            any_enabled = any(row[self.enabled_index] for row in self.sheet.store)
            enable_all_button.set_sensitive(any_disabled)
            disable_all_button.set_sensitive(any_enabled)

        def on_row_inserted(store, path, iter_):
            store.set_value(iter_, self.enabled_index, True)
            update_bulk_buttons(store, path, iter_)

        # Track selection changes
        selection = view.get_selection()
        selection.connect("changed", on_selection_changed)

        # Track changes in the model
        store.connect("row-changed", update_bulk_buttons)
        store.connect("row-inserted", on_row_inserted)
        store.connect("row-deleted", update_bulk_buttons)

        toggle_row_button = make_clickable_button("Disable Row", toggle_selected_row)
        enable_all_button = make_clickable_button("Enable All", enable_all_rows)
        disable_all_button = make_clickable_button("Disable All", disable_all_rows)

        sheet.buttons_box.add(toggle_row_button)
        sheet.buttons_box.add(enable_all_button)
        sheet.buttons_box.add(disable_all_button)

        view.connect("button-press-event", on_right_click)

    def _style_row(self, column, cell, model, iter_, col_index):
        """Render rows grayed out when disabled."""
        value = model.get_value(iter_, col_index)
        enabled = model.get_value(iter_, self.enabled_index)

        cell.set_property("text", str(value) if value is not None else "")

        if not enabled:
            cell.set_property("foreground", "#888")
            cell.set_property("style", Pango.Style.ITALIC)
            cell.set_property("cell-background", "#f6f6f6")
        else:
            cell.set_property("foreground", None)
            cell.set_property("style", Pango.Style.NORMAL)
            cell.set_property("cell-background", None)

    def _set_all_rows(self, enabled):
        """Set all rows to the given enabled/disabled state."""
        model = self.view.get_model()
        if model is None:
            return
        iter_ = model.get_iter_first()
        while iter_:
            model.set_value(iter_, self.enabled_index, enabled)
            iter_ = model.iter_next(iter_)
        self.view.queue_draw()

def make_correspondence_row(correspondence, names):
    return [correspondence.id,
            RE.context_as_string(correspondence.context),
            ','.join(correspondence.syllable_types),
            correspondence.proto_form] + \
            [', '.join(v)
             for v in (correspondence.daughter_forms.get(name)
                       for name in names)] + [True]

class CorrespondenceSheet(ExpandableSheet, DisableableRowsMixin):
    def __init__(self, table, status_bar):
        store = Gtk.ListStore(*([str, str, str, str] +
                                len(table.daughter_languages) * [str]
                                + [bool]))
        for c in table.correspondences:
            store.append(make_correspondence_row(c, table.daughter_languages))
        self.names = table.daughter_languages
        super().__init__(['ID', 'Context', 'Slot', '*'] + table.daughter_languages,
                         store,
                         'Correspondences',
                         lambda: status_bar.add_dirty('correspondences'))

        self.setup_disableable_rows(self.sheet, store.get_n_columns() - 1)

    def fill(self, table):
        for row in self.store:
            if row[self.enabled_index]:
                table.add_correspondence(
                    RE.Correspondence(
                        row[0],
                        RE.read_context_from_string(row[1]),
                        [x.strip() for x in row[2].split(',')], row[3],
                        dict(zip(self.names, ([x.strip() for x in token.split(',')]
                                              for token in row[4:])))))

    def scroll_to_correspondence(self, correspondence):
        return self.scroll_to_row_matching(lambda row: (row[0] == correspondence.id))

class RuleSheet(ExpandableSheet, DisableableRowsMixin):
    def __init__(self, table, status_bar):
        store = Gtk.ListStore(*([str, str, str, str, str, str, bool]))
        self.enabled_index = 6
        for rule in table.rules:
            store.append([rule.id,
                          RE.context_as_string(rule.context),
                          rule.input,
                          ', '.join(rule.outcome),
                          ', '.join(rule.languages),
                          str(rule.stage),
                          True])
        super().__init__(['RID', 'Context', 'Input', 'Outcome', 'Languages', 'Stage'],
                         store, 'Rules', lambda: status_bar.add_dirty('rules'))
        self.setup_disableable_rows(self.sheet, store.get_n_columns() - 1)

    def fill(self, table):
        for row in self.store:
            if row[self.enabled_index]:
                table.add_rule(
                    RE.Rule(
                        row[0],
                        RE.read_context_from_string(row[1]),
                        row[2].strip(),
                        [x.strip() for x in row[3].split(',')],
                        [x.strip() for x in row[4].split(',')],
                        int(row[5])))

    def scroll_to_rule(self, rule):
        return self.scroll_to_row_matching(lambda row: (row[0] == rule.id))

# given a sound classes object, construct a widget that allows users
# to specify a dictionary.
class SoundClassSheet(ExpandableSheet):
    def __init__(self, sound_classes, status_bar):
        store = Gtk.ListStore(*([str, str]))
        for (sound_class, constituents) in sound_classes.items():
            store.append([sound_class,
                          ', '.join(constituents)])
        super().__init__(['Class', 'Constituents'],
                         store, 'Sound Classes', lambda: status_bar.add_dirty('sound_classes'))

    def sound_classes(self):
        return {row[0]: [x.strip() for x in row[1].split(',')]
                for row in self.store}

# given a quirks object, construct a widget that allows users to
# specify exceptions.
class QuirksSheet(ExpandableSheet, DisableableRowsMixin):
    def __init__(self, quirks, status_bar):
        store = Gtk.ListStore(*([str, str, str, str, str, bool]))
        for quirk in quirks.values():
            store.append([quirk.language,
                          quirk.form,
                          quirk.gloss,
                          quirk.alternative,
                          quirk.notes[0] if quirk.notes else '',
                          True]) # HACK.
        super().__init__(['Language', 'Form', 'Gloss', 'Alternative', 'Notes'],
                         store, 'Exceptions', lambda: status_bar.add_dirty('exceptions'))
        self.setup_disableable_rows(self.sheet, store.get_n_columns() - 1)

    def fill(self, table):
        for row in self.store:
            if row[self.enabled_index]:
                table.add_quirk(RE.Quirk(
                    '', '', row[0], row[1], row[2], row[3],
                    '', '', [row[4]]))

    def ensure_quirk(self, language, form, gloss):
        sheet = self.sheet
        for row in sheet.store: # look for quirk first.
            if (row[0] == language and
                row[1] == form and
                row[2] == gloss):
                path = sheet.view.get_model().get_path(row.iter)
                sheet.view.set_cursor(path)
                self.set_expanded(True)
                return
        row = self.store.get_n_columns() * ['']
        row[0] = language
        row[1] = form
        row[2] = gloss
        row[self.enabled_index] = True
        sheet.store.append(row)
        path = sheet.view.get_model().get_path(sheet.store[-1].iter)
        sheet.view.set_cursor(path)
        self.set_expanded(True)
        sheet.on_change()

class ParameterWidget(Gtk.Box):
    def __init__(self, parameters, status_bar):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.correspondence_sheet = CorrespondenceSheet(parameters.table, status_bar)
        self.rule_sheet = RuleSheet(parameters.table, status_bar)
        self.canon_widget = SyllableCanonWidget(parameters.syllable_canon, status_bar)
        self.quirks_sheet = QuirksSheet(parameters.table.quirks, status_bar)
        self.proto_language_name = parameters.proto_language_name
        self.mels = parameters.mels
        self.fuzzy = parameters.fuzzy
        self.add(self.canon_widget)
        self.add(self.correspondence_sheet)
        self.add(self.rule_sheet)
        self.add(self.quirks_sheet)

    def parameters(self):
        names = self.correspondence_sheet.names
        table = RE.TableOfCorrespondences('', names)
        self.correspondence_sheet.fill(table)
        self.rule_sheet.fill(table)
        self.quirks_sheet.fill(table)
        return RE.Parameters(
            table,
            self.canon_widget.syllable_canon(),
            self.proto_language_name,
            self.mels,
            self.fuzzy)

    def scroll_to(self, obj):
        if isinstance(obj, RE.Correspondence):
            self.correspondence_sheet.scroll_to_correspondence(obj)
        elif isinstance(obj, RE.Rule):
            self.rule_sheet.scroll_to_rule(obj)

    def ensure_quirk(self, form):
        if isinstance(form, RE.QuirkyForm):
            form = form.actual
        self.quirks_sheet.ensure_quirk(form.language, form.glyphs, form.gloss)

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

    def scroll_to(self, language, obj):
        for i in range(self.get_n_pages()):
            widget = self.get_nth_page(i)
            if widget.proto_language_name == language:
                self.set_current_page(i)
                widget.scroll_to(obj)
                break

    def ensure_quirk(self, language, form):
        for i in range(self.get_n_pages()):
            widget = self.get_nth_page(i)
            if widget.proto_language_name == language:
                self.set_current_page(i)
                widget.ensure_quirk(form)
                break

class SetsWidget(Gtk.Box):
    def __init__(self,
                 on_id_clicked=lambda l, id: None,
                 ensure_quirk_callback=lambda m, l, form: None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.window = Pane(vexpand=True)

        self.store = Gtk.TreeStore(str, str, int, str, object, object, object)

        # --- Search bar ---
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Filter by attested:")
        label.set_halign(Gtk.Align.START)
        self.pack_start(search_box, False, False, 6)

        self.lang_entry = Gtk.Entry(placeholder_text="Language")
        self.form_entry = Gtk.Entry(placeholder_text="Form")
        self.gloss_entry = Gtk.Entry(placeholder_text="Gloss")

        self.clear_button = Gtk.Button(label="Clear")

        search_box.pack_start(label, False, False, 0)
        search_box.pack_start(self.lang_entry, False, False, 0)
        search_box.pack_start(self.form_entry, False, False, 0)
        search_box.pack_start(self.gloss_entry, False, False, 0)
        search_box.pack_start(self.clear_button, False, False, 0)

        self.result_label = Gtk.Label(label="0 / 0 results")
        self.result_label.set_halign(Gtk.Align.START)
        search_box.pack_start(self.result_label, False, False, 6)

        def on_clear_search(button):
            self.lang_entry.set_text("")
            self.form_entry.set_text("")
            self.gloss_entry.set_text("")
            self.filter.refilter()

        self.clear_button.connect("clicked", on_clear_search)

        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self._filter_func)
        self.sorted = Gtk.TreeModelSort(model=self.filter)

        def on_changed():
            self.filter.refilter()
            self.update_result_count()

        # Instant filtering
        self.lang_entry.connect("changed", lambda e: on_changed())
        self.form_entry.connect("changed", lambda e: on_changed())
        self.gloss_entry.connect("changed", lambda e: on_changed())

        self.view = Gtk.TreeView.new_with_model(self.sorted)
        view = self.view

        # ID cell fun.
        def id_cell_fun(column, cell, model, iter_, data=None):
            ids = model.get_value(iter_, 4)
            text = model.get_value(iter_, 1)
            # highlight children as a link
            if ids:
                true_text = text.split()
                markup = ' '.join(
                    f'<span font_family="monospace" foreground="blue" underline="single">{c_str}</span>'
                    for c_str in true_text
                )
                cell.set_property("markup", markup)
            else:
                cell.set_property("text", text)

        for (i, column_name) in enumerate(['Reconstructions', 'IDs', '# attestations', 'mel']):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_name, renderer, text=i)
            column.set_sort_column_id(i)
            column.set_resizable(True)
            column.renderer = renderer
            if column_name == 'IDs':
                column.set_cell_data_func(renderer, id_cell_fun)
            elif column_name == '# attestations':
                column.set_alignment(1.0)
                renderer.set_alignment(1.0, 1.0)
                def render_attestation_count(column, cell, model, iter, data):
                    value = model.get_value(iter, 2)
                    cell.set_property("text", "" if value == 0 else str(value))
                column.set_cell_data_func(renderer, render_attestation_count)
            self.view.append_column(column)
        self.window.add(self.view)
        self.add(self.window)

        def on_right_button_press(view, event):
            # Find which row was clicked
            path_info = view.get_path_at_pos(int(event.x), int(event.y))
            if path_info is not None:
                path, col, cellx, celly = path_info
                view.grab_focus()
                view.set_cursor(path, col, 0)

                # Get the iter & model
                model = view.get_model()
                iter_ = model.get_iter(path)
                parent_language = model.get_value(iter_, 5)
                form = model.get_value(iter_, 6)

                # Build the popup menu dynamically
                menu = Gtk.Menu()

                item_inspect = Gtk.MenuItem(label="Make new/find existing exception.")
                item_inspect.connect("activate",
                                     lambda m, form: ensure_quirk_callback(
                                         parent_language, form),
                                     form)
                menu.append(item_inspect)

                menu.show_all()
                menu.popup_at_pointer(event)
                return True  # stop other handlers
            return False

        def on_button_press(view, event):
            # Right click
            if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
                return on_right_button_press(view, event)
            # Left click
            elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
                # Convert click coordinates to tree path
                x = int(event.x)
                y = int(event.y)
                pthinfo = view.get_path_at_pos(x, y)
                if pthinfo is not None:
                    path, col, cellx, celly = pthinfo
                    if col.get_title() != "IDs":
                        return False
                    model = view.get_model()
                    iter_ = model.get_iter(path)
                    text = model.get_value(iter_, 1)
                    target = model.get_value(iter_, 4)
                    if target is None:
                        return False

                    # FIXME: This code is such a giant hack.

                    true_text = text.split()
                    markup = ' '.join(
                        f'<span font_family="monospace" foreground="blue" underline="single">{c_str}</span>'
                        for c_str in true_text
                    )

                    # Create a Pango layout that understands the markup
                    layout = view.create_pango_layout("")
                    layout.set_markup(markup, -1)
                    total_width, _ = layout.get_pixel_size()
                    if len(text) == 0:
                        return False
                    char_width = total_width / len(text)

                    language = model.get_value(iter_, 5)
                    cumulative = 0
                    ids = text.split()
                    for i, id_str in enumerate(ids):
                        start = cumulative
                        end = cumulative + len(id_str) * char_width
                        if start <= cellx <= end:
                            print(language, target[i])
                            on_id_clicked(language, target[i])
                            break
                        cumulative = end + char_width  # +1 for the space

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
                target = model.get_value(iter_, 4)
                if col.get_title() == "IDs":
                    if target is not None:  # child row
                        window.set_cursor(Gdk.Cursor.new(Gdk.CursorType.HAND2))
                        return False
                window.set_cursor(None)  # reset
            return False

        view.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        view.connect("button-press-event", on_button_press)
        view.connect("motion-notify-event", on_motion_notify)

    def update_result_count(self):
        total = sum(1 for _ in self.store)
        filtered = sum(1 for row in self.filter if self._filter_func(self.filter, row.iter))
        self.result_label.set_text(f"{filtered} / {total} results")

    def _filter_func(self, model, iter_, data=None):
        lang_query = self.lang_entry.get_text().strip().lower()
        form_query = self.form_entry.get_text().strip().lower()
        gloss_query = self.gloss_entry.get_text().strip().lower()

        # Pull the original form object
        form = model.get_value(iter_, 6)
        if isinstance(form, RE.ProtoForm):
            for support in form.attested_support:
                if ((lang_query == '' or (lang_query in support.language.lower()))
                    and
                    (form_query == '' or (form_query in support.glyphs.lower()))
                    and
                    (gloss_query == '' or (gloss_query in support.gloss.lower()))):
                    return True
            return False

        return True

    def populate(self, proto_lexicon):
        """Populate this store with forms."""
        self.store.clear()

        def store_row(parent, form, parent_language):
            if isinstance(form, RE.ProtoForm):
                language = form.language
                row = self.store.append(
                    parent=parent,
                    row=['*' + form.glyphs if parent is None else str(form),
                         ' '.join(RE.correspondences_as_ids(form.correspondences).split()),
                         len(form.attested_support),
                         str(form.mel),
                         form.correspondences,
                         language,
                         form])
                # TODO: Sort by the language order in the table of
                # correspondences.
                for supporting_form in sorted(form.supporting_forms,
                                              key=lambda f: (f.language, f.glyphs)):
                    store_row(row, supporting_form, language)
            elif isinstance(form, RE.AlternateForm):
                if isinstance(form.actual, RE.ModernForm):
                    row = self.store.append(parent=parent, row=[str(form), '', 0, '', None,
                                                                parent_language,
                                                                form])
                else:
                    raise Exception('Unimplemented: Alternate form for stage0/Meso-form!')
            elif isinstance(form, RE.ModernForm):
                row = self.store.append(parent=parent, row=[str(form), '', 0, '', None,
                                                            parent_language,
                                                            form])
            elif isinstance(form, RE.Stage0Form):
                row = self.store.append(parent=parent, row=[str(form), '', 0, '', None,
                                                            parent_language,
                                                            form])
                last_applied = None
                ids = None
                for (stage, rules_applied) in form.history:
                    if last_applied:
                        self.store.append(parent=row,
                                          row=["> *" + stage,
                                               f"{ids}",
                                               0,
                                               "",
                                               last_applied,
                                               parent_language,
                                               form])
                    last_applied = rules_applied
                    ids = " ".join([rule.id for rule in rules_applied])
                self.store.append(parent=row,
                                  row=["> " + str(form.modern),
                                       f"{ids}",
                                       0,
                                       "",
                                       last_applied,
                                       parent_language,
                                       form])
            else:
                raise Exception('Why is there no form here?')

        for form in proto_lexicon.forms:
            store_row(None, form, None)

        self.update_result_count()

    def scroll_to_form(self, form):
        """Scroll and select the row with the given form."""
        treeview = self.view
        model = treeview.get_model()

        for row in model:
            if row[6] == form:
                path = model.get_path(row.iter)
                treeview.scroll_to_cell(path, None, True, 0.5, 0.0)
                treeview.set_cursor(path)
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

class IsolatesWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.window = Pane(vexpand=True)
        self.store = Gtk.TreeStore(str, str, str)

        view = Gtk.TreeView.new_with_model(self.store)

        view.set_search_equal_func(all_columns_search_func, None)
        view.set_search_column(0)

        for i, column_title in enumerate(['Language', 'Form', 'Gloss']):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, cell, text=i)
            column.set_sort_column_id(i)
            column.set_resizable(True)
            view.append_column(column)
        self.window.add(view)
        self.add(self.window)

    def populate(self, isolates):
        self.store.clear()

        def store_row(parent, form):
            if isinstance(form, RE.ProtoForm):
                row = self.store.append(
                    parent=parent,
                    row=[str(form) + ' ' + str(form.mel), '', ''])
                for supporting_form in form.supporting_forms:
                    store_row(row, supporting_form)
            elif isinstance(form, RE.Stage0Form):
                row = self.store.append(parent=parent, row=[str(form), '', ''])
                ids = None
                for (stage, rules_applied) in form.history:
                    if ids:
                        self.store.append(parent=row,
                                          row=["> *" + stage,
                                               f"{ids}",
                                               ""])
                    ids = ",".join([rule.id for rule in rules_applied])
                self.store.append(parent=row,
                                  row=["> " + str(form.modern),
                                       f"{ids}",
                                       ""])

        for (form, recons) in isolates.items():
            assert isinstance(form, (RE.ModernForm, RE.AlternateForm))
            row = self.store.append(parent=None, row=[form.language,
                                                      '‡' + form.glyphs if isinstance(form, RE.QuirkyForm)
                                                      else form.glyphs,
                                                      form.gloss])
            for recon in recons:
                store_row(row, recon)

class FailedParsesWidget(Pane):
    def __init__(self):
        super().__init__(vexpand=True, hexpand=True)
        self.store = Gtk.ListStore(str, str, str)

        view = Gtk.TreeView.new_with_model(self.store)

        view.set_search_equal_func(all_columns_search_func, None)
        view.set_search_column(0)

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
                '‡' + failed_parse.glyphs if isinstance(failed_parse, (RE.QuirkyForm))
                else failed_parse.glyphs,
                failed_parse.gloss
                if isinstance(failed_parse, (RE.Stage0Form,
                                             RE.ModernForm,
                                             RE.AlternateForm))
                else ''
            ])

class CorrespondenceIndexWidget(Gtk.Box):
    def __init__(self, on_form_clicked, languages):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
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

        view.set_search_equal_func(all_columns_search_func, None)
        view.set_search_column(0)

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

    # Show a brief summary of the correspondence.
    def display_correspondence(self, c):
        context = RE.context_as_string(c.context)
        if context != '':
            context = f'/ {context}'
        return f'{c.id}: ({", ".join(c.syllable_types)}) *{c.proto_form} {context}'

    def populate(self, correspondence_index):
        self.store.clear()
        for (correspondence, forms) in correspondence_index.items():
            row = self.store.append(parent=None,
                                    row=[self.display_correspondence(correspondence),
                                         len(forms),
                                         None])
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
                ("—", None, None),
                ("Quit", Gtk.main_quit, None),
            ],
            "Edit": [
                ("Edit lexical data...", self.window.open_lexicon_editor, None),
            ],
            "View": [
                ("Show quick compare...", self.window.show_quick_compare, None),
                ("—", None, None),
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
        self.dirtied = set()

    def set_message(self, text):
        self.message_label.set_text(text)

    def add_dirty(self, thing):
        self.dirtied.add(thing)
        self.dirty_label.set_text("● Unsaved changes")
        self.dirty_label.get_style_context().add_class("dirty")

    def clear_dirty(self):
        self.dirtied.clear()
        self.dirty_label.set_text("")
        self.dirty_label.get_style_context().remove_class("dirty")

    def lexicons_changed(self):
        return 'lexicons' in self.dirtied

    def parameters_changed(self):
        return 'lexicons' in self.dirtied

class DownstreamWidget(Gtk.Box):
    def __init__(self):
        Gtk.Window.__init__(self, title='The Reconstruction Engine',
                            default_height=800, default_width=1400)

class DiffWidget(Gtk.Box):
    def __init__(self, on_id_clicked=lambda l, id: None,
                 ensure_quirk_callback=lambda m, id: None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.pack_start(paned, True, True, 0)

        self.sets_lost_widget = SetsWidget(on_id_clicked=on_id_clicked,
                                           ensure_quirk_callback=ensure_quirk_callback)
        self.sets_gained_widget = SetsWidget(on_id_clicked=on_id_clicked,
                                             ensure_quirk_callback=ensure_quirk_callback)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.left_label = Gtk.Label()
        left_box.pack_start(self.left_label, False, False, 4)
        left_box.pack_start(self.sets_lost_widget, True, True, 0)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.right_label = Gtk.Label()

        right_box.pack_start(self.right_label, False, False, 4)
        right_box.pack_start(self.sets_gained_widget, True, True, 0)

        paned.pack1(left_box, resize=True, shrink=False)
        paned.pack2(right_box, resize=True, shrink=False)

        self.set_label_counts(0, 0)

    def set_label_counts(self, lost_count, gained_count):
        self.left_label.set_markup(f"<b>Sets lost since last run ({lost_count})</b>")
        self.left_label.set_justify(Gtk.Justification.CENTER)
        self.right_label.set_markup(f"<b>Sets gained in new run ({gained_count})</b>")
        self.right_label.set_justify(Gtk.Justification.CENTER)

    def populate(self, lost, gained):
        self.sets_lost_widget.populate(lost)
        self.sets_gained_widget.populate(gained)
        self.set_label_counts(len(lost.forms), len(gained.forms))

class LexiconEditorWindow(Gtk.Window):
    def __init__(self, parent, lexicons_widget, status_bar):
        super().__init__(title="Lexicon Editor", transient_for=parent, destroy_with_parent=True)
        self.set_default_size(800, 600)

        # Main vertical layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Reuse the existing LexiconsWidget, but display *shared stores*
        # so that editing here updates the main window’s view.
        shared_notebook = Gtk.Notebook()
        vbox.pack_start(shared_notebook, True, True, 0)

        for page_num in range(lexicons_widget.get_n_pages()):
            orig_page = lexicons_widget.get_nth_page(page_num)
            assert isinstance(orig_page, LexiconWidget)
            # Create a Sheet with the *same* shared store.
            sheet = Sheet(["Form", "Gloss"], orig_page.store,
                          name=orig_page.language,
                          on_change=lambda: status_bar.add_dirty('lexicons'))
            scrolled = Gtk.ScrolledWindow()
            scrolled.add(sheet)
            shared_notebook.append_page(scrolled, Gtk.Label(label=orig_page.language))

        self.show_all()

class REWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='The Reconstruction Engine',
                            default_height=800, default_width=1400)
        sys.excepthook = self.dialog_excepthook
        # Track zoom state
        self.zoom_level = 1.0

        # Keyboard shortcuts
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        # Cache the last proto-lexicon generated for quick compare.
        self.last_proto_lexicon = None

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

        # persistent diff window
        self.diff_window = Gtk.Window(title="Diff Viewer", transient_for=self, destroy_with_parent=True)
        self.diff_window.set_default_size(800, 600)
        self.diff_window.hide()

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
            self.isolates_widget.populate(RE.extract_isolates(proto_lexicon))
            self.failed_parses_widget.populate(statistics.failed_parses)
            self.correspondence_index_widget.populate(statistics.correspondence_index)
            if self.last_proto_lexicon:
                (sets_lost, sets_gained) = RE.compare_proto_lexicons_modulo_details(
                    self.last_proto_lexicon,
                    proto_lexicon)
                self.diff_widget.populate(sets_lost, sets_gained)
            self.last_proto_lexicon = proto_lexicon
        out = sys.stdout
        sys.stdout = self.log_widget.get_buffer()
        try:
            proto_lexicon = RE.upstream_tree(
                self.settings.upstream_target,
                self.settings.upstream,
                self.parameters_widget.parameter_tree(),
                self.lexicons_widget.lexicons(),
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
        for child in self.diff_window.get_children():
            self.diff_window.remove(child)

    # Load lexicons and parameters into widgets.
    def load(self, attested_lexicons, initial_parameter_tree):
        # Clear old widgets.
        self.clear_widgets()
        self.status_bar.clear_dirty()

        # Input widgets
        self.lexicons_widget = LexiconsWidget(attested_lexicons.values())
        self.parameters_widget = ParameterTreeWidget(initial_parameter_tree, self.status_bar)

        # Output widgets
        self.sets_widget = SetsWidget(on_id_clicked=self.parameters_widget.scroll_to,
                                      ensure_quirk_callback=self.parameters_widget.ensure_quirk)
        self.log_widget = LogWidget()
        self.isolates_widget = IsolatesWidget()
        self.failed_parses_widget = FailedParsesWidget()
        self.correspondence_index_widget = CorrespondenceIndexWidget(
            self.sets_widget.scroll_to_form,
            [lexicon.language for lexicon in attested_lexicons.values()])

        # Diff widgets
        self.diff_widget = DiffWidget(on_id_clicked=self.parameters_widget.scroll_to)
        self.diff_window.add(self.diff_widget)

        # Upstream button.
        upstream_button = make_clickable_button("Batch All Upstream",
                                                lambda w: self.on_batch_all_upstream())

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

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(self.sets_widget)
        box.add(upstream_button)
        self.right_pane.add1(box)

        stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        stats_box.pack_start(stack_switcher, False, False, 0)
        stats_box.pack_start(self.statistics_stack, True, True, 0)
        self.right_pane.add2(stats_box)  # add the stack here

        self.left_pane.add2(self.parameters_widget)

        self.show_all()

    # Initially load widgets from a settings file.
    def open_from_settings(self, settings):
        self.on_disk_lexicons = read.read_attested_lexicons(settings)

        self.settings = settings

        initial_parameter_tree = {language:
                                  read.read_correspondence_file(
                                      os.path.join(settings.directory_path,
                                                   correspondence_filename),
                                      language,
                                      settings.upstream[language],
                                      language,
                                      settings.mel_filename,
                                      settings.fuzzy_filename)
                                  for (language, correspondence_filename)
                                  in settings.proto_languages.items()
                                  }
        self.load(self.on_disk_lexicons, initial_parameter_tree)

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
        fuzzy = None if selection['fuzzy'] == 'None' else selection['fuzzy']
        settings = read.read_settings_file(parameters_file,
                                           mel=mel,
                                           fuzzy=fuzzy,
                                           recon=selection['recon'])
        # dummy an arg object for load hooks. FIXME
        dummy.mel = mel
        dummy.fuzzy = fuzzy
        dummy.recon = selection['recon']
        load_hooks.load_hook(projects.projects[project], dummy, settings)
        self.status_bar.set_message(f'Opened project {project} from projects directory.')
        self.open_from_settings(settings)

    def create_checkpoint(self, widget):
        dialog = CheckpointDialog(self, action_type="save")
        if dialog.run() == Gtk.ResponseType.OK:
            checkpoint_path = dialog.get_filename()
            print(f"Creating checkpoint at: {checkpoint_path}")
            checkpoint_data = checkpoint.CheckpointData(self.lexicons_widget.lexicons(),
                                                        self.parameters_widget.parameter_tree())
            checkpoint.save_checkpoint_to_path(checkpoint_path, checkpoint_data)
            self.status_bar.set_message(f'Created checkpoint: {checkpoint_path}')
            self.status_bar.clear_dirty()
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

    def show_quick_compare(self, widget):
        def _on_window_close(window, event):
            window.hide()
            return True # prevent destruction
        self.diff_window.show_all()
        self.diff_window.connect("delete-event", _on_window_close)

    def save_project(self, widget):
        for (proto_language_name, parameters) in self.parameters_widget.parameter_tree().items():
            serialize.serialize_correspondence_file(
                os.path.join(
                    self.settings.directory_path,
                    self.settings.proto_languages[proto_language_name]),
                parameters)

        widget_lexicons = self.lexicons_widget.lexicons()
        for (language, widget_lexicon) in widget_lexicons.items():
            if widget_lexicon != self.on_disk_lexicons[language]:
                serialize.serialize_lexicon(
                    widget_lexicon,
                    os.path.join(self.settings.directory_path,
                                 self.settings.attested[language]))
        self.on_disk_lexicons = widget_lexicons

        self.status_bar.set_message(f'Saved project {self.project} into projects directory.')
        self.status_bar.clear_dirty()

    def open_lexicon_editor(self, widget):
        editor = LexiconEditorWindow(self, self.lexicons_widget, self.status_bar)
        editor.show_all()

    def dialog_excepthook(self, exc_type, exc_value, exc_traceback):
        """Display an error message."""
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        if issubclass(exc_type, KeyboardInterrupt):
            return
        try:
            dialog = Gtk.MessageDialog(transient_for=self,
                                       flags=0,
                                       message_type=Gtk.MessageType.ERROR,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="An unexpected error occurred.")
            text = ''.join(traceback.format_exception(exc_type,
                                                      exc_value,
                                                      exc_value.__traceback__))
            markup = f'<span font_family="monospace">{text}</span>'

            # TextView for traceback
            textview = Gtk.TextView(editable=False, cursor_visible=False)
            textview.set_wrap_mode(Gtk.WrapMode.NONE)
            buffer = textview.get_buffer()
            buffer.insert_markup(buffer.get_end_iter(), markup, -1)

            # Scrolled container
            scroller = Gtk.ScrolledWindow()
            scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroller.set_min_content_height(200)
            scroller.add(textview)

            dialog.set_default_size(800, 500)
            dialog.set_resizable(True)
            scroller.set_min_content_height(300)

            content = dialog.get_content_area()
            content.pack_start(scroller, True, True, 0)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
        except Exception:
            print('Exception while displaying exception in error dialog.')

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
