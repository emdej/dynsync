import subprocess
from os.path import dirname, join, getsize
from dir_compare import wait_dirs_equal
from utils import writefile, initialize
import pytest
from conftest import dynsync_process_initialized


# def test_complex_shell():
#     print subprocess.check_output(join(dirname(__file__), "test_simple.sh"), shell=True, stderr=subprocess.STDOUT)


# def test_initial_sync(local_dir, remote_dir):
#     with dynsync_process_initialized(local_dir, remote_dir):
#         pass


def test_simple_sync(dynsync, local_dir, remote_dir):
    wait_dirs_equal(local_dir, remote_dir)
    initialize(local_dir)
    with open(join(local_dir, "f1"), 'w') as f:
        f.write("a")
    wait_dirs_equal(local_dir, remote_dir)


# def test_mkdir_mkfile(dynsync, local_dir, remote_dir):
#     initialize(local_dir)
#     wait_dirs_equal(local_dir, remote_dir)
#     initialize(local_dir, prefix="A", depth=1)
#     wait_dirs_equal(local_dir, remote_dir)


# def test_remote_feedback_not_overwriting_local_changes(dynsync, local_dir, remote_dir):
#     filepath = join(local_dir, "file")
#     writefile(filepath, byte_count=100)
#     wait_dirs_equal(local_dir, remote_dir)
#     assert getsize(filepath) == 100


# def test_ignore(local_dir, remote_dir):
#     with dynsync_process_initialized(local_dir, remote_dir, ['--ignore=ignored_file']):
#         from time import sleep
#         sleep(0.5)
#     filepath1 = join(local_dir, "not_ignored_file1")
#     writefile(filepath1, byte_count=1)
#     wait_dirs_equal(local_dir, remote_dir)
# 
#     assert getsize(filepath1) == 100