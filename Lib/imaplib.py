"""IMAP4 client.

Based on RFC 2060.

Public class:           IMAP4
Public variable:        Debug
Public functions:       Internaldate2tuple
                        Int2AP
                        ParseFlags
                        Time2Internaldate
"""

# Author: Piers Lauder <piers@cs.su.oz.au> December 1997.
#
# Authentication code contributed by Donn Cave <donn@u.washington.edu> June 1998.
# String method conversion by ESR, February 2001.
# GET/SETACL contributed by Anthony Baxter <anthony@interlink.com.au> April 2001.
# IMAP4_SSL contributed by Tino Lange <Tino.Lange@isg.de> March 2002.
# GET/SETQUOTA contributed by Andreas Zeidler <az@kreativkombinat.de> June 2002.
# PROXYAUTH contributed by Rick Holbert <holbert.13@osu.edu> November 2002.
# GET/SETANNOTATION contributed by Tomas Lindroos <skitta@abo.fi> June 2005.

__version__ = "2.58"

agiza binascii, errno, random, re, socket, subprocess, sys, time, calendar
kutoka datetime agiza datetime, timezone, timedelta
kutoka io agiza DEFAULT_BUFFER_SIZE

jaribu:
    agiza ssl
    HAVE_SSL = Kweli
tatizo ImportError:
    HAVE_SSL = Uongo

__all__ = ["IMAP4", "IMAP4_stream", "Internaldate2tuple",
           "Int2AP", "ParseFlags", "Time2Internaldate"]

#       Globals

CRLF = b'\r\n'
Debug = 0
IMAP4_PORT = 143
IMAP4_SSL_PORT = 993
AllowedVersions = ('IMAP4REV1', 'IMAP4')        # Most recent first

# Maximal line length when calling readline(). This ni to prevent
# reading arbitrary length lines. RFC 3501 na 2060 (IMAP 4rev1)
# don't specify a line length. RFC 2683 suggests limiting client
# command lines to 1000 octets na that servers should be prepared
# to accept command lines up to 8000 octets, so we used to use 10K here.
# In the modern world (eg: gmail) the response to, kila example, a
# search command can be quite large, so we now use 1M.
_MAXLINE = 1000000


#       Commands

Commands = {
        # name            valid states
        'APPEND':       ('AUTH', 'SELECTED'),
        'AUTHENTICATE': ('NONAUTH',),
        'CAPABILITY':   ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'CHECK':        ('SELECTED',),
        'CLOSE':        ('SELECTED',),
        'COPY':         ('SELECTED',),
        'CREATE':       ('AUTH', 'SELECTED'),
        'DELETE':       ('AUTH', 'SELECTED'),
        'DELETEACL':    ('AUTH', 'SELECTED'),
        'ENABLE':       ('AUTH', ),
        'EXAMINE':      ('AUTH', 'SELECTED'),
        'EXPUNGE':      ('SELECTED',),
        'FETCH':        ('SELECTED',),
        'GETACL':       ('AUTH', 'SELECTED'),
        'GETANNOTATION':('AUTH', 'SELECTED'),
        'GETQUOTA':     ('AUTH', 'SELECTED'),
        'GETQUOTAROOT': ('AUTH', 'SELECTED'),
        'MYRIGHTS':     ('AUTH', 'SELECTED'),
        'LIST':         ('AUTH', 'SELECTED'),
        'LOGIN':        ('NONAUTH',),
        'LOGOUT':       ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'LSUB':         ('AUTH', 'SELECTED'),
        'MOVE':         ('SELECTED',),
        'NAMESPACE':    ('AUTH', 'SELECTED'),
        'NOOP':         ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'PARTIAL':      ('SELECTED',),                                  # NB: obsolete
        'PROXYAUTH':    ('AUTH',),
        'RENAME':       ('AUTH', 'SELECTED'),
        'SEARCH':       ('SELECTED',),
        'SELECT':       ('AUTH', 'SELECTED'),
        'SETACL':       ('AUTH', 'SELECTED'),
        'SETANNOTATION':('AUTH', 'SELECTED'),
        'SETQUOTA':     ('AUTH', 'SELECTED'),
        'SORT':         ('SELECTED',),
        'STARTTLS':     ('NONAUTH',),
        'STATUS':       ('AUTH', 'SELECTED'),
        'STORE':        ('SELECTED',),
        'SUBSCRIBE':    ('AUTH', 'SELECTED'),
        'THREAD':       ('SELECTED',),
        'UID':          ('SELECTED',),
        'UNSUBSCRIBE':  ('AUTH', 'SELECTED'),
        }

#       Patterns to match server responses

Continuation = re.compile(br'\+( (?P<data>.*))?')
Flags = re.compile(br'.*FLAGS \((?P<flags>[^\)]*)\)')
InternalDate = re.compile(br'.*INTERNALDATE "'
        br'(?P<day>[ 0123][0-9])-(?P<mon>[A-Z][a-z][a-z])-(?P<year>[0-9][0-9][0-9][0-9])'
        br' (?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9])'
        br' (?P<zonen>[-+])(?P<zoneh>[0-9][0-9])(?P<zonem>[0-9][0-9])'
        br'"')
# Literal ni no longer used; kept kila backward compatibility.
Literal = re.compile(br'.*{(?P<size>\d+)}$', re.ASCII)
MapCRLF = re.compile(br'\r\n|\r|\n')
# We no longer exclude the ']' character kutoka the data portion of the response
# code, even though it violates the RFC.  Popular IMAP servers such kama Gmail
# allow flags ukijumuisha ']', na there are programs (including imaplib!) that can
# produce them.  The problem ukijumuisha this ni ikiwa the 'text' portion of the response
# includes a ']' we'll parse the response wrong (which ni the point of the RFC
# restriction).  However, that seems less likely to be a problem kwenye practice
# than being unable to correctly parse flags that include ']' chars, which
# was reported kama a real-world problem kwenye issue #21815.
Response_code = re.compile(br'\[(?P<type>[A-Z-]+)( (?P<data>.*))?\]')
Untagged_response = re.compile(br'\* (?P<type>[A-Z-]+)( (?P<data>.*))?')
# Untagged_status ni no longer used; kept kila backward compatibility
Untagged_status = re.compile(
    br'\* (?P<data>\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?', re.ASCII)
# We compile these kwenye _mode_xxx.
_Literal = br'.*{(?P<size>\d+)}$'
_Untagged_status = br'\* (?P<data>\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?'



