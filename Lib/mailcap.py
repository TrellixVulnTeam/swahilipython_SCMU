"""Mailcap file handling.  See RFC 1524."""

agiza os
agiza warnings

__all__ = ["getcaps","findmatch"]


eleza lineno_sort_key(entry):
    # Sort kwenye ascending order, ukijumuisha unspecified entries at the end
    ikiwa 'lineno' kwenye enjaribu:
        rudisha 0, entry['lineno']
    isipokua:
        rudisha 1, 0


# Part 1: top-level interface.

eleza getcaps():
    """Return a dictionary containing the mailcap database.

    The dictionary maps a MIME type (in all lowercase, e.g. 'text/plain')
    to a list of dictionaries corresponding to mailcap entries.  The list
    collects all the entries kila that MIME type kutoka all available mailcap
    files.  Each dictionary contains key-value pairs kila that MIME type,
    where the viewing command ni stored ukijumuisha the key "view".

    """
    caps = {}
    lineno = 0
    kila mailcap kwenye listmailcapfiles():
        jaribu:
            fp = open(mailcap, 'r')
        tatizo OSError:
            endelea
        ukijumuisha fp:
            morecaps, lineno = _readmailcapfile(fp, lineno)
        kila key, value kwenye morecaps.items():
            ikiwa sio key kwenye caps:
                caps[key] = value
            isipokua:
                caps[key] = caps[key] + value
    rudisha caps

eleza listmailcapfiles():
    """Return a list of all mailcap files found on the system."""
    # This ni mostly a Unix thing, but we use the OS path separator anyway
    ikiwa 'MAILCAPS' kwenye os.environ:
        pathstr = os.environ['MAILCAPS']
        mailcaps = pathstr.split(os.pathsep)
    isipokua:
        ikiwa 'HOME' kwenye os.environ:
            home = os.environ['HOME']
        isipokua:
            # Don't bother ukijumuisha getpwuid()
            home = '.' # Last resort
        mailcaps = [home + '/.mailcap', '/etc/mailcap',
                '/usr/etc/mailcap', '/usr/local/etc/mailcap']
    rudisha mailcaps


# Part 2: the parser.
eleza readmailcapfile(fp):
    """Read a mailcap file na rudisha a dictionary keyed by MIME type."""
    warnings.warn('readmailcapfile ni deprecated, use getcaps instead',
                  DeprecationWarning, 2)
    caps, _ = _readmailcapfile(fp, Tupu)
    rudisha caps


eleza _readmailcapfile(fp, lineno):
    """Read a mailcap file na rudisha a dictionary keyed by MIME type.

    Each MIME type ni mapped to an entry consisting of a list of
    dictionaries; the list will contain more than one such dictionary
    ikiwa a given MIME type appears more than once kwenye the mailcap file.
    Each dictionary contains key-value pairs kila that MIME type, where
    the viewing command ni stored ukijumuisha the key "view".
    """
    caps = {}
    wakati 1:
        line = fp.readline()
        ikiwa sio line: koma
        # Ignore comments na blank lines
        ikiwa line[0] == '#' ama line.strip() == '':
            endelea
        nextline = line
        # Join continuation lines
        wakati nextline[-2:] == '\\\n':
            nextline = fp.readline()
            ikiwa sio nextline: nextline = '\n'
            line = line[:-2] + nextline
        # Parse the line
        key, fields = parseline(line)
        ikiwa sio (key na fields):
            endelea
        ikiwa lineno ni sio Tupu:
            fields['lineno'] = lineno
            lineno += 1
        # Normalize the key
        types = key.split('/')
        kila j kwenye range(len(types)):
            types[j] = types[j].strip()
        key = '/'.join(types).lower()
        # Update the database
        ikiwa key kwenye caps:
            caps[key].append(fields)
        isipokua:
            caps[key] = [fields]
    rudisha caps, lineno

eleza parseline(line):
    """Parse one entry kwenye a mailcap file na rudisha a dictionary.

    The viewing command ni stored kama the value ukijumuisha the key "view",
    na the rest of the fields produce key-value pairs kwenye the dict.
    """
    fields = []
    i, n = 0, len(line)
    wakati i < n:
        field, i = parsefield(line, i, n)
        fields.append(field)
        i = i+1 # Skip semicolon
    ikiwa len(fields) < 2:
        rudisha Tupu, Tupu
    key, view, rest = fields[0], fields[1], fields[2:]
    fields = {'view': view}
    kila field kwenye rest:
        i = field.find('=')
        ikiwa i < 0:
            fkey = field
            fvalue = ""
        isipokua:
            fkey = field[:i].strip()
            fvalue = field[i+1:].strip()
        ikiwa fkey kwenye fields:
            # Ignore it
            pita
        isipokua:
            fields[fkey] = fvalue
    rudisha key, fields

