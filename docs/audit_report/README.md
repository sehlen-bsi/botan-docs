# Audit Report - Botan

This document is part of the BSI project "Pflege und Weiterentwicklung der Kryptobibliothek Botan".

## How to build the Documentation

This document has a custom build step to generate the audit report document from
YAML files and information from the GitHub API. This is done with a generator
that resides in `../../tools/genaudit` written in Python with a few dependencies.

As with the other documents, local and external dependencies are managed using
Poetry. To generate the document, simply run:

```bash
poetry install
poetry run make latexpdf
```

Note that the GitHub API has a rather tight rate limit on clients without a
GitHub access token. To obtain one, go to your personal settings on GitHub and
generate a "Personal Access Token" with minimal permissions. All to-be-retrieved
information is public anyway.

## Configuration

The `changes` directory contains a configuration file for the audit generator
(namely `config.yml`). For local editing it is sometimes helpful to override
some of the environment configuration that resides in that file. This is done
with environment variables. Most notably:

* `AUDIT_REPO_LOCATION` defines a path to a local repository checkout of Botan
* `AUDIT_CACHE_LOCATION` defines the API request cache location
* `BASIC_GH_TOKEN` contains your GitHub Personal Access Token (see chapter below)

## List Patches that are not yet referenced

During the development of a new version of the library, it is helpful to
periodically update the patch references in this document. More specifically,
the patches that are referenced in the audit *.yml files in the `changes`
directory. Assuming that you changed the `$BOTAN_REF` variable in
`config/botan.env`, run:

```bash
poetry run python3 -m genaudit.cli unrefed --yaml changes
```

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
