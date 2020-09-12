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
import threading
import time

from config import Config

class MsgTx:
    def __init__(self, executor, q):
        self.executor = executor
        self.q = q
        self.sockList = []
        self.sockListLock = threading.Lock()

    def Shutdown(self):
        self.q.put("============== SERVICE SHUTDOWN ================")
        time.sleep(0.2)
        logging.info("MsgTx shutdown")
        with self.sockListLock:
            for s in self.sockList:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            self.sockList = []

    def Start(self):
        self.executor.submit(MsgTx.MainTask, self)
        self.executor.submit(MsgTx.SenderTask, self)

    def MainTask(self):
        try:
            self.MainTaskReal()
        except:
            logging.exception("Exception in MainTask")

    def MainTaskReal(self):
        host = '0.0.0.0'
        port = Config.conf()['msgPort']

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen()
            
            while True:
                conn, addr = s.accept()
                conn.setblocking(0)
                logging.info("MsgTx accepted a connection")
                with self.sockListLock:
                    self.sockList.append(conn)
    
    def SenderTask(self):
        try:
            self.SenderTaskReal()
        except:
            logging.exception("Exception in SenderTask")
    
    def SenderTaskReal(self):
        while True:
            msg = self.q.get()
            #logging.info("SenderTask: %s"%(msg,))
            with self.sockListLock:
                nextSockList = []
                logging.info("Sending to %d clients: %s"%(len(self.sockList), msg))
                for s in self.sockList:
                    try:
                        s.sendall(msg.encode('utf8'))
                    except:
                        s = None
                    if s is not None and s.fileno() != -1:
                        nextSockList.append(s)
                    else:
                        logging.info("Removing sock")
                self.sockList = nextSockList
