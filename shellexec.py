# from ctypes import *
import ctypes
# from PyShellcode import ExecutableCode

import sys
import os
import mmap
import base64

### FIXME: test function
import socket
###

# hello_code = "\x65\x78\x61\x6d\x70\x6c\x65\x5f\x73\x68\x65\x6c\x6c\x63\x6f\x64\x65\x5f\x66\x69\x6c\x65\x0a"
# shell_code = b"\xeb\x13\xb8\x01\x00\x00\x00\xbf\x01\x00\x00\x00\x5e\xba\x0f\x00\x00\x00\x0f\x05\xc3\xe8\xe8\xff\xff\xff\x48\x65\x6c\x6c\x6f\x2c\x20\x57\x6f\x72\x6c\x64\x21\x0a"

def child_task(payload, port):
    new_process = os.fork()
    if new_process == 0:
        print 'Hi, My pid is ', os.getpid()
        print 'encoded string : ' + payload
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
        print >>sys.stderr, 'child waiting connection'
        connection, client_addr = shell_binding.accept()
        ###
    ### Sample 
    print 'child process done!'
    return 'success'
    # os._exit(0)