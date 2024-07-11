# Release Checklist

The following actions are necessary to prepare the documents for submission.
This checklist assumes that the documents' main contents are ready, and should
act as a guideline to verify that all auxiliary content summaries and technical
details are in place.

Typically, we do that for every upstream Botan release. Once the upstream Botan
repository has a tagged release, we can start prepping the audit documents for
that release. Ideally, this preparatory work is done on a release branch and not
on the document repo's main branch.

* **Create a Release Branch**

  The release branch (in the form `release/<botan semver version>`) will stay
  forever and archive the audit documents for that release.
  See: https://nvie.com/posts/a-successful-git-branching-model/

  * *Create and push: `release/<botan semver version>`*

* **Pin the Botan Version**

  The following configuration variables are set in `config/botan.env`. Note, that
  the "patch auto-update bot" will stop collecting new patches if `BOTAN_REF` is
  configured as a static git tag (rather than some git sha on master).

  * *Set `BOTAN_REF` to the release semver string*
  * *Ensure that `BOTAN_VERSION` contains the same semver string*
  * *`BOTAN_BASE_REF` should be the semver string of the previous audit target*

* **Update Changelogs**

  Not all documents contain changelogs. Here's a list of
  the ones that do:

  * *Audit Method*
  * *Cryptographic Documentation*

  Generally, the document versions are in lockstep with the audited version of
  Botan. People that contributed to the described iteration are mentioned with
  their initials. The datestamp in the changelog should be the day of the final
  content update and reasonably close to the final release date of the document.

* **Double-check References in the Documents**

  * Architecture Overview

    This document contains hard-coded section-specific references into Botan's
    upstream handbook. Currently we have to manually check and update them for
    each release.

  * Cryptographic Documentation

    We are referencing BSI's technical guidelines and they are updated regularly.
    Make sure that the references are up-to-date and that any changes in the
    guidelines do not affect Botan's conformance.

* **Audit Report Summaries**

  * *Update the "audited modules list"*

    An inline comment in the document explains how this is done in detail

  * *Summarize the most-notable changes in the "Changes Overview" chapter*

    This should contain enough detail to gain an insight to the scope of this
    release. Summarize the major added end-user values of this release in terms
    of both significant fixes and added features. Usually, Botan's `news.rst`
    file is a good starting point to compile this.

  * *Update the bullet-point summary in the final section ("Summary and Results")*

    Typically, this mentions the same changes as the "Overview" above but much
    shorter: i.e. as a bullet-point list of changed things.

  * *Ensure that the "Security and Vulnerabilities" section is up-to-date*

    This section may be empty if no vulnerabilities were discovered and/or fixed
    during the given audit cycle. Otherwise, vulnerabilities and their end-user
    impact should be summarized with relevant references to online resources.

  * *Add a concise and matching summary description to every topic YAML file*
  * *Ensure that all topics have a matching security relevance classification*

* **Prepare for next Audit Cycle**

  This preparation should happen on the document repo's main branch *after* the
  release branch diverted from it. At this point, `main` will strive towards the
  next audit cycle while `release/*` stays frozen on the now finished cycle.

  * *Set `BOTAN_REF` to the latest git sha on upstream master*

    Use a naked git sha (NOT the `master` ref!). This will enable the "patch
    auto-update bot", who will resume collecting patches from upstream.

  * *Set `BOTAN_VERSION` to the expected next Botan semver version*

    This string is displayed as the audit target throughout the documents.

  * *Set `BOTAN_BASE_REF` to the previous audit target*

    Typically, this is the semver version of the audit documents we're
    currently preparing for submission.

  * *Clear the summary text blocks outlined in "Audit Report Summaries*

    Replace them by generic `.. todo::` remarks to find them quickly once the
    time comes for the next release.
