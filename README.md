# Hitcon-Agent

- Host Agent
    - POST /host/api/shellcode :[shellcode],[pid]\(optional\)
        - shellcode -> base64 encode
        - pid -> kill orignal pid
        - Return
            - success or not
            - pid
            - e.g success,58211

    - POST /host/api/status :[pid]
        - request with pid number
        - Return
            - process status
                - e.g running/sleeping/ or 'Process Dead'
            - cpu / memroy usage
                - e.g ,0.1,969796



### TODO
1. setrlimit testing (CPU usage...)
2. shellcode testing
3. logging system - qemu(-) / host(V)

### Bug Fixed
- If user input is not valid , will crash the program
- Agent shutdown when client close connection.
- request with non-exist pid will crash the program

### Announcement
user binding may need to use **socket.gethostname()**
