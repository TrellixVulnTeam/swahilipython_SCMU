#!/usr/bin/python
'''
From gdb 7 onwards, gdb's build can be configured --with-python, allowing gdb
to be extended ukijumuisha Python code e.g. kila library-specific data visualizations,
such kama kila the C++ STL types.  Documentation on this API can be seen at:
http://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html


This python module deals ukijumuisha the case when the process being debugged (the
"inferior process" kwenye gdb parlance) ni itself python, ama more specifically,
linked against libpython.  In this situation, almost every item of data ni a
(PyObject*), na having the debugger merely print their addresses ni sio very
enlightening.

This module embeds knowledge about the implementation details of libpython so
that we can emit useful visualizations e.g. a string, a list, a dict, a frame
giving file/line information na the state of local variables

In particular, given a gdb.Value corresponding to a PyObject* kwenye the inferior
process, we can generate a "proxy value" within the gdb process.  For example,
given a PyObject* kwenye the inferior process that ni kwenye fact a PyListObject*
holding three PyObject* that turn out to be PyBytesObject* instances, we can
generate a proxy value within the gdb process that ni a list of bytes
instances:
  [b"foo", b"bar", b"baz"]

Doing so can be expensive kila complicated graphs of objects, na could take
some time, so we also have a "write_repr" method that writes a representation
of the data to a file-like object.  This allows us to stop the traversal by
having the file-like object ashiria an exception ikiwa it gets too much data.

With both "proxyval" na "write_repr" we keep track of the set of all addresses
visited so far kwenye the traversal, to avoid infinite recursion due to cycles in
the graph of object references.

We try to defer gdb.lookup_type() invocations kila python types until kama late as
possible: kila a dynamically linked python binary, when the process starts in
the debugger, the libpython.so hasn't been dynamically loaded yet, so none of
the type names are known to the debugger

The module also extends gdb ukijumuisha some python-specific commands.
'''

# NOTE: some gdbs are linked ukijumuisha Python 3, so this file should be dual-syntax
# compatible (2.6+ na 3.0+).  See #19308.

kutoka __future__ agiza print_function
agiza gdb
agiza os
agiza locale
agiza sys

ikiwa sys.version_info[0] >= 3:
    unichr = chr
    xrange = range
    long = int

# Look up the gdb.Type kila some standard types:
# Those need to be refreshed kama types (pointer sizes) may change when
# gdb loads different executables

eleza _type_char_ptr():
    rudisha gdb.lookup_type('char').pointer()  # char*


eleza _type_unsigned_char_ptr():
    rudisha gdb.lookup_type('unsigned char').pointer()  # unsigned char*


eleza _type_unsigned_short_ptr():
    rudisha gdb.lookup_type('unsigned short').pointer()


eleza _type_unsigned_int_ptr():
    rudisha gdb.lookup_type('unsigned int').pointer()


eleza _sizeof_void_p():
    rudisha gdb.lookup_type('void').pointer().sizeof


# value computed later, see PyUnicodeObjectPtr.proxy()
_is_pep393 = Tupu

Py_TPFLAGS_HEAPTYPE = (1 << 9)
Py_TPFLAGS_LONG_SUBCLASS     = (1 << 24)
Py_TPFLAGS_LIST_SUBCLASS     = (1 << 25)
Py_TPFLAGS_TUPLE_SUBCLASS    = (1 << 26)
Py_TPFLAGS_BYTES_SUBCLASS    = (1 << 27)
Py_TPFLAGS_UNICODE_SUBCLASS  = (1 << 28)
Py_TPFLAGS_DICT_SUBCLASS     = (1 << 29)
Py_TPFLAGS_BASE_EXC_SUBCLASS = (1 << 30)
Py_TPFLAGS_TYPE_SUBCLASS     = (1 << 31)


MAX_OUTPUT_LEN=1024

hexdigits = "0123456789abcdef"

ENCODING = locale.getpreferredencoding()

EVALFRAME = '_PyEval_EvalFrameDefault'

kundi NullPyObjectPtr(RuntimeError):
    pita


eleza safety_limit(val):
    # Given an integer value kutoka the process being debugged, limit it to some
    # safety threshold so that arbitrary komaage within said process doesn't
    # koma the gdb process too much (e.g. sizes of iterations, sizes of lists)
    rudisha min(val, 1000)


eleza safe_range(val):
    # As per range, but don't trust the value too much: cap it to a safety
    # threshold kwenye case the data was corrupted
    rudisha xrange(safety_limit(int(val)))

ikiwa sys.version_info[0] >= 3:
    eleza write_unicode(file, text):
        file.write(text)
isipokua:
    eleza write_unicode(file, text):
        # Write a byte ama unicode string to file. Unicode strings are encoded to
        # ENCODING encoding ukijumuisha 'backslashreplace' error handler to avoid
        # UnicodeEncodeError.
        ikiwa isinstance(text, unicode):
            text = text.encode(ENCODING, 'backslashreplace')
        file.write(text)

jaribu:
    os_fsencode = os.fsencode
tatizo AttributeError:
    eleza os_fsencode(filename):
        ikiwa sio isinstance(filename, unicode):
            rudisha filename
        encoding = sys.getfilesystemencoding()
        ikiwa encoding == 'mbcs':
            # mbcs doesn't support surrogateescape
            rudisha filename.encode(encoding)
        encoded = []
        kila char kwenye filename:
            # surrogateescape error handler
            ikiwa 0xDC80 <= ord(char) <= 0xDCFF:
                byte = chr(ord(char) - 0xDC00)
            isipokua:
                byte = char.encode(encoding)
            encoded.append(byte)
        rudisha ''.join(encoded)

kundi StringTruncated(RuntimeError):
    pita

kundi TruncatedStringIO(object):
    '''Similar to io.StringIO, but can truncate the output by raising a
    StringTruncated exception'''
    eleza __init__(self, maxlen=Tupu):
        self._val = ''
        self.maxlen = maxlen

    eleza write(self, data):
        ikiwa self.maxlen:
            ikiwa len(data) + len(self._val) > self.maxlen:
                # Truncation:
                self._val += data[0:self.maxlen - len(self._val)]
                ashiria StringTruncated()

        self._val += data

    eleza getvalue(self):
        rudisha self._val

