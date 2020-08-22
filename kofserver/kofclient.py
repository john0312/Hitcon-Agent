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
$ python3 kofclient.py --host=127.0.0.1 --port=29110 --action=creategame --game_name=game1 --scenario=MyScenario
"""

import logging
import os
import argparse
import grpc

from kofserver_pb2 import ErrorCode as KOFErrorCode
import kofserver_pb2, kofserver_pb2_grpc

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='KOF client.')
    # gRPC connection details
    parser.add_argument('--host', type=str, default='127.0.0.1', help='The host to connect to')
    parser.add_argument('--port', type=int, default=29110, help='The port to connect to')

    # Commands 
    parser.add_argument('--action', type=str, choices=['creategame'], help='Action to carry out.')
    parser.add_argument('--game_name', type=str, default='MyGame')
    parser.add_argument('--scenario', type=str, default='MyScenario')
    
    """
    --action=creategame --game_name=<GameName> --name=<Scenario>
    """

    args = parser.parse_args()
    with grpc.insecure_channel('%s:%d'%(args.host, args.port)) as channel:
        stub = kofserver_pb2_grpc.KOFServerStub(channel)
        
        if args.action == 'creategame':
            req = kofserver_pb2.CreateGameReq(gameName=args.game_name, scenarioName=args.scenario)
            reply = stub.CreateGame(req)
            if reply.error == KOFErrorCode.ERROR_NONE:
                print("Create game successful")
            else:
                print("Create game failed: %s"%(str(reply.error),))

if __name__ == "__main__":
    main()
