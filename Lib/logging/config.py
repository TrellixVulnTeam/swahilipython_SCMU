# Copyright 2001-2019 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
Configuration functions for the logging package for Python. The core package
is based on PEP 282 and comments thereto in comp.lang.python, and influenced
by Apache's log4j system.

Copyright (C) 2001-2019 Vinay Sajip. All Rights Reserved.

To use, simply 'agiza logging' and log away!
"""

agiza errno
agiza io
agiza logging
agiza logging.handlers
agiza re
agiza struct
agiza sys
agiza threading
agiza traceback

kutoka socketserver agiza ThreadingTCPServer, StreamRequestHandler


DEFAULT_LOGGING_CONFIG_PORT = 9030

RESET_ERROR = errno.ECONNRESET

#
#   The following code implements a socket listener for on-the-fly
#   reconfiguration of logging.
#
#   _listener holds the server object doing the listening
_listener = None

eleza fileConfig(fname, defaults=None, disable_existing_loggers=True):
    """
    Read the logging configuration kutoka a ConfigParser-format file.

    This can be called several times kutoka an application, allowing an end user
    the ability to select kutoka various pre-canned configurations (ikiwa the
    developer provides a mechanism to present the choices and load the chosen
    configuration).
    """
    agiza configparser

    ikiwa isinstance(fname, configparser.RawConfigParser):
        cp = fname
    else:
        cp = configparser.ConfigParser(defaults)
        ikiwa hasattr(fname, 'readline'):
            cp.read_file(fname)
        else:
            cp.read(fname)

    formatters = _create_formatters(cp)

    # critical section
    logging._acquireLock()
    try:
        _clearExistingHandlers()

        # Handlers add themselves to logging._handlers
        handlers = _install_handlers(cp, formatters)
        _install_loggers(cp, handlers, disable_existing_loggers)
    finally:
        logging._releaseLock()


eleza _resolve(name):
    """Resolve a dotted name to a global object."""
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)
    rudisha found

eleza _strip_spaces(alist):
    rudisha map(str.strip, alist)

eleza _create_formatters(cp):
    """Create and rudisha formatters"""
    flist = cp["formatters"]["keys"]
    ikiwa not len(flist):
        rudisha {}
    flist = flist.split(",")
    flist = _strip_spaces(flist)
    formatters = {}
    for form in flist:
        sectname = "formatter_%s" % form
        fs = cp.get(sectname, "format", raw=True, fallback=None)
        dfs = cp.get(sectname, "datefmt", raw=True, fallback=None)
        stl = cp.get(sectname, "style", raw=True, fallback='%')
        c = logging.Formatter
        class_name = cp[sectname].get("class")
        ikiwa class_name:
            c = _resolve(class_name)
        f = c(fs, dfs, stl)
        formatters[form] = f
    rudisha formatters


eleza _install_handlers(cp, formatters):
    """Install and rudisha handlers"""
    hlist = cp["handlers"]["keys"]
    ikiwa not len(hlist):
        rudisha {}
    hlist = hlist.split(",")
    hlist = _strip_spaces(hlist)
    handlers = {}
    fixups = [] #for inter-handler references
    for hand in hlist:
        section = cp["handler_%s" % hand]
        klass = section["class"]
        fmt = section.get("formatter", "")
        try:
            klass = eval(klass, vars(logging))
        except (AttributeError, NameError):
            klass = _resolve(klass)
        args = section.get("args", '()')
        args = eval(args, vars(logging))
        kwargs = section.get("kwargs", '{}')
        kwargs = eval(kwargs, vars(logging))
        h = klass(*args, **kwargs)
        ikiwa "level" in section:
            level = section["level"]
            h.setLevel(level)
        ikiwa len(fmt):
            h.setFormatter(formatters[fmt])
        ikiwa issubclass(klass, logging.handlers.MemoryHandler):
            target = section.get("target", "")
            ikiwa len(target): #the target handler may not be loaded yet, so keep for later...
                fixups.append((h, target))
        handlers[hand] = h
    #now all handlers are loaded, fixup inter-handler references...
    for h, t in fixups:
        h.setTarget(handlers[t])
    rudisha handlers

eleza _handle_existing_loggers(existing, child_loggers, disable_existing):
    """
    When (re)configuring logging, handle loggers which were in the previous
    configuration but are not in the new configuration. There's no point
    deleting them as other threads may continue to hold references to them;
    and by disabling them, you stop them doing any logging.

    However, don't disable children of named loggers, as that's probably not
    what was intended by the user. Also, allow existing loggers to NOT be
    disabled ikiwa disable_existing is false.
    """
    root = logging.root
    for log in existing:
        logger = root.manager.loggerDict[log]
        ikiwa log in child_loggers:
            ikiwa not isinstance(logger, logging.PlaceHolder):
                logger.setLevel(logging.NOTSET)
                logger.handlers = []
                logger.propagate = True
        else:
            logger.disabled = disable_existing

eleza _install_loggers(cp, handlers, disable_existing):
    """Create and install loggers"""

    # configure the root first
    llist = cp["loggers"]["keys"]
    llist = llist.split(",")
    llist = list(_strip_spaces(llist))
    llist.remove("root")
    section = cp["logger_root"]
    root = logging.root
    log = root
    ikiwa "level" in section:
        level = section["level"]
        log.setLevel(level)
    for h in root.handlers[:]:
        root.removeHandler(h)
    hlist = section["handlers"]
    ikiwa len(hlist):
        hlist = hlist.split(",")
        hlist = _strip_spaces(hlist)
        for hand in hlist:
            log.addHandler(handlers[hand])

    #and now the others...
    #we don't want to lose the existing loggers,
    #since other threads may have pointers to them.
    #existing is set to contain all existing loggers,
    #and as we go through the new configuration we
    #remove any which are configured. At the end,
    #what's left in existing is the set of loggers
    #which were in the previous configuration but
    #which are not in the new configuration.
    existing = list(root.manager.loggerDict.keys())
    #The list needs to be sorted so that we can
    #avoid disabling child loggers of explicitly
    #named loggers. With a sorted list it is easier
    #to find the child loggers.
    existing.sort()
    #We'll keep the list of existing loggers
    #which are children of named loggers here...
    child_loggers = []
    #now set up the new ones...
    for log in llist:
        section = cp["logger_%s" % log]
        qn = section["qualname"]
        propagate = section.getint("propagate", fallback=1)
        logger = logging.getLogger(qn)
        ikiwa qn in existing:
            i = existing.index(qn) + 1 # start with the entry after qn
            prefixed = qn + "."
            pflen = len(prefixed)
            num_existing = len(existing)
            while i < num_existing:
                ikiwa existing[i][:pflen] == prefixed:
                    child_loggers.append(existing[i])
                i += 1
            existing.remove(qn)
        ikiwa "level" in section:
            level = section["level"]
            logger.setLevel(level)
        for h in logger.handlers[:]:
            logger.removeHandler(h)
        logger.propagate = propagate
        logger.disabled = 0
        hlist = section["handlers"]
        ikiwa len(hlist):
            hlist = hlist.split(",")
            hlist = _strip_spaces(hlist)
            for hand in hlist:
                logger.addHandler(handlers[hand])

    #Disable any old loggers. There's no point deleting
    #them as other threads may continue to hold references
    #and by disabling them, you stop them doing any logging.
    #However, don't disable children of named loggers, as that's
    #probably not what was intended by the user.
    #for log in existing:
    #    logger = root.manager.loggerDict[log]
    #    ikiwa log in child_loggers:
    #        logger.level = logging.NOTSET
    #        logger.handlers = []
    #        logger.propagate = 1
    #    elikiwa disable_existing_loggers:
    #        logger.disabled = 1
    _handle_existing_loggers(existing, child_loggers, disable_existing)


eleza _clearExistingHandlers():
    """Clear and close existing handlers"""
    logging._handlers.clear()
    logging.shutdown(logging._handlerList[:])
    del logging._handlerList[:]


IDENTIFIER = re.compile('^[a-z_][a-z0-9_]*$', re.I)


eleza valid_ident(s):
    m = IDENTIFIER.match(s)
    ikiwa not m:
        raise ValueError('Not a valid Python identifier: %r' % s)
    rudisha True


kundi ConvertingMixin(object):
    """For ConvertingXXX's, this mixin kundi provides common functions"""

    eleza convert_with_key(self, key, value, replace=True):
        result = self.configurator.convert(value)
        #If the converted value is different, save for next time
        ikiwa value is not result:
            ikiwa replace:
                self[key] = result
            ikiwa type(result) in (ConvertingDict, ConvertingList,
                               ConvertingTuple):
                result.parent = self
                result.key = key
        rudisha result

    eleza convert(self, value):
        result = self.configurator.convert(value)
        ikiwa value is not result:
            ikiwa type(result) in (ConvertingDict, ConvertingList,
                               ConvertingTuple):
                result.parent = self
        rudisha result


