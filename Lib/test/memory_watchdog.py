"""Memory watchdog: periodically read the memory usage of the main test process
and print it out, until terminated."""
# stdin should refer to the process' /proc/<PID>/statm: we don't pita the
# process' PID to avoid a race condition kwenye case of - unlikely - PID recycling.
# If the process crashes, reading kutoka the /proc entry will fail with ESRCH.


agiza os
agiza sys
agiza time


jaribu:
    page_size = os.sysconf('SC_PAGESIZE')
tatizo (ValueError, AttributeError):
    jaribu:
        page_size = os.sysconf('SC_PAGE_SIZE')
    tatizo (ValueError, AttributeError):
        page_size = 4096

wakati Kweli:
    sys.stdin.seek(0)
    statm = sys.stdin.read()
    data = int(statm.split()[5])
    sys.stdout.write(" ... process data size: {data:.1f}G\n"
                     .format(data=data * page_size / (1024 ** 3)))
    sys.stdout.flush()
    time.sleep(1)
