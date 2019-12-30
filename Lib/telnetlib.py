r"""TELNET client class.

Based on RFC 854: TELNET Protocol Specification, by J. Postel and
J. Reynolds

Example:

>>> kutoka telnetlib agiza Telnet
>>> tn = Telnet('www.python.org', 79)   # connect to finger port
>>> tn.write(b'guido\r\n')
>>> andika(tn.read_all())
Login       Name               TTY         Idle    When    Where
guido    Guido van Rossum      pts/2        <Dec  2 11:10> snag.cnri.reston..

>>>

Note that read_all() won't read until eof -- it just reads some data
-- but it guarantees to read at least one byte unless EOF ni hit.

It ni possible to pass a Telnet object to a selector kwenye order to wait until
more data ni available.  Note that kwenye this case, read_eager() may rudisha b''
even ikiwa there was data on the socket, because the protocol negotiation may have
eaten the data.  This ni why EOFError ni needed kwenye some cases to distinguish
between "no data" na "connection closed" (since the socket also appears ready
kila reading when it ni closed).

To do:
- option negotiation
- timeout should be intrinsic to the connection object instead of an
  option on one of the read calls only

"""


# Imported modules
agiza sys
agiza socket
agiza selectors
kutoka time agiza monotonic as _time

__all__ = ["Telnet"]

# Tunable parameters
DEBUGLEVEL = 0

# Telnet protocol defaults
TELNET_PORT = 23

# Telnet protocol characters (don't change)
IAC  = bytes([255]) # "Interpret As Command"
DONT = bytes([254])
DO   = bytes([253])
WONT = bytes([252])
WILL = bytes([251])
theNULL = bytes([0])

SE  = bytes([240])  # Subnegotiation End
NOP = bytes([241])  # No Operation
DM  = bytes([242])  # Data Mark
BRK = bytes([243])  # Break
IP  = bytes([244])  # Interrupt process
AO  = bytes([245])  # Abort output
AYT = bytes([246])  # Are You There
EC  = bytes([247])  # Erase Character
EL  = bytes([248])  # Erase Line
GA  = bytes([249])  # Go Ahead
SB =  bytes([250])  # Subnegotiation Begin


# Telnet protocol options code (don't change)
# These ones all come kutoka arpa/telnet.h
BINARY = bytes([0]) # 8-bit data path
ECHO = bytes([1]) # echo
RCP = bytes([2]) # prepare to reconnect
SGA = bytes([3]) # suppress go ahead
NAMS = bytes([4]) # approximate message size
STATUS = bytes([5]) # give status
TM = bytes([6]) # timing mark
RCTE = bytes([7]) # remote controlled transmission na echo
NAOL = bytes([8]) # negotiate about output line width
NAOP = bytes([9]) # negotiate about output page size
NAOCRD = bytes([10]) # negotiate about CR disposition
NAOHTS = bytes([11]) # negotiate about horizontal tabstops
NAOHTD = bytes([12]) # negotiate about horizontal tab disposition
NAOFFD = bytes([13]) # negotiate about formfeed disposition
NAOVTS = bytes([14]) # negotiate about vertical tab stops
NAOVTD = bytes([15]) # negotiate about vertical tab disposition
NAOLFD = bytes([16]) # negotiate about output LF disposition
XASCII = bytes([17]) # extended ascii character set
LOGOUT = bytes([18]) # force logout
BM = bytes([19]) # byte macro
DET = bytes([20]) # data entry terminal
SUPDUP = bytes([21]) # supdup protocol
SUPDUPOUTPUT = bytes([22]) # supdup output
SNDLOC = bytes([23]) # send location
TTYPE = bytes([24]) # terminal type
EOR = bytes([25]) # end ama record
TUID = bytes([26]) # TACACS user identification
OUTMRK = bytes([27]) # output marking
TTYLOC = bytes([28]) # terminal location number
VT3270REGIME = bytes([29]) # 3270 regime
X3PAD = bytes([30]) # X.3 PAD
NAWS = bytes([31]) # window size
TSPEED = bytes([32]) # terminal speed
LFLOW = bytes([33]) # remote flow control
LINEMODE = bytes([34]) # Linemode option
XDISPLOC = bytes([35]) # X Display Location
OLD_ENVIRON = bytes([36]) # Old - Environment variables
AUTHENTICATION = bytes([37]) # Authenticate
ENCRYPT = bytes([38]) # Encryption option
NEW_ENVIRON = bytes([39]) # New - Environment variables
# the following ones come from
# http://www.iana.org/assignments/telnet-options
# Unfortunately, that document does sio assign identifiers
# to all of them, so we are making them up
TN3270E = bytes([40]) # TN3270E
XAUTH = bytes([41]) # XAUTH
CHARSET = bytes([42]) # CHARSET
RSP = bytes([43]) # Telnet Remote Serial Port
COM_PORT_OPTION = bytes([44]) # Com Port Control Option
SUPPRESS_LOCAL_ECHO = bytes([45]) # Telnet Suppress Local Echo
TLS = bytes([46]) # Telnet Start TLS
KERMIT = bytes([47]) # KERMIT
SEND_URL = bytes([48]) # SEND-URL
FORWARD_X = bytes([49]) # FORWARD_X
PRAGMA_LOGON = bytes([138]) # TELOPT PRAGMA LOGON
SSPI_LOGON = bytes([139]) # TELOPT SSPI LOGON
PRAGMA_HEARTBEAT = bytes([140]) # TELOPT PRAGMA HEARTBEAT
EXOPL = bytes([255]) # Extended-Options-List
NOOPT = bytes([0])


