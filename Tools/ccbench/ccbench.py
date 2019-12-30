# This file should be kept compatible ukijumuisha both Python 2.6 na Python >= 3.0.

kutoka __future__ agiza division
kutoka __future__ agiza print_function

"""
ccbench, a Python concurrency benchmark.
"""

agiza time
agiza os
agiza sys
agiza itertools
agiza threading
agiza subprocess
agiza socket
kutoka optparse agiza OptionParser, SUPPRESS_HELP
agiza platform

# Compatibility
jaribu:
    xrange
tatizo NameError:
    xrange = range

jaribu:
    map = itertools.imap
tatizo AttributeError:
    pita


THROUGHPUT_DURATION = 2.0

LATENCY_PING_INTERVAL = 0.1
LATENCY_DURATION = 2.0

BANDWIDTH_PACKET_SIZE = 1024
BANDWIDTH_DURATION = 2.0


eleza task_pidigits():
    """Pi calculation (Python)"""
    _map = map
    _count = itertools.count
    _islice = itertools.islice

    eleza calc_ndigits(n):
        # From http://shootout.alioth.debian.org/
        eleza gen_x():
            rudisha _map(lambda k: (k, 4*k + 2, 0, 2*k + 1), _count(1))

        eleza compose(a, b):
            aq, ar, as_, at = a
            bq, br, bs, bt = b
            rudisha (aq * bq,
                    aq * br + ar * bt,
                    as_ * bq + at * bs,
                    as_ * br + at * bt)

        eleza extract(z, j):
            q, r, s, t = z
            rudisha (q*j + r) // (s*j + t)

        eleza pi_digits():
            z = (1, 0, 0, 1)
            x = gen_x()
            wakati 1:
                y = extract(z, 3)
                wakati y != extract(z, 4):
                    z = compose(z, next(x))
                    y = extract(z, 3)
                z = compose((10, -10*y, 0, 1), z)
                tuma y

        rudisha list(_islice(pi_digits(), n))

    rudisha calc_ndigits, (50, )

eleza task_regex():
    """regular expression (C)"""
    # XXX this task gives horrendous latency results.
    agiza re
    # Taken kutoka the `inspect` module
    pat = re.compile(r'^(\s*def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)', re.MULTILINE)
    ukijumuisha open(__file__, "r") kama f:
        arg = f.read(2000)

    eleza findall(s):
        t = time.time()
        jaribu:
            rudisha pat.findall(s)
        mwishowe:
            andika(time.time() - t)
    rudisha pat.findall, (arg, )

eleza task_sort():
    """list sorting (C)"""
    eleza list_sort(l):
        l = l[::-1]
        l.sort()

    rudisha list_sort, (list(range(1000)), )

eleza task_compress_zlib():
    """zlib compression (C)"""
    agiza zlib
    ukijumuisha open(__file__, "rb") kama f:
        arg = f.read(5000) * 3

    eleza compress(s):
        zlib.decompress(zlib.compress(s, 5))
    rudisha compress, (arg, )

eleza task_compress_bz2():
    """bz2 compression (C)"""
    agiza bz2
    ukijumuisha open(__file__, "rb") kama f:
        arg = f.read(3000) * 2

    eleza compress(s):
        bz2.compress(s)
    rudisha compress, (arg, )

eleza task_hashing():
    """SHA1 hashing (C)"""
    agiza hashlib
    ukijumuisha open(__file__, "rb") kama f:
        arg = f.read(5000) * 30

    eleza compute(s):
        hashlib.sha1(s).digest()
    rudisha compute, (arg, )


throughput_tasks = [task_pidigits, task_regex]
kila mod kwenye 'bz2', 'hashlib':
    jaribu:
        globals()[mod] = __import__(mod)
    tatizo ImportError:
        globals()[mod] = Tupu

# For whatever reasons, zlib gives irregular results, so we prefer bz2 ama
# hashlib ikiwa available.
# (NOTE: hashlib releases the GIL kutoka 2.7 na 3.1 onwards)
ikiwa bz2 ni sio Tupu:
    throughput_tasks.append(task_compress_bz2)
lasivyo hashlib ni sio Tupu:
    throughput_tasks.append(task_hashing)
isipokua:
    throughput_tasks.append(task_compress_zlib)

latency_tasks = throughput_tasks
bandwidth_tasks = [task_pidigits]


