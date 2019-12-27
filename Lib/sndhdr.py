"""Routines to help recognizing sound files.

Function whathdr() recognizes various types of sound file headers.
It understands almost all headers that SOX can decode.

The rudisha tuple contains the following items, in this order:
- file type (as SOX understands it)
- sampling rate (0 ikiwa unknown or hard to decode)
- number of channels (0 ikiwa unknown or hard to decode)
- number of frames in the file (-1 ikiwa unknown or hard to decode)
- number of bits/sample, or 'U' for U-LAW, or 'A' for A-LAW

If the file doesn't have a recognizable type, it returns None.
If the file can't be opened, OSError is raised.

To compute the total time, divide the number of frames by the
sampling rate (a frame contains a sample for each channel).

Function what() calls whathdr().  (It used to also use some
heuristics for raw data, but this doesn't work very well.)

Finally, the function test() is a simple main program that calls
what() for all files mentioned on the argument list.  For directory
arguments it calls what() for all files in that directory.  Default
argument is "." (testing all files in the current directory).  The
option -r tells it to recurse down directories found inside
explicitly given directories.
"""

# The file structure is top-down except that the test program and its
# subroutine come last.

__all__ = ['what', 'whathdr']

kutoka collections agiza namedtuple

SndHeaders = namedtuple('SndHeaders',
                        'filetype framerate nchannels nframes sampwidth')

SndHeaders.filetype.__doc__ = ("""The value for type indicates the data type
and will be one of the strings 'aifc', 'aiff', 'au','hcom',
'sndr', 'sndt', 'voc', 'wav', '8svx', 'sb', 'ub', or 'ul'.""")
SndHeaders.framerate.__doc__ = ("""The sampling_rate will be either the actual
value or 0 ikiwa unknown or difficult to decode.""")
SndHeaders.nchannels.__doc__ = ("""The number of channels or 0 ikiwa it cannot be
determined or ikiwa the value is difficult to decode.""")
SndHeaders.nframes.__doc__ = ("""The value for frames will be either the number
of frames or -1.""")
SndHeaders.sampwidth.__doc__ = ("""Either the sample size in bits or
'A' for A-LAW or 'U' for u-LAW.""")

eleza what(filename):
    """Guess the type of a sound file."""
    res = whathdr(filename)
    rudisha res


eleza whathdr(filename):
    """Recognize sound headers."""
    with open(filename, 'rb') as f:
        h = f.read(512)
        for tf in tests:
            res = tf(h, f)
            ikiwa res:
                rudisha SndHeaders(*res)
        rudisha None


#-----------------------------------#
# Subroutines per sound header type #
#-----------------------------------#

tests = []

eleza test_aifc(h, f):
    agiza aifc
    ikiwa not h.startswith(b'FORM'):
        rudisha None
    ikiwa h[8:12] == b'AIFC':
        fmt = 'aifc'
    elikiwa h[8:12] == b'AIFF':
        fmt = 'aiff'
    else:
        rudisha None
    f.seek(0)
    try:
        a = aifc.open(f, 'r')
    except (EOFError, aifc.Error):
        rudisha None
    rudisha (fmt, a.getframerate(), a.getnchannels(),
            a.getnframes(), 8 * a.getsampwidth())

tests.append(test_aifc)


eleza test_au(h, f):
    ikiwa h.startswith(b'.snd'):
        func = get_long_be
    elikiwa h[:4] in (b'\0ds.', b'dns.'):
        func = get_long_le
    else:
        rudisha None
    filetype = 'au'
    hdr_size = func(h[4:8])
    data_size = func(h[8:12])
    encoding = func(h[12:16])
    rate = func(h[16:20])
    nchannels = func(h[20:24])
    sample_size = 1 # default
    ikiwa encoding == 1:
        sample_bits = 'U'
    elikiwa encoding == 2:
        sample_bits = 8
    elikiwa encoding == 3:
        sample_bits = 16
        sample_size = 2
    else:
        sample_bits = '?'
    frame_size = sample_size * nchannels
    ikiwa frame_size:
        nframe = data_size / frame_size
    else:
        nframe = -1
    rudisha filetype, rate, nchannels, nframe, sample_bits

