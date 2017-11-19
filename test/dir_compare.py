import subprocess


def dirs_equal(dir1, dir2):
    cmp_cmd = "tar --sort=name -cm --owner=0 --group=0 -f - -C {} . | sha256sum | cut -d' ' -f1"
    s1 = subprocess.check_output(cmp_cmd.format(dir1), shell=True)
    s2 = subprocess.check_output(cmp_cmd.format(dir2), shell=True)
    return s1 == s2
