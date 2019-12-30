#!/usr/bin/env python3

"""
Remote python client.
Execute Python commands remotely na send output back.
"""

agiza sys
kutoka socket agiza socket, AF_INET, SOCK_STREAM, SHUT_WR

PORT = 4127
BUFSIZE = 1024

eleza main():
    ikiwa len(sys.argv) < 3:
        andika("usage: rpython host command")
        sys.exit(2)
    host = sys.argv[1]
    port = PORT
    i = host.find(':')
    ikiwa i >= 0:
        port = int(host[i+1:])
        host = host[:i]
    command = ' '.join(sys.argv[2:])
    ukijumuisha socket(AF_INET, SOCK_STREAM) kama s:
        s.connect((host, port))
        s.send(command.encode())
        s.shutdown(SHUT_WR)
        reply = b''
        wakati Kweli:
            data = s.recv(BUFSIZE)
            ikiwa sio data:
                koma
            reply += data
        andika(reply.decode(), end=' ')

main()
