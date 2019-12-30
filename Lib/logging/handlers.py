# Copyright 2001-2016 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, na distribute this software na its
# documentation kila any purpose na without fee ni hereby granted,
# provided that the above copyright notice appear kwenye all copies na that
# both that copyright notice na this permission notice appear kwenye
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
Additional handlers kila the logging package kila Python. The core package is
based on PEP 282 na comments thereto kwenye comp.lang.python.

Copyright (C) 2001-2016 Vinay Sajip. All Rights Reserved.

To use, simply 'agiza logging.handlers' na log away!
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

_MIDNIGHT = 24 * 60 * 60  # number of seconds kwenye a day

kundi BaseRotatingHandler(logging.FileHandler):
    """
    Base kundi kila handlers that rotate log files at a certain point.
    Not meant to be instantiated directly.  Instead, use RotatingFileHandler
    ama TimedRotatingFileHandler.
    """
    eleza __init__(self, filename, mode, encoding=Tupu, delay=Uongo):
        """
        Use the specified filename kila streamed logging
        """
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.mode = mode
        self.encoding = encoding
        self.namer = Tupu
        self.rotator = Tupu

    eleza emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering kila rollover kama described
        kwenye doRollover().
        """
        jaribu:
            ikiwa self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        tatizo Exception:
            self.handleError(record)

    eleza rotation_filename(self, default_name):
        """
        Modify the filename of a log file when rotating.

        This ni provided so that a custom filename can be provided.

        The default implementation calls the 'namer' attribute of the
        handler, ikiwa it's callable, pitaing the default name to
        it. If the attribute isn't callable (the default ni Tupu), the name
        ni returned unchanged.

        :param default_name: The default name kila the log file.
        """
        ikiwa sio callable(self.namer):
            result = default_name
        isipokua:
            result = self.namer(default_name)
        rudisha result

    eleza rotate(self, source, dest):
        """
        When rotating, rotate the current log.

        The default implementation calls the 'rotator' attribute of the
        handler, ikiwa it's callable, pitaing the source na dest arguments to
        it. If the attribute isn't callable (the default ni Tupu), the source
        ni simply renamed to the destination.

        :param source: The source filename. This ni normally the base
                       filename, e.g. 'test.log'
        :param dest:   The destination filename. This ni normally
                       what the source ni rotated to, e.g. 'test.log.1'.
        """
        ikiwa sio callable(self.rotator):
            # Issue 18940: A file may sio have been created ikiwa delay ni Kweli.
            ikiwa os.path.exists(source):
                os.rename(source, dest)
        isipokua:
            self.rotator(source, dest)

kundi RotatingFileHandler(BaseRotatingHandler):
    """
    Handler kila logging to a set of files, which switches kutoka one file
    to the next when the current file reaches a certain size.
    """
    eleza __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=Tupu, delay=Uongo):
        """
        Open the specified file na use it kama the stream kila logging.

        By default, the file grows indefinitely. You can specify particular
        values of maxBytes na backupCount to allow the file to rollover at
        a predetermined size.

        Rollover occurs whenever the current log file ni nearly maxBytes kwenye
        length. If backupCount ni >= 1, the system will successively create
        new files ukijumuisha the same pathname kama the base file, but ukijumuisha extensions
        ".1", ".2" etc. appended to it. For example, ukijumuisha a backupCount of 5
        na a base file name of "app.log", you would get "app.log",
        "app.log.1", "app.log.2", ... through to "app.log.5". The file being
        written to ni always "app.log" - when it gets filled up, it ni closed
        na renamed to "app.log.1", na ikiwa files "app.log.1", "app.log.2" etc.
        exist, then they are renamed to "app.log.2", "app.log.3" etc.
        respectively.

        If maxBytes ni zero, rollover never occurs.
        """
        # If rotation/rollover ni wanted, it doesn't make sense to use another
        # mode. If kila example 'w' were specified, then ikiwa there were multiple
        # runs of the calling application, the logs kutoka previous runs would be
        # lost ikiwa the 'w' ni respected, because the log file would be truncated
        # on each run.
        ikiwa maxBytes > 0:
            mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    eleza doRollover(self):
        """
        Do a rollover, kama described kwenye __init__().
        """
        ikiwa self.stream:
            self.stream.close()
            self.stream = Tupu
        ikiwa self.backupCount > 0:
            kila i kwenye range(self.backupCount - 1, 0, -1):
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
        ikiwa sio self.delay:
            self.stream = self._open()

    eleza shouldRollover(self, record):
        """
        Determine ikiwa rollover should occur.

        Basically, see ikiwa the supplied record would cause the file to exceed
        the size limit we have.
        """
        ikiwa self.stream ni Tupu:                 # delay was set...
            self.stream = self._open()
        ikiwa self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            ikiwa self.stream.tell() + len(msg) >= self.maxBytes:
                rudisha 1
        rudisha 0

kundi TimedRotatingFileHandler(BaseRotatingHandler):
    """
    Handler kila logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount ni > 0, when rollover ni done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """
    eleza __init__(self, filename, when='h', interval=1, backupCount=0, encoding=Tupu, delay=Uongo, utc=Uongo, atTime=Tupu):
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)
        self.when = when.upper()
        self.backupCount = backupCount
        self.utc = utc
        self.atTime = atTime
        # Calculate the real rollover interval, which ni just the number of
        # seconds between rollovers.  Also set the filename suffix used when
        # a rollover occurs.  Current 'when' events supported:
        # S - Seconds
        # M - Minutes
        # H - Hours
        # D - Days
        # midnight - roll over at midnight
        # W{0-6} - roll over on a certain day; 0 - Monday
        #
        # Case of the 'when' specifier ni sio important; lower ama upper case
        # will work.
        ikiwa self.when == 'S':
            self.interval = 1 # one second
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.\w+)?$"
        lasivyo self.when == 'M':
            self.interval = 60 # one minute
            self.suffix = "%Y-%m-%d_%H-%M"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}(\.\w+)?$"
        lasivyo self.when == 'H':
            self.interval = 60 * 60 # one hour
            self.suffix = "%Y-%m-%d_%H"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}(\.\w+)?$"
        lasivyo self.when == 'D' ama self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24 # one day
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        lasivyo self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7 # one week
            ikiwa len(self.when) != 2:
                ashiria ValueError("You must specify a day kila weekly rollover kutoka 0 to 6 (0 ni Monday): %s" % self.when)
            ikiwa self.when[1] < '0' ama self.when[1] > '6':
                ashiria ValueError("Invalid day specified kila weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        isipokua:
            ashiria ValueError("Invalid rollover interval specified: %s" % self.when)

        self.extMatch = re.compile(self.extMatch, re.ASCII)
        self.interval = self.interval * interval # multiply by units requested
        # The following line added because the filename pitaed kwenye could be a
        # path object (see Issue #27493), but self.baseFilename will be a string
        filename = self.baseFilename
        ikiwa os.path.exists(filename):
            t = os.stat(filename)[ST_MTIME]
        isipokua:
            t = int(time.time())
        self.rolloverAt = self.computeRollover(t)

    eleza computeRollover(self, currentTime):
        """
        Work out the rollover time based on the specified time.
        """
        result = currentTime + self.interval
        # If we are rolling over at midnight ama weekly, then the interval ni already known.
        # What we need to figure out ni WHEN the next interval is.  In other words,
        # ikiwa you are rolling over at midnight, then your base interval ni 1 day,
        # but you want to start that one day clock at midnight, sio now.  So, we
        # have to fudge the rolloverAt value kwenye order to trigger the first rollover
        # at the right time.  After that, the regular interval will take care of
        # the rest.  Note that this code doesn't care about leap seconds. :)
        ikiwa self.when == 'MIDNIGHT' ama self.when.startswith('W'):
            # This could be done ukijumuisha less code, but I wanted it to be clear
            ikiwa self.utc:
                t = time.gmtime(currentTime)
            isipokua:
                t = time.localtime(currentTime)
            currentHour = t[3]
            currentMinute = t[4]
            currentSecond = t[5]
            currentDay = t[6]
            # r ni the number of seconds left between now na the next rotation
            ikiwa self.atTime ni Tupu:
                rotate_ts = _MIDNIGHT
            isipokua:
                rotate_ts = ((self.atTime.hour * 60 + self.atTime.minute)*60 +
                    self.atTime.second)

            r = rotate_ts - ((currentHour * 60 + currentMinute) * 60 +
                currentSecond)
            ikiwa r < 0:
                # Rotate time ni before the current time (kila example when
                # self.rotateAt ni 13:45 na it now 14:15), rotation is
                # tomorrow.
                r += _MIDNIGHT
                currentDay = (currentDay + 1) % 7
            result = currentTime + r
            # If we are rolling over on a certain day, add kwenye the number of days until
            # the next rollover, but offset by 1 since we just calculated the time
            # until the next day starts.  There are three cases:
            # Case 1) The day to rollover ni today; kwenye this case, do nothing
            # Case 2) The day to rollover ni further kwenye the interval (i.e., today is
            #         day 2 (Wednesday) na rollover ni on day 6 (Sunday).  Days to
            #         next rollover ni simply 6 - 2 - 1, ama 3.
            # Case 3) The day to rollover ni behind us kwenye the interval (i.e., today
            #         ni day 5 (Saturday) na rollover ni on day 3 (Thursday).
            #         Days to rollover ni 6 - 5 + 3, ama 4.  In this case, it's the
            #         number of days left kwenye the current week (1) plus the number
            #         of days kwenye the next week until the rollover day (3).
            # The calculations described kwenye 2) na 3) above need to have a day added.
            # This ni because the above time calculation takes us to midnight on this
            # day, i.e. the start of the next day.
            ikiwa self.when.startswith('W'):
                day = currentDay # 0 ni Monday
                ikiwa day != self.dayOfWeek:
                    ikiwa day < self.dayOfWeek:
                        daysToWait = self.dayOfWeek - day
                    isipokua:
                        daysToWait = 6 - day + self.dayOfWeek + 1
                    newRolloverAt = result + (daysToWait * (60 * 60 * 24))
                    ikiwa sio self.utc:
                        dstNow = t[-1]
                        dstAtRollover = time.localtime(newRolloverAt)[-1]
                        ikiwa dstNow != dstAtRollover:
                            ikiwa sio dstNow:  # DST kicks kwenye before next rollover, so we need to deduct an hour
                                addend = -3600
                            isipokua:           # DST bows out before next rollover, so we need to add an hour
                                addend = 3600
                            newRolloverAt += addend
                    result = newRolloverAt
        rudisha result

    eleza shouldRollover(self, record):
        """
        Determine ikiwa rollover should occur.

        record ni sio used, kama we are just comparing times, but it ni needed so
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
        kila fileName kwenye fileNames:
            ikiwa fileName[:plen] == prefix:
                suffix = fileName[plen:]
                ikiwa self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        ikiwa len(result) < self.backupCount:
            result = []
        isipokua:
            result.sort()
            result = result[:len(result) - self.backupCount]
        rudisha result

    eleza doRollover(self):
        """
        do a rollover; kwenye this case, a date/time stamp ni appended to the filename
        when the rollover happens.  However, you want the file to be named kila the
        start of the interval, sio the current time.  If there ni a backup count,
        then we have to get a list of matching filenames, sort them na remove
        the one ukijumuisha the oldest suffix.
        """
        ikiwa self.stream:
            self.stream.close()
            self.stream = Tupu
        # get the time that this sequence started at na make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        ikiwa self.utc:
            timeTuple = time.gmtime(t)
        isipokua:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            ikiwa dstNow != dstThen:
                ikiwa dstNow:
                    addend = 3600
                isipokua:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        ikiwa os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        ikiwa self.backupCount > 0:
            kila s kwenye self.getFilesToDelete():
                os.remove(s)
        ikiwa sio self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        wakati newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes na midnight ama weekly rollover, adjust kila this.
        ikiwa (self.when == 'MIDNIGHT' ama self.when.startswith('W')) na sio self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            ikiwa dstNow != dstAtRollover:
                ikiwa sio dstNow:  # DST kicks kwenye before next rollover, so we need to deduct an hour
                    addend = -3600
                isipokua:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

