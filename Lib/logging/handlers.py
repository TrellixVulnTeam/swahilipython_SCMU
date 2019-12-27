# Copyright 2001-2016 by Vinay Sajip. All Rights Reserved.
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
Additional handlers for the logging package for Python. The core package is
based on PEP 282 and comments thereto in comp.lang.python.

Copyright (C) 2001-2016 Vinay Sajip. All Rights Reserved.

To use, simply 'agiza logging.handlers' and log away!
"""

agiza logging, socket, os, pickle, struct, time, re
kutoka stat agiza ST_DEV, ST_INO, ST_MTIME
agiza queue
agiza threading
agiza copy

#
# Some constants...
#

DEFAULT_TCP_LOGGING_PORT    = 9020
DEFAULT_UDP_LOGGING_PORT    = 9021
DEFAULT_HTTP_LOGGING_PORT   = 9022
DEFAULT_SOAP_LOGGING_PORT   = 9023
SYSLOG_UDP_PORT             = 514
SYSLOG_TCP_PORT             = 514

_MIDNIGHT = 24 * 60 * 60  # number of seconds in a day

kundi BaseRotatingHandler(logging.FileHandler):
    """
    Base kundi for handlers that rotate log files at a certain point.
    Not meant to be instantiated directly.  Instead, use RotatingFileHandler
    or TimedRotatingFileHandler.
    """
    eleza __init__(self, filename, mode, encoding=None, delay=False):
        """
        Use the specified filename for streamed logging
        """
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.mode = mode
        self.encoding = encoding
        self.namer = None
        self.rotator = None

    eleza emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            ikiwa self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        except Exception:
            self.handleError(record)

    eleza rotation_filename(self, default_name):
        """
        Modify the filename of a log file when rotating.

        This is provided so that a custom filename can be provided.

        The default implementation calls the 'namer' attribute of the
        handler, ikiwa it's callable, passing the default name to
        it. If the attribute isn't callable (the default is None), the name
        is returned unchanged.

        :param default_name: The default name for the log file.
        """
        ikiwa not callable(self.namer):
            result = default_name
        else:
            result = self.namer(default_name)
        rudisha result

    eleza rotate(self, source, dest):
        """
        When rotating, rotate the current log.

        The default implementation calls the 'rotator' attribute of the
        handler, ikiwa it's callable, passing the source and dest arguments to
        it. If the attribute isn't callable (the default is None), the source
        is simply renamed to the destination.

        :param source: The source filename. This is normally the base
                       filename, e.g. 'test.log'
        :param dest:   The destination filename. This is normally
                       what the source is rotated to, e.g. 'test.log.1'.
        """
        ikiwa not callable(self.rotator):
            # Issue 18940: A file may not have been created ikiwa delay is True.
            ikiwa os.path.exists(source):
                os.rename(source, dest)
        else:
            self.rotator(source, dest)

kundi RotatingFileHandler(BaseRotatingHandler):
    """
    Handler for logging to a set of files, which switches kutoka one file
    to the next when the current file reaches a certain size.
    """
    eleza __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        """
        Open the specified file and use it as the stream for logging.

        By default, the file grows indefinitely. You can specify particular
        values of maxBytes and backupCount to allow the file to rollover at
        a predetermined size.

        Rollover occurs whenever the current log file is nearly maxBytes in
        length. If backupCount is >= 1, the system will successively create
        new files with the same pathname as the base file, but with extensions
        ".1", ".2" etc. appended to it. For example, with a backupCount of 5
        and a base file name of "app.log", you would get "app.log",
        "app.log.1", "app.log.2", ... through to "app.log.5". The file being
        written to is always "app.log" - when it gets filled up, it is closed
        and renamed to "app.log.1", and ikiwa files "app.log.1", "app.log.2" etc.
        exist, then they are renamed to "app.log.2", "app.log.3" etc.
        respectively.

        If maxBytes is zero, rollover never occurs.
        """
        # If rotation/rollover is wanted, it doesn't make sense to use another
        # mode. If for example 'w' were specified, then ikiwa there were multiple
        # runs of the calling application, the logs kutoka previous runs would be
        # lost ikiwa the 'w' is respected, because the log file would be truncated
        # on each run.
        ikiwa maxBytes > 0:
            mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    eleza doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        ikiwa self.stream:
            self.stream.close()
            self.stream = None
        ikiwa self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" % (self.baseFilename,
                                                        i + 1))
                ikiwa os.path.exists(sfn):
                    ikiwa os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            ikiwa os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        ikiwa not self.delay:
            self.stream = self._open()

    eleza shouldRollover(self, record):
        """
        Determine ikiwa rollover should occur.

        Basically, see ikiwa the supplied record would cause the file to exceed
        the size limit we have.
        """
        ikiwa self.stream is None:                 # delay was set...
            self.stream = self._open()
        ikiwa self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            ikiwa self.stream.tell() + len(msg) >= self.maxBytes:
                rudisha 1
        rudisha 0

kundi TimedRotatingFileHandler(BaseRotatingHandler):
    """
    Handler for logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount is > 0, when rollover is done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """
    eleza __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)
        self.when = when.upper()
        self.backupCount = backupCount
        self.utc = utc
        self.atTime = atTime
        # Calculate the real rollover interval, which is just the number of
        # seconds between rollovers.  Also set the filename suffix used when
        # a rollover occurs.  Current 'when' events supported:
        # S - Seconds
        # M - Minutes
        # H - Hours
        # D - Days
        # midnight - roll over at midnight
        # W{0-6} - roll over on a certain day; 0 - Monday
        #
        # Case of the 'when' specifier is not agizaant; lower or upper case
        # will work.
        ikiwa self.when == 'S':
            self.interval = 1 # one second
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.\w+)?$"
        elikiwa self.when == 'M':
            self.interval = 60 # one minute
            self.suffix = "%Y-%m-%d_%H-%M"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}(\.\w+)?$"
        elikiwa self.when == 'H':
            self.interval = 60 * 60 # one hour
            self.suffix = "%Y-%m-%d_%H"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}(\.\w+)?$"
        elikiwa self.when == 'D' or self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24 # one day
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        elikiwa self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7 # one week
            ikiwa len(self.when) != 2:
                raise ValueError("You must specify a day for weekly rollover kutoka 0 to 6 (0 is Monday): %s" % self.when)
            ikiwa self.when[1] < '0' or self.when[1] > '6':
                raise ValueError("Invalid day specified for weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)

        self.extMatch = re.compile(self.extMatch, re.ASCII)
        self.interval = self.interval * interval # multiply by units requested
        # The following line added because the filename passed in could be a
        # path object (see Issue #27493), but self.baseFilename will be a string
        filename = self.baseFilename
        ikiwa os.path.exists(filename):
            t = os.stat(filename)[ST_MTIME]
        else:
            t = int(time.time())
        self.rolloverAt = self.computeRollover(t)

    eleza computeRollover(self, currentTime):
        """
        Work out the rollover time based on the specified time.
        """
        result = currentTime + self.interval
        # If we are rolling over at midnight or weekly, then the interval is already known.
        # What we need to figure out is WHEN the next interval is.  In other words,
        # ikiwa you are rolling over at midnight, then your base interval is 1 day,
        # but you want to start that one day clock at midnight, not now.  So, we
        # have to fudge the rolloverAt value in order to trigger the first rollover
        # at the right time.  After that, the regular interval will take care of
        # the rest.  Note that this code doesn't care about leap seconds. :)
        ikiwa self.when == 'MIDNIGHT' or self.when.startswith('W'):
            # This could be done with less code, but I wanted it to be clear
            ikiwa self.utc:
                t = time.gmtime(currentTime)
            else:
                t = time.localtime(currentTime)
            currentHour = t[3]
            currentMinute = t[4]
            currentSecond = t[5]
            currentDay = t[6]
            # r is the number of seconds left between now and the next rotation
            ikiwa self.atTime is None:
                rotate_ts = _MIDNIGHT
            else:
                rotate_ts = ((self.atTime.hour * 60 + self.atTime.minute)*60 +
                    self.atTime.second)

            r = rotate_ts - ((currentHour * 60 + currentMinute) * 60 +
                currentSecond)
            ikiwa r < 0:
                # Rotate time is before the current time (for example when
                # self.rotateAt is 13:45 and it now 14:15), rotation is
                # tomorrow.
                r += _MIDNIGHT
                currentDay = (currentDay + 1) % 7
            result = currentTime + r
            # If we are rolling over on a certain day, add in the number of days until
            # the next rollover, but offset by 1 since we just calculated the time
            # until the next day starts.  There are three cases:
            # Case 1) The day to rollover is today; in this case, do nothing
            # Case 2) The day to rollover is further in the interval (i.e., today is
            #         day 2 (Wednesday) and rollover is on day 6 (Sunday).  Days to
            #         next rollover is simply 6 - 2 - 1, or 3.
            # Case 3) The day to rollover is behind us in the interval (i.e., today
            #         is day 5 (Saturday) and rollover is on day 3 (Thursday).
            #         Days to rollover is 6 - 5 + 3, or 4.  In this case, it's the
            #         number of days left in the current week (1) plus the number
            #         of days in the next week until the rollover day (3).
            # The calculations described in 2) and 3) above need to have a day added.
            # This is because the above time calculation takes us to midnight on this
            # day, i.e. the start of the next day.
            ikiwa self.when.startswith('W'):
                day = currentDay # 0 is Monday
                ikiwa day != self.dayOfWeek:
                    ikiwa day < self.dayOfWeek:
                        daysToWait = self.dayOfWeek - day
                    else:
                        daysToWait = 6 - day + self.dayOfWeek + 1
                    newRolloverAt = result + (daysToWait * (60 * 60 * 24))
                    ikiwa not self.utc:
                        dstNow = t[-1]
                        dstAtRollover = time.localtime(newRolloverAt)[-1]
                        ikiwa dstNow != dstAtRollover:
                            ikiwa not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                                addend = -3600
                            else:           # DST bows out before next rollover, so we need to add an hour
                                addend = 3600
                            newRolloverAt += addend
                    result = newRolloverAt
        rudisha result

    eleza shouldRollover(self, record):
        """
        Determine ikiwa rollover should occur.

        record is not used, as we are just comparing times, but it is needed so
        the method signatures are the same
        """
        t = int(time.time())
        ikiwa t >= self.rolloverAt:
            rudisha 1
        rudisha 0

    eleza getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.

        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            ikiwa fileName[:plen] == prefix:
                suffix = fileName[plen:]
                ikiwa self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        ikiwa len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        rudisha result

    eleza doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        ikiwa self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        ikiwa self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            ikiwa dstNow != dstThen:
                ikiwa dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        ikiwa os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        ikiwa self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        ikiwa not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        ikiwa (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            ikiwa dstNow != dstAtRollover:
                ikiwa not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

kundi WatchedFileHandler(logging.FileHandler):
    """
    A handler for logging to a file, which watches the file
    to see ikiwa it has changed while in use. This can happen because of
    usage of programs such as newsyslog and logrotate which perform
    log file rotation. This handler, intended for use under Unix,
    watches the file to see ikiwa it has changed since the last emit.
    (A file has changed ikiwa its device or inode have changed.)
    If it has changed, the old file stream is closed, and the file
    opened to get a new stream.

    This handler is not appropriate for use under Windows, because
    under Windows open files cannot be moved or renamed - logging
    opens the files with exclusive locks - and so there is no need
    for such a handler. Furthermore, ST_INO is not supported under
    Windows; stat always returns zero for this value.

    This handler is based on a suggestion and patch by Chad J.
    Schroeder.
    """
    eleza __init__(self, filename, mode='a', encoding=None, delay=False):
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.dev, self.ino = -1, -1
        self._statstream()

    eleza _statstream(self):
        ikiwa self.stream:
            sres = os.fstat(self.stream.fileno())
            self.dev, self.ino = sres[ST_DEV], sres[ST_INO]

    eleza reopenIfNeeded(self):
        """
        Reopen log file ikiwa needed.

        Checks ikiwa the underlying file has changed, and ikiwa it
        has, close the old stream and reopen the file to get the
        current stream.
        """
        # Reduce the chance of race conditions by stat'ing by path only
        # once and then fstat'ing our new fd ikiwa we opened a new log stream.
        # See issue #14632: Thanks to John Mulligan for the problem report
        # and patch.
        try:
            # stat the file by path, checking for existence
            sres = os.stat(self.baseFilename)
        except FileNotFoundError:
            sres = None
        # compare file system stat with that of our stream file handle
        ikiwa not sres or sres[ST_DEV] != self.dev or sres[ST_INO] != self.ino:
            ikiwa self.stream is not None:
                # we have an open file handle, clean it up
                self.stream.flush()
                self.stream.close()
                self.stream = None  # See Issue #21742: _open () might fail.
                # open a new file handle and get new stat info kutoka that fd
                self.stream = self._open()
                self._statstream()

    eleza emit(self, record):
        """
        Emit a record.

        If underlying file has changed, reopen the file before emitting the
        record to it.
        """
        self.reopenIfNeeded()
        logging.FileHandler.emit(self, record)


kundi SocketHandler(logging.Handler):
    """
    A handler kundi which writes logging records, in pickle format, to
    a streaming socket. The socket is kept open across logging calls.
    If the peer resets it, an attempt is made to reconnect on the next call.
    The pickle which is sent is that of the LogRecord's attribute dictionary
    (__dict__), so that the receiver does not need to have the logging module
    installed in order to process the logging event.

    To unpickle the record at the receiving end into a LogRecord, use the
    makeLogRecord function.
    """

    eleza __init__(self, host, port):
        """
        Initializes the handler with a specific host address and port.

        When the attribute *closeOnError* is set to True - ikiwa a socket error
        occurs, the socket is silently closed and then reopened on the next
        logging call.
        """
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        ikiwa port is None:
            self.address = host
        else:
            self.address = (host, port)
        self.sock = None
        self.closeOnError = False
        self.retryTime = None
        #
        # Exponential backoff parameters.
        #
        self.retryStart = 1.0
        self.retryMax = 30.0
        self.retryFactor = 2.0

    eleza makeSocket(self, timeout=1):
        """
        A factory method which allows subclasses to define the precise
        type of socket they want.
        """
        ikiwa self.port is not None:
            result = socket.create_connection(self.address, timeout=timeout)
        else:
            result = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            result.settimeout(timeout)
            try:
                result.connect(self.address)
            except OSError:
                result.close()  # Issue 19182
                raise
        rudisha result

    eleza createSocket(self):
        """
        Try to create a socket, using an exponential backoff with
        a max retry time. Thanks to Robert Olson for the original patch
        (SF #815911) which has been slightly refactored.
        """
        now = time.time()
        # Either retryTime is None, in which case this
        # is the first time back after a disconnect, or
        # we've waited long enough.
        ikiwa self.retryTime is None:
            attempt = True
        else:
            attempt = (now >= self.retryTime)
        ikiwa attempt:
            try:
                self.sock = self.makeSocket()
                self.retryTime = None # next time, no delay before trying
            except OSError:
                #Creation failed, so set the retry time and return.
                ikiwa self.retryTime is None:
                    self.retryPeriod = self.retryStart
                else:
                    self.retryPeriod = self.retryPeriod * self.retryFactor
                    ikiwa self.retryPeriod > self.retryMax:
                        self.retryPeriod = self.retryMax
                self.retryTime = now + self.retryPeriod

    eleza send(self, s):
        """
        Send a pickled string to the socket.

        This function allows for partial sends which can happen when the
        network is busy.
        """
        ikiwa self.sock is None:
            self.createSocket()
        #self.sock can be None either because we haven't reached the retry
        #time yet, or because we have reached the retry time and retried,
        #but are still unable to connect.
        ikiwa self.sock:
            try:
                self.sock.sendall(s)
            except OSError: #pragma: no cover
                self.sock.close()
                self.sock = None  # so we can call createSocket next time

    eleza makePickle(self, record):
        """
        Pickles the record in binary format with a length prefix, and
        returns it ready for transmission across the socket.
        """
        ei = record.exc_info
        ikiwa ei:
            # just to get traceback text into record.exc_text ...
            dummy = self.format(record)
        # See issue #14436: If msg or args are objects, they may not be
        # available on the receiving end. So we convert the msg % args
        # to a string, save it as msg and zap the args.
        d = dict(record.__dict__)
        d['msg'] = record.getMessage()
        d['args'] = None
        d['exc_info'] = None
        # Issue #25685: delete 'message' ikiwa present: redundant with 'msg'
        d.pop('message', None)
        s = pickle.dumps(d, 1)
        slen = struct.pack(">L", len(s))
        rudisha slen + s

    eleza handleError(self, record):
        """
        Handle an error during logging.

        An error has occurred during logging. Most likely cause -
        connection lost. Close the socket so that we can retry on the
        next event.
        """
        ikiwa self.closeOnError and self.sock:
            self.sock.close()
            self.sock = None        #try to reconnect next time
        else:
            logging.Handler.handleError(self, record)

    eleza emit(self, record):
        """
        Emit a record.

        Pickles the record and writes it to the socket in binary format.
        If there is an error with the socket, silently drop the packet.
        If there was a problem with the socket, re-establishes the
        socket.
        """
        try:
            s = self.makePickle(record)
            self.send(s)
        except Exception:
            self.handleError(record)

    eleza close(self):
        """
        Closes the socket.
        """
        self.acquire()
        try:
            sock = self.sock
            ikiwa sock:
                self.sock = None
                sock.close()
            logging.Handler.close(self)
        finally:
            self.release()

kundi DatagramHandler(SocketHandler):
    """
    A handler kundi which writes logging records, in pickle format, to
    a datagram socket.  The pickle which is sent is that of the LogRecord's
    attribute dictionary (__dict__), so that the receiver does not need to
    have the logging module installed in order to process the logging event.

    To unpickle the record at the receiving end into a LogRecord, use the
    makeLogRecord function.

    """
    eleza __init__(self, host, port):
        """
        Initializes the handler with a specific host address and port.
        """
        SocketHandler.__init__(self, host, port)
        self.closeOnError = False

    eleza makeSocket(self):
        """
        The factory method of SocketHandler is here overridden to create
        a UDP socket (SOCK_DGRAM).
        """
        ikiwa self.port is None:
            family = socket.AF_UNIX
        else:
            family = socket.AF_INET
        s = socket.socket(family, socket.SOCK_DGRAM)
        rudisha s

    eleza send(self, s):
        """
        Send a pickled string to a socket.

        This function no longer allows for partial sends which can happen
        when the network is busy - UDP does not guarantee delivery and
        can deliver packets out of sequence.
        """
        ikiwa self.sock is None:
            self.createSocket()
        self.sock.sendto(s, self.address)

kundi SysLogHandler(logging.Handler):
    """
    A handler kundi which sends formatted logging records to a syslog
    server. Based on Sam Rushing's syslog module:
    http://www.nightmare.com/squirl/python-ext/misc/syslog.py
    Contributed by Nicolas Untz (after which minor refactoring changes
    have been made).
    """

    # kutoka <linux/sys/syslog.h>:
    # ======================================================================
    # priorities/facilities are encoded into a single 32-bit quantity, where
    # the bottom 3 bits are the priority (0-7) and the top 28 bits are the
    # facility (0-big number). Both the priorities and the facilities map
    # roughly one-to-one to strings in the syslogd(8) source code.  This
    # mapping is included in this file.
    #
    # priorities (these are ordered)

    LOG_EMERG     = 0       #  system is unusable
    LOG_ALERT     = 1       #  action must be taken immediately
    LOG_CRIT      = 2       #  critical conditions
    LOG_ERR       = 3       #  error conditions
    LOG_WARNING   = 4       #  warning conditions
    LOG_NOTICE    = 5       #  normal but significant condition
    LOG_INFO      = 6       #  informational
    LOG_DEBUG     = 7       #  debug-level messages

    #  facility codes
    LOG_KERN      = 0       #  kernel messages
    LOG_USER      = 1       #  random user-level messages
    LOG_MAIL      = 2       #  mail system
    LOG_DAEMON    = 3       #  system daemons
    LOG_AUTH      = 4       #  security/authorization messages
    LOG_SYSLOG    = 5       #  messages generated internally by syslogd
    LOG_LPR       = 6       #  line printer subsystem
    LOG_NEWS      = 7       #  network news subsystem
    LOG_UUCP      = 8       #  UUCP subsystem
    LOG_CRON      = 9       #  clock daemon
    LOG_AUTHPRIV  = 10      #  security/authorization messages (private)
    LOG_FTP       = 11      #  FTP daemon

    #  other codes through 15 reserved for system use
    LOG_LOCAL0    = 16      #  reserved for local use
    LOG_LOCAL1    = 17      #  reserved for local use
    LOG_LOCAL2    = 18      #  reserved for local use
    LOG_LOCAL3    = 19      #  reserved for local use
    LOG_LOCAL4    = 20      #  reserved for local use
    LOG_LOCAL5    = 21      #  reserved for local use
    LOG_LOCAL6    = 22      #  reserved for local use
    LOG_LOCAL7    = 23      #  reserved for local use

    priority_names = {
        "alert":    LOG_ALERT,
        "crit":     LOG_CRIT,
        "critical": LOG_CRIT,
        "debug":    LOG_DEBUG,
        "emerg":    LOG_EMERG,
        "err":      LOG_ERR,
        "error":    LOG_ERR,        #  DEPRECATED
        "info":     LOG_INFO,
        "notice":   LOG_NOTICE,
        "panic":    LOG_EMERG,      #  DEPRECATED
        "warn":     LOG_WARNING,    #  DEPRECATED
        "warning":  LOG_WARNING,
        }

    facility_names = {
        "auth":     LOG_AUTH,
        "authpriv": LOG_AUTHPRIV,
        "cron":     LOG_CRON,
        "daemon":   LOG_DAEMON,
        "ftp":      LOG_FTP,
        "kern":     LOG_KERN,
        "lpr":      LOG_LPR,
        "mail":     LOG_MAIL,
        "news":     LOG_NEWS,
        "security": LOG_AUTH,       #  DEPRECATED
        "syslog":   LOG_SYSLOG,
        "user":     LOG_USER,
        "uucp":     LOG_UUCP,
        "local0":   LOG_LOCAL0,
        "local1":   LOG_LOCAL1,
        "local2":   LOG_LOCAL2,
        "local3":   LOG_LOCAL3,
        "local4":   LOG_LOCAL4,
        "local5":   LOG_LOCAL5,
        "local6":   LOG_LOCAL6,
        "local7":   LOG_LOCAL7,
        }

    #The map below appears to be trivially lowercasing the key. However,
    #there's more to it than meets the eye - in some locales, lowercasing
    #gives unexpected results. See SF #1524081: in the Turkish locale,
    #"INFO".lower() != "info"
    priority_map = {
        "DEBUG" : "debug",
        "INFO" : "info",
        "WARNING" : "warning",
        "ERROR" : "error",
        "CRITICAL" : "critical"
    }

    eleza __init__(self, address=('localhost', SYSLOG_UDP_PORT),
                 facility=LOG_USER, socktype=None):
        """
        Initialize a handler.

        If address is specified as a string, a UNIX socket is used. To log to a
        local syslogd, "SysLogHandler(address="/dev/log")" can be used.
        If facility is not specified, LOG_USER is used. If socktype is
        specified as socket.SOCK_DGRAM or socket.SOCK_STREAM, that specific
        socket type will be used. For Unix sockets, you can also specify a
        socktype of None, in which case socket.SOCK_DGRAM will be used, falling
        back to socket.SOCK_STREAM.
        """
        logging.Handler.__init__(self)

        self.address = address
        self.facility = facility
        self.socktype = socktype

        ikiwa isinstance(address, str):
            self.unixsocket = True
            # Syslog server may be unavailable during handler initialisation.
            # C's openlog() function also ignores connection errors.
            # Moreover, we ignore these errors while logging, so it not worse
            # to ignore it also here.
            try:
                self._connect_unixsocket(address)
            except OSError:
                pass
        else:
            self.unixsocket = False
            ikiwa socktype is None:
                socktype = socket.SOCK_DGRAM
            host, port = address
            ress = socket.getaddrinfo(host, port, 0, socktype)
            ikiwa not ress:
                raise OSError("getaddrinfo returns an empty list")
            for res in ress:
                af, socktype, proto, _, sa = res
                err = sock = None
                try:
                    sock = socket.socket(af, socktype, proto)
                    ikiwa socktype == socket.SOCK_STREAM:
                        sock.connect(sa)
                    break
                except OSError as exc:
                    err = exc
                    ikiwa sock is not None:
                        sock.close()
            ikiwa err is not None:
                raise err
            self.socket = sock
            self.socktype = socktype

    eleza _connect_unixsocket(self, address):
        use_socktype = self.socktype
        ikiwa use_socktype is None:
            use_socktype = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_UNIX, use_socktype)
        try:
            self.socket.connect(address)
            # it worked, so set self.socktype to the used type
            self.socktype = use_socktype
        except OSError:
            self.socket.close()
            ikiwa self.socktype is not None:
                # user didn't specify falling back, so fail
                raise
            use_socktype = socket.SOCK_STREAM
            self.socket = socket.socket(socket.AF_UNIX, use_socktype)
            try:
                self.socket.connect(address)
                # it worked, so set self.socktype to the used type
                self.socktype = use_socktype
            except OSError:
                self.socket.close()
                raise

    eleza encodePriority(self, facility, priority):
        """
        Encode the facility and priority. You can pass in strings or
        integers - ikiwa strings are passed, the facility_names and
        priority_names mapping dictionaries are used to convert them to
        integers.
        """
        ikiwa isinstance(facility, str):
            facility = self.facility_names[facility]
        ikiwa isinstance(priority, str):
            priority = self.priority_names[priority]
        rudisha (facility << 3) | priority

    eleza close(self):
        """
        Closes the socket.
        """
        self.acquire()
        try:
            self.socket.close()
            logging.Handler.close(self)
        finally:
            self.release()

    eleza mapPriority(self, levelName):
        """
        Map a logging level name to a key in the priority_names map.
        This is useful in two scenarios: when custom levels are being
        used, and in the case where you can't do a straightforward
        mapping by lowercasing the logging level name because of locale-
        specific issues (see SF #1524081).
        """
        rudisha self.priority_map.get(levelName, "warning")

    ident = ''          # prepended to all messages
    append_nul = True   # some old syslog daemons expect a NUL terminator

    eleza emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the syslog server. If
        exception information is present, it is NOT sent to the server.
        """
        try:
            msg = self.format(record)
            ikiwa self.ident:
                msg = self.ident + msg
            ikiwa self.append_nul:
                msg += '\000'

            # We need to convert record level to lowercase, maybe this will
            # change in the future.
            prio = '<%d>' % self.encodePriority(self.facility,
                                                self.mapPriority(record.levelname))
            prio = prio.encode('utf-8')
            # Message is a string. Convert to bytes as required by RFC 5424
            msg = msg.encode('utf-8')
            msg = prio + msg
            ikiwa self.unixsocket:
                try:
                    self.socket.send(msg)
                except OSError:
                    self.socket.close()
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elikiwa self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except Exception:
            self.handleError(record)

kundi SMTPHandler(logging.Handler):
    """
    A handler kundi which sends an SMTP email for each logging event.
    """
    eleza __init__(self, mailhost, kutokaaddr, toaddrs, subject,
                 credentials=None, secure=None, timeout=5.0):
        """
        Initialize the handler.

        Initialize the instance with the kutoka and to addresses and subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format for the mailhost argument. To specify
        authentication credentials, supply a (username, password) tuple
        for the credentials argument. To specify the use of a secure
        protocol (TLS), pass in a tuple for the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, or a single-value tuple with the name
        of a keyfile, or a 2-value tuple with the names of the keyfile and
        certificate file. (This tuple is passed to the `starttls` method).
        A timeout in seconds can be specified for the SMTP connection (the
        default is one second).
        """
        logging.Handler.__init__(self)
        ikiwa isinstance(mailhost, (list, tuple)):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None
        ikiwa isinstance(credentials, (list, tuple)):
            self.username, self.password = credentials
        else:
            self.username = None
        self.kutokaaddr = kutokaaddr
        ikiwa isinstance(toaddrs, str):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure
        self.timeout = timeout

    eleza getSubject(self, record):
        """
        Determine the subject for the email.

        If you want to specify a subject line which is record-dependent,
        override this method.
        """
        rudisha self.subject

    eleza emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            agiza smtplib
            kutoka email.message agiza EmailMessage
            agiza email.utils

            port = self.mailport
            ikiwa not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port, timeout=self.timeout)
            msg = EmailMessage()
            msg['From'] = self.kutokaaddr
            msg['To'] = ','.join(self.toaddrs)
            msg['Subject'] = self.getSubject(record)
            msg['Date'] = email.utils.localtime()
            msg.set_content(self.format(record))
            ikiwa self.username:
                ikiwa self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.send_message(msg)
            smtp.quit()
        except Exception:
            self.handleError(record)

kundi NTEventLogHandler(logging.Handler):
    """
    A handler kundi which sends events to the NT Event Log. Adds a
    registry entry for the specified application name. If no dllname is
    provided, win32service.pyd (which contains some basic message
    placeholders) is used. Note that use of these placeholders will make
    your event logs big, as the entire message source is held in the log.
    If you want slimmer logs, you have to pass in the name of your own DLL
    which contains the message definitions you want to use in the event log.
    """
    eleza __init__(self, appname, dllname=None, logtype="Application"):
        logging.Handler.__init__(self)
        try:
            agiza win32evtlogutil, win32evtlog
            self.appname = appname
            self._welu = win32evtlogutil
            ikiwa not dllname:
                dllname = os.path.split(self._welu.__file__)
                dllname = os.path.split(dllname[0])
                dllname = os.path.join(dllname[0], r'win32service.pyd')
            self.dllname = dllname
            self.logtype = logtype
            self._welu.AddSourceToRegistry(appname, dllname, logtype)
            self.deftype = win32evtlog.EVENTLOG_ERROR_TYPE
            self.typemap = {
                logging.DEBUG   : win32evtlog.EVENTLOG_INFORMATION_TYPE,
                logging.INFO    : win32evtlog.EVENTLOG_INFORMATION_TYPE,
                logging.WARNING : win32evtlog.EVENTLOG_WARNING_TYPE,
                logging.ERROR   : win32evtlog.EVENTLOG_ERROR_TYPE,
                logging.CRITICAL: win32evtlog.EVENTLOG_ERROR_TYPE,
         }
        except ImportError:
            andika("The Python Win32 extensions for NT (service, event "\
                        "logging) appear not to be available.")
            self._welu = None

    eleza getMessageID(self, record):
        """
        Return the message ID for the event record. If you are using your
        own messages, you could do this by having the msg passed to the
        logger being an ID rather than a formatting string. Then, in here,
        you could use a dictionary lookup to get the message ID. This
        version returns 1, which is the base message ID in win32service.pyd.
        """
        rudisha 1

    eleza getEventCategory(self, record):
        """
        Return the event category for the record.

        Override this ikiwa you want to specify your own categories. This version
        returns 0.
        """
        rudisha 0

    eleza getEventType(self, record):
        """
        Return the event type for the record.

        Override this ikiwa you want to specify your own types. This version does
        a mapping using the handler's typemap attribute, which is set up in
        __init__() to a dictionary which contains mappings for DEBUG, INFO,
        WARNING, ERROR and CRITICAL. If you are using your own levels you will
        either need to override this method or place a suitable dictionary in
        the handler's typemap attribute.
        """
        rudisha self.typemap.get(record.levelno, self.deftype)

    eleza emit(self, record):
        """
        Emit a record.

        Determine the message ID, event category and event type. Then
        log the message in the NT event log.
        """
        ikiwa self._welu:
            try:
                id = self.getMessageID(record)
                cat = self.getEventCategory(record)
                type = self.getEventType(record)
                msg = self.format(record)
                self._welu.ReportEvent(self.appname, id, cat, type, [msg])
            except Exception:
                self.handleError(record)

    eleza close(self):
        """
        Clean up this handler.

        You can remove the application name kutoka the registry as a
        source of event log entries. However, ikiwa you do this, you will
        not be able to see the events as you intended in the Event Log
        Viewer - it needs to be able to access the registry to get the
        DLL name.
        """
        #self._welu.RemoveSourceFromRegistry(self.appname, self.logtype)
        logging.Handler.close(self)

kundi HTTPHandler(logging.Handler):
    """
    A kundi which sends records to a Web server, using either GET or
    POST semantics.
    """
    eleza __init__(self, host, url, method="GET", secure=False, credentials=None,
                 context=None):
        """
        Initialize the instance with the host, the request URL, and the method
        ("GET" or "POST")
        """
        logging.Handler.__init__(self)
        method = method.upper()
        ikiwa method not in ["GET", "POST"]:
            raise ValueError("method must be GET or POST")
        ikiwa not secure and context is not None:
            raise ValueError("context parameter only makes sense "
                             "with secure=True")
        self.host = host
        self.url = url
        self.method = method
        self.secure = secure
        self.credentials = credentials
        self.context = context

    eleza mapLogRecord(self, record):
        """
        Default implementation of mapping the log record into a dict
        that is sent as the CGI data. Overwrite in your class.
        Contributed by Franz Glasner.
        """
        rudisha record.__dict__

    eleza emit(self, record):
        """
        Emit a record.

        Send the record to the Web server as a percent-encoded dictionary
        """
        try:
            agiza http.client, urllib.parse
            host = self.host
            ikiwa self.secure:
                h = http.client.HTTPSConnection(host, context=self.context)
            else:
                h = http.client.HTTPConnection(host)
            url = self.url
            data = urllib.parse.urlencode(self.mapLogRecord(record))
            ikiwa self.method == "GET":
                ikiwa (url.find('?') >= 0):
                    sep = '&'
                else:
                    sep = '?'
                url = url + "%c%s" % (sep, data)
            h.putrequest(self.method, url)
            # support multiple hosts on one IP address...
            # need to strip optional :port kutoka host, ikiwa present
            i = host.find(":")
            ikiwa i >= 0:
                host = host[:i]
            # See issue #30904: putrequest call above already adds this header
            # on Python 3.x.
            # h.putheader("Host", host)
            ikiwa self.method == "POST":
                h.putheader("Content-type",
                            "application/x-www-form-urlencoded")
                h.putheader("Content-length", str(len(data)))
            ikiwa self.credentials:
                agiza base64
                s = ('%s:%s' % self.credentials).encode('utf-8')
                s = 'Basic ' + base64.b64encode(s).strip().decode('ascii')
                h.putheader('Authorization', s)
            h.endheaders()
            ikiwa self.method == "POST":
                h.send(data.encode('utf-8'))
            h.getresponse()    #can't do anything with the result
        except Exception:
            self.handleError(record)

kundi BufferingHandler(logging.Handler):
    """
  A handler kundi which buffers logging records in memory. Whenever each
  record is added to the buffer, a check is made to see ikiwa the buffer should
  be flushed. If it should, then flush() is expected to do what's needed.
    """
    eleza __init__(self, capacity):
        """
        Initialize the handler with the buffer size.
        """
        logging.Handler.__init__(self)
        self.capacity = capacity
        self.buffer = []

    eleza shouldFlush(self, record):
        """
        Should the handler flush its buffer?

        Returns true ikiwa the buffer is up to capacity. This method can be
        overridden to implement custom flushing strategies.
        """
        rudisha (len(self.buffer) >= self.capacity)

    eleza emit(self, record):
        """
        Emit a record.

        Append the record. If shouldFlush() tells us to, call flush() to process
        the buffer.
        """
        self.buffer.append(record)
        ikiwa self.shouldFlush(record):
            self.flush()

    eleza flush(self):
        """
        Override to implement custom flushing behaviour.

        This version just zaps the buffer to empty.
        """
        self.acquire()
        try:
            self.buffer = []
        finally:
            self.release()

    eleza close(self):
        """
        Close the handler.

        This version just flushes and chains to the parent class' close().
        """
        try:
            self.flush()
        finally:
            logging.Handler.close(self)

kundi MemoryHandler(BufferingHandler):
    """
    A handler kundi which buffers logging records in memory, periodically
    flushing them to a target handler. Flushing occurs whenever the buffer
    is full, or when an event of a certain severity or greater is seen.
    """
    eleza __init__(self, capacity, flushLevel=logging.ERROR, target=None,
                 flushOnClose=True):
        """
        Initialize the handler with the buffer size, the level at which
        flushing should occur and an optional target.

        Note that without a target being set either here or via setTarget(),
        a MemoryHandler is no use to anyone!

        The ``flushOnClose`` argument is ``True`` for backward compatibility
        reasons - the old behaviour is that when the handler is closed, the
        buffer is flushed, even ikiwa the flush level hasn't been exceeded nor the
        capacity exceeded. To prevent this, set ``flushOnClose`` to ``False``.
        """
        BufferingHandler.__init__(self, capacity)
        self.flushLevel = flushLevel
        self.target = target
        # See Issue #26559 for why this has been added
        self.flushOnClose = flushOnClose

    eleza shouldFlush(self, record):
        """
        Check for buffer full or a record at the flushLevel or higher.
        """
        rudisha (len(self.buffer) >= self.capacity) or \
                (record.levelno >= self.flushLevel)

    eleza setTarget(self, target):
        """
        Set the target handler for this handler.
        """
        self.target = target

    eleza flush(self):
        """
        For a MemoryHandler, flushing means just sending the buffered
        records to the target, ikiwa there is one. Override ikiwa you want
        different behaviour.

        The record buffer is also cleared by this operation.
        """
        self.acquire()
        try:
            ikiwa self.target:
                for record in self.buffer:
                    self.target.handle(record)
                self.buffer = []
        finally:
            self.release()

    eleza close(self):
        """
        Flush, ikiwa appropriately configured, set the target to None and lose the
        buffer.
        """
        try:
            ikiwa self.flushOnClose:
                self.flush()
        finally:
            self.acquire()
            try:
                self.target = None
                BufferingHandler.close(self)
            finally:
                self.release()


kundi QueueHandler(logging.Handler):
    """
    This handler sends events to a queue. Typically, it would be used together
    with a multiprocessing Queue to centralise logging to file in one process
    (in a multi-process application), so as to avoid file write contention
    between processes.

    This code is new in Python 3.2, but this kundi can be copy pasted into
    user code for use with earlier Python versions.
    """

    eleza __init__(self, queue):
        """
        Initialise an instance, using the passed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    eleza enqueue(self, record):
        """
        Enqueue a record.

        The base implementation uses put_nowait. You may want to override
        this method ikiwa you want to use blocking, timeouts or custom queue
        implementations.
        """
        self.queue.put_nowait(record)

    eleza prepare(self, record):
        """
        Prepares a record for queuing. The object returned by this method is
        enqueued.

        The base implementation formats the record to merge the message
        and arguments, and removes unpickleable items kutoka the record
        in-place.

        You might want to override this method ikiwa you want to convert
        the record to a dict or JSON string, or send a modified copy
        of the record while leaving the original intact.
        """
        # The format operation gets traceback text into record.exc_text
        # (ikiwa there's exception data), and also returns the formatted
        # message. We can then use this to replace the original
        # msg + args, as these might be unpickleable. We also zap the
        # exc_info and exc_text attributes, as they are no longer
        # needed and, ikiwa not None, will typically not be pickleable.
        msg = self.format(record)
        # bpo-35726: make copy of record to avoid affecting other handlers in the chain.
        record = copy.copy(record)
        record.message = msg
        record.msg = msg
        record.args = None
        record.exc_info = None
        record.exc_text = None
        rudisha record

    eleza emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it for pickling first.
        """
        try:
            self.enqueue(self.prepare(record))
        except Exception:
            self.handleError(record)


kundi QueueListener(object):
    """
    This kundi implements an internal threaded listener which watches for
    LogRecords being added to a queue, removes them and passes them to a
    list of handlers for processing.
    """
    _sentinel = None

    eleza __init__(self, queue, *handlers, respect_handler_level=False):
        """
        Initialise an instance with the specified queue and
        handlers.
        """
        self.queue = queue
        self.handlers = handlers
        self._thread = None
        self.respect_handler_level = respect_handler_level

    eleza dequeue(self, block):
        """
        Dequeue a record and rudisha it, optionally blocking.

        The base implementation uses get. You may want to override this method
        ikiwa you want to use timeouts or work with custom queue implementations.
        """
        rudisha self.queue.get(block)

    eleza start(self):
        """
        Start the listener.

        This starts up a background thread to monitor the queue for
        LogRecords to process.
        """
        self._thread = t = threading.Thread(target=self._monitor)
        t.daemon = True
        t.start()

    eleza prepare(self, record):
        """
        Prepare a record for handling.

        This method just returns the passed-in record. You may want to
        override this method ikiwa you need to do any custom marshalling or
        manipulation of the record before passing it to the handlers.
        """
        rudisha record

    eleza handle(self, record):
        """
        Handle a record.

        This just loops through the handlers offering them the record
        to handle.
        """
        record = self.prepare(record)
        for handler in self.handlers:
            ikiwa not self.respect_handler_level:
                process = True
            else:
                process = record.levelno >= handler.level
            ikiwa process:
                handler.handle(record)

    eleza _monitor(self):
        """
        Monitor the queue for records, and ask the handler
        to deal with them.

        This method runs on a separate, internal thread.
        The thread will terminate ikiwa it sees a sentinel object in the queue.
        """
        q = self.queue
        has_task_done = hasattr(q, 'task_done')
        while True:
            try:
                record = self.dequeue(True)
                ikiwa record is self._sentinel:
                    ikiwa has_task_done:
                        q.task_done()
                    break
                self.handle(record)
                ikiwa has_task_done:
                    q.task_done()
            except queue.Empty:
                break

    eleza enqueue_sentinel(self):
        """
        This is used to enqueue the sentinel record.

        The base implementation uses put_nowait. You may want to override this
        method ikiwa you want to use timeouts or work with custom queue
        implementations.
        """
        self.queue.put_nowait(self._sentinel)

    eleza stop(self):
        """
        Stop the listener.

        This asks the thread to terminate, and then waits for it to do so.
        Note that ikiwa you don't call this before your application exits, there
        may be some records still left on the queue, which won't be processed.
        """
        self.enqueue_sentinel()
        self._thread.join()
        self._thread = None
