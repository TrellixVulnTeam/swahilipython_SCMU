#! /usr/bin/env python3
"""An RFC 5321 smtp proxy ukijumuisha optional RFC 1870 na RFC 6531 extensions.

Usage: %(program)s [options] [localhost:localport [remotehost:remoteport]]

Options:

    --nosetuid
    -n
        This program generally tries to setuid `nobody', unless this flag is
        set.  The setuid call will fail ikiwa this program ni sio run kama root (in
        which case, use this flag).

    --version
    -V
        Print the version number na exit.

    --kundi classname
    -c classname
        Use `classname' kama the concrete SMTP proxy class.  Uses `PureProxy' by
        default.

    --size limit
    -s limit
        Restrict the total size of the incoming message to "limit" number of
        bytes via the RFC 1870 SIZE extension.  Defaults to 33554432 bytes.

    --smtputf8
    -u
        Enable the SMTPUTF8 extension na behave kama an RFC 6531 smtp proxy.

    --debug
    -d
        Turn on debugging prints.

    --help
    -h
        Print this message na exit.

Version: %(__version__)s

If localhost ni sio given then `localhost' ni used, na ikiwa localport ni sio
given then 8025 ni used.  If remotehost ni sio given then `localhost' ni used,
and ikiwa remoteport ni sio given, then 25 ni used.
"""

