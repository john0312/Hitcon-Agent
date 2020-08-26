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

class IRC:
    def __init__(self, agent):
        try:
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc.connect((Config.conf()["ircServer"], Config.conf()["ircPort"]))
            self.agent = agent
        except:
            raise
        
    def run(self):
        try:
            botNick = Config.conf()["botNick"]
            channel = Config.conf()["channel"]
            self.irc.send(("USER " + botNick + " " + botNick + " " + botNick + " :This is a hitcon bot\n").encode())
            self.irc.send(("NICK " + botNick + "\n").encode())
            
            while True:
                ### Guest!Guest@protectedhost-2D06700E.hinet-ip.hinet.net PRIVMSG #test :ds
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
                    shellcode = t[-1]
                    b = base64.b64encode(shellcode.encode())
                    
                    ### TODO: Check admin register
                    if nick == Config.conf()["supervisor"]:
                        if shellcode == "/CreateGame":
                            ### TODO: CreateGame
                            pass
                        elif shellcode == "/StartGame":
                            ### TODO: StartGame
                            pass
                        elif shellcode == "/DestroyGame":
                            ### TODO: DestroyGame
                            pass
                        else:
                            pass
                    else:
                        ### TODO: Test gRPC
                        pid = self.agent.shellcode("test", nick, shellcode)
                        if pid != None:
                            reply = "PRIVMSG %s : %s ==> pid: %s \n" % (channel, str(nick), str(pid))
                            self.irc.send(reply)

        except Exception:
            logging.exception("IRC crashed")