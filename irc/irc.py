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
import base64
import pydle

from config import Config
from kofserver_pb2 import ErrorCode as KOFErrorCode

class IRC(pydle.Client):
    async def on_connect(self):
        await self.join(self.channel)
        logging.info("Bot Join %s" % (self.channel))

    async def on_message(self, target, nick, message):
        if nick == self.nickname:
            # Never respond to self.
            return

        reply = None
        if self._IsAdmin(nick):
            if message.startswith("CreateGame ") == True:
                reply = self.CreateGame(message)
            elif message.startswith("StartGame ") == True:
                self.StartGame(message)
            elif message.startswith("DestroyGame ") == True:
                self.DestroyGame(message)
            elif message.startswith("SetCurrentGame ") == True:
                self.SetCurrentGame(message)
            else:
                pass
            if reply is not None:
                await self.message(target, reply)
        
        if message.startswith("Scoreboard") == True:
            replies = self.GetScoreBoard()
            for r in replies:
                await self.message(target, r)
            return

        # Admin can play too
        if self.gameName == None or self.scenario == None:
            return
        if nick not in self.userSet:
            self.PlayerRegister(self.gameName, nick)
            self.userSet.add(nick)
        if message.startswith("Cmd ") == True:
            self.PlayerIssueCmd(self.gameName, nick, message)
        elif message.startswith("Shellcode ") == True:
            self.PlayerIssueSC(self.gameName, nick, message)
        else:
            pass

    def _IsAdmin(self, nick):
        return nick == Config.conf()["admin"]

    def SetChannel(self, channel):
        self.channel = channel
    
    def SetAgent(self, agent):
        self.agent = agent
    
    def ResetGame(self):
        self.userSet = set()
        self.gameName = None
        self.scenario = None

    def SetCurrentGame(self, message):
        message = message.split(" ")
        if len(message) != 2:
            errMsg = "SetCurrentGame format error!"
            return errMsg
        if self.gameName is not None:
            errMsg = "Cant set current game if previous game is not destroyed"
            return errMsg
        self.gameName = message[1]
        return None

    def CreateGame(self, message):
        message = message.split(" ")
        if len(message) != 3:
            errMsg = "CreateGame parameters format error!"
            return errMsg
        if self.gameName is not None:
            errMsg = "Previous game not destroyed properly!"
            return errMsg
        self.gameName = message[1]
        self.scenario = message[2]
        result = self.agent.CreateGame(self.gameName, self.scenario)
        if result != KOFErrorCode.ERROR_NONE:
            errMsg = "Game creation failed, error code %s"%(str(result),)
        else:
            errMsg = "Game created"
        return errMsg
        
    
    def StartGame(self, message):
        message = message.split(" ")
        if len(message) != 2:
            logging.error("StartGame parameters format error!")
            return
        self.agent.StartGame(message[1])

    def DestroyGame(self, message):
        message = message.split(" ")
        if len(message) != 2:
            logging.error("StartGame parameters format error!")
            return
        self.agent.DestroyGame(message[1])
        self.ResetGame()

    def PlayerRegister(self, gameName, nick):
        self.agent.PlayerRegister(gameName, nick)    
    
    def PlayerIssueSC(self, gameName, nick, message):
        message = message.split(" ")
        if len(message) != 2:
            logging.error("Shellcode parameters format error!")
            return
        encodedMessage = base64.b64encode(message[1].encode())
        self.agent.PlayerIssueSC(gameName, nick, encodedMessage)
    
    def PlayerIssueCmd(self, gameName, nick, message):
        # Command could contain space.
        idx = message.find(" ")
        if idx == -1:
            errMsg = "Cmd parameters format error!"
            return errMsg
        cmd = message[idx+1:]
        result = self.agent.PlayerIssueCmd(gameName, nick, cmd)
        if result.reply.error != KOFErrorCode.ERROR_NONE:
            errMsg = "Run command failed, error code %s"%(str(result.reply.error),)
        else:
            # No message for success, for now.
            errMsg = None
        return errMsg

    def GetScoreBoard(self):
        result = self.agent.QueryScore("", "")
        if result.reply.error != KOFErrorCode.ERROR_NONE:
            return ["Failed to query score, error code %s"%(str(result.reply.error),),]
        msg = []
        for s in result.scores:
            msg.append('%s\t%d'%(s.playerName, s.score))
        return msg

            
