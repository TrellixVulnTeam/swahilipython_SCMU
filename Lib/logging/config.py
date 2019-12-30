# Copyright 2001-2019 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, na distribute this software na its
# documentation kila any purpose na without fee ni hereby granted,
# provided that the above copyright notice appear kwenye all copies na that
# both that copyright notice na this permission notice appear in
# supporting documentation, na that the name of Vinay Sajip
# sio be used kwenye advertising ama publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
Configuration functions kila the logging package kila Python. The core package
is based on PEP 282 na comments thereto kwenye comp.lang.python, na influenced
by Apache's log4j system.

Copyright (C) 2001-2019 Vinay Sajip. All Rights Reserved.

To use, simply 'agiza logging' na log away!
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
#   The following code implements a socket listener kila on-the-fly
#   reconfiguration of logging.
#
#   _listener holds the server object doing the listening
_listener = Tupu

eleza fileConfig(fname, defaults=Tupu, disable_existing_loggers=Kweli):
    """
    Read the logging configuration kutoka a ConfigParser-format file.

    This can be called several times kutoka an application, allowing an end user
    the ability to select kutoka various pre-canned configurations (ikiwa the
    developer provides a mechanism to present the choices na load the chosen
    configuration).
    """
    agiza configparser

    ikiwa isinstance(fname, configparser.RawConfigParser):
        cp = fname
    isipokua:
        cp = configparser.ConfigParser(defaults)
        ikiwa hasattr(fname, 'readline'):
            cp.read_file(fname)
        isipokua:
            cp.read(fname)

    formatters = _create_formatters(cp)

    # critical section
    logging._acquireLock()
    jaribu:
        _clearExistingHandlers()

        # Handlers add themselves to logging._handlers
        handlers = _install_handlers(cp, formatters)
        _install_loggers(cp, handlers, disable_existing_loggers)
    mwishowe:
        logging._releaseLock()


eleza _resolve(name):
    """Resolve a dotted name to a global object."""
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    kila n kwenye name:
        used = used + '.' + n
        jaribu:
            found = getattr(found, n)
        tatizo AttributeError:
            __import__(used)
            found = getattr(found, n)
    rudisha found

eleza _strip_spaces(alist):
    rudisha map(str.strip, alist)

eleza _create_formatters(cp):
    """Create na rudisha formatters"""
    flist = cp["formatters"]["keys"]
    ikiwa sio len(flist):
        rudisha {}
    flist = flist.split(",")
    flist = _strip_spaces(flist)
    formatters = {}
    kila form kwenye flist:
        sectname = "formatter_%s" % form
        fs = cp.get(sectname, "format", raw=Kweli, fallback=Tupu)
        dfs = cp.get(sectname, "datefmt", raw=Kweli, fallback=Tupu)
        stl = cp.get(sectname, "style", raw=Kweli, fallback='%')
        c = logging.Formatter
        class_name = cp[sectname].get("class")
        ikiwa class_name:
            c = _resolve(class_name)
        f = c(fs, dfs, stl)
        formatters[form] = f
    rudisha formatters


eleza _install_handlers(cp, formatters):
    """Install na rudisha handlers"""
    hlist = cp["handlers"]["keys"]
    ikiwa sio len(hlist):
        rudisha {}
    hlist = hlist.split(",")
    hlist = _strip_spaces(hlist)
    handlers = {}
    fixups = [] #kila inter-handler references
    kila hand kwenye hlist:
        section = cp["handler_%s" % hand]
        klass = section["class"]
        fmt = section.get("formatter", "")
        jaribu:
            klass = eval(klass, vars(logging))
        tatizo (AttributeError, NameError):
            klass = _resolve(klass)
        args = section.get("args", '()')
        args = eval(args, vars(logging))
        kwargs = section.get("kwargs", '{}')
        kwargs = eval(kwargs, vars(logging))
        h = klass(*args, **kwargs)
        ikiwa "level" kwenye section:
            level = section["level"]
            h.setLevel(level)
        ikiwa len(fmt):
            h.setFormatter(formatters[fmt])
        ikiwa issubclass(klass, logging.handlers.MemoryHandler):
            target = section.get("target", "")
            ikiwa len(target): #the target handler may sio be loaded yet, so keep kila later...
                fixups.append((h, target))
        handlers[hand] = h
    #now all handlers are loaded, fixup inter-handler references...
    kila h, t kwenye fixups:
        h.setTarget(handlers[t])
    rudisha handlers

