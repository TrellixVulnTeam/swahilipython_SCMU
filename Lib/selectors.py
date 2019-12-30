"""Selectors module.

This module allows high-level na efficient I/O multiplexing, built upon the
`select` module primitives.
"""


kutoka abc agiza ABCMeta, abstractmethod
kutoka collections agiza namedtuple
kutoka collections.abc agiza Mapping
agiza math
agiza select
agiza sys


# generic events, that must be mapped to implementation-specific ones
EVENT_READ = (1 << 0)
EVENT_WRITE = (1 << 1)


eleza _fileobj_to_fd(fileobj):
    """Return a file descriptor kutoka a file object.

    Parameters:
    fileobj -- file object ama file descriptor

    Returns:
    corresponding file descriptor

    Raises:
    ValueError ikiwa the object ni invalid
    """
    ikiwa isinstance(fileobj, int):
        fd = fileobj
    isipokua:
        jaribu:
            fd = int(fileobj.fileno())
        tatizo (AttributeError, TypeError, ValueError):
            ashiria ValueError("Invalid file object: "
                             "{!r}".format(fileobj)) kutoka Tupu
    ikiwa fd < 0:
        ashiria ValueError("Invalid file descriptor: {}".format(fd))
    rudisha fd


SelectorKey = namedtuple('SelectorKey', ['fileobj', 'fd', 'events', 'data'])

SelectorKey.__doc__ = """SelectorKey(fileobj, fd, events, data)

    Object used to associate a file object to its backing
    file descriptor, selected event mask, na attached data.
"""
ikiwa sys.version_info >= (3, 5):
    SelectorKey.fileobj.__doc__ = 'File object registered.'
    SelectorKey.fd.__doc__ = 'Underlying file descriptor.'
    SelectorKey.events.__doc__ = 'Events that must be waited kila on this file object.'
    SelectorKey.data.__doc__ = ('''Optional opaque data associated to this file object.
    For example, this could be used to store a per-client session ID.''')

kundi _SelectorMapping(Mapping):
    """Mapping of file objects to selector keys."""

    eleza __init__(self, selector):
        self._selector = selector

    eleza __len__(self):
        rudisha len(self._selector._fd_to_key)

    eleza __getitem__(self, fileobj):
        jaribu:
            fd = self._selector._fileobj_lookup(fileobj)
            rudisha self._selector._fd_to_key[fd]
        tatizo KeyError:
            ashiria KeyError("{!r} ni sio registered".format(fileobj)) kutoka Tupu

    eleza __iter__(self):
        rudisha iter(self._selector._fd_to_key)


kundi BaseSelector(metaclass=ABCMeta):
    """Selector abstract base class.

    A selector supports registering file objects to be monitored kila specific
    I/O events.

    A file object ni a file descriptor ama any object ukijumuisha a `fileno()` method.
    An arbitrary object can be attached to the file object, which can be used
    kila example to store context information, a callback, etc.

    A selector can use various implementations (select(), poll(), epoll()...)
    depending on the platform. The default `Selector` kundi uses the most
    efficient implementation on the current platform.
    """

    @abstractmethod
    eleza register(self, fileobj, events, data=Tupu):
        """Register a file object.

        Parameters:
        fileobj -- file object ama file descriptor
        events  -- events to monitor (bitwise mask of EVENT_READ|EVENT_WRITE)
        data    -- attached data

        Returns:
        SelectorKey instance

        Raises:
        ValueError ikiwa events ni invalid
        KeyError ikiwa fileobj ni already registered
        OSError ikiwa fileobj ni closed ama otherwise ni unacceptable to
                the underlying system call (ikiwa a system call ni made)

        Note:
        OSError may ama may sio be ashiriad
        """
        ashiria NotImplementedError

    @abstractmethod
    eleza unregister(self, fileobj):
        """Unregister a file object.

        Parameters:
        fileobj -- file object ama file descriptor

        Returns:
        SelectorKey instance

        Raises:
        KeyError ikiwa fileobj ni sio registered

        Note:
        If fileobj ni registered but has since been closed this does
        *not* ashiria OSError (even ikiwa the wrapped syscall does)
        """
        ashiria NotImplementedError

    eleza modify(self, fileobj, events, data=Tupu):
        """Change a registered file object monitored events ama attached data.

        Parameters:
        fileobj -- file object ama file descriptor
        events  -- events to monitor (bitwise mask of EVENT_READ|EVENT_WRITE)
        data    -- attached data

        Returns:
        SelectorKey instance

        Raises:
        Anything that unregister() ama register() ashirias
        """
        self.unregister(fileobj)
        rudisha self.register(fileobj, events, data)

    @abstractmethod
    eleza select(self, timeout=Tupu):
        """Perform the actual selection, until some monitored file objects are
        ready ama a timeout expires.

        Parameters:
        timeout -- ikiwa timeout > 0, this specifies the maximum wait time, in
                   seconds
                   ikiwa timeout <= 0, the select() call won't block, na will
                   report the currently ready file objects
                   ikiwa timeout ni Tupu, select() will block until a monitored
                   file object becomes ready

        Returns:
        list of (key, events) kila ready file objects
        `events` ni a bitwise mask of EVENT_READ|EVENT_WRITE
        """
        ashiria NotImplementedError

    eleza close(self):
        """Close the selector.

        This must be called to make sure that any underlying resource ni freed.
        """
        pita

    eleza get_key(self, fileobj):
        """Return the key associated to a registered file object.

        Returns:
        SelectorKey kila this file object
        """
        mapping = self.get_map()
        ikiwa mapping ni Tupu:
            ashiria RuntimeError('Selector ni closed')
        jaribu:
            rudisha mapping[fileobj]
        tatizo KeyError:
            ashiria KeyError("{!r} ni sio registered".format(fileobj)) kutoka Tupu

    @abstractmethod
    eleza get_map(self):
        """Return a mapping of file objects to selector keys."""
        ashiria NotImplementedError

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()


