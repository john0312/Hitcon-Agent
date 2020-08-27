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

import socket
import sys
import logging
import base64
from config import Config
from concurrent import futures

class IRC:
    def __init__(self, agent):
        self.agent = agent
        self.gameName = ""
        self.scenario = ""
        self.executor = futures.ThreadPoolExecutor(max_workers=1)
        self.executor.submit(lambda: self.Connect()).result()

    # TODO: Need to fix missconnection situation, ensure the connecting quality.
    def Connect(self):
        for i in range(Config.conf()["ircRetryTimes"]):
            try:
                self.irc = socket.create_connection((Config.conf()["ircServer"], Config.conf()["ircPort"]), timeout=Config.conf()["ircConnectionTimeOut"])
                self.irc.settimeout(None)
            except Error as e:
                logging.error(e)
                continue

    def Run(self):
        try:
            botNick = Config.conf()["botNick"]
            channel = Config.conf()["channel"]
            self.irc.send(("USER " + botNick + " " + botNick + " " + botNick + " :This is a hitcon bot\n").encode())
            self.irc.send(("NICK " + botNick + "\n").encode())
            
            while True:
                text = self.irc.recv(Config.conf()["bufferSize"]).strip().decode()
                if text.find("PING") != -1:
                    self.irc.send(("PONG " + text.split()[1] + "\n").encode())
                
                if text.find("255 " + botNick) != -1:
                    self.irc.send(("JOIN " + channel + "\n").encode())
                    logging.info(botNick + " has joined!")

                if text.find("PRIVMSG " + channel) != -1:
                    logging.info(text)
                    t = text.split(":")
                    nick = t[1].split("!")[0]
                    message = t[-1]

                    # TODO: Check admin register
                    # TODO: Start with character '/'
                    if nick == Config.conf()["admin"]:
                        if message.startswith("CreateGame ") == True:
                            self.CreateGame(message)
                        elif message.startswith("StartGame ") == True:
                            self.StartGame(message)
                        elif message.startswith("DestroyGame ") == True:
                            self.DestroyGame(message)
                        else:
                            pass
                    else:
                        if message.startswith("Cmd ") == True:
                            self.PlayerIssueSC(self.gameName, nick, message)
                        elif message.startswith("Shellcode ") == True:
                            self.PlayerIssueSC(self.gameName, nick, message)
                        else:
                            pass
        except:
            logging.exception("IRC crashed")

    def CreateGame(self, message):
        message = message.split(" ")
        if len(message) != 3:
            logging.error("CreateGame parameters format error!")
            return
        self.gameName = message[1]
        self.scenario = message[2]
        self.agent.CreateGame(self.gameName, self.scenario)
    
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
        self.gameName = ""
        self.scenario = ""

    def PlayerRegister(self, gameName, nick):
        self.agent.PlayerRegister(gameName, nick)    
    
    def PlayerIssueSC(self, gameName, nick, message):
        message = message.split(" ")[1]
        if len(message) != 2:
            logging.error("Shellcode parameters format error!")
            return
        encodedMessage = base64.b64encode(message[1].encode())
        self.agent.PlayerIssueSC(gameName, nick, encodedMessage)
    
    def PlayerIssueCmd(self, gameName, nick, message):
        message = message.split(" ")
        if len(message) != 2:
            logging.error("Cmd parameters format error!")
            return
        self.agent.PlayerIssueCmd(gameName, nick, message[1])
