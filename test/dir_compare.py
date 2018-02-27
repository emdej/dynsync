import subprocess
from utils import wait_for


class NotEqualException(Exception):
    pass


def dirs_equal(dir1, dir2):
    cmp_cmd = "tar --sort=name -cm --owner=0 --group=0 -f - -C {} . | sha256sum | cut -d' ' -f1"
    s1 = subprocess.check_output(cmp_cmd.format(dir1), shell=True)
    s2 = subprocess.check_output(cmp_cmd.format(dir2), shell=True)
    return s1 == s2


def wait_dirs_equal(dir1, dir2, timeout=5):
    wait_for(lambda: dirs_equal(dir1, dir2), timeout=timeout, ex_type=NotEqualException)
