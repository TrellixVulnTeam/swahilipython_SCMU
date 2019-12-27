"""Get useful information kutoka live Python objects.

This module encapsulates the interface provided by the internal special
attributes (co_*, im_*, tb_*, etc.) in a friendlier fashion.
It also provides some help for examining source code and kundi layout.

Here are some of the useful functions provided by this module:

    ismodule(), isclass(), ismethod(), isfunction(), isgeneratorfunction(),
        isgenerator(), istraceback(), isframe(), iscode(), isbuiltin(),
        isroutine() - check object types
    getmembers() - get members of an object that satisfy a given condition

    getfile(), getsourcefile(), getsource() - find an object's source code
    getdoc(), getcomments() - get documentation on an object
    getmodule() - determine the module that an object came kutoka
    getclasstree() - arrange classes so as to represent their hierarchy

    getargvalues(), getcallargs() - get info about function arguments
    getfullargspec() - same, with support for Python 3 features
    formatargvalues() - format an argument spec
    getouterframes(), getinnerframes() - get info about frames
    currentframe() - get the current stack frame
    stack(), trace() - get info about frames on the stack or in a traceback

    signature() - get a Signature object for the callable
"""

# This module is in the public domain.  No warranties.

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

# Create constants for the compiler flags in Include/code.h
# We try to get them kutoka dis to avoid duplication
mod_dict = globals()
for k, v in dis.COMPILER_FLAG_NAMES.items():
    mod_dict["CO_" + v] = k

# See Include/object.h
TPFLAGS_IS_ABSTRACT = 1 << 20

# ----------------------------------------------------------- type-checking
eleza ismodule(object):
    """Return true ikiwa the object is a module.

    Module objects provide these attributes:
        __cached__      pathname to byte compiled file
        __doc__         documentation string
        __file__        filename (missing for built-in modules)"""
    rudisha isinstance(object, types.ModuleType)

eleza isclass(object):
    """Return true ikiwa the object is a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module in which this kundi was defined"""
    rudisha isinstance(object, type)

eleza ismethod(object):
    """Return true ikiwa the object is an instance method.

    Instance method objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this method was defined
        __func__        function object containing implementation of method
        __self__        instance to which this method is bound"""
    rudisha isinstance(object, types.MethodType)

eleza ismethoddescriptor(object):
    """Return true ikiwa the object is a method descriptor.

    But not ikiwa ismethod() or isclass() or isfunction() are true.

    This is new in Python 2.2, and, for example, is true of int.__add__.
    An object passing this test has a __get__ attribute but not a __set__
    attribute, but beyond that the set of attributes varies.  __name__ is
    usually sensible, and __doc__ often is.

    Methods implemented via descriptors that also pass one of the other
    tests rudisha false kutoka the ismethoddescriptor() test, simply because
    the other tests promise more -- you can, e.g., count on having the
    __func__ attribute (etc) when an object passes ismethod()."""
    ikiwa isclass(object) or ismethod(object) or isfunction(object):
        # mutual exclusion
        rudisha False
    tp = type(object)
    rudisha hasattr(tp, "__get__") and not hasattr(tp, "__set__")

eleza isdatadescriptor(object):
    """Return true ikiwa the object is a data descriptor.

    Data descriptors have a __set__ or a __delete__ attribute.  Examples are
    properties (defined in Python) and getsets and members (defined in C).
    Typically, data descriptors will also have __name__ and __doc__ attributes
    (properties, getsets, and members have both of these attributes), but this
    is not guaranteed."""
    ikiwa isclass(object) or ismethod(object) or isfunction(object):
        # mutual exclusion
        rudisha False
    tp = type(object)
    rudisha hasattr(tp, "__set__") or hasattr(tp, "__delete__")

ikiwa hasattr(types, 'MemberDescriptorType'):
    # CPython and equivalent
    eleza ismemberdescriptor(object):
        """Return true ikiwa the object is a member descriptor.

        Member descriptors are specialized descriptors defined in extension
        modules."""
        rudisha isinstance(object, types.MemberDescriptorType)
else:
    # Other implementations
    eleza ismemberdescriptor(object):
        """Return true ikiwa the object is a member descriptor.

        Member descriptors are specialized descriptors defined in extension
        modules."""
        rudisha False

ikiwa hasattr(types, 'GetSetDescriptorType'):
    # CPython and equivalent
    eleza isgetsetdescriptor(object):
        """Return true ikiwa the object is a getset descriptor.

        getset descriptors are specialized descriptors defined in extension
        modules."""
        rudisha isinstance(object, types.GetSetDescriptorType)
else:
    # Other implementations
    eleza isgetsetdescriptor(object):
        """Return true ikiwa the object is a getset descriptor.

        getset descriptors are specialized descriptors defined in extension
        modules."""
        rudisha False

eleza isfunction(object):
    """Return true ikiwa the object is a user-defined function.

    Function objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this function was defined
        __code__        code object containing compiled function bytecode
        __defaults__    tuple of any default values for arguments
        __globals__     global namespace in which this function was defined
        __annotations__ dict of parameter annotations
        __kwdefaults__  dict of keyword only parameters with defaults"""
    rudisha isinstance(object, types.FunctionType)

eleza _has_code_flag(f, flag):
    """Return true ikiwa ``f`` is a function (or a method or functools.partial
    wrapper wrapping a function) whose code object has the given ``flag``
    set in its flags."""
    while ismethod(f):
        f = f.__func__
    f = functools._unwrap_partial(f)
    ikiwa not isfunction(f):
        rudisha False
    rudisha bool(f.__code__.co_flags & flag)

eleza isgeneratorfunction(obj):
    """Return true ikiwa the object is a user-defined generator function.

    Generator function objects provide the same attributes as functions.
    See help(isfunction) for a list of attributes."""
    rudisha _has_code_flag(obj, CO_GENERATOR)

eleza iscoroutinefunction(obj):
    """Return true ikiwa the object is a coroutine function.

    Coroutine functions are defined with "async def" syntax.
    """
    rudisha _has_code_flag(obj, CO_COROUTINE)

eleza isasyncgenfunction(obj):
    """Return true ikiwa the object is an asynchronous generator function.

    Asynchronous generator functions are defined with "async def"
    syntax and have "yield" expressions in their body.
    """
    rudisha _has_code_flag(obj, CO_ASYNC_GENERATOR)

eleza isasyncgen(object):
    """Return true ikiwa the object is an asynchronous generator."""
    rudisha isinstance(object, types.AsyncGeneratorType)

eleza isgenerator(object):
    """Return true ikiwa the object is a generator.

    Generator objects provide these attributes:
        __iter__        defined to support iteration over container
        close           raises a new GeneratorExit exception inside the
                        generator to terminate the iteration
        gi_code         code object
        gi_frame        frame object or possibly None once the generator has
                        been exhausted
        gi_running      set to 1 when generator is executing, 0 otherwise
        next            rudisha the next item kutoka the container
        send            resumes the generator and "sends" a value that becomes
                        the result of the current yield-expression
        throw           used to raise an exception inside the generator"""
    rudisha isinstance(object, types.GeneratorType)

eleza iscoroutine(object):
    """Return true ikiwa the object is a coroutine."""
    rudisha isinstance(object, types.CoroutineType)

eleza isawaitable(object):
    """Return true ikiwa object can be passed to an ``await`` expression."""
    rudisha (isinstance(object, types.CoroutineType) or
            isinstance(object, types.GeneratorType) and
                bool(object.gi_code.co_flags & CO_ITERABLE_COROUTINE) or
            isinstance(object, collections.abc.Awaitable))

eleza istraceback(object):
    """Return true ikiwa the object is a traceback.

    Traceback objects provide these attributes:
        tb_frame        frame object at this level
        tb_lasti        index of last attempted instruction in bytecode
        tb_lineno       current line number in Python source code
        tb_next         next inner traceback object (called by this level)"""
    rudisha isinstance(object, types.TracebackType)

eleza isframe(object):
    """Return true ikiwa the object is a frame object.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller)
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed in this frame
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction in bytecode
        f_lineno        current line number in Python source code
        f_locals        local namespace seen by this frame
        f_trace         tracing function for this frame, or None"""
    rudisha isinstance(object, types.FrameType)

eleza iscode(object):
    """Return true ikiwa the object is a code object.

    Code objects provide these attributes:
        co_argcount         number of arguments (not including *, ** args
                            or keyword only arguments)
        co_code             string of raw compiled bytecode
        co_cellvars         tuple of names of cell variables
        co_consts           tuple of constants used in the bytecode
        co_filename         name of file in which this code object was created
        co_firstlineno      number of first line in Python source code
        co_flags            bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg
                            | 16=nested | 32=generator | 64=nofree | 128=coroutine
                            | 256=iterable_coroutine | 512=async_generator
        co_freevars         tuple of names of free variables
        co_posonlyargcount  number of positional only arguments
        co_kwonlyargcount   number of keyword only arguments (not including ** arg)
        co_lnotab           encoded mapping of line numbers to bytecode indices
        co_name             name with which this code object was defined
        co_names            tuple of names of local variables
        co_nlocals          number of local variables
        co_stacksize        virtual machine stack space required
        co_varnames         tuple of names of arguments and local variables"""
    rudisha isinstance(object, types.CodeType)

eleza isbuiltin(object):
    """Return true ikiwa the object is a built-in function or method.

    Built-in functions and methods provide these attributes:
        __doc__         documentation string
        __name__        original name of this function or method
        __self__        instance to which a method is bound, or None"""
    rudisha isinstance(object, types.BuiltinFunctionType)

eleza isroutine(object):
    """Return true ikiwa the object is any kind of function or method."""
    rudisha (isbuiltin(object)
            or isfunction(object)
            or ismethod(object)
            or ismethoddescriptor(object))

eleza isabstract(object):
    """Return true ikiwa the object is an abstract base kundi (ABC)."""
    ikiwa not isinstance(object, type):
        rudisha False
    ikiwa object.__flags__ & TPFLAGS_IS_ABSTRACT:
        rudisha True
    ikiwa not issubclass(type(object), abc.ABCMeta):
        rudisha False
    ikiwa hasattr(object, '__abstractmethods__'):
        # It looks like ABCMeta.__new__ has finished running;
        # TPFLAGS_IS_ABSTRACT should have been accurate.
        rudisha False
    # It looks like ABCMeta.__new__ has not finished running yet; we're
    # probably in __init_subclass__. We'll look for abstractmethods manually.
    for name, value in object.__dict__.items():
        ikiwa getattr(value, "__isabstractmethod__", False):
            rudisha True
    for base in object.__bases__:
        for name in getattr(base, "__abstractmethods__", ()):
            value = getattr(object, name, None)
            ikiwa getattr(value, "__isabstractmethod__", False):
                rudisha True
    rudisha False

