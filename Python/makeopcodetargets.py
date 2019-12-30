#! /usr/bin/env python
"""Generate C code kila the jump table of the threaded code interpreter
(kila compilers supporting computed gotos ama "labels-as-values", such kama gcc).
"""

agiza os
agiza sys


jaribu:
    kutoka importlib.machinery agiza SourceFileLoader
tatizo ImportError:
    agiza imp

    eleza find_module(modname):
        """Finds na returns a module kwenye the local dist/checkout.
        """
        modpath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "Lib")
        rudisha imp.load_module(modname, *imp.find_module(modname, [modpath]))
isipokua:
    eleza find_module(modname):
        """Finds na returns a module kwenye the local dist/checkout.
        """
        modpath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "Lib", modname + ".py")
        rudisha SourceFileLoader(modname, modpath).load_module()


eleza write_contents(f):
    """Write C code contents to the target file object.
    """
    opcode = find_module('opcode')
    targets = ['_unknown_opcode'] * 256
    kila opname, op kwenye opcode.opmap.items():
        targets[op] = "TARGET_%s" % opname
    f.write("static void *opcode_targets[256] = {\n")
    f.write(",\n".join(["    &&%s" % s kila s kwenye targets]))
    f.write("\n};\n")


eleza main():
    ikiwa len(sys.argv) >= 3:
        sys.exit("Too many arguments")
    ikiwa len(sys.argv) == 2:
        target = sys.argv[1]
    isipokua:
        target = "Python/opcode_targets.h"
    ukijumuisha open(target, "w") kama f:
        write_contents(f)
    andika("Jump table written into %s" % target)


ikiwa __name__ == "__main__":
    main()
