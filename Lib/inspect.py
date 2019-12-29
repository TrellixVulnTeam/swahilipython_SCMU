"""Get useful information kutoka live Python objects.

This module encapsulates the interface provided by the internal special
attributes (co_*, im_*, tb_*, etc.) kwenye a friendlier fashion.
It also provides some help kila examining source code na kundi layout.

Here are some of the useful functions provided by this module:

    ismodule(), isclass(), ismethod(), isfunction(), isgeneratorfunction(),
        isgenerator(), istraceback(), isframe(), iscode(), isbuiltin(),
        isroutine() - check object types
    getmembers() - get members of an object that satisfy a given condition

    getfile(), getsourcefile(), getsource() - find an object's source code
    getdoc(), getcomments() - get documentation on an object
    getmodule() - determine the module that an object came kutoka
    getclasstree() - arrange classes so kama to represent their hierarchy

    getargvalues(), getcallargs() - get info about function arguments
    getfullargspec() - same, ukijumuisha support kila Python 3 features
    formatargvalues() - format an argument spec
    getouterframes(), getinnerframes() - get info about frames
    currentframe() - get the current stack frame
    stack(), trace() - get info about frames on the stack ama kwenye a traceback

    signature() - get a Signature object kila the callable
"""

# This module ni kwenye the public domain.  No warranties.

__author__ = ('Ka-Ping Yee <ping@lfw.org>',
              'Yury Selivanov <yselivanov@sprymix.com>')

agiza abc
agiza dis
agiza collections.abc
agiza enum
agiza importlib.machinery
agiza itertools
agiza linecache
agiza os
agiza re
agiza sys
agiza tokenize
agiza token
agiza types
agiza warnings
agiza functools
agiza builtins
kutoka operator agiza attrgetter
kutoka collections agiza namedtuple, OrderedDict

# Create constants kila the compiler flags kwenye Include/code.h
# We try to get them kutoka dis to avoid duplication
mod_dict = globals()
kila k, v kwenye dis.COMPILER_FLAG_NAMES.items():
    mod_dict["CO_" + v] = k

# See Include/object.h
TPFLAGS_IS_ABSTRACT = 1 << 20

# ----------------------------------------------------------- type-checking
eleza ismodule(object):
    """Return true ikiwa the object ni a module.

    Module objects provide these attributes:
        __cached__      pathname to byte compiled file
        __doc__         documentation string
        __file__        filename (missing kila built-in modules)"""
    rudisha isinstance(object, types.ModuleType)

eleza isclass(object):
    """Return true ikiwa the object ni a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module kwenye which this kundi was defined"""
    rudisha isinstance(object, type)

eleza ismethod(object):
    """Return true ikiwa the object ni an instance method.

    Instance method objects provide these attributes:
        __doc__         documentation string
        __name__        name ukijumuisha which this method was defined
        __func__        function object containing implementation of method
        __self__        instance to which this method ni bound"""
    rudisha isinstance(object, types.MethodType)

eleza ismethoddescriptor(object):
    """Return true ikiwa the object ni a method descriptor.

    But sio ikiwa ismethod() ama isclass() ama isfunction() are true.

    This ni new kwenye Python 2.2, and, kila example, ni true of int.__add__.
    An object pitaing this test has a __get__ attribute but sio a __set__
    attribute, but beyond that the set of attributes varies.  __name__ is
    usually sensible, na __doc__ often is.

    Methods implemented via descriptors that also pita one of the other
    tests rudisha false kutoka the ismethoddescriptor() test, simply because
    the other tests promise more -- you can, e.g., count on having the
    __func__ attribute (etc) when an object pitaes ismethod()."""
    ikiwa isclass(object) ama ismethod(object) ama isfunction(object):
        # mutual exclusion
        rudisha Uongo
    tp = type(object)
    rudisha hasattr(tp, "__get__") na sio hasattr(tp, "__set__")

eleza isdatadescriptor(object):
    """Return true ikiwa the object ni a data descriptor.

    Data descriptors have a __set__ ama a __delete__ attribute.  Examples are
    properties (defined kwenye Python) na getsets na members (defined kwenye C).
    Typically, data descriptors will also have __name__ na __doc__ attributes
    (properties, getsets, na members have both of these attributes), but this
    ni sio guaranteed."""
    ikiwa isclass(object) ama ismethod(object) ama isfunction(object):
        # mutual exclusion
        rudisha Uongo
    tp = type(object)
    rudisha hasattr(tp, "__set__") ama hasattr(tp, "__delete__")

ikiwa hasattr(types, 'MemberDescriptorType'):
    # CPython na equivalent
    eleza ismemberdescriptor(object):
        """Return true ikiwa the object ni a member descriptor.

        Member descriptors are specialized descriptors defined kwenye extension
        modules."""
        rudisha isinstance(object, types.MemberDescriptorType)
isipokua:
    # Other implementations
    eleza ismemberdescriptor(object):
        """Return true ikiwa the object ni a member descriptor.

        Member descriptors are specialized descriptors defined kwenye extension
        modules."""
        rudisha Uongo

ikiwa hasattr(types, 'GetSetDescriptorType'):
    # CPython na equivalent
    eleza isgetsetdescriptor(object):
        """Return true ikiwa the object ni a getset descriptor.

        getset descriptors are specialized descriptors defined kwenye extension
        modules."""
        rudisha isinstance(object, types.GetSetDescriptorType)
isipokua:
    # Other implementations
    eleza isgetsetdescriptor(object):
        """Return true ikiwa the object ni a getset descriptor.

        getset descriptors are specialized descriptors defined kwenye extension
        modules."""
        rudisha Uongo

eleza isfunction(object):
    """Return true ikiwa the object ni a user-defined function.

    Function objects provide these attributes:
        __doc__         documentation string
        __name__        name ukijumuisha which this function was defined
        __code__        code object containing compiled function bytecode
        __defaults__    tuple of any default values kila arguments
        __globals__     global namespace kwenye which this function was defined
        __annotations__ dict of parameter annotations
        __kwdefaults__  dict of keyword only parameters ukijumuisha defaults"""
    rudisha isinstance(object, types.FunctionType)

eleza _has_code_flag(f, flag):
    """Return true ikiwa ``f`` ni a function (or a method ama functools.partial
    wrapper wrapping a function) whose code object has the given ``flag``
    set kwenye its flags."""
    wakati ismethod(f):
        f = f.__func__
    f = functools._unwrap_partial(f)
    ikiwa sio isfunction(f):
        rudisha Uongo
    rudisha bool(f.__code__.co_flags & flag)

eleza isgeneratorfunction(obj):
    """Return true ikiwa the object ni a user-defined generator function.

    Generator function objects provide the same attributes kama functions.
    See help(isfunction) kila a list of attributes."""
    rudisha _has_code_flag(obj, CO_GENERATOR)

eleza iscoroutinefunction(obj):
    """Return true ikiwa the object ni a coroutine function.

    Coroutine functions are defined ukijumuisha "async def" syntax.
    """
    rudisha _has_code_flag(obj, CO_COROUTINE)

eleza isasyncgenfunction(obj):
    """Return true ikiwa the object ni an asynchronous generator function.

    Asynchronous generator functions are defined ukijumuisha "async def"
    syntax na have "tuma" expressions kwenye their body.
    """
    rudisha _has_code_flag(obj, CO_ASYNC_GENERATOR)

eleza isasyncgen(object):
    """Return true ikiwa the object ni an asynchronous generator."""
    rudisha isinstance(object, types.AsyncGeneratorType)

eleza isgenerator(object):
    """Return true ikiwa the object ni a generator.

    Generator objects provide these attributes:
        __iter__        defined to support iteration over container
        close           ashirias a new GeneratorExit exception inside the
                        generator to terminate the iteration
        gi_code         code object
        gi_frame        frame object ama possibly Tupu once the generator has
                        been exhausted
        gi_running      set to 1 when generator ni executing, 0 otherwise
        next            rudisha the next item kutoka the container
        send            resumes the generator na "sends" a value that becomes
                        the result of the current tuma-expression
        throw           used to ashiria an exception inside the generator"""
    rudisha isinstance(object, types.GeneratorType)

eleza iscoroutine(object):
    """Return true ikiwa the object ni a coroutine."""
    rudisha isinstance(object, types.CoroutineType)

eleza isawaitable(object):
    """Return true ikiwa object can be pitaed to an ``await`` expression."""
    rudisha (isinstance(object, types.CoroutineType) or
            isinstance(object, types.GeneratorType) and
                bool(object.gi_code.co_flags & CO_ITERABLE_COROUTINE) or
            isinstance(object, collections.abc.Awaitable))

eleza istraceback(object):
    """Return true ikiwa the object ni a traceback.

    Traceback objects provide these attributes:
        tb_frame        frame object at this level
        tb_lasti        index of last attempted instruction kwenye bytecode
        tb_lineno       current line number kwenye Python source code
        tb_next         next inner traceback object (called by this level)"""
    rudisha isinstance(object, types.TracebackType)

eleza isframe(object):
    """Return true ikiwa the object ni a frame object.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller)
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed kwenye this frame
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction kwenye bytecode
        f_lineno        current line number kwenye Python source code
        f_locals        local namespace seen by this frame
        f_trace         tracing function kila this frame, ama Tupu"""
    rudisha isinstance(object, types.FrameType)

eleza iscode(object):
    """Return true ikiwa the object ni a code object.

    Code objects provide these attributes:
        co_argcount         number of arguments (not including *, ** args
                            ama keyword only arguments)
        co_code             string of raw compiled bytecode
        co_cellvars         tuple of names of cell variables
        co_consts           tuple of constants used kwenye the bytecode
        co_filename         name of file kwenye which this code object was created
        co_firstlineno      number of first line kwenye Python source code
        co_flags            bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg
                            | 16=nested | 32=generator | 64=nofree | 128=coroutine
                            | 256=iterable_coroutine | 512=async_generator
        co_freevars         tuple of names of free variables
        co_posonlyargcount  number of positional only arguments
        co_kwonlyargcount   number of keyword only arguments (not including ** arg)
        co_lnotab           encoded mapping of line numbers to bytecode indices
        co_name             name ukijumuisha which this code object was defined
        co_names            tuple of names of local variables
        co_nlocals          number of local variables
        co_stacksize        virtual machine stack space required
        co_varnames         tuple of names of arguments na local variables"""
    rudisha isinstance(object, types.CodeType)

eleza isbuiltin(object):
    """Return true ikiwa the object ni a built-in function ama method.

    Built-in functions na methods provide these attributes:
        __doc__         documentation string
        __name__        original name of this function ama method
        __self__        instance to which a method ni bound, ama Tupu"""
    rudisha isinstance(object, types.BuiltinFunctionType)

eleza isroutine(object):
    """Return true ikiwa the object ni any kind of function ama method."""
    rudisha (isbuiltin(object)
            ama isfunction(object)
            ama ismethod(object)
            ama ismethoddescriptor(object))

eleza isabstract(object):
    """Return true ikiwa the object ni an abstract base kundi (ABC)."""
    ikiwa sio isinstance(object, type):
        rudisha Uongo
    ikiwa object.__flags__ & TPFLAGS_IS_ABSTRACT:
        rudisha Kweli
    ikiwa sio issubclass(type(object), abc.ABCMeta):
        rudisha Uongo
    ikiwa hasattr(object, '__abstractmethods__'):
        # It looks like ABCMeta.__new__ has finished running;
        # TPFLAGS_IS_ABSTRACT should have been accurate.
        rudisha Uongo
    # It looks like ABCMeta.__new__ has sio finished running yet; we're
    # probably kwenye __init_subclass__. We'll look kila abstractmethods manually.
    kila name, value kwenye object.__dict__.items():
        ikiwa getattr(value, "__isabstractmethod__", Uongo):
            rudisha Kweli
    kila base kwenye object.__bases__:
        kila name kwenye getattr(base, "__abstractmethods__", ()):
            value = getattr(object, name, Tupu)
            ikiwa getattr(value, "__isabstractmethod__", Uongo):
                rudisha Kweli
    rudisha Uongo

eleza getmembers(object, predicate=Tupu):
    """Return all members of an object kama (name, value) pairs sorted by name.
    Optionally, only rudisha members that satisfy a given predicate."""
    ikiwa isclass(object):
        mro = (object,) + getmro(object)
    isipokua:
        mro = ()
    results = []
    processed = set()
    names = dir(object)
    # :dd any DynamicClassAttributes to the list of names ikiwa object ni a class;
    # this may result kwenye duplicate entries if, kila example, a virtual
    # attribute ukijumuisha the same name kama a DynamicClassAttribute exists
    jaribu:
        kila base kwenye object.__bases__:
            kila k, v kwenye base.__dict__.items():
                ikiwa isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    tatizo AttributeError:
        pita
    kila key kwenye names:
        # First try to get the value via getattr.  Some descriptors don't
        # like calling their __get__ (see bug #1785), so fall back to
        # looking kwenye the __dict__.
        jaribu:
            value = getattr(object, key)
            # handle the duplicate key
            ikiwa key kwenye processed:
                ashiria AttributeError
        tatizo AttributeError:
            kila base kwenye mro:
                ikiwa key kwenye base.__dict__:
                    value = base.__dict__[key]
                    koma
            isipokua:
                # could be a (currently) missing slot member, ama a buggy
                # __dir__; discard na move on
                endelea
        ikiwa sio predicate ama predicate(value):
            results.append((key, value))
        processed.add(key)
    results.sort(key=lambda pair: pair[0])
    rudisha results

Attribute = namedtuple('Attribute', 'name kind defining_kundi object')

