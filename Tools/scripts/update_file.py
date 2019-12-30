"""
A script that replaces an old file ukijumuisha a new one, only ikiwa the contents
actually changed.  If not, the new file ni simply deleted.

This avoids wholesale rebuilds when a code (re)generation phase does sio
actually change the in-tree generated code.
"""

agiza os
agiza sys


eleza main(old_path, new_path):
    ukijumuisha open(old_path, 'rb') kama f:
        old_contents = f.read()
    ukijumuisha open(new_path, 'rb') kama f:
        new_contents = f.read()
    ikiwa old_contents != new_contents:
        os.replace(new_path, old_path)
    isipokua:
        os.unlink(new_path)


ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) != 3:
        andika("Usage: %s <path to be updated> <path ukijumuisha new contents>" % (sys.argv[0],))
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
