#!/usr/bin/env python3

import argparse
import sys
import os
import subprocess
import tarfile
import filecmp

from urllib.request import urlretrieve
import auditinfo

# This script downloads and checks the source archive released by upstream.
# When the current build targets an unreleased version, the script will
# report an error and fail. Note that the GitHub workflow should make sure
# that it is not executed in such cases.

# Files that may be different without causing an error
TO_IGNORE = [
    'src/build-data/version.txt' # This contains specific release information, and may differ
    ]

# The maximum number of paths to print when differences are found
MAX_DIFFERENCES = 10

def _print_error(msg):
    print(msg, file=sys.stderr)


def _run(cmd, working_directory=".", stderr_ok=False):
    p = subprocess.Popen(cmd, cwd=working_directory,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    errcode = p.wait()
    if errcode != 0 or (stderr and not stderr_ok):
        raise RuntimeError(f"Failed to run {cmd[0]}: \n{stderr}")
    return stdout


def download(url: str) -> str:
    file, httpresponse = urlretrieve(url)
    return file


# Source: https://stackoverflow.com/a/24860799/4842497
class dircmp(filecmp.dircmp):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path, not just the
    file attributes.
    """
    def phase3(self):
        fcomp = filecmp.cmpfiles(self.left, self.right, self.common_files,
                                 shallow=False)
        self.same_files, self.diff_files, self.funny_files = fcomp


def recursive_diff(dir1, dir2):
    compared = dircmp(dir1, dir2)
    differing_paths = []
    if (compared.left_only or compared.right_only or compared.diff_files
        or compared.funny_files):
        return compared.left_only + compared.right_only + compared.diff_files + compared.funny_files
    for subdir in compared.common_dirs:
        if diff_entries := recursive_diff(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
            differing_paths += [os.path.join(subdir, entry) for entry in diff_entries]
    return differing_paths


def main():
    parser = argparse.ArgumentParser(
        description='This is a tool to verify the upstream release source archive.')
    parser.add_argument(
        '-s', '--source-dir', help='Location of the botan source checkout', required=True)
    parser.add_argument(
        '-t', '--tar-source-dir', help='Location to extract the source archive to', required=True)

    args = parser.parse_args(sys.argv[1:])

    if not os.path.isdir(args.source_dir):
        _print_error(f"Did not find botan source directory: {args.source_dir}")
        return 1

    if not os.path.exists(args.tar_source_dir):
        os.makedirs(args.tar_source_dir)

    if os.listdir(args.tar_source_dir):
        _print_error(f"The provided extraction target directory is not empty: {args.tar_source_dir}")
        return 1

    sha = _run(['git', 'rev-parse', 'HEAD'],
               args.source_dir).decode('utf-8').strip()
    if len(sha) != 40:
        _print_error("failed to recognize botan's git repository")
        return 1

    if not auditinfo.botan_is_upstream_release():
        _print_error("The current build targets an unreleased version")
        return 1

    src_tarball_url = auditinfo.botan_get_released_source_tarball_url()
    print(f"Downloading source tarball from {src_tarball_url}...")
    tarball = download(src_tarball_url)

    src_tarball_signature_url = auditinfo.botan_get_released_source_tarball_signature()
    print(f"Downloading source tarball signature from {src_tarball_signature_url}...")
    signature = download(src_tarball_signature_url)

    print("Verifying signature...")
    _run(["gpg", "--verify", signature, tarball], stderr_ok=True)

    print("Extracting tarball...")
    with tarfile.open(tarball, "r:*") as tar:
        tar.extractall(path=args.tar_source_dir, filter='tar')

    extract_result = os.listdir(args.tar_source_dir)
    if len(extract_result) != 1:
        _print_error("Tarball extraction yielded unexpected results")
        return 1

    extracted_sources = os.path.join(args.tar_source_dir, extract_result[0])
    if not os.path.isdir(extracted_sources):
        _print_error("Tarball extraction yielded a file but not a directory")
        return 1

    print("Comparing source directories...")
    differing_paths = recursive_diff(args.source_dir, extracted_sources)
    if differing_paths and not all(path in TO_IGNORE for path in differing_paths):
        _print_error("Source directories do not match")
        print(f"{len(differing_paths)} paths differ:")
        print('\n'.join(differing_paths[:MAX_DIFFERENCES]))
        if len(differing_paths) > MAX_DIFFERENCES:
            print("...")
        return 1

    print("Source directories match. All good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
