Changes Overview
================

In relation to the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings some minor extensions of functionality and bug fixes. Among the latter, there are fixes for three CVEs, which probably are the most important updates in this Botan version:

- CVE-2026-32877: Fix a heap over-read during SM2 decryption (GH #5450)
- CVE-2026-32883: Fix an OCSP response forgery vulnerability (GH #5449)
- CVE-2026-32884: Fix a name constraints bypass for DNS names (GH #5448)

Furthermore, a number of code optimizations have been introduced.
