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

# from ctypes import *
import ctypes
# from PyShellcode import ExecutableCode
from cgroupLimit import *

import sys
import os
import mmap
import base64
import time
import psutil

### FIXME: test function
import socket
###

# hello_code = "\x65\x78\x61\x6d\x70\x6c\x65\x5f\x73\x68\x65\x6c\x6c\x63\x6f\x64\x65\x5f\x66\x69\x6c\x65\x0a"
# shell_code = b"\xeb\x13\xb8\x01\x00\x00\x00\xbf\x01\x00\x00\x00\x5e\xba\x0f\x00\x00\x00\x0f\x05\xc3\xe8\xe8\xff\xff\xff\x48\x65\x6c\x6c\x6f\x2c\x20\x57\x6f\x72\x6c\x64\x21\x0a"

'''
def memory_limit():
    with open('/proc/meminfo', 'r') as mem:
'''     

def child_task(payload, port):
    new_process = -1
    new_process = os.fork()
    if new_process == 0:
        pid = os.getpid()
        # FIXME:
        # p = psutil.Process(pid)
        # p.rlimit(psutil.RLIMIT_NOFILE, (128, 128))
        # p.rlimit(psutil.RLIMIT_FSIZE, (1024, 1024))
        # p.rlimit(psutil.RLIMIT_CPU, (1, 1))
        # p.
        set_limit('CPU', 1)
        set_limit('VMEM', 1024)
        create_rlimits()
        # p.rlimit(psutil.R)
        # cpu_percent

        print('Hi, My pid is ', pid)
        print('encoded string : ' + payload)
        decodeShell = base64.b64decode(payload)
    ### Sample 
        page_rwx_value = 0x40
        process_all = 0x1F0FFF
        memcommit = 0x00001000
        mm = mmap.mmap(-1, len(decodeShell), flags=mmap.MAP_SHARED | mmap.MAP_ANONYMOUS, prot=mmap.PROT_WRITE | mmap.PROT_READ | mmap.PROT_EXEC)
        mm.write(decodeShell)
        
        restype = ctypes.c_int64
        argtypes = tuple()
        ctypes_buffer = ctypes.c_int.from_buffer(mm)
        function = ctypes.CFUNCTYPE(restype, *argtypes)(ctypes.addressof(ctypes_buffer))
        function()
        ### FIXME: test function - port binding
        shell_binding = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        child_host = '127.0.0.1'
        child_port = int(port)
        bind_addr = (child_host, child_port)
        shell_binding.bind(bind_addr)
        shell_binding.listen(1)
        print('child waiting connection', file=sys.stderr)
        connection, client_addr = shell_binding.accept()
        ###
    ### Sample 
    time.sleep(1)
    print('child process done!')
    print('pid : %d' % (new_process))
    if new_process == -1:
        return False, None
    else:
        return True, new_process
    # os._exit(0)
