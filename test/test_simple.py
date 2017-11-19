import subprocess
from os.path import dirname, join

def test_simple():
    pass

def test_complex():
    print subprocess.check_output(join(dirname(__file__), "test_simple.sh"), shell=True, stderr=subprocess.STDOUT)