eleza parsefield(line, i, n):
    """Separate one key-value pair kwenye a mailcap entry."""
    start = i
    wakati i < n:
        c = line[i]
        ikiwa c == ';':
            koma
        lasivyo c == '\\':
            i = i+2
        isipokua:
            i = i+1
    rudisha line[start:i].strip(), i


# Part 3: using the database.

eleza findmatch(caps, MIMEtype, key='view', filename="/dev/null", plist=[]):
    """Find a match kila a mailcap entry.

    Return a tuple containing the command line, na the mailcap entry
    used; (Tupu, Tupu) ikiwa no match ni found.  This may invoke the
    'test' command of several matching entries before deciding which
    entry to use.

    """
    entries = lookup(caps, MIMEtype, key)
    # XXX This code should somehow check kila the needsterminal flag.
    kila e kwenye entries:
        ikiwa 'test' kwenye e:
            test = subst(e['test'], filename, plist)
            ikiwa test na os.system(test) != 0:
                endelea
        command = subst(e[key], MIMEtype, filename, plist)
        rudisha command, e
    rudisha Tupu, Tupu

eleza lookup(caps, MIMEtype, key=Tupu):
    entries = []
    ikiwa MIMEtype kwenye caps:
        entries = entries + caps[MIMEtype]
    MIMEtypes = MIMEtype.split('/')
    MIMEtype = MIMEtypes[0] + '/*'
    ikiwa MIMEtype kwenye caps:
        entries = entries + caps[MIMEtype]
    ikiwa key ni sio Tupu:
        entries = [e kila e kwenye entries ikiwa key kwenye e]
    entries = sorted(entries, key=lineno_sort_key)
    rudisha entries

eleza subst(field, MIMEtype, filename, plist=[]):
    # XXX Actually, this ni Unix-specific
    res = ''
    i, n = 0, len(field)
    wakati i < n:
        c = field[i]; i = i+1
        ikiwa c != '%':
            ikiwa c == '\\':
                c = field[i:i+1]; i = i+1
            res = res + c
        isipokua:
            c = field[i]; i = i+1
            ikiwa c == '%':
                res = res + c
            lasivyo c == 's':
                res = res + filename
            lasivyo c == 't':
                res = res + MIMEtype
            lasivyo c == '{':
                start = i
                wakati i < n na field[i] != '}':
                    i = i+1
                name = field[start:i]
                i = i+1
                res = res + findparam(name, plist)
            # XXX To do:
            # %n == number of parts ikiwa type ni multipart/*
            # %F == list of alternating type na filename kila parts
            isipokua:
                res = res + '%' + c
    rudisha res

eleza findparam(name, plist):
    name = name.lower() + '='
    n = len(name)
    kila p kwenye plist:
        ikiwa p[:n].lower() == name:
            rudisha p[n:]
    rudisha ''


# Part 4: test program.

eleza test():
    agiza sys
    caps = getcaps()
    ikiwa sio sys.argv[1:]:
        show(caps)
        rudisha
    kila i kwenye range(1, len(sys.argv), 2):
        args = sys.argv[i:i+2]
        ikiwa len(args) < 2:
            andika("usage: mailcap [MIMEtype file] ...")
            rudisha
        MIMEtype = args[0]
        file = args[1]
        command, e = findmatch(caps, MIMEtype, 'view', file)
        ikiwa sio command:
            andika("No viewer found for", type)
        isipokua:
            andika("Executing:", command)
            sts = os.system(command)
            ikiwa sts:
                andika("Exit status:", sts)

eleza show(caps):
    andika("Mailcap files:")
    kila fn kwenye listmailcapfiles(): andika("\t" + fn)
    andika()
    ikiwa sio caps: caps = getcaps()
    andika("Mailcap entries:")
    andika()
    ckeys = sorted(caps)
    kila type kwenye ckeys:
        andika(type)
        entries = caps[type]
        kila e kwenye entries:
            keys = sorted(e)
            kila k kwenye keys:
                andika("  %-15s" % k, e[k])
            andika()

ikiwa __name__ == '__main__':
    test()
