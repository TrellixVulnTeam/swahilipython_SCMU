# Copyright 2001-2017 by Vinay Sajip. All Rights Reserved.
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
Logging package kila Python. Based on PEP 282 na comments thereto in
comp.lang.python.

Copyright (C) 2001-2017 Vinay Sajip. All Rights Reserved.

To use, simply 'agiza logging' na log away!
"""

agiza sys, os, time, io, re, traceback, warnings, weakref, collections.abc

kutoka string agiza Template
kutoka string agiza Formatter kama StrFormatter


__all__ = ['BASIC_FORMAT', 'BufferingFormatter', 'CRITICAL', 'DEBUG', 'ERROR',
           'FATAL', 'FileHandler', 'Filter', 'Formatter', 'Handler', 'INFO',
           'LogRecord', 'Logger', 'LoggerAdapter', 'NOTSET', 'NullHandler',
           'StreamHandler', 'WARN', 'WARNING', 'addLevelName', 'basicConfig',
           'captureWarnings', 'critical', 'debug', 'disable', 'error',
           'exception', 'fatal', 'getLevelName', 'getLogger', 'getLoggerClass',
           'info', 'log', 'makeLogRecord', 'setLoggerClass', 'shutdown',
           'warn', 'warning', 'getLogRecordFactory', 'setLogRecordFactory',
           'lastResort', 'ashiriaExceptions']

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
#_startTime ni used kama the base when calculating the relative time of events
#
_startTime = time.time()

#
#ashiriaExceptions ni used to see ikiwa exceptions during handling should be
#propagated
#
ashiriaExceptions = Kweli

#
# If you don't want threading information kwenye the log, set this to zero
#
logThreads = Kweli

#
# If you don't want multiprocessing information kwenye the log, set this to zero
#
logMultiprocessing = Kweli

#
# If you don't want process information kwenye the log, set this to zero
#
logProcesses = Kweli

#---------------------------------------------------------------------------
#   Level related stuff
#---------------------------------------------------------------------------
#
# Default levels na level names, these can be replaced with any positive set
# of values having corresponding names. There ni a pseudo-level, NOTSET, which
# ni only really there kama a lower limit kila user-defined levels. Handlers and
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

    If the level ni one of the predefined levels (CRITICAL, ERROR, WARNING,
    INFO, DEBUG) then you get the corresponding string. If you have
    associated levels with names using addLevelName then the name you have
    associated with 'level' ni rudishaed.

    If a numeric value corresponding to one of the defined levels ni pitaed
    in, the corresponding string representation ni rudishaed.

    Otherwise, the string "Level %s" % level ni rudishaed.
    """
    # See Issues #22386, #27937 na #29220 kila why it's this way
    result = _levelToName.get(level)
    ikiwa result ni sio Tupu:
        rudisha result
    result = _nameToLevel.get(level)
    ikiwa result ni sio Tupu:
        rudisha result
    rudisha "Level %s" % level

eleza addLevelName(level, levelName):
    """
    Associate 'levelName' with 'level'.

    This ni used when converting levels to text during message formatting.
    """
    _acquireLock()
    jaribu:    #unlikely to cause an exception, but you never know...
        _levelToName[level] = levelName
        _nameToLevel[levelName] = level
    mwishowe:
        _releaseLock()

ikiwa hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
isipokua: #pragma: no cover
    eleza currentframe():
        """Return the frame object kila the caller's stack frame."""
        jaribu:
            ashiria Exception
        tatizo Exception:
            rudisha sys.exc_info()[2].tb_frame.f_back

#
# _srcfile ni used when walking the stack to check when we've got the first
# caller stack frame, by skipping frames whose filename ni that of this
# module's source. It therefore should contain the filename of this module's
# source file.
#
# Ordinarily we would use __file__ kila this, but frozen modules don't always
# have __file__ set, kila some reason (see Issue #21736). Thus, we get the
# filename kutoka a handy code object kutoka a function defined kwenye this module.
# (There's no particular reason kila picking addLevelName.)
#

_srcfile = os.path.normcase(addLevelName.__code__.co_filename)

# _srcfile ni only used kwenye conjunction with sys._getframe().
# To provide compatibility with older versions of Python, set _srcfile
# to Tupu ikiwa _getframe() ni sio available; this value will prevent
# findCaller() kutoka being called. You can also do this ikiwa you want to avoid
# the overhead of fetching caller information, even when _getframe() is
# available.
#ikiwa sio hasattr(sys, '_getframe'):
#    _srcfile = Tupu


eleza _checkLevel(level):
    ikiwa isinstance(level, int):
        rv = level
    elikiwa str(level) == level:
        ikiwa level haiko kwenye _nameToLevel:
            ashiria ValueError("Unknown level: %r" % level)
        rv = _nameToLevel[level]
    isipokua:
        ashiria TypeError("Level sio an integer ama a valid string: %r" % level)
    rudisha rv

#---------------------------------------------------------------------------
#   Thread-related stuff
#---------------------------------------------------------------------------

#
#_lock ni used to serialize access to shared data structures kwenye this module.
#This needs to be an RLock because fileConfig() creates na configures
#Handlers, na so might arbitrary user threads. Since Handler code updates the
#shared dictionary _handlers, it needs to acquire the lock. But ikiwa configuring,
#the lock would already have been acquired - so we need an RLock.
#The same argument applies to Loggers na Manager.loggerDict.
#
_lock = threading.RLock()

