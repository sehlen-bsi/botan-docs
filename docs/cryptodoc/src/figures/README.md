# Figures

TikZ sources for figures used in the cryptodoc. The rendered artifacts
(`.pdf` for the LaTeX builder, `.svg` for the HTML builder) are committed
alongside the `.tex` sources and referenced from the RST files via
`.. figure:: figures/<name>.*` (Sphinx picks the format matching the
builder).

After editing a `.tex` source, re-render both artifacts:

```sh
pdflatex <name>.tex
pdftocairo -svg <name>.pdf <name>.svg
rm -f <name>.aux <name>.log
```

Requirements: a TeX installation with TikZ and the `tgheros` font
(Debian: `texlive-latex-extra`, `tex-gyre`), and `pdftocairo` from
poppler-utils.