kundi WatchedFileHandler(logging.FileHandler):
    """
    A handler kila logging to a file, which watches the file
    to see ikiwa it has changed wakati kwenye use. This can happen because of
    usage of programs such kama newsyslog na logrotate which perform
    log file rotation. This handler, intended kila use under Unix,
    watches the file to see ikiwa it has changed since the last emit.
    (A file has changed ikiwa its device ama inode have changed.)
    If it has changed, the old file stream ni closed, na the file
    opened to get a new stream.

    This handler ni sio appropriate kila use under Windows, because
    under Windows open files cansio be moved ama renamed - logging
    opens the files ukijumuisha exclusive locks - na so there ni no need
    kila such a handler. Furthermore, ST_INO ni sio supported under
    Windows; stat always returns zero kila this value.

    This handler ni based on a suggestion na patch by Chad J.
    Schroeder.
    """
    eleza __init__(self, filename, mode='a', encoding=Tupu, delay=Uongo):
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

        Checks ikiwa the underlying file has changed, na ikiwa it
        has, close the old stream na reopen the file to get the
        current stream.
        """
        # Reduce the chance of race conditions by stat'ing by path only
        # once na then fstat'ing our new fd ikiwa we opened a new log stream.
        # See issue #14632: Thanks to John Mulligan kila the problem report
        # na patch.
        jaribu:
            # stat the file by path, checking kila existence
            sres = os.stat(self.baseFilename)
        tatizo FileNotFoundError:
            sres = Tupu
        # compare file system stat ukijumuisha that of our stream file handle
        ikiwa sio sres ama sres[ST_DEV] != self.dev ama sres[ST_INO] != self.ino:
            ikiwa self.stream ni sio Tupu:
                # we have an open file handle, clean it up
                self.stream.flush()
                self.stream.close()
                self.stream = Tupu  # See Issue #21742: _open () might fail.
                # open a new file handle na get new stat info kutoka that fd
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
    A handler kundi which writes logging records, kwenye pickle format, to
    a streaming socket. The socket ni kept open across logging calls.
    If the peer resets it, an attempt ni made to reconnect on the next call.
    The pickle which ni sent ni that of the LogRecord's attribute dictionary
    (__dict__), so that the receiver does sio need to have the logging module
    installed kwenye order to process the logging event.

    To unpickle the record at the receiving end into a LogRecord, use the
    makeLogRecord function.
    """

    eleza __init__(self, host, port):
        """
        Initializes the handler ukijumuisha a specific host address na port.

        When the attribute *closeOnError* ni set to Kweli - ikiwa a socket error
        occurs, the socket ni silently closed na then reopened on the next
        logging call.
        """
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        ikiwa port ni Tupu:
            self.address = host
        isipokua:
            self.address = (host, port)
        self.sock = Tupu
        self.closeOnError = Uongo
        self.retryTime = Tupu
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
        ikiwa self.port ni sio Tupu:
            result = socket.create_connection(self.address, timeout=timeout)
        isipokua:
            result = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            result.settimeout(timeout)
            jaribu:
                result.connect(self.address)
            tatizo OSError:
                result.close()  # Issue 19182
                raise
        rudisha result

    eleza createSocket(self):
        """
        Try to create a socket, using an exponential backoff with
        a max retry time. Thanks to Robert Olson kila the original patch
        (SF #815911) which has been slightly refactored.
        """
        now = time.time()
        # Either retryTime ni Tupu, kwenye which case this
        # ni the first time back after a disconnect, ama
        # we've waited long enough.
        ikiwa self.retryTime ni Tupu:
            attempt = Kweli
        isipokua:
            attempt = (now >= self.retryTime)
        ikiwa attempt:
            jaribu:
                self.sock = self.makeSocket()
                self.retryTime = Tupu # next time, no delay before trying
            tatizo OSError:
                #Creation failed, so set the retry time na return.
                ikiwa self.retryTime ni Tupu:
                    self.retryPeriod = self.retryStart
                isipokua:
                    self.retryPeriod = self.retryPeriod * self.retryFactor
                    ikiwa self.retryPeriod > self.retryMax:
                        self.retryPeriod = self.retryMax
                self.retryTime = now + self.retryPeriod

    eleza send(self, s):
        """
        Send a pickled string to the socket.

        This function allows kila partial sends which can happen when the
        network ni busy.
        """
        ikiwa self.sock ni Tupu:
            self.createSocket()
        #self.sock can be Tupu either because we haven't reached the retry
        #time yet, ama because we have reached the retry time na retried,
        #but are still unable to connect.
        ikiwa self.sock:
            jaribu:
                self.sock.sendall(s)
            tatizo OSError: #pragma: no cover
                self.sock.close()
                self.sock = Tupu  # so we can call createSocket next time

    eleza makePickle(self, record):
        """
        Pickles the record kwenye binary format ukijumuisha a length prefix, na
        returns it ready kila transmission across the socket.
        """
        ei = record.exc_info
        ikiwa ei:
            # just to get traceback text into record.exc_text ...
            dummy = self.format(record)
        # See issue #14436: If msg ama args are objects, they may sio be
        # available on the receiving end. So we convert the msg % args
        # to a string, save it kama msg na zap the args.
        d = dict(record.__dict__)
        d['msg'] = record.getMessage()
        d['args'] = Tupu
        d['exc_info'] = Tupu
        # Issue #25685: delete 'message' ikiwa present: redundant ukijumuisha 'msg'
        d.pop('message', Tupu)
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
        ikiwa self.closeOnError na self.sock:
            self.sock.close()
            self.sock = Tupu        #try to reconnect next time
        isipokua:
            logging.Handler.handleError(self, record)

    eleza emit(self, record):
        """
        Emit a record.

        Pickles the record na writes it to the socket kwenye binary format.
        If there ni an error ukijumuisha the socket, silently drop the packet.
        If there was a problem ukijumuisha the socket, re-establishes the
        socket.
        """
        jaribu:
            s = self.makePickle(record)
            self.send(s)
        tatizo Exception:
            self.handleError(record)

    eleza close(self):
        """
        Closes the socket.
        """
        self.acquire()
        jaribu:
            sock = self.sock
            ikiwa sock:
                self.sock = Tupu
                sock.close()
            logging.Handler.close(self)
        mwishowe:
            self.release()

