"""Python part of the warnings subsystem."""

agiza sys


__all__ = ["warn", "warn_explicit", "showwarning",
           "formatwarning", "filterwarnings", "simplefilter",
           "resetwarnings", "catch_warnings"]

eleza showwarning(message, category, filename, lineno, file=Tupu, line=Tupu):
    """Hook to write a warning to a file; replace ikiwa you like."""
    msg = WarningMessage(message, category, filename, lineno, file, line)
    _showwarnmsg_impl(msg)

eleza formatwarning(message, category, filename, lineno, line=Tupu):
    """Function to format a warning the standard way."""
    msg = WarningMessage(message, category, filename, lineno, Tupu, line)
    rudisha _formatwarnmsg_impl(msg)

eleza _showwarnmsg_impl(msg):
    file = msg.file
    ikiwa file ni Tupu:
        file = sys.stderr
        ikiwa file ni Tupu:
            # sys.stderr ni Tupu when run ukijumuisha pythonw.exe:
            # warnings get lost
            return
    text = _formatwarnmsg(msg)
    jaribu:
        file.write(text)
    except OSError:
        # the file (probably stderr) ni invalid - this warning gets lost.
        pass

eleza _formatwarnmsg_impl(msg):
    category = msg.category.__name__
    s =  f"{msg.filename}:{msg.lineno}: {category}: {msg.message}\n"

    ikiwa msg.line ni Tupu:
        jaribu:
            agiza linecache
            line = linecache.getline(msg.filename, msg.lineno)
        except Exception:
            # When a warning ni logged during Python shutdown, linecache
            # na the agiza machinery don't work anymore
            line = Tupu
            linecache = Tupu
    isipokua:
        line = msg.line
    ikiwa line:
        line = line.strip()
        s += "  %s\n" % line

    ikiwa msg.source ni sio Tupu:
        jaribu:
            agiza tracemalloc
        # Logging a warning should sio  ashiria a new exception:
        # catch Exception, sio only ImportError na RecursionError.
        except Exception:
            # don't suggest to enable tracemalloc ikiwa it's sio available
            tracing = Kweli
            tb = Tupu
        isipokua:
            tracing = tracemalloc.is_tracing()
            jaribu:
                tb = tracemalloc.get_object_traceback(msg.source)
            except Exception:
                # When a warning ni logged during Python shutdown, tracemalloc
                # na the agiza machinery don't work anymore
                tb = Tupu

        ikiwa tb ni sio Tupu:
            s += 'Object allocated at (most recent call last):\n'
            kila frame kwenye tb:
                s += ('  File "%s", lineno %s\n'
                      % (frame.filename, frame.lineno))

                jaribu:
                    ikiwa linecache ni sio Tupu:
                        line = linecache.getline(frame.filename, frame.lineno)
                    isipokua:
                        line = Tupu
                except Exception:
                    line = Tupu
                ikiwa line:
                    line = line.strip()
                    s += '    %s\n' % line
        elikiwa sio tracing:
            s += (f'{category}: Enable tracemalloc to get the object '
                  f'allocation traceback\n')
    rudisha s

# Keep a reference to check ikiwa the function was replaced
_showwarning_orig = showwarning

eleza _showwarnmsg(msg):
    """Hook to write a warning to a file; replace ikiwa you like."""
    jaribu:
        sw = showwarning
    except NameError:
        pass
    isipokua:
        ikiwa sw ni sio _showwarning_orig:
            # warnings.showwarning() was replaced
            ikiwa sio callable(sw):
                 ashiria TypeError("warnings.showwarning() must be set to a "
                                "function ama method")

            sw(msg.message, msg.category, msg.filename, msg.lineno,
               msg.file, msg.line)
            return
    _showwarnmsg_impl(msg)

# Keep a reference to check ikiwa the function was replaced
_formatwarning_orig = formatwarning

eleza _formatwarnmsg(msg):
    """Function to format a warning the standard way."""
    jaribu:
        fw = formatwarning
    except NameError:
        pass
    isipokua:
        ikiwa fw ni sio _formatwarning_orig:
            # warnings.formatwarning() was replaced
            rudisha fw(msg.message, msg.category,
                      msg.filename, msg.lineno, msg.line)
    rudisha _formatwarnmsg_impl(msg)