eleza getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only rudisha members that satisfy a given predicate."""
    ikiwa isclass(object):
        mro = (object,) + getmro(object)
    else:
        mro = ()
    results = []
    processed = set()
    names = dir(object)
    # :dd any DynamicClassAttributes to the list of names ikiwa object is a class;
    # this may result in duplicate entries if, for example, a virtual
    # attribute with the same name as a DynamicClassAttribute exists
    try:
        for base in object.__bases__:
            for k, v in base.__dict__.items():
                ikiwa isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    except AttributeError:
        pass
    for key in names:
        # First try to get the value via getattr.  Some descriptors don't
        # like calling their __get__ (see bug #1785), so fall back to
        # looking in the __dict__.
        try:
            value = getattr(object, key)
            # handle the duplicate key
            ikiwa key in processed:
                raise AttributeError
        except AttributeError:
            for base in mro:
                ikiwa key in base.__dict__:
                    value = base.__dict__[key]
                    break
            else:
                # could be a (currently) missing slot member, or a buggy
                # __dir__; discard and move on
                continue
        ikiwa not predicate or predicate(value):
            results.append((key, value))
        processed.add(key)
    results.sort(key=lambda pair: pair[0])
    rudisha results

Attribute = namedtuple('Attribute', 'name kind defining_kundi object')

eleza classify_class_attrs(cls):
    """Return list of attribute-descriptor tuples.

    For each name in dir(cls), the rudisha list contains a 4-tuple
    with these elements:

        0. The name (a string).

        1. The kind of attribute this is, one of these strings:
               'kundi method'    created via classmethod()
               'static method'   created via staticmethod()
               'property'        created via property()
               'method'          any other flavor of method or descriptor
               'data'            not a method

        2. The kundi which defined this attribute (a class).

        3. The object as obtained by calling getattr; ikiwa this fails, or ikiwa the
           resulting object does not live anywhere in the class' mro (including
           metaclasses) then the object is looked up in the defining class's
           dict (found by walking the mro).

    If one of the items in dir(cls) is stored in the metakundi it will now
    be discovered and not have None be listed as the kundi in which it was
    defined.  Any items whose home kundi cannot be discovered are skipped.
    """

    mro = getmro(cls)
    metamro = getmro(type(cls)) # for attributes stored in the metaclass
    metamro = tuple(cls for cls in metamro ikiwa cls not in (type, object))
    class_bases = (cls,) + mro
    all_bases = class_bases + metamro
    names = dir(cls)
    # :dd any DynamicClassAttributes to the list of names;
    # this may result in duplicate entries if, for example, a virtual
    # attribute with the same name as a DynamicClassAttribute exists.
    for base in mro:
        for k, v in base.__dict__.items():
            ikiwa isinstance(v, types.DynamicClassAttribute):
                names.append(k)
    result = []
    processed = set()

    for name in names:
        # Get the object associated with the name, and where it was defined.
        # Normal objects will be looked up with both getattr and directly in
        # its class' dict (in case getattr fails [bug #1785], and also to look
        # for a docstring).
        # For DynamicClassAttributes on the second pass we only look in the
        # class's dict.
        #
        # Getting an obj kutoka the __dict__ sometimes reveals more than
        # using getattr.  Static and kundi methods are dramatic examples.
        homecls = None
        get_obj = None
        dict_obj = None
        ikiwa name not in processed:
            try:
                ikiwa name == '__dict__':
                    raise Exception("__dict__ is special, don't want the proxy")
                get_obj = getattr(cls, name)
            except Exception as exc:
                pass
            else:
                homecls = getattr(get_obj, "__objclass__", homecls)
                ikiwa homecls not in class_bases:
                    # ikiwa the resulting object does not live somewhere in the
                    # mro, drop it and search the mro manually
                    homecls = None
                    last_cls = None
                    # first look in the classes
                    for srch_cls in class_bases:
                        srch_obj = getattr(srch_cls, name, None)
                        ikiwa srch_obj is get_obj:
                            last_cls = srch_cls
                    # then check the metaclasses
                    for srch_cls in metamro:
                        try:
                            srch_obj = srch_cls.__getattr__(cls, name)
                        except AttributeError:
                            continue
                        ikiwa srch_obj is get_obj:
                            last_cls = srch_cls
                    ikiwa last_cls is not None:
                        homecls = last_cls
        for base in all_bases:
            ikiwa name in base.__dict__:
                dict_obj = base.__dict__[name]
                ikiwa homecls not in metamro:
                    homecls = base
                break
        ikiwa homecls is None:
            # unable to locate the attribute anywhere, most likely due to
            # buggy custom __dir__; discard and move on
            continue
        obj = get_obj ikiwa get_obj is not None else dict_obj
        # Classify the object or its descriptor.
        ikiwa isinstance(dict_obj, (staticmethod, types.BuiltinMethodType)):
            kind = "static method"
            obj = dict_obj
        elikiwa isinstance(dict_obj, (classmethod, types.ClassMethodDescriptorType)):
            kind = "kundi method"
            obj = dict_obj
        elikiwa isinstance(dict_obj, property):
            kind = "property"
            obj = dict_obj
        elikiwa isroutine(obj):
            kind = "method"
        else:
            kind = "data"
        result.append(Attribute(name, kind, homecls, obj))
        processed.add(name)
    rudisha result

# ----------------------------------------------------------- kundi helpers

eleza getmro(cls):
    "Return tuple of base classes (including cls) in method resolution order."
    rudisha cls.__mro__

# -------------------------------------------------------- function helpers

eleza unwrap(func, *, stop=None):
    """Get the object wrapped by *func*.

   Follows the chain of :attr:`__wrapped__` attributes returning the last
   object in the chain.

   *stop* is an optional callback accepting an object in the wrapper chain
   as its sole argument that allows the unwrapping to be terminated early if
   the callback returns a true value. If the callback never returns a true
   value, the last object in the chain is returned as usual. For example,
   :func:`signature` uses this to stop unwrapping ikiwa any object in the
   chain has a ``__signature__`` attribute defined.

   :exc:`ValueError` is raised ikiwa a cycle is encountered.

    """
    ikiwa stop is None:
        eleza _is_wrapper(f):
            rudisha hasattr(f, '__wrapped__')
    else:
        eleza _is_wrapper(f):
            rudisha hasattr(f, '__wrapped__') and not stop(f)
    f = func  # remember the original func for error reporting
    # Memoise by id to tolerate non-hashable objects, but store objects to
    # ensure they aren't destroyed, which would allow their IDs to be reused.
    memo = {id(f): f}
    recursion_limit = sys.getrecursionlimit()
    while _is_wrapper(func):
        func = func.__wrapped__
        id_func = id(func)
        ikiwa (id_func in memo) or (len(memo) >= recursion_limit):
            raise ValueError('wrapper loop when unwrapping {!r}'.format(f))
        memo[id_func] = func
    rudisha func

# -------------------------------------------------- source code extraction
eleza indentsize(line):
    """Return the indent size, in spaces, at the start of a line of text."""
    expline = line.expandtabs()
    rudisha len(expline) - len(expline.lstrip())

eleza _findclass(func):
    cls = sys.modules.get(func.__module__)
    ikiwa cls is None:
        rudisha None
    for name in func.__qualname__.split('.')[:-1]:
        cls = getattr(cls, name)
    ikiwa not isclass(cls):
        rudisha None
    rudisha cls

eleza _finddoc(obj):
    ikiwa isclass(obj):
        for base in obj.__mro__:
            ikiwa base is not object:
                try:
                    doc = base.__doc__
                except AttributeError:
                    continue
                ikiwa doc is not None:
                    rudisha doc
        rudisha None

    ikiwa ismethod(obj):
        name = obj.__func__.__name__
        self = obj.__self__
        ikiwa (isclass(self) and
            getattr(getattr(self, name, None), '__func__') is obj.__func__):
            # classmethod
            cls = self
        else:
            cls = self.__class__
    elikiwa isfunction(obj):
        name = obj.__name__
        cls = _findclass(obj)
        ikiwa cls is None or getattr(cls, name) is not obj:
            rudisha None
    elikiwa isbuiltin(obj):
        name = obj.__name__
        self = obj.__self__
        ikiwa (isclass(self) and
            self.__qualname__ + '.' + name == obj.__qualname__):
            # classmethod
            cls = self
        else:
            cls = self.__class__
    # Should be tested before isdatadescriptor().
    elikiwa isinstance(obj, property):
        func = obj.fget
        name = func.__name__
        cls = _findclass(func)
        ikiwa cls is None or getattr(cls, name) is not obj:
            rudisha None
    elikiwa ismethoddescriptor(obj) or isdatadescriptor(obj):
        name = obj.__name__
        cls = obj.__objclass__
        ikiwa getattr(cls, name) is not obj:
            rudisha None
        ikiwa ismemberdescriptor(obj):
            slots = getattr(cls, '__slots__', None)
            ikiwa isinstance(slots, dict) and name in slots:
                rudisha slots[name]
    else:
        rudisha None
    for base in cls.__mro__:
        try:
            doc = getattr(base, name).__doc__
        except AttributeError:
            continue
        ikiwa doc is not None:
            rudisha doc
    rudisha None

eleza getdoc(object):
    """Get the documentation string for an object.

    All tabs are expanded to spaces.  To clean up docstrings that are
    indented to line up with blocks of code, any whitespace than can be
    uniformly removed kutoka the second line onwards is removed."""
    try:
        doc = object.__doc__
    except AttributeError:
        rudisha None
    ikiwa doc is None:
        try:
            doc = _finddoc(object)
        except (AttributeError, TypeError):
            rudisha None
    ikiwa not isinstance(doc, str):
        rudisha None
    rudisha cleandoc(doc)

eleza cleandoc(doc):
    """Clean up indentation kutoka docstrings.

    Any whitespace that can be uniformly removed kutoka the second line
    onwards is removed."""
    try:
        lines = doc.expandtabs().split('\n')
    except UnicodeError:
        rudisha None
    else:
        # Find minimum indentation of any non-blank lines after first line.
        margin = sys.maxsize
        for line in lines[1:]:
            content = len(line.lstrip())
            ikiwa content:
                indent = len(line) - content
                margin = min(margin, indent)
        # Remove indentation.
        ikiwa lines:
            lines[0] = lines[0].lstrip()
        ikiwa margin < sys.maxsize:
            for i in range(1, len(lines)): lines[i] = lines[i][margin:]
        # Remove any trailing or leading blank lines.
        while lines and not lines[-1]:
            lines.pop()
        while lines and not lines[0]:
            lines.pop(0)
        rudisha '\n'.join(lines)

eleza getfile(object):
    """Work out which source or compiled file an object was defined in."""
    ikiwa ismodule(object):
        ikiwa getattr(object, '__file__', None):
            rudisha object.__file__
        raise TypeError('{!r} is a built-in module'.format(object))
    ikiwa isclass(object):
        ikiwa hasattr(object, '__module__'):
            module = sys.modules.get(object.__module__)
            ikiwa getattr(module, '__file__', None):
                rudisha module.__file__
        raise TypeError('{!r} is a built-in class'.format(object))
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
    raise TypeError('module, class, method, function, traceback, frame, or '
                    'code object was expected, got {}'.format(
                    type(object).__name__))

eleza getmodulename(path):
    """Return the module name for a given file, or None."""
    fname = os.path.basename(path)
    # Check for paths that look like an actual module file
    suffixes = [(-len(suffix), suffix)
                    for suffix in importlib.machinery.all_suffixes()]
    suffixes.sort() # try longest suffixes first, in case they overlap
    for neglen, suffix in suffixes:
        ikiwa fname.endswith(suffix):
            rudisha fname[:neglen]
    rudisha None

eleza getsourcefile(object):
    """Return the filename that can be used to locate an object's source.
    Return None ikiwa no way can be identified to get the source.
    """
    filename = getfile(object)
    all_bytecode_suffixes = importlib.machinery.DEBUG_BYTECODE_SUFFIXES[:]
    all_bytecode_suffixes += importlib.machinery.OPTIMIZED_BYTECODE_SUFFIXES[:]
    ikiwa any(filename.endswith(s) for s in all_bytecode_suffixes):
        filename = (os.path.splitext(filename)[0] +
                    importlib.machinery.SOURCE_SUFFIXES[0])
    elikiwa any(filename.endswith(s) for s in
                 importlib.machinery.EXTENSION_SUFFIXES):
        rudisha None
    ikiwa os.path.exists(filename):
        rudisha filename
    # only rudisha a non-existent filename ikiwa the module has a PEP 302 loader
    ikiwa getattr(getmodule(object, filename), '__loader__', None) is not None:
        rudisha filename
    # or it is in the linecache
    ikiwa filename in linecache.cache:
        rudisha filename

eleza getabsfile(object, _filename=None):
    """Return an absolute path to the source or compiled file for an object.

    The idea is for each object to have a unique origin, so this routine
    normalizes the result as much as possible."""
    ikiwa _filename is None:
        _filename = getsourcefile(object) or getfile(object)
    rudisha os.path.normcase(os.path.abspath(_filename))

modulesbyfile = {}
_filesbymodname = {}

eleza getmodule(object, _filename=None):
    """Return the module an object was defined in, or None ikiwa not found."""
    ikiwa ismodule(object):
        rudisha object
    ikiwa hasattr(object, '__module__'):
        rudisha sys.modules.get(object.__module__)
    # Try the filename to modulename cache
    ikiwa _filename is not None and _filename in modulesbyfile:
        rudisha sys.modules.get(modulesbyfile[_filename])
    # Try the cache again with the absolute file name
    try:
        file = getabsfile(object, _filename)
    except TypeError:
        rudisha None
    ikiwa file in modulesbyfile:
        rudisha sys.modules.get(modulesbyfile[file])
    # Update the filename to module name cache and check yet again
    # Copy sys.modules in order to cope with changes while iterating
    for modname, module in list(sys.modules.items()):
        ikiwa ismodule(module) and hasattr(module, '__file__'):
            f = module.__file__
            ikiwa f == _filesbymodname.get(modname, None):
                # Have already mapped this module, so skip it
                continue
            _filesbymodname[modname] = f
            f = getabsfile(module)
            # Always map to the name the module knows itself by
            modulesbyfile[f] = modulesbyfile[
                os.path.realpath(f)] = module.__name__
    ikiwa file in modulesbyfile:
        rudisha sys.modules.get(modulesbyfile[file])
    # Check the main module
    main = sys.modules['__main__']
    ikiwa not hasattr(object, '__name__'):
        rudisha None
    ikiwa hasattr(main, object.__name__):
        mainobject = getattr(main, object.__name__)
        ikiwa mainobject is object:
            rudisha main
    # Check builtins
    builtin = sys.modules['builtins']
    ikiwa hasattr(builtin, object.__name__):
        builtinobject = getattr(builtin, object.__name__)
        ikiwa builtinobject is object:
            rudisha builtin

eleza findsource(object):
    """Return the entire source file and starting line number for an object.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a list of all the lines
    in the file and the line number indexes a line in that list.  An OSError
    is raised ikiwa the source code cannot be retrieved."""

    file = getsourcefile(object)
    ikiwa file:
        # Invalidate cache ikiwa needed.
        linecache.checkcache(file)
    else:
        file = getfile(object)
        # Allow filenames in form of "<something>" to pass through.
        # `doctest` monkeypatches `linecache` module to enable
        # inspection, so let `linecache.getlines` to be called.
        ikiwa not (file.startswith('<') and file.endswith('>')):
            raise OSError('source code not available')

    module = getmodule(object, file)
    ikiwa module:
        lines = linecache.getlines(file, module.__dict__)
    else:
        lines = linecache.getlines(file)
    ikiwa not lines:
        raise OSError('could not get source code')

    ikiwa ismodule(object):
        rudisha lines, 0

    ikiwa isclass(object):
        name = object.__name__
        pat = re.compile(r'^(\s*)class\s*' + name + r'\b')
        # make some effort to find the best matching kundi definition:
        # use the one with the least indentation, which is the one
        # that's most probably not inside a function definition.
        candidates = []
        for i in range(len(lines)):
            match = pat.match(lines[i])
            ikiwa match:
                # ikiwa it's at toplevel, it's already the best one
                ikiwa lines[i][0] == 'c':
                    rudisha lines, i
                # else add whitespace to candidate list
                candidates.append((match.group(1), i))
        ikiwa candidates:
            # this will sort by whitespace, and by line number,
            # less whitespace first
            candidates.sort()
            rudisha lines, candidates[0][1]
        else:
            raise OSError('could not find kundi definition')

    ikiwa ismethod(object):
        object = object.__func__
    ikiwa isfunction(object):
        object = object.__code__
    ikiwa istraceback(object):
        object = object.tb_frame
    ikiwa isframe(object):
        object = object.f_code
    ikiwa iscode(object):
        ikiwa not hasattr(object, 'co_firstlineno'):
            raise OSError('could not find function definition')
        lnum = object.co_firstlineno - 1
        pat = re.compile(r'^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
        while lnum > 0:
            ikiwa pat.match(lines[lnum]): break
            lnum = lnum - 1
        rudisha lines, lnum
    raise OSError('could not find code object')

eleza getcomments(object):
    """Get lines of comments immediately preceding an object's source code.

    Returns None when source can't be found.
    """
    try:
        lines, lnum = findsource(object)
    except (OSError, TypeError):
        rudisha None

    ikiwa ismodule(object):
        # Look for a comment block at the top of the file.
        start = 0
        ikiwa lines and lines[0][:2] == '#!': start = 1
        while start < len(lines) and lines[start].strip() in ('', '#'):
            start = start + 1
        ikiwa start < len(lines) and lines[start][:1] == '#':
            comments = []
            end = start
            while end < len(lines) and lines[end][:1] == '#':
                comments.append(lines[end].expandtabs())
                end = end + 1
            rudisha ''.join(comments)

    # Look for a preceding block of comments at the same indentation.
    elikiwa lnum > 0:
        indent = indentsize(lines[lnum])
        end = lnum - 1
        ikiwa end >= 0 and lines[end].lstrip()[:1] == '#' and \
            indentsize(lines[end]) == indent:
            comments = [lines[end].expandtabs().lstrip()]
            ikiwa end > 0:
                end = end - 1
                comment = lines[end].expandtabs().lstrip()
                while comment[:1] == '#' and indentsize(lines[end]) == indent:
                    comments[:0] = [comment]
                    end = end - 1
                    ikiwa end < 0: break
                    comment = lines[end].expandtabs().lstrip()
            while comments and comments[0].strip() == '#':
                comments[:1] = []
            while comments and comments[-1].strip() == '#':
                comments[-1:] = []
            rudisha ''.join(comments)

kundi EndOfBlock(Exception): pass

kundi BlockFinder:
    """Provide a tokeneater() method to detect the end of a code block."""
    eleza __init__(self):
        self.indent = 0
        self.islambda = False
        self.started = False
        self.passline = False
        self.indecorator = False
        self.decoratorhasargs = False
        self.last = 1

    eleza tokeneater(self, type, token, srowcol, erowcol, line):
        ikiwa not self.started and not self.indecorator:
            # skip any decorators
            ikiwa token == "@":
                self.indecorator = True
            # look for the first "def", "class" or "lambda"
            elikiwa token in ("def", "class", "lambda"):
                ikiwa token == "lambda":
                    self.islambda = True
                self.started = True
            self.passline = True    # skip to the end of the line
        elikiwa token == "(":
            ikiwa self.indecorator:
                self.decoratorhasargs = True
        elikiwa token == ")":
            ikiwa self.indecorator:
                self.indecorator = False
                self.decoratorhasargs = False
        elikiwa type == tokenize.NEWLINE:
            self.passline = False   # stop skipping when a NEWLINE is seen
            self.last = srowcol[0]
            ikiwa self.islambda:       # lambdas always end at the first NEWLINE
                raise EndOfBlock
            # hitting a NEWLINE when in a decorator without args
            # ends the decorator
            ikiwa self.indecorator and not self.decoratorhasargs:
                self.indecorator = False
        elikiwa self.passline:
            pass
        elikiwa type == tokenize.INDENT:
            self.indent = self.indent + 1
            self.passline = True
        elikiwa type == tokenize.DEDENT:
            self.indent = self.indent - 1
            # the end of matching indent/dedent pairs end a block
            # (note that this only works for "def"/"class" blocks,
            #  not e.g. for "if: else:" or "try: finally:" blocks)
            ikiwa self.indent <= 0:
                raise EndOfBlock
        elikiwa self.indent == 0 and type not in (tokenize.COMMENT, tokenize.NL):
            # any other token on the same indentation level end the previous
            # block as well, except the pseudo-tokens COMMENT and NL.
            raise EndOfBlock

eleza getblock(lines):
    """Extract the block of code at the top of the given list of lines."""
    blockfinder = BlockFinder()
    try:
        tokens = tokenize.generate_tokens(iter(lines).__next__)
        for _token in tokens:
            blockfinder.tokeneater(*_token)
    except (EndOfBlock, IndentationError):
        pass
    rudisha lines[:blockfinder.last]

eleza getsourcelines(object):
    """Return a list of source lines and starting line number for an object.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a list of the lines
    corresponding to the object and the line number indicates where in the
    original source file the first line of code was found.  An OSError is
    raised ikiwa the source code cannot be retrieved."""
    object = unwrap(object)
    lines, lnum = findsource(object)

    ikiwa istraceback(object):
        object = object.tb_frame

    # for module or frame that corresponds to module, rudisha all source lines
    ikiwa (ismodule(object) or
        (isframe(object) and object.f_code.co_name == "<module>")):
        rudisha lines, 0
    else:
        rudisha getblock(lines[lnum:]), lnum + 1

eleza getsource(object):
    """Return the text of the source code for an object.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a single string.  An
    OSError is raised ikiwa the source code cannot be retrieved."""
    lines, lnum = getsourcelines(object)
    rudisha ''.join(lines)

# --------------------------------------------------- kundi tree extraction
eleza walktree(classes, children, parent):
    """Recursive helper function for getclasstree()."""
    results = []
    classes.sort(key=attrgetter('__module__', '__name__'))
    for c in classes:
        results.append((c, c.__bases__))
        ikiwa c in children:
            results.append(walktree(children[c], children, c))
    rudisha results

eleza getclasstree(classes, unique=False):
    """Arrange the given list of classes into a hierarchy of nested lists.

    Where a nested list appears, it contains classes derived kutoka the class
    whose entry immediately precedes the list.  Each entry is a 2-tuple
    containing a kundi and a tuple of its base classes.  If the 'unique'
    argument is true, exactly one entry appears in the returned structure
    for each kundi in the given list.  Otherwise, classes using multiple
    inheritance and their descendants will appear multiple times."""
    children = {}
    roots = []
    for c in classes:
        ikiwa c.__bases__:
            for parent in c.__bases__:
                ikiwa parent not in children:
                    children[parent] = []
                ikiwa c not in children[parent]:
                    children[parent].append(c)
                ikiwa unique and parent in classes: break
        elikiwa c not in roots:
            roots.append(c)
    for parent in children:
        ikiwa parent not in classes:
            roots.append(parent)
    rudisha walktree(roots, children, None)

# ------------------------------------------------ argument list extraction
Arguments = namedtuple('Arguments', 'args, varargs, varkw')

eleza getargs(co):
    """Get information about the arguments accepted by a code object.

    Three things are returned: (args, varargs, varkw), where
    'args' is the list of argument names. Keyword-only arguments are
    appended. 'varargs' and 'varkw' are the names of the * and **
    arguments or None."""
    ikiwa not iscode(co):
        raise TypeError('{!r} is not a code object'.format(co))

    names = co.co_varnames
    nargs = co.co_argcount
    nkwargs = co.co_kwonlyargcount
    args = list(names[:nargs])
    kwonlyargs = list(names[nargs:nargs+nkwargs])
    step = 0

    nargs += nkwargs
    varargs = None
    ikiwa co.co_flags & CO_VARARGS:
        varargs = co.co_varnames[nargs]
        nargs = nargs + 1
    varkw = None
    ikiwa co.co_flags & CO_VARKEYWORDS:
        varkw = co.co_varnames[nargs]
    rudisha Arguments(args + kwonlyargs, varargs, varkw)

ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')

eleza getargspec(func):
    """Get the names and default values of a function's parameters.

    A tuple of four things is returned: (args, varargs, keywords, defaults).
    'args' is a list of the argument names, including keyword-only argument names.
    'varargs' and 'keywords' are the names of the * and ** parameters or None.
    'defaults' is an n-tuple of the default values of the last n parameters.

    This function is deprecated, as it does not support annotations or
    keyword-only parameters and will raise ValueError ikiwa either is present
    on the supplied callable.

    For a more structured introspection API, use inspect.signature() instead.

    Alternatively, use getfullargspec() for an API with a similar namedtuple
    based interface, but full support for annotations and keyword-only
    parameters.

    Deprecated since Python 3.5, use `inspect.getfullargspec()`.
    """
    warnings.warn("inspect.getargspec() is deprecated since Python 3.0, "
                  "use inspect.signature() or inspect.getfullargspec()",
                  DeprecationWarning, stacklevel=2)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = \
        getfullargspec(func)
    ikiwa kwonlyargs or ann:
        raise ValueError("Function has keyword-only parameters or annotations"
                         ", use inspect.signature() API which can support them")
    rudisha ArgSpec(args, varargs, varkw, defaults)

FullArgSpec = namedtuple('FullArgSpec',
    'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations')

eleza getfullargspec(func):
    """Get the names and default values of a callable object's parameters.

    A tuple of seven things is returned:
    (args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations).
    'args' is a list of the parameter names.
    'varargs' and 'varkw' are the names of the * and ** parameters or None.
    'defaults' is an n-tuple of the default values of the last n parameters.
    'kwonlyargs' is a list of keyword-only parameter names.
    'kwonlydefaults' is a dictionary mapping names kutoka kwonlyargs to defaults.
    'annotations' is a dictionary mapping parameter names to annotations.

    Notable differences kutoka inspect.signature():
      - the "self" parameter is always reported, even for bound methods
      - wrapper chains defined by __wrapped__ *not* unwrapped automatically
    """
    try:
        # Re: `skip_bound_arg=False`
        #
        # There is a notable difference in behaviour between getfullargspec
        # and Signature: the former always returns 'self' parameter for bound
        # methods, whereas the Signature always shows the actual calling
        # signature of the passed object.
        #
        # To simulate this behaviour, we "unbind" bound methods, to trick
        # inspect.signature to always rudisha their first parameter ("self",
        # usually)

        # Re: `follow_wrapper_chains=False`
        #
        # getfullargspec() historically ignored __wrapped__ attributes,
        # so we ensure that remains the case in 3.3+

        sig = _signature_kutoka_callable(func,
                                       follow_wrapper_chains=False,
                                       skip_bound_arg=False,
                                       sigcls=Signature)
    except Exception as ex:
        # Most of the times 'signature' will raise ValueError.
        # But, it can also raise AttributeError, and, maybe something
        # else. So to be fully backwards compatible, we catch all
        # possible exceptions here, and reraise a TypeError.
        raise TypeError('unsupported callable') kutoka ex

    args = []
    varargs = None
    varkw = None
    posonlyargs = []
    kwonlyargs = []
    defaults = ()
    annotations = {}
    defaults = ()
    kwdefaults = {}

    ikiwa sig.return_annotation is not sig.empty:
        annotations['return'] = sig.return_annotation

    for param in sig.parameters.values():
        kind = param.kind
        name = param.name

        ikiwa kind is _POSITIONAL_ONLY:
            posonlyargs.append(name)
            ikiwa param.default is not param.empty:
                defaults += (param.default,)
        elikiwa kind is _POSITIONAL_OR_KEYWORD:
            args.append(name)
            ikiwa param.default is not param.empty:
                defaults += (param.default,)
        elikiwa kind is _VAR_POSITIONAL:
            varargs = name
        elikiwa kind is _KEYWORD_ONLY:
            kwonlyargs.append(name)
            ikiwa param.default is not param.empty:
                kwdefaults[name] = param.default
        elikiwa kind is _VAR_KEYWORD:
            varkw = name

        ikiwa param.annotation is not param.empty:
            annotations[name] = param.annotation

    ikiwa not kwdefaults:
        # compatibility with 'func.__kwdefaults__'
        kwdefaults = None

    ikiwa not defaults:
        # compatibility with 'func.__defaults__'
        defaults = None

    rudisha FullArgSpec(posonlyargs + args, varargs, varkw, defaults,
                       kwonlyargs, kwdefaults, annotations)


ArgInfo = namedtuple('ArgInfo', 'args varargs keywords locals')

eleza getargvalues(frame):
    """Get information about arguments passed into a particular frame.

    A tuple of four things is returned: (args, varargs, varkw, locals).
    'args' is a list of the argument names.
    'varargs' and 'varkw' are the names of the * and ** arguments or None.
    'locals' is the locals dictionary of the given frame."""
    args, varargs, varkw = getargs(frame.f_code)
    rudisha ArgInfo(args, varargs, varkw, frame.f_locals)

eleza formatannotation(annotation, base_module=None):
    ikiwa getattr(annotation, '__module__', None) == 'typing':
        rudisha repr(annotation).replace('typing.', '')
    ikiwa isinstance(annotation, type):
        ikiwa annotation.__module__ in ('builtins', base_module):
            rudisha annotation.__qualname__
        rudisha annotation.__module__+'.'+annotation.__qualname__
    rudisha repr(annotation)

eleza formatannotationrelativeto(object):
    module = getattr(object, '__module__', None)
    eleza _formatannotation(annotation):
        rudisha formatannotation(annotation, module)
    rudisha _formatannotation

eleza formatargspec(args, varargs=None, varkw=None, defaults=None,
                  kwonlyargs=(), kwonlydefaults={}, annotations={},
                  formatarg=str,
                  formatvarargs=lambda name: '*' + name,
                  formatvarkw=lambda name: '**' + name,
                  formatvalue=lambda value: '=' + repr(value),
                  formatreturns=lambda text: ' -> ' + text,
                  formatannotation=formatannotation):
    """Format an argument spec kutoka the values returned by getfullargspec.

    The first seven arguments are (args, varargs, varkw, defaults,
    kwonlyargs, kwonlydefaults, annotations).  The other five arguments
    are the corresponding optional formatting functions that are called to
    turn names and values into strings.  The last argument is an optional
    function to format the sequence of arguments.

    Deprecated since Python 3.5: use the `signature` function and `Signature`
    objects.
    """

    kutoka warnings agiza warn

    warn("`formatargspec` is deprecated since Python 3.5. Use `signature` and "
         "the `Signature` object directly",
         DeprecationWarning,
         stacklevel=2)

    eleza formatargandannotation(arg):
        result = formatarg(arg)
        ikiwa arg in annotations:
            result += ': ' + formatannotation(annotations[arg])
        rudisha result
    specs = []
    ikiwa defaults:
        firstdefault = len(args) - len(defaults)
    for i, arg in enumerate(args):
        spec = formatargandannotation(arg)
        ikiwa defaults and i >= firstdefault:
            spec = spec + formatvalue(defaults[i - firstdefault])
        specs.append(spec)
    ikiwa varargs is not None:
        specs.append(formatvarargs(formatargandannotation(varargs)))
    else:
        ikiwa kwonlyargs:
            specs.append('*')
    ikiwa kwonlyargs:
        for kwonlyarg in kwonlyargs:
            spec = formatargandannotation(kwonlyarg)
            ikiwa kwonlydefaults and kwonlyarg in kwonlydefaults:
                spec += formatvalue(kwonlydefaults[kwonlyarg])
            specs.append(spec)
    ikiwa varkw is not None:
        specs.append(formatvarkw(formatargandannotation(varkw)))
    result = '(' + ', '.join(specs) + ')'
    ikiwa 'return' in annotations:
        result += formatreturns(formatannotation(annotations['return']))
    rudisha result

eleza formatargvalues(args, varargs, varkw, locals,
                    formatarg=str,
                    formatvarargs=lambda name: '*' + name,
                    formatvarkw=lambda name: '**' + name,
                    formatvalue=lambda value: '=' + repr(value)):
    """Format an argument spec kutoka the 4 values returned by getargvalues.

    The first four arguments are (args, varargs, varkw, locals).  The
    next four arguments are the corresponding optional formatting functions
    that are called to turn names and values into strings.  The ninth
    argument is an optional function to format the sequence of arguments."""
    eleza convert(name, locals=locals,
                formatarg=formatarg, formatvalue=formatvalue):
        rudisha formatarg(name) + formatvalue(locals[name])
    specs = []
    for i in range(len(args)):
        specs.append(convert(args[i]))
    ikiwa varargs:
        specs.append(formatvarargs(varargs) + formatvalue(locals[varargs]))
    ikiwa varkw:
        specs.append(formatvarkw(varkw) + formatvalue(locals[varkw]))
    rudisha '(' + ', '.join(specs) + ')'

eleza _missing_arguments(f_name, argnames, pos, values):
    names = [repr(name) for name in argnames ikiwa name not in values]
    missing = len(names)
    ikiwa missing == 1:
        s = names[0]
    elikiwa missing == 2:
        s = "{} and {}".format(*names)
    else:
        tail = ", {} and {}".format(*names[-2:])
        del names[-2:]
        s = ", ".join(names) + tail
    raise TypeError("%s() missing %i required %s argument%s: %s" %
                    (f_name, missing,
                      "positional" ikiwa pos else "keyword-only",
                      "" ikiwa missing == 1 else "s", s))

eleza _too_many(f_name, args, kwonly, varargs, defcount, given, values):
    atleast = len(args) - defcount
    kwonly_given = len([arg for arg in kwonly ikiwa arg in values])
    ikiwa varargs:
        plural = atleast != 1
        sig = "at least %d" % (atleast,)
    elikiwa defcount:
        plural = True
        sig = "kutoka %d to %d" % (atleast, len(args))
    else:
        plural = len(args) != 1
        sig = str(len(args))
    kwonly_sig = ""
    ikiwa kwonly_given:
        msg = " positional argument%s (and %d keyword-only argument%s)"
        kwonly_sig = (msg % ("s" ikiwa given != 1 else "", kwonly_given,
                             "s" ikiwa kwonly_given != 1 else ""))
    raise TypeError("%s() takes %s positional argument%s but %d%s %s given" %
            (f_name, sig, "s" ikiwa plural else "", given, kwonly_sig,
             "was" ikiwa given == 1 and not kwonly_given else "were"))

eleza getcallargs(func, /, *positional, **named):
    """Get the mapping of arguments to values.

    A dict is returned, with keys the function argument names (including the
    names of the * and ** arguments, ikiwa any), and values the respective bound
    values kutoka 'positional' and 'named'."""
    spec = getfullargspec(func)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = spec
    f_name = func.__name__
    arg2value = {}


    ikiwa ismethod(func) and func.__self__ is not None:
        # implicit 'self' (or 'cls' for classmethods) argument
        positional = (func.__self__,) + positional
    num_pos = len(positional)
    num_args = len(args)
    num_defaults = len(defaults) ikiwa defaults else 0

    n = min(num_pos, num_args)
    for i in range(n):
        arg2value[args[i]] = positional[i]
    ikiwa varargs:
        arg2value[varargs] = tuple(positional[n:])
    possible_kwargs = set(args + kwonlyargs)
    ikiwa varkw:
        arg2value[varkw] = {}
    for kw, value in named.items():
        ikiwa kw not in possible_kwargs:
            ikiwa not varkw:
                raise TypeError("%s() got an unexpected keyword argument %r" %
                                (f_name, kw))
            arg2value[varkw][kw] = value
            continue
        ikiwa kw in arg2value:
            raise TypeError("%s() got multiple values for argument %r" %
                            (f_name, kw))
        arg2value[kw] = value
    ikiwa num_pos > num_args and not varargs:
        _too_many(f_name, args, kwonlyargs, varargs, num_defaults,
                   num_pos, arg2value)
    ikiwa num_pos < num_args:
        req = args[:num_args - num_defaults]
        for arg in req:
            ikiwa arg not in arg2value:
                _missing_arguments(f_name, req, True, arg2value)
        for i, arg in enumerate(args[num_args - num_defaults:]):
            ikiwa arg not in arg2value:
                arg2value[arg] = defaults[i]
    missing = 0
    for kwarg in kwonlyargs:
        ikiwa kwarg not in arg2value:
            ikiwa kwonlydefaults and kwarg in kwonlydefaults:
                arg2value[kwarg] = kwonlydefaults[kwarg]
            else:
                missing += 1
    ikiwa missing:
        _missing_arguments(f_name, kwonlyargs, False, arg2value)
    rudisha arg2value

ClosureVars = namedtuple('ClosureVars', 'nonlocals globals builtins unbound')

eleza getclosurevars(func):
    """
    Get the mapping of free variables to their current values.

    Returns a named tuple of dicts mapping the current nonlocal, global
    and builtin references as seen by the body of the function. A final
    set of unbound names that could not be resolved is also provided.
    """

    ikiwa ismethod(func):
        func = func.__func__

    ikiwa not isfunction(func):
        raise TypeError("{!r} is not a Python function".format(func))

    code = func.__code__
    # Nonlocal references are named in co_freevars and resolved
    # by looking them up in __closure__ by positional index
    ikiwa func.__closure__ is None:
        nonlocal_vars = {}
    else:
        nonlocal_vars = {
            var : cell.cell_contents
            for var, cell in zip(code.co_freevars, func.__closure__)
       }

    # Global and builtin references are named in co_names and resolved
    # by looking them up in __globals__ or __builtins__
    global_ns = func.__globals__
    builtin_ns = global_ns.get("__builtins__", builtins.__dict__)
    ikiwa ismodule(builtin_ns):
        builtin_ns = builtin_ns.__dict__
    global_vars = {}
    builtin_vars = {}
    unbound_names = set()
    for name in code.co_names:
        ikiwa name in ("None", "True", "False"):
            # Because these used to be builtins instead of keywords, they
            # may still show up as name references. We ignore them.
            continue
        try:
            global_vars[name] = global_ns[name]
        except KeyError:
            try:
                builtin_vars[name] = builtin_ns[name]
            except KeyError:
                unbound_names.add(name)

    rudisha ClosureVars(nonlocal_vars, global_vars,
                       builtin_vars, unbound_names)

# -------------------------------------------------- stack frame extraction

Traceback = namedtuple('Traceback', 'filename lineno function code_context index')

eleza getframeinfo(frame, context=1):
    """Get information about a frame or traceback object.

    A tuple of five things is returned: the filename, the line number of
    the current line, the function name, a list of lines of context kutoka
    the source code, and the index of the current line within that list.
    The optional second argument specifies the number of lines of context
    to return, which are centered around the current line."""
    ikiwa istraceback(frame):
        lineno = frame.tb_lineno
        frame = frame.tb_frame
    else:
        lineno = frame.f_lineno
    ikiwa not isframe(frame):
        raise TypeError('{!r} is not a frame or traceback object'.format(frame))

    filename = getsourcefile(frame) or getfile(frame)
    ikiwa context > 0:
        start = lineno - 1 - context//2
        try:
            lines, lnum = findsource(frame)
        except OSError:
            lines = index = None
        else:
            start = max(0, min(start, len(lines) - context))
            lines = lines[start:start+context]
            index = lineno - 1 - start
    else:
        lines = index = None

    rudisha Traceback(filename, lineno, frame.f_code.co_name, lines, index)

eleza getlineno(frame):
    """Get the line number kutoka a frame object, allowing for optimization."""
    # FrameType.f_lineno is now a descriptor that grovels co_lnotab
    rudisha frame.f_lineno

FrameInfo = namedtuple('FrameInfo', ('frame',) + Traceback._fields)

eleza getouterframes(frame, context=1):
    """Get a list of records for a frame and all higher (calling) frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, and index within the context."""
    framelist = []
    while frame:
        frameinfo = (frame,) + getframeinfo(frame, context)
        framelist.append(FrameInfo(*frameinfo))
        frame = frame.f_back
    rudisha framelist

eleza getinnerframes(tb, context=1):
    """Get a list of records for a traceback's frame and all lower frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, and index within the context."""
    framelist = []
    while tb:
        frameinfo = (tb.tb_frame,) + getframeinfo(tb, context)
        framelist.append(FrameInfo(*frameinfo))
        tb = tb.tb_next
    rudisha framelist