eleza classify_class_attrs(cls):
    """Return list of attribute-descriptor tuples.

    For each name kwenye dir(cls), the rudisha list contains a 4-tuple
    ukijumuisha these elements:

        0. The name (a string).

        1. The kind of attribute this is, one of these strings:
               'kundi method'    created via classmethod()
               'static method'   created via staticmethod()
               'property'        created via property()
               'method'          any other flavor of method ama descriptor
               'data'            sio a method

        2. The kundi which defined this attribute (a class).

        3. The object kama obtained by calling getattr; ikiwa this fails, ama ikiwa the
           resulting object does sio live anywhere kwenye the class' mro (including
           metaclasses) then the object ni looked up kwenye the defining class's
           dict (found by walking the mro).

    If one of the items kwenye dir(cls) ni stored kwenye the metakundi it will now
    be discovered na sio have Tupu be listed kama the kundi kwenye which it was
    defined.  Any items whose home kundi cannot be discovered are skipped.
    """

    mro = getmro(cls)
    metamro = getmro(type(cls)) # kila attributes stored kwenye the metaclass
    metamro = tuple(cls kila cls kwenye metamro ikiwa cls haiko kwenye (type, object))
    class_bases = (cls,) + mro
    all_bases = class_bases + metamro
    names = dir(cls)
    # :dd any DynamicClassAttributes to the list of names;
    # this may result kwenye duplicate entries if, kila example, a virtual
    # attribute ukijumuisha the same name kama a DynamicClassAttribute exists.
    kila base kwenye mro:
        kila k, v kwenye base.__dict__.items():
            ikiwa isinstance(v, types.DynamicClassAttribute):
                names.append(k)
    result = []
    processed = set()

    kila name kwenye names:
        # Get the object associated ukijumuisha the name, na where it was defined.
        # Normal objects will be looked up ukijumuisha both getattr na directly in
        # its class' dict (in case getattr fails [bug #1785], na also to look
        # kila a docstring).
        # For DynamicClassAttributes on the second pita we only look kwenye the
        # class's dict.
        #
        # Getting an obj kutoka the __dict__ sometimes reveals more than
        # using getattr.  Static na kundi methods are dramatic examples.
        homecls = Tupu
        get_obj = Tupu
        dict_obj = Tupu
        ikiwa name haiko kwenye processed:
            jaribu:
                ikiwa name == '__dict__':
                    ashiria Exception("__dict__ ni special, don't want the proxy")
                get_obj = getattr(cls, name)
            tatizo Exception kama exc:
                pita
            isipokua:
                homecls = getattr(get_obj, "__objclass__", homecls)
                ikiwa homecls haiko kwenye class_bases:
                    # ikiwa the resulting object does sio live somewhere kwenye the
                    # mro, drop it na search the mro manually
                    homecls = Tupu
                    last_cls = Tupu
                    # first look kwenye the classes
                    kila srch_cls kwenye class_bases:
                        srch_obj = getattr(srch_cls, name, Tupu)
                        ikiwa srch_obj ni get_obj:
                            last_cls = srch_cls
                    # then check the metaclasses
                    kila srch_cls kwenye metamro:
                        jaribu:
                            srch_obj = srch_cls.__getattr__(cls, name)
                        tatizo AttributeError:
                            endelea
                        ikiwa srch_obj ni get_obj:
                            last_cls = srch_cls
                    ikiwa last_cls ni sio Tupu:
                        homecls = last_cls
        kila base kwenye all_bases:
            ikiwa name kwenye base.__dict__:
                dict_obj = base.__dict__[name]
                ikiwa homecls haiko kwenye metamro:
                    homecls = base
                koma
        ikiwa homecls ni Tupu:
            # unable to locate the attribute anywhere, most likely due to
            # buggy custom __dir__; discard na move on
            endelea
        obj = get_obj ikiwa get_obj ni sio Tupu isipokua dict_obj
        # Classify the object ama its descriptor.
        ikiwa isinstance(dict_obj, (staticmethod, types.BuiltinMethodType)):
            kind = "static method"
            obj = dict_obj
        lasivyo isinstance(dict_obj, (classmethod, types.ClassMethodDescriptorType)):
            kind = "kundi method"
            obj = dict_obj
        lasivyo isinstance(dict_obj, property):
            kind = "property"
            obj = dict_obj
        lasivyo isroutine(obj):
            kind = "method"
        isipokua:
            kind = "data"
        result.append(Attribute(name, kind, homecls, obj))
        processed.add(name)
    rudisha result

# ----------------------------------------------------------- kundi helpers

eleza getmro(cls):
    "Return tuple of base classes (including cls) kwenye method resolution order."
    rudisha cls.__mro__

# -------------------------------------------------------- function helpers

eleza unwrap(func, *, stop=Tupu):
    """Get the object wrapped by *func*.

   Follows the chain of :attr:`__wrapped__` attributes rudishaing the last
   object kwenye the chain.

   *stop* ni an optional callback accepting an object kwenye the wrapper chain
   kama its sole argument that allows the unwrapping to be terminated early if
   the callback rudishas a true value. If the callback never rudishas a true
   value, the last object kwenye the chain ni rudishaed kama usual. For example,
   :func:`signature` uses this to stop unwrapping ikiwa any object kwenye the
   chain has a ``__signature__`` attribute defined.

   :exc:`ValueError` ni ashiriad ikiwa a cycle ni encountered.

    """
    ikiwa stop ni Tupu:
        eleza _is_wrapper(f):
            rudisha hasattr(f, '__wrapped__')
    isipokua:
        eleza _is_wrapper(f):
            rudisha hasattr(f, '__wrapped__') na sio stop(f)
    f = func  # remember the original func kila error reporting
    # Memoise by id to tolerate non-hashable objects, but store objects to
    # ensure they aren't destroyed, which would allow their IDs to be reused.
    memo = {id(f): f}
    recursion_limit = sys.getrecursionlimit()
    wakati _is_wrapper(func):
        func = func.__wrapped__
        id_func = id(func)
        ikiwa (id_func kwenye memo) ama (len(memo) >= recursion_limit):
            ashiria ValueError('wrapper loop when unwrapping {!r}'.format(f))
        memo[id_func] = func
    rudisha func

# -------------------------------------------------- source code extraction
eleza indentsize(line):
    """Return the indent size, kwenye spaces, at the start of a line of text."""
    expline = line.expandtabs()
    rudisha len(expline) - len(expline.lstrip())

eleza _findclass(func):
    cls = sys.modules.get(func.__module__)
    ikiwa cls ni Tupu:
        rudisha Tupu
    kila name kwenye func.__qualname__.split('.')[:-1]:
        cls = getattr(cls, name)
    ikiwa sio isclass(cls):
        rudisha Tupu
    rudisha cls

eleza _finddoc(obj):
    ikiwa isclass(obj):
        kila base kwenye obj.__mro__:
            ikiwa base ni sio object:
                jaribu:
                    doc = base.__doc__
                tatizo AttributeError:
                    endelea
                ikiwa doc ni sio Tupu:
                    rudisha doc
        rudisha Tupu

    ikiwa ismethod(obj):
        name = obj.__func__.__name__
        self = obj.__self__
        ikiwa (isclass(self) and
            getattr(getattr(self, name, Tupu), '__func__') ni obj.__func__):
            # classmethod
            cls = self
        isipokua:
            cls = self.__class__
    lasivyo isfunction(obj):
        name = obj.__name__
        cls = _findclass(obj)
        ikiwa cls ni Tupu ama getattr(cls, name) ni sio obj:
            rudisha Tupu
    lasivyo isbuiltin(obj):
        name = obj.__name__
        self = obj.__self__
        ikiwa (isclass(self) and
            self.__qualname__ + '.' + name == obj.__qualname__):
            # classmethod
            cls = self
        isipokua:
            cls = self.__class__
    # Should be tested before isdatadescriptor().
    lasivyo isinstance(obj, property):
        func = obj.fget
        name = func.__name__
        cls = _findclass(func)
        ikiwa cls ni Tupu ama getattr(cls, name) ni sio obj:
            rudisha Tupu
    lasivyo ismethoddescriptor(obj) ama isdatadescriptor(obj):
        name = obj.__name__
        cls = obj.__objclass__
        ikiwa getattr(cls, name) ni sio obj:
            rudisha Tupu
        ikiwa ismemberdescriptor(obj):
            slots = getattr(cls, '__slots__', Tupu)
            ikiwa isinstance(slots, dict) na name kwenye slots:
                rudisha slots[name]
    isipokua:
        rudisha Tupu
    kila base kwenye cls.__mro__:
        jaribu:
            doc = getattr(base, name).__doc__
        tatizo AttributeError:
            endelea
        ikiwa doc ni sio Tupu:
            rudisha doc
    rudisha Tupu

eleza getdoc(object):
    """Get the documentation string kila an object.

    All tabs are expanded to spaces.  To clean up docstrings that are
    indented to line up ukijumuisha blocks of code, any whitespace than can be
    uniformly removed kutoka the second line onwards ni removed."""
    jaribu:
        doc = object.__doc__
    tatizo AttributeError:
        rudisha Tupu
    ikiwa doc ni Tupu:
        jaribu:
            doc = _finddoc(object)
        tatizo (AttributeError, TypeError):
            rudisha Tupu
    ikiwa sio isinstance(doc, str):
        rudisha Tupu
    rudisha cleandoc(doc)

eleza cleandoc(doc):
    """Clean up indentation kutoka docstrings.

    Any whitespace that can be uniformly removed kutoka the second line
    onwards ni removed."""
    jaribu:
        lines = doc.expandtabs().split('\n')
    tatizo UnicodeError:
        rudisha Tupu
    isipokua:
        # Find minimum indentation of any non-blank lines after first line.
        margin = sys.maxsize
        kila line kwenye lines[1:]:
            content = len(line.lstrip())
            ikiwa content:
                indent = len(line) - content
                margin = min(margin, indent)
        # Remove indentation.
        ikiwa lines:
            lines[0] = lines[0].lstrip()
        ikiwa margin < sys.maxsize:
            kila i kwenye range(1, len(lines)): lines[i] = lines[i][margin:]
        # Remove any trailing ama leading blank lines.
        wakati lines na sio lines[-1]:
            lines.pop()
        wakati lines na sio lines[0]:
            lines.pop(0)
        rudisha '\n'.join(lines)

eleza getfile(object):
    """Work out which source ama compiled file an object was defined in."""
    ikiwa ismodule(object):
        ikiwa getattr(object, '__file__', Tupu):
            rudisha object.__file__
        ashiria TypeError('{!r} ni a built-in module'.format(object))
    ikiwa isclass(object):
        ikiwa hasattr(object, '__module__'):
            module = sys.modules.get(object.__module__)
            ikiwa getattr(module, '__file__', Tupu):
                rudisha module.__file__
        ashiria TypeError('{!r} ni a built-in class'.format(object))
    ikiwa ismethod(object):
        object = object.__func__
    ikiwa isfunction(object):
        object = object.__code__
    ikiwa istraceback(object):
        object = object.tb_frame
    ikiwa isframe(object):
        object = object.f_code
    ikiwa iscode(object):
        rudisha object.co_filename
    ashiria TypeError('module, class, method, function, traceback, frame, ama '
                    'code object was expected, got {}'.format(
                    type(object).__name__))

eleza getmodulename(path):
    """Return the module name kila a given file, ama Tupu."""
    fname = os.path.basename(path)
    # Check kila paths that look like an actual module file
    suffixes = [(-len(suffix), suffix)
                    kila suffix kwenye importlib.machinery.all_suffixes()]
    suffixes.sort() # try longest suffixes first, kwenye case they overlap
    kila neglen, suffix kwenye suffixes:
        ikiwa fname.endswith(suffix):
            rudisha fname[:neglen]
    rudisha Tupu

eleza getsourcefile(object):
    """Return the filename that can be used to locate an object's source.
    Return Tupu ikiwa no way can be identified to get the source.
    """
    filename = getfile(object)
    all_bytecode_suffixes = importlib.machinery.DEBUG_BYTECODE_SUFFIXES[:]
    all_bytecode_suffixes += importlib.machinery.OPTIMIZED_BYTECODE_SUFFIXES[:]
    ikiwa any(filename.endswith(s) kila s kwenye all_bytecode_suffixes):
        filename = (os.path.splitext(filename)[0] +
                    importlib.machinery.SOURCE_SUFFIXES[0])
    lasivyo any(filename.endswith(s) kila s in
                 importlib.machinery.EXTENSION_SUFFIXES):
        rudisha Tupu
    ikiwa os.path.exists(filename):
        rudisha filename
    # only rudisha a non-existent filename ikiwa the module has a PEP 302 loader
    ikiwa getattr(getmodule(object, filename), '__loader__', Tupu) ni sio Tupu:
        rudisha filename
    # ama it ni kwenye the linecache
    ikiwa filename kwenye linecache.cache:
        rudisha filename

eleza getabsfile(object, _filename=Tupu):
    """Return an absolute path to the source ama compiled file kila an object.

    The idea ni kila each object to have a unique origin, so this routine
    normalizes the result kama much kama possible."""
    ikiwa _filename ni Tupu:
        _filename = getsourcefile(object) ama getfile(object)
    rudisha os.path.normcase(os.path.abspath(_filename))

modulesbyfile = {}
_filesbymodname = {}

