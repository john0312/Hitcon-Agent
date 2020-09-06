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
import os
import subprocess
import random
import psutil
import queue

from shellexec import child_task
import guest_agent_pb2, guest_agent_pb2_grpc
import kofserver_pb2

class GuestAgent(guest_agent_pb2_grpc.GuestAgentServicer):
    def __init__(self, procWatcher, procRunner, executor):
        self.procWatcher = procWatcher
        self.executor = executor
        self.procRunner = procRunner

    def Ping(self, request, context):
        # Ping always succeed.
        logging.debug("Ping received")
        return guest_agent_pb2.Rep(error=guest_agent_pb2.ErrorCode.ERROR_NONE)
    
    def RunCmd(self, request, context):
        cmd = request.cmd
        logging.info("RunCmd called with '%s'"%cmd)
        # TODO: Set various limits? Memory limit? CPU limit?
        try:
            result = self.procRunner.RunCmd([cmd,])
        except Exception:
            logging.exception("Failed to RunCmd(%s)"%(cmd,))
            errorCode = guest_agent_pb2.Rep(error=guest_agent_pb2.ErrorCode.ERROR_RUN_CMD_FAILED)
            return guest_agent_pb2.RunCmdRep(reply=errorCode)
        
        # Run command is successful, the command is probably running,
        # let's return the PID.
        genericReply = guest_agent_pb2.Rep(error=guest_agent_pb2.ErrorCode.ERROR_NONE)
        reply = guest_agent_pb2.RunCmdRep(reply=genericReply, pid=result.pid)
        return reply

    def RunSC(self, request, context):
        b64code = request.shellcode
        userPort = request.userPort
        killProc = request.killProc
        logging.info("RunSC called with %s"%b64code)
        if killProc != 0:
            kill_cmd = 'kill %d'%killProc
            os.system(kill_cmd)
        if userPort == 0:
            # Use a random port to disable this feature.
            userPort = random.randint(10100, 10500)
        result, pid = child_task(b64code, userPort)
        if not result:
            # Failed
            errorCode = guest_agent_pb2.Rep(error=guest_agent_pb2.ErrorCode.ERROR_RUN_SC_FAILED)
            return guest_agent_pb2.RunSCRep(reply=errorCode)
        genericReply = guest_agent_pb2.Rep(error=guest_agent_pb2.ErrorCode.ERROR_NONE)
        reply = guest_agent_pb2.RunSCRep(reply=genericReply, pid=pid)
        return reply

    def QueryProcInfo(self, request, context):
        result = []
        for proc in psutil.process_iter(["name", "cmdline", "cpu_times", "memory_info", "status"]):
            pstatus = proc.info['status']
            if pstatus == psutil.STATUS_ZOMBIE or pstatus == psutil.STATUS_DEAD:
                continue
            pinfo = kofserver_pb2.ProcInfo(pid=proc.pid)
            pinfo.name = proc.info['name']
            pinfo.cmdline = ' '.join(proc.info['cmdline'])
            pinfo.cpu_time = proc.info['cpu_times'].user + proc.info['cpu_times'].system
            pinfo.memory_usage = proc.info['memory_info'].rss
            result.append(pinfo)
        genericReply = guest_agent_pb2.Rep(error=guest_agent_pb2.ErrorCode.ERROR_NONE)
        reply = guest_agent_pb2.QueryProcInfoRep(reply=genericReply)
        for r in result:
            reply.info.append(r)
        return reply

    def EventListener(self, request, context):
        logging.info("EventListener started")
        q = queue.Queue(32)
        self.procWatcher.RegisterQueue(q)
        try:
            while True:
                event = q.get()
                yield event
        except:
            logging.exception("EventListener ended")
        self.procWatcher.UnregisterQueue(q)
