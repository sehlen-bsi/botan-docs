# Audit Report Generator

The audit generator is a tool that helps generating audit reports for Botan
releases. Audit reports are structured by categorizing patch sets and defining
the changes that they contain. Typically, those patch sets are in the
granularity of GitHub pull requests or individual commits in the Botan Git
repository.

## Editing Topics

Topics describe some semantically coherent portion of changes in the Botan
library. This might be a new feature (such as a new TLS protocol version), a new
algorithm (such as Kyber), or some other concern (like CI improvements).

Typically any single topic is addressed by a number of patches that landed in
the code base. We review patches in the context of their related topic to ease
reasoning about library additions. This provides a comprehensive view of _all_
changes that landed in the code base in the audited library version interval.

Each topic is defined by a YAML-file that provides editorial details (like a
title and an rST description) as well as a classification regarding the security
relevance and a list of related patches.

```yaml
title: ECKCDSA

description: |
  This algorithm requires a specific hash truncation that was not handled
  correctly in all circumstances.

classification: relevant

patches:
# Support hash truncation in ECKCDSA (#2742)  (@lieser)
- pr: 3393  # GitHub pull request number
  classification: relevant  # (or: 'unspecified', 'out of scope', 'info', 'critical')
  comment: |
    Ensures that hash truncation in ECKCDSA is performed as specified in ISO
    14888-3:2016.

# Disable ECKCDSA signing with hash truncation  (@randombit)
- pr: 2749
  classification: relevant
  auditer: reneme

# Remove bogus comment [ci skip]  (@Jack Lloyd)
- commit: b61c1c149971f52b0ce273af29074843581e3581 # Git commit SHA
  classification: info
```

Note that topic description or patch comments can contain the full richness of
restructured text formatting markups. Mentions of patch references (e.g. "See GH
#3393 for further details") are automagically linked to GitHub. Also, referring
to other topics is possible by simply using the other topic's YAML file name as
the reference target. E.g. "See also :ref:\`changes/my_other_topic\` for further
info".

"Approvers" of a patch are users that approved a pull request, users that merged
other user's pull requests or an explicit "auditer" stated in the YAML file.
Auditers from the YAML file are rendered in parenthesis along with potential
approvers from GitHub in the final rendering. Use the auditer's GitHub handle!

Eventually, the directory with all topic description YAML files is passed to
the CLI to render them into rST documents to be consumed by Sphinx.

## Usage of the CLI

The CLI can be launched like this:

```bash
python3 -m genaudit.cli
```

Currently, the script has three modes: `render`, `unrefed` and `verify_merges`.
It takes a configuration file (`config.yml`) and requires a number of parameters
to be passed. Most notably, a GitHub access token (via `--token` or from the
environment variable `$BASIC_GH_TOKEN`). All information pulled from GitHub by
the generator is public; nevertheless requests that feature an access token are
subject to relaxed API rate limits.

By providing a `--cache-location` directory the GitHub API requests can be
cached for later invocations. Bare in mind that this might prevent upstream
updates to propagate, though.

### Configuration File (`config.yml`) and Directory Structure

This file contains the basic information for rendering and should be placed
along with the topic descriptions.

```
* config.yml
* topics_directory/
-> * my_topic.yml
-> * my_other_topic.yml
```

`config.yml` then might look like this:

```yaml
project: Changes since last Audit
rst_ref: changes

repo:
  local_checkout: /path/to/local/repo/checkout

topics: topics_directory
cache: /path/to/github/cache/directory  # (optional)
```

### Rendering (`python3 -m genaudit.cli render`)

This renders all topics into restructured text files to be consumed by a Sphinx
documentation generator. Example:

```bash
export BASIC_GH_TOKEN="<mytoken>" # should be placed in the environment in some reasonable way
python3 -m genaudit.cli render -o <output_dir> <config_dir>
```

### Finding unreferenced Patches (`python3 -m genaudit.cli unrefed`)

This is useful to find patches that landed in the relevant audit interval
(see `config/botan.env`) but are not referenced in any topic
description file, yet. It allows to render these patches in a compatible YAML
format right away to simplify the auditing workflow.

Example:

```bash
export BASIC_GH_TOKEN="<mytoken>" # should be placed in the environment in some reasonable way
python3 -m genaudit.cli unrefed --yaml <config_dir>
```

### Verifying Pull Requests' Merge Commits (`python3 -m genaudit.cli`)

For accountability reasons we keep track of the merge commits' hashes for each
pull request that landed. This command allows validating that all referenced
pull requests are associated with the correct merge commit (given a local
repository check out as ground truth).

Example:

```bash
export BASIC_GH_TOKEN="<mytoken>" # should be placed in the environment in some reasonable way
python3 -m genaudit.cli verify_merges <config_dir>
```

To additionally gain YAML-formatted corrections for pull requests that don't
feature any merge commit or that appear inconsistent with the local checkout, run:

```bash
python3 -m genaudit.cli verify_merges --yaml <config_dir>
```

## Limitations

### Co-Authorship is Ignored

The reported author of a pull request is always the user that opened the pull
request. If the pull request contains commits with varying authorship, other
users are currently not listed. This should be achievable by scanning all
commits of a pull request, however.

Commits with co-authors (via `Co-Authored-By: First Last <email@company.org>`)
are also reported as being authored by just the principal author. Parsing the
commit messages for said markups is possible. Though, it remains to be seen
whether the GitHub API allows resolving email addresses to GitHub handles.
