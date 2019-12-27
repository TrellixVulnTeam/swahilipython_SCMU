"""Python part of the warnings subsystem."""

agiza sys


__all__ = ["warn", "warn_explicit", "showwarning",
           "formatwarning", "filterwarnings", "simplefilter",
           "resetwarnings", "catch_warnings"]

eleza showwarning(message, category, filename, lineno, file=None, line=None):
    """Hook to write a warning to a file; replace ikiwa you like."""
    msg = WarningMessage(message, category, filename, lineno, file, line)
    _showwarnmsg_impl(msg)

eleza formatwarning(message, category, filename, lineno, line=None):
    """Function to format a warning the standard way."""
    msg = WarningMessage(message, category, filename, lineno, None, line)
    rudisha _formatwarnmsg_impl(msg)

eleza _showwarnmsg_impl(msg):
    file = msg.file
    ikiwa file is None:
        file = sys.stderr
        ikiwa file is None:
            # sys.stderr is None when run with pythonw.exe:
            # warnings get lost
            return
    text = _formatwarnmsg(msg)
    try:
        file.write(text)
    except OSError:
        # the file (probably stderr) is invalid - this warning gets lost.
        pass

eleza _formatwarnmsg_impl(msg):
    category = msg.category.__name__
    s =  f"{msg.filename}:{msg.lineno}: {category}: {msg.message}\n"

    ikiwa msg.line is None:
        try:
            agiza linecache
            line = linecache.getline(msg.filename, msg.lineno)
        except Exception:
            # When a warning is logged during Python shutdown, linecache
            # and the agiza machinery don't work anymore
            line = None
            linecache = None
    else:
        line = msg.line
    ikiwa line:
        line = line.strip()
        s += "  %s\n" % line

    ikiwa msg.source is not None:
        try:
            agiza tracemalloc
        # Logging a warning should not raise a new exception:
        # catch Exception, not only ImportError and RecursionError.
        except Exception:
            # don't suggest to enable tracemalloc ikiwa it's not available
            tracing = True
            tb = None
        else:
            tracing = tracemalloc.is_tracing()
            try:
                tb = tracemalloc.get_object_traceback(msg.source)
            except Exception:
                # When a warning is logged during Python shutdown, tracemalloc
                # and the agiza machinery don't work anymore
                tb = None

        ikiwa tb is not None:
            s += 'Object allocated at (most recent call last):\n'
            for frame in tb:
                s += ('  File "%s", lineno %s\n'
                      % (frame.filename, frame.lineno))

                try:
                    ikiwa linecache is not None:
                        line = linecache.getline(frame.filename, frame.lineno)
                    else:
                        line = None
                except Exception:
                    line = None
                ikiwa line:
                    line = line.strip()
                    s += '    %s\n' % line
        elikiwa not tracing:
            s += (f'{category}: Enable tracemalloc to get the object '
                  f'allocation traceback\n')
    rudisha s

# Keep a reference to check ikiwa the function was replaced
_showwarning_orig = showwarning

eleza _showwarnmsg(msg):
    """Hook to write a warning to a file; replace ikiwa you like."""
    try:
        sw = showwarning
    except NameError:
        pass
    else:
        ikiwa sw is not _showwarning_orig:
            # warnings.showwarning() was replaced
            ikiwa not callable(sw):
                raise TypeError("warnings.showwarning() must be set to a "
                                "function or method")

            sw(msg.message, msg.category, msg.filename, msg.lineno,
               msg.file, msg.line)
            return
    _showwarnmsg_impl(msg)

# Keep a reference to check ikiwa the function was replaced
_formatwarning_orig = formatwarning

eleza _formatwarnmsg(msg):
    """Function to format a warning the standard way."""
    try:
        fw = formatwarning
    except NameError:
        pass
    else:
        ikiwa fw is not _formatwarning_orig:
            # warnings.formatwarning() was replaced
            rudisha fw(msg.message, msg.category,
                      msg.filename, msg.lineno, msg.line)
    rudisha _formatwarnmsg_impl(msg)

