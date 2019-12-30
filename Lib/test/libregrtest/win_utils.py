agiza _winapi
agiza math
agiza msvcrt
agiza os
agiza subprocess
agiza uuid
agiza winreg
kutoka test agiza support
kutoka test.libregrtest.utils agiza print_warning


# Max size of asynchronous reads
BUFSIZE = 8192
# Seconds per measurement
SAMPLING_INTERVAL = 1
# Exponential damping factor to compute exponentially weighted moving average
# on 1 minute (60 seconds)
LOAD_FACTOR_1 = 1 / math.exp(SAMPLING_INTERVAL / 60)
# Initialize the load using the arithmetic mean of the first NVALUE values
# of the Processor Queue Length
NVALUE = 5
# Windows registry subkey of HKEY_LOCAL_MACHINE where the counter names
# of typeperf are registered
COUNTER_REGISTRY_KEY = (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                        r"\Perflib\CurrentLanguage")


kundi WindowsLoadTracker():
    """
    This kundi asynchronously interacts ukijumuisha the `typeperf` command to read
    the system load on Windows. Multiprocessing na threads can't be used
    here because they interfere ukijumuisha the test suite's cases kila those
    modules.
    """

    eleza __init__(self):
        self._values = []
        self._load = Tupu
        self._buffer = ''
        self._popen = Tupu
        self.start()

    eleza start(self):
        # Create a named pipe which allows kila asynchronous IO kwenye Windows
        pipe_name =  r'\\.\pipe\typeperf_output_' + str(uuid.uuid4())

        open_mode =  _winapi.PIPE_ACCESS_INBOUND
        open_mode |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE
        open_mode |= _winapi.FILE_FLAG_OVERLAPPED

        # This ni the read end of the pipe, where we will be grabbing output
        self.pipe = _winapi.CreateNamedPipe(
            pipe_name, open_mode, _winapi.PIPE_WAIT,
            1, BUFSIZE, BUFSIZE, _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL
        )
        # The write end of the pipe which ni pitaed to the created process
        pipe_write_end = _winapi.CreateFile(
            pipe_name, _winapi.GENERIC_WRITE, 0, _winapi.NULL,
            _winapi.OPEN_EXISTING, 0, _winapi.NULL
        )
        # Open up the handle kama a python file object so we can pita it to
        # subprocess
        command_stdout = msvcrt.open_osfhandle(pipe_write_end, 0)

        # Connect to the read end of the pipe kwenye overlap/async mode
        overlap = _winapi.ConnectNamedPipe(self.pipe, overlapped=Kweli)
        overlap.GetOverlappedResult(Kweli)

        # Spawn off the load monitor
        counter_name = self._get_counter_name()
        command = ['typeperf', counter_name, '-si', str(SAMPLING_INTERVAL)]
        self._popen = subprocess.Popen(' '.join(command), stdout=command_stdout, cwd=support.SAVEDCWD)

        # Close our copy of the write end of the pipe
        os.close(command_stdout)

    eleza _get_counter_name(self):
        # accessing the registry to get the counter localization name
        ukijumuisha winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, COUNTER_REGISTRY_KEY) kama perfkey:
            counters = winreg.QueryValueEx(perfkey, 'Counter')[0]

        # Convert [key1, value1, key2, value2, ...] list
        # to {key1: value1, key2: value2, ...} dict
        counters = iter(counters)
        counters_dict = dict(zip(counters, counters))

        # System counter has key '2' na Processor Queue Length has key '44'
        system = counters_dict['2']
        process_queue_length = counters_dict['44']
        rudisha f'"\\{system}\\{process_queue_length}"'

    eleza close(self, kill=Kweli):
        ikiwa self._popen ni Tupu:
            rudisha

        self._load = Tupu

        ikiwa kill:
            self._popen.kill()
        self._popen.wait()
        self._popen = Tupu

    eleza __del__(self):
        self.close()

    eleza _parse_line(self, line):
        # typeperf outputs kwenye a CSV format like this:
        # "07/19/2018 01:32:26.605","3.000000"
        # (date, process queue length)
        tokens = line.split(',')
        ikiwa len(tokens) != 2:
            ashiria ValueError

        value = tokens[1]
        ikiwa sio value.startswith('"') ama sio value.endswith('"'):
            ashiria ValueError
        value = value[1:-1]
        rudisha float(value)

    eleza _read_lines(self):
        overlapped, _ = _winapi.ReadFile(self.pipe, BUFSIZE, Kweli)
        bytes_read, res = overlapped.GetOverlappedResult(Uongo)
        ikiwa res != 0:
            rudisha ()

        output = overlapped.getbuffer()
        output = output.decode('oem', 'replace')
        output = self._buffer + output
        lines = output.splitlines(Kweli)

        # bpo-36670: typeperf only writes a newline *before* writing a value,
        # sio after. Sometimes, the written line kwenye incomplete (ex: only
        # timestamp, without the process queue length). Only pita the last line
        # to the parser ikiwa it's a valid value, otherwise store it kwenye
        # self._buffer.
        jaribu:
            self._parse_line(lines[-1])
        tatizo ValueError:
            self._buffer = lines.pop(-1)
        isipokua:
            self._buffer = ''

        rudisha lines

    eleza getloadavg(self):
        ikiwa self._popen ni Tupu:
            rudisha Tupu

        returncode = self._popen.poll()
        ikiwa returncode ni sio Tupu:
            self.close(kill=Uongo)
            rudisha Tupu

        jaribu:
            lines = self._read_lines()
        tatizo BrokenPipeError:
            self.close()
            rudisha Tupu

        kila line kwenye lines:
            line = line.rstrip()

            # Ignore the initial header:
            # "(PDH-CSV 4.0)","\\\\WIN\\System\\Processor Queue Length"
            ikiwa 'PDH-CSV' kwenye line:
                endelea

            # Ignore blank lines
            ikiwa sio line:
                endelea

            jaribu:
                processor_queue_length = self._parse_line(line)
            tatizo ValueError:
                print_warning("Failed to parse typeperf output: %a" % line)
                endelea

            # We use an exponentially weighted moving average, imitating the
            # load calculation on Unix systems.
            # https://en.wikipedia.org/wiki/Load_(computing)#Unix-style_load_calculation
            # https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
            ikiwa self._load ni sio Tupu:
                self._load = (self._load * LOAD_FACTOR_1
                              + processor_queue_length  * (1.0 - LOAD_FACTOR_1))
            lasivyo len(self._values) < NVALUE:
                self._values.append(processor_queue_length)
            isipokua:
                self._load = sum(self._values) / len(self._values)

        rudisha self._load
