kutoka collections.abc agiza Sequence, Iterable
kutoka functools agiza total_ordering
agiza fnmatch
agiza linecache
agiza os.path
agiza pickle

# Import types na functions implemented kwenye C
kutoka _tracemalloc agiza *
kutoka _tracemalloc agiza _get_object_traceback, _get_traces


eleza _format_size(size, sign):
    kila unit kwenye ('B', 'KiB', 'MiB', 'GiB', 'TiB'):
        ikiwa abs(size) < 100 na unit != 'B':
            # 3 digits (xx.x UNIT)
            ikiwa sign:
                rudisha "%+.1f %s" % (size, unit)
            isipokua:
                rudisha "%.1f %s" % (size, unit)
        ikiwa abs(size) < 10 * 1024 ama unit == 'TiB':
            # 4 ama 5 digits (xxxx UNIT)
            ikiwa sign:
                rudisha "%+.0f %s" % (size, unit)
            isipokua:
                rudisha "%.0f %s" % (size, unit)
        size /= 1024


kundi Statistic:
    """
    Statistic difference on memory allocations between two Snapshot instance.
    """

    __slots__ = ('traceback', 'size', 'count')

    eleza __init__(self, traceback, size, count):
        self.traceback = traceback
        self.size = size
        self.count = count

    eleza __hash__(self):
        rudisha hash((self.traceback, self.size, self.count))

    eleza __eq__(self, other):
        rudisha (self.traceback == other.traceback
                na self.size == other.size
                na self.count == other.count)

    eleza __str__(self):
        text = ("%s: size=%s, count=%i"
                 % (self.traceback,
                    _format_size(self.size, Uongo),
                    self.count))
        ikiwa self.count:
            average = self.size / self.count
            text += ", average=%s" % _format_size(average, Uongo)
        rudisha text

    eleza __repr__(self):
        rudisha ('<Statistic traceback=%r size=%i count=%i>'
                % (self.traceback, self.size, self.count))

    eleza _sort_key(self):
        rudisha (self.size, self.count, self.traceback)


kundi StatisticDiff:
    """
    Statistic difference on memory allocations between an old na a new
    Snapshot instance.
    """
    __slots__ = ('traceback', 'size', 'size_diff', 'count', 'count_diff')

    eleza __init__(self, traceback, size, size_diff, count, count_diff):
        self.traceback = traceback
        self.size = size
        self.size_diff = size_diff
        self.count = count
        self.count_diff = count_diff

    eleza __hash__(self):
        rudisha hash((self.traceback, self.size, self.size_diff,
                     self.count, self.count_diff))

    eleza __eq__(self, other):
        rudisha (self.traceback == other.traceback
                na self.size == other.size
                na self.size_diff == other.size_diff
                na self.count == other.count
                na self.count_diff == other.count_diff)

    eleza __str__(self):
        text = ("%s: size=%s (%s), count=%i (%+i)"
                % (self.traceback,
                   _format_size(self.size, Uongo),
                   _format_size(self.size_diff, Kweli),
                   self.count,
                   self.count_diff))
        ikiwa self.count:
            average = self.size / self.count
            text += ", average=%s" % _format_size(average, Uongo)
        rudisha text

    eleza __repr__(self):
        rudisha ('<StatisticDiff traceback=%r size=%i (%+i) count=%i (%+i)>'
                % (self.traceback, self.size, self.size_diff,
                   self.count, self.count_diff))

    eleza _sort_key(self):
        rudisha (abs(self.size_diff), self.size,
                abs(self.count_diff), self.count,
                self.traceback)


eleza _compare_grouped_stats(old_group, new_group):
    statistics = []
    kila traceback, stat kwenye new_group.items():
        previous = old_group.pop(traceback, Tupu)
        ikiwa previous ni sio Tupu:
            stat = StatisticDiff(traceback,
                                 stat.size, stat.size - previous.size,
                                 stat.count, stat.count - previous.count)
        isipokua:
            stat = StatisticDiff(traceback,
                                 stat.size, stat.size,
                                 stat.count, stat.count)
        statistics.append(stat)

    kila traceback, stat kwenye old_group.items():
        stat = StatisticDiff(traceback, 0, -stat.size, 0, -stat.count)
        statistics.append(stat)
    rudisha statistics


