#! /usr/bin/env python3
"""An RFC 5321 smtp proxy with optional RFC 1870 and RFC 6531 extensions.

Usage: %(program)s [options] [localhost:localport [remotehost:remoteport]]

Options:

    --nosetuid
    -n
        This program generally tries to setuid `nobody', unless this flag is
        set.  The setuid call will fail ikiwa this program is not run as root (in
        which case, use this flag).

    --version
    -V
        Print the version number and exit.

    --kundi classname
    -c classname
        Use `classname' as the concrete SMTP proxy class.  Uses `PureProxy' by
        default.

    --size limit
    -s limit
        Restrict the total size of the incoming message to "limit" number of
        bytes via the RFC 1870 SIZE extension.  Defaults to 33554432 bytes.

    --smtputf8
    -u
        Enable the SMTPUTF8 extension and behave as an RFC 6531 smtp proxy.

    --debug
    -d
        Turn on debugging prints.

    --help
    -h
        Print this message and exit.

Version: %(__version__)s

If localhost is not given then `localhost' is used, and ikiwa localport is not
given then 8025 is used.  If remotehost is not given then `localhost' is used,
and ikiwa remoteport is not given, then 25 is used.
"""

# Overview:
#
# This file implements the minimal SMTP protocol as defined in RFC 5321.  It
# has a hierarchy of classes which implement the backend functionality for the
# smtpd.  A number of classes are provided:
#
#   SMTPServer - the base kundi for the backend.  Raises NotImplementedError
#   ikiwa you try to use it.
#
#   DebuggingServer - simply prints each message it receives on stdout.
#
#   PureProxy - Proxies all messages to a real smtpd which does final
#   delivery.  One known problem with this kundi is that it doesn't handle
#   SMTP errors kutoka the backend server at all.  This should be fixed
#   (contributions are welcome!).
#
#   MailmanProxy - An experimental hack to work with GNU Mailman
#   <www.list.org>.  Using this server as your real incoming smtpd, your
#   mailhost will automatically recognize and accept mail destined to Mailman
#   lists when those lists are created.  Every message not destined for a list
#   gets forwarded to a real backend smtpd, as with PureProxy.  Again, errors
#   are not handled correctly yet.
#
#
# Author: Barry Warsaw <barry@python.org>
#
# TODO:
#
# - support mailbox delivery
# - alias files
# - Handle more ESMTP extensions
# - handle error codes kutoka the backend smtpd

agiza sys
agiza os
agiza errno
agiza getopt
agiza time
agiza socket
agiza asyncore
agiza asynchat
agiza collections
kutoka warnings agiza warn
kutoka email._header_value_parser agiza get_addr_spec, get_angle_addr

__all__ = [
    "SMTPChannel", "SMTPServer", "DebuggingServer", "PureProxy",
    "MailmanProxy",
]

program = sys.argv[0]
__version__ = 'Python SMTP proxy version 0.3'


kundi Devnull:
    eleza write(self, msg): pass
    eleza flush(self): pass


DEBUGSTREAM = Devnull()
NEWLINE = '\n'
COMMASPACE = ', '
DATA_SIZE_DEFAULT = 33554432


eleza usage(code, msg=''):
    andika(__doc__ % globals(), file=sys.stderr)
    ikiwa msg:
        andika(msg, file=sys.stderr)
    sys.exit(code)


