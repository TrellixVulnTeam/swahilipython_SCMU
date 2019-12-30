#! /usr/bin/env python3

'''SMTP/ESMTP client class.

This should follow RFC 821 (SMTP), RFC 1869 (ESMTP), RFC 2554 (SMTP
Authentication) na RFC 2487 (Secure SMTP over TLS).

Notes:

Please remember, when doing ESMTP, that the names of the SMTP service
extensions are NOT the same thing kama the option keywords kila the RCPT
and MAIL commands!

Example:

  >>> agiza smtplib
  >>> s=smtplib.SMTP("localhost")
  >>> andika(s.help())
  This ni Sendmail version 8.8.4
  Topics:
      HELO    EHLO    MAIL    RCPT    DATA
      RSET    NOOP    QUIT    HELP    VRFY
      EXPN    VERB    ETRN    DSN
  For more info use "HELP <topic>".
  To report bugs kwenye the implementation send email to
      sendmail-bugs@sendmail.org.
  For local information send email to Postmaster at your site.
  End of HELP info
  >>> s.putcmd("vrfy","someone@here")
  >>> s.getreply()
  (250, "Somebody OverHere <somebody@here.my.org>")
  >>> s.quit()
'''

# Author: The Dragon De Monsyne <dragondm@integral.org>
# ESMTP support, test code na doc fixes added by
#     Eric S. Raymond <esr@thyrsus.com>
# Better RFC 821 compliance (MAIL na RCPT, na CRLF kwenye data)
#     by Carey Evans <c.evans@clear.net.nz>, kila picky mail servers.
# RFC 2554 (authentication) support by Gerhard Haering <gerhard@bigfoot.de>.
#
# This was modified kutoka the Python 1.5 library HTTP lib.

agiza socket
agiza io
agiza re
agiza email.utils
agiza email.message
agiza email.generator
agiza base64
agiza hmac
agiza copy
agiza datetime
agiza sys
kutoka email.base64mime agiza body_encode kama encode_base64

__all__ = ["SMTPException", "SMTPNotSupportedError", "SMTPServerDisconnected", "SMTPResponseException",
           "SMTPSenderRefused", "SMTPRecipientsRefused", "SMTPDataError",
           "SMTPConnectError", "SMTPHeloError", "SMTPAuthenticationError",
           "quoteaddr", "quotedata", "SMTP"]

SMTP_PORT = 25
SMTP_SSL_PORT = 465
CRLF = "\r\n"
bCRLF = b"\r\n"
_MAXLINE = 8192 # more than 8 times larger than RFC 821, 4.5.3

OLDSTYLE_AUTH = re.compile(r"auth=(.*)", re.I)

# Exception classes used by this module.
kundi SMTPException(OSError):
    """Base kundi kila all exceptions raised by this module."""

kundi SMTPNotSupportedError(SMTPException):
    """The command ama option ni sio supported by the SMTP server.

    This exception ni raised when an attempt ni made to run a command ama a
    command ukijumuisha an option which ni sio supported by the server.
    """

kundi SMTPServerDisconnected(SMTPException):
    """Not connected to any SMTP server.

    This exception ni raised when the server unexpectedly disconnects,
    ama when an attempt ni made to use the SMTP instance before
    connecting it to a server.
    """

kundi SMTPResponseException(SMTPException):
    """Base kundi kila all exceptions that include an SMTP error code.

    These exceptions are generated kwenye some instances when the SMTP
    server returns an error code.  The error code ni stored kwenye the
    `smtp_code' attribute of the error, na the `smtp_error' attribute
    ni set to the error message.
    """

    eleza __init__(self, code, msg):
        self.smtp_code = code
        self.smtp_error = msg
        self.args = (code, msg)

kundi SMTPSenderRefused(SMTPResponseException):
    """Sender address refused.

    In addition to the attributes set by on all SMTPResponseException
    exceptions, this sets `sender' to the string that the SMTP refused.
    """

    eleza __init__(self, code, msg, sender):
        self.smtp_code = code
        self.smtp_error = msg
        self.sender = sender
        self.args = (code, msg, sender)

kundi SMTPRecipientsRefused(SMTPException):
    """All recipient addresses refused.

    The errors kila each recipient are accessible through the attribute
    'recipients', which ni a dictionary of exactly the same sort as
    SMTP.sendmail() returns.
    """

    eleza __init__(self, recipients):
        self.recipients = recipients
        self.args = (recipients,)


kundi SMTPDataError(SMTPResponseException):
    """The SMTP server didn't accept the data."""

kundi SMTPConnectError(SMTPResponseException):
    """Error during connection establishment."""

kundi SMTPHeloError(SMTPResponseException):
    """The server refused our HELO reply."""

kundi SMTPAuthenticationError(SMTPResponseException):
    """Authentication error.

    Most probably the server didn't accept the username/pitaword
    combination provided.
    """

