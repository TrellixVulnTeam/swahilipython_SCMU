"""Selectors module.

This module allows high-level and efficient I/O multiplexing, built upon the
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
    fileobj -- file object or file descriptor

    Returns:
    corresponding file descriptor

    Raises:
    ValueError ikiwa the object is invalid
    """
    ikiwa isinstance(fileobj, int):
        fd = fileobj
    else:
        try:
            fd = int(fileobj.fileno())
        except (AttributeError, TypeError, ValueError):
            raise ValueError("Invalid file object: "
                             "{!r}".format(fileobj)) kutoka None
    ikiwa fd < 0:
        raise ValueError("Invalid file descriptor: {}".format(fd))
    rudisha fd


SelectorKey = namedtuple('SelectorKey', ['fileobj', 'fd', 'events', 'data'])

SelectorKey.__doc__ = """SelectorKey(fileobj, fd, events, data)

    Object used to associate a file object to its backing
    file descriptor, selected event mask, and attached data.
"""
ikiwa sys.version_info >= (3, 5):
    SelectorKey.fileobj.__doc__ = 'File object registered.'
    SelectorKey.fd.__doc__ = 'Underlying file descriptor.'
    SelectorKey.events.__doc__ = 'Events that must be waited for on this file object.'
    SelectorKey.data.__doc__ = ('''Optional opaque data associated to this file object.
    For example, this could be used to store a per-client session ID.''')

kundi _SelectorMapping(Mapping):
    """Mapping of file objects to selector keys."""

    eleza __init__(self, selector):
        self._selector = selector

    eleza __len__(self):
        rudisha len(self._selector._fd_to_key)

    eleza __getitem__(self, fileobj):
        try:
            fd = self._selector._fileobj_lookup(fileobj)
            rudisha self._selector._fd_to_key[fd]
        except KeyError:
            raise KeyError("{!r} is not registered".format(fileobj)) kutoka None

    eleza __iter__(self):
        rudisha iter(self._selector._fd_to_key)


kundi BaseSelector(metaclass=ABCMeta):
    """Selector abstract base class.

    A selector supports registering file objects to be monitored for specific
    I/O events.

    A file object is a file descriptor or any object with a `fileno()` method.
    An arbitrary object can be attached to the file object, which can be used
    for example to store context information, a callback, etc.

    A selector can use various implementations (select(), poll(), epoll()...)
    depending on the platform. The default `Selector` kundi uses the most
    efficient implementation on the current platform.
    """

    @abstractmethod
    eleza register(self, fileobj, events, data=None):
        """Register a file object.

        Parameters:
        fileobj -- file object or file descriptor
        events  -- events to monitor (bitwise mask of EVENT_READ|EVENT_WRITE)
        data    -- attached data

        Returns:
        SelectorKey instance

        Raises:
        ValueError ikiwa events is invalid
        KeyError ikiwa fileobj is already registered
        OSError ikiwa fileobj is closed or otherwise is unacceptable to
                the underlying system call (ikiwa a system call is made)

        Note:
        OSError may or may not be raised
        """
        raise NotImplementedError

    @abstractmethod
    eleza unregister(self, fileobj):
        """Unregister a file object.

        Parameters:
        fileobj -- file object or file descriptor

        Returns:
        SelectorKey instance

        Raises:
        KeyError ikiwa fileobj is not registered

        Note:
        If fileobj is registered but has since been closed this does
        *not* raise OSError (even ikiwa the wrapped syscall does)
        """
        raise NotImplementedError

    eleza modify(self, fileobj, events, data=None):
        """Change a registered file object monitored events or attached data.

        Parameters:
        fileobj -- file object or file descriptor
        events  -- events to monitor (bitwise mask of EVENT_READ|EVENT_WRITE)
        data    -- attached data

        Returns:
        SelectorKey instance

        Raises:
        Anything that unregister() or register() raises
        """
        self.unregister(fileobj)
        rudisha self.register(fileobj, events, data)

    @abstractmethod
    eleza select(self, timeout=None):
        """Perform the actual selection, until some monitored file objects are
        ready or a timeout expires.

        Parameters:
        timeout -- ikiwa timeout > 0, this specifies the maximum wait time, in
                   seconds
                   ikiwa timeout <= 0, the select() call won't block, and will
                   report the currently ready file objects
                   ikiwa timeout is None, select() will block until a monitored
                   file object becomes ready

        Returns:
        list of (key, events) for ready file objects
        `events` is a bitwise mask of EVENT_READ|EVENT_WRITE
        """
        raise NotImplementedError

    eleza close(self):
        """Close the selector.

        This must be called to make sure that any underlying resource is freed.
        """
        pass

    eleza get_key(self, fileobj):
        """Return the key associated to a registered file object.

        Returns:
        SelectorKey for this file object
        """
        mapping = self.get_map()
        ikiwa mapping is None:
            raise RuntimeError('Selector is closed')
        try:
            rudisha mapping[fileobj]
        except KeyError:
            raise KeyError("{!r} is not registered".format(fileobj)) kutoka None

    @abstractmethod
    eleza get_map(self):
        """Return a mapping of file objects to selector keys."""
        raise NotImplementedError

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()


