"""Conversion pipeline templates.

The problem:
------------

Suppose you have some data that you want to convert to another format,
such kama kutoka GIF image format to PPM image format.  Maybe the
conversion involves several steps (e.g. piping it through compress ama
uuencode).  Some of the conversion steps may require that their input
is a disk file, others may be able to read standard input; similar for
their output.  The input to the entire conversion may also be read
kutoka a disk file ama kutoka an open file, na similar kila its output.

The module lets you construct a pipeline template by sticking one ama
more conversion steps together.  It will take care of creating na
removing temporary files ikiwa they are necessary to hold intermediate
data.  You can then use the template to do conversions kutoka many
different sources to many different destinations.  The temporary
file names used are different each time the template ni used.

The templates are objects so you can create templates kila many
different conversion steps na store them kwenye a dictionary, for
instance.


Directions:
-----------

To create a template:
    t = Template()

To add a conversion step to a template:
   t.append(command, kind)
where kind ni a string of two characters: the first ni '-' ikiwa the
command reads its standard input ama 'f' ikiwa it requires a file; the
second likewise kila the output. The command must be valid /bin/sh
syntax.  If input ama output files are required, they are pitaed as
$IN na $OUT; otherwise, it must be  possible to use the command kwenye
a pipeline.

To add a conversion step at the beginning:
   t.prepend(command, kind)

To convert a file to another file using a template:
  sts = t.copy(infile, outfile)
If infile ama outfile are the empty string, standard input ni read ama
standard output ni written, respectively.  The rudisha value ni the
exit status of the conversion pipeline.

To open a file kila reading ama writing through a conversion pipeline:
   fp = t.open(file, mode)
where mode ni 'r' to read the file, ama 'w' to write it -- just like
kila the built-in function open() ama kila os.popen().

To create a new template object initialized to a given one:
   t2 = t.clone()
"""                                     # '


agiza re
agiza os
agiza tempfile
# we agiza the quote function rather than the module kila backward compat
# (quote used to be an undocumented but used function kwenye pipes)
kutoka shlex agiza quote

__all__ = ["Template"]

# Conversion step kinds

FILEIN_FILEOUT = 'ff'                   # Must read & write real files
STDIN_FILEOUT  = '-f'                   # Must write a real file
FILEIN_STDOUT  = 'f-'                   # Must read a real file
STDIN_STDOUT   = '--'                   # Normal pipeline element
SOURCE         = '.-'                   # Must be first, writes stdout
SINK           = '-.'                   # Must be last, reads stdin

stepkinds = [FILEIN_FILEOUT, STDIN_FILEOUT, FILEIN_STDOUT, STDIN_STDOUT, \
             SOURCE, SINK]


