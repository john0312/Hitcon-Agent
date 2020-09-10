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

# This file holds the primray logic for the guest agent, and handles all the
# guest agent request.

import logging
import time
import threading
import subprocess
import fcntl
import os

import guest_agent_pb2
import kofserver_pb2
from config import Config

class ProcRunner:
    def __init__(self, executor):
        self.executor = executor
        
        self.procList = []
        self.procListLock = threading.Lock()

        # A thread for handling the processes, such as waiting on them.
        self.procHandlerMainExit = False
        self.procHandlerThread = executor.submit(ProcRunner._ProcHandlerMain, self)
        
        # This is the list of queue for which we'll insert the stdout event.
        self.queueSet = set()
        # Lock for the above.
        self.queueSetLock = threading.Lock()

    def RegisterQueue(self, q):
        with self.queueSetLock:
            self.queueSet.add(q)
        return True
    
    def UnregisterQueue(self, q):
        with self.queueSetLock:
            try:
                self.queueSet.remove(q)
            except Exception:
                logging.exception("Failed to remove queue for ProcWatcher")
                return False
        return True

    def Shutdown(self):
        self.procHandlerMainExit = True
        self.procHandlerThread.result()
        # Note: Intentionally let the child process become orphan.

    def _ProcHandlerMain(self):
        try:
            self._ProcHandlerMainReal()
        except Exception:
            logging.exception("Exception in _ProcHandlerMain")
    
    def _ProcHandlerMainReal(self):
        while not self.procHandlerMainExit:
            time.sleep(Config.conf()['procRunnerDelay'])
            with self.procListLock:
                remaining = []
                for p in self.procList:
                    # Try read from it?
                    out = None
                    try:
                        out = p.stdout.read()
                    except IOError:
                        # Whatever.
                        pass
                    except:
                        logging.exception("Problem reading from process")
                    if p.stdoutReadTotal < Config.conf()['procReadLimit']:
                        # We'll still deliver the message.
                        p.stdoutReadTotal += len(out)
                        if p.stdoutReadTotal > Config.conf()['procReadLimit']:
                            out = out[0:(len(out)-(p.stdoutReadTotal-Config.conf()['procReadLimit']))]
                        if len(out) > 0:
                            self._HandleStdout(p.pid, out)

                    # Reap the child?
                    ret = p.poll()
                    if ret is not None:
                        logging.info("Reaping PID %d"%(p.pid,))
                        p.wait()
                        # Done with this process, we don't insert it back.
                        continue
                    remaining.append(p)
                self.procList = remaining

    def RunCmd(self, cmdAndArgs):
        if Config.conf()['procRunner'] != "":
            cmdAndArgs = [Config.conf()['procRunner'],] + cmdAndArgs
        try:
            process = subprocess.Popen(cmdAndArgs, shell=True, stdout=subprocess.PIPE)
            ProcRunner.MakeNonBlocking(process.stdout)
            process.stdoutReadTotal = 0
        except Exception:
            logging.exception("Problem running command")
            return None
        self.procList.append(process)
        return process

    def _HandleStdout(self, pid, data):
        event = kofserver_pb2.GameEvent(eventType=kofserver_pb2.GameEventType.PROC_OUTPUT)
        event.procOutput = data
        event.info.pid = pid
        with self.queueSetLock:
            removalSet = set()
            for q in self.queueSet:
                try:
                    q.put(event, True, 0.5)
                except Exception:
                    logging.exception("Problem notifying process output")
                    removalSet.add(q)
            for q in removalSet:
                self.queueSet.remove(q)

    @staticmethod
    def MakeNonBlocking(p):
        fcntl.fcntl(p, fcntl.F_SETFL, fcntl.fcntl(p, fcntl.F_GETFL) | os.O_NONBLOCK)
