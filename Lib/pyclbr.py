"""Parse a Python module and describe its classes and functions.

Parse enough of a Python file to recognize agizas and kundi and
function definitions, and to find out the superclasses of a class.

The interface consists of a single function:
    readmodule_ex(module, path=None)
where module is the name of a Python module, and path is an optional
list of directories where the module is to be searched.  If present,
path is prepended to the system search path sys.path.  The rudisha value
is a dictionary.  The keys of the dictionary are the names of the
classes and functions defined in the module (including classes that are
defined via the kutoka XXX agiza YYY construct).  The values are
instances of classes Class and Function.  One special key/value pair is
present for packages: the key '__path__' has a list as its value which
contains the package search path.

Classes and Functions have a common superclass: _Object.  Every instance
has the following attributes:
    module  -- name of the module;
    name    -- name of the object;
    file    -- file in which the object is defined;
    lineno  -- line in the file where the object's definition starts;
    parent  -- parent of this object, ikiwa any;
    children -- nested objects contained in this object.
The 'children' attribute is a dictionary mapping names to objects.

Instances of Function describe functions with the attributes kutoka _Object.

Instances of Class describe classes with the attributes kutoka _Object,
plus the following:
    super   -- list of super classes (Class instances ikiwa possible);
    methods -- mapping of method names to beginning line numbers.
If the name of a super kundi is not recognized, the corresponding
entry in the list of super classes is not a kundi instance but a
string giving the name of the super class.  Since agiza statements
are recognized and imported modules are scanned as well, this
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
    "Information about Python kundi or function."
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
    eleza __init__(self, module, name, file, lineno, parent=None):
        _Object.__init__(self, module, name, file, lineno, parent)


kundi Class(_Object):
    "Information about a Python class."
    eleza __init__(self, module, name, super, file, lineno, parent=None):
        _Object.__init__(self, module, name, file, lineno, parent)
        self.super = [] ikiwa super is None else super
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

eleza _nest_class(ob, class_name, lineno, super=None):
    "Return a Class after nesting within ob."
    newkundi = Class(ob.module, class_name, super, ob.file, lineno, ob)
    ob._addchild(class_name, newclass)
    rudisha newclass

eleza readmodule(module, path=None):
    """Return Class objects for the top-level classes in module.

    This is the original interface, before Functions were added.
    """

    res = {}
    for key, value in _readmodule(module, path or []).items():
        ikiwa isinstance(value, Class):
            res[key] = value
    rudisha res

eleza readmodule_ex(module, path=None):
    """Return a dictionary with all functions and classes in module.

    Search for module in PATH + sys.path.
    If possible, include imported superclasses.
    Do this by reading source, without agizaing (and executing) it.
    """
    rudisha _readmodule(module, path or [])

eleza _readmodule(module, path, inpackage=None):
    """Do the hard work for readmodule[_ex].

    If inpackage is given, it must be the dotted name of the package in
    which we are searching for a submodule, and then PATH must be the
    package search path; otherwise, we are searching for a top-level
    module, and path is combined with sys.path.
    """
    # Compute the full module name (prepending inpackage ikiwa set).
    ikiwa inpackage is not None:
        fullmodule = "%s.%s" % (inpackage, module)
    else:
        fullmodule = module

    # Check in the cache.
    ikiwa fullmodule in _modules:
        rudisha _modules[fullmodule]

    # Initialize the dict for this module's contents.
    tree = {}

    # Check ikiwa it is a built-in module; we don't do much for these.
    ikiwa module in sys.builtin_module_names and inpackage is None:
        _modules[module] = tree
        rudisha tree

    # Check for a dotted module name.
    i = module.rfind('.')
    ikiwa i >= 0:
        package = module[:i]
        submodule = module[i+1:]
        parent = _readmodule(package, path, inpackage)
        ikiwa inpackage is not None:
            package = "%s.%s" % (inpackage, package)
        ikiwa not '__path__' in parent:
            raise ImportError('No package named {}'.format(package))
        rudisha _readmodule(submodule, parent['__path__'], package)

    # Search the path for the module.
    f = None
    ikiwa inpackage is not None:
        search_path = path
    else:
        search_path = path + sys.path
    spec = importlib.util._find_spec_kutoka_path(fullmodule, search_path)
    ikiwa spec is None:
        raise ModuleNotFoundError(f"no module named {fullmodule!r}", name=fullmodule)
    _modules[fullmodule] = tree
    # Is module a package?
    ikiwa spec.submodule_search_locations is not None:
        tree['__path__'] = spec.submodule_search_locations
    try:
        source = spec.loader.get_source(fullmodule)
    except (AttributeError, ImportError):
        # If module is not Python source, we cannot do anything.
        rudisha tree
    else:
        ikiwa source is None:
            rudisha tree

    fname = spec.loader.get_filename(fullmodule)
    rudisha _create_tree(fullmodule, path, fname, source, tree, inpackage)


eleza _create_tree(fullmodule, path, fname, source, tree, inpackage):
    """Return the tree for a particular module.

    fullmodule (full module name), inpackage+module, becomes o.module.
    path is passed to recursive calls of _readmodule.
    fname becomes o.file.
    source is tokenized.  Imports cause recursive calls to _readmodule.
    tree is {} or {'__path__': <submodule search locations>}.
    inpackage, None or string, is passed to recursive calls of _readmodule.

    The effect of recursive calls is mutation of global _modules.
    """
    f = io.StringIO(source)

    stack = [] # Initialize stack of (class, indent) pairs.

    g = tokenize.generate_tokens(f.readline)
    try:
        for tokentype, token, start, _end, _line in g:
            ikiwa tokentype == DEDENT:
                lineno, thisindent = start
                # Close previous nested classes and defs.
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]
            elikiwa token == 'def':
                lineno, thisindent = start
                # Close previous nested classes and defs.
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]
                tokentype, func_name, start = next(g)[0:3]
                ikiwa tokentype != NAME:
                    continue  # Skip eleza with syntax error.
                cur_func = None
                ikiwa stack:
                    cur_obj = stack[-1][0]
                    cur_func = _nest_function(cur_obj, func_name, lineno)
                else:
                    # It is just a function.
                    cur_func = Function(fullmodule, func_name, fname, lineno)
                    tree[func_name] = cur_func
                stack.append((cur_func, thisindent))
            elikiwa token == 'class':
                lineno, thisindent = start
                # Close previous nested classes and defs.
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]
                tokentype, class_name, start = next(g)[0:3]
                ikiwa tokentype != NAME:
                    continue # Skip kundi with syntax error.
                # Parse what follows the kundi name.
                tokentype, token, start = next(g)[0:3]
                inherit = None
                ikiwa token == '(':
                    names = [] # Initialize list of superclasses.
                    level = 1
                    super = [] # Tokens making up current superclass.
                    while True:
                        tokentype, token, start = next(g)[0:3]
                        ikiwa token in (')', ',') and level == 1:
                            n = "".join(super)
                            ikiwa n in tree:
                                # We know this super class.
                                n = tree[n]
                            else:
                                c = n.split('.')
                                ikiwa len(c) > 1:
                                    # Super kundi form is module.class:
                                    # look in module for class.
                                    m = c[-2]
                                    c = c[-1]
                                    ikiwa m in _modules:
                                        d = _modules[m]
                                        ikiwa c in d:
                                            n = d[c]
                            names.append(n)
                            super = []
                        ikiwa token == '(':
                            level += 1
                        elikiwa token == ')':
                            level -= 1
                            ikiwa level == 0:
                                break
                        elikiwa token == ',' and level == 1:
                            pass
                        # Only use NAME and OP (== dot) tokens for type name.
                        elikiwa tokentype in (NAME, OP) and level == 1:
                            super.append(token)
                        # Expressions in the base list are not supported.
                    inherit = names
                ikiwa stack:
                    cur_obj = stack[-1][0]
                    cur_kundi = _nest_class(
                            cur_obj, class_name, lineno, inherit)
                else:
                    cur_kundi = Class(fullmodule, class_name, inherit,
                                      fname, lineno)
                    tree[class_name] = cur_class
                stack.append((cur_class, thisindent))
            elikiwa token == 'agiza' and start[1] == 0:
                modules = _getnamelist(g)
                for mod, _mod2 in modules:
                    try:
                        # Recursively read the imported module.
                        ikiwa inpackage is None:
                            _readmodule(mod, path)
                        else:
                            try:
                                _readmodule(mod, path, inpackage)
                            except ImportError:
                                _readmodule(mod, [])
                    except:
                        # If we can't find or parse the imported module,
                        # too bad -- don't die here.
                        pass
            elikiwa token == 'kutoka' and start[1] == 0:
                mod, token = _getname(g)
                ikiwa not mod or token != "agiza":
                    continue
                names = _getnamelist(g)
                try:
                    # Recursively read the imported module.
                    d = _readmodule(mod, path, inpackage)
                except:
                    # If we can't find or parse the imported module,
                    # too bad -- don't die here.
                    continue
                # Add any classes that were defined in the imported module
                # to our name space ikiwa they were mentioned in the list.
                for n, n2 in names:
                    ikiwa n in d:
                        tree[n2 or n] = d[n]
                    elikiwa n == '*':
                        # Don't add names that start with _.
                        for n in d:
                            ikiwa n[0] != '_':
                                tree[n] = d[n]
    except StopIteration:
        pass

    f.close()
    rudisha tree


eleza _getnamelist(g):
    """Return list of (dotted-name, as-name or None) tuples for token source g.

    An as-name is the name that follows 'as' in an as clause.
    """
    names = []
    while True:
        name, token = _getname(g)
        ikiwa not name:
            break
        ikiwa token == 'as':
            name2, token = _getname(g)
        else:
            name2 = None
        names.append((name, name2))
        while token != "," and "\n" not in token:
            token = next(g)[1]
        ikiwa token != ",":
            break
    rudisha names


eleza _getname(g):
    "Return (dotted-name or None, next-token) tuple for token source g."
    parts = []
    tokentype, token = next(g)[0:2]
    ikiwa tokentype != NAME and token != '*':
        rudisha (None, token)
    parts.append(token)
    while True:
        tokentype, token = next(g)[0:2]
        ikiwa token != '.':
            break
        tokentype, token = next(g)[0:2]
        ikiwa tokentype != NAME:
            break
        parts.append(token)
    rudisha (".".join(parts), token)


eleza _main():
    "Print module output (default this file) for quick visual check."
    agiza os
    try:
        mod = sys.argv[1]
    except:
        mod = __file__
    ikiwa os.path.exists(mod):
        path = [os.path.dirname(mod)]
        mod = os.path.basename(mod)
        ikiwa mod.lower().endswith(".py"):
            mod = mod[:-3]
    else:
        path = []
    tree = readmodule_ex(mod, path)
    lineno_key = lambda a: getattr(a, 'lineno', 0)
    objs = sorted(tree.values(), key=lineno_key, reverse=True)
    indent_level = 2
    while objs:
        obj = objs.pop()
        ikiwa isinstance(obj, list):
            # Value is a __path__ key.
            continue
        ikiwa not hasattr(obj, 'indent'):
            obj.indent = 0

        ikiwa isinstance(obj, _Object):
            new_objs = sorted(obj.children.values(),
                              key=lineno_key, reverse=True)
            for ob in new_objs:
                ob.indent = obj.indent + indent_level
            objs.extend(new_objs)
        ikiwa isinstance(obj, Class):
            andika("{}kundi {} {} {}"
                  .format(' ' * obj.indent, obj.name, obj.super, obj.lineno))
        elikiwa isinstance(obj, Function):
            andika("{}eleza {} {}".format(' ' * obj.indent, obj.name, obj.lineno))

ikiwa __name__ == "__main__":
    _main()