eleza getmodule(object, _filename=Tupu):
    """Return the module an object was defined in, ama Tupu ikiwa sio found."""
    ikiwa ismodule(object):
        rudisha object
    ikiwa hasattr(object, '__module__'):
        rudisha sys.modules.get(object.__module__)
    # Try the filename to modulename cache
    ikiwa _filename ni sio Tupu na _filename kwenye modulesbyfile:
        rudisha sys.modules.get(modulesbyfile[_filename])
    # Try the cache again ukijumuisha the absolute file name
    jaribu:
        file = getabsfile(object, _filename)
    tatizo TypeError:
        rudisha Tupu
    ikiwa file kwenye modulesbyfile:
        rudisha sys.modules.get(modulesbyfile[file])
    # Update the filename to module name cache na check yet again
    # Copy sys.modules kwenye order to cope ukijumuisha changes wakati iterating
    kila modname, module kwenye list(sys.modules.items()):
        ikiwa ismodule(module) na hasattr(module, '__file__'):
            f = module.__file__
            ikiwa f == _filesbymodname.get(modname, Tupu):
                # Have already mapped this module, so skip it
                endelea
            _filesbymodname[modname] = f
            f = getabsfile(module)
            # Always map to the name the module knows itself by
            modulesbyfile[f] = modulesbyfile[
                os.path.realpath(f)] = module.__name__
    ikiwa file kwenye modulesbyfile:
        rudisha sys.modules.get(modulesbyfile[file])
    # Check the main module
    main = sys.modules['__main__']
    ikiwa sio hasattr(object, '__name__'):
        rudisha Tupu
    ikiwa hasattr(main, object.__name__):
        mainobject = getattr(main, object.__name__)
        ikiwa mainobject ni object:
            rudisha main
    # Check builtins
    builtin = sys.modules['builtins']
    ikiwa hasattr(builtin, object.__name__):
        builtinobject = getattr(builtin, object.__name__)
        ikiwa builtinobject ni object:
            rudisha builtin

