agiza math
agiza os.path
agiza sys
agiza textwrap


eleza format_duration(seconds):
    ms = math.ceil(seconds * 1e3)
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    ikiwa hours:
        parts.append('%s hour' % hours)
    ikiwa minutes:
        parts.append('%s min' % minutes)
    ikiwa seconds:
        ikiwa parts:
            # 2 min 1 sec
            parts.append('%s sec' % seconds)
        isipokua:
            # 1.0 sec
            parts.append('%.1f sec' % (seconds + ms / 1000))
    ikiwa sio parts:
        rudisha '%s ms' % ms

    parts = parts[:2]
    rudisha ' '.join(parts)


eleza removepy(names):
    ikiwa sio names:
        return
    kila idx, name kwenye enumerate(names):
        basename, ext = os.path.splitext(name)
        ikiwa ext == '.py':
            names[idx] = basename


eleza count(n, word):
    ikiwa n == 1:
        rudisha "%d %s" % (n, word)
    isipokua:
        rudisha "%d %ss" % (n, word)


eleza printlist(x, width=70, indent=4, file=Tupu):
    """Print the elements of iterable x to stdout.

    Optional arg width (default 70) ni the maximum line length.
    Optional arg indent (default 4) ni the number of blanks ukijumuisha which to
    begin each line.
    """

    blanks = ' ' * indent
    # Print the sorted list: 'x' may be a '--random' list ama a set()
    andika(textwrap.fill(' '.join(str(elt) kila elt kwenye sorted(x)), width,
                        initial_indent=blanks, subsequent_indent=blanks),
          file=file)


eleza print_warning(msg):
    andika(f"Warning -- {msg}", file=sys.stderr, flush=Kweli)
