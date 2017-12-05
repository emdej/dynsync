import subprocess
import time


class NotEqualException(Exception):
    pass


def dirs_equal(dir1, dir2):
    cmp_cmd = "tar --sort=name -cm --owner=0 --group=0 -f - -C {} . | sha256sum | cut -d' ' -f1"
    s1 = subprocess.check_output(cmp_cmd.format(dir1), shell=True)
    s2 = subprocess.check_output(cmp_cmd.format(dir2), shell=True)
    return s1 == s2


def wait_dirs_equal(dir1, dir2, timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if dirs_equal(dir1, dir2):
            return
        time.sleep(0.1)
    raise NotEqualException()
