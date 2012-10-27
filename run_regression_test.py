#!/usr/bin/env python

import tempfile
import sys
import subprocess
import shutil
import os
import hashlib
import contextlib
import gzip
import fnmatch
import tarfile
import zipfile


def generate_file_list(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


def sha1_file(name, checksum=None):
    CHUNKSIZE = 1024
    if checksum is None:
        checksum = hashlib.sha1()
    if fnmatch.fnmatch(name, "*.dat"):
        opener = gzip.open
    else:
        opener = open

    with contextlib.closing(opener(name, 'rb')) as data:
        chunk = data.read(CHUNKSIZE)
        while len(chunk) == CHUNKSIZE:
            checksum.update(chunk)
            chunk = data.read(CHUNKSIZE)
        else:
            checksum.update(chunk)
    return checksum


def calculate_result(directory):
    checksum = hashlib.sha1()
    for filename in sorted(generate_file_list(directory)):
        sha1_file(filename, checksum)
    return checksum.hexdigest()


@contextlib.contextmanager
def temporary_directory(prefix='regr'):
    name = tempfile.mkdtemp(prefix)
    try:
        yield name
    finally:
        shutil.rmtree(name)


@contextlib.contextmanager
def directory_clone(src):
    with temporary_directory('regr') as name:
        subdir = os.path.join(name, "subdir")
        shutil.copytree(src, subdir)
        yield subdir


@contextlib.contextmanager
def unzipped_content(src):
    with temporary_directory() as dest:
        f = zipfile.ZipFile(src)
        f.extractall(dest)
        yield dest


@contextlib.contextmanager
def untared_content(src):
    with temporary_directory() as dest:
        f = tarfile.TarFile.open(src)
        f.extractall(dest)
        yield dest


def launch_subprocess(directory, arguments, env=None):
    #my python breaks with an empty environ, i think it wants PATH
    #if sys.platform == "win32":
    if env is None:
        env = {}

    newenv = {}
    newenv.update(os.environ)
    newenv.update(env)

    proc = subprocess.Popen((["python.exe"] if sys.platform == "win32" else []) + [
            "./mce.py",
            directory] + arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=newenv)

    return proc


class RegressionError(Exception):
    pass


def do_test(test_data, result_check, arguments=()):
    """Run a regression test on the given world.

    result_check - sha1 of the recursive tree generated
    arguments - arguments to give to mce.py on execution
    """
    result_check = result_check.lower()

    env = {
            'MCE_RANDOM_SEED': '42',
            'MCE_LAST_PLAYED': '42',
    }

    if 'MCE_PROFILE' in os.environ:
        env['MCE_PROFILE'] = os.environ['MCE_PROFILE']

    with directory_clone(test_data) as directory:
        proc = launch_subprocess(directory, arguments, env)
        proc.stdin.close()
        proc.wait()

        if proc.returncode:
            raise RegressionError("Program execution failed!")

        checksum = calculate_result(directory).lower()
        if checksum != result_check.lower():
            raise RegressionError("Checksum mismatch: {0!r} != {1!r}".format(checksum, result_check))
    print "[OK] (sha1sum of result is {0!r}, as expected)".format(result_check)


def do_test_match_output(test_data, result_check, arguments=()):
    result_check = result_check.lower()

    env = {
            'MCE_RANDOM_SEED': '42',
            'MCE_LAST_PLAYED': '42'
    }

    with directory_clone(test_data) as directory:
        proc = launch_subprocess(directory, arguments, env)
        proc.stdin.close()
        output = proc.stdout.read()
        proc.wait()

        if proc.returncode:
            raise RegressionError("Program execution failed!")

        print "Output\n{0}".format(output)

        checksum = hashlib.sha1()
        checksum.update(output)
        checksum = checksum.hexdigest()

        if checksum != result_check.lower():
            raise RegressionError("Checksum mismatch: {0!r} != {1!r}".format(checksum, result_check))

    print "[OK] (sha1sum of result is {0!r}, as expected)".format(result_check)


alpha_tests = [
    (do_test, 'baseline', '9e7460d39c8e0456789cf89fee45276db2719aaa', []),
    (do_test, 'degrief', '403e6c6147cf1f8d73377b18bbf5e4973606a311', ['degrief']),
    (do_test_match_output, 'analyze', '89ae362dec7f6c0fd743d6ed4e3957459cb3c34d', ['analyze']),
    (do_test, 'relight', 'e0cf60c62adfdb313f198af5314c31f89d158c12', ['relight']),
    (do_test, 'replace', 'd73767293e903b6d1c49c1838eb1849b69d83ad8', ['replace', 'Water (active)', 'with', 'Lava (active)']),
    (do_test, 'fill', 'f4f57c3d902b6894031d416cb9279232e7e24bd7', ['fill', 'Water (active)']),
    (do_test, 'heightmap', '9e7460d39c8e0456789cf89fee45276db2719aaa', ['heightmap', 'regression_test/mars.png']),
]

import optparse

parser = optparse.OptionParser()
parser.add_option("--profile", help="Perform profiling on regression tests", action="store_true")


def main(argv):
    options, args = parser.parse_args(argv)

    if len(args) <= 1:
        do_these_regressions = ['*']
    else:
        do_these_regressions = args[1:]

    with untared_content("regression_test/alpha.tar.gz") as directory:
        test_data = os.path.join(directory, "alpha")
        passes = []
        fails = []

        for func, name, sha, args in alpha_tests:
            print "Starting regression {0} ({1})".format(name, args)

            if any(fnmatch.fnmatch(name, x) for x in do_these_regressions):
                if options.profile:
                    print >> sys.stderr, "Starting to profile to %s.profile" % name
                    os.environ['MCE_PROFILE'] = '%s.profile' % name
                try:
                    func(test_data, sha, args)
                except RegressionError, e:
                    fails.append("Regression {0} failed: {1}".format(name, e))
                    print fails[-1]
                else:
                    passes.append("Regression {0!r} complete.".format(name))
                    print passes[-1]

        print "{0} tests passed.".format(len(passes))
        for line in fails:
            print line


if __name__ == '__main__':
    sys.exit(main(sys.argv))
