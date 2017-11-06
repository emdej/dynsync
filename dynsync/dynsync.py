import os
import sys
import time
import subprocess

import click
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.observers.api import DEFAULT_OBSERVER_TIMEOUT


# OSError: inotify watch limit reached

def _get_what(event):
    return 'directory' if event.is_directory else 'file'


class RSyncEventHandler(FileSystemEventHandler):
    def __init__(self, local_path, remote_path, tmp, ignores=[]):
        self.ignores = ignores
        self.local_path = local_path
        self.remote_path = remote_path
        self.changed_paths = []
        self.tmp = tmp
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
            cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} --include-from=- {} {}".format(self.tmp, self.local_path, self.remote_path)
        else:
            local_changes = []
            cmd = "rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir={} {} {}".format(self.tmp, self.local_path, self.remote_path)
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

@click.command()
@click.argument('local-path')
@click.argument('remote-path')
@click.option('--tmp', default='/tmp', help='Dir to store tmp files')
def main(local_path, remote_path, tmp):
    if subprocess.call(['which', 'rsync']) != 0:
        sys.exit(1)

    from get_changes import make_observer
    observed_path = local_path

    event_handler = RSyncEventHandler(local_path, remote_path, tmp)

    def change_consumer(path):
        event_handler.changed_paths.insert(0, path)

    observer = make_observer(observed_path, change_consumer)
    observer.start()
#     remote_observer = start_remote_observer(remote_path)
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
    except KeyboardInterrupt:
        observer.stop()
#         remote_observer.stop()
    observer.join()
#     remote_observer.join()

if __name__ == '__main__':
    main()