kundi TimedLoop:
    eleza __init__(self, func, args):
        self.func = func
        self.args = args

    eleza __call__(self, start_time, min_duration, end_event, do_yield=Uongo):
        step = 20
        niters = 0
        duration = 0.0
        _time = time.time
        _sleep = time.sleep
        _func = self.func
        _args = self.args
        t1 = start_time
        wakati Kweli:
            kila i kwenye range(step):
                _func(*_args)
            t2 = _time()
            # If another thread terminated, the current measurement ni invalid
            # => rudisha the previous one.
            ikiwa end_event:
                rudisha niters, duration
            niters += step
            duration = t2 - start_time
            ikiwa duration >= min_duration:
                end_event.append(Tupu)
                rudisha niters, duration
            ikiwa t2 - t1 < 0.01:
                # Minimize interference of measurement on overall runtime
                step = step * 3 // 2
            lasivyo do_yield:
                # OS scheduling of Python threads ni sometimes so bad that we
                # have to force thread switching ourselves, otherwise we get
                # completely useless results.
                _sleep(0.0001)
            t1 = t2


eleza run_throughput_test(func, args, nthreads):
    assert nthreads >= 1

    # Warm up
    func(*args)

    results = []
    loop = TimedLoop(func, args)
    end_event = []

    ikiwa nthreads == 1:
        # Pure single-threaded performance, without any switching ama
        # synchronization overhead.
        start_time = time.time()
        results.append(loop(start_time, THROUGHPUT_DURATION,
                            end_event, do_yield=Uongo))
        rudisha results

    started = Uongo
    ready_cond = threading.Condition()
    start_cond = threading.Condition()
    ready = []

    eleza run():
        ukijumuisha ready_cond:
            ready.append(Tupu)
            ready_cond.notify()
        ukijumuisha start_cond:
            wakati sio started:
                start_cond.wait()
        results.append(loop(start_time, THROUGHPUT_DURATION,
                            end_event, do_yield=Kweli))

    threads = []
    kila i kwenye range(nthreads):
        threads.append(threading.Thread(target=run))
    kila t kwenye threads:
        t.setDaemon(Kweli)
        t.start()
    # We don't want measurements to include thread startup overhead,
    # so we arrange kila timing to start after all threads are ready.
    ukijumuisha ready_cond:
        wakati len(ready) < nthreads:
            ready_cond.wait()
    ukijumuisha start_cond:
        start_time = time.time()
        started = Kweli
        start_cond.notify(nthreads)
    kila t kwenye threads:
        t.join()

    rudisha results

eleza run_throughput_tests(max_threads):
    kila task kwenye throughput_tasks:
        andika(task.__doc__)
        andika()
        func, args = task()
        nthreads = 1
        baseline_speed = Tupu
        wakati nthreads <= max_threads:
            results = run_throughput_test(func, args, nthreads)
            # Taking the max duration rather than average gives pessimistic
            # results rather than optimistic.
            speed = sum(r[0] kila r kwenye results) / max(r[1] kila r kwenye results)
            andika("threads=%d: %d" % (nthreads, speed), end="")
            ikiwa baseline_speed ni Tupu:
                andika(" iterations/s.")
                baseline_speed = speed
            isipokua:
                andika(" ( %d %%)" % (speed / baseline_speed * 100))
            nthreads += 1
        andika()


LAT_END = "END"

eleza _sendto(sock, s, addr):
    sock.sendto(s.encode('ascii'), addr)

eleza _recv(sock, n):
    rudisha sock.recv(n).decode('ascii')

eleza latency_client(addr, nb_pings, interval):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    jaribu:
        _time = time.time
        _sleep = time.sleep
        eleza _ping():
            _sendto(sock, "%r\n" % _time(), addr)
        # The first ping signals the parent process that we are ready.
        _ping()
        # We give the parent a bit of time to notice.
        _sleep(1.0)
        kila i kwenye range(nb_pings):
            _sleep(interval)
            _ping()
        _sendto(sock, LAT_END + "\n", addr)
    mwishowe:
        sock.close()

eleza run_latency_client(**kwargs):
    cmd_line = [sys.executable, '-E', os.path.abspath(__file__)]
    cmd_line.extend(['--latclient', repr(kwargs)])
    rudisha subprocess.Popen(cmd_line) #, stdin=subprocess.PIPE,
                            #stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

