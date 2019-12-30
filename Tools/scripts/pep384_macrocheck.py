"""
pep384_macrocheck.py

This programm tries to locate errors kwenye the relevant Python header
files where macros access type fields when they are reachable from
the limided API.

The idea ni to search macros ukijumuisha the string "->tp_" kwenye it.
When the macro name does sio begin ukijumuisha an underscore,
then we have found a dormant error.

Christian Tismer
2018-06-02
"""

agiza sys
agiza os
agiza re


DEBUG = Uongo

eleza dandika(*args, **kw):
    ikiwa DEBUG:
        andika(*args, **kw)

eleza parse_headerfiles(startpath):
    """
    Scan all header files which are reachable fronm Python.h
    """
    search = "Python.h"
    name = os.path.join(startpath, search)
    ikiwa sio os.path.exists(name):
        ashiria ValueError("file {} was sio found kwenye {}\n"
            "Please give the path to Python's include directory."
            .format(search, startpath))
    errors = 0
    ukijumuisha open(name) kama python_h:
        wakati Kweli:
            line = python_h.readline()
            ikiwa sio line:
                koma
            found = re.match(r'^\s*#\s*include\s*"(\w+\.h)"', line)
            ikiwa sio found:
                endelea
            include = found.group(1)
            dandika("Scanning", include)
            name = os.path.join(startpath, include)
            ikiwa sio os.path.exists(name):
                name = os.path.join(startpath, "../PC", include)
            errors += parse_file(name)
    rudisha errors

eleza ifdef_level_gen():
    """
    Scan lines kila #ifeleza na track the level.
    """
    level = 0
    ifdef_pattern = r"^\s*#\s*if"  # covers ifeleza na ifneleza kama well
    endif_pattern = r"^\s*#\s*endif"
    wakati Kweli:
        line = tuma level
        ikiwa re.match(ifdef_pattern, line):
            level += 1
        lasivyo re.match(endif_pattern, line):
            level -= 1

eleza limited_gen():
    """
    Scan lines kila Py_LIMITED_API yes(1) no(-1) ama nothing (0)
    """
    limited = [0]   # nothing
    unlimited_pattern = r"^\s*#\s*ifndef\s+Py_LIMITED_API"
    limited_pattern = "|".join([
        r"^\s*#\s*ifdef\s+Py_LIMITED_API",
        r"^\s*#\s*(el)?if\s+!\s*defined\s*\(\s*Py_LIMITED_API\s*\)\s*\|\|",
        r"^\s*#\s*(el)?if\s+defined\s*\(\s*Py_LIMITED_API"
        ])
    else_pattern =      r"^\s*#\s*else"
    ifdef_level = ifdef_level_gen()
    status = next(ifdef_level)
    wait_kila = -1
    wakati Kweli:
        line = tuma limited[-1]
        new_status = ifdef_level.send(line)
        dir = new_status - status
        status = new_status
        ikiwa dir == 1:
            ikiwa re.match(unlimited_pattern, line):
                limited.append(-1)
                wait_kila = status - 1
            lasivyo re.match(limited_pattern, line):
                limited.append(1)
                wait_kila = status - 1
        lasivyo dir == -1:
            # this must have been an endif
            ikiwa status == wait_for:
                limited.pop()
                wait_kila = -1
        isipokua:
            # it could be that we have an elif
            ikiwa re.match(limited_pattern, line):
                limited.append(1)
                wait_kila = status - 1
            lasivyo re.match(else_pattern, line):
                limited.append(-limited.pop())  # negate top

eleza parse_file(fname):
    errors = 0
    ukijumuisha open(fname) kama f:
        lines = f.readlines()
    type_pattern = r"^.*?->\s*tp_"
    define_pattern = r"^\s*#\s*define\s+(\w+)"
    limited = limited_gen()
    status = next(limited)
    kila nr, line kwenye enumerate(lines):
        status = limited.send(line)
        line = line.rstrip()
        dandika(fname, nr, status, line)
        ikiwa status != -1:
            ikiwa re.match(define_pattern, line):
                name = re.match(define_pattern, line).group(1)
                ikiwa sio name.startswith("_"):
                    # found a candidate, check it!
                    macro = line + "\n"
                    idx = nr
                    wakati line.endswith("\\"):
                        idx += 1
                        line = lines[idx].rstrip()
                        macro += line + "\n"
                    ikiwa re.match(type_pattern, macro, re.DOTALL):
                        # this type field can reach the limited API
                        report(fname, nr + 1, macro)
                        errors += 1
    rudisha errors

eleza report(fname, nr, macro):
    f = sys.stderr
    andika(fname + ":" + str(nr), file=f)
    andika(macro, file=f)

ikiwa __name__ == "__main__":
    p = sys.argv[1] ikiwa sys.argv[1:] isipokua "../../Include"
    errors = parse_headerfiles(p)
    ikiwa errors:
        # somehow it makes sense to ashiria a TypeError :-)
        ashiria TypeError("These {} locations contradict the limited API."
                        .format(errors))
