"""An FTP client kundi na some helper functions.

Based on RFC 959: File Transfer Protocol (FTP), by J. Postel na J. Reynolds

Example:

>>> kutoka ftplib agiza FTP
>>> ftp = FTP('ftp.python.org') # connect to host, default port
>>> ftp.login() # default, i.e.: user anonymous, pitawd anonymous@
'230 Guest login ok, access restrictions apply.'
>>> ftp.retrlines('LIST') # list directory contents
total 9
drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 .
drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 ..
drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 bin
drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 etc
d-wxrwxr-x   2 ftp      wheel        1024 Sep  5 13:43 incoming
drwxr-xr-x   2 root     wheel        1024 Nov 17  1993 lib
drwxr-xr-x   6 1094     wheel        1024 Sep 13 19:07 pub
drwxr-xr-x   3 root     wheel        1024 Jan  3  1994 usr
-rw-r--r--   1 root     root          312 Aug  1  1994 welcome.msg
'226 Transfer complete.'
>>> ftp.quit()
'221 Goodbye.'
>>>

A nice test that reveals some of the network dialogue would be:
python ftplib.py -d localhost -l -p -l
"""

#
# Changes na improvements suggested by Steve Majewski.
# Modified by Jack to work on the mac.
# Modified by Siebren to support docstrings na PASV.
# Modified by Phil Schwartz to add storbinary na storlines callbacks.
# Modified by Giampaolo Rodola' to add TLS support.
#

agiza sys
agiza socket
kutoka socket agiza _GLOBAL_DEFAULT_TIMEOUT

__all__ = ["FTP", "error_reply", "error_temp", "error_perm", "error_proto",
           "all_errors"]

# Magic number kutoka <socket.h>
MSG_OOB = 0x1                           # Process data out of band


# The standard FTP server control port
FTP_PORT = 21
# The sizehint parameter pitaed to readline() calls
MAXLINE = 8192


# Exception ashiriad when an error ama invalid response ni received
kundi Error(Exception): pita
kundi error_reply(Error): pita          # unexpected [123]xx reply
kundi error_temp(Error): pita           # 4xx errors
kundi error_perm(Error): pita           # 5xx errors
kundi error_proto(Error): pita          # response does sio begin ukijumuisha [1-5]


# All exceptions (hopefully) that may be ashiriad here na that aren't
# (always) programming errors on our side
all_errors = (Error, OSError, EOFError)


# Line terminators (we always output CRLF, but accept any of CRLF, CR, LF)
CRLF = '\r\n'
B_CRLF = b'\r\n'

