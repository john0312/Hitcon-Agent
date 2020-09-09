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

# This file host the Game class, which contains the primary logic for a game.

import logging
import yaml
import os
import random
import traceback
import time
import threading

import kofserver_pb2, kofserver_pb2_grpc
from kofserver_pb2 import GameState
from kofserver_pb2 import GameEventType
from kofserver_pb2 import ErrorCode as KOFErrorCode
from guest_agent_pb2 import ErrorCode as GuestErrorCode
from vm_manager import VMManager, VM
from config import Config
from guest_agent import GuestAgent
from scorer import Scorer

class Game:
    def __init__(self, executor, vmManager, scoreboard, scanner, gameName, scenarioName):
        self.gameName = gameName
        
        # executor is a concurrent.futures.Executor class that allows us to
        # run stuff.
        self.executor = executor
        
        # Store the scoreboard and scanner for future use.
        self.scoreboard = scoreboard
        self.scanner = scanner
        
        # Load the scenario
        self.scenarioName = scenarioName
        self.scenario = Game.LoadScenario(scenarioName)

        # The state that the game is in, needs to happen before starting gameTask.
        self.state = GameState.GAME_CREATED

        # Start the Game Task, which runs anything in the game that need to
        # be done repeatedly, such as scoring the user.
        self.gameTaskClosures = []
        self.gameTaskClosuresLock = threading.Lock()
        self.gameTaskExit = False
        self.gameTask = executor.submit(Game._GameFunc, self)

        # Create the guest agent proxy.
        self.agent = GuestAgent(self.executor, self.GetIP())

        # Init the player variables.
        self.users = {}
        self.portToUser = {}
        self.pidToUser = {}

        # Create the VM that we'll be using for this game.
        self.vmManager = vmManager
        self.vm = vmManager.CreateVM(self.scenario['vmPath'], self.scenarioName)
        
        # Create the scorer for scoring the users.
        self.scorer = Scorer(self)
    
        # Initialize event callbacks
        # Callback inserted by kofserver into this class.
        # Used by this class to notify kofserver API users.
        self.eventCallbackSet = set()
        self.eventCallbackSetLock = threading.Lock()

        # Callback inserted into guest agent and called by guest agent.
        self.eventCallback = lambda x: self.EmitGameEvents([x,])
        self.agent.AddCallback(self.eventCallback)

    def __del__(self):
        self.StopGameFunc()

    def AddEventCallback(self, cb):
        with self.eventCallbackSetLock:
            if self.state == GameState.GAME_DESTROYING or self.state == GameState.GAME_DESTROYED:
                cb(None)
            else:
                self.eventCallbackSet.add(cb)
    
    
    def RemoveEventCallback(self, cb):
        with self.eventCallbackSetLock:
            self.eventCallbackSet.remove(cb)

    def EmitGameEvents(self, evts):
        # TODO: Event filtering?
        filteredEvents = []
        for evt in evts:
            if evt == GameEventType.PROC_OUTPUT and not self.scenario['allowStdout']:
                # Filtered
                continue
            filteredEvents.append(evt)
        with self.eventCallbackSetLock:
            for cb in self.eventCallbackSet:
                for evt in filteredEvents:
                    cb(evt)

    # Start the game.
    def Start(self):
        # Set it to we are starting.
        result = KOFErrorCode.ERROR_NONE
        evt = threading.Event()
        def StartInGameTask():
            if self.state == GameState.GAME_CREATED:
                self.state = GameState.GAME_STARTING1
            else:
                logging.warn("Trying to start %s when it's not in created state"%self.gameName)
                result = KOFErrorCode.ERROR_INCORRECT_STATE
            evt.set()
        with self.gameTaskClosuresLock:
            self.gameTaskClosures.append(StartInGameTask)
        evt.wait()
        # GameFunc will handle the rest.
        # ie. Initialize the VM, waiting for guest agent... etc
        return result

    # Destroy the game.
    def Destroy(self):
        result = KOFErrorCode.ERROR_NONE
        evt = threading.Event()
        def DestroyInGameTask():
            if self.state != GameState.GAME_RUNNING:
                logging.warn("Destroying game not in running state: %s %s"%(self.gameName, str(self.state)))
            self.state = GameState.GAME_DESTROYING
            evt.set()
        with self.gameTaskClosuresLock:
            self.gameTaskClosures.append(DestroyInGameTask)
        evt.wait()
        # GameFunc will handle the rest.
        # ie. Initialize the VM, waiting for guest agent... etc
        return result

    def PlayerIssueCmd(self, playerName, cmd):
        if self.state != GameState.GAME_RUNNING:
            logging.info("Player %s issued command when game %s is not running."%(playerName, self.gameName))
            return KOFErrorCode.ERROR_GAME_NOT_RUNNING
        if not self.scenario['allowCommand']:
            logging.info("Player %s tried to issue command when game %s doesn't allow."%(playerName, self.gameName))
            return KOFErrorCode.ERROR_GAME_NOT_ALLOW
        if playerName not in self.users:
            logging.info("Player %s not register id game %s."%(playerName, self.gameName))
            return KOFErrorCode.ERROR_USER_NOT_REGISTERED
        if self.users[playerName]["lastCmd"]+self.scenario["CmdCooldown"]>time.time():
            logging.info("Player %s need to cooldown before running command."%(playerName,))
            return KOFErrorCode.ERROR_COOLDOWN
        res = self.agent.RunCmd(cmd)
        if res.reply.error != GuestErrorCode.ERROR_NONE:
            logging.warning("Executing command '%s' failed due to agent problem %s."%(cmd, res.reply.error))
            return KOFErrorCode.ERROR_AGENT_PROBLEM
        self.SetPlayerPID(playerName, res.pid)
        self.users[playerName]["lastCmd"] = time.time()
        return KOFErrorCode.ERROR_NONE

    def SetPlayerPID(self, playerName, pid):
        assert playerName in self.users
        self.users[playerName]['pid'] = pid
        self.pidToUser[pid] = playerName

    # Return the Game protobuf for this game.
    def GetGameProto(self):
        result = kofserver_pb2.Game(name=self.gameName, state=self.state)
        return result
    
    def _GameFunc(self):
        # We need to catch the exception because it doesn't showup until
        # very late, when .result() is called.
        try:
            self._GameFuncReal()
        except Exception:
            logging.exception("Exception in GameFunc")

    def _GameFuncReal(self):
        logging.info("GameFunc for %s running"%(self.gameName,))
        # This method runs for the entire time life cycle of the game.
        while True:
            with self.gameTaskClosuresLock:
                for c in self.gameTaskClosures:
                    c()
                self.gameTaskClosures = []

            if self.gameTaskExit:
                # Time to go
                return True
            
            if self.state == GameState.GAME_CREATED:
                # Nothing to do
                time.sleep(0.5)
                continue
            
            if self.state == GameState.GAME_STARTING1:
                if self.vm.GetState() == VM.VMState.CREATED:
                    # Init and start the VM
                    res = self.vm.Init()
                    if not res or self.vm.GetState() != VM.VMState.READY:
                        logging.error("Failed to init VM (%s) or invalid VM state after Init() (%s)"%(str(res), str(self.vm.GetState())))
                        self.state = GameState.GAME_ERROR
                        continue

                    res = self.vm.Boot()
                    if not res:
                        logging.error("Failed to boot VM")
                        self.state = GameState.GAME_ERROR
                        continue
                    
                    continue
                else:
                    # We've finished init and start VM step, so wait for it
                    # to be running.
                    if self.vm.GetState() == VM.VMState.RUNNING:
                        logging.info("VM for Game %s is running."%(self.gameName,))
                        self.state = GameState.GAME_STARTING2
                    # Wait some time?
                    time.sleep(0.5)
                
            if self.state == GameState.GAME_STARTING2 or self.state == GameState.GAME_REBOOTING2:
                # Wait for the guest agent to be connected.
                if self.agent.EnsureConnection():
                    # It's connected, so we can move onto the started state
                    logging.info("Agent for Game %s is ready."%(self.gameName,))
                    self.state = GameState.GAME_RUNNING
                    self.scorer.NotifyGameStarted()
                    continue
                # See if it's a timeout.
                uptime = self.vm.GetUptime()
                if uptime is not None and uptime > self.scenario['startupLimit']:
                    logging.warn("Game %s's VM exceeded startup limit, resetting it."%self.gameName)
                    self.state = GameState.GAME_RECREATING
                    continue
                
                # If agent is responsive, then we don't have to check the VM.
                # Wait and try again.
                time.sleep(0.5)
                continue
            
            if self.state == GameState.GAME_RUNNING:
                playerScored = self.scorer.TryScorePlayers()
                if not playerScored:
                    # Maybe it's disconnected?
                    if not self.agent.CheckAlive():
                        # It's down.
                        if self.state == GameState.GAME_RUNNING:
                            logging.error("Game rebooting due to dead agent")
                            self.state = GameState.GAME_REBOOTING1
                        else:
                            logging.error("Game agent dead but game state = %s"%(str(self.state),))
                        continue
                    # Don't stress it too much otherwise.
                    time.sleep(0.3)
            
            if self.state == GameState.GAME_REBOOTING1:
                if self.vm.GetState() == VM.VMState.RUNNING:
                    # VM is running, shut it down.
                    res = self.vm.Shutdown()
                    if not res or self.vm.GetState() != VM.VMState.READY:
                        logging.error("Failed to shutdown VM (%s) or invalid VM state after Shutdown() (%s) during reboot"%(str(res), str(self.vm.GetState())))
                        self.state = GameState.GAME_ERROR
                    continue
                
                if self.vm.GetState() == VM.VMState.READY:
                    # VM is down, restart it and put it into the new state.
                    res = self.vm.Boot()
                    if not res or self.vm.GetState() != VM.VMState.RUNNING:
                        logging.error("Failed to boot VM during reboot.")
                        self.state = GameState.GAME_ERROR
                    else:
                        self.state = GameState.GAME_REBOOTING2
                    continue
            
            if self.state == GameState.GAME_DESTROYING or self.state == GameState.GAME_RECREATING:
                # Shutdown the VM and reset the guest agent.
                self.agent.ResetConnection()
                if self.vm.GetState() == VM.VMState.RUNNING:
                    result = self.vm.Shutdown()
                    if not result:
                        logging.error("Failed to shutdown VM")
                        self.state = GameState.GAME_ERROR
                        continue
                
                if self.vm.GetState() == VM.VMState.READY:
                    # Let's destroy it.
                    result = self.vm.Destroy()
                    if not result:
                        logging.error("Failed to destroy VM")
                        self.state = GameState.GAME_ERROR
                        continue
                    if self.state == GameState.GAME_RECREATING:
                        # We're done, restart the game/VM.
                        self.state = GameState.GAME_STARTING1
                        self.vm = self.vmManager.CreateVM(self.scenario['vmPath'], self.scenarioName)
                        continue
                    else:
                        # VM's cleaned up, let's get the event handlers off.
                        with self.eventCallbackSetLock:
                            for cb in self.eventCallbackSet:
                                cb(None)
                        self.state = GameState.GAME_DESTROYED
                    
    
    def StopGameFunc(self):
        # Note: Should never be called from GameFunc, or it'll deadlock.
        self.gameTaskExit = True
        # Wait for it to end by asking for its result.
        self.gameTask.result()

    def GetIP(self):
        return self.scenario['ip']

    def RegisterPlayer(self, username):
        if username in self.users:
            return KOFErrorCode.ERROR_USER_ALREADY_EXISTS
        
        self.users[username] = {}
        
        # Generate a port for the user.
        for i in range(1000000):
            # Not a while True so if something went wrong we know.
            
            port = random.randint(Config.conf()['portStart'], Config.conf()['portEnd'])
            if port in self.portToUser:
                port = -1
                continue
            break
        if port == -1:
            # This shouldn't happen, so it's an Exception not a return code.
            raise Exception("No valid port available")
        self.portToUser[port] = username
        self.users[username]["port"] = port
        self.users[username]["pid"] = -1 # Not available yet.
        self.users[username]["pidUp"] = False # User's pid up when we last check?
        self.users[username]["portUp"] = False # User's port up when we last check?
        self.users[username]["lastCmd"] = 0.0
        self.users[username]["lastSC"] = 0.0

        return KOFErrorCode.ERROR_NONE
    
    def QueryPlayerInfo(self, playerName):
        if playerName != "":
            return [self.GetPlayerInfoProto(playerName),]
        # playerName == "", so we retrieve all the players.
        res = []
        for p in self.users:
            res.append(self.GetPlayerInfoProto(p))
        return res

    def GetPlayerInfoProto(self, playerName):
        if playerName not in self.users:
            raise Exception("Invalid player %s for GetPlayerInfoProto"%playerName)
        
        udict = self.users[playerName]
        result = kofserver_pb2.PlayerInfo(playerName=playerName)
        result.port = udict["port"]
        result.pid = udict["pid"]
        result.portUp = udict["portUp"]
        result.pidUp = udict["pidUp"]
        return result

    def Shutdown(self):
        # Exit game task thread first
        self.gameTaskExit = True
        # Wait for it to terminate
        self.gameTask.result()

        # Clear all closures and event handlers
        with self.gameTaskClosuresLock:
            for c in self.gameTaskClosures:
                c()
            self.gameTaskClosures = []
        with self.eventCallbackSetLock:
            for cb in self.eventCallbackSet:
                cb(None)
                
        # Reset VM state.
        self.state = GameState.GAME_ERROR
        if self.vm.GetState() == VM.VMState.RUNNING:
            result = self.vm.Shutdown()
            if not result:
                logging.error("Failed to shutdown VM during shutdown")
            
        if self.vm.GetState() == VM.VMState.READY:
            result = self.vm.Destroy()
            if not result:
                logging.error("Failed to destroy VM during shutdown")
                    


    @staticmethod
    def LoadScenario(scenarioName):
        scenarioDir = Config.conf()['scenarioDir']
        scenarioDir = os.path.abspath(scenarioDir)
        scenarioPath = os.path.join(scenarioDir, scenarioName)
        ymlPath = os.path.join(scenarioPath, "scenario.yml")
        try:
            with open(ymlPath) as f:
                result = yaml.load(f, Loader=yaml.FullLoader)
        except Exception:
            logging.exception("Failed to open scenario.yml file %s"%ymlPath)
            raise
        # If vmPath is relative, we convert it to absolute here.
        if not os.path.isabs(result['vmPath']):
            result['vmPath'] = os.path.join(scenarioPath, result['vmPath'])
        return result