eleza quoteaddr(addrstring):
    """Quote a subset of the email addresses defined by RFC 821.

    Should be able to handle anything email.utils.parseaddr can handle.
    """
    displayname, addr = email.utils.parseaddr(addrstring)
    ikiwa (displayname, addr) == ('', ''):
        # parseaddr couldn't parse it, use it kama ni na hope kila the best.
        ikiwa addrstring.strip().startswith('<'):
            rudisha addrstring
        rudisha "<%s>" % addrstring
    rudisha "<%s>" % addr

eleza _addr_only(addrstring):
    displayname, addr = email.utils.parseaddr(addrstring)
    ikiwa (displayname, addr) == ('', ''):
        # parseaddr couldn't parse it, so use it kama is.
        rudisha addrstring
    rudisha addr

# Legacy method kept kila backward compatibility.
eleza quotedata(data):
    """Quote data kila email.

    Double leading '.', na change Unix newline '\\n', ama Mac '\\r' into
    Internet CRLF end-of-line.
    """
    rudisha re.sub(r'(?m)^\.', '..',
        re.sub(r'(?:\r\n|\n|\r(?!\n))', CRLF, data))

eleza _quote_periods(bindata):
    rudisha re.sub(br'(?m)^\.', b'..', bindata)

eleza _fix_eols(data):
    rudisha  re.sub(r'(?:\r\n|\n|\r(?!\n))', CRLF, data)

jaribu:
    agiza ssl
tatizo ImportError:
    _have_ssl = Uongo
isipokua:
    _have_ssl = Kweli


