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

# This file (will) host a high performance port scanner (soon, hopefully).

class PortScanner:
    def __init__(self):
        pass

    # ScanHostPorts scans the host's ports.
    # host is the IP address of the target.
    # ports is a list of ports to scan.
    # Returns a list of boolean to indicate if the port is reachable.
    # Example:
    # ScanHostPorts("192.168.0.1", [12345, 54321, 9876, 1111])
    # would returns:
    # [True, True, True, False]
    # If only 1111 is not reachable, and the rest are reachable.
    def ScanHostPorts(self, host, ports):
        # TODO
        # Lazy scanner pretends every port is not reachable!
        return [False,]*len(ports)
    
        