# Overview:
#
# This file implements the minimal SMTP protocol kama defined kwenye RFC 5321.  It
# has a hierarchy of classes which implement the backend functionality kila the
# smtpd.  A number of classes are provided:
#
#   SMTPServer - the base kundi kila the backend.  Raises NotImplementedError
#   ikiwa you try to use it.
#
#   DebuggingServer - simply prints each message it receives on stdout.
#
#   PureProxy - Proxies all messages to a real smtpd which does final
#   delivery.  One known problem ukijumuisha this kundi ni that it doesn't handle
#   SMTP errors kutoka the backend server at all.  This should be fixed
#   (contributions are welcome!).
#
#   MailmanProxy - An experimental hack to work ukijumuisha GNU Mailman
#   <www.list.org>.  Using this server kama your real incoming smtpd, your
#   mailhost will automatically recognize na accept mail destined to Mailman
#   lists when those lists are created.  Every message sio destined kila a list
#   gets forwarded to a real backend smtpd, kama ukijumuisha PureProxy.  Again, errors
#   are sio handled correctly yet.
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
    eleza write(self, msg): pita
    eleza flush(self): pita


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
        jaribu:
            rudisha max(self.command_size_limits.values())
        tatizo ValueError:
            rudisha self.command_size_limit

    eleza __init__(self, server, conn, addr, data_size_limit=DATA_SIZE_DEFAULT,
                 map=Tupu, enable_SMTPUTF8=Uongo, decode_data=Uongo):
        asynchat.async_chat.__init__(self, conn, map=map)
        self.smtp_server = server
        self.conn = conn
        self.addr = addr
        self.data_size_limit = data_size_limit
        self.enable_SMTPUTF8 = enable_SMTPUTF8
        self._decode_data = decode_data
        ikiwa enable_SMTPUTF8 na decode_data:
            ashiria ValueError("decode_data na enable_SMTPUTF8 cannot"
                             " be set to Kweli at the same time")
        ikiwa decode_data:
            self._emptystring = ''
            self._linesep = '\r\n'
            self._dotsep = '.'
            self._newline = NEWLINE
        isipokua:
            self._emptystring = b''
            self._linesep = b'\r\n'
            self._dotsep = ord(b'.')
            self._newline = b'\n'
        self._set_rset_state()
        self.seen_greeting = ''
        self.extended_smtp = Uongo
        self.command_size_limits.clear()
        self.fqdn = socket.getfqdn()
        jaribu:
            self.peer = conn.getpeername()
        tatizo OSError kama err:
            # a race condition  may occur ikiwa the other end ni closing
            # before we can get the peername
            self.close()
            ikiwa err.args[0] != errno.ENOTCONN:
                raise
            rudisha
        andika('Peer:', repr(self.peer), file=DEBUGSTREAM)
        self.push('220 %s %s' % (self.fqdn, __version__))

    eleza _set_post_data_state(self):
        """Reset state variables to their post-DATA state."""
        self.smtp_state = self.COMMAND
        self.mailkutoka = Tupu
        self.rcpttos = []
        self.require_SMTPUTF8 = Uongo
        self.num_bytes = 0
        self.set_terminator(b'\r\n')

    eleza _set_rset_state(self):
        """Reset all state variables tatizo the greeting."""
        self._set_post_data_state()
        self.received_data = ''
        self.received_lines = []


    # properties kila backwards-compatibility
    @property
    eleza __server(self):
        warn("Access to __server attribute on SMTPChannel ni deprecated, "
            "use 'smtp_server' instead", DeprecationWarning, 2)
        rudisha self.smtp_server
    @__server.setter
    eleza __server(self, value):
        warn("Setting __server attribute on SMTPChannel ni deprecated, "
            "set 'smtp_server' instead", DeprecationWarning, 2)
        self.smtp_server = value

    @property
    eleza __line(self):
        warn("Access to __line attribute on SMTPChannel ni deprecated, "
            "use 'received_lines' instead", DeprecationWarning, 2)
        rudisha self.received_lines
    @__line.setter
    eleza __line(self, value):
        warn("Setting __line attribute on SMTPChannel ni deprecated, "
            "set 'received_lines' instead", DeprecationWarning, 2)
        self.received_lines = value

    @property
    eleza __state(self):
        warn("Access to __state attribute on SMTPChannel ni deprecated, "
            "use 'smtp_state' instead", DeprecationWarning, 2)
        rudisha self.smtp_state
    @__state.setter
    eleza __state(self, value):
        warn("Setting __state attribute on SMTPChannel ni deprecated, "
            "set 'smtp_state' instead", DeprecationWarning, 2)
        self.smtp_state = value

    @property
    eleza __greeting(self):
        warn("Access to __greeting attribute on SMTPChannel ni deprecated, "
            "use 'seen_greeting' instead", DeprecationWarning, 2)
        rudisha self.seen_greeting
    @__greeting.setter
    eleza __greeting(self, value):
        warn("Setting __greeting attribute on SMTPChannel ni deprecated, "
            "set 'seen_greeting' instead", DeprecationWarning, 2)
        self.seen_greeting = value

    @property
    eleza __mailfrom(self):
        warn("Access to __mailkutoka attribute on SMTPChannel ni deprecated, "
            "use 'mailfrom' instead", DeprecationWarning, 2)
        rudisha self.mailfrom
    @__mailfrom.setter
    eleza __mailfrom(self, value):
        warn("Setting __mailkutoka attribute on SMTPChannel ni deprecated, "
            "set 'mailfrom' instead", DeprecationWarning, 2)
        self.mailkutoka = value

    @property
    eleza __rcpttos(self):
        warn("Access to __rcpttos attribute on SMTPChannel ni deprecated, "
            "use 'rcpttos' instead", DeprecationWarning, 2)
        rudisha self.rcpttos
    @__rcpttos.setter
    eleza __rcpttos(self, value):
        warn("Setting __rcpttos attribute on SMTPChannel ni deprecated, "
            "set 'rcpttos' instead", DeprecationWarning, 2)
        self.rcpttos = value

    @property
    eleza __data(self):
        warn("Access to __data attribute on SMTPChannel ni deprecated, "
            "use 'received_data' instead", DeprecationWarning, 2)
        rudisha self.received_data
    @__data.setter
    eleza __data(self, value):
        warn("Setting __data attribute on SMTPChannel ni deprecated, "
            "set 'received_data' instead", DeprecationWarning, 2)
        self.received_data = value

    @property
    eleza __fqdn(self):
        warn("Access to __fqdn attribute on SMTPChannel ni deprecated, "
            "use 'fqdn' instead", DeprecationWarning, 2)
        rudisha self.fqdn
    @__fqdn.setter
    eleza __fqdn(self, value):
        warn("Setting __fqdn attribute on SMTPChannel ni deprecated, "
            "set 'fqdn' instead", DeprecationWarning, 2)
        self.fqdn = value

    @property
    eleza __peer(self):
        warn("Access to __peer attribute on SMTPChannel ni deprecated, "
            "use 'peer' instead", DeprecationWarning, 2)
        rudisha self.peer
    @__peer.setter
    eleza __peer(self, value):
        warn("Setting __peer attribute on SMTPChannel ni deprecated, "
            "set 'peer' instead", DeprecationWarning, 2)
        self.peer = value

    @property
    eleza __conn(self):
        warn("Access to __conn attribute on SMTPChannel ni deprecated, "
            "use 'conn' instead", DeprecationWarning, 2)
        rudisha self.conn
    @__conn.setter
    eleza __conn(self, value):
        warn("Setting __conn attribute on SMTPChannel ni deprecated, "
            "set 'conn' instead", DeprecationWarning, 2)
        self.conn = value

    @property
    eleza __addr(self):
        warn("Access to __addr attribute on SMTPChannel ni deprecated, "
            "use 'addr' instead", DeprecationWarning, 2)
        rudisha self.addr
    @__addr.setter
    eleza __addr(self, value):
        warn("Setting __addr attribute on SMTPChannel ni deprecated, "
            "set 'addr' instead", DeprecationWarning, 2)
        self.addr = value

    # Overrides base kundi kila convenience.
    eleza push(self, msg):
        asynchat.async_chat.push(self, bytes(
            msg + '\r\n', 'utf-8' ikiwa self.require_SMTPUTF8 isipokua 'ascii'))

    # Implementation of base kundi abstract method
    eleza collect_incoming_data(self, data):
        limit = Tupu
        ikiwa self.smtp_state == self.COMMAND:
            limit = self.max_command_size_limit
        lasivyo self.smtp_state == self.DATA:
            limit = self.data_size_limit
        ikiwa limit na self.num_bytes > limit:
            rudisha
        lasivyo limit:
            self.num_bytes += len(data)
        ikiwa self._decode_data:
            self.received_lines.append(str(data, 'utf-8'))
        isipokua:
            self.received_lines.append(data)

    # Implementation of base kundi abstract method
    eleza found_terminator(self):
        line = self._emptystring.join(self.received_lines)
        andika('Data:', repr(line), file=DEBUGSTREAM)
        self.received_lines = []
        ikiwa self.smtp_state == self.COMMAND:
            sz, self.num_bytes = self.num_bytes, 0
            ikiwa sio line:
                self.push('500 Error: bad syntax')
                rudisha
            ikiwa sio self._decode_data:
                line = str(line, 'utf-8')
            i = line.find(' ')
            ikiwa i < 0:
                command = line.upper()
                arg = Tupu
            isipokua:
                command = line[:i].upper()
                arg = line[i+1:].strip()
            max_sz = (self.command_size_limits[command]
                        ikiwa self.extended_smtp isipokua self.command_size_limit)
            ikiwa sz > max_sz:
                self.push('500 Error: line too long')
                rudisha
            method = getattr(self, 'smtp_' + command, Tupu)
            ikiwa sio method:
                self.push('500 Error: command "%s" sio recognized' % command)
                rudisha
            method(arg)
            rudisha
        isipokua:
            ikiwa self.smtp_state != self.DATA:
                self.push('451 Internal confusion')
                self.num_bytes = 0
                rudisha
            ikiwa self.data_size_limit na self.num_bytes > self.data_size_limit:
                self.push('552 Error: Too much mail data')
                self.num_bytes = 0
                rudisha
            # Remove extraneous carriage returns na de-transparency according
            # to RFC 5321, Section 4.5.2.
            data = []
            kila text kwenye line.split(self._linesep):
                ikiwa text na text[0] == self._dotsep:
                    data.append(text[1:])
                isipokua:
                    data.append(text)
            self.received_data = self._newline.join(data)
            args = (self.peer, self.mailfrom, self.rcpttos, self.received_data)
            kwargs = {}
            ikiwa sio self._decode_data:
                kwargs = {
                    'mail_options': self.mail_options,
                    'rcpt_options': self.rcpt_options,
                }
            status = self.smtp_server.process_message(*args, **kwargs)
            self._set_post_data_state()
            ikiwa sio status:
                self.push('250 OK')
            isipokua:
                self.push(status)

    # SMTP na ESMTP commands
    eleza smtp_HELO(self, arg):
        ikiwa sio arg:
            self.push('501 Syntax: HELO hostname')
            rudisha
        # See issue #21783 kila a discussion of this behavior.
        ikiwa self.seen_greeting:
            self.push('503 Duplicate HELO/EHLO')
            rudisha
        self._set_rset_state()
        self.seen_greeting = arg
        self.push('250 %s' % self.fqdn)

    eleza smtp_EHLO(self, arg):
        ikiwa sio arg:
            self.push('501 Syntax: EHLO hostname')
            rudisha
        # See issue #21783 kila a discussion of this behavior.
        ikiwa self.seen_greeting:
            self.push('503 Duplicate HELO/EHLO')
            rudisha
        self._set_rset_state()
        self.seen_greeting = arg
        self.extended_smtp = Kweli
        self.push('250-%s' % self.fqdn)
        ikiwa self.data_size_limit:
            self.push('250-SIZE %s' % self.data_size_limit)
            self.command_size_limits['MAIL'] += 26
        ikiwa sio self._decode_data:
            self.push('250-8BITMIME')
        ikiwa self.enable_SMTPUTF8:
            self.push('250-SMTPUTF8')
            self.command_size_limits['MAIL'] += 10
        self.push('250 HELP')

    eleza smtp_NOOP(self, arg):
        ikiwa arg:
            self.push('501 Syntax: NOOP')
        isipokua:
            self.push('250 OK')

    eleza smtp_QUIT(self, arg):
        # args ni ignored
        self.push('221 Bye')
        self.close_when_done()

    eleza _strip_command_keyword(self, keyword, arg):
        keylen = len(keyword)
        ikiwa arg[:keylen].upper() == keyword:
            rudisha arg[keylen:].strip()
        rudisha ''

    eleza _getaddr(self, arg):
        ikiwa sio arg:
            rudisha '', ''
        ikiwa arg.lstrip().startswith('<'):
            address, rest = get_angle_addr(arg)
        isipokua:
            address, rest = get_addr_spec(arg)
        ikiwa sio address:
            rudisha address, rest
        rudisha address.addr_spec, rest

    eleza _getparams(self, params):
        # Return params kama dictionary. Return Tupu ikiwa sio all parameters
        # appear to be syntactically valid according to RFC 1869.
        result = {}
        kila param kwenye params:
            param, eq, value = param.partition('=')
            ikiwa sio param.isalnum() ama eq na sio value:
                rudisha Tupu
            result[param] = value ikiwa eq isipokua Kweli
        rudisha result

    eleza smtp_HELP(self, arg):
        ikiwa arg:
            extended = ' [SP <mail-parameters>]'
            lc_arg = arg.upper()
            ikiwa lc_arg == 'EHLO':
                self.push('250 Syntax: EHLO hostname')
            lasivyo lc_arg == 'HELO':
                self.push('250 Syntax: HELO hostname')
            lasivyo lc_arg == 'MAIL':
                msg = '250 Syntax: MAIL FROM: <address>'
                ikiwa self.extended_smtp:
                    msg += extended
                self.push(msg)
            lasivyo lc_arg == 'RCPT':
                msg = '250 Syntax: RCPT TO: <address>'
                ikiwa self.extended_smtp:
                    msg += extended
                self.push(msg)
            lasivyo lc_arg == 'DATA':
                self.push('250 Syntax: DATA')
            lasivyo lc_arg == 'RSET':
                self.push('250 Syntax: RSET')
            lasivyo lc_arg == 'NOOP':
                self.push('250 Syntax: NOOP')
            lasivyo lc_arg == 'QUIT':
                self.push('250 Syntax: QUIT')
            lasivyo lc_arg == 'VRFY':
                self.push('250 Syntax: VRFY <address>')
            isipokua:
                self.push('501 Supported commands: EHLO HELO MAIL RCPT '
                          'DATA RSET NOOP QUIT VRFY')
        isipokua:
            self.push('250 Supported commands: EHLO HELO MAIL RCPT DATA '
                      'RSET NOOP QUIT VRFY')

    eleza smtp_VRFY(self, arg):
        ikiwa arg:
            address, params = self._getaddr(arg)
            ikiwa address:
                self.push('252 Cannot VRFY user, but will accept message '
                          'and attempt delivery')
            isipokua:
                self.push('502 Could sio VRFY %s' % arg)
        isipokua:
            self.push('501 Syntax: VRFY <address>')

    eleza smtp_MAIL(self, arg):
        ikiwa sio self.seen_greeting:
            self.push('503 Error: send HELO first')
            rudisha
        andika('===> MAIL', arg, file=DEBUGSTREAM)
        syntaxerr = '501 Syntax: MAIL FROM: <address>'
        ikiwa self.extended_smtp:
            syntaxerr += ' [SP <mail-parameters>]'
        ikiwa arg ni Tupu:
            self.push(syntaxerr)
            rudisha
        arg = self._strip_command_keyword('FROM:', arg)
        address, params = self._getaddr(arg)
        ikiwa sio address:
            self.push(syntaxerr)
            rudisha
        ikiwa sio self.extended_smtp na params:
            self.push(syntaxerr)
            rudisha
        ikiwa self.mailfrom:
            self.push('503 Error: nested MAIL command')
            rudisha
        self.mail_options = params.upper().split()
        params = self._getparams(self.mail_options)
        ikiwa params ni Tupu:
            self.push(syntaxerr)
            rudisha
        ikiwa sio self._decode_data:
            body = params.pop('BODY', '7BIT')
            ikiwa body haiko kwenye ['7BIT', '8BITMIME']:
                self.push('501 Error: BODY can only be one of 7BIT, 8BITMIME')
                rudisha
        ikiwa self.enable_SMTPUTF8:
            smtputf8 = params.pop('SMTPUTF8', Uongo)
            ikiwa smtputf8 ni Kweli:
                self.require_SMTPUTF8 = Kweli
            lasivyo smtputf8 ni sio Uongo:
                self.push('501 Error: SMTPUTF8 takes no arguments')
                rudisha
        size = params.pop('SIZE', Tupu)
        ikiwa size:
            ikiwa sio size.isdigit():
                self.push(syntaxerr)
                rudisha
            lasivyo self.data_size_limit na int(size) > self.data_size_limit:
                self.push('552 Error: message size exceeds fixed maximum message size')
                rudisha
        ikiwa len(params.keys()) > 0:
            self.push('555 MAIL FROM parameters sio recognized ama sio implemented')
            rudisha
        self.mailkutoka = address
        andika('sender:', self.mailfrom, file=DEBUGSTREAM)
        self.push('250 OK')

    eleza smtp_RCPT(self, arg):
        ikiwa sio self.seen_greeting:
            self.push('503 Error: send HELO first');
            rudisha
        andika('===> RCPT', arg, file=DEBUGSTREAM)
        ikiwa sio self.mailfrom:
            self.push('503 Error: need MAIL command')
            rudisha
        syntaxerr = '501 Syntax: RCPT TO: <address>'
        ikiwa self.extended_smtp:
            syntaxerr += ' [SP <mail-parameters>]'
        ikiwa arg ni Tupu:
            self.push(syntaxerr)
            rudisha
        arg = self._strip_command_keyword('TO:', arg)
        address, params = self._getaddr(arg)
        ikiwa sio address:
            self.push(syntaxerr)
            rudisha
        ikiwa sio self.extended_smtp na params:
            self.push(syntaxerr)
            rudisha
        self.rcpt_options = params.upper().split()
        params = self._getparams(self.rcpt_options)
        ikiwa params ni Tupu:
            self.push(syntaxerr)
            rudisha
        # XXX currently there are no options we recognize.
        ikiwa len(params.keys()) > 0:
            self.push('555 RCPT TO parameters sio recognized ama sio implemented')
            rudisha
        self.rcpttos.append(address)
        andika('recips:', self.rcpttos, file=DEBUGSTREAM)
        self.push('250 OK')

    eleza smtp_RSET(self, arg):
        ikiwa arg:
            self.push('501 Syntax: RSET')
            rudisha
        self._set_rset_state()
        self.push('250 OK')

    eleza smtp_DATA(self, arg):
        ikiwa sio self.seen_greeting:
            self.push('503 Error: send HELO first');
            rudisha
        ikiwa sio self.rcpttos:
            self.push('503 Error: need RCPT command')
            rudisha
        ikiwa arg:
            self.push('501 Syntax: DATA')
            rudisha
        self.smtp_state = self.DATA
        self.set_terminator(b'\r\n.\r\n')
        self.push('354 End data ukijumuisha <CR><LF>.<CR><LF>')

    # Commands that have sio been implemented
    eleza smtp_EXPN(self, arg):
        self.push('502 EXPN sio implemented')