eleza currentframe():
    """Return the frame of the caller or None ikiwa this is not possible."""
    rudisha sys._getframe(1) ikiwa hasattr(sys, "_getframe") else None

eleza stack(context=1):
    """Return a list of records for the stack above the caller's frame."""
    rudisha getouterframes(sys._getframe(1), context)

eleza trace(context=1):
    """Return a list of records for the stack below the current exception."""
    rudisha getinnerframes(sys.exc_info()[2], context)


# ------------------------------------------------ static version of getattr

_sentinel = object()

eleza _static_getmro(klass):
    rudisha type.__dict__['__mro__'].__get__(klass)

eleza _check_instance(obj, attr):
    instance_dict = {}
    try:
        instance_dict = object.__getattribute__(obj, "__dict__")
    except AttributeError:
        pass
    rudisha dict.get(instance_dict, attr, _sentinel)


eleza _check_class(klass, attr):
    for entry in _static_getmro(klass):
        ikiwa _shadowed_dict(type(entry)) is _sentinel:
            try:
                rudisha entry.__dict__[attr]
            except KeyError:
                pass
    rudisha _sentinel

eleza _is_type(obj):
    try:
        _static_getmro(obj)
    except TypeError:
        rudisha False
    rudisha True

eleza _shadowed_dict(klass):
    dict_attr = type.__dict__["__dict__"]
    for entry in _static_getmro(klass):
        try:
            class_dict = dict_attr.__get__(entry)["__dict__"]
        except KeyError:
            pass
        else:
            ikiwa not (type(class_dict) is types.GetSetDescriptorType and
                    class_dict.__name__ == "__dict__" and
                    class_dict.__objclass__ is entry):
                rudisha class_dict
    rudisha _sentinel