@total_ordering
kundi Frame:
    """
    Frame of a traceback.
    """
    __slots__ = ("_frame",)

    eleza __init__(self, frame):
        # frame ni a tuple: (filename: str, lineno: int)
        self._frame = frame

    @property
    eleza filename(self):
        rudisha self._frame[0]

    @property
    eleza lineno(self):
        rudisha self._frame[1]

    eleza __eq__(self, other):
        rudisha (self._frame == other._frame)

    eleza __lt__(self, other):
        rudisha (self._frame < other._frame)

    eleza __hash__(self):
        rudisha hash(self._frame)

    eleza __str__(self):
        rudisha "%s:%s" % (self.filename, self.lineno)

    eleza __repr__(self):
        rudisha "<Frame filename=%r lineno=%r>" % (self.filename, self.lineno)


@total_ordering
kundi Traceback(Sequence):
    """
    Sequence of Frame instances sorted kutoka the oldest frame
    to the most recent frame.
    """
    __slots__ = ("_frames",)

    eleza __init__(self, frames):
        Sequence.__init__(self)
        # frames ni a tuple of frame tuples: see Frame constructor kila the
        # format of a frame tuple; it ni reversed, because _tracemalloc
        # returns frames sorted kutoka most recent to oldest, but the
        # Python API expects oldest to most recent
        self._frames = tuple(reversed(frames))

    eleza __len__(self):
        rudisha len(self._frames)

    eleza __getitem__(self, index):
        ikiwa isinstance(index, slice):
            rudisha tuple(Frame(trace) kila trace kwenye self._frames[index])
        isipokua:
            rudisha Frame(self._frames[index])

    eleza __contains__(self, frame):
        rudisha frame._frame kwenye self._frames

    eleza __hash__(self):
        rudisha hash(self._frames)

    eleza __eq__(self, other):
        rudisha (self._frames == other._frames)

    eleza __lt__(self, other):
        rudisha (self._frames < other._frames)

    eleza __str__(self):
        rudisha str(self[0])

    eleza __repr__(self):
        rudisha "<Traceback %r>" % (tuple(self),)

    eleza format(self, limit=Tupu, most_recent_first=Uongo):
        lines = []
        ikiwa limit ni sio Tupu:
            ikiwa limit > 0:
                frame_slice = self[-limit:]
            isipokua:
                frame_slice = self[:limit]
        isipokua:
            frame_slice = self

        ikiwa most_recent_first:
            frame_slice = reversed(frame_slice)
        kila frame kwenye frame_slice:
            lines.append('  File "%s", line %s'
                         % (frame.filename, frame.lineno))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            ikiwa line:
                lines.append('    %s' % line)
        rudisha lines


eleza get_object_traceback(obj):
    """
    Get the traceback where the Python object *obj* was allocated.
    Return a Traceback instance.

    Return Tupu ikiwa the tracemalloc module ni sio tracing memory allocations or
    did sio trace the allocation of the object.
    """
    frames = _get_object_traceback(obj)
    ikiwa frames ni sio Tupu:
        rudisha Traceback(frames)
    isipokua:
        rudisha Tupu


kundi Trace:
    """
    Trace of a memory block.
    """
    __slots__ = ("_trace",)

    eleza __init__(self, trace):
        # trace ni a tuple: (domain: int, size: int, traceback: tuple).
        # See Traceback constructor kila the format of the traceback tuple.
        self._trace = trace

    @property
    eleza domain(self):
        rudisha self._trace[0]

    @property
    eleza size(self):
        rudisha self._trace[1]

    @property
    eleza traceback(self):
        rudisha Traceback(self._trace[2])

    eleza __eq__(self, other):
        rudisha (self._trace == other._trace)

    eleza __hash__(self):
        rudisha hash(self._trace)

    eleza __str__(self):
        rudisha "%s: %s" % (self.traceback, _format_size(self.size, Uongo))

    eleza __repr__(self):
        rudisha ("<Trace domain=%s size=%s, traceback=%r>"
                % (self.domain, _format_size(self.size, Uongo), self.traceback))


