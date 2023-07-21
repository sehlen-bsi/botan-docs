#!/usr/bin/env python3

import argparse
import sys
import os
import zipfile
import subprocess
import re

# This script packages a prestine botan source directory into a source archive.
# The output archive will be called: botan-[version string]-[short git sha].zip
#
# Below are lists that define which dirs/files of the checkout should be
# packaged or ignored. If there are any additional files, or listed files are
# missing, the script fails. This is to make sure that the packaged elements are
# always selected deliberately.

TO_IGNORE = ['.git', '.github', '.gitignore', '.clang-format', '.codecov.yml', '.lgtm.yml']
TO_PACKAGE = ['doc', 'src', 'configure.py',
              'license.txt', 'news.rst', 'readme.rst']


def _print_error(msg):
    print(msg, file=sys.stderr)


def _run(cmd, working_directory="."):
    p = subprocess.Popen(cmd, cwd=working_directory,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    errcode = p.wait()
    if stderr or errcode != 0:
        raise RuntimeError(f"Failed to run {cmd[0]}: \n{stderr}")
    return stdout


def _read_botan_version(src_dir):
    """ Adapted from botan's ./configure.py """

    version_txt = os.path.join(src_dir, 'src', 'build-data', 'version.txt')
    if not os.path.isfile(version_txt):
        raise RuntimeError(
            "Did not find version.txt in botan source directory")

    with open(version_txt, encoding='utf-8') as version_file:
        key_and_val = re.compile(r"([a-z_]+) = ([a-zA-Z0-9:\-\']+)")

        results = {}
        for line in version_file.readlines():
            if not line or line[0] == '#':
                continue
            match = key_and_val.match(line)
            if match:
                key = match.group(1)
                val = match.group(2)

                if val == 'None':
                    val = None
                elif val.startswith("'") and val.endswith("'"):
                    val = val[1:len(val)-1]
                else:
                    val = int(val)

                results[key] = val

        version = f"{results['release_major']}.{results['release_minor']}.{results['release_patch']}{results['release_suffix']}"
        return version


def main():
    parser = argparse.ArgumentParser(
        description='This is a tool to generate a source archive from botan\'s source checkout.')
    parser.add_argument(
        '-o', '--output-dir', help='Where to store the final archive (missing directories will be created)', required=True)
    parser.add_argument(
        '-s', '--source-dir', help='Location of the botan source checkout', required=True)

    args = parser.parse_args(sys.argv[1:])

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)

    if not os.path.isdir(args.source_dir):
        _print_error(f"Did not find botan source directory: {args.source_dir}")
        return 1

    sha = _run(['git', 'rev-parse', 'HEAD'],
               args.source_dir).decode('utf-8').strip()
    if len(sha) != 40:
        _print_error("failed to recognize botan's git repository")
        return 1

    all_found_files_listed = all(f in TO_PACKAGE + TO_IGNORE for f in os.listdir(args.source_dir))
    all_listed_files_found = all(f in os.listdir(args.source_dir) for f in TO_PACKAGE)
    if not all_found_files_listed or not all_listed_files_found:
        _print_error("Detected missing or additional files in the claimed source checkout. Wrong --source-dir or different botan version?")
        return 1

    version = _read_botan_version(args.source_dir)
    zip_filename = f"botan-{version}-{sha[0:7]}.zip"
    with zipfile.ZipFile(os.path.join(args.output_dir, zip_filename), "w") as zip:
        [zip.write(os.path.join(args.source_dir, f), f) for f in TO_PACKAGE]

    return 0


if __name__ == "__main__":
    sys.exit(main())
