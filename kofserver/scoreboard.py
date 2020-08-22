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

class ScoreBoard:
    def __init__(self):
        # TODO
        pass

    # This is called every time the Game logic checks if a player is alive.
    # If the player is alive, then this method is used to record the score for
    # being alive.
    # portUptime and pidUptime is usually the check interval.
    def LogTick(gameName, playerName, portUptime, portScorePerSec, pidUptime, pidScorePerSec):
        # TODO
        pass

    # TODO
    # def LogPlayerAction(...):

    # Query the current score, returns an array of dict.
    def QueryScore(gameName, playerName):
        # TODO
        return []
