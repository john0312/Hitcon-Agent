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

import logging
from concurrent import futures

from irc import IRC
from agent import Agent
from config import Config

# TODO: Enhance performance
def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize the config.
    Config.Init()

    # Initialize agent
    executor = futures.ThreadPoolExecutor(max_workers=32)
    agent = Agent(executor)

    # Initialize IRC
    irc = IRC(nickname=Config.conf()['botNickName'])
    irc.SetChannel(Config.conf()['channel'])
    irc.ResetGame()
    irc.SetAgent(agent)
    irc.run(hostname=Config.conf()['ircServer'], port=Config.conf()['ircSSLPort'], tls=True, tls_verify=False)

if __name__ == '__main__':
    main()
