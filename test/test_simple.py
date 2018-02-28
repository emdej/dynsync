import subprocess
from os.path import dirname, join, getsize
from dir_compare import dirs_equal, wait_dirs_equal, NotEqualException
from utils import writefile, initialize
import pytest


def test_simple():
    pass


def test_complex_shell():
    print subprocess.check_output(join(dirname(__file__), "test_simple.sh"), shell=True, stderr=subprocess.STDOUT)


def test_simple_py(dynsync, local_dir, remote_dir):
    assert dirs_equal(local_dir, remote_dir)


def test_simple_sync(dynsync, local_dir, remote_dir):
    initialize(local_dir)
    wait_dirs_equal(local_dir, remote_dir)


def test_simple_sync_remote(dynsync, local_dir, remote_dir):
    import time
    time.sleep(1)
    # use: pgrep -f '[-] /tmp/pytest-of-emdej/pytest-151/remote0'
    initialize(remote_dir)
    wait_dirs_equal(local_dir, remote_dir, timeout=5)


def test_mkdir_mkfile(dynsync, local_dir, remote_dir):
    initialize(local_dir)
    wait_dirs_equal(local_dir, remote_dir)
    initialize(local_dir, prefix="A", depth=1)
    wait_dirs_equal(local_dir, remote_dir)


def test_remote_feedback_not_overwriting_local_changes(dynsync, local_dir, remote_dir):
    filepath = join(local_dir, "file")
    writefile(filepath, byte_count=100)
    wait_dirs_equal(local_dir, remote_dir)
    assert getsize(filepath) == 100


def test_ignore_local(dynsync, local_dir, remote_dir):
    writefile((local_dir, "ignored_file"))
    with pytest.raises(NotEqualException):
        wait_dirs_equal(local_dir, remote_dir)


def test_ignore_remote(dynsync, local_dir, remote_dir):
    writefile((remote_dir, "ignored_file"))
    with pytest.raises(NotEqualException):
        wait_dirs_equal(local_dir, remote_dir, timeout=5)
