#!/usr/bin/env python3
"""Generate Python documentation in HTML or text for interactive use.

At the Python interactive prompt, calling help(thing) on a Python object
documents the object, and calling help() starts up an interactive
help session.

Or, at the shell command line outside of Python:

Run "pydoc <name>" to show documentation on something.  <name> may be
the name of a function, module, package, or a dotted reference to a
kundi or function within a module or module in a package.  If the
argument contains a path segment delimiter (e.g. slash on Unix,
backslash on Windows) it is treated as the path to a Python source file.

Run "pydoc -k <keyword>" to search for a keyword in the synopsis lines
of all available modules.

Run "pydoc -n <hostname>" to start an HTTP server with the given
hostname (default: localhost) on the local machine.

Run "pydoc -p <port>" to start an HTTP server on the given port on the
local machine.  Port number 0 can be used to get an arbitrary unused port.

Run "pydoc -b" to start an HTTP server on an arbitrary unused port and
open a Web browser to interactively browse documentation.  Combine with
the -n and -p options to control the hostname and port used.

Run "pydoc -w <name>" to write out the HTML documentation for a module
to a file named "<name>.html".

Module docs for core modules are assumed to be in

    https://docs.python.org/X.Y/library/

This can be overridden by setting the PYTHONDOCS environment variable
to a different URL or to a local directory containing the Library
Reference Manual pages.
"""
__all__ = ['help']
__author__ = "Ka-Ping Yee <ping@lfw.org>"
__date__ = "26 February 2001"

__credits__ = """Guido van Rossum, for an excellent programming language.
Tommy Burnette, the original creator of manpy.
Paul Prescod, for all his work on onlinehelp.
Richard Chamberlain, for the first implementation of textdoc.
"""

# Known bugs that can't be fixed here:
#   - synopsis() cannot be prevented kutoka clobbering existing
#     loaded modules.
#   - If the __file__ attribute on a module is a relative path and
#     the current directory is changed with os.chdir(), an incorrect
#     path will be displayed.

agiza builtins
agiza importlib._bootstrap
agiza importlib._bootstrap_external
agiza importlib.machinery
agiza importlib.util
agiza inspect
agiza io
agiza os
agiza pkgutil
agiza platform
agiza re
agiza sys
agiza time
agiza tokenize
agiza urllib.parse
agiza warnings
kutoka collections agiza deque
kutoka reprlib agiza Repr
kutoka traceback agiza format_exception_only


# --------------------------------------------------------- common routines

eleza pathdirs():
    """Convert sys.path into a list of absolute, existing, unique paths."""
    dirs = []
    normdirs = []
    for dir in sys.path:
        dir = os.path.abspath(dir or '.')
        normdir = os.path.normcase(dir)
        ikiwa normdir not in normdirs and os.path.isdir(dir):
            dirs.append(dir)
            normdirs.append(normdir)
    rudisha dirs

eleza getdoc(object):
    """Get the doc string or comments for an object."""
    result = inspect.getdoc(object) or inspect.getcomments(object)
    rudisha result and re.sub('^ *\n', '', result.rstrip()) or ''

eleza splitdoc(doc):
    """Split a doc string into a synopsis line (ikiwa any) and the rest."""
    lines = doc.strip().split('\n')
    ikiwa len(lines) == 1:
        rudisha lines[0], ''
    elikiwa len(lines) >= 2 and not lines[1].rstrip():
        rudisha lines[0], '\n'.join(lines[2:])
    rudisha '', '\n'.join(lines)

eleza classname(object, modname):
    """Get a kundi name and qualify it with a module name ikiwa necessary."""
    name = object.__name__
    ikiwa object.__module__ != modname:
        name = object.__module__ + '.' + name
    rudisha name

eleza isdata(object):
    """Check ikiwa an object is of a type that probably means it's data."""
    rudisha not (inspect.ismodule(object) or inspect.isclass(object) or
                inspect.isroutine(object) or inspect.isframe(object) or
                inspect.istraceback(object) or inspect.iscode(object))

eleza replace(text, *pairs):
    """Do a series of global replacements on a string."""
    while pairs:
        text = pairs[1].join(text.split(pairs[0]))
        pairs = pairs[2:]
    rudisha text

