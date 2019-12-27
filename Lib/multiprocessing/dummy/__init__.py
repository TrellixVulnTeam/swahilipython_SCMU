#
# Support for the API of the multiprocessing package using threads
#
# multiprocessing/dummy/__init__.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [
    'Process', 'current_process', 'active_children', 'freeze_support',
    'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition',
    'Event', 'Barrier', 'Queue', 'Manager', 'Pipe', 'Pool', 'JoinableQueue'
    ]

#
# Imports
#

agiza threading
agiza sys
agiza weakref
agiza array

kutoka .connection agiza Pipe
kutoka threading agiza Lock, RLock, Semaphore, BoundedSemaphore
kutoka threading agiza Event, Condition, Barrier
kutoka queue agiza Queue

#
#
#

kundi DummyProcess(threading.Thread):

    eleza __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._pid = None
        self._children = weakref.WeakKeyDictionary()
        self._start_called = False
        self._parent = current_process()

    eleza start(self):
        ikiwa self._parent is not current_process():
            raise RuntimeError(
                "Parent is {0!r} but current_process is {1!r}".format(
                    self._parent, current_process()))
        self._start_called = True
        ikiwa hasattr(self._parent, '_children'):
            self._parent._children[self] = None
        threading.Thread.start(self)

    @property
    eleza exitcode(self):
        ikiwa self._start_called and not self.is_alive():
            rudisha 0
        else:
            rudisha None

#
#
#

Process = DummyProcess
current_process = threading.current_thread
current_process()._children = weakref.WeakKeyDictionary()

eleza active_children():
    children = current_process()._children
    for p in list(children):
        ikiwa not p.is_alive():
            children.pop(p, None)
    rudisha list(children)

eleza freeze_support():
    pass

#
#
#

kundi Namespace(object):
    eleza __init__(self, /, **kwds):
        self.__dict__.update(kwds)
    eleza __repr__(self):
        items = list(self.__dict__.items())
        temp = []
        for name, value in items:
            ikiwa not name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        rudisha '%s(%s)' % (self.__class__.__name__, ', '.join(temp))

dict = dict
list = list

eleza Array(typecode, sequence, lock=True):
    rudisha array.array(typecode, sequence)

kundi Value(object):
    eleza __init__(self, typecode, value, lock=True):
        self._typecode = typecode
        self._value = value

    @property
    eleza value(self):
        rudisha self._value

    @value.setter
    eleza value(self, value):
        self._value = value

    eleza __repr__(self):
        rudisha '<%s(%r, %r)>'%(type(self).__name__,self._typecode,self._value)

eleza Manager():
    rudisha sys.modules[__name__]

eleza shutdown():
    pass

eleza Pool(processes=None, initializer=None, initargs=()):
    kutoka ..pool agiza ThreadPool
    rudisha ThreadPool(processes, initializer, initargs)

JoinableQueue = Queue
