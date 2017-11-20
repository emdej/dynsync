import subprocess
from os.path import dirname, join
from dir_compare import dirs_equal, wait_dirs_equal


def test_simple():
    pass


def test_complex_shell():
    print subprocess.check_output(join(dirname(__file__), "test_simple.sh"), shell=True, stderr=subprocess.STDOUT)


def test_simple_py(dynsync, local_dir, remote_dir):
    assert dirs_equal(local_dir, remote_dir)

import os
def initialize(dir, prefix="", depth=3):
    if not depth:
        return
    for i in range(10):
        new_dir = join(dir, "%s_dir_%d" % (prefix, i))
        os.mkdir(new_dir)
        with open(join(dir, "%s_file_%d" % (prefix, i)), 'w') as f:
            f.write("%d" % i)
        initialize(new_dir, prefix, depth-1)


from time import sleep
def writefile(filepath, byte_count, delay=0.1):
    for _ in range(byte_count):
        with open(filepath, 'a') as f:
            f.write("a")
        sleep(delay)


def test_simple_sync(dynsync, local_dir, remote_dir):
    wait_dirs_equal(local_dir, remote_dir)
    initialize(local_dir)
    with open(join(local_dir, "f1"), 'w') as f:
        f.write("a")
    wait_dirs_equal(local_dir, remote_dir)


def test_2(dynsync, local_dir, remote_dir):
    initialize(local_dir)
    wait_dirs_equal(local_dir, remote_dir)

    initialize(local_dir, prefix="A", depth=1)
    wait_dirs_equal(local_dir, remote_dir)

def test_nok(dynsync, local_dir, remote_dir):
    filepath = join(local_dir, "file")
    writefile(filepath, byte_count=100)
    wait_dirs_equal(local_dir, remote_dir)
    assert os.path.getsize(filepath) == 100
