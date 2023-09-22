# Test Result Report

This document summarizes test results for certain configurations of
[Botan](https://botan.randombit.net/). It is part of the BSI project "Pflege und
Weiterentwicklung der Kryptobibliothek Botan".

## How to build the Document

The report is generated from JUnit files that are obtained from Botan's unit
test framework. Those need to be available before the documentation generation
can start. The Makefile of this document will run a script
(`scripts/bsi_test_report.py`) that picks up the JUnit *.xml files.

For local development, the script may be configured using a number of command
line parameters. See the script's help text for more information. When run
automatically on CI, it typically is more convenient to configure it using
environment variables.

Here's a list of relevant environment variables that typically must be
configured:

* `TEST_REPORT_JUNIT_INPUT_DIRECTORY`
  Path to the directory containing the JUnit *.xml reports to be rendered
* `TEST_REPORT_OUTPUT_FILE`
  Output file for the rendered restructured text
