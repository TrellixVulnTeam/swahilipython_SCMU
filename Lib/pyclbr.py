"""Parse a Python module na describe its classes na functions.

Parse enough of a Python file to recognize imports na kundi and
function definitions, na to find out the superclasses of a class.

The interface consists of a single function:
    readmodule_ex(module, path=Tupu)
where module ni the name of a Python module, na path ni an optional
list of directories where the module ni to be searched.  If present,
path ni prepended to the system search path sys.path.  The rudisha value
is a dictionary.  The keys of the dictionary are the names of the
classes na functions defined kwenye the module (including classes that are
defined via the kutoka XXX agiza YYY construct).  The values are
instances of classes Class na Function.  One special key/value pair is
present kila packages: the key '__path__' has a list as its value which
contains the package search path.

Classes na Functions have a common superclass: _Object.  Every instance
has the following attributes:
    module  -- name of the module;
    name    -- name of the object;
    file    -- file kwenye which the object ni defined;
    lineno  -- line kwenye the file where the object's definition starts;
    parent  -- parent of this object, ikiwa any;
    children -- nested objects contained kwenye this object.
The 'children' attribute ni a dictionary mapping names to objects.

Instances of Function describe functions ukijumuisha the attributes kutoka _Object.

Instances of Class describe classes ukijumuisha the attributes kutoka _Object,
plus the following:
    super   -- list of super classes (Class instances ikiwa possible);
    methods -- mapping of method names to beginning line numbers.
If the name of a super kundi ni sio recognized, the corresponding
entry kwenye the list of super classes ni sio a kundi instance but a
string giving the name of the super class.  Since agiza statements
are recognized na imported modules are scanned as well, this
shouldn't happen often.
"""

agiza io
agiza sys
agiza importlib.util
agiza tokenize
kutoka token agiza NAME, DEDENT, OP

__all__ = ["readmodule", "readmodule_ex", "Class", "Function"]

_modules = {}  # Initialize cache of modules we've seen.


kundi _Object:
    "Information about Python kundi ama function."
    eleza __init__(self, module, name, file, lineno, parent):
        self.module = module
        self.name = name
        self.file = file
        self.lineno = lineno
        self.parent = parent
        self.children = {}

    eleza _addchild(self, name, obj):
        self.children[name] = obj


kundi Function(_Object):
    "Information about a Python function, including methods."
    eleza __init__(self, module, name, file, lineno, parent=Tupu):
        _Object.__init__(self, module, name, file, lineno, parent)


kundi Class(_Object):
    "Information about a Python class."
    eleza __init__(self, module, name, super, file, lineno, parent=Tupu):
        _Object.__init__(self, module, name, file, lineno, parent)
        self.super = [] ikiwa super ni Tupu isipokua super
        self.methods = {}

    eleza _addmethod(self, name, lineno):
        self.methods[name] = lineno


eleza _nest_function(ob, func_name, lineno):
    "Return a Function after nesting within ob."
    newfunc = Function(ob.module, func_name, ob.file, lineno, ob)
    ob._addchild(func_name, newfunc)
    ikiwa isinstance(ob, Class):
        ob._addmethod(func_name, lineno)
    rudisha newfunc

eleza _nest_class(ob, class_name, lineno, super=Tupu):
    "Return a Class after nesting within ob."
    newkundi = Class(ob.module, class_name, super, ob.file, lineno, ob)
    ob._addchild(class_name, newclass)
    rudisha newclass

eleza readmodule(module, path=Tupu):
    """Return Class objects kila the top-level classes kwenye module.

    This ni the original interface, before Functions were added.
    """

    res = {}
    kila key, value kwenye _readmodule(module, path ama []).items():
        ikiwa isinstance(value, Class):
            res[key] = value
    rudisha res

eleza readmodule_ex(module, path=Tupu):
    """Return a dictionary ukijumuisha all functions na classes kwenye module.

    Search kila module kwenye PATH + sys.path.
    If possible, include imported superclasses.
    Do this by reading source, without importing (and executing) it.
    """
    rudisha _readmodule(module, path ama [])

