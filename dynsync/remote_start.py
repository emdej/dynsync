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

#     transport = client.get_transport()
#     channel = transport.open_session()

    #stdin, stdout, stderr = client.exec_command('TERM=xterm /usr/bin/python2.7 - /home/emdej/git/ul-phy', get_pty=True)
    stdin, stdout, stderr = client.exec_command('python2.7 - /home/emdej/git/ul-phy', get_pty=False)
    
    
    with open('get_changes.py', 'r') as f:
#         x = '''
# import signal\n
# import os
# import sys
# def sigint_handler(signal, frame): f = open("/tmp/logfile2", "a"); f.write(str(signal)); f.close()
# signal.signal(signal.SIGINT, sigint_handler)
# signal.signal(signal.SIGHUP, sigint_handler)
# signal.signal(signal.SIGTERM, sigint_handler)
# signal.signal(signal.SIGPIPE, sigint_handler)
# import time\nwhile True:\n    print "dupa"\n    time.sleep(1);\n    import sys; sys.stdout.flush()\n'''
#         stdin.write(x)

#         stdin.write('print "dupa"\n')
#         x = 
#         channel.sendall(x)
#         print x
#         x = '''import time\nwhile True:\n    print "dupa"\n    time.sleep(1);\n    import sys; sys.stdout.flush()\n'''
        stdin.write(f.read())
#     stdin.write("\x17")
#     stdin.write("\x03")
#     stdin.write("\x04")
    stdin.flush()

#     stdin.close()
    stdin.channel.shutdown_write() #send EOF
#     import pdb;pdb.set_trace()
    import signal
    import time
#     def sigint_handler(signal, frame):
#         print 'Interrupted'
#         import sys; sys.stdout.flush()
# #         import pdb;pdb.set_trace()
# #         stdin.channel.send("\x03")
# #         stdin.write("\x03")
# #         stdin.flush()
#         stdin.channel.close()
#         stdin.channel.transport.close()
#         sys.exit(0)
#     signal.signal(signal.SIGINT, sigint_handler)
#     signal.signal(signal.SIGHUP, sigint_handler)
#     signal.signal(signal.SIGTERM, sigint_handler)

    try:
#         stdout.channel.settimeout(1)
        while not stdout.channel.eof_received:
#             import pdb;pdb.set_trace()
#             if stdout.readable():
            if stdout.channel.recv_ready() or True:
                line = stdout.readline()
#                 for line in iter(lambda: stdout.readline(2048), ""):
#                 for line in stdout.xreadlines():
                if line:
                    print line
                else:
                    print stdout.channel.eof_received #True
                    sys.exit(0) #remote end error
            else:
                time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        stdin.channel.close()
        stdin.channel.transport.close()