kundi SMTPChannel(asynchat.async_chat):
    COMMAND = 0
    DATA = 1

    command_size_limit = 512
    command_size_limits = collections.defaultdict(lambda x=command_size_limit: x)

    @property
    eleza max_command_size_limit(self):
        try:
            rudisha max(self.command_size_limits.values())
        except ValueError:
            rudisha self.command_size_limit

    eleza __init__(self, server, conn, addr, data_size_limit=DATA_SIZE_DEFAULT,
                 map=None, enable_SMTPUTF8=False, decode_data=False):
        asynchat.async_chat.__init__(self, conn, map=map)
        self.smtp_server = server
        self.conn = conn
        self.addr = addr
        self.data_size_limit = data_size_limit
        self.enable_SMTPUTF8 = enable_SMTPUTF8
        self._decode_data = decode_data
        ikiwa enable_SMTPUTF8 and decode_data:
            raise ValueError("decode_data and enable_SMTPUTF8 cannot"
                             " be set to True at the same time")
        ikiwa decode_data:
            self._emptystring = ''
            self._linesep = '\r\n'
            self._dotsep = '.'
            self._newline = NEWLINE
        else:
            self._emptystring = b''
            self._linesep = b'\r\n'
            self._dotsep = ord(b'.')
            self._newline = b'\n'
        self._set_rset_state()
        self.seen_greeting = ''
        self.extended_smtp = False
        self.command_size_limits.clear()
        self.fqdn = socket.getfqdn()
        try:
            self.peer = conn.getpeername()
        except OSError as err:
            # a race condition  may occur ikiwa the other end is closing
            # before we can get the peername
            self.close()
            ikiwa err.args[0] != errno.ENOTCONN:
                raise
            return
        andika('Peer:', repr(self.peer), file=DEBUGSTREAM)
        self.push('220 %s %s' % (self.fqdn, __version__))

    eleza _set_post_data_state(self):
        """Reset state variables to their post-DATA state."""
        self.smtp_state = self.COMMAND
        self.mailkutoka = None
        self.rcpttos = []
        self.require_SMTPUTF8 = False
        self.num_bytes = 0
        self.set_terminator(b'\r\n')

    eleza _set_rset_state(self):
        """Reset all state variables except the greeting."""
        self._set_post_data_state()
        self.received_data = ''
        self.received_lines = []


    # properties for backwards-compatibility
    @property
    eleza __server(self):
        warn("Access to __server attribute on SMTPChannel is deprecated, "
            "use 'smtp_server' instead", DeprecationWarning, 2)
        rudisha self.smtp_server
    @__server.setter
    eleza __server(self, value):
        warn("Setting __server attribute on SMTPChannel is deprecated, "
            "set 'smtp_server' instead", DeprecationWarning, 2)
        self.smtp_server = value

    @property
    eleza __line(self):
        warn("Access to __line attribute on SMTPChannel is deprecated, "
            "use 'received_lines' instead", DeprecationWarning, 2)
        rudisha self.received_lines
    @__line.setter
    eleza __line(self, value):
        warn("Setting __line attribute on SMTPChannel is deprecated, "
            "set 'received_lines' instead", DeprecationWarning, 2)
        self.received_lines = value

    @property
    eleza __state(self):
        warn("Access to __state attribute on SMTPChannel is deprecated, "
            "use 'smtp_state' instead", DeprecationWarning, 2)
        rudisha self.smtp_state
    @__state.setter
    eleza __state(self, value):
        warn("Setting __state attribute on SMTPChannel is deprecated, "
            "set 'smtp_state' instead", DeprecationWarning, 2)
        self.smtp_state = value

    @property
    eleza __greeting(self):
        warn("Access to __greeting attribute on SMTPChannel is deprecated, "
            "use 'seen_greeting' instead", DeprecationWarning, 2)
        rudisha self.seen_greeting
    @__greeting.setter
    eleza __greeting(self, value):
        warn("Setting __greeting attribute on SMTPChannel is deprecated, "
            "set 'seen_greeting' instead", DeprecationWarning, 2)
        self.seen_greeting = value

    @property
    eleza __mailkutoka(self):
        warn("Access to __mailkutoka attribute on SMTPChannel is deprecated, "
            "use 'mailkutoka' instead", DeprecationWarning, 2)
        rudisha self.mailkutoka
    @__mailkutoka.setter
    eleza __mailkutoka(self, value):
        warn("Setting __mailkutoka attribute on SMTPChannel is deprecated, "
            "set 'mailkutoka' instead", DeprecationWarning, 2)
        self.mailkutoka = value

    @property
    eleza __rcpttos(self):
        warn("Access to __rcpttos attribute on SMTPChannel is deprecated, "
            "use 'rcpttos' instead", DeprecationWarning, 2)
        rudisha self.rcpttos
    @__rcpttos.setter
    eleza __rcpttos(self, value):
        warn("Setting __rcpttos attribute on SMTPChannel is deprecated, "
            "set 'rcpttos' instead", DeprecationWarning, 2)
        self.rcpttos = value

    @property
    eleza __data(self):
        warn("Access to __data attribute on SMTPChannel is deprecated, "
            "use 'received_data' instead", DeprecationWarning, 2)
        rudisha self.received_data
    @__data.setter
    eleza __data(self, value):
        warn("Setting __data attribute on SMTPChannel is deprecated, "
            "set 'received_data' instead", DeprecationWarning, 2)
        self.received_data = value

    @property
    eleza __fqdn(self):
        warn("Access to __fqdn attribute on SMTPChannel is deprecated, "
            "use 'fqdn' instead", DeprecationWarning, 2)
        rudisha self.fqdn
    @__fqdn.setter
    eleza __fqdn(self, value):
        warn("Setting __fqdn attribute on SMTPChannel is deprecated, "
            "set 'fqdn' instead", DeprecationWarning, 2)
        self.fqdn = value

    @property
    eleza __peer(self):
        warn("Access to __peer attribute on SMTPChannel is deprecated, "
            "use 'peer' instead", DeprecationWarning, 2)
        rudisha self.peer
    @__peer.setter
    eleza __peer(self, value):
        warn("Setting __peer attribute on SMTPChannel is deprecated, "
            "set 'peer' instead", DeprecationWarning, 2)
        self.peer = value

    @property
    eleza __conn(self):
        warn("Access to __conn attribute on SMTPChannel is deprecated, "
            "use 'conn' instead", DeprecationWarning, 2)
        rudisha self.conn
    @__conn.setter
    eleza __conn(self, value):
        warn("Setting __conn attribute on SMTPChannel is deprecated, "
            "set 'conn' instead", DeprecationWarning, 2)
        self.conn = value

    @property
    eleza __addr(self):
        warn("Access to __addr attribute on SMTPChannel is deprecated, "
            "use 'addr' instead", DeprecationWarning, 2)
        rudisha self.addr
    @__addr.setter
    eleza __addr(self, value):
        warn("Setting __addr attribute on SMTPChannel is deprecated, "
            "set 'addr' instead", DeprecationWarning, 2)
        self.addr = value

    # Overrides base kundi for convenience.
    eleza push(self, msg):
        asynchat.async_chat.push(self, bytes(
            msg + '\r\n', 'utf-8' ikiwa self.require_SMTPUTF8 else 'ascii'))

    # Implementation of base kundi abstract method
    eleza collect_incoming_data(self, data):
        limit = None
        ikiwa self.smtp_state == self.COMMAND:
            limit = self.max_command_size_limit
        elikiwa self.smtp_state == self.DATA:
            limit = self.data_size_limit
        ikiwa limit and self.num_bytes > limit:
            return
        elikiwa limit:
            self.num_bytes += len(data)
        ikiwa self._decode_data:
            self.received_lines.append(str(data, 'utf-8'))
        else:
            self.received_lines.append(data)

    # Implementation of base kundi abstract method
    eleza found_terminator(self):
        line = self._emptystring.join(self.received_lines)
        andika('Data:', repr(line), file=DEBUGSTREAM)
        self.received_lines = []
        ikiwa self.smtp_state == self.COMMAND:
            sz, self.num_bytes = self.num_bytes, 0
            ikiwa not line:
                self.push('500 Error: bad syntax')
                return
            ikiwa not self._decode_data:
                line = str(line, 'utf-8')
            i = line.find(' ')
            ikiwa i < 0:
                command = line.upper()
                arg = None
            else:
                command = line[:i].upper()
                arg = line[i+1:].strip()
            max_sz = (self.command_size_limits[command]
                        ikiwa self.extended_smtp else self.command_size_limit)
            ikiwa sz > max_sz:
                self.push('500 Error: line too long')
                return
            method = getattr(self, 'smtp_' + command, None)
            ikiwa not method:
                self.push('500 Error: command "%s" not recognized' % command)
                return
            method(arg)
            return
        else:
            ikiwa self.smtp_state != self.DATA:
                self.push('451 Internal confusion')
                self.num_bytes = 0
                return
            ikiwa self.data_size_limit and self.num_bytes > self.data_size_limit:
                self.push('552 Error: Too much mail data')
                self.num_bytes = 0
                return
            # Remove extraneous carriage returns and de-transparency according
            # to RFC 5321, Section 4.5.2.
            data = []
            for text in line.split(self._linesep):
                ikiwa text and text[0] == self._dotsep:
                    data.append(text[1:])
                else:
                    data.append(text)
            self.received_data = self._newline.join(data)
            args = (self.peer, self.mailkutoka, self.rcpttos, self.received_data)
            kwargs = {}
            ikiwa not self._decode_data:
                kwargs = {
                    'mail_options': self.mail_options,
                    'rcpt_options': self.rcpt_options,
                }
            status = self.smtp_server.process_message(*args, **kwargs)
            self._set_post_data_state()
            ikiwa not status:
                self.push('250 OK')
            else:
                self.push(status)

    # SMTP and ESMTP commands
    eleza smtp_HELO(self, arg):
        ikiwa not arg:
            self.push('501 Syntax: HELO hostname')
            return
        # See issue #21783 for a discussion of this behavior.
        ikiwa self.seen_greeting:
            self.push('503 Duplicate HELO/EHLO')
            return
        self._set_rset_state()
        self.seen_greeting = arg
        self.push('250 %s' % self.fqdn)

    eleza smtp_EHLO(self, arg):
        ikiwa not arg:
            self.push('501 Syntax: EHLO hostname')
            return
        # See issue #21783 for a discussion of this behavior.
        ikiwa self.seen_greeting:
            self.push('503 Duplicate HELO/EHLO')
            return
        self._set_rset_state()
        self.seen_greeting = arg
        self.extended_smtp = True
        self.push('250-%s' % self.fqdn)
        ikiwa self.data_size_limit:
            self.push('250-SIZE %s' % self.data_size_limit)
            self.command_size_limits['MAIL'] += 26
        ikiwa not self._decode_data:
            self.push('250-8BITMIME')
        ikiwa self.enable_SMTPUTF8:
            self.push('250-SMTPUTF8')
            self.command_size_limits['MAIL'] += 10
        self.push('250 HELP')

    eleza smtp_NOOP(self, arg):
        ikiwa arg:
            self.push('501 Syntax: NOOP')
        else:
            self.push('250 OK')

    eleza smtp_QUIT(self, arg):
        # args is ignored
        self.push('221 Bye')
        self.close_when_done()

    eleza _strip_command_keyword(self, keyword, arg):
        keylen = len(keyword)
        ikiwa arg[:keylen].upper() == keyword:
            rudisha arg[keylen:].strip()
        rudisha ''

    eleza _getaddr(self, arg):
        ikiwa not arg:
            rudisha '', ''
        ikiwa arg.lstrip().startswith('<'):
            address, rest = get_angle_addr(arg)
        else:
            address, rest = get_addr_spec(arg)
        ikiwa not address:
            rudisha address, rest
        rudisha address.addr_spec, rest

    eleza _getparams(self, params):
        # Return params as dictionary. Return None ikiwa not all parameters
        # appear to be syntactically valid according to RFC 1869.
        result = {}
        for param in params:
            param, eq, value = param.partition('=')
            ikiwa not param.isalnum() or eq and not value:
                rudisha None
            result[param] = value ikiwa eq else True
        rudisha result

    eleza smtp_HELP(self, arg):
        ikiwa arg:
            extended = ' [SP <mail-parameters>]'
            lc_arg = arg.upper()
            ikiwa lc_arg == 'EHLO':
                self.push('250 Syntax: EHLO hostname')
            elikiwa lc_arg == 'HELO':
                self.push('250 Syntax: HELO hostname')
            elikiwa lc_arg == 'MAIL':
                msg = '250 Syntax: MAIL FROM: <address>'
                ikiwa self.extended_smtp:
                    msg += extended
                self.push(msg)
            elikiwa lc_arg == 'RCPT':
                msg = '250 Syntax: RCPT TO: <address>'
                ikiwa self.extended_smtp:
                    msg += extended
                self.push(msg)
            elikiwa lc_arg == 'DATA':
                self.push('250 Syntax: DATA')
            elikiwa lc_arg == 'RSET':
                self.push('250 Syntax: RSET')
            elikiwa lc_arg == 'NOOP':
                self.push('250 Syntax: NOOP')
            elikiwa lc_arg == 'QUIT':
                self.push('250 Syntax: QUIT')
            elikiwa lc_arg == 'VRFY':
                self.push('250 Syntax: VRFY <address>')
            else:
                self.push('501 Supported commands: EHLO HELO MAIL RCPT '
                          'DATA RSET NOOP QUIT VRFY')
        else:
            self.push('250 Supported commands: EHLO HELO MAIL RCPT DATA '
                      'RSET NOOP QUIT VRFY')

    eleza smtp_VRFY(self, arg):
        ikiwa arg:
            address, params = self._getaddr(arg)
            ikiwa address:
                self.push('252 Cannot VRFY user, but will accept message '
                          'and attempt delivery')
            else:
                self.push('502 Could not VRFY %s' % arg)
        else:
            self.push('501 Syntax: VRFY <address>')

    eleza smtp_MAIL(self, arg):
        ikiwa not self.seen_greeting:
            self.push('503 Error: send HELO first')
            return
        andika('===> MAIL', arg, file=DEBUGSTREAM)
        syntaxerr = '501 Syntax: MAIL FROM: <address>'
        ikiwa self.extended_smtp:
            syntaxerr += ' [SP <mail-parameters>]'
        ikiwa arg is None:
            self.push(syntaxerr)
            return
        arg = self._strip_command_keyword('FROM:', arg)
        address, params = self._getaddr(arg)
        ikiwa not address:
            self.push(syntaxerr)
            return
        ikiwa not self.extended_smtp and params:
            self.push(syntaxerr)
            return
        ikiwa self.mailkutoka:
            self.push('503 Error: nested MAIL command')
            return
        self.mail_options = params.upper().split()
        params = self._getparams(self.mail_options)
        ikiwa params is None:
            self.push(syntaxerr)
            return
        ikiwa not self._decode_data:
            body = params.pop('BODY', '7BIT')
            ikiwa body not in ['7BIT', '8BITMIME']:
                self.push('501 Error: BODY can only be one of 7BIT, 8BITMIME')
                return
        ikiwa self.enable_SMTPUTF8:
            smtputf8 = params.pop('SMTPUTF8', False)
            ikiwa smtputf8 is True:
                self.require_SMTPUTF8 = True
            elikiwa smtputf8 is not False:
                self.push('501 Error: SMTPUTF8 takes no arguments')
                return
        size = params.pop('SIZE', None)
        ikiwa size:
            ikiwa not size.isdigit():
                self.push(syntaxerr)
                return
            elikiwa self.data_size_limit and int(size) > self.data_size_limit:
                self.push('552 Error: message size exceeds fixed maximum message size')
                return
        ikiwa len(params.keys()) > 0:
            self.push('555 MAIL FROM parameters not recognized or not implemented')
            return
        self.mailkutoka = address
        andika('sender:', self.mailkutoka, file=DEBUGSTREAM)
        self.push('250 OK')

    eleza smtp_RCPT(self, arg):
        ikiwa not self.seen_greeting:
            self.push('503 Error: send HELO first');
            return
        andika('===> RCPT', arg, file=DEBUGSTREAM)
        ikiwa not self.mailkutoka:
            self.push('503 Error: need MAIL command')
            return
        syntaxerr = '501 Syntax: RCPT TO: <address>'
        ikiwa self.extended_smtp:
            syntaxerr += ' [SP <mail-parameters>]'
        ikiwa arg is None:
            self.push(syntaxerr)
            return
        arg = self._strip_command_keyword('TO:', arg)
        address, params = self._getaddr(arg)
        ikiwa not address:
            self.push(syntaxerr)
            return
        ikiwa not self.extended_smtp and params:
            self.push(syntaxerr)
            return
        self.rcpt_options = params.upper().split()
        params = self._getparams(self.rcpt_options)
        ikiwa params is None:
            self.push(syntaxerr)
            return
        # XXX currently there are no options we recognize.
        ikiwa len(params.keys()) > 0:
            self.push('555 RCPT TO parameters not recognized or not implemented')
            return
        self.rcpttos.append(address)
        andika('recips:', self.rcpttos, file=DEBUGSTREAM)
        self.push('250 OK')

    eleza smtp_RSET(self, arg):
        ikiwa arg:
            self.push('501 Syntax: RSET')
            return
        self._set_rset_state()
        self.push('250 OK')

    eleza smtp_DATA(self, arg):
        ikiwa not self.seen_greeting:
            self.push('503 Error: send HELO first');
            return
        ikiwa not self.rcpttos:
            self.push('503 Error: need RCPT command')
            return
        ikiwa arg:
            self.push('501 Syntax: DATA')
            return
        self.smtp_state = self.DATA
        self.set_terminator(b'\r\n.\r\n')
        self.push('354 End data with <CR><LF>.<CR><LF>')

    # Commands that have not been implemented
    eleza smtp_EXPN(self, arg):
        self.push('502 EXPN not implemented')


