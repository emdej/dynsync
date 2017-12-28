from time import sleep, time
import os
from os.path import join


def writefile(filepath, byte_count=1, delay=0.1):
    if isinstance(filepath, tuple):
        filepath = join(*filepath)
    for _ in range(byte_count):
        with open(filepath, 'a') as f:
            f.write("a")
        sleep(delay)


def initialize(dir, prefix="", depth=3):
    if not depth:
        return
    for i in range(10):
        new_dir = join(dir, "%s_dir_%d" % (prefix, i))
        os.mkdir(new_dir)
        with open(join(dir, "%s_file_%d" % (prefix, i)), 'w') as f:
            f.write("%d" % i)
        initialize(new_dir, prefix, depth-1)


def wait_for(pred, timeout=2, ex_type=Exception):
    deadline = time() + timeout
    while time() < deadline:
        if pred():
            return
        sleep(0.1)
    raise ex_type()