kundi SMTP:
    """This kundi manages a connection to an SMTP ama ESMTP server.
    SMTP Objects:
        SMTP objects have the following attributes:
            helo_resp
                This ni the message given by the server kwenye response to the
                most recent HELO command.

            ehlo_resp
                This ni the message given by the server kwenye response to the
                most recent EHLO command. This ni usually multiline.

            does_esmtp
                This ni a Kweli value _after you do an EHLO command_, ikiwa the
                server supports ESMTP.

            esmtp_features
                This ni a dictionary, which, ikiwa the server supports ESMTP,
                will _after you do an EHLO command_, contain the names of the
                SMTP service extensions this server supports, na their
                parameters (ikiwa any).

                Note, all extension names are mapped to lower case kwenye the
                dictionary.

        See each method's docstrings kila details.  In general, there ni a
        method of the same name to perform each SMTP command.  There ni also a
        method called 'sendmail' that will do an entire mail transaction.
        """
    debuglevel = 0

    sock = Tupu
    file = Tupu
    helo_resp = Tupu
    ehlo_msg = "ehlo"
    ehlo_resp = Tupu
    does_esmtp = 0
    default_port = SMTP_PORT

    eleza __init__(self, host='', port=0, local_hostname=Tupu,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=Tupu):
        """Initialize a new instance.

        If specified, `host' ni the name of the remote host to which to
        connect.  If specified, `port' specifies the port to which to connect.
        By default, smtplib.SMTP_PORT ni used.  If a host ni specified the
        connect method ni called, na ikiwa it returns anything other than a
        success code an SMTPConnectError ni raised.  If specified,
        `local_hostname` ni used kama the FQDN of the local host kwenye the HELO/EHLO
        command.  Otherwise, the local hostname ni found using
        socket.getfqdn(). The `source_address` parameter takes a 2-tuple (host,
        port) kila the socket to bind to kama its source address before
        connecting. If the host ni '' na port ni 0, the OS default behavior
        will be used.

        """
        self._host = host
        self.timeout = timeout
        self.esmtp_features = {}
        self.command_encoding = 'ascii'
        self.source_address = source_address

        ikiwa host:
            (code, msg) = self.connect(host, port)
            ikiwa code != 220:
                self.close()
                ashiria SMTPConnectError(code, msg)
        ikiwa local_hostname ni sio Tupu:
            self.local_hostname = local_hostname
        isipokua:
            # RFC 2821 says we should use the fqdn kwenye the EHLO/HELO verb, na
            # ikiwa that can't be calculated, that we should use a domain literal
            # instead (essentially an encoded IP address like [A.B.C.D]).
            fqdn = socket.getfqdn()
            ikiwa '.' kwenye fqdn:
                self.local_hostname = fqdn
            isipokua:
                # We can't find an fqdn hostname, so use a domain literal
                addr = '127.0.0.1'
                jaribu:
                    addr = socket.gethostbyname(socket.gethostname())
                tatizo socket.gaierror:
                    pita
                self.local_hostname = '[%s]' % addr

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        jaribu:
            code, message = self.docmd("QUIT")
            ikiwa code != 221:
                ashiria SMTPResponseException(code, message)
        tatizo SMTPServerDisconnected:
            pita
        mwishowe:
            self.close()

    eleza set_debuglevel(self, debuglevel):
        """Set the debug output level.

        A non-false value results kwenye debug messages kila connection na kila all
        messages sent to na received kutoka the server.

        """
        self.debuglevel = debuglevel

    eleza _print_debug(self, *args):
        ikiwa self.debuglevel > 1:
            andika(datetime.datetime.now().time(), *args, file=sys.stderr)
        isipokua:
            andika(*args, file=sys.stderr)

    eleza _get_socket(self, host, port, timeout):
        # This makes it simpler kila SMTP_SSL to use the SMTP connect code
        # na just alter the socket connection bit.
        ikiwa self.debuglevel > 0:
            self._print_debug('connect: to', (host, port), self.source_address)
        rudisha socket.create_connection((host, port), timeout,
                                        self.source_address)

    eleza connect(self, host='localhost', port=0, source_address=Tupu):
        """Connect to a host on a given port.

        If the hostname ends ukijumuisha a colon (`:') followed by a number, na
        there ni no port specified, that suffix will be stripped off na the
        number interpreted kama the port number to use.

        Note: This method ni automatically invoked by __init__, ikiwa a host is
        specified during instantiation.

        """

        ikiwa source_address:
            self.source_address = source_address

        ikiwa sio port na (host.find(':') == host.rfind(':')):
            i = host.rfind(':')
            ikiwa i >= 0:
                host, port = host[:i], host[i + 1:]
                jaribu:
                    port = int(port)
                tatizo ValueError:
                    ashiria OSError("nonnumeric port")
        ikiwa sio port:
            port = self.default_port
        ikiwa self.debuglevel > 0:
            self._print_debug('connect:', (host, port))
        sys.audit("smtplib.connect", self, host, port)
        self.sock = self._get_socket(host, port, self.timeout)
        self.file = Tupu
        (code, msg) = self.getreply()
        ikiwa self.debuglevel > 0:
            self._print_debug('connect:', repr(msg))
        rudisha (code, msg)

    eleza send(self, s):
        """Send `s' to the server."""
        ikiwa self.debuglevel > 0:
            self._print_debug('send:', repr(s))
        ikiwa self.sock:
            ikiwa isinstance(s, str):
                # send ni used by the 'data' command, where command_encoding
                # should sio be used, but 'data' needs to convert the string to
                # binary itself anyway, so that's sio a problem.
                s = s.encode(self.command_encoding)
            sys.audit("smtplib.send", self, s)
            jaribu:
                self.sock.sendall(s)
            tatizo OSError:
                self.close()
                ashiria SMTPServerDisconnected('Server sio connected')
        isipokua:
            ashiria SMTPServerDisconnected('please run connect() first')

    eleza putcmd(self, cmd, args=""):
        """Send a command to the server."""
        ikiwa args == "":
            str = '%s%s' % (cmd, CRLF)
        isipokua:
            str = '%s %s%s' % (cmd, args, CRLF)
        self.send(str)

    eleza getreply(self):
        """Get a reply kutoka the server.

        Returns a tuple consisting of:

          - server response code (e.g. '250', ama such, ikiwa all goes well)
            Note: returns -1 ikiwa it can't read response code.

          - server response string corresponding to response code (multiline
            responses are converted to a single, multiline string).

        Raises SMTPServerDisconnected ikiwa end-of-file ni reached.
        """
        resp = []
        ikiwa self.file ni Tupu:
            self.file = self.sock.makefile('rb')
        wakati 1:
            jaribu:
                line = self.file.readline(_MAXLINE + 1)
            tatizo OSError kama e:
                self.close()
                ashiria SMTPServerDisconnected("Connection unexpectedly closed: "
                                             + str(e))
            ikiwa sio line:
                self.close()
                ashiria SMTPServerDisconnected("Connection unexpectedly closed")
            ikiwa self.debuglevel > 0:
                self._print_debug('reply:', repr(line))
            ikiwa len(line) > _MAXLINE:
                self.close()
                ashiria SMTPResponseException(500, "Line too long.")
            resp.append(line[4:].strip(b' \t\r\n'))
            code = line[:3]
            # Check that the error code ni syntactically correct.
            # Don't attempt to read a continuation line ikiwa it ni broken.
            jaribu:
                errcode = int(code)
            tatizo ValueError:
                errcode = -1
                koma
            # Check ikiwa multiline response.
            ikiwa line[3:4] != b"-":
                koma

        errmsg = b"\n".join(resp)
        ikiwa self.debuglevel > 0:
            self._print_debug('reply: retcode (%s); Msg: %a' % (errcode, errmsg))
        rudisha errcode, errmsg

    eleza docmd(self, cmd, args=""):
        """Send a command, na rudisha its response code."""
        self.putcmd(cmd, args)
        rudisha self.getreply()

    # std smtp commands
    eleza helo(self, name=''):
        """SMTP 'helo' command.
        Hostname to send kila this command defaults to the FQDN of the local
        host.
        """
        self.putcmd("helo", name ama self.local_hostname)
        (code, msg) = self.getreply()
        self.helo_resp = msg
        rudisha (code, msg)

    eleza ehlo(self, name=''):
        """ SMTP 'ehlo' command.
        Hostname to send kila this command defaults to the FQDN of the local
        host.
        """
        self.esmtp_features = {}
        self.putcmd(self.ehlo_msg, name ama self.local_hostname)
        (code, msg) = self.getreply()
        # According to RFC1869 some (badly written)
        # MTA's will disconnect on an ehlo. Toss an exception if
        # that happens -ddm
        ikiwa code == -1 na len(msg) == 0:
            self.close()
            ashiria SMTPServerDisconnected("Server sio connected")
        self.ehlo_resp = msg
        ikiwa code != 250:
            rudisha (code, msg)
        self.does_esmtp = 1
        #parse the ehlo response -ddm
        assert isinstance(self.ehlo_resp, bytes), repr(self.ehlo_resp)
        resp = self.ehlo_resp.decode("latin-1").split('\n')
        toa resp[0]
        kila each kwenye resp:
            # To be able to communicate ukijumuisha kama many SMTP servers kama possible,
            # we have to take the old-style auth advertisement into account,
            # because:
            # 1) Else our SMTP feature parser gets confused.
            # 2) There are some servers that only advertise the auth methods we
            #    support using the old style.
            auth_match = OLDSTYLE_AUTH.match(each)
            ikiwa auth_match:
                # This doesn't remove duplicates, but that's no problem
                self.esmtp_features["auth"] = self.esmtp_features.get("auth", "") \
                        + " " + auth_match.groups(0)[0]
                endelea

            # RFC 1869 requires a space between ehlo keyword na parameters.
            # It's actually stricter, kwenye that only spaces are allowed between
            # parameters, but were sio going to check kila that here.  Note
            # that the space isn't present ikiwa there are no parameters.
            m = re.match(r'(?P<feature>[A-Za-z0-9][A-Za-z0-9\-]*) ?', each)
            ikiwa m:
                feature = m.group("feature").lower()
                params = m.string[m.end("feature"):].strip()
                ikiwa feature == "auth":
                    self.esmtp_features[feature] = self.esmtp_features.get(feature, "") \
                            + " " + params
                isipokua:
                    self.esmtp_features[feature] = params
        rudisha (code, msg)

    eleza has_extn(self, opt):
        """Does the server support a given SMTP service extension?"""
        rudisha opt.lower() kwenye self.esmtp_features

    eleza help(self, args=''):
        """SMTP 'help' command.
        Returns help text kutoka server."""
        self.putcmd("help", args)
        rudisha self.getreply()[1]

    eleza rset(self):
        """SMTP 'rset' command -- resets session."""
        self.command_encoding = 'ascii'
        rudisha self.docmd("rset")

    eleza _rset(self):
        """Internal 'rset' command which ignores any SMTPServerDisconnected error.

        Used internally kwenye the library, since the server disconnected error
        should appear to the application when the *next* command ni issued, if
        we are doing an internal "safety" reset.
        """
        jaribu:
            self.rset()
        tatizo SMTPServerDisconnected:
            pita

    eleza noop(self):
        """SMTP 'noop' command -- doesn't do anything :>"""
        rudisha self.docmd("noop")

    eleza mail(self, sender, options=()):
        """SMTP 'mail' command -- begins mail xfer session.

        This method may ashiria the following exceptions:

         SMTPNotSupportedError  The options parameter includes 'SMTPUTF8'
                                but the SMTPUTF8 extension ni sio supported by
                                the server.
        """
        optionlist = ''
        ikiwa options na self.does_esmtp:
            ikiwa any(x.lower()=='smtputf8' kila x kwenye options):
                ikiwa self.has_extn('smtputf8'):
                    self.command_encoding = 'utf-8'
                isipokua:
                    ashiria SMTPNotSupportedError(
                        'SMTPUTF8 sio supported by server')
            optionlist = ' ' + ' '.join(options)
        self.putcmd("mail", "FROM:%s%s" % (quoteaddr(sender), optionlist))
        rudisha self.getreply()

    eleza rcpt(self, recip, options=()):
        """SMTP 'rcpt' command -- indicates 1 recipient kila this mail."""
        optionlist = ''
        ikiwa options na self.does_esmtp:
            optionlist = ' ' + ' '.join(options)
        self.putcmd("rcpt", "TO:%s%s" % (quoteaddr(recip), optionlist))
        rudisha self.getreply()

    eleza data(self, msg):
        """SMTP 'DATA' command -- sends message data to server.

        Automatically quotes lines beginning ukijumuisha a period per rfc821.
        Raises SMTPDataError ikiwa there ni an unexpected reply to the
        DATA command; the rudisha value kutoka this method ni the final
        response code received when the all data ni sent.  If msg
        ni a string, lone '\\r' na '\\n' characters are converted to
        '\\r\\n' characters.  If msg ni bytes, it ni transmitted kama is.
        """
        self.putcmd("data")
        (code, repl) = self.getreply()
        ikiwa self.debuglevel > 0:
            self._print_debug('data:', (code, repl))
        ikiwa code != 354:
            ashiria SMTPDataError(code, repl)
        isipokua:
            ikiwa isinstance(msg, str):
                msg = _fix_eols(msg).encode('ascii')
            q = _quote_periods(msg)
            ikiwa q[-2:] != bCRLF:
                q = q + bCRLF
            q = q + b"." + bCRLF
            self.send(q)
            (code, msg) = self.getreply()
            ikiwa self.debuglevel > 0:
                self._print_debug('data:', (code, msg))
            rudisha (code, msg)

    eleza verify(self, address):
        """SMTP 'verify' command -- checks kila address validity."""
        self.putcmd("vrfy", _addr_only(address))
        rudisha self.getreply()
    # a.k.a.
    vrfy = verify

    eleza expn(self, address):
        """SMTP 'expn' command -- expands a mailing list."""
        self.putcmd("expn", _addr_only(address))
        rudisha self.getreply()

    # some useful methods

    eleza ehlo_or_helo_if_needed(self):
        """Call self.ehlo() and/or self.helo() ikiwa needed.

        If there has been no previous EHLO ama HELO command this session, this
        method tries ESMTP EHLO first.

        This method may ashiria the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
        """
        ikiwa self.helo_resp ni Tupu na self.ehlo_resp ni Tupu:
            ikiwa sio (200 <= self.ehlo()[0] <= 299):
                (code, resp) = self.helo()
                ikiwa sio (200 <= code <= 299):
                    ashiria SMTPHeloError(code, resp)

    eleza auth(self, mechanism, authobject, *, initial_response_ok=Kweli):
        """Authentication command - requires response processing.

        'mechanism' specifies which authentication mechanism ni to
        be used - the valid values are those listed kwenye the 'auth'
        element of 'esmtp_features'.

        'authobject' must be a callable object taking a single argument:

                data = authobject(challenge)

        It will be called to process the server's challenge response; the
        challenge argument it ni pitaed will be a bytes.  It should rudisha
        an ASCII string that will be base64 encoded na sent to the server.

        Keyword arguments:
            - initial_response_ok: Allow sending the RFC 4954 initial-response
              to the AUTH command, ikiwa the authentication methods supports it.
        """
        # RFC 4954 allows auth methods to provide an initial response.  Not all
        # methods support it.  By definition, ikiwa they rudisha something other
        # than Tupu when challenge ni Tupu, then they do.  See issue #15014.
        mechanism = mechanism.upper()
        initial_response = (authobject() ikiwa initial_response_ok isipokua Tupu)
        ikiwa initial_response ni sio Tupu:
            response = encode_base64(initial_response.encode('ascii'), eol='')
            (code, resp) = self.docmd("AUTH", mechanism + " " + response)
        isipokua:
            (code, resp) = self.docmd("AUTH", mechanism)
        # If server responds ukijumuisha a challenge, send the response.
        ikiwa code == 334:
            challenge = base64.decodebytes(resp)
            response = encode_base64(
                authobject(challenge).encode('ascii'), eol='')
            (code, resp) = self.docmd(response)
        ikiwa code kwenye (235, 503):
            rudisha (code, resp)
        ashiria SMTPAuthenticationError(code, resp)

    eleza auth_cram_md5(self, challenge=Tupu):
        """ Authobject to use ukijumuisha CRAM-MD5 authentication. Requires self.user
        na self.pitaword to be set."""
        # CRAM-MD5 does sio support initial-response.
        ikiwa challenge ni Tupu:
            rudisha Tupu
        rudisha self.user + " " + hmac.HMAC(
            self.pitaword.encode('ascii'), challenge, 'md5').hexdigest()

    eleza auth_plain(self, challenge=Tupu):
        """ Authobject to use ukijumuisha PLAIN authentication. Requires self.user na
        self.pitaword to be set."""
        rudisha "\0%s\0%s" % (self.user, self.pitaword)

    eleza auth_login(self, challenge=Tupu):
        """ Authobject to use ukijumuisha LOGIN authentication. Requires self.user na
        self.pitaword to be set."""
        ikiwa challenge ni Tupu:
            rudisha self.user
        isipokua:
            rudisha self.pitaword

    eleza login(self, user, pitaword, *, initial_response_ok=Kweli):
        """Log kwenye on an SMTP server that requires authentication.

        The arguments are:
            - user:         The user name to authenticate with.
            - pitaword:     The pitaword kila the authentication.

        Keyword arguments:
            - initial_response_ok: Allow sending the RFC 4954 initial-response
              to the AUTH command, ikiwa the authentication methods supports it.

        If there has been no previous EHLO ama HELO command this session, this
        method tries ESMTP EHLO first.

        This method will rudisha normally ikiwa the authentication was successful.

        This method may ashiria the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
         SMTPAuthenticationError  The server didn't accept the username/
                                  pitaword combination.
         SMTPNotSupportedError    The AUTH command ni sio supported by the
                                  server.
         SMTPException            No suitable authentication method was
                                  found.
        """

        self.ehlo_or_helo_if_needed()
        ikiwa sio self.has_extn("auth"):
            ashiria SMTPNotSupportedError(
                "SMTP AUTH extension sio supported by server.")

        # Authentication methods the server claims to support
        advertised_authlist = self.esmtp_features["auth"].split()

        # Authentication methods we can handle kwenye our preferred order:
        preferred_auths = ['CRAM-MD5', 'PLAIN', 'LOGIN']

        # We try the supported authentications kwenye our preferred order, if
        # the server supports them.
        authlist = [auth kila auth kwenye preferred_auths
                    ikiwa auth kwenye advertised_authlist]
        ikiwa sio authlist:
            ashiria SMTPException("No suitable authentication method found.")

        # Some servers advertise authentication methods they don't really
        # support, so ikiwa authentication fails, we endelea until we've tried
        # all methods.
        self.user, self.pitaword = user, pitaword
        kila authmethod kwenye authlist:
            method_name = 'auth_' + authmethod.lower().replace('-', '_')
            jaribu:
                (code, resp) = self.auth(
                    authmethod, getattr(self, method_name),
                    initial_response_ok=initial_response_ok)
                # 235 == 'Authentication successful'
                # 503 == 'Error: already authenticated'
                ikiwa code kwenye (235, 503):
                    rudisha (code, resp)
            tatizo SMTPAuthenticationError kama e:
                last_exception = e

        # We could sio login successfully.  Return result of last attempt.
        ashiria last_exception

    eleza starttls(self, keyfile=Tupu, certfile=Tupu, context=Tupu):
        """Puts the connection to the SMTP server into TLS mode.

        If there has been no previous EHLO ama HELO command this session, this
        method tries ESMTP EHLO first.

        If the server supports TLS, this will encrypt the rest of the SMTP
        session. If you provide the keyfile na certfile parameters,
        the identity of the SMTP server na client can be checked. This,
        however, depends on whether the socket module really checks the
        certificates.

        This method may ashiria the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
        """
        self.ehlo_or_helo_if_needed()
        ikiwa sio self.has_extn("starttls"):
            ashiria SMTPNotSupportedError(
                "STARTTLS extension sio supported by server.")
        (resp, reply) = self.docmd("STARTTLS")
        ikiwa resp == 220:
            ikiwa sio _have_ssl:
                ashiria RuntimeError("No SSL support included kwenye this Python")
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
            ikiwa context ni Tupu:
                context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
            self.sock = context.wrap_socket(self.sock,
                                            server_hostname=self._host)
            self.file = Tupu
            # RFC 3207:
            # The client MUST discard any knowledge obtained from
            # the server, such kama the list of SMTP service extensions,
            # which was sio obtained kutoka the TLS negotiation itself.
            self.helo_resp = Tupu
            self.ehlo_resp = Tupu
            self.esmtp_features = {}
            self.does_esmtp = 0
        isipokua:
            # RFC 3207:
            # 501 Syntax error (no parameters allowed)
            # 454 TLS sio available due to temporary reason
            ashiria SMTPResponseException(resp, reply)
        rudisha (resp, reply)

    eleza sendmail(self, from_addr, to_addrs, msg, mail_options=(),
                 rcpt_options=()):
        """This command performs an entire mail transaction.

        The arguments are:
            - from_addr    : The address sending this mail.
            - to_addrs     : A list of addresses to send this mail to.  A bare
                             string will be treated kama a list ukijumuisha 1 address.
            - msg          : The message to send.
            - mail_options : List of ESMTP options (such kama 8bitmime) kila the
                             mail command.
            - rcpt_options : List of ESMTP options (such kama DSN commands) for
                             all the rcpt commands.

        msg may be a string containing characters kwenye the ASCII range, ama a byte
        string.  A string ni encoded to bytes using the ascii codec, na lone
        \\r na \\n characters are converted to \\r\\n characters.

        If there has been no previous EHLO ama HELO command this session, this
        method tries ESMTP EHLO first.  If the server does ESMTP, message size
        na each of the specified options will be pitaed to it.  If EHLO
        fails, HELO will be tried na ESMTP options suppressed.

        This method will rudisha normally ikiwa the mail ni accepted kila at least
        one recipient.  It returns a dictionary, ukijumuisha one entry kila each
        recipient that was refused.  Each entry contains a tuple of the SMTP
        error code na the accompanying error message sent by the server.

        This method may ashiria the following exceptions:

         SMTPHeloError          The server didn't reply properly to
                                the helo greeting.
         SMTPRecipientsRefused  The server rejected ALL recipients
                                (no mail was sent).
         SMTPSenderRefused      The server didn't accept the from_addr.
         SMTPDataError          The server replied ukijumuisha an unexpected
                                error code (other than a refusal of
                                a recipient).
         SMTPNotSupportedError  The mail_options parameter includes 'SMTPUTF8'
                                but the SMTPUTF8 extension ni sio supported by
                                the server.

        Note: the connection will be open even after an exception ni raised.

        Example:

         >>> agiza smtplib
         >>> s=smtplib.SMTP("localhost")
         >>> tolist=["one@one.org","two@two.org","three@three.org","four@four.org"]
         >>> msg = '''\\
         ... From: Me@my.org
         ... Subject: testin'...
         ...
         ... This ni a test '''
         >>> s.sendmail("me@my.org",tolist,msg)
         { "three@three.org" : ( 550 ,"User unknown" ) }
         >>> s.quit()

        In the above example, the message was accepted kila delivery to three
        of the four addresses, na one was rejected, ukijumuisha the error code
        550.  If all addresses are accepted, then the method will rudisha an
        empty dictionary.

        """
        self.ehlo_or_helo_if_needed()
        esmtp_opts = []
        ikiwa isinstance(msg, str):
            msg = _fix_eols(msg).encode('ascii')
        ikiwa self.does_esmtp:
            ikiwa self.has_extn('size'):
                esmtp_opts.append("size=%d" % len(msg))
            kila option kwenye mail_options:
                esmtp_opts.append(option)
        (code, resp) = self.mail(from_addr, esmtp_opts)
        ikiwa code != 250:
            ikiwa code == 421:
                self.close()
            isipokua:
                self._rset()
            ashiria SMTPSenderRefused(code, resp, from_addr)
        senderrs = {}
        ikiwa isinstance(to_addrs, str):
            to_addrs = [to_addrs]
        kila each kwenye to_addrs:
            (code, resp) = self.rcpt(each, rcpt_options)
            ikiwa (code != 250) na (code != 251):
                senderrs[each] = (code, resp)
            ikiwa code == 421:
                self.close()
                ashiria SMTPRecipientsRefused(senderrs)
        ikiwa len(senderrs) == len(to_addrs):
            # the server refused all our recipients
            self._rset()
            ashiria SMTPRecipientsRefused(senderrs)
        (code, resp) = self.data(msg)
        ikiwa code != 250:
            ikiwa code == 421:
                self.close()
            isipokua:
                self._rset()
            ashiria SMTPDataError(code, resp)
        #ikiwa we got here then somebody got our mail
        rudisha senderrs

    eleza send_message(self, msg, from_addr=Tupu, to_addrs=Tupu,
                     mail_options=(), rcpt_options=()):
        """Converts message to a bytestring na pitaes it to sendmail.

        The arguments are kama kila sendmail, tatizo that msg ni an
        email.message.Message object.  If from_addr ni Tupu ama to_addrs is
        Tupu, these arguments are taken kutoka the headers of the Message as
        described kwenye RFC 2822 (a ValueError ni raised ikiwa there ni more than
        one set of 'Resent-' headers).  Regardless of the values of from_addr na
        to_addr, any Bcc field (or Resent-Bcc field, when the Message ni a
        resent) of the Message object won't be transmitted.  The Message
        object ni then serialized using email.generator.BytesGenerator na
        sendmail ni called to transmit the message.  If the sender ama any of
        the recipient addresses contain non-ASCII na the server advertises the
        SMTPUTF8 capability, the policy ni cloned ukijumuisha utf8 set to Kweli kila the
        serialization, na SMTPUTF8 na BODY=8BITMIME are asserted on the send.
        If the server does sio support SMTPUTF8, an SMTPNotSupported error is
        raised.  Otherwise the generator ni called without modifying the
        policy.

        """
        # 'Resent-Date' ni a mandatory field ikiwa the Message ni resent (RFC 2822
        # Section 3.6.6). In such a case, we use the 'Resent-*' fields.  However,
        # ikiwa there ni more than one 'Resent-' block there's no way to
        # unambiguously determine which one ni the most recent kwenye all cases,
        # so rather than guess we ashiria a ValueError kwenye that case.
        #
        # TODO implement heuristics to guess the correct Resent-* block ukijumuisha an
        # option allowing the user to enable the heuristics.  (It should be
        # possible to guess correctly almost all of the time.)

        self.ehlo_or_helo_if_needed()
        resent = msg.get_all('Resent-Date')
        ikiwa resent ni Tupu:
            header_prefix = ''
        lasivyo len(resent) == 1:
            header_prefix = 'Resent-'
        isipokua:
            ashiria ValueError("message has more than one 'Resent-' header block")
        ikiwa from_addr ni Tupu:
            # Prefer the sender field per RFC 2822:3.6.2.
            from_addr = (msg[header_prefix + 'Sender']
                           ikiwa (header_prefix + 'Sender') kwenye msg
                           isipokua msg[header_prefix + 'From'])
            from_addr = email.utils.getaddresses([from_addr])[0][1]
        ikiwa to_addrs ni Tupu:
            addr_fields = [f kila f kwenye (msg[header_prefix + 'To'],
                                       msg[header_prefix + 'Bcc'],
                                       msg[header_prefix + 'Cc'])
                           ikiwa f ni sio Tupu]
            to_addrs = [a[1] kila a kwenye email.utils.getaddresses(addr_fields)]
        # Make a local copy so we can delete the bcc headers.
        msg_copy = copy.copy(msg)
        toa msg_copy['Bcc']
        toa msg_copy['Resent-Bcc']
        international = Uongo
        jaribu:
            ''.join([from_addr, *to_addrs]).encode('ascii')
        tatizo UnicodeEncodeError:
            ikiwa sio self.has_extn('smtputf8'):
                ashiria SMTPNotSupportedError(
                    "One ama more source ama delivery addresses require"
                    " internationalized email support, but the server"
                    " does sio advertise the required SMTPUTF8 capability")
            international = Kweli
        ukijumuisha io.BytesIO() kama bytesmsg:
            ikiwa international:
                g = email.generator.BytesGenerator(
                    bytesmsg, policy=msg.policy.clone(utf8=Kweli))
                mail_options = (*mail_options, 'SMTPUTF8', 'BODY=8BITMIME')
            isipokua:
                g = email.generator.BytesGenerator(bytesmsg)
            g.flatten(msg_copy, linesep='\r\n')
            flatmsg = bytesmsg.getvalue()
        rudisha self.sendmail(from_addr, to_addrs, flatmsg, mail_options,
                             rcpt_options)

    eleza close(self):
        """Close the connection to the SMTP server."""
        jaribu:
            file = self.file
            self.file = Tupu
            ikiwa file:
                file.close()
        mwishowe:
            sock = self.sock
            self.sock = Tupu
            ikiwa sock:
                sock.close()

    eleza quit(self):
        """Terminate the SMTP session."""
        res = self.docmd("quit")
        # A new EHLO ni required after reconnecting ukijumuisha connect()
        self.ehlo_resp = self.helo_resp = Tupu
        self.esmtp_features = {}
        self.does_esmtp = Uongo
        self.close()
        rudisha res