eleza getattr_static(obj, attr, default=_sentinel):
    """Retrieve attributes without triggering dynamic lookup via the
       descriptor protocol,  __getattr__ or __getattribute__.

       Note: this function may not be able to retrieve all attributes
       that getattr can fetch (like dynamically created attributes)
       and may find attributes that getattr can't (like descriptors
       that raise AttributeError). It can also rudisha descriptor objects
       instead of instance members in some cases. See the
       documentation for details.
    """
    instance_result = _sentinel
    ikiwa not _is_type(obj):
        klass = type(obj)
        dict_attr = _shadowed_dict(klass)
        ikiwa (dict_attr is _sentinel or
            type(dict_attr) is types.MemberDescriptorType):
            instance_result = _check_instance(obj, attr)
    else:
        klass = obj

    klass_result = _check_class(klass, attr)

    ikiwa instance_result is not _sentinel and klass_result is not _sentinel:
        ikiwa (_check_class(type(klass_result), '__get__') is not _sentinel and
            _check_class(type(klass_result), '__set__') is not _sentinel):
            rudisha klass_result

    ikiwa instance_result is not _sentinel:
        rudisha instance_result
    ikiwa klass_result is not _sentinel:
        rudisha klass_result

    ikiwa obj is klass:
        # for types we check the metakundi too
        for entry in _static_getmro(type(klass)):
            ikiwa _shadowed_dict(type(entry)) is _sentinel:
                try:
                    rudisha entry.__dict__[attr]
                except KeyError:
                    pass
    ikiwa default is not _sentinel:
        rudisha default
    raise AttributeError(attr)


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
      GEN_SUSPENDED: Currently suspended at a yield expression.
      GEN_CLOSED: Execution has completed.
    """
    ikiwa generator.gi_running:
        rudisha GEN_RUNNING
    ikiwa generator.gi_frame is None:
        rudisha GEN_CLOSED
    ikiwa generator.gi_frame.f_lasti == -1:
        rudisha GEN_CREATED
    rudisha GEN_SUSPENDED


eleza getgeneratorlocals(generator):
    """
    Get the mapping of generator local variables to their current values.

    A dict is returned, with the keys the local variable names and values the
    bound values."""

    ikiwa not isgenerator(generator):
        raise TypeError("{!r} is not a Python generator".format(generator))

    frame = getattr(generator, "gi_frame", None)
    ikiwa frame is not None:
        rudisha generator.gi_frame.f_locals
    else:
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
    ikiwa coroutine.cr_frame is None:
        rudisha CORO_CLOSED
    ikiwa coroutine.cr_frame.f_lasti == -1:
        rudisha CORO_CREATED
    rudisha CORO_SUSPENDED


eleza getcoroutinelocals(coroutine):
    """
    Get the mapping of coroutine local variables to their current values.

    A dict is returned, with the keys the local variable names and values the
    bound values."""
    frame = getattr(coroutine, "cr_frame", None)
    ikiwa frame is not None:
        rudisha frame.f_locals
    else:
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
    named ``method_name`` and returns it only ikiwa it is a
    pure python function.
    """
    try:
        meth = getattr(cls, method_name)
    except AttributeError:
        return
    else:
        ikiwa not isinstance(meth, _NonUserDefinedCallables):
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

    partial_args = partial.args or ()
    partial_keywords = partial.keywords or {}

    ikiwa extra_args:
        partial_args = extra_args + partial_args

    try:
        ba = wrapped_sig.bind_partial(*partial_args, **partial_keywords)
    except TypeError as ex:
        msg = 'partial object {!r} has incorrect arguments'.format(partial)
        raise ValueError(msg) kutoka ex


    transform_to_kwonly = False
    for param_name, param in old_params.items():
        try:
            arg_value = ba.arguments[param_name]
        except KeyError:
            pass
        else:
            ikiwa param.kind is _POSITIONAL_ONLY:
                # If positional-only parameter is bound by partial,
                # it effectively disappears kutoka the signature
                new_params.pop(param_name)
                continue

            ikiwa param.kind is _POSITIONAL_OR_KEYWORD:
                ikiwa param_name in partial_keywords:
                    # This means that this parameter, and all parameters
                    # after it should be keyword-only (and var-positional
                    # should be removed). Here's why. Consider the following
                    # function:
                    #     foo(a, b, *args, c):
                    #         pass
                    #
                    # "partial(foo, a='spam')" will have the following
                    # signature: "(*, a='spam', b, c)". Because attempting
                    # to call that partial with "(10, 20)" arguments will
                    # raise a TypeError, saying that "a" argument received
                    # multiple values.
                    transform_to_kwonly = True
                    # Set the new default value
                    new_params[param_name] = param.replace(default=arg_value)
                else:
                    # was passed as a positional argument
                    new_params.pop(param.name)
                    continue

            ikiwa param.kind is _KEYWORD_ONLY:
                # Set the new default value
                new_params[param_name] = param.replace(default=arg_value)

        ikiwa transform_to_kwonly:
            assert param.kind is not _POSITIONAL_ONLY

            ikiwa param.kind is _POSITIONAL_OR_KEYWORD:
                new_param = new_params[param_name].replace(kind=_KEYWORD_ONLY)
                new_params[param_name] = new_param
                new_params.move_to_end(param_name)
            elikiwa param.kind in (_KEYWORD_ONLY, _VAR_KEYWORD):
                new_params.move_to_end(param_name)
            elikiwa param.kind is _VAR_POSITIONAL:
                new_params.pop(param.name)

    rudisha wrapped_sig.replace(parameters=new_params.values())