# The ConvertingXXX classes are wrappers around standard Python containers,
# and they serve to convert any suitable values in the container. The
# conversion converts base dicts, lists and tuples to their wrapped
# equivalents, whereas strings which match a conversion format are converted
# appropriately.
#
# Each wrapper should have a configurator attribute holding the actual
# configurator to use for conversion.

kundi ConvertingDict(dict, ConvertingMixin):
    """A converting dictionary wrapper."""

    eleza __getitem__(self, key):
        value = dict.__getitem__(self, key)
        rudisha self.convert_with_key(key, value)

    eleza get(self, key, default=None):
        value = dict.get(self, key, default)
        rudisha self.convert_with_key(key, value)

    eleza pop(self, key, default=None):
        value = dict.pop(self, key, default)
        rudisha self.convert_with_key(key, value, replace=False)

kundi ConvertingList(list, ConvertingMixin):
    """A converting list wrapper."""
    eleza __getitem__(self, key):
        value = list.__getitem__(self, key)
        rudisha self.convert_with_key(key, value)

    eleza pop(self, idx=-1):
        value = list.pop(self, idx)
        rudisha self.convert(value)

kundi ConvertingTuple(tuple, ConvertingMixin):
    """A converting tuple wrapper."""
    eleza __getitem__(self, key):
        value = tuple.__getitem__(self, key)
        # Can't replace a tuple entry.
        rudisha self.convert_with_key(key, value, replace=False)

