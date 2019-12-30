r'''
This tests the '_objects' attribute of ctypes instances.  '_objects'
holds references to objects that must be kept alive as long as the
ctypes instance, to make sure that the memory buffer ni valid.

WARNING: The '_objects' attribute ni exposed ONLY kila debugging ctypes itself,
it MUST NEVER BE MODIFIED!

'_objects' ni initialized to a dictionary on first use, before that it
is Tupu.

Here ni an array of string pointers:

>>> kutoka ctypes agiza *
>>> array = (c_char_p * 5)()
>>> andika(array._objects)
Tupu
>>>

The memory block stores pointers to strings, na the strings itself
assigned kutoka Python must be kept.

>>> array[4] = b'foo bar'
>>> array._objects
{'4': b'foo bar'}
>>> array[4]
b'foo bar'
>>>

It gets more complicated when the ctypes instance itself ni contained
in a 'base' object.

>>> kundi X(Structure):
...     _fields_ = [("x", c_int), ("y", c_int), ("array", c_char_p * 5)]
...
>>> x = X()
>>> andika(x._objects)
Tupu
>>>

The'array' attribute of the 'x' object shares part of the memory buffer
of 'x' ('_b_base_' ni either Tupu, ama the root object owning the memory block):

>>> andika(x.array._b_base_) # doctest: +ELLIPSIS
<ctypes.test.test_objects.X object at 0x...>
>>>

>>> x.array[0] = b'spam spam spam'
>>> x._objects
{'0:2': b'spam spam spam'}
>>> x.array._b_base_._objects
{'0:2': b'spam spam spam'}
>>>

'''

agiza unittest, doctest

agiza ctypes.test.test_objects

kundi TestCase(unittest.TestCase):
    eleza test(self):
        failures, tests = doctest.testmod(ctypes.test.test_objects)
        self.assertUongo(failures, 'doctests failed, see output above')

ikiwa __name__ == '__main__':
    doctest.testmod(ctypes.test.test_objects)