tests.append(test_au)


eleza test_hcom(h, f):
    ikiwa h[65:69] != b'FSSD' or h[128:132] != b'HCOM':
        rudisha None
    divisor = get_long_be(h[144:148])
    ikiwa divisor:
        rate = 22050 / divisor
    else:
        rate = 0
    rudisha 'hcom', rate, 1, -1, 8

tests.append(test_hcom)


eleza test_voc(h, f):
    ikiwa not h.startswith(b'Creative Voice File\032'):
        rudisha None
    sbseek = get_short_le(h[20:22])
    rate = 0
    ikiwa 0 <= sbseek < 500 and h[sbseek] == 1:
        ratecode = 256 - h[sbseek+4]
        ikiwa ratecode:
            rate = int(1000000.0 / ratecode)
    rudisha 'voc', rate, 1, -1, 8

tests.append(test_voc)


eleza test_wav(h, f):
    agiza wave
    # 'RIFF' <len> 'WAVE' 'fmt ' <len>
    ikiwa not h.startswith(b'RIFF') or h[8:12] != b'WAVE' or h[12:16] != b'fmt ':
        rudisha None
    f.seek(0)
    try:
        w = wave.open(f, 'r')
    except (EOFError, wave.Error):
        rudisha None
    rudisha ('wav', w.getframerate(), w.getnchannels(),
                   w.getnframes(), 8*w.getsampwidth())

tests.append(test_wav)


eleza test_8svx(h, f):
    ikiwa not h.startswith(b'FORM') or h[8:12] != b'8SVX':
        rudisha None
    # Should decode it to get #channels -- assume always 1
    rudisha '8svx', 0, 1, 0, 8

tests.append(test_8svx)


eleza test_sndt(h, f):
    ikiwa h.startswith(b'SOUND'):
        nsamples = get_long_le(h[8:12])
        rate = get_short_le(h[20:22])
        rudisha 'sndt', rate, 1, nsamples, 8

tests.append(test_sndt)


eleza test_sndr(h, f):
    ikiwa h.startswith(b'\0\0'):
        rate = get_short_le(h[2:4])
        ikiwa 4000 <= rate <= 25000:
            rudisha 'sndr', rate, 1, -1, 8

tests.append(test_sndr)


#-------------------------------------------#
# Subroutines to extract numbers kutoka bytes #
#-------------------------------------------#

eleza get_long_be(b):
    rudisha (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]

eleza get_long_le(b):
    rudisha (b[3] << 24) | (b[2] << 16) | (b[1] << 8) | b[0]

eleza get_short_be(b):
    rudisha (b[0] << 8) | b[1]

eleza get_short_le(b):
    rudisha (b[1] << 8) | b[0]


#--------------------#
# Small test program #
#--------------------#

eleza test():
    agiza sys
    recursive = 0
    ikiwa sys.argv[1:] and sys.argv[1] == '-r':
        del sys.argv[1:2]
        recursive = 1
    try:
        ikiwa sys.argv[1:]:
            testall(sys.argv[1:], recursive, 1)
        else:
            testall(['.'], recursive, 1)
    except KeyboardInterrupt:
        sys.stderr.write('\n[Interrupted]\n')
        sys.exit(1)

eleza testall(list, recursive, toplevel):
    agiza sys
    agiza os
    for filename in list:
        ikiwa os.path.isdir(filename):
            andika(filename + '/:', end=' ')
            ikiwa recursive or toplevel:
                andika('recursing down:')
                agiza glob
                names = glob.glob(os.path.join(filename, '*'))
                testall(names, recursive, 0)
            else:
                andika('*** directory (use -r) ***')
        else:
            andika(filename + ':', end=' ')
            sys.stdout.flush()
            try:
                andika(what(filename))
            except OSError:
                andika('*** not found ***')

ikiwa __name__ == '__main__':
    test()
