#!/usr/bin/env python3

"""
CI build script
(C) 2017-2022 Jack Lloyd
    2022 René Meusel - Rohde & Schwarz Cybersecurity
    2023 Philippe Lieser - Rohde & Schwarz Cybersecurity


Botan is released under the Simplified BSD License (see license.txt)
"""

import os
import platform
import subprocess
import sys
import time
import tempfile
import optparse # pylint: disable=deprecated-module
import multiprocessing

def get_concurrency():
    def_concurrency = 2
    max_concurrency = 16

    try:
        return min(max_concurrency, multiprocessing.cpu_count())
    except ImportError:
        return def_concurrency

def known_targets():
    return [
        'coverage',
        'pdf_docs',
        'shared',
        'static',
    ]

def build_targets(target, target_os):
    if target in ['shared']:
        yield 'shared'
    elif target in ['static']:
        yield 'static'
    elif target_os in ['windows']:
        yield 'shared'
    else:
        yield 'shared'
        yield 'static'

    yield 'cli'
    yield 'tests'

def determine_flags(target, target_os, target_cc, ccache,
                    root_dir, test_results_dir):
    """
    Return the configure.py flags as well as make/test running prefixes
    """

    if target_os not in ['linux', 'osx', 'windows']:
        print('Error unknown OS %s' % (target_os))
        return (None, None, None)

    make_prefix = []
    test_prefix = []
    test_cmd = ['botan-test',
                '--data-dir=%s' % os.path.join(root_dir, 'src', 'tests', 'data'),
                '--run-memory-intensive-tests',
                '--run-online-tests',
                '--run-long-tests']

    # generate JUnit test report
    if test_results_dir:
        if not os.path.isdir(test_results_dir):
            raise Exception("Test results directory does not exist")

        def sanitize_kv(some_string):
            return some_string.replace(':', '').replace(',', '')

        report_props = {"ci_target": target, "os": target_os}

        test_cmd += ['--test-results-dir=%s' % test_results_dir]
        test_cmd += ['--report-properties=%s' %
                     ','.join(['%s:%s' % (sanitize_kv(k), sanitize_kv(v)) for k, v in report_props.items()])]

    install_prefix = tempfile.mkdtemp(prefix='botan-install-')

    flags = ['--prefix=%s' % (install_prefix),
             '--cc=%s' % (target_cc),
             '--os=%s' % (target_os),
             '--build-targets=%s' % ','.join(build_targets(target, target_os)),
             '--link-method=symlink']

    if ccache is not None:
        flags += ['--no-store-vc-rev', '--compiler-cache=%s' % (ccache)]

    flags += ['--werror-mode']

    flags += ['--module-policy=bsi', '--enable-modules=tls12,tls13,tls_cbc,pkcs11,xts']

    if target in ['pdf_docs']:
        flags += ['--with-doxygen', '--with-sphinx', '--with-pdf']
        test_cmd = None

    if target in ['coverage']:
        flags += ['--with-coverage-info']
        flags += ['--with-debug-info']

    # Flags specific to native targets

    if target_os in ['osx', 'linux']:
        flags += ['--with-sqlite']

    if target_os in ['osx']:
        flags += ['--with-commoncrypto']

    if target in ['coverage', 'shared']:
        flags += ['--with-boost']
        if target_cc == 'clang':
            # make sure clang ignores warnings in boost headers
            flags += ["--extra-cxxflags=--system-header-prefix=boost/"]

        if target_os in ['windows']:
            # ./configure.py needs boost's location on Windows
            if 'BOOST_INCLUDEDIR' in os.environ:
                flags += ['--with-external-includedir', os.environ.get('BOOST_INCLUDEDIR')]

    if target_os == 'linux':
        flags += ['--with-tpm']

    if test_cmd is None:
        run_test_command = None
    else:
        run_test_command = test_prefix + test_cmd

    return flags, run_test_command, make_prefix

def run_cmd(cmd, root_dir):
    """
    Execute a command, die if it failed
    """
    print("Running '%s' ..." % (' '.join(cmd)))
    sys.stdout.flush()

    start = time.time()

    cmd = [os.path.expandvars(elem) for elem in cmd]
    sub_env = os.environ.copy()
    sub_env['PYTHONPATH'] = os.path.abspath(os.path.join(root_dir, 'src/python'))
    cwd = None

    redirect_stdout_fd = None
    redirect_stdout_fsname = None

    if len(cmd) >= 3 and cmd[-2] == '>':
        redirect_stdout_fsname = cmd[-1]
        redirect_stdout_fd = open(redirect_stdout_fsname, 'w', encoding='utf8')
        cmd = cmd[:-2]
    if len(cmd) > 1 and cmd[0].startswith('indir:'):
        cwd = cmd[0][6:]
        cmd = cmd[1:]
    while len(cmd) > 1 and cmd[0].startswith('env:') and cmd[0].find('=') > 0:
        env_key, env_val = cmd[0][4:].split('=')
        sub_env[env_key] = env_val
        cmd = cmd[1:]

    proc = subprocess.Popen(cmd, cwd=cwd, close_fds=True, env=sub_env, stdout=redirect_stdout_fd)
    proc.communicate()

    time_taken = int(time.time() - start)

    if time_taken > 10:
        print("Ran for %d seconds" % (time_taken))

    if proc.returncode != 0:
        print("Command '%s' failed with error code %d" % (' '.join(cmd), proc.returncode))

        if redirect_stdout_fd is not None:
            redirect_stdout_fd.close()
            last_lines = open(redirect_stdout_fsname, encoding='utf8').readlines()[-100:]
            print("%s", ''.join(last_lines))

        if cmd[0] not in ['lcov', 'codecov']:
            sys.exit(proc.returncode)

