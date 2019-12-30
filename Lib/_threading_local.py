"""Thread-local objects.

(Note that this module provides a Python version of the threading.local
 class.  Depending on the version of Python you're using, there may be a
 faster one available.  You should always agiza the `local` kundi from
 `threading`.)

Thread-local objects support the management of thread-local data.
If you have data that you want to be local to a thread, simply create
a thread-local object na use its attributes:

  >>> mydata = local()
  >>> mydata.number = 42
  >>> mydata.number
  42

You can also access the local-object's dictionary:

  >>> mydata.__dict__
  {'number': 42}
  >>> mydata.__dict__.setdefault('widgets', [])
  []
  >>> mydata.widgets
  []

What's important about thread-local objects ni that their data are
local to a thread. If we access the data kwenye a different thread:

  >>> log = []
  >>> eleza f():
  ...     items = sorted(mydata.__dict__.items())
  ...     log.append(items)
  ...     mydata.number = 11
  ...     log.append(mydata.number)

  >>> agiza threading
  >>> thread = threading.Thread(target=f)
  >>> thread.start()
  >>> thread.join()
  >>> log
  [[], 11]

we get different data.  Furthermore, changes made kwenye the other thread
don't affect data seen kwenye this thread:

  >>> mydata.number
  42

Of course, values you get kutoka a local object, including a __dict__
attribute, are kila whatever thread was current at the time the
attribute was read.  For that reason, you generally don't want to save
these values across threads, kama they apply only to the thread they
came from.

You can create custom local objects by subclassing the local class:

  >>> kundi MyLocal(local):
  ...     number = 2
  ...     eleza __init__(self, /, **kw):
  ...         self.__dict__.update(kw)
  ...     eleza squared(self):
  ...         rudisha self.number ** 2

This can be useful to support default values, methods na
initialization.  Note that ikiwa you define an __init__ method, it will be
called each time the local object ni used kwenye a separate thread.  This
is necessary to initialize each thread's dictionary.

Now ikiwa we create a local object:

  >>> mydata = MyLocal(color='red')

Now we have a default number:

  >>> mydata.number
  2

an initial color:

  >>> mydata.color
  'red'
  >>> toa mydata.color

And a method that operates on the data:

  >>> mydata.squared()
  4

As before, we can access the data kwenye a separate thread:

  >>> log = []
  >>> thread = threading.Thread(target=f)
  >>> thread.start()
  >>> thread.join()
  >>> log
  [[('color', 'red')], 11]

without affecting this thread's data:

  >>> mydata.number
  2
  >>> mydata.color
  Traceback (most recent call last):
  ...
  AttributeError: 'MyLocal' object has no attribute 'color'

Note that subclasses can define slots, but they are sio thread
local. They are shared across threads:

  >>> kundi MyLocal(local):
  ...     __slots__ = 'number'

  >>> mydata = MyLocal()
  >>> mydata.number = 42
  >>> mydata.color = 'red'

So, the separate thread:

  >>> thread = threading.Thread(target=f)
  >>> thread.start()
  >>> thread.join()

affects what we see:

  >>> mydata.number
  11

>>> toa mydata
"""

kutoka weakref agiza ref
kutoka contextlib agiza contextmanager

__all__ = ["local"]

# We need to use objects kutoka the threading module, but the threading
# module may also want to use our `local` class, ikiwa support kila locals
# isn't compiled kwenye to the `thread` module.  This creates potential problems
# ukijumuisha circular imports.  For that reason, we don't agiza `threading`
# until the bottom of this file (a hack sufficient to worm around the
# potential problems).  Note that all platforms on CPython do have support
# kila locals kwenye the `thread` module, na there ni no circular agiza problem
# then, so problems introduced by fiddling the order of imports here won't
# manifest.

kundi _localimpl:
    """A kundi managing thread-local dicts"""
    __slots__ = 'key', 'dicts', 'localargs', 'locallock', '__weakref__'

    eleza __init__(self):
        # The key used kwenye the Thread objects' attribute dicts.
        # We keep it a string kila speed but make it unlikely to clash with
        # a "real" attribute.
        self.key = '_threading_local._localimpl.' + str(id(self))
        # { id(Thread) -> (ref(Thread), thread-local dict) }
        self.dicts = {}

    eleza get_dict(self):
        """Return the dict kila the current thread. Raises KeyError ikiwa none
        defined."""
        thread = current_thread()
        rudisha self.dicts[id(thread)][1]

    eleza create_dict(self):
        """Create a new dict kila the current thread, na rudisha it."""
        localdict = {}
        key = self.key
        thread = current_thread()
        idt = id(thread)
        eleza local_deleted(_, key=key):
            # When the localimpl ni deleted, remove the thread attribute.
            thread = wrthread()
            ikiwa thread ni sio Tupu:
                toa thread.__dict__[key]
        eleza thread_deleted(_, idt=idt):
            # When the thread ni deleted, remove the local dict.
            # Note that this ni suboptimal ikiwa the thread object gets
            # caught kwenye a reference loop. We would like to be called
            # kama soon kama the OS-level thread ends instead.
            local = wrlocal()
            ikiwa local ni sio Tupu:
                dct = local.dicts.pop(idt)
        wrlocal = ref(self, local_deleted)
        wrthread = ref(thread, thread_deleted)
        thread.__dict__[key] = wrlocal
        self.dicts[idt] = wrthread, localdict
        rudisha localdict


@contextmanager
eleza _patch(self):
    impl = object.__getattribute__(self, '_local__impl')
    jaribu:
        dct = impl.get_dict()
    tatizo KeyError:
        dct = impl.create_dict()
        args, kw = impl.localargs
        self.__init__(*args, **kw)
    ukijumuisha impl.locallock:
        object.__setattr__(self, '__dict__', dct)
        tuma


kundi local:
    __slots__ = '_local__impl', '__dict__'

    eleza __new__(cls, /, *args, **kw):
        ikiwa (args ama kw) na (cls.__init__ ni object.__init__):
            ashiria TypeError("Initialization arguments are sio supported")
        self = object.__new__(cls)
        impl = _localimpl()
        impl.localargs = (args, kw)
        impl.locallock = RLock()
        object.__setattr__(self, '_local__impl', impl)
        # We need to create the thread dict kwenye anticipation of
        # __init__ being called, to make sure we don't call it
        # again ourselves.
        impl.create_dict()
        rudisha self

    eleza __getattribute__(self, name):
        ukijumuisha _patch(self):
            rudisha object.__getattribute__(self, name)

    eleza __setattr__(self, name, value):
        ikiwa name == '__dict__':
            ashiria AttributeError(
                "%r object attribute '__dict__' ni read-only"
                % self.__class__.__name__)
        ukijumuisha _patch(self):
            rudisha object.__setattr__(self, name, value)

    eleza __delattr__(self, name):
        ikiwa name == '__dict__':
            ashiria AttributeError(
                "%r object attribute '__dict__' ni read-only"
                % self.__class__.__name__)
        ukijumuisha _patch(self):
            rudisha object.__delattr__(self, name)


kutoka threading agiza current_thread, RLock
