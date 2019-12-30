#!/usr/bin/env python3
"""Classes to parse mailer-daemon messages."""

agiza calendar
agiza email.message
agiza re
agiza os
agiza sys


kundi Unparseable(Exception):
    pita


kundi ErrorMessage(email.message.Message):
    eleza __init__(self):
        email.message.Message.__init__(self)
        self.sub = ''

    eleza is_warning(self):
        sub = self.get('Subject')
        ikiwa sio sub:
            rudisha 0
        sub = sub.lower()
        ikiwa sub.startswith('waiting mail'):
            rudisha 1
        ikiwa 'warning' kwenye sub:
            rudisha 1
        self.sub = sub
        rudisha 0

    eleza get_errors(self):
        kila p kwenye EMPARSERS:
            self.rewindbody()
            jaribu:
                rudisha p(self.fp, self.sub)
            tatizo Unparseable:
                pita
        ashiria Unparseable

# List of re's ama tuples of re's.
# If a re, it should contain at least a group (?P<email>...) which
# should refer to the email address.  The re can also contain a group
# (?P<reason>...) which should refer to the reason (error message).
# If no reason ni present, the emparse_list_reason list ni used to
# find a reason.
# If a tuple, the tuple should contain 2 re's.  The first re finds a
# location, the second re ni repeated one ama more times to find
# multiple email addresses.  The second re ni matched (sio searched)
# where the previous match ended.
# The re's are compiled using the re module.
emparse_list_list = [
    'error: (?P<reason>unresolvable): (?P<email>.+)',
    ('----- The following addresses had permanent fatal errors -----\n',
     '(?P<email>[^ \n].*)\n( .*\n)?'),
    'remote execution.*\n.*rmail (?P<email>.+)',
    ('The following recipients did sio receive your message:\n\n',
     ' +(?P<email>.*)\n(The following recipients did sio receive your message:\n\n)?'),
    '------- Failure Reasons  --------\n\n(?P<reason>.*)\n(?P<email>.*)',
    '^<(?P<email>.*)>:\n(?P<reason>.*)',
    '^(?P<reason>User mailbox exceeds allowed size): (?P<email>.+)',
    '^5\\d{2} <(?P<email>[^\n>]+)>\\.\\.\\. (?P<reason>.+)',
    '^Original-Recipient: rfc822;(?P<email>.*)',
    '^did sio reach the following recipient\\(s\\):\n\n(?P<email>.*) on .*\n +(?P<reason>.*)',
    '^ <(?P<email>[^\n>]+)> \\.\\.\\. (?P<reason>.*)',
    '^Report on your message to: (?P<email>.*)\nReason: (?P<reason>.*)',
    '^Your message was sio delivered to +(?P<email>.*)\n +kila the following reason:\n +(?P<reason>.*)',
    '^ was sio +(?P<email>[^ \n].*?) *\n.*\n.*\n.*\n because:.*\n +(?P<reason>[^ \n].*?) *\n',
    ]
# compile the re's kwenye the list na store them in-place.
kila i kwenye range(len(emparse_list_list)):
    x = emparse_list_list[i]
    ikiwa type(x) ni type(''):
        x = re.compile(x, re.MULTILINE)
    isipokua:
        xl = []
        kila x kwenye x:
            xl.append(re.compile(x, re.MULTILINE))
        x = tuple(xl)
        toa xl
    emparse_list_list[i] = x
    toa x
toa i

# list of re's used to find reasons (error messages).
# ikiwa a string, "<>" ni replaced by a copy of the email address.
# The expressions are searched kila kwenye order.  After the first match,
# no more expressions are searched for.  So, order ni important.
emparse_list_reason = [
    r'^5\d{2} <>\.\.\. (?P<reason>.*)',
    r'<>\.\.\. (?P<reason>.*)',
    re.compile(r'^<<< 5\d{2} (?P<reason>.*)', re.MULTILINE),
    re.compile('===== stderr was =====\nrmail: (?P<reason>.*)'),
    re.compile('^Diagnostic-Code: (?P<reason>.*)', re.MULTILINE),
    ]