eleza _signature_bound_method(sig):
    """Private helper to transform signatures for unbound
    functions to bound methods.
    """

    params = tuple(sig.parameters.values())

    ikiwa not params or params[0].kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
        raise ValueError('invalid method signature')

    kind = params[0].kind
    ikiwa kind in (_POSITIONAL_OR_KEYWORD, _POSITIONAL_ONLY):
        # Drop first parameter:
        # '(p1, p2[, ...])' -> '(p2[, ...])'
        params = params[1:]
    else:
        ikiwa kind is not _VAR_POSITIONAL:
            # Unless we add a new parameter type we never
            # get here
            raise ValueError('invalid argument type')
        # It's a var-positional parameter.
        # Do nothing. '(*args[, ...])' -> '(*args[, ...])'

    rudisha sig.replace(parameters=params)


eleza _signature_is_builtin(obj):
    """Private helper to test ikiwa `obj` is a callable that might
    support Argument Clinic's __text_signature__ protocol.
    """
    rudisha (isbuiltin(obj) or
            ismethoddescriptor(obj) or
            isinstance(obj, _NonUserDefinedCallables) or
            # Can't test 'isinstance(type)' here, as it would
            # also be True for regular python classes
            obj in (type, object))


eleza _signature_is_functionlike(obj):
    """Private helper to test ikiwa `obj` is a duck type of FunctionType.
    A good example of such objects are functions compiled with
    Cython, which have all attributes that a pure Python function
    would have, but have their code statically compiled.
    """

    ikiwa not callable(obj) or isclass(obj):
        # All function-like objects are obviously callables,
        # and not classes.
        rudisha False

    name = getattr(obj, '__name__', None)
    code = getattr(obj, '__code__', None)
    defaults = getattr(obj, '__defaults__', _void) # Important to use _void ...
    kwdefaults = getattr(obj, '__kwdefaults__', _void) # ... and not None here
    annotations = getattr(obj, '__annotations__', None)

    rudisha (isinstance(code, types.CodeType) and
            isinstance(name, str) and
            (defaults is None or isinstance(defaults, tuple)) and
            (kwdefaults is None or isinstance(kwdefaults, dict)) and
            isinstance(annotations, dict))