kundi PyObjectPtr(object):
    """
    Class wrapping a gdb.Value that's either a (PyObject*) within the
    inferior process, ama some subkundi pointer e.g. (PyBytesObject*)

    There will be a subkundi kila every refined PyObject type that we care
    about.

    Note that at every stage the underlying pointer could be NULL, point
    to corrupt data, etc; this ni the debugger, after all.
    """
    _typename = 'PyObject'

    eleza __init__(self, gdbval, cast_to=Tupu):
        ikiwa cast_to:
            self._gdbval = gdbval.cast(cast_to)
        isipokua:
            self._gdbval = gdbval

    eleza field(self, name):
        '''
        Get the gdb.Value kila the given field within the PyObject, coping with
        some python 2 versus python 3 differences.

        Various libpython types are defined using the "PyObject_HEAD" na
        "PyObject_VAR_HEAD" macros.

        In Python 2, this these are defined so that "ob_type" na (kila a var
        object) "ob_size" are fields of the type kwenye question.

        In Python 3, this ni defined kama an embedded PyVarObject type thus:
           PyVarObject ob_base;
        so that the "ob_size" field ni located insize the "ob_base" field, na
        the "ob_type" ni most easily accessed by casting back to a (PyObject*).
        '''
        ikiwa self.is_null():
            ashiria NullPyObjectPtr(self)

        ikiwa name == 'ob_type':
            pyo_ptr = self._gdbval.cast(PyObjectPtr.get_gdb_type())
            rudisha pyo_ptr.dereference()[name]

        ikiwa name == 'ob_size':
            pyo_ptr = self._gdbval.cast(PyVarObjectPtr.get_gdb_type())
            rudisha pyo_ptr.dereference()[name]

        # General case: look it up inside the object:
        rudisha self._gdbval.dereference()[name]

    eleza pyop_field(self, name):
        '''
        Get a PyObjectPtr kila the given PyObject* field within this PyObject,
        coping ukijumuisha some python 2 versus python 3 differences.
        '''
        rudisha PyObjectPtr.from_pyobject_ptr(self.field(name))

    eleza write_field_repr(self, name, out, visited):
        '''
        Extract the PyObject* field named "name", na write its representation
        to file-like object "out"
        '''
        field_obj = self.pyop_field(name)
        field_obj.write_repr(out, visited)

    eleza get_truncated_repr(self, maxlen):
        '''
        Get a repr-like string kila the data, but truncate it at "maxlen" bytes
        (ending the object graph traversal kama soon kama you do)
        '''
        out = TruncatedStringIO(maxlen)
        jaribu:
            self.write_repr(out, set())
        tatizo StringTruncated:
            # Truncation occurred:
            rudisha out.getvalue() + '...(truncated)'

        # No truncation occurred:
        rudisha out.getvalue()

    eleza type(self):
        rudisha PyTypeObjectPtr(self.field('ob_type'))

    eleza is_null(self):
        rudisha 0 == long(self._gdbval)

    eleza is_optimized_out(self):
        '''
        Is the value of the underlying PyObject* visible to the debugger?

        This can vary ukijumuisha the precise version of the compiler used to build
        Python, na the precise version of gdb.

        See e.g. https://bugzilla.redhat.com/show_bug.cgi?id=556975 with
        PyEval_EvalFrameEx's "f"
        '''
        rudisha self._gdbval.is_optimized_out

    eleza safe_tp_name(self):
        jaribu:
            ob_type = self.type()
            tp_name = ob_type.field('tp_name')
            rudisha tp_name.string()
        # NullPyObjectPtr: NULL tp_name?
        # RuntimeError: Can't even read the object at all?
        # UnicodeDecodeError: Failed to decode tp_name bytestring
        tatizo (NullPyObjectPtr, RuntimeError, UnicodeDecodeError):
            rudisha 'unknown'

    eleza proxyval(self, visited):
        '''
        Scrape a value kutoka the inferior process, na try to represent it
        within the gdb process, whilst (hopefully) avoiding crashes when
        the remote data ni corrupt.

        Derived classes will override this.

        For example, a PyIntObject* ukijumuisha ob_ival 42 kwenye the inferior process
        should result kwenye an int(42) kwenye this process.

        visited: a set of all gdb.Value pyobject pointers already visited
        whilst generating this value (to guard against infinite recursion when
        visiting object graphs ukijumuisha loops).  Analogous to Py_ReprEnter na
        Py_ReprLeave
        '''

        kundi FakeRepr(object):
            """
            Class representing a non-descript PyObject* value kwenye the inferior
            process kila when we don't have a custom scraper, intended to have
            a sane repr().
            """

            eleza __init__(self, tp_name, address):
                self.tp_name = tp_name
                self.address = address

            eleza __repr__(self):
                # For the NULL pointer, we have no way of knowing a type, so
                # special-case it kama per
                # http://bugs.python.org/issue8032#msg100882
                ikiwa self.address == 0:
                    rudisha '0x0'
                rudisha '<%s at remote 0x%x>' % (self.tp_name, self.address)

        rudisha FakeRepr(self.safe_tp_name(),
                        long(self._gdbval))

    eleza write_repr(self, out, visited):
        '''
        Write a string representation of the value scraped kutoka the inferior
        process to "out", a file-like object.
        '''
        # Default implementation: generate a proxy value na write its repr
        # However, this could involve a lot of work kila complicated objects,
        # so kila derived classes we specialize this
        rudisha out.write(repr(self.proxyval(visited)))

    @classmethod
    eleza subclass_from_type(cls, t):
        '''
        Given a PyTypeObjectPtr instance wrapping a gdb.Value that's a
        (PyTypeObject*), determine the corresponding subkundi of PyObjectPtr
        to use

        Ideally, we would look up the symbols kila the global types, but that
        isn't working yet:
          (gdb) python print gdb.lookup_symbol('PyList_Type')[0].value
          Traceback (most recent call last):
            File "<string>", line 1, kwenye <module>
          NotImplementedError: Symbol type sio yet supported kwenye Python scripts.
          Error wakati executing Python code.

        For now, we use tp_flags, after doing some string comparisons on the
        tp_name kila some special-cases that don't seem to be visible through
        flags
        '''
        jaribu:
            tp_name = t.field('tp_name').string()
            tp_flags = int(t.field('tp_flags'))
        # RuntimeError: NULL pointers
        # UnicodeDecodeError: string() fails to decode the bytestring
        tatizo (RuntimeError, UnicodeDecodeError):
            # Handle any kind of error e.g. NULL ptrs by simply using the base
            # class
            rudisha cls

        #andika('tp_flags = 0x%08x' % tp_flags)
        #andika('tp_name = %r' % tp_name)

        name_map = {'bool': PyBoolObjectPtr,
                    'classobj': PyClassObjectPtr,
                    'TupuType': PyTupuStructPtr,
                    'frame': PyFrameObjectPtr,
                    'set' : PySetObjectPtr,
                    'frozenset' : PySetObjectPtr,
                    'builtin_function_or_method' : PyCFunctionObjectPtr,
                    'method-wrapper': wrapperobject,
                    }
        ikiwa tp_name kwenye name_map:
            rudisha name_map[tp_name]

        ikiwa tp_flags & Py_TPFLAGS_HEAPTYPE:
            rudisha HeapTypeObjectPtr

        ikiwa tp_flags & Py_TPFLAGS_LONG_SUBCLASS:
            rudisha PyLongObjectPtr
        ikiwa tp_flags & Py_TPFLAGS_LIST_SUBCLASS:
            rudisha PyListObjectPtr
        ikiwa tp_flags & Py_TPFLAGS_TUPLE_SUBCLASS:
            rudisha PyTupleObjectPtr
        ikiwa tp_flags & Py_TPFLAGS_BYTES_SUBCLASS:
            rudisha PyBytesObjectPtr
        ikiwa tp_flags & Py_TPFLAGS_UNICODE_SUBCLASS:
            rudisha PyUnicodeObjectPtr
        ikiwa tp_flags & Py_TPFLAGS_DICT_SUBCLASS:
            rudisha PyDictObjectPtr
        ikiwa tp_flags & Py_TPFLAGS_BASE_EXC_SUBCLASS:
            rudisha PyBaseExceptionObjectPtr
        #ikiwa tp_flags & Py_TPFLAGS_TYPE_SUBCLASS:
        #    rudisha PyTypeObjectPtr

        # Use the base class:
        rudisha cls

    @classmethod
    eleza from_pyobject_ptr(cls, gdbval):
        '''
        Try to locate the appropriate derived kundi dynamically, na cast
        the pointer accordingly.
        '''
        jaribu:
            p = PyObjectPtr(gdbval)
            cls = cls.subclass_from_type(p.type())
            rudisha cls(gdbval, cast_to=cls.get_gdb_type())
        tatizo RuntimeError:
            # Handle any kind of error e.g. NULL ptrs by simply using the base
            # class
            pita
        rudisha cls(gdbval)

    @classmethod
    eleza get_gdb_type(cls):
        rudisha gdb.lookup_type(cls._typename).pointer()

    eleza as_address(self):
        rudisha long(self._gdbval)

kundi PyVarObjectPtr(PyObjectPtr):
    _typename = 'PyVarObject'

kundi ProxyAlreadyVisited(object):
    '''
    Placeholder proxy to use when protecting against infinite recursion due to
    loops kwenye the object graph.

    Analogous to the values emitted by the users of Py_ReprEnter na Py_ReprLeave
    '''
    eleza __init__(self, rep):
        self._rep = rep

    eleza __repr__(self):
        rudisha self._rep


eleza _write_instance_repr(out, visited, name, pyop_attrdict, address):
    '''Shared code kila use by all classes:
    write a representation to file-like object "out"'''
    out.write('<')
    out.write(name)

    # Write dictionary of instance attributes:
    ikiwa isinstance(pyop_attrdict, PyDictObjectPtr):
        out.write('(')
        first = Kweli
        kila pyop_arg, pyop_val kwenye pyop_attrdict.iteritems():
            ikiwa sio first:
                out.write(', ')
            first = Uongo
            out.write(pyop_arg.proxyval(visited))
            out.write('=')
            pyop_val.write_repr(out, visited)
        out.write(')')
    out.write(' at remote 0x%x>' % address)