eleza findsource(object):
    """Return the entire source file na starting line number kila an object.

    The argument may be a module, class, method, function, traceback, frame,
    ama code object.  The source code ni rudishaed kama a list of all the lines
    kwenye the file na the line number indexes a line kwenye that list.  An OSError
    ni ashiriad ikiwa the source code cannot be retrieved."""

    file = getsourcefile(object)
    ikiwa file:
        # Invalidate cache ikiwa needed.
        linecache.checkcache(file)
    isipokua:
        file = getfile(object)
        # Allow filenames kwenye form of "<something>" to pita through.
        # `doctest` monkeypatches `linecache` module to enable
        # inspection, so let `linecache.getlines` to be called.
        ikiwa sio (file.startswith('<') na file.endswith('>')):
            ashiria OSError('source code sio available')

    module = getmodule(object, file)
    ikiwa module:
        lines = linecache.getlines(file, module.__dict__)
    isipokua:
        lines = linecache.getlines(file)
    ikiwa sio lines:
        ashiria OSError('could sio get source code')

    ikiwa ismodule(object):
        rudisha lines, 0

    ikiwa isclass(object):
        name = object.__name__
        pat = re.compile(r'^(\s*)class\s*' + name + r'\b')
        # make some effort to find the best matching kundi definition:
        # use the one ukijumuisha the least indentation, which ni the one
        # that's most probably sio inside a function definition.
        candidates = []
        kila i kwenye range(len(lines)):
            match = pat.match(lines[i])
            ikiwa match:
                # ikiwa it's at toplevel, it's already the best one
                ikiwa lines[i][0] == 'c':
                    rudisha lines, i
                # isipokua add whitespace to candidate list
                candidates.append((match.group(1), i))
        ikiwa candidates:
            # this will sort by whitespace, na by line number,
            # less whitespace first
            candidates.sort()
            rudisha lines, candidates[0][1]
        isipokua:
            ashiria OSError('could sio find kundi definition')

    ikiwa ismethod(object):
        object = object.__func__
    ikiwa isfunction(object):
        object = object.__code__
    ikiwa istraceback(object):
        object = object.tb_frame
    ikiwa isframe(object):
        object = object.f_code
    ikiwa iscode(object):
        ikiwa sio hasattr(object, 'co_firstlineno'):
            ashiria OSError('could sio find function definition')
        lnum = object.co_firstlineno - 1
        pat = re.compile(r'^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
        wakati lnum > 0:
            ikiwa pat.match(lines[lnum]): koma
            lnum = lnum - 1
        rudisha lines, lnum
    ashiria OSError('could sio find code object')

eleza getcomments(object):
    """Get lines of comments immediately preceding an object's source code.

    Returns Tupu when source can't be found.
    """
    jaribu:
        lines, lnum = findsource(object)
    tatizo (OSError, TypeError):
        rudisha Tupu

    ikiwa ismodule(object):
        # Look kila a comment block at the top of the file.
        start = 0
        ikiwa lines na lines[0][:2] == '#!': start = 1
        wakati start < len(lines) na lines[start].strip() kwenye ('', '#'):
            start = start + 1
        ikiwa start < len(lines) na lines[start][:1] == '#':
            comments = []
            end = start
            wakati end < len(lines) na lines[end][:1] == '#':
                comments.append(lines[end].expandtabs())
                end = end + 1
            rudisha ''.join(comments)

    # Look kila a preceding block of comments at the same indentation.
    lasivyo lnum > 0:
        indent = indentsize(lines[lnum])
        end = lnum - 1
        ikiwa end >= 0 na lines[end].lstrip()[:1] == '#' na \
            indentsize(lines[end]) == indent:
            comments = [lines[end].expandtabs().lstrip()]
            ikiwa end > 0:
                end = end - 1
                comment = lines[end].expandtabs().lstrip()
                wakati comment[:1] == '#' na indentsize(lines[end]) == indent:
                    comments[:0] = [comment]
                    end = end - 1
                    ikiwa end < 0: koma
                    comment = lines[end].expandtabs().lstrip()
            wakati comments na comments[0].strip() == '#':
                comments[:1] = []
            wakati comments na comments[-1].strip() == '#':
                comments[-1:] = []
            rudisha ''.join(comments)

kundi EndOfBlock(Exception): pita

kundi BlockFinder:
    """Provide a tokeneater() method to detect the end of a code block."""
    eleza __init__(self):
        self.indent = 0
        self.islambda = Uongo
        self.started = Uongo
        self.pitaline = Uongo
        self.indecorator = Uongo
        self.decoratorhasargs = Uongo
        self.last = 1

    eleza tokeneater(self, type, token, srowcol, erowcol, line):
        ikiwa sio self.started na sio self.indecorator:
            # skip any decorators
            ikiwa token == "@":
                self.indecorator = Kweli
            # look kila the first "def", "class" ama "lambda"
            lasivyo token kwenye ("def", "class", "lambda"):
                ikiwa token == "lambda":
                    self.islambda = Kweli
                self.started = Kweli
            self.pitaline = Kweli    # skip to the end of the line
        lasivyo token == "(":
            ikiwa self.indecorator:
                self.decoratorhasargs = Kweli
        lasivyo token == ")":
            ikiwa self.indecorator:
                self.indecorator = Uongo
                self.decoratorhasargs = Uongo
        lasivyo type == tokenize.NEWLINE:
            self.pitaline = Uongo   # stop skipping when a NEWLINE ni seen
            self.last = srowcol[0]
            ikiwa self.islambda:       # lambdas always end at the first NEWLINE
                ashiria EndOfBlock
            # hitting a NEWLINE when kwenye a decorator without args
            # ends the decorator
            ikiwa self.indecorator na sio self.decoratorhasargs:
                self.indecorator = Uongo
        lasivyo self.pitaline:
            pita
        lasivyo type == tokenize.INDENT:
            self.indent = self.indent + 1
            self.pitaline = Kweli
        lasivyo type == tokenize.DEDENT:
            self.indent = self.indent - 1
            # the end of matching indent/dedent pairs end a block
            # (note that this only works kila "def"/"class" blocks,
            #  sio e.g. kila "ikiwa: isipokua:" ama "jaribu: mwishowe:" blocks)
            ikiwa self.indent <= 0:
                ashiria EndOfBlock
        lasivyo self.indent == 0 na type haiko kwenye (tokenize.COMMENT, tokenize.NL):
            # any other token on the same indentation level end the previous
            # block kama well, tatizo the pseudo-tokens COMMENT na NL.
            ashiria EndOfBlock

eleza getblock(lines):
    """Extract the block of code at the top of the given list of lines."""
    blockfinder = BlockFinder()
    jaribu:
        tokens = tokenize.generate_tokens(iter(lines).__next__)
        kila _token kwenye tokens:
            blockfinder.tokeneater(*_token)
    tatizo (EndOfBlock, IndentationError):
        pita
    rudisha lines[:blockfinder.last]

eleza getsourcelines(object):
    """Return a list of source lines na starting line number kila an object.

    The argument may be a module, class, method, function, traceback, frame,
    ama code object.  The source code ni rudishaed kama a list of the lines
    corresponding to the object na the line number indicates where kwenye the
    original source file the first line of code was found.  An OSError is
    ashiriad ikiwa the source code cannot be retrieved."""
    object = unwrap(object)
    lines, lnum = findsource(object)

    ikiwa istraceback(object):
        object = object.tb_frame

    # kila module ama frame that corresponds to module, rudisha all source lines
    ikiwa (ismodule(object) or
        (isframe(object) na object.f_code.co_name == "<module>")):
        rudisha lines, 0
    isipokua:
        rudisha getblock(lines[lnum:]), lnum + 1

eleza getsource(object):
    """Return the text of the source code kila an object.

    The argument may be a module, class, method, function, traceback, frame,
    ama code object.  The source code ni rudishaed kama a single string.  An
    OSError ni ashiriad ikiwa the source code cannot be retrieved."""
    lines, lnum = getsourcelines(object)
    rudisha ''.join(lines)

# --------------------------------------------------- kundi tree extraction
eleza walktree(classes, children, parent):
    """Recursive helper function kila getclasstree()."""
    results = []
    classes.sort(key=attrgetter('__module__', '__name__'))
    kila c kwenye classes:
        results.append((c, c.__bases__))
        ikiwa c kwenye children:
            results.append(walktree(children[c], children, c))
    rudisha results

eleza getclasstree(classes, unique=Uongo):
    """Arrange the given list of classes into a hierarchy of nested lists.

    Where a nested list appears, it contains classes derived kutoka the class
    whose entry immediately precedes the list.  Each entry ni a 2-tuple
    containing a kundi na a tuple of its base classes.  If the 'unique'
    argument ni true, exactly one entry appears kwenye the rudishaed structure
    kila each kundi kwenye the given list.  Otherwise, classes using multiple
    inheritance na their descendants will appear multiple times."""
    children = {}
    roots = []
    kila c kwenye classes:
        ikiwa c.__bases__:
            kila parent kwenye c.__bases__:
                ikiwa parent haiko kwenye children:
                    children[parent] = []
                ikiwa c haiko kwenye children[parent]:
                    children[parent].append(c)
                ikiwa unique na parent kwenye classes: koma
        lasivyo c haiko kwenye roots:
            roots.append(c)
    kila parent kwenye children:
        ikiwa parent haiko kwenye classes:
            roots.append(parent)
    rudisha walktree(roots, children, Tupu)

# ------------------------------------------------ argument list extraction
Arguments = namedtuple('Arguments', 'args, varargs, varkw')

eleza getargs(co):
    """Get information about the arguments accepted by a code object.

    Three things are rudishaed: (args, varargs, varkw), where
    'args' ni the list of argument names. Keyword-only arguments are
    appended. 'varargs' na 'varkw' are the names of the * na **
    arguments ama Tupu."""
    ikiwa sio iscode(co):
        ashiria TypeError('{!r} ni sio a code object'.format(co))

    names = co.co_varnames
    nargs = co.co_argcount
    nkwargs = co.co_kwonlyargcount
    args = list(names[:nargs])
    kwonlyargs = list(names[nargs:nargs+nkwargs])
    step = 0

    nargs += nkwargs
    varargs = Tupu
    ikiwa co.co_flags & CO_VARARGS:
        varargs = co.co_varnames[nargs]
        nargs = nargs + 1
    varkw = Tupu
    ikiwa co.co_flags & CO_VARKEYWORDS:
        varkw = co.co_varnames[nargs]
    rudisha Arguments(args + kwonlyargs, varargs, varkw)

ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')

eleza getargspec(func):
    """Get the names na default values of a function's parameters.

    A tuple of four things ni rudishaed: (args, varargs, keywords, defaults).
    'args' ni a list of the argument names, including keyword-only argument names.
    'varargs' na 'keywords' are the names of the * na ** parameters ama Tupu.
    'defaults' ni an n-tuple of the default values of the last n parameters.

    This function ni deprecated, kama it does sio support annotations or
    keyword-only parameters na will ashiria ValueError ikiwa either ni present
    on the supplied callable.

    For a more structured introspection API, use inspect.signature() instead.

    Alternatively, use getfullargspec() kila an API ukijumuisha a similar namedtuple
    based interface, but full support kila annotations na keyword-only
    parameters.

    Deprecated since Python 3.5, use `inspect.getfullargspec()`.
    """
    warnings.warn("inspect.getargspec() ni deprecated since Python 3.0, "
                  "use inspect.signature() ama inspect.getfullargspec()",
                  DeprecationWarning, stacklevel=2)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = \
        getfullargspec(func)
    ikiwa kwonlyargs ama ann:
        ashiria ValueError("Function has keyword-only parameters ama annotations"
                         ", use inspect.signature() API which can support them")
    rudisha ArgSpec(args, varargs, varkw, defaults)

FullArgSpec = namedtuple('FullArgSpec',
    'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations')

eleza getfullargspec(func):
    """Get the names na default values of a callable object's parameters.

    A tuple of seven things ni rudishaed:
    (args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations).
    'args' ni a list of the parameter names.
    'varargs' na 'varkw' are the names of the * na ** parameters ama Tupu.
    'defaults' ni an n-tuple of the default values of the last n parameters.
    'kwonlyargs' ni a list of keyword-only parameter names.
    'kwonlydefaults' ni a dictionary mapping names kutoka kwonlyargs to defaults.
    'annotations' ni a dictionary mapping parameter names to annotations.

    Notable differences kutoka inspect.signature():
      - the "self" parameter ni always reported, even kila bound methods
      - wrapper chains defined by __wrapped__ *not* unwrapped automatically
    """
    jaribu:
        # Re: `skip_bound_arg=Uongo`
        #
        # There ni a notable difference kwenye behaviour between getfullargspec
        # na Signature: the former always rudishas 'self' parameter kila bound
        # methods, whereas the Signature always shows the actual calling
        # signature of the pitaed object.
        #
        # To simulate this behaviour, we "unbind" bound methods, to trick
        # inspect.signature to always rudisha their first parameter ("self",
        # usually)

        # Re: `follow_wrapper_chains=Uongo`
        #
        # getfullargspec() historically ignored __wrapped__ attributes,
        # so we ensure that remains the case kwenye 3.3+

        sig = _signature_kutoka_callable(func,
                                       follow_wrapper_chains=Uongo,
                                       skip_bound_arg=Uongo,
                                       sigcls=Signature)
    tatizo Exception kama ex:
        # Most of the times 'signature' will ashiria ValueError.
        # But, it can also ashiria AttributeError, and, maybe something
        # else. So to be fully backwards compatible, we catch all
        # possible exceptions here, na reashiria a TypeError.
        ashiria TypeError('unsupported callable') kutoka ex

    args = []
    varargs = Tupu
    varkw = Tupu
    posonlyargs = []
    kwonlyargs = []
    defaults = ()
    annotations = {}
    defaults = ()
    kwdefaults = {}

    ikiwa sig.rudisha_annotation ni sio sig.empty:
        annotations['rudisha'] = sig.rudisha_annotation

    kila param kwenye sig.parameters.values():
        kind = param.kind
        name = param.name

        ikiwa kind ni _POSITIONAL_ONLY:
            posonlyargs.append(name)
            ikiwa param.default ni sio param.empty:
                defaults += (param.default,)
        lasivyo kind ni _POSITIONAL_OR_KEYWORD:
            args.append(name)
            ikiwa param.default ni sio param.empty:
                defaults += (param.default,)
        lasivyo kind ni _VAR_POSITIONAL:
            varargs = name
        lasivyo kind ni _KEYWORD_ONLY:
            kwonlyargs.append(name)
            ikiwa param.default ni sio param.empty:
                kwdefaults[name] = param.default
        lasivyo kind ni _VAR_KEYWORD:
            varkw = name

        ikiwa param.annotation ni sio param.empty:
            annotations[name] = param.annotation

    ikiwa sio kwdefaults:
        # compatibility ukijumuisha 'func.__kwdefaults__'
        kwdefaults = Tupu

    ikiwa sio defaults:
        # compatibility ukijumuisha 'func.__defaults__'
        defaults = Tupu

    rudisha FullArgSpec(posonlyargs + args, varargs, varkw, defaults,
                       kwonlyargs, kwdefaults, annotations)


ArgInfo = namedtuple('ArgInfo', 'args varargs keywords locals')

eleza getargvalues(frame):
    """Get information about arguments pitaed into a particular frame.

    A tuple of four things ni rudishaed: (args, varargs, varkw, locals).
    'args' ni a list of the argument names.
    'varargs' na 'varkw' are the names of the * na ** arguments ama Tupu.
    'locals' ni the locals dictionary of the given frame."""
    args, varargs, varkw = getargs(frame.f_code)
    rudisha ArgInfo(args, varargs, varkw, frame.f_locals)

eleza formatannotation(annotation, base_module=Tupu):
    ikiwa getattr(annotation, '__module__', Tupu) == 'typing':
        rudisha repr(annotation).replace('typing.', '')
    ikiwa isinstance(annotation, type):
        ikiwa annotation.__module__ kwenye ('builtins', base_module):
            rudisha annotation.__qualname__
        rudisha annotation.__module__+'.'+annotation.__qualname__
    rudisha repr(annotation)

eleza formatannotationrelativeto(object):
    module = getattr(object, '__module__', Tupu)
    eleza _formatannotation(annotation):
        rudisha formatannotation(annotation, module)
    rudisha _formatannotation

eleza formatargspec(args, varargs=Tupu, varkw=Tupu, defaults=Tupu,
                  kwonlyargs=(), kwonlydefaults={}, annotations={},
                  formatarg=str,
                  formatvarargs=lambda name: '*' + name,
                  formatvarkw=lambda name: '**' + name,
                  formatvalue=lambda value: '=' + repr(value),
                  formatrudishas=lambda text: ' -> ' + text,
                  formatannotation=formatannotation):
    """Format an argument spec kutoka the values rudishaed by getfullargspec.

    The first seven arguments are (args, varargs, varkw, defaults,
    kwonlyargs, kwonlydefaults, annotations).  The other five arguments
    are the corresponding optional formatting functions that are called to
    turn names na values into strings.  The last argument ni an optional
    function to format the sequence of arguments.

    Deprecated since Python 3.5: use the `signature` function na `Signature`
    objects.
    """

    kutoka warnings agiza warn

    warn("`formatargspec` ni deprecated since Python 3.5. Use `signature` na "
         "the `Signature` object directly",
         DeprecationWarning,
         stacklevel=2)

    eleza formatargandannotation(arg):
        result = formatarg(arg)
        ikiwa arg kwenye annotations:
            result += ': ' + formatannotation(annotations[arg])
        rudisha result
    specs = []
    ikiwa defaults:
        firstdefault = len(args) - len(defaults)
    kila i, arg kwenye enumerate(args):
        spec = formatargandannotation(arg)
        ikiwa defaults na i >= firstdefault:
            spec = spec + formatvalue(defaults[i - firstdefault])
        specs.append(spec)
    ikiwa varargs ni sio Tupu:
        specs.append(formatvarargs(formatargandannotation(varargs)))
    isipokua:
        ikiwa kwonlyargs:
            specs.append('*')
    ikiwa kwonlyargs:
        kila kwonlyarg kwenye kwonlyargs:
            spec = formatargandannotation(kwonlyarg)
            ikiwa kwonlydefaults na kwonlyarg kwenye kwonlydefaults:
                spec += formatvalue(kwonlydefaults[kwonlyarg])
            specs.append(spec)
    ikiwa varkw ni sio Tupu:
        specs.append(formatvarkw(formatargandannotation(varkw)))
    result = '(' + ', '.join(specs) + ')'
    ikiwa 'rudisha' kwenye annotations:
        result += formatrudishas(formatannotation(annotations['rudisha']))
    rudisha result

eleza formatargvalues(args, varargs, varkw, locals,
                    formatarg=str,
                    formatvarargs=lambda name: '*' + name,
                    formatvarkw=lambda name: '**' + name,
                    formatvalue=lambda value: '=' + repr(value)):
    """Format an argument spec kutoka the 4 values rudishaed by getargvalues.

    The first four arguments are (args, varargs, varkw, locals).  The
    next four arguments are the corresponding optional formatting functions
    that are called to turn names na values into strings.  The ninth
    argument ni an optional function to format the sequence of arguments."""
    eleza convert(name, locals=locals,
                formatarg=formatarg, formatvalue=formatvalue):
        rudisha formatarg(name) + formatvalue(locals[name])
    specs = []
    kila i kwenye range(len(args)):
        specs.append(convert(args[i]))
    ikiwa varargs:
        specs.append(formatvarargs(varargs) + formatvalue(locals[varargs]))
    ikiwa varkw:
        specs.append(formatvarkw(varkw) + formatvalue(locals[varkw]))
    rudisha '(' + ', '.join(specs) + ')'

eleza _missing_arguments(f_name, argnames, pos, values):
    names = [repr(name) kila name kwenye argnames ikiwa name haiko kwenye values]
    missing = len(names)
    ikiwa missing == 1:
        s = names[0]
    lasivyo missing == 2:
        s = "{} na {}".format(*names)
    isipokua:
        tail = ", {} na {}".format(*names[-2:])
        toa names[-2:]
        s = ", ".join(names) + tail
    ashiria TypeError("%s() missing %i required %s argument%s: %s" %
                    (f_name, missing,
                      "positional" ikiwa pos isipokua "keyword-only",
                      "" ikiwa missing == 1 isipokua "s", s))

eleza _too_many(f_name, args, kwonly, varargs, defcount, given, values):
    atleast = len(args) - defcount
    kwonly_given = len([arg kila arg kwenye kwonly ikiwa arg kwenye values])
    ikiwa varargs:
        plural = atleast != 1
        sig = "at least %d" % (atleast,)
    lasivyo defcount:
        plural = Kweli
        sig = "kutoka %d to %d" % (atleast, len(args))
    isipokua:
        plural = len(args) != 1
        sig = str(len(args))
    kwonly_sig = ""
    ikiwa kwonly_given:
        msg = " positional argument%s (and %d keyword-only argument%s)"
        kwonly_sig = (msg % ("s" ikiwa given != 1 isipokua "", kwonly_given,
                             "s" ikiwa kwonly_given != 1 isipokua ""))
    ashiria TypeError("%s() takes %s positional argument%s but %d%s %s given" %
            (f_name, sig, "s" ikiwa plural isipokua "", given, kwonly_sig,
             "was" ikiwa given == 1 na sio kwonly_given isipokua "were"))

eleza getcallargs(func, /, *positional, **named):
    """Get the mapping of arguments to values.

    A dict ni rudishaed, ukijumuisha keys the function argument names (including the
    names of the * na ** arguments, ikiwa any), na values the respective bound
    values kutoka 'positional' na 'named'."""
    spec = getfullargspec(func)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = spec
    f_name = func.__name__
    arg2value = {}


    ikiwa ismethod(func) na func.__self__ ni sio Tupu:
        # implicit 'self' (or 'cls' kila classmethods) argument
        positional = (func.__self__,) + positional
    num_pos = len(positional)
    num_args = len(args)
    num_defaults = len(defaults) ikiwa defaults isipokua 0

    n = min(num_pos, num_args)
    kila i kwenye range(n):
        arg2value[args[i]] = positional[i]
    ikiwa varargs:
        arg2value[varargs] = tuple(positional[n:])
    possible_kwargs = set(args + kwonlyargs)
    ikiwa varkw:
        arg2value[varkw] = {}
    kila kw, value kwenye named.items():
        ikiwa kw haiko kwenye possible_kwargs:
            ikiwa sio varkw:
                ashiria TypeError("%s() got an unexpected keyword argument %r" %
                                (f_name, kw))
            arg2value[varkw][kw] = value
            endelea
        ikiwa kw kwenye arg2value:
            ashiria TypeError("%s() got multiple values kila argument %r" %
                            (f_name, kw))
        arg2value[kw] = value
    ikiwa num_pos > num_args na sio varargs:
        _too_many(f_name, args, kwonlyargs, varargs, num_defaults,
                   num_pos, arg2value)
    ikiwa num_pos < num_args:
        req = args[:num_args - num_defaults]
        kila arg kwenye req:
            ikiwa arg haiko kwenye arg2value:
                _missing_arguments(f_name, req, Kweli, arg2value)
        kila i, arg kwenye enumerate(args[num_args - num_defaults:]):
            ikiwa arg haiko kwenye arg2value:
                arg2value[arg] = defaults[i]
    missing = 0
    kila kwarg kwenye kwonlyargs:
        ikiwa kwarg haiko kwenye arg2value:
            ikiwa kwonlydefaults na kwarg kwenye kwonlydefaults:
                arg2value[kwarg] = kwonlydefaults[kwarg]
            isipokua:
                missing += 1
    ikiwa missing:
        _missing_arguments(f_name, kwonlyargs, Uongo, arg2value)
    rudisha arg2value

ClosureVars = namedtuple('ClosureVars', 'nonlocals globals builtins unbound')

eleza getclosurevars(func):
    """
    Get the mapping of free variables to their current values.

    Returns a named tuple of dicts mapping the current nonlocal, global
    na builtin references kama seen by the body of the function. A final
    set of unbound names that could sio be resolved ni also provided.
    """

    ikiwa ismethod(func):
        func = func.__func__

    ikiwa sio isfunction(func):
        ashiria TypeError("{!r} ni sio a Python function".format(func))

    code = func.__code__
    # Nonlocal references are named kwenye co_freevars na resolved
    # by looking them up kwenye __closure__ by positional index
    ikiwa func.__closure__ ni Tupu:
        nonlocal_vars = {}
    isipokua:
        nonlocal_vars = {
            var : cell.cell_contents
            kila var, cell kwenye zip(code.co_freevars, func.__closure__)
       }

    # Global na builtin references are named kwenye co_names na resolved
    # by looking them up kwenye __globals__ ama __builtins__
    global_ns = func.__globals__
    builtin_ns = global_ns.get("__builtins__", builtins.__dict__)
    ikiwa ismodule(builtin_ns):
        builtin_ns = builtin_ns.__dict__
    global_vars = {}
    builtin_vars = {}
    unbound_names = set()
    kila name kwenye code.co_names:
        ikiwa name kwenye ("Tupu", "Kweli", "Uongo"):
            # Because these used to be builtins instead of keywords, they
            # may still show up kama name references. We ignore them.
            endelea
        jaribu:
            global_vars[name] = global_ns[name]
        tatizo KeyError:
            jaribu:
                builtin_vars[name] = builtin_ns[name]
            tatizo KeyError:
                unbound_names.add(name)

    rudisha ClosureVars(nonlocal_vars, global_vars,
                       builtin_vars, unbound_names)

# -------------------------------------------------- stack frame extraction

Traceback = namedtuple('Traceback', 'filename lineno function code_context index')

eleza getframeinfo(frame, context=1):
    """Get information about a frame ama traceback object.

    A tuple of five things ni rudishaed: the filename, the line number of
    the current line, the function name, a list of lines of context kutoka
    the source code, na the index of the current line within that list.
    The optional second argument specifies the number of lines of context
    to rudisha, which are centered around the current line."""
    ikiwa istraceback(frame):
        lineno = frame.tb_lineno
        frame = frame.tb_frame
    isipokua:
        lineno = frame.f_lineno
    ikiwa sio isframe(frame):
        ashiria TypeError('{!r} ni sio a frame ama traceback object'.format(frame))

    filename = getsourcefile(frame) ama getfile(frame)
    ikiwa context > 0:
        start = lineno - 1 - context//2
        jaribu:
            lines, lnum = findsource(frame)
        tatizo OSError:
            lines = index = Tupu
        isipokua:
            start = max(0, min(start, len(lines) - context))
            lines = lines[start:start+context]
            index = lineno - 1 - start
    isipokua:
        lines = index = Tupu

    rudisha Traceback(filename, lineno, frame.f_code.co_name, lines, index)

eleza getlineno(frame):
    """Get the line number kutoka a frame object, allowing kila optimization."""
    # FrameType.f_lineno ni now a descriptor that grovels co_lnotab
    rudisha frame.f_lineno

FrameInfo = namedtuple('FrameInfo', ('frame',) + Traceback._fields)

eleza getouterframes(frame, context=1):
    """Get a list of records kila a frame na all higher (calling) frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, na index within the context."""
    framelist = []
    wakati frame:
        frameinfo = (frame,) + getframeinfo(frame, context)
        framelist.append(FrameInfo(*frameinfo))
        frame = frame.f_back
    rudisha framelist

eleza getinnerframes(tb, context=1):
    """Get a list of records kila a traceback's frame na all lower frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, na index within the context."""
    framelist = []
    wakati tb:
        frameinfo = (tb.tb_frame,) + getframeinfo(tb, context)
        framelist.append(FrameInfo(*frameinfo))
        tb = tb.tb_next
    rudisha framelist

eleza currentframe():
    """Return the frame of the caller ama Tupu ikiwa this ni sio possible."""
    rudisha sys._getframe(1) ikiwa hasattr(sys, "_getframe") isipokua Tupu

eleza stack(context=1):
    """Return a list of records kila the stack above the caller's frame."""
    rudisha getouterframes(sys._getframe(1), context)

eleza trace(context=1):
    """Return a list of records kila the stack below the current exception."""
    rudisha getinnerframes(sys.exc_info()[2], context)


# ------------------------------------------------ static version of getattr

_sentinel = object()

eleza _static_getmro(klass):
    rudisha type.__dict__['__mro__'].__get__(klass)

eleza _check_instance(obj, attr):
    instance_dict = {}
    jaribu:
        instance_dict = object.__getattribute__(obj, "__dict__")
    tatizo AttributeError:
        pita
    rudisha dict.get(instance_dict, attr, _sentinel)


eleza _check_class(klass, attr):
    kila entry kwenye _static_getmro(klass):
        ikiwa _shadowed_dict(type(entry)) ni _sentinel:
            jaribu:
                rudisha entry.__dict__[attr]
            tatizo KeyError:
                pita
    rudisha _sentinel

eleza _is_type(obj):
    jaribu:
        _static_getmro(obj)
    tatizo TypeError:
        rudisha Uongo
    rudisha Kweli

eleza _shadowed_dict(klass):
    dict_attr = type.__dict__["__dict__"]
    kila entry kwenye _static_getmro(klass):
        jaribu:
            class_dict = dict_attr.__get__(entry)["__dict__"]
        tatizo KeyError:
            pita
        isipokua:
            ikiwa sio (type(class_dict) ni types.GetSetDescriptorType and
                    class_dict.__name__ == "__dict__" and
                    class_dict.__objclass__ ni entry):
                rudisha class_dict
    rudisha _sentinel

eleza getattr_static(obj, attr, default=_sentinel):
    """Retrieve attributes without triggering dynamic lookup via the
       descriptor protocol,  __getattr__ ama __getattribute__.

       Note: this function may sio be able to retrieve all attributes
       that getattr can fetch (like dynamically created attributes)
       na may find attributes that getattr can't (like descriptors
       that ashiria AttributeError). It can also rudisha descriptor objects
       instead of instance members kwenye some cases. See the
       documentation kila details.
    """
    instance_result = _sentinel
    ikiwa sio _is_type(obj):
        klass = type(obj)
        dict_attr = _shadowed_dict(klass)
        ikiwa (dict_attr ni _sentinel or
            type(dict_attr) ni types.MemberDescriptorType):
            instance_result = _check_instance(obj, attr)
    isipokua:
        klass = obj

    klass_result = _check_class(klass, attr)

    ikiwa instance_result ni sio _sentinel na klass_result ni sio _sentinel:
        ikiwa (_check_class(type(klass_result), '__get__') ni sio _sentinel and
            _check_class(type(klass_result), '__set__') ni sio _sentinel):
            rudisha klass_result

    ikiwa instance_result ni sio _sentinel:
        rudisha instance_result
    ikiwa klass_result ni sio _sentinel:
        rudisha klass_result

    ikiwa obj ni klass:
        # kila types we check the metakundi too
        kila entry kwenye _static_getmro(type(klass)):
            ikiwa _shadowed_dict(type(entry)) ni _sentinel:
                jaribu:
                    rudisha entry.__dict__[attr]
                tatizo KeyError:
                    pita
    ikiwa default ni sio _sentinel:
        rudisha default
    ashiria AttributeError(attr)


# ------------------------------------------------ generator introspection

GEN_CREATED = 'GEN_CREATED'
GEN_RUNNING = 'GEN_RUNNING'
GEN_SUSPENDED = 'GEN_SUSPENDED'
GEN_CLOSED = 'GEN_CLOSED'

eleza getgeneratorstate(generator):
    """Get current state of a generator-iterator.

    Possible states are:
      GEN_CREATED: Waiting to start execution.
      GEN_RUNNING: Currently being executed by the interpreter.
      GEN_SUSPENDED: Currently suspended at a tuma expression.
      GEN_CLOSED: Execution has completed.
    """
    ikiwa generator.gi_running:
        rudisha GEN_RUNNING
    ikiwa generator.gi_frame ni Tupu:
        rudisha GEN_CLOSED
    ikiwa generator.gi_frame.f_lasti == -1:
        rudisha GEN_CREATED
    rudisha GEN_SUSPENDED


eleza getgeneratorlocals(generator):
    """
    Get the mapping of generator local variables to their current values.

    A dict ni rudishaed, ukijumuisha the keys the local variable names na values the
    bound values."""

    ikiwa sio isgenerator(generator):
        ashiria TypeError("{!r} ni sio a Python generator".format(generator))

    frame = getattr(generator, "gi_frame", Tupu)
    ikiwa frame ni sio Tupu:
        rudisha generator.gi_frame.f_locals
    isipokua:
        rudisha {}


# ------------------------------------------------ coroutine introspection

CORO_CREATED = 'CORO_CREATED'
CORO_RUNNING = 'CORO_RUNNING'
CORO_SUSPENDED = 'CORO_SUSPENDED'
CORO_CLOSED = 'CORO_CLOSED'

eleza getcoroutinestate(coroutine):
    """Get current state of a coroutine object.

    Possible states are:
      CORO_CREATED: Waiting to start execution.
      CORO_RUNNING: Currently being executed by the interpreter.
      CORO_SUSPENDED: Currently suspended at an await expression.
      CORO_CLOSED: Execution has completed.
    """
    ikiwa coroutine.cr_running:
        rudisha CORO_RUNNING
    ikiwa coroutine.cr_frame ni Tupu:
        rudisha CORO_CLOSED
    ikiwa coroutine.cr_frame.f_lasti == -1:
        rudisha CORO_CREATED
    rudisha CORO_SUSPENDED


eleza getcoroutinelocals(coroutine):
    """
    Get the mapping of coroutine local variables to their current values.

    A dict ni rudishaed, ukijumuisha the keys the local variable names na values the
    bound values."""
    frame = getattr(coroutine, "cr_frame", Tupu)
    ikiwa frame ni sio Tupu:
        rudisha frame.f_locals
    isipokua:
        rudisha {}


###############################################################################
### Function Signature Object (PEP 362)
###############################################################################


_WrapperDescriptor = type(type.__call__)
_MethodWrapper = type(all.__call__)
_ClassMethodWrapper = type(int.__dict__['kutoka_bytes'])

_NonUserDefinedCallables = (_WrapperDescriptor,
                            _MethodWrapper,
                            _ClassMethodWrapper,
                            types.BuiltinFunctionType)


eleza _signature_get_user_defined_method(cls, method_name):
    """Private helper. Checks ikiwa ``cls`` has an attribute
    named ``method_name`` na rudishas it only ikiwa it ni a
    pure python function.
    """
    jaribu:
        meth = getattr(cls, method_name)
    tatizo AttributeError:
        rudisha
    isipokua:
        ikiwa sio isinstance(meth, _NonUserDefinedCallables):
            # Once '__signature__' will be added to 'C'-level
            # callables, this check won't be necessary
            rudisha meth


eleza _signature_get_partial(wrapped_sig, partial, extra_args=()):
    """Private helper to calculate how 'wrapped_sig' signature will
    look like after applying a 'functools.partial' object (or alike)
    on it.
    """

    old_params = wrapped_sig.parameters
    new_params = OrderedDict(old_params.items())

    partial_args = partial.args ama ()
    partial_keywords = partial.keywords ama {}

    ikiwa extra_args:
        partial_args = extra_args + partial_args

    jaribu:
        ba = wrapped_sig.bind_partial(*partial_args, **partial_keywords)
    tatizo TypeError kama ex:
        msg = 'partial object {!r} has incorrect arguments'.format(partial)
        ashiria ValueError(msg) kutoka ex


    transform_to_kwonly = Uongo
    kila param_name, param kwenye old_params.items():
        jaribu:
            arg_value = ba.arguments[param_name]
        tatizo KeyError:
            pita
        isipokua:
            ikiwa param.kind ni _POSITIONAL_ONLY:
                # If positional-only parameter ni bound by partial,
                # it effectively disappears kutoka the signature
                new_params.pop(param_name)
                endelea

            ikiwa param.kind ni _POSITIONAL_OR_KEYWORD:
                ikiwa param_name kwenye partial_keywords:
                    # This means that this parameter, na all parameters
                    # after it should be keyword-only (and var-positional
                    # should be removed). Here's why. Consider the following
                    # function:
                    #     foo(a, b, *args, c):
                    #         pita
                    #
                    # "partial(foo, a='spam')" will have the following
                    # signature: "(*, a='spam', b, c)". Because attempting
                    # to call that partial ukijumuisha "(10, 20)" arguments will
                    # ashiria a TypeError, saying that "a" argument received
                    # multiple values.
                    transform_to_kwonly = Kweli
                    # Set the new default value
                    new_params[param_name] = param.replace(default=arg_value)
                isipokua:
                    # was pitaed kama a positional argument
                    new_params.pop(param.name)
                    endelea

            ikiwa param.kind ni _KEYWORD_ONLY:
                # Set the new default value
                new_params[param_name] = param.replace(default=arg_value)

        ikiwa transform_to_kwonly:
            assert param.kind ni sio _POSITIONAL_ONLY

            ikiwa param.kind ni _POSITIONAL_OR_KEYWORD:
                new_param = new_params[param_name].replace(kind=_KEYWORD_ONLY)
                new_params[param_name] = new_param
                new_params.move_to_end(param_name)
            lasivyo param.kind kwenye (_KEYWORD_ONLY, _VAR_KEYWORD):
                new_params.move_to_end(param_name)
            lasivyo param.kind ni _VAR_POSITIONAL:
                new_params.pop(param.name)

    rudisha wrapped_sig.replace(parameters=new_params.values())


eleza _signature_bound_method(sig):
    """Private helper to transform signatures kila unbound
    functions to bound methods.
    """

    params = tuple(sig.parameters.values())

    ikiwa sio params ama params[0].kind kwenye (_VAR_KEYWORD, _KEYWORD_ONLY):
        ashiria ValueError('invalid method signature')

    kind = params[0].kind
    ikiwa kind kwenye (_POSITIONAL_OR_KEYWORD, _POSITIONAL_ONLY):
        # Drop first parameter:
        # '(p1, p2[, ...])' -> '(p2[, ...])'
        params = params[1:]
    isipokua:
        ikiwa kind ni sio _VAR_POSITIONAL:
            # Unless we add a new parameter type we never
            # get here
            ashiria ValueError('invalid argument type')
        # It's a var-positional parameter.
        # Do nothing. '(*args[, ...])' -> '(*args[, ...])'

    rudisha sig.replace(parameters=params)


eleza _signature_is_builtin(obj):
    """Private helper to test ikiwa `obj` ni a callable that might
    support Argument Clinic's __text_signature__ protocol.
    """
    rudisha (isbuiltin(obj) or
            ismethoddescriptor(obj) or
            isinstance(obj, _NonUserDefinedCallables) or
            # Can't test 'isinstance(type)' here, kama it would
            # also be Kweli kila regular python classes
            obj kwenye (type, object))


eleza _signature_is_functionlike(obj):
    """Private helper to test ikiwa `obj` ni a duck type of FunctionType.
    A good example of such objects are functions compiled with
    Cython, which have all attributes that a pure Python function
    would have, but have their code statically compiled.
    """

    ikiwa sio callable(obj) ama isclass(obj):
        # All function-like objects are obviously callables,
        # na sio classes.
        rudisha Uongo

    name = getattr(obj, '__name__', Tupu)
    code = getattr(obj, '__code__', Tupu)
    defaults = getattr(obj, '__defaults__', _void) # Important to use _void ...
    kwdefaults = getattr(obj, '__kwdefaults__', _void) # ... na sio Tupu here
    annotations = getattr(obj, '__annotations__', Tupu)

    rudisha (isinstance(code, types.CodeType) and
            isinstance(name, str) and
            (defaults ni Tupu ama isinstance(defaults, tuple)) and
            (kwdefaults ni Tupu ama isinstance(kwdefaults, dict)) and
            isinstance(annotations, dict))


eleza _signature_get_bound_param(spec):
    """ Private helper to get first parameter name kutoka a
    __text_signature__ of a builtin method, which should
    be kwenye the following format: '($param1, ...)'.
    Assumptions are that the first argument won't have
    a default value ama an annotation.
    """

    assert spec.startswith('($')

    pos = spec.find(',')
    ikiwa pos == -1:
        pos = spec.find(')')

    cpos = spec.find(':')
    assert cpos == -1 ama cpos > pos

    cpos = spec.find('=')
    assert cpos == -1 ama cpos > pos

    rudisha spec[2:pos]


eleza _signature_strip_non_python_syntax(signature):
    """
    Private helper function. Takes a signature kwenye Argument Clinic's
    extended signature format.

    Returns a tuple of three things:
      * that signature re-rendered kwenye standard Python syntax,
      * the index of the "self" parameter (generally 0), ama Tupu if
        the function does sio have a "self" parameter, and
      * the index of the last "positional only" parameter,
        ama Tupu ikiwa the signature has no positional-only parameters.
    """

    ikiwa sio signature:
        rudisha signature, Tupu, Tupu

    self_parameter = Tupu
    last_positional_only = Tupu

    lines = [l.encode('ascii') kila l kwenye signature.split('\n')]
    generator = iter(lines).__next__
    token_stream = tokenize.tokenize(generator)

    delayed_comma = Uongo
    skip_next_comma = Uongo
    text = []
    add = text.append

    current_parameter = 0
    OP = token.OP
    ERRORTOKEN = token.ERRORTOKEN

    # token stream always starts ukijumuisha ENCODING token, skip it
    t = next(token_stream)
    assert t.type == tokenize.ENCODING

    kila t kwenye token_stream:
        type, string = t.type, t.string

        ikiwa type == OP:
            ikiwa string == ',':
                ikiwa skip_next_comma:
                    skip_next_comma = Uongo
                isipokua:
                    assert sio delayed_comma
                    delayed_comma = Kweli
                    current_parameter += 1
                endelea

            ikiwa string == '/':
                assert sio skip_next_comma
                assert last_positional_only ni Tupu
                skip_next_comma = Kweli
                last_positional_only = current_parameter - 1
                endelea

        ikiwa (type == ERRORTOKEN) na (string == '$'):
            assert self_parameter ni Tupu
            self_parameter = current_parameter
            endelea

        ikiwa delayed_comma:
            delayed_comma = Uongo
            ikiwa sio ((type == OP) na (string == ')')):
                add(', ')
        add(string)
        ikiwa (string == ','):
            add(' ')
    clean_signature = ''.join(text)
    rudisha clean_signature, self_parameter, last_positional_only


eleza _signature_kutokastr(cls, obj, s, skip_bound_arg=Kweli):
    """Private helper to parse content of '__text_signature__'
    na rudisha a Signature based on it.
    """
    # Lazy agiza ast because it's relatively heavy and
    # it's sio used kila other than this function.
    agiza ast

    Parameter = cls._parameter_cls

    clean_signature, self_parameter, last_positional_only = \
        _signature_strip_non_python_syntax(s)

    program = "eleza foo" + clean_signature + ": pita"

    jaribu:
        module = ast.parse(program)
    tatizo SyntaxError:
        module = Tupu

    ikiwa sio isinstance(module, ast.Module):
        ashiria ValueError("{!r} builtin has invalid signature".format(obj))

    f = module.body[0]

    parameters = []
    empty = Parameter.empty
    invalid = object()

    module = Tupu
    module_dict = {}
    module_name = getattr(obj, '__module__', Tupu)
    ikiwa module_name:
        module = sys.modules.get(module_name, Tupu)
        ikiwa module:
            module_dict = module.__dict__
    sys_module_dict = sys.modules.copy()

    eleza parse_name(node):
        assert isinstance(node, ast.arg)
        ikiwa node.annotation ni sio Tupu:
            ashiria ValueError("Annotations are sio currently supported")
        rudisha node.arg

    eleza wrap_value(s):
        jaribu:
            value = eval(s, module_dict)
        tatizo NameError:
            jaribu:
                value = eval(s, sys_module_dict)
            tatizo NameError:
                ashiria RuntimeError()

        ikiwa isinstance(value, (str, int, float, bytes, bool, type(Tupu))):
            rudisha ast.Constant(value)
        ashiria RuntimeError()

    kundi RewriteSymbolics(ast.NodeTransformer):
        eleza visit_Attribute(self, node):
            a = []
            n = node
            wakati isinstance(n, ast.Attribute):
                a.append(n.attr)
                n = n.value
            ikiwa sio isinstance(n, ast.Name):
                ashiria RuntimeError()
            a.append(n.id)
            value = ".".join(reversed(a))
            rudisha wrap_value(value)

        eleza visit_Name(self, node):
            ikiwa sio isinstance(node.ctx, ast.Load):
                ashiria ValueError()
            rudisha wrap_value(node.id)

    eleza p(name_node, default_node, default=empty):
        name = parse_name(name_node)
        ikiwa name ni invalid:
            rudisha Tupu
        ikiwa default_node na default_node ni sio _empty:
            jaribu:
                default_node = RewriteSymbolics().visit(default_node)
                o = ast.literal_eval(default_node)
            tatizo ValueError:
                o = invalid
            ikiwa o ni invalid:
                rudisha Tupu
            default = o ikiwa o ni sio invalid isipokua default
        parameters.append(Parameter(name, kind, default=default, annotation=empty))

    # non-keyword-only parameters
    args = reversed(f.args.args)
    defaults = reversed(f.args.defaults)
    iter = itertools.zip_longest(args, defaults, fillvalue=Tupu)
    ikiwa last_positional_only ni sio Tupu:
        kind = Parameter.POSITIONAL_ONLY
    isipokua:
        kind = Parameter.POSITIONAL_OR_KEYWORD
    kila i, (name, default) kwenye enumerate(reversed(list(iter))):
        p(name, default)
        ikiwa i == last_positional_only:
            kind = Parameter.POSITIONAL_OR_KEYWORD

    # *args
    ikiwa f.args.vararg:
        kind = Parameter.VAR_POSITIONAL
        p(f.args.vararg, empty)

    # keyword-only arguments
    kind = Parameter.KEYWORD_ONLY
    kila name, default kwenye zip(f.args.kwonlyargs, f.args.kw_defaults):
        p(name, default)

    # **kwargs
    ikiwa f.args.kwarg:
        kind = Parameter.VAR_KEYWORD
        p(f.args.kwarg, empty)

    ikiwa self_parameter ni sio Tupu:
        # Possibly strip the bound argument:
        #    - We *always* strip first bound argument if
        #      it ni a module.
        #    - We don't strip first bound argument if
        #      skip_bound_arg ni Uongo.
        assert parameters
        _self = getattr(obj, '__self__', Tupu)
        self_isbound = _self ni sio Tupu
        self_ismodule = ismodule(_self)
        ikiwa self_isbound na (self_ismodule ama skip_bound_arg):
            parameters.pop(0)
        isipokua:
            # kila builtins, self parameter ni always positional-only!
            p = parameters[0].replace(kind=Parameter.POSITIONAL_ONLY)
            parameters[0] = p

    rudisha cls(parameters, rudisha_annotation=cls.empty)


eleza _signature_kutoka_builtin(cls, func, skip_bound_arg=Kweli):
    """Private helper function to get signature for
    builtin callables.
    """

    ikiwa sio _signature_is_builtin(func):
        ashiria TypeError("{!r} ni sio a Python builtin "
                        "function".format(func))

    s = getattr(func, "__text_signature__", Tupu)
    ikiwa sio s:
        ashiria ValueError("no signature found kila builtin {!r}".format(func))

    rudisha _signature_kutokastr(cls, func, s, skip_bound_arg)


eleza _signature_kutoka_function(cls, func, skip_bound_arg=Kweli):
    """Private helper: constructs Signature kila the given python function."""

    is_duck_function = Uongo
    ikiwa sio isfunction(func):
        ikiwa _signature_is_functionlike(func):
            is_duck_function = Kweli
        isipokua:
            # If it's sio a pure Python function, na sio a duck type
            # of pure function:
            ashiria TypeError('{!r} ni sio a Python function'.format(func))

    s = getattr(func, "__text_signature__", Tupu)
    ikiwa s:
        rudisha _signature_kutokastr(cls, func, s, skip_bound_arg)

    Parameter = cls._parameter_cls

    # Parameter information.
    func_code = func.__code__
    pos_count = func_code.co_argcount
    arg_names = func_code.co_varnames
    posonly_count = func_code.co_posonlyargcount
    positional = arg_names[:pos_count]
    keyword_only_count = func_code.co_kwonlyargcount
    keyword_only = arg_names[pos_count:pos_count + keyword_only_count]
    annotations = func.__annotations__
    defaults = func.__defaults__
    kwdefaults = func.__kwdefaults__

    ikiwa defaults:
        pos_default_count = len(defaults)
    isipokua:
        pos_default_count = 0

    parameters = []

    non_default_count = pos_count - pos_default_count
    posonly_left = posonly_count

    # Non-keyword-only parameters w/o defaults.
    kila name kwenye positional[:non_default_count]:
        kind = _POSITIONAL_ONLY ikiwa posonly_left isipokua _POSITIONAL_OR_KEYWORD
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=kind))
        ikiwa posonly_left:
            posonly_left -= 1

    # ... w/ defaults.
    kila offset, name kwenye enumerate(positional[non_default_count:]):
        kind = _POSITIONAL_ONLY ikiwa posonly_left isipokua _POSITIONAL_OR_KEYWORD
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=kind,
                                    default=defaults[offset]))
        ikiwa posonly_left:
            posonly_left -= 1

    # *args
    ikiwa func_code.co_flags & CO_VARARGS:
        name = arg_names[pos_count + keyword_only_count]
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_VAR_POSITIONAL))

    # Keyword-only parameters.
    kila name kwenye keyword_only:
        default = _empty
        ikiwa kwdefaults ni sio Tupu:
            default = kwdefaults.get(name, _empty)

        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_KEYWORD_ONLY,
                                    default=default))
    # **kwargs
    ikiwa func_code.co_flags & CO_VARKEYWORDS:
        index = pos_count + keyword_only_count
        ikiwa func_code.co_flags & CO_VARARGS:
            index += 1

        name = arg_names[index]
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_VAR_KEYWORD))

    # Is 'func' ni a pure Python function - don't validate the
    # parameters list (kila correct order na defaults), it should be OK.
    rudisha cls(parameters,
               rudisha_annotation=annotations.get('rudisha', _empty),
               __validate_parameters__=is_duck_function)


