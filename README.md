# Botan BSI Documentation

Extended documentation for the [Botan](https://botan.randombit.net/)
cryptography library in the context of the BSI project "Pflege und
Weiterentwicklung der Kryptobibliothek Botan".

## How to build the Documentation

The documents are written using
[reStructuredText](https://docutils.sourceforge.io/rst.html) and
[Sphinx](https://www.sphinx-doc.org). Specific documents might need additional
tooling and generation steps. See the document-specific readmes for further
guidance.

Install Sphinx and other Python requirements using pip:
```bash
# Go into the directory of the document you want to build, e.g.
cd cryptodoc
# Install Sphinx and the respective Python dependencies
pip install -r requirements.txt
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
cd cryptodoc
# Create the PDF
make latexpdf
```

The PDF will be in the `_build/latex/` subfolder.

## How to edit the Documentation

The recommended editor for editing the documentation is [*Visual Studio
Code*](https://code.visualstudio.com/). A minimal configuration for *Visual
Studio Code* with recommended extensions is included in the repository.

Some extensions need additional Python requirements. Install them using pip within
the respective directory:

```bash
pip install -r requirements-dev.txt
```