eleza _handle_existing_loggers(existing, child_loggers, disable_existing):
    """
    When (re)configuring logging, handle loggers which were kwenye the previous
    configuration but are haiko kwenye the new configuration. There's no point
    deleting them kama other threads may endelea to hold references to them;
    na by disabling them, you stop them doing any logging.

    However, don't disable children of named loggers, kama that's probably not
    what was intended by the user. Also, allow existing loggers to NOT be
    disabled ikiwa disable_existing ni false.
    """
    root = logging.root
    kila log kwenye existing:
        logger = root.manager.loggerDict[log]
        ikiwa log kwenye child_loggers:
            ikiwa sio isinstance(logger, logging.PlaceHolder):
                logger.setLevel(logging.NOTSET)
                logger.handlers = []
                logger.propagate = Kweli
        isipokua:
            logger.disabled = disable_existing

eleza _install_loggers(cp, handlers, disable_existing):
    """Create na install loggers"""

    # configure the root first
    llist = cp["loggers"]["keys"]
    llist = llist.split(",")
    llist = list(_strip_spaces(llist))
    llist.remove("root")
    section = cp["logger_root"]
    root = logging.root
    log = root
    ikiwa "level" kwenye section:
        level = section["level"]
        log.setLevel(level)
    kila h kwenye root.handlers[:]:
        root.removeHandler(h)
    hlist = section["handlers"]
    ikiwa len(hlist):
        hlist = hlist.split(",")
        hlist = _strip_spaces(hlist)
        kila hand kwenye hlist:
            log.addHandler(handlers[hand])

    #and now the others...
    #we don't want to lose the existing loggers,
    #since other threads may have pointers to them.
    #existing ni set to contain all existing loggers,
    #and kama we go through the new configuration we
    #remove any which are configured. At the end,
    #what's left kwenye existing ni the set of loggers
    #which were kwenye the previous configuration but
    #which are haiko kwenye the new configuration.
    existing = list(root.manager.loggerDict.keys())
    #The list needs to be sorted so that we can
    #avoid disabling child loggers of explicitly
    #named loggers. With a sorted list it ni easier
    #to find the child loggers.
    existing.sort()
    #We'll keep the list of existing loggers
    #which are children of named loggers here...
    child_loggers = []
    #now set up the new ones...
    kila log kwenye llist:
        section = cp["logger_%s" % log]
        qn = section["qualname"]
        propagate = section.getint("propagate", fallback=1)
        logger = logging.getLogger(qn)
        ikiwa qn kwenye existing:
            i = existing.index(qn) + 1 # start ukijumuisha the entry after qn
            prefixed = qn + "."
            pflen = len(prefixed)
            num_existing = len(existing)
            wakati i < num_existing:
                ikiwa existing[i][:pflen] == prefixed:
                    child_loggers.append(existing[i])
                i += 1
            existing.remove(qn)
        ikiwa "level" kwenye section:
            level = section["level"]
            logger.setLevel(level)
        kila h kwenye logger.handlers[:]:
            logger.removeHandler(h)
        logger.propagate = propagate
        logger.disabled = 0
        hlist = section["handlers"]
        ikiwa len(hlist):
            hlist = hlist.split(",")
            hlist = _strip_spaces(hlist)
            kila hand kwenye hlist:
                logger.addHandler(handlers[hand])

    #Disable any old loggers. There's no point deleting
    #them kama other threads may endelea to hold references
    #and by disabling them, you stop them doing any logging.
    #However, don't disable children of named loggers, kama that's
    #probably sio what was intended by the user.
    #kila log kwenye existing:
    #    logger = root.manager.loggerDict[log]
    #    ikiwa log kwenye child_loggers:
    #        logger.level = logging.NOTSET
    #        logger.handlers = []
    #        logger.propagate = 1
    #    lasivyo disable_existing_loggers:
    #        logger.disabled = 1
    _handle_existing_loggers(existing, child_loggers, disable_existing)