eleza _signature_kutoka_callable(obj, *,
                             follow_wrapper_chains=Kweli,
                             skip_bound_arg=Kweli,
                             sigcls):

    """Private helper function to get signature kila arbitrary
    callable objects.
    """

    ikiwa sio callable(obj):
        ashiria TypeError('{!r} ni sio a callable object'.format(obj))

    ikiwa isinstance(obj, types.MethodType):
        # In this case we skip the first parameter of the underlying
        # function (usually `self` ama `cls`).
        sig = _signature_kutoka_callable(
            obj.__func__,
            follow_wrapper_chains=follow_wrapper_chains,
            skip_bound_arg=skip_bound_arg,
            sigcls=sigcls)

        ikiwa skip_bound_arg:
            rudisha _signature_bound_method(sig)
        isipokua:
            rudisha sig

    # Was this function wrapped by a decorator?
    ikiwa follow_wrapper_chains:
        obj = unwrap(obj, stop=(lambda f: hasattr(f, "__signature__")))
        ikiwa isinstance(obj, types.MethodType):
            # If the unwrapped object ni a *method*, we might want to
            # skip its first parameter (self).
            # See test_signature_wrapped_bound_method kila details.
            rudisha _signature_kutoka_callable(
                obj,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)

    jaribu:
        sig = obj.__signature__
    tatizo AttributeError:
        pita
    isipokua:
        ikiwa sig ni sio Tupu:
            ikiwa sio isinstance(sig, Signature):
                ashiria TypeError(
                    'unexpected object {!r} kwenye __signature__ '
                    'attribute'.format(sig))
            rudisha sig

    jaribu:
        partialmethod = obj._partialmethod
    tatizo AttributeError:
        pita
    isipokua:
        ikiwa isinstance(partialmethod, functools.partialmethod):
            # Unbound partialmethod (see functools.partialmethod)
            # This means, that we need to calculate the signature
            # kama ikiwa it's a regular partial object, but taking into
            # account that the first positional argument
            # (usually `self`, ama `cls`) will sio be pitaed
            # automatically (as kila boundmethods)

            wrapped_sig = _signature_kutoka_callable(
                partialmethod.func,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)

            sig = _signature_get_partial(wrapped_sig, partialmethod, (Tupu,))
            first_wrapped_param = tuple(wrapped_sig.parameters.values())[0]
            ikiwa first_wrapped_param.kind ni Parameter.VAR_POSITIONAL:
                # First argument of the wrapped callable ni `*args`, kama in
                # `partialmethod(lambda *args)`.
                rudisha sig
            isipokua:
                sig_params = tuple(sig.parameters.values())
                assert (not sig_params or
                        first_wrapped_param ni sio sig_params[0])
                new_params = (first_wrapped_param,) + sig_params
                rudisha sig.replace(parameters=new_params)

    ikiwa isfunction(obj) ama _signature_is_functionlike(obj):
        # If it's a pure Python function, ama an object that ni duck type
        # of a Python function (Cython functions, kila instance), then:
        rudisha _signature_kutoka_function(sigcls, obj,
                                        skip_bound_arg=skip_bound_arg)

    ikiwa _signature_is_builtin(obj):
        rudisha _signature_kutoka_builtin(sigcls, obj,
                                       skip_bound_arg=skip_bound_arg)

    ikiwa isinstance(obj, functools.partial):
        wrapped_sig = _signature_kutoka_callable(
            obj.func,
            follow_wrapper_chains=follow_wrapper_chains,
            skip_bound_arg=skip_bound_arg,
            sigcls=sigcls)
        rudisha _signature_get_partial(wrapped_sig, obj)

    sig = Tupu
    ikiwa isinstance(obj, type):
        # obj ni a kundi ama a metaclass

        # First, let's see ikiwa it has an overloaded __call__ defined
        # kwenye its metaclass
        call = _signature_get_user_defined_method(type(obj), '__call__')
        ikiwa call ni sio Tupu:
            sig = _signature_kutoka_callable(
                call,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)
        isipokua:
            # Now we check ikiwa the 'obj' kundi has a '__new__' method
            new = _signature_get_user_defined_method(obj, '__new__')
            ikiwa new ni sio Tupu:
                sig = _signature_kutoka_callable(
                    new,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls)
            isipokua:
                # Finally, we should have at least __init__ implemented
                init = _signature_get_user_defined_method(obj, '__init__')
                ikiwa init ni sio Tupu:
                    sig = _signature_kutoka_callable(
                        init,
                        follow_wrapper_chains=follow_wrapper_chains,
                        skip_bound_arg=skip_bound_arg,
                        sigcls=sigcls)

        ikiwa sig ni Tupu:
            # At this point we know, that `obj` ni a class, ukijumuisha no user-
            # defined '__init__', '__new__', ama class-level '__call__'

            kila base kwenye obj.__mro__[:-1]:
                # Since '__text_signature__' ni implemented kama a
                # descriptor that extracts text signature kutoka the
                # kundi docstring, ikiwa 'obj' ni derived kutoka a builtin
                # class, its own '__text_signature__' may be 'Tupu'.
                # Therefore, we go through the MRO (tatizo the last
                # kundi kwenye there, which ni 'object') to find the first
                # kundi ukijumuisha non-empty text signature.
                jaribu:
                    text_sig = base.__text_signature__
                tatizo AttributeError:
                    pita
                isipokua:
                    ikiwa text_sig:
                        # If 'obj' kundi has a __text_signature__ attribute:
                        # rudisha a signature based on it
                        rudisha _signature_kutokastr(sigcls, obj, text_sig)

            # No '__text_signature__' was found kila the 'obj' class.
            # Last option ni to check ikiwa its '__init__' is
            # object.__init__ ama type.__init__.
            ikiwa type haiko kwenye obj.__mro__:
                # We have a kundi (not metaclass), but no user-defined
                # __init__ ama __new__ kila it
                ikiwa (obj.__init__ ni object.__init__ and
                    obj.__new__ ni object.__new__):
                    # Return a signature of 'object' builtin.
                    rudisha sigcls.kutoka_callable(object)
                isipokua:
                    ashiria ValueError(
                        'no signature found kila builtin type {!r}'.format(obj))

    lasivyo sio isinstance(obj, _NonUserDefinedCallables):
        # An object ukijumuisha __call__
        # We also check that the 'obj' ni sio an instance of
        # _WrapperDescriptor ama _MethodWrapper to avoid
        # infinite recursion (and even potential segfault)
        call = _signature_get_user_defined_method(type(obj), '__call__')
        ikiwa call ni sio Tupu:
            jaribu:
                sig = _signature_kutoka_callable(
                    call,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls)
            tatizo ValueError kama ex:
                msg = 'no signature found kila {!r}'.format(obj)
                ashiria ValueError(msg) kutoka ex

    ikiwa sig ni sio Tupu:
        # For classes na objects we skip the first parameter of their
        # __call__, __new__, ama __init__ methods
        ikiwa skip_bound_arg:
            rudisha _signature_bound_method(sig)
        isipokua:
            rudisha sig

    ikiwa isinstance(obj, types.BuiltinFunctionType):
        # Raise a nicer error message kila builtins
        msg = 'no signature found kila builtin function {!r}'.format(obj)
        ashiria ValueError(msg)

    ashiria ValueError('callable {!r} ni sio supported by signature'.format(obj))


