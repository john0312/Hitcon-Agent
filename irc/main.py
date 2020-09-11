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

import logging
import grpc
from concurrent import futures
import queue
import asyncio

from irc import IRC
from agent import Agent
from config import Config
import irc_pb2_grpc, irc_pb2
from cmd_rx import CmdRx
from msg_tx import MsgTx

class CmdInjector:
    def __init__(self, executor, irc):
        self.executor = executor
        self.irc = irc
    
    def Inject(self, request, context):
        self.irc.InjectCommand(None, request.msg)
        return irc_pb2.InjectRep()

# TODO: Enhance performance
def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize the config.
    Config.Init()

    # Initialize agent
    executor = futures.ThreadPoolExecutor(max_workers=1024)

    agent = Agent(executor)

    # Initialize IRC
    irc = IRC(nickname=Config.conf()['botNickName'])

    q = queue.Queue(maxsize=64)
    def onCmdRx(n, m):
        irc.InjectCommand(n, m)
        msg = '%s: %s\n'%(n, m)
        q.put(msg)
    crx = CmdRx(executor, onCmdRx)
    crx.Start()
    mtx = MsgTx(executor, q)
    mtx.Start()

    def tmpA(msg):
        q.put(msg)

    irc.InitQueue(executor, tmpA)
    #irc.SetChannel(Config.conf()['channel'])
    irc.ResetGame()
    irc.SetAgent(agent)

    # grpc
    injector = CmdInjector(executor, irc)
    server = grpc.server(executor)
    irc_pb2_grpc.add_CmdInjectorServicer_to_server(injector, server)
    server.add_insecure_port('[::]:29130')
    server.start()

    loop = asyncio.get_event_loop()
    irc.loop = loop
    irc.channel = 'channel'
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.info("Loop ending")
        crx.Shutdown()
        mtx.Shutdown()
        loop.close()

    # irc.run(hostname='127.0.0.1', port=Config.conf()['ircSSLPort'], tls=True, tls_verify=False)

if __name__ == '__main__':
    main()
