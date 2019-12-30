"""Routines to help recognizing sound files.

Function whathdr() recognizes various types of sound file headers.
It understands almost all headers that SOX can decode.

The rudisha tuple contains the following items, kwenye this order:
- file type (as SOX understands it)
- sampling rate (0 ikiwa unknown ama hard to decode)
- number of channels (0 ikiwa unknown ama hard to decode)
- number of frames kwenye the file (-1 ikiwa unknown ama hard to decode)
- number of bits/sample, ama 'U' kila U-LAW, ama 'A' kila A-LAW

If the file doesn't have a recognizable type, it returns Tupu.
If the file can't be opened, OSError ni raised.

To compute the total time, divide the number of frames by the
sampling rate (a frame contains a sample kila each channel).

Function what() calls whathdr().  (It used to also use some
heuristics kila raw data, but this doesn't work very well.)

Finally, the function test() ni a simple main program that calls
what() kila all files mentioned on the argument list.  For directory
arguments it calls what() kila all files kwenye that directory.  Default
argument ni "." (testing all files kwenye the current directory).  The
option -r tells it to recurse down directories found inside
explicitly given directories.
"""

# The file structure ni top-down tatizo that the test program na its
# subroutine come last.

__all__ = ['what', 'whathdr']

kutoka collections agiza namedtuple

SndHeaders = namedtuple('SndHeaders',
                        'filetype framerate nchannels nframes sampwidth')

SndHeaders.filetype.__doc__ = ("""The value kila type indicates the data type
and will be one of the strings 'aifc', 'aiff', 'au','hcom',
'sndr', 'sndt', 'voc', 'wav', '8svx', 'sb', 'ub', ama 'ul'.""")
SndHeaders.framerate.__doc__ = ("""The sampling_rate will be either the actual
value ama 0 ikiwa unknown ama difficult to decode.""")
SndHeaders.nchannels.__doc__ = ("""The number of channels ama 0 ikiwa it cansio be
determined ama ikiwa the value ni difficult to decode.""")
SndHeaders.nframes.__doc__ = ("""The value kila frames will be either the number
of frames ama -1.""")
SndHeaders.sampwidth.__doc__ = ("""Either the sample size kwenye bits ama
'A' kila A-LAW ama 'U' kila u-LAW.""")

eleza what(filename):
    """Guess the type of a sound file."""
    res = whathdr(filename)
    rudisha res


eleza whathdr(filename):
    """Recognize sound headers."""
    ukijumuisha open(filename, 'rb') kama f:
        h = f.read(512)
        kila tf kwenye tests:
            res = tf(h, f)
            ikiwa res:
                rudisha SndHeaders(*res)
        rudisha Tupu


#-----------------------------------#
# Subroutines per sound header type #
#-----------------------------------#

tests = []

eleza test_aifc(h, f):
    agiza aifc
    ikiwa sio h.startswith(b'FORM'):
        rudisha Tupu
    ikiwa h[8:12] == b'AIFC':
        fmt = 'aifc'
    lasivyo h[8:12] == b'AIFF':
        fmt = 'aiff'
    isipokua:
        rudisha Tupu
    f.seek(0)
    jaribu:
        a = aifc.open(f, 'r')
    tatizo (EOFError, aifc.Error):
        rudisha Tupu
    rudisha (fmt, a.getframerate(), a.getnchannels(),
            a.getnframes(), 8 * a.getsampwidth())

tests.append(test_aifc)


eleza test_au(h, f):
    ikiwa h.startswith(b'.snd'):
        func = get_long_be
    lasivyo h[:4] kwenye (b'\0ds.', b'dns.'):
        func = get_long_le
    isipokua:
        rudisha Tupu
    filetype = 'au'
    hdr_size = func(h[4:8])
    data_size = func(h[8:12])
    encoding = func(h[12:16])
    rate = func(h[16:20])
    nchannels = func(h[20:24])
    sample_size = 1 # default
    ikiwa encoding == 1:
        sample_bits = 'U'
    lasivyo encoding == 2:
        sample_bits = 8
    lasivyo encoding == 3:
        sample_bits = 16
        sample_size = 2
    isipokua:
        sample_bits = '?'
    frame_size = sample_size * nchannels
    ikiwa frame_size:
        nframe = data_size / frame_size
    isipokua:
        nframe = -1
    rudisha filetype, rate, nchannels, nframe, sample_bits

tests.append(test_au)


eleza test_hcom(h, f):
    ikiwa h[65:69] != b'FSSD' ama h[128:132] != b'HCOM':
        rudisha Tupu
    divisor = get_long_be(h[144:148])
    ikiwa divisor:
        rate = 22050 / divisor
    isipokua:
        rate = 0
    rudisha 'hcom', rate, 1, -1, 8

tests.append(test_hcom)


eleza test_voc(h, f):
    ikiwa sio h.startswith(b'Creative Voice File\032'):
        rudisha Tupu
    sbseek = get_short_le(h[20:22])
    rate = 0
    ikiwa 0 <= sbseek < 500 na h[sbseek] == 1:
        ratecode = 256 - h[sbseek+4]
        ikiwa ratecode:
            rate = int(1000000.0 / ratecode)
    rudisha 'voc', rate, 1, -1, 8

tests.append(test_voc)


eleza test_wav(h, f):
    agiza wave
    # 'RIFF' <len> 'WAVE' 'fmt ' <len>
    ikiwa sio h.startswith(b'RIFF') ama h[8:12] != b'WAVE' ama h[12:16] != b'fmt ':
        rudisha Tupu
    f.seek(0)
    jaribu:
        w = wave.open(f, 'r')
    tatizo (EOFError, wave.Error):
        rudisha Tupu
    rudisha ('wav', w.getframerate(), w.getnchannels(),
                   w.getnframes(), 8*w.getsampwidth())

tests.append(test_wav)


eleza test_8svx(h, f):
    ikiwa sio h.startswith(b'FORM') ama h[8:12] != b'8SVX':
        rudisha Tupu
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
    ikiwa sys.argv[1:] na sys.argv[1] == '-r':
        toa sys.argv[1:2]
        recursive = 1
    jaribu:
        ikiwa sys.argv[1:]:
            testall(sys.argv[1:], recursive, 1)
        isipokua:
            testall(['.'], recursive, 1)
    tatizo KeyboardInterrupt:
        sys.stderr.write('\n[Interrupted]\n')
        sys.exit(1)

eleza testall(list, recursive, toplevel):
    agiza sys
    agiza os
    kila filename kwenye list:
        ikiwa os.path.isdir(filename):
            andika(filename + '/:', end=' ')
            ikiwa recursive ama toplevel:
                andika('recursing down:')
                agiza glob
                names = glob.glob(os.path.join(filename, '*'))
                testall(names, recursive, 0)
            isipokua:
                andika('*** directory (use -r) ***')
        isipokua:
            andika(filename + ':', end=' ')
            sys.stdout.flush()
            jaribu:
                andika(what(filename))
            tatizo OSError:
                andika('*** sio found ***')

ikiwa __name__ == '__main__':
    test()
