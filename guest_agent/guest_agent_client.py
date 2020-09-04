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

"""
Example usage
$ python3 guest_agent_client.py --host=127.0.0.1 --port=29120 --action=ping
$ python3 guest_agent_client.py --host=127.0.0.1 --port=29120 --action=runcmd '--cmd=echo HelloWorld'
$ python3 guest_agent_client.py --action=queryprocinfo
$ python3 guest_agent_client.py --action=procevent --timeout=5.0
"""

import logging
import os
import argparse
import grpc
import time
from concurrent import futures

import guest_agent_pb2, guest_agent_pb2_grpc

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Guest agent client.')
    # gRPC connection details
    parser.add_argument('--host', type=str, default='127.0.0.1', help='The host to connect to')
    parser.add_argument('--port', type=int, default=29120, help='The port to connect to')

    # Commands 
    parser.add_argument('--action', type=str, choices=['ping', 'runcmd', 'runsc', 'queryprocinfo', 'procevent'], help='Action to carry out.')
    parser.add_argument('--cmd', type=str, default='echo HelloWorld')
    parser.add_argument('--shellcode', type=str, default='6xO4AQAAAL8BAAAAXroPAAAADwXD6Oj///9IZWxsbywgV29ybGQhCgo=')
    parser.add_argument('--timeout', type=float, default=-1.0, help='Timeout for procevent')
    
    """
    --action=ping // No other arguments required.
    --action=runcmd --cmd=<CMD>
    --action=runsc --shellcode=<b64shellcode>
    --action=queryprocinfo
    --action=procevent [--timeout=<timeout>]
    """

    args = parser.parse_args()
    with grpc.insecure_channel('%s:%d'%(args.host, args.port)) as channel:
        f = grpc.channel_ready_future(channel)
        logging.info("Connecting...")
        f.result(timeout=5.0)
        logging.info("Connected")
        
        stub = guest_agent_pb2_grpc.GuestAgentStub(channel)
        
        if args.action == 'ping':
            response = stub.Ping(guest_agent_pb2.PingReq())
            if response.error == guest_agent_pb2.ErrorCode.ERROR_NONE:
                print("Ping successful")
            else:
                print("Ping failed: %s"%(str(response.error),))
        
        if args.action == 'runcmd':
            response = stub.RunCmd(guest_agent_pb2.RunCmdReq(cmd=args.cmd))
            if response.reply.error == guest_agent_pb2.ErrorCode.ERROR_NONE:
                print("Run CMD successful, pid=%d"%(response.pid))
            else:
                print("Run CMD failed: %s"%(str(response.reply.error),))
        
        if args.action == 'runsc':
            req = guest_agent_pb2.RunSCReq(shellcode=args.shellcode)
            response = stub.RunSC(req)
            if response.reply.error == guest_agent_pb2.ErrorCode.ERROR_NONE:
                print("Run CMD successful, pid=%d"%(response.pid))
            else:
                print("Run CMD failed: %s"%(str(response.reply.error),))
        
        if args.action == 'queryprocinfo':
            req = guest_agent_pb2.QueryProcInfoReq()
            response = stub.QueryProcInfo(req)
            if response.reply.error == guest_agent_pb2.ErrorCode.ERROR_NONE:
                print("Query Process Info successful, result:")
                print(response.info)
            else:
                print("Query process info failed: %s"%(str(response.reply.error),))

        if args.action == 'procevent':
            executor = futures.ThreadPoolExecutor(max_workers=8)
            stream = stub.ProcessEventListener(guest_agent_pb2.ProcessEventListenerReq())
            def killstream(s):
                time.sleep(args.timeout)
                stream.cancel()
            if args.timeout > 0.0:
                executor.submit(killstream, stream)
            try:
                for evt in stream:
                    print("Event: %s"%(str(evt),))
            except Exception:
                logging.exception("Done listening for event")
            executor.shutdown()

if __name__ == "__main__":
    main()
