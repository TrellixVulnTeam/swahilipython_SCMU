"""A simple log mechanism styled after PEP 282."""

# The kundi here ni styled after PEP 282 so that it could later be
# replaced ukijumuisha a standard Python logging implementation.

DEBUG = 1
INFO = 2
WARN = 3
ERROR = 4
FATAL = 5

agiza sys

kundi Log:

    eleza __init__(self, threshold=WARN):
        self.threshold = threshold

    eleza _log(self, level, msg, args):
        ikiwa level haiko kwenye (DEBUG, INFO, WARN, ERROR, FATAL):
            ashiria ValueError('%s wrong log level' % str(level))

        ikiwa level >= self.threshold:
            ikiwa args:
                msg = msg % args
            ikiwa level kwenye (WARN, ERROR, FATAL):
                stream = sys.stderr
            isipokua:
                stream = sys.stdout
            jaribu:
                stream.write('%s\n' % msg)
            tatizo UnicodeEncodeError:
                # emulate backslashreplace error handler
                encoding = stream.encoding
                msg = msg.encode(encoding, "backslashreplace").decode(encoding)
                stream.write('%s\n' % msg)
            stream.flush()

    eleza log(self, level, msg, *args):
        self._log(level, msg, args)

    eleza debug(self, msg, *args):
        self._log(DEBUG, msg, args)

    eleza info(self, msg, *args):
        self._log(INFO, msg, args)

    eleza warn(self, msg, *args):
        self._log(WARN, msg, args)

    eleza error(self, msg, *args):
        self._log(ERROR, msg, args)

    eleza fatal(self, msg, *args):
        self._log(FATAL, msg, args)

_global_log = Log()
log = _global_log.log
debug = _global_log.debug
info = _global_log.info
warn = _global_log.warn
error = _global_log.error
fatal = _global_log.fatal

eleza set_threshold(level):
    # rudisha the old threshold kila use kutoka tests
    old = _global_log.threshold
    _global_log.threshold = level
    rudisha old

eleza set_verbosity(v):
    ikiwa v <= 0:
        set_threshold(WARN)
    lasivyo v == 1:
        set_threshold(INFO)
    lasivyo v >= 2:
        set_threshold(DEBUG)
