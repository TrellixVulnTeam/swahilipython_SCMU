"""A generally useful event scheduler class.

Each instance of this kundi manages its own queue.
No multi-threading ni implied; you are supposed to hack that
yourself, ama use a single instance per application.

Each instance ni parametrized ukijumuisha two functions, one that is
supposed to rudisha the current time, one that ni supposed to
implement a delay.  You can implement real-time scheduling by
substituting time na sleep kutoka built-in module time, ama you can
implement simulated time by writing your own functions.  This can
also be used to integrate scheduling ukijumuisha STDWIN events; the delay
function ni allowed to modify the queue.  Time can be expressed as
integers ama floating point numbers, kama long kama it ni consistent.

Events are specified by tuples (time, priority, action, argument, kwargs).
As kwenye UNIX, lower priority numbers mean higher priority; kwenye this
way the queue can be maintained kama a priority queue.  Execution of the
event means calling the action function, pitaing it the argument
sequence kwenye "argument" (remember that kwenye Python, multiple function
arguments are be packed kwenye a sequence) na keyword parameters kwenye "kwargs".
The action function may be an instance method so it
has another way to reference private data (besides global variables).
"""

agiza time
agiza heapq
kutoka collections agiza namedtuple
agiza threading
kutoka time agiza monotonic kama _time

__all__ = ["scheduler"]

kundi Event(namedtuple('Event', 'time, priority, action, argument, kwargs')):
    __slots__ = []
    eleza __eq__(s, o): rudisha (s.time, s.priority) == (o.time, o.priority)
    eleza __lt__(s, o): rudisha (s.time, s.priority) <  (o.time, o.priority)
    eleza __le__(s, o): rudisha (s.time, s.priority) <= (o.time, o.priority)
    eleza __gt__(s, o): rudisha (s.time, s.priority) >  (o.time, o.priority)
    eleza __ge__(s, o): rudisha (s.time, s.priority) >= (o.time, o.priority)

Event.time.__doc__ = ('''Numeric type compatible ukijumuisha the rudisha value of the
timefunc function pitaed to the constructor.''')
Event.priority.__doc__ = ('''Events scheduled kila the same time will be executed
in the order of their priority.''')
Event.action.__doc__ = ('''Executing the event means executing
action(*argument, **kwargs)''')
Event.argument.__doc__ = ('''argument ni a sequence holding the positional
arguments kila the action.''')
Event.kwargs.__doc__ = ('''kwargs ni a dictionary holding the keyword
arguments kila the action.''')

_sentinel = object()

kundi scheduler:

    eleza __init__(self, timefunc=_time, delayfunc=time.sleep):
        """Initialize a new instance, pitaing the time na delay
        functions"""
        self._queue = []
        self._lock = threading.RLock()
        self.timefunc = timefunc
        self.delayfunc = delayfunc

    eleza enterabs(self, time, priority, action, argument=(), kwargs=_sentinel):
        """Enter a new event kwenye the queue at an absolute time.

        Returns an ID kila the event which can be used to remove it,
        ikiwa necessary.

        """
        ikiwa kwargs ni _sentinel:
            kwargs = {}
        event = Event(time, priority, action, argument, kwargs)
        ukijumuisha self._lock:
            heapq.heappush(self._queue, event)
        rudisha event # The ID

    eleza enter(self, delay, priority, action, argument=(), kwargs=_sentinel):
        """A variant that specifies the time kama a relative time.

        This ni actually the more commonly used interface.

        """
        time = self.timefunc() + delay
        rudisha self.enterabs(time, priority, action, argument, kwargs)

    eleza cancel(self, event):
        """Remove an event kutoka the queue.

        This must be presented the ID kama returned by enter().
        If the event ni haiko kwenye the queue, this raises ValueError.

        """
        ukijumuisha self._lock:
            self._queue.remove(event)
            heapq.heapify(self._queue)

    eleza empty(self):
        """Check whether the queue ni empty."""
        ukijumuisha self._lock:
            rudisha sio self._queue

    eleza run(self, blocking=Kweli):
        """Execute events until the queue ni empty.
        If blocking ni Uongo executes the scheduled events due to
        expire soonest (ikiwa any) na then rudisha the deadline of the
        next scheduled call kwenye the scheduler.

        When there ni a positive delay until the first event, the
        delay function ni called na the event ni left kwenye the queue;
        otherwise, the event ni removed kutoka the queue na executed
        (its action function ni called, pitaing it the argument).  If
        the delay function returns prematurely, it ni simply
        restarted.

        It ni legal kila both the delay function na the action
        function to modify the queue ama to ashiria an exception;
        exceptions are sio caught but the scheduler's state remains
        well-defined so run() may be called again.

        A questionable hack ni added to allow other threads to run:
        just after an event ni executed, a delay of 0 ni executed, to
        avoid monopolizing the CPU when other threads are also
        runnable.

        """
        # localize variable access to minimize overhead
        # na to improve thread safety
        lock = self._lock
        q = self._queue
        delayfunc = self.delayfunc
        timefunc = self.timefunc
        pop = heapq.heappop
        wakati Kweli:
            ukijumuisha lock:
                ikiwa sio q:
                    koma
                time, priority, action, argument, kwargs = q[0]
                now = timefunc()
                ikiwa time > now:
                    delay = Kweli
                isipokua:
                    delay = Uongo
                    pop(q)
            ikiwa delay:
                ikiwa sio blocking:
                    rudisha time - now
                delayfunc(time - now)
            isipokua:
                action(*argument, **kwargs)
                delayfunc(0)   # Let other threads run

    @property
    eleza queue(self):
        """An ordered list of upcoming events.

        Events are named tuples ukijumuisha fields for:
            time, priority, action, arguments, kwargs

        """
        # Use heapq to sort the queue rather than using 'sorted(self._queue)'.
        # With heapq, two events scheduled at the same time will show in
        # the actual order they would be retrieved.
        ukijumuisha self._lock:
            events = self._queue[:]
        rudisha list(map(heapq.heappop, [events]*len(events)))