# The kundi itself
kundi FTP:

    '''An FTP client class.

    To create a connection, call the kundi using these arguments:
            host, user, pitawd, acct, timeout

    The first four arguments are all strings, na have default value ''.
    timeout must be numeric na defaults to Tupu ikiwa sio pitaed,
    meaning that no timeout will be set on any ftp socket(s)
    If a timeout ni pitaed, then this ni now the default timeout kila all ftp
    socket operations kila this instance.

    Then use self.connect() ukijumuisha optional host na port argument.

    To download a file, use ftp.retrlines('RETR ' + filename),
    ama ftp.retrbinary() ukijumuisha slightly different arguments.
    To upload a file, use ftp.storlines() ama ftp.storbinary(),
    which have an open file kama argument (see their definitions
    below kila details).
    The download/upload functions first issue appropriate TYPE
    na PORT ama PASV commands.
    '''

    debugging = 0
    host = ''
    port = FTP_PORT
    maxline = MAXLINE
    sock = Tupu
    file = Tupu
    welcome = Tupu
    pitaiveserver = 1
    encoding = "latin-1"

    # Initialization method (called by kundi instantiation).
    # Initialize host to localhost, port to standard ftp port
    # Optional arguments are host (kila connect()),
    # na user, pitawd, acct (kila login())
    eleza __init__(self, host='', user='', pitawd='', acct='',
                 timeout=_GLOBAL_DEFAULT_TIMEOUT, source_address=Tupu):
        self.source_address = source_address
        self.timeout = timeout
        ikiwa host:
            self.connect(host)
            ikiwa user:
                self.login(user, pitawd, acct)

    eleza __enter__(self):
        rudisha self

    # Context management protocol: try to quit() ikiwa active
    eleza __exit__(self, *args):
        ikiwa self.sock ni sio Tupu:
            jaribu:
                self.quit()
            tatizo (OSError, EOFError):
                pita
            mwishowe:
                ikiwa self.sock ni sio Tupu:
                    self.close()

    eleza connect(self, host='', port=0, timeout=-999, source_address=Tupu):
        '''Connect to host.  Arguments are:
         - host: hostname to connect to (string, default previous host)
         - port: port to connect to (integer, default previous port)
         - timeout: the timeout to set against the ftp socket(s)
         - source_address: a 2-tuple (host, port) kila the socket to bind
           to kama its source address before connecting.
        '''
        ikiwa host != '':
            self.host = host
        ikiwa port > 0:
            self.port = port
        ikiwa timeout != -999:
            self.timeout = timeout
        ikiwa source_address ni sio Tupu:
            self.source_address = source_address
        sys.audit("ftplib.connect", self, self.host, self.port)
        self.sock = socket.create_connection((self.host, self.port), self.timeout,
                                             source_address=self.source_address)
        self.af = self.sock.family
        self.file = self.sock.makefile('r', encoding=self.encoding)
        self.welcome = self.getresp()
        rudisha self.welcome

    eleza getwelcome(self):
        '''Get the welcome message kutoka the server.
        (this ni read na squirreled away by connect())'''
        ikiwa self.debugging:
            andika('*welcome*', self.sanitize(self.welcome))
        rudisha self.welcome

    eleza set_debuglevel(self, level):
        '''Set the debugging level.
        The required argument level means:
        0: no debugging output (default)
        1: print commands na responses but sio body text etc.
        2: also print raw lines read na sent before stripping CR/LF'''
        self.debugging = level
    debug = set_debuglevel

    eleza set_pasv(self, val):
        '''Use pitaive ama active mode kila data transfers.
        With a false argument, use the normal PORT mode,
        With a true argument, use the PASV command.'''
        self.pitaiveserver = val

    # Internal: "sanitize" a string kila printing
    eleza sanitize(self, s):
        ikiwa s[:5] kwenye {'pita ', 'PASS '}:
            i = len(s.rstrip('\r\n'))
            s = s[:5] + '*'*(i-5) + s[i:]
        rudisha repr(s)

    # Internal: send one line to the server, appending CRLF
    eleza putline(self, line):
        ikiwa '\r' kwenye line ama '\n' kwenye line:
            ashiria ValueError('an illegal newline character should sio be contained')
        sys.audit("ftplib.sendcmd", self, line)
        line = line + CRLF
        ikiwa self.debugging > 1:
            andika('*put*', self.sanitize(line))
        self.sock.sendall(line.encode(self.encoding))

    # Internal: send one command to the server (through putline())
    eleza putcmd(self, line):
        ikiwa self.debugging: andika('*cmd*', self.sanitize(line))
        self.putline(line)

    # Internal: rudisha one line kutoka the server, stripping CRLF.
    # Raise EOFError ikiwa the connection ni closed
    eleza getline(self):
        line = self.file.readline(self.maxline + 1)
        ikiwa len(line) > self.maxline:
            ashiria Error("got more than %d bytes" % self.maxline)
        ikiwa self.debugging > 1:
            andika('*get*', self.sanitize(line))
        ikiwa sio line:
            ashiria EOFError
        ikiwa line[-2:] == CRLF:
            line = line[:-2]
        lasivyo line[-1:] kwenye CRLF:
            line = line[:-1]
        rudisha line

    # Internal: get a response kutoka the server, which may possibly
    # consist of multiple lines.  Return a single string ukijumuisha no
    # trailing CRLF.  If the response consists of multiple lines,
    # these are separated by '\n' characters kwenye the string
    eleza getmultiline(self):
        line = self.getline()
        ikiwa line[3:4] == '-':
            code = line[:3]
            wakati 1:
                nextline = self.getline()
                line = line + ('\n' + nextline)
                ikiwa nextline[:3] == code na \
                        nextline[3:4] != '-':
                    koma
        rudisha line

    # Internal: get a response kutoka the server.
    # Raise various errors ikiwa the response indicates an error
    eleza getresp(self):
        resp = self.getmultiline()
        ikiwa self.debugging:
            andika('*resp*', self.sanitize(resp))
        self.lastresp = resp[:3]
        c = resp[:1]
        ikiwa c kwenye {'1', '2', '3'}:
            rudisha resp
        ikiwa c == '4':
            ashiria error_temp(resp)
        ikiwa c == '5':
            ashiria error_perm(resp)
        ashiria error_proto(resp)

    eleza voidresp(self):
        """Expect a response beginning ukijumuisha '2'."""
        resp = self.getresp()
        ikiwa resp[:1] != '2':
            ashiria error_reply(resp)
        rudisha resp

    eleza abort(self):
        '''Abort a file transfer.  Uses out-of-band data.
        This does sio follow the procedure kutoka the RFC to send Telnet
        IP na Synch; that doesn't seem to work ukijumuisha the servers I've
        tried.  Instead, just send the ABOR command kama OOB data.'''
        line = b'ABOR' + B_CRLF
        ikiwa self.debugging > 1:
            andika('*put urgent*', self.sanitize(line))
        self.sock.sendall(line, MSG_OOB)
        resp = self.getmultiline()
        ikiwa resp[:3] haiko kwenye {'426', '225', '226'}:
            ashiria error_proto(resp)
        rudisha resp

    eleza sendcmd(self, cmd):
        '''Send a command na rudisha the response.'''
        self.putcmd(cmd)
        rudisha self.getresp()

    eleza voidcmd(self, cmd):
        """Send a command na expect a response beginning ukijumuisha '2'."""
        self.putcmd(cmd)
        rudisha self.voidresp()

    eleza sendport(self, host, port):
        '''Send a PORT command ukijumuisha the current host na the given
        port number.
        '''
        hbytes = host.split('.')
        pbytes = [repr(port//256), repr(port%256)]
        bytes = hbytes + pbytes
        cmd = 'PORT ' + ','.join(bytes)
        rudisha self.voidcmd(cmd)

    eleza sendeprt(self, host, port):
        '''Send an EPRT command ukijumuisha the current host na the given port number.'''
        af = 0
        ikiwa self.af == socket.AF_INET:
            af = 1
        ikiwa self.af == socket.AF_INET6:
            af = 2
        ikiwa af == 0:
            ashiria error_proto('unsupported address family')
        fields = ['', repr(af), host, repr(port), '']
        cmd = 'EPRT ' + '|'.join(fields)
        rudisha self.voidcmd(cmd)

    eleza makeport(self):
        '''Create a new socket na send a PORT command kila it.'''
        sock = socket.create_server(("", 0), family=self.af, backlog=1)
        port = sock.getsockname()[1] # Get proper port
        host = self.sock.getsockname()[0] # Get proper host
        ikiwa self.af == socket.AF_INET:
            resp = self.sendport(host, port)
        isipokua:
            resp = self.sendeprt(host, port)
        ikiwa self.timeout ni sio _GLOBAL_DEFAULT_TIMEOUT:
            sock.settimeout(self.timeout)
        rudisha sock

    eleza makepasv(self):
        ikiwa self.af == socket.AF_INET:
            host, port = parse227(self.sendcmd('PASV'))
        isipokua:
            host, port = parse229(self.sendcmd('EPSV'), self.sock.getpeername())
        rudisha host, port

    eleza ntransfercmd(self, cmd, rest=Tupu):
        """Initiate a transfer over the data connection.

        If the transfer ni active, send a port command na the
        transfer command, na accept the connection.  If the server is
        pitaive, send a pasv command, connect to it, na start the
        transfer command.  Either way, rudisha the socket kila the
        connection na the expected size of the transfer.  The
        expected size may be Tupu ikiwa it could sio be determined.

        Optional `rest' argument can be a string that ni sent kama the
        argument to a REST command.  This ni essentially a server
        marker used to tell the server to skip over any data up to the
        given marker.
        """
        size = Tupu
        ikiwa self.pitaiveserver:
            host, port = self.makepasv()
            conn = socket.create_connection((host, port), self.timeout,
                                            source_address=self.source_address)
            jaribu:
                ikiwa rest ni sio Tupu:
                    self.sendcmd("REST %s" % rest)
                resp = self.sendcmd(cmd)
                # Some servers apparently send a 200 reply to
                # a LIST ama STOR command, before the 150 reply
                # (and way before the 226 reply). This seems to
                # be kwenye violation of the protocol (which only allows
                # 1xx ama error messages kila LIST), so we just discard
                # this response.
                ikiwa resp[0] == '2':
                    resp = self.getresp()
                ikiwa resp[0] != '1':
                    ashiria error_reply(resp)
            tatizo:
                conn.close()
                ashiria
        isipokua:
            ukijumuisha self.makeport() kama sock:
                ikiwa rest ni sio Tupu:
                    self.sendcmd("REST %s" % rest)
                resp = self.sendcmd(cmd)
                # See above.
                ikiwa resp[0] == '2':
                    resp = self.getresp()
                ikiwa resp[0] != '1':
                    ashiria error_reply(resp)
                conn, sockaddr = sock.accept()
                ikiwa self.timeout ni sio _GLOBAL_DEFAULT_TIMEOUT:
                    conn.settimeout(self.timeout)
        ikiwa resp[:3] == '150':
            # this ni conditional kwenye case we received a 125
            size = parse150(resp)
        rudisha conn, size

    eleza transfercmd(self, cmd, rest=Tupu):
        """Like ntransfercmd() but rudishas only the socket."""
        rudisha self.ntransfercmd(cmd, rest)[0]

    eleza login(self, user = '', pitawd = '', acct = ''):
        '''Login, default anonymous.'''
        ikiwa sio user:
            user = 'anonymous'
        ikiwa sio pitawd:
            pitawd = ''
        ikiwa sio acct:
            acct = ''
        ikiwa user == 'anonymous' na pitawd kwenye {'', '-'}:
            # If there ni no anonymous ftp pitaword specified
            # then we'll just use anonymous@
            # We don't send any other thing because:
            # - We want to remain anonymous
            # - We want to stop SPAM
            # - We don't want to let ftp sites to discriminate by the user,
            #   host ama country.
            pitawd = pitawd + 'anonymous@'
        resp = self.sendcmd('USER ' + user)
        ikiwa resp[0] == '3':
            resp = self.sendcmd('PASS ' + pitawd)
        ikiwa resp[0] == '3':
            resp = self.sendcmd('ACCT ' + acct)
        ikiwa resp[0] != '2':
            ashiria error_reply(resp)
        rudisha resp

    eleza retrbinary(self, cmd, callback, blocksize=8192, rest=Tupu):
        """Retrieve data kwenye binary mode.  A new port ni created kila you.

        Args:
          cmd: A RETR command.
          callback: A single parameter callable to be called on each
                    block of data read.
          blocksize: The maximum number of bytes to read kutoka the
                     socket at one time.  [default: 8192]
          rest: Passed to transfercmd().  [default: Tupu]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE I')
        ukijumuisha self.transfercmd(cmd, rest) kama conn:
            wakati 1:
                data = conn.recv(blocksize)
                ikiwa sio data:
                    koma
                callback(data)
            # shutdown ssl layer
            ikiwa _SSLSocket ni sio Tupu na isinstance(conn, _SSLSocket):
                conn.unwrap()
        rudisha self.voidresp()

    eleza retrlines(self, cmd, callback = Tupu):
        """Retrieve data kwenye line mode.  A new port ni created kila you.

        Args:
          cmd: A RETR, LIST, ama NLST command.
          callback: An optional single parameter callable that ni called
                    kila each line ukijumuisha the trailing CRLF stripped.
                    [default: print_line()]

        Returns:
          The response code.
        """
        ikiwa callback ni Tupu:
            callback = print_line
        resp = self.sendcmd('TYPE A')
        ukijumuisha self.transfercmd(cmd) kama conn, \
                 conn.makefile('r', encoding=self.encoding) kama fp:
            wakati 1:
                line = fp.readline(self.maxline + 1)
                ikiwa len(line) > self.maxline:
                    ashiria Error("got more than %d bytes" % self.maxline)
                ikiwa self.debugging > 2:
                    andika('*retr*', repr(line))
                ikiwa sio line:
                    koma
                ikiwa line[-2:] == CRLF:
                    line = line[:-2]
                lasivyo line[-1:] == '\n':
                    line = line[:-1]
                callback(line)
            # shutdown ssl layer
            ikiwa _SSLSocket ni sio Tupu na isinstance(conn, _SSLSocket):
                conn.unwrap()
        rudisha self.voidresp()

    eleza storbinary(self, cmd, fp, blocksize=8192, callback=Tupu, rest=Tupu):
        """Store a file kwenye binary mode.  A new port ni created kila you.

        Args:
          cmd: A STOR command.
          fp: A file-like object ukijumuisha a read(num_bytes) method.
          blocksize: The maximum data size to read kutoka fp na send over
                     the connection at once.  [default: 8192]
          callback: An optional single parameter callable that ni called on
                    each block of data after it ni sent.  [default: Tupu]
          rest: Passed to transfercmd().  [default: Tupu]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE I')
        ukijumuisha self.transfercmd(cmd, rest) kama conn:
            wakati 1:
                buf = fp.read(blocksize)
                ikiwa sio buf:
                    koma
                conn.sendall(buf)
                ikiwa callback:
                    callback(buf)
            # shutdown ssl layer
            ikiwa _SSLSocket ni sio Tupu na isinstance(conn, _SSLSocket):
                conn.unwrap()
        rudisha self.voidresp()

    eleza storlines(self, cmd, fp, callback=Tupu):
        """Store a file kwenye line mode.  A new port ni created kila you.

        Args:
          cmd: A STOR command.
          fp: A file-like object ukijumuisha a readline() method.
          callback: An optional single parameter callable that ni called on
                    each line after it ni sent.  [default: Tupu]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE A')
        ukijumuisha self.transfercmd(cmd) kama conn:
            wakati 1:
                buf = fp.readline(self.maxline + 1)
                ikiwa len(buf) > self.maxline:
                    ashiria Error("got more than %d bytes" % self.maxline)
                ikiwa sio buf:
                    koma
                ikiwa buf[-2:] != B_CRLF:
                    ikiwa buf[-1] kwenye B_CRLF: buf = buf[:-1]
                    buf = buf + B_CRLF
                conn.sendall(buf)
                ikiwa callback:
                    callback(buf)
            # shutdown ssl layer
            ikiwa _SSLSocket ni sio Tupu na isinstance(conn, _SSLSocket):
                conn.unwrap()
        rudisha self.voidresp()

    eleza acct(self, pitaword):
        '''Send new account name.'''
        cmd = 'ACCT ' + pitaword
        rudisha self.voidcmd(cmd)

    eleza nlst(self, *args):
        '''Return a list of files kwenye a given directory (default the current).'''
        cmd = 'NLST'
        kila arg kwenye args:
            cmd = cmd + (' ' + arg)
        files = []
        self.retrlines(cmd, files.append)
        rudisha files

    eleza dir(self, *args):
        '''List a directory kwenye long form.
        By default list current directory to stdout.
        Optional last argument ni callback function; all
        non-empty arguments before it are concatenated to the
        LIST command.  (This *should* only be used kila a pathname.)'''
        cmd = 'LIST'
        func = Tupu
        ikiwa args[-1:] na type(args[-1]) != type(''):
            args, func = args[:-1], args[-1]
        kila arg kwenye args:
            ikiwa arg:
                cmd = cmd + (' ' + arg)
        self.retrlines(cmd, func)

    eleza mlsd(self, path="", facts=[]):
        '''List a directory kwenye a standardized format by using MLSD
        command (RFC-3659). If path ni omitted the current directory
        ni assumed. "facts" ni a list of strings representing the type
        of information desired (e.g. ["type", "size", "perm"]).

        Return a generator object tumaing a tuple of two elements
        kila every file found kwenye path.
        First element ni the file name, the second one ni a dictionary
        including a variable number of "facts" depending on the server
        na whether "facts" argument has been provided.
        '''
        ikiwa facts:
            self.sendcmd("OPTS MLST " + ";".join(facts) + ";")
        ikiwa path:
            cmd = "MLSD %s" % path
        isipokua:
            cmd = "MLSD"
        lines = []
        self.retrlines(cmd, lines.append)
        kila line kwenye lines:
            facts_found, _, name = line.rstrip(CRLF).partition(' ')
            entry = {}
            kila fact kwenye facts_found[:-1].split(";"):
                key, _, value = fact.partition("=")
                entry[key.lower()] = value
            tuma (name, entry)

    eleza rename(self, kutokaname, toname):
        '''Rename a file.'''
        resp = self.sendcmd('RNFR ' + kutokaname)
        ikiwa resp[0] != '3':
            ashiria error_reply(resp)
        rudisha self.voidcmd('RNTO ' + toname)

    eleza delete(self, filename):
        '''Delete a file.'''
        resp = self.sendcmd('DELE ' + filename)
        ikiwa resp[:3] kwenye {'250', '200'}:
            rudisha resp
        isipokua:
            ashiria error_reply(resp)

    eleza cwd(self, dirname):
        '''Change to a directory.'''
        ikiwa dirname == '..':
            jaribu:
                rudisha self.voidcmd('CDUP')
            tatizo error_perm kama msg:
                ikiwa msg.args[0][:3] != '500':
                    ashiria
        lasivyo dirname == '':
            dirname = '.'  # does nothing, but could rudisha error
        cmd = 'CWD ' + dirname
        rudisha self.voidcmd(cmd)

    eleza size(self, filename):
        '''Retrieve the size of a file.'''
        # The SIZE command ni defined kwenye RFC-3659
        resp = self.sendcmd('SIZE ' + filename)
        ikiwa resp[:3] == '213':
            s = resp[3:].strip()
            rudisha int(s)

    eleza mkd(self, dirname):
        '''Make a directory, rudisha its full pathname.'''
        resp = self.voidcmd('MKD ' + dirname)
        # fix around non-compliant implementations such kama IIS shipped
        # ukijumuisha Windows server 2003
        ikiwa sio resp.startswith('257'):
            rudisha ''
        rudisha parse257(resp)

    eleza rmd(self, dirname):
        '''Remove a directory.'''
        rudisha self.voidcmd('RMD ' + dirname)

    eleza pwd(self):
        '''Return current working directory.'''
        resp = self.voidcmd('PWD')
        # fix around non-compliant implementations such kama IIS shipped
        # ukijumuisha Windows server 2003
        ikiwa sio resp.startswith('257'):
            rudisha ''
        rudisha parse257(resp)

    eleza quit(self):
        '''Quit, na close the connection.'''
        resp = self.voidcmd('QUIT')
        self.close()
        rudisha resp

    eleza close(self):
        '''Close the connection without assuming anything about it.'''
        jaribu:
            file = self.file
            self.file = Tupu
            ikiwa file ni sio Tupu:
                file.close()
        mwishowe:
            sock = self.sock
            self.sock = Tupu
            ikiwa sock ni sio Tupu:
                sock.close()

jaribu:
    agiza ssl
tatizo ImportError:
    _SSLSocket = Tupu
isipokua:
    _SSLSocket = ssl.SSLSocket

    kundi FTP_TLS(FTP):
        '''A FTP subkundi which adds TLS support to FTP kama described
        kwenye RFC-4217.

        Connect kama usual to port 21 implicitly securing the FTP control
        connection before authenticating.

        Securing the data connection requires user to explicitly ask
        kila it by calling prot_p() method.

        Usage example:
        >>> kutoka ftplib agiza FTP_TLS
        >>> ftps = FTP_TLS('ftp.python.org')
        >>> ftps.login()  # login anonymously previously securing control channel
        '230 Guest login ok, access restrictions apply.'
        >>> ftps.prot_p()  # switch to secure data connection
        '200 Protection level set to P'
        >>> ftps.retrlines('LIST')  # list directory content securely
        total 9
        drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 .
        drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 ..
        drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 bin
        drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 etc
        d-wxrwxr-x   2 ftp      wheel        1024 Sep  5 13:43 incoming
        drwxr-xr-x   2 root     wheel        1024 Nov 17  1993 lib
        drwxr-xr-x   6 1094     wheel        1024 Sep 13 19:07 pub
        drwxr-xr-x   3 root     wheel        1024 Jan  3  1994 usr
        -rw-r--r--   1 root     root          312 Aug  1  1994 welcome.msg
        '226 Transfer complete.'
        >>> ftps.quit()
        '221 Goodbye.'
        >>>
        '''
        ssl_version = ssl.PROTOCOL_TLS_CLIENT

        eleza __init__(self, host='', user='', pitawd='', acct='', keyfile=Tupu,
                     certfile=Tupu, context=Tupu,
                     timeout=_GLOBAL_DEFAULT_TIMEOUT, source_address=Tupu):
            ikiwa context ni sio Tupu na keyfile ni sio Tupu:
                ashiria ValueError("context na keyfile arguments are mutually "
                                 "exclusive")
            ikiwa context ni sio Tupu na certfile ni sio Tupu:
                ashiria ValueError("context na certfile arguments are mutually "
                                 "exclusive")
            ikiwa keyfile ni sio Tupu ama certfile ni sio Tupu:
                agiza warnings
                warnings.warn("keyfile na certfile are deprecated, use a "
                              "custom context instead", DeprecationWarning, 2)
            self.keyfile = keyfile
            self.certfile = certfile
            ikiwa context ni Tupu:
                context = ssl._create_stdlib_context(self.ssl_version,
                                                     certfile=certfile,
                                                     keyfile=keyfile)
            self.context = context
            self._prot_p = Uongo
            FTP.__init__(self, host, user, pitawd, acct, timeout, source_address)

        eleza login(self, user='', pitawd='', acct='', secure=Kweli):
            ikiwa secure na sio isinstance(self.sock, ssl.SSLSocket):
                self.auth()
            rudisha FTP.login(self, user, pitawd, acct)

        eleza auth(self):
            '''Set up secure control connection by using TLS/SSL.'''
            ikiwa isinstance(self.sock, ssl.SSLSocket):
                ashiria ValueError("Already using TLS")
            ikiwa self.ssl_version >= ssl.PROTOCOL_TLS:
                resp = self.voidcmd('AUTH TLS')
            isipokua:
                resp = self.voidcmd('AUTH SSL')
            self.sock = self.context.wrap_socket(self.sock,
                                                 server_hostname=self.host)
            self.file = self.sock.makefile(mode='r', encoding=self.encoding)
            rudisha resp

        eleza ccc(self):
            '''Switch back to a clear-text control connection.'''
            ikiwa sio isinstance(self.sock, ssl.SSLSocket):
                ashiria ValueError("not using TLS")
            resp = self.voidcmd('CCC')
            self.sock = self.sock.unwrap()
            rudisha resp

        eleza prot_p(self):
            '''Set up secure data connection.'''
            # PROT defines whether ama sio the data channel ni to be protected.
            # Though RFC-2228 defines four possible protection levels,
            # RFC-4217 only recommends two, Clear na Private.
            # Clear (PROT C) means that no security ni to be used on the
            # data-channel, Private (PROT P) means that the data-channel
            # should be protected by TLS.
            # PBSZ command MUST still be issued, but must have a parameter of
            # '0' to indicate that no buffering ni taking place na the data
            # connection should sio be encapsulated.
            self.voidcmd('PBSZ 0')
            resp = self.voidcmd('PROT P')
            self._prot_p = Kweli
            rudisha resp

        eleza prot_c(self):
            '''Set up clear text data connection.'''
            resp = self.voidcmd('PROT C')
            self._prot_p = Uongo
            rudisha resp

        # --- Overridden FTP methods

        eleza ntransfercmd(self, cmd, rest=Tupu):
            conn, size = FTP.ntransfercmd(self, cmd, rest)
            ikiwa self._prot_p:
                conn = self.context.wrap_socket(conn,
                                                server_hostname=self.host)
            rudisha conn, size

        eleza abort(self):
            # overridden kama we can't pita MSG_OOB flag to sendall()
            line = b'ABOR' + B_CRLF
            self.sock.sendall(line)
            resp = self.getmultiline()
            ikiwa resp[:3] haiko kwenye {'426', '225', '226'}:
                ashiria error_proto(resp)
            rudisha resp

    __all__.append('FTP_TLS')
    all_errors = (Error, OSError, EOFError, ssl.SSLError)


_150_re = Tupu

eleza parse150(resp):
    '''Parse the '150' response kila a RETR request.
    Returns the expected transfer size ama Tupu; size ni sio guaranteed to
    be present kwenye the 150 message.
    '''
    ikiwa resp[:3] != '150':
        ashiria error_reply(resp)
    global _150_re
    ikiwa _150_re ni Tupu:
        agiza re
        _150_re = re.compile(
            r"150 .* \((\d+) bytes\)", re.IGNORECASE | re.ASCII)
    m = _150_re.match(resp)
    ikiwa sio m:
        rudisha Tupu
    rudisha int(m.group(1))


_227_re = Tupu

eleza parse227(resp):
    '''Parse the '227' response kila a PASV request.
    Raises error_proto ikiwa it does sio contain '(h1,h2,h3,h4,p1,p2)'
    Return ('host.addr.as.numbers', port#) tuple.'''

    ikiwa resp[:3] != '227':
        ashiria error_reply(resp)
    global _227_re
    ikiwa _227_re ni Tupu:
        agiza re
        _227_re = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', re.ASCII)
    m = _227_re.search(resp)
    ikiwa sio m:
        ashiria error_proto(resp)
    numbers = m.groups()
    host = '.'.join(numbers[:4])
    port = (int(numbers[4]) << 8) + int(numbers[5])
    rudisha host, port


eleza parse229(resp, peer):
    '''Parse the '229' response kila an EPSV request.
    Raises error_proto ikiwa it does sio contain '(|||port|)'
    Return ('host.addr.as.numbers', port#) tuple.'''

    ikiwa resp[:3] != '229':
        ashiria error_reply(resp)
    left = resp.find('(')
    ikiwa left < 0: ashiria error_proto(resp)
    right = resp.find(')', left + 1)
    ikiwa right < 0:
        ashiria error_proto(resp) # should contain '(|||port|)'
    ikiwa resp[left + 1] != resp[right - 1]:
        ashiria error_proto(resp)
    parts = resp[left + 1:right].split(resp[left+1])
    ikiwa len(parts) != 5:
        ashiria error_proto(resp)
    host = peer[0]
    port = int(parts[3])
    rudisha host, port


eleza parse257(resp):
    '''Parse the '257' response kila a MKD ama PWD request.
    This ni a response to a MKD ama PWD request: a directory name.
    Returns the directoryname kwenye the 257 reply.'''

    ikiwa resp[:3] != '257':
        ashiria error_reply(resp)
    ikiwa resp[3:5] != ' "':
        rudisha '' # Not compliant to RFC 959, but UNIX ftpd does this
    dirname = ''
    i = 5
    n = len(resp)
    wakati i < n:
        c = resp[i]
        i = i+1
        ikiwa c == '"':
            ikiwa i >= n ama resp[i] != '"':
                koma
            i = i+1
        dirname = dirname + c
    rudisha dirname


eleza print_line(line):
    '''Default retrlines callback to print a line.'''
    andika(line)


eleza ftpcp(source, sourcename, target, targetname = '', type = 'I'):
    '''Copy file kutoka one FTP-instance to another.'''
    ikiwa sio targetname:
        targetname = sourcename
    type = 'TYPE ' + type
    source.voidcmd(type)
    target.voidcmd(type)
    sourcehost, sourceport = parse227(source.sendcmd('PASV'))
    target.sendport(sourcehost, sourceport)
    # RFC 959: the user must "listen" [...] BEFORE sending the
    # transfer request.
    # So: STOR before RETR, because here the target ni a "user".
    treply = target.sendcmd('STOR ' + targetname)
    ikiwa treply[:3] haiko kwenye {'125', '150'}:
        ashiria error_proto  # RFC 959
    sreply = source.sendcmd('RETR ' + sourcename)
    ikiwa sreply[:3] haiko kwenye {'125', '150'}:
        ashiria error_proto  # RFC 959
    source.voidresp()
    target.voidresp()


eleza test():
    '''Test program.
    Usage: ftp [-d] [-r[file]] host [-l[dir]] [-d[dir]] [-p] [file] ...

    -d dir
    -l list
    -p pitaword
    '''

    ikiwa len(sys.argv) < 2:
        andika(test.__doc__)
        sys.exit(0)

    agiza netrc

    debugging = 0
    rcfile = Tupu
    wakati sys.argv[1] == '-d':
        debugging = debugging+1
        toa sys.argv[1]
    ikiwa sys.argv[1][:2] == '-r':
        # get name of alternate ~/.netrc file:
        rcfile = sys.argv[1][2:]
        toa sys.argv[1]
    host = sys.argv[1]
    ftp = FTP(host)
    ftp.set_debuglevel(debugging)
    userid = pitawd = acct = ''
    jaribu:
        netrcobj = netrc.netrc(rcfile)
    tatizo OSError:
        ikiwa rcfile ni sio Tupu:
            sys.stderr.write("Could sio open account file"
                             " -- using anonymous login.")
    isipokua:
        jaribu:
            userid, acct, pitawd = netrcobj.authenticators(host)
        tatizo KeyError:
            # no account kila host
            sys.stderr.write(
                    "No account -- using anonymous login.")
    ftp.login(userid, pitawd, acct)
    kila file kwenye sys.argv[2:]:
        ikiwa file[:2] == '-l':
            ftp.dir(file[2:])
        lasivyo file[:2] == '-d':
            cmd = 'CWD'
            ikiwa file[2:]: cmd = cmd + ' ' + file[2:]
            resp = ftp.sendcmd(cmd)
        lasivyo file == '-p':
            ftp.set_pasv(sio ftp.pitaiveserver)
        isipokua:
            ftp.retrbinary('RETR ' + file, \
                           sys.stdout.write, 1024)
    ftp.quit()


ikiwa __name__ == '__main__':
    test()