kundi _BaseSelectorImpl(BaseSelector):
    """Base selector implementation."""

    eleza __init__(self):
        # this maps file descriptors to keys
        self._fd_to_key = {}
        # read-only mapping rudishaed by get_map()
        self._map = _SelectorMapping(self)

    eleza _fileobj_lookup(self, fileobj):
        """Return a file descriptor kutoka a file object.

        This wraps _fileobj_to_fd() to do an exhaustive search kwenye case
        the object ni invalid but we still have it kwenye our map.  This
        ni used by unregister() so we can unregister an object that
        was previously registered even ikiwa it ni closed.  It ni also
        used by _SelectorMapping.
        """
        jaribu:
            rudisha _fileobj_to_fd(fileobj)
        tatizo ValueError:
            # Do an exhaustive search.
            kila key kwenye self._fd_to_key.values():
                ikiwa key.fileobj ni fileobj:
                    rudisha key.fd
            # Raise ValueError after all.
            ashiria

    eleza register(self, fileobj, events, data=Tupu):
        ikiwa (sio events) ama (events & ~(EVENT_READ | EVENT_WRITE)):
            ashiria ValueError("Invalid events: {!r}".format(events))

        key = SelectorKey(fileobj, self._fileobj_lookup(fileobj), events, data)

        ikiwa key.fd kwenye self._fd_to_key:
            ashiria KeyError("{!r} (FD {}) ni already registered"
                           .format(fileobj, key.fd))

        self._fd_to_key[key.fd] = key
        rudisha key

    eleza unregister(self, fileobj):
        jaribu:
            key = self._fd_to_key.pop(self._fileobj_lookup(fileobj))
        tatizo KeyError:
            ashiria KeyError("{!r} ni sio registered".format(fileobj)) kutoka Tupu
        rudisha key

    eleza modify(self, fileobj, events, data=Tupu):
        jaribu:
            key = self._fd_to_key[self._fileobj_lookup(fileobj)]
        tatizo KeyError:
            ashiria KeyError("{!r} ni sio registered".format(fileobj)) kutoka Tupu
        ikiwa events != key.events:
            self.unregister(fileobj)
            key = self.register(fileobj, events, data)
        lasivyo data != key.data:
            # Use a shortcut to update the data.
            key = key._replace(data=data)
            self._fd_to_key[key.fd] = key
        rudisha key

    eleza close(self):
        self._fd_to_key.clear()
        self._map = Tupu

    eleza get_map(self):
        rudisha self._map

    eleza _key_from_fd(self, fd):
        """Return the key associated to a given file descriptor.

        Parameters:
        fd -- file descriptor

        Returns:
        corresponding key, ama Tupu ikiwa sio found
        """
        jaribu:
            rudisha self._fd_to_key[fd]
        tatizo KeyError:
            rudisha Tupu