eleza cram(text, maxlen):
    """Omit part of a string ikiwa needed to make it fit in a maximum length."""
    ikiwa len(text) > maxlen:
        pre = max(0, (maxlen-3)//2)
        post = max(0, maxlen-3-pre)
        rudisha text[:pre] + '...' + text[len(text)-post:]
    rudisha text

_re_stripid = re.compile(r' at 0x[0-9a-f]{6,16}(>+)$', re.IGNORECASE)
eleza stripid(text):
    """Remove the hexadecimal id kutoka a Python object representation."""
    # The behaviour of %p is implementation-dependent in terms of case.
    rudisha _re_stripid.sub(r'\1', text)

eleza _is_bound_method(fn):
    """
    Returns True ikiwa fn is a bound method, regardless of whether
    fn was implemented in Python or in C.
    """
    ikiwa inspect.ismethod(fn):
        rudisha True
    ikiwa inspect.isbuiltin(fn):
        self = getattr(fn, '__self__', None)
        rudisha not (inspect.ismodule(self) or (self is None))
    rudisha False


eleza allmethods(cl):
    methods = {}
    for key, value in inspect.getmembers(cl, inspect.isroutine):
        methods[key] = 1
    for base in cl.__bases__:
        methods.update(allmethods(base)) # all your base are belong to us
    for key in methods.keys():
        methods[key] = getattr(cl, key)
    rudisha methods

eleza _split_list(s, predicate):
    """Split sequence s via predicate, and rudisha pair ([true], [false]).

    The rudisha value is a 2-tuple of lists,
        ([x for x in s ikiwa predicate(x)],
         [x for x in s ikiwa not predicate(x)])
    """

    yes = []
    no = []
    for x in s:
        ikiwa predicate(x):
            yes.append(x)
        else:
            no.append(x)
    rudisha yes, no

eleza visiblename(name, all=None, obj=None):
    """Decide whether to show documentation on a variable."""
    # Certain special names are redundant or internal.
    # XXX Remove __initializing__?
    ikiwa name in {'__author__', '__builtins__', '__cached__', '__credits__',
                '__date__', '__doc__', '__file__', '__spec__',
                '__loader__', '__module__', '__name__', '__package__',
                '__path__', '__qualname__', '__slots__', '__version__'}:
        rudisha 0
    # Private names are hidden, but special names are displayed.
    ikiwa name.startswith('__') and name.endswith('__'): rudisha 1
    # Namedtuples have public fields and methods with a single leading underscore
    ikiwa name.startswith('_') and hasattr(obj, '_fields'):
        rudisha True
    ikiwa all is not None:
        # only document that which the programmer exported in __all__
        rudisha name in all
    else:
        rudisha not name.startswith('_')

eleza classify_class_attrs(object):
    """Wrap inspect.classify_class_attrs, with fixup for data descriptors."""
    results = []
    for (name, kind, cls, value) in inspect.classify_class_attrs(object):
        ikiwa inspect.isdatadescriptor(value):
            kind = 'data descriptor'
            ikiwa isinstance(value, property) and value.fset is None:
                kind = 'readonly property'
        results.append((name, kind, cls, value))
    rudisha results

eleza sort_attributes(attrs, object):
    'Sort the attrs list in-place by _fields and then alphabetically by name'
    # This allows data descriptors to be ordered according
    # to a _fields attribute ikiwa present.
    fields = getattr(object, '_fields', [])
    try:
        field_order = {name : i-len(fields) for (i, name) in enumerate(fields)}
    except TypeError:
        field_order = {}
    keyfunc = lambda attr: (field_order.get(attr[0], 0), attr[0])
    attrs.sort(key=keyfunc)

# ----------------------------------------------------- module manipulation

eleza ispackage(path):
    """Guess whether a path refers to a package directory."""
    ikiwa os.path.isdir(path):
        for ext in ('.py', '.pyc'):
            ikiwa os.path.isfile(os.path.join(path, '__init__' + ext)):
                rudisha True
    rudisha False

eleza source_synopsis(file):
    line = file.readline()
    while line[:1] == '#' or not line.strip():
        line = file.readline()
        ikiwa not line: break
    line = line.strip()
    ikiwa line[:4] == 'r"""': line = line[1:]
    ikiwa line[:3] == '"""':
        line = line[3:]
        ikiwa line[-1:] == '\\': line = line[:-1]
        while not line.strip():
            line = file.readline()
            ikiwa not line: break
        result = line.split('"""')[0].strip()
    else: result = None
    rudisha result

eleza synopsis(filename, cache={}):
    """Get the one-line summary out of a module file."""
    mtime = os.stat(filename).st_mtime
    lastupdate, result = cache.get(filename, (None, None))
    ikiwa lastupdate is None or lastupdate < mtime:
        # Look for binary suffixes first, falling back to source.
        ikiwa filename.endswith(tuple(importlib.machinery.BYTECODE_SUFFIXES)):
            loader_cls = importlib.machinery.SourcelessFileLoader
        elikiwa filename.endswith(tuple(importlib.machinery.EXTENSION_SUFFIXES)):
            loader_cls = importlib.machinery.ExtensionFileLoader
        else:
            loader_cls = None
        # Now handle the choice.
        ikiwa loader_cls is None:
            # Must be a source file.
            try:
                file = tokenize.open(filename)
            except OSError:
                # module can't be opened, so skip it
                rudisha None
            # text modules can be directly examined
            with file:
                result = source_synopsis(file)
        else:
            # Must be a binary module, which has to be imported.
            loader = loader_cls('__temp__', filename)
            # XXX We probably don't need to pass in the loader here.
            spec = importlib.util.spec_kutoka_file_location('__temp__', filename,
                                                          loader=loader)
            try:
                module = importlib._bootstrap._load(spec)
            except:
                rudisha None
            del sys.modules['__temp__']
            result = module.__doc__.splitlines()[0] ikiwa module.__doc__ else None
        # Cache the result.
        cache[filename] = (mtime, result)
    rudisha result

kundi ErrorDuringImport(Exception):
    """Errors that occurred while trying to agiza something to document it."""
    eleza __init__(self, filename, exc_info):
        self.filename = filename
        self.exc, self.value, self.tb = exc_info

    eleza __str__(self):
        exc = self.exc.__name__
        rudisha 'problem in %s - %s: %s' % (self.filename, exc, self.value)

eleza agizafile(path):
    """Import a Python source file or compiled file given its path."""
    magic = importlib.util.MAGIC_NUMBER
    with open(path, 'rb') as file:
        is_bytecode = magic == file.read(len(magic))
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    ikiwa is_bytecode:
        loader = importlib._bootstrap_external.SourcelessFileLoader(name, path)
    else:
        loader = importlib._bootstrap_external.SourceFileLoader(name, path)
    # XXX We probably don't need to pass in the loader here.
    spec = importlib.util.spec_kutoka_file_location(name, path, loader=loader)
    try:
        rudisha importlib._bootstrap._load(spec)
    except:
        raise ErrorDuringImport(path, sys.exc_info())

eleza safeagiza(path, forceload=0, cache={}):
    """Import a module; handle errors; rudisha None ikiwa the module isn't found.

    If the module *is* found but an exception occurs, it's wrapped in an
    ErrorDuringImport exception and reraised.  Unlike __import__, ikiwa a
    package path is specified, the module at the end of the path is returned,
    not the package at the beginning.  If the optional 'forceload' argument
    is 1, we reload the module kutoka disk (unless it's a dynamic extension)."""
    try:
        # If forceload is 1 and the module has been previously loaded kutoka
        # disk, we always have to reload the module.  Checking the file's
        # mtime isn't good enough (e.g. the module could contain a class
        # that inherits kutoka another module that has changed).
        ikiwa forceload and path in sys.modules:
            ikiwa path not in sys.builtin_module_names:
                # Remove the module kutoka sys.modules and re-agiza to try
                # and avoid problems with partially loaded modules.
                # Also remove any submodules because they won't appear
                # in the newly loaded module's namespace ikiwa they're already
                # in sys.modules.
                subs = [m for m in sys.modules ikiwa m.startswith(path + '.')]
                for key in [path] + subs:
                    # Prevent garbage collection.
                    cache[key] = sys.modules[key]
                    del sys.modules[key]
        module = __import__(path)
    except:
        # Did the error occur before or after the module was found?
        (exc, value, tb) = info = sys.exc_info()
        ikiwa path in sys.modules:
            # An error occurred while executing the imported module.
            raise ErrorDuringImport(sys.modules[path].__file__, info)
        elikiwa exc is SyntaxError:
            # A SyntaxError occurred before we could execute the module.
            raise ErrorDuringImport(value.filename, info)
        elikiwa issubclass(exc, ImportError) and value.name == path:
            # No such module in the path.
            rudisha None
        else:
            # Some other error occurred during the agizaing process.
            raise ErrorDuringImport(path, sys.exc_info())
    for part in path.split('.')[1:]:
        try: module = getattr(module, part)
        except AttributeError: rudisha None
    rudisha module

# ---------------------------------------------------- formatter base class

kundi Doc:

    PYTHONDOCS = os.environ.get("PYTHONDOCS",
                                "https://docs.python.org/%d.%d/library"
                                % sys.version_info[:2])

    eleza document(self, object, name=None, *args):
        """Generate documentation for an object."""
        args = (object, name) + args
        # 'try' clause is to attempt to handle the possibility that inspect
        # identifies something in a way that pydoc itself has issues handling;
        # think 'super' and how it is a descriptor (which raises the exception
        # by lacking a __name__ attribute) and an instance.
        try:
            ikiwa inspect.ismodule(object): rudisha self.docmodule(*args)
            ikiwa inspect.isclass(object): rudisha self.docclass(*args)
            ikiwa inspect.isroutine(object): rudisha self.docroutine(*args)
        except AttributeError:
            pass
        ikiwa inspect.isdatadescriptor(object): rudisha self.docdata(*args)
        rudisha self.docother(*args)

    eleza fail(self, object, name=None, *args):
        """Raise an exception for unimplemented types."""
        message = "don't know how to document object%s of type %s" % (
            name and ' ' + repr(name), type(object).__name__)
        raise TypeError(message)

    docmodule = dockundi = docroutine = docother = docproperty = docdata = fail

    eleza getdocloc(self, object,
                  basedir=os.path.join(sys.base_exec_prefix, "lib",
                                       "python%d.%d" %  sys.version_info[:2])):
        """Return the location of module docs or None"""

        try:
            file = inspect.getabsfile(object)
        except TypeError:
            file = '(built-in)'

        docloc = os.environ.get("PYTHONDOCS", self.PYTHONDOCS)

        basedir = os.path.normcase(basedir)
        ikiwa (isinstance(object, type(os)) and
            (object.__name__ in ('errno', 'exceptions', 'gc', 'imp',
                                 'marshal', 'posix', 'signal', 'sys',
                                 '_thread', 'zipagiza') or
             (file.startswith(basedir) and
              not file.startswith(os.path.join(basedir, 'site-packages')))) and
            object.__name__ not in ('xml.etree', 'test.pydoc_mod')):
            ikiwa docloc.startswith(("http://", "https://")):
                docloc = "%s/%s" % (docloc.rstrip("/"), object.__name__.lower())
            else:
                docloc = os.path.join(docloc, object.__name__.lower() + ".html")
        else:
            docloc = None
        rudisha docloc

# -------------------------------------------- HTML documentation generator

kundi HTMLRepr(Repr):
    """Class for safely making an HTML representation of a Python object."""
    eleza __init__(self):
        Repr.__init__(self)
        self.maxlist = self.maxtuple = 20
        self.maxdict = 10
        self.maxstring = self.maxother = 100

    eleza escape(self, text):
        rudisha replace(text, '&', '&amp;', '<', '&lt;', '>', '&gt;')

    eleza repr(self, object):
        rudisha Repr.repr(self, object)

    eleza repr1(self, x, level):
        ikiwa hasattr(type(x), '__name__'):
            methodname = 'repr_' + '_'.join(type(x).__name__.split())
            ikiwa hasattr(self, methodname):
                rudisha getattr(self, methodname)(x, level)
        rudisha self.escape(cram(stripid(repr(x)), self.maxother))

    eleza repr_string(self, x, level):
        test = cram(x, self.maxstring)
        testrepr = repr(test)
        ikiwa '\\' in test and '\\' not in replace(testrepr, r'\\', ''):
            # Backslashes are only literal in the string and are never
            # needed to make any special characters, so show a raw string.
            rudisha 'r' + testrepr[0] + self.escape(test) + testrepr[0]
        rudisha re.sub(r'((\\[\\abfnrtv\'"]|\\[0-9]..|\\x..|\\u....)+)',
                      r'<font color="#c040c0">\1</font>',
                      self.escape(testrepr))

    repr_str = repr_string

    eleza repr_instance(self, x, level):
        try:
            rudisha self.escape(cram(stripid(repr(x)), self.maxstring))
        except:
            rudisha self.escape('<%s instance>' % x.__class__.__name__)

    repr_unicode = repr_string

kundi HTMLDoc(Doc):
    """Formatter kundi for HTML documentation."""

    # ------------------------------------------- HTML formatting utilities

    _repr_instance = HTMLRepr()
    repr = _repr_instance.repr
    escape = _repr_instance.escape

    eleza page(self, title, contents):
        """Format an HTML page."""
        rudisha '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title>Python: %s</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body bgcolor="#f0f0f8">
%s
</body></html>''' % (title, contents)

    eleza heading(self, title, fgcol, bgcol, extras=''):
        """Format a page heading."""
        rudisha '''
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="heading">
<tr bgcolor="%s">
<td valign=bottom>&nbsp;<br>
<font color="%s" face="helvetica, arial">&nbsp;<br>%s</font></td
><td align=right valign=bottom
><font color="%s" face="helvetica, arial">%s</font></td></tr></table>
    ''' % (bgcol, fgcol, title, fgcol, extras or '&nbsp;')

    eleza section(self, title, fgcol, bgcol, contents, width=6,
                prelude='', marginalia=None, gap='&nbsp;'):
        """Format a section with a heading."""
        ikiwa marginalia is None:
            marginalia = '<tt>' + '&nbsp;' * width + '</tt>'
        result = '''<p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="%s">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="%s" face="helvetica, arial">%s</font></td></tr>
    ''' % (bgcol, fgcol, title)
        ikiwa prelude:
            result = result + '''
<tr bgcolor="%s"><td rowspan=2>%s</td>
<td colspan=2>%s</td></tr>
<tr><td>%s</td>''' % (bgcol, marginalia, prelude, gap)
        else:
            result = result + '''
<tr><td bgcolor="%s">%s</td><td>%s</td>''' % (bgcol, marginalia, gap)

        rudisha result + '\n<td width="100%%">%s</td></tr></table>' % contents

    eleza bigsection(self, title, *args):
        """Format a section with a big heading."""
        title = '<big><strong>%s</strong></big>' % title
        rudisha self.section(title, *args)

    eleza preformat(self, text):
        """Format literal preformatted text."""
        text = self.escape(text.expandtabs())
        rudisha replace(text, '\n\n', '\n \n', '\n\n', '\n \n',
                             ' ', '&nbsp;', '\n', '<br>\n')

    eleza multicolumn(self, list, format, cols=4):
        """Format a list of items into a multi-column list."""
        result = ''
        rows = (len(list)+cols-1)//cols
        for col in range(cols):
            result = result + '<td width="%d%%" valign=top>' % (100//cols)
            for i in range(rows*col, rows*col+rows):
                ikiwa i < len(list):
                    result = result + format(list[i]) + '<br>\n'
            result = result + '</td>'
        rudisha '<table width="100%%" summary="list"><tr>%s</tr></table>' % result

    eleza grey(self, text): rudisha '<font color="#909090">%s</font>' % text

    eleza namelink(self, name, *dicts):
        """Make a link for an identifier, given name-to-URL mappings."""
        for dict in dicts:
            ikiwa name in dict:
                rudisha '<a href="%s">%s</a>' % (dict[name], name)
        rudisha name

    eleza classlink(self, object, modname):
        """Make a link for a class."""
        name, module = object.__name__, sys.modules.get(object.__module__)
        ikiwa hasattr(module, name) and getattr(module, name) is object:
            rudisha '<a href="%s.html#%s">%s</a>' % (
                module.__name__, name, classname(object, modname))
        rudisha classname(object, modname)

    eleza modulelink(self, object):
        """Make a link for a module."""
        rudisha '<a href="%s.html">%s</a>' % (object.__name__, object.__name__)

    eleza modpkglink(self, modpkginfo):
        """Make a link for a module or package to display in an index."""
        name, path, ispackage, shadowed = modpkginfo
        ikiwa shadowed:
            rudisha self.grey(name)
        ikiwa path:
            url = '%s.%s.html' % (path, name)
        else:
            url = '%s.html' % name
        ikiwa ispackage:
            text = '<strong>%s</strong>&nbsp;(package)' % name
        else:
            text = name
        rudisha '<a href="%s">%s</a>' % (url, text)

    eleza filelink(self, url, path):
        """Make a link to source file."""
        rudisha '<a href="file:%s">%s</a>' % (url, path)

    eleza markup(self, text, escape=None, funcs={}, classes={}, methods={}):
        """Mark up some plain text, given a context of symbols to look for.
        Each context dictionary maps object names to anchor names."""
        escape = escape or self.escape
        results = []
        here = 0
        pattern = re.compile(r'\b((http|ftp)://\S+[\w/]|'
                                r'RFC[- ]?(\d+)|'
                                r'PEP[- ]?(\d+)|'
                                r'(self\.)?(\w+))')
        while True:
            match = pattern.search(text, here)
            ikiwa not match: break
            start, end = match.span()
            results.append(escape(text[here:start]))

            all, scheme, rfc, pep, selfdot, name = match.groups()
            ikiwa scheme:
                url = escape(all).replace('"', '&quot;')
                results.append('<a href="%s">%s</a>' % (url, url))
            elikiwa rfc:
                url = 'http://www.rfc-editor.org/rfc/rfc%d.txt' % int(rfc)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            elikiwa pep:
                url = 'http://www.python.org/dev/peps/pep-%04d/' % int(pep)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            elikiwa selfdot:
                # Create a link for methods like 'self.method(...)'
                # and use <strong> for attributes like 'self.attr'
                ikiwa text[end:end+1] == '(':
                    results.append('self.' + self.namelink(name, methods))
                else:
                    results.append('self.<strong>%s</strong>' % name)
            elikiwa text[end:end+1] == '(':
                results.append(self.namelink(name, methods, funcs, classes))
            else:
                results.append(self.namelink(name, classes))
            here = end
        results.append(escape(text[here:]))
        rudisha ''.join(results)

    # ---------------------------------------------- type-specific routines

    eleza formattree(self, tree, modname, parent=None):
        """Produce HTML for a kundi tree as given by inspect.getclasstree()."""
        result = ''
        for entry in tree:
            ikiwa type(entry) is type(()):
                c, bases = entry
                result = result + '<dt><font face="helvetica, arial">'
                result = result + self.classlink(c, modname)
                ikiwa bases and bases != (parent,):
                    parents = []
                    for base in bases:
                        parents.append(self.classlink(base, modname))
                    result = result + '(' + ', '.join(parents) + ')'
                result = result + '\n</font></dt>'
            elikiwa type(entry) is type([]):
                result = result + '<dd>\n%s</dd>\n' % self.formattree(
                    entry, modname, c)
        rudisha '<dl>\n%s</dl>\n' % result

    eleza docmodule(self, object, name=None, mod=None, *ignored):
        """Produce HTML documentation for a module object."""
        name = object.__name__ # ignore the passed-in name
        try:
            all = object.__all__
        except AttributeError:
            all = None
        parts = name.split('.')
        links = []
        for i in range(len(parts)-1):
            links.append(
                '<a href="%s.html"><font color="#ffffff">%s</font></a>' %
                ('.'.join(parts[:i+1]), parts[i]))
        linkedname = '.'.join(links + parts[-1:])
        head = '<big><big><strong>%s</strong></big></big>' % linkedname
        try:
            path = inspect.getabsfile(object)
            url = urllib.parse.quote(path)
            filelink = self.filelink(url, path)
        except TypeError:
            filelink = '(built-in)'
        info = []
        ikiwa hasattr(object, '__version__'):
            version = str(object.__version__)
            ikiwa version[:11] == '$' + 'Revision: ' and version[-1:] == '$':
                version = version[11:-1].strip()
            info.append('version %s' % self.escape(version))
        ikiwa hasattr(object, '__date__'):
            info.append(self.escape(str(object.__date__)))
        ikiwa info:
            head = head + ' (%s)' % ', '.join(info)
        docloc = self.getdocloc(object)
        ikiwa docloc is not None:
            docloc = '<br><a href="%(docloc)s">Module Reference</a>' % locals()
        else:
            docloc = ''
        result = self.heading(
            head, '#ffffff', '#7799ee',
            '<a href=".">index</a><br>' + filelink + docloc)

        modules = inspect.getmembers(object, inspect.ismodule)

        classes, cdict = [], {}
        for key, value in inspect.getmembers(object, inspect.isclass):
            # ikiwa __all__ exists, believe it.  Otherwise use old heuristic.
            ikiwa (all is not None or
                (inspect.getmodule(value) or object) is object):
                ikiwa visiblename(key, all, object):
                    classes.append((key, value))
                    cdict[key] = cdict[value] = '#' + key
        for key, value in classes:
            for base in value.__bases__:
                key, modname = base.__name__, base.__module__
                module = sys.modules.get(modname)
                ikiwa modname != name and module and hasattr(module, key):
                    ikiwa getattr(module, key) is base:
                        ikiwa not key in cdict:
                            cdict[key] = cdict[base] = modname + '.html#' + key
        funcs, fdict = [], {}
        for key, value in inspect.getmembers(object, inspect.isroutine):
            # ikiwa __all__ exists, believe it.  Otherwise use old heuristic.
            ikiwa (all is not None or
                inspect.isbuiltin(value) or inspect.getmodule(value) is object):
                ikiwa visiblename(key, all, object):
                    funcs.append((key, value))
                    fdict[key] = '#-' + key
                    ikiwa inspect.isfunction(value): fdict[value] = fdict[key]
        data = []
        for key, value in inspect.getmembers(object, isdata):
            ikiwa visiblename(key, all, object):
                data.append((key, value))

        doc = self.markup(getdoc(object), self.preformat, fdict, cdict)
        doc = doc and '<tt>%s</tt>' % doc
        result = result + '<p>%s</p>\n' % doc

        ikiwa hasattr(object, '__path__'):
            modpkgs = []
            for importer, modname, ispkg in pkgutil.iter_modules(object.__path__):
                modpkgs.append((modname, name, ispkg, 0))
            modpkgs.sort()
            contents = self.multicolumn(modpkgs, self.modpkglink)
            result = result + self.bigsection(
                'Package Contents', '#ffffff', '#aa55cc', contents)
        elikiwa modules:
            contents = self.multicolumn(
                modules, lambda t: self.modulelink(t[1]))
            result = result + self.bigsection(
                'Modules', '#ffffff', '#aa55cc', contents)

        ikiwa classes:
            classlist = [value for (key, value) in classes]
            contents = [
                self.formattree(inspect.getclasstree(classlist, 1), name)]
            for key, value in classes:
                contents.append(self.document(value, key, name, fdict, cdict))
            result = result + self.bigsection(
                'Classes', '#ffffff', '#ee77aa', ' '.join(contents))
        ikiwa funcs:
            contents = []
            for key, value in funcs:
                contents.append(self.document(value, key, name, fdict, cdict))
            result = result + self.bigsection(
                'Functions', '#ffffff', '#eeaa77', ' '.join(contents))
        ikiwa data:
            contents = []
            for key, value in data:
                contents.append(self.document(value, key))
            result = result + self.bigsection(
                'Data', '#ffffff', '#55aa55', '<br>\n'.join(contents))
        ikiwa hasattr(object, '__author__'):
            contents = self.markup(str(object.__author__), self.preformat)
            result = result + self.bigsection(
                'Author', '#ffffff', '#7799ee', contents)
        ikiwa hasattr(object, '__credits__'):
            contents = self.markup(str(object.__credits__), self.preformat)
            result = result + self.bigsection(
                'Credits', '#ffffff', '#7799ee', contents)

        rudisha result

    eleza docclass(self, object, name=None, mod=None, funcs={}, classes={},
                 *ignored):
        """Produce HTML documentation for a kundi object."""
        realname = object.__name__
        name = name or realname
        bases = object.__bases__

        contents = []
        push = contents.append

        # Cute little kundi to pump out a horizontal rule between sections.
        kundi HorizontalRule:
            eleza __init__(self):
                self.needone = 0
            eleza maybe(self):
                ikiwa self.needone:
                    push('<hr>\n')
                self.needone = 1
        hr = HorizontalRule()

        # List the mro, ikiwa non-trivial.
        mro = deque(inspect.getmro(object))
        ikiwa len(mro) > 2:
            hr.maybe()
            push('<dl><dt>Method resolution order:</dt>\n')
            for base in mro:
                push('<dd>%s</dd>\n' % self.classlink(base,
                                                      object.__module__))
            push('</dl>\n')

        eleza spill(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            ikiwa ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    try:
                        value = getattr(object, name)
                    except Exception:
                        # Some descriptors may meet a failure in their __get__.
                        # (bug #1785)
                        push(self.docdata(value, name, mod))
                    else:
                        push(self.document(value, name, mod,
                                        funcs, classes, mdict, object))
                    push('\n')
            rudisha attrs

        eleza spilldescriptors(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            ikiwa ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    push(self.docdata(value, name, mod))
            rudisha attrs

        eleza spilldata(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            ikiwa ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    base = self.docother(getattr(object, name), name, mod)
                    ikiwa callable(value) or inspect.isdatadescriptor(value):
                        doc = getattr(value, "__doc__", None)
                    else:
                        doc = None
                    ikiwa doc is None:
                        push('<dl><dt>%s</dl>\n' % base)
                    else:
                        doc = self.markup(getdoc(value), self.preformat,
                                          funcs, classes, mdict)
                        doc = '<dd><tt>%s</tt>' % doc
                        push('<dl><dt>%s%s</dl>\n' % (base, doc))
                    push('\n')
            rudisha attrs

        attrs = [(name, kind, cls, value)
                 for name, kind, cls, value in classify_class_attrs(object)
                 ikiwa visiblename(name, obj=object)]

        mdict = {}
        for key, kind, homecls, value in attrs:
            mdict[key] = anchor = '#' + name + '-' + key
            try:
                value = getattr(object, name)
            except Exception:
                # Some descriptors may meet a failure in their __get__.
                # (bug #1785)
                pass
            try:
                # The value may not be hashable (e.g., a data attr with
                # a dict or list value).
                mdict[value] = anchor
            except TypeError:
                pass

        while attrs:
            ikiwa mro:
                thiskundi = mro.popleft()
            else:
                thiskundi = attrs[0][2]
            attrs, inherited = _split_list(attrs, lambda t: t[2] is thisclass)

            ikiwa object is not builtins.object and thiskundi is builtins.object:
                attrs = inherited
                continue
            elikiwa thiskundi is object:
                tag = 'defined here'
            else:
                tag = 'inherited kutoka %s' % self.classlink(thisclass,
                                                           object.__module__)
            tag += ':<br>\n'

            sort_attributes(attrs, object)

            # Pump out the attrs, segregated by kind.
            attrs = spill('Methods %s' % tag, attrs,
                          lambda t: t[1] == 'method')
            attrs = spill('Class methods %s' % tag, attrs,
                          lambda t: t[1] == 'kundi method')
            attrs = spill('Static methods %s' % tag, attrs,
                          lambda t: t[1] == 'static method')
            attrs = spilldescriptors("Readonly properties %s" % tag, attrs,
                                     lambda t: t[1] == 'readonly property')
            attrs = spilldescriptors('Data descriptors %s' % tag, attrs,
                                     lambda t: t[1] == 'data descriptor')
            attrs = spilldata('Data and other attributes %s' % tag, attrs,
                              lambda t: t[1] == 'data')
            assert attrs == []
            attrs = inherited

        contents = ''.join(contents)

        ikiwa name == realname:
            title = '<a name="%s">kundi <strong>%s</strong></a>' % (
                name, realname)
        else:
            title = '<strong>%s</strong> = <a name="%s">kundi %s</a>' % (
                name, name, realname)
        ikiwa bases:
            parents = []
            for base in bases:
                parents.append(self.classlink(base, object.__module__))
            title = title + '(%s)' % ', '.join(parents)

        decl = ''
        try:
            signature = inspect.signature(object)
        except (ValueError, TypeError):
            signature = None
        ikiwa signature:
            argspec = str(signature)
            ikiwa argspec and argspec != '()':
                decl = name + self.escape(argspec) + '\n\n'

        doc = getdoc(object)
        ikiwa decl:
            doc = decl + (doc or '')
        doc = self.markup(doc, self.preformat, funcs, classes, mdict)
        doc = doc and '<tt>%s<br>&nbsp;</tt>' % doc

        rudisha self.section(title, '#000000', '#ffc8d8', contents, 3, doc)

    eleza formatvalue(self, object):
        """Format an argument default value as text."""
        rudisha self.grey('=' + self.repr(object))

    eleza docroutine(self, object, name=None, mod=None,
                   funcs={}, classes={}, methods={}, cl=None):
        """Produce HTML documentation for a function or method object."""
        realname = object.__name__
        name = name or realname
        anchor = (cl and cl.__name__ or '') + '-' + name
        note = ''
        skipdocs = 0
        ikiwa _is_bound_method(object):
            imkundi = object.__self__.__class__
            ikiwa cl:
                ikiwa imkundi is not cl:
                    note = ' kutoka ' + self.classlink(imclass, mod)
            else:
                ikiwa object.__self__ is not None:
                    note = ' method of %s instance' % self.classlink(
                        object.__self__.__class__, mod)
                else:
                    note = ' unbound %s method' % self.classlink(imclass,mod)

        ikiwa (inspect.iscoroutinefunction(object) or
                inspect.isasyncgenfunction(object)):
            asyncqualifier = 'async '
        else:
            asyncqualifier = ''

        ikiwa name == realname:
            title = '<a name="%s"><strong>%s</strong></a>' % (anchor, realname)
        else:
            ikiwa cl and inspect.getattr_static(cl, realname, []) is object:
                reallink = '<a href="#%s">%s</a>' % (
                    cl.__name__ + '-' + realname, realname)
                skipdocs = 1
            else:
                reallink = realname
            title = '<a name="%s"><strong>%s</strong></a> = %s' % (
                anchor, name, reallink)
        argspec = None
        ikiwa inspect.isroutine(object):
            try:
                signature = inspect.signature(object)
            except (ValueError, TypeError):
                signature = None
            ikiwa signature:
                argspec = str(signature)
                ikiwa realname == '<lambda>':
                    title = '<strong>%s</strong> <em>lambda</em> ' % name
                    # XXX lambda's won't usually have func_annotations['return']
                    # since the syntax doesn't support but it is possible.
                    # So removing parentheses isn't truly safe.
                    argspec = argspec[1:-1] # remove parentheses
        ikiwa not argspec:
            argspec = '(...)'

        decl = asyncqualifier + title + self.escape(argspec) + (note and
               self.grey('<font face="helvetica, arial">%s</font>' % note))

        ikiwa skipdocs:
            rudisha '<dl><dt>%s</dt></dl>\n' % decl
        else:
            doc = self.markup(
                getdoc(object), self.preformat, funcs, classes, methods)
            doc = doc and '<dd><tt>%s</tt></dd>' % doc
            rudisha '<dl><dt>%s</dt>%s</dl>\n' % (decl, doc)

    eleza docdata(self, object, name=None, mod=None, cl=None):
        """Produce html documentation for a data descriptor."""
        results = []
        push = results.append

        ikiwa name:
            push('<dl><dt><strong>%s</strong></dt>\n' % name)
        doc = self.markup(getdoc(object), self.preformat)
        ikiwa doc:
            push('<dd><tt>%s</tt></dd>\n' % doc)
        push('</dl>\n')

        rudisha ''.join(results)

    docproperty = docdata

    eleza docother(self, object, name=None, mod=None, *ignored):
        """Produce HTML documentation for a data object."""
        lhs = name and '<strong>%s</strong> = ' % name or ''
        rudisha lhs + self.repr(object)

    eleza index(self, dir, shadowed=None):
        """Generate an HTML index for a directory of modules."""
        modpkgs = []
        ikiwa shadowed is None: shadowed = {}
        for importer, name, ispkg in pkgutil.iter_modules([dir]):
            ikiwa any((0xD800 <= ord(ch) <= 0xDFFF) for ch in name):
                # ignore a module ikiwa its name contains a surrogate character
                continue
            modpkgs.append((name, '', ispkg, name in shadowed))
            shadowed[name] = 1

        modpkgs.sort()
        contents = self.multicolumn(modpkgs, self.modpkglink)
        rudisha self.bigsection(dir, '#ffffff', '#ee77aa', contents)

# -------------------------------------------- text documentation generator

kundi TextRepr(Repr):
    """Class for safely making a text representation of a Python object."""
    eleza __init__(self):
        Repr.__init__(self)
        self.maxlist = self.maxtuple = 20
        self.maxdict = 10
        self.maxstring = self.maxother = 100

    eleza repr1(self, x, level):
        ikiwa hasattr(type(x), '__name__'):
            methodname = 'repr_' + '_'.join(type(x).__name__.split())
            ikiwa hasattr(self, methodname):
                rudisha getattr(self, methodname)(x, level)
        rudisha cram(stripid(repr(x)), self.maxother)

    eleza repr_string(self, x, level):
        test = cram(x, self.maxstring)
        testrepr = repr(test)
        ikiwa '\\' in test and '\\' not in replace(testrepr, r'\\', ''):
            # Backslashes are only literal in the string and are never
            # needed to make any special characters, so show a raw string.
            rudisha 'r' + testrepr[0] + test + testrepr[0]
        rudisha testrepr

    repr_str = repr_string

    eleza repr_instance(self, x, level):
        try:
            rudisha cram(stripid(repr(x)), self.maxstring)
        except:
            rudisha '<%s instance>' % x.__class__.__name__

kundi TextDoc(Doc):
    """Formatter kundi for text documentation."""

    # ------------------------------------------- text formatting utilities

    _repr_instance = TextRepr()
    repr = _repr_instance.repr

    eleza bold(self, text):
        """Format a string in bold by overstriking."""
        rudisha ''.join(ch + '\b' + ch for ch in text)

    eleza indent(self, text, prefix='    '):
        """Indent text by prepending a given prefix to each line."""
        ikiwa not text: rudisha ''
        lines = [prefix + line for line in text.split('\n')]
        ikiwa lines: lines[-1] = lines[-1].rstrip()
        rudisha '\n'.join(lines)

    eleza section(self, title, contents):
        """Format a section with a given heading."""
        clean_contents = self.indent(contents).rstrip()
        rudisha self.bold(title) + '\n' + clean_contents + '\n\n'

    # ---------------------------------------------- type-specific routines

    eleza formattree(self, tree, modname, parent=None, prefix=''):
        """Render in text a kundi tree as returned by inspect.getclasstree()."""
        result = ''
        for entry in tree:
            ikiwa type(entry) is type(()):
                c, bases = entry
                result = result + prefix + classname(c, modname)
                ikiwa bases and bases != (parent,):
                    parents = (classname(c, modname) for c in bases)
                    result = result + '(%s)' % ', '.join(parents)
                result = result + '\n'
            elikiwa type(entry) is type([]):
                result = result + self.formattree(
                    entry, modname, c, prefix + '    ')
        rudisha result

    eleza docmodule(self, object, name=None, mod=None):
        """Produce text documentation for a given module object."""
        name = object.__name__ # ignore the passed-in name
        synop, desc = splitdoc(getdoc(object))
        result = self.section('NAME', name + (synop and ' - ' + synop))
        all = getattr(object, '__all__', None)
        docloc = self.getdocloc(object)
        ikiwa docloc is not None:
            result = result + self.section('MODULE REFERENCE', docloc + """

The following documentation is automatically generated kutoka the Python
source files.  It may be incomplete, incorrect or include features that
are considered implementation detail and may vary between Python
implementations.  When in doubt, consult the module reference at the
location listed above.
""")

        ikiwa desc:
            result = result + self.section('DESCRIPTION', desc)

        classes = []
        for key, value in inspect.getmembers(object, inspect.isclass):
            # ikiwa __all__ exists, believe it.  Otherwise use old heuristic.
            ikiwa (all is not None
                or (inspect.getmodule(value) or object) is object):
                ikiwa visiblename(key, all, object):
                    classes.append((key, value))
        funcs = []
        for key, value in inspect.getmembers(object, inspect.isroutine):
            # ikiwa __all__ exists, believe it.  Otherwise use old heuristic.
            ikiwa (all is not None or
                inspect.isbuiltin(value) or inspect.getmodule(value) is object):
                ikiwa visiblename(key, all, object):
                    funcs.append((key, value))
        data = []
        for key, value in inspect.getmembers(object, isdata):
            ikiwa visiblename(key, all, object):
                data.append((key, value))

        modpkgs = []
        modpkgs_names = set()
        ikiwa hasattr(object, '__path__'):
            for importer, modname, ispkg in pkgutil.iter_modules(object.__path__):
                modpkgs_names.add(modname)
                ikiwa ispkg:
                    modpkgs.append(modname + ' (package)')
                else:
                    modpkgs.append(modname)

            modpkgs.sort()
            result = result + self.section(
                'PACKAGE CONTENTS', '\n'.join(modpkgs))

        # Detect submodules as sometimes created by C extensions
        submodules = []
        for key, value in inspect.getmembers(object, inspect.ismodule):
            ikiwa value.__name__.startswith(name + '.') and key not in modpkgs_names:
                submodules.append(key)
        ikiwa submodules:
            submodules.sort()
            result = result + self.section(
                'SUBMODULES', '\n'.join(submodules))

        ikiwa classes:
            classlist = [value for key, value in classes]
            contents = [self.formattree(
                inspect.getclasstree(classlist, 1), name)]
            for key, value in classes:
                contents.append(self.document(value, key, name))
            result = result + self.section('CLASSES', '\n'.join(contents))

        ikiwa funcs:
            contents = []
            for key, value in funcs:
                contents.append(self.document(value, key, name))
            result = result + self.section('FUNCTIONS', '\n'.join(contents))

        ikiwa data:
            contents = []
            for key, value in data:
                contents.append(self.docother(value, key, name, maxlen=70))
            result = result + self.section('DATA', '\n'.join(contents))

        ikiwa hasattr(object, '__version__'):
            version = str(object.__version__)
            ikiwa version[:11] == '$' + 'Revision: ' and version[-1:] == '$':
                version = version[11:-1].strip()
            result = result + self.section('VERSION', version)
        ikiwa hasattr(object, '__date__'):
            result = result + self.section('DATE', str(object.__date__))
        ikiwa hasattr(object, '__author__'):
            result = result + self.section('AUTHOR', str(object.__author__))
        ikiwa hasattr(object, '__credits__'):
            result = result + self.section('CREDITS', str(object.__credits__))
        try:
            file = inspect.getabsfile(object)
        except TypeError:
            file = '(built-in)'
        result = result + self.section('FILE', file)
        rudisha result

    eleza docclass(self, object, name=None, mod=None, *ignored):
        """Produce text documentation for a given kundi object."""
        realname = object.__name__
        name = name or realname
        bases = object.__bases__

        eleza makename(c, m=object.__module__):
            rudisha classname(c, m)

        ikiwa name == realname:
            title = 'kundi ' + self.bold(realname)
        else:
            title = self.bold(name) + ' = kundi ' + realname
        ikiwa bases:
            parents = map(makename, bases)
            title = title + '(%s)' % ', '.join(parents)

        contents = []
        push = contents.append

        try:
            signature = inspect.signature(object)
        except (ValueError, TypeError):
            signature = None
        ikiwa signature:
            argspec = str(signature)
            ikiwa argspec and argspec != '()':
                push(name + argspec + '\n')

        doc = getdoc(object)
        ikiwa doc:
            push(doc + '\n')

        # List the mro, ikiwa non-trivial.
        mro = deque(inspect.getmro(object))
        ikiwa len(mro) > 2:
            push("Method resolution order:")
            for base in mro:
                push('    ' + makename(base))
            push('')

        # List the built-in subclasses, ikiwa any:
        subclasses = sorted(
            (str(cls.__name__) for cls in type.__subclasses__(object)
             ikiwa not cls.__name__.startswith("_") and cls.__module__ == "builtins"),
            key=str.lower
        )
        no_of_subclasses = len(subclasses)
        MAX_SUBCLASSES_TO_DISPLAY = 4
        ikiwa subclasses:
            push("Built-in subclasses:")
            for subclassname in subclasses[:MAX_SUBCLASSES_TO_DISPLAY]:
                push('    ' + subclassname)
            ikiwa no_of_subclasses > MAX_SUBCLASSES_TO_DISPLAY:
                push('    ... and ' +
                     str(no_of_subclasses - MAX_SUBCLASSES_TO_DISPLAY) +
                     ' other subclasses')
            push('')

        # Cute little kundi to pump out a horizontal rule between sections.
        kundi HorizontalRule:
            eleza __init__(self):
                self.needone = 0
            eleza maybe(self):
                ikiwa self.needone:
                    push('-' * 70)
                self.needone = 1
        hr = HorizontalRule()

        eleza spill(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            ikiwa ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    try:
                        value = getattr(object, name)
                    except Exception:
                        # Some descriptors may meet a failure in their __get__.
                        # (bug #1785)
                        push(self.docdata(value, name, mod))
                    else:
                        push(self.document(value,
                                        name, mod, object))
            rudisha attrs

        eleza spilldescriptors(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            ikiwa ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    push(self.docdata(value, name, mod))
            rudisha attrs

        eleza spilldata(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            ikiwa ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    ikiwa callable(value) or inspect.isdatadescriptor(value):
                        doc = getdoc(value)
                    else:
                        doc = None
                    try:
                        obj = getattr(object, name)
                    except AttributeError:
                        obj = homecls.__dict__[name]
                    push(self.docother(obj, name, mod, maxlen=70, doc=doc) +
                         '\n')
            rudisha attrs

        attrs = [(name, kind, cls, value)
                 for name, kind, cls, value in classify_class_attrs(object)
                 ikiwa visiblename(name, obj=object)]

        while attrs:
            ikiwa mro:
                thiskundi = mro.popleft()
            else:
                thiskundi = attrs[0][2]
            attrs, inherited = _split_list(attrs, lambda t: t[2] is thisclass)

            ikiwa object is not builtins.object and thiskundi is builtins.object:
                attrs = inherited
                continue
            elikiwa thiskundi is object:
                tag = "defined here"
            else:
                tag = "inherited kutoka %s" % classname(thisclass,
                                                      object.__module__)

            sort_attributes(attrs, object)

            # Pump out the attrs, segregated by kind.
            attrs = spill("Methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'method')
            attrs = spill("Class methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'kundi method')
            attrs = spill("Static methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'static method')
            attrs = spilldescriptors("Readonly properties %s:\n" % tag, attrs,
                                     lambda t: t[1] == 'readonly property')
            attrs = spilldescriptors("Data descriptors %s:\n" % tag, attrs,
                                     lambda t: t[1] == 'data descriptor')
            attrs = spilldata("Data and other attributes %s:\n" % tag, attrs,
                              lambda t: t[1] == 'data')

            assert attrs == []
            attrs = inherited

        contents = '\n'.join(contents)
        ikiwa not contents:
            rudisha title + '\n'
        rudisha title + '\n' + self.indent(contents.rstrip(), ' |  ') + '\n'

    eleza formatvalue(self, object):
        """Format an argument default value as text."""
        rudisha '=' + self.repr(object)

    eleza docroutine(self, object, name=None, mod=None, cl=None):
        """Produce text documentation for a function or method object."""
        realname = object.__name__
        name = name or realname
        note = ''
        skipdocs = 0
        ikiwa _is_bound_method(object):
            imkundi = object.__self__.__class__
            ikiwa cl:
                ikiwa imkundi is not cl:
                    note = ' kutoka ' + classname(imclass, mod)
            else:
                ikiwa object.__self__ is not None:
                    note = ' method of %s instance' % classname(
                        object.__self__.__class__, mod)
                else:
                    note = ' unbound %s method' % classname(imclass,mod)

        ikiwa (inspect.iscoroutinefunction(object) or
                inspect.isasyncgenfunction(object)):
            asyncqualifier = 'async '
        else:
            asyncqualifier = ''

        ikiwa name == realname:
            title = self.bold(realname)
        else:
            ikiwa cl and inspect.getattr_static(cl, realname, []) is object:
                skipdocs = 1
            title = self.bold(name) + ' = ' + realname
        argspec = None

        ikiwa inspect.isroutine(object):
            try:
                signature = inspect.signature(object)
            except (ValueError, TypeError):
                signature = None
            ikiwa signature:
                argspec = str(signature)
                ikiwa realname == '<lambda>':
                    title = self.bold(name) + ' lambda '
                    # XXX lambda's won't usually have func_annotations['return']
                    # since the syntax doesn't support but it is possible.
                    # So removing parentheses isn't truly safe.
                    argspec = argspec[1:-1] # remove parentheses
        ikiwa not argspec:
            argspec = '(...)'
        decl = asyncqualifier + title + argspec + note

        ikiwa skipdocs:
            rudisha decl + '\n'
        else:
            doc = getdoc(object) or ''
            rudisha decl + '\n' + (doc and self.indent(doc).rstrip() + '\n')

    eleza docdata(self, object, name=None, mod=None, cl=None):
        """Produce text documentation for a data descriptor."""
        results = []
        push = results.append

        ikiwa name:
            push(self.bold(name))
            push('\n')
        doc = getdoc(object) or ''
        ikiwa doc:
            push(self.indent(doc))
            push('\n')
        rudisha ''.join(results)

    docproperty = docdata

    eleza docother(self, object, name=None, mod=None, parent=None, maxlen=None, doc=None):
        """Produce text documentation for a data object."""
        repr = self.repr(object)
        ikiwa maxlen:
            line = (name and name + ' = ' or '') + repr
            chop = maxlen - len(line)
            ikiwa chop < 0: repr = repr[:chop] + '...'
        line = (name and self.bold(name) + ' = ' or '') + repr
        ikiwa doc is not None:
            line += '\n' + self.indent(str(doc))
        rudisha line

kundi _PlainTextDoc(TextDoc):
    """Subkundi of TextDoc which overrides string styling"""
    eleza bold(self, text):
        rudisha text

# --------------------------------------------------------- user interfaces

eleza pager(text):
    """The first time this is called, determine what kind of pager to use."""
    global pager
    pager = getpager()
    pager(text)

eleza getpager():
    """Decide what method to use for paging through text."""
    ikiwa not hasattr(sys.stdin, "isatty"):
        rudisha plainpager
    ikiwa not hasattr(sys.stdout, "isatty"):
        rudisha plainpager
    ikiwa not sys.stdin.isatty() or not sys.stdout.isatty():
        rudisha plainpager
    use_pager = os.environ.get('MANPAGER') or os.environ.get('PAGER')
    ikiwa use_pager:
        ikiwa sys.platform == 'win32': # pipes completely broken in Windows
            rudisha lambda text: tempfilepager(plain(text), use_pager)
        elikiwa os.environ.get('TERM') in ('dumb', 'emacs'):
            rudisha lambda text: pipepager(plain(text), use_pager)
        else:
            rudisha lambda text: pipepager(text, use_pager)
    ikiwa os.environ.get('TERM') in ('dumb', 'emacs'):
        rudisha plainpager
    ikiwa sys.platform == 'win32':
        rudisha lambda text: tempfilepager(plain(text), 'more <')
    ikiwa hasattr(os, 'system') and os.system('(less) 2>/dev/null') == 0:
        rudisha lambda text: pipepager(text, 'less')

    agiza tempfile
    (fd, filename) = tempfile.mkstemp()
    os.close(fd)
    try:
        ikiwa hasattr(os, 'system') and os.system('more "%s"' % filename) == 0:
            rudisha lambda text: pipepager(text, 'more')
        else:
            rudisha ttypager
    finally:
        os.unlink(filename)

eleza plain(text):
    """Remove boldface formatting kutoka text."""
    rudisha re.sub('.\b', '', text)

eleza pipepager(text, cmd):
    """Page through text by feeding it to another program."""
    agiza subprocess
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
    try:
        with io.TextIOWrapper(proc.stdin, errors='backslashreplace') as pipe:
            try:
                pipe.write(text)
            except KeyboardInterrupt:
                # We've hereby abandoned whatever text hasn't been written,
                # but the pager is still in control of the terminal.
                pass
    except OSError:
        pass # Ignore broken pipes caused by quitting the pager program.
    while True:
        try:
            proc.wait()
            break
        except KeyboardInterrupt:
            # Ignore ctl-c like the pager itself does.  Otherwise the pager is
            # left running and the terminal is in raw mode and unusable.
            pass

eleza tempfilepager(text, cmd):
    """Page through text by invoking a program on a temporary file."""
    agiza tempfile
    filename = tempfile.mktemp()
    with open(filename, 'w', errors='backslashreplace') as file:
        file.write(text)
    try:
        os.system(cmd + ' "' + filename + '"')
    finally:
        os.unlink(filename)

eleza _escape_stdout(text):
    # Escape non-encodable characters to avoid encoding errors later
    encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
    rudisha text.encode(encoding, 'backslashreplace').decode(encoding)

eleza ttypager(text):
    """Page through text on a text terminal."""
    lines = plain(_escape_stdout(text)).split('\n')
    try:
        agiza tty
        fd = sys.stdin.fileno()
        old = tty.tcgetattr(fd)
        tty.setcbreak(fd)
        getchar = lambda: sys.stdin.read(1)
    except (ImportError, AttributeError, io.UnsupportedOperation):
        tty = None
        getchar = lambda: sys.stdin.readline()[:-1][:1]

    try:
        try:
            h = int(os.environ.get('LINES', 0))
        except ValueError:
            h = 0
        ikiwa h <= 1:
            h = 25
        r = inc = h - 1
        sys.stdout.write('\n'.join(lines[:inc]) + '\n')
        while lines[r:]:
            sys.stdout.write('-- more --')
            sys.stdout.flush()
            c = getchar()

            ikiwa c in ('q', 'Q'):
                sys.stdout.write('\r          \r')
                break
            elikiwa c in ('\r', '\n'):
                sys.stdout.write('\r          \r' + lines[r] + '\n')
                r = r + 1
                continue
            ikiwa c in ('b', 'B', '\x1b'):
                r = r - inc - inc
                ikiwa r < 0: r = 0
            sys.stdout.write('\n' + '\n'.join(lines[r:r+inc]) + '\n')
            r = r + inc

    finally:
        ikiwa tty:
            tty.tcsetattr(fd, tty.TCSAFLUSH, old)

eleza plainpager(text):
    """Simply print unformatted text.  This is the ultimate fallback."""
    sys.stdout.write(plain(_escape_stdout(text)))

eleza describe(thing):
    """Produce a short description of the given thing."""
    ikiwa inspect.ismodule(thing):
        ikiwa thing.__name__ in sys.builtin_module_names:
            rudisha 'built-in module ' + thing.__name__
        ikiwa hasattr(thing, '__path__'):
            rudisha 'package ' + thing.__name__
        else:
            rudisha 'module ' + thing.__name__
    ikiwa inspect.isbuiltin(thing):
        rudisha 'built-in function ' + thing.__name__
    ikiwa inspect.isgetsetdescriptor(thing):
        rudisha 'getset descriptor %s.%s.%s' % (
            thing.__objclass__.__module__, thing.__objclass__.__name__,
            thing.__name__)
    ikiwa inspect.ismemberdescriptor(thing):
        rudisha 'member descriptor %s.%s.%s' % (
            thing.__objclass__.__module__, thing.__objclass__.__name__,
            thing.__name__)
    ikiwa inspect.isclass(thing):
        rudisha 'kundi ' + thing.__name__
    ikiwa inspect.isfunction(thing):
        rudisha 'function ' + thing.__name__
    ikiwa inspect.ismethod(thing):
        rudisha 'method ' + thing.__name__
    rudisha type(thing).__name__

eleza locate(path, forceload=0):
    """Locate an object by name or dotted path, agizaing as necessary."""
    parts = [part for part in path.split('.') ikiwa part]
    module, n = None, 0
    while n < len(parts):
        nextmodule = safeagiza('.'.join(parts[:n+1]), forceload)
        ikiwa nextmodule: module, n = nextmodule, n + 1
        else: break
    ikiwa module:
        object = module
    else:
        object = builtins
    for part in parts[n:]:
        try:
            object = getattr(object, part)
        except AttributeError:
            rudisha None
    rudisha object

# --------------------------------------- interactive interpreter interface

text = TextDoc()
plaintext = _PlainTextDoc()
html = HTMLDoc()

eleza resolve(thing, forceload=0):
    """Given an object or a path to an object, get the object and its name."""
    ikiwa isinstance(thing, str):
        object = locate(thing, forceload)
        ikiwa object is None:
            raise ImportError('''\
No Python documentation found for %r.
Use help() to get the interactive help utility.
Use help(str) for help on the str class.''' % thing)
        rudisha object, thing
    else:
        name = getattr(thing, '__name__', None)
        rudisha thing, name ikiwa isinstance(name, str) else None

eleza render_doc(thing, title='Python Library Documentation: %s', forceload=0,
        renderer=None):
    """Render text documentation, given an object or a path to an object."""
    ikiwa renderer is None:
        renderer = text
    object, name = resolve(thing, forceload)
    desc = describe(object)
    module = inspect.getmodule(object)
    ikiwa name and '.' in name:
        desc += ' in ' + name[:name.rfind('.')]
    elikiwa module and module is not object:
        desc += ' in module ' + module.__name__

    ikiwa not (inspect.ismodule(object) or
              inspect.isclass(object) or
              inspect.isroutine(object) or
              inspect.isdatadescriptor(object)):
        # If the passed object is a piece of data or an instance,
        # document its available methods instead of its value.
        object = type(object)
        desc += ' object'
    rudisha title % desc + '\n\n' + renderer.document(object, name)

eleza doc(thing, title='Python Library Documentation: %s', forceload=0,
        output=None):
    """Display text documentation, given an object or a path to an object."""
    try:
        ikiwa output is None:
            pager(render_doc(thing, title, forceload))
        else:
            output.write(render_doc(thing, title, forceload, plaintext))
    except (ImportError, ErrorDuringImport) as value:
        andika(value)

eleza writedoc(thing, forceload=0):
    """Write HTML documentation to a file in the current directory."""
    try:
        object, name = resolve(thing, forceload)
        page = html.page(describe(object), html.document(object, name))
        with open(name + '.html', 'w', encoding='utf-8') as file:
            file.write(page)
        andika('wrote', name + '.html')
    except (ImportError, ErrorDuringImport) as value:
        andika(value)

eleza writedocs(dir, pkgpath='', done=None):
    """Write out HTML documentation for all modules in a directory tree."""
    ikiwa done is None: done = {}
    for importer, modname, ispkg in pkgutil.walk_packages([dir], pkgpath):
        writedoc(modname)
    return

kundi Helper:

    # These dictionaries map a topic name to either an alias, or a tuple
    # (label, seealso-items).  The "label" is the label of the corresponding
    # section in the .rst file under Doc/ and an index into the dictionary
    # in pydoc_data/topics.py.
    #
    # CAUTION: ikiwa you change one of these dictionaries, be sure to adapt the
    #          list of needed labels in Doc/tools/extensions/pyspecific.py and
    #          regenerate the pydoc_data/topics.py file by running
    #              make pydoc-topics
    #          in Doc/ and copying the output file into the Lib/ directory.

    keywords = {
        'False': '',
        'None': '',
        'True': '',
        'and': 'BOOLEAN',
        'as': 'with',
        'assert': ('assert', ''),
        'async': ('async', ''),
        'await': ('await', ''),
        'break': ('break', 'while for'),
        'class': ('class', 'CLASSES SPECIALMETHODS'),
        'continue': ('continue', 'while for'),
        'def': ('function', ''),
        'del': ('del', 'BASICMETHODS'),
        'elif': 'if',
        'else': ('else', 'while for'),
        'except': 'try',
        'finally': 'try',
        'for': ('for', 'break continue while'),
        'kutoka': 'agiza',
        'global': ('global', 'nonlocal NAMESPACES'),
        'if': ('if', 'TRUTHVALUE'),
        'agiza': ('agiza', 'MODULES'),
        'in': ('in', 'SEQUENCEMETHODS'),
        'is': 'COMPARISON',
        'lambda': ('lambda', 'FUNCTIONS'),
        'nonlocal': ('nonlocal', 'global NAMESPACES'),
        'not': 'BOOLEAN',
        'or': 'BOOLEAN',
        'pass': ('pass', ''),
        'raise': ('raise', 'EXCEPTIONS'),
        'return': ('return', 'FUNCTIONS'),
        'try': ('try', 'EXCEPTIONS'),
        'while': ('while', 'break continue ikiwa TRUTHVALUE'),
        'with': ('with', 'CONTEXTMANAGERS EXCEPTIONS yield'),
        'yield': ('yield', ''),
    }
    # Either add symbols to this dictionary or to the symbols dictionary
    # directly: Whichever is easier. They are merged later.
    _strprefixes = [p + q for p in ('b', 'f', 'r', 'u') for q in ("'", '"')]
    _symbols_inverse = {
        'STRINGS' : ("'", "'''", '"', '"""', *_strprefixes),
        'OPERATORS' : ('+', '-', '*', '**', '/', '//', '%', '<<', '>>', '&',
                       '|', '^', '~', '<', '>', '<=', '>=', '==', '!=', '<>'),
        'COMPARISON' : ('<', '>', '<=', '>=', '==', '!=', '<>'),
        'UNARY' : ('-', '~'),
        'AUGMENTEDASSIGNMENT' : ('+=', '-=', '*=', '/=', '%=', '&=', '|=',
                                '^=', '<<=', '>>=', '**=', '//='),
        'BITWISE' : ('<<', '>>', '&', '|', '^', '~'),
        'COMPLEX' : ('j', 'J')
    }
    symbols = {
        '%': 'OPERATORS FORMATTING',
        '**': 'POWER',
        ',': 'TUPLES LISTS FUNCTIONS',
        '.': 'ATTRIBUTES FLOAT MODULES OBJECTS',
        '...': 'ELLIPSIS',
        ':': 'SLICINGS DICTIONARYLITERALS',
        '@': 'eleza class',
        '\\': 'STRINGS',
        '_': 'PRIVATENAMES',
        '__': 'PRIVATENAMES SPECIALMETHODS',
        '`': 'BACKQUOTES',
        '(': 'TUPLES FUNCTIONS CALLS',
        ')': 'TUPLES FUNCTIONS CALLS',
        '[': 'LISTS SUBSCRIPTS SLICINGS',
        ']': 'LISTS SUBSCRIPTS SLICINGS'
    }
    for topic, symbols_ in _symbols_inverse.items():
        for symbol in symbols_:
            topics = symbols.get(symbol, topic)
            ikiwa topic not in topics:
                topics = topics + ' ' + topic
            symbols[symbol] = topics

    topics = {
        'TYPES': ('types', 'STRINGS UNICODE NUMBERS SEQUENCES MAPPINGS '
                  'FUNCTIONS CLASSES MODULES FILES inspect'),
        'STRINGS': ('strings', 'str UNICODE SEQUENCES STRINGMETHODS '
                    'FORMATTING TYPES'),
        'STRINGMETHODS': ('string-methods', 'STRINGS FORMATTING'),
        'FORMATTING': ('formatstrings', 'OPERATORS'),
        'UNICODE': ('strings', 'encodings unicode SEQUENCES STRINGMETHODS '
                    'FORMATTING TYPES'),
        'NUMBERS': ('numbers', 'INTEGER FLOAT COMPLEX TYPES'),
        'INTEGER': ('integers', 'int range'),
        'FLOAT': ('floating', 'float math'),
        'COMPLEX': ('imaginary', 'complex cmath'),
        'SEQUENCES': ('typesseq', 'STRINGMETHODS FORMATTING range LISTS'),
        'MAPPINGS': 'DICTIONARIES',
        'FUNCTIONS': ('typesfunctions', 'eleza TYPES'),
        'METHODS': ('typesmethods', 'kundi eleza CLASSES TYPES'),
        'CODEOBJECTS': ('bltin-code-objects', 'compile FUNCTIONS TYPES'),
        'TYPEOBJECTS': ('bltin-type-objects', 'types TYPES'),
        'FRAMEOBJECTS': 'TYPES',
        'TRACEBACKS': 'TYPES',
        'NONE': ('bltin-null-object', ''),
        'ELLIPSIS': ('bltin-ellipsis-object', 'SLICINGS'),
        'SPECIALATTRIBUTES': ('specialattrs', ''),
        'CLASSES': ('types', 'kundi SPECIALMETHODS PRIVATENAMES'),
        'MODULES': ('typesmodules', 'agiza'),
        'PACKAGES': 'agiza',
        'EXPRESSIONS': ('operator-summary', 'lambda or and not in is BOOLEAN '
                        'COMPARISON BITWISE SHIFTING BINARY FORMATTING POWER '
                        'UNARY ATTRIBUTES SUBSCRIPTS SLICINGS CALLS TUPLES '
                        'LISTS DICTIONARIES'),
        'OPERATORS': 'EXPRESSIONS',
        'PRECEDENCE': 'EXPRESSIONS',
        'OBJECTS': ('objects', 'TYPES'),
        'SPECIALMETHODS': ('specialnames', 'BASICMETHODS ATTRIBUTEMETHODS '
                           'CALLABLEMETHODS SEQUENCEMETHODS MAPPINGMETHODS '
                           'NUMBERMETHODS CLASSES'),
        'BASICMETHODS': ('customization', 'hash repr str SPECIALMETHODS'),
        'ATTRIBUTEMETHODS': ('attribute-access', 'ATTRIBUTES SPECIALMETHODS'),
        'CALLABLEMETHODS': ('callable-types', 'CALLS SPECIALMETHODS'),
        'SEQUENCEMETHODS': ('sequence-types', 'SEQUENCES SEQUENCEMETHODS '
                             'SPECIALMETHODS'),
        'MAPPINGMETHODS': ('sequence-types', 'MAPPINGS SPECIALMETHODS'),
        'NUMBERMETHODS': ('numeric-types', 'NUMBERS AUGMENTEDASSIGNMENT '
                          'SPECIALMETHODS'),
        'EXECUTION': ('execmodel', 'NAMESPACES DYNAMICFEATURES EXCEPTIONS'),
        'NAMESPACES': ('naming', 'global nonlocal ASSIGNMENT DELETION DYNAMICFEATURES'),
        'DYNAMICFEATURES': ('dynamic-features', ''),
        'SCOPING': 'NAMESPACES',
        'FRAMES': 'NAMESPACES',
        'EXCEPTIONS': ('exceptions', 'try except finally raise'),
        'CONVERSIONS': ('conversions', ''),
        'IDENTIFIERS': ('identifiers', 'keywords SPECIALIDENTIFIERS'),
        'SPECIALIDENTIFIERS': ('id-classes', ''),
        'PRIVATENAMES': ('atom-identifiers', ''),
        'LITERALS': ('atom-literals', 'STRINGS NUMBERS TUPLELITERALS '
                     'LISTLITERALS DICTIONARYLITERALS'),
        'TUPLES': 'SEQUENCES',
        'TUPLELITERALS': ('exprlists', 'TUPLES LITERALS'),
        'LISTS': ('typesseq-mutable', 'LISTLITERALS'),
        'LISTLITERALS': ('lists', 'LISTS LITERALS'),
        'DICTIONARIES': ('typesmapping', 'DICTIONARYLITERALS'),
        'DICTIONARYLITERALS': ('dict', 'DICTIONARIES LITERALS'),
        'ATTRIBUTES': ('attribute-references', 'getattr hasattr setattr ATTRIBUTEMETHODS'),
        'SUBSCRIPTS': ('subscriptions', 'SEQUENCEMETHODS'),
        'SLICINGS': ('slicings', 'SEQUENCEMETHODS'),
        'CALLS': ('calls', 'EXPRESSIONS'),
        'POWER': ('power', 'EXPRESSIONS'),
        'UNARY': ('unary', 'EXPRESSIONS'),
        'BINARY': ('binary', 'EXPRESSIONS'),
        'SHIFTING': ('shifting', 'EXPRESSIONS'),
        'BITWISE': ('bitwise', 'EXPRESSIONS'),
        'COMPARISON': ('comparisons', 'EXPRESSIONS BASICMETHODS'),
        'BOOLEAN': ('booleans', 'EXPRESSIONS TRUTHVALUE'),
        'ASSERTION': 'assert',
        'ASSIGNMENT': ('assignment', 'AUGMENTEDASSIGNMENT'),
        'AUGMENTEDASSIGNMENT': ('augassign', 'NUMBERMETHODS'),
        'DELETION': 'del',
        'RETURNING': 'return',
        'IMPORTING': 'agiza',
        'CONDITIONAL': 'if',
        'LOOPING': ('compound', 'for while break continue'),
        'TRUTHVALUE': ('truth', 'ikiwa while and or not BASICMETHODS'),
        'DEBUGGING': ('debugger', 'pdb'),
        'CONTEXTMANAGERS': ('context-managers', 'with'),
    }

    eleza __init__(self, input=None, output=None):
        self._input = input
        self._output = output

    @property
    eleza input(self):
        rudisha self._input or sys.stdin

    @property
    eleza output(self):
        rudisha self._output or sys.stdout

    eleza __repr__(self):
        ikiwa inspect.stack()[1][3] == '?':
            self()
            rudisha ''
        rudisha '<%s.%s instance>' % (self.__class__.__module__,
                                     self.__class__.__qualname__)

    _GoInteractive = object()
    eleza __call__(self, request=_GoInteractive):
        ikiwa request is not self._GoInteractive:
            self.help(request)
        else:
            self.intro()
            self.interact()
            self.output.write('''
You are now leaving help and returning to the Python interpreter.
If you want to ask for help on a particular object directly kutoka the
interpreter, you can type "help(object)".  Executing "help('string')"
has the same effect as typing a particular string at the help> prompt.
''')

    eleza interact(self):
        self.output.write('\n')
        while True:
            try:
                request = self.getline('help> ')
                ikiwa not request: break
            except (KeyboardInterrupt, EOFError):
                break
            request = request.strip()

            # Make sure significant trailing quoting marks of literals don't
            # get deleted while cleaning input
            ikiwa (len(request) > 2 and request[0] == request[-1] in ("'", '"')
                    and request[0] not in request[1:-1]):
                request = request[1:-1]
            ikiwa request.lower() in ('q', 'quit'): break
            ikiwa request == 'help':
                self.intro()
            else:
                self.help(request)

    eleza getline(self, prompt):
        """Read one line, using input() when appropriate."""
        ikiwa self.input is sys.stdin:
            rudisha input(prompt)
        else:
            self.output.write(prompt)
            self.output.flush()
            rudisha self.input.readline()

    eleza help(self, request):
        ikiwa type(request) is type(''):
            request = request.strip()
            ikiwa request == 'keywords': self.listkeywords()
            elikiwa request == 'symbols': self.listsymbols()
            elikiwa request == 'topics': self.listtopics()
            elikiwa request == 'modules': self.listmodules()
            elikiwa request[:8] == 'modules ':
                self.listmodules(request.split()[1])
            elikiwa request in self.symbols: self.showsymbol(request)
            elikiwa request in ['True', 'False', 'None']:
                # special case these keywords since they are objects too
                doc(eval(request), 'Help on %s:')
            elikiwa request in self.keywords: self.showtopic(request)
            elikiwa request in self.topics: self.showtopic(request)
            elikiwa request: doc(request, 'Help on %s:', output=self._output)
            else: doc(str, 'Help on %s:', output=self._output)
        elikiwa isinstance(request, Helper): self()
        else: doc(request, 'Help on %s:', output=self._output)
        self.output.write('\n')

    eleza intro(self):
        self.output.write('''
Welcome to Python {0}'s help utility!

If this is your first time using Python, you should definitely check out
the tutorial on the Internet at https://docs.python.org/{0}/tutorial/.

Enter the name of any module, keyword, or topic to get help on writing
Python programs and using Python modules.  To quit this help utility and
rudisha to the interpreter, just type "quit".

To get a list of available modules, keywords, symbols, or topics, type
"modules", "keywords", "symbols", or "topics".  Each module also comes
with a one-line summary of what it does; to list the modules whose name
or summary contain a given string such as "spam", type "modules spam".
'''.format('%d.%d' % sys.version_info[:2]))

    eleza list(self, items, columns=4, width=80):
        items = list(sorted(items))
        colw = width // columns
        rows = (len(items) + columns - 1) // columns
        for row in range(rows):
            for col in range(columns):
                i = col * rows + row
                ikiwa i < len(items):
                    self.output.write(items[i])
                    ikiwa col < columns - 1:
                        self.output.write(' ' + ' ' * (colw - 1 - len(items[i])))
            self.output.write('\n')

    eleza listkeywords(self):
        self.output.write('''
Here is a list of the Python keywords.  Enter any keyword to get more help.

''')
        self.list(self.keywords.keys())

    eleza listsymbols(self):
        self.output.write('''
Here is a list of the punctuation symbols which Python assigns special meaning
to. Enter any symbol to get more help.

''')
        self.list(self.symbols.keys())

    eleza listtopics(self):
        self.output.write('''
Here is a list of available topics.  Enter any topic name to get more help.

''')
        self.list(self.topics.keys())

    eleza showtopic(self, topic, more_xrefs=''):
        try:
            agiza pydoc_data.topics
        except ImportError:
            self.output.write('''
Sorry, topic and keyword documentation is not available because the
module "pydoc_data.topics" could not be found.
''')
            return
        target = self.topics.get(topic, self.keywords.get(topic))
        ikiwa not target:
            self.output.write('no documentation found for %s\n' % repr(topic))
            return
        ikiwa type(target) is type(''):
            rudisha self.showtopic(target, more_xrefs)

        label, xrefs = target
        try:
            doc = pydoc_data.topics.topics[label]
        except KeyError:
            self.output.write('no documentation found for %s\n' % repr(topic))
            return
        doc = doc.strip() + '\n'
        ikiwa more_xrefs:
            xrefs = (xrefs or '') + ' ' + more_xrefs
        ikiwa xrefs:
            agiza textwrap
            text = 'Related help topics: ' + ', '.join(xrefs.split()) + '\n'
            wrapped_text = textwrap.wrap(text, 72)
            doc += '\n%s\n' % '\n'.join(wrapped_text)
        pager(doc)

    eleza _gettopic(self, topic, more_xrefs=''):
        """Return unbuffered tuple of (topic, xrefs).

        If an error occurs here, the exception is caught and displayed by
        the url handler.

        This function duplicates the showtopic method but returns its
        result directly so it can be formatted for display in an html page.
        """
        try:
            agiza pydoc_data.topics
        except ImportError:
            return('''
Sorry, topic and keyword documentation is not available because the
module "pydoc_data.topics" could not be found.
''' , '')
        target = self.topics.get(topic, self.keywords.get(topic))
        ikiwa not target:
            raise ValueError('could not find topic')
        ikiwa isinstance(target, str):
            rudisha self._gettopic(target, more_xrefs)
        label, xrefs = target
        doc = pydoc_data.topics.topics[label]
        ikiwa more_xrefs:
            xrefs = (xrefs or '') + ' ' + more_xrefs
        rudisha doc, xrefs

    eleza showsymbol(self, symbol):
        target = self.symbols[symbol]
        topic, _, xrefs = target.partition(' ')
        self.showtopic(topic, xrefs)

    eleza listmodules(self, key=''):
        ikiwa key:
            self.output.write('''
Here is a list of modules whose name or summary contains '{}'.
If there are any, enter a module name to get more help.

'''.format(key))
            apropos(key)
        else:
            self.output.write('''
Please wait a moment while I gather a list of all available modules...

''')
            modules = {}
            eleza callback(path, modname, desc, modules=modules):
                ikiwa modname and modname[-9:] == '.__init__':
                    modname = modname[:-9] + ' (package)'
                ikiwa modname.find('.') < 0:
                    modules[modname] = 1
            eleza onerror(modname):
                callback(None, modname, None)
            ModuleScanner().run(callback, onerror=onerror)
            self.list(modules.keys())
            self.output.write('''
Enter any module name to get more help.  Or, type "modules spam" to search
for modules whose name or summary contain the string "spam".
''')

help = Helper()

kundi ModuleScanner:
    """An interruptible scanner that searches module synopses."""

    eleza run(self, callback, key=None, completer=None, onerror=None):
        ikiwa key: key = key.lower()
        self.quit = False
        seen = {}

        for modname in sys.builtin_module_names:
            ikiwa modname != '__main__':
                seen[modname] = 1
                ikiwa key is None:
                    callback(None, modname, '')
                else:
                    name = __import__(modname).__doc__ or ''
                    desc = name.split('\n')[0]
                    name = modname + ' - ' + desc
                    ikiwa name.lower().find(key) >= 0:
                        callback(None, modname, desc)

        for importer, modname, ispkg in pkgutil.walk_packages(onerror=onerror):
            ikiwa self.quit:
                break

            ikiwa key is None:
                callback(None, modname, '')
            else:
                try:
                    spec = pkgutil._get_spec(importer, modname)
                except SyntaxError:
                    # raised by tests for bad coding cookies or BOM
                    continue
                loader = spec.loader
                ikiwa hasattr(loader, 'get_source'):
                    try:
                        source = loader.get_source(modname)
                    except Exception:
                        ikiwa onerror:
                            onerror(modname)
                        continue
                    desc = source_synopsis(io.StringIO(source)) or ''
                    ikiwa hasattr(loader, 'get_filename'):
                        path = loader.get_filename(modname)
                    else:
                        path = None
                else:
                    try:
                        module = importlib._bootstrap._load(spec)
                    except ImportError:
                        ikiwa onerror:
                            onerror(modname)
                        continue
                    desc = module.__doc__.splitlines()[0] ikiwa module.__doc__ else ''
                    path = getattr(module,'__file__',None)
                name = modname + ' - ' + desc
                ikiwa name.lower().find(key) >= 0:
                    callback(path, modname, desc)

        ikiwa completer:
            completer()

eleza apropos(key):
    """Print all the one-line module summaries that contain a substring."""
    eleza callback(path, modname, desc):
        ikiwa modname[-9:] == '.__init__':
            modname = modname[:-9] + ' (package)'
        andika(modname, desc and '- ' + desc)
    eleza onerror(modname):
        pass
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore') # ignore problems during agiza
        ModuleScanner().run(callback, key, onerror=onerror)

# --------------------------------------- enhanced Web browser interface

eleza _start_server(urlhandler, hostname, port):
    """Start an HTTP server thread on a specific port.

    Start an HTML/text server thread, so HTML or text documents can be
    browsed dynamically and interactively with a Web browser.  Example use:

        >>> agiza time
        >>> agiza pydoc

        Define a URL handler.  To determine what the client is asking
        for, check the URL and content_type.

        Then get or generate some text or HTML code and rudisha it.

        >>> eleza my_url_handler(url, content_type):
        ...     text = 'the URL sent was: (%s, %s)' % (url, content_type)
        ...     rudisha text

        Start server thread on port 0.
        If you use port 0, the server will pick a random port number.
        You can then use serverthread.port to get the port number.

        >>> port = 0
        >>> serverthread = pydoc._start_server(my_url_handler, port)

        Check that the server is really started.  If it is, open browser
        and get first page.  Use serverthread.url as the starting page.

        >>> ikiwa serverthread.serving:
        ...    agiza webbrowser

        The next two lines are commented out so a browser doesn't open if
        doctest is run on this module.

        #...    webbrowser.open(serverthread.url)
        #True

        Let the server do its thing. We just need to monitor its status.
        Use time.sleep so the loop doesn't hog the CPU.

        >>> starttime = time.monotonic()
        >>> timeout = 1                    #seconds

        This is a short timeout for testing purposes.

        >>> while serverthread.serving:
        ...     time.sleep(.01)
        ...     ikiwa serverthread.serving and time.monotonic() - starttime > timeout:
        ...          serverthread.stop()
        ...          break

        Print any errors that may have occurred.

        >>> andika(serverthread.error)
        None
   """
    agiza http.server
    agiza email.message
    agiza select
    agiza threading

    kundi DocHandler(http.server.BaseHTTPRequestHandler):

        eleza do_GET(self):
            """Process a request kutoka an HTML browser.

            The URL received is in self.path.
            Get an HTML page kutoka self.urlhandler and send it.
            """
            ikiwa self.path.endswith('.css'):
                content_type = 'text/css'
            else:
                content_type = 'text/html'
            self.send_response(200)
            self.send_header('Content-Type', '%s; charset=UTF-8' % content_type)
            self.end_headers()
            self.wfile.write(self.urlhandler(
                self.path, content_type).encode('utf-8'))

        eleza log_message(self, *args):
            # Don't log messages.
            pass

    kundi DocServer(http.server.HTTPServer):

        eleza __init__(self, host, port, callback):
            self.host = host
            self.address = (self.host, port)
            self.callback = callback
            self.base.__init__(self, self.address, self.handler)
            self.quit = False

        eleza serve_until_quit(self):
            while not self.quit:
                rd, wr, ex = select.select([self.socket.fileno()], [], [], 1)
                ikiwa rd:
                    self.handle_request()
            self.server_close()

        eleza server_activate(self):
            self.base.server_activate(self)
            ikiwa self.callback:
                self.callback(self)

    kundi ServerThread(threading.Thread):

        eleza __init__(self, urlhandler, host, port):
            self.urlhandler = urlhandler
            self.host = host
            self.port = int(port)
            threading.Thread.__init__(self)
            self.serving = False
            self.error = None

        eleza run(self):
            """Start the server."""
            try:
                DocServer.base = http.server.HTTPServer
                DocServer.handler = DocHandler
                DocHandler.MessageClass = email.message.Message
                DocHandler.urlhandler = staticmethod(self.urlhandler)
                docsvr = DocServer(self.host, self.port, self.ready)
                self.docserver = docsvr
                docsvr.serve_until_quit()
            except Exception as e:
                self.error = e

        eleza ready(self, server):
            self.serving = True
            self.host = server.host
            self.port = server.server_port
            self.url = 'http://%s:%d/' % (self.host, self.port)

        eleza stop(self):
            """Stop the server and this thread nicely"""
            self.docserver.quit = True
            self.join()
            # explicitly break a reference cycle: DocServer.callback
            # has indirectly a reference to ServerThread.
            self.docserver = None
            self.serving = False
            self.url = None

    thread = ServerThread(urlhandler, hostname, port)
    thread.start()
    # Wait until thread.serving is True to make sure we are
    # really up before returning.
    while not thread.error and not thread.serving:
        time.sleep(.01)
    rudisha thread


eleza _url_handler(url, content_type="text/html"):
    """The pydoc url handler for use with the pydoc server.

    If the content_type is 'text/css', the _pydoc.css style
    sheet is read and returned ikiwa it exits.

    If the content_type is 'text/html', then the result of
    get_html_page(url) is returned.
    """
    kundi _HTMLDoc(HTMLDoc):

        eleza page(self, title, contents):
            """Format an HTML page."""
            css_path = "pydoc_data/_pydoc.css"
            css_link = (
                '<link rel="stylesheet" type="text/css" href="%s">' %
                css_path)
            rudisha '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title>Pydoc: %s</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
%s</head><body bgcolor="#f0f0f8">%s<div style="clear:both;padding-top:.5em;">%s</div>
</body></html>''' % (title, css_link, html_navbar(), contents)

        eleza filelink(self, url, path):
            rudisha '<a href="getfile?key=%s">%s</a>' % (url, path)


    html = _HTMLDoc()

    eleza html_navbar():
        version = html.escape("%s [%s, %s]" % (platform.python_version(),
                                               platform.python_build()[0],
                                               platform.python_compiler()))
        rudisha """
            <div style='float:left'>
                Python %s<br>%s
            </div>
            <div style='float:right'>
                <div style='text-align:center'>
                  <a href="index.html">Module Index</a>
                  : <a href="topics.html">Topics</a>
                  : <a href="keywords.html">Keywords</a>
                </div>
                <div>
                    <form action="get" style='display:inline;'>
                      <input type=text name=key size=15>
                      <input type=submit value="Get">
                    </form>&nbsp;
                    <form action="search" style='display:inline;'>
                      <input type=text name=key size=15>
                      <input type=submit value="Search">
                    </form>
                </div>
            </div>
            """ % (version, html.escape(platform.platform(terse=True)))

    eleza html_index():
        """Module Index page."""

        eleza bltinlink(name):
            rudisha '<a href="%s.html">%s</a>' % (name, name)

        heading = html.heading(
            '<big><big><strong>Index of Modules</strong></big></big>',
            '#ffffff', '#7799ee')
        names = [name for name in sys.builtin_module_names
                 ikiwa name != '__main__']
        contents = html.multicolumn(names, bltinlink)
        contents = [heading, '<p>' + html.bigsection(
            'Built-in Modules', '#ffffff', '#ee77aa', contents)]

        seen = {}
        for dir in sys.path:
            contents.append(html.index(dir, seen))

        contents.append(
            '<p align=right><font color="#909090" face="helvetica,'
            'arial"><strong>pydoc</strong> by Ka-Ping Yee'
            '&lt;ping@lfw.org&gt;</font>')
        rudisha 'Index of Modules', ''.join(contents)

    eleza html_search(key):
        """Search results page."""
        # scan for modules
        search_result = []

        eleza callback(path, modname, desc):
            ikiwa modname[-9:] == '.__init__':
                modname = modname[:-9] + ' (package)'
            search_result.append((modname, desc and '- ' + desc))

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore') # ignore problems during agiza
            eleza onerror(modname):
                pass
            ModuleScanner().run(callback, key, onerror=onerror)

        # format page
        eleza bltinlink(name):
            rudisha '<a href="%s.html">%s</a>' % (name, name)

        results = []
        heading = html.heading(
            '<big><big><strong>Search Results</strong></big></big>',
            '#ffffff', '#7799ee')
        for name, desc in search_result:
            results.append(bltinlink(name) + desc)
        contents = heading + html.bigsection(
            'key = %s' % key, '#ffffff', '#ee77aa', '<br>'.join(results))
        rudisha 'Search Results', contents

    eleza html_getfile(path):
        """Get and display a source file listing safely."""
        path = urllib.parse.unquote(path)
        with tokenize.open(path) as fp:
            lines = html.escape(fp.read())
        body = '<pre>%s</pre>' % lines
        heading = html.heading(
            '<big><big><strong>File Listing</strong></big></big>',
            '#ffffff', '#7799ee')
        contents = heading + html.bigsection(
            'File: %s' % path, '#ffffff', '#ee77aa', body)
        rudisha 'getfile %s' % path, contents

    eleza html_topics():
        """Index of topic texts available."""

        eleza bltinlink(name):
            rudisha '<a href="topic?key=%s">%s</a>' % (name, name)

        heading = html.heading(
            '<big><big><strong>INDEX</strong></big></big>',
            '#ffffff', '#7799ee')
        names = sorted(Helper.topics.keys())

        contents = html.multicolumn(names, bltinlink)
        contents = heading + html.bigsection(
            'Topics', '#ffffff', '#ee77aa', contents)
        rudisha 'Topics', contents

    eleza html_keywords():
        """Index of keywords."""
        heading = html.heading(
            '<big><big><strong>INDEX</strong></big></big>',
            '#ffffff', '#7799ee')
        names = sorted(Helper.keywords.keys())

        eleza bltinlink(name):
            rudisha '<a href="topic?key=%s">%s</a>' % (name, name)

        contents = html.multicolumn(names, bltinlink)
        contents = heading + html.bigsection(
            'Keywords', '#ffffff', '#ee77aa', contents)
        rudisha 'Keywords', contents

    eleza html_topicpage(topic):
        """Topic or keyword help page."""
        buf = io.StringIO()
        htmlhelp = Helper(buf, buf)
        contents, xrefs = htmlhelp._gettopic(topic)
        ikiwa topic in htmlhelp.keywords:
            title = 'KEYWORD'
        else:
            title = 'TOPIC'
        heading = html.heading(
            '<big><big><strong>%s</strong></big></big>' % title,
            '#ffffff', '#7799ee')
        contents = '<pre>%s</pre>' % html.markup(contents)
        contents = html.bigsection(topic , '#ffffff','#ee77aa', contents)
        ikiwa xrefs:
            xrefs = sorted(xrefs.split())

            eleza bltinlink(name):
                rudisha '<a href="topic?key=%s">%s</a>' % (name, name)

            xrefs = html.multicolumn(xrefs, bltinlink)
            xrefs = html.section('Related help topics: ',
                                 '#ffffff', '#ee77aa', xrefs)
        rudisha ('%s %s' % (title, topic),
                ''.join((heading, contents, xrefs)))

    eleza html_getobj(url):
        obj = locate(url, forceload=1)
        ikiwa obj is None and url != 'None':
            raise ValueError('could not find object')
        title = describe(obj)
        content = html.document(obj, url)
        rudisha title, content

    eleza html_error(url, exc):
        heading = html.heading(
            '<big><big><strong>Error</strong></big></big>',
            '#ffffff', '#7799ee')
        contents = '<br>'.join(html.escape(line) for line in
                               format_exception_only(type(exc), exc))
        contents = heading + html.bigsection(url, '#ffffff', '#bb0000',
                                             contents)
        rudisha "Error - %s" % url, contents

    eleza get_html_page(url):
        """Generate an HTML page for url."""
        complete_url = url
        ikiwa url.endswith('.html'):
            url = url[:-5]
        try:
            ikiwa url in ("", "index"):
                title, content = html_index()
            elikiwa url == "topics":
                title, content = html_topics()
            elikiwa url == "keywords":
                title, content = html_keywords()
            elikiwa '=' in url:
                op, _, url = url.partition('=')
                ikiwa op == "search?key":
                    title, content = html_search(url)
                elikiwa op == "getfile?key":
                    title, content = html_getfile(url)
                elikiwa op == "topic?key":
                    # try topics first, then objects.
                    try:
                        title, content = html_topicpage(url)
                    except ValueError:
                        title, content = html_getobj(url)
                elikiwa op == "get?key":
                    # try objects first, then topics.
                    ikiwa url in ("", "index"):
                        title, content = html_index()
                    else:
                        try:
                            title, content = html_getobj(url)
                        except ValueError:
                            title, content = html_topicpage(url)
                else:
                    raise ValueError('bad pydoc url')
            else:
                title, content = html_getobj(url)
        except Exception as exc:
            # Catch any errors and display them in an error page.
            title, content = html_error(complete_url, exc)
        rudisha html.page(title, content)

    ikiwa url.startswith('/'):
        url = url[1:]
    ikiwa content_type == 'text/css':
        path_here = os.path.dirname(os.path.realpath(__file__))
        css_path = os.path.join(path_here, url)
        with open(css_path) as fp:
            rudisha ''.join(fp.readlines())
    elikiwa content_type == 'text/html':
        rudisha get_html_page(url)
    # Errors outside the url handler are caught by the server.
    raise TypeError('unknown content type %r for url %s' % (content_type, url))


eleza browse(port=0, *, open_browser=True, hostname='localhost'):
    """Start the enhanced pydoc Web server and open a Web browser.

    Use port '0' to start the server on an arbitrary port.
    Set open_browser to False to suppress opening a browser.
    """
    agiza webbrowser
    serverthread = _start_server(_url_handler, hostname, port)
    ikiwa serverthread.error:
        andika(serverthread.error)
        return
    ikiwa serverthread.serving:
        server_help_msg = 'Server commands: [b]rowser, [q]uit'
        ikiwa open_browser:
            webbrowser.open(serverthread.url)
        try:
            andika('Server ready at', serverthread.url)
            andika(server_help_msg)
            while serverthread.serving:
                cmd = input('server> ')
                cmd = cmd.lower()
                ikiwa cmd == 'q':
                    break
                elikiwa cmd == 'b':
                    webbrowser.open(serverthread.url)
                else:
                    andika(server_help_msg)
        except (KeyboardInterrupt, EOFError):
            andika()
        finally:
            ikiwa serverthread.serving:
                serverthread.stop()
                andika('Server stopped')


# -------------------------------------------------- command-line interface

eleza ispath(x):
    rudisha isinstance(x, str) and x.find(os.sep) >= 0

eleza _get_revised_path(given_path, argv0):
    """Ensures current directory is on returned path, and argv0 directory is not

    Exception: argv0 dir is left alone ikiwa it's also pydoc's directory.

    Returns a new path entry list, or None ikiwa no adjustment is needed.
    """
    # Scripts may get the current directory in their path by default ikiwa they're
    # run with the -m switch, or directly kutoka the current directory.
    # The interactive prompt also allows agizas kutoka the current directory.

    # Accordingly, ikiwa the current directory is already present, don't make
    # any changes to the given_path
    ikiwa '' in given_path or os.curdir in given_path or os.getcwd() in given_path:
        rudisha None

    # Otherwise, add the current directory to the given path, and remove the
    # script directory (as long as the latter isn't also pydoc's directory.
    stdlib_dir = os.path.dirname(__file__)
    script_dir = os.path.dirname(argv0)
    revised_path = given_path.copy()
    ikiwa script_dir in given_path and not os.path.samefile(script_dir, stdlib_dir):
        revised_path.remove(script_dir)
    revised_path.insert(0, os.getcwd())
    rudisha revised_path


# Note: the tests only cover _get_revised_path, not _adjust_cli_path itself
eleza _adjust_cli_sys_path():
    """Ensures current directory is on sys.path, and __main__ directory is not.

    Exception: __main__ dir is left alone ikiwa it's also pydoc's directory.
    """
    revised_path = _get_revised_path(sys.path, sys.argv[0])
    ikiwa revised_path is not None:
        sys.path[:] = revised_path


eleza cli():
    """Command-line interface (looks at sys.argv to decide what to do)."""
    agiza getopt
    kundi BadUsage(Exception): pass

    _adjust_cli_sys_path()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'bk:n:p:w')
        writing = False
        start_server = False
        open_browser = False
        port = 0
        hostname = 'localhost'
        for opt, val in opts:
            ikiwa opt == '-b':
                start_server = True
                open_browser = True
            ikiwa opt == '-k':
                apropos(val)
                return
            ikiwa opt == '-p':
                start_server = True
                port = val
            ikiwa opt == '-w':
                writing = True
            ikiwa opt == '-n':
                start_server = True
                hostname = val

        ikiwa start_server:
            browse(port, hostname=hostname, open_browser=open_browser)
            return

        ikiwa not args: raise BadUsage
        for arg in args:
            ikiwa ispath(arg) and not os.path.exists(arg):
                andika('file %r does not exist' % arg)
                break
            try:
                ikiwa ispath(arg) and os.path.isfile(arg):
                    arg = agizafile(arg)
                ikiwa writing:
                    ikiwa ispath(arg) and os.path.isdir(arg):
                        writedocs(arg)
                    else:
                        writedoc(arg)
                else:
                    help.help(arg)
            except ErrorDuringImport as value:
                andika(value)

    except (getopt.error, BadUsage):
        cmd = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        andika("""pydoc - the Python documentation tool

{cmd} <name> ...
    Show text documentation on something.  <name> may be the name of a
    Python keyword, topic, function, module, or package, or a dotted
    reference to a kundi or function within a module or module in a
    package.  If <name> contains a '{sep}', it is used as the path to a
    Python source file to document. If name is 'keywords', 'topics',
    or 'modules', a listing of these things is displayed.

{cmd} -k <keyword>
    Search for a keyword in the synopsis lines of all available modules.

{cmd} -n <hostname>
    Start an HTTP server with the given hostname (default: localhost).

{cmd} -p <port>
    Start an HTTP server on the given port on the local machine.  Port
    number 0 can be used to get an arbitrary unused port.

{cmd} -b
    Start an HTTP server on an arbitrary unused port and open a Web browser
    to interactively browse documentation.  This option can be used in
    combination with -n and/or -p.

{cmd} -w <name> ...
    Write out the HTML documentation for a module to a file in the current
    directory.  If <name> contains a '{sep}', it is treated as a filename; if
    it names a directory, documentation is written for all the contents.
""".format(cmd=cmd, sep=os.sep))

ikiwa __name__ == '__main__':
    cli()
