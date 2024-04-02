#!/bin/bash

# Updates poetry dependencies in the right order. Run this from the
# repository root.

function poetry_update() {
    echo "Updating $1"
    (cd $1; rm poetry.lock; poetry update)
}

poetry_update tools/auditinfo
poetry_update tools/auditutils
poetry_update tools/sourceref
poetry_update tools/auditupdate
poetry_update tools/genaudit
poetry_update tools/tarball_checker

poetry_update docs/architecture
poetry_update docs/audit_method
poetry_update docs/audit_report
poetry_update docs/cryptodoc
poetry_update docs/testreport
poetry_update docs/testspec
