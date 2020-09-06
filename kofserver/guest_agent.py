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

# This file contains the GuestAgent class, it is in charge of talking to the
# agent running within the QEMU/KVM guest. i.e. It is the proxy to guest agent.

import grpc
import logging
import threading
import time

import guest_agent_pb2, guest_agent_pb2_grpc
from config import Config

class GuestAgent:
    def __init__(self, executor, guestIP):
        self.executor = executor
        self.guestIP = guestIP
        # The gRPC channel
        self.channel = None
        # The guest agent gRPC stub
        self.stub = None
        # Lock required to write self.stub. Reading doesn't require the lock.
        self.stubLock = threading.Lock()
        # The event thread for listening for event.
        self.eventThread = None
        
        self.eventCallbackSet = set()
        self.eventCallbackSetLock = threading.Lock()
    
    def AddCallback(self, cb):
        with self.eventCallbackSetLock:
            self.eventCallbackSet.add(cb)
    
    def RemoveCallback(self, cb):
        with self.eventCallbackSetLock:
            self.eventCallbackSet.remove(cb)

    def _EventThreadMain(self):
        try:
            self._EventThreadMainReal()
        except:
            logging.exception("Exception in Guest Agent _EventThreadMain")

    def _EventThreadMainReal(self):
        while True:
            self._DoListenForEvent()
            if self.stub is None:
                return
            logging.warn('DoListenForEvent exited, maybe connection is dead?')
            time.sleep(1.0)
    
    def _DoListenForEvent(self):
        if self.stub is None:
            logging.warn('No stub when trying to DoListenForEvent')
            return
        
        stream = self.stub.EventListener(guest_agent_pb2.EventListenerReq())
        try:
            for evt in stream:
                with self.eventCallbackSetLock:
                    for cb in self.eventCallbackSet:
                        cb(evt)
        except Exception:
            logging.exception("GuestAgent EventListener interrupted.")
        return

    # Try to connect to the agent, return True if it's reachable.
    def EnsureConnection(self):
        with self.stubLock:
            if self.channel is not None or self.stub is not None:
                # Already connected.
                logging.warn('EnsureConnection() when it is already connected')
                return True
            
            host = self.guestIP
            port = Config.conf()['agentPort']

            channel = grpc.insecure_channel('%s:%d'%(host, port))
            f = grpc.channel_ready_future(channel)
            try:
                f.result(timeout=Config.conf()['agentConnectTimeout'])
            except Exception:
                # Failed to connect.
                return False

            self.channel = channel
            self.stub = guest_agent_pb2_grpc.GuestAgentStub(channel)

            # We've the stub, now start the event thread.
            self.eventThread = self.executor.submit(GuestAgent._EventThreadMain, self)

        # Give it a ping to see if it's working?
        result = self.CheckAlive()
        if result:
            logging.info('Guest agent at %s:%d connected'%(host, port))
        else:
            logging.info('Bad guest agent at %s:%d'%(host, port))
        return result

    # CheckAlive checks if the guest agent is responsive.
    def CheckAlive(self):
        if self.stub is None or self.channel is None:
            # Not connected.
            logging.warn('CheckAlive() but it is not connected')
            return False
        
        try:
            reply = self.stub.Ping(guest_agent_pb2.PingReq())
        except:
            self.ResetConnection()
            logging.exception("Failed to check guest agent, it's probably dead.")
            return False

        if reply.error == guest_agent_pb2.ErrorCode.ERROR_NONE:
            # Everything is good.
            return True
        
        # Connect is bad, let's clean it up.
        self.ResetConnection()
        
        return False
        
        
    # Close the connection. Usually called when we are shutting down.
    # Do not call from event thread, it'll deadlock.
    def ResetConnection(self):
        with self.stubLock:
            if self.channel is not None:
                self.channel.close()
            self.stub = None
            self.channel = None
            if self.eventThread is not None:
                logging.info("Waiting for event thread to exit")
                self.eventThread.result()
                logging.info("Done waiting for event thread to exit.")

    def RunShellcode(self, shellcode):
        # TODO
        pass

    # Return the protobuf directly.
    def QueryProcInfo(self):
        # reply for failure situation.
        errorCode = guest_agent_pb2.ErrorCode.ERROR_CLIENT
        genericRep = guest_agent_pb2.Rep(error=errorCode)
        failureReply = guest_agent_pb2.QueryProcInfoRep(reply=genericRep)

        if self.stub is None:
            logging.warn("QueryProcInfo() called when connection is not ready.")
            return failureReply

        try:
            result = self.stub.QueryProcInfo(guest_agent_pb2.QueryProcInfoReq())
        except Exception:
            logging.exception("Failed to QueryProcInfo(), resetting channel.")
            self.ResetConnection()
            return failureReply
        
        return result

    def RunCmd(self, cmd):
        # reply for failure situation.
        errorCode = guest_agent_pb2.ErrorCode.ERROR_CLIENT
        genericRep = guest_agent_pb2.Rep(error=errorCode)
        failureReply = guest_agent_pb2.RunCmdRep(reply=genericRep)

        if self.stub is None:
            logging.warn("RunCmd() called when connection is not ready.")
            return failureReply

        try:
            result = self.stub.RunCmd(guest_agent_pb2.RunCmdReq(cmd=cmd))
        except Exception:
            logging.exception("Failed to RunCmd(), resetting channel.")
            self.ResetConnection()
            return failureReply
        
        return result
