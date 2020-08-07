# Hitcon-Agent
For gaming use, No commercial purpose

- Host Agent
    - POST /host/api/shellcode :[shellcode]
        - shellcode -> base64 encode
        - Return
            - success or not
            - pid

    - POST /host/api/status :[pid]
        - request with pid number
        - Return
            - process status