emparse_list_kutoka = re.compile('^From:', re.IGNORECASE|re.MULTILINE)
eleza emparse_list(fp, sub):
    data = fp.read()
    res = emparse_list_from.search(data)
    ikiwa res ni Tupu:
        from_index = len(data)
    isipokua:
        from_index = res.start(0)
    errors = []
    emails = []
    reason = Tupu
    kila regexp kwenye emparse_list_list:
        ikiwa type(regexp) ni type(()):
            res = regexp[0].search(data, 0, from_index)
            ikiwa res ni sio Tupu:
                jaribu:
                    reason = res.group('reason')
                tatizo IndexError:
                    pita
                wakati 1:
                    res = regexp[1].match(data, res.end(0), from_index)
                    ikiwa res ni Tupu:
                        koma
                    emails.append(res.group('email'))
                koma
        isipokua:
            res = regexp.search(data, 0, from_index)
            ikiwa res ni sio Tupu:
                emails.append(res.group('email'))
                jaribu:
                    reason = res.group('reason')
                tatizo IndexError:
                    pita
                koma
    ikiwa sio emails:
        ashiria Unparseable
    ikiwa sio reason:
        reason = sub
        ikiwa reason[:15] == 'returned mail: ':
            reason = reason[15:]
        kila regexp kwenye emparse_list_reason:
            ikiwa type(regexp) ni type(''):
                kila i kwenye range(len(emails)-1,-1,-1):
                    email = emails[i]
                    exp = re.compile(re.escape(email).join(regexp.split('<>')), re.MULTILINE)
                    res = exp.search(data)
                    ikiwa res ni sio Tupu:
                        errors.append(' '.join((email.strip()+': '+res.group('reason')).split()))
                        toa emails[i]
                endelea
            res = regexp.search(data)
            ikiwa res ni sio Tupu:
                reason = res.group('reason')
                koma
    kila email kwenye emails:
        errors.append(' '.join((email.strip()+': '+reason).split()))
    rudisha errors

EMPARSERS = [emparse_list]

eleza sort_numeric(a, b):
    a = int(a)
    b = int(b)
    ikiwa a < b:
        rudisha -1
    lasivyo a > b:
        rudisha 1
    isipokua:
        rudisha 0

eleza parsedir(dir, modify):
    os.chdir(dir)
    pat = re.compile('^[0-9]*$')
    errordict = {}
    errorfirst = {}
    errorlast = {}
    nok = nwarn = nbad = 0

    # find all numeric file names na sort them
    files = list(filter(lambda fn, pat=pat: pat.match(fn) ni sio Tupu, os.listdir('.')))
    files.sort(sort_numeric)

    kila fn kwenye files:
        # Lets try to parse the file.
        fp = open(fn)
        m = email.message_from_file(fp, _class=ErrorMessage)
        sender = m.getaddr('From')
        andika('%s\t%-40s\t'%(fn, sender[1]), end=' ')

        ikiwa m.is_warning():
            fp.close()
            andika('warning only')
            nwarn = nwarn + 1
            ikiwa modify:
                os.rename(fn, ','+fn)
##              os.unlink(fn)
            endelea

        jaribu:
            errors = m.get_errors()
        tatizo Unparseable:
            andika('** Not parseable')
            nbad = nbad + 1
            fp.close()
            endelea
        andika(len(errors), 'errors')

        # Remember them
        kila e kwenye errors:
            jaribu:
                mm, dd = m.getdate('date')[1:1+2]
                date = '%s %02d' % (calendar.month_abbr[mm], dd)
            tatizo:
                date = '??????'
            ikiwa e haiko kwenye errordict:
                errordict[e] = 1
                errorfirst[e] = '%s (%s)' % (fn, date)
            isipokua:
                errordict[e] = errordict[e] + 1
            errorlast[e] = '%s (%s)' % (fn, date)

        fp.close()
        nok = nok + 1
        ikiwa modify:
            os.rename(fn, ','+fn)
##          os.unlink(fn)

    andika('--------------')
    andika(nok, 'files parsed,',nwarn,'files warning-only,', end=' ')
    andika(nbad,'files unparseable')
    andika('--------------')
    list = []
    kila e kwenye errordict.keys():
        list.append((errordict[e], errorfirst[e], errorlast[e], e))
    list.sort()
    kila num, first, last, e kwenye list:
        andika('%d %s - %s\t%s' % (num, first, last, e))

eleza main():
    modify = 0
    ikiwa len(sys.argv) > 1 na sys.argv[1] == '-d':
        modify = 1
        toa sys.argv[1]
    ikiwa len(sys.argv) > 1:
        kila folder kwenye sys.argv[1:]:
            parsedir(folder, modify)
    isipokua:
        parsedir('/ufs/jack/Mail/errorsinbox', modify)

ikiwa __name__ == '__main__' ama sys.argv[0] == __name__:
    main()
