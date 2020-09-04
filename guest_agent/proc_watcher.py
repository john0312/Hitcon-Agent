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
import psutil
import threading

import guest_agent_pb2
from config import Config

class ProcWatcher:
    def __init__(self, executor):
        self.executor = executor
        # Set to True to exit mainthread.
        self.mainThreadExit = False
        self.mainThread = self.executor.submit(ProcWatcher._MainThread, self)
        self.procDict = {}

        # This is the list of queue for which we'll insert the creation/termination event.
        self.queueSet = set()
        # Lock for the above.
        self.queueSetLock = threading.Lock()
    
    def Shutdown(self):
        self.mainThreadExit = True
        self.mainThread.result()
    
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

    def _MainThread(self):
        try:
            self._MainThreadReal()
        except Exception:
            logging.exception("Exception in ProcWatcher._MainThread")
    
    def _MainThreadReal(self):
        time.sleep(Config.conf()['procWatcherFirstDelay'])
        
        # Initialize the process list.
        self.procDict = self._GetProcDict()

        # Collect the processes
        while not self.mainThreadExit:
            time.sleep(Config.conf()['procWatcherDelay'])

            newProcDict = self._GetProcDict()
            
            for k in newProcDict:
                if k not in self.procDict:
                    # New process
                    self._NotifyEvent(newProcDict[k], guest_agent_pb2.ProcEventType.PROC_CREATE)
                    
            for k in self.procDict:
                if k not in newProcDict:
                    # Terminated
                    self._NotifyEvent(self.procDict[k], guest_agent_pb2.ProcEventType.PROC_TERMINATE)
            
            self.procDict = newProcDict
    
    def _GetProcDict(self):
        result = {}
        for proc in psutil.process_iter(["name", "cmdline", "cpu_times", "memory_info"]):
            pinfo = guest_agent_pb2.ProcInfo(pid=proc.pid)
            pinfo.name = proc.info['name']
            pinfo.cmdline = ' '.join(proc.info['cmdline'])
            pinfo.cpu_time = proc.info['cpu_times'].user + proc.info['cpu_times'].system
            pinfo.memory_usage = proc.info['memory_info'].rss
            result[pinfo.pid] = pinfo
        return result

    def _NotifyEvent(self, procInfo, procEventType):
        with self.queueSetLock:
            for q in self.queueSet:
                event = guest_agent_pb2.ProcEvent(eventType=procEventType, info=procInfo)
                try:
                    q.put(event, False)
                except Exception:
                    logging.exception("Problem notifying create process")
    