kundi DatagramHandler(SocketHandler):
    """
    A handler kundi which writes logging records, kwenye pickle format, to
    a datagram socket.  The pickle which ni sent ni that of the LogRecord's
    attribute dictionary (__dict__), so that the receiver does sio need to
    have the logging module installed kwenye order to process the logging event.

    To unpickle the record at the receiving end into a LogRecord, use the
    makeLogRecord function.

    """
    eleza __init__(self, host, port):
        """
        Initializes the handler ukijumuisha a specific host address na port.
        """
        SocketHandler.__init__(self, host, port)
        self.closeOnError = Uongo

    eleza makeSocket(self):
        """
        The factory method of SocketHandler ni here overridden to create
        a UDP socket (SOCK_DGRAM).
        """
        ikiwa self.port ni Tupu:
            family = socket.AF_UNIX
        isipokua:
            family = socket.AF_INET
        s = socket.socket(family, socket.SOCK_DGRAM)
        rudisha s

    eleza send(self, s):
        """
        Send a pickled string to a socket.

        This function no longer allows kila partial sends which can happen
        when the network ni busy - UDP does sio guarantee delivery na
        can deliver packets out of sequence.
        """
        ikiwa self.sock ni Tupu:
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
    # the bottom 3 bits are the priority (0-7) na the top 28 bits are the
    # facility (0-big number). Both the priorities na the facilities map
    # roughly one-to-one to strings kwenye the syslogd(8) source code.  This
    # mapping ni included kwenye this file.
    #
    # priorities (these are ordered)

    LOG_EMERG     = 0       #  system ni unusable
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

    #  other codes through 15 reserved kila system use
    LOG_LOCAL0    = 16      #  reserved kila local use
    LOG_LOCAL1    = 17      #  reserved kila local use
    LOG_LOCAL2    = 18      #  reserved kila local use
    LOG_LOCAL3    = 19      #  reserved kila local use
    LOG_LOCAL4    = 20      #  reserved kila local use
    LOG_LOCAL5    = 21      #  reserved kila local use
    LOG_LOCAL6    = 22      #  reserved kila local use
    LOG_LOCAL7    = 23      #  reserved kila local use

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
    #there's more to it than meets the eye - kwenye some locales, lowercasing
    #gives unexpected results. See SF #1524081: kwenye the Turkish locale,
    #"INFO".lower() != "info"
    priority_map = {
        "DEBUG" : "debug",
        "INFO" : "info",
        "WARNING" : "warning",
        "ERROR" : "error",
        "CRITICAL" : "critical"
    }

    eleza __init__(self, address=('localhost', SYSLOG_UDP_PORT),
                 facility=LOG_USER, socktype=Tupu):
        """
        Initialize a handler.

        If address ni specified kama a string, a UNIX socket ni used. To log to a
        local syslogd, "SysLogHandler(address="/dev/log")" can be used.
        If facility ni sio specified, LOG_USER ni used. If socktype is
        specified kama socket.SOCK_DGRAM ama socket.SOCK_STREAM, that specific
        socket type will be used. For Unix sockets, you can also specify a
        socktype of Tupu, kwenye which case socket.SOCK_DGRAM will be used, falling
        back to socket.SOCK_STREAM.
        """
        logging.Handler.__init__(self)

        self.address = address
        self.facility = facility
        self.socktype = socktype

        ikiwa isinstance(address, str):
            self.unixsocket = Kweli
            # Syslog server may be unavailable during handler initialisation.
            # C's openlog() function also ignores connection errors.
            # Moreover, we ignore these errors wakati logging, so it sio worse
            # to ignore it also here.
            jaribu:
                self._connect_unixsocket(address)
            tatizo OSError:
                pita
        isipokua:
            self.unixsocket = Uongo
            ikiwa socktype ni Tupu:
                socktype = socket.SOCK_DGRAM
            host, port = address
            ress = socket.getaddrinfo(host, port, 0, socktype)
            ikiwa sio ress:
                ashiria OSError("getaddrinfo returns an empty list")
            kila res kwenye ress:
                af, socktype, proto, _, sa = res
                err = sock = Tupu
                jaribu:
                    sock = socket.socket(af, socktype, proto)
                    ikiwa socktype == socket.SOCK_STREAM:
                        sock.connect(sa)
                    koma
                tatizo OSError kama exc:
                    err = exc
                    ikiwa sock ni sio Tupu:
                        sock.close()
            ikiwa err ni sio Tupu:
                ashiria err
            self.socket = sock
            self.socktype = socktype

    eleza _connect_unixsocket(self, address):
        use_socktype = self.socktype
        ikiwa use_socktype ni Tupu:
            use_socktype = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_UNIX, use_socktype)
        jaribu:
            self.socket.connect(address)
            # it worked, so set self.socktype to the used type
            self.socktype = use_socktype
        tatizo OSError:
            self.socket.close()
            ikiwa self.socktype ni sio Tupu:
                # user didn't specify falling back, so fail
                raise
            use_socktype = socket.SOCK_STREAM
            self.socket = socket.socket(socket.AF_UNIX, use_socktype)
            jaribu:
                self.socket.connect(address)
                # it worked, so set self.socktype to the used type
                self.socktype = use_socktype
            tatizo OSError:
                self.socket.close()
                raise

    eleza encodePriority(self, facility, priority):
        """
        Encode the facility na priority. You can pita kwenye strings ama
        integers - ikiwa strings are pitaed, the facility_names na
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
        jaribu:
            self.socket.close()
            logging.Handler.close(self)
        mwishowe:
            self.release()

    eleza mapPriority(self, levelName):
        """
        Map a logging level name to a key kwenye the priority_names map.
        This ni useful kwenye two scenarios: when custom levels are being
        used, na kwenye the case where you can't do a straightforward
        mapping by lowercasing the logging level name because of locale-
        specific issues (see SF #1524081).
        """
        rudisha self.priority_map.get(levelName, "warning")

    ident = ''          # prepended to all messages
    append_nul = Kweli   # some old syslog daemons expect a NUL terminator

    eleza emit(self, record):
        """
        Emit a record.

        The record ni formatted, na then sent to the syslog server. If
        exception information ni present, it ni NOT sent to the server.
        """
        jaribu:
            msg = self.format(record)
            ikiwa self.ident:
                msg = self.ident + msg
            ikiwa self.append_nul:
                msg += '\000'

            # We need to convert record level to lowercase, maybe this will
            # change kwenye the future.
            prio = '<%d>' % self.encodePriority(self.facility,
                                                self.mapPriority(record.levelname))
            prio = prio.encode('utf-8')
            # Message ni a string. Convert to bytes kama required by RFC 5424
            msg = msg.encode('utf-8')
            msg = prio + msg
            ikiwa self.unixsocket:
                jaribu:
                    self.socket.send(msg)
                tatizo OSError:
                    self.socket.close()
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            lasivyo self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            isipokua:
                self.socket.sendall(msg)
        tatizo Exception:
            self.handleError(record)

kundi SMTPHandler(logging.Handler):
    """
    A handler kundi which sends an SMTP email kila each logging event.
    """
    eleza __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=Tupu, secure=Tupu, timeout=5.0):
        """
        Initialize the handler.

        Initialize the instance ukijumuisha the kutoka na to addresses na subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format kila the mailhost argument. To specify
        authentication credentials, supply a (username, password) tuple
        kila the credentials argument. To specify the use of a secure
        protocol (TLS), pita kwenye a tuple kila the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, ama a single-value tuple ukijumuisha the name
        of a keyfile, ama a 2-value tuple ukijumuisha the names of the keyfile na
        certificate file. (This tuple ni pitaed to the `starttls` method).
        A timeout kwenye seconds can be specified kila the SMTP connection (the
        default ni one second).
        """
        logging.Handler.__init__(self)
        ikiwa isinstance(mailhost, (list, tuple)):
            self.mailhost, self.mailport = mailhost
        isipokua:
            self.mailhost, self.mailport = mailhost, Tupu
        ikiwa isinstance(credentials, (list, tuple)):
            self.username, self.password = credentials
        isipokua:
            self.username = Tupu
        self.fromaddr = fromaddr
        ikiwa isinstance(toaddrs, str):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure
        self.timeout = timeout

    eleza getSubject(self, record):
        """
        Determine the subject kila the email.

        If you want to specify a subject line which ni record-dependent,
        override this method.
        """
        rudisha self.subject

    eleza emit(self, record):
        """
        Emit a record.

        Format the record na send it to the specified addressees.
        """
        jaribu:
            agiza smtplib
            kutoka email.message agiza EmailMessage
            agiza email.utils

            port = self.mailport
            ikiwa sio port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port, timeout=self.timeout)
            msg = EmailMessage()
            msg['From'] = self.fromaddr
            msg['To'] = ','.join(self.toaddrs)
            msg['Subject'] = self.getSubject(record)
            msg['Date'] = email.utils.localtime()
            msg.set_content(self.format(record))
            ikiwa self.username:
                ikiwa self.secure ni sio Tupu:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.send_message(msg)
            smtp.quit()
        tatizo Exception:
            self.handleError(record)

kundi NTEventLogHandler(logging.Handler):
    """
    A handler kundi which sends events to the NT Event Log. Adds a
    registry entry kila the specified application name. If no dllname is
    provided, win32service.pyd (which contains some basic message
    placeholders) ni used. Note that use of these placeholders will make
    your event logs big, kama the entire message source ni held kwenye the log.
    If you want slimmer logs, you have to pita kwenye the name of your own DLL
    which contains the message definitions you want to use kwenye the event log.
    """
    eleza __init__(self, appname, dllname=Tupu, logtype="Application"):
        logging.Handler.__init__(self)
        jaribu:
            agiza win32evtlogutil, win32evtlog
            self.appname = appname
            self._welu = win32evtlogutil
            ikiwa sio dllname:
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
        tatizo ImportError:
            andika("The Python Win32 extensions kila NT (service, event "\
                        "logging) appear sio to be available.")
            self._welu = Tupu

    eleza getMessageID(self, record):
        """
        Return the message ID kila the event record. If you are using your
        own messages, you could do this by having the msg pitaed to the
        logger being an ID rather than a formatting string. Then, kwenye here,
        you could use a dictionary lookup to get the message ID. This
        version returns 1, which ni the base message ID kwenye win32service.pyd.
        """
        rudisha 1

    eleza getEventCategory(self, record):
        """
        Return the event category kila the record.

        Override this ikiwa you want to specify your own categories. This version
        returns 0.
        """
        rudisha 0

    eleza getEventType(self, record):
        """
        Return the event type kila the record.

        Override this ikiwa you want to specify your own types. This version does
        a mapping using the handler's typemap attribute, which ni set up kwenye
        __init__() to a dictionary which contains mappings kila DEBUG, INFO,
        WARNING, ERROR na CRITICAL. If you are using your own levels you will
        either need to override this method ama place a suitable dictionary kwenye
        the handler's typemap attribute.
        """
        rudisha self.typemap.get(record.levelno, self.deftype)

    eleza emit(self, record):
        """
        Emit a record.

        Determine the message ID, event category na event type. Then
        log the message kwenye the NT event log.
        """
        ikiwa self._welu:
            jaribu:
                id = self.getMessageID(record)
                cat = self.getEventCategory(record)
                type = self.getEventType(record)
                msg = self.format(record)
                self._welu.ReportEvent(self.appname, id, cat, type, [msg])
            tatizo Exception:
                self.handleError(record)

    eleza close(self):
        """
        Clean up this handler.

        You can remove the application name kutoka the registry kama a
        source of event log entries. However, ikiwa you do this, you will
        sio be able to see the events kama you intended kwenye the Event Log
        Viewer - it needs to be able to access the registry to get the
        DLL name.
        """
        #self._welu.RemoveSourceFromRegistry(self.appname, self.logtype)
        logging.Handler.close(self)

kundi HTTPHandler(logging.Handler):
    """
    A kundi which sends records to a Web server, using either GET ama
    POST semantics.
    """
    eleza __init__(self, host, url, method="GET", secure=Uongo, credentials=Tupu,
                 context=Tupu):
        """
        Initialize the instance ukijumuisha the host, the request URL, na the method
        ("GET" ama "POST")
        """
        logging.Handler.__init__(self)
        method = method.upper()
        ikiwa method haiko kwenye ["GET", "POST"]:
            ashiria ValueError("method must be GET ama POST")
        ikiwa sio secure na context ni sio Tupu:
            ashiria ValueError("context parameter only makes sense "
                             "ukijumuisha secure=Kweli")
        self.host = host
        self.url = url
        self.method = method
        self.secure = secure
        self.credentials = credentials
        self.context = context

    eleza mapLogRecord(self, record):
        """
        Default implementation of mapping the log record into a dict
        that ni sent kama the CGI data. Overwrite kwenye your class.
        Contributed by Franz Glasner.
        """
        rudisha record.__dict__

    eleza emit(self, record):
        """
        Emit a record.

        Send the record to the Web server kama a percent-encoded dictionary
        """
        jaribu:
            agiza http.client, urllib.parse
            host = self.host
            ikiwa self.secure:
                h = http.client.HTTPSConnection(host, context=self.context)
            isipokua:
                h = http.client.HTTPConnection(host)
            url = self.url
            data = urllib.parse.urlencode(self.mapLogRecord(record))
            ikiwa self.method == "GET":
                ikiwa (url.find('?') >= 0):
                    sep = '&'
                isipokua:
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
            h.getresponse()    #can't do anything ukijumuisha the result
        tatizo Exception:
            self.handleError(record)

kundi BufferingHandler(logging.Handler):
    """
  A handler kundi which buffers logging records kwenye memory. Whenever each
  record ni added to the buffer, a check ni made to see ikiwa the buffer should
  be flushed. If it should, then flush() ni expected to do what's needed.
    """
    eleza __init__(self, capacity):
        """
        Initialize the handler ukijumuisha the buffer size.
        """
        logging.Handler.__init__(self)
        self.capacity = capacity
        self.buffer = []

    eleza shouldFlush(self, record):
        """
        Should the handler flush its buffer?

        Returns true ikiwa the buffer ni up to capacity. This method can be
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
        jaribu:
            self.buffer = []
        mwishowe:
            self.release()

    eleza close(self):
        """
        Close the handler.

        This version just flushes na chains to the parent class' close().
        """
        jaribu:
            self.flush()
        mwishowe:
            logging.Handler.close(self)

kundi MemoryHandler(BufferingHandler):
    """
    A handler kundi which buffers logging records kwenye memory, periodically
    flushing them to a target handler. Flushing occurs whenever the buffer
    ni full, ama when an event of a certain severity ama greater ni seen.
    """
    eleza __init__(self, capacity, flushLevel=logging.ERROR, target=Tupu,
                 flushOnClose=Kweli):
        """
        Initialize the handler ukijumuisha the buffer size, the level at which
        flushing should occur na an optional target.

        Note that without a target being set either here ama via setTarget(),
        a MemoryHandler ni no use to anyone!

        The ``flushOnClose`` argument ni ``Kweli`` kila backward compatibility
        reasons - the old behaviour ni that when the handler ni closed, the
        buffer ni flushed, even ikiwa the flush level hasn't been exceeded nor the
        capacity exceeded. To prevent this, set ``flushOnClose`` to ``Uongo``.
        """
        BufferingHandler.__init__(self, capacity)
        self.flushLevel = flushLevel
        self.target = target
        # See Issue #26559 kila why this has been added
        self.flushOnClose = flushOnClose

    eleza shouldFlush(self, record):
        """
        Check kila buffer full ama a record at the flushLevel ama higher.
        """
        rudisha (len(self.buffer) >= self.capacity) ama \
                (record.levelno >= self.flushLevel)

    eleza setTarget(self, target):
        """
        Set the target handler kila this handler.
        """
        self.target = target

    eleza flush(self):
        """
        For a MemoryHandler, flushing means just sending the buffered
        records to the target, ikiwa there ni one. Override ikiwa you want
        different behaviour.

        The record buffer ni also cleared by this operation.
        """
        self.acquire()
        jaribu:
            ikiwa self.target:
                kila record kwenye self.buffer:
                    self.target.handle(record)
                self.buffer = []
        mwishowe:
            self.release()

    eleza close(self):
        """
        Flush, ikiwa appropriately configured, set the target to Tupu na lose the
        buffer.
        """
        jaribu:
            ikiwa self.flushOnClose:
                self.flush()
        mwishowe:
            self.acquire()
            jaribu:
                self.target = Tupu
                BufferingHandler.close(self)
            mwishowe:
                self.release()


kundi QueueHandler(logging.Handler):
    """
    This handler sends events to a queue. Typically, it would be used together
    ukijumuisha a multiprocessing Queue to centralise logging to file kwenye one process
    (in a multi-process application), so kama to avoid file write contention
    between processes.

    This code ni new kwenye Python 3.2, but this kundi can be copy pasted into
    user code kila use ukijumuisha earlier Python versions.
    """

    eleza __init__(self, queue):
        """
        Initialise an instance, using the pitaed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    eleza enqueue(self, record):
        """
        Enqueue a record.

        The base implementation uses put_nowait. You may want to override
        this method ikiwa you want to use blocking, timeouts ama custom queue
        implementations.
        """
        self.queue.put_nowait(record)

    eleza prepare(self, record):
        """
        Prepares a record kila queuing. The object returned by this method is
        enqueued.

        The base implementation formats the record to merge the message
        na arguments, na removes unpickleable items kutoka the record
        in-place.

        You might want to override this method ikiwa you want to convert
        the record to a dict ama JSON string, ama send a modified copy
        of the record wakati leaving the original intact.
        """
        # The format operation gets traceback text into record.exc_text
        # (ikiwa there's exception data), na also returns the formatted
        # message. We can then use this to replace the original
        # msg + args, kama these might be unpickleable. We also zap the
        # exc_info na exc_text attributes, kama they are no longer
        # needed and, ikiwa sio Tupu, will typically sio be pickleable.
        msg = self.format(record)
        # bpo-35726: make copy of record to avoid affecting other handlers kwenye the chain.
        record = copy.copy(record)
        record.message = msg
        record.msg = msg
        record.args = Tupu
        record.exc_info = Tupu
        record.exc_text = Tupu
        rudisha record

    eleza emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it kila pickling first.
        """
        jaribu:
            self.enqueue(self.prepare(record))
        tatizo Exception:
            self.handleError(record)


kundi QueueListener(object):
    """
    This kundi implements an internal threaded listener which watches for
    LogRecords being added to a queue, removes them na pitaes them to a
    list of handlers kila processing.
    """
    _sentinel = Tupu

    eleza __init__(self, queue, *handlers, respect_handler_level=Uongo):
        """
        Initialise an instance ukijumuisha the specified queue na
        handlers.
        """
        self.queue = queue
        self.handlers = handlers
        self._thread = Tupu
        self.respect_handler_level = respect_handler_level

    eleza dequeue(self, block):
        """
        Dequeue a record na rudisha it, optionally blocking.

        The base implementation uses get. You may want to override this method
        ikiwa you want to use timeouts ama work ukijumuisha custom queue implementations.
        """
        rudisha self.queue.get(block)

    eleza start(self):
        """
        Start the listener.

        This starts up a background thread to monitor the queue for
        LogRecords to process.
        """
        self._thread = t = threading.Thread(target=self._monitor)
        t.daemon = Kweli
        t.start()

    eleza prepare(self, record):
        """
        Prepare a record kila handling.

        This method just returns the pitaed-in record. You may want to
        override this method ikiwa you need to do any custom marshalling ama
        manipulation of the record before pitaing it to the handlers.
        """
        rudisha record

    eleza handle(self, record):
        """
        Handle a record.

        This just loops through the handlers offering them the record
        to handle.
        """
        record = self.prepare(record)
        kila handler kwenye self.handlers:
            ikiwa sio self.respect_handler_level:
                process = Kweli
            isipokua:
                process = record.levelno >= handler.level
            ikiwa process:
                handler.handle(record)

    eleza _monitor(self):
        """
        Monitor the queue kila records, na ask the handler
        to deal ukijumuisha them.

        This method runs on a separate, internal thread.
        The thread will terminate ikiwa it sees a sentinel object kwenye the queue.
        """
        q = self.queue
        has_task_done = hasattr(q, 'task_done')
        wakati Kweli:
            jaribu:
                record = self.dequeue(Kweli)
                ikiwa record ni self._sentinel:
                    ikiwa has_task_done:
                        q.task_done()
                    koma
                self.handle(record)
                ikiwa has_task_done:
                    q.task_done()
            tatizo queue.Empty:
                koma

    eleza enqueue_sentinel(self):
        """
        This ni used to enqueue the sentinel record.

        The base implementation uses put_nowait. You may want to override this
        method ikiwa you want to use timeouts ama work ukijumuisha custom queue
        implementations.
        """
        self.queue.put_nowait(self._sentinel)

    eleza stop(self):
        """
        Stop the listener.

        This asks the thread to terminate, na then waits kila it to do so.
        Note that ikiwa you don't call this before your application exits, there
        may be some records still left on the queue, which won't be processed.
        """
        self.enqueue_sentinel()
        self._thread.join()
        self._thread = Tupu