kundi InstanceProxy(object):

    eleza __init__(self, cl_name, attrdict, address):
        self.cl_name = cl_name
        self.attrdict = attrdict
        self.address = address

    eleza __repr__(self):
        ikiwa isinstance(self.attrdict, dict):
            kwargs = ', '.join(["%s=%r" % (arg, val)
                                kila arg, val kwenye self.attrdict.iteritems()])
            rudisha '<%s(%s) at remote 0x%x>' % (self.cl_name,
                                                kwargs, self.address)
        isipokua:
            rudisha '<%s at remote 0x%x>' % (self.cl_name,
                                            self.address)

eleza _PyObject_VAR_SIZE(typeobj, nitems):
    ikiwa _PyObject_VAR_SIZE._type_size_t ni Tupu:
        _PyObject_VAR_SIZE._type_size_t = gdb.lookup_type('size_t')

    rudisha ( ( typeobj.field('tp_basicsize') +
               nitems * typeobj.field('tp_itemsize') +
               (_sizeof_void_p() - 1)
             ) & ~(_sizeof_void_p() - 1)
           ).cast(_PyObject_VAR_SIZE._type_size_t)
_PyObject_VAR_SIZE._type_size_t = Tupu

kundi HeapTypeObjectPtr(PyObjectPtr):
    _typename = 'PyObject'

    eleza get_attr_dict(self):
        '''
        Get the PyDictObject ptr representing the attribute dictionary
        (or Tupu ikiwa there's a problem)
        '''
        jaribu:
            typeobj = self.type()
            dictoffset = int_from_int(typeobj.field('tp_dictoffset'))
            ikiwa dictoffset != 0:
                ikiwa dictoffset < 0:
                    type_PyVarObject_ptr = gdb.lookup_type('PyVarObject').pointer()
                    tsize = int_from_int(self._gdbval.cast(type_PyVarObject_ptr)['ob_size'])
                    ikiwa tsize < 0:
                        tsize = -tsize
                    size = _PyObject_VAR_SIZE(typeobj, tsize)
                    dictoffset += size
                    assert dictoffset > 0
                    assert dictoffset % _sizeof_void_p() == 0

                dictptr = self._gdbval.cast(_type_char_ptr()) + dictoffset
                PyObjectPtrPtr = PyObjectPtr.get_gdb_type().pointer()
                dictptr = dictptr.cast(PyObjectPtrPtr)
                rudisha PyObjectPtr.from_pyobject_ptr(dictptr.dereference())
        tatizo RuntimeError:
            # Corrupt data somewhere; fail safe
            pita

        # Not found, ama some kind of error:
        rudisha Tupu

    eleza proxyval(self, visited):
        '''
        Support kila classes.

        Currently we just locate the dictionary using a transliteration to
        python of _PyObject_GetDictPtr, ignoring descriptors
        '''
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            rudisha ProxyAlreadyVisited('<...>')
        visited.add(self.as_address())

        pyop_attr_dict = self.get_attr_dict()
        ikiwa pyop_attr_dict:
            attr_dict = pyop_attr_dict.proxyval(visited)
        isipokua:
            attr_dict = {}
        tp_name = self.safe_tp_name()

        # Class:
        rudisha InstanceProxy(tp_name, attr_dict, long(self._gdbval))

    eleza write_repr(self, out, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            out.write('<...>')
            rudisha
        visited.add(self.as_address())

        pyop_attrdict = self.get_attr_dict()
        _write_instance_repr(out, visited,
                             self.safe_tp_name(), pyop_attrdict, self.as_address())

kundi ProxyException(Exception):
    eleza __init__(self, tp_name, args):
        self.tp_name = tp_name
        self.args = args

    eleza __repr__(self):
        rudisha '%s%r' % (self.tp_name, self.args)

kundi PyBaseExceptionObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyBaseExceptionObject* i.e. an exception
    within the process being debugged.
    """
    _typename = 'PyBaseExceptionObject'

    eleza proxyval(self, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            rudisha ProxyAlreadyVisited('(...)')
        visited.add(self.as_address())
        arg_proxy = self.pyop_field('args').proxyval(visited)
        rudisha ProxyException(self.safe_tp_name(),
                              arg_proxy)

    eleza write_repr(self, out, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            out.write('(...)')
            rudisha
        visited.add(self.as_address())

        out.write(self.safe_tp_name())
        self.write_field_repr('args', out, visited)

kundi PyClassObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyClassObject* i.e. a <classobj>
    instance within the process being debugged.
    """
    _typename = 'PyClassObject'


kundi BuiltInFunctionProxy(object):
    eleza __init__(self, ml_name):
        self.ml_name = ml_name

    eleza __repr__(self):
        rudisha "<built-in function %s>" % self.ml_name

kundi BuiltInMethodProxy(object):
    eleza __init__(self, ml_name, pyop_m_self):
        self.ml_name = ml_name
        self.pyop_m_self = pyop_m_self

    eleza __repr__(self):
        rudisha ('<built-in method %s of %s object at remote 0x%x>'
                % (self.ml_name,
                   self.pyop_m_self.safe_tp_name(),
                   self.pyop_m_self.as_address())
                )

kundi PyCFunctionObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyCFunctionObject*
    (see Include/methodobject.h na Objects/methodobject.c)
    """
    _typename = 'PyCFunctionObject'

    eleza proxyval(self, visited):
        m_ml = self.field('m_ml') # m_ml ni a (PyMethodDef*)
        jaribu:
            ml_name = m_ml['ml_name'].string()
        tatizo UnicodeDecodeError:
            ml_name = '<ml_name:UnicodeDecodeError>'

        pyop_m_self = self.pyop_field('m_self')
        ikiwa pyop_m_self.is_null():
            rudisha BuiltInFunctionProxy(ml_name)
        isipokua:
            rudisha BuiltInMethodProxy(ml_name, pyop_m_self)


kundi PyCodeObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyCodeObject* i.e. a <code> instance
    within the process being debugged.
    """
    _typename = 'PyCodeObject'

    eleza addr2line(self, addrq):
        '''
        Get the line number kila a given bytecode offset

        Analogous to PyCode_Addr2Line; translated kutoka pseudocode in
        Objects/lnotab_notes.txt
        '''
        co_lnotab = self.pyop_field('co_lnotab').proxyval(set())

        # Initialize lineno to co_firstlineno kama per PyCode_Addr2Line
        # sio 0, kama lnotab_notes.txt has it:
        lineno = int_from_int(self.field('co_firstlineno'))

        addr = 0
        kila addr_incr, line_incr kwenye zip(co_lnotab[::2], co_lnotab[1::2]):
            addr += ord(addr_incr)
            ikiwa addr > addrq:
                rudisha lineno
            lineno += ord(line_incr)
        rudisha lineno


kundi PyDictObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyDictObject* i.e. a dict instance
    within the process being debugged.
    """
    _typename = 'PyDictObject'

    eleza iteritems(self):
        '''
        Yields a sequence of (PyObjectPtr key, PyObjectPtr value) pairs,
        analogous to dict.iteritems()
        '''
        keys = self.field('ma_keys')
        values = self.field('ma_values')
        entries, nentries = self._get_entries(keys)
        kila i kwenye safe_range(nentries):
            ep = entries[i]
            ikiwa long(values):
                pyop_value = PyObjectPtr.from_pyobject_ptr(values[i])
            isipokua:
                pyop_value = PyObjectPtr.from_pyobject_ptr(ep['me_value'])
            ikiwa sio pyop_value.is_null():
                pyop_key = PyObjectPtr.from_pyobject_ptr(ep['me_key'])
                tuma (pyop_key, pyop_value)

    eleza proxyval(self, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            rudisha ProxyAlreadyVisited('{...}')
        visited.add(self.as_address())

        result = {}
        kila pyop_key, pyop_value kwenye self.iteritems():
            proxy_key = pyop_key.proxyval(visited)
            proxy_value = pyop_value.proxyval(visited)
            result[proxy_key] = proxy_value
        rudisha result

    eleza write_repr(self, out, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            out.write('{...}')
            rudisha
        visited.add(self.as_address())

        out.write('{')
        first = Kweli
        kila pyop_key, pyop_value kwenye self.iteritems():
            ikiwa sio first:
                out.write(', ')
            first = Uongo
            pyop_key.write_repr(out, visited)
            out.write(': ')
            pyop_value.write_repr(out, visited)
        out.write('}')

    eleza _get_entries(self, keys):
        dk_nentries = int(keys['dk_nentries'])
        dk_size = int(keys['dk_size'])
        jaribu:
            # <= Python 3.5
            rudisha keys['dk_entries'], dk_size
        tatizo RuntimeError:
            # >= Python 3.6
            pita

        ikiwa dk_size <= 0xFF:
            offset = dk_size
        lasivyo dk_size <= 0xFFFF:
            offset = 2 * dk_size
        lasivyo dk_size <= 0xFFFFFFFF:
            offset = 4 * dk_size
        isipokua:
            offset = 8 * dk_size

        ent_addr = keys['dk_indices'].address
        ent_addr = ent_addr.cast(_type_unsigned_char_ptr()) + offset
        ent_ptr_t = gdb.lookup_type('PyDictKeyEntry').pointer()
        ent_addr = ent_addr.cast(ent_ptr_t)

        rudisha ent_addr, dk_nentries


kundi PyListObjectPtr(PyObjectPtr):
    _typename = 'PyListObject'

    eleza __getitem__(self, i):
        # Get the gdb.Value kila the (PyObject*) ukijumuisha the given index:
        field_ob_item = self.field('ob_item')
        rudisha field_ob_item[i]

    eleza proxyval(self, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            rudisha ProxyAlreadyVisited('[...]')
        visited.add(self.as_address())

        result = [PyObjectPtr.from_pyobject_ptr(self[i]).proxyval(visited)
                  kila i kwenye safe_range(int_from_int(self.field('ob_size')))]
        rudisha result

    eleza write_repr(self, out, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            out.write('[...]')
            rudisha
        visited.add(self.as_address())

        out.write('[')
        kila i kwenye safe_range(int_from_int(self.field('ob_size'))):
            ikiwa i > 0:
                out.write(', ')
            element = PyObjectPtr.from_pyobject_ptr(self[i])
            element.write_repr(out, visited)
        out.write(']')

kundi PyLongObjectPtr(PyObjectPtr):
    _typename = 'PyLongObject'

    eleza proxyval(self, visited):
        '''
        Python's Include/longobjrep.h has this declaration:
           struct _longobject {
               PyObject_VAR_HEAD
               digit ob_digit[1];
           };

        ukijumuisha this description:
            The absolute value of a number ni equal to
                 SUM(kila i=0 through abs(ob_size)-1) ob_digit[i] * 2**(SHIFT*i)
            Negative numbers are represented ukijumuisha ob_size < 0;
            zero ni represented by ob_size == 0.

        where SHIFT can be either:
            #define PyLong_SHIFT        30
            #define PyLong_SHIFT        15
        '''
        ob_size = long(self.field('ob_size'))
        ikiwa ob_size == 0:
            rudisha 0

        ob_digit = self.field('ob_digit')

        ikiwa gdb.lookup_type('digit').sizeof == 2:
            SHIFT = 15
        isipokua:
            SHIFT = 30

        digits = [long(ob_digit[i]) * 2**(SHIFT*i)
                  kila i kwenye safe_range(abs(ob_size))]
        result = sum(digits)
        ikiwa ob_size < 0:
            result = -result
        rudisha result

    eleza write_repr(self, out, visited):
        # Write this out kama a Python 3 int literal, i.e. without the "L" suffix
        proxy = self.proxyval(visited)
        out.write("%s" % proxy)


kundi PyBoolObjectPtr(PyLongObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyBoolObject* i.e. one of the two
    <bool> instances (Py_Kweli/Py_Uongo) within the process being debugged.
    """
    eleza proxyval(self, visited):
        ikiwa PyLongObjectPtr.proxyval(self, visited):
            rudisha Kweli
        isipokua:
            rudisha Uongo

kundi PyTupuStructPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyObject* pointing to the
    singleton (we hope) _Py_TupuStruct ukijumuisha ob_type PyTupu_Type
    """
    _typename = 'PyObject'

    eleza proxyval(self, visited):
        rudisha Tupu


kundi PyFrameObjectPtr(PyObjectPtr):
    _typename = 'PyFrameObject'

    eleza __init__(self, gdbval, cast_to=Tupu):
        PyObjectPtr.__init__(self, gdbval, cast_to)

        ikiwa sio self.is_optimized_out():
            self.co = PyCodeObjectPtr.from_pyobject_ptr(self.field('f_code'))
            self.co_name = self.co.pyop_field('co_name')
            self.co_filename = self.co.pyop_field('co_filename')

            self.f_lineno = int_from_int(self.field('f_lineno'))
            self.f_lasti = int_from_int(self.field('f_lasti'))
            self.co_nlocals = int_from_int(self.co.field('co_nlocals'))
            self.co_varnames = PyTupleObjectPtr.from_pyobject_ptr(self.co.field('co_varnames'))

    eleza iter_locals(self):
        '''
        Yield a sequence of (name,value) pairs of PyObjectPtr instances, for
        the local variables of this frame
        '''
        ikiwa self.is_optimized_out():
            rudisha

        f_localsplus = self.field('f_localsplus')
        kila i kwenye safe_range(self.co_nlocals):
            pyop_value = PyObjectPtr.from_pyobject_ptr(f_localsplus[i])
            ikiwa sio pyop_value.is_null():
                pyop_name = PyObjectPtr.from_pyobject_ptr(self.co_varnames[i])
                tuma (pyop_name, pyop_value)

    eleza iter_globals(self):
        '''
        Yield a sequence of (name,value) pairs of PyObjectPtr instances, for
        the global variables of this frame
        '''
        ikiwa self.is_optimized_out():
            rudisha ()

        pyop_globals = self.pyop_field('f_globals')
        rudisha pyop_globals.iteritems()

    eleza iter_builtins(self):
        '''
        Yield a sequence of (name,value) pairs of PyObjectPtr instances, for
        the builtin variables
        '''
        ikiwa self.is_optimized_out():
            rudisha ()

        pyop_builtins = self.pyop_field('f_builtins')
        rudisha pyop_builtins.iteritems()

    eleza get_var_by_name(self, name):
        '''
        Look kila the named local variable, returning a (PyObjectPtr, scope) pair
        where scope ni a string 'local', 'global', 'builtin'

        If sio found, rudisha (Tupu, Tupu)
        '''
        kila pyop_name, pyop_value kwenye self.iter_locals():
            ikiwa name == pyop_name.proxyval(set()):
                rudisha pyop_value, 'local'
        kila pyop_name, pyop_value kwenye self.iter_globals():
            ikiwa name == pyop_name.proxyval(set()):
                rudisha pyop_value, 'global'
        kila pyop_name, pyop_value kwenye self.iter_builtins():
            ikiwa name == pyop_name.proxyval(set()):
                rudisha pyop_value, 'builtin'
        rudisha Tupu, Tupu

    eleza filename(self):
        '''Get the path of the current Python source file, kama a string'''
        ikiwa self.is_optimized_out():
            rudisha '(frame information optimized out)'
        rudisha self.co_filename.proxyval(set())

    eleza current_line_num(self):
        '''Get current line number kama an integer (1-based)

        Translated kutoka PyFrame_GetLineNumber na PyCode_Addr2Line

        See Objects/lnotab_notes.txt
        '''
        ikiwa self.is_optimized_out():
            rudisha Tupu
        f_trace = self.field('f_trace')
        ikiwa long(f_trace) != 0:
            # we have a non-NULL f_trace:
            rudisha self.f_lineno

        jaribu:
            rudisha self.co.addr2line(self.f_lasti)
        tatizo Exception:
            # bpo-34989: addr2line() ni a complex function, it can fail kwenye many
            # ways. For example, it fails ukijumuisha a TypeError on "FakeRepr" if
            # gdb fails to load debug symbols. Use a catch-all "except
            # Exception" to make the whole function safe. The caller has to
            # handle Tupu anyway kila optimized Python.
            rudisha Tupu

    eleza current_line(self):
        '''Get the text of the current source line kama a string, ukijumuisha a trailing
        newline character'''
        ikiwa self.is_optimized_out():
            rudisha '(frame information optimized out)'

        lineno = self.current_line_num()
        ikiwa lineno ni Tupu:
            rudisha '(failed to get frame line number)'

        filename = self.filename()
        jaribu:
            ukijumuisha open(os_fsencode(filename), 'r') kama fp:
                lines = fp.readlines()
        tatizo IOError:
            rudisha Tupu

        jaribu:
            # Convert kutoka 1-based current_line_num to 0-based list offset
            rudisha lines[lineno - 1]
        tatizo IndexError:
            rudisha Tupu

    eleza write_repr(self, out, visited):
        ikiwa self.is_optimized_out():
            out.write('(frame information optimized out)')
            rudisha
        lineno = self.current_line_num()
        lineno = str(lineno) ikiwa lineno ni sio Tupu isipokua "?"
        out.write('Frame 0x%x, kila file %s, line %s, kwenye %s ('
                  % (self.as_address(),
                     self.co_filename.proxyval(visited),
                     lineno,
                     self.co_name.proxyval(visited)))
        first = Kweli
        kila pyop_name, pyop_value kwenye self.iter_locals():
            ikiwa sio first:
                out.write(', ')
            first = Uongo

            out.write(pyop_name.proxyval(visited))
            out.write('=')
            pyop_value.write_repr(out, visited)

        out.write(')')

    eleza print_traceback(self):
        ikiwa self.is_optimized_out():
            sys.stdout.write('  (frame information optimized out)\n')
            rudisha
        visited = set()
        lineno = self.current_line_num()
        lineno = str(lineno) ikiwa lineno ni sio Tupu isipokua "?"
        sys.stdout.write('  File "%s", line %s, kwenye %s\n'
                  % (self.co_filename.proxyval(visited),
                     lineno,
                     self.co_name.proxyval(visited)))

kundi PySetObjectPtr(PyObjectPtr):
    _typename = 'PySetObject'

    @classmethod
    eleza _dummy_key(self):
        rudisha gdb.lookup_global_symbol('_PySet_Dummy').value()

    eleza __iter__(self):
        dummy_ptr = self._dummy_key()
        table = self.field('table')
        kila i kwenye safe_range(self.field('mask') + 1):
            setentry = table[i]
            key = setentry['key']
            ikiwa key != 0 na key != dummy_ptr:
                tuma PyObjectPtr.from_pyobject_ptr(key)

    eleza proxyval(self, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            rudisha ProxyAlreadyVisited('%s(...)' % self.safe_tp_name())
        visited.add(self.as_address())

        members = (key.proxyval(visited) kila key kwenye self)
        ikiwa self.safe_tp_name() == 'frozenset':
            rudisha frozenset(members)
        isipokua:
            rudisha set(members)

    eleza write_repr(self, out, visited):
        # Emulate Python 3's set_repr
        tp_name = self.safe_tp_name()

        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            out.write('(...)')
            rudisha
        visited.add(self.as_address())

        # Python 3's set_repr special-cases the empty set:
        ikiwa sio self.field('used'):
            out.write(tp_name)
            out.write('()')
            rudisha

        # Python 3 uses {} kila set literals:
        ikiwa tp_name != 'set':
            out.write(tp_name)
            out.write('(')

        out.write('{')
        first = Kweli
        kila key kwenye self:
            ikiwa sio first:
                out.write(', ')
            first = Uongo
            key.write_repr(out, visited)
        out.write('}')

        ikiwa tp_name != 'set':
            out.write(')')


kundi PyBytesObjectPtr(PyObjectPtr):
    _typename = 'PyBytesObject'

    eleza __str__(self):
        field_ob_size = self.field('ob_size')
        field_ob_sval = self.field('ob_sval')
        char_ptr = field_ob_sval.address.cast(_type_unsigned_char_ptr())
        rudisha ''.join([chr(char_ptr[i]) kila i kwenye safe_range(field_ob_size)])

    eleza proxyval(self, visited):
        rudisha str(self)

    eleza write_repr(self, out, visited):
        # Write this out kama a Python 3 bytes literal, i.e. ukijumuisha a "b" prefix

        # Get a PyStringObject* within the Python 2 gdb process:
        proxy = self.proxyval(visited)

        # Transliteration of Python 3's Objects/bytesobject.c:PyBytes_Repr
        # to Python 2 code:
        quote = "'"
        ikiwa "'" kwenye proxy na sio '"' kwenye proxy:
            quote = '"'
        out.write('b')
        out.write(quote)
        kila byte kwenye proxy:
            ikiwa byte == quote ama byte == '\\':
                out.write('\\')
                out.write(byte)
            lasivyo byte == '\t':
                out.write('\\t')
            lasivyo byte == '\n':
                out.write('\\n')
            lasivyo byte == '\r':
                out.write('\\r')
            lasivyo byte < ' ' ama ord(byte) >= 0x7f:
                out.write('\\x')
                out.write(hexdigits[(ord(byte) & 0xf0) >> 4])
                out.write(hexdigits[ord(byte) & 0xf])
            isipokua:
                out.write(byte)
        out.write(quote)

kundi PyTupleObjectPtr(PyObjectPtr):
    _typename = 'PyTupleObject'

    eleza __getitem__(self, i):
        # Get the gdb.Value kila the (PyObject*) ukijumuisha the given index:
        field_ob_item = self.field('ob_item')
        rudisha field_ob_item[i]

    eleza proxyval(self, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            rudisha ProxyAlreadyVisited('(...)')
        visited.add(self.as_address())

        result = tuple(PyObjectPtr.from_pyobject_ptr(self[i]).proxyval(visited)
                       kila i kwenye safe_range(int_from_int(self.field('ob_size'))))
        rudisha result

    eleza write_repr(self, out, visited):
        # Guard against infinite loops:
        ikiwa self.as_address() kwenye visited:
            out.write('(...)')
            rudisha
        visited.add(self.as_address())

        out.write('(')
        kila i kwenye safe_range(int_from_int(self.field('ob_size'))):
            ikiwa i > 0:
                out.write(', ')
            element = PyObjectPtr.from_pyobject_ptr(self[i])
            element.write_repr(out, visited)
        ikiwa self.field('ob_size') == 1:
            out.write(',)')
        isipokua:
            out.write(')')

kundi PyTypeObjectPtr(PyObjectPtr):
    _typename = 'PyTypeObject'


eleza _unichr_is_printable(char):
    # Logic adapted kutoka Python 3's Tools/unicode/makeunicodedata.py
    ikiwa char == u" ":
        rudisha Kweli
    agiza unicodedata
    rudisha unicodedata.category(char) haiko kwenye ("C", "Z")

ikiwa sys.maxunicode >= 0x10000:
    _unichr = unichr
isipokua:
    # Needed kila proper surrogate support ikiwa sizeof(Py_UNICODE) ni 2 kwenye gdb
    eleza _unichr(x):
        ikiwa x < 0x10000:
            rudisha unichr(x)
        x -= 0x10000
        ch1 = 0xD800 | (x >> 10)
        ch2 = 0xDC00 | (x & 0x3FF)
        rudisha unichr(ch1) + unichr(ch2)


kundi PyUnicodeObjectPtr(PyObjectPtr):
    _typename = 'PyUnicodeObject'

    eleza char_width(self):
        _type_Py_UNICODE = gdb.lookup_type('Py_UNICODE')
        rudisha _type_Py_UNICODE.sizeof

    eleza proxyval(self, visited):
        global _is_pep393
        ikiwa _is_pep393 ni Tupu:
            fields = gdb.lookup_type('PyUnicodeObject').fields()
            _is_pep393 = 'data' kwenye [f.name kila f kwenye fields]
        ikiwa _is_pep393:
            # Python 3.3 na newer
            may_have_surrogates = Uongo
            compact = self.field('_base')
            ascii = compact['_base']
            state = ascii['state']
            is_compact_ascii = (int(state['ascii']) na int(state['compact']))
            ikiwa sio int(state['ready']):
                # string ni sio ready
                field_length = long(compact['wstr_length'])
                may_have_surrogates = Kweli
                field_str = ascii['wstr']
            isipokua:
                field_length = long(ascii['length'])
                ikiwa is_compact_ascii:
                    field_str = ascii.address + 1
                lasivyo int(state['compact']):
                    field_str = compact.address + 1
                isipokua:
                    field_str = self.field('data')['any']
                repr_kind = int(state['kind'])
                ikiwa repr_kind == 1:
                    field_str = field_str.cast(_type_unsigned_char_ptr())
                lasivyo repr_kind == 2:
                    field_str = field_str.cast(_type_unsigned_short_ptr())
                lasivyo repr_kind == 4:
                    field_str = field_str.cast(_type_unsigned_int_ptr())
        isipokua:
            # Python 3.2 na earlier
            field_length = long(self.field('length'))
            field_str = self.field('str')
            may_have_surrogates = self.char_width() == 2

        # Gather a list of ints kutoka the Py_UNICODE array; these are either
        # UCS-1, UCS-2 ama UCS-4 code points:
        ikiwa sio may_have_surrogates:
            Py_UNICODEs = [int(field_str[i]) kila i kwenye safe_range(field_length)]
        isipokua:
            # A more elaborate routine ikiwa sizeof(Py_UNICODE) ni 2 kwenye the
            # inferior process: we must join surrogate pairs.
            Py_UNICODEs = []
            i = 0
            limit = safety_limit(field_length)
            wakati i < limit:
                ucs = int(field_str[i])
                i += 1
                ikiwa ucs < 0xD800 ama ucs >= 0xDC00 ama i == field_length:
                    Py_UNICODEs.append(ucs)
                    endelea
                # This could be a surrogate pair.
                ucs2 = int(field_str[i])
                ikiwa ucs2 < 0xDC00 ama ucs2 > 0xDFFF:
                    endelea
                code = (ucs & 0x03FF) << 10
                code |= ucs2 & 0x03FF
                code += 0x00010000
                Py_UNICODEs.append(code)
                i += 1

        # Convert the int code points to unicode characters, na generate a
        # local unicode instance.
        # This splits surrogate pairs ikiwa sizeof(Py_UNICODE) ni 2 here (in gdb).
        result = u''.join([
            (_unichr(ucs) ikiwa ucs <= 0x10ffff isipokua '\ufffd')
            kila ucs kwenye Py_UNICODEs])
        rudisha result

    eleza write_repr(self, out, visited):
        # Write this out kama a Python 3 str literal, i.e. without a "u" prefix

        # Get a PyUnicodeObject* within the Python 2 gdb process:
        proxy = self.proxyval(visited)

        # Transliteration of Python 3's Object/unicodeobject.c:unicode_repr
        # to Python 2:
        ikiwa "'" kwenye proxy na '"' haiko kwenye proxy:
            quote = '"'
        isipokua:
            quote = "'"
        out.write(quote)

        i = 0
        wakati i < len(proxy):
            ch = proxy[i]
            i += 1

            # Escape quotes na backslashes
            ikiwa ch == quote ama ch == '\\':
                out.write('\\')
                out.write(ch)

            #  Map special whitespace to '\t', \n', '\r'
            lasivyo ch == '\t':
                out.write('\\t')
            lasivyo ch == '\n':
                out.write('\\n')
            lasivyo ch == '\r':
                out.write('\\r')

            # Map non-printable US ASCII to '\xhh' */
            lasivyo ch < ' ' ama ch == 0x7F:
                out.write('\\x')
                out.write(hexdigits[(ord(ch) >> 4) & 0x000F])
                out.write(hexdigits[ord(ch) & 0x000F])

            # Copy ASCII characters as-is
            lasivyo ord(ch) < 0x7F:
                out.write(ch)

            # Non-ASCII characters
            isipokua:
                ucs = ch
                ch2 = Tupu
                ikiwa sys.maxunicode < 0x10000:
                    # If sizeof(Py_UNICODE) ni 2 here (in gdb), join
                    # surrogate pairs before calling _unichr_is_printable.
                    ikiwa (i < len(proxy)
                    na 0xD800 <= ord(ch) < 0xDC00 \
                    na 0xDC00 <= ord(proxy[i]) <= 0xDFFF):
                        ch2 = proxy[i]
                        ucs = ch + ch2
                        i += 1

                # Unfortuately, Python 2's unicode type doesn't seem
                # to expose the "isprintable" method
                printable = _unichr_is_printable(ucs)
                ikiwa printable:
                    jaribu:
                        ucs.encode(ENCODING)
                    tatizo UnicodeEncodeError:
                        printable = Uongo

                # Map Unicode whitespace na control characters
                # (categories Z* na C* tatizo ASCII space)
                ikiwa sio printable:
                    ikiwa ch2 ni sio Tupu:
                        # Match Python 3's representation of non-printable
                        # wide characters.
                        code = (ord(ch) & 0x03FF) << 10
                        code |= ord(ch2) & 0x03FF
                        code += 0x00010000
                    isipokua:
                        code = ord(ucs)

                    # Map 8-bit characters to '\\xhh'
                    ikiwa code <= 0xff:
                        out.write('\\x')
                        out.write(hexdigits[(code >> 4) & 0x000F])
                        out.write(hexdigits[code & 0x000F])
                    # Map 21-bit characters to '\U00xxxxxx'
                    lasivyo code >= 0x10000:
                        out.write('\\U')
                        out.write(hexdigits[(code >> 28) & 0x0000000F])
                        out.write(hexdigits[(code >> 24) & 0x0000000F])
                        out.write(hexdigits[(code >> 20) & 0x0000000F])
                        out.write(hexdigits[(code >> 16) & 0x0000000F])
                        out.write(hexdigits[(code >> 12) & 0x0000000F])
                        out.write(hexdigits[(code >> 8) & 0x0000000F])
                        out.write(hexdigits[(code >> 4) & 0x0000000F])
                        out.write(hexdigits[code & 0x0000000F])
                    # Map 16-bit characters to '\uxxxx'
                    isipokua:
                        out.write('\\u')
                        out.write(hexdigits[(code >> 12) & 0x000F])
                        out.write(hexdigits[(code >> 8) & 0x000F])
                        out.write(hexdigits[(code >> 4) & 0x000F])
                        out.write(hexdigits[code & 0x000F])
                isipokua:
                    # Copy characters as-is
                    out.write(ch)
                    ikiwa ch2 ni sio Tupu:
                        out.write(ch2)

        out.write(quote)


kundi wrapperobject(PyObjectPtr):
    _typename = 'wrapperobject'

    eleza safe_name(self):
        jaribu:
            name = self.field('descr')['d_base']['name'].string()
            rudisha repr(name)
        tatizo (NullPyObjectPtr, RuntimeError, UnicodeDecodeError):
            rudisha '<unknown name>'

    eleza safe_tp_name(self):
        jaribu:
            rudisha self.field('self')['ob_type']['tp_name'].string()
        tatizo (NullPyObjectPtr, RuntimeError, UnicodeDecodeError):
            rudisha '<unknown tp_name>'

    eleza safe_self_addresss(self):
        jaribu:
            address = long(self.field('self'))
            rudisha '%#x' % address
        tatizo (NullPyObjectPtr, RuntimeError):
            rudisha '<failed to get self address>'

    eleza proxyval(self, visited):
        name = self.safe_name()
        tp_name = self.safe_tp_name()
        self_address = self.safe_self_addresss()
        rudisha ("<method-wrapper %s of %s object at %s>"
                % (name, tp_name, self_address))

    eleza write_repr(self, out, visited):
        proxy = self.proxyval(visited)
        out.write(proxy)


eleza int_from_int(gdbval):
    rudisha int(gdbval)


eleza stringify(val):
    # TODO: repr() puts everything on one line; pformat can be nicer, but
    # can lead to v.long results; this function isolates the choice
    ikiwa Kweli:
        rudisha repr(val)
    isipokua:
        kutoka pprint agiza pformat
        rudisha pformat(val)


kundi PyObjectPtrPrinter:
    "Prints a (PyObject*)"

    eleza __init__ (self, gdbval):
        self.gdbval = gdbval

    eleza to_string (self):
        pyop = PyObjectPtr.from_pyobject_ptr(self.gdbval)
        ikiwa Kweli:
            rudisha pyop.get_truncated_repr(MAX_OUTPUT_LEN)
        isipokua:
            # Generate full proxy value then stringify it.
            # Doing so could be expensive
            proxyval = pyop.proxyval(set())
            rudisha stringify(proxyval)

eleza pretty_printer_lookup(gdbval):
    type = gdbval.type.unqualified()
    ikiwa type.code != gdb.TYPE_CODE_PTR:
        rudisha Tupu

    type = type.target().unqualified()
    t = str(type)
    ikiwa t kwenye ("PyObject", "PyFrameObject", "PyUnicodeObject", "wrapperobject"):
        rudisha PyObjectPtrPrinter(gdbval)

"""
During development, I've been manually invoking the code kwenye this way:
(gdb) python

agiza sys
sys.path.append('/home/david/coding/python-gdb')
agiza libpython
end

then reloading it after each edit like this:
(gdb) python reload(libpython)

The following code should ensure that the prettyprinter ni registered
ikiwa the code ni autoloaded by gdb when visiting libpython.so, provided
that this python file ni installed to the same path kama the library (or its
.debug file) plus a "-gdb.py" suffix, e.g:
  /usr/lib/libpython2.6.so.1.0-gdb.py
  /usr/lib/debug/usr/lib/libpython2.6.so.1.0.debug-gdb.py
"""
eleza register (obj):
    ikiwa obj ni Tupu:
        obj = gdb

    # Wire up the pretty-printer
    obj.pretty_printers.append(pretty_printer_lookup)

register (gdb.current_objfile ())



# Unfortunately, the exact API exposed by the gdb module varies somewhat
# kutoka build to build
# See http://bugs.python.org/issue8279?#msg102276

kundi Frame(object):
    '''
    Wrapper kila gdb.Frame, adding various methods
    '''
    eleza __init__(self, gdbframe):
        self._gdbframe = gdbframe

    eleza older(self):
        older = self._gdbframe.older()
        ikiwa older:
            rudisha Frame(older)
        isipokua:
            rudisha Tupu

    eleza newer(self):
        newer = self._gdbframe.newer()
        ikiwa newer:
            rudisha Frame(newer)
        isipokua:
            rudisha Tupu

    eleza select(self):
        '''If supported, select this frame na rudisha Kweli; rudisha Uongo ikiwa unsupported

        Not all builds have a gdb.Frame.select method; seems to be present on Fedora 12
        onwards, but absent on Ubuntu buildbot'''
        ikiwa sio hasattr(self._gdbframe, 'select'):
            print ('Unable to select frame: '
                   'this build of gdb does sio expose a gdb.Frame.select method')
            rudisha Uongo
        self._gdbframe.select()
        rudisha Kweli

    eleza get_index(self):
        '''Calculate index of frame, starting at 0 kila the newest frame within
        this thread'''
        index = 0
        # Go down until you reach the newest frame:
        iter_frame = self
        wakati iter_frame.newer():
            index += 1
            iter_frame = iter_frame.newer()
        rudisha index

    # We divide frames into:
    #   - "python frames":
    #       - "bytecode frames" i.e. PyEval_EvalFrameEx
    #       - "other python frames": things that are of interest kutoka a python
    #         POV, but aren't bytecode (e.g. GC, GIL)
    #   - everything isipokua

    eleza is_python_frame(self):
        '''Is this a _PyEval_EvalFrameDefault frame, ama some other important
        frame? (see is_other_python_frame kila what "important" means kwenye this
        context)'''
        ikiwa self.is_evalframe():
            rudisha Kweli
        ikiwa self.is_other_python_frame():
            rudisha Kweli
        rudisha Uongo

    eleza is_evalframe(self):
        '''Is this a _PyEval_EvalFrameDefault frame?'''
        ikiwa self._gdbframe.name() == EVALFRAME:
            '''
            I believe we also need to filter on the inline
            struct frame_id.inline_depth, only regarding frames with
            an inline depth of 0 kama actually being this function

            So we reject those ukijumuisha type gdb.INLINE_FRAME
            '''
            ikiwa self._gdbframe.type() == gdb.NORMAL_FRAME:
                # We have a _PyEval_EvalFrameDefault frame:
                rudisha Kweli

        rudisha Uongo

    eleza is_other_python_frame(self):
        '''Is this frame worth displaying kwenye python backtraces?
        Examples:
          - waiting on the GIL
          - garbage-collecting
          - within a CFunction
         If it is, rudisha a descriptive string
         For other frames, rudisha Uongo
         '''
        ikiwa self.is_waiting_for_gil():
            rudisha 'Waiting kila the GIL'

        ikiwa self.is_gc_collect():
            rudisha 'Garbage-collecting'

        # Detect invocations of PyCFunction instances:
        frame = self._gdbframe
        caller = frame.name()
        ikiwa sio caller:
            rudisha Uongo

        ikiwa (caller.startswith('cfunction_vectorcall_') ama
            caller == 'cfunction_call_varargs'):
            arg_name = 'func'
            # Within that frame:
            #   "func" ni the local containing the PyObject* of the
            # PyCFunctionObject instance
            #   "f" ni the same value, but cast to (PyCFunctionObject*)
            #   "self" ni the (PyObject*) of the 'self'
            jaribu:
                # Use the prettyprinter kila the func:
                func = frame.read_var(arg_name)
                rudisha str(func)
            tatizo ValueError:
                rudisha ('PyCFunction invocation (unable to read %s: '
                        'missing debuginfos?)' % arg_name)
            tatizo RuntimeError:
                rudisha 'PyCFunction invocation (unable to read %s)' % arg_name

        ikiwa caller == 'wrapper_call':
            arg_name = 'wp'
            jaribu:
                func = frame.read_var(arg_name)
                rudisha str(func)
            tatizo ValueError:
                rudisha ('<wrapper_call invocation (unable to read %s: '
                        'missing debuginfos?)>' % arg_name)
            tatizo RuntimeError:
                rudisha '<wrapper_call invocation (unable to read %s)>' % arg_name

        # This frame isn't worth reporting:
        rudisha Uongo

    eleza is_waiting_for_gil(self):
        '''Is this frame waiting on the GIL?'''
        # This assumes the _POSIX_THREADS version of Python/ceval_gil.h:
        name = self._gdbframe.name()
        ikiwa name:
            rudisha 'pthread_cond_timedwait' kwenye name

    eleza is_gc_collect(self):
        '''Is this frame "collect" within the garbage-collector?'''
        rudisha self._gdbframe.name() == 'collect'

    eleza get_pyop(self):
        jaribu:
            f = self._gdbframe.read_var('f')
            frame = PyFrameObjectPtr.from_pyobject_ptr(f)
            ikiwa sio frame.is_optimized_out():
                rudisha frame
            # gdb ni unable to get the "f" argument of PyEval_EvalFrameEx()
            # because it was "optimized out". Try to get "f" kutoka the frame
            # of the caller, PyEval_EvalCodeEx().
            orig_frame = frame
            caller = self._gdbframe.older()
            ikiwa caller:
                f = caller.read_var('f')
                frame = PyFrameObjectPtr.from_pyobject_ptr(f)
                ikiwa sio frame.is_optimized_out():
                    rudisha frame
            rudisha orig_frame
        tatizo ValueError:
            rudisha Tupu

    @classmethod
    eleza get_selected_frame(cls):
        _gdbframe = gdb.selected_frame()
        ikiwa _gdbframe:
            rudisha Frame(_gdbframe)
        rudisha Tupu

    @classmethod
    eleza get_selected_python_frame(cls):
        '''Try to obtain the Frame kila the python-related code kwenye the selected
        frame, ama Tupu'''
        jaribu:
            frame = cls.get_selected_frame()
        tatizo gdb.error:
            # No frame: Python didn't start yet
            rudisha Tupu

        wakati frame:
            ikiwa frame.is_python_frame():
                rudisha frame
            frame = frame.older()

        # Not found:
        rudisha Tupu

    @classmethod
    eleza get_selected_bytecode_frame(cls):
        '''Try to obtain the Frame kila the python bytecode interpreter kwenye the
        selected GDB frame, ama Tupu'''
        frame = cls.get_selected_frame()

        wakati frame:
            ikiwa frame.is_evalframe():
                rudisha frame
            frame = frame.older()

        # Not found:
        rudisha Tupu

    eleza print_summary(self):
        ikiwa self.is_evalframe():
            pyop = self.get_pyop()
            ikiwa pyop:
                line = pyop.get_truncated_repr(MAX_OUTPUT_LEN)
                write_unicode(sys.stdout, '#%i %s\n' % (self.get_index(), line))
                ikiwa sio pyop.is_optimized_out():
                    line = pyop.current_line()
                    ikiwa line ni sio Tupu:
                        sys.stdout.write('    %s\n' % line.strip())
            isipokua:
                sys.stdout.write('#%i (unable to read python frame information)\n' % self.get_index())
        isipokua:
            info = self.is_other_python_frame()
            ikiwa info:
                sys.stdout.write('#%i %s\n' % (self.get_index(), info))
            isipokua:
                sys.stdout.write('#%i\n' % self.get_index())

    eleza print_traceback(self):
        ikiwa self.is_evalframe():
            pyop = self.get_pyop()
            ikiwa pyop:
                pyop.print_traceback()
                ikiwa sio pyop.is_optimized_out():
                    line = pyop.current_line()
                    ikiwa line ni sio Tupu:
                        sys.stdout.write('    %s\n' % line.strip())
            isipokua:
                sys.stdout.write('  (unable to read python frame information)\n')
        isipokua:
            info = self.is_other_python_frame()
            ikiwa info:
                sys.stdout.write('  %s\n' % info)
            isipokua:
                sys.stdout.write('  (sio a python frame)\n')

kundi PyList(gdb.Command):
    '''List the current Python source code, ikiwa any

    Use
       py-list START
    to list at a different line number within the python source.

    Use
       py-list START, END
    to list a specific range of lines within the python source.
    '''

    eleza __init__(self):
        gdb.Command.__init__ (self,
                              "py-list",
                              gdb.COMMAND_FILES,
                              gdb.COMPLETE_NONE)


    eleza invoke(self, args, from_tty):
        agiza re

        start = Tupu
        end = Tupu

        m = re.match(r'\s*(\d+)\s*', args)
        ikiwa m:
            start = int(m.group(0))
            end = start + 10

        m = re.match(r'\s*(\d+)\s*,\s*(\d+)\s*', args)
        ikiwa m:
            start, end = map(int, m.groups())

        # py-list requires an actual PyEval_EvalFrameEx frame:
        frame = Frame.get_selected_bytecode_frame()
        ikiwa sio frame:
            andika('Unable to locate gdb frame kila python bytecode interpreter')
            rudisha

        pyop = frame.get_pyop()
        ikiwa sio pyop ama pyop.is_optimized_out():
            andika('Unable to read information on python frame')
            rudisha

        filename = pyop.filename()
        lineno = pyop.current_line_num()
        ikiwa lineno ni Tupu:
            andika('Unable to read python frame line number')
            rudisha

        ikiwa start ni Tupu:
            start = lineno - 5
            end = lineno + 5

        ikiwa start<1:
            start = 1

        jaribu:
            f = open(os_fsencode(filename), 'r')
        tatizo IOError kama err:
            sys.stdout.write('Unable to open %s: %s\n'
                             % (filename, err))
            rudisha
        ukijumuisha f:
            all_lines = f.readlines()
            # start na end are 1-based, all_lines ni 0-based;
            # so [start-1:end] kama a python slice gives us [start, end] kama a
            # closed interval
            kila i, line kwenye enumerate(all_lines[start-1:end]):
                linestr = str(i+start)
                # Highlight current line:
                ikiwa i + start == lineno:
                    linestr = '>' + linestr
                sys.stdout.write('%4s    %s' % (linestr, line))


# ...and register the command:
PyList()

eleza move_in_stack(move_up):
    '''Move up ama down the stack (kila the py-up/py-down command)'''
    frame = Frame.get_selected_python_frame()
    ikiwa sio frame:
        andika('Unable to locate python frame')
        rudisha

    wakati frame:
        ikiwa move_up:
            iter_frame = frame.older()
        isipokua:
            iter_frame = frame.newer()

        ikiwa sio iter_frame:
            koma

        ikiwa iter_frame.is_python_frame():
            # Result:
            ikiwa iter_frame.select():
                iter_frame.print_summary()
            rudisha

        frame = iter_frame

    ikiwa move_up:
        andika('Unable to find an older python frame')
    isipokua:
        andika('Unable to find a newer python frame')

kundi PyUp(gdb.Command):
    'Select na print the python stack frame that called this one (ikiwa any)'
    eleza __init__(self):
        gdb.Command.__init__ (self,
                              "py-up",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    eleza invoke(self, args, from_tty):
        move_in_stack(move_up=Kweli)

kundi PyDown(gdb.Command):
    'Select na print the python stack frame called by this one (ikiwa any)'
    eleza __init__(self):
        gdb.Command.__init__ (self,
                              "py-down",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    eleza invoke(self, args, from_tty):
        move_in_stack(move_up=Uongo)

# Not all builds of gdb have gdb.Frame.select
ikiwa hasattr(gdb.Frame, 'select'):
    PyUp()
    PyDown()

kundi PyBacktraceFull(gdb.Command):
    'Display the current python frame na all the frames within its call stack (ikiwa any)'
    eleza __init__(self):
        gdb.Command.__init__ (self,
                              "py-bt-full",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    eleza invoke(self, args, from_tty):
        frame = Frame.get_selected_python_frame()
        ikiwa sio frame:
            andika('Unable to locate python frame')
            rudisha

        wakati frame:
            ikiwa frame.is_python_frame():
                frame.print_summary()
            frame = frame.older()

PyBacktraceFull()

kundi PyBacktrace(gdb.Command):
    'Display the current python frame na all the frames within its call stack (ikiwa any)'
    eleza __init__(self):
        gdb.Command.__init__ (self,
                              "py-bt",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    eleza invoke(self, args, from_tty):
        frame = Frame.get_selected_python_frame()
        ikiwa sio frame:
            andika('Unable to locate python frame')
            rudisha

        sys.stdout.write('Traceback (most recent call first):\n')
        wakati frame:
            ikiwa frame.is_python_frame():
                frame.print_traceback()
            frame = frame.older()

PyBacktrace()

kundi PyPrint(gdb.Command):
    'Look up the given python variable name, na print it'
    eleza __init__(self):
        gdb.Command.__init__ (self,
                              "py-print",
                              gdb.COMMAND_DATA,
                              gdb.COMPLETE_NONE)


    eleza invoke(self, args, from_tty):
        name = str(args)

        frame = Frame.get_selected_python_frame()
        ikiwa sio frame:
            andika('Unable to locate python frame')
            rudisha

        pyop_frame = frame.get_pyop()
        ikiwa sio pyop_frame:
            andika('Unable to read information on python frame')
            rudisha

        pyop_var, scope = pyop_frame.get_var_by_name(name)

        ikiwa pyop_var:
            andika('%s %r = %s'
                   % (scope,
                      name,
                      pyop_var.get_truncated_repr(MAX_OUTPUT_LEN)))
        isipokua:
            andika('%r sio found' % name)

PyPrint()

kundi PyLocals(gdb.Command):
    'Look up the given python variable name, na print it'
    eleza __init__(self):
        gdb.Command.__init__ (self,
                              "py-locals",
                              gdb.COMMAND_DATA,
                              gdb.COMPLETE_NONE)


    eleza invoke(self, args, from_tty):
        name = str(args)

        frame = Frame.get_selected_python_frame()
        ikiwa sio frame:
            andika('Unable to locate python frame')
            rudisha

        pyop_frame = frame.get_pyop()
        ikiwa sio pyop_frame:
            andika('Unable to read information on python frame')
            rudisha

        kila pyop_name, pyop_value kwenye pyop_frame.iter_locals():
            andika('%s = %s'
                   % (pyop_name.proxyval(set()),
                      pyop_value.get_truncated_repr(MAX_OUTPUT_LEN)))

PyLocals()
