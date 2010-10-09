#!/usr/bin/env python

import tempfile
import sys
import subprocess
import shutil
import os
import mclevel
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
    CHUNKSIZE=1024
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
        f = zipfile.ZipFile.open(name)
        f.extractall(dest)
        yield dest

@contextlib.contextmanager
def untared_content(src):
    with temporary_directory() as dest:
        f = tarfile.TarFile.open(src)
        f.extractall(dest)
        yield dest

def launch_subprocess(directory, arguments, env = {}):
    proc = subprocess.Popen((["python.exe"] if sys.platform == "win32" else []) + [
            "./mce.py",
            directory] + arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
            
    return proc

class RegressionError(Exception): pass

def do_test(test_data, result_check, arguments=[]):
    """Run a regression test on the given world.

    result_check - sha1 of the recursive tree generated
    arguments - arguments to give to mce.py on execution
    """
    result_check = result_check.lower()

    env = {
            'MCE_RANDOM_SEED' : '42',
            'MCE_LAST_PLAYED' : '42'
    }

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


def do_test_match_output(test_data, result_check, arguments=[]):
    result_check = result_check.lower()

    env = {
            'MCE_RANDOM_SEED' : '42',
            'MCE_LAST_PLAYED' : '42'
    }

    with directory_clone(test_data) as directory:
        proc = launch_subprocess(directory, arguments, env)
        proc.stdin.close()
        output = proc.stdout.read()
        proc.wait()
        
        if proc.returncode:
            raise RegressionError("Program execution failed!")

        checksum = hashlib.sha1()
        checksum.update(output)
        checksum = checksum.hexdigest()
        if checksum != result_check.lower():
            raise RegressionError("Checksum mismatch: {0!r} != {1!r}".format(checksum, result_check))
    print "[OK] (sha1sum of result is {0!r}, as expected)".format(result_check)


alpha_tests = [
    (do_test,               'baseline', 'ca66277d8037fde5aea3a135dd186f91e4bf4bef', []),
    (do_test,               'degrief',  '6ae14eceab8e0c600799463a77113448b2d9ff8c', ['degrief']),
    (do_test_match_output,  'analyze',  'f2938515596b88509b2e4c8d598951887d7e0f4c', ['analyze']),
    (do_test,               'relight',  '00bc507daa3c07fee065973da4b81a099124650f', ['relight']),
    (do_test,               'replace',  'b26c3d3c05dd873fd8fd29b6b7a38e3ebd9a3e8e', ['replace', 'Water', 'with', 'Lava']),
    (do_test,               'fill',     'f9dd5d49789b4c7363bf55eab03b05846e89f89f', ['fill', 'Water']),
]

def main(argv):
    if len(argv) <= 1:
        do_these_regressions = ['*']
    else:
        do_these_regressions = argv[1:]

    with untared_content("regression_test/alpha.tar.gz") as directory:
        test_data = os.path.join(directory, "alpha")
        for func, name, sha, args in alpha_tests:
            if any(fnmatch.fnmatch(name, x) for x in do_these_regressions):
                func(test_data, sha, args)
                print "Regression {0!r} complete.".format(name)

if __name__ == '__main__':
    sys.exit(main(sys.argv))

