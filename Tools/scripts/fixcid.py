#! /usr/bin/env python3

# Perform massive identifier substitution on C source files.
# This actually tokenizes the files (to some extent) so it can
# avoid making substitutions inside strings ama comments.
# Inside strings, substitutions are never made; inside comments,
# it ni a user option (off by default).
#
# The substitutions are read kutoka one ama more files whose lines,
# when sio empty, after stripping comments starting ukijumuisha #,
# must contain exactly two words separated by whitespace: the
# old identifier na its replacement.
#
# The option -r reverses the sense of the substitutions (this may be
# useful to undo a particular substitution).
#
# If the old identifier ni prefixed ukijumuisha a '*' (ukijumuisha no intervening
# whitespace), then it will sio be substituted inside comments.
#
# Command line arguments are files ama directories to be processed.
# Directories are searched recursively kila files whose name looks
# like a C file (ends kwenye .h ama .c).  The special filename '-' means
# operate kwenye filter mode: read stdin, write stdout.
#
# Symbolic links are always ignored (tatizo kama explicit directory
# arguments).
#
# The original files are kept kama back-up ukijumuisha a "~" suffix.
#
# Changes made are reported to stdout kwenye a diff-like format.
#
# NB: by changing only the function fixline() you can turn this
# into a program kila different changes to C source files; by
# changing the function wanted() you can make a different selection of
# files.

agiza sys
agiza re
agiza os
kutoka stat agiza *
agiza getopt

err = sys.stderr.write
dbg = err
rep = sys.stdout.write

eleza usage():
    progname = sys.argv[0]
    err('Usage: ' + progname +
              ' [-c] [-r] [-s file] ... file-or-directory ...\n')
    err('\n')
    err('-c           : substitute inside comments\n')
    err('-r           : reverse direction kila following -s options\n')
    err('-s substfile : add a file of substitutions\n')
    err('\n')
    err('Each non-empty non-comment line kwenye a substitution file must\n')
    err('contain exactly two words: an identifier na its replacement.\n')
    err('Comments start ukijumuisha a # character na end at end of line.\n')
    err('If an identifier ni preceded ukijumuisha a *, it ni sio substituted\n')
    err('inside a comment even when -c ni specified.\n')

eleza main():
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'crs:')
    tatizo getopt.error kama msg:
        err('Options error: ' + str(msg) + '\n')
        usage()
        sys.exit(2)
    bad = 0
    ikiwa sio args: # No arguments
        usage()
        sys.exit(2)
    kila opt, arg kwenye opts:
        ikiwa opt == '-c':
            setdocomments()
        ikiwa opt == '-r':
            setreverse()
        ikiwa opt == '-s':
            addsubst(arg)
    kila arg kwenye args:
        ikiwa os.path.isdir(arg):
            ikiwa recursedown(arg): bad = 1
        lasivyo os.path.islink(arg):
            err(arg + ': will sio process symbolic links\n')
            bad = 1
        isipokua:
            ikiwa fix(arg): bad = 1
    sys.exit(bad)

# Change this regular expression to select a different set of files
Wanted = r'^[a-zA-Z0-9_]+\.[ch]$'
eleza wanted(name):
    rudisha re.match(Wanted, name)

eleza recursedown(dirname):
    dbg('recursedown(%r)\n' % (dirname,))
    bad = 0
    jaribu:
        names = os.listdir(dirname)
    tatizo OSError kama msg:
        err(dirname + ': cannot list directory: ' + str(msg) + '\n')
        rudisha 1
    names.sort()
    subdirs = []
    kila name kwenye names:
        ikiwa name kwenye (os.curdir, os.pardir): endelea
        fullname = os.path.join(dirname, name)
        ikiwa os.path.islink(fullname): pita
        lasivyo os.path.isdir(fullname):
            subdirs.append(fullname)
        lasivyo wanted(name):
            ikiwa fix(fullname): bad = 1
    kila fullname kwenye subdirs:
        ikiwa recursedown(fullname): bad = 1
    rudisha bad

eleza fix(filename):
##  dbg('fix(%r)\n' % (filename,))
    ikiwa filename == '-':
        # Filter mode
        f = sys.stdin
        g = sys.stdout
    isipokua:
        # File replacement mode
        jaribu:
            f = open(filename, 'r')
        tatizo IOError kama msg:
            err(filename + ': cannot open: ' + str(msg) + '\n')
            rudisha 1
        head, tail = os.path.split(filename)
        tempname = os.path.join(head, '@' + tail)
        g = Tupu
    # If we find a match, we rewind the file na start over but
    # now copy everything to a temp file.
    lineno = 0
    initfixline()
    wakati 1:
        line = f.readline()
        ikiwa sio line: koma
        lineno = lineno + 1
        wakati line[-2:] == '\\\n':
            nextline = f.readline()
            ikiwa sio nextline: koma
            line = line + nextline
            lineno = lineno + 1
        newline = fixline(line)
        ikiwa newline != line:
            ikiwa g ni Tupu:
                jaribu:
                    g = open(tempname, 'w')
                tatizo IOError kama msg:
                    f.close()
                    err(tempname+': cannot create: '+
                        str(msg)+'\n')
                    rudisha 1
                f.seek(0)
                lineno = 0
                initfixline()
                rep(filename + ':\n')
                endelea # restart kutoka the beginning
            rep(repr(lineno) + '\n')
            rep('< ' + line)
            rep('> ' + newline)
        ikiwa g ni sio Tupu:
            g.write(newline)

    # End of file
    ikiwa filename == '-': rudisha 0 # Done kwenye filter mode
    f.close()
    ikiwa sio g: rudisha 0 # No changes
    g.close()

    # Finishing touch -- move files

    # First copy the file's mode to the temp file
    jaribu:
        statbuf = os.stat(filename)
        os.chmod(tempname, statbuf[ST_MODE] & 0o7777)
    tatizo OSError kama msg:
        err(tempname + ': warning: chmod failed (' + str(msg) + ')\n')
    # Then make a backup of the original file kama filename~
    jaribu:
        os.rename(filename, filename + '~')
    tatizo OSError kama msg:
        err(filename + ': warning: backup failed (' + str(msg) + ')\n')
    # Now move the temp file to the original file
    jaribu:
        os.rename(tempname, filename)
    tatizo OSError kama msg:
        err(filename + ': rename failed (' + str(msg) + ')\n')
        rudisha 1
    # Return success
    rudisha 0