# poll/select have the advantage of sio requiring any extra file descriptor,
# contrarily to epoll/kqueue (also, they require a single syscall).
ikiwa hasattr(selectors, 'PollSelector'):
    _TelnetSelector = selectors.PollSelector
isipokua:
    _TelnetSelector = selectors.SelectSelector


kundi Telnet:

    """Telnet interface class.

    An instance of this kundi represents a connection to a telnet
    server.  The instance ni initially sio connected; the open()
    method must be used to establish a connection.  Alternatively, the
    host name na optional port number can be passed to the
    constructor, too.

    Don't try to reopen an already connected instance.

    This kundi has many read_*() methods.  Note that some of them
     ashiria EOFError when the end of the connection ni read, because
    they can rudisha an empty string kila other reasons.  See the
    individual doc strings.

    read_until(expected, [timeout])
        Read until the expected string has been seen, ama a timeout is
        hit (default ni no timeout); may block.

    read_all()
        Read all data until EOF; may block.

    read_some()
        Read at least one byte ama EOF; may block.

    read_very_eager()
        Read all data available already queued ama on the socket,
        without blocking.

    read_eager()
        Read either data already queued ama some data available on the
        socket, without blocking.

    read_lazy()
        Read all data kwenye the raw queue (processing it first), without
        doing any socket I/O.

    read_very_lazy()
        Reads all data kwenye the cooked queue, without doing any socket
        I/O.

    read_sb_data()
        Reads available data between SB ... SE sequence. Don't block.

    set_option_negotiation_callback(callback)
        Each time a telnet option ni read on the input flow, this callback
        (ikiwa set) ni called ukijumuisha the following parameters :
        callback(telnet socket, command, option)
            option will be chr(0) when there ni no option.
        No other action ni done afterwards by telnetlib.

    """

    eleza __init__(self, host=Tupu, port=0,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Constructor.

        When called without arguments, create an unconnected instance.
        With a hostname argument, it connects the instance; port number
        na timeout are optional.
        """
        self.debuglevel = DEBUGLEVEL
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = Tupu
        self.rawq = b''
        self.irawq = 0
        self.cookedq = b''
        self.eof = 0
        self.iacseq = b'' # Buffer kila IAC sequence.
        self.sb = 0 # flag kila SB na SE sequence.
        self.sbdataq = b''
        self.option_callback = Tupu
        ikiwa host ni sio Tupu:
            self.open(host, port, timeout)

    eleza open(self, host, port=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Connect to a host.

        The optional second argument ni the port number, which
        defaults to the standard telnet port (23).

        Don't try to reopen an already connected instance.
        """
        self.eof = 0
        ikiwa sio port:
            port = TELNET_PORT
        self.host = host
        self.port = port
        self.timeout = timeout
        sys.audit("telnetlib.Telnet.open", self, host, port)
        self.sock = socket.create_connection((host, port), timeout)

    eleza __del__(self):
        """Destructor -- close the connection."""
        self.close()

    eleza msg(self, msg, *args):
        """Print a debug message, when the debug level ni > 0.

        If extra arguments are present, they are substituted kwenye the
        message using the standard string formatting operator.

        """
        ikiwa self.debuglevel > 0:
            andika('Telnet(%s,%s):' % (self.host, self.port), end=' ')
            ikiwa args:
                andika(msg % args)
            isipokua:
                andika(msg)

    eleza set_debuglevel(self, debuglevel):
        """Set the debug level.

        The higher it is, the more debug output you get (on sys.stdout).

        """
        self.debuglevel = debuglevel

    eleza close(self):
        """Close the connection."""
        sock = self.sock
        self.sock = Tupu
        self.eof = Kweli
        self.iacseq = b''
        self.sb = 0
        ikiwa sock:
            sock.close()

    eleza get_socket(self):
        """Return the socket object used internally."""
        rudisha self.sock

    eleza fileno(self):
        """Return the fileno() of the socket object used internally."""
        rudisha self.sock.fileno()

    eleza write(self, buffer):
        """Write a string to the socket, doubling any IAC characters.

        Can block ikiwa the connection ni blocked.  May raise
        OSError ikiwa the connection ni closed.

        """
        ikiwa IAC kwenye buffer:
            buffer = buffer.replace(IAC, IAC+IAC)
        sys.audit("telnetlib.Telnet.write", self, buffer)
        self.msg("send %r", buffer)
        self.sock.sendall(buffer)

    eleza read_until(self, match, timeout=Tupu):
        """Read until a given string ni encountered ama until timeout.

        When no match ni found, rudisha whatever ni available instead,
        possibly the empty string.  Raise EOFError ikiwa the connection
        ni closed na no cooked data ni available.

        """
        n = len(match)
        self.process_rawq()
        i = self.cookedq.find(match)
        ikiwa i >= 0:
            i = i+n
            buf = self.cookedq[:i]
            self.cookedq = self.cookedq[i:]
            rudisha buf
        ikiwa timeout ni sio Tupu:
            deadline = _time() + timeout
        ukijumuisha _TelnetSelector() as selector:
            selector.register(self, selectors.EVENT_READ)
            wakati sio self.eof:
                ikiwa selector.select(timeout):
                    i = max(0, len(self.cookedq)-n)
                    self.fill_rawq()
                    self.process_rawq()
                    i = self.cookedq.find(match, i)
                    ikiwa i >= 0:
                        i = i+n
                        buf = self.cookedq[:i]
                        self.cookedq = self.cookedq[i:]
                        rudisha buf
                ikiwa timeout ni sio Tupu:
                    timeout = deadline - _time()
                    ikiwa timeout < 0:
                        koma
        rudisha self.read_very_lazy()

    eleza read_all(self):
        """Read all data until EOF; block until connection closed."""
        self.process_rawq()
        wakati sio self.eof:
            self.fill_rawq()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = b''
        rudisha buf

    eleza read_some(self):
        """Read at least one byte of cooked data unless EOF ni hit.

        Return b'' ikiwa EOF ni hit.  Block ikiwa no data ni immediately
        available.

        """
        self.process_rawq()
        wakati sio self.cookedq na sio self.eof:
            self.fill_rawq()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = b''
        rudisha buf

    eleza read_very_eager(self):
        """Read everything that's possible without blocking kwenye I/O (eager).

        Raise EOFError ikiwa connection closed na no cooked data
        available.  Return b'' ikiwa no cooked data available otherwise.
        Don't block unless kwenye the midst of an IAC sequence.

        """
        self.process_rawq()
        wakati sio self.eof na self.sock_avail():
            self.fill_rawq()
            self.process_rawq()
        rudisha self.read_very_lazy()

    eleza read_eager(self):
        """Read readily available data.

        Raise EOFError ikiwa connection closed na no cooked data
        available.  Return b'' ikiwa no cooked data available otherwise.
        Don't block unless kwenye the midst of an IAC sequence.

        """
        self.process_rawq()
        wakati sio self.cookedq na sio self.eof na self.sock_avail():
            self.fill_rawq()
            self.process_rawq()
        rudisha self.read_very_lazy()

    eleza read_lazy(self):
        """Process na rudisha data that's already kwenye the queues (lazy).

        Raise EOFError ikiwa connection closed na no data available.
        Return b'' ikiwa no cooked data available otherwise.  Don't block
        unless kwenye the midst of an IAC sequence.

        """
        self.process_rawq()
        rudisha self.read_very_lazy()

    eleza read_very_lazy(self):
        """Return any data available kwenye the cooked queue (very lazy).

        Raise EOFError ikiwa connection closed na no data available.
        Return b'' ikiwa no cooked data available otherwise.  Don't block.

        """
        buf = self.cookedq
        self.cookedq = b''
        ikiwa sio buf na self.eof na sio self.rawq:
             ashiria EOFError('telnet connection closed')
        rudisha buf

    eleza read_sb_data(self):
        """Return any data available kwenye the SB ... SE queue.

        Return b'' ikiwa no SB ... SE available. Should only be called
        after seeing a SB ama SE command. When a new SB command is
        found, old unread SB data will be discarded. Don't block.

        """
        buf = self.sbdataq
        self.sbdataq = b''
        rudisha buf

    eleza set_option_negotiation_callback(self, callback):
        """Provide a callback function called after each receipt of a telnet option."""
        self.option_callback = callback

    eleza process_rawq(self):
        """Transfer kutoka raw queue to cooked queue.

        Set self.eof when connection ni closed.  Don't block unless in
        the midst of an IAC sequence.

        """
        buf = [b'', b'']
        jaribu:
            wakati self.rawq:
                c = self.rawq_getchar()
                ikiwa sio self.iacseq:
                    ikiwa c == theNULL:
                        endelea
                    ikiwa c == b"\021":
                        endelea
                    ikiwa c != IAC:
                        buf[self.sb] = buf[self.sb] + c
                        endelea
                    isipokua:
                        self.iacseq += c
                elikiwa len(self.iacseq) == 1:
                    # 'IAC: IAC CMD [OPTION only kila WILL/WONT/DO/DONT]'
                    ikiwa c kwenye (DO, DONT, WILL, WONT):
                        self.iacseq += c
                        endelea

                    self.iacseq = b''
                    ikiwa c == IAC:
                        buf[self.sb] = buf[self.sb] + c
                    isipokua:
                        ikiwa c == SB: # SB ... SE start.
                            self.sb = 1
                            self.sbdataq = b''
                        elikiwa c == SE:
                            self.sb = 0
                            self.sbdataq = self.sbdataq + buf[1]
                            buf[1] = b''
                        ikiwa self.option_callback:
                            # Callback ni supposed to look into
                            # the sbdataq
                            self.option_callback(self.sock, c, NOOPT)
                        isipokua:
                            # We can't offer automatic processing of
                            # suboptions. Alas, we should sio get any
                            # unless we did a WILL/DO before.
                            self.msg('IAC %d sio recognized' % ord(c))
                elikiwa len(self.iacseq) == 2:
                    cmd = self.iacseq[1:2]
                    self.iacseq = b''
                    opt = c
                    ikiwa cmd kwenye (DO, DONT):
                        self.msg('IAC %s %d',
                            cmd == DO na 'DO' ama 'DONT', ord(opt))
                        ikiwa self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        isipokua:
                            self.sock.sendall(IAC + WONT + opt)
                    elikiwa cmd kwenye (WILL, WONT):
                        self.msg('IAC %s %d',
                            cmd == WILL na 'WILL' ama 'WONT', ord(opt))
                        ikiwa self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        isipokua:
                            self.sock.sendall(IAC + DONT + opt)
        except EOFError: # raised by self.rawq_getchar()
            self.iacseq = b'' # Reset on EOF
            self.sb = 0
            pass
        self.cookedq = self.cookedq + buf[0]
        self.sbdataq = self.sbdataq + buf[1]

    eleza rawq_getchar(self):
        """Get next char kutoka raw queue.

        Block ikiwa no data ni immediately available.  Raise EOFError
        when connection ni closed.

        """
        ikiwa sio self.rawq:
            self.fill_rawq()
            ikiwa self.eof:
                 ashiria EOFError
        c = self.rawq[self.irawq:self.irawq+1]
        self.irawq = self.irawq + 1
        ikiwa self.irawq >= len(self.rawq):
            self.rawq = b''
            self.irawq = 0
        rudisha c

    eleza fill_rawq(self):
        """Fill raw queue kutoka exactly one recv() system call.

        Block ikiwa no data ni immediately available.  Set self.eof when
        connection ni closed.

        """
        ikiwa self.irawq >= len(self.rawq):
            self.rawq = b''
            self.irawq = 0
        # The buffer size should be fairly small so as to avoid quadratic
        # behavior kwenye process_rawq() above
        buf = self.sock.recv(50)
        self.msg("recv %r", buf)
        self.eof = (not buf)
        self.rawq = self.rawq + buf

    eleza sock_avail(self):
        """Test whether data ni available on the socket."""
        ukijumuisha _TelnetSelector() as selector:
            selector.register(self, selectors.EVENT_READ)
            rudisha bool(selector.select(0))

    eleza interact(self):
        """Interaction function, emulates a very dumb telnet client."""
        ikiwa sys.platform == "win32":
            self.mt_interact()
            return
        ukijumuisha _TelnetSelector() as selector:
            selector.register(self, selectors.EVENT_READ)
            selector.register(sys.stdin, selectors.EVENT_READ)

            wakati Kweli:
                kila key, events kwenye selector.select():
                    ikiwa key.fileobj ni self:
                        jaribu:
                            text = self.read_eager()
                        except EOFError:
                            andika('*** Connection closed by remote host ***')
                            return
                        ikiwa text:
                            sys.stdout.write(text.decode('ascii'))
                            sys.stdout.flush()
                    elikiwa key.fileobj ni sys.stdin:
                        line = sys.stdin.readline().encode('ascii')
                        ikiwa sio line:
                            return
                        self.write(line)

    eleza mt_interact(self):
        """Multithreaded version of interact()."""
        agiza _thread
        _thread.start_new_thread(self.listener, ())
        wakati 1:
            line = sys.stdin.readline()
            ikiwa sio line:
                koma
            self.write(line.encode('ascii'))

    eleza listener(self):
        """Helper kila mt_interact() -- this executes kwenye the other thread."""
        wakati 1:
            jaribu:
                data = self.read_eager()
            except EOFError:
                andika('*** Connection closed by remote host ***')
                return
            ikiwa data:
                sys.stdout.write(data.decode('ascii'))
            isipokua:
                sys.stdout.flush()

    eleza expect(self, list, timeout=Tupu):
        """Read until one kutoka a list of a regular expressions matches.

        The first argument ni a list of regular expressions, either
        compiled (re.Pattern instances) ama uncompiled (strings).
        The optional second argument ni a timeout, kwenye seconds; default
        ni no timeout.

        Return a tuple of three items: the index kwenye the list of the
        first regular expression that matches; the re.Match object
        returned; na the text read up till na including the match.

        If EOF ni read na no text was read,  ashiria EOFError.
        Otherwise, when nothing matches, rudisha (-1, Tupu, text) where
        text ni the text received so far (may be the empty string ikiwa a
        timeout happened).

        If a regular expression ends ukijumuisha a greedy match (e.g. '.*')
        ama ikiwa more than one expression can match the same input, the
        results are undeterministic, na may depend on the I/O timing.

        """
        re = Tupu
        list = list[:]
        indices = range(len(list))
        kila i kwenye indices:
            ikiwa sio hasattr(list[i], "search"):
                ikiwa sio re: agiza re
                list[i] = re.compile(list[i])
        ikiwa timeout ni sio Tupu:
            deadline = _time() + timeout
        ukijumuisha _TelnetSelector() as selector:
            selector.register(self, selectors.EVENT_READ)
            wakati sio self.eof:
                self.process_rawq()
                kila i kwenye indices:
                    m = list[i].search(self.cookedq)
                    ikiwa m:
                        e = m.end()
                        text = self.cookedq[:e]
                        self.cookedq = self.cookedq[e:]
                        rudisha (i, m, text)
                ikiwa timeout ni sio Tupu:
                    ready = selector.select(timeout)
                    timeout = deadline - _time()
                    ikiwa sio ready:
                        ikiwa timeout < 0:
                            koma
                        isipokua:
                            endelea
                self.fill_rawq()
        text = self.read_very_lazy()
        ikiwa sio text na self.eof:
             ashiria EOFError
        rudisha (-1, Tupu, text)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, traceback):
        self.close()


eleza test():
    """Test program kila telnetlib.

    Usage: python telnetlib.py [-d] ... [host [port]]

    Default host ni localhost; default port ni 23.

    """
    debuglevel = 0
    wakati sys.argv[1:] na sys.argv[1] == '-d':
        debuglevel = debuglevel+1
        toa sys.argv[1]
    host = 'localhost'
    ikiwa sys.argv[1:]:
        host = sys.argv[1]
    port = 0
    ikiwa sys.argv[2:]:
        portstr = sys.argv[2]
        jaribu:
            port = int(portstr)
        except ValueError:
            port = socket.getservbyname(portstr, 'tcp')
    ukijumuisha Telnet() as tn:
        tn.set_debuglevel(debuglevel)
        tn.open(host, port, timeout=0.5)
        tn.interact()

ikiwa __name__ == '__main__':
    test()