eleza filterwarnings(action, message="", category=Warning, module="", lineno=0,
                   append=Uongo):
    """Insert an entry into the list of warnings filters (at the front).

    'action' -- one of "error", "ignore", "always", "default", "module",
                ama "once"
    'message' -- a regex that the warning message must match
    'category' -- a kundi that the warning must be a subkundi of
    'module' -- a regex that the module name must match
    'lineno' -- an integer line number, 0 matches all warnings
    'append' -- ikiwa true, append to the list of filters
    """
    assert action kwenye ("error", "ignore", "always", "default", "module",
                      "once"), "invalid action: %r" % (action,)
    assert isinstance(message, str), "message must be a string"
    assert isinstance(category, type), "category must be a class"
    assert issubclass(category, Warning), "category must be a Warning subclass"
    assert isinstance(module, str), "module must be a string"
    assert isinstance(lineno, int) na lineno >= 0, \
           "lineno must be an int >= 0"

    ikiwa message ama module:
        agiza re

    ikiwa message:
        message = re.compile(message, re.I)
    isipokua:
        message = Tupu
    ikiwa module:
        module = re.compile(module)
    isipokua:
        module = Tupu

    _add_filter(action, message, category, module, lineno, append=append)

eleza simplefilter(action, category=Warning, lineno=0, append=Uongo):
    """Insert a simple entry into the list of warnings filters (at the front).

    A simple filter matches all modules na messages.
    'action' -- one of "error", "ignore", "always", "default", "module",
                ama "once"
    'category' -- a kundi that the warning must be a subkundi of
    'lineno' -- an integer line number, 0 matches all warnings
    'append' -- ikiwa true, append to the list of filters
    """
    assert action kwenye ("error", "ignore", "always", "default", "module",
                      "once"), "invalid action: %r" % (action,)
    assert isinstance(lineno, int) na lineno >= 0, \
           "lineno must be an int >= 0"
    _add_filter(action, Tupu, category, Tupu, lineno, append=append)

eleza _add_filter(*item, append):
    # Remove possible duplicate filters, so new one will be placed
    # kwenye correct place. If append=Kweli na duplicate exists, do nothing.
    ikiwa sio append:
        jaribu:
            filters.remove(item)
        except ValueError:
            pass
        filters.insert(0, item)
    isipokua:
        ikiwa item sio kwenye filters:
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
    kila arg kwenye args:
        jaribu:
            _setoption(arg)
        except _OptionError as msg:
            andika("Invalid -W option ignored:", msg, file=sys.stderr)

# Helper kila _processoptions()
eleza _setoption(arg):
    agiza re
    parts = arg.split(':')
    ikiwa len(parts) > 5:
         ashiria _OptionError("too many fields (max 5): %r" % (arg,))
    wakati len(parts) < 5:
        parts.append('')
    action, message, category, module, lineno = [s.strip()
                                                 kila s kwenye parts]
    action = _getaction(action)
    message = re.escape(message)
    category = _getcategory(category)
    module = re.escape(module)
    ikiwa module:
        module = module + '$'
    ikiwa lineno:
        jaribu:
            lineno = int(lineno)
            ikiwa lineno < 0:
                 ashiria ValueError
        except (ValueError, OverflowError):
             ashiria _OptionError("invalid lineno %r" % (lineno,)) kutoka Tupu
    isipokua:
        lineno = 0
    filterwarnings(action, message, category, module, lineno)

# Helper kila _setoption()
eleza _getaction(action):
    ikiwa sio action:
        rudisha "default"
    ikiwa action == "all": rudisha "always" # Alias
    kila a kwenye ('default', 'always', 'ignore', 'module', 'once', 'error'):
        ikiwa a.startswith(action):
            rudisha a
     ashiria _OptionError("invalid action: %r" % (action,))

# Helper kila _setoption()
eleza _getcategory(category):
    agiza re
    ikiwa sio category:
        rudisha Warning
    ikiwa re.match("^[a-zA-Z0-9_]+$", category):
        jaribu:
            cat = eval(category)
        except NameError:
             ashiria _OptionError("unknown warning category: %r" % (category,)) kutoka Tupu
    isipokua:
        i = category.rfind(".")
        module = category[:i]
        klass = category[i+1:]
        jaribu:
            m = __import__(module, Tupu, Tupu, [klass])
        except ImportError:
             ashiria _OptionError("invalid module name: %r" % (module,)) kutoka Tupu
        jaribu:
            cat = getattr(m, klass)
        except AttributeError:
             ashiria _OptionError("unknown warning category: %r" % (category,)) kutoka Tupu
    ikiwa sio issubclass(cat, Warning):
         ashiria _OptionError("invalid warning category: %r" % (category,))
    rudisha cat