eleza run_latency_test(func, args, nthreads):
    # Create a listening socket to receive the pings. We use UDP which should
    # be painlessly cross-platform.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    addr = sock.getsockname()

    interval = LATENCY_PING_INTERVAL
    duration = LATENCY_DURATION
    nb_pings = int(duration / interval)

    results = []
    threads = []
    end_event = []
    start_cond = threading.Condition()
    started = Uongo
    ikiwa nthreads > 0:
        # Warm up
        func(*args)

        results = []
        loop = TimedLoop(func, args)
        ready = []
        ready_cond = threading.Condition()

        eleza run():
            ukijumuisha ready_cond:
                ready.append(Tupu)
                ready_cond.notify()
            ukijumuisha start_cond:
                wakati sio started:
                    start_cond.wait()
            loop(start_time, duration * 1.5, end_event, do_yield=Uongo)

        kila i kwenye range(nthreads):
            threads.append(threading.Thread(target=run))
        kila t kwenye threads:
            t.setDaemon(Kweli)
            t.start()
        # Wait kila threads to be ready
        ukijumuisha ready_cond:
            wakati len(ready) < nthreads:
                ready_cond.wait()

    # Run the client na wait kila the first ping(s) to arrive before
    # unblocking the background threads.
    chunks = []
    process = run_latency_client(addr=sock.getsockname(),
                                 nb_pings=nb_pings, interval=interval)
    s = _recv(sock, 4096)
    _time = time.time

    ukijumuisha start_cond:
        start_time = _time()
        started = Kweli
        start_cond.notify(nthreads)

    wakati LAT_END haiko kwenye s:
        s = _recv(sock, 4096)
        t = _time()
        chunks.append((t, s))

    # Tell the background threads to stop.
    end_event.append(Tupu)
    kila t kwenye threads:
        t.join()
    process.wait()
    sock.close()

    kila recv_time, chunk kwenye chunks:
        # NOTE: it ni assumed that a line sent by a client wasn't received
        # kwenye two chunks because the lines are very small.
        kila line kwenye chunk.splitlines():
            line = line.strip()
            ikiwa line na line != LAT_END:
                send_time = eval(line)
                assert isinstance(send_time, float)
                results.append((send_time, recv_time))

    rudisha results

eleza run_latency_tests(max_threads):
    kila task kwenye latency_tasks:
        andika("Background CPU task:", task.__doc__)
        andika()
        func, args = task()
        nthreads = 0
        wakati nthreads <= max_threads:
            results = run_latency_test(func, args, nthreads)
            n = len(results)
            # We andika out milliseconds
            lats = [1000 * (t2 - t1) kila (t1, t2) kwenye results]
            #andika(list(map(int, lats)))
            avg = sum(lats) / n
            dev = (sum((x - avg) ** 2 kila x kwenye lats) / n) ** 0.5
            andika("CPU threads=%d: %d ms. (std dev: %d ms.)" % (nthreads, avg, dev), end="")
            andika()
            #andika("    [... kutoka %d samples]" % n)
            nthreads += 1
        andika()


BW_END = "END"

eleza bandwidth_client(addr, packet_size, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    local_addr = sock.getsockname()
    _time = time.time
    _sleep = time.sleep
    eleza _send_chunk(msg):
        _sendto(sock, ("%r#%s\n" % (local_addr, msg)).rjust(packet_size), addr)
    # We give the parent some time to be ready.
    _sleep(1.0)
    jaribu:
        start_time = _time()
        end_time = start_time + duration * 2.0
        i = 0
        wakati _time() < end_time:
            _send_chunk(str(i))
            s = _recv(sock, packet_size)
            assert len(s) == packet_size
            i += 1
        _send_chunk(BW_END)
    mwishowe:
        sock.close()

eleza run_bandwidth_client(**kwargs):
    cmd_line = [sys.executable, '-E', os.path.abspath(__file__)]
    cmd_line.extend(['--bwclient', repr(kwargs)])
    rudisha subprocess.Popen(cmd_line) #, stdin=subprocess.PIPE,
                            #stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

eleza run_bandwidth_test(func, args, nthreads):
    # Create a listening socket to receive the packets. We use UDP which should
    # be painlessly cross-platform.
    ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_DGRAM) kama sock:
        sock.bind(("127.0.0.1", 0))
        addr = sock.getsockname()

        duration = BANDWIDTH_DURATION
        packet_size = BANDWIDTH_PACKET_SIZE

        results = []
        threads = []
        end_event = []
        start_cond = threading.Condition()
        started = Uongo
        ikiwa nthreads > 0:
            # Warm up
            func(*args)

            results = []
            loop = TimedLoop(func, args)
            ready = []
            ready_cond = threading.Condition()

            eleza run():
                ukijumuisha ready_cond:
                    ready.append(Tupu)
                    ready_cond.notify()
                ukijumuisha start_cond:
                    wakati sio started:
                        start_cond.wait()
                loop(start_time, duration * 1.5, end_event, do_yield=Uongo)

            kila i kwenye range(nthreads):
                threads.append(threading.Thread(target=run))
            kila t kwenye threads:
                t.setDaemon(Kweli)
                t.start()
            # Wait kila threads to be ready
            ukijumuisha ready_cond:
                wakati len(ready) < nthreads:
                    ready_cond.wait()

        # Run the client na wait kila the first packet to arrive before
        # unblocking the background threads.
        process = run_bandwidth_client(addr=addr,
                                       packet_size=packet_size,
                                       duration=duration)
        _time = time.time
        # This will also wait kila the parent to be ready
        s = _recv(sock, packet_size)
        remote_addr = eval(s.partition('#')[0])

        ukijumuisha start_cond:
            start_time = _time()
            started = Kweli
            start_cond.notify(nthreads)

        n = 0
        first_time = Tupu
        wakati sio end_event na BW_END haiko kwenye s:
            _sendto(sock, s, remote_addr)
            s = _recv(sock, packet_size)
            ikiwa first_time ni Tupu:
                first_time = _time()
            n += 1
        end_time = _time()

    end_event.append(Tupu)
    kila t kwenye threads:
        t.join()
    process.kill()

    rudisha (n - 1) / (end_time - first_time)