kundi IMAP4:

    r"""IMAP4 client class.

    Instantiate with: IMAP4([host[, port]])

            host - host's name (default: localhost);
            port - port number (default: standard IMAP4 port).

    All IMAP4rev1 commands are supported by methods of the same
    name (in lower-case).

    All arguments to commands are converted to strings, tatizo for
    AUTHENTICATE, na the last argument to APPEND which ni pitaed as
    an IMAP4 literal.  If necessary (the string contains any
    non-printing characters ama white-space na isn't enclosed with
    either parentheses ama double quotes) each string ni quoted.
    However, the 'pitaword' argument to the LOGIN command ni always
    quoted.  If you want to avoid having an argument string quoted
    (eg: the 'flags' argument to STORE) then enclose the string in
    parentheses (eg: "(\Deleted)").

    Each command returns a tuple: (type, [data, ...]) where 'type'
    ni usually 'OK' ama 'NO', na 'data' ni either the text kutoka the
    tagged response, ama untagged results kutoka command. Each 'data'
    ni either a string, ama a tuple. If a tuple, then the first part
    ni the header of the response, na the second part contains
    the data (ie: 'literal' value).

    Errors ashiria the exception kundi <instance>.error("<reason>").
    IMAP4 server errors ashiria <instance>.abort("<reason>"),
    which ni a sub-kundi of 'error'. Mailbox status changes
    kutoka READ-WRITE to READ-ONLY ashiria the exception class
    <instance>.readonly("<reason>"), which ni a sub-kundi of 'abort'.

    "error" exceptions imply a program error.
    "abort" exceptions imply the connection should be reset, na
            the command re-tried.
    "readonly" exceptions imply the command should be re-tried.

    Note: to use this module, you must read the RFCs pertaining to the
    IMAP4 protocol, kama the semantics of the arguments to each IMAP4
    command are left to the invoker, sio to mention the results. Also,
    most IMAP servers implement a sub-set of the commands available here.
    """

    kundi error(Exception): pita    # Logical errors - debug required
    kundi abort(error): pita        # Service errors - close na retry
    kundi readonly(abort): pita     # Mailbox status changed to READ-ONLY

    eleza __init__(self, host='', port=IMAP4_PORT):
        self.debug = Debug
        self.state = 'LOGOUT'
        self.literal = Tupu             # A literal argument to a command
        self.tagged_commands = {}       # Tagged commands awaiting response
        self.untagged_responses = {}    # {typ: [data, ...], ...}
        self.continuation_response = '' # Last continuation response
        self.is_readonly = Uongo        # READ-ONLY desired state
        self.tagnum = 0
        self._tls_established = Uongo
        self._mode_ascii()

        # Open socket to server.

        self.open(host, port)

        jaribu:
            self._connect()
        tatizo Exception:
            jaribu:
                self.shutdown()
            tatizo OSError:
                pita
            raise

    eleza _mode_ascii(self):
        self.utf8_enabled = Uongo
        self._encoding = 'ascii'
        self.Literal = re.compile(_Literal, re.ASCII)
        self.Untagged_status = re.compile(_Untagged_status, re.ASCII)


    eleza _mode_utf8(self):
        self.utf8_enabled = Kweli
        self._encoding = 'utf-8'
        self.Literal = re.compile(_Literal)
        self.Untagged_status = re.compile(_Untagged_status)


    eleza _connect(self):
        # Create unique tag kila this session,
        # na compile tagged response matcher.

        self.tagpre = Int2AP(random.randint(4096, 65535))
        self.tagre = re.compile(br'(?P<tag>'
                        + self.tagpre
                        + br'\d+) (?P<type>[A-Z]+) (?P<data>.*)', re.ASCII)

        # Get server welcome message,
        # request na store CAPABILITY response.

        ikiwa __debug__:
            self._cmd_log_len = 10
            self._cmd_log_idx = 0
            self._cmd_log = {}           # Last `_cmd_log_len' interactions
            ikiwa self.debug >= 1:
                self._mesg('imaplib version %s' % __version__)
                self._mesg('new IMAP4 connection, tag=%s' % self.tagpre)

        self.welcome = self._get_response()
        ikiwa 'PREAUTH' kwenye self.untagged_responses:
            self.state = 'AUTH'
        lasivyo 'OK' kwenye self.untagged_responses:
            self.state = 'NONAUTH'
        isipokua:
            ashiria self.error(self.welcome)

        self._get_capabilities()
        ikiwa __debug__:
            ikiwa self.debug >= 3:
                self._mesg('CAPABILITIES: %r' % (self.capabilities,))

        kila version kwenye AllowedVersions:
            ikiwa sio version kwenye self.capabilities:
                endelea
            self.PROTOCOL_VERSION = version
            rudisha

        ashiria self.error('server sio IMAP4 compliant')


    eleza __getattr__(self, attr):
        #       Allow UPPERCASE variants of IMAP4 command methods.
        ikiwa attr kwenye Commands:
            rudisha getattr(self, attr.lower())
        ashiria AttributeError("Unknown IMAP4 command: '%s'" % attr)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        ikiwa self.state == "LOGOUT":
            rudisha

        jaribu:
            self.logout()
        tatizo OSError:
            pita


    #       Overridable methods


    eleza _create_socket(self):
        # Default value of IMAP4.host ni '', but socket.getaddrinfo()
        # (which ni used by socket.create_connection()) expects Tupu
        # kama a default value kila host.
        host = Tupu ikiwa sio self.host isipokua self.host
        sys.audit("imaplib.open", self, self.host, self.port)
        rudisha socket.create_connection((host, self.port))

    eleza open(self, host = '', port = IMAP4_PORT):
        """Setup connection to remote server on "host:port"
            (default: localhost:standard IMAP4 port).
        This connection will be used by the routines:
            read, readline, send, shutdown.
        """
        self.host = host
        self.port = port
        self.sock = self._create_socket()
        self.file = self.sock.makefile('rb')


    eleza read(self, size):
        """Read 'size' bytes kutoka remote."""
        rudisha self.file.read(size)


    eleza readline(self):
        """Read line kutoka remote."""
        line = self.file.readline(_MAXLINE + 1)
        ikiwa len(line) > _MAXLINE:
            ashiria self.error("got more than %d bytes" % _MAXLINE)
        rudisha line


    eleza send(self, data):
        """Send data to remote."""
        sys.audit("imaplib.send", self, data)
        self.sock.sendall(data)


    eleza shutdown(self):
        """Close I/O established kwenye "open"."""
        self.file.close()
        jaribu:
            self.sock.shutdown(socket.SHUT_RDWR)
        tatizo OSError kama exc:
            # The server might already have closed the connection.
            # On Windows, this may result kwenye WSAEINVAL (error 10022):
            # An invalid operation was attempted.
            ikiwa (exc.errno != errno.ENOTCONN
               na getattr(exc, 'winerror', 0) != 10022):
                raise
        mwishowe:
            self.sock.close()


    eleza socket(self):
        """Return socket instance used to connect to IMAP4 server.

        socket = <instance>.socket()
        """
        rudisha self.sock



    #       Utility methods


    eleza recent(self):
        """Return most recent 'RECENT' responses ikiwa any exist,
        isipokua prompt server kila an update using the 'NOOP' command.

        (typ, [data]) = <instance>.recent()

        'data' ni Tupu ikiwa no new messages,
        isipokua list of RECENT responses, most recent last.
        """
        name = 'RECENT'
        typ, dat = self._untagged_response('OK', [Tupu], name)
        ikiwa dat[-1]:
            rudisha typ, dat
        typ, dat = self.noop()  # Prod server kila response
        rudisha self._untagged_response(typ, dat, name)


    eleza response(self, code):
        """Return data kila response 'code' ikiwa received, ama Tupu.

        Old value kila response 'code' ni cleared.

        (code, [data]) = <instance>.response(code)
        """
        rudisha self._untagged_response(code, [Tupu], code.upper())



    #       IMAP4 commands


    eleza append(self, mailbox, flags, date_time, message):
        """Append message to named mailbox.

        (typ, [data]) = <instance>.append(mailbox, flags, date_time, message)

                All args tatizo `message' can be Tupu.
        """
        name = 'APPEND'
        ikiwa sio mailbox:
            mailbox = 'INBOX'
        ikiwa flags:
            ikiwa (flags[0],flags[-1]) != ('(',')'):
                flags = '(%s)' % flags
        isipokua:
            flags = Tupu
        ikiwa date_time:
            date_time = Time2Internaldate(date_time)
        isipokua:
            date_time = Tupu
        literal = MapCRLF.sub(CRLF, message)
        ikiwa self.utf8_enabled:
            literal = b'UTF8 (' + literal + b')'
        self.literal = literal
        rudisha self._simple_command(name, mailbox, flags, date_time)


    eleza authenticate(self, mechanism, authobject):
        """Authenticate command - requires response processing.

        'mechanism' specifies which authentication mechanism ni to
        be used - it must appear kwenye <instance>.capabilities kwenye the
        form AUTH=<mechanism>.

        'authobject' must be a callable object:

                data = authobject(response)

        It will be called to process server continuation responses; the
        response argument it ni pitaed will be a bytes.  It should rudisha bytes
        data that will be base64 encoded na sent to the server.  It should
        rudisha Tupu ikiwa the client abort response '*' should be sent instead.
        """
        mech = mechanism.upper()
        # XXX: shouldn't this code be removed, sio commented out?
        #cap = 'AUTH=%s' % mech
        #ikiwa sio cap kwenye self.capabilities:       # Let the server decide!
        #    ashiria self.error("Server doesn't allow %s authentication." % mech)
        self.literal = _Authenticator(authobject).process
        typ, dat = self._simple_command('AUTHENTICATE', mech)
        ikiwa typ != 'OK':
            ashiria self.error(dat[-1].decode('utf-8', 'replace'))
        self.state = 'AUTH'
        rudisha typ, dat


    eleza capability(self):
        """(typ, [data]) = <instance>.capability()
        Fetch capabilities list kutoka server."""

        name = 'CAPABILITY'
        typ, dat = self._simple_command(name)
        rudisha self._untagged_response(typ, dat, name)


    eleza check(self):
        """Checkpoint mailbox on server.

        (typ, [data]) = <instance>.check()
        """
        rudisha self._simple_command('CHECK')


    eleza close(self):
        """Close currently selected mailbox.

        Deleted messages are removed kutoka writable mailbox.
        This ni the recommended command before 'LOGOUT'.

        (typ, [data]) = <instance>.close()
        """
        jaribu:
            typ, dat = self._simple_command('CLOSE')
        mwishowe:
            self.state = 'AUTH'
        rudisha typ, dat


    eleza copy(self, message_set, new_mailbox):
        """Copy 'message_set' messages onto end of 'new_mailbox'.

        (typ, [data]) = <instance>.copy(message_set, new_mailbox)
        """
        rudisha self._simple_command('COPY', message_set, new_mailbox)


    eleza create(self, mailbox):
        """Create new mailbox.

        (typ, [data]) = <instance>.create(mailbox)
        """
        rudisha self._simple_command('CREATE', mailbox)


    eleza delete(self, mailbox):
        """Delete old mailbox.

        (typ, [data]) = <instance>.delete(mailbox)
        """
        rudisha self._simple_command('DELETE', mailbox)

    eleza deleteacl(self, mailbox, who):
        """Delete the ACLs (remove any rights) set kila who on mailbox.

        (typ, [data]) = <instance>.deleteacl(mailbox, who)
        """
        rudisha self._simple_command('DELETEACL', mailbox, who)

    eleza enable(self, capability):
        """Send an RFC5161 enable string to the server.

        (typ, [data]) = <intance>.enable(capability)
        """
        ikiwa 'ENABLE' haiko kwenye self.capabilities:
            ashiria IMAP4.error("Server does sio support ENABLE")
        typ, data = self._simple_command('ENABLE', capability)
        ikiwa typ == 'OK' na 'UTF8=ACCEPT' kwenye capability.upper():
            self._mode_utf8()
        rudisha typ, data

    eleza expunge(self):
        """Permanently remove deleted items kutoka selected mailbox.

        Generates 'EXPUNGE' response kila each deleted message.

        (typ, [data]) = <instance>.expunge()

        'data' ni list of 'EXPUNGE'd message numbers kwenye order received.
        """
        name = 'EXPUNGE'
        typ, dat = self._simple_command(name)
        rudisha self._untagged_response(typ, dat, name)


    eleza fetch(self, message_set, message_parts):
        """Fetch (parts of) messages.

        (typ, [data, ...]) = <instance>.fetch(message_set, message_parts)

        'message_parts' should be a string of selected parts
        enclosed kwenye parentheses, eg: "(UID BODY[TEXT])".

        'data' are tuples of message part envelope na data.
        """
        name = 'FETCH'
        typ, dat = self._simple_command(name, message_set, message_parts)
        rudisha self._untagged_response(typ, dat, name)


    eleza getacl(self, mailbox):
        """Get the ACLs kila a mailbox.

        (typ, [data]) = <instance>.getacl(mailbox)
        """
        typ, dat = self._simple_command('GETACL', mailbox)
        rudisha self._untagged_response(typ, dat, 'ACL')


    eleza getannotation(self, mailbox, entry, attribute):
        """(typ, [data]) = <instance>.getannotation(mailbox, entry, attribute)
        Retrieve ANNOTATIONs."""

        typ, dat = self._simple_command('GETANNOTATION', mailbox, entry, attribute)
        rudisha self._untagged_response(typ, dat, 'ANNOTATION')


    eleza getquota(self, root):
        """Get the quota root's resource usage na limits.

        Part of the IMAP4 QUOTA extension defined kwenye rfc2087.

        (typ, [data]) = <instance>.getquota(root)
        """
        typ, dat = self._simple_command('GETQUOTA', root)
        rudisha self._untagged_response(typ, dat, 'QUOTA')


    eleza getquotaroot(self, mailbox):
        """Get the list of quota roots kila the named mailbox.

        (typ, [[QUOTAROOT responses...], [QUOTA responses]]) = <instance>.getquotaroot(mailbox)
        """
        typ, dat = self._simple_command('GETQUOTAROOT', mailbox)
        typ, quota = self._untagged_response(typ, dat, 'QUOTA')
        typ, quotaroot = self._untagged_response(typ, dat, 'QUOTAROOT')
        rudisha typ, [quotaroot, quota]


    eleza list(self, directory='""', pattern='*'):
        """List mailbox names kwenye directory matching pattern.

        (typ, [data]) = <instance>.list(directory='""', pattern='*')

        'data' ni list of LIST responses.
        """
        name = 'LIST'
        typ, dat = self._simple_command(name, directory, pattern)
        rudisha self._untagged_response(typ, dat, name)


    eleza login(self, user, pitaword):
        """Identify client using plaintext pitaword.

        (typ, [data]) = <instance>.login(user, pitaword)

        NB: 'pitaword' will be quoted.
        """
        typ, dat = self._simple_command('LOGIN', user, self._quote(pitaword))
        ikiwa typ != 'OK':
            ashiria self.error(dat[-1])
        self.state = 'AUTH'
        rudisha typ, dat


    eleza login_cram_md5(self, user, pitaword):
        """ Force use of CRAM-MD5 authentication.

        (typ, [data]) = <instance>.login_cram_md5(user, pitaword)
        """
        self.user, self.pitaword = user, pitaword
        rudisha self.authenticate('CRAM-MD5', self._CRAM_MD5_AUTH)


    eleza _CRAM_MD5_AUTH(self, challenge):
        """ Authobject to use ukijumuisha CRAM-MD5 authentication. """
        agiza hmac
        pwd = (self.pitaword.encode('utf-8') ikiwa isinstance(self.pitaword, str)
                                             isipokua self.pitaword)
        rudisha self.user + " " + hmac.HMAC(pwd, challenge, 'md5').hexdigest()


    eleza logout(self):
        """Shutdown connection to server.

        (typ, [data]) = <instance>.logout()

        Returns server 'BYE' response.
        """
        self.state = 'LOGOUT'
        typ, dat = self._simple_command('LOGOUT')
        self.shutdown()
        rudisha typ, dat


    eleza lsub(self, directory='""', pattern='*'):
        """List 'subscribed' mailbox names kwenye directory matching pattern.

        (typ, [data, ...]) = <instance>.lsub(directory='""', pattern='*')

        'data' are tuples of message part envelope na data.
        """
        name = 'LSUB'
        typ, dat = self._simple_command(name, directory, pattern)
        rudisha self._untagged_response(typ, dat, name)

    eleza myrights(self, mailbox):
        """Show my ACLs kila a mailbox (i.e. the rights that I have on mailbox).

        (typ, [data]) = <instance>.myrights(mailbox)
        """
        typ,dat = self._simple_command('MYRIGHTS', mailbox)
        rudisha self._untagged_response(typ, dat, 'MYRIGHTS')

    eleza namespace(self):
        """ Returns IMAP namespaces ala rfc2342

        (typ, [data, ...]) = <instance>.namespace()
        """
        name = 'NAMESPACE'
        typ, dat = self._simple_command(name)
        rudisha self._untagged_response(typ, dat, name)


    eleza noop(self):
        """Send NOOP command.

        (typ, [data]) = <instance>.noop()
        """
        ikiwa __debug__:
            ikiwa self.debug >= 3:
                self._dump_ur(self.untagged_responses)
        rudisha self._simple_command('NOOP')


    eleza partial(self, message_num, message_part, start, length):
        """Fetch truncated part of a message.

        (typ, [data, ...]) = <instance>.partial(message_num, message_part, start, length)

        'data' ni tuple of message part envelope na data.
        """
        name = 'PARTIAL'
        typ, dat = self._simple_command(name, message_num, message_part, start, length)
        rudisha self._untagged_response(typ, dat, 'FETCH')


    eleza proxyauth(self, user):
        """Assume authentication kama "user".

        Allows an authorised administrator to proxy into any user's
        mailbox.

        (typ, [data]) = <instance>.proxyauth(user)
        """

        name = 'PROXYAUTH'
        rudisha self._simple_command('PROXYAUTH', user)


    eleza rename(self, oldmailbox, newmailbox):
        """Rename old mailbox name to new.

        (typ, [data]) = <instance>.rename(oldmailbox, newmailbox)
        """
        rudisha self._simple_command('RENAME', oldmailbox, newmailbox)


    eleza search(self, charset, *criteria):
        """Search mailbox kila matching messages.

        (typ, [data]) = <instance>.search(charset, criterion, ...)

        'data' ni space separated list of matching message numbers.
        If UTF8 ni enabled, charset MUST be Tupu.
        """
        name = 'SEARCH'
        ikiwa charset:
            ikiwa self.utf8_enabled:
                ashiria IMAP4.error("Non-Tupu charset sio valid kwenye UTF8 mode")
            typ, dat = self._simple_command(name, 'CHARSET', charset, *criteria)
        isipokua:
            typ, dat = self._simple_command(name, *criteria)
        rudisha self._untagged_response(typ, dat, name)


    eleza select(self, mailbox='INBOX', readonly=Uongo):
        """Select a mailbox.

        Flush all untagged responses.

        (typ, [data]) = <instance>.select(mailbox='INBOX', readonly=Uongo)

        'data' ni count of messages kwenye mailbox ('EXISTS' response).

        Mandated responses are ('FLAGS', 'EXISTS', 'RECENT', 'UIDVALIDITY'), so
        other responses should be obtained via <instance>.response('FLAGS') etc.
        """
        self.untagged_responses = {}    # Flush old responses.
        self.is_readonly = readonly
        ikiwa readonly:
            name = 'EXAMINE'
        isipokua:
            name = 'SELECT'
        typ, dat = self._simple_command(name, mailbox)
        ikiwa typ != 'OK':
            self.state = 'AUTH'     # Might have been 'SELECTED'
            rudisha typ, dat
        self.state = 'SELECTED'
        ikiwa 'READ-ONLY' kwenye self.untagged_responses \
                na sio readonly:
            ikiwa __debug__:
                ikiwa self.debug >= 1:
                    self._dump_ur(self.untagged_responses)
            ashiria self.readonly('%s ni sio writable' % mailbox)
        rudisha typ, self.untagged_responses.get('EXISTS', [Tupu])


    eleza setacl(self, mailbox, who, what):
        """Set a mailbox acl.

        (typ, [data]) = <instance>.setacl(mailbox, who, what)
        """
        rudisha self._simple_command('SETACL', mailbox, who, what)


    eleza setannotation(self, *args):
        """(typ, [data]) = <instance>.setannotation(mailbox[, entry, attribute]+)
        Set ANNOTATIONs."""

        typ, dat = self._simple_command('SETANNOTATION', *args)
        rudisha self._untagged_response(typ, dat, 'ANNOTATION')


    eleza setquota(self, root, limits):
        """Set the quota root's resource limits.

        (typ, [data]) = <instance>.setquota(root, limits)
        """
        typ, dat = self._simple_command('SETQUOTA', root, limits)
        rudisha self._untagged_response(typ, dat, 'QUOTA')


    eleza sort(self, sort_criteria, charset, *search_criteria):
        """IMAP4rev1 extension SORT command.

        (typ, [data]) = <instance>.sort(sort_criteria, charset, search_criteria, ...)
        """
        name = 'SORT'
        #ikiwa sio name kwenye self.capabilities:      # Let the server decide!
        #       ashiria self.error('unimplemented extension command: %s' % name)
        ikiwa (sort_criteria[0],sort_criteria[-1]) != ('(',')'):
            sort_criteria = '(%s)' % sort_criteria
        typ, dat = self._simple_command(name, sort_criteria, charset, *search_criteria)
        rudisha self._untagged_response(typ, dat, name)


    eleza starttls(self, ssl_context=Tupu):
        name = 'STARTTLS'
        ikiwa sio HAVE_SSL:
            ashiria self.error('SSL support missing')
        ikiwa self._tls_established:
            ashiria self.abort('TLS session already established')
        ikiwa name haiko kwenye self.capabilities:
            ashiria self.abort('TLS sio supported by server')
        # Generate a default SSL context ikiwa none was pitaed.
        ikiwa ssl_context ni Tupu:
            ssl_context = ssl._create_stdlib_context()
        typ, dat = self._simple_command(name)
        ikiwa typ == 'OK':
            self.sock = ssl_context.wrap_socket(self.sock,
                                                server_hostname=self.host)
            self.file = self.sock.makefile('rb')
            self._tls_established = Kweli
            self._get_capabilities()
        isipokua:
            ashiria self.error("Couldn't establish TLS session")
        rudisha self._untagged_response(typ, dat, name)


    eleza status(self, mailbox, names):
        """Request named status conditions kila mailbox.

        (typ, [data]) = <instance>.status(mailbox, names)
        """
        name = 'STATUS'
        #ikiwa self.PROTOCOL_VERSION == 'IMAP4':   # Let the server decide!
        #    ashiria self.error('%s unimplemented kwenye IMAP4 (obtain IMAP4rev1 server, ama re-code)' % name)
        typ, dat = self._simple_command(name, mailbox, names)
        rudisha self._untagged_response(typ, dat, name)


    eleza store(self, message_set, command, flags):
        """Alters flag dispositions kila messages kwenye mailbox.

        (typ, [data]) = <instance>.store(message_set, command, flags)
        """
        ikiwa (flags[0],flags[-1]) != ('(',')'):
            flags = '(%s)' % flags  # Avoid quoting the flags
        typ, dat = self._simple_command('STORE', message_set, command, flags)
        rudisha self._untagged_response(typ, dat, 'FETCH')


    eleza subscribe(self, mailbox):
        """Subscribe to new mailbox.

        (typ, [data]) = <instance>.subscribe(mailbox)
        """
        rudisha self._simple_command('SUBSCRIBE', mailbox)


    eleza thread(self, threading_algorithm, charset, *search_criteria):
        """IMAPrev1 extension THREAD command.

        (type, [data]) = <instance>.thread(threading_algorithm, charset, search_criteria, ...)
        """
        name = 'THREAD'
        typ, dat = self._simple_command(name, threading_algorithm, charset, *search_criteria)
        rudisha self._untagged_response(typ, dat, name)


    eleza uid(self, command, *args):
        """Execute "command arg ..." ukijumuisha messages identified by UID,
                rather than message number.

        (typ, [data]) = <instance>.uid(command, arg1, arg2, ...)

        Returns response appropriate to 'command'.
        """
        command = command.upper()
        ikiwa sio command kwenye Commands:
            ashiria self.error("Unknown IMAP4 UID command: %s" % command)
        ikiwa self.state haiko kwenye Commands[command]:
            ashiria self.error("command %s illegal kwenye state %s, "
                             "only allowed kwenye states %s" %
                             (command, self.state,
                              ', '.join(Commands[command])))
        name = 'UID'
        typ, dat = self._simple_command(name, command, *args)
        ikiwa command kwenye ('SEARCH', 'SORT', 'THREAD'):
            name = command
        isipokua:
            name = 'FETCH'
        rudisha self._untagged_response(typ, dat, name)


    eleza unsubscribe(self, mailbox):
        """Unsubscribe kutoka old mailbox.

        (typ, [data]) = <instance>.unsubscribe(mailbox)
        """
        rudisha self._simple_command('UNSUBSCRIBE', mailbox)


    eleza xatom(self, name, *args):
        """Allow simple extension commands
                notified by server kwenye CAPABILITY response.

        Assumes command ni legal kwenye current state.

        (typ, [data]) = <instance>.xatom(name, arg, ...)

        Returns response appropriate to extension command `name'.
        """
        name = name.upper()
        #ikiwa sio name kwenye self.capabilities:      # Let the server decide!
        #    ashiria self.error('unknown extension command: %s' % name)
        ikiwa sio name kwenye Commands:
            Commands[name] = (self.state,)
        rudisha self._simple_command(name, *args)



    #       Private methods


    eleza _append_untagged(self, typ, dat):
        ikiwa dat ni Tupu:
            dat = b''
        ur = self.untagged_responses
        ikiwa __debug__:
            ikiwa self.debug >= 5:
                self._mesg('untagged_responses[%s] %s += ["%r"]' %
                        (typ, len(ur.get(typ,'')), dat))
        ikiwa typ kwenye ur:
            ur[typ].append(dat)
        isipokua:
            ur[typ] = [dat]


    eleza _check_bye(self):
        bye = self.untagged_responses.get('BYE')
        ikiwa bye:
            ashiria self.abort(bye[-1].decode(self._encoding, 'replace'))


    eleza _command(self, name, *args):

        ikiwa self.state haiko kwenye Commands[name]:
            self.literal = Tupu
            ashiria self.error("command %s illegal kwenye state %s, "
                             "only allowed kwenye states %s" %
                             (name, self.state,
                              ', '.join(Commands[name])))

        kila typ kwenye ('OK', 'NO', 'BAD'):
            ikiwa typ kwenye self.untagged_responses:
                toa self.untagged_responses[typ]

        ikiwa 'READ-ONLY' kwenye self.untagged_responses \
        na sio self.is_readonly:
            ashiria self.readonly('mailbox status changed to READ-ONLY')

        tag = self._new_tag()
        name = bytes(name, self._encoding)
        data = tag + b' ' + name
        kila arg kwenye args:
            ikiwa arg ni Tupu: endelea
            ikiwa isinstance(arg, str):
                arg = bytes(arg, self._encoding)
            data = data + b' ' + arg

        literal = self.literal
        ikiwa literal ni sio Tupu:
            self.literal = Tupu
            ikiwa type(literal) ni type(self._command):
                literator = literal
            isipokua:
                literator = Tupu
                data = data + bytes(' {%s}' % len(literal), self._encoding)

        ikiwa __debug__:
            ikiwa self.debug >= 4:
                self._mesg('> %r' % data)
            isipokua:
                self._log('> %r' % data)

        jaribu:
            self.send(data + CRLF)
        tatizo OSError kama val:
            ashiria self.abort('socket error: %s' % val)

        ikiwa literal ni Tupu:
            rudisha tag

        wakati 1:
            # Wait kila continuation response

            wakati self._get_response():
                ikiwa self.tagged_commands[tag]:   # BAD/NO?
                    rudisha tag

            # Send literal

            ikiwa literator:
                literal = literator(self.continuation_response)

            ikiwa __debug__:
                ikiwa self.debug >= 4:
                    self._mesg('write literal size %s' % len(literal))

            jaribu:
                self.send(literal)
                self.send(CRLF)
            tatizo OSError kama val:
                ashiria self.abort('socket error: %s' % val)

            ikiwa sio literator:
                koma

        rudisha tag


    eleza _command_complete(self, name, tag):
        logout = (name == 'LOGOUT')
        # BYE ni expected after LOGOUT
        ikiwa sio logout:
            self._check_bye()
        jaribu:
            typ, data = self._get_tagged_response(tag, expect_bye=logout)
        tatizo self.abort kama val:
            ashiria self.abort('command: %s => %s' % (name, val))
        tatizo self.error kama val:
            ashiria self.error('command: %s => %s' % (name, val))
        ikiwa sio logout:
            self._check_bye()
        ikiwa typ == 'BAD':
            ashiria self.error('%s command error: %s %s' % (name, typ, data))
        rudisha typ, data


    eleza _get_capabilities(self):
        typ, dat = self.capability()
        ikiwa dat == [Tupu]:
            ashiria self.error('no CAPABILITY response kutoka server')
        dat = str(dat[-1], self._encoding)
        dat = dat.upper()
        self.capabilities = tuple(dat.split())


    eleza _get_response(self):

        # Read response na store.
        #
        # Returns Tupu kila continuation responses,
        # otherwise first response line received.

        resp = self._get_line()

        # Command completion response?

        ikiwa self._match(self.tagre, resp):
            tag = self.mo.group('tag')
            ikiwa sio tag kwenye self.tagged_commands:
                ashiria self.abort('unexpected tagged response: %r' % resp)

            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            dat = self.mo.group('data')
            self.tagged_commands[tag] = (typ, [dat])
        isipokua:
            dat2 = Tupu

            # '*' (untagged) responses?

            ikiwa sio self._match(Untagged_response, resp):
                ikiwa self._match(self.Untagged_status, resp):
                    dat2 = self.mo.group('data2')

            ikiwa self.mo ni Tupu:
                # Only other possibility ni '+' (continuation) response...

                ikiwa self._match(Continuation, resp):
                    self.continuation_response = self.mo.group('data')
                    rudisha Tupu     # NB: indicates continuation

                ashiria self.abort("unexpected response: %r" % resp)

            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            dat = self.mo.group('data')
            ikiwa dat ni Tupu: dat = b''        # Null untagged response
            ikiwa dat2: dat = dat + b' ' + dat2

            # Is there a literal to come?

            wakati self._match(self.Literal, dat):

                # Read literal direct kutoka connection.

                size = int(self.mo.group('size'))
                ikiwa __debug__:
                    ikiwa self.debug >= 4:
                        self._mesg('read literal size %s' % size)
                data = self.read(size)

                # Store response ukijumuisha literal kama tuple

                self._append_untagged(typ, (dat, data))

                # Read trailer - possibly containing another literal

                dat = self._get_line()

            self._append_untagged(typ, dat)

        # Bracketed response information?

        ikiwa typ kwenye ('OK', 'NO', 'BAD') na self._match(Response_code, dat):
            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            self._append_untagged(typ, self.mo.group('data'))

        ikiwa __debug__:
            ikiwa self.debug >= 1 na typ kwenye ('NO', 'BAD', 'BYE'):
                self._mesg('%s response: %r' % (typ, dat))

        rudisha resp


    eleza _get_tagged_response(self, tag, expect_bye=Uongo):

        wakati 1:
            result = self.tagged_commands[tag]
            ikiwa result ni sio Tupu:
                toa self.tagged_commands[tag]
                rudisha result

            ikiwa expect_bye:
                typ = 'BYE'
                bye = self.untagged_responses.pop(typ, Tupu)
                ikiwa bye ni sio Tupu:
                    # Server replies to the "LOGOUT" command ukijumuisha "BYE"
                    rudisha (typ, bye)

            # If we've seen a BYE at this point, the socket will be
            # closed, so report the BYE now.
            self._check_bye()

            # Some have reported "unexpected response" exceptions.
            # Note that ignoring them here causes loops.
            # Instead, send me details of the unexpected response na
            # I'll update the code kwenye `_get_response()'.

            jaribu:
                self._get_response()
            tatizo self.abort kama val:
                ikiwa __debug__:
                    ikiwa self.debug >= 1:
                        self.print_log()
                raise


    eleza _get_line(self):

        line = self.readline()
        ikiwa sio line:
            ashiria self.abort('socket error: EOF')

        # Protocol mandates all lines terminated by CRLF
        ikiwa sio line.endswith(b'\r\n'):
            ashiria self.abort('socket error: unterminated line: %r' % line)

        line = line[:-2]
        ikiwa __debug__:
            ikiwa self.debug >= 4:
                self._mesg('< %r' % line)
            isipokua:
                self._log('< %r' % line)
        rudisha line


    eleza _match(self, cre, s):

        # Run compiled regular expression match method on 's'.
        # Save result, rudisha success.

        self.mo = cre.match(s)
        ikiwa __debug__:
            ikiwa self.mo ni sio Tupu na self.debug >= 5:
                self._mesg("\tmatched %r => %r" % (cre.pattern, self.mo.groups()))
        rudisha self.mo ni sio Tupu


    eleza _new_tag(self):

        tag = self.tagpre + bytes(str(self.tagnum), self._encoding)
        self.tagnum = self.tagnum + 1
        self.tagged_commands[tag] = Tupu
        rudisha tag


    eleza _quote(self, arg):

        arg = arg.replace('\\', '\\\\')
        arg = arg.replace('"', '\\"')

        rudisha '"' + arg + '"'


    eleza _simple_command(self, name, *args):

        rudisha self._command_complete(name, self._command(name, *args))


    eleza _untagged_response(self, typ, dat, name):
        ikiwa typ == 'NO':
            rudisha typ, dat
        ikiwa sio name kwenye self.untagged_responses:
            rudisha typ, [Tupu]
        data = self.untagged_responses.pop(name)
        ikiwa __debug__:
            ikiwa self.debug >= 5:
                self._mesg('untagged_responses[%s] => %s' % (name, data))
        rudisha typ, data


    ikiwa __debug__:

        eleza _mesg(self, s, secs=Tupu):
            ikiwa secs ni Tupu:
                secs = time.time()
            tm = time.strftime('%M:%S', time.localtime(secs))
            sys.stderr.write('  %s.%02d %s\n' % (tm, (secs*100)%100, s))
            sys.stderr.flush()

        eleza _dump_ur(self, dict):
            # Dump untagged responses (in `dict').
            l = dict.items()
            ikiwa sio l: rudisha
            t = '\n\t\t'
            l = map(lambda x:'%s: "%s"' % (x[0], x[1][0] na '" "'.join(x[1]) ama ''), l)
            self._mesg('untagged responses dump:%s%s' % (t, t.join(l)))

        eleza _log(self, line):
            # Keep log of last `_cmd_log_len' interactions kila debugging.
            self._cmd_log[self._cmd_log_idx] = (line, time.time())
            self._cmd_log_idx += 1
            ikiwa self._cmd_log_idx >= self._cmd_log_len:
                self._cmd_log_idx = 0

        eleza print_log(self):
            self._mesg('last %d IMAP4 interactions:' % len(self._cmd_log))
            i, n = self._cmd_log_idx, self._cmd_log_len
            wakati n:
                jaribu:
                    self._mesg(*self._cmd_log[i])
                tatizo:
                    pita
                i += 1
                ikiwa i >= self._cmd_log_len:
                    i = 0
                n -= 1