ikiwa _have_ssl:

    kundi SMTP_SSL(SMTP):
        """ This ni a subkundi derived kutoka SMTP that connects over an SSL
        encrypted socket (to use this kundi you need a socket module that was
        compiled ukijumuisha SSL support). If host ni sio specified, '' (the local
        host) ni used. If port ni omitted, the standard SMTP-over-SSL port
        (465) ni used.  local_hostname na source_address have the same meaning
        kama they do kwenye the SMTP class.  keyfile na certfile are also optional -
        they can contain a PEM formatted private key na certificate chain file
        kila the SSL connection. context also optional, can contain a
        SSLContext, na ni an alternative to keyfile na certfile; If it is
        specified both keyfile na certfile must be Tupu.

        """

        default_port = SMTP_SSL_PORT

        eleza __init__(self, host='', port=0, local_hostname=Tupu,
                     keyfile=Tupu, certfile=Tupu,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     source_address=Tupu, context=Tupu):
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
                context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
            self.context = context
            SMTP.__init__(self, host, port, local_hostname, timeout,
                    source_address)

        eleza _get_socket(self, host, port, timeout):
            ikiwa self.debuglevel > 0:
                self._print_debug('connect:', (host, port))
            new_socket = socket.create_connection((host, port), timeout,
                    self.source_address)
            new_socket = self.context.wrap_socket(new_socket,
                                                  server_hostname=self._host)
            rudisha new_socket

    __all__.append("SMTP_SSL")

