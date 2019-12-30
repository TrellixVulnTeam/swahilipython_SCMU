#
# Support kila the API of the multiprocessing package using threads
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

    eleza __init__(self, group=Tupu, target=Tupu, name=Tupu, args=(), kwargs={}):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._pid = Tupu
        self._children = weakref.WeakKeyDictionary()
        self._start_called = Uongo
        self._parent = current_process()

    eleza start(self):
        ikiwa self._parent ni sio current_process():
             ashiria RuntimeError(
                "Parent ni {0!r} but current_process ni {1!r}".format(
                    self._parent, current_process()))
        self._start_called = Kweli
        ikiwa hasattr(self._parent, '_children'):
            self._parent._children[self] = Tupu
        threading.Thread.start(self)

    @property
    eleza exitcode(self):
        ikiwa self._start_called na sio self.is_alive():
            rudisha 0
        isipokua:
            rudisha Tupu

#
#
#

Process = DummyProcess
current_process = threading.current_thread
current_process()._children = weakref.WeakKeyDictionary()

eleza active_children():
    children = current_process()._children
    kila p kwenye list(children):
        ikiwa sio p.is_alive():
            children.pop(p, Tupu)
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
        kila name, value kwenye items:
            ikiwa sio name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        rudisha '%s(%s)' % (self.__class__.__name__, ', '.join(temp))

dict = dict
list = list

eleza Array(typecode, sequence, lock=Kweli):
    rudisha array.array(typecode, sequence)

kundi Value(object):
    eleza __init__(self, typecode, value, lock=Kweli):
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

eleza Pool(processes=Tupu, initializer=Tupu, initargs=()):
    kutoka ..pool agiza ThreadPool
    rudisha ThreadPool(processes, initializer, initargs)

JoinableQueue = Queue