ikiwa HAVE_SSL:

    kundi IMAP4_SSL(IMAP4):

        """IMAP4 client kundi over SSL connection

        Instantiate with: IMAP4_SSL([host[, port[, keyfile[, certfile[, ssl_context]]]]])

                host - host's name (default: localhost);
                port - port number (default: standard IMAP4 SSL port);
                keyfile - PEM formatted file that contains your private key (default: Tupu);
                certfile - PEM formatted certificate chain file (default: Tupu);
                ssl_context - a SSLContext object that contains your certificate chain
                              na private key (default: Tupu)
                Note: ikiwa ssl_context ni provided, then parameters keyfile ama
                certfile should sio be set otherwise ValueError ni raised.

        kila more documentation see the docstring of the parent kundi IMAP4.
        """


        eleza __init__(self, host='', port=IMAP4_SSL_PORT, keyfile=Tupu,
                     certfile=Tupu, ssl_context=Tupu):
            ikiwa ssl_context ni sio Tupu na keyfile ni sio Tupu:
                ashiria ValueError("ssl_context na keyfile arguments are mutually "
                                 "exclusive")
            ikiwa ssl_context ni sio Tupu na certfile ni sio Tupu:
                ashiria ValueError("ssl_context na certfile arguments are mutually "
                                 "exclusive")
            ikiwa keyfile ni sio Tupu ama certfile ni sio Tupu:
                agiza warnings
                warnings.warn("keyfile na certfile are deprecated, use a "
                              "custom ssl_context instead", DeprecationWarning, 2)
            self.keyfile = keyfile
            self.certfile = certfile
            ikiwa ssl_context ni Tupu:
                ssl_context = ssl._create_stdlib_context(certfile=certfile,
                                                         keyfile=keyfile)
            self.ssl_context = ssl_context
            IMAP4.__init__(self, host, port)

        eleza _create_socket(self):
            sock = IMAP4._create_socket(self)
            rudisha self.ssl_context.wrap_socket(sock,
                                                server_hostname=self.host)

        eleza open(self, host='', port=IMAP4_SSL_PORT):
            """Setup connection to remote server on "host:port".
                (default: localhost:standard IMAP4 SSL port).
            This connection will be used by the routines:
                read, readline, send, shutdown.
            """
            IMAP4.open(self, host, port)

    __all__.append("IMAP4_SSL")