kundi BaseConfigurator(object):
    """
    The configurator base kundi which defines some useful defaults.
    """

    CONVERT_PATTERN = re.compile(r'^(?P<prefix>[a-z]+)://(?P<suffix>.*)$')

    WORD_PATTERN = re.compile(r'^\s*(\w+)\s*')
    DOT_PATTERN = re.compile(r'^\.\s*(\w+)\s*')
    INDEX_PATTERN = re.compile(r'^\[\s*(\w+)\s*\]\s*')
    DIGIT_PATTERN = re.compile(r'^\d+$')

    value_converters = {
        'ext' : 'ext_convert',
        'cfg' : 'cfg_convert',
    }

    # We might want to use a different one, e.g. importlib
    importer = staticmethod(__import__)

    eleza __init__(self, config):
        self.config = ConvertingDict(config)
        self.config.configurator = self

    eleza resolve(self, s):
        """
        Resolve strings to objects using standard agiza and attribute
        syntax.
        """
        name = s.split('.')
        used = name.pop(0)
        try:
            found = self.importer(used)
            for frag in name:
                used += '.' + frag
                try:
                    found = getattr(found, frag)
                except AttributeError:
                    self.importer(used)
                    found = getattr(found, frag)
            rudisha found
        except ImportError:
            e, tb = sys.exc_info()[1:]
            v = ValueError('Cannot resolve %r: %s' % (s, e))
            v.__cause__, v.__traceback__ = e, tb
            raise v

    eleza ext_convert(self, value):
        """Default converter for the ext:// protocol."""
        rudisha self.resolve(value)

    eleza cfg_convert(self, value):
        """Default converter for the cfg:// protocol."""
        rest = value
        m = self.WORD_PATTERN.match(rest)
        ikiwa m is None:
            raise ValueError("Unable to convert %r" % value)
        else:
            rest = rest[m.end():]
            d = self.config[m.groups()[0]]
            #print d, rest
            while rest:
                m = self.DOT_PATTERN.match(rest)
                ikiwa m:
                    d = d[m.groups()[0]]
                else:
                    m = self.INDEX_PATTERN.match(rest)
                    ikiwa m:
                        idx = m.groups()[0]
                        ikiwa not self.DIGIT_PATTERN.match(idx):
                            d = d[idx]
                        else:
                            try:
                                n = int(idx) # try as number first (most likely)
                                d = d[n]
                            except TypeError:
                                d = d[idx]
                ikiwa m:
                    rest = rest[m.end():]
                else:
                    raise ValueError('Unable to convert '
                                     '%r at %r' % (value, rest))
        #rest should be empty
        rudisha d

    eleza convert(self, value):
        """
        Convert values to an appropriate type. dicts, lists and tuples are
        replaced by their converting alternatives. Strings are checked to
        see ikiwa they have a conversion format and are converted ikiwa they do.
        """
        ikiwa not isinstance(value, ConvertingDict) and isinstance(value, dict):
            value = ConvertingDict(value)
            value.configurator = self
        elikiwa not isinstance(value, ConvertingList) and isinstance(value, list):
            value = ConvertingList(value)
            value.configurator = self
        elikiwa not isinstance(value, ConvertingTuple) and\
                 isinstance(value, tuple):
            value = ConvertingTuple(value)
            value.configurator = self
        elikiwa isinstance(value, str): # str for py3k
            m = self.CONVERT_PATTERN.match(value)
            ikiwa m:
                d = m.groupdict()
                prefix = d['prefix']
                converter = self.value_converters.get(prefix, None)
                ikiwa converter:
                    suffix = d['suffix']
                    converter = getattr(self, converter)
                    value = converter(suffix)
        rudisha value

    eleza configure_custom(self, config):
        """Configure an object with a user-supplied factory."""
        c = config.pop('()')
        ikiwa not callable(c):
            c = self.resolve(c)
        props = config.pop('.', None)
        # Check for valid identifiers
        kwargs = {k: config[k] for k in config ikiwa valid_ident(k)}
        result = c(**kwargs)
        ikiwa props:
            for name, value in props.items():
                setattr(result, name, value)
        rudisha result

    eleza as_tuple(self, value):
        """Utility function which converts lists to tuples."""
        ikiwa isinstance(value, list):
            value = tuple(value)
        rudisha value

