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

# This file holds the main function for the guest/qemu agent.

import grpc
import logging
from concurrent import futures

import guest_agent_pb2, guest_agent_pb2_grpc
import guest_agent
from proc_watcher import ProcWatcher
from proc_runner import ProcRunner
from config import Config

def main():
    # Setup logging and config
    logging.basicConfig(level=logging.INFO)
    Config.Init()

    # Create the executor that we'll run the server from.
    executor = futures.ThreadPoolExecutor(max_workers=8)

    # Create the server adaptor instance.
    procWatcher = ProcWatcher(executor)
    procRunner = ProcRunner(executor)
    servicer = guest_agent.GuestAgent(procWatcher, procRunner, executor)

    # Start the Guest Agent server
    server = grpc.server(executor)
    guest_agent_pb2_grpc.add_GuestAgentServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:29120')
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.warn("Ctrl-C Detected, shutting down.")
        server.stop(2.0)

    procRunner.Shutdown()
    procWatcher.Shutdown()
    executor.shutdown()

if __name__ == "__main__":
    main()