eleza filterwarnings(action, message="", category=Warning, module="", lineno=0,
                   append=False):
    """Insert an entry into the list of warnings filters (at the front).

    'action' -- one of "error", "ignore", "always", "default", "module",
                or "once"
    'message' -- a regex that the warning message must match
    'category' -- a kundi that the warning must be a subkundi of
    'module' -- a regex that the module name must match
    'lineno' -- an integer line number, 0 matches all warnings
    'append' -- ikiwa true, append to the list of filters
    """
    assert action in ("error", "ignore", "always", "default", "module",
                      "once"), "invalid action: %r" % (action,)
    assert isinstance(message, str), "message must be a string"
    assert isinstance(category, type), "category must be a class"
    assert issubclass(category, Warning), "category must be a Warning subclass"
    assert isinstance(module, str), "module must be a string"
    assert isinstance(lineno, int) and lineno >= 0, \
           "lineno must be an int >= 0"

    ikiwa message or module:
        agiza re

    ikiwa message:
        message = re.compile(message, re.I)
    else:
        message = None
    ikiwa module:
        module = re.compile(module)
    else:
        module = None

    _add_filter(action, message, category, module, lineno, append=append)

eleza simplefilter(action, category=Warning, lineno=0, append=False):
    """Insert a simple entry into the list of warnings filters (at the front).

    A simple filter matches all modules and messages.
    'action' -- one of "error", "ignore", "always", "default", "module",
                or "once"
    'category' -- a kundi that the warning must be a subkundi of
    'lineno' -- an integer line number, 0 matches all warnings
    'append' -- ikiwa true, append to the list of filters
    """
    assert action in ("error", "ignore", "always", "default", "module",
                      "once"), "invalid action: %r" % (action,)
    assert isinstance(lineno, int) and lineno >= 0, \
           "lineno must be an int >= 0"
    _add_filter(action, None, category, None, lineno, append=append)

eleza _add_filter(*item, append):
    # Remove possible duplicate filters, so new one will be placed
    # in correct place. If append=True and duplicate exists, do nothing.
    ikiwa not append:
        try:
            filters.remove(item)
        except ValueError:
            pass
        filters.insert(0, item)
    else:
        ikiwa item not in filters:
            filters.append(item)
    _filters_mutated()

eleza resetwarnings():
    """Clear the list of warning filters, so that no filters are active."""
    filters[:] = []
    _filters_mutated()

kundi _OptionError(Exception):
    """Exception used by option processing helpers."""
    pass

# Helper to process -W options passed via sys.warnoptions
eleza _processoptions(args):
    for arg in args:
        try:
            _setoption(arg)
        except _OptionError as msg:
            andika("Invalid -W option ignored:", msg, file=sys.stderr)

# Helper for _processoptions()
eleza _setoption(arg):
    agiza re
    parts = arg.split(':')
    ikiwa len(parts) > 5:
        raise _OptionError("too many fields (max 5): %r" % (arg,))
    while len(parts) < 5:
        parts.append('')
    action, message, category, module, lineno = [s.strip()
                                                 for s in parts]
    action = _getaction(action)
    message = re.escape(message)
    category = _getcategory(category)
    module = re.escape(module)
    ikiwa module:
        module = module + '$'
    ikiwa lineno:
        try:
            lineno = int(lineno)
            ikiwa lineno < 0:
                raise ValueError
        except (ValueError, OverflowError):
            raise _OptionError("invalid lineno %r" % (lineno,)) kutoka None
    else:
        lineno = 0
    filterwarnings(action, message, category, module, lineno)

# Helper for _setoption()
eleza _getaction(action):
    ikiwa not action:
        rudisha "default"
    ikiwa action == "all": rudisha "always" # Alias
    for a in ('default', 'always', 'ignore', 'module', 'once', 'error'):
        ikiwa a.startswith(action):
            rudisha a
    raise _OptionError("invalid action: %r" % (action,))

# Helper for _setoption()
eleza _getcategory(category):
    agiza re
    ikiwa not category:
        rudisha Warning
    ikiwa re.match("^[a-zA-Z0-9_]+$", category):
        try:
            cat = eval(category)
        except NameError:
            raise _OptionError("unknown warning category: %r" % (category,)) kutoka None
    else:
        i = category.rfind(".")
        module = category[:i]
        klass = category[i+1:]
        try:
            m = __import__(module, None, None, [klass])
        except ImportError:
            raise _OptionError("invalid module name: %r" % (module,)) kutoka None
        try:
            cat = getattr(m, klass)
        except AttributeError:
            raise _OptionError("unknown warning category: %r" % (category,)) kutoka None
    ikiwa not issubclass(cat, Warning):
        raise _OptionError("invalid warning category: %r" % (category,))
    rudisha cat


eleza _is_internal_frame(frame):
    """Signal whether the frame is an internal CPython implementation detail."""
    filename = frame.f_code.co_filename
    rudisha 'importlib' in filename and '_bootstrap' in filename


