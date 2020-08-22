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

"""
Configurable system resource limits
"""
 
import resource
 
 
LIMITS = {
    # CPU seconds, defaulting to 1.
    "CPU": 1,
    # Real time, defaulting to 1 second.
    "REALTIME": 1,
    # Total process virutal memory, in bytes, defaulting to unlimited.
    "VMEM": 0,
    # Size of files creatable, in bytes, defaulting to nothing can be written.
    "FSIZE": 0,
}
 
 
def set_limit(limit_name, value):
    """
    Set a limit for jailed code.
 
    `limit_name` is a string, the name of the limit to set. `value` is the
    value to use for that limit.  The type, meaning, default, and range of
    accepted values depend on `limit_name`.
 
    These limits are available:
 
        * `"CPU"`: the maximum number of CPU seconds the jailed code can use.
            The value is an integer, defaulting to 1.
 
        * `"REALTIME"`: the maximum number of seconds the jailed code can run,
            in real time.  The default is 1 second.
 
        * `"VMEM"`: the total virtual memory available to the jailed code, in
            bytes.  The default is 0 (no memory limit).
 
        * `"FSIZE"`: the maximum size of files creatable by the jailed code,
            in bytes.  The default is 0 (no files may be created).
 
        * `"PROXY"`: 1 to use a proxy process, 0 to not use one. This isn't
            really a limit, sorry about that.
 
    Limits are process-wide, and will affect all future calls to jail_code.
    Providing a limit of 0 will disable that limit.
 
    """
    LIMITS[limit_name] = value
 
 
def create_rlimits():
    """
    Create a list of resource limits for our jailed processes.
    """
    rlimits = []
 
    # No subprocesses.
    rlimits.append((resource.RLIMIT_NPROC, (0, 0)))
 
    # CPU seconds, not wall clock time.
    cpu = LIMITS["CPU"]
    if cpu:
        # Set the soft limit and the hard limit differently.  When the process
        # reaches the soft limit, a SIGXCPU will be sent, which should kill the
        # process.  If you set the soft and hard limits the same, then the hard
        # limit is reached, and a SIGKILL is sent, which is less distinctive.
        rlimits.append((resource.RLIMIT_CPU, (cpu, cpu+1)))
 
    # Total process virtual memory.
    vmem = LIMITS["VMEM"]
    if vmem:
        rlimits.append((resource.RLIMIT_AS, (vmem, vmem)))
 
    # Size of written files.  Can be zero (nothing can be written).
    fsize = LIMITS["FSIZE"]
    rlimits.append((resource.RLIMIT_FSIZE, (fsize, fsize)))
 
    return rlimits