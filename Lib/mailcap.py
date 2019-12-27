"""Mailcap file handling.  See RFC 1524."""

agiza os
agiza warnings

__all__ = ["getcaps","findmatch"]


eleza lineno_sort_key(entry):
    # Sort in ascending order, with unspecified entries at the end
    ikiwa 'lineno' in entry:
        rudisha 0, entry['lineno']
    else:
        rudisha 1, 0


# Part 1: top-level interface.

eleza getcaps():
    """Return a dictionary containing the mailcap database.

    The dictionary maps a MIME type (in all lowercase, e.g. 'text/plain')
    to a list of dictionaries corresponding to mailcap entries.  The list
    collects all the entries for that MIME type kutoka all available mailcap
    files.  Each dictionary contains key-value pairs for that MIME type,
    where the viewing command is stored with the key "view".

    """
    caps = {}
    lineno = 0
    for mailcap in listmailcapfiles():
        try:
            fp = open(mailcap, 'r')
        except OSError:
            continue
        with fp:
            morecaps, lineno = _readmailcapfile(fp, lineno)
        for key, value in morecaps.items():
            ikiwa not key in caps:
                caps[key] = value
            else:
                caps[key] = caps[key] + value
    rudisha caps

eleza listmailcapfiles():
    """Return a list of all mailcap files found on the system."""
    # This is mostly a Unix thing, but we use the OS path separator anyway
    ikiwa 'MAILCAPS' in os.environ:
        pathstr = os.environ['MAILCAPS']
        mailcaps = pathstr.split(os.pathsep)
    else:
        ikiwa 'HOME' in os.environ:
            home = os.environ['HOME']
        else:
            # Don't bother with getpwuid()
            home = '.' # Last resort
        mailcaps = [home + '/.mailcap', '/etc/mailcap',
                '/usr/etc/mailcap', '/usr/local/etc/mailcap']
    rudisha mailcaps


# Part 2: the parser.
eleza readmailcapfile(fp):
    """Read a mailcap file and rudisha a dictionary keyed by MIME type."""
    warnings.warn('readmailcapfile is deprecated, use getcaps instead',
                  DeprecationWarning, 2)
    caps, _ = _readmailcapfile(fp, None)
    rudisha caps


eleza _readmailcapfile(fp, lineno):
    """Read a mailcap file and rudisha a dictionary keyed by MIME type.

    Each MIME type is mapped to an entry consisting of a list of
    dictionaries; the list will contain more than one such dictionary
    ikiwa a given MIME type appears more than once in the mailcap file.
    Each dictionary contains key-value pairs for that MIME type, where
    the viewing command is stored with the key "view".
    """
    caps = {}
    while 1:
        line = fp.readline()
        ikiwa not line: break
        # Ignore comments and blank lines
        ikiwa line[0] == '#' or line.strip() == '':
            continue
        nextline = line
        # Join continuation lines
        while nextline[-2:] == '\\\n':
            nextline = fp.readline()
            ikiwa not nextline: nextline = '\n'
            line = line[:-2] + nextline
        # Parse the line
        key, fields = parseline(line)
        ikiwa not (key and fields):
            continue
        ikiwa lineno is not None:
            fields['lineno'] = lineno
            lineno += 1
        # Normalize the key
        types = key.split('/')
        for j in range(len(types)):
            types[j] = types[j].strip()
        key = '/'.join(types).lower()
        # Update the database
        ikiwa key in caps:
            caps[key].append(fields)
        else:
            caps[key] = [fields]
    rudisha caps, lineno

eleza parseline(line):
    """Parse one entry in a mailcap file and rudisha a dictionary.

    The viewing command is stored as the value with the key "view",
    and the rest of the fields produce key-value pairs in the dict.
    """
    fields = []
    i, n = 0, len(line)
    while i < n:
        field, i = parsefield(line, i, n)
        fields.append(field)
        i = i+1 # Skip semicolon
    ikiwa len(fields) < 2:
        rudisha None, None
    key, view, rest = fields[0], fields[1], fields[2:]
    fields = {'view': view}
    for field in rest:
        i = field.find('=')
        ikiwa i < 0:
            fkey = field
            fvalue = ""
        else:
            fkey = field[:i].strip()
            fvalue = field[i+1:].strip()
        ikiwa fkey in fields:
            # Ignore it
            pass
        else:
            fields[fkey] = fvalue
    rudisha key, fields

