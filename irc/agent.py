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
import grpc
from config import Config
import kofserver_pb2, kofserver_pb2_grpc
from kofserver_pb2 import ErrorCode as KOFErrorCode

class Agent:
    def __init__(self):
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
        self.stub = kofserver_pb2_grpc.KOFServerStub(self.channel)

    def PlayerIssueSC(self, gameName, playerName, shellCode):
        req = kofserver_pb2.PlayerIssueSCReq(gameName=gameName, playerName=playerName, shellCode=shellCode)
        reply = self.stub.PlayerIssueSC(req)
        if reply.reply.error == KOFErrorCode.ERROR_NONE:
            print("Player Issue Command successful, result: ")
            print(reply)
        else:
            print("Player Issue Command failed: %s"%(str(reply.reply.error),))
    
    def PlayerIssueCmd(self, gameName, playerName, cmd):
        req = kofserver_pb2.PlayerIssueCmdReq(gameName=gameName, playerName=playerName, cmd=cmd)
        reply = self.stub.PlayerIssueCmd(req)
        if reply.reply.error == KOFErrorCode.ERROR_NONE:
            print("Player Issue Command successful, result: ")
            print(reply)
        else:
            print("Player Issue Command failed: %s"%(str(reply.reply.error),))

    def CreateGame(self, gameName, scenarioName):
        req = kofserver_pb2.CreateGameReq(gameName=gameName, scenarioName=scenarioName)
        reply = self.stub.CreateGame(req)
        if reply.error == KOFErrorCode.ERROR_NONE:
            print("Create game successful")
        else:
            print("Create game failed: %s"%(str(reply.error),))
    
    def StartGame(self, gameName):
        req = kofserver_pb2.StartGameReq(gameName=gameName)
        reply = self.stub.StartGame(req)
        if reply.error == KOFErrorCode.ERROR_NONE:
            print("Start game successful")
        else:
            print("Start game failed: %s"%(str(reply.error),))
    
    def PlayerRegister(self, gameName, playerName):
        req = kofserver_pb2.PlayerRegisterReq(gameName=gameName, playerName=playerName)
        reply = self.stub.PlayerRegister(req)
        if reply.error == KOFErrorCode.ERROR_NONE:
            print("Player register successful")
        else:
            print("Player register failed: %s"%(str(reply.error),))

    # TODO: Destory game
    # def DestroyGame(self):
    #     pass