eleza run_bandwidth_tests(max_threads):
    kila task kwenye bandwidth_tasks:
        andika("Background CPU task:", task.__doc__)
        andika()
        func, args = task()
        nthreads = 0
        baseline_speed = Tupu
        wakati nthreads <= max_threads:
            results = run_bandwidth_test(func, args, nthreads)
            speed = results
            #speed = len(results) * 1.0 / results[-1][0]
            andika("CPU threads=%d: %.1f" % (nthreads, speed), end="")
            ikiwa baseline_speed ni Tupu:
                andika(" packets/s.")
                baseline_speed = speed
            isipokua:
                andika(" ( %d %%)" % (speed / baseline_speed * 100))
            nthreads += 1
        andika()


eleza main():
    usage = "usage: %prog [-h|--help] [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--throughput",
                      action="store_true", dest="throughput", default=Uongo,
                      help="run throughput tests")
    parser.add_option("-l", "--latency",
                      action="store_true", dest="latency", default=Uongo,
                      help="run latency tests")
    parser.add_option("-b", "--bandwidth",
                      action="store_true", dest="bandwidth", default=Uongo,
                      help="run I/O bandwidth tests")
    parser.add_option("-i", "--interval",
                      action="store", type="int", dest="check_interval", default=Tupu,
                      help="sys.setcheckinterval() value")
    parser.add_option("-I", "--switch-interval",
                      action="store", type="float", dest="switch_interval", default=Tupu,
                      help="sys.setswitchinterval() value")
    parser.add_option("-n", "--num-threads",
                      action="store", type="int", dest="nthreads", default=4,
                      help="max number of threads kwenye tests")

    # Hidden option to run the pinging na bandwidth clients
    parser.add_option("", "--latclient",
                      action="store", dest="latclient", default=Tupu,
                      help=SUPPRESS_HELP)
    parser.add_option("", "--bwclient",
                      action="store", dest="bwclient", default=Tupu,
                      help=SUPPRESS_HELP)

    options, args = parser.parse_args()
    ikiwa args:
        parser.error("unexpected arguments")

    ikiwa options.latclient:
        kwargs = eval(options.latclient)
        latency_client(**kwargs)
        rudisha

    ikiwa options.bwclient:
        kwargs = eval(options.bwclient)
        bandwidth_client(**kwargs)
        rudisha

    ikiwa sio options.throughput na sio options.latency na sio options.bandwidth:
        options.throughput = options.latency = options.bandwidth = Kweli
    ikiwa options.check_interval:
        sys.setcheckinterval(options.check_interval)
    ikiwa options.switch_interval:
        sys.setswitchinterval(options.switch_interval)

    andika("== %s %s (%s) ==" % (
        platform.python_implementation(),
        platform.python_version(),
        platform.python_build()[0],
    ))
    # Processor identification often has repeated spaces
    cpu = ' '.join(platform.processor().split())
    andika("== %s %s on '%s' ==" % (
        platform.machine(),
        platform.system(),
        cpu,
    ))
    andika()

    ikiwa options.throughput:
        andika("--- Throughput ---")
        andika()
        run_throughput_tests(options.nthreads)

    ikiwa options.latency:
        andika("--- Latency ---")
        andika()
        run_latency_tests(options.nthreads)

    ikiwa options.bandwidth:
        andika("--- I/O bandwidth ---")
        andika()
        run_bandwidth_tests(options.nthreads)

ikiwa __name__ == "__main__":
    main()