kundi SelectSelector(_BaseSelectorImpl):
    """Select-based selector."""

    eleza __init__(self):
        super().__init__()
        self._readers = set()
        self._writers = set()

    eleza register(self, fileobj, events, data=Tupu):
        key = super().register(fileobj, events, data)
        ikiwa events & EVENT_READ:
            self._readers.add(key.fd)
        ikiwa events & EVENT_WRITE:
            self._writers.add(key.fd)
        rudisha key

    eleza unregister(self, fileobj):
        key = super().unregister(fileobj)
        self._readers.discard(key.fd)
        self._writers.discard(key.fd)
        rudisha key

    ikiwa sys.platform == 'win32':
        eleza _select(self, r, w, _, timeout=Tupu):
            r, w, x = select.select(r, w, w, timeout)
            rudisha r, w + x, []
    isipokua:
        _select = select.select

    eleza select(self, timeout=Tupu):
        timeout = Tupu ikiwa timeout ni Tupu isipokua max(timeout, 0)
        ready = []
        jaribu:
            r, w, _ = self._select(self._readers, self._writers, [], timeout)
        tatizo InterruptedError:
            rudisha ready
        r = set(r)
        w = set(w)
        kila fd kwenye r | w:
            events = 0
            ikiwa fd kwenye r:
                events |= EVENT_READ
            ikiwa fd kwenye w:
                events |= EVENT_WRITE

            key = self._key_from_fd(fd)
            ikiwa key:
                ready.append((key, events & key.events))
        rudisha ready


kundi _PollLikeSelector(_BaseSelectorImpl):
    """Base kundi shared between poll, epoll na devpoll selectors."""
    _selector_cls = Tupu
    _EVENT_READ = Tupu
    _EVENT_WRITE = Tupu

    eleza __init__(self):
        super().__init__()
        self._selector = self._selector_cls()

    eleza register(self, fileobj, events, data=Tupu):
        key = super().register(fileobj, events, data)
        poller_events = 0
        ikiwa events & EVENT_READ:
            poller_events |= self._EVENT_READ
        ikiwa events & EVENT_WRITE:
            poller_events |= self._EVENT_WRITE
        jaribu:
            self._selector.register(key.fd, poller_events)
        tatizo:
            super().unregister(fileobj)
            ashiria
        rudisha key

    eleza unregister(self, fileobj):
        key = super().unregister(fileobj)
        jaribu:
            self._selector.unregister(key.fd)
        tatizo OSError:
            # This can happen ikiwa the FD was closed since it
            # was registered.
            pita
        rudisha key

    eleza modify(self, fileobj, events, data=Tupu):
        jaribu:
            key = self._fd_to_key[self._fileobj_lookup(fileobj)]
        tatizo KeyError:
            ashiria KeyError(f"{fileobj!r} ni sio registered") kutoka Tupu

        changed = Uongo
        ikiwa events != key.events:
            selector_events = 0
            ikiwa events & EVENT_READ:
                selector_events |= self._EVENT_READ
            ikiwa events & EVENT_WRITE:
                selector_events |= self._EVENT_WRITE
            jaribu:
                self._selector.modify(key.fd, selector_events)
            tatizo:
                super().unregister(fileobj)
                ashiria
            changed = Kweli
        ikiwa data != key.data:
            changed = Kweli

        ikiwa changed:
            key = key._replace(events=events, data=data)
            self._fd_to_key[key.fd] = key
        rudisha key

    eleza select(self, timeout=Tupu):
        # This ni shared between poll() na epoll().
        # epoll() has a different signature na handling of timeout parameter.
        ikiwa timeout ni Tupu:
            timeout = Tupu
        lasivyo timeout <= 0:
            timeout = 0
        isipokua:
            # poll() has a resolution of 1 millisecond, round away kutoka
            # zero to wait *at least* timeout seconds.
            timeout = math.ceil(timeout * 1e3)
        ready = []
        jaribu:
            fd_event_list = self._selector.poll(timeout)
        tatizo InterruptedError:
            rudisha ready
        kila fd, event kwenye fd_event_list:
            events = 0
            ikiwa event & ~self._EVENT_READ:
                events |= EVENT_WRITE
            ikiwa event & ~self._EVENT_WRITE:
                events |= EVENT_READ

            key = self._key_from_fd(fd)
            ikiwa key:
                ready.append((key, events & key.events))
        rudisha ready


ikiwa hasattr(select, 'poll'):

    kundi PollSelector(_PollLikeSelector):
        """Poll-based selector."""
        _selector_cls = select.poll
        _EVENT_READ = select.POLLIN
        _EVENT_WRITE = select.POLLOUT


