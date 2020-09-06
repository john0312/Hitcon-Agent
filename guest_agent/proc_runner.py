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

import guest_agent_pb2
from config import Config

class ProcRunner:
    def __init__(self, executor):
        self.executor = executor
        
        self.procList = []
        self.procListLock = threading.Lock()

        # A thread for handling the processes, such as waiting on them.
        self.procHandlerMainExit = False
        self.procHandlerThread = executor.submit(ProcRunner._ProcHandlerMain, self)
    
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
        try:
            process = subprocess.Popen(cmdAndArgs, shell=True)
        except Exception:
            # Let the caller handle it.
            raise
        with self.procListLock:
            self.procList.append(process)
        return process

            
