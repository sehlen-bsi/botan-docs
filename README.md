# Botan BSI Documentation

Extended documentation for the [Botan](https://botan.randombit.net/)
cryptography library in the context of the BSI project "Pflege und
Weiterentwicklung der Kryptobibliothek Botan".

## Status

[![Audit Auto-update](https://github.com/sehlen-bsi/botan-docs/actions/workflows/auto-update.yml/badge.svg)](https://github.com/sehlen-bsi/botan-docs/actions/workflows/auto-update.yml)

## Repository Anatomy

This monorepo contains documents (in `/docs`) as well as auxiliary helper
scripts (in `/tools`). Most documents come with a `Makefile` to build them as
PDF, HTML or other formats. Some generators depend on the helper scripts in
`/tools`. We use [Poetry](https://python-poetry.org/) to manage the
local and external dependencies.

## How to build the Documentation

The documents are written using
[reStructuredText](https://docutils.sourceforge.io/rst.html) and
[Sphinx](https://www.sphinx-doc.org). Specific documents might need additional
tooling and generation steps. See the document-specific readmes for further
guidance.

We use [Poetry](https://python-poetry.org/) to manage the (internal and
external) Python dependencies of the document generators. In contrast to `pip`,
Poetry manages dependencies in virtual Python environments. Therefore, it
transparently handles the environment setup for the document generators.

To install poetry, run:

```bash
sudo apt install python3-poetry
```

Now, install Sphinx and other Python requirements of individual documents using
Poetry:

```bash
# Go into the directory of the document you want to build, e.g.
cd docs/cryptodoc
# Install Sphinx and the respective Python dependencies
poetry install
```

### Create PDF

Required packages:

```bash
# Ubuntu
sudo apt install texlive-latex-extra texlive-fonts-recommended tex-gyre latexmk

# Fedora
dnf install texlive-collection-latexextra latexmk
```

To build a PDF do the following:

```bash
# Go into the directory of the document you want to build, e.g.
cd docs/cryptodoc
# Create the PDF
poetry run make latexpdf
```

The PDF will be in the `_build/latex/` subfolder.

## How to edit the Documentation

The recommended editor for editing the documentation is [*Visual Studio
Code*](https://code.visualstudio.com/). A minimal configuration for *Visual
Studio Code* with recommended extensions is included in the repository.

Some extensions need additional Python requirements. They are installed
automatically via Poetry. To use the underlying language server (esbonio),
VS Code either needs to be launched from the virtual environment of `poetry shell`
or the respective venv interpreter must be configured in a running VS Code
instance.

```bash
cd docs/cryptodoc
poetry install # (if not already done)
poetry shell
code ../..
```

**Caveats:** The completion and preview are configured to work in the crypto
documentation (see `.vscode/settings.json`). So far, we didn't find a way to
make it work for all documents without manual reconfiguration.
