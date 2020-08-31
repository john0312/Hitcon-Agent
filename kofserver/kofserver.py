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

# This file host the primary logic for KOF Server, and handles all the
# KOF Server request.

import logging

from kofserver_pb2 import ErrorCode as KOFErrorCode
from kofserver_pb2 import GameState
import kofserver_pb2, kofserver_pb2_grpc
import game
from scoreboard import ScoreBoard
from database import Database
from port_scanner import PortScanner

class KOFServer(kofserver_pb2_grpc.KOFServerServicer):

    def __init__(self, executor, vmManager):
        # games is a dictionary that maps the gameName to Game object.
        self.games = {}
        # executor is a concurrent.futures.Executor class that allows us to
        # run stuff.
        self.executor = executor
        # vmManager is the VMManager instance for managing Virtual Machines.
        self.vmManager = vmManager
        # scanner is a port scanner.
        self.scanner = PortScanner()

        # Create a scoreboard and database instance.
        self.database = Database()
        self.scoreboard = ScoreBoard(self.database)

    def CreateGame(self, request, context):
        self._GarbageCollectGames()
        if request.gameName in self.games:
            return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_GAME_ALREADY_EXISTS)

        try:
            self.games[request.gameName] = game.Game(self.executor, self.vmManager, self.scoreboard, self.scanner, request.gameName, request.scenarioName)
        except Exception:
            logging.exception("Failed to create game")
            return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_CREATE_GAME)
        return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_NONE)

    def StartGame(self, request, context):
        self._GarbageCollectGames()
        if request.gameName not in self.games:
            return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_GAME_NOT_FOUND)
        error = self.games[request.gameName].Start()
        return kofserver_pb2.Rep(error=error)
    
    def DestroyGame(self, request, context):
        self._GarbageCollectGames()
        if request.gameName not in self.games:
            return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_GAME_NOT_FOUND)
        error = self.games[request.gameName].Destroy()
        return kofserver_pb2.Rep(error=error)

    def QueryGame(self, request, context):
        self._GarbageCollectGames()
        results = []
        if request.gameName != "":
            if request.gameName not in self.games:
                return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_GAME_NOT_FOUND)
            results.append(self.games[request.gameName].GetGameProto())
        else:
            for gn in self.games:
                results.append(self.games[gn].GetGameProto())
        genericReply = kofserver_pb2.Rep(error=KOFErrorCode.ERROR_NONE)
        return kofserver_pb2.QueryGameRep(reply=genericReply, games=results)

    def PlayerRegister(self, request, context):
        if request.gameName not in self.games:
            return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_GAME_NOT_FOUND)
        error = self.games[request.gameName].RegisterPlayer(request.playerName)
        return kofserver_pb2.Rep(error=error)

    def PlayerInfo(self, request, context):
        if request.gameName not in self.games:
            return kofserver_pb2.Rep(error=KOFErrorCode.ERROR_GAME_NOT_FOUND)
        error = self.games[request.gameName].QueryPlayerInfo(request.playerName)
        return kofserver_pb2.Rep(error=error)

    def PlayerIssueCmd(self, request, context):
        if request.gameName not in self.games:
            genericReply = kofserver_pb2.Rep(error=KOFErrorCode.ERROR_GAME_NOT_FOUND)
            return kofserver_pb2.PlayerIssueCmdRep(reply=genericReply)
        error = self.games[request.gameName].PlayerIssueCmd(request.playerName, request.cmd)
        genericReply = kofserver_pb2.Rep(error=error)
        return kofserver_pb2.PlayerIssueCmdRep(reply=genericReply)

    def QueryScore(self, request, context):
        result = self.scoreboard.QueryScore(request.gameName, request.playerName)
        genericReply = kofserver_pb2.Rep(error=KOFErrorCode.ERROR_NONE)
        reply = kofserver_pb2.QueryScoreRep(reply=genericReply)
        for r in result:
            score = kofserver_pb2.PlayerScore()
            score.playerName = r['playerName']
            score.score = r['totalScore']
            score.pidUptime = r['pidUptime']
            score.portUptime = r['portUptime']
            reply.scores.append(score)
        return reply

    def Shutdown(self):
        logging.info("Shutting down all games.")
        for g in self.games:
            self.games[g].Shutdown()
        self.scanner.Shutdown()
        self.scanner = None

    def _GarbageCollectGames(self):
        newGames = {}
        for g in self.games:
            if self.games[g].GetGameProto().state != GameState.GAME_DESTROYED:
                newGames[g] = self.games[g]
        self.games = newGames