kundi _BaseSelectorImpl(BaseSelector):
    """Base selector implementation."""

    eleza __init__(self):
        # this maps file descriptors to keys
        self._fd_to_key = {}
        # read-only mapping returned by get_map()
        self._map = _SelectorMapping(self)

    eleza _fileobj_lookup(self, fileobj):
        """Return a file descriptor kutoka a file object.

        This wraps _fileobj_to_fd() to do an exhaustive search in case
        the object is invalid but we still have it in our map.  This
        is used by unregister() so we can unregister an object that
        was previously registered even ikiwa it is closed.  It is also
        used by _SelectorMapping.
        """
        try:
            rudisha _fileobj_to_fd(fileobj)
        except ValueError:
            # Do an exhaustive search.
            for key in self._fd_to_key.values():
                ikiwa key.fileobj is fileobj:
                    rudisha key.fd
            # Raise ValueError after all.
            raise

    eleza register(self, fileobj, events, data=None):
        ikiwa (not events) or (events & ~(EVENT_READ | EVENT_WRITE)):
            raise ValueError("Invalid events: {!r}".format(events))

        key = SelectorKey(fileobj, self._fileobj_lookup(fileobj), events, data)

        ikiwa key.fd in self._fd_to_key:
            raise KeyError("{!r} (FD {}) is already registered"
                           .format(fileobj, key.fd))

        self._fd_to_key[key.fd] = key
        rudisha key

    eleza unregister(self, fileobj):
        try:
            key = self._fd_to_key.pop(self._fileobj_lookup(fileobj))
        except KeyError:
            raise KeyError("{!r} is not registered".format(fileobj)) kutoka None
        rudisha key

    eleza modify(self, fileobj, events, data=None):
        try:
            key = self._fd_to_key[self._fileobj_lookup(fileobj)]
        except KeyError:
            raise KeyError("{!r} is not registered".format(fileobj)) kutoka None
        ikiwa events != key.events:
            self.unregister(fileobj)
            key = self.register(fileobj, events, data)
        elikiwa data != key.data:
            # Use a shortcut to update the data.
            key = key._replace(data=data)
            self._fd_to_key[key.fd] = key
        rudisha key

    eleza close(self):
        self._fd_to_key.clear()
        self._map = None

    eleza get_map(self):
        rudisha self._map

    eleza _key_kutoka_fd(self, fd):
        """Return the key associated to a given file descriptor.

        Parameters:
        fd -- file descriptor

        Returns:
        corresponding key, or None ikiwa not found
        """
        try:
            rudisha self._fd_to_key[fd]
        except KeyError:
            rudisha None


kundi SelectSelector(_BaseSelectorImpl):
    """Select-based selector."""

    eleza __init__(self):
        super().__init__()
        self._readers = set()
        self._writers = set()

    eleza register(self, fileobj, events, data=None):
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
        eleza _select(self, r, w, _, timeout=None):
            r, w, x = select.select(r, w, w, timeout)
            rudisha r, w + x, []
    else:
        _select = select.select

    eleza select(self, timeout=None):
        timeout = None ikiwa timeout is None else max(timeout, 0)
        ready = []
        try:
            r, w, _ = self._select(self._readers, self._writers, [], timeout)
        except InterruptedError:
            rudisha ready
        r = set(r)
        w = set(w)
        for fd in r | w:
            events = 0
            ikiwa fd in r:
                events |= EVENT_READ
            ikiwa fd in w:
                events |= EVENT_WRITE

            key = self._key_kutoka_fd(fd)
            ikiwa key:
                ready.append((key, events & key.events))
        rudisha ready