eleza parsefield(line, i, n):
    """Separate one key-value pair in a mailcap entry."""
    start = i
    while i < n:
        c = line[i]
        ikiwa c == ';':
            break
        elikiwa c == '\\':
            i = i+2
        else:
            i = i+1
    rudisha line[start:i].strip(), i


# Part 3: using the database.

eleza findmatch(caps, MIMEtype, key='view', filename="/dev/null", plist=[]):
    """Find a match for a mailcap entry.

    Return a tuple containing the command line, and the mailcap entry
    used; (None, None) ikiwa no match is found.  This may invoke the
    'test' command of several matching entries before deciding which
    entry to use.

    """
    entries = lookup(caps, MIMEtype, key)
    # XXX This code should somehow check for the needsterminal flag.
    for e in entries:
        ikiwa 'test' in e:
            test = subst(e['test'], filename, plist)
            ikiwa test and os.system(test) != 0:
                continue
        command = subst(e[key], MIMEtype, filename, plist)
        rudisha command, e
    rudisha None, None

eleza lookup(caps, MIMEtype, key=None):
    entries = []
    ikiwa MIMEtype in caps:
        entries = entries + caps[MIMEtype]
    MIMEtypes = MIMEtype.split('/')
    MIMEtype = MIMEtypes[0] + '/*'
    ikiwa MIMEtype in caps:
        entries = entries + caps[MIMEtype]
    ikiwa key is not None:
        entries = [e for e in entries ikiwa key in e]
    entries = sorted(entries, key=lineno_sort_key)
    rudisha entries

eleza subst(field, MIMEtype, filename, plist=[]):
    # XXX Actually, this is Unix-specific
    res = ''
    i, n = 0, len(field)
    while i < n:
        c = field[i]; i = i+1
        ikiwa c != '%':
            ikiwa c == '\\':
                c = field[i:i+1]; i = i+1
            res = res + c
        else:
            c = field[i]; i = i+1
            ikiwa c == '%':
                res = res + c
            elikiwa c == 's':
                res = res + filename
            elikiwa c == 't':
                res = res + MIMEtype
            elikiwa c == '{':
                start = i
                while i < n and field[i] != '}':
                    i = i+1
                name = field[start:i]
                i = i+1
                res = res + findparam(name, plist)
            # XXX To do:
            # %n == number of parts ikiwa type is multipart/*
            # %F == list of alternating type and filename for parts
            else:
                res = res + '%' + c
    rudisha res

eleza findparam(name, plist):
    name = name.lower() + '='
    n = len(name)
    for p in plist:
        ikiwa p[:n].lower() == name:
            rudisha p[n:]
    rudisha ''


# Part 4: test program.

eleza test():
    agiza sys
    caps = getcaps()
    ikiwa not sys.argv[1:]:
        show(caps)
        return
    for i in range(1, len(sys.argv), 2):
        args = sys.argv[i:i+2]
        ikiwa len(args) < 2:
            andika("usage: mailcap [MIMEtype file] ...")
            return
        MIMEtype = args[0]
        file = args[1]
        command, e = findmatch(caps, MIMEtype, 'view', file)
        ikiwa not command:
            andika("No viewer found for", type)
        else:
            andika("Executing:", command)
            sts = os.system(command)
            ikiwa sts:
                andika("Exit status:", sts)

eleza show(caps):
    andika("Mailcap files:")
    for fn in listmailcapfiles(): andika("\t" + fn)
    andika()
    ikiwa not caps: caps = getcaps()
    andika("Mailcap entries:")
    andika()
    ckeys = sorted(caps)
    for type in ckeys:
        andika(type)
        entries = caps[type]
        for e in entries:
            keys = sorted(e)
            for k in keys:
                andika("  %-15s" % k, e[k])
            andika()

ikiwa __name__ == '__main__':
    test()
