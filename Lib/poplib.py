"""A POP3 client class.

Based on the J. Myers POP3 draft, Jan. 96
"""

# Author: David Ascher <david_ascher@brown.edu>
#         [heavily stealing kutoka nntplib.py]
# Updated: Piers Lauder <piers@cs.su.oz.au> [Jul '97]
# String method conversion and test jig improvements by ESR, February 2001.
# Added the POP3_SSL class. Methods loosely based on IMAP_SSL. Hector Urtubia <urtubia@mrbook.org> Aug 2003

# Example (see the test function at the end of this file)

# Imports

agiza errno
agiza re
agiza socket
agiza sys

try:
    agiza ssl
    HAVE_SSL = True
except ImportError:
    HAVE_SSL = False

__all__ = ["POP3","error_proto"]

# Exception raised when an error or invalid response is received:

kundi error_proto(Exception): pass

# Standard Port
POP3_PORT = 110

# POP SSL PORT
POP3_SSL_PORT = 995

# Line terminators (we always output CRLF, but accept any of CRLF, LFCR, LF)
CR = b'\r'
LF = b'\n'
CRLF = CR+LF

# maximal line length when calling readline(). This is to prevent
# reading arbitrary length lines. RFC 1939 limits POP3 line length to
# 512 characters, including CRLF. We have selected 2048 just to be on
# the safe side.
_MAXLINE = 2048


