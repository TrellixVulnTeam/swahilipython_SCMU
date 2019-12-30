#!/usr/bin/env python3

"""
Remote python server.
Execute Python commands remotely na send output back.

WARNING: This version has a gaping security hole -- it accepts requests
kutoka any host on the Internet!
"""

agiza sys
kutoka socket agiza socket, AF_INET, SOCK_STREAM
agiza io
agiza traceback

PORT = 4127
BUFSIZE = 1024

eleza main():
    ikiwa len(sys.argv) > 1:
        port = int(sys.argv[1])
    isipokua:
        port = PORT
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    wakati Kweli:
        conn, (remotehost, remoteport) = s.accept()
        ukijumuisha conn:
            andika('connection from', remotehost, remoteport)
            request = b''
            wakati 1:
                data = conn.recv(BUFSIZE)
                ikiwa sio data:
                    koma
                request += data
            reply = execute(request.decode())
            conn.send(reply.encode())

eleza execute(request):
    stdout = sys.stdout
    stderr = sys.stderr
    sys.stdout = sys.stderr = fakefile = io.StringIO()
    jaribu:
        jaribu:
            exec(request, {}, {})
        tatizo:
            andika()
            traceback.print_exc(100)
    mwishowe:
        sys.stderr = stderr
        sys.stdout = stdout
    rudisha fakefile.getvalue()

jaribu:
    main()
tatizo KeyboardInterrupt:
    pita
