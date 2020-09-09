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
import logging
import subprocess
import os
import yaml
import time
import uuid

from config import Config

class VM():
    class VMState(enum.Enum):
        ERROR = 0
        CREATED = 1
        READY = 2
        RUNNING = 3
        DESTROYED = 4
    
    def __init__(self, vmPath, vmName):
        logging.info("Creating VM from %s"%(vmPath,))
        self.vmPath = vmPath
        self.dirName = os.path.dirname(vmPath)
        self.imgDir = Config.conf()['diskImageDir']
        if not os.path.isabs(self.imgDir):
            self.imgDir = os.path.join(os.getcwd(), self.imgDir)
        self.tmpImgDir = Config.conf()['tmpDiskImageDir']
        if not os.path.isabs(self.tmpImgDir):
            self.tmpImgDir = os.path.join(os.getcwd(), self.tmpImgDir)
        self.state = VM.VMState.CREATED
        self.vmName = vmName
        self.vmID = str(uuid.uuid4())
        # Load the VM YML
        self.vmConf = VM.LoadVM(self.vmPath)
        
        # This is the time at which VM is started. It'll be None if VM is not running.
        self.vmStartupTime = None
    
    def GetUptime(self):
        if self.vmStartupTime is None:
            logging.warn("Querying for uptime when it's not running")
            return None
        return time.time() - self.vmStartupTime

    def _GetType(self):
        return self.vmConf['vmType']
    
    def _GetScriptEnv(self):
        env = {}
        env['VMDIR'] = self.dirName
        env['IMAGEDIR'] = self.imgDir
        env['TMPIMAGEDIR'] = self.tmpImgDir
        env['VMNAME'] = self.vmName
        env['VMID'] = self.vmID
        return env

    def _RunScript(self, script, args):
        if not os.path.isabs(script):
            script = os.path.join(self.dirName, script)
        cmd = [script,]+args
        # Note: capture_output might not be available depending on python version.
        # Setting stdout/stderr to PIPE instead.
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self._GetScriptEnv())
        if result.returncode != 0:
            logging.error("Failed to run script %s for VM: %s"%(str(cmd),result))
            return False
        return True

    def Init(self):
        if self.state != VM.VMState.CREATED:
            raise Exception("VM.Init() called in invalid state %s"%(str(self.state)))

        logging.info("Initializing VM based on %s"%(self.vmPath,))
        if self._GetType() == 'noop':
            pass
        elif self._GetType() == 'shellscript':
            if not self._RunScript(self.vmConf['shellscript']['init'], []):
                raise Exception("Failed to run shellscript for Init()")
        else:
            raise Exception("Unknown vmType %s, not sure how to Init()"%(self._GetType(),))

        self.state = VM.VMState.READY
        return True

    def Boot(self):
        if self.state != VM.VMState.READY:
            raise Exception("VM.Boot() called in invalid state %s"%(str(self.state)))

        logging.info("Booting VM based on %s"%(self.vmPath,))
        if self._GetType() == 'noop':
            pass
        elif self._GetType() == 'shellscript':
            if not self._RunScript(self.vmConf['shellscript']['boot'], []):
                raise Exception("Failed to run shellscript for Boot()")
        else:
            raise Exception("Unknown vmType %s, not sure how to Boot()"%(self._GetType(),))

        self.state = VM.VMState.RUNNING
        self.vmStartupTime = time.time()
        return True

    def CheckState(self):
        # ??
        pass

    def Shutdown(self):
        if self.state != VM.VMState.RUNNING:
            raise Exception("VM.Shutdown() called in invalid state %s"%(str(self.state)))

        logging.info("Shutting down VM based on %s"%(self.vmPath,))
        if self._GetType() == 'noop':
            pass
        elif self._GetType() == 'shellscript':
            if not self._RunScript(self.vmConf['shellscript']['shutdown'], []):
                raise Exception("Failed to run shellscript for Shutdown()")
        else:
            raise Exception("Unknown vmType %s, not sure how to Shutdown()"%(self._GetType(),))

        self.state = VM.VMState.READY
        self.vmStartupTime = None
        return True

    def Destroy(self):
        if self.state != VM.VMState.READY:
            raise Exception("VM.Destroy() called in invalid state %s"%(str(self.state)))

        logging.info("Destroying VM based on %s"%(self.vmPath,))
        if self._GetType() == 'noop':
            pass
        elif self._GetType() == 'shellscript':
            if not self._RunScript(self.vmConf['shellscript']['destroy'], []):
                raise Exception("Failed to run shellscript for Destroy()")
        else:
            raise Exception("Unknown vmType %s, not sure how to Destroy()"%(self._GetType(),))

        self.state = VM.VMState.DESTROYED
        return True

    def GetState(self):
        return self.state

    @staticmethod
    def LoadVM(vmPath):
        try:
            with open(vmPath) as f:
                result = yaml.load(f, Loader=yaml.FullLoader)
        except Exception:
            logging.exception("Failed to open vm config yml file %s"%vmPath)
            raise
        return result

class VMManager():
    def __init__(self):
        pass

    # vmPath is the path to a template that describes the VM to be created.
    # The template format is specific to KOF.
    # Throw an exception for failure.
    def CreateVM(self, vmPath, vmName):
        vm = VM(vmPath, vmName)
        return vm