kundi _Traces(Sequence):
    eleza __init__(self, traces):
        Sequence.__init__(self)
        # traces ni a tuple of trace tuples: see Trace constructor
        self._traces = traces

    eleza __len__(self):
        rudisha len(self._traces)

    eleza __getitem__(self, index):
        ikiwa isinstance(index, slice):
            rudisha tuple(Trace(trace) kila trace kwenye self._traces[index])
        isipokua:
            rudisha Trace(self._traces[index])

    eleza __contains__(self, trace):
        rudisha trace._trace kwenye self._traces

    eleza __eq__(self, other):
        rudisha (self._traces == other._traces)

    eleza __repr__(self):
        rudisha "<Traces len=%s>" % len(self)


eleza _normalize_filename(filename):
    filename = os.path.normcase(filename)
    ikiwa filename.endswith('.pyc'):
        filename = filename[:-1]
    rudisha filename


kundi BaseFilter:
    eleza __init__(self, inclusive):
        self.inclusive = inclusive

    eleza _match(self, trace):
         ashiria NotImplementedError


kundi Filter(BaseFilter):
    eleza __init__(self, inclusive, filename_pattern,
                 lineno=Tupu, all_frames=Uongo, domain=Tupu):
        super().__init__(inclusive)
        self.inclusive = inclusive
        self._filename_pattern = _normalize_filename(filename_pattern)
        self.lineno = lineno
        self.all_frames = all_frames
        self.domain = domain

    @property
    eleza filename_pattern(self):
        rudisha self._filename_pattern

    eleza _match_frame_impl(self, filename, lineno):
        filename = _normalize_filename(filename)
        ikiwa sio fnmatch.fnmatch(filename, self._filename_pattern):
            rudisha Uongo
        ikiwa self.lineno ni Tupu:
            rudisha Kweli
        isipokua:
            rudisha (lineno == self.lineno)

    eleza _match_frame(self, filename, lineno):
        rudisha self._match_frame_impl(filename, lineno) ^ (not self.inclusive)

    eleza _match_traceback(self, traceback):
        ikiwa self.all_frames:
            ikiwa any(self._match_frame_impl(filename, lineno)
                   kila filename, lineno kwenye traceback):
                rudisha self.inclusive
            isipokua:
                rudisha (not self.inclusive)
        isipokua:
            filename, lineno = traceback[0]
            rudisha self._match_frame(filename, lineno)

    eleza _match(self, trace):
        domain, size, traceback = trace
        res = self._match_traceback(traceback)
        ikiwa self.domain ni sio Tupu:
            ikiwa self.inclusive:
                rudisha res na (domain == self.domain)
            isipokua:
                rudisha res ama (domain != self.domain)
        rudisha res


kundi DomainFilter(BaseFilter):
    eleza __init__(self, inclusive, domain):
        super().__init__(inclusive)
        self._domain = domain

    @property
    eleza domain(self):
        rudisha self._domain

    eleza _match(self, trace):
        domain, size, traceback = trace
        rudisha (domain == self.domain) ^ (not self.inclusive)


