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

# This is a simple client for testing the guest agent.


import logging
import os
import argparse
import grpc
from concurrent import futures

import irc_pb2, irc_pb2_grpc

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='IRC Injector client.')
    # gRPC connection details
    parser.add_argument('--host', type=str, default='127.0.0.1', help='The host to connect to')
    parser.add_argument('--port', type=int, default=29130, help='The port to connect to')

    # Commands 
    parser.add_argument('--msg', type=str, help='Action to carry out.')

    args = parser.parse_args()
    with grpc.insecure_channel('%s:%d'%(args.host, args.port)) as channel:
        stub = irc_pb2_grpc.CmdInjectorStub(channel)

        req = irc_pb2.InjectReq(msg=args.msg)
        stub.Inject(req)
        
if __name__ == "__main__":
    main()
