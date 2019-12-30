#!/usr/bin/env python3

# Make a reST file compliant to our pre-commit hook.
# Currently just remove trailing whitespace.

agiza sys

agiza patchcheck

eleza main(argv=sys.argv):
    patchcheck.normalize_docs_whitespace(argv[1:])

ikiwa __name__ == '__main__':
    sys.exit(main())
