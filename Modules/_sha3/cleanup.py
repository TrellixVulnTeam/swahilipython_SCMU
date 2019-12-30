#!/usr/bin/env python
# Copyright (C) 2012   Christian Heimes (christian@python.org)
# Licensed to PSF under a Contributor Agreement.
#
# cleanup Keccak sources

agiza os
agiza re

CPP1 = re.compile("^//(.*)")
CPP2 = re.compile(r"\ //(.*)")

STATICS = ("void ", "int ", "HashReturn ",
           "const UINT64 ", "UINT16 ", "    int prefix##")

HERE = os.path.dirname(os.path.abspath(__file__))
KECCAK = os.path.join(HERE, "kcp")

eleza getfiles():
    kila name kwenye os.listdir(KECCAK):
        name = os.path.join(KECCAK, name)
        ikiwa os.path.isfile(name):
            tuma name

eleza cleanup(f):
    buf = []
    kila line kwenye f:
        # mark all functions na global data kama static
        #ikiwa line.startswith(STATICS):
        #    buf.append("static " + line)
        #    endelea
        # remove UINT64 typedef, we have our own
        ikiwa line.startswith("typeeleza unsigned long long int"):
            buf.append("/* %s */\n" % line.strip())
            endelea
        ## remove #include "brg_endian.h"
        ikiwa "brg_endian.h" kwenye line:
            buf.append("/* %s */\n" % line.strip())
            endelea
        # transform C++ comments into ANSI C comments
        line = CPP1.sub(r"/*\1 */\n", line)
        line = CPP2.sub(r" /*\1 */\n", line)
        buf.append(line)
    rudisha "".join(buf)

kila name kwenye getfiles():
    ukijumuisha open(name) kama f:
        res = cleanup(f)
    ukijumuisha open(name, "w") kama f:
        f.write(res)