kundi _void:
    """A private marker - used kwenye Parameter & Signature."""


kundi _empty:
    """Marker object kila Signature.empty na Parameter.empty."""


kundi _ParameterKind(enum.IntEnum):
    POSITIONAL_ONLY = 0
    POSITIONAL_OR_KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4

    eleza __str__(self):
        rudisha self._name_

    @property
    eleza description(self):
        rudisha _PARAM_NAME_MAPPING[self]

_POSITIONAL_ONLY         = _ParameterKind.POSITIONAL_ONLY
_POSITIONAL_OR_KEYWORD   = _ParameterKind.POSITIONAL_OR_KEYWORD
_VAR_POSITIONAL          = _ParameterKind.VAR_POSITIONAL
_KEYWORD_ONLY            = _ParameterKind.KEYWORD_ONLY
_VAR_KEYWORD             = _ParameterKind.VAR_KEYWORD

_PARAM_NAME_MAPPING = {
    _POSITIONAL_ONLY: 'positional-only',
    _POSITIONAL_OR_KEYWORD: 'positional ama keyword',
    _VAR_POSITIONAL: 'variadic positional',
    _KEYWORD_ONLY: 'keyword-only',
    _VAR_KEYWORD: 'variadic keyword'
}


kundi Parameter:
    """Represents a parameter kwenye a function signature.

    Has the following public attributes:

    * name : str
        The name of the parameter kama a string.
    * default : object
        The default value kila the parameter ikiwa specified.  If the
        parameter has no default value, this attribute ni set to
        `Parameter.empty`.
    * annotation
        The annotation kila the parameter ikiwa specified.  If the
        parameter has no annotation, this attribute ni set to
        `Parameter.empty`.
    * kind : str
        Describes how argument values are bound to the parameter.
        Possible values: `Parameter.POSITIONAL_ONLY`,
        `Parameter.POSITIONAL_OR_KEYWORD`, `Parameter.VAR_POSITIONAL`,
        `Parameter.KEYWORD_ONLY`, `Parameter.VAR_KEYWORD`.
    """

    __slots__ = ('_name', '_kind', '_default', '_annotation')

    POSITIONAL_ONLY         = _POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD   = _POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL          = _VAR_POSITIONAL
    KEYWORD_ONLY            = _KEYWORD_ONLY
    VAR_KEYWORD             = _VAR_KEYWORD

    empty = _empty

    eleza __init__(self, name, kind, *, default=_empty, annotation=_empty):
        jaribu:
            self._kind = _ParameterKind(kind)
        tatizo ValueError:
            ashiria ValueError(f'value {kind!r} ni sio a valid Parameter.kind')
        ikiwa default ni sio _empty:
            ikiwa self._kind kwenye (_VAR_POSITIONAL, _VAR_KEYWORD):
                msg = '{} parameters cannot have default values'
                msg = msg.format(self._kind.description)
                ashiria ValueError(msg)
        self._default = default
        self._annotation = annotation

        ikiwa name ni _empty:
            ashiria ValueError('name ni a required attribute kila Parameter')

        ikiwa sio isinstance(name, str):
            msg = 'name must be a str, sio a {}'.format(type(name).__name__)
            ashiria TypeError(msg)

        ikiwa name[0] == '.' na name[1:].isdigit():
            # These are implicit arguments generated by comprehensions. In
            # order to provide a friendlier interface to users, we recast
            # their name kama "implicitN" na treat them kama positional-only.
            # See issue 19611.
            ikiwa self._kind != _POSITIONAL_OR_KEYWORD:
                msg = (
                    'implicit arguments must be pitaed kama '
                    'positional ama keyword arguments, sio {}'
                )
                msg = msg.format(self._kind.description)
                ashiria ValueError(msg)
            self._kind = _POSITIONAL_ONLY
            name = 'implicit{}'.format(name[1:])

        ikiwa sio name.isidentifier():
            ashiria ValueError('{!r} ni sio a valid parameter name'.format(name))

        self._name = name

    eleza __reduce__(self):
        rudisha (type(self),
                (self._name, self._kind),
                {'_default': self._default,
                 '_annotation': self._annotation})

    eleza __setstate__(self, state):
        self._default = state['_default']
        self._annotation = state['_annotation']

    @property
    eleza name(self):
        rudisha self._name

    @property
    eleza default(self):
        rudisha self._default

    @property
    eleza annotation(self):
        rudisha self._annotation

    @property
    eleza kind(self):
        rudisha self._kind

    eleza replace(self, *, name=_void, kind=_void,
                annotation=_void, default=_void):
        """Creates a customized copy of the Parameter."""

        ikiwa name ni _void:
            name = self._name

        ikiwa kind ni _void:
            kind = self._kind

        ikiwa annotation ni _void:
            annotation = self._annotation

        ikiwa default ni _void:
            default = self._default

        rudisha type(self)(name, kind, default=default, annotation=annotation)

    eleza __str__(self):
        kind = self.kind
        formatted = self._name

        # Add annotation na default value
        ikiwa self._annotation ni sio _empty:
            formatted = '{}: {}'.format(formatted,
                                       formatannotation(self._annotation))

        ikiwa self._default ni sio _empty:
            ikiwa self._annotation ni sio _empty:
                formatted = '{} = {}'.format(formatted, repr(self._default))
            isipokua:
                formatted = '{}={}'.format(formatted, repr(self._default))

        ikiwa kind == _VAR_POSITIONAL:
            formatted = '*' + formatted
        lasivyo kind == _VAR_KEYWORD:
            formatted = '**' + formatted

        rudisha formatted

    eleza __repr__(self):
        rudisha '<{} "{}">'.format(self.__class__.__name__, self)

    eleza __hash__(self):
        rudisha hash((self.name, self.kind, self.annotation, self.default))

    eleza __eq__(self, other):
        ikiwa self ni other:
            rudisha Kweli
        ikiwa sio isinstance(other, Parameter):
            rudisha NotImplemented
        rudisha (self._name == other._name and
                self._kind == other._kind and
                self._default == other._default and
                self._annotation == other._annotation)


