# Audit Information

This library provides central information of the targeted Botan repository, the
relevant revision and other corner-stone information of the audit project. Use
this to dissipate information instead of hard-coding it into the individual
documents.

## Configuration

Botan version and repository info is located in a config file in
`config/botan.env`. This file is read by this python module as well as the CI.
The configuration in there can be overridden with environment variables.
