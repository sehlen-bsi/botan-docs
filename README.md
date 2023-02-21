# Botan BSI Cryptographic Documentation

BSI Cryptographic Documentation for the [Botan](https://botan.randombit.net/) cryptography library.

## How to build

The document is written using [reStructuredText](https://docutils.sourceforge.io/rst.html) and [Sphinx](https://www.sphinx-doc.org).

Install Sphinx and other Python requirements using pip:

```bash
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
# Create the PDF
make latexpdf
```

The PDF will be in the `_build/latex/` subfolder.
