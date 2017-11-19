import subprocess
from os.path import dirname, join
from dir_compare import dirs_equal


def test_simple():
    pass


def test_complex_shell():
    print subprocess.check_output(join(dirname(__file__), "test_simple.sh"), shell=True, stderr=subprocess.STDOUT)


def test_simple_py(dynsync, local_dir, remote_dir):
    assert dirs_equal(local_dir, remote_dir)