eleza _signature_get_bound_param(spec):
    """ Private helper to get first parameter name kutoka a
    __text_signature__ of a builtin method, which should
    be in the following format: '($param1, ...)'.
    Assumptions are that the first argument won't have
    a default value or an annotation.
    """

    assert spec.startswith('($')

    pos = spec.find(',')
    ikiwa pos == -1:
        pos = spec.find(')')

    cpos = spec.find(':')
    assert cpos == -1 or cpos > pos

    cpos = spec.find('=')
    assert cpos == -1 or cpos > pos

    rudisha spec[2:pos]


eleza _signature_strip_non_python_syntax(signature):
    """
    Private helper function. Takes a signature in Argument Clinic's
    extended signature format.

    Returns a tuple of three things:
      * that signature re-rendered in standard Python syntax,
      * the index of the "self" parameter (generally 0), or None if
        the function does not have a "self" parameter, and
      * the index of the last "positional only" parameter,
        or None ikiwa the signature has no positional-only parameters.
    """

    ikiwa not signature:
        rudisha signature, None, None

    self_parameter = None
    last_positional_only = None

    lines = [l.encode('ascii') for l in signature.split('\n')]
    generator = iter(lines).__next__
    token_stream = tokenize.tokenize(generator)

    delayed_comma = False
    skip_next_comma = False
    text = []
    add = text.append

    current_parameter = 0
    OP = token.OP
    ERRORTOKEN = token.ERRORTOKEN

    # token stream always starts with ENCODING token, skip it
    t = next(token_stream)
    assert t.type == tokenize.ENCODING

    for t in token_stream:
        type, string = t.type, t.string

        ikiwa type == OP:
            ikiwa string == ',':
                ikiwa skip_next_comma:
                    skip_next_comma = False
                else:
                    assert not delayed_comma
                    delayed_comma = True
                    current_parameter += 1
                continue

            ikiwa string == '/':
                assert not skip_next_comma
                assert last_positional_only is None
                skip_next_comma = True
                last_positional_only = current_parameter - 1
                continue

        ikiwa (type == ERRORTOKEN) and (string == '$'):
            assert self_parameter is None
            self_parameter = current_parameter
            continue

        ikiwa delayed_comma:
            delayed_comma = False
            ikiwa not ((type == OP) and (string == ')')):
                add(', ')
        add(string)
        ikiwa (string == ','):
            add(' ')
    clean_signature = ''.join(text)
    rudisha clean_signature, self_parameter, last_positional_only


eleza _signature_kutokastr(cls, obj, s, skip_bound_arg=True):
    """Private helper to parse content of '__text_signature__'
    and rudisha a Signature based on it.
    """
    # Lazy agiza ast because it's relatively heavy and
    # it's not used for other than this function.
    agiza ast

    Parameter = cls._parameter_cls

    clean_signature, self_parameter, last_positional_only = \
        _signature_strip_non_python_syntax(s)

    program = "eleza foo" + clean_signature + ": pass"

    try:
        module = ast.parse(program)
    except SyntaxError:
        module = None

    ikiwa not isinstance(module, ast.Module):
        raise ValueError("{!r} builtin has invalid signature".format(obj))

    f = module.body[0]

    parameters = []
    empty = Parameter.empty
    invalid = object()

    module = None
    module_dict = {}
    module_name = getattr(obj, '__module__', None)
    ikiwa module_name:
        module = sys.modules.get(module_name, None)
        ikiwa module:
            module_dict = module.__dict__
    sys_module_dict = sys.modules.copy()

    eleza parse_name(node):
        assert isinstance(node, ast.arg)
        ikiwa node.annotation is not None:
            raise ValueError("Annotations are not currently supported")
        rudisha node.arg

    eleza wrap_value(s):
        try:
            value = eval(s, module_dict)
        except NameError:
            try:
                value = eval(s, sys_module_dict)
            except NameError:
                raise RuntimeError()

        ikiwa isinstance(value, (str, int, float, bytes, bool, type(None))):
            rudisha ast.Constant(value)
        raise RuntimeError()

    kundi RewriteSymbolics(ast.NodeTransformer):
        eleza visit_Attribute(self, node):
            a = []
            n = node
            while isinstance(n, ast.Attribute):
                a.append(n.attr)
                n = n.value
            ikiwa not isinstance(n, ast.Name):
                raise RuntimeError()
            a.append(n.id)
            value = ".".join(reversed(a))
            rudisha wrap_value(value)

        eleza visit_Name(self, node):
            ikiwa not isinstance(node.ctx, ast.Load):
                raise ValueError()
            rudisha wrap_value(node.id)

    eleza p(name_node, default_node, default=empty):
        name = parse_name(name_node)
        ikiwa name is invalid:
            rudisha None
        ikiwa default_node and default_node is not _empty:
            try:
                default_node = RewriteSymbolics().visit(default_node)
                o = ast.literal_eval(default_node)
            except ValueError:
                o = invalid
            ikiwa o is invalid:
                rudisha None
            default = o ikiwa o is not invalid else default
        parameters.append(Parameter(name, kind, default=default, annotation=empty))

    # non-keyword-only parameters
    args = reversed(f.args.args)
    defaults = reversed(f.args.defaults)
    iter = itertools.zip_longest(args, defaults, fillvalue=None)
    ikiwa last_positional_only is not None:
        kind = Parameter.POSITIONAL_ONLY
    else:
        kind = Parameter.POSITIONAL_OR_KEYWORD
    for i, (name, default) in enumerate(reversed(list(iter))):
        p(name, default)
        ikiwa i == last_positional_only:
            kind = Parameter.POSITIONAL_OR_KEYWORD

    # *args
    ikiwa f.args.vararg:
        kind = Parameter.VAR_POSITIONAL
        p(f.args.vararg, empty)

    # keyword-only arguments
    kind = Parameter.KEYWORD_ONLY
    for name, default in zip(f.args.kwonlyargs, f.args.kw_defaults):
        p(name, default)

    # **kwargs
    ikiwa f.args.kwarg:
        kind = Parameter.VAR_KEYWORD
        p(f.args.kwarg, empty)

    ikiwa self_parameter is not None:
        # Possibly strip the bound argument:
        #    - We *always* strip first bound argument if
        #      it is a module.
        #    - We don't strip first bound argument if
        #      skip_bound_arg is False.
        assert parameters
        _self = getattr(obj, '__self__', None)
        self_isbound = _self is not None
        self_ismodule = ismodule(_self)
        ikiwa self_isbound and (self_ismodule or skip_bound_arg):
            parameters.pop(0)
        else:
            # for builtins, self parameter is always positional-only!
            p = parameters[0].replace(kind=Parameter.POSITIONAL_ONLY)
            parameters[0] = p

    rudisha cls(parameters, return_annotation=cls.empty)


eleza _signature_kutoka_builtin(cls, func, skip_bound_arg=True):
    """Private helper function to get signature for
    builtin callables.
    """

    ikiwa not _signature_is_builtin(func):
        raise TypeError("{!r} is not a Python builtin "
                        "function".format(func))

    s = getattr(func, "__text_signature__", None)
    ikiwa not s:
        raise ValueError("no signature found for builtin {!r}".format(func))

    rudisha _signature_kutokastr(cls, func, s, skip_bound_arg)


eleza _signature_kutoka_function(cls, func, skip_bound_arg=True):
    """Private helper: constructs Signature for the given python function."""

    is_duck_function = False
    ikiwa not isfunction(func):
        ikiwa _signature_is_functionlike(func):
            is_duck_function = True
        else:
            # If it's not a pure Python function, and not a duck type
            # of pure function:
            raise TypeError('{!r} is not a Python function'.format(func))

    s = getattr(func, "__text_signature__", None)
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
    else:
        pos_default_count = 0

    parameters = []

    non_default_count = pos_count - pos_default_count
    posonly_left = posonly_count

    # Non-keyword-only parameters w/o defaults.
    for name in positional[:non_default_count]:
        kind = _POSITIONAL_ONLY ikiwa posonly_left else _POSITIONAL_OR_KEYWORD
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=kind))
        ikiwa posonly_left:
            posonly_left -= 1

    # ... w/ defaults.
    for offset, name in enumerate(positional[non_default_count:]):
        kind = _POSITIONAL_ONLY ikiwa posonly_left else _POSITIONAL_OR_KEYWORD
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
    for name in keyword_only:
        default = _empty
        ikiwa kwdefaults is not None:
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

    # Is 'func' is a pure Python function - don't validate the
    # parameters list (for correct order and defaults), it should be OK.
    rudisha cls(parameters,
               return_annotation=annotations.get('return', _empty),
               __validate_parameters__=is_duck_function)