def default_os():
    platform_os = platform.system().lower()
    if platform_os == 'darwin':
        return 'osx'
    return platform_os

def detect_compiler_cache():
    compiler_cache = None
    # Autodetect compiler cache
    if have_prog('sccache'):
        compiler_cache = 'sccache'
    elif have_prog('ccache'):
        compiler_cache = 'ccache'
    if compiler_cache:
        print(f"Found '{compiler_cache}' installed, will use it...")

    return compiler_cache

def parse_args(args):
    """
    Parse arguments
    """
    parser = optparse.OptionParser()

    parser.add_option('--cc', default='gcc',
                      help='Set the target compiler type (default %default)')
    parser.add_option('--root-dir', metavar='D', default='.',
                      help='Set directory to execute from (default %default)')

    parser.add_option('--make-tool', metavar='TOOL', default='make',
                      help='Specify tool to run to build source (default %default)')

    parser.add_option('--test-results-dir', default=None,
                      help='Directory to store JUnit XML test reports')

    return parser.parse_args(args)

def have_prog(prog):
    """
    Check if some named program exists in the path
    """
    for path in os.environ['PATH'].split(os.pathsep):
        exe_file = os.path.join(path, prog)
        for ef in [exe_file, exe_file + ".exe"]:
            if os.path.exists(ef) and os.access(ef, os.X_OK):
                return True
    return False

def main(args):
    """
    Parse options, do the things
    """

    print("Invoked as '%s'" % (' '.join(args)))
    (options, args) = parse_args(args)

    if len(args) != 2:
        print('Usage: %s [options] target' % (args[0]))
        return 1

    target = args[1]

    if target not in known_targets():
        print("Unknown target '%s'" % (target))
        return 2

    py_interp = 'python3'

    target_os = default_os()
    compiler_cache = detect_compiler_cache()

    root_dir = options.root_dir

    if not os.access(root_dir, os.R_OK):
        raise Exception('Bad root dir setting, dir %s not readable' % (root_dir))

    cmds = []

    config_flags, run_test_command, make_prefix = determine_flags(
        target, target_os, options.cc,
        compiler_cache, root_dir, options.test_results_dir)

    cmds.append([py_interp, os.path.join(root_dir, 'configure.py')] + config_flags)

    if options.make_tool == '':
        options.make_tool = 'make'

    make_cmd = [options.make_tool]
    if options.make_tool != 'nmake':
        build_jobs = get_concurrency()
        if build_jobs > 1 and options.make_tool != 'nmake':
            make_cmd += ['-j%d' % (build_jobs)]

    make_cmd += ['-k']

    if target in ['pdf_docs']:
        cmds.append(make_cmd + ['docs'])
    else:
        if compiler_cache is not None:
            cmds.append([compiler_cache, '--show-stats'])

        make_targets = ['libs', 'tests', 'cli']

        cmds.append(make_prefix + make_cmd + make_targets)

        if compiler_cache is not None:
            cmds.append([compiler_cache, '--show-stats'])

    if run_test_command is not None:
        cmds.append(run_test_command)

    if target in ['shared', 'static']:
        cmds.append(make_cmd + ['install'])
        build_config = 'build/build_config.json'
        cmds.append([py_interp, os.path.join(root_dir, 'src/scripts/ci_check_install.py'), build_config])
        cmds.append([py_interp, os.path.join(root_dir, 'src/scripts/ci_check_headers.py'), build_config])

    if target in ['coverage']:
        cov_file = 'coverage.lcov'
        raw_cov_file = 'coverage.raw.lcov'

        cmds.append(['lcov', '--capture', '--directory', '.', '--output-file', raw_cov_file])
        cmds.append(['lcov', '--remove', raw_cov_file, '/usr/*', '--output-file', cov_file])
        cmds.append(['lcov', '--list', cov_file])
        cmds.append([os.path.join(root_dir, 'src/scripts/rewrite_lcov.py'), cov_file])

        # Generate a local HTML report
        cmds.append(['genhtml', cov_file, '--output-directory', 'lcov-out'])

    for cmd in cmds:
        run_cmd(cmd, root_dir)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))