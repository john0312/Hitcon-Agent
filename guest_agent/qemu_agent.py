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
        data = connection.recv(4096)
        data = data.strip('\n')
        print >>sys.stderr, 'received "%s"' % data
        if data.startswith('POST /api/getUserStatus :'):
            run_pid = data.split('POST /api/getUserStatus :')[1]
            #
            try:
                process = psutil.Process(int(run_pid))
                status = process.status()
                ### FIXME: Not sure cpu usage is correct
                cpu = process.cpu_percent(interval=1)
                memory = process.memory_info()[0]
                if (status != psutil.STATUS_ZOMBIE and status != psutil.STATUS_DEAD and status != psutil.STATUS_STOPPED and status != psutil.STATUS_TRACING_STOP) or status == psutil.STATUS_RUNNING:
                    response = str(status) + ',' + str(cpu) + ',' + str(memory)
                    connection.sendall(response)
                else:
                    response = 'Process Dead'
                    connection.sendall(response)
                #all_process = os.popen('ps aux | grep "python"').read()
            except psutil.NoSuchProcess:
                response = 'No such process'
                connection.sendall(response)

        elif data.startswith('POST /api/sendexploit :'):
            # data = prefix + shell_code + ',' + str(rand_port) + ',' + str(kill_pid)
            print >>sys.stderr, 'Client exploit sending'
            response = ''
            ## FIXME: subprocess / multiprocessing
            ## Is fork() dangerous for each user?
            sub_pid = os.fork()
            if sub_pid == 0:
                payload = data.split('POST /api/sendexploit :')[1]
                autoPane = payload.split(',')
                if len(autoPane) > 2:
                    killproc = payload.split(',')[2]
                    kill_cmd = 'kill ' + str(killproc)
                    os.system(kill_cmd)
                b64code = payload.split(',')[0]
                userPort = payload.split(',')[1]
                result, pid = child_task(b64code, userPort)
                if result:
                    response = 'success,'+str(pid)
                else:
                    response = 'false'
            # print >>sys.stderr, 'sending data back to the client'
            # pid, status = os.waitpid(sub_pid, 0)
            connection.sendall(response)
        elif data.startswith('POST /api/getAliveUser :'):
            # netstat -plnt
            connNet = os.popen('netstat -pnltu | grep -i "54321"').read()
            connection.sendall(connNet)
            #
    finally:
        connection.close()