kundi SMTPServer(asyncore.dispatcher):
    # SMTPChannel kundi to use for managing client connections
    channel_kundi = SMTPChannel

    eleza __init__(self, localaddr, remoteaddr,
                 data_size_limit=DATA_SIZE_DEFAULT, map=None,
                 enable_SMTPUTF8=False, decode_data=False):
        self._localaddr = localaddr
        self._remoteaddr = remoteaddr
        self.data_size_limit = data_size_limit
        self.enable_SMTPUTF8 = enable_SMTPUTF8
        self._decode_data = decode_data
        ikiwa enable_SMTPUTF8 and decode_data:
            raise ValueError("decode_data and enable_SMTPUTF8 cannot"
                             " be set to True at the same time")
        asyncore.dispatcher.__init__(self, map=map)
        try:
            gai_results = socket.getaddrinfo(*localaddr,
                                             type=socket.SOCK_STREAM)
            self.create_socket(gai_results[0][0], gai_results[0][1])
            # try to re-use a server port ikiwa possible
            self.set_reuse_addr()
            self.bind(localaddr)
            self.listen(5)
        except:
            self.close()
            raise
        else:
            andika('%s started at %s\n\tLocal addr: %s\n\tRemote addr:%s' % (
                self.__class__.__name__, time.ctime(time.time()),
                localaddr, remoteaddr), file=DEBUGSTREAM)

    eleza handle_accepted(self, conn, addr):
        andika('Incoming connection kutoka %s' % repr(addr), file=DEBUGSTREAM)
        channel = self.channel_class(self,
                                     conn,
                                     addr,
                                     self.data_size_limit,
                                     self._map,
                                     self.enable_SMTPUTF8,
                                     self._decode_data)

    # API for "doing something useful with the message"
    eleza process_message(self, peer, mailkutoka, rcpttos, data, **kwargs):
        """Override this abstract method to handle messages kutoka the client.

        peer is a tuple containing (ipaddr, port) of the client that made the
        socket connection to our smtp port.

        mailkutoka is the raw address the client claims the message is coming
        kutoka.

        rcpttos is a list of raw addresses the client wishes to deliver the
        message to.

        data is a string containing the entire full text of the message,
        headers (ikiwa supplied) and all.  It has been `de-transparencied'
        according to RFC 821, Section 4.5.2.  In other words, a line
        containing a `.' followed by other text has had the leading dot
        removed.

        kwargs is a dictionary containing additional information.  It is
        empty ikiwa decode_data=True was given as init parameter, otherwise
        it will contain the following keys:
            'mail_options': list of parameters to the mail command.  All
                            elements are uppercase strings.  Example:
                            ['BODY=8BITMIME', 'SMTPUTF8'].
            'rcpt_options': same, for the rcpt command.

        This function should rudisha None for a normal `250 Ok' response;
        otherwise, it should rudisha the desired response string in RFC 821
        format.

        """
        raise NotImplementedError


