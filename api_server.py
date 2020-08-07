import os
import socket
import sys
import subprocess

import proc
import psutil

from shellexec import child_task

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_addr = ('localhost', 54321)
print >>sys.stderr, 'start server on %s port %s' % server_addr
sock.bind(server_addr)

sock.listen(1)

while True:
    print >>sys.stderr, 'waiting for connection'
    connection, client_addr = sock.accept()
    try:
        print >>sys.stderr, 'connection from', client_addr
        # while True:
        data = connection.recv(1024)
        data = data.strip('\n')
        print >>sys.stderr, 'received "%s"' % data
        if data.startswith('POST /api/getUserStatus :'):
            run_pid = data.split('POST /api/getUserStatus :')[1]
            #
            process = psutil.Process(int(run_pid))
            status = process.status()
            #all_process = os.popen('ps aux | grep "python"').read()
            connection.sendall(status)

        elif data.startswith('POST /api/sendexploit :'):
            print >>sys.stderr, 'Client exploit sending'
            response = ''
            ## FIXME: subprocess / multiprocessing
            sub_pid = os.fork()
            if sub_pid == 0:
                payload = data.split('POST /api/sendexploit :')[1]
                b64code = payload.split(',')[0]
                userPort = payload.split(',')[1]
                response = child_task(payload, userPort)
            print >>sys.stderr, 'sending data back to the client'
            # pid, status = os.waitpid(sub_pid, 0)
            connection.sendall(response)
        elif data.startswith('POST /api/getAliveUser :'):
            # netstat -plnt
            connNet = os.popen('netstat -pnltu | grep -i "54321"').read()
            connection.sendall(connNet)
            #
        else:
            print >>sys.stderr, 'No data from ', client_addr
            break
    finally:
        connection.close()