eleza _signature_kutoka_callable(obj, *,
                             follow_wrapper_chains=True,
                             skip_bound_arg=True,
                             sigcls):

    """Private helper function to get signature for arbitrary
    callable objects.
    """

    ikiwa not callable(obj):
        raise TypeError('{!r} is not a callable object'.format(obj))

    ikiwa isinstance(obj, types.MethodType):
        # In this case we skip the first parameter of the underlying
        # function (usually `self` or `cls`).
        sig = _signature_kutoka_callable(
            obj.__func__,
            follow_wrapper_chains=follow_wrapper_chains,
            skip_bound_arg=skip_bound_arg,
            sigcls=sigcls)

        ikiwa skip_bound_arg:
            rudisha _signature_bound_method(sig)
        else:
            rudisha sig

    # Was this function wrapped by a decorator?
    ikiwa follow_wrapper_chains:
        obj = unwrap(obj, stop=(lambda f: hasattr(f, "__signature__")))
        ikiwa isinstance(obj, types.MethodType):
            # If the unwrapped object is a *method*, we might want to
            # skip its first parameter (self).
            # See test_signature_wrapped_bound_method for details.
            rudisha _signature_kutoka_callable(
                obj,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)

    try:
        sig = obj.__signature__
    except AttributeError:
        pass
    else:
        ikiwa sig is not None:
            ikiwa not isinstance(sig, Signature):
                raise TypeError(
                    'unexpected object {!r} in __signature__ '
                    'attribute'.format(sig))
            rudisha sig

    try:
        partialmethod = obj._partialmethod
    except AttributeError:
        pass
    else:
        ikiwa isinstance(partialmethod, functools.partialmethod):
            # Unbound partialmethod (see functools.partialmethod)
            # This means, that we need to calculate the signature
            # as ikiwa it's a regular partial object, but taking into
            # account that the first positional argument
            # (usually `self`, or `cls`) will not be passed
            # automatically (as for boundmethods)

            wrapped_sig = _signature_kutoka_callable(
                partialmethod.func,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)

            sig = _signature_get_partial(wrapped_sig, partialmethod, (None,))
            first_wrapped_param = tuple(wrapped_sig.parameters.values())[0]
            ikiwa first_wrapped_param.kind is Parameter.VAR_POSITIONAL:
                # First argument of the wrapped callable is `*args`, as in
                # `partialmethod(lambda *args)`.
                rudisha sig
            else:
                sig_params = tuple(sig.parameters.values())
                assert (not sig_params or
                        first_wrapped_param is not sig_params[0])
                new_params = (first_wrapped_param,) + sig_params
                rudisha sig.replace(parameters=new_params)

    ikiwa isfunction(obj) or _signature_is_functionlike(obj):
        # If it's a pure Python function, or an object that is duck type
        # of a Python function (Cython functions, for instance), then:
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

    sig = None
    ikiwa isinstance(obj, type):
        # obj is a kundi or a metaclass

        # First, let's see ikiwa it has an overloaded __call__ defined
        # in its metaclass
        call = _signature_get_user_defined_method(type(obj), '__call__')
        ikiwa call is not None:
            sig = _signature_kutoka_callable(
                call,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)
        else:
            # Now we check ikiwa the 'obj' kundi has a '__new__' method
            new = _signature_get_user_defined_method(obj, '__new__')
            ikiwa new is not None:
                sig = _signature_kutoka_callable(
                    new,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls)
            else:
                # Finally, we should have at least __init__ implemented
                init = _signature_get_user_defined_method(obj, '__init__')
                ikiwa init is not None:
                    sig = _signature_kutoka_callable(
                        init,
                        follow_wrapper_chains=follow_wrapper_chains,
                        skip_bound_arg=skip_bound_arg,
                        sigcls=sigcls)

        ikiwa sig is None:
            # At this point we know, that `obj` is a class, with no user-
            # defined '__init__', '__new__', or class-level '__call__'

            for base in obj.__mro__[:-1]:
                # Since '__text_signature__' is implemented as a
                # descriptor that extracts text signature kutoka the
                # kundi docstring, ikiwa 'obj' is derived kutoka a builtin
                # class, its own '__text_signature__' may be 'None'.
                # Therefore, we go through the MRO (except the last
                # kundi in there, which is 'object') to find the first
                # kundi with non-empty text signature.
                try:
                    text_sig = base.__text_signature__
                except AttributeError:
                    pass
                else:
                    ikiwa text_sig:
                        # If 'obj' kundi has a __text_signature__ attribute:
                        # rudisha a signature based on it
                        rudisha _signature_kutokastr(sigcls, obj, text_sig)

            # No '__text_signature__' was found for the 'obj' class.
            # Last option is to check ikiwa its '__init__' is
            # object.__init__ or type.__init__.
            ikiwa type not in obj.__mro__:
                # We have a kundi (not metaclass), but no user-defined
                # __init__ or __new__ for it
                ikiwa (obj.__init__ is object.__init__ and
                    obj.__new__ is object.__new__):
                    # Return a signature of 'object' builtin.
                    rudisha sigcls.kutoka_callable(object)
                else:
                    raise ValueError(
                        'no signature found for builtin type {!r}'.format(obj))

    elikiwa not isinstance(obj, _NonUserDefinedCallables):
        # An object with __call__
        # We also check that the 'obj' is not an instance of
        # _WrapperDescriptor or _MethodWrapper to avoid
        # infinite recursion (and even potential segfault)
        call = _signature_get_user_defined_method(type(obj), '__call__')
        ikiwa call is not None:
            try:
                sig = _signature_kutoka_callable(
                    call,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls)
            except ValueError as ex:
                msg = 'no signature found for {!r}'.format(obj)
                raise ValueError(msg) kutoka ex

    ikiwa sig is not None:
        # For classes and objects we skip the first parameter of their
        # __call__, __new__, or __init__ methods
        ikiwa skip_bound_arg:
            rudisha _signature_bound_method(sig)
        else:
            rudisha sig

    ikiwa isinstance(obj, types.BuiltinFunctionType):
        # Raise a nicer error message for builtins
        msg = 'no signature found for builtin function {!r}'.format(obj)
        raise ValueError(msg)

    raise ValueError('callable {!r} is not supported by signature'.format(obj))


kundi _void:
    """A private marker - used in Parameter & Signature."""


kundi _empty:
    """Marker object for Signature.empty and Parameter.empty."""


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
    _POSITIONAL_OR_KEYWORD: 'positional or keyword',
    _VAR_POSITIONAL: 'variadic positional',
    _KEYWORD_ONLY: 'keyword-only',
    _VAR_KEYWORD: 'variadic keyword'
}


