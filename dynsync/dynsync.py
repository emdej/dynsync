import os
import sys
import time
import subprocess
import threading

import click
from watchdog.events import FileSystemEventHandler


class RSyncEventHandler(FileSystemEventHandler):
    def __init__(self, local_path, remote_path, local_tmp, remote_tmp, ignores=[]):
        self.ignores = ignores
        self.local_path = local_path
        self.remote_path = remote_path
        self.remote_path_short = remote_path.split(':')[1]
        self.changed_paths = []
        self.local_tmp = local_tmp
        self.remote_tmp = remote_tmp
        print "initial synchronization in progress..."
        self.rsync()
        print "done."

    def on_moved(self, event):
        super(RSyncEventHandler, self).on_moved(event)
        self.changed_paths.insert(0, event.src_path)
        self.changed_paths.insert(0, event.dest_path)

    def on_created(self, event):
        super(RSyncEventHandler, self).on_created(event)
        self.changed_paths.insert(0, event.src_path)

    def on_deleted(self, event):
        super(RSyncEventHandler, self).on_deleted(event)
        self.changed_paths.insert(0, event.src_path)

    def on_modified(self, event):
        super(RSyncEventHandler, self).on_modified(event)
        self.changed_paths.insert(0, event.src_path)

    def rsync(self, changes=None):
        if changes:
            local_changes = [''.join(abs_change.split(self.local_path)[1:]) for abs_change in changes]
            local_changes.sort()
            cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} --include-from=- {} {}"
            cmd = cmd.format(self.remote_tmp, self.local_path, self.remote_path)
        else:
            local_changes = []
            cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} {} {}"
            cmd = cmd.format(self.remote_tmp, self.local_path, self.remote_path)
        try:
            import shlex
            p = subprocess.Popen(
                shlex.split(cmd),
                stdin=subprocess.PIPE
            )
            input = ''.join(['+ /%s\n' % change for change in local_changes if change])
            input += '- *\n'
            stdout, stderr = p.communicate(input=input.encode('utf8'))
        except Exception as e:
            print e
        p.wait()
        print stdout
        print stderr

    def rev_rsync(self, changes=None):
        local_changes = [''.join(abs_change.split(self.remote_path_short)[1:]) for abs_change in changes]
        local_changes.sort()
        cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} --include-from=- {} {}"
        cmd = cmd.format(self.local_tmp, self.remote_path, self.local_path)
        try:
            import shlex
            p = subprocess.Popen(
                shlex.split(cmd),
                stdin=subprocess.PIPE
            )
            input = ''.join(['+ /%s\n' % change for change in local_changes if change])
            input += '- *\n'
            stdout, stderr = p.communicate(input=input.encode('utf8'))
        except Exception as e:
            print e
        p.wait()


class ChangeFirewall:
    LOCAL = 1
    REMOTE = 2

    def __init__(self, lp, rp):
        self.changes = {
                ChangeFirewall.LOCAL: {},
                ChangeFirewall.REMOTE: {}
            }
        self.lp = lp
        self.rp = rp
        self.lock = threading.Lock()

    def verify(self, path, kind):
        with self.lock:
            if (kind == ChangeFirewall.REMOTE):
                path = ''.join(path.split(self.rp)[1:])
            else:
                path = ''.join(path.split(self.lp)[1:])
            self._cleanup()
            reverse_kind = (kind == ChangeFirewall.REMOTE) and ChangeFirewall.LOCAL or ChangeFirewall.REMOTE
            if path in self.changes[reverse_kind]:
                return False
            self.changes[kind].update({path: time.time()})
            return True

    def _cleanup(self):
        for key in self.changes:
            changes = self.changes[key]
            for (key, value) in changes.items():
                if value < (time.time() - 5):
                    del changes[key]


@click.command()
@click.argument('local-path')
@click.argument('remote-path')
@click.option('--local-tmp', default='/tmp', help='Local rir to store tmp files (defaults to /tmp)')
@click.option('--remote-tmp', default='/tmp', help='Remote dir to store tmp files (defaults to /tmp)')
@click.option('--remote-username', default=None, help='Username on remote machine')
@click.option('--remote-python', default='python2', help='Remote python path')
def main(local_path, remote_path, local_tmp, remote_tmp, remote_username, remote_python):
    if subprocess.call(['which', 'rsync']) != 0:
        sys.exit(1)

    def normalize_dir_path(path):
        if not path.endswith('/'):
            return path + '/'
        else:
            return path

    local_path = normalize_dir_path(local_path)
    remote_path = normalize_dir_path(remote_path)

    from get_changes import make_observer
    from remote_start import make_remote_observer
    observed_path = local_path

    event_handler = RSyncEventHandler(local_path, remote_path, local_tmp, remote_tmp)
    remote_changed_paths = []

    ci = ChangeFirewall(local_path, remote_path.split(':')[1])

    def change_consumer(path):
        if ci.verify(path, ChangeFirewall.LOCAL):
            event_handler.changed_paths.insert(0, path)

    def remote_change_consumer(path):
        if ci.verify(path, ChangeFirewall.REMOTE):
            remote_changed_paths.insert(0, path)

    observer = make_observer(observed_path, change_consumer)
    observer.start()
    remote_observer = make_remote_observer(remote_path.split(':')[0], remote_username,
                                           remote_path.split(':')[1], remote_change_consumer, remote_python)
    remote_observer.start()

    try:
        while True:
            time.sleep(0.5)
            changed_paths = []
            while event_handler.changed_paths:
                changed_paths.append(event_handler.changed_paths.pop())
            changed_paths = list(set(changed_paths))
            changed_paths2 = []
            for path in changed_paths:
                path = [path]
                while path[0] != '/':
                    changed_paths2.insert(0, path[0])
                    path[0] = os.path.dirname(path[0])
            changed_paths = list(set(changed_paths2))
            if changed_paths:
                event_handler.rsync(changed_paths)

            changed_paths = []
            while remote_changed_paths:
                changed_paths.append(remote_changed_paths.pop())
            changed_paths = list(set(changed_paths))
            changed_paths2 = []
            for path in changed_paths:
                path = [path]
                while path[0] != '/':
                    changed_paths2.insert(0, path[0])
                    path[0] = os.path.dirname(path[0])
            changed_paths = list(set(changed_paths2))
            if changed_paths:
                event_handler.rev_rsync(changed_paths)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        observer.stop()
        remote_observer.stop()
    observer.join()
    remote_observer.join()


if __name__ == '__main__':
    main()
