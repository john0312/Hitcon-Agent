# Copyright (c) 2020 HITCON Agent Contributors
# See CONTRIBUTORS file for the list of HITCON Agent Contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import socket
import sys
import subprocess
import logging
# logging.basicConfig(level=logging.INFO)

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
# logging.debug('start server on %s port %s' % server_addr)
print 'start server on %s port %s' % server_addr
sock.bind(server_addr)

sock.listen(1)

while True:
    # print >>sys.stderr, 'waiting for connection'
    print 'waiting for connection'
    connection, client_addr = sock.accept()
    sys.stdout = open('host_agent.log', 'a+')
    sys.stderr = open('host_error.log', 'a+')
    try:
        # print >>sys.stderr, 'connection from', client_addr
        print('connection from', client_addr)
        # while True:
        data = connection.recv(4096)
        data = data.strip('\n')
        # print >>sys.stderr, 'received "%s"' % data
        # logging.debug('received "%s"' % data)
        print 'received "%s"' % data

        if data.startswith('POST /host/api/shellcode :'):
            rand_port = random.randint(1025, 65535)
            # connection.send(str(rand_port))
            # print 'Random Port on %d', rand_port
            prefix = 'POST /api/sendexploit :'
            # logging.critical('Random Port on %d', rand_port)
            print 'Random Port on %d', rand_port
            shell_code = data.split('POST /host/api/shellcode :')[1]
            isPidAppend = shell_code.split(',')
            if len(isPidAppend) < 2:
                data = prefix + str(isPidAppend[0]) + ',' + str(rand_port)
            else:
                data = prefix + str(isPidAppend[0]) + ',' + str(rand_port) + ',' + str(isPidAppend[1])
            # spawn a new socket
            host_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = '127.0.0.1'
            port = 54321
            host_sock.connect((host,port))
            host_sock.send(data)
            response = host_sock.recv(4096)
            # logging.info('qemu-agent response : ' + str(response))
            print 'qemu-agent response : ' + str(response)
            # print response
            connection.sendall(response)
            host_sock.close()
            print '------------------------------------'

        elif data.startswith('POST /host/api/status :'):
            request_port = data.split('POST /host/api/status :')[1]
            # spawn a new socket
            host_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = '127.0.0.1'
            port = 54321
            host_sock.connect((host,port))
            prefix = 'POST /api/getUserStatus :'
            data = prefix + request_port
            host_sock.send(data)
            response = host_sock.recv(4096)
            # logging.info('qemu-agent response : ' + str(response))
            print 'qemu-agent response : ' + str(response)
            connection.sendall(response)
            host_sock.close()
            print '------------------------------------'
        #     print >>sys.stderr, 'sending data back to the client'
        #     connection.sendall(data)
    finally:
        connection.close()
        # sys.stdout.close()
        # sys.stderr.close()
