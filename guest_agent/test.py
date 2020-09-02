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


import socket
import base64
from pwn import *

host = '172.17.0.2'
# host = '104.199.184.47'
port = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port)) # one parameter present address

# client.send('POST /api/getUserStatus : Hello World\r\n\r\n')
# response = client.recv(4096)
# print response
# print '---------------------------------'
# client.send('POST /api/sendexploit : \x12\x23\x34\x45\x56\x67\x78\x89')
# response = client.recv(4096)
# print response

print '---------------------------------'
shell_code = b"\xeb\x13\xb8\x01\x00\x00\x00\xbf\x01\x00\x00\x00\x5e\xba\x0f\x00\x00\x00\x0f\x05\xc3\xe8\xe8\xff\xff\xff\x48\x65\x6c\x6c\x6f\x2c\x20\x57\x6f\x72\x6c\x64\x21\x0a"

client.send('POST /host/api/shellcode :' + base64.b64encode(shell_code))
# client.send('POST /host/api/shellcode :' + base64.b64encode(shell_code) + ',' + '25180')
response = client.recv(4096)
resp = response.split(',')
if resp[0] == 'success':
    log.success('PID: ' + str(resp[1]))

# print '---------------------------------'
# pid = 25180
# client.send('POST /host/api/status :' + str(pid))
# response = client.recv(4096)
# log.success('Process Status: ' + response)

# a = 'aaa'
# b = a.split(',')
# # print len(b)
# if len(b) < 2:
#     print 'No value append'
# else:
#     print 'hello world'
