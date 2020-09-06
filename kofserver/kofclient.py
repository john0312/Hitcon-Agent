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
$ python3 kofclient.py --action=startgame --game_name=game1
$ python3 kofclient.py --action=destroygame --game_name=game1
$ python3 kofclient.py --action=querygame --game_name=
$ python3 kofclient.py --action=playerreg --game_name=game1 --player=John
$ python3 kofclient.py --action=playerinfo --game_name=game1 --player=John
$ python3 kofclient.py --action=playerissuecmd --game_name=game1 --player=John '--cmd=echo Start; sleep 30; echo End'
$ python3 kofclient.py --action=queryscore --game_name=game1 --player=
$ python3 kofclient.py --action=gameevent --game_name=game1
"""

import logging
import os
import argparse
import grpc
from concurrent import futures

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
    parser.add_argument('--action', type=str, choices=['creategame', 'startgame', 'destroygame', 'querygame', 'playerreg', 'playerinfo', 'playerissuecmd', 'queryscore', 'gameevent'], help='Action to carry out.')
    parser.add_argument('--game_name', type=str, default='MyGame')
    parser.add_argument('--scenario', type=str, default='MyScenario')
    parser.add_argument('--player', type=str, default='John')
    parser.add_argument('--cmd', type=str, default='sleep 30')
    parser.add_argument('--timeout', type=float, default=-1.0, help='Timeout for gameevent')
    
    """
    --action=creategame --game_name=<GameName> --name=<Scenario>
    --action=startgame --game_name=<GameName>
    --action=destroygame --game_name=<GameName>
    --action=querygame [--game_name=<GameName>]
    --action=playerreg --game_name=<GameName> --player=<PlayerName>
    --action=playerinfo --game_name=<GameName> --player=<PlayerName>
    --action=playerissuecmd --game_name=<GameName> --player=<PlayerName> --cmd=<Cmd>
    --action=queryscore --game_name=<GameName> --player=<PlayerName>
    --action=gameevent --game_name=<GameName>
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

        if args.action == 'startgame':
            req = kofserver_pb2.StartGameReq(gameName=args.game_name)
            reply = stub.StartGame(req)
            if reply.error == KOFErrorCode.ERROR_NONE:
                print("Start game successful")
            else:
                print("Start game failed: %s"%(str(reply.error),))
        
        if args.action == 'destroygame':
            req = kofserver_pb2.DestroyGameReq(gameName=args.game_name)
            reply = stub.DestroyGame(req)
            if reply.error == KOFErrorCode.ERROR_NONE:
                print("Destroy game successful")
            else:
                print("Destroy game failed: %s"%(str(reply.error),))
        
        if args.action == 'querygame':
            req = kofserver_pb2.QueryGameReq(gameName=args.game_name)
            reply = stub.QueryGame(req)
            if reply.reply.error == KOFErrorCode.ERROR_NONE:
                print("Result:")
                print(reply)
            else:
                print("Query game failed: %s"%(str(reply.reply.error),))
        
        if args.action == 'playerreg':
            req = kofserver_pb2.PlayerRegisterReq(gameName=args.game_name, playerName=args.player)
            reply = stub.PlayerRegister(req)
            if reply.error == KOFErrorCode.ERROR_NONE:
                print("Player register successful")
            else:
                print("Player register failed: %s"%(str(reply.error),))
        
        if args.action == 'playerinfo':
            req = kofserver_pb2.PlayerInfoReq(gameName=args.game_name, playerName=args.player)
            reply = stub.PlayerInfo(req)
            if reply.reply.error == KOFErrorCode.ERROR_NONE:
                print("Result:")
                print(reply)
            else:
                print("Query player info failed: %s"%(str(reply.reply.error),))
        
        if args.action == 'playerissuecmd':
            req = kofserver_pb2.PlayerIssueCmdReq(gameName=args.game_name, playerName=args.player, cmd=args.cmd)
            reply = stub.PlayerIssueCmd(req)
            if reply.reply.error == KOFErrorCode.ERROR_NONE:
                print("Player Issue Command successful, result: ")
                print(reply)
            else:
                print("Player Issue Command failed: %s"%(str(reply.reply.error),))
        
        if args.action == 'queryscore':
            req = kofserver_pb2.QueryScoreReq(gameName=args.game_name, playerName=args.player)
            reply = stub.QueryScore(req)
            if reply.reply.error == KOFErrorCode.ERROR_NONE:
                print("Query score successful, Result:")
                print(reply)
            else:
                print("Query score failed: %s"%(str(reply.reply.error),))
        
        if args.action == 'gameevent':
            executor = futures.ThreadPoolExecutor(max_workers=8)

            req = kofserver_pb2.GameEventListenerReq(gameName=args.game_name)
            stream = stub.GameEventListener(req)
            def killstream():
                time.sleep(args.timeout)
                stream.cancel()
            if args.timeout > 0.0:
                executor.submit(killstream)
            try:
                for evt in stream:
                    print("Event: %s"%(str(evt),))
            except Exception:
                logging.exception("Done listening for event")
            executor.shutdown
        
if __name__ == "__main__":
    main()