kundi DebuggingServer(SMTPServer):

    eleza _print_message_content(self, peer, data):
        inheaders = 1
        lines = data.splitlines()
        for line in lines:
            # headers first
            ikiwa inheaders and not line:
                peerheader = 'X-Peer: ' + peer[0]
                ikiwa not isinstance(data, str):
                    # decoded_data=false; make header match other binary output
                    peerheader = repr(peerheader.encode('utf-8'))
                andika(peerheader)
                inheaders = 0
            ikiwa not isinstance(data, str):
                # Avoid spurious 'str on bytes instance' warning.
                line = repr(line)
            andika(line)

    eleza process_message(self, peer, mailkutoka, rcpttos, data, **kwargs):
        andika('---------- MESSAGE FOLLOWS ----------')
        ikiwa kwargs:
            ikiwa kwargs.get('mail_options'):
                andika('mail options: %s' % kwargs['mail_options'])
            ikiwa kwargs.get('rcpt_options'):
                andika('rcpt options: %s\n' % kwargs['rcpt_options'])
        self._print_message_content(peer, data)
        andika('------------ END MESSAGE ------------')


kundi PureProxy(SMTPServer):
    eleza __init__(self, *args, **kwargs):
        ikiwa 'enable_SMTPUTF8' in kwargs and kwargs['enable_SMTPUTF8']:
            raise ValueError("PureProxy does not support SMTPUTF8.")
        super(PureProxy, self).__init__(*args, **kwargs)

    eleza process_message(self, peer, mailkutoka, rcpttos, data):
        lines = data.split('\n')
        # Look for the last header
        i = 0
        for line in lines:
            ikiwa not line:
                break
            i += 1
        lines.insert(i, 'X-Peer: %s' % peer[0])
        data = NEWLINE.join(lines)
        refused = self._deliver(mailkutoka, rcpttos, data)
        # TBD: what to do with refused addresses?
        andika('we got some refusals:', refused, file=DEBUGSTREAM)

    eleza _deliver(self, mailkutoka, rcpttos, data):
        agiza smtplib
        refused = {}
        try:
            s = smtplib.SMTP()
            s.connect(self._remoteaddr[0], self._remoteaddr[1])
            try:
                refused = s.sendmail(mailkutoka, rcpttos, data)
            finally:
                s.quit()
        except smtplib.SMTPRecipientsRefused as e:
            andika('got SMTPRecipientsRefused', file=DEBUGSTREAM)
            refused = e.recipients
        except (OSError, smtplib.SMTPException) as e:
            andika('got', e.__class__, file=DEBUGSTREAM)
            # All recipients were refused.  If the exception had an associated
            # error code, use it.  Otherwise,fake it with a non-triggering
            # exception code.
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            for r in rcpttos:
                refused[r] = (errcode, errmsg)
        rudisha refused