eleza _next_external_frame(frame):
    """Find the next frame that doesn't involve CPython internals."""
    frame = frame.f_back
    while frame is not None and _is_internal_frame(frame):
        frame = frame.f_back
    rudisha frame


# Code typically replaced by _warnings
eleza warn(message, category=None, stacklevel=1, source=None):
    """Issue a warning, or maybe ignore it or raise an exception."""
    # Check ikiwa message is already a Warning object
    ikiwa isinstance(message, Warning):
        category = message.__class__
    # Check category argument
    ikiwa category is None:
        category = UserWarning
    ikiwa not (isinstance(category, type) and issubclass(category, Warning)):
        raise TypeError("category must be a Warning subclass, "
                        "not '{:s}'".format(type(category).__name__))
    # Get context information
    try:
        ikiwa stacklevel <= 1 or _is_internal_frame(sys._getframe(1)):
            # If frame is too small to care or ikiwa the warning originated in
            # internal code, then do not try to hide any frames.
            frame = sys._getframe(stacklevel)
        else:
            frame = sys._getframe(1)
            # Look for one frame less since the above line starts us off.
            for x in range(stacklevel-1):
                frame = _next_external_frame(frame)
                ikiwa frame is None:
                    raise ValueError
    except ValueError:
        globals = sys.__dict__
        filename = "sys"
        lineno = 1
    else:
        globals = frame.f_globals
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
    ikiwa '__name__' in globals:
        module = globals['__name__']
    else:
        module = "<string>"
    registry = globals.setdefault("__warningregistry__", {})
    warn_explicit(message, category, filename, lineno, module, registry,
                  globals, source)

eleza warn_explicit(message, category, filename, lineno,
                  module=None, registry=None, module_globals=None,
                  source=None):
    lineno = int(lineno)
    ikiwa module is None:
        module = filename or "<unknown>"
        ikiwa module[-3:].lower() == ".py":
            module = module[:-3] # XXX What about leading pathname?
    ikiwa registry is None:
        registry = {}
    ikiwa registry.get('version', 0) != _filters_version:
        registry.clear()
        registry['version'] = _filters_version
    ikiwa isinstance(message, Warning):
        text = str(message)
        category = message.__class__
    else:
        text = message
        message = category(message)
    key = (text, category, lineno)
    # Quick test for common case
    ikiwa registry.get(key):
        return
    # Search the filters
    for item in filters:
        action, msg, cat, mod, ln = item
        ikiwa ((msg is None or msg.match(text)) and
            issubclass(category, cat) and
            (mod is None or mod.match(module)) and
            (ln == 0 or lineno == ln)):
            break
    else:
        action = defaultaction
    # Early exit actions
    ikiwa action == "ignore":
        return

    # Prime the linecache for formatting, in case the
    # "file" is actually in a zipfile or something.
    agiza linecache
    linecache.getlines(filename, module_globals)

    ikiwa action == "error":
        raise message
    # Other actions
    ikiwa action == "once":
        registry[key] = 1
        oncekey = (text, category)
        ikiwa onceregistry.get(oncekey):
            return
        onceregistry[oncekey] = 1
    elikiwa action == "always":
        pass
    elikiwa action == "module":
        registry[key] = 1
        altkey = (text, category, 0)
        ikiwa registry.get(altkey):
            return
        registry[altkey] = 1
    elikiwa action == "default":
        registry[key] = 1
    else:
        # Unrecognized actions are errors
        raise RuntimeError(
              "Unrecognized action (%r) in warnings.filters:\n %s" %
              (action, item))
    # Print message and context
    msg = WarningMessage(message, category, filename, lineno, source)
    _showwarnmsg(msg)


kundi WarningMessage(object):

    _WARNING_DETAILS = ("message", "category", "filename", "lineno", "file",
                        "line", "source")

    eleza __init__(self, message, category, filename, lineno, file=None,
                 line=None, source=None):
        self.message = message
        self.category = category
        self.filename = filename
        self.lineno = lineno
        self.file = file
        self.line = line
        self.source = source
        self._category_name = category.__name__ ikiwa category else None

    eleza __str__(self):
        rudisha ("{message : %r, category : %r, filename : %r, lineno : %s, "
                    "line : %r}" % (self.message, self._category_name,
                                    self.filename, self.lineno, self.line))


