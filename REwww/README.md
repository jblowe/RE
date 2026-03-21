# REwww — The Reconstruction Engine Web Interface

REwww is a Flask-based web front-end for the Reconstruction Engine (RE).
It lets you configure and run upstream reconstructions, inspect results,
and edit correspondence tables, MEL files, and fuzzy-match rules — all
without touching the command line.

---

## Starting the server

```bash
cd REwww
python app.py                    # default: http://127.0.0.1:5001
python app.py --port 5001 --debug
python app.py --host 0.0.0.0    # expose to local network
```

Then open `http://127.0.0.1:5001` in your browser.

---

## Essential workflow

> **Select a project → select parameters → click Run → review results → edit as needed → rinse and repeat.**

1. On the **Projects** tab, choose your correspondence file (Recon), optionally a MEL and/or Fuzzy file, optionally an upstream specification, and click **Run**.
2. The **Log** tab appears and streams the run output. When the run finishes the badge turns green and you land on the **Sets** tab.
3. Browse results across **Sets**, **Stats**, **Parameters**, and **Lexicons**.
4. Use the **Edit** buttons on Parameters, MEL, and Fuzzy tabs to make corrections in-place and **Save**.
5. Click **Run** again on the Projects tab to re-run with the updated files.

---

## File layout

```
REwww/
  app.py          ← Flask app: path setup, Blueprint registration, entry point
  xslt.py         ← XSLT/XML rendering helpers
  routes.py       ← all HTTP route handlers (Blueprint)
  templates/
    index.html          ← page skeleton (includes partials below)
    _head.html          ← <head> tag with CSS styles
    _projects_pane.html ← Projects tab HTML (view + edit tables)
    _scripts.html       ← all client-side JavaScript
    about.html          ← About panel content
  static/asset/   ← Bootstrap, Font Awesome, reconengine.css, jQuery
```

The server reads project locations from `../projects.toml` (relative to
`REwww/`). Paths may be absolute or relative to that file.

---

## Tabs

### Projects

The landing tab. One row per project defined in `projects.toml`.

```
┌────────────┬──────────────┬──────────┬──────────┬──────────────────────────────┬────────┐
│ Project    │ Recon        │ MEL      │ Fuzzy    │ Upstream                     │ Action │
├────────────┼──────────────┼──────────┼──────────┼──────────────────────────────┼────────┤
│ ROMANCE    │ [dropdown ▼] │ [drop ▼] │ [drop ▼] │ [text: PIWR: PWR, it; ...]   │ [Run]  │
│ VANUATU    │ [dropdown ▼] │ N/A      │ N/A      │                              │ [Run]  │
└────────────┴──────────────┴──────────┴──────────┴──────────────────────────────┴────────┘
```

**Columns:**
- **Recon** — correspondence table file (`*correspondences.xml`). Required.
- **MEL** — Meaning/Etymology List file (`*.mel.xml`). Optional; enables the MEL tab after a run.
- **Fuzzy** — fuzzy-match override file (`*.fuz.xml`). Optional; enables the Fuzzy tab after a run.
- **Upstream** — override the proto-language hierarchy for this run. Leave blank to use the project default. Format: `Proto: Lg1, Lg2; SubProto: Lg3`.
- **Run** — starts the reconstruction in a background thread and switches to the Log tab.

**Toolbar buttons:**
- **Edit** — opens an editable table where you can add/remove projects and change their directory paths. Saves to `projects.toml`.
- **Refresh** — re-scans project directories for correspondence, MEL, and fuzzy files without reloading the page.

---

### Log

Appears automatically when a run starts. Shows live stdout from the RE engine as it processes the lexicons. A status badge shows `running`, `done`, or `error`.

