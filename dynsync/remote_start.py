import sys
import paramiko
from os.path import expanduser
import time

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
config_file = file(expanduser('~/.ssh/config'))
config = paramiko.config.SSHConfig()
config.parse(config_file)
hostinfo = config.lookup('localhost')
hostname = hostinfo['hostname']
client.connect(hostname, username='emdej')
stdin, stdout, stderr = client.exec_command('python2.7 - /home/emdej/git/ul-phy', get_pty=False)
with open('get_changes.py', 'r') as f:
    stdin.write(f.read())
stdin.flush()
stdin.channel.shutdown_write() #send EOF

try:
    while not stdout.channel.eof_received:
        line = stdout.readline()
        if line:
            print line
except (KeyboardInterrupt, SystemExit):
    pass
finally:
    stdin.channel.close()
    stdin.channel.transport.close()
