# Change Database Tools

## Change Database Generator

`update-change-db.py` collects the change entries from the audit topic YAML
files (by default `docs/audit_report/changes/topics`, resolved relative to the
script's location) and creates or updates a JSON database file.

The database file is named `botan-changes.<x.y.z>.json`, where `<x.y.z>` is the
`BOTAN_VERSION` configured in `config/botan.env`. By default it is written to
`docs/database` (created if necessary). If the database file already exists,
its entries are updated in-place: entries found in the topic files replace
their previous state in the database, new entries are appended, and entries no
longer found in the topic files are deleted after asking the user for
confirmation. The confirmation prompt allows applying the answer to all
remaining absent entries ("[Y]es to all" / "[N]o to all"). With
`--non-interactive` absent entries are deleted without confirmation.

The database contains meta information about the targeted Botan version of the
audit followed by the list of change entries. Each change entry directly
reflects the structure of its YAML source entry, except that the `categories`
field is always present as a JSON list: if the YAML entry carries a
`categories` field, its comma separated tags are used; otherwise the name of
the containing topic YAML file (without the `.yml` extension) becomes the only
list entry. Additionally, each change entry carries `title` and `author`
fields, filled from the comment lines directly preceding the YAML entry (as
emitted by the auditupdate tool):

```yaml
# Fix some build issues caught by test_all_configs.py
#   Author:    @randombit
- pr: 5579
  ...
```

```json
{
  "meta": {
    "botan_version": "3.12.0",
    "botan_ref": "3.12.0",
    "botan_base_ref": "3.11.0"
  },
  "changes": [
    {
      "title": "Fix some build issues caught by test_all_configs.py",
      "author": "@randombit",
      "pr": 5579,
      "merge_commit": "13e5dbb03bb69d61d6b2f5009b58194a314966b6",
      "classification": "unspecified",
      "categories": ["uncategorized"]
    }
  ]
}
```

### Usage

```bash
python3 tools/change-db/update-change-db.py [-t TOPICS_DIR] [-d DATABASE_FILE] [-n] [-v]
```

- `-t/--topics-dir`: overrides the topic YAML input directory
- `-d/--database-file`: overrides the database file location and name
- `-n/--non-interactive`: deletes absent entries without asking for confirmation
- `-v/--verbose`: enables detailed logging

## Change Database Viewer

`render-changes-db.py` collects all JSON database files from a directory (by
default `docs/database`) and renders them into a single self-contained HTML
page with a table of all changes. The table shows the columns "Audit version"
(the targeted Botan version from the database meta information),
"Classification", "Categories", "Title / comment" (the entry's title followed
by its audit comment), "Link" (pointing to the GitHub pull request or commit,
configured via `BOTAN_REPO` in `config/botan.env`) and "Auditor". The page supports live filtering by audit version, by category, by
classification and by free text matching words of the entries' title, comment
or auditor. The version, category and classification selectors accept multiple
selections (checkbox dropdowns); values selected within one selector combine
as "or", the different filters combine as "and". An empty selection means "no
filtering".

With `--reload SECONDS` the generated page reloads itself in the given
interval, so that it picks up a rebuilt database on its own — useful together
with the watcher described below. The current filter selection and search text
are stored in the URL fragment and restored after the reload, hence the view
doesn't jump back to the unfiltered table. A pending reload is postponed while
the search field has the focus or a selector dropdown is open, so it can't
interrupt an ongoing interaction. Without `--reload` (the default) the page is
static.

### Usage

```bash
python3 tools/change-db/render-changes-db.py [-i DATABASE_DIR] [-o OUTPUT_FILE]
                                             [-r SECONDS] [-v]
```

- `-i/--database-dir`: overrides the database input directory
- `-o/--output`: overrides the HTML output file (default:
  `botan-changes.html` in the database directory)
- `-r/--reload`: lets the page reload itself every SECONDS (0 disables it,
  which is the default)
- `-v/--verbose`: enables detailed logging

## Change Database Watcher

`watch-changes-db.py` continually monitors the topic YAML files (by default
`docs/audit_report/changes/topics`) and keeps the database and its HTML view up
to date. On every change of the YAML files it runs `update-change-db.py`
followed by `render-changes-db.py`. If `update-change-db.py` reports an error
(for instance because a YAML file is momentarily incomplete or malformed),
`render-changes-db.py` is *not* invoked and the watcher simply waits for the
next change of the YAML files.

Changes are detected by polling the files' modification time and size, so no
additional Python packages are required. Newly added and removed topic files
are noticed as well. After a change is seen, the watcher waits for the files to
settle before running the scripts, so that editors writing a file in several
steps don't trigger a run on half-written content.

Both scripts inherit the terminal, hence the deletion confirmation prompt of
`update-change-db.py` works as usual. Pass `--non-interactive` to delete absent
entries without confirmation, which is what you want when the watcher runs
unattended. Stop the watcher with Ctrl+C.

The watcher renders the page with a self-reload of 5 seconds by default, so
that a browser showing the page picks up the rebuilt view without manual
reloading. Use `--reload` to change the interval or `--reload 0` to render a
static page.

### Usage

```bash
python3 tools/change-db/watch-changes-db.py [-t TOPICS_DIR] [-d DATABASE_FILE]
                                            [-i DATABASE_DIR] [-o OUTPUT_FILE]
                                            [-n] [-r SECONDS] [--interval SECONDS]
                                            [--no-initial-run] [-v]
```

- `-t/--topics-dir`: overrides the watched topic YAML directory
- `-d/--database-file`: passed on to `update-change-db.py`
- `-i/--database-dir`: passed on to `render-changes-db.py` (defaults to the
  directory of `--database-file`)
- `-o/--output`: passed on to `render-changes-db.py`
- `-n/--non-interactive`: passed on to `update-change-db.py`
- `-r/--reload`: self-reload interval of the rendered page in seconds
  (default: 5.0, 0 renders a static page)
- `--interval`: seconds between checks for changes (default: 1.0)
- `--no-initial-run`: don't update and render once on startup, wait for the
  first change instead
- `-v/--verbose`: enables detailed logging, also for the invoked scripts