eleza _clearExistingHandlers():
    """Clear na close existing handlers"""
    logging._handlers.clear()
    logging.shutdown(logging._handlerList[:])
    toa logging._handlerList[:]


IDENTIFIER = re.compile('^[a-z_][a-z0-9_]*$', re.I)


eleza valid_ident(s):
    m = IDENTIFIER.match(s)
    ikiwa sio m:
        ashiria ValueError('Not a valid Python identifier: %r' % s)
    rudisha Kweli


kundi ConvertingMixin(object):
    """For ConvertingXXX's, this mixin kundi provides common functions"""

    eleza convert_with_key(self, key, value, replace=Kweli):
        result = self.configurator.convert(value)
        #If the converted value ni different, save kila next time
        ikiwa value ni sio result:
            ikiwa replace:
                self[key] = result
            ikiwa type(result) kwenye (ConvertingDict, ConvertingList,
                               ConvertingTuple):
                result.parent = self
                result.key = key
        rudisha result

    eleza convert(self, value):
        result = self.configurator.convert(value)
        ikiwa value ni sio result:
            ikiwa type(result) kwenye (ConvertingDict, ConvertingList,
                               ConvertingTuple):
                result.parent = self
        rudisha result


# The ConvertingXXX classes are wrappers around standard Python containers,
# na they serve to convert any suitable values kwenye the container. The
# conversion converts base dicts, lists na tuples to their wrapped
# equivalents, whereas strings which match a conversion format are converted
# appropriately.
#
# Each wrapper should have a configurator attribute holding the actual
# configurator to use kila conversion.

