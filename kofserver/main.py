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


# This file holds the main function for KOF Server.

import grpc
import logging
from concurrent import futures

import kofserver_pb2, kofserver_pb2_grpc
import kofserver
import vm_manager
from config import Config

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize the config.
    Config.Init()
    
    # Create the VM Manager service.
    vmManager = vm_manager.VMManager()

    # Create the executor that we'll run the server from.
    executor = futures.ThreadPoolExecutor(max_workers=32)
    # Create the server adaptor instance.
    kofservicer = kofserver.KOFServer(executor, vmManager)

    # Start the KOF Server service
    server = grpc.server(executor)
    kofserver_pb2_grpc.add_KOFServerServicer_to_server(kofservicer, server)
    server.add_insecure_port('[::]:29110')
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.warn("Ctrl-C Detected, shutting down.")

    kofservicer.Shutdown()
    executor.shutdown()

if __name__ == '__main__':
    main()

    


