import socket
import base64

host = '127.0.0.1'
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
# print '---------------------------------'
# shell_code = b"\xeb\x13\xb8\x01\x00\x00\x00\xbf\x01\x00\x00\x00\x5e\xba\x0f\x00\x00\x00\x0f\x05\xc3\xe8\xe8\xff\xff\xff\x48\x65\x6c\x6c\x6f\x2c\x20\x57\x6f\x72\x6c\x64\x21\x0a"

# client.send('POST /host/api/shellcode :' + base64.b64encode(shell_code))
# response = client.recv(4096)
# print response

print '---------------------------------'
pid = raw_input()
client.send('POST /host/api/status :' + str(pid))
response = client.recv(4096)
print response