kundi IMAP4_stream(IMAP4):

    """IMAP4 client kundi over a stream

    Instantiate with: IMAP4_stream(command)

            "command" - a string that can be pitaed to subprocess.Popen()

    kila more documentation see the docstring of the parent kundi IMAP4.
    """


    eleza __init__(self, command):
        self.command = command
        IMAP4.__init__(self)


    eleza open(self, host = Tupu, port = Tupu):
        """Setup a stream connection.
        This connection will be used by the routines:
            read, readline, send, shutdown.
        """
        self.host = Tupu        # For compatibility ukijumuisha parent class
        self.port = Tupu
        self.sock = Tupu
        self.file = Tupu
        self.process = subprocess.Popen(self.command,
            bufsize=DEFAULT_BUFFER_SIZE,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            shell=Kweli, close_fds=Kweli)
        self.writefile = self.process.stdin
        self.readfile = self.process.stdout

    eleza read(self, size):
        """Read 'size' bytes kutoka remote."""
        rudisha self.readfile.read(size)


    eleza readline(self):
        """Read line kutoka remote."""
        rudisha self.readfile.readline()


    eleza send(self, data):
        """Send data to remote."""
        self.writefile.write(data)
        self.writefile.flush()


    eleza shutdown(self):
        """Close I/O established kwenye "open"."""
        self.readfile.close()
        self.writefile.close()
        self.process.wait()