eleza _is_internal_frame(frame):
    """Signal whether the frame ni an internal CPython implementation detail."""
    filename = frame.f_code.co_filename
    rudisha 'importlib' kwenye filename na '_bootstrap' kwenye filename


eleza _next_external_frame(frame):
    """Find the next frame that doesn't involve CPython internals."""
    frame = frame.f_back
    wakati frame ni sio Tupu na _is_internal_frame(frame):
        frame = frame.f_back
    rudisha frame


# Code typically replaced by _warnings
eleza warn(message, category=Tupu, stacklevel=1, source=Tupu):
    """Issue a warning, ama maybe ignore it ama  ashiria an exception."""
    # Check ikiwa message ni already a Warning object
    ikiwa isinstance(message, Warning):
        category = message.__class__
    # Check category argument
    ikiwa category ni Tupu:
        category = UserWarning
    ikiwa sio (isinstance(category, type) na issubclass(category, Warning)):
         ashiria TypeError("category must be a Warning subclass, "
                        "not '{:s}'".format(type(category).__name__))
    # Get context information
    jaribu:
        ikiwa stacklevel <= 1 ama _is_internal_frame(sys._getframe(1)):
            # If frame ni too small to care ama ikiwa the warning originated in
            # internal code, then do sio try to hide any frames.
            frame = sys._getframe(stacklevel)
        isipokua:
            frame = sys._getframe(1)
            # Look kila one frame less since the above line starts us off.
            kila x kwenye range(stacklevel-1):
                frame = _next_external_frame(frame)
                ikiwa frame ni Tupu:
                     ashiria ValueError
    except ValueError:
        globals = sys.__dict__
        filename = "sys"
        lineno = 1
    isipokua:
        globals = frame.f_globals
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
    ikiwa '__name__' kwenye globals:
        module = globals['__name__']
    isipokua:
        module = "<string>"
    registry = globals.setdefault("__warningregistry__", {})
    warn_explicit(message, category, filename, lineno, module, registry,
                  globals, source)

eleza warn_explicit(message, category, filename, lineno,
                  module=Tupu, registry=Tupu, module_globals=Tupu,
                  source=Tupu):
    lineno = int(lineno)
    ikiwa module ni Tupu:
        module = filename ama "<unknown>"
        ikiwa module[-3:].lower() == ".py":
            module = module[:-3] # XXX What about leading pathname?
    ikiwa registry ni Tupu:
        registry = {}
    ikiwa registry.get('version', 0) != _filters_version:
        registry.clear()
        registry['version'] = _filters_version
    ikiwa isinstance(message, Warning):
        text = str(message)
        category = message.__class__
    isipokua:
        text = message
        message = category(message)
    key = (text, category, lineno)
    # Quick test kila common case
    ikiwa registry.get(key):
        return
    # Search the filters
    kila item kwenye filters:
        action, msg, cat, mod, ln = item
        ikiwa ((msg ni Tupu ama msg.match(text)) and
            issubclass(category, cat) and
            (mod ni Tupu ama mod.match(module)) and
            (ln == 0 ama lineno == ln)):
            koma
    isipokua:
        action = defaultaction
    # Early exit actions
    ikiwa action == "ignore":
        return

    # Prime the linecache kila formatting, kwenye case the
    # "file" ni actually kwenye a zipfile ama something.
    agiza linecache
    linecache.getlines(filename, module_globals)

    ikiwa action == "error":
         ashiria message
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
    isipokua:
        # Unrecognized actions are errors
         ashiria RuntimeError(
              "Unrecognized action (%r) kwenye warnings.filters:\n %s" %
              (action, item))
    # Print message na context
    msg = WarningMessage(message, category, filename, lineno, source)
    _showwarnmsg(msg)


kundi WarningMessage(object):

    _WARNING_DETAILS = ("message", "category", "filename", "lineno", "file",
                        "line", "source")

    eleza __init__(self, message, category, filename, lineno, file=Tupu,
                 line=Tupu, source=Tupu):
        self.message = message
        self.category = category
        self.filename = filename
        self.lineno = lineno
        self.file = file
        self.line = line
        self.source = source
        self._category_name = category.__name__ ikiwa category isipokua Tupu

    eleza __str__(self):
        rudisha ("{message : %r, category : %r, filename : %r, lineno : %s, "
                    "line : %r}" % (self.message, self._category_name,
                                    self.filename, self.lineno, self.line))


