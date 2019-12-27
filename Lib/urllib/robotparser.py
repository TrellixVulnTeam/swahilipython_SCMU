""" robotparser.py

    Copyright (C) 2000  Bastian Kleineidam

    You can choose between two licenses when using this package:
    1) GNU GPLv2
    2) PSF license for Python 2.2

    The robots.txt Exclusion Protocol is implemented as specified in
    http://www.robotstxt.org/norobots-rfc.txt
"""

agiza collections
agiza urllib.parse
agiza urllib.request

__all__ = ["RobotFileParser"]

RequestRate = collections.namedtuple("RequestRate", "requests seconds")


kundi RobotFileParser:
    """ This kundi provides a set of methods to read, parse and answer
    questions about a single robots.txt file.

    """

    eleza __init__(self, url=''):
        self.entries = []
        self.sitemaps = []
        self.default_entry = None
        self.disallow_all = False
        self.allow_all = False
        self.set_url(url)
        self.last_checked = 0

    eleza mtime(self):
        """Returns the time the robots.txt file was last fetched.

        This is useful for long-running web spiders that need to
        check for new robots.txt files periodically.

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
        """Reads the robots.txt URL and feeds it to the parser."""
        try:
            f = urllib.request.urlopen(self.url)
        except urllib.error.HTTPError as err:
            ikiwa err.code in (401, 403):
                self.disallow_all = True
            elikiwa err.code >= 400 and err.code < 500:
                self.allow_all = True
        else:
            raw = f.read()
            self.parse(raw.decode("utf-8").splitlines())

    eleza _add_entry(self, entry):
        ikiwa "*" in entry.useragents:
            # the default entry is considered last
            ikiwa self.default_entry is None:
                # the first default entry wins
                self.default_entry = entry
        else:
            self.entries.append(entry)

    eleza parse(self, lines):
        """Parse the input lines kutoka a robots.txt file.

        We allow that a user-agent: line is not preceded by
        one or more blank lines.
        """
        # states:
        #   0: start state
        #   1: saw user-agent line
        #   2: saw an allow or disallow line
        state = 0
        entry = Entry()

        self.modified()
        for line in lines:
            ikiwa not line:
                ikiwa state == 1:
                    entry = Entry()
                    state = 0
                elikiwa state == 2:
                    self._add_entry(entry)
                    entry = Entry()
                    state = 0
            # remove optional comment and strip line
            i = line.find('#')
            ikiwa i >= 0:
                line = line[:i]
            line = line.strip()
            ikiwa not line:
                continue
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
                elikiwa line[0] == "disallow":
                    ikiwa state != 0:
                        entry.rulelines.append(RuleLine(line[1], False))
                        state = 2
                elikiwa line[0] == "allow":
                    ikiwa state != 0:
                        entry.rulelines.append(RuleLine(line[1], True))
                        state = 2
                elikiwa line[0] == "crawl-delay":
                    ikiwa state != 0:
                        # before trying to convert to int we need to make
                        # sure that robots.txt has valid syntax otherwise
                        # it will crash
                        ikiwa line[1].strip().isdigit():
                            entry.delay = int(line[1])
                        state = 2
                elikiwa line[0] == "request-rate":
                    ikiwa state != 0:
                        numbers = line[1].split('/')
                        # check ikiwa all values are sane
                        ikiwa (len(numbers) == 2 and numbers[0].strip().isdigit()
                            and numbers[1].strip().isdigit()):
                            entry.req_rate = RequestRate(int(numbers[0]), int(numbers[1]))
                        state = 2
                elikiwa line[0] == "sitemap":
                    # According to http://www.sitemaps.org/protocol.html
                    # "This directive is independent of the user-agent line,
                    #  so it doesn't matter where you place it in your file."
                    # Therefore we do not change the state of the parser.
                    self.sitemaps.append(line[1])
        ikiwa state == 2:
            self._add_entry(entry)

    eleza can_fetch(self, useragent, url):
        """using the parsed robots.txt decide ikiwa useragent can fetch url"""
        ikiwa self.disallow_all:
            rudisha False
        ikiwa self.allow_all:
            rudisha True
        # Until the robots.txt file has been read or found not
        # to exist, we must assume that no url is allowable.
        # This prevents false positives when a user erroneously
        # calls can_fetch() before calling read().
        ikiwa not self.last_checked:
            rudisha False
        # search for given user agent matches
        # the first match counts
        parsed_url = urllib.parse.urlparse(urllib.parse.unquote(url))
        url = urllib.parse.urlunparse(('','',parsed_url.path,
            parsed_url.params,parsed_url.query, parsed_url.fragment))
        url = urllib.parse.quote(url)
        ikiwa not url:
            url = "/"
        for entry in self.entries:
            ikiwa entry.applies_to(useragent):
                rudisha entry.allowance(url)
        # try the default entry last
        ikiwa self.default_entry:
            rudisha self.default_entry.allowance(url)
        # agent not found ==> access granted
        rudisha True

    eleza crawl_delay(self, useragent):
        ikiwa not self.mtime():
            rudisha None
        for entry in self.entries:
            ikiwa entry.applies_to(useragent):
                rudisha entry.delay
        ikiwa self.default_entry:
            rudisha self.default_entry.delay
        rudisha None

    eleza request_rate(self, useragent):
        ikiwa not self.mtime():
            rudisha None
        for entry in self.entries:
            ikiwa entry.applies_to(useragent):
                rudisha entry.req_rate
        ikiwa self.default_entry:
            rudisha self.default_entry.req_rate
        rudisha None

    eleza site_maps(self):
        ikiwa not self.sitemaps:
            rudisha None
        rudisha self.sitemaps

    eleza __str__(self):
        entries = self.entries
        ikiwa self.default_entry is not None:
            entries = entries + [self.default_entry]
        rudisha '\n\n'.join(map(str, entries))


kundi RuleLine:
    """A rule line is a single "Allow:" (allowance==True) or "Disallow:"
       (allowance==False) followed by a path."""
    eleza __init__(self, path, allowance):
        ikiwa path == '' and not allowance:
            # an empty value means allow all
            allowance = True
        path = urllib.parse.urlunparse(urllib.parse.urlparse(path))
        self.path = urllib.parse.quote(path)
        self.allowance = allowance

    eleza applies_to(self, filename):
        rudisha self.path == "*" or filename.startswith(self.path)

    eleza __str__(self):
        rudisha ("Allow" ikiwa self.allowance else "Disallow") + ": " + self.path


kundi Entry:
    """An entry has one or more user-agents and zero or more rulelines"""
    eleza __init__(self):
        self.useragents = []
        self.rulelines = []
        self.delay = None
        self.req_rate = None

    eleza __str__(self):
        ret = []
        for agent in self.useragents:
            ret.append(f"User-agent: {agent}")
        ikiwa self.delay is not None:
            ret.append(f"Crawl-delay: {self.delay}")
        ikiwa self.req_rate is not None:
            rate = self.req_rate
            ret.append(f"Request-rate: {rate.requests}/{rate.seconds}")
        ret.extend(map(str, self.rulelines))
        rudisha '\n'.join(ret)

    eleza applies_to(self, useragent):
        """check ikiwa this entry applies to the specified agent"""
        # split the name token and make it lower case
        useragent = useragent.split("/")[0].lower()
        for agent in self.useragents:
            ikiwa agent == '*':
                # we have the catch-all agent
                rudisha True
            agent = agent.lower()
            ikiwa agent in useragent:
                rudisha True
        rudisha False

    eleza allowance(self, filename):
        """Preconditions:
        - our agent applies to this entry
        - filename is URL decoded"""
        for line in self.rulelines:
            ikiwa line.applies_to(filename):
                rudisha line.allowance
        rudisha True