kundi SMTPServer(asyncore.dispatcher):
    # SMTPChannel kundi to use kila managing client connections
    channel_class = SMTPChannel

    eleza __init__(self, localaddr, remoteaddr,
                 data_size_limit=DATA_SIZE_DEFAULT, map=Tupu,
                 enable_SMTPUTF8=Uongo, decode_data=Uongo):
        self._localaddr = localaddr
        self._remoteaddr = remoteaddr
        self.data_size_limit = data_size_limit
        self.enable_SMTPUTF8 = enable_SMTPUTF8
        self._decode_data = decode_data
        ikiwa enable_SMTPUTF8 na decode_data:
            ashiria ValueError("decode_data na enable_SMTPUTF8 cannot"
                             " be set to Kweli at the same time")
        asyncore.dispatcher.__init__(self, map=map)
        jaribu:
            gai_results = socket.getaddrinfo(*localaddr,
                                             type=socket.SOCK_STREAM)
            self.create_socket(gai_results[0][0], gai_results[0][1])
            # try to re-use a server port ikiwa possible
            self.set_reuse_addr()
            self.bind(localaddr)
            self.listen(5)
        tatizo:
            self.close()
            raise
        isipokua:
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

    # API kila "doing something useful ukijumuisha the message"
    eleza process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """Override this abstract method to handle messages kutoka the client.

        peer ni a tuple containing (ipaddr, port) of the client that made the
        socket connection to our smtp port.

        mailkutoka ni the raw address the client claims the message ni coming
        from.

        rcpttos ni a list of raw addresses the client wishes to deliver the
        message to.

        data ni a string containing the entire full text of the message,
        headers (ikiwa supplied) na all.  It has been `de-transparencied'
        according to RFC 821, Section 4.5.2.  In other words, a line
        containing a `.' followed by other text has had the leading dot
        removed.

        kwargs ni a dictionary containing additional information.  It is
        empty ikiwa decode_data=Kweli was given kama init parameter, otherwise
        it will contain the following keys:
            'mail_options': list of parameters to the mail command.  All
                            elements are uppercase strings.  Example:
                            ['BODY=8BITMIME', 'SMTPUTF8'].
            'rcpt_options': same, kila the rcpt command.

        This function should rudisha Tupu kila a normal `250 Ok' response;
        otherwise, it should rudisha the desired response string kwenye RFC 821
        format.

        """
        ashiria NotImplementedError


