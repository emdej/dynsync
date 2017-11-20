import pytest
import subprocess


@pytest.fixture
def local_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('local').strpath


@pytest.fixture
def remote_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('remote').strpath


@pytest.yield_fixture
def dynsync(local_dir, remote_dir):
    try:
        p = subprocess.Popen(["dynsync", local_dir, "localhost:"+remote_dir])
        yield p
    finally:
        p.terminate()