kundi ConvertingDict(dict, ConvertingMixin):
    """A converting dictionary wrapper."""

    eleza __getitem__(self, key):
        value = dict.__getitem__(self, key)
        rudisha self.convert_with_key(key, value)

    eleza get(self, key, default=Tupu):
        value = dict.get(self, key, default)
        rudisha self.convert_with_key(key, value)

    eleza pop(self, key, default=Tupu):
        value = dict.pop(self, key, default)
        rudisha self.convert_with_key(key, value, replace=Uongo)

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
        rudisha self.convert_with_key(key, value, replace=Uongo)

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
        Resolve strings to objects using standard agiza na attribute
        syntax.
        """
        name = s.split('.')
        used = name.pop(0)
        jaribu:
            found = self.importer(used)
            kila frag kwenye name:
                used += '.' + frag
                jaribu:
                    found = getattr(found, frag)
                tatizo AttributeError:
                    self.importer(used)
                    found = getattr(found, frag)
            rudisha found
        tatizo ImportError:
            e, tb = sys.exc_info()[1:]
            v = ValueError('Cannot resolve %r: %s' % (s, e))
            v.__cause__, v.__traceback__ = e, tb
            ashiria v

    eleza ext_convert(self, value):
        """Default converter kila the ext:// protocol."""
        rudisha self.resolve(value)

    eleza cfg_convert(self, value):
        """Default converter kila the cfg:// protocol."""
        rest = value
        m = self.WORD_PATTERN.match(rest)
        ikiwa m ni Tupu:
            ashiria ValueError("Unable to convert %r" % value)
        isipokua:
            rest = rest[m.end():]
            d = self.config[m.groups()[0]]
            #print d, rest
            wakati rest:
                m = self.DOT_PATTERN.match(rest)
                ikiwa m:
                    d = d[m.groups()[0]]
                isipokua:
                    m = self.INDEX_PATTERN.match(rest)
                    ikiwa m:
                        idx = m.groups()[0]
                        ikiwa sio self.DIGIT_PATTERN.match(idx):
                            d = d[idx]
                        isipokua:
                            jaribu:
                                n = int(idx) # try kama number first (most likely)
                                d = d[n]
                            tatizo TypeError:
                                d = d[idx]
                ikiwa m:
                    rest = rest[m.end():]
                isipokua:
                    ashiria ValueError('Unable to convert '
                                     '%r at %r' % (value, rest))
        #rest should be empty
        rudisha d

    eleza convert(self, value):
        """
        Convert values to an appropriate type. dicts, lists na tuples are
        replaced by their converting alternatives. Strings are checked to
        see ikiwa they have a conversion format na are converted ikiwa they do.
        """
        ikiwa sio isinstance(value, ConvertingDict) na isinstance(value, dict):
            value = ConvertingDict(value)
            value.configurator = self
        lasivyo sio isinstance(value, ConvertingList) na isinstance(value, list):
            value = ConvertingList(value)
            value.configurator = self
        lasivyo sio isinstance(value, ConvertingTuple) and\
                 isinstance(value, tuple):
            value = ConvertingTuple(value)
            value.configurator = self
        lasivyo isinstance(value, str): # str kila py3k
            m = self.CONVERT_PATTERN.match(value)
            ikiwa m:
                d = m.groupdict()
                prefix = d['prefix']
                converter = self.value_converters.get(prefix, Tupu)
                ikiwa converter:
                    suffix = d['suffix']
                    converter = getattr(self, converter)
                    value = converter(suffix)
        rudisha value

    eleza configure_custom(self, config):
        """Configure an object ukijumuisha a user-supplied factory."""
        c = config.pop('()')
        ikiwa sio callable(c):
            c = self.resolve(c)
        props = config.pop('.', Tupu)
        # Check kila valid identifiers
        kwargs = {k: config[k] kila k kwenye config ikiwa valid_ident(k)}
        result = c(**kwargs)
        ikiwa props:
            kila name, value kwenye props.items():
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
        ikiwa 'version' haiko kwenye config:
            ashiria ValueError("dictionary doesn't specify a version")
        ikiwa config['version'] != 1:
            ashiria ValueError("Unsupported version: %s" % config['version'])
        incremental = config.pop('incremental', Uongo)
        EMPTY_DICT = {}
        logging._acquireLock()
        jaribu:
            ikiwa incremental:
                handlers = config.get('handlers', EMPTY_DICT)
                kila name kwenye handlers:
                    ikiwa name haiko kwenye logging._handlers:
                        ashiria ValueError('No handler found ukijumuisha '
                                         'name %r'  % name)
                    isipokua:
                        jaribu:
                            handler = logging._handlers[name]
                            handler_config = handlers[name]
                            level = handler_config.get('level', Tupu)
                            ikiwa level:
                                handler.setLevel(logging._checkLevel(level))
                        tatizo Exception kama e:
                            ashiria ValueError('Unable to configure handler '
                                             '%r' % name) kutoka e
                loggers = config.get('loggers', EMPTY_DICT)
                kila name kwenye loggers:
                    jaribu:
                        self.configure_logger(name, loggers[name], Kweli)
                    tatizo Exception kama e:
                        ashiria ValueError('Unable to configure logger '
                                         '%r' % name) kutoka e
                root = config.get('root', Tupu)
                ikiwa root:
                    jaribu:
                        self.configure_root(root, Kweli)
                    tatizo Exception kama e:
                        ashiria ValueError('Unable to configure root '
                                         'logger') kutoka e
            isipokua:
                disable_existing = config.pop('disable_existing_loggers', Kweli)

                _clearExistingHandlers()

                # Do formatters first - they don't refer to anything isipokua
                formatters = config.get('formatters', EMPTY_DICT)
                kila name kwenye formatters:
                    jaribu:
                        formatters[name] = self.configure_formatter(
                                                            formatters[name])
                    tatizo Exception kama e:
                        ashiria ValueError('Unable to configure '
                                         'formatter %r' % name) kutoka e
                # Next, do filters - they don't refer to anything else, either
                filters = config.get('filters', EMPTY_DICT)
                kila name kwenye filters:
                    jaribu:
                        filters[name] = self.configure_filter(filters[name])
                    tatizo Exception kama e:
                        ashiria ValueError('Unable to configure '
                                         'filter %r' % name) kutoka e

                # Next, do handlers - they refer to formatters na filters
                # As handlers can refer to other handlers, sort the keys
                # to allow a deterministic order of configuration
                handlers = config.get('handlers', EMPTY_DICT)
                deferred = []
                kila name kwenye sorted(handlers):
                    jaribu:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    tatizo Exception kama e:
                        ikiwa 'target sio configured yet' kwenye str(e.__cause__):
                            deferred.append(name)
                        isipokua:
                            ashiria ValueError('Unable to configure handler '
                                             '%r' % name) kutoka e

                # Now do any that were deferred
                kila name kwenye deferred:
                    jaribu:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    tatizo Exception kama e:
                        ashiria ValueError('Unable to configure handler '
                                         '%r' % name) kutoka e

                # Next, do loggers - they refer to handlers na filters

                #we don't want to lose the existing loggers,
                #since other threads may have pointers to them.
                #existing ni set to contain all existing loggers,
                #and kama we go through the new configuration we
                #remove any which are configured. At the end,
                #what's left kwenye existing ni the set of loggers
                #which were kwenye the previous configuration but
                #which are haiko kwenye the new configuration.
                root = logging.root
                existing = list(root.manager.loggerDict.keys())
                #The list needs to be sorted so that we can
                #avoid disabling child loggers of explicitly
                #named loggers. With a sorted list it ni easier
                #to find the child loggers.
                existing.sort()
                #We'll keep the list of existing loggers
                #which are children of named loggers here...
                child_loggers = []
                #now set up the new ones...
                loggers = config.get('loggers', EMPTY_DICT)
                kila name kwenye loggers:
                    ikiwa name kwenye existing:
                        i = existing.index(name) + 1 # look after name
                        prefixed = name + "."
                        pflen = len(prefixed)
                        num_existing = len(existing)
                        wakati i < num_existing:
                            ikiwa existing[i][:pflen] == prefixed:
                                child_loggers.append(existing[i])
                            i += 1
                        existing.remove(name)
                    jaribu:
                        self.configure_logger(name, loggers[name])
                    tatizo Exception kama e:
                        ashiria ValueError('Unable to configure logger '
                                         '%r' % name) kutoka e

                #Disable any old loggers. There's no point deleting
                #them kama other threads may endelea to hold references
                #and by disabling them, you stop them doing any logging.
                #However, don't disable children of named loggers, kama that's
                #probably sio what was intended by the user.
                #kila log kwenye existing:
                #    logger = root.manager.loggerDict[log]
                #    ikiwa log kwenye child_loggers:
                #        logger.level = logging.NOTSET
                #        logger.handlers = []
                #        logger.propagate = Kweli
                #    lasivyo disable_existing:
                #        logger.disabled = Kweli
                _handle_existing_loggers(existing, child_loggers,
                                         disable_existing)

                # And finally, do the root logger
                root = config.get('root', Tupu)
                ikiwa root:
                    jaribu:
                        self.configure_root(root)
                    tatizo Exception kama e:
                        ashiria ValueError('Unable to configure root '
                                         'logger') kutoka e
        mwishowe:
            logging._releaseLock()

    eleza configure_formatter(self, config):
        """Configure a formatter kutoka a dictionary."""
        ikiwa '()' kwenye config:
            factory = config['()'] # kila use kwenye exception handler
            jaribu:
                result = self.configure_custom(config)
            tatizo TypeError kama te:
                ikiwa "'format'" haiko kwenye str(te):
                    raise
                #Name of parameter changed kutoka fmt to format.
                #Retry ukijumuisha old name.
                #This ni so that code can be used ukijumuisha older Python versions
                #(e.g. by Django)
                config['fmt'] = config.pop('format')
                config['()'] = factory
                result = self.configure_custom(config)
        isipokua:
            fmt = config.get('format', Tupu)
            dfmt = config.get('datefmt', Tupu)
            style = config.get('style', '%')
            cname = config.get('class', Tupu)

            ikiwa sio cname:
                c = logging.Formatter
            isipokua:
                c = _resolve(cname)

            # A TypeError would be raised ikiwa "validate" key ni pitaed kwenye ukijumuisha a formatter callable
            # that does sio accept "validate" kama a parameter
            ikiwa 'validate' kwenye config:  # ikiwa user hasn't mentioned it, the default will be fine
                result = c(fmt, dfmt, style, config['validate'])
            isipokua:
                result = c(fmt, dfmt, style)

        rudisha result

    eleza configure_filter(self, config):
        """Configure a filter kutoka a dictionary."""
        ikiwa '()' kwenye config:
            result = self.configure_custom(config)
        isipokua:
            name = config.get('name', '')
            result = logging.Filter(name)
        rudisha result

    eleza add_filters(self, filterer, filters):
        """Add filters to a filterer kutoka a list of names."""
        kila f kwenye filters:
            jaribu:
                filterer.addFilter(self.config['filters'][f])
            tatizo Exception kama e:
                ashiria ValueError('Unable to add filter %r' % f) kutoka e

    eleza configure_handler(self, config):
        """Configure a handler kutoka a dictionary."""
        config_copy = dict(config)  # kila restoring kwenye case of error
        formatter = config.pop('formatter', Tupu)
        ikiwa formatter:
            jaribu:
                formatter = self.config['formatters'][formatter]
            tatizo Exception kama e:
                ashiria ValueError('Unable to set formatter '
                                 '%r' % formatter) kutoka e
        level = config.pop('level', Tupu)
        filters = config.pop('filters', Tupu)
        ikiwa '()' kwenye config:
            c = config.pop('()')
            ikiwa sio callable(c):
                c = self.resolve(c)
            factory = c
        isipokua:
            cname = config.pop('class')
            klass = self.resolve(cname)
            #Special case kila handler which refers to another handler
            ikiwa issubclass(klass, logging.handlers.MemoryHandler) and\
                'target' kwenye config:
                jaribu:
                    th = self.config['handlers'][config['target']]
                    ikiwa sio isinstance(th, logging.Handler):
                        config.update(config_copy)  # restore kila deferred cfg
                        ashiria TypeError('target sio configured yet')
                    config['target'] = th
                tatizo Exception kama e:
                    ashiria ValueError('Unable to set target handler '
                                     '%r' % config['target']) kutoka e
            lasivyo issubclass(klass, logging.handlers.SMTPHandler) and\
                'mailhost' kwenye config:
                config['mailhost'] = self.as_tuple(config['mailhost'])
            lasivyo issubclass(klass, logging.handlers.SysLogHandler) and\
                'address' kwenye config:
                config['address'] = self.as_tuple(config['address'])
            factory = klass
        props = config.pop('.', Tupu)
        kwargs = {k: config[k] kila k kwenye config ikiwa valid_ident(k)}
        jaribu:
            result = factory(**kwargs)
        tatizo TypeError kama te:
            ikiwa "'stream'" haiko kwenye str(te):
                raise
            #The argument name changed kutoka strm to stream
            #Retry ukijumuisha old name.
            #This ni so that code can be used ukijumuisha older Python versions
            #(e.g. by Django)
            kwargs['strm'] = kwargs.pop('stream')
            result = factory(**kwargs)
        ikiwa formatter:
            result.setFormatter(formatter)
        ikiwa level ni sio Tupu:
            result.setLevel(logging._checkLevel(level))
        ikiwa filters:
            self.add_filters(result, filters)
        ikiwa props:
            kila name, value kwenye props.items():
                setattr(result, name, value)
        rudisha result

    eleza add_handlers(self, logger, handlers):
        """Add handlers to a logger kutoka a list of names."""
        kila h kwenye handlers:
            jaribu:
                logger.addHandler(self.config['handlers'][h])
            tatizo Exception kama e:
                ashiria ValueError('Unable to add handler %r' % h) kutoka e

    eleza common_logger_config(self, logger, config, incremental=Uongo):
        """
        Perform configuration which ni common to root na non-root loggers.
        """
        level = config.get('level', Tupu)
        ikiwa level ni sio Tupu:
            logger.setLevel(logging._checkLevel(level))
        ikiwa sio incremental:
            #Remove any existing handlers
            kila h kwenye logger.handlers[:]:
                logger.removeHandler(h)
            handlers = config.get('handlers', Tupu)
            ikiwa handlers:
                self.add_handlers(logger, handlers)
            filters = config.get('filters', Tupu)
            ikiwa filters:
                self.add_filters(logger, filters)

    eleza configure_logger(self, name, config, incremental=Uongo):
        """Configure a non-root logger kutoka a dictionary."""
        logger = logging.getLogger(name)
        self.common_logger_config(logger, config, incremental)
        propagate = config.get('propagate', Tupu)
        ikiwa propagate ni sio Tupu:
            logger.propagate = propagate

    eleza configure_root(self, config, incremental=Uongo):
        """Configure a root logger kutoka a dictionary."""
        root = logging.getLogger()
        self.common_logger_config(root, config, incremental)