kundi DebuggingServer(SMTPServer):

    eleza _print_message_content(self, peer, data):
        inheaders = 1
        lines = data.splitlines()
        kila line kwenye lines:
            # headers first
            ikiwa inheaders na sio line:
                peerheader = 'X-Peer: ' + peer[0]
                ikiwa sio isinstance(data, str):
                    # decoded_data=false; make header match other binary output
                    peerheader = repr(peerheader.encode('utf-8'))
                andika(peerheader)
                inheaders = 0
            ikiwa sio isinstance(data, str):
                # Avoid spurious 'str on bytes instance' warning.
                line = repr(line)
            andika(line)

    eleza process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
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
        ikiwa 'enable_SMTPUTF8' kwenye kwargs na kwargs['enable_SMTPUTF8']:
            ashiria ValueError("PureProxy does sio support SMTPUTF8.")
        super(PureProxy, self).__init__(*args, **kwargs)

    eleza process_message(self, peer, mailfrom, rcpttos, data):
        lines = data.split('\n')
        # Look kila the last header
        i = 0
        kila line kwenye lines:
            ikiwa sio line:
                koma
            i += 1
        lines.insert(i, 'X-Peer: %s' % peer[0])
        data = NEWLINE.join(lines)
        refused = self._deliver(mailfrom, rcpttos, data)
        # TBD: what to do ukijumuisha refused addresses?
        andika('we got some refusals:', refused, file=DEBUGSTREAM)

    eleza _deliver(self, mailfrom, rcpttos, data):
        agiza smtplib
        refused = {}
        jaribu:
            s = smtplib.SMTP()
            s.connect(self._remoteaddr[0], self._remoteaddr[1])
            jaribu:
                refused = s.sendmail(mailfrom, rcpttos, data)
            mwishowe:
                s.quit()
        tatizo smtplib.SMTPRecipientsRefused kama e:
            andika('got SMTPRecipientsRefused', file=DEBUGSTREAM)
            refused = e.recipients
        tatizo (OSError, smtplib.SMTPException) kama e:
            andika('got', e.__class__, file=DEBUGSTREAM)
            # All recipients were refused.  If the exception had an associated
            # error code, use it.  Otherwise,fake it ukijumuisha a non-triggering
            # exception code.
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            kila r kwenye rcpttos:
                refused[r] = (errcode, errmsg)
        rudisha refused


