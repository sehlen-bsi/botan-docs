#!/usr/bin/env python3

"""
Renders the JSON change database files into a self-contained HTML page.

By default all JSON database files in docs/database (relative to this script's
location in the repository) are collected into a single table that can be
filtered live by category, classification and free text on title and comment.
"""

import argparse
import json
import logging
import os
import re
import sys
from glob import glob


def repository_root() -> str:
    this_path = os.path.dirname(os.path.realpath(__file__))
    expected_parents = ["change-db", "tools"]
    for p in expected_parents:
        if not os.path.basename(this_path) == p:
            raise RuntimeError(f"view-changes-db.py resides in an unexpected location: {__file__}")
        this_path = os.path.dirname(this_path)
    return this_path


def github_repo() -> str:
    """ The GitHub repository referenced by the change links, as configured in
        config/botan.env (with a fallback for standalone usage). """
    try:
        config_file = os.path.join(repository_root(), "config", "botan.env")
        cfgpattern = re.compile(r"(^[a-zA-Z_0-9]+)=\"?([^\"]+)\"?\n$")
        with open(config_file, encoding="utf-8") as cfg:
            for line in cfg.readlines():
                match = cfgpattern.match(line)
                if match and match.group(1) == "BOTAN_REPO":
                    return match.group(2)
    except (RuntimeError, OSError):
        pass
    return "randombit/botan"


