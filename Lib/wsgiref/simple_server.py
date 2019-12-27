"""BaseHTTPServer that implements the Python WSGI protocol (PEP 3333)

This is both an example of how WSGI can be implemented, and a basis for running
simple web applications on a local machine, such as might be done when testing
or debugging an application.  It has not been reviewed for security issues,
however, and we strongly recommend that you use a "real" web server for
production use.

For example usage, see the 'ikiwa __name__=="__main__"' block at the end of the
module.  See also the BaseHTTPServer module docs for other API information.
"""

kutoka http.server agiza BaseHTTPRequestHandler, HTTPServer
agiza sys
agiza urllib.parse
kutoka wsgiref.handlers agiza SimpleHandler
kutoka platform agiza python_implementation

__version__ = "0.2"
__all__ = ['WSGIServer', 'WSGIRequestHandler', 'demo_app', 'make_server']


server_version = "WSGIServer/" + __version__
sys_version = python_implementation() + "/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version


kundi ServerHandler(SimpleHandler):

    server_software = software_version

    eleza close(self):
        try:
            self.request_handler.log_request(
                self.status.split(' ',1)[0], self.bytes_sent
            )
        finally:
            SimpleHandler.close(self)



kundi WSGIServer(HTTPServer):

    """BaseHTTPServer that implements the Python WSGI protocol"""

    application = None

    eleza server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    eleza setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''

    eleza get_app(self):
        rudisha self.application

    eleza set_app(self,application):
        self.application = application



kundi WSGIRequestHandler(BaseHTTPRequestHandler):

    server_version = "WSGIServer/" + __version__

    eleza get_environ(self):
        env = self.server.base_environ.copy()
        env['SERVER_PROTOCOL'] = self.request_version
        env['SERVER_SOFTWARE'] = self.server_version
        env['REQUEST_METHOD'] = self.command
        ikiwa '?' in self.path:
            path,query = self.path.split('?',1)
        else:
            path,query = self.path,''

        env['PATH_INFO'] = urllib.parse.unquote(path, 'iso-8859-1')
        env['QUERY_STRING'] = query

        host = self.address_string()
        ikiwa host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]

        ikiwa self.headers.get('content-type') is None:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        else:
            env['CONTENT_TYPE'] = self.headers['content-type']

        length = self.headers.get('content-length')
        ikiwa length:
            env['CONTENT_LENGTH'] = length

        for k, v in self.headers.items():
            k=k.replace('-','_').upper(); v=v.strip()
            ikiwa k in env:
                continue                    # skip content length, type,etc.
            ikiwa 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v
        rudisha env

    eleza get_stderr(self):
        rudisha sys.stderr

    eleza handle(self):
        """Handle a single HTTP request"""

        self.raw_requestline = self.rfile.readline(65537)
        ikiwa len(self.raw_requestline) > 65536:
            self.requestline = ''
            self.request_version = ''
            self.command = ''
            self.send_error(414)
            return

        ikiwa not self.parse_request(): # An error code has been sent, just exit
            return

        handler = ServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ(),
            multithread=False,
        )
        handler.request_handler = self      # backpointer for logging
        handler.run(self.server.get_app())



eleza demo_app(environ,start_response):
    kutoka io agiza StringIO
    stdout = StringIO()
    andika("Hello world!", file=stdout)
    andika(file=stdout)
    h = sorted(environ.items())
    for k,v in h:
        andika(k,'=',repr(v), file=stdout)
    start_response("200 OK", [('Content-Type','text/plain; charset=utf-8')])
    rudisha [stdout.getvalue().encode("utf-8")]


eleza make_server(
    host, port, app, server_class=WSGIServer, handler_class=WSGIRequestHandler
):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    server = server_class((host, port), handler_class)
    server.set_app(app)
    rudisha server


ikiwa __name__ == '__main__':
    with make_server('', 8000, demo_app) as httpd:
        sa = httpd.socket.getsockname()
        andika("Serving HTTP on", sa[0], "port", sa[1], "...")
        agiza webbrowser
        webbrowser.open('http://localhost:8000/xyz?abc')
        httpd.handle_request()  # serve one request, then exit