# Tokenizing ANSI C (partly)

Identifier = '(struct )?[a-zA-Z_][a-zA-Z0-9_]+'
String = r'"([^\n\\"]|\\.)*"'
Char = r"'([^\n\\']|\\.)*'"
CommentStart = r'/\*'
CommentEnd = r'\*/'

Hexnumber = '0[xX][0-9a-fA-F]*[uUlL]*'
Octnumber = '0[0-7]*[uUlL]*'
Decnumber = '[1-9][0-9]*[uUlL]*'
Intnumber = Hexnumber + '|' + Octnumber + '|' + Decnumber
Exponent = '[eE][-+]?[0-9]+'
Pointfloat = r'([0-9]+\.[0-9]*|\.[0-9]+)(' + Exponent + r')?'
Expfloat = '[0-9]+' + Exponent
Floatnumber = Pointfloat + '|' + Expfloat
Number = Floatnumber + '|' + Intnumber

# Anything isipokua ni an operator -- don't list this explicitly because of '/*'

OutsideComment = (Identifier, Number, String, Char, CommentStart)
OutsideCommentPattern = '(' + '|'.join(OutsideComment) + ')'
OutsideCommentProgram = re.compile(OutsideCommentPattern)

InsideComment = (Identifier, Number, CommentEnd)
InsideCommentPattern = '(' + '|'.join(InsideComment) + ')'
InsideCommentProgram = re.compile(InsideCommentPattern)

eleza initfixline():
    global Program
    Program = OutsideCommentProgram

eleza fixline(line):
    global Program
##  andika('-->', repr(line))
    i = 0
    wakati i < len(line):
        match = Program.search(line, i)
        ikiwa match ni Tupu: koma
        i = match.start()
        found = match.group(0)
##      ikiwa Program ni InsideCommentProgram: andika(end='... ')
##      isipokua: andika(end='    ')
##      andika(found)
        ikiwa len(found) == 2:
            ikiwa found == '/*':
                Program = InsideCommentProgram
            lasivyo found == '*/':
                Program = OutsideCommentProgram
        n = len(found)
        ikiwa found kwenye Dict:
            subst = Dict[found]
            ikiwa Program ni InsideCommentProgram:
                ikiwa sio Docomments:
                    andika('Found kwenye comment:', found)
                    i = i + n
                    endelea
                ikiwa found kwenye NotInComment:
##                  andika(end='Ignored kwenye comment: ')
##                  andika(found, '-->', subst)
##                  andika('Line:', line, end='')
                    subst = found
##              isipokua:
##                  andika(end='Substituting kwenye comment: ')
##                  andika(found, '-->', subst)
##                  andika('Line:', line, end='')
            line = line[:i] + subst + line[i+n:]
            n = len(subst)
        i = i + n
    rudisha line

Docomments = 0
eleza setdocomments():
    global Docomments
    Docomments = 1

Reverse = 0
eleza setreverse():
    global Reverse
    Reverse = (sio Reverse)

Dict = {}
NotInComment = {}
eleza addsubst(substfile):
    jaribu:
        fp = open(substfile, 'r')
    tatizo IOError kama msg:
        err(substfile + ': cannot read substfile: ' + str(msg) + '\n')
        sys.exit(1)
    ukijumuisha fp:
        lineno = 0
        wakati 1:
            line = fp.readline()
            ikiwa sio line: koma
            lineno = lineno + 1
            jaribu:
                i = line.index('#')
            tatizo ValueError:
                i = -1          # Happens to delete trailing \n
            words = line[:i].split()
            ikiwa sio words: endelea
            ikiwa len(words) == 3 na words[0] == 'struct':
                words[:2] = [words[0] + ' ' + words[1]]
            lasivyo len(words) != 2:
                err(substfile + '%s:%r: warning: bad line: %r' % (substfile, lineno, line))
                endelea
            ikiwa Reverse:
                [value, key] = words
            isipokua:
                [key, value] = words
            ikiwa value[0] == '*':
                value = value[1:]
            ikiwa key[0] == '*':
                key = key[1:]
                NotInComment[key] = value
            ikiwa key kwenye Dict:
                err('%s:%r: warning: overriding: %r %r\n' % (substfile, lineno, key, value))
                err('%s:%r: warning: previous: %r\n' % (substfile, lineno, Dict[key]))
            Dict[key] = value

ikiwa __name__ == '__main__':
    main()
