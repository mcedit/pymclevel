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
        proc = subprocess.Popen([
            "./mce.py",
            directory] + arguments, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        proc.stdin.close()
        result = proc.wait()

        if os.WIFEXITED(result) and os.WEXITSTATUS(result):
            raise RegressionError("Program execution failed!")

        checksum = calculate_result(directory).lower()
        if checksum != result_check.lower():
            raise RegressionError("Checksum mismatch: {0!r} != {1!r}".format(checksum, result_check))
    print "[OK]"


def do_test_match_output(test_data, result_check, arguments=[]):
    result_check = result_check.lower()

    env = {
            'MCE_RANDOM_SEED' : '42',
            'MCE_LAST_PLAYED' : '42'
    }

    with directory_clone(test_data) as directory:
        proc = subprocess.Popen([
            "./mce.py",
            directory] + arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        proc.stdin.close()
        output = proc.stdout.read()
        result = proc.wait()

        if os.WIFEXITED(result) and os.WEXITSTATUS(result):
            raise RegressionError("Program execution failed!")

        checksum = hashlib.sha1()
        checksum.update(output)
        checksum = checksum.hexdigest()
        if checksum != result_check.lower():
            raise RegressionError("Checksum mismatch: {0!r} != {1!r}".format(checksum, result_check))
    print "[OK]"



def main(argv):
    with untared_content("regression_test/alpha.tar.gz") as directory:
        test_data = os.path.join(directory, "alpha")
        do_test(test_data, 'ca66277d8037fde5aea3a135dd186f91e4bf4bef')
        do_test(test_data, '0f4cbb81f7f109cee10606b82f27fb2681a22f50', ['degrief'])
        do_test_match_output(test_data, 'f2938515596b88509b2e4c8d598951887d7e0f4c', ['analyze'])

if __name__ == '__main__':
    sys.exit(main(sys.argv))