kundi _Authenticator:

    """Private kundi to provide en/decoding
            kila base64-based authentication conversation.
    """

    eleza __init__(self, mechinst):
        self.mech = mechinst    # Callable object to provide/process data

    eleza process(self, data):
        ret = self.mech(self.decode(data))
        ikiwa ret ni Tupu:
            rudisha b'*'     # Abort conversation
        rudisha self.encode(ret)

    eleza encode(self, inp):
        #
        #  Invoke binascii.b2a_base64 iteratively with
        #  short even length buffers, strip the trailing
        #  line feed kutoka the result na append.  "Even"
        #  means a number that factors to both 6 na 8,
        #  so when it gets to the end of the 8-bit input
        #  there's no partial 6-bit output.
        #
        oup = b''
        ikiwa isinstance(inp, str):
            inp = inp.encode('utf-8')
        wakati inp:
            ikiwa len(inp) > 48:
                t = inp[:48]
                inp = inp[48:]
            isipokua:
                t = inp
                inp = b''
            e = binascii.b2a_base64(t)
            ikiwa e:
                oup = oup + e[:-1]
        rudisha oup

    eleza decode(self, inp):
        ikiwa sio in:
            rudisha b''
        rudisha binascii.a2b_base64(inp)

Months = ' Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
Mon2num = {s.encode():n+1 kila n, s kwenye enumerate(Months[1:])}