def load_databases(database_dir: str) -> list[dict]:
    database_files = sorted(glob(os.path.join(database_dir, "*.json")))
    if not database_files:
        raise RuntimeError(f"No JSON database files found in: {database_dir}")

    rows = []
    for database_file in database_files:
        with open(database_file, encoding="utf-8") as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError as ex:
                raise RuntimeError(f"Failed to parse '{database_file}': {ex}") from ex
        version = db.get('meta', {}).get('botan_version', '?')
        for entry in db.get('changes', []):
            rows.append({
                "version": version,
                "title": entry.get('title'),
                "classification": entry.get('classification', 'unspecified'),
                "categories": entry.get('categories', []),
                "comment": entry.get('comment'),
                "auditer": entry.get('auditer'),
                "pr": entry.get('pr'),
                "commit": entry.get('commit'),
            })
        logging.info("Read %d change entries from: %s", len(db.get('changes', [])), database_file)
    return rows


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Botan Audit Changes</title>
<style>
  :root {
    color-scheme: light dark;
    --border: #d0d4da;
    --head-bg: #eceff3;
    --row-alt: #f6f8fa;
    --muted: #667085;
  }
  @media (prefers-color-scheme: dark) {
    :root { --border: #3a3f46; --head-bg: #23272d; --row-alt: #1d2126; --muted: #98a2b3; }
  }
  body { font-family: system-ui, sans-serif; margin: 1.5rem; }
  h1 { font-size: 1.4rem; }
  .filters { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem; align-items: end; }
  .filters label { display: block; font-size: 0.8rem; color: var(--muted); margin-bottom: 0.2rem; }
  .filters input[type="search"] { padding: 0.35rem 0.5rem; font-size: 0.9rem; min-width: 18rem; }
  .filter details { position: relative; }
  .filter summary { list-style: none; cursor: pointer; user-select: none; font-size: 0.9rem;
                    padding: 0.35rem 0.5rem; border: 1px solid var(--border); border-radius: 4px;
                    min-width: 9rem; }
  .filter summary::after { content: " \\25be"; color: var(--muted); }
  .filter .options { position: absolute; top: calc(100% + 2px); left: 0; z-index: 10;
                     background: Canvas; border: 1px solid var(--border); border-radius: 4px;
                     padding: 0.4rem 0.6rem; max-height: 16rem; overflow-y: auto; }
  .filter .options label { display: flex; align-items: center; gap: 0.35rem; font-size: 0.9rem;
                           color: inherit; white-space: nowrap; margin: 0.15rem 0; }
  .filter .options input[type="checkbox"] { margin: 0; }
  #count { color: var(--muted); font-size: 0.85rem; margin-bottom: 0.5rem; }
  table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
  th, td { border: 1px solid var(--border); padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; }
  th { background: var(--head-bg); position: sticky; top: 0; }
  tbody tr:nth-child(even) { background: var(--row-alt); }
  td.comment { white-space: pre-wrap; max-width: 40rem; }
  td.comment .title { font-style: italic; color: var(--muted); }
  td.nowrap { white-space: nowrap; }
  mark { background: #ffdf70; color: inherit; border-radius: 2px; }
  @media (prefers-color-scheme: dark) { mark { background: #7a5d00; } }
</style>
</head>
<body>
<h1>Botan Audit Changes</h1>
<div class="filters">
  <div class="filter" id="filter-version"></div>
  <div class="filter" id="filter-category"></div>
  <div class="filter" id="filter-classification"></div>
  <div>
    <label for="text">Title / comment / auditor text</label>
    <input id="text" type="search" placeholder="filter words&hellip;">
  </div>
</div>
<div id="count"></div>
<table>
  <thead>
    <tr>
      <th>Audit version</th>
      <th>Classification</th>
      <th>Categories</th>
      <th>Title / comment</th>
      <th>Link</th>
      <th>Auditor</th>
    </tr>
  </thead>
  <tbody id="rows"></tbody>
</table>
<script>
const REPO = __REPO__;
const RELOAD_SECONDS = __RELOAD__;
const DATA = __DATA__;

const textInput = document.getElementById('text');
const tbody = document.getElementById('rows');
const count = document.getElementById('count');

const FILTERS = [
  {id: 'version', label: 'Audit version', values: row => [row.version]},
  {id: 'category', label: 'Category', values: row => row.categories},
  {id: 'classification', label: 'Classification', values: row => [row.classification]},
];

// The current filter selection is kept in the URL fragment, so that it
// survives the periodic self-reload of the page.
const RESTORED = new URLSearchParams((location.hash || '').replace(/^#/, ''));

function distinct(values) {
  return [...new Set(values)].sort((a, b) => a.localeCompare(b, undefined, {numeric: true}));
}

function buildFilter(spec) {
  const available = distinct(DATA.flatMap(spec.values));
  spec.selected = new Set((RESTORED.get(spec.id) || '').split('|')
    .filter(value => available.includes(value)));

  const container = document.getElementById('filter-' + spec.id);
  const caption = document.createElement('label');
  caption.textContent = spec.label;
  const details = document.createElement('details');
  const summary = document.createElement('summary');
  const options = document.createElement('div');
  options.className = 'options';

  function updateSummary() {
    summary.textContent = spec.selected.size === 0 ? 'All'
      : spec.selected.size <= 2 ? [...spec.selected].join(', ')
      : `${spec.selected.size} selected`;
  }
  updateSummary();

  for (const value of available) {
    const option = document.createElement('label');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = value;
    checkbox.checked = spec.selected.has(value);
    checkbox.addEventListener('change', () => {
      if (checkbox.checked) { spec.selected.add(value); } else { spec.selected.delete(value); }
      updateSummary();
      render();
    });
    option.appendChild(checkbox);
    option.appendChild(document.createTextNode(value));
    options.appendChild(option);
  }

  details.appendChild(summary);
  details.appendChild(options);
  container.appendChild(caption);
  container.appendChild(details);
}

function link(row) {
  if (row.pr !== null && row.pr !== undefined) {
    return {url: `https://github.com/${REPO}/pull/${row.pr}`, label: `GH #${row.pr}`};
  }
  if (row.commit) {
    return {url: `https://github.com/${REPO}/commit/${row.commit}`, label: row.commit.substring(0, 10)};
  }
  return null;
}

function searchTerms() {
  return textInput.value.toLowerCase().split(/\\s+/).filter(Boolean);
}

function matches(row) {
  for (const spec of FILTERS) {
    if (spec.selected.size && !spec.values(row).some(value => spec.selected.has(value))) {
      return false;
    }
  }
  const haystack = `${row.title || ''} ${row.comment || ''} ${row.auditer || ''}`.toLowerCase();
  return searchTerms().every(word => haystack.includes(word));
}

function matchRanges(text, terms) {
  const lower = text.toLowerCase();
  const ranges = [];
  for (const term of terms) {
    for (let idx = lower.indexOf(term); idx !== -1; idx = lower.indexOf(term, idx + 1)) {
      ranges.push([idx, idx + term.length]);
    }
  }
  ranges.sort((a, b) => a[0] - b[0]);
  const merged = [];
  for (const range of ranges) {
    const last = merged[merged.length - 1];
    if (last && range[0] <= last[1]) { last[1] = Math.max(last[1], range[1]); }
    else { merged.push(range); }
  }
  return merged;
}

function highlighted(text) {
  const terms = searchTerms();
  const ranges = text && terms.length ? matchRanges(text, terms) : [];
  if (!ranges.length) {
    return text;
  }
  const fragment = document.createDocumentFragment();
  let pos = 0;
  for (const [start, end] of ranges) {
    if (start > pos) {
      fragment.appendChild(document.createTextNode(text.slice(pos, start)));
    }
    const mark = document.createElement('mark');
    mark.textContent = text.slice(start, end);
    fragment.appendChild(mark);
    pos = end;
  }
  if (pos < text.length) {
    fragment.appendChild(document.createTextNode(text.slice(pos)));
  }
  return fragment;
}

function cell(tr, content, className) {
  const td = document.createElement('td');
  if (content instanceof Node) { td.appendChild(content); } else { td.textContent = content; }
  if (className) { td.className = className; }
  tr.appendChild(td);
}

function append(parent, content) {
  if (content instanceof Node) {
    parent.appendChild(content);
  } else if (content) {
    parent.appendChild(document.createTextNode(content));
  }
}

function commentContent(row) {
  const fragment = document.createDocumentFragment();
  if (row.title) {
    const title = document.createElement('div');
    title.className = 'title';
    append(title, highlighted(row.title));
    fragment.appendChild(title);
  }
  append(fragment, highlighted(row.comment || ''));
  return fragment;
}

function render() {
  tbody.replaceChildren();
  const rows = DATA.filter(matches);
  for (const row of rows) {
    const tr = document.createElement('tr');
    cell(tr, row.version, 'nowrap');
    cell(tr, row.classification, 'nowrap');
    cell(tr, row.categories.join(', '));
    cell(tr, commentContent(row), 'comment');
    const ref = link(row);
    if (ref) {
      const a = document.createElement('a');
      a.href = ref.url;
      a.textContent = ref.label;
      a.title = row.title || '';
      cell(tr, a, 'nowrap');
    } else {
      cell(tr, '');
    }
    cell(tr, highlighted(row.auditer || ''), 'nowrap');
    tbody.appendChild(tr);
  }
  count.textContent = `${rows.length} of ${DATA.length} changes`
    + (RELOAD_SECONDS ? ` \\u00b7 reloading every ${RELOAD_SECONDS}s` : '');
}

function currentStateHash() {
  const params = new URLSearchParams();
  for (const spec of FILTERS) {
    if (spec.selected.size) { params.set(spec.id, [...spec.selected].join('|')); }
  }
  if (textInput.value) { params.set('q', textInput.value); }
  return params.toString();
}

function scheduleReload() {
  if (!RELOAD_SECONDS) {
    return;
  }
  setTimeout(() => {
    // Don't reload while the view is being operated; try again shortly.
    if (document.activeElement === textInput || document.querySelector('.filter details[open]')) {
      scheduleReload();
      return;
    }
    location.hash = currentStateHash();
    location.reload();
  }, RELOAD_SECONDS * 1000);
}

textInput.value = RESTORED.get('q') || '';
FILTERS.forEach(buildFilter);
document.addEventListener('click', event => {
  for (const details of document.querySelectorAll('.filter details[open]')) {
    if (!details.contains(event.target)) {
      details.open = false;
    }
  }
});
textInput.addEventListener('input', render);
render();
scheduleReload();
</script>
</body>
</html>
"""


def render_page(rows: list[dict], reload_seconds: float = 0) -> str:
    def embed(value):
        # '</' must not appear verbatim inside the inline <script> block
        return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')

    return (PAGE_TEMPLATE
            .replace('__RELOAD__', embed(reload_seconds))
            .replace('__REPO__', embed(github_repo()))
            .replace('__DATA__', embed(rows)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--database-dir',
                        default=os.path.join(repository_root(), "docs", "database"),
                        help="Directory containing the JSON change database files")
    parser.add_argument('-o', '--output',
                        default=None,
                        help="HTML output file (default: botan-changes.html in the database directory)")
    parser.add_argument('-r', '--reload', type=float, default=0, metavar='SECONDS',
                        help="Let the rendered page reload itself every SECONDS "
                             "(0 disables the self-reload, which is the default)")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Enable detailed logging")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s %(message)s',
                        level=logging.DEBUG if args.verbose else logging.INFO)

    rows = load_databases(args.database_dir)
    output_file = args.output or os.path.join(args.database_dir, "botan-changes.html")
    with open(output_file, 'w', encoding="utf-8") as f:
        f.write(render_page(rows, args.reload))
    logging.info("Wrote %d change entries to: %s", len(rows), output_file)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as ex:
        logging.error(ex)
        sys.exit(1)