kundi MailmanProxy(PureProxy):
    eleza __init__(self, *args, **kwargs):
        ikiwa 'enable_SMTPUTF8' in kwargs and kwargs['enable_SMTPUTF8']:
            raise ValueError("MailmanProxy does not support SMTPUTF8.")
        super(PureProxy, self).__init__(*args, **kwargs)

    eleza process_message(self, peer, mailkutoka, rcpttos, data):
        kutoka io agiza StringIO
        kutoka Mailman agiza Utils
        kutoka Mailman agiza Message
        kutoka Mailman agiza MailList
        # If the message is to a Mailman mailing list, then we'll invoke the
        # Mailman script directly, without going through the real smtpd.
        # Otherwise we'll forward it to the local proxy for disposition.
        listnames = []
        for rcpt in rcpttos:
            local = rcpt.lower().split('@')[0]
            # We allow the following variations on the theme
            #   listname
            #   listname-admin
            #   listname-owner
            #   listname-request
            #   listname-join
            #   listname-leave
            parts = local.split('-')
            ikiwa len(parts) > 2:
                continue
            listname = parts[0]
            ikiwa len(parts) == 2:
                command = parts[1]
            else:
                command = ''
            ikiwa not Utils.list_exists(listname) or command not in (
                    '', 'admin', 'owner', 'request', 'join', 'leave'):
                continue
            listnames.append((rcpt, listname, command))
        # Remove all list recipients kutoka rcpttos and forward what we're not
        # going to take care of ourselves.  Linear removal should be fine
        # since we don't expect a large number of recipients.
        for rcpt, listname, command in listnames:
            rcpttos.remove(rcpt)
        # If there's any non-list destined recipients left,
        andika('forwarding recips:', ' '.join(rcpttos), file=DEBUGSTREAM)
        ikiwa rcpttos:
            refused = self._deliver(mailkutoka, rcpttos, data)
            # TBD: what to do with refused addresses?
            andika('we got refusals:', refused, file=DEBUGSTREAM)
        # Now deliver directly to the list commands
        mlists = {}
        s = StringIO(data)
        msg = Message.Message(s)
        # These headers are required for the proper execution of Mailman.  All
        # MTAs in existence seem to add these ikiwa the original message doesn't
        # have them.
        ikiwa not msg.get('kutoka'):
            msg['From'] = mailkutoka
        ikiwa not msg.get('date'):
            msg['Date'] = time.ctime(time.time())
        for rcpt, listname, command in listnames:
            andika('sending message to', rcpt, file=DEBUGSTREAM)
            mlist = mlists.get(listname)
            ikiwa not mlist:
                mlist = MailList.MailList(listname, lock=0)
                mlists[listname] = mlist
            # dispatch on the type of command
            ikiwa command == '':
                # post
                msg.Enqueue(mlist, tolist=1)
            elikiwa command == 'admin':
                msg.Enqueue(mlist, toadmin=1)
            elikiwa command == 'owner':
                msg.Enqueue(mlist, toowner=1)
            elikiwa command == 'request':
                msg.Enqueue(mlist, torequest=1)
            elikiwa command in ('join', 'leave'):
                # TBD: this is a hack!
                ikiwa command == 'join':
                    msg['Subject'] = 'subscribe'
                else:
                    msg['Subject'] = 'unsubscribe'
                msg.Enqueue(mlist, torequest=1)


