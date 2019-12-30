
# The cycle GC collector can be executed when any GC-tracked object is
# allocated, e.g. during a call to PyList_New(), PyDict_New(), ...
# Moreover, it can invoke arbitrary Python code via a weakref callback.
# This means that there are many places kwenye the source where an arbitrary
# mutation could unexpectedly occur.

# The example below shows list_slice() sio expecting the call to
# PyList_New to mutate the input list.  (Of course there are many
# more examples like this one.)


agiza weakref

kundi A(object):
    pass

eleza callback(x):
    toa lst[:]


keepalive = []

kila i kwenye range(100):
    lst = [str(i)]
    a = A()
    a.cycle = a
    keepalive.append(weakref.ref(a, callback))
    toa a
    wakati lst:
        keepalive.append(lst[:])