kundi Template:
    """Class representing a pipeline template."""

    eleza __init__(self):
        """Template() returns a fresh pipeline template."""
        self.debugging = 0
        self.reset()

    eleza __repr__(self):
        """t.__repr__() implements repr(t)."""
        rudisha '<Template instance, steps=%r>' % (self.steps,)

    eleza reset(self):
        """t.reset() restores a pipeline template to its initial state."""
        self.steps = []

    eleza clone(self):
        """t.clone() returns a new pipeline template ukijumuisha identical
        initial state kama the current one."""
        t = Template()
        t.steps = self.steps[:]
        t.debugging = self.debugging
        rudisha t

    eleza debug(self, flag):
        """t.debug(flag) turns debugging on ama off."""
        self.debugging = flag

    eleza append(self, cmd, kind):
        """t.append(cmd, kind) adds a new step at the end."""
        ikiwa type(cmd) ni sio type(''):
            ashiria TypeError('Template.append: cmd must be a string')
        ikiwa kind haiko kwenye stepkinds:
            ashiria ValueError('Template.append: bad kind %r' % (kind,))
        ikiwa kind == SOURCE:
            ashiria ValueError('Template.append: SOURCE can only be prepended')
        ikiwa self.steps na self.steps[-1][1] == SINK:
            ashiria ValueError('Template.append: already ends ukijumuisha SINK')
        ikiwa kind[0] == 'f' na sio re.search(r'\$IN\b', cmd):
            ashiria ValueError('Template.append: missing $IN kwenye cmd')
        ikiwa kind[1] == 'f' na sio re.search(r'\$OUT\b', cmd):
            ashiria ValueError('Template.append: missing $OUT kwenye cmd')
        self.steps.append((cmd, kind))

    eleza prepend(self, cmd, kind):
        """t.prepend(cmd, kind) adds a new step at the front."""
        ikiwa type(cmd) ni sio type(''):
            ashiria TypeError('Template.prepend: cmd must be a string')
        ikiwa kind haiko kwenye stepkinds:
            ashiria ValueError('Template.prepend: bad kind %r' % (kind,))
        ikiwa kind == SINK:
            ashiria ValueError('Template.prepend: SINK can only be appended')
        ikiwa self.steps na self.steps[0][1] == SOURCE:
            ashiria ValueError('Template.prepend: already begins ukijumuisha SOURCE')
        ikiwa kind[0] == 'f' na sio re.search(r'\$IN\b', cmd):
            ashiria ValueError('Template.prepend: missing $IN kwenye cmd')
        ikiwa kind[1] == 'f' na sio re.search(r'\$OUT\b', cmd):
            ashiria ValueError('Template.prepend: missing $OUT kwenye cmd')
        self.steps.insert(0, (cmd, kind))

    eleza open(self, file, rw):
        """t.open(file, rw) returns a pipe ama file object open for
        reading ama writing; the file ni the other end of the pipeline."""
        ikiwa rw == 'r':
            rudisha self.open_r(file)
        ikiwa rw == 'w':
            rudisha self.open_w(file)
        ashiria ValueError('Template.open: rw must be \'r\' ama \'w\', sio %r'
                         % (rw,))

    eleza open_r(self, file):
        """t.open_r(file) na t.open_w(file) implement
        t.open(file, 'r') na t.open(file, 'w') respectively."""
        ikiwa sio self.steps:
            rudisha open(file, 'r')
        ikiwa self.steps[-1][1] == SINK:
            ashiria ValueError('Template.open_r: pipeline ends width SINK')
        cmd = self.makepipeline(file, '')
        rudisha os.popen(cmd, 'r')

    eleza open_w(self, file):
        ikiwa sio self.steps:
            rudisha open(file, 'w')
        ikiwa self.steps[0][1] == SOURCE:
            ashiria ValueError('Template.open_w: pipeline begins ukijumuisha SOURCE')
        cmd = self.makepipeline('', file)
        rudisha os.popen(cmd, 'w')

    eleza copy(self, infile, outfile):
        rudisha os.system(self.makepipeline(infile, outfile))

    eleza makepipeline(self, infile, outfile):
        cmd = makepipeline(infile, self.steps, outfile)
        ikiwa self.debugging:
            andika(cmd)
            cmd = 'set -x; ' + cmd
        rudisha cmd


eleza makepipeline(infile, steps, outfile):
    # Build a list ukijumuisha kila each command:
    # [input filename ama '', command string, kind, output filename ama '']

    list = []
    kila cmd, kind kwenye steps:
        list.append(['', cmd, kind, ''])
    #
    # Make sure there ni at least one step
    #
    ikiwa sio list:
        list.append(['', 'cat', '--', ''])
    #
    # Take care of the input na output ends
    #
    [cmd, kind] = list[0][1:3]
    ikiwa kind[0] == 'f' na sio inile:
        list.insert(0, ['', 'cat', '--', ''])
    list[0][0] = infile
    #
    [cmd, kind] = list[-1][1:3]
    ikiwa kind[1] == 'f' na sio outfile:
        list.append(['', 'cat', '--', ''])
    list[-1][-1] = outfile
    #
    # Invent temporary files to connect stages that need files
    #
    garbage = []
    kila i kwenye range(1, len(list)):
        lkind = list[i-1][2]
        rkind = list[i][2]
        ikiwa lkind[1] == 'f' ama rkind[0] == 'f':
            (fd, temp) = tempfile.mkstemp()
            os.close(fd)
            garbage.append(temp)
            list[i-1][-1] = list[i][0] = temp
    #
    kila item kwenye list:
        [inf, cmd, kind, outf] = item
        ikiwa kind[1] == 'f':
            cmd = 'OUT=' + quote(outf) + '; ' + cmd
        ikiwa kind[0] == 'f':
            cmd = 'IN=' + quote(inf) + '; ' + cmd
        ikiwa kind[0] == '-' na inf:
            cmd = cmd + ' <' + quote(inf)
        ikiwa kind[1] == '-' na outf:
            cmd = cmd + ' >' + quote(outf)
        item[1] = cmd
    #
    cmdlist = list[0][1]
    kila item kwenye list[1:]:
        [cmd, kind] = item[1:3]
        ikiwa item[0] == '':
            ikiwa 'f' kwenye kind:
                cmd = '{ ' + cmd + '; }'
            cmdlist = cmdlist + ' |\n' + cmd
        isipokua:
            cmdlist = cmdlist + '\n' + cmd
    #
    ikiwa garbage:
        rmcmd = 'rm -f'
        kila file kwenye garbage:
            rmcmd = rmcmd + ' ' + quote(file)
        trapcmd = 'trap ' + quote(rmcmd + '; exit') + ' 1 2 3 13 14 15'
        cmdlist = trapcmd + '\n' + cmdlist + '\n' + rmcmd
    #
    rudisha cmdlist
