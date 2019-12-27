# Copyright 2001-2017 by Vinay Sajip. All Rights Reserved.
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
Logging package for Python. Based on PEP 282 and comments thereto in
comp.lang.python.

Copyright (C) 2001-2017 Vinay Sajip. All Rights Reserved.

To use, simply 'agiza logging' and log away!
"""

agiza sys, os, time, io, re, traceback, warnings, weakref, collections.abc

kutoka string agiza Template
kutoka string agiza Formatter as StrFormatter


__all__ = ['BASIC_FORMAT', 'BufferingFormatter', 'CRITICAL', 'DEBUG', 'ERROR',
           'FATAL', 'FileHandler', 'Filter', 'Formatter', 'Handler', 'INFO',
           'LogRecord', 'Logger', 'LoggerAdapter', 'NOTSET', 'NullHandler',
           'StreamHandler', 'WARN', 'WARNING', 'addLevelName', 'basicConfig',
           'captureWarnings', 'critical', 'debug', 'disable', 'error',
           'exception', 'fatal', 'getLevelName', 'getLogger', 'getLoggerClass',
           'info', 'log', 'makeLogRecord', 'setLoggerClass', 'shutdown',
           'warn', 'warning', 'getLogRecordFactory', 'setLogRecordFactory',
           'lastResort', 'raiseExceptions']

agiza threading

__author__  = "Vinay Sajip <vinay_sajip@red-dove.com>"
__status__  = "production"
# The following module attributes are no longer updated.
__version__ = "0.5.1.2"
__date__    = "07 February 2010"

#---------------------------------------------------------------------------
#   Miscellaneous module data
#---------------------------------------------------------------------------

#
#_startTime is used as the base when calculating the relative time of events
#
_startTime = time.time()

#
#raiseExceptions is used to see ikiwa exceptions during handling should be
#propagated
#
raiseExceptions = True

#
# If you don't want threading information in the log, set this to zero
#
logThreads = True

#
# If you don't want multiprocessing information in the log, set this to zero
#
logMultiprocessing = True

#
# If you don't want process information in the log, set this to zero
#
logProcesses = True

#---------------------------------------------------------------------------
#   Level related stuff
#---------------------------------------------------------------------------
#
# Default levels and level names, these can be replaced with any positive set
# of values having corresponding names. There is a pseudo-level, NOTSET, which
# is only really there as a lower limit for user-defined levels. Handlers and
# loggers are initialized with NOTSET so that they will log all messages, even
# at user-defined levels.
#

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_levelToName = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
}
_nameToLevel = {
    'CRITICAL': CRITICAL,
    'FATAL': FATAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
}

eleza getLevelName(level):
    """
    Return the textual representation of logging level 'level'.

    If the level is one of the predefined levels (CRITICAL, ERROR, WARNING,
    INFO, DEBUG) then you get the corresponding string. If you have
    associated levels with names using addLevelName then the name you have
    associated with 'level' is returned.

    If a numeric value corresponding to one of the defined levels is passed
    in, the corresponding string representation is returned.

    Otherwise, the string "Level %s" % level is returned.
    """
    # See Issues #22386, #27937 and #29220 for why it's this way
    result = _levelToName.get(level)
    ikiwa result is not None:
        rudisha result
    result = _nameToLevel.get(level)
    ikiwa result is not None:
        rudisha result
    rudisha "Level %s" % level

eleza addLevelName(level, levelName):
    """
    Associate 'levelName' with 'level'.

    This is used when converting levels to text during message formatting.
    """
    _acquireLock()
    try:    #unlikely to cause an exception, but you never know...
        _levelToName[level] = levelName
        _nameToLevel[levelName] = level
    finally:
        _releaseLock()

ikiwa hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
else: #pragma: no cover
    eleza currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            rudisha sys.exc_info()[2].tb_frame.f_back

#
# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame, by skipping frames whose filename is that of this
# module's source. It therefore should contain the filename of this module's
# source file.
#
# Ordinarily we would use __file__ for this, but frozen modules don't always
# have __file__ set, for some reason (see Issue #21736). Thus, we get the
# filename kutoka a handy code object kutoka a function defined in this module.
# (There's no particular reason for picking addLevelName.)
#

_srcfile = os.path.normcase(addLevelName.__code__.co_filename)

# _srcfile is only used in conjunction with sys._getframe().
# To provide compatibility with older versions of Python, set _srcfile
# to None ikiwa _getframe() is not available; this value will prevent
# findCaller() kutoka being called. You can also do this ikiwa you want to avoid
# the overhead of fetching caller information, even when _getframe() is
# available.
#ikiwa not hasattr(sys, '_getframe'):
#    _srcfile = None


eleza _checkLevel(level):
    ikiwa isinstance(level, int):
        rv = level
    elikiwa str(level) == level:
        ikiwa level not in _nameToLevel:
            raise ValueError("Unknown level: %r" % level)
        rv = _nameToLevel[level]
    else:
        raise TypeError("Level not an integer or a valid string: %r" % level)
    rudisha rv

#---------------------------------------------------------------------------
#   Thread-related stuff
#---------------------------------------------------------------------------

#
#_lock is used to serialize access to shared data structures in this module.
#This needs to be an RLock because fileConfig() creates and configures
#Handlers, and so might arbitrary user threads. Since Handler code updates the
#shared dictionary _handlers, it needs to acquire the lock. But ikiwa configuring,
#the lock would already have been acquired - so we need an RLock.
#The same argument applies to Loggers and Manager.loggerDict.
#
_lock = threading.RLock()

eleza _acquireLock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    ikiwa _lock:
        _lock.acquire()

eleza _releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    ikiwa _lock:
        _lock.release()


# Prevent a held logging lock kutoka blocking a child kutoka logging.

ikiwa not hasattr(os, 'register_at_fork'):  # Windows and friends.
    eleza _register_at_fork_reinit_lock(instance):
        pass  # no-op when os.register_at_fork does not exist.
else:
    # A collection of instances with a createLock method (logging.Handler)
    # to be called in the child after forking.  The weakref avoids us keeping
    # discarded Handler instances alive.  A set is used to avoid accumulating
    # duplicate registrations as createLock() is responsible for registering
    # a new Handler instance with this set in the first place.
    _at_fork_reinit_lock_weakset = weakref.WeakSet()

    eleza _register_at_fork_reinit_lock(instance):
        _acquireLock()
        try:
            _at_fork_reinit_lock_weakset.add(instance)
        finally:
            _releaseLock()

    eleza _after_at_fork_child_reinit_locks():
        # _acquireLock() was called in the parent before forking.
        for handler in _at_fork_reinit_lock_weakset:
            try:
                handler.createLock()
            except Exception as err:
                # Similar to what PyErr_WriteUnraisable does.
                andika("Ignoring exception kutoka logging atfork", instance,
                      "._reinit_lock() method:", err, file=sys.stderr)
        _releaseLock()  # Acquired by os.register_at_fork(before=.


    os.register_at_fork(before=_acquireLock,
                        after_in_child=_after_at_fork_child_reinit_locks,
                        after_in_parent=_releaseLock)


#---------------------------------------------------------------------------
#   The logging record
#---------------------------------------------------------------------------

kundi LogRecord(object):
    """
    A LogRecord instance represents an event being logged.

    LogRecord instances are created every time something is logged. They
    contain all the information pertinent to the event being logged. The
    main information passed in is in msg and args, which are combined
    using str(msg) % args to create the message field of the record. The
    record also includes information such as when the record was created,
    the source line where the logging call was made, and any exception
    information to be logged.
    """
    eleza __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=None, sinfo=None, **kwargs):
        """
        Initialize a logging record with interesting information.
        """
        ct = time.time()
        self.name = name
        self.msg = msg
        #
        # The following statement allows passing of a dictionary as a sole
        # argument, so that you can do something like
        #  logging.debug("a %(a)d b %(b)s", {'a':1, 'b':2})
        # Suggested by Stefan Behnel.
        # Note that without the test for args[0], we get a problem because
        # during formatting, we test to see ikiwa the arg is present using
        # 'ikiwa self.args:'. If the event being logged is e.g. 'Value is %d'
        # and ikiwa the passed arg fails 'ikiwa self.args:' then no formatting
        # is done. For example, logger.warning('Value is %d', 0) would log
        # 'Value is %d' instead of 'Value is 0'.
        # For the use case of passing a dictionary, this should not be a
        # problem.
        # Issue #21172: a request was made to relax the isinstance check
        # to hasattr(args[0], '__getitem__'). However, the docs on string
        # formatting still seem to suggest a mapping object is required.
        # Thus, while not removing the isinstance check, it does now look
        # for collections.abc.Mapping rather than, as before, dict.
        ikiwa (args and len(args) == 1 and isinstance(args[0], collections.abc.Mapping)
            and args[0]):
            args = args[0]
        self.args = args
        self.levelname = getLevelName(level)
        self.levelno = level
        self.pathname = pathname
        try:
            self.filename = os.path.basename(pathname)
            self.module = os.path.splitext(self.filename)[0]
        except (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = "Unknown module"
        self.exc_info = exc_info
        self.exc_text = None      # used to cache the traceback text
        self.stack_info = sinfo
        self.lineno = lineno
        self.funcName = func
        self.created = ct
        self.msecs = (ct - int(ct)) * 1000
        self.relativeCreated = (self.created - _startTime) * 1000
        ikiwa logThreads:
            self.thread = threading.get_ident()
            self.threadName = threading.current_thread().name
        else: # pragma: no cover
            self.thread = None
            self.threadName = None
        ikiwa not logMultiprocessing: # pragma: no cover
            self.processName = None
        else:
            self.processName = 'MainProcess'
            mp = sys.modules.get('multiprocessing')
            ikiwa mp is not None:
                # Errors may occur ikiwa multiprocessing has not finished loading
                # yet - e.g. ikiwa a custom agiza hook causes third-party code
                # to run when multiprocessing calls agiza. See issue 8200
                # for an example
                try:
                    self.processName = mp.current_process().name
                except Exception: #pragma: no cover
                    pass
        ikiwa logProcesses and hasattr(os, 'getpid'):
            self.process = os.getpid()
        else:
            self.process = None

    eleza __repr__(self):
        rudisha '<LogRecord: %s, %s, %s, %s, "%s">'%(self.name, self.levelno,
            self.pathname, self.lineno, self.msg)

    eleza getMessage(self):
        """
        Return the message for this LogRecord.

        Return the message for this LogRecord after merging any user-supplied
        arguments with the message.
        """
        msg = str(self.msg)
        ikiwa self.args:
            msg = msg % self.args
        rudisha msg

#
#   Determine which kundi to use when instantiating log records.
#
_logRecordFactory = LogRecord

eleza setLogRecordFactory(factory):
    """
    Set the factory to be used when instantiating a log record.

    :param factory: A callable which will be called to instantiate
    a log record.
    """
    global _logRecordFactory
    _logRecordFactory = factory

eleza getLogRecordFactory():
    """
    Return the factory to be used when instantiating a log record.
    """

    rudisha _logRecordFactory

eleza makeLogRecord(dict):
    """
    Make a LogRecord whose attributes are defined by the specified dictionary,
    This function is useful for converting a logging event received over
    a socket connection (which is sent as a dictionary) into a LogRecord
    instance.
    """
    rv = _logRecordFactory(None, None, "", 0, "", (), None, None)
    rv.__dict__.update(dict)
    rudisha rv


#---------------------------------------------------------------------------
#   Formatter classes and functions
#---------------------------------------------------------------------------
_str_formatter = StrFormatter()
del StrFormatter


kundi PercentStyle(object):

    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'
    validation_pattern = re.compile(r'%\(\w+\)[#0+ -]*(\*|\d+)?(\.(\*|\d+))?[diouxefgcrsa%]', re.I)

    eleza __init__(self, fmt):
        self._fmt = fmt or self.default_format

    eleza usesTime(self):
        rudisha self._fmt.find(self.asctime_search) >= 0

    eleza validate(self):
        """Validate the input format, ensure it matches the correct style"""
        ikiwa not self.validation_pattern.search(self._fmt):
            raise ValueError("Invalid format '%s' for '%s' style" % (self._fmt, self.default_format[0]))

    eleza _format(self, record):
        rudisha self._fmt % record.__dict__

    eleza format(self, record):
        try:
            rudisha self._format(record)
        except KeyError as e:
            raise ValueError('Formatting field not found in record: %s' % e)


kundi StrFormatStyle(PercentStyle):
    default_format = '{message}'
    asctime_format = '{asctime}'
    asctime_search = '{asctime'

    fmt_spec = re.compile(r'^(.?[<>=^])?[+ -]?#?0?(\d+|{\w+})?[,_]?(\.(\d+|{\w+}))?[bcdefgnosx%]?$', re.I)
    field_spec = re.compile(r'^(\d+|\w+)(\.\w+|\[[^]]+\])*$')

    eleza _format(self, record):
        rudisha self._fmt.format(**record.__dict__)

    eleza validate(self):
        """Validate the input format, ensure it is the correct string formatting style"""
        fields = set()
        try:
            for _, fieldname, spec, conversion in _str_formatter.parse(self._fmt):
                ikiwa fieldname:
                    ikiwa not self.field_spec.match(fieldname):
                        raise ValueError('invalid field name/expression: %r' % fieldname)
                    fields.add(fieldname)
                ikiwa conversion and conversion not in 'rsa':
                    raise ValueError('invalid conversion: %r' % conversion)
                ikiwa spec and not self.fmt_spec.match(spec):
                    raise ValueError('bad specifier: %r' % spec)
        except ValueError as e:
            raise ValueError('invalid format: %s' % e)
        ikiwa not fields:
            raise ValueError('invalid format: no fields')


kundi StringTemplateStyle(PercentStyle):
    default_format = '${message}'
    asctime_format = '${asctime}'
    asctime_search = '${asctime}'

    eleza __init__(self, fmt):
        self._fmt = fmt or self.default_format
        self._tpl = Template(self._fmt)

    eleza usesTime(self):
        fmt = self._fmt
        rudisha fmt.find('$asctime') >= 0 or fmt.find(self.asctime_format) >= 0

    eleza validate(self):
        pattern = Template.pattern
        fields = set()
        for m in pattern.finditer(self._fmt):
            d = m.groupdict()
            ikiwa d['named']:
                fields.add(d['named'])
            elikiwa d['braced']:
                fields.add(d['braced'])
            elikiwa m.group(0) == '$':
                raise ValueError('invalid format: bare \'$\' not allowed')
        ikiwa not fields:
            raise ValueError('invalid format: no fields')

    eleza _format(self, record):
        rudisha self._tpl.substitute(**record.__dict__)


BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"

_STYLES = {
    '%': (PercentStyle, BASIC_FORMAT),
    '{': (StrFormatStyle, '{levelname}:{name}:{message}'),
    '$': (StringTemplateStyle, '${levelname}:${name}:${message}'),
}

kundi Formatter(object):
    """
    Formatter instances are used to convert a LogRecord to text.

    Formatters need to know how a LogRecord is constructed. They are
    responsible for converting a LogRecord to (usually) a string which can
    be interpreted by either a human or an external system. The base Formatter
    allows a formatting string to be specified. If none is supplied, the
    the style-dependent default value, "%(message)s", "{message}", or
    "${message}", is used.

    The Formatter can be initialized with a format string which makes use of
    knowledge of the LogRecord attributes - e.g. the default value mentioned
    above makes use of the fact that the user's message and arguments are pre-
    formatted into a LogRecord's message attribute. Currently, the useful
    attributes in a LogRecord are described by:

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (ikiwa available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (ikiwa available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        rudisha value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (ikiwa available)
    %(threadName)s      Thread name (ikiwa available)
    %(process)d         Process ID (ikiwa available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted
    """

    converter = time.localtime

    eleza __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        """
        Initialize the formatter with specified format strings.

        Initialize the formatter either with the specified format string, or a
        default as described above. Allow for specialized date formatting with
        the optional datefmt argument. If datefmt is omitted, you get an
        ISO8601-like (or RFC 3339-like) format.

        Use a style parameter of '%', '{' or '$' to specify that you want to
        use one of %-formatting, :meth:`str.format` (``{}``) formatting or
        :class:`string.Template` formatting in your format string.

        .. versionchanged:: 3.2
           Added the ``style`` parameter.
        """
        ikiwa style not in _STYLES:
            raise ValueError('Style must be one of: %s' % ','.join(
                             _STYLES.keys()))
        self._style = _STYLES[style][0](fmt)
        ikiwa validate:
            self._style.validate()

        self._fmt = self._style._fmt
        self.datefmt = datefmt

    default_time_format = '%Y-%m-%d %H:%M:%S'
    default_msec_format = '%s,%03d'

    eleza formatTime(self, record, datefmt=None):
        """
        Return the creation time of the specified LogRecord as formatted text.

        This method should be called kutoka format() by a formatter which
        wants to make use of a formatted time. This method can be overridden
        in formatters to provide for any specific requirement, but the
        basic behaviour is as follows: ikiwa datefmt (a string) is specified,
        it is used with time.strftime() to format the creation time of the
        record. Otherwise, an ISO8601-like (or RFC 3339-like) format is used.
        The resulting string is returned. This function uses a user-configurable
        function to convert the creation time to a tuple. By default,
        time.localtime() is used; to change this for a particular formatter
        instance, set the 'converter' attribute to a function with the same
        signature as time.localtime() or time.gmtime(). To change it for all
        formatters, for example ikiwa you want all logging times to be shown in GMT,
        set the 'converter' attribute in the Formatter class.
        """
        ct = self.converter(record.created)
        ikiwa datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime(self.default_time_format, ct)
            s = self.default_msec_format % (t, record.msecs)
        rudisha s

    eleza formatException(self, ei):
        """
        Format and rudisha the specified exception information as a string.

        This default implementation just uses
        traceback.print_exception()
        """
        sio = io.StringIO()
        tb = ei[2]
        # See issues #9427, #1553375. Commented out for now.
        #ikiwa getattr(self, 'fullstack', False):
        #    traceback.print_stack(tb.tb_frame.f_back, file=sio)
        traceback.print_exception(ei[0], ei[1], tb, None, sio)
        s = sio.getvalue()
        sio.close()
        ikiwa s[-1:] == "\n":
            s = s[:-1]
        rudisha s

    eleza usesTime(self):
        """
        Check ikiwa the format uses the creation time of the record.
        """
        rudisha self._style.usesTime()

    eleza formatMessage(self, record):
        rudisha self._style.format(record)

    eleza formatStack(self, stack_info):
        """
        This method is provided as an extension point for specialized
        formatting of stack information.

        The input data is a string as returned kutoka a call to
        :func:`traceback.print_stack`, but with the last trailing newline
        removed.

        The base implementation just returns the value passed in.
        """
        rudisha stack_info

    eleza format(self, record):
        """
        Format the specified record as text.

        The record's attribute dictionary is used as the operand to a
        string formatting operation which yields the returned string.
        Before formatting the dictionary, a couple of preparatory steps
        are carried out. The message attribute of the record is computed
        using LogRecord.getMessage(). If the formatting string uses the
        time (as determined by a call to usesTime(), formatTime() is
        called to format the event time. If there is exception information,
        it is formatted using formatException() and appended to the message.
        """
        record.message = record.getMessage()
        ikiwa self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        ikiwa record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            ikiwa not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        ikiwa record.exc_text:
            ikiwa s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        ikiwa record.stack_info:
            ikiwa s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        rudisha s

#
#   The default formatter to use when no other is specified
#
_defaultFormatter = Formatter()

kundi BufferingFormatter(object):
    """
    A formatter suitable for formatting a number of records.
    """
    eleza __init__(self, linefmt=None):
        """
        Optionally specify a formatter which will be used to format each
        individual record.
        """
        ikiwa linefmt:
            self.linefmt = linefmt
        else:
            self.linefmt = _defaultFormatter

    eleza formatHeader(self, records):
        """
        Return the header string for the specified records.
        """
        rudisha ""

    eleza formatFooter(self, records):
        """
        Return the footer string for the specified records.
        """
        rudisha ""

    eleza format(self, records):
        """
        Format the specified records and rudisha the result as a string.
        """
        rv = ""
        ikiwa len(records) > 0:
            rv = rv + self.formatHeader(records)
            for record in records:
                rv = rv + self.linefmt.format(record)
            rv = rv + self.formatFooter(records)
        rudisha rv

#---------------------------------------------------------------------------
#   Filter classes and functions
#---------------------------------------------------------------------------

kundi Filter(object):
    """
    Filter instances are used to perform arbitrary filtering of LogRecords.

    Loggers and Handlers can optionally use Filter instances to filter
    records as desired. The base filter kundi only allows events which are
    below a certain point in the logger hierarchy. For example, a filter
    initialized with "A.B" will allow events logged by loggers "A.B",
    "A.B.C", "A.B.C.D", "A.B.D" etc. but not "A.BB", "B.A.B" etc. If
    initialized with the empty string, all events are passed.
    """
    eleza __init__(self, name=''):
        """
        Initialize a filter.

        Initialize with the name of the logger which, together with its
        children, will have its events allowed through the filter. If no
        name is specified, allow every event.
        """
        self.name = name
        self.nlen = len(name)

    eleza filter(self, record):
        """
        Determine ikiwa the specified record is to be logged.

        Is the specified record to be logged? Returns 0 for no, nonzero for
        yes. If deemed appropriate, the record may be modified in-place.
        """
        ikiwa self.nlen == 0:
            rudisha True
        elikiwa self.name == record.name:
            rudisha True
        elikiwa record.name.find(self.name, 0, self.nlen) != 0:
            rudisha False
        rudisha (record.name[self.nlen] == ".")

kundi Filterer(object):
    """
    A base kundi for loggers and handlers which allows them to share
    common code.
    """
    eleza __init__(self):
        """
        Initialize the list of filters to be an empty list.
        """
        self.filters = []

    eleza addFilter(self, filter):
        """
        Add the specified filter to this handler.
        """
        ikiwa not (filter in self.filters):
            self.filters.append(filter)

    eleza removeFilter(self, filter):
        """
        Remove the specified filter kutoka this handler.
        """
        ikiwa filter in self.filters:
            self.filters.remove(filter)

    eleza filter(self, record):
        """
        Determine ikiwa a record is loggable by consulting all the filters.

        The default is to allow the record to be logged; any filter can veto
        this and the record is then dropped. Returns a zero value ikiwa a record
        is to be dropped, else non-zero.

        .. versionchanged:: 3.2

           Allow filters to be just callables.
        """
        rv = True
        for f in self.filters:
            ikiwa hasattr(f, 'filter'):
                result = f.filter(record)
            else:
                result = f(record) # assume callable - will raise ikiwa not
            ikiwa not result:
                rv = False
                break
        rudisha rv

#---------------------------------------------------------------------------
#   Handler classes and functions
#---------------------------------------------------------------------------

_handlers = weakref.WeakValueDictionary()  #map of handler names to handlers
_handlerList = [] # added to allow handlers to be removed in reverse of order initialized

eleza _removeHandlerRef(wr):
    """
    Remove a handler reference kutoka the internal cleanup list.
    """
    # This function can be called during module teardown, when globals are
    # set to None. It can also be called kutoka another thread. So we need to
    # pre-emptively grab the necessary globals and check ikiwa they're None,
    # to prevent race conditions and failures during interpreter shutdown.
    acquire, release, handlers = _acquireLock, _releaseLock, _handlerList
    ikiwa acquire and release and handlers:
        acquire()
        try:
            ikiwa wr in handlers:
                handlers.remove(wr)
        finally:
            release()

eleza _addHandlerRef(handler):
    """
    Add a handler to the internal cleanup list using a weak reference.
    """
    _acquireLock()
    try:
        _handlerList.append(weakref.ref(handler, _removeHandlerRef))
    finally:
        _releaseLock()

kundi Handler(Filterer):
    """
    Handler instances dispatch logging events to specific destinations.

    The base handler class. Acts as a placeholder which defines the Handler
    interface. Handlers can optionally use Formatter instances to format
    records as desired. By default, no formatter is specified; in this case,
    the 'raw' message as determined by record.message is logged.
    """
    eleza __init__(self, level=NOTSET):
        """
        Initializes the instance - basically setting the formatter to None
        and the filter list to empty.
        """
        Filterer.__init__(self)
        self._name = None
        self.level = _checkLevel(level)
        self.formatter = None
        # Add the handler to the global _handlerList (for cleanup on shutdown)
        _addHandlerRef(self)
        self.createLock()

    eleza get_name(self):
        rudisha self._name

    eleza set_name(self, name):
        _acquireLock()
        try:
            ikiwa self._name in _handlers:
                del _handlers[self._name]
            self._name = name
            ikiwa name:
                _handlers[name] = self
        finally:
            _releaseLock()

    name = property(get_name, set_name)

    eleza createLock(self):
        """
        Acquire a thread lock for serializing access to the underlying I/O.
        """
        self.lock = threading.RLock()
        _register_at_fork_reinit_lock(self)

    eleza acquire(self):
        """
        Acquire the I/O thread lock.
        """
        ikiwa self.lock:
            self.lock.acquire()

    eleza release(self):
        """
        Release the I/O thread lock.
        """
        ikiwa self.lock:
            self.lock.release()

    eleza setLevel(self, level):
        """
        Set the logging level of this handler.  level must be an int or a str.
        """
        self.level = _checkLevel(level)

    eleza format(self, record):
        """
        Format the specified record.

        If a formatter is set, use it. Otherwise, use the default formatter
        for the module.
        """
        ikiwa self.formatter:
            fmt = self.formatter
        else:
            fmt = _defaultFormatter
        rudisha fmt.format(record)

    eleza emit(self, record):
        """
        Do whatever it takes to actually log the specified logging record.

        This version is intended to be implemented by subclasses and so
        raises a NotImplementedError.
        """
        raise NotImplementedError('emit must be implemented '
                                  'by Handler subclasses')

    eleza handle(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record with acquisition/release of
        the I/O thread lock. Returns whether the filter passed the record for
        emission.
        """
        rv = self.filter(record)
        ikiwa rv:
            self.acquire()
            try:
                self.emit(record)
            finally:
                self.release()
        rudisha rv

    eleza setFormatter(self, fmt):
        """
        Set the formatter for this handler.
        """
        self.formatter = fmt

    eleza flush(self):
        """
        Ensure all logging output has been flushed.

        This version does nothing and is intended to be implemented by
        subclasses.
        """
        pass

    eleza close(self):
        """
        Tidy up any resources used by the handler.

        This version removes the handler kutoka an internal map of handlers,
        _handlers, which is used for handler lookup by name. Subclasses
        should ensure that this gets called kutoka overridden close()
        methods.
        """
        #get the module data lock, as we're updating a shared structure.
        _acquireLock()
        try:    #unlikely to raise an exception, but you never know...
            ikiwa self._name and self._name in _handlers:
                del _handlers[self._name]
        finally:
            _releaseLock()

    eleza handleError(self, record):
        """
        Handle errors which occur during an emit() call.

        This method should be called kutoka handlers when an exception is
        encountered during an emit() call. If raiseExceptions is false,
        exceptions get silently ignored. This is what is mostly wanted
        for a logging system - most users will not care about errors in
        the logging system, they are more interested in application errors.
        You could, however, replace this with a custom handler ikiwa you wish.
        The record which was being processed is passed in to this method.
        """
        ikiwa raiseExceptions and sys.stderr:  # see issue 13807
            t, v, tb = sys.exc_info()
            try:
                sys.stderr.write('--- Logging error ---\n')
                traceback.print_exception(t, v, tb, None, sys.stderr)
                sys.stderr.write('Call stack:\n')
                # Walk the stack frame up until we're out of logging,
                # so as to print the calling context.
                frame = tb.tb_frame
                while (frame and os.path.dirname(frame.f_code.co_filename) ==
                       __path__[0]):
                    frame = frame.f_back
                ikiwa frame:
                    traceback.print_stack(frame, file=sys.stderr)
                else:
                    # couldn't find the right stack frame, for some reason
                    sys.stderr.write('Logged kutoka file %s, line %s\n' % (
                                     record.filename, record.lineno))
                # Issue 18671: output logging message and arguments
                try:
                    sys.stderr.write('Message: %r\n'
                                     'Arguments: %s\n' % (record.msg,
                                                          record.args))
                except RecursionError:  # See issue 36272
                    raise
                except Exception:
                    sys.stderr.write('Unable to print the message and arguments'
                                     ' - possible formatting error.\nUse the'
                                     ' traceback above to help find the error.\n'
                                    )
            except OSError: #pragma: no cover
                pass    # see issue 5971
            finally:
                del t, v, tb

    eleza __repr__(self):
        level = getLevelName(self.level)
        rudisha '<%s (%s)>' % (self.__class__.__name__, level)

kundi StreamHandler(Handler):
    """
    A handler kundi which writes logging records, appropriately formatted,
    to a stream. Note that this kundi does not close the stream, as
    sys.stdout or sys.stderr may be used.
    """

    terminator = '\n'

    eleza __init__(self, stream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        Handler.__init__(self)
        ikiwa stream is None:
            stream = sys.stderr
        self.stream = stream

    eleza flush(self):
        """
        Flushes the stream.
        """
        self.acquire()
        try:
            ikiwa self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
        finally:
            self.release()

    eleza emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)

    eleza setStream(self, stream):
        """
        Sets the StreamHandler's stream to the specified value,
        ikiwa it is different.

        Returns the old stream, ikiwa the stream was changed, or None
        ikiwa it wasn't.
        """
        ikiwa stream is self.stream:
            result = None
        else:
            result = self.stream
            self.acquire()
            try:
                self.flush()
                self.stream = stream
            finally:
                self.release()
        rudisha result

    eleza __repr__(self):
        level = getLevelName(self.level)
        name = getattr(self.stream, 'name', '')
        #  bpo-36015: name can be an int
        name = str(name)
        ikiwa name:
            name += ' '
        rudisha '<%s %s(%s)>' % (self.__class__.__name__, name, level)


kundi FileHandler(StreamHandler):
    """
    A handler kundi which writes formatted logging records to disk files.
    """
    eleza __init__(self, filename, mode='a', encoding=None, delay=False):
        """
        Open the specified file and use it as the stream for logging.
        """
        # Issue #27493: add support for Path objects to be passed in
        filename = os.fspath(filename)
        #keep the absolute path, otherwise derived classes which use this
        #may come a cropper when the current directory changes
        self.baseFilename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        ikiwa delay:
            #We don't open the stream, but we still need to call the
            #Handler constructor to set level, formatter, lock etc.
            Handler.__init__(self)
            self.stream = None
        else:
            StreamHandler.__init__(self, self._open())

    eleza close(self):
        """
        Closes the stream.
        """
        self.acquire()
        try:
            try:
                ikiwa self.stream:
                    try:
                        self.flush()
                    finally:
                        stream = self.stream
                        self.stream = None
                        ikiwa hasattr(stream, "close"):
                            stream.close()
            finally:
                # Issue #19523: call unconditionally to
                # prevent a handler leak when delay is set
                StreamHandler.close(self)
        finally:
            self.release()

    eleza _open(self):
        """
        Open the current base file with the (original) mode and encoding.
        Return the resulting stream.
        """
        rudisha open(self.baseFilename, self.mode, encoding=self.encoding)

    eleza emit(self, record):
        """
        Emit a record.

        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """
        ikiwa self.stream is None:
            self.stream = self._open()
        StreamHandler.emit(self, record)

    eleza __repr__(self):
        level = getLevelName(self.level)
        rudisha '<%s %s (%s)>' % (self.__class__.__name__, self.baseFilename, level)


kundi _StderrHandler(StreamHandler):
    """
    This kundi is like a StreamHandler using sys.stderr, but always uses
    whatever sys.stderr is currently set to rather than the value of
    sys.stderr at handler construction time.
    """
    eleza __init__(self, level=NOTSET):
        """
        Initialize the handler.
        """
        Handler.__init__(self, level)

    @property
    eleza stream(self):
        rudisha sys.stderr


_defaultLastResort = _StderrHandler(WARNING)
lastResort = _defaultLastResort

#---------------------------------------------------------------------------
#   Manager classes and functions
#---------------------------------------------------------------------------

kundi PlaceHolder(object):
    """
    PlaceHolder instances are used in the Manager logger hierarchy to take
    the place of nodes for which no loggers have been defined. This kundi is
    intended for internal use only and not as part of the public API.
    """
    eleza __init__(self, alogger):
        """
        Initialize with the specified logger being a child of this placeholder.
        """
        self.loggerMap = { alogger : None }

    eleza append(self, alogger):
        """
        Add the specified logger as a child of this placeholder.
        """
        ikiwa alogger not in self.loggerMap:
            self.loggerMap[alogger] = None

#
#   Determine which kundi to use when instantiating loggers.
#

eleza setLoggerClass(klass):
    """
    Set the kundi to be used when instantiating a logger. The kundi should
    define __init__() such that only a name argument is required, and the
    __init__() should call Logger.__init__()
    """
    ikiwa klass != Logger:
        ikiwa not issubclass(klass, Logger):
            raise TypeError("logger not derived kutoka logging.Logger: "
                            + klass.__name__)
    global _loggerClass
    _loggerClass = klass

eleza getLoggerClass():
    """
    Return the kundi to be used when instantiating a logger.
    """
    rudisha _loggerClass

kundi Manager(object):
    """
    There is [under normal circumstances] just one Manager instance, which
    holds the hierarchy of loggers.
    """
    eleza __init__(self, rootnode):
        """
        Initialize the manager with the root node of the logger hierarchy.
        """
        self.root = rootnode
        self.disable = 0
        self.emittedNoHandlerWarning = False
        self.loggerDict = {}
        self.loggerClass = None
        self.logRecordFactory = None

    eleza getLogger(self, name):
        """
        Get a logger with the specified name (channel name), creating it
        ikiwa it doesn't yet exist. This name is a dot-separated hierarchical
        name, such as "a", "a.b", "a.b.c" or similar.

        If a PlaceHolder existed for the specified name [i.e. the logger
        didn't exist but a child of it did], replace it with the created
        logger and fix up the parent/child references which pointed to the
        placeholder to now point to the logger.
        """
        rv = None
        ikiwa not isinstance(name, str):
            raise TypeError('A logger name must be a string')
        _acquireLock()
        try:
            ikiwa name in self.loggerDict:
                rv = self.loggerDict[name]
                ikiwa isinstance(rv, PlaceHolder):
                    ph = rv
                    rv = (self.loggerClass or _loggerClass)(name)
                    rv.manager = self
                    self.loggerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            else:
                rv = (self.loggerClass or _loggerClass)(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupParents(rv)
        finally:
            _releaseLock()
        rudisha rv

    eleza setLoggerClass(self, klass):
        """
        Set the kundi to be used when instantiating a logger with this Manager.
        """
        ikiwa klass != Logger:
            ikiwa not issubclass(klass, Logger):
                raise TypeError("logger not derived kutoka logging.Logger: "
                                + klass.__name__)
        self.loggerClass = klass

    eleza setLogRecordFactory(self, factory):
        """
        Set the factory to be used when instantiating a log record with this
        Manager.
        """
        self.logRecordFactory = factory

    eleza _fixupParents(self, alogger):
        """
        Ensure that there are either loggers or placeholders all the way
        kutoka the specified logger to the root of the logger hierarchy.
        """
        name = alogger.name
        i = name.rfind(".")
        rv = None
        while (i > 0) and not rv:
            substr = name[:i]
            ikiwa substr not in self.loggerDict:
                self.loggerDict[substr] = PlaceHolder(alogger)
            else:
                obj = self.loggerDict[substr]
                ikiwa isinstance(obj, Logger):
                    rv = obj
                else:
                    assert isinstance(obj, PlaceHolder)
                    obj.append(alogger)
            i = name.rfind(".", 0, i - 1)
        ikiwa not rv:
            rv = self.root
        alogger.parent = rv

    eleza _fixupChildren(self, ph, alogger):
        """
        Ensure that children of the placeholder ph are connected to the
        specified logger.
        """
        name = alogger.name
        namelen = len(name)
        for c in ph.loggerMap.keys():
            #The ikiwa means ... ikiwa not c.parent.name.startswith(nm)
            ikiwa c.parent.name[:namelen] != name:
                alogger.parent = c.parent
                c.parent = alogger

    eleza _clear_cache(self):
        """
        Clear the cache for all loggers in loggerDict
        Called when level changes are made
        """

        _acquireLock()
        for logger in self.loggerDict.values():
            ikiwa isinstance(logger, Logger):
                logger._cache.clear()
        self.root._cache.clear()
        _releaseLock()

#---------------------------------------------------------------------------
#   Logger classes and functions
#---------------------------------------------------------------------------

kundi Logger(Filterer):
    """
    Instances of the Logger kundi represent a single logging channel. A
    "logging channel" indicates an area of an application. Exactly how an
    "area" is defined is up to the application developer. Since an
    application can have any number of areas, logging channels are identified
    by a unique string. Application areas can be nested (e.g. an area
    of "input processing" might include sub-areas "read CSV files", "read
    XLS files" and "read Gnumeric files"). To cater for this natural nesting,
    channel names are organized into a namespace hierarchy where levels are
    separated by periods, much like the Java or Python package namespace. So
    in the instance given above, channel names might be "input" for the upper
    level, and "input.csv", "input.xls" and "input.gnu" for the sub-levels.
    There is no arbitrary limit to the depth of nesting.
    """
    eleza __init__(self, name, level=NOTSET):
        """
        Initialize the logger with a name and an optional level.
        """
        Filterer.__init__(self)
        self.name = name
        self.level = _checkLevel(level)
        self.parent = None
        self.propagate = True
        self.handlers = []
        self.disabled = False
        self._cache = {}

    eleza setLevel(self, level):
        """
        Set the logging level of this logger.  level must be an int or a str.
        """
        self.level = _checkLevel(level)
        self.manager._clear_cache()

    eleza debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

    eleza info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

    eleza warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    eleza warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method is deprecated, "
            "use 'warning' instead", DeprecationWarning, 2)
        self.warning(msg, *args, **kwargs)

    eleza error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    eleza exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    eleza critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        ikiwa self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

    fatal = critical

    eleza log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        ikiwa not isinstance(level, int):
            ikiwa raiseExceptions:
                raise TypeError("level must be an integer")
            else:
                return
        ikiwa self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    eleza findCaller(self, stack_info=False, stacklevel=1):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        ikiwa f is not None:
            f = f.f_back
        orig_f = f
        while f and stacklevel > 1:
            f = f.f_back
            stacklevel -= 1
        ikiwa not f:
            f = orig_f
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            ikiwa filename == _srcfile:
                f = f.f_back
                continue
            sinfo = None
            ikiwa stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                ikiwa sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        rudisha rv

    eleza makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = _logRecordFactory(name, level, fn, lno, msg, args, exc_info, func,
                             sinfo)
        ikiwa extra is not None:
            for key in extra:
                ikiwa (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        rudisha rv

    eleza _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        sinfo = None
        ikiwa _srcfile:
            #IronPython doesn't track Python frames, so findCaller raises an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            try:
                fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
            except ValueError: # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else: # pragma: no cover
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        ikiwa exc_info:
            ikiwa isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elikiwa not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args,
                                 exc_info, func, extra, sinfo)
        self.handle(record)

    eleza handle(self, record):
        """
        Call the handlers for the specified record.

        This method is used for unpickled records received kutoka a socket, as
        well as those created locally. Logger-level filtering is applied.
        """
        ikiwa (not self.disabled) and self.filter(record):
            self.callHandlers(record)

    eleza addHandler(self, hdlr):
        """
        Add the specified handler to this logger.
        """
        _acquireLock()
        try:
            ikiwa not (hdlr in self.handlers):
                self.handlers.append(hdlr)
        finally:
            _releaseLock()

    eleza removeHandler(self, hdlr):
        """
        Remove the specified handler kutoka this logger.
        """
        _acquireLock()
        try:
            ikiwa hdlr in self.handlers:
                self.handlers.remove(hdlr)
        finally:
            _releaseLock()

    eleza hasHandlers(self):
        """
        See ikiwa this logger has any handlers configured.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. Return True ikiwa a handler was found, else False.
        Stop searching up the hierarchy whenever a logger with the "propagate"
        attribute set to zero is found - that will be the last logger which
        is checked for the existence of handlers.
        """
        c = self
        rv = False
        while c:
            ikiwa c.handlers:
                rv = True
                break
            ikiwa not c.propagate:
                break
            else:
                c = c.parent
        rudisha rv

    eleza callHandlers(self, record):
        """
        Pass a record to all relevant handlers.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger with the "propagate" attribute set to zero is found - that
        will be the last logger whose handlers are called.
        """
        c = self
        found = 0
        while c:
            for hdlr in c.handlers:
                found = found + 1
                ikiwa record.levelno >= hdlr.level:
                    hdlr.handle(record)
            ikiwa not c.propagate:
                c = None    #break out
            else:
                c = c.parent
        ikiwa (found == 0):
            ikiwa lastResort:
                ikiwa record.levelno >= lastResort.level:
                    lastResort.handle(record)
            elikiwa raiseExceptions and not self.manager.emittedNoHandlerWarning:
                sys.stderr.write("No handlers could be found for logger"
                                 " \"%s\"\n" % self.name)
                self.manager.emittedNoHandlerWarning = True

    eleza getEffectiveLevel(self):
        """
        Get the effective level for this logger.

        Loop through this logger and its parents in the logger hierarchy,
        looking for a non-zero logging level. Return the first one found.
        """
        logger = self
        while logger:
            ikiwa logger.level:
                rudisha logger.level
            logger = logger.parent
        rudisha NOTSET

    eleza isEnabledFor(self, level):
        """
        Is this logger enabled for level 'level'?
        """
        ikiwa self.disabled:
            rudisha False

        try:
            rudisha self._cache[level]
        except KeyError:
            _acquireLock()
            ikiwa self.manager.disable >= level:
                is_enabled = self._cache[level] = False
            else:
                is_enabled = self._cache[level] = level >= self.getEffectiveLevel()
            _releaseLock()

            rudisha is_enabled

    eleza getChild(self, suffix):
        """
        Get a logger which is a descendant to this one.

        This is a convenience method, such that

        logging.getLogger('abc').getChild('def.ghi')

        is the same as

        logging.getLogger('abc.def.ghi')

        It's useful, for example, when the parent logger is named using
        __name__ rather than a literal string.
        """
        ikiwa self.root is not self:
            suffix = '.'.join((self.name, suffix))
        rudisha self.manager.getLogger(suffix)

    eleza __repr__(self):
        level = getLevelName(self.getEffectiveLevel())
        rudisha '<%s %s (%s)>' % (self.__class__.__name__, self.name, level)

    eleza __reduce__(self):
        # In general, only the root logger will not be accessible via its name.
        # However, the root logger's kundi has its own __reduce__ method.
        ikiwa getLogger(self.name) is not self:
            agiza pickle
            raise pickle.PicklingError('logger cannot be pickled')
        rudisha getLogger, (self.name,)


kundi RootLogger(Logger):
    """
    A root logger is not that different to any other logger, except that
    it must have a logging level and there is only one instance of it in
    the hierarchy.
    """
    eleza __init__(self, level):
        """
        Initialize the logger with the name "root".
        """
        Logger.__init__(self, "root", level)

    eleza __reduce__(self):
        rudisha getLogger, ()

_loggerClass = Logger

kundi LoggerAdapter(object):
    """
    An adapter for loggers which makes it easier to specify contextual
    information in logging output.
    """

    eleza __init__(self, logger, extra):
        """
        Initialize the adapter with a logger and a dict-like object which
        provides contextual information. This constructor signature allows
        easy stacking of LoggerAdapters, ikiwa so desired.

        You can effectively pass keyword arguments as shown in the
        following example:

        adapter = LoggerAdapter(someLogger, dict(p1=v1, p2="v2"))
        """
        self.logger = logger
        self.extra = extra

    eleza process(self, msg, kwargs):
        """
        Process the logging message and keyword arguments passed in to
        a logging call to insert contextual information. You can either
        manipulate the message itself, the keyword args or both. Return
        the message and kwargs modified (or not) to suit your needs.

        Normally, you'll only need to override this one method in a
        LoggerAdapter subkundi for your specific needs.
        """
        kwargs["extra"] = self.extra
        rudisha msg, kwargs

    #
    # Boilerplate convenience methods
    #
    eleza debug(self, msg, *args, **kwargs):
        """
        Delegate a debug call to the underlying logger.
        """
        self.log(DEBUG, msg, *args, **kwargs)

    eleza info(self, msg, *args, **kwargs):
        """
        Delegate an info call to the underlying logger.
        """
        self.log(INFO, msg, *args, **kwargs)

    eleza warning(self, msg, *args, **kwargs):
        """
        Delegate a warning call to the underlying logger.
        """
        self.log(WARNING, msg, *args, **kwargs)

    eleza warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method is deprecated, "
            "use 'warning' instead", DeprecationWarning, 2)
        self.warning(msg, *args, **kwargs)

    eleza error(self, msg, *args, **kwargs):
        """
        Delegate an error call to the underlying logger.
        """
        self.log(ERROR, msg, *args, **kwargs)

    eleza exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Delegate an exception call to the underlying logger.
        """
        self.log(ERROR, msg, *args, exc_info=exc_info, **kwargs)

    eleza critical(self, msg, *args, **kwargs):
        """
        Delegate a critical call to the underlying logger.
        """
        self.log(CRITICAL, msg, *args, **kwargs)

    eleza log(self, level, msg, *args, **kwargs):
        """
        Delegate a log call to the underlying logger, after adding
        contextual information kutoka this adapter instance.
        """
        ikiwa self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger.log(level, msg, *args, **kwargs)

    eleza isEnabledFor(self, level):
        """
        Is this logger enabled for level 'level'?
        """
        rudisha self.logger.isEnabledFor(level)

    eleza setLevel(self, level):
        """
        Set the specified level on the underlying logger.
        """
        self.logger.setLevel(level)

    eleza getEffectiveLevel(self):
        """
        Get the effective level for the underlying logger.
        """
        rudisha self.logger.getEffectiveLevel()

    eleza hasHandlers(self):
        """
        See ikiwa the underlying logger has any handlers.
        """
        rudisha self.logger.hasHandlers()

    eleza _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        """
        Low-level log implementation, proxied to allow nested logger adapters.
        """
        rudisha self.logger._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
        )

    @property
    eleza manager(self):
        rudisha self.logger.manager

    @manager.setter
    eleza manager(self, value):
        self.logger.manager = value

    @property
    eleza name(self):
        rudisha self.logger.name

    eleza __repr__(self):
        logger = self.logger
        level = getLevelName(logger.getEffectiveLevel())
        rudisha '<%s %s (%s)>' % (self.__class__.__name__, logger.name, level)

root = RootLogger(WARNING)
Logger.root = root
Logger.manager = Manager(Logger.root)

#---------------------------------------------------------------------------
# Configuration classes and functions
#---------------------------------------------------------------------------

eleza basicConfig(**kwargs):
    """
    Do basic configuration for the logging system.

    This function does nothing ikiwa the root logger already has handlers
    configured, unless the keyword argument *force* is set to ``True``.
    It is a convenience method intended for use by simple scripts
    to do one-shot configuration of the logging package.

    The default behaviour is to create a StreamHandler which writes to
    sys.stderr, set a formatter using the BASIC_FORMAT format string, and
    add the handler to the root logger.

    A number of optional keyword arguments may be specified, which can alter
    the default behaviour.

    filename  Specifies that a FileHandler be created, using the specified
              filename, rather than a StreamHandler.
    filemode  Specifies the mode to open the file, ikiwa filename is specified
              (ikiwa filemode is unspecified, it defaults to 'a').
    format    Use the specified format string for the handler.
    datefmt   Use the specified date/time format.
    style     If a format string is specified, use this to specify the
              type of format string (possible values '%', '{', '$', for
              %-formatting, :meth:`str.format` and :class:`string.Template`
              - defaults to '%').
    level     Set the root logger level to the specified level.
    stream    Use the specified stream to initialize the StreamHandler. Note
              that this argument is incompatible with 'filename' - ikiwa both
              are present, 'stream' is ignored.
    handlers  If specified, this should be an iterable of already created
              handlers, which will be added to the root handler. Any handler
              in the list which does not have a formatter assigned will be
              assigned the formatter created in this function.
    force     If this keyword  is specified as true, any existing handlers
              attached to the root logger are removed and closed, before
              carrying out the configuration as specified by the other
              arguments.
    Note that you could specify a stream created using open(filename, mode)
    rather than passing the filename and mode in. However, it should be
    remembered that StreamHandler does not close its stream (since it may be
    using sys.stdout or sys.stderr), whereas FileHandler closes its stream
    when the handler is closed.

    .. versionchanged:: 3.8
       Added the ``force`` parameter.

    .. versionchanged:: 3.2
       Added the ``style`` parameter.

    .. versionchanged:: 3.3
       Added the ``handlers`` parameter. A ``ValueError`` is now thrown for
       incompatible arguments (e.g. ``handlers`` specified together with
       ``filename``/``filemode``, or ``filename``/``filemode`` specified
       together with ``stream``, or ``handlers`` specified together with
       ``stream``.
    """
    # Add thread safety in case someone mistakenly calls
    # basicConfig() kutoka multiple threads
    _acquireLock()
    try:
        force = kwargs.pop('force', False)
        ikiwa force:
            for h in root.handlers[:]:
                root.removeHandler(h)
                h.close()
        ikiwa len(root.handlers) == 0:
            handlers = kwargs.pop("handlers", None)
            ikiwa handlers is None:
                ikiwa "stream" in kwargs and "filename" in kwargs:
                    raise ValueError("'stream' and 'filename' should not be "
                                     "specified together")
            else:
                ikiwa "stream" in kwargs or "filename" in kwargs:
                    raise ValueError("'stream' or 'filename' should not be "
                                     "specified together with 'handlers'")
            ikiwa handlers is None:
                filename = kwargs.pop("filename", None)
                mode = kwargs.pop("filemode", 'a')
                ikiwa filename:
                    h = FileHandler(filename, mode)
                else:
                    stream = kwargs.pop("stream", None)
                    h = StreamHandler(stream)
                handlers = [h]
            dfs = kwargs.pop("datefmt", None)
            style = kwargs.pop("style", '%')
            ikiwa style not in _STYLES:
                raise ValueError('Style must be one of: %s' % ','.join(
                                 _STYLES.keys()))
            fs = kwargs.pop("format", _STYLES[style][1])
            fmt = Formatter(fs, dfs, style)
            for h in handlers:
                ikiwa h.formatter is None:
                    h.setFormatter(fmt)
                root.addHandler(h)
            level = kwargs.pop("level", None)
            ikiwa level is not None:
                root.setLevel(level)
            ikiwa kwargs:
                keys = ', '.join(kwargs.keys())
                raise ValueError('Unrecognised argument(s): %s' % keys)
    finally:
        _releaseLock()

#---------------------------------------------------------------------------
# Utility functions at module level.
# Basically delegate everything to the root logger.
#---------------------------------------------------------------------------

eleza getLogger(name=None):
    """
    Return a logger with the specified name, creating it ikiwa necessary.

    If no name is specified, rudisha the root logger.
    """
    ikiwa name:
        rudisha Logger.manager.getLogger(name)
    else:
        rudisha root

eleza critical(msg, *args, **kwargs):
    """
    Log a message with severity 'CRITICAL' on the root logger. If the logger
    has no handlers, call basicConfig() to add a console handler with a
    pre-defined format.
    """
    ikiwa len(root.handlers) == 0:
        basicConfig()
    root.critical(msg, *args, **kwargs)

fatal = critical

eleza error(msg, *args, **kwargs):
    """
    Log a message with severity 'ERROR' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    ikiwa len(root.handlers) == 0:
        basicConfig()
    root.error(msg, *args, **kwargs)

eleza exception(msg, *args, exc_info=True, **kwargs):
    """
    Log a message with severity 'ERROR' on the root logger, with exception
    information. If the logger has no handlers, basicConfig() is called to add
    a console handler with a pre-defined format.
    """
    error(msg, *args, exc_info=exc_info, **kwargs)

eleza warning(msg, *args, **kwargs):
    """
    Log a message with severity 'WARNING' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    ikiwa len(root.handlers) == 0:
        basicConfig()
    root.warning(msg, *args, **kwargs)

eleza warn(msg, *args, **kwargs):
    warnings.warn("The 'warn' function is deprecated, "
        "use 'warning' instead", DeprecationWarning, 2)
    warning(msg, *args, **kwargs)

eleza info(msg, *args, **kwargs):
    """
    Log a message with severity 'INFO' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    ikiwa len(root.handlers) == 0:
        basicConfig()
    root.info(msg, *args, **kwargs)

eleza debug(msg, *args, **kwargs):
    """
    Log a message with severity 'DEBUG' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    ikiwa len(root.handlers) == 0:
        basicConfig()
    root.debug(msg, *args, **kwargs)

eleza log(level, msg, *args, **kwargs):
    """
    Log 'msg % args' with the integer severity 'level' on the root logger. If
    the logger has no handlers, call basicConfig() to add a console handler
    with a pre-defined format.
    """
    ikiwa len(root.handlers) == 0:
        basicConfig()
    root.log(level, msg, *args, **kwargs)

eleza disable(level=CRITICAL):
    """
    Disable all logging calls of severity 'level' and below.
    """
    root.manager.disable = level
    root.manager._clear_cache()

eleza shutdown(handlerList=_handlerList):
    """
    Perform any cleanup actions in the logging system (e.g. flushing
    buffers).

    Should be called at application exit.
    """
    for wr in reversed(handlerList[:]):
        #errors might occur, for example, ikiwa files are locked
        #we just ignore them ikiwa raiseExceptions is not set
        try:
            h = wr()
            ikiwa h:
                try:
                    h.acquire()
                    h.flush()
                    h.close()
                except (OSError, ValueError):
                    # Ignore errors which might be caused
                    # because handlers have been closed but
                    # references to them are still around at
                    # application exit.
                    pass
                finally:
                    h.release()
        except: # ignore everything, as we're shutting down
            ikiwa raiseExceptions:
                raise
            #else, swallow

#Let's try and shutdown automatically on application exit...
agiza atexit
atexit.register(shutdown)

# Null handler

kundi NullHandler(Handler):
    """
    This handler does nothing. It's intended to be used to avoid the
    "No handlers could be found for logger XXX" one-off warning. This is
    agizaant for library code, which may contain code to log events. If a user
    of the library does not configure logging, the one-off warning might be
    produced; to avoid this, the library developer simply needs to instantiate
    a NullHandler and add it to the top-level logger of the library module or
    package.
    """
    eleza handle(self, record):
        """Stub."""

    eleza emit(self, record):
        """Stub."""

    eleza createLock(self):
        self.lock = None

# Warnings integration

_warnings_showwarning = None

eleza _showwarning(message, category, filename, lineno, file=None, line=None):
    """
    Implementation of showwarnings which redirects to logging, which will first
    check to see ikiwa the file parameter is None. If a file is specified, it will
    delegate to the original warnings implementation of showwarning. Otherwise,
    it will call warnings.formatwarning and will log the resulting string to a
    warnings logger named "py.warnings" with level logging.WARNING.
    """
    ikiwa file is not None:
        ikiwa _warnings_showwarning is not None:
            _warnings_showwarning(message, category, filename, lineno, file, line)
    else:
        s = warnings.formatwarning(message, category, filename, lineno, line)
        logger = getLogger("py.warnings")
        ikiwa not logger.handlers:
            logger.addHandler(NullHandler())
        logger.warning("%s", s)

eleza captureWarnings(capture):
    """
    If capture is true, redirect all warnings to the logging package.
    If capture is False, ensure that warnings are not redirected to logging
    but to their original destinations.
    """
    global _warnings_showwarning
    ikiwa capture:
        ikiwa _warnings_showwarning is None:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = _showwarning
    else:
        ikiwa _warnings_showwarning is not None:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = None
