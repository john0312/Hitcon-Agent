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

# This hosts the ScoreBoard class which records the player's score and other stats.
import time
import logging

class ScoreBoard:
    def __init__(self, database):
        self.database = database
        # Create scoreboard table
        self.database.executor.submit(ScoreBoard.CreateScoreTable, self).result()
        self.database.executor.submit(ScoreBoard.CreateActionTable, self).result()

    # This is called every time the Game logic checks if the players are alive.
    # This method is used to record players who are alive.
    # gameName: A string that is the name of the game that we are recording.
    # playerName: An array of player's name.
    # portUptime: An array of uptime for the player's port.
    # portScorePerSec: An array of scores per second of uptime for the player.
    # pidUptime: An array of uptime for the player's process.
    # pidScorePerSec: An array of scores per second of uptime for the player.
    # Array sizes for playerName, portUptime, portScorePerSec, pidUptime and
    # pidScorePerSec are guaranteed to be the same.
    # portUptime and pidUptime is usually the check interval.
    # 
    # For example:
    # - In the past 30 seconds:
    #     - Player Alice's process is online, but the port is unreachable.
    #     - Player Bob's process is online, and the port is reachable.
    #     - Player Eve's process and port are both offline.
    # - In this round:
    #     - Process being up is worth 5 points per seconds.
    #     - Port reachable is worth 10 points per seconds.
    # Then, the call to LogTicks will look like this:
    # LogTicks(
    #     "Game1",                   # gameName
    #     [ "Alice", "Bob", "Eve" ], # playerName
    #     [ 0, 30, 0 ],              # portUptime
    #     [ 10, 10, 10 ],            # portScorePerSec
    #     [ 30, 30, 0 ],             # pidUptime
    #     [ 5, 5, 5 ]                # pidScorePerSec
    # )
    # In this case, Alice should get 30*5 points, Bob should get 30*5+30*10
    # points, and Eve doesn't get any point.
    def LogTicks(self, gameName, playerName, portUptime, portScorePerSec, pidUptime, pidScorePerSec):
        return self.database.executor.submit(ScoreBoard._LogTicks, self, gameName, playerName, portUptime, portScorePerSec, pidUptime, pidScorePerSec).result()

    def _LogTicks(self, gameName, playerName, portUptime, portScorePerSec, pidUptime, pidScorePerSec):
        now = int(time.time())
        sql = "INSERT INTO score (game_name, player_name, port_uptime, port_score_per_sec, pid_uptime, pid_score_per_sec, create_time) VALUES (?, ?, ?, ?, ?, ?, ?);"
        values = []
        for i in range(len(playerName)):
            values.append((gameName, playerName[i], portUptime[i], portScorePerSec[i], pidUptime[i], pidScorePerSec[i], now))
            
        cursor = self.database.ExecuteMany(sql, values)
        try:
            self.database.Commit()
            results = False if cursor.rowcount == -1 else True
            cursor.close()
            return results
        except:  
            raise

    # Logs the player's action, such as "Shellcode", "Command", and "OpenURL".
    # gameName: a string that is the name of the game that we are recording.
    # playerName: Name of the player doing the action.
    # actionType: A string that represents the action type.
    #             Currently, "Shellcode", "Command" and "OpenURL" is possible.
    #             Others could be added in the future.
    # actionContent: A string that represents the content of the action. For
    #                shellcode, this would be the base64 of the shellcode.
    #                For command, this is the full command, and for open URL,
    #                This is the full URL.
    #                Note that this field could be rather large, and it doesn't
    #                need to be searched. (ie. no index, could use blob type or
    #                even off database storage)
    # Example:
    # LogPlayerAction("game1", "malice", "command", "rm -rf /")
    def LogPlayerAction(self, gameName, playerName, actionType, actionContent):
        return self.database.executor.submit(ScoreBoard._LogPlayerAction, self, gameName, playerName, actionType, actionContent).result()

    def _LogPlayerAction(self, gameName, playerName, actionType, actionContent):
        now = int(time.time())
        sql = "INSERT INTO action (game_name, player_name, type, content, create_time) VALUES (?, ?, ?, ?, ?);"
        values = (gameName, playerName, actionType, actionContent, now)
        cursor = self.database.Execute(sql, values)
        try:
            self.database.Commit()
            results = False if cursor.rowcount == -1 else True
            cursor.close()
            return results
        except:  
            raise

    # Query the current score, returns an array of dict of score and other
    # statistics. The returned dict should contain:
    # - "playerName"
    # - "portUptime"
    # - "portScore"
    # - "pidUptime"
    # - "pidScore"
    # - "totalScore"
    # If gameName is "", then scores for all games are queried and the results
    # are summed for each player.
    # If playerName is "", then all players with non-zero scores are returned.
    # If there's a problem with the database, an exception is raised.
    # Example:
    # If the example above on LogTicks is called twice, then:
    # QueryScore("game1", "Alice") should results in:
    # [ { "playerName": "Alice", "portUptime": 0, "portScore": 0,
    #     "pidUptime": 60, "pidScore": 300, "totalScore": 300 } ]
    def QueryScore(self, gameName, playerName):
        return self.database.executor.submit(ScoreBoard._QueryScore, self, gameName, playerName).result()

    def _QueryScore(self, gameName, playerName):
        sql = "SELECT player_name, SUM(port_uptime), SUM(port_score_per_sec), SUM(pid_uptime), SUM(pid_score_per_sec) FROM score %s GROUP BY game_name, player_name;"
        values = []
        whereSQL = ""
        if gameName != "":
            whereSQL += "WHERE game_name=?"
            values.append(gameName)
        if playerName != "":
            whereSQL += "WHERE player_name=?" if whereSQL == "" else " AND player_name=?"
            values.append(playerName)

        sql = sql % (whereSQL)
        cursor = self.database.Execute(sql, tuple(values))
        try:
            records = cursor.fetchall()
            cursor.close()
            results = []
            if len(records) > 0:
                for r in records:
                    portScore = r[1] * r[2]
                    pidScore = r[3] * r[4]
                    totalScore = portScore + pidScore
                    # If playerName is "", then all players with non-zero scores are returned.
                    if playerName == "" and totalScore == 0:
                        continue
                    results.append({
                        "playerName": r[0],
                        "portUptime": r[1],
                        "portScore": portScore,
                        "pidUptime": r[3],
                        "pidScore": pidScore,
                        "totalScore": totalScore})
            return results
        except:  
            raise

    def CreateScoreTable(self):
        sql = """CREATE TABLE IF NOT EXISTS score
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                player_name TEXT NOT NULL,
                port_uptime INTEGER,
                port_score_per_sec INTEGER,
                pid_uptime INTEGER,
                pid_score_per_sec INTEGER,
                create_time INTEGER NOT NULL);"""
        cursor = self.database.Execute(sql)
        try:
            self.database.Commit()
            results = False if cursor.rowcount == -1 else True
            cursor.close()
            return results
        except:  
            raise

    def CreateActionTable(self):
        sql = """CREATE TABLE IF NOT EXISTS action
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                player_name TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT,
                create_time INTEGER NOT NULL);"""
        cursor = self.database.Execute(sql)
        try:
            self.database.Commit()
            results = False if cursor.rowcount == -1 else True
            cursor.close()
            return results
        except:  
            raise