kundi Parameter:
    """Represents a parameter in a function signature.

    Has the following public attributes:

    * name : str
        The name of the parameter as a string.
    * default : object
        The default value for the parameter ikiwa specified.  If the
        parameter has no default value, this attribute is set to
        `Parameter.empty`.
    * annotation
        The annotation for the parameter ikiwa specified.  If the
        parameter has no annotation, this attribute is set to
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
        try:
            self._kind = _ParameterKind(kind)
        except ValueError:
            raise ValueError(f'value {kind!r} is not a valid Parameter.kind')
        ikiwa default is not _empty:
            ikiwa self._kind in (_VAR_POSITIONAL, _VAR_KEYWORD):
                msg = '{} parameters cannot have default values'
                msg = msg.format(self._kind.description)
                raise ValueError(msg)
        self._default = default
        self._annotation = annotation

        ikiwa name is _empty:
            raise ValueError('name is a required attribute for Parameter')

        ikiwa not isinstance(name, str):
            msg = 'name must be a str, not a {}'.format(type(name).__name__)
            raise TypeError(msg)

        ikiwa name[0] == '.' and name[1:].isdigit():
            # These are implicit arguments generated by comprehensions. In
            # order to provide a friendlier interface to users, we recast
            # their name as "implicitN" and treat them as positional-only.
            # See issue 19611.
            ikiwa self._kind != _POSITIONAL_OR_KEYWORD:
                msg = (
                    'implicit arguments must be passed as '
                    'positional or keyword arguments, not {}'
                )
                msg = msg.format(self._kind.description)
                raise ValueError(msg)
            self._kind = _POSITIONAL_ONLY
            name = 'implicit{}'.format(name[1:])

        ikiwa not name.isidentifier():
            raise ValueError('{!r} is not a valid parameter name'.format(name))

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

        ikiwa name is _void:
            name = self._name

        ikiwa kind is _void:
            kind = self._kind

        ikiwa annotation is _void:
            annotation = self._annotation

        ikiwa default is _void:
            default = self._default

        rudisha type(self)(name, kind, default=default, annotation=annotation)

    eleza __str__(self):
        kind = self.kind
        formatted = self._name

        # Add annotation and default value
        ikiwa self._annotation is not _empty:
            formatted = '{}: {}'.format(formatted,
                                       formatannotation(self._annotation))

        ikiwa self._default is not _empty:
            ikiwa self._annotation is not _empty:
                formatted = '{} = {}'.format(formatted, repr(self._default))
            else:
                formatted = '{}={}'.format(formatted, repr(self._default))

        ikiwa kind == _VAR_POSITIONAL:
            formatted = '*' + formatted
        elikiwa kind == _VAR_KEYWORD:
            formatted = '**' + formatted

        rudisha formatted

    eleza __repr__(self):
        rudisha '<{} "{}">'.format(self.__class__.__name__, self)

    eleza __hash__(self):
        rudisha hash((self.name, self.kind, self.annotation, self.default))

    eleza __eq__(self, other):
        ikiwa self is other:
            rudisha True
        ikiwa not isinstance(other, Parameter):
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
        Does not contain arguments' default values.
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
        for param_name, param in self._signature.parameters.items():
            ikiwa param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                break

            try:
                arg = self.arguments[param_name]
            except KeyError:
                # We're done here. Other arguments
                # will be mapped in 'BoundArguments.kwargs'
                break
            else:
                ikiwa param.kind == _VAR_POSITIONAL:
                    # *args
                    args.extend(arg)
                else:
                    # plain argument
                    args.append(arg)

        rudisha tuple(args)

    @property
    eleza kwargs(self):
        kwargs = {}
        kwargs_started = False
        for param_name, param in self._signature.parameters.items():
            ikiwa not kwargs_started:
                ikiwa param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                    kwargs_started = True
                else:
                    ikiwa param_name not in self.arguments:
                        kwargs_started = True
                        continue

            ikiwa not kwargs_started:
                continue

            try:
                arg = self.arguments[param_name]
            except KeyError:
                pass
            else:
                ikiwa param.kind == _VAR_KEYWORD:
                    # **kwargs
                    kwargs.update(arg)
                else:
                    # plain keyword argument
                    kwargs[param_name] = arg

        rudisha kwargs

    eleza apply_defaults(self):
        """Set default values for missing arguments.

        For variable-positional arguments (*args) the default is an
        empty tuple.

        For variable-keyword arguments (**kwargs) the default is an
        empty dict.
        """
        arguments = self.arguments
        new_arguments = []
        for name, param in self._signature.parameters.items():
            try:
                new_arguments.append((name, arguments[name]))
            except KeyError:
                ikiwa param.default is not _empty:
                    val = param.default
                elikiwa param.kind is _VAR_POSITIONAL:
                    val = ()
                elikiwa param.kind is _VAR_KEYWORD:
                    val = {}
                else:
                    # This BoundArguments was likely produced by
                    # Signature.bind_partial().
                    continue
                new_arguments.append((name, val))
        self.arguments = OrderedDict(new_arguments)

    eleza __eq__(self, other):
        ikiwa self is other:
            rudisha True
        ikiwa not isinstance(other, BoundArguments):
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
        for arg, value in self.arguments.items():
            args.append('{}={!r}'.format(arg, value))
        rudisha '<{} ({})>'.format(self.__class__.__name__, ', '.join(args))


kundi Signature:
    """A Signature object represents the overall signature of a function.
    It stores a Parameter object for each parameter accepted by the
    function, as well as information specific to the function itself.

    A Signature object has the following public attributes and methods:

    * parameters : OrderedDict
        An ordered mapping of parameters' names to the corresponding
        Parameter objects (keyword-only arguments are in the same order
        as listed in `code.co_varnames`).
    * return_annotation : object
        The annotation for the rudisha type of the function ikiwa specified.
        If the function has no annotation for its rudisha type, this
        attribute is set to `Signature.empty`.
    * bind(*args, **kwargs) -> BoundArguments
        Creates a mapping kutoka positional and keyword arguments to
        parameters.
    * bind_partial(*args, **kwargs) -> BoundArguments
        Creates a partial mapping kutoka positional and keyword arguments
        to parameters (simulating 'functools.partial' behavior.)
    """

    __slots__ = ('_return_annotation', '_parameters')

    _parameter_cls = Parameter
    _bound_arguments_cls = BoundArguments

    empty = _empty

    eleza __init__(self, parameters=None, *, return_annotation=_empty,
                 __validate_parameters__=True):
        """Constructs Signature kutoka the given list of Parameter
        objects and 'return_annotation'.  All arguments are optional.
        """

        ikiwa parameters is None:
            params = OrderedDict()
        else:
            ikiwa __validate_parameters__:
                params = OrderedDict()
                top_kind = _POSITIONAL_ONLY
                kind_defaults = False

                for idx, param in enumerate(parameters):
                    kind = param.kind
                    name = param.name

                    ikiwa kind < top_kind:
                        msg = (
                            'wrong parameter order: {} parameter before {} '
                            'parameter'
                        )
                        msg = msg.format(top_kind.description,
                                         kind.description)
                        raise ValueError(msg)
                    elikiwa kind > top_kind:
                        kind_defaults = False
                        top_kind = kind

                    ikiwa kind in (_POSITIONAL_ONLY, _POSITIONAL_OR_KEYWORD):
                        ikiwa param.default is _empty:
                            ikiwa kind_defaults:
                                # No default for this parameter, but the
                                # previous parameter of the same kind had
                                # a default
                                msg = 'non-default argument follows default ' \
                                      'argument'
                                raise ValueError(msg)
                        else:
                            # There is a default for this parameter.
                            kind_defaults = True

                    ikiwa name in params:
                        msg = 'duplicate parameter name: {!r}'.format(name)
                        raise ValueError(msg)

                    params[name] = param
            else:
                params = OrderedDict(((param.name, param)
                                                for param in parameters))

        self._parameters = types.MappingProxyType(params)
        self._return_annotation = return_annotation

    @classmethod
    eleza kutoka_function(cls, func):
        """Constructs Signature for the given python function.

        Deprecated since Python 3.5, use `Signature.kutoka_callable()`.
        """

        warnings.warn("inspect.Signature.kutoka_function() is deprecated since "
                      "Python 3.5, use Signature.kutoka_callable()",
                      DeprecationWarning, stacklevel=2)
        rudisha _signature_kutoka_function(cls, func)

    @classmethod
    eleza kutoka_builtin(cls, func):
        """Constructs Signature for the given builtin function.

        Deprecated since Python 3.5, use `Signature.kutoka_callable()`.
        """

        warnings.warn("inspect.Signature.kutoka_builtin() is deprecated since "
                      "Python 3.5, use Signature.kutoka_callable()",
                      DeprecationWarning, stacklevel=2)
        rudisha _signature_kutoka_builtin(cls, func)

    @classmethod
    eleza kutoka_callable(cls, obj, *, follow_wrapped=True):
        """Constructs Signature for the given callable object."""
        rudisha _signature_kutoka_callable(obj, sigcls=cls,
                                        follow_wrapper_chains=follow_wrapped)

    @property
    eleza parameters(self):
        rudisha self._parameters

    @property
    eleza return_annotation(self):
        rudisha self._return_annotation

    eleza replace(self, *, parameters=_void, return_annotation=_void):
        """Creates a customized copy of the Signature.
        Pass 'parameters' and/or 'return_annotation' arguments
        to override them in the new copy.
        """

        ikiwa parameters is _void:
            parameters = self.parameters.values()

        ikiwa return_annotation is _void:
            return_annotation = self._return_annotation

        rudisha type(self)(parameters,
                          return_annotation=return_annotation)

    eleza _hash_basis(self):
        params = tuple(param for param in self.parameters.values()
                             ikiwa param.kind != _KEYWORD_ONLY)

        kwo_params = {param.name: param for param in self.parameters.values()
                                        ikiwa param.kind == _KEYWORD_ONLY}

        rudisha params, kwo_params, self.return_annotation

    eleza __hash__(self):
        params, kwo_params, return_annotation = self._hash_basis()
        kwo_params = frozenset(kwo_params.values())
        rudisha hash((params, kwo_params, return_annotation))

    eleza __eq__(self, other):
        ikiwa self is other:
            rudisha True
        ikiwa not isinstance(other, Signature):
            rudisha NotImplemented
        rudisha self._hash_basis() == other._hash_basis()

    eleza _bind(self, args, kwargs, *, partial=False):
        """Private method. Don't use directly."""

        arguments = OrderedDict()

        parameters = iter(self.parameters.values())
        parameters_ex = ()
        arg_vals = iter(args)

        while True:
            # Let's iterate through the positional arguments and corresponding
            # parameters
            try:
                arg_val = next(arg_vals)
            except StopIteration:
                # No more positional arguments
                try:
                    param = next(parameters)
                except StopIteration:
                    # No more parameters. That's it. Just need to check that
                    # we have no `kwargs` after this while loop
                    break
                else:
                    ikiwa param.kind == _VAR_POSITIONAL:
                        # That's OK, just empty *args.  Let's start parsing
                        # kwargs
                        break
                    elikiwa param.name in kwargs:
                        ikiwa param.kind == _POSITIONAL_ONLY:
                            msg = '{arg!r} parameter is positional only, ' \
                                  'but was passed as a keyword'
                            msg = msg.format(arg=param.name)
                            raise TypeError(msg) kutoka None
                        parameters_ex = (param,)
                        break
                    elikiwa (param.kind == _VAR_KEYWORD or
                                                param.default is not _empty):
                        # That's fine too - we have a default value for this
                        # parameter.  So, lets start parsing `kwargs`, starting
                        # with the current parameter
                        parameters_ex = (param,)
                        break
                    else:
                        # No default, not VAR_KEYWORD, not VAR_POSITIONAL,
                        # not in `kwargs`
                        ikiwa partial:
                            parameters_ex = (param,)
                            break
                        else:
                            msg = 'missing a required argument: {arg!r}'
                            msg = msg.format(arg=param.name)
                            raise TypeError(msg) kutoka None
            else:
                # We have a positional argument to process
                try:
                    param = next(parameters)
                except StopIteration:
                    raise TypeError('too many positional arguments') kutoka None
                else:
                    ikiwa param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                        # Looks like we have no parameter for this positional
                        # argument
                        raise TypeError(
                            'too many positional arguments') kutoka None

                    ikiwa param.kind == _VAR_POSITIONAL:
                        # We have an '*args'-like argument, let's fill it with
                        # all positional arguments we have left and move on to
                        # the next phase
                        values = [arg_val]
                        values.extend(arg_vals)
                        arguments[param.name] = tuple(values)
                        break

                    ikiwa param.name in kwargs:
                        raise TypeError(
                            'multiple values for argument {arg!r}'.format(
                                arg=param.name)) kutoka None

                    arguments[param.name] = arg_val

        # Now, we iterate through the remaining parameters to process
        # keyword arguments
        kwargs_param = None
        for param in itertools.chain(parameters_ex, parameters):
            ikiwa param.kind == _VAR_KEYWORD:
                # Memorize that we have a '**kwargs'-like parameter
                kwargs_param = param
                continue

            ikiwa param.kind == _VAR_POSITIONAL:
                # Named arguments don't refer to '*args'-like parameters.
                # We only arrive here ikiwa the positional arguments ended
                # before reaching the last parameter before *args.
                continue

            param_name = param.name
            try:
                arg_val = kwargs.pop(param_name)
            except KeyError:
                # We have no value for this parameter.  It's fine though,
                # ikiwa it has a default value, or it is an '*args'-like
                # parameter, left alone by the processing of positional
                # arguments.
                ikiwa (not partial and param.kind != _VAR_POSITIONAL and
                                                    param.default is _empty):
                    raise TypeError('missing a required argument: {arg!r}'. \
                                    format(arg=param_name)) kutoka None

            else:
                ikiwa param.kind == _POSITIONAL_ONLY:
                    # This should never happen in case of a properly built
                    # Signature object (but let's have this check here
                    # to ensure correct behaviour just in case)
                    raise TypeError('{arg!r} parameter is positional only, '
                                    'but was passed as a keyword'. \
                                    format(arg=param.name))

                arguments[param_name] = arg_val

        ikiwa kwargs:
            ikiwa kwargs_param is not None:
                # Process our '**kwargs'-like parameter
                arguments[kwargs_param.name] = kwargs
            else:
                raise TypeError(
                    'got an unexpected keyword argument {arg!r}'.format(
                        arg=next(iter(kwargs))))

        rudisha self._bound_arguments_cls(self, arguments)

    eleza bind(self, /, *args, **kwargs):
        """Get a BoundArguments object, that maps the passed `args`
        and `kwargs` to the function's signature.  Raises `TypeError`
        ikiwa the passed arguments can not be bound.
        """
        rudisha self._bind(args, kwargs)

    eleza bind_partial(self, /, *args, **kwargs):
        """Get a BoundArguments object, that partially maps the
        passed `args` and `kwargs` to the function's signature.
        Raises `TypeError` ikiwa the passed arguments can not be bound.
        """
        rudisha self._bind(args, kwargs, partial=True)

    eleza __reduce__(self):
        rudisha (type(self),
                (tuple(self._parameters.values()),),
                {'_return_annotation': self._return_annotation})

    eleza __setstate__(self, state):
        self._return_annotation = state['_return_annotation']

    eleza __repr__(self):
        rudisha '<{} {}>'.format(self.__class__.__name__, self)

    eleza __str__(self):
        result = []
        render_pos_only_separator = False
        render_kw_only_separator = True
        for param in self.parameters.values():
            formatted = str(param)

            kind = param.kind

            ikiwa kind == _POSITIONAL_ONLY:
                render_pos_only_separator = True
            elikiwa render_pos_only_separator:
                # It's not a positional-only parameter, and the flag
                # is set to 'True' (there were pos-only params before.)
                result.append('/')
                render_pos_only_separator = False

            ikiwa kind == _VAR_POSITIONAL:
                # OK, we have an '*args'-like parameter, so we won't need
                # a '*' to separate keyword-only arguments
                render_kw_only_separator = False
            elikiwa kind == _KEYWORD_ONLY and render_kw_only_separator:
                # We have a keyword-only parameter to render and we haven't
                # rendered an '*args'-like parameter before, so add a '*'
                # separator to the parameters list ("foo(arg1, *, arg2)" case)
                result.append('*')
                # This condition should be only triggered once, so
                # reset the flag
                render_kw_only_separator = False

            result.append(formatted)

        ikiwa render_pos_only_separator:
            # There were only positional-only parameters, hence the
            # flag was not reset to 'False'
            result.append('/')

        rendered = '({})'.format(', '.join(result))

        ikiwa self.return_annotation is not _empty:
            anno = formatannotation(self.return_annotation)
            rendered += ' -> {}'.format(anno)

        rudisha rendered


eleza signature(obj, *, follow_wrapped=True):
    """Get a signature object for the passed callable."""
    rudisha Signature.kutoka_callable(obj, follow_wrapped=follow_wrapped)


eleza _main():
    """ Logic for inspecting an object given at command line """
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
    try:
        obj = module = importlib.import_module(mod_name)
    except Exception as exc:
        msg = "Failed to agiza {} ({}: {})".format(mod_name,
                                                    type(exc).__name__,
                                                    exc)
        andika(msg, file=sys.stderr)
        sys.exit(2)

    ikiwa has_attrs:
        parts = attrs.split(".")
        obj = module
        for part in parts:
            obj = getattr(obj, part)

    ikiwa module.__name__ in sys.builtin_module_names:
        andika("Can't get info for builtin modules.", file=sys.stderr)
        sys.exit(1)

    ikiwa args.details:
        andika('Target: {}'.format(target))
        andika('Origin: {}'.format(getsourcefile(module)))
        andika('Cached: {}'.format(module.__cached__))
        ikiwa obj is module:
            andika('Loader: {}'.format(repr(module.__loader__)))
            ikiwa hasattr(module, '__path__'):
                andika('Submodule search path: {}'.format(module.__path__))
        else:
            try:
                __, lineno = findsource(obj)
            except Exception:
                pass
            else:
                andika('Line: {}'.format(lineno))

        andika('\n')
    else:
        andika(getsource(obj))


ikiwa __name__ == "__main__":
    _main()
