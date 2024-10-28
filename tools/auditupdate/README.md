# Auto-update Audit Patch References

This allows tracking upstream patch updates automatically. As long as the
current audit report document is not pinned to a specific target tag (i.e.
`$BOTAN_REF` is set to a concrete commit SHA on the upstream main branch),
this will check the upstream repository for newer patches.

If the upstream repository received new patches, this will create a pull request
on the documentation repository and add references to the those patches in the
Audit Report document. A human auditor may then pull the auto-generated branch,
audit and categorize the newly discovered patches and incorporate it into the
document.

## Manual Update: Preparing Patches for a Specific Git Reference Locally

This allows pulling and preparing all patches from the current git reference (as
noted in `$BOTAN_REF`) to the passed future reference (commit SHA, tag or branch).

Typically this is useful when a manual local update is needed. For instance, to
incorporate an upstream hotfix release into a documentation release branch that
was already created but not yet finalized.

For instance, to manually prepare the patches from (current) Botan 3.6.0 to an
upstream hotfix Botan 3.6.1, run:

```
cd tools/auditupdate
poetry run python3 -m auditupdate.cli \
    --repo-location "<path to a local Botan checkout>" \
    --manual-update 3.6.1 \ # the target Git revision
    ../../docs/audit_report/changes
```

The above invocation will create a new
`docs/audit_report/changes/topics/uncategorized.yml` containing all patches
between the current `$BOTAN_REF` and the requested (`--manual-update`) ref.
Also, it will update the `$BOTAN_REF` in `config/botan.env` to whatever was
passed to `--manual-update`.
