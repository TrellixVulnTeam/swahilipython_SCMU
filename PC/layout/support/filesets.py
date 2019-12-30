"""
File sets na globbing helper kila make_layout.
"""

__author__ = "Steve Dower <steve.dower@python.org>"
__version__ = "3.8"

agiza os


kundi FileStemSet:
    eleza __init__(self, *patterns):
        self._names = set()
        self._prefixes = []
        self._suffixes = []
        kila p kwenye map(os.path.normcase, patterns):
            ikiwa p.endswith("*"):
                self._prefixes.append(p[:-1])
            lasivyo p.startswith("*"):
                self._suffixes.append(p[1:])
            isipokua:
                self._names.add(p)

    eleza _make_name(self, f):
        rudisha os.path.normcase(f.stem)

    eleza __contains__(self, f):
        bn = self._make_name(f)
        rudisha (
            bn kwenye self._names
            ama any(map(bn.startswith, self._prefixes))
            ama any(map(bn.endswith, self._suffixes))
        )


kundi FileNameSet(FileStemSet):
    eleza _make_name(self, f):
        rudisha os.path.normcase(f.name)


kundi FileSuffixSet:
    eleza __init__(self, *patterns):
        self._names = set()
        self._prefixes = []
        self._suffixes = []
        kila p kwenye map(os.path.normcase, patterns):
            ikiwa p.startswith("*."):
                self._names.add(p[1:])
            lasivyo p.startswith("*"):
                self._suffixes.append(p[1:])
            lasivyo p.endswith("*"):
                self._prefixes.append(p[:-1])
            lasivyo p.startswith("."):
                self._names.add(p)
            isipokua:
                self._names.add("." + p)

    eleza _make_name(self, f):
        rudisha os.path.normcase(f.suffix)

    eleza __contains__(self, f):
        bn = self._make_name(f)
        rudisha (
            bn kwenye self._names
            ama any(map(bn.startswith, self._prefixes))
            ama any(map(bn.endswith, self._suffixes))
        )


eleza _rglob(root, pattern, condition):
    dirs = [root]
    recurse = pattern[:3] kwenye {"**/", "**\\"}
    ikiwa recurse:
        pattern = pattern[3:]

    wakati dirs:
        d = dirs.pop(0)
        ikiwa recurse:
            dirs.extend(
                filter(
                    condition, (type(root)(f2) kila f2 kwenye os.scandir(d) ikiwa f2.is_dir())
                )
            )
        tuma kutoka (
            (f.relative_to(root), f)
            kila f kwenye d.glob(pattern)
            ikiwa f.is_file() na condition(f)
        )


eleza _return_true(f):
    rudisha Kweli


eleza rglob(root, patterns, condition=Tupu):
    ikiwa isinstance(patterns, tuple):
        kila p kwenye patterns:
            tuma kutoka _rglob(root, p, condition ama _return_true)
    isipokua:
        tuma kutoka _rglob(root, patterns, condition ama _return_true)
