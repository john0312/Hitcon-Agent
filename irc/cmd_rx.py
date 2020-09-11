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
import logging
import re
import threading
from config import Config

class CmdRx:
    def __init__(self, executor, handler):
        self.executor = executor
        self.ctr = 0
        self.handler = handler
        self.sockList = []
        self.sockListLock = threading.Lock()

    def Shutdown(self):
        logging.info("CmdRx shutdown")
        with self.sockListLock:
            for s in self.sockList:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            self.sockList = []

    def Start(self):
        self.executor.submit(CmdRx.MainTask, self)

    def MainTask(self):
        try:
            self.MainTaskReal()
        except:
            logging.exception("Exception in MainTask")

    def MainTaskReal(self):
        host = '0.0.0.0'
        port = Config.conf()['cmdPort']

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen()
            
            while True:
                conn, addr = s.accept()
                self.executor.submit(CmdRx.SockHandler, self, conn, 'client%03d'%(self.ctr,))
                self.ctr += 1
    
    def SockHandler(self, conn, nick):
        try:
            self.SockHandlerReal(conn, nick)
        except:
            logging.exception("Exception in SockHandler")

    def SockHandlerReal(self, conn, nick):
        with self.sockListLock:
            self.sockList.append(conn)
        f = conn.makefile()
        while not f.closed and conn.fileno() != -1:
            try:
                l = f.readline().strip()
                if len(l) == 0:
                    break
                if l.startswith('Nick ') and re.match('^[a-zA-Z0-9]{2,20}$', l[5:]) is not None:
                    self.handler(nick, "Renaming to '%s'"%(l[5:],))
                    nick = l[5:]
                else:
                    self.handler(nick, l)
            except:
                logging.exception("Exception in readline")
                f.close()
                conn.close()
                break
        f.close()
        conn.close()
        self.handler(nick, "Bye~~ Disconnecting")
        with self.sockListLock:
            sockList = []
            for s in self.sockList:
                if s != conn:
                    sockList.append(s)
            self.sockList = sockList