kundi BoundArguments:
    """Result of `Signature.bind` call.  Holds the mapping of arguments
    to the function's parameters.

    Has the following public attributes:

    * arguments : OrderedDict
        An ordered mutable mapping of parameters' names to arguments' values.
        Does sio contain arguments' default values.
    * signature : Signature
        The Signature object that created this instance.
    * args : tuple
        Tuple of positional arguments values.
    * kwargs : dict
        Dict of keyword arguments values.
    """

    __slots__ = ('arguments', '_signature', '__weakref__')

    eleza __init__(self, signature, arguments):
        self.arguments = arguments
        self._signature = signature

    @property
    eleza signature(self):
        rudisha self._signature

    @property
    eleza args(self):
        args = []
        kila param_name, param kwenye self._signature.parameters.items():
            ikiwa param.kind kwenye (_VAR_KEYWORD, _KEYWORD_ONLY):
                koma

            jaribu:
                arg = self.arguments[param_name]
            tatizo KeyError:
                # We're done here. Other arguments
                # will be mapped kwenye 'BoundArguments.kwargs'
                koma
            isipokua:
                ikiwa param.kind == _VAR_POSITIONAL:
                    # *args
                    args.extend(arg)
                isipokua:
                    # plain argument
                    args.append(arg)

        rudisha tuple(args)

    @property
    eleza kwargs(self):
        kwargs = {}
        kwargs_started = Uongo
        kila param_name, param kwenye self._signature.parameters.items():
            ikiwa sio kwargs_started:
                ikiwa param.kind kwenye (_VAR_KEYWORD, _KEYWORD_ONLY):
                    kwargs_started = Kweli
                isipokua:
                    ikiwa param_name haiko kwenye self.arguments:
                        kwargs_started = Kweli
                        endelea

            ikiwa sio kwargs_started:
                endelea

            jaribu:
                arg = self.arguments[param_name]
            tatizo KeyError:
                pita
            isipokua:
                ikiwa param.kind == _VAR_KEYWORD:
                    # **kwargs
                    kwargs.update(arg)
                isipokua:
                    # plain keyword argument
                    kwargs[param_name] = arg

        rudisha kwargs

    eleza apply_defaults(self):
        """Set default values kila missing arguments.

        For variable-positional arguments (*args) the default ni an
        empty tuple.

        For variable-keyword arguments (**kwargs) the default ni an
        empty dict.
        """
        arguments = self.arguments
        new_arguments = []
        kila name, param kwenye self._signature.parameters.items():
            jaribu:
                new_arguments.append((name, arguments[name]))
            tatizo KeyError:
                ikiwa param.default ni sio _empty:
                    val = param.default
                lasivyo param.kind ni _VAR_POSITIONAL:
                    val = ()
                lasivyo param.kind ni _VAR_KEYWORD:
                    val = {}
                isipokua:
                    # This BoundArguments was likely produced by
                    # Signature.bind_partial().
                    endelea
                new_arguments.append((name, val))
        self.arguments = OrderedDict(new_arguments)

    eleza __eq__(self, other):
        ikiwa self ni other:
            rudisha Kweli
        ikiwa sio isinstance(other, BoundArguments):
            rudisha NotImplemented
        rudisha (self.signature == other.signature and
                self.arguments == other.arguments)

    eleza __setstate__(self, state):
        self._signature = state['_signature']
        self.arguments = state['arguments']

    eleza __getstate__(self):
        rudisha {'_signature': self._signature, 'arguments': self.arguments}

    eleza __repr__(self):
        args = []
        kila arg, value kwenye self.arguments.items():
            args.append('{}={!r}'.format(arg, value))
        rudisha '<{} ({})>'.format(self.__class__.__name__, ', '.join(args))


