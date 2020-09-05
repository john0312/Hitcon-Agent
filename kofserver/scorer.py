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

# This file host the Scorer class, it is in charge of scoring the players.

import logging
import time

from kofserver_pb2 import GameState
from guest_agent_pb2 import ErrorCode as GuestErrorCode

class Scorer:
    def __init__(self, game):
        # Initialize the variables from Game.
        self.game = game
        self.scenario = game.scenario
        self.scoreboard = game.scoreboard
        self.scanner = game.scanner
        
        # When's the last time we check the player's stats?
        self.pidLastCheckTime = None
        self.portLastCheckTime = None

    # This is called by Game class when the game is started.
    def NotifyGameStarted(self):
        assert self.game.state == GameState.GAME_RUNNING
        currentTime = time.time()
        self.pidLastCheckTime = currentTime
        self.portLastCheckTime = currentTime
    
    # Try to score the players. Return True is players are scored,
    # False otherwise.
    def TryScorePlayers(self):
        if self.game.state != GameState.GAME_RUNNING:
            logging.warn("Trying to score players when game is not running")
            return False
        
        assert self.pidLastCheckTime is not None
        assert self.portLastCheckTime is not None
        
        pidUptime = {}
        portUptime = {}
        playerSet = set() # Just a dictionary to store the players
        for p in self.game.users:
            playerSet.add(p)
        
        currentTime = time.time()
        if self.pidLastCheckTime + self.scenario['pidCheckInterval'] <= currentTime:
            # Do the pid check.
            try:
                pidUptime = self.CheckPID(playerSet)
            except Exception:
                if self.game.state != GameState.GAME_RUNNING:
                    # Game no longer running we're checking.
                    logging.warn("Game shutdown (%s) while we are checking PID"%(str(self.game.state),))
                else:
                    # Game's still running but check failed, that's a problem.
                    logging.exception("Game still running but checking pid failed")
                return False
            self.pidLastCheckTime += self.scenario['pidCheckInterval']
        
        if self.portLastCheckTime + self.scenario['portCheckInterval'] <= currentTime:
            # Do the port check.
            try:
                portUptime = self.CheckPort(playerSet)
            except Exception:
                if self.game.state != GameState.GAME_RUNNING:
                    # Game no longer running we're checking.
                    logging.warn("Game shutdown (%s) while we are checking port"%(str(self.game.state),))
                else:
                    # Game's still running but check failed, that's a problem.
                    logging.exception("Game still running but checking port failed")
                return False
            self.portLastCheckTime += self.scenario['portCheckInterval']
    
        # Generate the tick
        if len(pidUptime) == 0 and len(portUptime) == 0:
            # No tick required
            return False
        
        playerList = []
        portUptimeList = []
        portScorePerSec = []
        pidUptimeList = []
        pidScorePerSec = []
        for p in playerSet:
            if p in pidUptime or p in portUptime:
                playerList.append(p)
                portUptimeList.append(portUptime[p] if p in portUptime else 0.0)
                portScorePerSec.append(self.scenario['portScorePerSec'] if p in portUptime else 0.0)
                pidUptimeList.append(pidUptime[p] if p in pidUptime else 0.0)
                pidScorePerSec.append(self.scenario['pidScorePerSec'] if p in pidUptime else 0.0)
        
        self.scoreboard.LogTicks(self.game.gameName, playerList, portUptimeList, portScorePerSec, pidUptimeList, pidScorePerSec)
        
        return True
        
    # Given a list of player name, return a dict of up time.
    def CheckPID(self, playerSet):
        procInfo = self.game.agent.QueryProcInfo()
        if procInfo.reply.error != GuestErrorCode.ERROR_NONE:
            logging.error("Failed to QueryProcInfo(), can't score player's PID")
            return False
        
        pidUptime = {}
        for proc in procInfo.info:
            if proc.pid in self.game.pidToUser:
                # TODO: Check the process state as well.
                username = self.game.pidToUser[proc.pid]
                if username not in playerSet:
                    # Race condition on pidToUser, ignore this user.
                    logging.warn("Race condition on pidToUser: %s", username)
                    continue
                assert username not in pidUptime
                pidUptime[username] = self.scenario['pidCheckInterval']
        
        for user in playerSet:
            if user not in pidUptime:
                pidUptime[user] = 0.0

        return pidUptime
    
    def CheckPort(self, playerSet):
        playerList = [] # Maybe not needed, optimize later.
        portList = []
        for player in playerSet:
            playerList.append(player)
            portList.append(self.game.users[player]["port"])
        
        upList = self.scanner.ScanHostPorts(self.game.GetIP(), portList)
        assert len(upList) == len(playerList)
        portUptime = {}
        for i in range(len(playerList)):
            portUptime[playerList[i]] = self.scenario['portCheckInterval'] if upList[i] else 0.0
        
        return portUptime

