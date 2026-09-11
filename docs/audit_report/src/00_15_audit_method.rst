.. _sec-trace-changes:

Tracking Changes
================

Use of Git and GitHub in the Development of the Library
-------------------------------------------------------

The library is developed publicly on GitHub [#botangithub]_. Larger changes to
the code are usually made via topic-specific "pull requests" [#botanpulls]_
after a technical review process by one of the library's core developers
(GitHub "collaborators"). In exceptional cases the main developer (Jack Lloyd)
commits smaller changes directly to the library's development branch. These
direct changes in particular are always signed by the main developer using GPG
[#jackgpg]_.

In both cases, the pull requests and the direct changes allow all changes to
the library to be tracked transparently and to be classified by topic with
comparatively little effort. In the following, the term "patch" refers both to
changes that were merged by means of a pull request and to direct changes made
by the main developer.

The data model of Git ensures that applying all patches between two source code
versions leads unambiguously from the older to the newer version. Thus all
actual changes between two versions are captured by the entirety of the patches
that led from the older to the newer version.

This audit approach presupposes the trustworthiness of Git and its data model.
The end of this chapter therefore contains a brief discussion of the
trustworthiness of Git (see :ref:`about_git`).

.. [#botangithub] `github.com/randombit/botan <https://github.com/randombit/botan>`_
.. [#botanpulls] `github.com/randombit/botan/pulls <https://github.com/randombit/botan/pulls>`_
.. [#jackgpg] GPG key ID of Jack Lloyd: ``9F:FD:59:6F:AB:50:F9:0D``

Retrospective Change Tracking
-----------------------------

Individual versions of the library have already been audited in the past. The
goal of change tracking is to identify all changes to the library that have
been added since the last audit, to classify them according to their relevance,
and to examine relevant changes in more detail.

For this purpose, as described above, Git is used to identify all patches to
the library that led from an already audited version to the new target version.
Individual patches usually have a topical focus and a technical description
(commit message or pull request description). For example, "Add XMSS Parameter
sets defined in NIST SP.800-208" [#xmssparams]_ contains the source code
changes that extend the XMSS implementation by the parameters specified by
NIST.

In principle, each patch can affect arbitrary components of the library. The
components considered here are the library itself (directory *src/lib*), the
test suite (directory *src/tests*), the command line interface (directory
*src/cli*), the Python wrapper (directory *src/python*), the build system
(script *configure.py* and directory *src/build-data*), and the documentation
(directory *doc*).

All identified patches are manually pre-sorted by topic and then analyzed
individually, classified according to their security relevance in relation to
the audit scope, and the contained changes are documented. The result is a
detailed, topic-oriented change report with references to all relevant patches.
This makes it easy to ensure later traceability (for instance by third parties).

.. [#xmssparams] GitHub pull request: `#3292 <https://github.com/randombit/botan/pull/3292>`_

Classification
--------------

Whether a change is security-relevant is decided based on several criteria. For
changes to the build system, whether they are critical depends on the nature of
the changes. Among other things, the build system ensures that only those
modules are present in the compiled artifact that were selected during the
configuration of the build, so changes to this logic are to be regarded as
critical. Changes to the test suite are to be regarded as critical as soon as
they affect modules that are contained in the BSI module policy or as soon as
they affect dependent modules. Likewise, changes to modules of the library that
are contained in the BSI module policy or that affect dependent modules can be
regarded as critical.

.. Unclear how this is to be understood, therefore commented out by Falko Strenzke:
  Each change is assigned to one of three categories. Changes of category I
  denote security-critical changes, i.e., changes that impair the proper
  operation of the cryptographic functions. Changes of category II denote
  security-relevant changes, i.e., changes that increase the efficiency or
  effectiveness of the cryptographic functions. Changes of category III denote
  further, non-security-critical changes, i.e., changes made for reasons other
  than security.

Topical Grouping
----------------

For a better overview and to simplify the audit process, patches are sorted by
topic wherever possible. There is explicitly no one-to-one relationship between
patches and topics. A patch may well be relevant to more than one of the topics
considered and thus be assigned more than once.

.. Possibly better to list the predefined categories here instead
  Conceivable topics are, for example, "Adding an implementation of
  CRYSTALS-Kyber", "Closing a security vulnerability in the validation of
  X.509 certificates", or "Speeding up the continuous integration pipeline".
  For each topic, the relevant patches are enumerated and the contained
  changes are documented collectively.

Topics may also receive a classification of their security relevance. Where
applicable, the depth of examination of the patches in the context of the topic
is determined by this classification.

.. _about_git:

Security and Trustworthiness of Git
-----------------------------------

Git uses a cryptographic hash function for the data management and integrity
verification of repositories. For historical reasons, SHA-1 is still used for
this purpose. Since SHA-1 is no longer regarded as fundamentally secure, the
following explains why Git can nevertheless be used in a trustworthy manner at
the present time.

The SHA-1 hash of a Git commit is computed from the source tree of the commit
(the delta) and various header information, such as the SHA-1 commit hash of
the predecessor commit, the author information, the committer information, and
the commit description.

The integrity of the repository is ensured via the SHA-1 commit hash of the
predecessor commit. Since the header of the predecessor commit contains the
SHA-1 hash of its own predecessor, the chain can be constructed and verified
back to the initial commit. This means that modifying a commit changes all
subsequent commit hashes, and this modification is detected. To ensure that a
local copy of a repository has not been modified, the SHA-1 hash of the last,
i.e. most recent, commit of the local repository must therefore be compared
with the remote repository (e.g. on GitHub).

Git is thus inherently dependent on the collision resistance of SHA-1. Using a
hash collision, pairs of commits with the same SHA-1 hash could be used to
inject malicious code into a repository unnoticed by the audit process
described above. To do so, an attacker would have to create a pair of valid Git
commit objects, one with harmless (but functional) changes and the other with
malicious code, that have the same commit hash. A weakness in SHA-1 published
by Stevens et al. in 2017 [SHATRD]_ makes this possible in theory; however, at
the present time we are not aware of any example where this has been
successfully demonstrated for Git commit objects.

It is important to note that for a successful collision, both commits (the
harmless one as well as the manipulated one) would have to be created by the
attacker. It is thus explicitly *not* possible to retroactively replace an
existing legitimate commit of the repository. The attacker would therefore have
to inject the harmless commit into Botan early on.

Using counter-cryptanalysis, objects that are part of such an attack can be
detected reliably (see SHA-1-DC [SHA1DC]_). Since the weakness became known,
both GitHub [#githubsha1]_ and Git [#gitsha1]_ use SHA-1-DC and reject objects
that are part of a collision created in this way. The injection would thus not
go unnoticed, which prevents a successful attack.

In the long term, a migration to a secure hash function should of course be
pursued. However, due to the lack of support by Git hosting providers (such as
GitHub) [#lwngitsha1]_, this is not in the hands of the Botan developers or the
auditors in this project. Given the effective countermeasures provided by
SHA-1-DC, it is nevertheless justifiable at the present time to trust Git for
the audit process described here.

Furthermore, Git offers the possibility to sign individual commits using GPG.
In this way the authenticity of the commits is ensured. The Botan developers
make use of this possibility to a large extent.

Part of the delivery package of each audit is a signed source code archive of
the audited library version. Users of the library thus have access to the
complete source code even without using Git.


Deliverables
------------

After the examination of the version under review, the audit report is
presented to the BSI. The following documents are submitted for this purpose:

-  The present document "Audit Report"
-  Botan Reference Documentation
-  Document "Architecture Description"
-  Document "Test Specification"
-  Document "Cryptographic Documentation"
-  Signed archive of the source code
-  The document "Test Report" (generated automatically by the CI within a pull request)

.. [#githubsha1] `github.blog/2017-03-20-sha-1-collision-detection-on-github-com <https://github.blog/2017-03-20-sha-1-collision-detection-on-github-com>`_
.. [#gitsha1] `github.blog/2017-05-10-git-2-13-has-been-released <https://github.blog/2017-05-10-git-2-13-has-been-released/#sha-1-collision-detection>`_
.. [#lwngitsha1] `lwn.net/Articles/898522 <https://lwn.net/Articles/898522>`_
