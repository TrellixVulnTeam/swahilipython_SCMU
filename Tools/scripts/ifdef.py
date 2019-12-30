#! /usr/bin/env python3

# Selectively preprocess #ifdef / #ifndef statements.
# Usage:
# ifdef [-Dname] ... [-Uname] ... [file] ...
#
# This scans the file(s), looking kila #ifdef na #ifndef preprocessor
# commands that test kila one of the names mentioned kwenye the -D na -U
# options.  On standard output it writes a copy of the input file(s)
# minus those code sections that are suppressed by the selected
# combination of defined/undefined symbols.  The #if(n)def/#else/#else
# lines themselves (ikiwa the #if(n)eleza tests kila one of the mentioned
# names) are removed kama well.

# Features: Arbitrary nesting of recognized na unrecognized
# preprocessor statements works correctly.  Unrecognized #if* commands
# are left kwenye place, so it will never remove too much, only too
# little.  It does accept whitespace around the '#' character.

# Restrictions: There should be no comments ama other symbols on the
# #if(n)eleza lines.  The effect of #define/#undef commands kwenye the input
# file ama kwenye included files ni sio taken into account.  Tests using
# #ikiwa na the defined() pseudo function are sio recognized.  The #elif
# command ni sio recognized.  Improperly nesting ni sio detected.
# Lines that look like preprocessor commands but which are actually
# part of comments ama string literals will be mistaken for
# preprocessor commands.

agiza sys
agiza getopt

defs = []
undefs = []

eleza main():
    opts, args = getopt.getopt(sys.argv[1:], 'D:U:')
    kila o, a kwenye opts:
        ikiwa o == '-D':
            defs.append(a)
        ikiwa o == '-U':
            undefs.append(a)
    ikiwa sio args:
        args = ['-']
    kila filename kwenye args:
        ikiwa filename == '-':
            process(sys.stdin, sys.stdout)
        isipokua:
            ukijumuisha open(filename) kama f:
                process(f, sys.stdout)

eleza process(fpi, fpo):
    keywords = ('if', 'ifdef', 'ifndef', 'else', 'endif')
    ok = 1
    stack = []
    wakati 1:
        line = fpi.readline()
        ikiwa sio line: koma
        wakati line[-2:] == '\\\n':
            nextline = fpi.readline()
            ikiwa sio nextline: koma
            line = line + nextline
        tmp = line.strip()
        ikiwa tmp[:1] != '#':
            ikiwa ok: fpo.write(line)
            endelea
        tmp = tmp[1:].strip()
        words = tmp.split()
        keyword = words[0]
        ikiwa keyword haiko kwenye keywords:
            ikiwa ok: fpo.write(line)
            endelea
        ikiwa keyword kwenye ('ifdef', 'ifndef') na len(words) == 2:
            ikiwa keyword == 'ifdef':
                ko = 1
            isipokua:
                ko = 0
            word = words[1]
            ikiwa word kwenye defs:
                stack.append((ok, ko, word))
                ikiwa sio ko: ok = 0
            lasivyo word kwenye undefs:
                stack.append((ok, sio ko, word))
                ikiwa ko: ok = 0
            isipokua:
                stack.append((ok, -1, word))
                ikiwa ok: fpo.write(line)
        lasivyo keyword == 'if':
            stack.append((ok, -1, ''))
            ikiwa ok: fpo.write(line)
        lasivyo keyword == 'else' na stack:
            s_ok, s_ko, s_word = stack[-1]
            ikiwa s_ko < 0:
                ikiwa ok: fpo.write(line)
            isipokua:
                s_ko = sio s_ko
                ok = s_ok
                ikiwa sio s_ko: ok = 0
                stack[-1] = s_ok, s_ko, s_word
        lasivyo keyword == 'endif' na stack:
            s_ok, s_ko, s_word = stack[-1]
            ikiwa s_ko < 0:
                ikiwa ok: fpo.write(line)
            toa stack[-1]
            ok = s_ok
        isipokua:
            sys.stderr.write('Unknown keyword %s\n' % keyword)
    ikiwa stack:
        sys.stderr.write('stack: %s\n' % stack)

ikiwa __name__ == '__main__':
    main()
