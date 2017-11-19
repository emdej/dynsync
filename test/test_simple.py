import subprocess
from os.path import dirname, join
import pytest
import filecmp


def test_simple():
    pass


def test_complex_shell():
    print subprocess.check_output(join(dirname(__file__), "test_simple.sh"), shell=True, stderr=subprocess.STDOUT)


@pytest.fixture
def local_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('local').strpath


@pytest.fixture
def remote_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('remote').strpath


@pytest.yield_fixture
def dynsync(local_dir, remote_dir):
    try:
        p = subprocess.Popen(["dynsync", local_dir, "localhost:"+remote_dir],
                             stdout=subprocess.PIPE)
        yield p
    finally:
        p.terminate()


def dirs_equal(dir1, dir2):
    cmp_cmd = "tar --sort=name -cm --owner=0 --group=0 -f - -C {} . | sha256sum | cut -d' ' -f1"
    s1 = subprocess.check_output(cmp_cmd.format(dir1), shell=True);
    s2 = subprocess.check_output(cmp_cmd.format(dir2), shell=True);
    return s1 == s2


def test_simple_py(dynsync, local_dir, remote_dir):
    assert dirs_equal(local_dir, remote_dir)
