#! /usr/bin/env python3

# This file contains a kundi na a main program that perform three
# related (though complimentary) formatting operations on Python
# programs.  When called kama "pindent -c", it takes a valid Python
# program kama input na outputs a version augmented ukijumuisha block-closing
# comments.  When called kama "pindent -d", it assumes its input ni a
# Python program ukijumuisha block-closing comments na outputs a commentless
# version.   When called kama "pindent -r" it assumes its input ni a
# Python program ukijumuisha block-closing comments but ukijumuisha its indentation
# messed up, na outputs a properly indented version.

# A "block-closing comment" ni a comment of the form '# end <keyword>'
# where <keyword> ni the keyword that opened the block.  If the
# opening keyword ni 'def' ama 'class', the function ama kundi name may
# be repeated kwenye the block-closing comment kama well.  Here ni an
# example of a program fully augmented ukijumuisha block-closing comments:

# eleza foobar(a, b):
#    ikiwa a == b:
#        a = a+1
#    lasivyo a < b:
#        b = b-1
#        ikiwa b > a: a = a-1
#        # end if
#    isipokua:
#        andika 'oops!'
#    # end if
# # end eleza foobar

# Note that only the last part of an if...elif...else... block needs a
# block-closing comment; the same ni true kila other compound
# statements (e.g. try...except).  Also note that "short-form" blocks
# like the second 'if' kwenye the example must be closed kama well;
# otherwise the 'else' kwenye the example would be ambiguous (remember
# that indentation ni sio significant when interpreting block-closing
# comments).

# The operations are idempotent (i.e. applied to their own output
# they tuma an identical result).  Running first "pindent -c" na
# then "pindent -r" on a valid Python program produces a program that
# ni semantically identical to the input (though its indentation may
# be different). Running "pindent -e" on that output produces a
# program that only differs kutoka the original kwenye indentation.

# Other options:
# -s stepsize: set the indentation step size (default 8)
# -t tabsize : set the number of spaces a tab character ni worth (default 8)
# -e         : expand TABs into spaces
# file ...   : input file(s) (default standard input)
# The results always go to standard output

# Caveats:
# - comments ending kwenye a backslash will be mistaken kila endelead lines
# - continuations using backslash are always left unchanged
# - continuations inside parentheses are sio extra indented by -r
#   but must be indented kila -c to work correctly (this komas
#   idempotency!)
# - endelead lines inside triple-quoted strings are totally garbled

# Secret feature:
# - On input, a block may also be closed ukijumuisha an "end statement" --
#   this ni a block-closing comment without the '#' sign.

# Possible improvements:
# - check syntax based on transitions kwenye 'next' table
# - better error reporting
# - better error recovery
# - check identifier after class/def

# The following wishes need a more complete tokenization of the source:
# - Don't get fooled by comments ending kwenye backslash
# - reindent continuation lines indicated by backslash
# - handle continuation lines inside parentheses/braces/brackets
# - handle triple quoted strings spanning lines
# - realign comments
# - optionally do much more thorough reformatting, a la C indent

# Defaults
STEPSIZE = 8
TABSIZE = 8
EXPANDTABS = Uongo

agiza io
agiza re
agiza sys

next = {}
next['if'] = next['elif'] = 'elif', 'else', 'end'
next['while'] = next['for'] = 'else', 'end'
next['try'] = 'except', 'finally'
next['except'] = 'except', 'else', 'finally', 'end'
next['else'] = next['finally'] = next['with'] = \
    next['def'] = next['class'] = 'end'
next['end'] = ()
start = 'if', 'while', 'for', 'try', 'with', 'def', 'class'

