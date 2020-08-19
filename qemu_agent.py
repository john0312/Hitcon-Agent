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
            except NoSuchProcess:
                response = 'No such process'
                connection.sendall(response)

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
    finally:
        connection.close()