eleza Internaldate2tuple(resp):
    """Parse an IMAP4 INTERNALDATE string.

    Return corresponding local time.  The rudisha value ni a
    time.struct_time tuple ama Tupu ikiwa the string has wrong format.
    """

    mo = InternalDate.match(resp)
    ikiwa sio mo:
        rudisha Tupu

    mon = Mon2num[mo.group('mon')]
    zonen = mo.group('zonen')

    day = int(mo.group('day'))
    year = int(mo.group('year'))
    hour = int(mo.group('hour'))
    min = int(mo.group('min'))
    sec = int(mo.group('sec'))
    zoneh = int(mo.group('zoneh'))
    zonem = int(mo.group('zonem'))

    # INTERNALDATE timezone must be subtracted to get UT

    zone = (zoneh*60 + zonem)*60
    ikiwa zonen == b'-':
        zone = -zone

    tt = (year, mon, day, hour, min, sec, -1, -1, -1)
    utc = calendar.timegm(tt) - zone

    rudisha time.localtime(utc)



eleza Int2AP(num):

    """Convert integer to A-P string representation."""

    val = b''; AP = b'ABCDEFGHIJKLMNOP'
    num = int(abs(num))
    wakati num:
        num, mod = divmod(num, 16)
        val = AP[mod:mod+1] + val
    rudisha val



