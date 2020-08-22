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

# This file contains the VMManager class, it exports a set of API for dealing
# with libvirt from a KOF perspective.

import enum

class VM():
    class VMState(enum.Enum):
        CREATED = 1
        READY = 2
        RUNNING = 3
        DESTROYED = 4
    
    def __init__(self, vmPath):
        self.vmPath = vmPath
        self.state = VMState.CREATED
    
    def Init(self):
        if self.state != VMState.CREATED:
            raise Exception("VM.Init() called in invalid state %s"%(str(self.state)))
        
        self.vmConf = VM.LoadVM(vmPath)
        self.state = VMState.READY

    def Boot(self):
        if self.state != VMState.READY:
            raise Exception("VM.Boot() called in invalid state %s"%(str(self.state)))
        pass

    def Shutdown(self):
        if self.state != VMState.RUNNING:
            raise Exception("VM.Shutdown() called in invalid state %s"%(str(self.state)))
        pass

    def GetState(self):
        return self.state

    @staticmethod
    def LoadVM(vmPath):
        pass

class VMManager():
    def __init__(self):
        pass

    # vmPath is the path to a template that describes the VM to be created.
    # The template format is specific to KOF.
    # Throw an exception for failure.
    def CreateVM(self, vmPath):
        pass