eleza _readmodule(module, path, inpackage=Tupu):
    """Do the hard work kila readmodule[_ex].

    If inpackage ni given, it must be the dotted name of the package in
    which we are searching kila a submodule, na then PATH must be the
    package search path; otherwise, we are searching kila a top-level
    module, na path ni combined ukijumuisha sys.path.
    """
    # Compute the full module name (prepending inpackage ikiwa set).
    ikiwa inpackage ni sio Tupu:
        fullmodule = "%s.%s" % (inpackage, module)
    isipokua:
        fullmodule = module

    # Check kwenye the cache.
    ikiwa fullmodule kwenye _modules:
        rudisha _modules[fullmodule]

    # Initialize the dict kila this module's contents.
    tree = {}

    # Check ikiwa it ni a built-in module; we don't do much kila these.
    ikiwa module kwenye sys.builtin_module_names na inpackage ni Tupu:
        _modules[module] = tree
        rudisha tree

    # Check kila a dotted module name.
    i = module.rfind('.')
    ikiwa i >= 0:
        package = module[:i]
        submodule = module[i+1:]
        parent = _readmodule(package, path, inpackage)
        ikiwa inpackage ni sio Tupu:
            package = "%s.%s" % (inpackage, package)
        ikiwa sio '__path__' kwenye parent:
             ashiria ImportError('No package named {}'.format(package))
        rudisha _readmodule(submodule, parent['__path__'], package)

    # Search the path kila the module.
    f = Tupu
    ikiwa inpackage ni sio Tupu:
        search_path = path
    isipokua:
        search_path = path + sys.path
    spec = importlib.util._find_spec_from_path(fullmodule, search_path)
    ikiwa spec ni Tupu:
         ashiria ModuleNotFoundError(f"no module named {fullmodule!r}", name=fullmodule)
    _modules[fullmodule] = tree
    # Is module a package?
    ikiwa spec.submodule_search_locations ni sio Tupu:
        tree['__path__'] = spec.submodule_search_locations
    jaribu:
        source = spec.loader.get_source(fullmodule)
    except (AttributeError, ImportError):
        # If module ni sio Python source, we cannot do anything.
        rudisha tree
    isipokua:
        ikiwa source ni Tupu:
            rudisha tree

    fname = spec.loader.get_filename(fullmodule)
    rudisha _create_tree(fullmodule, path, fname, source, tree, inpackage)


eleza _create_tree(fullmodule, path, fname, source, tree, inpackage):
    """Return the tree kila a particular module.

    fullmodule (full module name), inpackage+module, becomes o.module.
    path ni passed to recursive calls of _readmodule.
    fname becomes o.file.
    source ni tokenized.  Imports cause recursive calls to _readmodule.
    tree ni {} ama {'__path__': <submodule search locations>}.
    inpackage, Tupu ama string, ni passed to recursive calls of _readmodule.

    The effect of recursive calls ni mutation of global _modules.
    """
    f = io.StringIO(source)

    stack = [] # Initialize stack of (class, indent) pairs.

    g = tokenize.generate_tokens(f.readline)
    jaribu:
        kila tokentype, token, start, _end, _line kwenye g:
            ikiwa tokentype == DEDENT:
                lineno, thisindent = start
                # Close previous nested classes na defs.
                wakati stack na stack[-1][1] >= thisindent:
                    toa stack[-1]
            elikiwa token == 'def':
                lineno, thisindent = start
                # Close previous nested classes na defs.
                wakati stack na stack[-1][1] >= thisindent:
                    toa stack[-1]
                tokentype, func_name, start = next(g)[0:3]
                ikiwa tokentype != NAME:
                    endelea  # Skip eleza ukijumuisha syntax error.
                cur_func = Tupu
                ikiwa stack:
                    cur_obj = stack[-1][0]
                    cur_func = _nest_function(cur_obj, func_name, lineno)
                isipokua:
                    # It ni just a function.
                    cur_func = Function(fullmodule, func_name, fname, lineno)
                    tree[func_name] = cur_func
                stack.append((cur_func, thisindent))
            elikiwa token == 'class':
                lineno, thisindent = start
                # Close previous nested classes na defs.
                wakati stack na stack[-1][1] >= thisindent:
                    toa stack[-1]
                tokentype, class_name, start = next(g)[0:3]
                ikiwa tokentype != NAME:
                    endelea # Skip kundi ukijumuisha syntax error.
                # Parse what follows the kundi name.
                tokentype, token, start = next(g)[0:3]
                inherit = Tupu
                ikiwa token == '(':
                    names = [] # Initialize list of superclasses.
                    level = 1
                    super = [] # Tokens making up current superclass.
                    wakati Kweli:
                        tokentype, token, start = next(g)[0:3]
                        ikiwa token kwenye (')', ',') na level == 1:
                            n = "".join(super)
                            ikiwa n kwenye tree:
                                # We know this super class.
                                n = tree[n]
                            isipokua:
                                c = n.split('.')
                                ikiwa len(c) > 1:
                                    # Super kundi form ni module.class:
                                    # look kwenye module kila class.
                                    m = c[-2]
                                    c = c[-1]
                                    ikiwa m kwenye _modules:
                                        d = _modules[m]
                                        ikiwa c kwenye d:
                                            n = d[c]
                            names.append(n)
                            super = []
                        ikiwa token == '(':
                            level += 1
                        elikiwa token == ')':
                            level -= 1
                            ikiwa level == 0:
                                koma
                        elikiwa token == ',' na level == 1:
                            pass
                        # Only use NAME na OP (== dot) tokens kila type name.
                        elikiwa tokentype kwenye (NAME, OP) na level == 1:
                            super.append(token)
                        # Expressions kwenye the base list are sio supported.
                    inherit = names
                ikiwa stack:
                    cur_obj = stack[-1][0]
                    cur_kundi = _nest_class(
                            cur_obj, class_name, lineno, inherit)
                isipokua:
                    cur_kundi = Class(fullmodule, class_name, inherit,
                                      fname, lineno)
                    tree[class_name] = cur_class
                stack.append((cur_class, thisindent))
            elikiwa token == 'import' na start[1] == 0:
                modules = _getnamelist(g)
                kila mod, _mod2 kwenye modules:
                    jaribu:
                        # Recursively read the imported module.
                        ikiwa inpackage ni Tupu:
                            _readmodule(mod, path)
                        isipokua:
                            jaribu:
                                _readmodule(mod, path, inpackage)
                            except ImportError:
                                _readmodule(mod, [])
                    tatizo:
                        # If we can't find ama parse the imported module,
                        # too bad -- don't die here.
                        pass
            elikiwa token == 'from' na start[1] == 0:
                mod, token = _getname(g)
                ikiwa sio mod ama token != "import":
                    endelea
                names = _getnamelist(g)
                jaribu:
                    # Recursively read the imported module.
                    d = _readmodule(mod, path, inpackage)
                tatizo:
                    # If we can't find ama parse the imported module,
                    # too bad -- don't die here.
                    endelea
                # Add any classes that were defined kwenye the imported module
                # to our name space ikiwa they were mentioned kwenye the list.
                kila n, n2 kwenye names:
                    ikiwa n kwenye d:
                        tree[n2 ama n] = d[n]
                    elikiwa n == '*':
                        # Don't add names that start ukijumuisha _.
                        kila n kwenye d:
                            ikiwa n[0] != '_':
                                tree[n] = d[n]
    except StopIteration:
        pass

    f.close()
    rudisha tree


