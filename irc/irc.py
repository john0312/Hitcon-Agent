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
import asyncio
import yaml
import queue

from config import Config
from kofserver_pb2 import ErrorCode as KOFErrorCode
from kofserver_pb2 import GameEventType
import kofserver_pb2

class IRC(pydle.Client):
    def InitQueue(self, executor, onBroadcast):
        self.rxQueue = queue.Queue(maxsize=64)
        self.txQueue = queue.Queue(maxsize=64)
        self.executor = executor
        self.onBroadcast = onBroadcast
    
    def MessageAsync(self, target, reply):
        logging.info("MessageAsync %s %s"%(target, reply))
        try:
            #self.txQueue.put((target, reply), False)
            self.onBroadcast("### SYSTEM ###: %s\n"%(reply,))
        except queue.Full:
            logging.warn("txQueue Full! Dropping %s %s"%(target, reply))
        #self.TryHandleTxQueue()
    
    def TryHandleTxQueue(self):
        r = self._TryHandleTxQueueReal()
        asyncio.run_coroutine_threadsafe(r, self.loop)
    
    async def _TryHandleTxQueueReal(self):
        msgs = []
        while True:
            try:
                itm = self.txQueue.get(False)
                msgs.append(itm)
            except queue.Empty:
                break
        r = [self._MyMessage(x[0], x[1]) for x in msgs]
        await asyncio.wait(r)

    async def _MyMessage(self, target, reply):
        #return await self.message(target, reply)
        return None

    async def on_connect(self):
        self.loop = asyncio.get_event_loop()
        await self.join(self.channel)
        logging.info("Bot Join %s" % (self.channel))

    def InjectCommand(self, nick, msg):
        if nick is None:
            #await self.message(self.channel, "Admin: %s"%msg)
            self.onBroadcast("Admin: %s\n"%msg)
            nick = Config.conf()["admin"][0]
        self._on_message_real(self.channel, nick, msg)

    async def on_message(self, target, nick, message):
        return self._on_message_real(target, nick, message)
    
    def _on_message_real(self, target, nick, message):
        try:
            self.rxQueue.put((target, nick, message), False)
        except queue.Full:
            logging.warn("rxQueue Full! Dropping %s %s %s"%(target, nick, message))
        self.TryHandleRxQueue()

    def _TryHandleRxQueueReal(self):
        while True:
            try:
                itm = self.rxQueue.get(False)
                self.executor.submit(IRC.OnMessageSync, self, itm[0], itm[1], itm[2])
            except queue.Empty:
                break
    
    def TryHandleRxQueue(self):
        self.executor.submit(IRC._TryHandleRxQueueReal, self)

    def OnMessageSync(self, target, nick, message):
        if nick == self.nickname:
            # Never respond to self.
            return
        if target != self.channel:
            logging.warn("Discarding message from %s to %s: %s"%(nick, target, message))
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
                self.MessageAsync(target, reply)
        
        if message.startswith("Scoreboard") == True:
            replies = self.GetScoreBoard()
            for r in replies:
                self.MessageAsync(target, r)
            return

        # Admin can play too
        if self.gameName == None or self.scenario == None:
            return
        if nick not in self.userSet:
            registerMsg = self.PlayerRegister(self.gameName, nick)
            self.MessageAsync(target, registerMsg)
            self.userSet.add(nick)
        if message.startswith("Cmd ") == True:
            msg = self.PlayerIssueCmd(self.gameName, nick, message)
            if msg is not None:
                self.MessageAsync(target, msg)
        #elif message.startswith("Shellcode ") == True:
        #    self.PlayerIssueSC(self.gameName, nick, message)
        elif message == "CurrentGame":
            msg = self.GetCurrentGame()
            if msg is not None:
                self.MessageAsync(target, msg)
        else:
            pass

    def _IsAdmin(self, nick):
        for n in Config.conf()["admin"]:
            if n == nick:
                return True
        return False

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
        self.OnGameSet(self.gameName)
        return None

    def GetCurrentGame(self):
        if self.gameName is None:
            return "No game is currently running"

        result = self.agent.QueryGame(self.gameName)
        if result.reply.error != KOFErrorCode.ERROR_NONE:
            logging.error("GetCurrentGame QueryGame result: %s"%(str(result.reply.error),))
            return "Internal error 1 querying current game"
        if len(result.games) != 1:
            logging.error("Incorrect number of games returned %d"%(len(result.games),))
            return "Internal error 2 querying current game"
        game = result.games[0]
        msg = "Game State: %s\nDescription: %s\n"%(kofserver_pb2.GameState.Name(game.state), self.scenario['description'])
        return msg
        
    def CreateGame(self, message):
        message = message.split(" ")
        if len(message) != 3:
            errMsg = "CreateGame parameters format error!"
            return errMsg
        if self.gameName is not None:
            errMsg = "Previous game not destroyed properly!"
            return errMsg
        gameName = message[1]
        scenario = message[2]
        result = self.agent.CreateGame(gameName, scenario)
        if result != KOFErrorCode.ERROR_NONE:
            errMsg = "Game creation failed, error code %s"%(str(result),)
        else:
            errMsg = "Game created"
        self.OnGameSet(gameName)
        return errMsg
    
    # This is called when a game is started or it is known that we are on a game (through SetCurrentGame).
    def OnGameSet(self, gameName):
        self.gameName = gameName
        
        # Get the game scenario
        result = self.agent.QueryGame(self.gameName)
        if result.reply.error != KOFErrorCode.ERROR_NONE:
            logging.error("SetCurrentGame QueryGame result: %s"%(str(result.reply.error),))
            return "Internal error 1 querying current game"
        if len(result.games) != 1:
            logging.error("Incorrect number of games returned %d"%(len(result.games),))
            return "Internal error 2 querying current game"
        self.scenario = yaml.load(result.games[0].scenarioYML, Loader=yaml.SafeLoader)

        # Start the event listener
        def onGameEvent(evt):
            # agent runs on executor, so we need to post it to the loop here.
            #self.executor.submit(IRC._OnEvent, self, gameName, evt)
            self._OnEvent(self.gameName, evt)
        self.agent.ListenForGameEvent(self.gameName, onGameEvent)

    def _OnEvent(self, gameName, evt):
        print("Event: %s"%(str(evt),))
        if gameName != self.gameName:
            logging.warn("Discarding event %s not for current game %s/%s"%(str(evt), self.gameName, gameName))
            return
        if evt.eventType == GameEventType.PROC_CREATE or evt.eventType == GameEventType.PROC_TERMINATE:
            action = "created" if evt.eventType == GameEventType.PROC_CREATE else "terminated"
            playerMsg = ""
            if evt.playerName != "":
                playerMsg = "by %s "%(evt.playerName,)
            msg = "PID %d (%s) %s%s"%(evt.info.pid, evt.info.cmdline, playerMsg, action)
            if evt.info.cmdline != "":
                self.MessageAsync(self.channel, msg)

        if evt.eventType == GameEventType.PLAYER_START_GAIN:
            reason = IRC.Reason2Str(evt.gainReason)
            msg = "Player %s's %s is up! Somebody bash him/her/them!"%(evt.playerName, reason)
            self.MessageAsync(self.channel, msg)
        if evt.eventType == GameEventType.PLAYER_STOP_GAIN:
            reason = IRC.Reason2Str(evt.gainReason)
            msg = "Player %s's %s is down! Too bad for him/her/them!"%(evt.playerName, reason)
            self.MessageAsync(self.channel, msg)
        
        if evt.eventType == GameEventType.PROC_OUTPUT:
            msg = "PID %d: %s"%(evt.info.pid, IRC.SanitizeString(evt.procOutput.decode('utf8', 'backslashreplace')))
            self.MessageAsync(self.channel, msg)
        
        if evt.eventType == GameEventType.GAME_STARTED:
            msg = "Game started!!!"
            self.MessageAsync(self.channel, msg)

        if evt.eventType == GameEventType.GAME_REBOOT:
            msg = "Machine is rebooting!"
            self.MessageAsync(self.channel, msg)

    # TODO: Move this somewhere else?
    @staticmethod
    def Reason2Str(r):
            if r == kofserver_pb2.GainReason.REASON_PORT:
                return "port"
            if r == kofserver_pb2.GainReason.REASON_PID:
                return "process"
            return "none"

            
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
        result = self.agent.PlayerRegister(gameName, nick)
        if result != KOFErrorCode.ERROR_NONE:
            msg = "Failed to register player %s for %s"%(nick, gameName)
            return msg
        # Now get the port number.
        result = self.agent.PlayerInfo(gameName, nick)
        if len(result.info) != 1:
            msg = "Internal register player error"
            return msg
        msg = "Player %s registered for %s; Port=%d"%(nick, gameName, result.info[0].port)
        return msg
    
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
        if result.reply.error == KOFErrorCode.ERROR_NONE:
            # No message for success, for now.
            errMsg = None
        elif result.reply.error == KOFErrorCode.ERROR_GAME_NOT_RUNNING:
            errMsg = "Game is not running."
        elif result.reply.error == KOFErrorCode.ERROR_COOLDOWN:
            errMsg = "You need to cool down."
        elif result.reply.error == KOFErrorCode.ERROR_DOOR_CLOSED:
            errMsg = "Too bad! Door is closed!"
        else:
            errMsg = "Run command failed, error code %s"%(KOFErrorCode.Name(result.reply.error),)
        return errMsg

    def GetScoreBoard(self):
        if self.gameName is None:
            return "Game not running"
        result = self.agent.QueryScore(self.gameName, "")
        if result.reply.error != KOFErrorCode.ERROR_NONE:
            return ["Failed to query score, error code %s"%(str(result.reply.error),),]
        msg = []
        for s in result.scores:
            msg.append('%s\t%d'%(s.playerName, s.score))
        return msg

    def SanitizeString(s):
        allowedStr = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ~!@#$%^&*()-_=+?<>.,[]{}|'
        resList = []
        for c in s:
            if allowedStr.find(c) != -1:
                resList.append(c)
            else:
                resList.append("\\x%02x"%(ord(c),))
        return ''.join(resList)