ikiwa hasattr(select, 'epoll'):

    kundi EpollSelector(_PollLikeSelector):
        """Epoll-based selector."""
        _selector_cls = select.epoll
        _EVENT_READ = select.EPOLLIN
        _EVENT_WRITE = select.EPOLLOUT

        eleza fileno(self):
            rudisha self._selector.fileno()

        eleza select(self, timeout=Tupu):
            ikiwa timeout ni Tupu:
                timeout = -1
            lasivyo timeout <= 0:
                timeout = 0
            isipokua:
                # epoll_wait() has a resolution of 1 millisecond, round away
                # kutoka zero to wait *at least* timeout seconds.
                timeout = math.ceil(timeout * 1e3) * 1e-3

            # epoll_wait() expects `maxevents` to be greater than zero;
            # we want to make sure that `select()` can be called when no
            # FD ni registered.
            max_ev = max(len(self._fd_to_key), 1)

            ready = []
            jaribu:
                fd_event_list = self._selector.poll(timeout, max_ev)
            tatizo InterruptedError:
                rudisha ready
            kila fd, event kwenye fd_event_list:
                events = 0
                ikiwa event & ~select.EPOLLIN:
                    events |= EVENT_WRITE
                ikiwa event & ~select.EPOLLOUT:
                    events |= EVENT_READ

                key = self._key_from_fd(fd)
                ikiwa key:
                    ready.append((key, events & key.events))
            rudisha ready

        eleza close(self):
            self._selector.close()
            super().close()


ikiwa hasattr(select, 'devpoll'):

    kundi DevpollSelector(_PollLikeSelector):
        """Solaris /dev/poll selector."""
        _selector_cls = select.devpoll
        _EVENT_READ = select.POLLIN
        _EVENT_WRITE = select.POLLOUT

        eleza fileno(self):
            rudisha self._selector.fileno()

        eleza close(self):
            self._selector.close()
            super().close()


ikiwa hasattr(select, 'kqueue'):

    kundi KqueueSelector(_BaseSelectorImpl):
        """Kqueue-based selector."""

        eleza __init__(self):
            super().__init__()
            self._selector = select.kqueue()

        eleza fileno(self):
            rudisha self._selector.fileno()

        eleza register(self, fileobj, events, data=Tupu):
            key = super().register(fileobj, events, data)
            jaribu:
                ikiwa events & EVENT_READ:
                    kev = select.kevent(key.fd, select.KQ_FILTER_READ,
                                        select.KQ_EV_ADD)
                    self._selector.control([kev], 0, 0)
                ikiwa events & EVENT_WRITE:
                    kev = select.kevent(key.fd, select.KQ_FILTER_WRITE,
                                        select.KQ_EV_ADD)
                    self._selector.control([kev], 0, 0)
            tatizo:
                super().unregister(fileobj)
                ashiria
            rudisha key

        eleza unregister(self, fileobj):
            key = super().unregister(fileobj)
            ikiwa key.events & EVENT_READ:
                kev = select.kevent(key.fd, select.KQ_FILTER_READ,
                                    select.KQ_EV_DELETE)
                jaribu:
                    self._selector.control([kev], 0, 0)
                tatizo OSError:
                    # This can happen ikiwa the FD was closed since it
                    # was registered.
                    pita
            ikiwa key.events & EVENT_WRITE:
                kev = select.kevent(key.fd, select.KQ_FILTER_WRITE,
                                    select.KQ_EV_DELETE)
                jaribu:
                    self._selector.control([kev], 0, 0)
                tatizo OSError:
                    # See comment above.
                    pita
            rudisha key

        eleza select(self, timeout=Tupu):
            timeout = Tupu ikiwa timeout ni Tupu isipokua max(timeout, 0)
            max_ev = len(self._fd_to_key)
            ready = []
            jaribu:
                kev_list = self._selector.control(Tupu, max_ev, timeout)
            tatizo InterruptedError:
                rudisha ready
            kila kev kwenye kev_list:
                fd = kev.ident
                flag = kev.filter
                events = 0
                ikiwa flag == select.KQ_FILTER_READ:
                    events |= EVENT_READ
                ikiwa flag == select.KQ_FILTER_WRITE:
                    events |= EVENT_WRITE

                key = self._key_from_fd(fd)
                ikiwa key:
                    ready.append((key, events & key.events))
            rudisha ready

        eleza close(self):
            self._selector.close()
            super().close()


# Choose the best implementation, roughly:
#    epoll|kqueue|devpoll > poll > select.
# select() also can't accept a FD > FD_SETSIZE (usually around 1024)
ikiwa 'KqueueSelector' kwenye globals():
    DefaultSelector = KqueueSelector
lasivyo 'EpollSelector' kwenye globals():
    DefaultSelector = EpollSelector
lasivyo 'DevpollSelector' kwenye globals():
    DefaultSelector = DevpollSelector
lasivyo 'PollSelector' kwenye globals():
    DefaultSelector = PollSelector
isipokua:
    DefaultSelector = SelectSelector