eleza _getnamelist(g):
    """Return list of (dotted-name, as-name ama Tupu) tuples kila token source g.

    An as-name ni the name that follows 'as' kwenye an as clause.
    """
    names = []
    wakati Kweli:
        name, token = _getname(g)
        ikiwa sio name:
            koma
        ikiwa token == 'as':
            name2, token = _getname(g)
        isipokua:
            name2 = Tupu
        names.append((name, name2))
        wakati token != "," na "\n" sio kwenye token:
            token = next(g)[1]
        ikiwa token != ",":
            koma
    rudisha names


eleza _getname(g):
    "Return (dotted-name ama Tupu, next-token) tuple kila token source g."
    parts = []
    tokentype, token = next(g)[0:2]
    ikiwa tokentype != NAME na token != '*':
        rudisha (Tupu, token)
    parts.append(token)
    wakati Kweli:
        tokentype, token = next(g)[0:2]
        ikiwa token != '.':
            koma
        tokentype, token = next(g)[0:2]
        ikiwa tokentype != NAME:
            koma
        parts.append(token)
    rudisha (".".join(parts), token)


eleza _main():
    "Print module output (default this file) kila quick visual check."
    agiza os
    jaribu:
        mod = sys.argv[1]
    tatizo:
        mod = __file__
    ikiwa os.path.exists(mod):
        path = [os.path.dirname(mod)]
        mod = os.path.basename(mod)
        ikiwa mod.lower().endswith(".py"):
            mod = mod[:-3]
    isipokua:
        path = []
    tree = readmodule_ex(mod, path)
    lineno_key = lambda a: getattr(a, 'lineno', 0)
    objs = sorted(tree.values(), key=lineno_key, reverse=Kweli)
    indent_level = 2
    wakati objs:
        obj = objs.pop()
        ikiwa isinstance(obj, list):
            # Value ni a __path__ key.
            endelea
        ikiwa sio hasattr(obj, 'indent'):
            obj.indent = 0

        ikiwa isinstance(obj, _Object):
            new_objs = sorted(obj.children.values(),
                              key=lineno_key, reverse=Kweli)
            kila ob kwenye new_objs:
                ob.indent = obj.indent + indent_level
            objs.extend(new_objs)
        ikiwa isinstance(obj, Class):
            andika("{}kundi {} {} {}"
                  .format(' ' * obj.indent, obj.name, obj.super, obj.lineno))
        elikiwa isinstance(obj, Function):
            andika("{}eleza {} {}".format(' ' * obj.indent, obj.name, obj.lineno))

ikiwa __name__ == "__main__":
    _main()