```
┌─ Run log ── [done] ────────────────────────────────────────────────────┐
│ Reading settings for ROMANCE...                                         │
│ Loading lexicon: fr (512 entries)                                       │
│ Loading lexicon: pt (489 entries)                                       │
│ ...                                                                     │
│ Sets computed: 347                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

On error the full Python traceback is appended in red.

---

### Sets

The main output: cognate sets grouped by proto-form. Two display modes:

- **Tabular** (default) — compact sortable table, one set per row.
- **Paragraph** — richer, one set per block with member words and glosses.

Click any column header to sort. Click again to reverse.

---

### Stats

Run statistics: number of sets, isolates, parse failures, coverage by language, and which correspondence rows were used. Rendered from the `*upstream.statistics.xml` output file via `stats2html.xsl`.

---

### Parameters

The Table of Correspondences (ToC) used in the run. Three sub-modes toggled by toolbar buttons:

- **View** (default) — read-only rendering of the correspondence table(s).
- **Freq** — same table annotated with how many sets each correspondence row was used in (row-level) and how many sets included each modern language reflex (cell-level). Useful for spotting unused or overused rules.
- **Edit** — renders the file as an interactive HTML form. Edit proto-forms, reflex segments, and context conditions directly. Click **Save** to write back to the XML file. Click **Cancel** to discard changes.

---

### Lexicons

The attested lexicon files used in the run, one section per language. Two display modes (same as Sets: Paragraph / Tabular).

---

### MEL _(conditional)_

Appears only if a MEL file was selected. Shows the Meaning/Etymology List — the semantic groupings that guide cognate matching.

- **Edit** — inline edit form for MEL entries (id and comma-separated glosses).
- **Save / Cancel** — write back or discard.

---

### Fuzzy _(conditional)_

Appears only if a Fuzzy file was selected. Shows the fuzzy-match override rules (dialect, from-segments, to-segment).

- **Edit / Save / Cancel** — same pattern as MEL.

---

## Editing workflow detail

All three editable files (Parameters/ToC, MEL, Fuzzy) follow the same pattern:

1. Run the project so a result set exists (Edit buttons are hidden until then).
2. Switch to the relevant tab and click **Edit**. The view is replaced by an interactive form generated by an XSLT stylesheet (`toc2html-edit.xsl`, `mel2html-edit.xsl`, `fuzzy2html-edit.xsl`).
3. Make changes in the form fields.
4. Click **Save** — the browser POSTs the form data to `/api/save_toc`, `/api/save_mel`, or `/api/save_fuz`. The server reconstructs the XML and writes it back to disk.
5. Switch back to Projects and click **Run** to see the effect of your edits.

---

## API summary

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Main page |
| `/api/projects` | GET | Re-scan and return project file lists as JSON |
| `/api/run` | POST | Start an upstream run; returns `run_id` |
| `/api/poll/<run_id>` | GET | Poll run status and log |
| `/api/tab/<run_id>/<tab>` | GET | Rendered HTML for a result tab (`?mode=…`) |
| `/api/raw/<run_id>/<tab>` | GET | Raw XML source for a file |
| `/api/save/<run_id>/<tab>` | POST | Save raw XML (well-formedness checked) |
| `/api/save_toc/<run_id>` | POST | Save correspondences from edit-form fields |
| `/api/save_mel/<run_id>` | POST | Save MEL from edit-form fields |
| `/api/save_fuz/<run_id>` | POST | Save fuzzy file from edit-form fields |
| `/api/save_projects` | POST | Rewrite `projects.toml` |

---

## XSLT stylesheets

Stylesheets in `../styles/` used by REwww:

| Stylesheet | Used for |
|---|---|
| `toc2html-view.xsl` | Parameters tab — view mode |
| `toc2html-edit.xsl` | Parameters tab — edit mode |
| `toc2html-freq.xsl` | Parameters tab — freq mode |
| `params2html-view.xsl` | Parameters tab (legacy `parameters.xml` files) |
| `sets2html.xsl` | Sets tab — paragraph mode |
| `sets2tabular.xsl` | Sets tab — tabular mode |
| `stats2html.xsl` | Stats tab |
| `lexicon2html.xsl` | Lexicons tab — paragraph mode |
| `lexicon2table.xsl` | Lexicons tab — tabular mode |
| `mel2html.xsl` | MEL tab — view mode |
| `mel2html-edit.xsl` | MEL tab — edit mode |
| `fuzzy2html.xsl` | Fuzzy tab — view mode |
| `fuzzy2html-edit.xsl` | Fuzzy tab — edit mode |


---

## Dependencies

```
pip install -r requirements.txt
```

Key packages: `flask`, `lxml`. See `../requirements.txt` for the full list.
