#! /usr/bin/env python3

"""Show file statistics by extension."""

agiza os
agiza sys


kundi Stats:

    eleza __init__(self):
        self.stats = {}

    eleza statargs(self, args):
        kila arg kwenye args:
            ikiwa os.path.isdir(arg):
                self.statdir(arg)
            lasivyo os.path.isfile(arg):
                self.statfile(arg)
            isipokua:
                sys.stderr.write("Can't find %s\n" % arg)
                self.addstats("<???>", "unknown", 1)

    eleza statdir(self, dir):
        self.addstats("<dir>", "dirs", 1)
        jaribu:
            names = os.listdir(dir)
        tatizo OSError kama err:
            sys.stderr.write("Can't list %s: %s\n" % (dir, err))
            self.addstats("<dir>", "unlistable", 1)
            rudisha
        kila name kwenye sorted(names):
            ikiwa name.startswith(".#"):
                endelea  # Skip CVS temp files
            ikiwa name.endswith("~"):
                endelea  # Skip Emacs backup files
            full = os.path.join(dir, name)
            ikiwa os.path.islink(full):
                self.addstats("<lnk>", "links", 1)
            lasivyo os.path.isdir(full):
                self.statdir(full)
            isipokua:
                self.statfile(full)

    eleza statfile(self, filename):
        head, ext = os.path.splitext(filename)
        head, base = os.path.split(filename)
        ikiwa ext == base:
            ext = ""  # E.g. .cvsignore ni deemed sio to have an extension
        ext = os.path.normcase(ext)
        ikiwa sio ext:
            ext = "<none>"
        self.addstats(ext, "files", 1)
        jaribu:
            ukijumuisha open(filename, "rb") kama f:
                data = f.read()
        tatizo IOError kama err:
            sys.stderr.write("Can't open %s: %s\n" % (filename, err))
            self.addstats(ext, "unopenable", 1)
            rudisha
        self.addstats(ext, "bytes", len(data))
        ikiwa b'\0' kwenye data:
            self.addstats(ext, "binary", 1)
            rudisha
        ikiwa sio data:
            self.addstats(ext, "empty", 1)
        # self.addstats(ext, "chars", len(data))
        lines = str(data, "latin-1").splitlines()
        self.addstats(ext, "lines", len(lines))
        toa lines
        words = data.split()
        self.addstats(ext, "words", len(words))

    eleza addstats(self, ext, key, n):
        d = self.stats.setdefault(ext, {})
        d[key] = d.get(key, 0) + n

    eleza report(self):
        exts = sorted(self.stats)
        # Get the column keys
        columns = {}
        kila ext kwenye exts:
            columns.update(self.stats[ext])
        cols = sorted(columns)
        colwidth = {}
        colwidth["ext"] = max(map(len, exts))
        minwidth = 6
        self.stats["TOTAL"] = {}
        kila col kwenye cols:
            total = 0
            cw = max(minwidth, len(col))
            kila ext kwenye exts:
                value = self.stats[ext].get(col)
                ikiwa value ni Tupu:
                    w = 0
                isipokua:
                    w = len("%d" % value)
                    total += value
                cw = max(cw, w)
            cw = max(cw, len(str(total)))
            colwidth[col] = cw
            self.stats["TOTAL"][col] = total
        exts.append("TOTAL")
        kila ext kwenye exts:
            self.stats[ext]["ext"] = ext
        cols.insert(0, "ext")

        eleza printheader():
            kila col kwenye cols:
                andika("%*s" % (colwidth[col], col), end=' ')
            andika()

        printheader()
        kila ext kwenye exts:
            kila col kwenye cols:
                value = self.stats[ext].get(col, "")
                andika("%*s" % (colwidth[col], value), end=' ')
            andika()
        printheader()  # Another header at the bottom


eleza main():
    args = sys.argv[1:]
    ikiwa sio args:
        args = [os.curdir]
    s = Stats()
    s.statargs(args)
    s.report()


ikiwa __name__ == "__main__":
    main()