eleza ParseFlags(resp):

    """Convert IMAP4 flags response to python tuple."""

    mo = Flags.match(resp)
    ikiwa sio mo:
        rudisha ()

    rudisha tuple(mo.group('flags').split())


eleza Time2Internaldate(date_time):

    """Convert date_time to IMAP4 INTERNALDATE representation.

    Return string kwenye form: '"DD-Mmm-YYYY HH:MM:SS +HHMM"'.  The
    date_time argument can be a number (int ama float) representing
    seconds since epoch (as returned by time.time()), a 9-tuple
    representing local time, an instance of time.struct_time (as
    returned by time.localtime()), an aware datetime instance ama a
    double-quoted string.  In the last case, it ni assumed to already
    be kwenye the correct format.
    """
    ikiwa isinstance(date_time, (int, float)):
        dt = datetime.fromtimestamp(date_time,
                                    timezone.utc).astimezone()
    lasivyo isinstance(date_time, tuple):
        jaribu:
            gmtoff = date_time.tm_gmtoff
        tatizo AttributeError:
            ikiwa time.daylight:
                dst = date_time[8]
                ikiwa dst == -1:
                    dst = time.localtime(time.mktime(date_time))[8]
                gmtoff = -(time.timezone, time.altzone)[dst]
            isipokua:
                gmtoff = -time.timezone
        delta = timedelta(seconds=gmtoff)
        dt = datetime(*date_time[:6], tzinfo=timezone(delta))
    lasivyo isinstance(date_time, datetime):
        ikiwa date_time.tzinfo ni Tupu:
            ashiria ValueError("date_time must be aware")
        dt = date_time
    lasivyo isinstance(date_time, str) na (date_time[0],date_time[-1]) == ('"','"'):
        rudisha date_time        # Assume kwenye correct format
    isipokua:
        ashiria ValueError("date_time sio of a known type")
    fmt = '"%d-{}-%Y %H:%M:%S %z"'.format(Months[dt.month])
    rudisha dt.strftime(fmt)