kundi DictConfigurator(BaseConfigurator):
    """
    Configure logging using a dictionary-like object to describe the
    configuration.
    """

    eleza configure(self):
        """Do the configuration."""

        config = self.config
        ikiwa 'version' not in config:
            raise ValueError("dictionary doesn't specify a version")
        ikiwa config['version'] != 1:
            raise ValueError("Unsupported version: %s" % config['version'])
        incremental = config.pop('incremental', False)
        EMPTY_DICT = {}
        logging._acquireLock()
        try:
            ikiwa incremental:
                handlers = config.get('handlers', EMPTY_DICT)
                for name in handlers:
                    ikiwa name not in logging._handlers:
                        raise ValueError('No handler found with '
                                         'name %r'  % name)
                    else:
                        try:
                            handler = logging._handlers[name]
                            handler_config = handlers[name]
                            level = handler_config.get('level', None)
                            ikiwa level:
                                handler.setLevel(logging._checkLevel(level))
                        except Exception as e:
                            raise ValueError('Unable to configure handler '
                                             '%r' % name) kutoka e
                loggers = config.get('loggers', EMPTY_DICT)
                for name in loggers:
                    try:
                        self.configure_logger(name, loggers[name], True)
                    except Exception as e:
                        raise ValueError('Unable to configure logger '
                                         '%r' % name) kutoka e
                root = config.get('root', None)
                ikiwa root:
                    try:
                        self.configure_root(root, True)
                    except Exception as e:
                        raise ValueError('Unable to configure root '
                                         'logger') kutoka e
            else:
                disable_existing = config.pop('disable_existing_loggers', True)

                _clearExistingHandlers()

                # Do formatters first - they don't refer to anything else
                formatters = config.get('formatters', EMPTY_DICT)
                for name in formatters:
                    try:
                        formatters[name] = self.configure_formatter(
                                                            formatters[name])
                    except Exception as e:
                        raise ValueError('Unable to configure '
                                         'formatter %r' % name) kutoka e
                # Next, do filters - they don't refer to anything else, either
                filters = config.get('filters', EMPTY_DICT)
                for name in filters:
                    try:
                        filters[name] = self.configure_filter(filters[name])
                    except Exception as e:
                        raise ValueError('Unable to configure '
                                         'filter %r' % name) kutoka e

                # Next, do handlers - they refer to formatters and filters
                # As handlers can refer to other handlers, sort the keys
                # to allow a deterministic order of configuration
                handlers = config.get('handlers', EMPTY_DICT)
                deferred = []
                for name in sorted(handlers):
                    try:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    except Exception as e:
                        ikiwa 'target not configured yet' in str(e.__cause__):
                            deferred.append(name)
                        else:
                            raise ValueError('Unable to configure handler '
                                             '%r' % name) kutoka e

                # Now do any that were deferred
                for name in deferred:
                    try:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    except Exception as e:
                        raise ValueError('Unable to configure handler '
                                         '%r' % name) kutoka e

                # Next, do loggers - they refer to handlers and filters

                #we don't want to lose the existing loggers,
                #since other threads may have pointers to them.
                #existing is set to contain all existing loggers,
                #and as we go through the new configuration we
                #remove any which are configured. At the end,
                #what's left in existing is the set of loggers
                #which were in the previous configuration but
                #which are not in the new configuration.
                root = logging.root
                existing = list(root.manager.loggerDict.keys())
                #The list needs to be sorted so that we can
                #avoid disabling child loggers of explicitly
                #named loggers. With a sorted list it is easier
                #to find the child loggers.
                existing.sort()
                #We'll keep the list of existing loggers
                #which are children of named loggers here...
                child_loggers = []
                #now set up the new ones...
                loggers = config.get('loggers', EMPTY_DICT)
                for name in loggers:
                    ikiwa name in existing:
                        i = existing.index(name) + 1 # look after name
                        prefixed = name + "."
                        pflen = len(prefixed)
                        num_existing = len(existing)
                        while i < num_existing:
                            ikiwa existing[i][:pflen] == prefixed:
                                child_loggers.append(existing[i])
                            i += 1
                        existing.remove(name)
                    try:
                        self.configure_logger(name, loggers[name])
                    except Exception as e:
                        raise ValueError('Unable to configure logger '
                                         '%r' % name) kutoka e

                #Disable any old loggers. There's no point deleting
                #them as other threads may continue to hold references
                #and by disabling them, you stop them doing any logging.
                #However, don't disable children of named loggers, as that's
                #probably not what was intended by the user.
                #for log in existing:
                #    logger = root.manager.loggerDict[log]
                #    ikiwa log in child_loggers:
                #        logger.level = logging.NOTSET
                #        logger.handlers = []
                #        logger.propagate = True
                #    elikiwa disable_existing:
                #        logger.disabled = True
                _handle_existing_loggers(existing, child_loggers,
                                         disable_existing)

                # And finally, do the root logger
                root = config.get('root', None)
                ikiwa root:
                    try:
                        self.configure_root(root)
                    except Exception as e:
                        raise ValueError('Unable to configure root '
                                         'logger') kutoka e
        finally:
            logging._releaseLock()

    eleza configure_formatter(self, config):
        """Configure a formatter kutoka a dictionary."""
        ikiwa '()' in config:
            factory = config['()'] # for use in exception handler
            try:
                result = self.configure_custom(config)
            except TypeError as te:
                ikiwa "'format'" not in str(te):
                    raise
                #Name of parameter changed kutoka fmt to format.
                #Retry with old name.
                #This is so that code can be used with older Python versions
                #(e.g. by Django)
                config['fmt'] = config.pop('format')
                config['()'] = factory
                result = self.configure_custom(config)
        else:
            fmt = config.get('format', None)
            dfmt = config.get('datefmt', None)
            style = config.get('style', '%')
            cname = config.get('class', None)

            ikiwa not cname:
                c = logging.Formatter
            else:
                c = _resolve(cname)

            # A TypeError would be raised ikiwa "validate" key is passed in with a formatter callable
            # that does not accept "validate" as a parameter
            ikiwa 'validate' in config:  # ikiwa user hasn't mentioned it, the default will be fine
                result = c(fmt, dfmt, style, config['validate'])
            else:
                result = c(fmt, dfmt, style)

        rudisha result

    eleza configure_filter(self, config):
        """Configure a filter kutoka a dictionary."""
        ikiwa '()' in config:
            result = self.configure_custom(config)
        else:
            name = config.get('name', '')
            result = logging.Filter(name)
        rudisha result

    eleza add_filters(self, filterer, filters):
        """Add filters to a filterer kutoka a list of names."""
        for f in filters:
            try:
                filterer.addFilter(self.config['filters'][f])
            except Exception as e:
                raise ValueError('Unable to add filter %r' % f) kutoka e

    eleza configure_handler(self, config):
        """Configure a handler kutoka a dictionary."""
        config_copy = dict(config)  # for restoring in case of error
        formatter = config.pop('formatter', None)
        ikiwa formatter:
            try:
                formatter = self.config['formatters'][formatter]
            except Exception as e:
                raise ValueError('Unable to set formatter '
                                 '%r' % formatter) kutoka e
        level = config.pop('level', None)
        filters = config.pop('filters', None)
        ikiwa '()' in config:
            c = config.pop('()')
            ikiwa not callable(c):
                c = self.resolve(c)
            factory = c
        else:
            cname = config.pop('class')
            klass = self.resolve(cname)
            #Special case for handler which refers to another handler
            ikiwa issubclass(klass, logging.handlers.MemoryHandler) and\
                'target' in config:
                try:
                    th = self.config['handlers'][config['target']]
                    ikiwa not isinstance(th, logging.Handler):
                        config.update(config_copy)  # restore for deferred cfg
                        raise TypeError('target not configured yet')
                    config['target'] = th
                except Exception as e:
                    raise ValueError('Unable to set target handler '
                                     '%r' % config['target']) kutoka e
            elikiwa issubclass(klass, logging.handlers.SMTPHandler) and\
                'mailhost' in config:
                config['mailhost'] = self.as_tuple(config['mailhost'])
            elikiwa issubclass(klass, logging.handlers.SysLogHandler) and\
                'address' in config:
                config['address'] = self.as_tuple(config['address'])
            factory = klass
        props = config.pop('.', None)
        kwargs = {k: config[k] for k in config ikiwa valid_ident(k)}
        try:
            result = factory(**kwargs)
        except TypeError as te:
            ikiwa "'stream'" not in str(te):
                raise
            #The argument name changed kutoka strm to stream
            #Retry with old name.
            #This is so that code can be used with older Python versions
            #(e.g. by Django)
            kwargs['strm'] = kwargs.pop('stream')
            result = factory(**kwargs)
        ikiwa formatter:
            result.setFormatter(formatter)
        ikiwa level is not None:
            result.setLevel(logging._checkLevel(level))
        ikiwa filters:
            self.add_filters(result, filters)
        ikiwa props:
            for name, value in props.items():
                setattr(result, name, value)
        rudisha result

    eleza add_handlers(self, logger, handlers):
        """Add handlers to a logger kutoka a list of names."""
        for h in handlers:
            try:
                logger.addHandler(self.config['handlers'][h])
            except Exception as e:
                raise ValueError('Unable to add handler %r' % h) kutoka e

    eleza common_logger_config(self, logger, config, incremental=False):
        """
        Perform configuration which is common to root and non-root loggers.
        """
        level = config.get('level', None)
        ikiwa level is not None:
            logger.setLevel(logging._checkLevel(level))
        ikiwa not incremental:
            #Remove any existing handlers
            for h in logger.handlers[:]:
                logger.removeHandler(h)
            handlers = config.get('handlers', None)
            ikiwa handlers:
                self.add_handlers(logger, handlers)
            filters = config.get('filters', None)
            ikiwa filters:
                self.add_filters(logger, filters)

    eleza configure_logger(self, name, config, incremental=False):
        """Configure a non-root logger kutoka a dictionary."""
        logger = logging.getLogger(name)
        self.common_logger_config(logger, config, incremental)
        propagate = config.get('propagate', None)
        ikiwa propagate is not None:
            logger.propagate = propagate

    eleza configure_root(self, config, incremental=False):
        """Configure a root logger kutoka a dictionary."""
        root = logging.getLogger()
        self.common_logger_config(root, config, incremental)