kundi POP3:

    """This kundi supports both the minimal and optional command sets.
    Arguments can be strings or integers (where appropriate)
    (e.g.: retr(1) and retr('1') both work equally well.

    Minimal Command Set:
            USER name               user(name)
            PASS string             pass_(string)
            STAT                    stat()
            LIST [msg]              list(msg = None)
            RETR msg                retr(msg)
            DELE msg                dele(msg)
            NOOP                    noop()
            RSET                    rset()
            QUIT                    quit()

    Optional Commands (some servers support these):
            RPOP name               rpop(name)
            APOP name digest        apop(name, digest)
            TOP msg n               top(msg, n)
            UIDL [msg]              uidl(msg = None)
            CAPA                    capa()
            STLS                    stls()
            UTF8                    utf8()

    Raises one exception: 'error_proto'.

    Instantiate with:
            POP3(hostname, port=110)

    NB:     the POP protocol locks the mailbox kutoka user
            authorization until QUIT, so be sure to get in, suck
            the messages, and quit, each time you access the
            mailbox.

            POP is a line-based protocol, which means large mail
            messages consume lots of python cycles reading them
            line-by-line.

            If it's available on your mail server, use IMAP4
            instead, it doesn't suffer kutoka the two problems
            above.
    """

    encoding = 'UTF-8'

    eleza __init__(self, host, port=POP3_PORT,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self._tls_established = False
        sys.audit("poplib.connect", self, host, port)
        self.sock = self._create_socket(timeout)
        self.file = self.sock.makefile('rb')
        self._debugging = 0
        self.welcome = self._getresp()

    eleza _create_socket(self, timeout):
        rudisha socket.create_connection((self.host, self.port), timeout)

    eleza _putline(self, line):
        ikiwa self._debugging > 1: andika('*put*', repr(line))
        sys.audit("poplib.putline", self, line)
        self.sock.sendall(line + CRLF)


    # Internal: send one command to the server (through _putline())

    eleza _putcmd(self, line):
        ikiwa self._debugging: andika('*cmd*', repr(line))
        line = bytes(line, self.encoding)
        self._putline(line)


    # Internal: rudisha one line kutoka the server, stripping CRLF.
    # This is where all the CPU time of this module is consumed.
    # Raise error_proto('-ERR EOF') ikiwa the connection is closed.

    eleza _getline(self):
        line = self.file.readline(_MAXLINE + 1)
        ikiwa len(line) > _MAXLINE:
            raise error_proto('line too long')

        ikiwa self._debugging > 1: andika('*get*', repr(line))
        ikiwa not line: raise error_proto('-ERR EOF')
        octets = len(line)
        # server can send any combination of CR & LF
        # however, 'readline()' returns lines ending in LF
        # so only possibilities are ...LF, ...CRLF, CR...LF
        ikiwa line[-2:] == CRLF:
            rudisha line[:-2], octets
        ikiwa line[:1] == CR:
            rudisha line[1:-1], octets
        rudisha line[:-1], octets


    # Internal: get a response kutoka the server.
    # Raise 'error_proto' ikiwa the response doesn't start with '+'.

    eleza _getresp(self):
        resp, o = self._getline()
        ikiwa self._debugging > 1: andika('*resp*', repr(resp))
        ikiwa not resp.startswith(b'+'):
            raise error_proto(resp)
        rudisha resp


    # Internal: get a response plus following text kutoka the server.

    eleza _getlongresp(self):
        resp = self._getresp()
        list = []; octets = 0
        line, o = self._getline()
        while line != b'.':
            ikiwa line.startswith(b'..'):
                o = o-1
                line = line[1:]
            octets = octets + o
            list.append(line)
            line, o = self._getline()
        rudisha resp, list, octets


    # Internal: send a command and get the response

    eleza _shortcmd(self, line):
        self._putcmd(line)
        rudisha self._getresp()


    # Internal: send a command and get the response plus following text

    eleza _longcmd(self, line):
        self._putcmd(line)
        rudisha self._getlongresp()


    # These can be useful:

    eleza getwelcome(self):
        rudisha self.welcome


    eleza set_debuglevel(self, level):
        self._debugging = level


    # Here are all the POP commands:

    eleza user(self, user):
        """Send user name, rudisha response

        (should indicate password required).
        """
        rudisha self._shortcmd('USER %s' % user)


    eleza pass_(self, pswd):
        """Send password, rudisha response

        (response includes message count, mailbox size).

        NB: mailbox is locked by server kutoka here to 'quit()'
        """
        rudisha self._shortcmd('PASS %s' % pswd)


    eleza stat(self):
        """Get mailbox status.

        Result is tuple of 2 ints (message count, mailbox size)
        """
        retval = self._shortcmd('STAT')
        rets = retval.split()
        ikiwa self._debugging: andika('*stat*', repr(rets))
        numMessages = int(rets[1])
        sizeMessages = int(rets[2])
        rudisha (numMessages, sizeMessages)


    eleza list(self, which=None):
        """Request listing, rudisha result.

        Result without a message number argument is in form
        ['response', ['mesg_num octets', ...], octets].

        Result when a message number argument is given is a
        single response: the "scan listing" for that message.
        """
        ikiwa which is not None:
            rudisha self._shortcmd('LIST %s' % which)
        rudisha self._longcmd('LIST')


    eleza retr(self, which):
        """Retrieve whole message number 'which'.

        Result is in form ['response', ['line', ...], octets].
        """
        rudisha self._longcmd('RETR %s' % which)


    eleza dele(self, which):
        """Delete message number 'which'.

        Result is 'response'.
        """
        rudisha self._shortcmd('DELE %s' % which)


    eleza noop(self):
        """Does nothing.

        One supposes the response indicates the server is alive.
        """
        rudisha self._shortcmd('NOOP')


    eleza rset(self):
        """Unmark all messages marked for deletion."""
        rudisha self._shortcmd('RSET')


    eleza quit(self):
        """Signoff: commit changes on server, unlock mailbox, close connection."""
        resp = self._shortcmd('QUIT')
        self.close()
        rudisha resp

    eleza close(self):
        """Close the connection without assuming anything about it."""
        try:
            file = self.file
            self.file = None
            ikiwa file is not None:
                file.close()
        finally:
            sock = self.sock
            self.sock = None
            ikiwa sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError as exc:
                    # The server might already have closed the connection.
                    # On Windows, this may result in WSAEINVAL (error 10022):
                    # An invalid operation was attempted.
                    ikiwa (exc.errno != errno.ENOTCONN
                       and getattr(exc, 'winerror', 0) != 10022):
                        raise
                finally:
                    sock.close()

    #__del__ = quit


    # optional commands:

    eleza rpop(self, user):
        """Not sure what this does."""
        rudisha self._shortcmd('RPOP %s' % user)


    timestamp = re.compile(br'\+OK.[^<]*(<.*>)')

    eleza apop(self, user, password):
        """Authorisation

        - only possible ikiwa server has supplied a timestamp in initial greeting.

        Args:
                user     - mailbox user;
                password - mailbox password.

        NB: mailbox is locked by server kutoka here to 'quit()'
        """
        secret = bytes(password, self.encoding)
        m = self.timestamp.match(self.welcome)
        ikiwa not m:
            raise error_proto('-ERR APOP not supported by server')
        agiza hashlib
        digest = m.group(1)+secret
        digest = hashlib.md5(digest).hexdigest()
        rudisha self._shortcmd('APOP %s %s' % (user, digest))


    eleza top(self, which, howmuch):
        """Retrieve message header of message number 'which'
        and first 'howmuch' lines of message body.

        Result is in form ['response', ['line', ...], octets].
        """
        rudisha self._longcmd('TOP %s %s' % (which, howmuch))


    eleza uidl(self, which=None):
        """Return message digest (unique id) list.

        If 'which', result contains unique id for that message
        in the form 'response mesgnum uid', otherwise result is
        the list ['response', ['mesgnum uid', ...], octets]
        """
        ikiwa which is not None:
            rudisha self._shortcmd('UIDL %s' % which)
        rudisha self._longcmd('UIDL')


    eleza utf8(self):
        """Try to enter UTF-8 mode (see RFC 6856). Returns server response.
        """
        rudisha self._shortcmd('UTF8')


    eleza capa(self):
        """Return server capabilities (RFC 2449) as a dictionary
        >>> c=poplib.POP3('localhost')
        >>> c.capa()
        {'IMPLEMENTATION': ['Cyrus', 'POP3', 'server', 'v2.2.12'],
         'TOP': [], 'LOGIN-DELAY': ['0'], 'AUTH-RESP-CODE': [],
         'EXPIRE': ['NEVER'], 'USER': [], 'STLS': [], 'PIPELINING': [],
         'UIDL': [], 'RESP-CODES': []}
        >>>

        Really, according to RFC 2449, the cyrus folks should avoid
        having the implementation split into multiple arguments...
        """
        eleza _parsecap(line):
            lst = line.decode('ascii').split()
            rudisha lst[0], lst[1:]

        caps = {}
        try:
            resp = self._longcmd('CAPA')
            rawcaps = resp[1]
            for capline in rawcaps:
                capnm, capargs = _parsecap(capline)
                caps[capnm] = capargs
        except error_proto as _err:
            raise error_proto('-ERR CAPA not supported by server')
        rudisha caps


    eleza stls(self, context=None):
        """Start a TLS session on the active connection as specified in RFC 2595.

                context - a ssl.SSLContext
        """
        ikiwa not HAVE_SSL:
            raise error_proto('-ERR TLS support missing')
        ikiwa self._tls_established:
            raise error_proto('-ERR TLS session already established')
        caps = self.capa()
        ikiwa not 'STLS' in caps:
            raise error_proto('-ERR STLS not supported by server')
        ikiwa context is None:
            context = ssl._create_stdlib_context()
        resp = self._shortcmd('STLS')
        self.sock = context.wrap_socket(self.sock,
                                        server_hostname=self.host)
        self.file = self.sock.makefile('rb')
        self._tls_established = True
        rudisha resp


ikiwa HAVE_SSL:

    kundi POP3_SSL(POP3):
        """POP3 client kundi over SSL connection

        Instantiate with: POP3_SSL(hostname, port=995, keyfile=None, certfile=None,
                                   context=None)

               hostname - the hostname of the pop3 over ssl server
               port - port number
               keyfile - PEM formatted file that contains your private key
               certfile - PEM formatted certificate chain file
               context - a ssl.SSLContext

        See the methods of the parent kundi POP3 for more documentation.
        """

        eleza __init__(self, host, port=POP3_SSL_PORT, keyfile=None, certfile=None,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT, context=None):
            ikiwa context is not None and keyfile is not None:
                raise ValueError("context and keyfile arguments are mutually "
                                 "exclusive")
            ikiwa context is not None and certfile is not None:
                raise ValueError("context and certfile arguments are mutually "
                                 "exclusive")
            ikiwa keyfile is not None or certfile is not None:
                agiza warnings
                warnings.warn("keyfile and certfile are deprecated, use a "
                              "custom context instead", DeprecationWarning, 2)
            self.keyfile = keyfile
            self.certfile = certfile
            ikiwa context is None:
                context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
            self.context = context
            POP3.__init__(self, host, port, timeout)

        eleza _create_socket(self, timeout):
            sock = POP3._create_socket(self, timeout)
            sock = self.context.wrap_socket(sock,
                                            server_hostname=self.host)
            rudisha sock

        eleza stls(self, keyfile=None, certfile=None, context=None):
            """The method unconditionally raises an exception since the
            STLS command doesn't make any sense on an already established
            SSL/TLS session.
            """
            raise error_proto('-ERR TLS session already established')

    __all__.append("POP3_SSL")

ikiwa __name__ == "__main__":
    agiza sys
    a = POP3(sys.argv[1])
    andika(a.getwelcome())
    a.user(sys.argv[2])
    a.pass_(sys.argv[3])
    a.list()
    (numMsgs, totalSize) = a.stat()
    for i in range(1, numMsgs + 1):
        (header, msg, octets) = a.retr(i)
        andika("Message %d:" % i)
        for line in msg:
            andika('   ' + line)
        andika('-----------------------')
    a.quit()
