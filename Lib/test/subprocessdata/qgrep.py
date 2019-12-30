"""When called ukijumuisha a single argument, simulated fgrep ukijumuisha a single
argument na no options."""

agiza sys

ikiwa __name__ == "__main__":
    pattern = sys.argv[1]
    kila line kwenye sys.stdin:
        ikiwa pattern kwenye line:
            sys.stdout.write(line)
