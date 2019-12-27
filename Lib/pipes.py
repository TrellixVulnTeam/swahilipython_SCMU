"""Conversion pipeline templates.

The problem:
------------

Suppose you have some data that you want to convert to another format,
such as kutoka GIF image format to PPM image format.  Maybe the
conversion involves several steps (e.g. piping it through compress or
uuencode).  Some of the conversion steps may require that their input
is a disk file, others may be able to read standard input; similar for
their output.  The input to the entire conversion may also be read
kutoka a disk file or kutoka an open file, and similar for its output.

The module lets you construct a pipeline template by sticking one or
more conversion steps together.  It will take care of creating and
removing temporary files ikiwa they are necessary to hold intermediate
data.  You can then use the template to do conversions kutoka many
different sources to many different destinations.  The temporary
file names used are different each time the template is used.

The templates are objects so you can create templates for many
different conversion steps and store them in a dictionary, for
instance.


Directions:
-----------

To create a template:
    t = Template()

To add a conversion step to a template:
   t.append(command, kind)
where kind is a string of two characters: the first is '-' ikiwa the
command reads its standard input or 'f' ikiwa it requires a file; the
second likewise for the output. The command must be valid /bin/sh
syntax.  If input or output files are required, they are passed as
$IN and $OUT; otherwise, it must be  possible to use the command in
a pipeline.

To add a conversion step at the beginning:
   t.prepend(command, kind)

To convert a file to another file using a template:
  sts = t.copy(infile, outfile)
If infile or outfile are the empty string, standard input is read or
standard output is written, respectively.  The rudisha value is the
exit status of the conversion pipeline.

To open a file for reading or writing through a conversion pipeline:
   fp = t.open(file, mode)
where mode is 'r' to read the file, or 'w' to write it -- just like
for the built-in function open() or for os.popen().

To create a new template object initialized to a given one:
   t2 = t.clone()
"""                                     # '


agiza re
agiza os
agiza tempfile
# we agiza the quote function rather than the module for backward compat
# (quote used to be an undocumented but used function in pipes)
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
        """t.clone() returns a new pipeline template with identical
        initial state as the current one."""
        t = Template()
        t.steps = self.steps[:]
        t.debugging = self.debugging
        rudisha t

    eleza debug(self, flag):
        """t.debug(flag) turns debugging on or off."""
        self.debugging = flag

    eleza append(self, cmd, kind):
        """t.append(cmd, kind) adds a new step at the end."""
        ikiwa type(cmd) is not type(''):
            raise TypeError('Template.append: cmd must be a string')
        ikiwa kind not in stepkinds:
            raise ValueError('Template.append: bad kind %r' % (kind,))
        ikiwa kind == SOURCE:
            raise ValueError('Template.append: SOURCE can only be prepended')
        ikiwa self.steps and self.steps[-1][1] == SINK:
            raise ValueError('Template.append: already ends with SINK')
        ikiwa kind[0] == 'f' and not re.search(r'\$IN\b', cmd):
            raise ValueError('Template.append: missing $IN in cmd')
        ikiwa kind[1] == 'f' and not re.search(r'\$OUT\b', cmd):
            raise ValueError('Template.append: missing $OUT in cmd')
        self.steps.append((cmd, kind))

    eleza prepend(self, cmd, kind):
        """t.prepend(cmd, kind) adds a new step at the front."""
        ikiwa type(cmd) is not type(''):
            raise TypeError('Template.prepend: cmd must be a string')
        ikiwa kind not in stepkinds:
            raise ValueError('Template.prepend: bad kind %r' % (kind,))
        ikiwa kind == SINK:
            raise ValueError('Template.prepend: SINK can only be appended')
        ikiwa self.steps and self.steps[0][1] == SOURCE:
            raise ValueError('Template.prepend: already begins with SOURCE')
        ikiwa kind[0] == 'f' and not re.search(r'\$IN\b', cmd):
            raise ValueError('Template.prepend: missing $IN in cmd')
        ikiwa kind[1] == 'f' and not re.search(r'\$OUT\b', cmd):
            raise ValueError('Template.prepend: missing $OUT in cmd')
        self.steps.insert(0, (cmd, kind))

    eleza open(self, file, rw):
        """t.open(file, rw) returns a pipe or file object open for
        reading or writing; the file is the other end of the pipeline."""
        ikiwa rw == 'r':
            rudisha self.open_r(file)
        ikiwa rw == 'w':
            rudisha self.open_w(file)
        raise ValueError('Template.open: rw must be \'r\' or \'w\', not %r'
                         % (rw,))

    eleza open_r(self, file):
        """t.open_r(file) and t.open_w(file) implement
        t.open(file, 'r') and t.open(file, 'w') respectively."""
        ikiwa not self.steps:
            rudisha open(file, 'r')
        ikiwa self.steps[-1][1] == SINK:
            raise ValueError('Template.open_r: pipeline ends width SINK')
        cmd = self.makepipeline(file, '')
        rudisha os.popen(cmd, 'r')

    eleza open_w(self, file):
        ikiwa not self.steps:
            rudisha open(file, 'w')
        ikiwa self.steps[0][1] == SOURCE:
            raise ValueError('Template.open_w: pipeline begins with SOURCE')
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
    # Build a list with for each command:
    # [input filename or '', command string, kind, output filename or '']

    list = []
    for cmd, kind in steps:
        list.append(['', cmd, kind, ''])
    #
    # Make sure there is at least one step
    #
    ikiwa not list:
        list.append(['', 'cat', '--', ''])
    #
    # Take care of the input and output ends
    #
    [cmd, kind] = list[0][1:3]
    ikiwa kind[0] == 'f' and not infile:
        list.insert(0, ['', 'cat', '--', ''])
    list[0][0] = infile
    #
    [cmd, kind] = list[-1][1:3]
    ikiwa kind[1] == 'f' and not outfile:
        list.append(['', 'cat', '--', ''])
    list[-1][-1] = outfile
    #
    # Invent temporary files to connect stages that need files
    #
    garbage = []
    for i in range(1, len(list)):
        lkind = list[i-1][2]
        rkind = list[i][2]
        ikiwa lkind[1] == 'f' or rkind[0] == 'f':
            (fd, temp) = tempfile.mkstemp()
            os.close(fd)
            garbage.append(temp)
            list[i-1][-1] = list[i][0] = temp
    #
    for item in list:
        [inf, cmd, kind, outf] = item
        ikiwa kind[1] == 'f':
            cmd = 'OUT=' + quote(outf) + '; ' + cmd
        ikiwa kind[0] == 'f':
            cmd = 'IN=' + quote(inf) + '; ' + cmd
        ikiwa kind[0] == '-' and inf:
            cmd = cmd + ' <' + quote(inf)
        ikiwa kind[1] == '-' and outf:
            cmd = cmd + ' >' + quote(outf)
        item[1] = cmd
    #
    cmdlist = list[0][1]
    for item in list[1:]:
        [cmd, kind] = item[1:3]
        ikiwa item[0] == '':
            ikiwa 'f' in kind:
                cmd = '{ ' + cmd + '; }'
            cmdlist = cmdlist + ' |\n' + cmd
        else:
            cmdlist = cmdlist + '\n' + cmd
    #
    ikiwa garbage:
        rmcmd = 'rm -f'
        for file in garbage:
            rmcmd = rmcmd + ' ' + quote(file)
        trapcmd = 'trap ' + quote(rmcmd + '; exit') + ' 1 2 3 13 14 15'
        cmdlist = trapcmd + '\n' + cmdlist + '\n' + rmcmd
    #
    rudisha cmdlist
