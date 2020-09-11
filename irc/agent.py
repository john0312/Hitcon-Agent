# -*- coding: utf-8 -*-
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
import asyncio
import grpc
from config import Config
import kofserver_pb2, kofserver_pb2_grpc
from kofserver_pb2 import ErrorCode as KOFErrorCode

class Agent:
    def __init__(self, executor):
        # TODO: Check connection health
        channel = grpc.insecure_channel('%s:%d'%(Config.conf()['agentHost'], Config.conf()['agentPort']))
        logging.info("Agent Connecting...")
        f = grpc.channel_ready_future(channel)
        try:
            f.result(timeout=Config.conf()['agentConnectTimeout'])
            logging.info("Agent Connected.")
        except Exception:
            logging.error("Agent failed to connect.")
            return None

        # The gRPC channel
        self.channel = channel
        # The kofserver gRPC stub
        #self.stub = kofserver_pb2_grpc.KOFServerStub(self.channel)

        # Store executor for future use.
        self.executor = executor
    
    def Stub(self):
        return kofserver_pb2_grpc.KOFServerStub(self.channel)

    def ListenForGameEvent(self, gameName, callback):
        def ListenForGameEventInternal():
            try:
                req = kofserver_pb2.GameEventListenerReq(gameName=gameName)
                stream = self.Stub().GameEventListener(req)
                for evt in stream:
                    callback(evt)
            except:
                logging.exception("Exception in ListenForGameEventInternal")
        result = self.executor.submit(ListenForGameEventInternal)

    def CreateGame(self, gameName, scenarioName):
        req = kofserver_pb2.CreateGameReq(gameName=gameName, scenarioName=scenarioName)
        reply = self.Stub().CreateGame(req)
        return reply.error

    def StartGame(self, gameName):
        req = kofserver_pb2.StartGameReq(gameName=gameName)
        reply = self.Stub().StartGame(req)
        if reply.error == KOFErrorCode.ERROR_NONE:
            print("Start game successful")
        else:
            print("Start game failed: %s"%(str(reply.error),))

    def DestroyGame(self, gameName):
        req = kofserver_pb2.DestroyGameReq(gameName=gameName)
        reply = self.Stub().DestroyGame(req)
        if reply.error == KOFErrorCode.ERROR_NONE:
            print("Destroy game successful")
        else:
            print("Destroy game failed: %s"%(str(reply.error),))
    
    async def QueryGame(self, gameName):
        req = kofserver_pb2.QueryGameReq(gameName=gameName)
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(self.executor, lambda: self.Stub().QueryGame(req))
        return reply

    def PlayerRegister(self, gameName, playerName):
        req = kofserver_pb2.PlayerRegisterReq(gameName=gameName, playerName=playerName)
        reply = self.Stub().PlayerRegister(req)
        return reply.error
    
    def PlayerInfo(self, gameName, playerName):
        req = kofserver_pb2.PlayerInfoReq(gameName=gameName, playerName=playerName)
        reply = self.Stub().PlayerInfo(req)
        return reply

    def PlayerIssueSC(self, gameName, playerName, shellCode):
        req = kofserver_pb2.PlayerIssueSCReq(gameName=gameName, playerName=playerName, shellCode=shellCode)
        reply = self.Stub().PlayerIssueSC(req)
        if reply.reply.error == KOFErrorCode.ERROR_NONE:
            print("Player Issue Command successful, result: ")
            print(reply)
        else:
            print("Player Issue Command failed: %s"%(str(reply.reply.error),))
    
    async def PlayerIssueCmd(self, gameName, playerName, cmd):
        req = kofserver_pb2.PlayerIssueCmdReq(gameName=gameName, playerName=playerName, cmd=cmd)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, lambda: self.Stub().PlayerIssueCmd(req))
        return result

    async def QueryScore(self, gameName, playerName):
        req = kofserver_pb2.QueryScoreReq(gameName=gameName, playerName=playerName)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, lambda: self.Stub().QueryScore(req))
        return result
