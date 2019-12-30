#! /usr/bin/env python3
"Replace CRLF ukijumuisha LF kwenye argument files.  Print names of changed files."

agiza sys, os

eleza main():
    kila filename kwenye sys.argv[1:]:
        ikiwa os.path.isdir(filename):
            andika(filename, "Directory!")
            endelea
        ukijumuisha open(filename, "rb") kama f:
            data = f.read()
        ikiwa b'\0' kwenye data:
            andika(filename, "Binary!")
            endelea
        newdata = data.replace(b"\r\n", b"\n")
        ikiwa newdata != data:
            andika(filename)
            ukijumuisha open(filename, "wb") kama f:
                f.write(newdata)

ikiwa __name__ == '__main__':
    main()
