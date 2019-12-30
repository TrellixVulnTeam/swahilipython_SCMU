#!/usr/bin/env python3
'''
Small wsgiref based web server. Takes a path to serve kutoka na an
optional port number (defaults to 8000), then tries to serve files.
Mime types are guessed kutoka the file names, 404 errors are raised
ikiwa the file ni sio found. Used kila the make serve target kwenye Doc.
'''
agiza sys
agiza os
agiza mimetypes
kutoka wsgiref agiza simple_server, util

eleza app(environ, respond):

    fn = os.path.join(path, environ['PATH_INFO'][1:])
    ikiwa '.' haiko kwenye fn.split(os.path.sep)[-1]:
        fn = os.path.join(fn, 'index.html')
    type = mimetypes.guess_type(fn)[0]

    ikiwa os.path.exists(fn):
        respond('200 OK', [('Content-Type', type)])
        rudisha util.FileWrapper(open(fn, "rb"))
    isipokua:
        respond('404 Not Found', [('Content-Type', 'text/plain')])
        rudisha [b'not found']

ikiwa __name__ == '__main__':
    path = sys.argv[1] ikiwa len(sys.argv) > 1 isipokua os.getcwd()
    port = int(sys.argv[2]) ikiwa len(sys.argv) > 2 isipokua 8000
    httpd = simple_server.make_server('', port, app)
    andika("Serving {} on port {}, control-C to stop".format(path, port))
    jaribu:
        httpd.serve_forever()
    tatizo KeyboardInterrupt:
        andika("Shutting down.")
        httpd.server_close()
