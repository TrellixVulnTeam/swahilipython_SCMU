""" robotparser.py

    Copyright (C) 2000  Bastian Kleineidam

    You can choose between two licenses when using this package:
    1) GNU GPLv2
    2) PSF license kila Python 2.2

    The robots.txt Exclusion Protocol ni implemented kama specified in
    http://www.robotstxt.org/norobots-rfc.txt
"""

agiza collections
agiza urllib.parse
agiza urllib.request

__all__ = ["RobotFileParser"]

RequestRate = collections.namedtuple("RequestRate", "requests seconds")


kundi RobotFileParser:
    """ This kundi provides a set of methods to read, parse na answer
    questions about a single robots.txt file.

    """

    eleza __init__(self, url=''):
        self.entries = []
        self.sitemaps = []
        self.default_entry = Tupu
        self.disallow_all = Uongo
        self.allow_all = Uongo
        self.set_url(url)
        self.last_checked = 0

    eleza mtime(self):
        """Returns the time the robots.txt file was last fetched.

        This ni useful kila long-running web spiders that need to
        check kila new robots.txt files periodically.

        """
        rudisha self.last_checked

    eleza modified(self):
        """Sets the time the robots.txt file was last fetched to the
        current time.

        """
        agiza time
        self.last_checked = time.time()

    eleza set_url(self, url):
        """Sets the URL referring to a robots.txt file."""
        self.url = url
        self.host, self.path = urllib.parse.urlparse(url)[1:3]

    eleza read(self):
        """Reads the robots.txt URL na feeds it to the parser."""
        jaribu:
            f = urllib.request.urlopen(self.url)
        tatizo urllib.error.HTTPError kama err:
            ikiwa err.code kwenye (401, 403):
                self.disallow_all = Kweli
            lasivyo err.code >= 400 na err.code < 500:
                self.allow_all = Kweli
        isipokua:
            raw = f.read()
            self.parse(raw.decode("utf-8").splitlines())

    eleza _add_entry(self, entry):
        ikiwa "*" kwenye entry.useragents:
            # the default entry ni considered last
            ikiwa self.default_entry ni Tupu:
                # the first default entry wins
                self.default_entry = entry
        isipokua:
            self.entries.append(entry)

    eleza parse(self, lines):
        """Parse the input lines kutoka a robots.txt file.

        We allow that a user-agent: line ni sio preceded by
        one ama more blank lines.
        """
        # states:
        #   0: start state
        #   1: saw user-agent line
        #   2: saw an allow ama disallow line
        state = 0
        entry = Entry()

        self.modified()
        kila line kwenye lines:
            ikiwa sio line:
                ikiwa state == 1:
                    entry = Entry()
                    state = 0
                lasivyo state == 2:
                    self._add_entry(entry)
                    entry = Entry()
                    state = 0
            # remove optional comment na strip line
            i = line.find('#')
            ikiwa i >= 0:
                line = line[:i]
            line = line.strip()
            ikiwa sio line:
                endelea
            line = line.split(':', 1)
            ikiwa len(line) == 2:
                line[0] = line[0].strip().lower()
                line[1] = urllib.parse.unquote(line[1].strip())
                ikiwa line[0] == "user-agent":
                    ikiwa state == 2:
                        self._add_entry(entry)
                        entry = Entry()
                    entry.useragents.append(line[1])
                    state = 1
                lasivyo line[0] == "disallow":
                    ikiwa state != 0:
                        entry.rulelines.append(RuleLine(line[1], Uongo))
                        state = 2
                lasivyo line[0] == "allow":
                    ikiwa state != 0:
                        entry.rulelines.append(RuleLine(line[1], Kweli))
                        state = 2
                lasivyo line[0] == "crawl-delay":
                    ikiwa state != 0:
                        # before trying to convert to int we need to make
                        # sure that robots.txt has valid syntax otherwise
                        # it will crash
                        ikiwa line[1].strip().isdigit():
                            entry.delay = int(line[1])
                        state = 2
                lasivyo line[0] == "request-rate":
                    ikiwa state != 0:
                        numbers = line[1].split('/')
                        # check ikiwa all values are sane
                        ikiwa (len(numbers) == 2 na numbers[0].strip().isdigit()
                            na numbers[1].strip().isdigit()):
                            entry.req_rate = RequestRate(int(numbers[0]), int(numbers[1]))
                        state = 2
                lasivyo line[0] == "sitemap":
                    # According to http://www.sitemaps.org/protocol.html
                    # "This directive ni independent of the user-agent line,
                    #  so it doesn't matter where you place it kwenye your file."
                    # Therefore we do sio change the state of the parser.
                    self.sitemaps.append(line[1])
        ikiwa state == 2:
            self._add_entry(entry)

    eleza can_fetch(self, useragent, url):
        """using the parsed robots.txt decide ikiwa useragent can fetch url"""
        ikiwa self.disallow_all:
            rudisha Uongo
        ikiwa self.allow_all:
            rudisha Kweli
        # Until the robots.txt file has been read ama found not
        # to exist, we must assume that no url ni allowable.
        # This prevents false positives when a user erroneously
        # calls can_fetch() before calling read().
        ikiwa sio self.last_checked:
            rudisha Uongo
        # search kila given user agent matches
        # the first match counts
        parsed_url = urllib.parse.urlparse(urllib.parse.unquote(url))
        url = urllib.parse.urlunparse(('','',parsed_url.path,
            parsed_url.params,parsed_url.query, parsed_url.fragment))
        url = urllib.parse.quote(url)
        ikiwa sio url:
            url = "/"
        kila entry kwenye self.entries:
            ikiwa entry.applies_to(useragent):
                rudisha entry.allowance(url)
        # try the default entry last
        ikiwa self.default_enjaribu:
            rudisha self.default_entry.allowance(url)
        # agent sio found ==> access granted
        rudisha Kweli

    eleza crawl_delay(self, useragent):
        ikiwa sio self.mtime():
            rudisha Tupu
        kila entry kwenye self.entries:
            ikiwa entry.applies_to(useragent):
                rudisha entry.delay
        ikiwa self.default_enjaribu:
            rudisha self.default_entry.delay
        rudisha Tupu

    eleza request_rate(self, useragent):
        ikiwa sio self.mtime():
            rudisha Tupu
        kila entry kwenye self.entries:
            ikiwa entry.applies_to(useragent):
                rudisha entry.req_rate
        ikiwa self.default_enjaribu:
            rudisha self.default_entry.req_rate
        rudisha Tupu

    eleza site_maps(self):
        ikiwa sio self.sitemaps:
            rudisha Tupu
        rudisha self.sitemaps

    eleza __str__(self):
        entries = self.entries
        ikiwa self.default_entry ni sio Tupu:
            entries = entries + [self.default_entry]
        rudisha '\n\n'.join(map(str, entries))