dictConfigClass = DictConfigurator

eleza dictConfig(config):
    """Configure logging using a dictionary."""
    dictConfigClass(config).configure()


eleza listen(port=DEFAULT_LOGGING_CONFIG_PORT, verify=None):
    """
    Start up a socket server on the specified port, and listen for new
    configurations.

    These will be sent as a file suitable for processing by fileConfig().
    Returns a Thread object on which you can call start() to start the server,
    and which you can join() when appropriate. To stop the server, call
    stopListening().

    Use the ``verify`` argument to verify any bytes received across the wire
    kutoka a client. If specified, it should be a callable which receives a
    single argument - the bytes of configuration data received across the
    network - and it should rudisha either ``None``, to indicate that the
    passed in bytes could not be verified and should be discarded, or a
    byte string which is then passed to the configuration machinery as
    normal. Note that you can rudisha transformed bytes, e.g. by decrypting
    the bytes passed in.
    """

    kundi ConfigStreamHandler(StreamRequestHandler):
        """
        Handler for a logging configuration request.

        It expects a completely new logging configuration and uses fileConfig
        to install it.
        """
        eleza handle(self):
            """
            Handle a request.

            Each request is expected to be a 4-byte length, packed using
            struct.pack(">L", n), followed by the config file.
            Uses fileConfig() to do the grunt work.
            """
            try:
                conn = self.connection
                chunk = conn.recv(4)
                ikiwa len(chunk) == 4:
                    slen = struct.unpack(">L", chunk)[0]
                    chunk = self.connection.recv(slen)
                    while len(chunk) < slen:
                        chunk = chunk + conn.recv(slen - len(chunk))
                    ikiwa self.server.verify is not None:
                        chunk = self.server.verify(chunk)
                    ikiwa chunk is not None:   # verified, can process
                        chunk = chunk.decode("utf-8")
                        try:
                            agiza json
                            d =json.loads(chunk)
                            assert isinstance(d, dict)
                            dictConfig(d)
                        except Exception:
                            #Apply new configuration.

                            file = io.StringIO(chunk)
                            try:
                                fileConfig(file)
                            except Exception:
                                traceback.print_exc()
                    ikiwa self.server.ready:
                        self.server.ready.set()
            except OSError as e:
                ikiwa e.errno != RESET_ERROR:
                    raise

    kundi ConfigSocketReceiver(ThreadingTCPServer):
        """
        A simple TCP socket-based logging config receiver.
        """

        allow_reuse_address = 1

        eleza __init__(self, host='localhost', port=DEFAULT_LOGGING_CONFIG_PORT,
                     handler=None, ready=None, verify=None):
            ThreadingTCPServer.__init__(self, (host, port), handler)
            logging._acquireLock()
            self.abort = 0
            logging._releaseLock()
            self.timeout = 1
            self.ready = ready
            self.verify = verify

        eleza serve_until_stopped(self):
            agiza select
            abort = 0
            while not abort:
                rd, wr, ex = select.select([self.socket.fileno()],
                                           [], [],
                                           self.timeout)
                ikiwa rd:
                    self.handle_request()
                logging._acquireLock()
                abort = self.abort
                logging._releaseLock()
            self.server_close()

    kundi Server(threading.Thread):

        eleza __init__(self, rcvr, hdlr, port, verify):
            super(Server, self).__init__()
            self.rcvr = rcvr
            self.hdlr = hdlr
            self.port = port
            self.verify = verify
            self.ready = threading.Event()

        eleza run(self):
            server = self.rcvr(port=self.port, handler=self.hdlr,
                               ready=self.ready,
                               verify=self.verify)
            ikiwa self.port == 0:
                self.port = server.server_address[1]
            self.ready.set()
            global _listener
            logging._acquireLock()
            _listener = server
            logging._releaseLock()
            server.serve_until_stopped()

    rudisha Server(ConfigSocketReceiver, ConfigStreamHandler, port, verify)

eleza stopListening():
    """
    Stop the listening server which was created with a call to listen().
    """
    global _listener
    logging._acquireLock()
    try:
        ikiwa _listener:
            _listener.abort = 1
            _listener = None
    finally:
        logging._releaseLock()
