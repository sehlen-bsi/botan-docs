# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = src
SCRIPTDIR     = scripts
CHANGESDIR    = changes
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

test_report_rendering:
	python3 $(SCRIPTDIR)/bsi_test_report.py --outfile $(BUILDDIR)/report.rst
	rm "$(SOURCEDIR)/report.rst"; ln -s "../$(BUILDDIR)/report.rst" "$(SOURCEDIR)/report.rst"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile test_report_rendering
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