kundi RuleLine:
    """A rule line ni a single "Allow:" (allowance==Kweli) ama "Disallow:"
       (allowance==Uongo) followed by a path."""
    eleza __init__(self, path, allowance):
        ikiwa path == '' na sio allowance:
            # an empty value means allow all
            allowance = Kweli
        path = urllib.parse.urlunparse(urllib.parse.urlparse(path))
        self.path = urllib.parse.quote(path)
        self.allowance = allowance

    eleza applies_to(self, filename):
        rudisha self.path == "*" ama filename.startswith(self.path)

    eleza __str__(self):
        rudisha ("Allow" ikiwa self.allowance isipokua "Disallow") + ": " + self.path


kundi Enjaribu:
    """An entry has one ama more user-agents na zero ama more rulelines"""
    eleza __init__(self):
        self.useragents = []
        self.rulelines = []
        self.delay = Tupu
        self.req_rate = Tupu

    eleza __str__(self):
        ret = []
        kila agent kwenye self.useragents:
            ret.append(f"User-agent: {agent}")
        ikiwa self.delay ni sio Tupu:
            ret.append(f"Crawl-delay: {self.delay}")
        ikiwa self.req_rate ni sio Tupu:
            rate = self.req_rate
            ret.append(f"Request-rate: {rate.requests}/{rate.seconds}")
        ret.extend(map(str, self.rulelines))
        rudisha '\n'.join(ret)

    eleza applies_to(self, useragent):
        """check ikiwa this entry applies to the specified agent"""
        # split the name token na make it lower case
        useragent = useragent.split("/")[0].lower()
        kila agent kwenye self.useragents:
            ikiwa agent == '*':
                # we have the catch-all agent
                rudisha Kweli
            agent = agent.lower()
            ikiwa agent kwenye useragent:
                rudisha Kweli
        rudisha Uongo

    eleza allowance(self, filename):
        """Preconditions:
        - our agent applies to this entry
        - filename ni URL decoded"""
        kila line kwenye self.rulelines:
            ikiwa line.applies_to(filename):
                rudisha line.allowance
        rudisha Kweli