eleza _acquireLock():
    """
    Acquire the module-level lock kila serializing access to shared data.

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

ikiwa sio hasattr(os, 'register_at_fork'):  # Windows na friends.
    eleza _register_at_fork_reinit_lock(instance):
        pita  # no-op when os.register_at_fork does sio exist.
isipokua:
    # A collection of instances with a createLock method (logging.Handler)
    # to be called kwenye the child after forking.  The weakref avoids us keeping
    # discarded Handler instances alive.  A set ni used to avoid accumulating
    # duplicate registrations kama createLock() ni responsible kila registering
    # a new Handler instance with this set kwenye the first place.
    _at_fork_reinit_lock_weakset = weakref.WeakSet()

    eleza _register_at_fork_reinit_lock(instance):
        _acquireLock()
        jaribu:
            _at_fork_reinit_lock_weakset.add(instance)
        mwishowe:
            _releaseLock()

    eleza _after_at_fork_child_reinit_locks():
        # _acquireLock() was called kwenye the parent before forking.
        kila handler kwenye _at_fork_reinit_lock_weakset:
            jaribu:
                handler.createLock()
            tatizo Exception kama err:
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

    LogRecord instances are created every time something ni logged. They
    contain all the information pertinent to the event being logged. The
    main information pitaed kwenye ni kwenye msg na args, which are combined
    using str(msg) % args to create the message field of the record. The
    record also includes information such kama when the record was created,
    the source line where the logging call was made, na any exception
    information to be logged.
    """
    eleza __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=Tupu, sinfo=Tupu, **kwargs):
        """
        Initialize a logging record with interesting information.
        """
        ct = time.time()
        self.name = name
        self.msg = msg
        #
        # The following statement allows pitaing of a dictionary kama a sole
        # argument, so that you can do something like
        #  logging.debug("a %(a)d b %(b)s", {'a':1, 'b':2})
        # Suggested by Stefan Behnel.
        # Note that without the test kila args[0], we get a problem because
        # during formatting, we test to see ikiwa the arg ni present using
        # 'ikiwa self.args:'. If the event being logged ni e.g. 'Value ni %d'
        # na ikiwa the pitaed arg fails 'ikiwa self.args:' then no formatting
        # ni done. For example, logger.warning('Value ni %d', 0) would log
        # 'Value ni %d' instead of 'Value ni 0'.
        # For the use case of pitaing a dictionary, this should sio be a
        # problem.
        # Issue #21172: a request was made to relax the isinstance check
        # to hasattr(args[0], '__getitem__'). However, the docs on string
        # formatting still seem to suggest a mapping object ni required.
        # Thus, wakati sio removing the isinstance check, it does now look
        # kila collections.abc.Mapping rather than, kama before, dict.
        ikiwa (args na len(args) == 1 na isinstance(args[0], collections.abc.Mapping)
            na args[0]):
            args = args[0]
        self.args = args
        self.levelname = getLevelName(level)
        self.levelno = level
        self.pathname = pathname
        jaribu:
            self.filename = os.path.basename(pathname)
            self.module = os.path.splitext(self.filename)[0]
        tatizo (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = "Unknown module"
        self.exc_info = exc_info
        self.exc_text = Tupu      # used to cache the traceback text
        self.stack_info = sinfo
        self.lineno = lineno
        self.funcName = func
        self.created = ct
        self.msecs = (ct - int(ct)) * 1000
        self.relativeCreated = (self.created - _startTime) * 1000
        ikiwa logThreads:
            self.thread = threading.get_ident()
            self.threadName = threading.current_thread().name
        isipokua: # pragma: no cover
            self.thread = Tupu
            self.threadName = Tupu
        ikiwa sio logMultiprocessing: # pragma: no cover
            self.processName = Tupu
        isipokua:
            self.processName = 'MainProcess'
            mp = sys.modules.get('multiprocessing')
            ikiwa mp ni sio Tupu:
                # Errors may occur ikiwa multiprocessing has sio finished loading
                # yet - e.g. ikiwa a custom agiza hook causes third-party code
                # to run when multiprocessing calls agiza. See issue 8200
                # kila an example
                jaribu:
                    self.processName = mp.current_process().name
                tatizo Exception: #pragma: no cover
                    pita
        ikiwa logProcesses na hasattr(os, 'getpid'):
            self.process = os.getpid()
        isipokua:
            self.process = Tupu

    eleza __repr__(self):
        rudisha '<LogRecord: %s, %s, %s, %s, "%s">'%(self.name, self.levelno,
            self.pathname, self.lineno, self.msg)

    eleza getMessage(self):
        """
        Return the message kila this LogRecord.

        Return the message kila this LogRecord after merging any user-supplied
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
    This function ni useful kila converting a logging event received over
    a socket connection (which ni sent kama a dictionary) into a LogRecord
    instance.
    """
    rv = _logRecordFactory(Tupu, Tupu, "", 0, "", (), Tupu, Tupu)
    rv.__dict__.update(dict)
    rudisha rv


#---------------------------------------------------------------------------
#   Formatter classes na functions
#---------------------------------------------------------------------------
_str_formatter = StrFormatter()
toa StrFormatter


kundi PercentStyle(object):

    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'
    validation_pattern = re.compile(r'%\(\w+\)[#0+ -]*(\*|\d+)?(\.(\*|\d+))?[diouxefgcrsa%]', re.I)

    eleza __init__(self, fmt):
        self._fmt = fmt ama self.default_format

    eleza usesTime(self):
        rudisha self._fmt.find(self.asctime_search) >= 0

    eleza validate(self):
        """Validate the input format, ensure it matches the correct style"""
        ikiwa sio self.validation_pattern.search(self._fmt):
            ashiria ValueError("Invalid format '%s' kila '%s' style" % (self._fmt, self.default_format[0]))

    eleza _format(self, record):
        rudisha self._fmt % record.__dict__

    eleza format(self, record):
        jaribu:
            rudisha self._format(record)
        tatizo KeyError kama e:
            ashiria ValueError('Formatting field sio found kwenye record: %s' % e)


kundi StrFormatStyle(PercentStyle):
    default_format = '{message}'
    asctime_format = '{asctime}'
    asctime_search = '{asctime'

    fmt_spec = re.compile(r'^(.?[<>=^])?[+ -]?#?0?(\d+|{\w+})?[,_]?(\.(\d+|{\w+}))?[bcdefgnosx%]?$', re.I)
    field_spec = re.compile(r'^(\d+|\w+)(\.\w+|\[[^]]+\])*$')

    eleza _format(self, record):
        rudisha self._fmt.format(**record.__dict__)

    eleza validate(self):
        """Validate the input format, ensure it ni the correct string formatting style"""
        fields = set()
        jaribu:
            kila _, fieldname, spec, conversion kwenye _str_formatter.parse(self._fmt):
                ikiwa fieldname:
                    ikiwa sio self.field_spec.match(fieldname):
                        ashiria ValueError('invalid field name/expression: %r' % fieldname)
                    fields.add(fieldname)
                ikiwa conversion na conversion haiko kwenye 'rsa':
                    ashiria ValueError('invalid conversion: %r' % conversion)
                ikiwa spec na sio self.fmt_spec.match(spec):
                    ashiria ValueError('bad specifier: %r' % spec)
        tatizo ValueError kama e:
            ashiria ValueError('invalid format: %s' % e)
        ikiwa sio fields:
            ashiria ValueError('invalid format: no fields')


kundi StringTemplateStyle(PercentStyle):
    default_format = '${message}'
    asctime_format = '${asctime}'
    asctime_search = '${asctime}'

    eleza __init__(self, fmt):
        self._fmt = fmt ama self.default_format
        self._tpl = Template(self._fmt)

    eleza usesTime(self):
        fmt = self._fmt
        rudisha fmt.find('$asctime') >= 0 ama fmt.find(self.asctime_format) >= 0

    eleza validate(self):
        pattern = Template.pattern
        fields = set()
        kila m kwenye pattern.finditer(self._fmt):
            d = m.groupdict()
            ikiwa d['named']:
                fields.add(d['named'])
            elikiwa d['braced']:
                fields.add(d['braced'])
            elikiwa m.group(0) == '$':
                ashiria ValueError('invalid format: bare \'$\' sio allowed')
        ikiwa sio fields:
            ashiria ValueError('invalid format: no fields')

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

    Formatters need to know how a LogRecord ni constructed. They are
    responsible kila converting a LogRecord to (usually) a string which can
    be interpreted by either a human ama an external system. The base Formatter
    allows a formatting string to be specified. If none ni supplied, the
    the style-dependent default value, "%(message)s", "{message}", or
    "${message}", ni used.

    The Formatter can be initialized with a format string which makes use of
    knowledge of the LogRecord attributes - e.g. the default value mentioned
    above makes use of the fact that the user's message na arguments are pre-
    formatted into a LogRecord's message attribute. Currently, the useful
    attributes kwenye a LogRecord are described by:

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level kila the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level kila the message ("DEBUG", "INFO",
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
    %(relativeCreated)d Time kwenye milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (ikiwa available)
    %(threadName)s      Thread name (ikiwa available)
    %(process)d         Process ID (ikiwa available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record ni emitted
    """

    converter = time.localtime

    eleza __init__(self, fmt=Tupu, datefmt=Tupu, style='%', validate=Kweli):
        """
        Initialize the formatter with specified format strings.

        Initialize the formatter either with the specified format string, ama a
        default kama described above. Allow kila specialized date formatting with
        the optional datefmt argument. If datefmt ni omitted, you get an
        ISO8601-like (or RFC 3339-like) format.

        Use a style parameter of '%', '{' ama '$' to specify that you want to
        use one of %-formatting, :meth:`str.format` (``{}``) formatting or
        :class:`string.Template` formatting kwenye your format string.

        .. versionchanged:: 3.2
           Added the ``style`` parameter.
        """
        ikiwa style haiko kwenye _STYLES:
            ashiria ValueError('Style must be one of: %s' % ','.join(
                             _STYLES.keys()))
        self._style = _STYLES[style][0](fmt)
        ikiwa validate:
            self._style.validate()

        self._fmt = self._style._fmt
        self.datefmt = datefmt

    default_time_format = '%Y-%m-%d %H:%M:%S'
    default_msec_format = '%s,%03d'

    eleza formatTime(self, record, datefmt=Tupu):
        """
        Return the creation time of the specified LogRecord kama formatted text.

        This method should be called kutoka format() by a formatter which
        wants to make use of a formatted time. This method can be overridden
        kwenye formatters to provide kila any specific requirement, but the
        basic behaviour ni kama follows: ikiwa datefmt (a string) ni specified,
        it ni used with time.strftime() to format the creation time of the
        record. Otherwise, an ISO8601-like (or RFC 3339-like) format ni used.
        The resulting string ni rudishaed. This function uses a user-configurable
        function to convert the creation time to a tuple. By default,
        time.localtime() ni used; to change this kila a particular formatter
        instance, set the 'converter' attribute to a function with the same
        signature kama time.localtime() ama time.gmtime(). To change it kila all
        formatters, kila example ikiwa you want all logging times to be shown kwenye GMT,
        set the 'converter' attribute kwenye the Formatter class.
        """
        ct = self.converter(record.created)
        ikiwa datefmt:
            s = time.strftime(datefmt, ct)
        isipokua:
            t = time.strftime(self.default_time_format, ct)
            s = self.default_msec_format % (t, record.msecs)
        rudisha s

    eleza formatException(self, ei):
        """
        Format na rudisha the specified exception information kama a string.

        This default implementation just uses
        traceback.print_exception()
        """
        sio = io.StringIO()
        tb = ei[2]
        # See issues #9427, #1553375. Commented out kila now.
        #ikiwa getattr(self, 'fullstack', Uongo):
        #    traceback.print_stack(tb.tb_frame.f_back, file=sio)
        traceback.print_exception(ei[0], ei[1], tb, Tupu, sio)
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
        This method ni provided kama an extension point kila specialized
        formatting of stack information.

        The input data ni a string kama rudishaed kutoka a call to
        :func:`traceback.print_stack`, but with the last trailing newline
        removed.

        The base implementation just rudishas the value pitaed in.
        """
        rudisha stack_info

    eleza format(self, record):
        """
        Format the specified record kama text.

        The record's attribute dictionary ni used kama the operand to a
        string formatting operation which tumas the rudishaed string.
        Before formatting the dictionary, a couple of preparatory steps
        are carried out. The message attribute of the record ni computed
        using LogRecord.getMessage(). If the formatting string uses the
        time (as determined by a call to usesTime(), formatTime() is
        called to format the event time. If there ni exception information,
        it ni formatted using formatException() na appended to the message.
        """
        record.message = record.getMessage()
        ikiwa self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        ikiwa record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            ikiwa sio record.exc_text:
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
#   The default formatter to use when no other ni specified
#
_defaultFormatter = Formatter()

kundi BufferingFormatter(object):
    """
    A formatter suitable kila formatting a number of records.
    """
    eleza __init__(self, linefmt=Tupu):
        """
        Optionally specify a formatter which will be used to format each
        individual record.
        """
        ikiwa linefmt:
            self.linefmt = linefmt
        isipokua:
            self.linefmt = _defaultFormatter

    eleza formatHeader(self, records):
        """
        Return the header string kila the specified records.
        """
        rudisha ""

    eleza formatFooter(self, records):
        """
        Return the footer string kila the specified records.
        """
        rudisha ""

    eleza format(self, records):
        """
        Format the specified records na rudisha the result kama a string.
        """
        rv = ""
        ikiwa len(records) > 0:
            rv = rv + self.formatHeader(records)
            kila record kwenye records:
                rv = rv + self.linefmt.format(record)
            rv = rv + self.formatFooter(records)
        rudisha rv

#---------------------------------------------------------------------------
#   Filter classes na functions
#---------------------------------------------------------------------------

kundi Filter(object):
    """
    Filter instances are used to perform arbitrary filtering of LogRecords.

    Loggers na Handlers can optionally use Filter instances to filter
    records kama desired. The base filter kundi only allows events which are
    below a certain point kwenye the logger hierarchy. For example, a filter
    initialized with "A.B" will allow events logged by loggers "A.B",
    "A.B.C", "A.B.C.D", "A.B.D" etc. but sio "A.BB", "B.A.B" etc. If
    initialized with the empty string, all events are pitaed.
    """
    eleza __init__(self, name=''):
        """
        Initialize a filter.

        Initialize with the name of the logger which, together with its
        children, will have its events allowed through the filter. If no
        name ni specified, allow every event.
        """
        self.name = name
        self.nlen = len(name)

    eleza filter(self, record):
        """
        Determine ikiwa the specified record ni to be logged.

        Is the specified record to be logged? Returns 0 kila no, nonzero for
        yes. If deemed appropriate, the record may be modified in-place.
        """
        ikiwa self.nlen == 0:
            rudisha Kweli
        elikiwa self.name == record.name:
            rudisha Kweli
        elikiwa record.name.find(self.name, 0, self.nlen) != 0:
            rudisha Uongo
        rudisha (record.name[self.nlen] == ".")

kundi Filterer(object):
    """
    A base kundi kila loggers na handlers which allows them to share
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
        ikiwa sio (filter kwenye self.filters):
            self.filters.append(filter)

    eleza removeFilter(self, filter):
        """
        Remove the specified filter kutoka this handler.
        """
        ikiwa filter kwenye self.filters:
            self.filters.remove(filter)

    eleza filter(self, record):
        """
        Determine ikiwa a record ni loggable by consulting all the filters.

        The default ni to allow the record to be logged; any filter can veto
        this na the record ni then dropped. Returns a zero value ikiwa a record
        ni to be dropped, else non-zero.

        .. versionchanged:: 3.2

           Allow filters to be just callables.
        """
        rv = Kweli
        kila f kwenye self.filters:
            ikiwa hasattr(f, 'filter'):
                result = f.filter(record)
            isipokua:
                result = f(record) # assume callable - will ashiria ikiwa not
            ikiwa sio result:
                rv = Uongo
                koma
        rudisha rv

#---------------------------------------------------------------------------
#   Handler classes na functions
#---------------------------------------------------------------------------

_handlers = weakref.WeakValueDictionary()  #map of handler names to handlers
_handlerList = [] # added to allow handlers to be removed kwenye reverse of order initialized

eleza _removeHandlerRef(wr):
    """
    Remove a handler reference kutoka the internal cleanup list.
    """
    # This function can be called during module teardown, when globals are
    # set to Tupu. It can also be called kutoka another thread. So we need to
    # pre-emptively grab the necessary globals na check ikiwa they're Tupu,
    # to prevent race conditions na failures during interpreter shutdown.
    acquire, release, handlers = _acquireLock, _releaseLock, _handlerList
    ikiwa acquire na release na handlers:
        acquire()
        jaribu:
            ikiwa wr kwenye handlers:
                handlers.remove(wr)
        mwishowe:
            release()

eleza _addHandlerRef(handler):
    """
    Add a handler to the internal cleanup list using a weak reference.
    """
    _acquireLock()
    jaribu:
        _handlerList.append(weakref.ref(handler, _removeHandlerRef))
    mwishowe:
        _releaseLock()

kundi Handler(Filterer):
    """
    Handler instances dispatch logging events to specific destinations.

    The base handler class. Acts kama a placeholder which defines the Handler
    interface. Handlers can optionally use Formatter instances to format
    records kama desired. By default, no formatter ni specified; kwenye this case,
    the 'raw' message kama determined by record.message ni logged.
    """
    eleza __init__(self, level=NOTSET):
        """
        Initializes the instance - basically setting the formatter to Tupu
        na the filter list to empty.
        """
        Filterer.__init__(self)
        self._name = Tupu
        self.level = _checkLevel(level)
        self.formatter = Tupu
        # Add the handler to the global _handlerList (kila cleanup on shutdown)
        _addHandlerRef(self)
        self.createLock()

    eleza get_name(self):
        rudisha self._name

    eleza set_name(self, name):
        _acquireLock()
        jaribu:
            ikiwa self._name kwenye _handlers:
                toa _handlers[self._name]
            self._name = name
            ikiwa name:
                _handlers[name] = self
        mwishowe:
            _releaseLock()

    name = property(get_name, set_name)

    eleza createLock(self):
        """
        Acquire a thread lock kila serializing access to the underlying I/O.
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
        Set the logging level of this handler.  level must be an int ama a str.
        """
        self.level = _checkLevel(level)

    eleza format(self, record):
        """
        Format the specified record.

        If a formatter ni set, use it. Otherwise, use the default formatter
        kila the module.
        """
        ikiwa self.formatter:
            fmt = self.formatter
        isipokua:
            fmt = _defaultFormatter
        rudisha fmt.format(record)

    eleza emit(self, record):
        """
        Do whatever it takes to actually log the specified logging record.

        This version ni intended to be implemented by subclasses na so
        ashirias a NotImplementedError.
        """
        ashiria NotImplementedError('emit must be implemented '
                                  'by Handler subclasses')

    eleza handle(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record with acquisition/release of
        the I/O thread lock. Returns whether the filter pitaed the record for
        emission.
        """
        rv = self.filter(record)
        ikiwa rv:
            self.acquire()
            jaribu:
                self.emit(record)
            mwishowe:
                self.release()
        rudisha rv

    eleza setFormatter(self, fmt):
        """
        Set the formatter kila this handler.
        """
        self.formatter = fmt

    eleza flush(self):
        """
        Ensure all logging output has been flushed.

        This version does nothing na ni intended to be implemented by
        subclasses.
        """
        pita

    eleza close(self):
        """
        Tidy up any resources used by the handler.

        This version removes the handler kutoka an internal map of handlers,
        _handlers, which ni used kila handler lookup by name. Subclasses
        should ensure that this gets called kutoka overridden close()
        methods.
        """
        #get the module data lock, kama we're updating a shared structure.
        _acquireLock()
        jaribu:    #unlikely to ashiria an exception, but you never know...
            ikiwa self._name na self._name kwenye _handlers:
                toa _handlers[self._name]
        mwishowe:
            _releaseLock()

    eleza handleError(self, record):
        """
        Handle errors which occur during an emit() call.

        This method should be called kutoka handlers when an exception is
        encountered during an emit() call. If ashiriaExceptions ni false,
        exceptions get silently ignored. This ni what ni mostly wanted
        kila a logging system - most users will sio care about errors in
        the logging system, they are more interested kwenye application errors.
        You could, however, replace this with a custom handler ikiwa you wish.
        The record which was being processed ni pitaed kwenye to this method.
        """
        ikiwa ashiriaExceptions na sys.stderr:  # see issue 13807
            t, v, tb = sys.exc_info()
            jaribu:
                sys.stderr.write('--- Logging error ---\n')
                traceback.print_exception(t, v, tb, Tupu, sys.stderr)
                sys.stderr.write('Call stack:\n')
                # Walk the stack frame up until we're out of logging,
                # so kama to print the calling context.
                frame = tb.tb_frame
                wakati (frame na os.path.dirname(frame.f_code.co_filename) ==
                       __path__[0]):
                    frame = frame.f_back
                ikiwa frame:
                    traceback.print_stack(frame, file=sys.stderr)
                isipokua:
                    # couldn't find the right stack frame, kila some reason
                    sys.stderr.write('Logged kutoka file %s, line %s\n' % (
                                     record.filename, record.lineno))
                # Issue 18671: output logging message na arguments
                jaribu:
                    sys.stderr.write('Message: %r\n'
                                     'Arguments: %s\n' % (record.msg,
                                                          record.args))
                tatizo RecursionError:  # See issue 36272
                    ashiria
                tatizo Exception:
                    sys.stderr.write('Unable to print the message na arguments'
                                     ' - possible formatting error.\nUse the'
                                     ' traceback above to help find the error.\n'
                                    )
            tatizo OSError: #pragma: no cover
                pita    # see issue 5971
            mwishowe:
                toa t, v, tb

    eleza __repr__(self):
        level = getLevelName(self.level)
        rudisha '<%s (%s)>' % (self.__class__.__name__, level)

kundi StreamHandler(Handler):
    """
    A handler kundi which writes logging records, appropriately formatted,
    to a stream. Note that this kundi does sio close the stream, as
    sys.stdout ama sys.stderr may be used.
    """

    terminator = '\n'

    eleza __init__(self, stream=Tupu):
        """
        Initialize the handler.

        If stream ni sio specified, sys.stderr ni used.
        """
        Handler.__init__(self)
        ikiwa stream ni Tupu:
            stream = sys.stderr
        self.stream = stream

    eleza flush(self):
        """
        Flushes the stream.
        """
        self.acquire()
        jaribu:
            ikiwa self.stream na hasattr(self.stream, "flush"):
                self.stream.flush()
        mwishowe:
            self.release()

    eleza emit(self, record):
        """
        Emit a record.

        If a formatter ni specified, it ni used to format the record.
        The record ni then written to the stream with a trailing newline.  If
        exception information ni present, it ni formatted using
        traceback.print_exception na appended to the stream.  If the stream
        has an 'encoding' attribute, it ni used to determine how to do the
        output to the stream.
        """
        jaribu:
            msg = self.format(record)
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)
            self.flush()
        tatizo RecursionError:  # See issue 36272
            ashiria
        tatizo Exception:
            self.handleError(record)

    eleza setStream(self, stream):
        """
        Sets the StreamHandler's stream to the specified value,
        ikiwa it ni different.

        Returns the old stream, ikiwa the stream was changed, ama Tupu
        ikiwa it wasn't.
        """
        ikiwa stream ni self.stream:
            result = Tupu
        isipokua:
            result = self.stream
            self.acquire()
            jaribu:
                self.flush()
                self.stream = stream
            mwishowe:
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
    eleza __init__(self, filename, mode='a', encoding=Tupu, delay=Uongo):
        """
        Open the specified file na use it kama the stream kila logging.
        """
        # Issue #27493: add support kila Path objects to be pitaed in
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
            self.stream = Tupu
        isipokua:
            StreamHandler.__init__(self, self._open())

    eleza close(self):
        """
        Closes the stream.
        """
        self.acquire()
        jaribu:
            jaribu:
                ikiwa self.stream:
                    jaribu:
                        self.flush()
                    mwishowe:
                        stream = self.stream
                        self.stream = Tupu
                        ikiwa hasattr(stream, "close"):
                            stream.close()
            mwishowe:
                # Issue #19523: call unconditionally to
                # prevent a handler leak when delay ni set
                StreamHandler.close(self)
        mwishowe:
            self.release()

    eleza _open(self):
        """
        Open the current base file with the (original) mode na encoding.
        Return the resulting stream.
        """
        rudisha open(self.baseFilename, self.mode, encoding=self.encoding)

    eleza emit(self, record):
        """
        Emit a record.

        If the stream was sio opened because 'delay' was specified kwenye the
        constructor, open it before calling the superclass's emit.
        """
        ikiwa self.stream ni Tupu:
            self.stream = self._open()
        StreamHandler.emit(self, record)

    eleza __repr__(self):
        level = getLevelName(self.level)
        rudisha '<%s %s (%s)>' % (self.__class__.__name__, self.baseFilename, level)


kundi _StderrHandler(StreamHandler):
    """
    This kundi ni like a StreamHandler using sys.stderr, but always uses
    whatever sys.stderr ni currently set to rather than the value of
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
#   Manager classes na functions
#---------------------------------------------------------------------------

kundi PlaceHolder(object):
    """
    PlaceHolder instances are used kwenye the Manager logger hierarchy to take
    the place of nodes kila which no loggers have been defined. This kundi is
    intended kila internal use only na sio kama part of the public API.
    """
    eleza __init__(self, alogger):
        """
        Initialize with the specified logger being a child of this placeholder.
        """
        self.loggerMap = { alogger : Tupu }

    eleza append(self, alogger):
        """
        Add the specified logger kama a child of this placeholder.
        """
        ikiwa alogger haiko kwenye self.loggerMap:
            self.loggerMap[alogger] = Tupu

#
#   Determine which kundi to use when instantiating loggers.
#

eleza setLoggerClass(klass):
    """
    Set the kundi to be used when instantiating a logger. The kundi should
    define __init__() such that only a name argument ni required, na the
    __init__() should call Logger.__init__()
    """
    ikiwa klass != Logger:
        ikiwa sio issubclass(klass, Logger):
            ashiria TypeError("logger sio derived kutoka logging.Logger: "
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
    There ni [under normal circumstances] just one Manager instance, which
    holds the hierarchy of loggers.
    """
    eleza __init__(self, rootnode):
        """
        Initialize the manager with the root node of the logger hierarchy.
        """
        self.root = rootnode
        self.disable = 0
        self.emittedNoHandlerWarning = Uongo
        self.loggerDict = {}
        self.loggerClass = Tupu
        self.logRecordFactory = Tupu

    eleza getLogger(self, name):
        """
        Get a logger with the specified name (channel name), creating it
        ikiwa it doesn't yet exist. This name ni a dot-separated hierarchical
        name, such kama "a", "a.b", "a.b.c" ama similar.

        If a PlaceHolder existed kila the specified name [i.e. the logger
        didn't exist but a child of it did], replace it with the created
        logger na fix up the parent/child references which pointed to the
        placeholder to now point to the logger.
        """
        rv = Tupu
        ikiwa sio isinstance(name, str):
            ashiria TypeError('A logger name must be a string')
        _acquireLock()
        jaribu:
            ikiwa name kwenye self.loggerDict:
                rv = self.loggerDict[name]
                ikiwa isinstance(rv, PlaceHolder):
                    ph = rv
                    rv = (self.loggerClass ama _loggerClass)(name)
                    rv.manager = self
                    self.loggerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            isipokua:
                rv = (self.loggerClass ama _loggerClass)(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupParents(rv)
        mwishowe:
            _releaseLock()
        rudisha rv

    eleza setLoggerClass(self, klass):
        """
        Set the kundi to be used when instantiating a logger with this Manager.
        """
        ikiwa klass != Logger:
            ikiwa sio issubclass(klass, Logger):
                ashiria TypeError("logger sio derived kutoka logging.Logger: "
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
        Ensure that there are either loggers ama placeholders all the way
        kutoka the specified logger to the root of the logger hierarchy.
        """
        name = alogger.name
        i = name.rfind(".")
        rv = Tupu
        wakati (i > 0) na sio rv:
            substr = name[:i]
            ikiwa substr haiko kwenye self.loggerDict:
                self.loggerDict[substr] = PlaceHolder(alogger)
            isipokua:
                obj = self.loggerDict[substr]
                ikiwa isinstance(obj, Logger):
                    rv = obj
                isipokua:
                    assert isinstance(obj, PlaceHolder)
                    obj.append(alogger)
            i = name.rfind(".", 0, i - 1)
        ikiwa sio rv:
            rv = self.root
        alogger.parent = rv

    eleza _fixupChildren(self, ph, alogger):
        """
        Ensure that children of the placeholder ph are connected to the
        specified logger.
        """
        name = alogger.name
        namelen = len(name)
        kila c kwenye ph.loggerMap.keys():
            #The ikiwa means ... ikiwa sio c.parent.name.startswith(nm)
            ikiwa c.parent.name[:namelen] != name:
                alogger.parent = c.parent
                c.parent = alogger

    eleza _clear_cache(self):
        """
        Clear the cache kila all loggers kwenye loggerDict
        Called when level changes are made
        """

        _acquireLock()
        kila logger kwenye self.loggerDict.values():
            ikiwa isinstance(logger, Logger):
                logger._cache.clear()
        self.root._cache.clear()
        _releaseLock()

#---------------------------------------------------------------------------
#   Logger classes na functions
#---------------------------------------------------------------------------

kundi Logger(Filterer):
    """
    Instances of the Logger kundi represent a single logging channel. A
    "logging channel" indicates an area of an application. Exactly how an
    "area" ni defined ni up to the application developer. Since an
    application can have any number of areas, logging channels are identified
    by a unique string. Application areas can be nested (e.g. an area
    of "input processing" might include sub-areas "read CSV files", "read
    XLS files" na "read Gnumeric files"). To cater kila this natural nesting,
    channel names are organized into a namespace hierarchy where levels are
    separated by periods, much like the Java ama Python package namespace. So
    kwenye the instance given above, channel names might be "input" kila the upper
    level, na "input.csv", "input.xls" na "input.gnu" kila the sub-levels.
    There ni no arbitrary limit to the depth of nesting.
    """
    eleza __init__(self, name, level=NOTSET):
        """
        Initialize the logger with a name na an optional level.
        """
        Filterer.__init__(self)
        self.name = name
        self.level = _checkLevel(level)
        self.parent = Tupu
        self.propagate = Kweli
        self.handlers = []
        self.disabled = Uongo
        self._cache = {}

    eleza setLevel(self, level):
        """
        Set the logging level of this logger.  level must be an int ama a str.
        """
        self.level = _checkLevel(level)
        self.manager._clear_cache()

    eleza debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pita exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

    eleza info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pita exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

    eleza warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pita exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    eleza warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method ni deprecated, "
            "use 'warning' instead", DeprecationWarning, 2)
        self.warning(msg, *args, **kwargs)

    eleza error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pita exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        ikiwa self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    eleza exception(self, msg, *args, exc_info=Kweli, **kwargs):
        """
        Convenience method kila logging an ERROR with exception information.
        """
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    eleza critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pita exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        ikiwa self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

    fatal = critical

    eleza log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pita exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        ikiwa sio isinstance(level, int):
            ikiwa ashiriaExceptions:
                ashiria TypeError("level must be an integer")
            isipokua:
                rudisha
        ikiwa self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    eleza findCaller(self, stack_info=Uongo, stacklevel=1):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number na function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() rudishas Tupu if
        #IronPython isn't run with -X:Frames.
        ikiwa f ni sio Tupu:
            f = f.f_back
        orig_f = f
        wakati f na stacklevel > 1:
            f = f.f_back
            stacklevel -= 1
        ikiwa sio f:
            f = orig_f
        rv = "(unknown file)", 0, "(unknown function)", Tupu
        wakati hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            ikiwa filename == _srcfile:
                f = f.f_back
                endelea
            sinfo = Tupu
            ikiwa stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                ikiwa sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            koma
        rudisha rv

    eleza makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=Tupu, extra=Tupu, sinfo=Tupu):
        """
        A factory method which can be overridden kwenye subclasses to create
        specialized LogRecords.
        """
        rv = _logRecordFactory(name, level, fn, lno, msg, args, exc_info, func,
                             sinfo)
        ikiwa extra ni sio Tupu:
            kila key kwenye extra:
                ikiwa (key kwenye ["message", "asctime"]) ama (key kwenye rv.__dict__):
                    ashiria KeyError("Attempt to overwrite %r kwenye LogRecord" % key)
                rv.__dict__[key] = extra[key]
        rudisha rv

    eleza _log(self, level, msg, args, exc_info=Tupu, extra=Tupu, stack_info=Uongo,
             stacklevel=1):
        """
        Low-level logging routine which creates a LogRecord na then calls
        all the handlers of this logger to handle the record.
        """
        sinfo = Tupu
        ikiwa _srcfile:
            #IronPython doesn't track Python frames, so findCaller ashirias an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            jaribu:
                fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
            tatizo ValueError: # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        isipokua: # pragma: no cover
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        ikiwa exc_info:
            ikiwa isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elikiwa sio isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args,
                                 exc_info, func, extra, sinfo)
        self.handle(record)

    eleza handle(self, record):
        """
        Call the handlers kila the specified record.

        This method ni used kila unpickled records received kutoka a socket, as
        well kama those created locally. Logger-level filtering ni applied.
        """
        ikiwa (not self.disabled) na self.filter(record):
            self.callHandlers(record)

    eleza addHandler(self, hdlr):
        """
        Add the specified handler to this logger.
        """
        _acquireLock()
        jaribu:
            ikiwa sio (hdlr kwenye self.handlers):
                self.handlers.append(hdlr)
        mwishowe:
            _releaseLock()

    eleza removeHandler(self, hdlr):
        """
        Remove the specified handler kutoka this logger.
        """
        _acquireLock()
        jaribu:
            ikiwa hdlr kwenye self.handlers:
                self.handlers.remove(hdlr)
        mwishowe:
            _releaseLock()

    eleza hasHandlers(self):
        """
        See ikiwa this logger has any handlers configured.

        Loop through all handlers kila this logger na its parents kwenye the
        logger hierarchy. Return Kweli ikiwa a handler was found, else Uongo.
        Stop searching up the hierarchy whenever a logger with the "propagate"
        attribute set to zero ni found - that will be the last logger which
        ni checked kila the existence of handlers.
        """
        c = self
        rv = Uongo
        wakati c:
            ikiwa c.handlers:
                rv = Kweli
                koma
            ikiwa sio c.propagate:
                koma
            isipokua:
                c = c.parent
        rudisha rv

    eleza callHandlers(self, record):
        """
        Pass a record to all relevant handlers.

        Loop through all handlers kila this logger na its parents kwenye the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger with the "propagate" attribute set to zero ni found - that
        will be the last logger whose handlers are called.
        """
        c = self
        found = 0
        wakati c:
            kila hdlr kwenye c.handlers:
                found = found + 1
                ikiwa record.levelno >= hdlr.level:
                    hdlr.handle(record)
            ikiwa sio c.propagate:
                c = Tupu    #koma out
            isipokua:
                c = c.parent
        ikiwa (found == 0):
            ikiwa lastResort:
                ikiwa record.levelno >= lastResort.level:
                    lastResort.handle(record)
            elikiwa ashiriaExceptions na sio self.manager.emittedNoHandlerWarning:
                sys.stderr.write("No handlers could be found kila logger"
                                 " \"%s\"\n" % self.name)
                self.manager.emittedNoHandlerWarning = Kweli

    eleza getEffectiveLevel(self):
        """
        Get the effective level kila this logger.

        Loop through this logger na its parents kwenye the logger hierarchy,
        looking kila a non-zero logging level. Return the first one found.
        """
        logger = self
        wakati logger:
            ikiwa logger.level:
                rudisha logger.level
            logger = logger.parent
        rudisha NOTSET

    eleza isEnabledFor(self, level):
        """
        Is this logger enabled kila level 'level'?
        """
        ikiwa self.disabled:
            rudisha Uongo

        jaribu:
            rudisha self._cache[level]
        tatizo KeyError:
            _acquireLock()
            ikiwa self.manager.disable >= level:
                is_enabled = self._cache[level] = Uongo
            isipokua:
                is_enabled = self._cache[level] = level >= self.getEffectiveLevel()
            _releaseLock()

            rudisha is_enabled

    eleza getChild(self, suffix):
        """
        Get a logger which ni a descendant to this one.

        This ni a convenience method, such that

        logging.getLogger('abc').getChild('def.ghi')

        ni the same as

        logging.getLogger('abc.def.ghi')

        It's useful, kila example, when the parent logger ni named using
        __name__ rather than a literal string.
        """
        ikiwa self.root ni sio self:
            suffix = '.'.join((self.name, suffix))
        rudisha self.manager.getLogger(suffix)

    eleza __repr__(self):
        level = getLevelName(self.getEffectiveLevel())
        rudisha '<%s %s (%s)>' % (self.__class__.__name__, self.name, level)

    eleza __reduce__(self):
        # In general, only the root logger will sio be accessible via its name.
        # However, the root logger's kundi has its own __reduce__ method.
        ikiwa getLogger(self.name) ni sio self:
            agiza pickle
            ashiria pickle.PicklingError('logger cannot be pickled')
        rudisha getLogger, (self.name,)


kundi RootLogger(Logger):
    """
    A root logger ni sio that different to any other logger, tatizo that
    it must have a logging level na there ni only one instance of it in
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
    An adapter kila loggers which makes it easier to specify contextual
    information kwenye logging output.
    """

    eleza __init__(self, logger, extra):
        """
        Initialize the adapter with a logger na a dict-like object which
        provides contextual information. This constructor signature allows
        easy stacking of LoggerAdapters, ikiwa so desired.

        You can effectively pita keyword arguments kama shown kwenye the
        following example:

        adapter = LoggerAdapter(someLogger, dict(p1=v1, p2="v2"))
        """
        self.logger = logger
        self.extra = extra

    eleza process(self, msg, kwargs):
        """
        Process the logging message na keyword arguments pitaed kwenye to
        a logging call to insert contextual information. You can either
        manipulate the message itself, the keyword args ama both. Return
        the message na kwargs modified (or not) to suit your needs.

        Normally, you'll only need to override this one method kwenye a
        LoggerAdapter subkundi kila your specific needs.
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
        warnings.warn("The 'warn' method ni deprecated, "
            "use 'warning' instead", DeprecationWarning, 2)
        self.warning(msg, *args, **kwargs)

    eleza error(self, msg, *args, **kwargs):
        """
        Delegate an error call to the underlying logger.
        """
        self.log(ERROR, msg, *args, **kwargs)

    eleza exception(self, msg, *args, exc_info=Kweli, **kwargs):
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
        Is this logger enabled kila level 'level'?
        """
        rudisha self.logger.isEnabledFor(level)

    eleza setLevel(self, level):
        """
        Set the specified level on the underlying logger.
        """
        self.logger.setLevel(level)

    eleza getEffectiveLevel(self):
        """
        Get the effective level kila the underlying logger.
        """
        rudisha self.logger.getEffectiveLevel()

    eleza hasHandlers(self):
        """
        See ikiwa the underlying logger has any handlers.
        """
        rudisha self.logger.hasHandlers()

    eleza _log(self, level, msg, args, exc_info=Tupu, extra=Tupu, stack_info=Uongo):
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
# Configuration classes na functions
#---------------------------------------------------------------------------

eleza basicConfig(**kwargs):
    """
    Do basic configuration kila the logging system.

    This function does nothing ikiwa the root logger already has handlers
    configured, unless the keyword argument *force* ni set to ``Kweli``.
    It ni a convenience method intended kila use by simple scripts
    to do one-shot configuration of the logging package.

    The default behaviour ni to create a StreamHandler which writes to
    sys.stderr, set a formatter using the BASIC_FORMAT format string, and
    add the handler to the root logger.

    A number of optional keyword arguments may be specified, which can alter
    the default behaviour.

    filename  Specifies that a FileHandler be created, using the specified
              filename, rather than a StreamHandler.
    filemode  Specifies the mode to open the file, ikiwa filename ni specified
              (ikiwa filemode ni unspecified, it defaults to 'a').
    format    Use the specified format string kila the handler.
    datefmt   Use the specified date/time format.
    style     If a format string ni specified, use this to specify the
              type of format string (possible values '%', '{', '$', for
              %-formatting, :meth:`str.format` na :class:`string.Template`
              - defaults to '%').
    level     Set the root logger level to the specified level.
    stream    Use the specified stream to initialize the StreamHandler. Note
              that this argument ni incompatible with 'filename' - ikiwa both
              are present, 'stream' ni ignored.
    handlers  If specified, this should be an iterable of already created
              handlers, which will be added to the root handler. Any handler
              kwenye the list which does sio have a formatter assigned will be
              assigned the formatter created kwenye this function.
    force     If this keyword  ni specified kama true, any existing handlers
              attached to the root logger are removed na closed, before
              carrying out the configuration kama specified by the other
              arguments.
    Note that you could specify a stream created using open(filename, mode)
    rather than pitaing the filename na mode in. However, it should be
    remembered that StreamHandler does sio close its stream (since it may be
    using sys.stdout ama sys.stderr), whereas FileHandler closes its stream
    when the handler ni closed.

    .. versionchanged:: 3.8
       Added the ``force`` parameter.

    .. versionchanged:: 3.2
       Added the ``style`` parameter.

    .. versionchanged:: 3.3
       Added the ``handlers`` parameter. A ``ValueError`` ni now thrown for
       incompatible arguments (e.g. ``handlers`` specified together with
       ``filename``/``filemode``, ama ``filename``/``filemode`` specified
       together with ``stream``, ama ``handlers`` specified together with
       ``stream``.
    """
    # Add thread safety kwenye case someone mistakenly calls
    # basicConfig() kutoka multiple threads
    _acquireLock()
    jaribu:
        force = kwargs.pop('force', Uongo)
        ikiwa force:
            kila h kwenye root.handlers[:]:
                root.removeHandler(h)
                h.close()
        ikiwa len(root.handlers) == 0:
            handlers = kwargs.pop("handlers", Tupu)
            ikiwa handlers ni Tupu:
                ikiwa "stream" kwenye kwargs na "filename" kwenye kwargs:
                    ashiria ValueError("'stream' na 'filename' should sio be "
                                     "specified together")
            isipokua:
                ikiwa "stream" kwenye kwargs ama "filename" kwenye kwargs:
                    ashiria ValueError("'stream' ama 'filename' should sio be "
                                     "specified together with 'handlers'")
            ikiwa handlers ni Tupu:
                filename = kwargs.pop("filename", Tupu)
                mode = kwargs.pop("filemode", 'a')
                ikiwa filename:
                    h = FileHandler(filename, mode)
                isipokua:
                    stream = kwargs.pop("stream", Tupu)
                    h = StreamHandler(stream)
                handlers = [h]
            dfs = kwargs.pop("datefmt", Tupu)
            style = kwargs.pop("style", '%')
            ikiwa style haiko kwenye _STYLES:
                ashiria ValueError('Style must be one of: %s' % ','.join(
                                 _STYLES.keys()))
            fs = kwargs.pop("format", _STYLES[style][1])
            fmt = Formatter(fs, dfs, style)
            kila h kwenye handlers:
                ikiwa h.formatter ni Tupu:
                    h.setFormatter(fmt)
                root.addHandler(h)
            level = kwargs.pop("level", Tupu)
            ikiwa level ni sio Tupu:
                root.setLevel(level)
            ikiwa kwargs:
                keys = ', '.join(kwargs.keys())
                ashiria ValueError('Unrecognised argument(s): %s' % keys)
    mwishowe:
        _releaseLock()

#---------------------------------------------------------------------------
# Utility functions at module level.
# Basically delegate everything to the root logger.
#---------------------------------------------------------------------------

eleza getLogger(name=Tupu):
    """
    Return a logger with the specified name, creating it ikiwa necessary.

    If no name ni specified, rudisha the root logger.
    """
    ikiwa name:
        rudisha Logger.manager.getLogger(name)
    isipokua:
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

eleza exception(msg, *args, exc_info=Kweli, **kwargs):
    """
    Log a message with severity 'ERROR' on the root logger, with exception
    information. If the logger has no handlers, basicConfig() ni called to add
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
    warnings.warn("The 'warn' function ni deprecated, "
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
    Disable all logging calls of severity 'level' na below.
    """
    root.manager.disable = level
    root.manager._clear_cache()

eleza shutdown(handlerList=_handlerList):
    """
    Perform any cleanup actions kwenye the logging system (e.g. flushing
    buffers).

    Should be called at application exit.
    """
    kila wr kwenye reversed(handlerList[:]):
        #errors might occur, kila example, ikiwa files are locked
        #we just ignore them ikiwa ashiriaExceptions ni sio set
        jaribu:
            h = wr()
            ikiwa h:
                jaribu:
                    h.acquire()
                    h.flush()
                    h.close()
                tatizo (OSError, ValueError):
                    # Ignore errors which might be caused
                    # because handlers have been closed but
                    # references to them are still around at
                    # application exit.
                    pita
                mwishowe:
                    h.release()
        except: # ignore everything, kama we're shutting down
            ikiwa ashiriaExceptions:
                ashiria
            #else, swallow

#Let's try na shutdown automatically on application exit...
agiza atexit
atexit.register(shutdown)

# Null handler

kundi NullHandler(Handler):
    """
    This handler does nothing. It's intended to be used to avoid the
    "No handlers could be found kila logger XXX" one-off warning. This is
    agizaant kila library code, which may contain code to log events. If a user
    of the library does sio configure logging, the one-off warning might be
    produced; to avoid this, the library developer simply needs to instantiate
    a NullHandler na add it to the top-level logger of the library module or
    package.
    """
    eleza handle(self, record):
        """Stub."""

    eleza emit(self, record):
        """Stub."""

    eleza createLock(self):
        self.lock = Tupu

# Warnings integration

_warnings_showwarning = Tupu

eleza _showwarning(message, category, filename, lineno, file=Tupu, line=Tupu):
    """
    Implementation of showwarnings which redirects to logging, which will first
    check to see ikiwa the file parameter ni Tupu. If a file ni specified, it will
    delegate to the original warnings implementation of showwarning. Otherwise,
    it will call warnings.formatwarning na will log the resulting string to a
    warnings logger named "py.warnings" with level logging.WARNING.
    """
    ikiwa file ni sio Tupu:
        ikiwa _warnings_showwarning ni sio Tupu:
            _warnings_showwarning(message, category, filename, lineno, file, line)
    isipokua:
        s = warnings.formatwarning(message, category, filename, lineno, line)
        logger = getLogger("py.warnings")
        ikiwa sio logger.handlers:
            logger.addHandler(NullHandler())
        logger.warning("%s", s)

eleza captureWarnings(capture):
    """
    If capture ni true, redirect all warnings to the logging package.
    If capture ni Uongo, ensure that warnings are sio redirected to logging
    but to their original destinations.
    """
    global _warnings_showwarning
    ikiwa capture:
        ikiwa _warnings_showwarning ni Tupu:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = _showwarning
    isipokua:
        ikiwa _warnings_showwarning ni sio Tupu:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = Tupu
