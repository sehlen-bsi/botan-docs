# Audit Report - Botan

This document is part of the BSI project "Pflege und Weiterentwicklung der Kryptobibliothek Botan".

## How to build the Documentation

This document has a custom build step to generate the audit report document from
YAML files and information from the GitHub API. This is done with a generator
that resides in `../../tools/genaudit` written in Python with a few dependencies.

As with the other documents, local and external dependencies are managed using
Poetry. To generate the document simply run:

```bash
poetry install
poetry run make latexpdf
```

Note that the GitHub API has a rather tight rate limit on clients without a
GitHub access token. To obtain one, go to your personal settings on GitHub and
generate a "Personal Access Token" with minimal permissions. All to-be-retrieved
information is public anyway.

## Obtaining a Personal Access Token from GitHub

After logging into GitHub, click on your avatar in the upper-right. Then, in the
drop-down menu, go to "Settings". Now, in the settings-menu on the left go to
"Developer Settings" (all the way down), and then "Personal Access Tokens". A
"classic" token is just fine.

Now click on "Generate new token", give it a reasonable name (e.g. "BSI
Generator") and click "Generate token". No need to give it any of the listed
permissions.

Finally, copy the generated token (it won't be presented to you again) and store
it in your environment as `$BASIC_GH_TOKEN`. For instance, you could amend your
`.bashrc` (or similar) like:

```bash
export BASIC_GH_TOKEN="ghp_<mytoken>..."
```

Now you shouldn't run into rate limits anymore and should be able to build the
document as outlined above.