kundi Snapshot:
    """
    Snapshot of traces of memory blocks allocated by Python.
    """

    eleza __init__(self, traces, traceback_limit):
        # traces ni a tuple of trace tuples: see _Traces constructor for
        # the exact format
        self.traces = _Traces(traces)
        self.traceback_limit = traceback_limit

    eleza dump(self, filename):
        """
        Write the snapshot into a file.
        """
        ukijumuisha open(filename, "wb") as fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    eleza load(filename):
        """
        Load a snapshot kutoka a file.
        """
        ukijumuisha open(filename, "rb") as fp:
            rudisha pickle.load(fp)

    eleza _filter_trace(self, include_filters, exclude_filters, trace):
        ikiwa include_filters:
            ikiwa sio any(trace_filter._match(trace)
                       kila trace_filter kwenye include_filters):
                rudisha Uongo
        ikiwa exclude_filters:
            ikiwa any(not trace_filter._match(trace)
                   kila trace_filter kwenye exclude_filters):
                rudisha Uongo
        rudisha Kweli

    eleza filter_traces(self, filters):
        """
        Create a new Snapshot instance ukijumuisha a filtered traces sequence, filters
        ni a list of Filter ama DomainFilter instances.  If filters ni an empty
        list, rudisha a new Snapshot instance ukijumuisha a copy of the traces.
        """
        ikiwa sio isinstance(filters, Iterable):
             ashiria TypeError("filters must be a list of filters, sio %s"
                            % type(filters).__name__)
        ikiwa filters:
            include_filters = []
            exclude_filters = []
            kila trace_filter kwenye filters:
                ikiwa trace_filter.inclusive:
                    include_filters.append(trace_filter)
                isipokua:
                    exclude_filters.append(trace_filter)
            new_traces = [trace kila trace kwenye self.traces._traces
                          ikiwa self._filter_trace(include_filters,
                                                exclude_filters,
                                                trace)]
        isipokua:
            new_traces = self.traces._traces.copy()
        rudisha Snapshot(new_traces, self.traceback_limit)

    eleza _group_by(self, key_type, cumulative):
        ikiwa key_type sio kwenye ('traceback', 'filename', 'lineno'):
             ashiria ValueError("unknown key_type: %r" % (key_type,))
        ikiwa cumulative na key_type sio kwenye ('lineno', 'filename'):
             ashiria ValueError("cumulative mode cannot by used "
                             "ukijumuisha key type %r" % key_type)

        stats = {}
        tracebacks = {}
        ikiwa sio cumulative:
            kila trace kwenye self.traces._traces:
                domain, size, trace_traceback = trace
                jaribu:
                    traceback = tracebacks[trace_traceback]
                except KeyError:
                    ikiwa key_type == 'traceback':
                        frames = trace_traceback
                    elikiwa key_type == 'lineno':
                        frames = trace_traceback[:1]
                    isipokua: # key_type == 'filename':
                        frames = ((trace_traceback[0][0], 0),)
                    traceback = Traceback(frames)
                    tracebacks[trace_traceback] = traceback
                jaribu:
                    stat = stats[traceback]
                    stat.size += size
                    stat.count += 1
                except KeyError:
                    stats[traceback] = Statistic(traceback, size, 1)
        isipokua:
            # cumulative statistics
            kila trace kwenye self.traces._traces:
                domain, size, trace_traceback = trace
                kila frame kwenye trace_traceback:
                    jaribu:
                        traceback = tracebacks[frame]
                    except KeyError:
                        ikiwa key_type == 'lineno':
                            frames = (frame,)
                        isipokua: # key_type == 'filename':
                            frames = ((frame[0], 0),)
                        traceback = Traceback(frames)
                        tracebacks[frame] = traceback
                    jaribu:
                        stat = stats[traceback]
                        stat.size += size
                        stat.count += 1
                    except KeyError:
                        stats[traceback] = Statistic(traceback, size, 1)
        rudisha stats

    eleza statistics(self, key_type, cumulative=Uongo):
        """
        Group statistics by key_type. Return a sorted list of Statistic
        instances.
        """
        grouped = self._group_by(key_type, cumulative)
        statistics = list(grouped.values())
        statistics.sort(reverse=Kweli, key=Statistic._sort_key)
        rudisha statistics

    eleza compare_to(self, old_snapshot, key_type, cumulative=Uongo):
        """
        Compute the differences ukijumuisha an old snapshot old_snapshot. Get
        statistics as a sorted list of StatisticDiff instances, grouped by
        group_by.
        """
        new_group = self._group_by(key_type, cumulative)
        old_group = old_snapshot._group_by(key_type, cumulative)
        statistics = _compare_grouped_stats(old_group, new_group)
        statistics.sort(reverse=Kweli, key=StatisticDiff._sort_key)
        rudisha statistics


eleza take_snapshot():
    """
    Take a snapshot of traces of memory blocks allocated by Python.
    """
    ikiwa sio is_tracing():
         ashiria RuntimeError("the tracemalloc module must be tracing memory "
                           "allocations to take a snapshot")
    traces = _get_traces()
    traceback_limit = get_traceback_limit()
    rudisha Snapshot(traces, traceback_limit)
