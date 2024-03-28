import sys
import argparse
import os
import re

import auditutils

# Runs Botan's `./configure.py --module-policy=bsi` with the module
# configuration that needs auditing and collects all its dependencies
# in an rST table.

def platform_dependent_modules():
    """ Modules whose parents are part of the audit scope but that are platform
        dependent or dependent on external libraries and therefore might not
        show up in a particular run of ./configure.py.

        NOTE: Dependency resolution _will not happen_ for those modules!
    """
    return set([
        'aes_armv8',
        'aes_ni',
        'aes_power8',
        'aes_vperm',
        'argon2_avx2',
        'argon2_ssse3',
        'certstor_sql',
        'certstor_sqlite3',
        'certstor_system_macos',
        'certstor_system_windows',
        'ghash_cpu',
        'ghash_vperm',
        'keccak_perm_bmi2',
        'sha1_armv8',
        'sha1_sse2',
        'sha1_x86',
        'sha2_32_armv8',
        'sha2_32_bmi2',
        'sha2_32_x86',
        'sha2_64_bmi2',
        'sha2_64_armv8',
    ])

def additional_modules():
    """ Modules that are not in Botan's BSI module policy but that are
        part of the audit scope regardless.

        NOTE: Dependency resolution will be performed for the listed modules.
    """
    return set([
        'certstor_flatfile',
        'certstor_system',
        'classic_mceliece',
        'dilithium_aes',
        'dilithium',
        'ffi',
        'frodokem',
        'frodokem_aes',
        'kyber_90s',
        'kyber',
        'pkcs11',
        'shake',
        'sphincsplus_sha2',
        'sphincsplus_shake',
        'tls_cbc',
        'tls12',
        'tls13_pqc',
        'tls13',
        'xts',
    ])


def print_table(columns: int, modules: list[str]):
    print(".. list-table::")
    print()

    for i, module in enumerate(modules):
        row_sep = "*" if i % columns == 0 else " "
        print(f"   {row_sep} - {module}")

    if len(modules) % columns != 0:
        for _ in range(columns - (len(modules) % columns)):
            print("     -")


def main():
    parser = argparse.ArgumentParser(
        description='Generate an rST table of the audited modules in Botan.')
    parser.add_argument('-r', '--repo-location',
                        help='Path to a local checkout of the Botan repository (overrides config.yml and defaults to AUDIT_REPO_LOCATION).',
                        default=os.environ.get('AUDIT_REPO_LOCATION'))
    parser.add_argument('-c', '--columns',
                        help='Number of columns in the final rST table',
                        default=4)

    args = parser.parse_args(sys.argv[1:])
    conf_py = os.path.join(args.repo_location, "configure.py")

    # verify that the manually listed modules are consistent with
    # the modules offered by the targetted Botan version
    available_modules = set(auditutils.run([conf_py, "--list-modules"], working_directory=args.repo_location).decode("utf-8").splitlines())
    unknown_platform_modules = platform_dependent_modules() - available_modules
    unknown_additional_modules = additional_modules() - available_modules
    if unknown_platform_modules:
        raise RuntimeError("Unknown platform dependent modules: %s" % ', '.join(unknown_platform_modules))
    if unknown_additional_modules:
        raise RuntimeError("Unknown additional modules: %s" % ', '.join(unknown_additional_modules))

    # list all modules that are part of the audit scope
    out = auditutils.run([conf_py,
                          "--module-policy=bsi",
                          "--enable-modules=%s" % ','.join(additional_modules())],
                         working_directory=args.repo_location).decode("utf-8")
    match = re.search(r'Loading modules: (.*)$', out, re.MULTILINE)
    if not match:
        raise RuntimeError("Didn't find loaded modules in configure.py output")
    modules = list(set(match.group(1).split(' ')) | platform_dependent_modules())
    modules.sort()

    # print the final result
    print_table(args.columns, modules)

if __name__ == "__main__":
    sys.exit(main())
