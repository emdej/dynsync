import sys
import os
def is_remote():
    return len(sys.argv) >= 2 and "--remote" in sys.argv

def action():
    print os.uname()

action()

if not is_remote():
    import paramiko
    import subprocess
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    from os.path import expanduser
    config_file = file(expanduser('~/.ssh/config'))
    config = paramiko.config.SSHConfig()
    config.parse(config_file)
    hostinfo = config.lookup('localhost')

    hostname = hostinfo['hostname']
    client.connect(hostname, username='emdej')
#     stdin, stdout, stderr = client.exec_command('uname -a')
#     print stdout.readlines()
#     stdin, stdout, stderr = client.exec_command('/home/jarycki/virtualenv/bin/python2.7 - /home/emdej/git/ul-phy')

    transport = client.get_transport()
    channel = transport.open_session()

    stdin, stdout, stderr = client.exec_command('/usr/bin/python2.7 - /home/emdej/git/ul-phy')
    
    
    with open('get_changes.py', 'r') as f:
#         x = 
#         channel.sendall(x)
#         print x
#         x = '''import time\nwhile True:\n    print "dupa"\n    time.sleep(1);\n    import sys; sys.stdout.flush()\n'''
        stdin.write(f.read())
    stdin.flush()
    stdin.close()
    stdin.channel.shutdown_write() #send EOF
#     import pdb;pdb.set_trace()
    import signal
    def sigint_handler(signal, frame):
        print 'Interrupted'
        import sys; sys.stdout.flush()
        stdin.channel.close()
        stdin.channel.transport.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        while True:
#             import pdb;pdb.set_trace()
            line = stdout.readline(4096)
    #     for line in iter(lambda: stdout.readline(2048), ""):
#             if line:
            print line
    except (KeyboardInterrupt, SystemExit) as e:
        import pdb;pdb.set_trace()
        stdin.channel.close()
        stdin.channel.transport.close()
#     print "ERR:"
#     print stderr.readlines()