kundi catch_warnings(object):

    """A context manager that copies and restores the warnings filter upon
    exiting the context.

    The 'record' argument specifies whether warnings should be captured by a
    custom implementation of warnings.showwarning() and be appended to a list
    returned by the context manager. Otherwise None is returned by the context
    manager. The objects appended to the list are arguments whose attributes
    mirror the arguments to showwarning().

    The 'module' argument is to specify an alternative module to the module
    named 'warnings' and imported under that name. This argument is only useful
    when testing the warnings module itself.

    """

    eleza __init__(self, *, record=False, module=None):
        """Specify whether to record warnings and ikiwa an alternative module
        should be used other than sys.modules['warnings'].

        For compatibility with Python 3.0, please consider all arguments to be
        keyword-only.

        """
        self._record = record
        self._module = sys.modules['warnings'] ikiwa module is None else module
        self._entered = False

    eleza __repr__(self):
        args = []
        ikiwa self._record:
            args.append("record=True")
        ikiwa self._module is not sys.modules['warnings']:
            args.append("module=%r" % self._module)
        name = type(self).__name__
        rudisha "%s(%s)" % (name, ", ".join(args))

    eleza __enter__(self):
        ikiwa self._entered:
            raise RuntimeError("Cannot enter %r twice" % self)
        self._entered = True
        self._filters = self._module.filters
        self._module.filters = self._filters[:]
        self._module._filters_mutated()
        self._showwarning = self._module.showwarning
        self._showwarnmsg_impl = self._module._showwarnmsg_impl
        ikiwa self._record:
            log = []
            self._module._showwarnmsg_impl = log.append
            # Reset showwarning() to the default implementation to make sure
            # that _showwarnmsg() calls _showwarnmsg_impl()
            self._module.showwarning = self._module._showwarning_orig
            rudisha log
        else:
            rudisha None

    eleza __exit__(self, *exc_info):
        ikiwa not self._entered:
            raise RuntimeError("Cannot exit %r without entering first" % self)
        self._module.filters = self._filters
        self._module._filters_mutated()
        self._module.showwarning = self._showwarning
        self._module._showwarnmsg_impl = self._showwarnmsg_impl


# Private utility function called by _PyErr_WarnUnawaitedCoroutine
eleza _warn_unawaited_coroutine(coro):
    msg_lines = [
        f"coroutine '{coro.__qualname__}' was never awaited\n"
    ]
    ikiwa coro.cr_origin is not None:
        agiza linecache, traceback
        eleza extract():
            for filename, lineno, funcname in reversed(coro.cr_origin):
                line = linecache.getline(filename, lineno)
                yield (filename, lineno, funcname, line)
        msg_lines.append("Coroutine created at (most recent call last)\n")
        msg_lines += traceback.format_list(list(extract()))
    msg = "".join(msg_lines).rstrip("\n")
    # Passing source= here means that ikiwa the user happens to have tracemalloc
    # enabled and tracking where the coroutine was created, the warning will
    # contain that traceback. This does mean that ikiwa they have *both*
    # coroutine origin tracking *and* tracemalloc enabled, they'll get two
    # partially-redundant tracebacks. If we wanted to be clever we could
    # probably detect this case and avoid it, but for now we don't bother.
    warn(msg, category=RuntimeWarning, stacklevel=2, source=coro)


# filters contains a sequence of filter 5-tuples
# The components of the 5-tuple are:
# - an action: error, ignore, always, default, module, or once
# - a compiled regex that must match the warning message
# - a kundi representing the warning category
# - a compiled regex that must match the module that is being warned
# - a line number for the line being warning, or 0 to mean any line
# If either ikiwa the compiled regexs are None, match anything.
try:
    kutoka _warnings agiza (filters, _defaultaction, _onceregistry,
                           warn, warn_explicit, _filters_mutated)
    defaultaction = _defaultaction
    onceregistry = _onceregistry
    _warnings_defaults = True
except ImportError:
    filters = []
    defaultaction = "default"
    onceregistry = {}

    _filters_version = 1

    eleza _filters_mutated():
        global _filters_version
        _filters_version += 1

    _warnings_defaults = False


# Module initialization
_processoptions(sys.warnoptions)
ikiwa not _warnings_defaults:
    # Several warning categories are ignored by default in regular builds
    ikiwa not hasattr(sys, 'gettotalrefcount'):
        filterwarnings("default", category=DeprecationWarning,
                       module="__main__", append=1)
        simplefilter("ignore", category=DeprecationWarning, append=1)
        simplefilter("ignore", category=PendingDeprecationWarning, append=1)
        simplefilter("ignore", category=ImportWarning, append=1)
        simplefilter("ignore", category=ResourceWarning, append=1)

del _warnings_defaults