#
# LMTP extension
#
LMTP_PORT = 2003

kundi LMTP(SMTP):
    """LMTP - Local Mail Transfer Protocol

    The LMTP protocol, which ni very similar to ESMTP, ni heavily based
    on the standard SMTP client. It's common to use Unix sockets for
    LMTP, so our connect() method must support that kama well kama a regular
    host:port server.  local_hostname na source_address have the same
    meaning kama they do kwenye the SMTP class.  To specify a Unix socket,
    you must use an absolute path kama the host, starting ukijumuisha a '/'.

    Authentication ni supported, using the regular SMTP mechanism. When
    using a Unix socket, LMTP generally don't support ama require any
    authentication, but your mileage might vary."""

    ehlo_msg = "lhlo"

    eleza __init__(self, host='', port=LMTP_PORT, local_hostname=Tupu,
            source_address=Tupu):
        """Initialize a new instance."""
        SMTP.__init__(self, host, port, local_hostname=local_hostname,
                      source_address=source_address)

    eleza connect(self, host='localhost', port=0, source_address=Tupu):
        """Connect to the LMTP daemon, on either a Unix ama a TCP socket."""
        ikiwa host[0] != '/':
            rudisha SMTP.connect(self, host, port, source_address=source_address)

        # Handle Unix-domain sockets.
        jaribu:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.file = Tupu
            self.sock.connect(host)
        tatizo OSError:
            ikiwa self.debuglevel > 0:
                self._print_debug('connect fail:', host)
            ikiwa self.sock:
                self.sock.close()
            self.sock = Tupu
            raise
        (code, msg) = self.getreply()
        ikiwa self.debuglevel > 0:
            self._print_debug('connect:', msg)
        rudisha (code, msg)


# Test the sendmail method, which tests most of the others.
# Note: This always sends to localhost.
ikiwa __name__ == '__main__':
    eleza prompt(prompt):
        sys.stdout.write(prompt + ": ")
        sys.stdout.flush()
        rudisha sys.stdin.readline().strip()

    fromaddr = prompt("From")
    toaddrs = prompt("To").split(',')
    andika("Enter message, end ukijumuisha ^D:")
    msg = ''
    wakati 1:
        line = sys.stdin.readline()
        ikiwa sio line:
            koma
        msg = msg + line
    andika("Message length ni %d" % len(msg))

    server = SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