kundi catch_warnings(object):

    """A context manager that copies na restores the warnings filter upon
    exiting the context.

    The 'record' argument specifies whether warnings should be captured by a
    custom implementation of warnings.showwarning() na be appended to a list
    returned by the context manager. Otherwise Tupu ni returned by the context
    manager. The objects appended to the list are arguments whose attributes
    mirror the arguments to showwarning().

    The 'module' argument ni to specify an alternative module to the module
    named 'warnings' na imported under that name. This argument ni only useful
    when testing the warnings module itself.

    """

    eleza __init__(self, *, record=Uongo, module=Tupu):
        """Specify whether to record warnings na ikiwa an alternative module
        should be used other than sys.modules['warnings'].

        For compatibility ukijumuisha Python 3.0, please consider all arguments to be
        keyword-only.

        """
        self._record = record
        self._module = sys.modules['warnings'] ikiwa module ni Tupu isipokua module
        self._entered = Uongo

    eleza __repr__(self):
        args = []
        ikiwa self._record:
            args.append("record=Kweli")
        ikiwa self._module ni sio sys.modules['warnings']:
            args.append("module=%r" % self._module)
        name = type(self).__name__
        rudisha "%s(%s)" % (name, ", ".join(args))

    eleza __enter__(self):
        ikiwa self._entered:
             ashiria RuntimeError("Cannot enter %r twice" % self)
        self._entered = Kweli
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
        isipokua:
            rudisha Tupu

    eleza __exit__(self, *exc_info):
        ikiwa sio self._entered:
             ashiria RuntimeError("Cannot exit %r without entering first" % self)
        self._module.filters = self._filters
        self._module._filters_mutated()
        self._module.showwarning = self._showwarning
        self._module._showwarnmsg_impl = self._showwarnmsg_impl


# Private utility function called by _PyErr_WarnUnawaitedCoroutine
eleza _warn_unawaited_coroutine(coro):
    msg_lines = [
        f"coroutine '{coro.__qualname__}' was never awaited\n"
    ]
    ikiwa coro.cr_origin ni sio Tupu:
        agiza linecache, traceback
        eleza extract():
            kila filename, lineno, funcname kwenye reversed(coro.cr_origin):
                line = linecache.getline(filename, lineno)
                tuma (filename, lineno, funcname, line)
        msg_lines.append("Coroutine created at (most recent call last)\n")
        msg_lines += traceback.format_list(list(extract()))
    msg = "".join(msg_lines).rstrip("\n")
    # Passing source= here means that ikiwa the user happens to have tracemalloc
    # enabled na tracking where the coroutine was created, the warning will
    # contain that traceback. This does mean that ikiwa they have *both*
    # coroutine origin tracking *and* tracemalloc enabled, they'll get two
    # partially-redundant tracebacks. If we wanted to be clever we could
    # probably detect this case na avoid it, but kila now we don't bother.
    warn(msg, category=RuntimeWarning, stacklevel=2, source=coro)


# filters contains a sequence of filter 5-tuples
# The components of the 5-tuple are:
# - an action: error, ignore, always, default, module, ama once
# - a compiled regex that must match the warning message
# - a kundi representing the warning category
# - a compiled regex that must match the module that ni being warned
# - a line number kila the line being warning, ama 0 to mean any line
# If either ikiwa the compiled regexs are Tupu, match anything.
jaribu:
    kutoka _warnings agiza (filters, _defaultaction, _onceregistry,
                           warn, warn_explicit, _filters_mutated)
    defaultaction = _defaultaction
    onceregistry = _onceregistry
    _warnings_defaults = Kweli
except ImportError:
    filters = []
    defaultaction = "default"
    onceregistry = {}

    _filters_version = 1

    eleza _filters_mutated():
        global _filters_version
        _filters_version += 1

    _warnings_defaults = Uongo


# Module initialization
_processoptions(sys.warnoptions)
ikiwa sio _warnings_defaults:
    # Several warning categories are ignored by default kwenye regular builds
    ikiwa sio hasattr(sys, 'gettotalrefcount'):
        filterwarnings("default", category=DeprecationWarning,
                       module="__main__", append=1)
        simplefilter("ignore", category=DeprecationWarning, append=1)
        simplefilter("ignore", category=PendingDeprecationWarning, append=1)
        simplefilter("ignore", category=ImportWarning, append=1)
        simplefilter("ignore", category=ResourceWarning, append=1)

toa _warnings_defaults
