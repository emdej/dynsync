from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import sleep
from sys import stdout

def make_observer(path, change_consumer):
    class EventHandler(FileSystemEventHandler):
        def __init__(self, change_consumer):
            self.change_consumer = change_consumer
    
        def on_any_event(self, event):
            path_properties = ('src_path', 'dest_path')
            for path in (getattr(event, prop, None) for prop in path_properties):
                if path:
                    self.change_consumer(path)

    observer = Observer()
    observer.schedule(EventHandler(change_consumer), path, recursive=True)
    return observer

if __name__ == '__main__':
    from sys import argv, exit
    if len(argv) != 2:
        print "usage: %s <path to observe>" % argv[0]
        exit(1)

    observed_path = argv[1]

    def change_consumer(path):
        print path
        stdout.flush()
    observer = make_observer(observed_path, change_consumer)
    observer.start()
    try:
        while True:
            sleep(1)
            stdout.write(" \b")
            stdout.flush()
    except (IOError, KeyboardInterrupt, SystemExit):
        observer.stop()
    observer.join()
