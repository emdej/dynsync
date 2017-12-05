import pytest
import subprocess
from contextlib import contextmanager
from utils import writefile
from os.path import join
from dir_compare import wait_dirs_equal


@pytest.fixture
def local_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('local').strpath


@pytest.fixture
def remote_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('remote').strpath


@contextmanager
def dynsync_process(local_dir, remote_dir, opts=[]):
    try:
        p = subprocess.Popen(["dynsync", local_dir, "localhost:"+remote_dir] + opts)
        yield p
    finally:
        if p.poll():
            raise Exception("process died before exit")
        p.terminate()


@contextmanager
def dynsync_process_initialized(local_dir, remote_dir, opts=[]):
    writefile(join(local_dir, "anyfile_746329435435"))
    with dynsync_process(local_dir, remote_dir, opts) as ds:
        wait_dirs_equal(local_dir, remote_dir)
        yield ds


@pytest.yield_fixture
def dynsync(local_dir, remote_dir):
    with dynsync_process_initialized(local_dir, remote_dir) as ds:
        yield ds