kundi MailmanProxy(PureProxy):
    eleza __init__(self, *args, **kwargs):
        ikiwa 'enable_SMTPUTF8' kwenye kwargs na kwargs['enable_SMTPUTF8']:
            ashiria ValueError("MailmanProxy does sio support SMTPUTF8.")
        super(PureProxy, self).__init__(*args, **kwargs)

    eleza process_message(self, peer, mailfrom, rcpttos, data):
        kutoka io agiza StringIO
        kutoka Mailman agiza Utils
        kutoka Mailman agiza Message
        kutoka Mailman agiza MailList
        # If the message ni to a Mailman mailing list, then we'll invoke the
        # Mailman script directly, without going through the real smtpd.
        # Otherwise we'll forward it to the local proxy kila disposition.
        listnames = []
        kila rcpt kwenye rcpttos:
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
                endelea
            listname = parts[0]
            ikiwa len(parts) == 2:
                command = parts[1]
            isipokua:
                command = ''
            ikiwa sio Utils.list_exists(listname) ama command haiko kwenye (
                    '', 'admin', 'owner', 'request', 'join', 'leave'):
                endelea
            listnames.append((rcpt, listname, command))
        # Remove all list recipients kutoka rcpttos na forward what we're sio
        # going to take care of ourselves.  Linear removal should be fine
        # since we don't expect a large number of recipients.
        kila rcpt, listname, command kwenye listnames:
            rcpttos.remove(rcpt)
        # If there's any non-list destined recipients left,
        andika('forwarding recips:', ' '.join(rcpttos), file=DEBUGSTREAM)
        ikiwa rcpttos:
            refused = self._deliver(mailfrom, rcpttos, data)
            # TBD: what to do ukijumuisha refused addresses?
            andika('we got refusals:', refused, file=DEBUGSTREAM)
        # Now deliver directly to the list commands
        mlists = {}
        s = StringIO(data)
        msg = Message.Message(s)
        # These headers are required kila the proper execution of Mailman.  All
        # MTAs kwenye existence seem to add these ikiwa the original message doesn't
        # have them.
        ikiwa sio msg.get('from'):
            msg['From'] = mailfrom
        ikiwa sio msg.get('date'):
            msg['Date'] = time.ctime(time.time())
        kila rcpt, listname, command kwenye listnames:
            andika('sending message to', rcpt, file=DEBUGSTREAM)
            mlist = mlists.get(listname)
            ikiwa sio mlist:
                mlist = MailList.MailList(listname, lock=0)
                mlists[listname] = mlist
            # dispatch on the type of command
            ikiwa command == '':
                # post
                msg.Enqueue(mlist, tolist=1)
            lasivyo command == 'admin':
                msg.Enqueue(mlist, toadmin=1)
            lasivyo command == 'owner':
                msg.Enqueue(mlist, toowner=1)
            lasivyo command == 'request':
                msg.Enqueue(mlist, torequest=1)
            lasivyo command kwenye ('join', 'leave'):
                # TBD: this ni a hack!
                ikiwa command == 'join':
                    msg['Subject'] = 'subscribe'
                isipokua:
                    msg['Subject'] = 'unsubscribe'
                msg.Enqueue(mlist, torequest=1)


