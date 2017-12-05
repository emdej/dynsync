from time import sleep
import os
from os.path import join


def writefile(filepath, byte_count, delay=0.1):
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
