"""Mock socket module used by the smtpd na smtplib tests.
"""

# imported kila _GLOBAL_DEFAULT_TIMEOUT
agiza socket as socket_module

# Mock socket module
_defaulttimeout = Tupu
_reply_data = Tupu

# This ni used to queue up data to be read through socket.makefile, typically
# *before* the socket object ni even created. It ni intended to handle a single
# line which the socket will feed on recv() ama makefile().
eleza reply_with(line):
    global _reply_data
    _reply_data = line


kundi MockFile:
    """Mock file object returned by MockSocket.makefile().
    """
    eleza __init__(self, lines):
        self.lines = lines
    eleza readline(self, limit=-1):
        result = self.lines.pop(0) + b'\r\n'
        ikiwa limit >= 0:
            # Re-insert the line, removing the \r\n we added.
            self.lines.insert(0, result[limit:-2])
            result = result[:limit]
        rudisha result
    eleza close(self):
        pass


kundi MockSocket:
    """Mock socket object used by smtpd na smtplib tests.
    """
    eleza __init__(self, family=Tupu):
        global _reply_data
        self.family = family
        self.output = []
        self.lines = []
        ikiwa _reply_data:
            self.lines.append(_reply_data)
            _reply_data = Tupu
        self.conn = Tupu
        self.timeout = Tupu

    eleza queue_recv(self, line):
        self.lines.append(line)

    eleza recv(self, bufsize, flags=Tupu):
        data = self.lines.pop(0) + b'\r\n'
        rudisha data

    eleza fileno(self):
        rudisha 0

    eleza settimeout(self, timeout):
        ikiwa timeout ni Tupu:
            self.timeout = _defaulttimeout
        isipokua:
            self.timeout = timeout

    eleza gettimeout(self):
        rudisha self.timeout

    eleza setsockopt(self, level, optname, value):
        pass

    eleza getsockopt(self, level, optname, buflen=Tupu):
        rudisha 0

    eleza bind(self, address):
        pass

    eleza accept(self):
        self.conn = MockSocket()
        rudisha self.conn, 'c'

    eleza getsockname(self):
        rudisha ('0.0.0.0', 0)

    eleza setblocking(self, flag):
        pass

    eleza listen(self, backlog):
        pass

    eleza makefile(self, mode='r', bufsize=-1):
        handle = MockFile(self.lines)
        rudisha handle

    eleza sendall(self, buffer, flags=Tupu):
        self.last = data
        self.output.append(data)
        rudisha len(data)

    eleza send(self, data, flags=Tupu):
        self.last = data
        self.output.append(data)
        rudisha len(data)

    eleza getpeername(self):
        rudisha ('peer-address', 'peer-port')

    eleza close(self):
        pass


eleza socket(family=Tupu, type=Tupu, proto=Tupu):
    rudisha MockSocket(family)

eleza create_connection(address, timeout=socket_module._GLOBAL_DEFAULT_TIMEOUT,
                      source_address=Tupu):
    jaribu:
        int_port = int(address[1])
    except ValueError:
         ashiria error
    ms = MockSocket()
    ikiwa timeout ni socket_module._GLOBAL_DEFAULT_TIMEOUT:
        timeout = getdefaulttimeout()
    ms.settimeout(timeout)
    rudisha ms


eleza setdefaulttimeout(timeout):
    global _defaulttimeout
    _defaulttimeout = timeout


eleza getdefaulttimeout():
    rudisha _defaulttimeout


eleza getfqdn():
    rudisha ""


eleza gethostname():
    pass


eleza gethostbyname(name):
    rudisha ""

eleza getaddrinfo(*args, **kw):
    rudisha socket_module.getaddrinfo(*args, **kw)

gaierror = socket_module.gaierror
error = socket_module.error


# Constants
AF_INET = socket_module.AF_INET
AF_INET6 = socket_module.AF_INET6
SOCK_STREAM = socket_module.SOCK_STREAM
SOL_SOCKET = Tupu
SO_REUSEADDR = Tupu