ikiwa __name__ == '__main__':

    # To test: invoke either kama 'python imaplib.py [IMAP4_server_hostname]'
    # ama 'python imaplib.py -s "rsh IMAP4_server_hostname exec /etc/rimapd"'
    # to test the IMAP4_stream class

    agiza getopt, getpita

    jaribu:
        optlist, args = getopt.getopt(sys.argv[1:], 'd:s:')
    tatizo getopt.error kama val:
        optlist, args = (), ()

    stream_command = Tupu
    kila opt,val kwenye optlist:
        ikiwa opt == '-d':
            Debug = int(val)
        lasivyo opt == '-s':
            stream_command = val
            ikiwa sio args: args = (stream_command,)

    ikiwa sio args: args = ('',)

    host = args[0]

    USER = getpita.getuser()
    PASSWD = getpita.getpita("IMAP pitaword kila %s on %s: " % (USER, host ama "localhost"))

    test_mesg = 'From: %(user)s@localhost%(lf)sSubject: IMAP4 test%(lf)s%(lf)sdata...%(lf)s' % {'user':USER, 'lf':'\n'}
    test_seq1 = (
    ('login', (USER, PASSWD)),
    ('create', ('/tmp/xxx 1',)),
    ('rename', ('/tmp/xxx 1', '/tmp/yyy')),
    ('CREATE', ('/tmp/yyz 2',)),
    ('append', ('/tmp/yyz 2', Tupu, Tupu, test_mesg)),
    ('list', ('/tmp', 'yy*')),
    ('select', ('/tmp/yyz 2',)),
    ('search', (Tupu, 'SUBJECT', 'test')),
    ('fetch', ('1', '(FLAGS INTERNALDATE RFC822)')),
    ('store', ('1', 'FLAGS', r'(\Deleted)')),
    ('namespace', ()),
    ('expunge', ()),
    ('recent', ()),
    ('close', ()),
    )

    test_seq2 = (
    ('select', ()),
    ('response',('UIDVALIDITY',)),
    ('uid', ('SEARCH', 'ALL')),
    ('response', ('EXISTS',)),
    ('append', (Tupu, Tupu, Tupu, test_mesg)),
    ('recent', ()),
    ('logout', ()),
    )

    eleza run(cmd, args):
        M._mesg('%s %s' % (cmd, args))
        typ, dat = getattr(M, cmd)(*args)
        M._mesg('%s => %s %s' % (cmd, typ, dat))
        ikiwa typ == 'NO': ashiria dat[0]
        rudisha dat

    jaribu:
        ikiwa stream_command:
            M = IMAP4_stream(stream_command)
        isipokua:
            M = IMAP4(host)
        ikiwa M.state == 'AUTH':
            test_seq1 = test_seq1[1:]   # Login sio needed
        M._mesg('PROTOCOL_VERSION = %s' % M.PROTOCOL_VERSION)
        M._mesg('CAPABILITIES = %r' % (M.capabilities,))

        kila cmd,args kwenye test_seq1:
            run(cmd, args)

        kila ml kwenye run('list', ('/tmp/', 'yy%')):
            mo = re.match(r'.*"([^"]+)"$', ml)
            ikiwa mo: path = mo.group(1)
            isipokua: path = ml.split()[-1]
            run('delete', (path,))

        kila cmd,args kwenye test_seq2:
            dat = run(cmd, args)

            ikiwa (cmd,args) != ('uid', ('SEARCH', 'ALL')):
                endelea

            uid = dat[-1].split()
            ikiwa sio uid: endelea
            run('uid', ('FETCH', '%s' % uid[-1],
                    '(FLAGS INTERNALDATE RFC822.SIZE RFC822.HEADER RFC822.TEXT)'))

        andika('\nAll tests OK.')

    tatizo:
        andika('\nTests failed.')

        ikiwa sio Debug:
            andika('''
If you would like to see debugging output,
jaribu: %s -d5
''' % sys.argv[0])

        raise
