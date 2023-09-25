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
