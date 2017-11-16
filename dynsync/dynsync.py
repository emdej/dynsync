import os
import sys
import time
import subprocess

import click
from watchdog.events import FileSystemEventHandler

# OSError: inotify watch limit reached

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
        opts = []
        if changes:
            local_changes = [''.join(abs_change.split(self.local_path)[1:]) for abs_change in changes]
            local_changes.sort()
            cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} --include-from=- {} {}".format(self.remote_tmp, self.local_path, self.remote_path)
        else:
            local_changes = []
            cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} {} {}".format(self.remote_tmp, self.local_path, self.remote_path)
        with open(os.devnull, 'w') as DEVNULL:
            try:
                import shlex
                p = subprocess.Popen(
                    shlex.split(cmd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )
                input = ''.join(['+ /%s\n' % change for change in local_changes if change])
                input += '- *\n'
                print "includes:", input
                stdout, stderr = p.communicate(input=input.encode('utf8'))
            except Exception as e:
                import pdb;pdb.set_trace()
            p.wait()
            print stdout
            print stderr

    def rev_rsync(self, changes=None):
        local_changes = [''.join(abs_change.split(self.remote_path_short)[1:]) for abs_change in changes]
        local_changes.sort()
        cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} --include-from=- {} {}".format(self.local_tmp, self.remote_path, self.local_path)
        with open(os.devnull, 'w') as DEVNULL:
            try:
                import shlex
                p = subprocess.Popen(
                    shlex.split(cmd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )
                input = ''.join(['+ /%s\n' % change for change in local_changes if change])
                input += '- *\n'
                print "reverse includes:", input
                stdout, stderr = p.communicate(input=input.encode('utf8'))
            except Exception as e:
                import pdb;pdb.set_trace()
            p.wait()
            print stdout
            print stderr

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

    from get_changes import make_observer
    from remote_start import make_remote_observer
    observed_path = local_path

    event_handler = RSyncEventHandler(local_path, remote_path, local_tmp, remote_tmp)
    remote_changed_paths = []

    def change_consumer(path):
        event_handler.changed_paths.insert(0, path)

    def remote_change_consumer(path):
        print "remote change:", path
        remote_changed_paths.insert(0, path)

    observer = make_observer(observed_path, change_consumer)
    observer.start()
    remote_observer = make_remote_observer(remote_path.split(':')[0], remote_username, remote_path.split(':')[1], remote_change_consumer, remote_python)
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

    except KeyboardInterrupt:
        observer.stop()
        remote_observer.stop()
    observer.join()
    remote_observer.join()

if __name__ == '__main__':
    main()
