import subprocess
from os.path import dirname, join
import pytest
from dynsync import dynsync


def test_simple():
    pass


def test_complex_shell():
    print subprocess.check_output(join(dirname(__file__), "test_simple.sh"), shell=True, stderr=subprocess.STDOUT)



@pytest.fixture
def local_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('local')

@pytest.fixture
def remote_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('remote')


def test_simple_py(local_dir, remote_dir):
    from threading import Thread
    from time import sleep
    def start():
        print "starting"
#         from click.testing import CliRunner
#         runner = CliRunner()
#         result = runner.invoke(dynsync.main, [local_dir.strpath, "localhost:"+remote_dir.strpath])
        dynsync.main(args=[local_dir.strpath, "localhost:"+remote_dir.strpath], prog_name="dynsync")
#         print result.output
#         print result
#         dynsync.main("dynsync", ["dynsync", local_dir.strpath, "localhost:"+remote_dir.strpath])
#     import pdb;pdb.set_trace()
    th = Thread(target=start)
    print "A"
    import pdb;pdb.set_trace()  
    th.start()
    print "B"
    sleep(3)
    print "C"
    dynsync.stop()
    th.join()
#     import pdb;pdb.set_trace()
#     sleep(3)