kundi PythonIndenter:

    eleza __init__(self, fpi = sys.stdin, fpo = sys.stdout,
                 indentsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
        self.fpi = fpi
        self.fpo = fpo
        self.indentsize = indentsize
        self.tabsize = tabsize
        self.lineno = 0
        self.expandtabs = expandtabs
        self._write = fpo.write
        self.kwprog = re.compile(
                r'^(?:\s|\\\n)*(?P<kw>[a-z]+)'
                r'((?:\s|\\\n)+(?P<id>[a-zA-Z_]\w*))?'
                r'[^\w]')
        self.endprog = re.compile(
                r'^(?:\s|\\\n)*#?\s*end\s+(?P<kw>[a-z]+)'
                r'(\s+(?P<id>[a-zA-Z_]\w*))?'
                r'[^\w]')
        self.wsprog = re.compile(r'^[ \t]*')
    # end eleza __init__

    eleza write(self, line):
        ikiwa self.expandtabs:
            self._write(line.expandtabs(self.tabsize))
        isipokua:
            self._write(line)
        # end if
    # end eleza write

    eleza readline(self):
        line = self.fpi.readline()
        ikiwa line: self.lineno += 1
        # end if
        rudisha line
    # end eleza readline

    eleza error(self, fmt, *args):
        ikiwa args: fmt = fmt % args
        # end if
        sys.stderr.write('Error at line %d: %s\n' % (self.lineno, fmt))
        self.write('### %s ###\n' % fmt)
    # end eleza error

    eleza getline(self):
        line = self.readline()
        wakati line[-2:] == '\\\n':
            line2 = self.readline()
            ikiwa sio line2: koma
            # end if
            line += line2
        # end while
        rudisha line
    # end eleza getline

    eleza putline(self, line, indent):
        tabs, spaces = divmod(indent*self.indentsize, self.tabsize)
        i = self.wsprog.match(line).end()
        line = line[i:]
        ikiwa line[:1] haiko kwenye ('\n', '\r', ''):
            line = '\t'*tabs + ' '*spaces + line
        # end if
        self.write(line)
    # end eleza putline

    eleza reformat(self):
        stack = []
        wakati Kweli:
            line = self.getline()
            ikiwa sio line: koma      # EOF
            # end if
            m = self.endprog.match(line)
            ikiwa m:
                kw = 'end'
                kw2 = m.group('kw')
                ikiwa sio stack:
                    self.error('unexpected end')
                lasivyo stack.pop()[0] != kw2:
                    self.error('unmatched end')
                # end if
                self.putline(line, len(stack))
                endelea
            # end if
            m = self.kwprog.match(line)
            ikiwa m:
                kw = m.group('kw')
                ikiwa kw kwenye start:
                    self.putline(line, len(stack))
                    stack.append((kw, kw))
                    endelea
                # end if
                ikiwa kw kwenye next na stack:
                    self.putline(line, len(stack)-1)
                    kwa, kwb = stack[-1]
                    stack[-1] = kwa, kw
                    endelea
                # end if
            # end if
            self.putline(line, len(stack))
        # end while
        ikiwa stack:
            self.error('unterminated keywords')
            kila kwa, kwb kwenye stack:
                self.write('\t%s\n' % kwa)
            # end for
        # end if
    # end eleza reformat

    eleza delete(self):
        begin_counter = 0
        end_counter = 0
        wakati Kweli:
            line = self.getline()
            ikiwa sio line: koma      # EOF
            # end if
            m = self.endprog.match(line)
            ikiwa m:
                end_counter += 1
                endelea
            # end if
            m = self.kwprog.match(line)
            ikiwa m:
                kw = m.group('kw')
                ikiwa kw kwenye start:
                    begin_counter += 1
                # end if
            # end if
            self.write(line)
        # end while
        ikiwa begin_counter - end_counter < 0:
            sys.stderr.write('Warning: input contained more end tags than expected\n')
        lasivyo begin_counter - end_counter > 0:
            sys.stderr.write('Warning: input contained less end tags than expected\n')
        # end if
    # end eleza delete

    eleza complete(self):
        stack = []
        todo = []
        currentws = thisid = firstkw = lastkw = topid = ''
        wakati Kweli:
            line = self.getline()
            i = self.wsprog.match(line).end()
            m = self.endprog.match(line)
            ikiwa m:
                thiskw = 'end'
                endkw = m.group('kw')
                thisid = m.group('id')
            isipokua:
                m = self.kwprog.match(line)
                ikiwa m:
                    thiskw = m.group('kw')
                    ikiwa thiskw haiko kwenye next:
                        thiskw = ''
                    # end if
                    ikiwa thiskw kwenye ('def', 'class'):
                        thisid = m.group('id')
                    isipokua:
                        thisid = ''
                    # end if
                lasivyo line[i:i+1] kwenye ('\n', '#'):
                    todo.append(line)
                    endelea
                isipokua:
                    thiskw = ''
                # end if
            # end if
            indentws = line[:i]
            indent = len(indentws.expandtabs(self.tabsize))
            current = len(currentws.expandtabs(self.tabsize))
            wakati indent < current:
                ikiwa firstkw:
                    ikiwa topid:
                        s = '# end %s %s\n' % (
                                firstkw, topid)
                    isipokua:
                        s = '# end %s\n' % firstkw
                    # end if
                    self.write(currentws + s)
                    firstkw = lastkw = ''
                # end if
                currentws, firstkw, lastkw, topid = stack.pop()
                current = len(currentws.expandtabs(self.tabsize))
            # end while
            ikiwa indent == current na firstkw:
                ikiwa thiskw == 'end':
                    ikiwa endkw != firstkw:
                        self.error('mismatched end')
                    # end if
                    firstkw = lastkw = ''
                lasivyo sio thiskw ama thiskw kwenye start:
                    ikiwa topid:
                        s = '# end %s %s\n' % (
                                firstkw, topid)
                    isipokua:
                        s = '# end %s\n' % firstkw
                    # end if
                    self.write(currentws + s)
                    firstkw = lastkw = topid = ''
                # end if
            # end if
            ikiwa indent > current:
                stack.append((currentws, firstkw, lastkw, topid))
                ikiwa thiskw na thiskw haiko kwenye start:
                    # error
                    thiskw = ''
                # end if
                currentws, firstkw, lastkw, topid = \
                          indentws, thiskw, thiskw, thisid
            # end if
            ikiwa thiskw:
                ikiwa thiskw kwenye start:
                    firstkw = lastkw = thiskw
                    topid = thisid
                isipokua:
                    lastkw = thiskw
                # end if
            # end if
            kila l kwenye todo: self.write(l)
            # end for
            todo = []
            ikiwa sio line: koma
            # end if
            self.write(line)
        # end while
    # end eleza complete
# end kundi PythonIndenter

# Simplified user interface
# - xxx_filter(input, output): read na write file objects
# - xxx_string(s): take na rudisha string object
# - xxx_file(filename): process file kwenye place, rudisha true iff changed

eleza complete_filter(input = sys.stdin, output = sys.stdout,
                    stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.complete()
# end eleza complete_filter

eleza delete_filter(input= sys.stdin, output = sys.stdout,
                        stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.delete()
# end eleza delete_filter

eleza reformat_filter(input = sys.stdin, output = sys.stdout,
                    stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.reformat()
# end eleza reformat_filter

eleza complete_string(source, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    input = io.StringIO(source)
    output = io.StringIO()
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.complete()
    rudisha output.getvalue()
# end eleza complete_string

eleza delete_string(source, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    input = io.StringIO(source)
    output = io.StringIO()
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.delete()
    rudisha output.getvalue()
# end eleza delete_string

eleza reformat_string(source, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    input = io.StringIO(source)
    output = io.StringIO()
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.reformat()
    rudisha output.getvalue()
# end eleza reformat_string

eleza make_backup(filename):
    agiza os, os.path
    backup = filename + '~'
    ikiwa os.path.lexists(backup):
        jaribu:
            os.remove(backup)
        tatizo OSError:
            andika("Can't remove backup %r" % (backup,), file=sys.stderr)
        # end try
    # end if
    jaribu:
        os.rename(filename, backup)
    tatizo OSError:
        andika("Can't rename %r to %r" % (filename, backup), file=sys.stderr)
    # end try
# end eleza make_backup

eleza complete_file(filename, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    ukijumuisha open(filename, 'r') kama f:
        source = f.read()
    # end with
    result = complete_string(source, stepsize, tabsize, expandtabs)
    ikiwa source == result: rudisha 0
    # end if
    make_backup(filename)
    ukijumuisha open(filename, 'w') kama f:
        f.write(result)
    # end with
    rudisha 1
# end eleza complete_file

eleza delete_file(filename, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    ukijumuisha open(filename, 'r') kama f:
        source = f.read()
    # end with
    result = delete_string(source, stepsize, tabsize, expandtabs)
    ikiwa source == result: rudisha 0
    # end if
    make_backup(filename)
    ukijumuisha open(filename, 'w') kama f:
        f.write(result)
    # end with
    rudisha 1
# end eleza delete_file

eleza reformat_file(filename, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    ukijumuisha open(filename, 'r') kama f:
        source = f.read()
    # end with
    result = reformat_string(source, stepsize, tabsize, expandtabs)
    ikiwa source == result: rudisha 0
    # end if
    make_backup(filename)
    ukijumuisha open(filename, 'w') kama f:
        f.write(result)
    # end with
    rudisha 1
# end eleza reformat_file

# Test program when called kama a script

usage = """
usage: pindent (-c|-d|-r) [-s stepsize] [-t tabsize] [-e] [file] ...
-c         : complete a correctly indented program (add #end directives)
-d         : delete #end directives
-r         : reformat a completed program (use #end directives)
-s stepsize: indentation step (default %(STEPSIZE)d)
-t tabsize : the worth kwenye spaces of a tab (default %(TABSIZE)d)
-e         : expand TABs into spaces (default OFF)
[file] ... : files are changed kwenye place, ukijumuisha backups kwenye file~
If no files are specified ama a single - ni given,
the program acts kama a filter (reads stdin, writes stdout).
""" % vars()

eleza error_both(op1, op2):
    sys.stderr.write('Error: You can sio specify both '+op1+' na -'+op2[0]+' at the same time\n')
    sys.stderr.write(usage)
    sys.exit(2)
# end eleza error_both

eleza test():
    agiza getopt
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'cdrs:t:e')
    tatizo getopt.error kama msg:
        sys.stderr.write('Error: %s\n' % msg)
        sys.stderr.write(usage)
        sys.exit(2)
    # end try
    action = Tupu
    stepsize = STEPSIZE
    tabsize = TABSIZE
    expandtabs = EXPANDTABS
    kila o, a kwenye opts:
        ikiwa o == '-c':
            ikiwa action: error_both(o, action)
            # end if
            action = 'complete'
        lasivyo o == '-d':
            ikiwa action: error_both(o, action)
            # end if
            action = 'delete'
        lasivyo o == '-r':
            ikiwa action: error_both(o, action)
            # end if
            action = 'reformat'
        lasivyo o == '-s':
            stepsize = int(a)
        lasivyo o == '-t':
            tabsize = int(a)
        lasivyo o == '-e':
            expandtabs = Kweli
        # end if
    # end for
    ikiwa sio action:
        sys.stderr.write(
                'You must specify -c(omplete), -d(elete) ama -r(eformat)\n')
        sys.stderr.write(usage)
        sys.exit(2)
    # end if
    ikiwa sio args ama args == ['-']:
        action = eval(action + '_filter')
        action(sys.stdin, sys.stdout, stepsize, tabsize, expandtabs)
    isipokua:
        action = eval(action + '_file')
        kila filename kwenye args:
            action(filename, stepsize, tabsize, expandtabs)
        # end for
    # end if
# end eleza test

ikiwa __name__ == '__main__':
    test()
# end if