dictConfigClass = DictConfigurator

eleza dictConfig(config):
    """Configure logging using a dictionary."""
    dictConfigClass(config).configure()


eleza listen(port=DEFAULT_LOGGING_CONFIG_PORT, verify=Tupu):
    """
    Start up a socket server on the specified port, na listen kila new
    configurations.

    These will be sent kama a file suitable kila processing by fileConfig().
    Returns a Thread object on which you can call start() to start the server,
    na which you can join() when appropriate. To stop the server, call
    stopListening().

    Use the ``verify`` argument to verify any bytes received across the wire
    kutoka a client. If specified, it should be a callable which receives a
    single argument - the bytes of configuration data received across the
    network - na it should rudisha either ``Tupu``, to indicate that the
    pitaed kwenye bytes could sio be verified na should be discarded, ama a
    byte string which ni then pitaed to the configuration machinery as
    normal. Note that you can rudisha transformed bytes, e.g. by decrypting
    the bytes pitaed in.
    """

    kundi ConfigStreamHandler(StreamRequestHandler):
        """
        Handler kila a logging configuration request.

        It expects a completely new logging configuration na uses fileConfig
        to install it.
        """
        eleza handle(self):
            """
            Handle a request.

            Each request ni expected to be a 4-byte length, packed using
            struct.pack(">L", n), followed by the config file.
            Uses fileConfig() to do the grunt work.
            """
            jaribu:
                conn = self.connection
                chunk = conn.recv(4)
                ikiwa len(chunk) == 4:
                    slen = struct.unpack(">L", chunk)[0]
                    chunk = self.connection.recv(slen)
                    wakati len(chunk) < slen:
                        chunk = chunk + conn.recv(slen - len(chunk))
                    ikiwa self.server.verify ni sio Tupu:
                        chunk = self.server.verify(chunk)
                    ikiwa chunk ni sio Tupu:   # verified, can process
                        chunk = chunk.decode("utf-8")
                        jaribu:
                            agiza json
                            d =json.loads(chunk)
                            assert isinstance(d, dict)
                            dictConfig(d)
                        tatizo Exception:
                            #Apply new configuration.

                            file = io.StringIO(chunk)
                            jaribu:
                                fileConfig(file)
                            tatizo Exception:
                                traceback.print_exc()
                    ikiwa self.server.ready:
                        self.server.ready.set()
            tatizo OSError kama e:
                ikiwa e.errno != RESET_ERROR:
                    raise

    kundi ConfigSocketReceiver(ThreadingTCPServer):
        """
        A simple TCP socket-based logging config receiver.
        """

        allow_reuse_address = 1

        eleza __init__(self, host='localhost', port=DEFAULT_LOGGING_CONFIG_PORT,
                     handler=Tupu, ready=Tupu, verify=Tupu):
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
            wakati sio abort:
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
    Stop the listening server which was created ukijumuisha a call to listen().
    """
    global _listener
    logging._acquireLock()
    jaribu:
        ikiwa _listener:
            _listener.abort = 1
            _listener = Tupu
    mwishowe:
        logging._releaseLock()