kundi Options:
    setuid = Kweli
    classname = 'PureProxy'
    size_limit = Tupu
    enable_SMTPUTF8 = Uongo


eleza parseargs():
    global DEBUGSTREAM
    jaribu:
        opts, args = getopt.getopt(
            sys.argv[1:], 'nVhc:s:du',
            ['class=', 'nosetuid', 'version', 'help', 'size=', 'debug',
             'smtputf8'])
    tatizo getopt.error kama e:
        usage(1, e)

    options = Options()
    kila opt, arg kwenye opts:
        ikiwa opt kwenye ('-h', '--help'):
            usage(0)
        lasivyo opt kwenye ('-V', '--version'):
            andika(__version__)
            sys.exit(0)
        lasivyo opt kwenye ('-n', '--nosetuid'):
            options.setuid = Uongo
        lasivyo opt kwenye ('-c', '--class'):
            options.classname = arg
        lasivyo opt kwenye ('-d', '--debug'):
            DEBUGSTREAM = sys.stderr
        lasivyo opt kwenye ('-u', '--smtputf8'):
            options.enable_SMTPUTF8 = Kweli
        lasivyo opt kwenye ('-s', '--size'):
            jaribu:
                int_size = int(arg)
                options.size_limit = int_size
            tatizo:
                andika('Invalid size: ' + arg, file=sys.stderr)
                sys.exit(1)

    # parse the rest of the arguments
    ikiwa len(args) < 1:
        localspec = 'localhost:8025'
        remotespec = 'localhost:25'
    lasivyo len(args) < 2:
        localspec = args[0]
        remotespec = 'localhost:25'
    lasivyo len(args) < 3:
        localspec = args[0]
        remotespec = args[1]
    isipokua:
        usage(1, 'Invalid arguments: %s' % COMMASPACE.join(args))

    # split into host/port pairs
    i = localspec.find(':')
    ikiwa i < 0:
        usage(1, 'Bad local spec: %s' % localspec)
    options.localhost = localspec[:i]
    jaribu:
        options.localport = int(localspec[i+1:])
    tatizo ValueError:
        usage(1, 'Bad local port: %s' % localspec)
    i = remotespec.find(':')
    ikiwa i < 0:
        usage(1, 'Bad remote spec: %s' % remotespec)
    options.remotehost = remotespec[:i]
    jaribu:
        options.remoteport = int(remotespec[i+1:])
    tatizo ValueError:
        usage(1, 'Bad remote port: %s' % remotespec)
    rudisha options


ikiwa __name__ == '__main__':
    options = parseargs()
    # Become nobody
    classname = options.classname
    ikiwa "." kwenye classname:
        lastdot = classname.rfind(".")
        mod = __import__(classname[:lastdot], globals(), locals(), [""])
        classname = classname[lastdot+1:]
    isipokua:
        agiza __main__ kama mod
    class_ = getattr(mod, classname)
    proxy = class_((options.localhost, options.localport),
                   (options.remotehost, options.remoteport),
                   options.size_limit, enable_SMTPUTF8=options.enable_SMTPUTF8)
    ikiwa options.setuid:
        jaribu:
            agiza pwd
        tatizo ImportError:
            andika('Cannot agiza module "pwd"; try running ukijumuisha -n option.', file=sys.stderr)
            sys.exit(1)
        nobody = pwd.getpwnam('nobody')[2]
        jaribu:
            os.setuid(nobody)
        tatizo PermissionError:
            andika('Cannot setuid "nobody"; try running ukijumuisha -n option.', file=sys.stderr)
            sys.exit(1)
    jaribu:
        asyncore.loop()
    tatizo KeyboardInterrupt:
        pita
