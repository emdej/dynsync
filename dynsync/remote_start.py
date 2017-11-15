import paramiko
from os.path import expanduser
from threading import Thread

class RemoteExecutor():
    def __init__(self, hostname, username, remote_python):
        self.hostname = hostname
        self.username = username
        self.remote_python = remote_python

    def execute(self, script, params, stdout_consumer):
        self._connect_ssh()
        stdin, stdout, stderr = self.client.exec_command('%s - %s' % (self.remote_python, params), get_pty=False)
        with open(script, 'r') as f:
            stdin.write(f.read())
        stdin.flush()
        stdin.channel.shutdown_write() #send EOF
        try:
            while not stdout.channel.closed:
                line = stdout.readline()
                if line:
                    stdout_consumer(line)
                else:
                    break
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.close()

    def close(self):
        self.client.close()

    def _connect_ssh(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        config_file = file(expanduser('~/.ssh/config'))
        config = paramiko.config.SSHConfig()
        config.parse(config_file)
        hostinfo = config.lookup(self.hostname)
        hostname = hostinfo['hostname']
        client.connect(hostname, username=self.username)
        self.client = client

class RemoteObserver():
    def __init__(self, hostname, username, path, change_consumer, remote_python):
        self.remote_executor = RemoteExecutor(hostname, username, remote_python)
        self.path = path

        def consumer_wrapper(line):
            stripped = line.strip(' \b\n')
            if (stripped):
                change_consumer(stripped)

        self.change_consumer = consumer_wrapper

    def start(self):
        def runner():
            self.remote_executor.execute("get_changes.py", self.path, stdout_consumer=self.change_consumer)
        self.thr = Thread(target=runner)
        self.thr.start()

    def stop(self):
        self.remote_executor.close()

    def join(self):
        self.thr.join()

def make_remote_observer(hostname, username, path, change_consumer, remote_python):
    return RemoteObserver(hostname, username, path, change_consumer, remote_python)