kundi _PollLikeSelector(_BaseSelectorImpl):
    """Base kundi shared between poll, epoll and devpoll selectors."""
    _selector_cls = None
    _EVENT_READ = None
    _EVENT_WRITE = None

    eleza __init__(self):
        super().__init__()
        self._selector = self._selector_cls()

    eleza register(self, fileobj, events, data=None):
        key = super().register(fileobj, events, data)
        poller_events = 0
        ikiwa events & EVENT_READ:
            poller_events |= self._EVENT_READ
        ikiwa events & EVENT_WRITE:
            poller_events |= self._EVENT_WRITE
        try:
            self._selector.register(key.fd, poller_events)
        except:
            super().unregister(fileobj)
            raise
        rudisha key

    eleza unregister(self, fileobj):
        key = super().unregister(fileobj)
        try:
            self._selector.unregister(key.fd)
        except OSError:
            # This can happen ikiwa the FD was closed since it
            # was registered.
            pass
        rudisha key

    eleza modify(self, fileobj, events, data=None):
        try:
            key = self._fd_to_key[self._fileobj_lookup(fileobj)]
        except KeyError:
            raise KeyError(f"{fileobj!r} is not registered") kutoka None

        changed = False
        ikiwa events != key.events:
            selector_events = 0
            ikiwa events & EVENT_READ:
                selector_events |= self._EVENT_READ
            ikiwa events & EVENT_WRITE:
                selector_events |= self._EVENT_WRITE
            try:
                self._selector.modify(key.fd, selector_events)
            except:
                super().unregister(fileobj)
                raise
            changed = True
        ikiwa data != key.data:
            changed = True

        ikiwa changed:
            key = key._replace(events=events, data=data)
            self._fd_to_key[key.fd] = key
        rudisha key

    eleza select(self, timeout=None):
        # This is shared between poll() and epoll().
        # epoll() has a different signature and handling of timeout parameter.
        ikiwa timeout is None:
            timeout = None
        elikiwa timeout <= 0:
            timeout = 0
        else:
            # poll() has a resolution of 1 millisecond, round away kutoka
            # zero to wait *at least* timeout seconds.
            timeout = math.ceil(timeout * 1e3)
        ready = []
        try:
            fd_event_list = self._selector.poll(timeout)
        except InterruptedError:
            rudisha ready
        for fd, event in fd_event_list:
            events = 0
            ikiwa event & ~self._EVENT_READ:
                events |= EVENT_WRITE
            ikiwa event & ~self._EVENT_WRITE:
                events |= EVENT_READ

            key = self._key_kutoka_fd(fd)
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

        eleza select(self, timeout=None):
            ikiwa timeout is None:
                timeout = -1
            elikiwa timeout <= 0:
                timeout = 0
            else:
                # epoll_wait() has a resolution of 1 millisecond, round away
                # kutoka zero to wait *at least* timeout seconds.
                timeout = math.ceil(timeout * 1e3) * 1e-3

            # epoll_wait() expects `maxevents` to be greater than zero;
            # we want to make sure that `select()` can be called when no
            # FD is registered.
            max_ev = max(len(self._fd_to_key), 1)

            ready = []
            try:
                fd_event_list = self._selector.poll(timeout, max_ev)
            except InterruptedError:
                rudisha ready
            for fd, event in fd_event_list:
                events = 0
                ikiwa event & ~select.EPOLLIN:
                    events |= EVENT_WRITE
                ikiwa event & ~select.EPOLLOUT:
                    events |= EVENT_READ

                key = self._key_kutoka_fd(fd)
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

        eleza register(self, fileobj, events, data=None):
            key = super().register(fileobj, events, data)
            try:
                ikiwa events & EVENT_READ:
                    kev = select.kevent(key.fd, select.KQ_FILTER_READ,
                                        select.KQ_EV_ADD)
                    self._selector.control([kev], 0, 0)
                ikiwa events & EVENT_WRITE:
                    kev = select.kevent(key.fd, select.KQ_FILTER_WRITE,
                                        select.KQ_EV_ADD)
                    self._selector.control([kev], 0, 0)
            except:
                super().unregister(fileobj)
                raise
            rudisha key

        eleza unregister(self, fileobj):
            key = super().unregister(fileobj)
            ikiwa key.events & EVENT_READ:
                kev = select.kevent(key.fd, select.KQ_FILTER_READ,
                                    select.KQ_EV_DELETE)
                try:
                    self._selector.control([kev], 0, 0)
                except OSError:
                    # This can happen ikiwa the FD was closed since it
                    # was registered.
                    pass
            ikiwa key.events & EVENT_WRITE:
                kev = select.kevent(key.fd, select.KQ_FILTER_WRITE,
                                    select.KQ_EV_DELETE)
                try:
                    self._selector.control([kev], 0, 0)
                except OSError:
                    # See comment above.
                    pass
            rudisha key

        eleza select(self, timeout=None):
            timeout = None ikiwa timeout is None else max(timeout, 0)
            max_ev = len(self._fd_to_key)
            ready = []
            try:
                kev_list = self._selector.control(None, max_ev, timeout)
            except InterruptedError:
                rudisha ready
            for kev in kev_list:
                fd = kev.ident
                flag = kev.filter
                events = 0
                ikiwa flag == select.KQ_FILTER_READ:
                    events |= EVENT_READ
                ikiwa flag == select.KQ_FILTER_WRITE:
                    events |= EVENT_WRITE

                key = self._key_kutoka_fd(fd)
                ikiwa key:
                    ready.append((key, events & key.events))
            rudisha ready

        eleza close(self):
            self._selector.close()
            super().close()


# Choose the best implementation, roughly:
#    epoll|kqueue|devpoll > poll > select.
# select() also can't accept a FD > FD_SETSIZE (usually around 1024)
ikiwa 'KqueueSelector' in globals():
    DefaultSelector = KqueueSelector
elikiwa 'EpollSelector' in globals():
    DefaultSelector = EpollSelector
elikiwa 'DevpollSelector' in globals():
    DefaultSelector = DevpollSelector
elikiwa 'PollSelector' in globals():
    DefaultSelector = PollSelector
else:
    DefaultSelector = SelectSelector
