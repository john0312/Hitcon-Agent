import os
import socket
import sys
import subprocess

import random

### 
# import subprocess
# proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True)
# (out, err) = proc.communicate()
# print "program output:", out
###

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostName = socket.gethostname()
server_addr = (hostName, 12345)
# if binding at 'localhost', then cannot connect in from external side
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

        # spawn a new socket
        host_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '127.0.0.1'
        port = 54321

        if data.startswith('POST /host/api/shellcode :'):
            rand_port = random.randint(1025, 65535)
            # connection.send(str(rand_port))
            print 'Random Port on %d', rand_port
            shell_code = data.split('POST /host/api/shellcode :')[1]
            isPidAppend = shell_code.split(',')
            prefix = 'POST /api/sendexploit :'
            if len(isPidAppend) < 2:
                data = prefix + str(isPidAppend[0]) + ',' + str(rand_port)
            else:
                data = prefix + str(isPidAppend[0]) + ',' + str(rand_port) + ',' + str(isPidAppend[1])
            host_sock.connect((host,port))
            host_sock.send(data)
            response = host_sock.recv(4096)
            # print response
            ### FIXME: return port number?
            connection.sendall(response)
            host_sock.close()

        elif data.startswith('POST /host/api/status :'):
            request_port = data.split('POST /host/api/status :')[1]
            host_sock.connect((host,port))
            prefix = 'POST /api/getUserStatus :'
            data = prefix + request_port
            host_sock.send(data)
            response = host_sock.recv(4096)
            connection.sendall(response)
            host_sock.close()
        #     print >>sys.stderr, 'sending data back to the client'
        #     connection.sendall(data)
    finally:
        connection.close()