import pytest
import subprocess
from utils import writefile, wait_for
from os.path import isdir
import shlex
from contextlib import contextmanager


@pytest.fixture
def local_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('local').strpath


@pytest.fixture
def remote_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('remote').strpath


@contextmanager
def process_stopped(pid):
    subprocess.call(["kill", "-STOP", str(pid)])
    try:
        yield
    finally:
        subprocess.call(["kill", "-CONT", str(pid)])


@pytest.fixture
def initial_files():
    return ["initial_file"]


@pytest.fixture
def ignored():
    return []


@pytest.fixture
def dynsync(local_dir, remote_dir, ignored, initial_files):
    try:
        for f in initial_files:
            writefile((local_dir, f))
        p = subprocess.Popen(["dynsync", local_dir, "localhost:"+remote_dir] + ["--ignore=%s" % i for i in ignored])

        def pred():
            if not p.pid:
                return False
            with process_stopped(p.pid):
                fds_path = "/proc/%d/fd" % p.pid
                cmd = "find %s -lname anon_inode:inotify" % fds_path
                return isdir(fds_path) and subprocess.check_output(shlex.split(cmd))
        wait_for(pred)
        yield p
    finally:
        p.terminate()


def pytest_addoption(parser):
    parser.addoption('--count', type='int', metavar='count',
                     help='Run each test the specified number of times.')


def multiply_tests(metafunc, count):
    if count:
        metafunc.fixturenames.append("test_instance_id")
        metafunc.parametrize("test_instance_id", [str(i) for i in range(count)])


def pytest_generate_tests(metafunc):
    multiply_tests(metafunc, metafunc.config.option.count)