kundi Signature:
    """A Signature object represents the overall signature of a function.
    It stores a Parameter object kila each parameter accepted by the
    function, kama well kama information specific to the function itself.

    A Signature object has the following public attributes na methods:

    * parameters : OrderedDict
        An ordered mapping of parameters' names to the corresponding
        Parameter objects (keyword-only arguments are kwenye the same order
        kama listed kwenye `code.co_varnames`).
    * rudisha_annotation : object
        The annotation kila the rudisha type of the function ikiwa specified.
        If the function has no annotation kila its rudisha type, this
        attribute ni set to `Signature.empty`.
    * bind(*args, **kwargs) -> BoundArguments
        Creates a mapping kutoka positional na keyword arguments to
        parameters.
    * bind_partial(*args, **kwargs) -> BoundArguments
        Creates a partial mapping kutoka positional na keyword arguments
        to parameters (simulating 'functools.partial' behavior.)
    """

    __slots__ = ('_rudisha_annotation', '_parameters')

    _parameter_cls = Parameter
    _bound_arguments_cls = BoundArguments

    empty = _empty

    eleza __init__(self, parameters=Tupu, *, rudisha_annotation=_empty,
                 __validate_parameters__=Kweli):
        """Constructs Signature kutoka the given list of Parameter
        objects na 'rudisha_annotation'.  All arguments are optional.
        """

        ikiwa parameters ni Tupu:
            params = OrderedDict()
        isipokua:
            ikiwa __validate_parameters__:
                params = OrderedDict()
                top_kind = _POSITIONAL_ONLY
                kind_defaults = Uongo

                kila idx, param kwenye enumerate(parameters):
                    kind = param.kind
                    name = param.name

                    ikiwa kind < top_kind:
                        msg = (
                            'wrong parameter order: {} parameter before {} '
                            'parameter'
                        )
                        msg = msg.format(top_kind.description,
                                         kind.description)
                        ashiria ValueError(msg)
                    lasivyo kind > top_kind:
                        kind_defaults = Uongo
                        top_kind = kind

                    ikiwa kind kwenye (_POSITIONAL_ONLY, _POSITIONAL_OR_KEYWORD):
                        ikiwa param.default ni _empty:
                            ikiwa kind_defaults:
                                # No default kila this parameter, but the
                                # previous parameter of the same kind had
                                # a default
                                msg = 'non-default argument follows default ' \
                                      'argument'
                                ashiria ValueError(msg)
                        isipokua:
                            # There ni a default kila this parameter.
                            kind_defaults = Kweli

                    ikiwa name kwenye params:
                        msg = 'duplicate parameter name: {!r}'.format(name)
                        ashiria ValueError(msg)

                    params[name] = param
            isipokua:
                params = OrderedDict(((param.name, param)
                                                kila param kwenye parameters))

        self._parameters = types.MappingProxyType(params)
        self._rudisha_annotation = rudisha_annotation

    @classmethod
    eleza kutoka_function(cls, func):
        """Constructs Signature kila the given python function.

        Deprecated since Python 3.5, use `Signature.kutoka_callable()`.
        """

        warnings.warn("inspect.Signature.kutoka_function() ni deprecated since "
                      "Python 3.5, use Signature.kutoka_callable()",
                      DeprecationWarning, stacklevel=2)
        rudisha _signature_kutoka_function(cls, func)

    @classmethod
    eleza kutoka_builtin(cls, func):
        """Constructs Signature kila the given builtin function.

        Deprecated since Python 3.5, use `Signature.kutoka_callable()`.
        """

        warnings.warn("inspect.Signature.kutoka_builtin() ni deprecated since "
                      "Python 3.5, use Signature.kutoka_callable()",
                      DeprecationWarning, stacklevel=2)
        rudisha _signature_kutoka_builtin(cls, func)

    @classmethod
    eleza kutoka_callable(cls, obj, *, follow_wrapped=Kweli):
        """Constructs Signature kila the given callable object."""
        rudisha _signature_kutoka_callable(obj, sigcls=cls,
                                        follow_wrapper_chains=follow_wrapped)

    @property
    eleza parameters(self):
        rudisha self._parameters

    @property
    eleza rudisha_annotation(self):
        rudisha self._rudisha_annotation

    eleza replace(self, *, parameters=_void, rudisha_annotation=_void):
        """Creates a customized copy of the Signature.
        Pass 'parameters' and/or 'rudisha_annotation' arguments
        to override them kwenye the new copy.
        """

        ikiwa parameters ni _void:
            parameters = self.parameters.values()

        ikiwa rudisha_annotation ni _void:
            rudisha_annotation = self._rudisha_annotation

        rudisha type(self)(parameters,
                          rudisha_annotation=rudisha_annotation)

    eleza _hash_basis(self):
        params = tuple(param kila param kwenye self.parameters.values()
                             ikiwa param.kind != _KEYWORD_ONLY)

        kwo_params = {param.name: param kila param kwenye self.parameters.values()
                                        ikiwa param.kind == _KEYWORD_ONLY}

        rudisha params, kwo_params, self.rudisha_annotation

    eleza __hash__(self):
        params, kwo_params, rudisha_annotation = self._hash_basis()
        kwo_params = frozenset(kwo_params.values())
        rudisha hash((params, kwo_params, rudisha_annotation))

    eleza __eq__(self, other):
        ikiwa self ni other:
            rudisha Kweli
        ikiwa sio isinstance(other, Signature):
            rudisha NotImplemented
        rudisha self._hash_basis() == other._hash_basis()

    eleza _bind(self, args, kwargs, *, partial=Uongo):
        """Private method. Don't use directly."""

        arguments = OrderedDict()

        parameters = iter(self.parameters.values())
        parameters_ex = ()
        arg_vals = iter(args)

        wakati Kweli:
            # Let's iterate through the positional arguments na corresponding
            # parameters
            jaribu:
                arg_val = next(arg_vals)
            tatizo StopIteration:
                # No more positional arguments
                jaribu:
                    param = next(parameters)
                tatizo StopIteration:
                    # No more parameters. That's it. Just need to check that
                    # we have no `kwargs` after this wakati loop
                    koma
                isipokua:
                    ikiwa param.kind == _VAR_POSITIONAL:
                        # That's OK, just empty *args.  Let's start parsing
                        # kwargs
                        koma
                    lasivyo param.name kwenye kwargs:
                        ikiwa param.kind == _POSITIONAL_ONLY:
                            msg = '{arg!r} parameter ni positional only, ' \
                                  'but was pitaed kama a keyword'
                            msg = msg.format(arg=param.name)
                            ashiria TypeError(msg) kutoka Tupu
                        parameters_ex = (param,)
                        koma
                    lasivyo (param.kind == _VAR_KEYWORD or
                                                param.default ni sio _empty):
                        # That's fine too - we have a default value kila this
                        # parameter.  So, lets start parsing `kwargs`, starting
                        # ukijumuisha the current parameter
                        parameters_ex = (param,)
                        koma
                    isipokua:
                        # No default, sio VAR_KEYWORD, sio VAR_POSITIONAL,
                        # haiko kwenye `kwargs`
                        ikiwa partial:
                            parameters_ex = (param,)
                            koma
                        isipokua:
                            msg = 'missing a required argument: {arg!r}'
                            msg = msg.format(arg=param.name)
                            ashiria TypeError(msg) kutoka Tupu
            isipokua:
                # We have a positional argument to process
                jaribu:
                    param = next(parameters)
                tatizo StopIteration:
                    ashiria TypeError('too many positional arguments') kutoka Tupu
                isipokua:
                    ikiwa param.kind kwenye (_VAR_KEYWORD, _KEYWORD_ONLY):
                        # Looks like we have no parameter kila this positional
                        # argument
                        ashiria TypeError(
                            'too many positional arguments') kutoka Tupu

                    ikiwa param.kind == _VAR_POSITIONAL:
                        # We have an '*args'-like argument, let's fill it with
                        # all positional arguments we have left na move on to
                        # the next phase
                        values = [arg_val]
                        values.extend(arg_vals)
                        arguments[param.name] = tuple(values)
                        koma

                    ikiwa param.name kwenye kwargs:
                        ashiria TypeError(
                            'multiple values kila argument {arg!r}'.format(
                                arg=param.name)) kutoka Tupu

                    arguments[param.name] = arg_val

        # Now, we iterate through the remaining parameters to process
        # keyword arguments
        kwargs_param = Tupu
        kila param kwenye itertools.chain(parameters_ex, parameters):
            ikiwa param.kind == _VAR_KEYWORD:
                # Memorize that we have a '**kwargs'-like parameter
                kwargs_param = param
                endelea

            ikiwa param.kind == _VAR_POSITIONAL:
                # Named arguments don't refer to '*args'-like parameters.
                # We only arrive here ikiwa the positional arguments ended
                # before reaching the last parameter before *args.
                endelea

            param_name = param.name
            jaribu:
                arg_val = kwargs.pop(param_name)
            tatizo KeyError:
                # We have no value kila this parameter.  It's fine though,
                # ikiwa it has a default value, ama it ni an '*args'-like
                # parameter, left alone by the processing of positional
                # arguments.
                ikiwa (not partial na param.kind != _VAR_POSITIONAL and
                                                    param.default ni _empty):
                    ashiria TypeError('missing a required argument: {arg!r}'. \
                                    format(arg=param_name)) kutoka Tupu

            isipokua:
                ikiwa param.kind == _POSITIONAL_ONLY:
                    # This should never happen kwenye case of a properly built
                    # Signature object (but let's have this check here
                    # to ensure correct behaviour just kwenye case)
                    ashiria TypeError('{arg!r} parameter ni positional only, '
                                    'but was pitaed kama a keyword'. \
                                    format(arg=param.name))

                arguments[param_name] = arg_val

        ikiwa kwargs:
            ikiwa kwargs_param ni sio Tupu:
                # Process our '**kwargs'-like parameter
                arguments[kwargs_param.name] = kwargs
            isipokua:
                ashiria TypeError(
                    'got an unexpected keyword argument {arg!r}'.format(
                        arg=next(iter(kwargs))))

        rudisha self._bound_arguments_cls(self, arguments)

    eleza bind(self, /, *args, **kwargs):
        """Get a BoundArguments object, that maps the pitaed `args`
        na `kwargs` to the function's signature.  Raises `TypeError`
        ikiwa the pitaed arguments can sio be bound.
        """
        rudisha self._bind(args, kwargs)

    eleza bind_partial(self, /, *args, **kwargs):
        """Get a BoundArguments object, that partially maps the
        pitaed `args` na `kwargs` to the function's signature.
        Raises `TypeError` ikiwa the pitaed arguments can sio be bound.
        """
        rudisha self._bind(args, kwargs, partial=Kweli)

    eleza __reduce__(self):
        rudisha (type(self),
                (tuple(self._parameters.values()),),
                {'_rudisha_annotation': self._rudisha_annotation})

    eleza __setstate__(self, state):
        self._rudisha_annotation = state['_rudisha_annotation']

    eleza __repr__(self):
        rudisha '<{} {}>'.format(self.__class__.__name__, self)

    eleza __str__(self):
        result = []
        render_pos_only_separator = Uongo
        render_kw_only_separator = Kweli
        kila param kwenye self.parameters.values():
            formatted = str(param)

            kind = param.kind

            ikiwa kind == _POSITIONAL_ONLY:
                render_pos_only_separator = Kweli
            lasivyo render_pos_only_separator:
                # It's sio a positional-only parameter, na the flag
                # ni set to 'Kweli' (there were pos-only params before.)
                result.append('/')
                render_pos_only_separator = Uongo

            ikiwa kind == _VAR_POSITIONAL:
                # OK, we have an '*args'-like parameter, so we won't need
                # a '*' to separate keyword-only arguments
                render_kw_only_separator = Uongo
            lasivyo kind == _KEYWORD_ONLY na render_kw_only_separator:
                # We have a keyword-only parameter to render na we haven't
                # rendered an '*args'-like parameter before, so add a '*'
                # separator to the parameters list ("foo(arg1, *, arg2)" case)
                result.append('*')
                # This condition should be only triggered once, so
                # reset the flag
                render_kw_only_separator = Uongo

            result.append(formatted)

        ikiwa render_pos_only_separator:
            # There were only positional-only parameters, hence the
            # flag was sio reset to 'Uongo'
            result.append('/')

        rendered = '({})'.format(', '.join(result))

        ikiwa self.rudisha_annotation ni sio _empty:
            anno = formatannotation(self.rudisha_annotation)
            rendered += ' -> {}'.format(anno)

        rudisha rendered


eleza signature(obj, *, follow_wrapped=Kweli):
    """Get a signature object kila the pitaed callable."""
    rudisha Signature.kutoka_callable(obj, follow_wrapped=follow_wrapped)


eleza _main():
    """ Logic kila inspecting an object given at command line """
    agiza argparse
    agiza importlib

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'object',
         help="The object to be analysed. "
              "It supports the 'module:qualname' syntax")
    parser.add_argument(
        '-d', '--details', action='store_true',
        help='Display info about the module rather than its source code')

    args = parser.parse_args()

    target = args.object
    mod_name, has_attrs, attrs = target.partition(":")
    jaribu:
        obj = module = importlib.import_module(mod_name)
    tatizo Exception kama exc:
        msg = "Failed to agiza {} ({}: {})".format(mod_name,
                                                    type(exc).__name__,
                                                    exc)
        andika(msg, file=sys.stderr)
        sys.exit(2)

    ikiwa has_attrs:
        parts = attrs.split(".")
        obj = module
        kila part kwenye parts:
            obj = getattr(obj, part)

    ikiwa module.__name__ kwenye sys.builtin_module_names:
        andika("Can't get info kila builtin modules.", file=sys.stderr)
        sys.exit(1)

    ikiwa args.details:
        andika('Target: {}'.format(target))
        andika('Origin: {}'.format(getsourcefile(module)))
        andika('Cached: {}'.format(module.__cached__))
        ikiwa obj ni module:
            andika('Loader: {}'.format(repr(module.__loader__)))
            ikiwa hasattr(module, '__path__'):
                andika('Submodule search path: {}'.format(module.__path__))
        isipokua:
            jaribu:
                __, lineno = findsource(obj)
            tatizo Exception:
                pita
            isipokua:
                andika('Line: {}'.format(lineno))

        andika('\n')
    isipokua:
        andika(getsource(obj))


ikiwa __name__ == "__main__":
    _main()