kundi Options:
    setuid = True
    classname = 'PureProxy'
    size_limit = None
    enable_SMTPUTF8 = False


eleza parseargs():
    global DEBUGSTREAM
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'nVhc:s:du',
            ['class=', 'nosetuid', 'version', 'help', 'size=', 'debug',
             'smtputf8'])
    except getopt.error as e:
        usage(1, e)

    options = Options()
    for opt, arg in opts:
        ikiwa opt in ('-h', '--help'):
            usage(0)
        elikiwa opt in ('-V', '--version'):
            andika(__version__)
            sys.exit(0)
        elikiwa opt in ('-n', '--nosetuid'):
            options.setuid = False
        elikiwa opt in ('-c', '--class'):
            options.classname = arg
        elikiwa opt in ('-d', '--debug'):
            DEBUGSTREAM = sys.stderr
        elikiwa opt in ('-u', '--smtputf8'):
            options.enable_SMTPUTF8 = True
        elikiwa opt in ('-s', '--size'):
            try:
                int_size = int(arg)
                options.size_limit = int_size
            except:
                andika('Invalid size: ' + arg, file=sys.stderr)
                sys.exit(1)

    # parse the rest of the arguments
    ikiwa len(args) < 1:
        localspec = 'localhost:8025'
        remotespec = 'localhost:25'
    elikiwa len(args) < 2:
        localspec = args[0]
        remotespec = 'localhost:25'
    elikiwa len(args) < 3:
        localspec = args[0]
        remotespec = args[1]
    else:
        usage(1, 'Invalid arguments: %s' % COMMASPACE.join(args))

    # split into host/port pairs
    i = localspec.find(':')
    ikiwa i < 0:
        usage(1, 'Bad local spec: %s' % localspec)
    options.localhost = localspec[:i]
    try:
        options.localport = int(localspec[i+1:])
    except ValueError:
        usage(1, 'Bad local port: %s' % localspec)
    i = remotespec.find(':')
    ikiwa i < 0:
        usage(1, 'Bad remote spec: %s' % remotespec)
    options.remotehost = remotespec[:i]
    try:
        options.remoteport = int(remotespec[i+1:])
    except ValueError:
        usage(1, 'Bad remote port: %s' % remotespec)
    rudisha options


ikiwa __name__ == '__main__':
    options = parseargs()
    # Become nobody
    classname = options.classname
    ikiwa "." in classname:
        lastdot = classname.rfind(".")
        mod = __import__(classname[:lastdot], globals(), locals(), [""])
        classname = classname[lastdot+1:]
    else:
        agiza __main__ as mod
    class_ = getattr(mod, classname)
    proxy = class_((options.localhost, options.localport),
                   (options.remotehost, options.remoteport),
                   options.size_limit, enable_SMTPUTF8=options.enable_SMTPUTF8)
    ikiwa options.setuid:
        try:
            agiza pwd
        except ImportError:
            andika('Cannot agiza module "pwd"; try running with -n option.', file=sys.stderr)
            sys.exit(1)
        nobody = pwd.getpwnam('nobody')[2]
        try:
            os.setuid(nobody)
        except PermissionError:
            andika('Cannot setuid "nobody"; try running with -n option.', file=sys.stderr)
            sys.exit(1)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
