"""distutils.fancy_getopt

Wrapper around the standard getopt module that provides the following
additional features:
  * short na long options are tied together
  * options have help strings, so fancy_getopt could potentially
    create a complete usage summary
  * options set attributes of a pitaed-in object
"""

agiza sys, string, re
agiza getopt
kutoka distutils.errors agiza *

# Much like command_re kwenye distutils.core, this ni close to but sio quite
# the same kama a Python NAME -- except, kwenye the spirit of most GNU
# utilities, we use '-' kwenye place of '_'.  (The spirit of LISP lives on!)
# The similarities to NAME are again sio a coincidence...
longopt_pat = r'[a-zA-Z](?:[a-zA-Z0-9-]*)'
longopt_re = re.compile(r'^%s$' % longopt_pat)

# For recognizing "negative alias" options, eg. "quiet=!verbose"
neg_alias_re = re.compile("^(%s)=!(%s)$" % (longopt_pat, longopt_pat))

# This ni used to translate long options to legitimate Python identifiers
# (kila use kama attributes of some object).
longopt_xlate = str.maketrans('-', '_')

kundi FancyGetopt:
    """Wrapper around the standard 'getopt()' module that provides some
    handy extra functionality:
      * short na long options are tied together
      * options have help strings, na help text can be assembled
        kutoka them
      * options set attributes of a pitaed-in object
      * boolean options can have "negative aliases" -- eg. if
        --quiet ni the "negative alias" of --verbose, then "--quiet"
        on the command line sets 'verbose' to false
    """

    eleza __init__(self, option_table=Tupu):
        # The option table ni (currently) a list of tuples.  The
        # tuples may have 3 ama four values:
        #   (long_option, short_option, help_string [, repeatable])
        # ikiwa an option takes an argument, its long_option should have '='
        # appended; short_option should just be a single character, no ':'
        # kwenye any case.  If a long_option doesn't have a corresponding
        # short_option, short_option should be Tupu.  All option tuples
        # must have long options.
        self.option_table = option_table

        # 'option_index' maps long option names to entries kwenye the option
        # table (ie. those 3-tuples).
        self.option_index = {}
        ikiwa self.option_table:
            self._build_index()

        # 'alias' records (duh) alias options; {'foo': 'bar'} means
        # --foo ni an alias kila --bar
        self.alias = {}

        # 'negative_alias' keeps track of options that are the boolean
        # opposite of some other option
        self.negative_alias = {}

        # These keep track of the information kwenye the option table.  We
        # don't actually populate these structures until we're ready to
        # parse the command-line, since the 'option_table' pitaed kwenye here
        # isn't necessarily the final word.
        self.short_opts = []
        self.long_opts = []
        self.short2long = {}
        self.attr_name = {}
        self.takes_arg = {}

        # And 'option_order' ni filled up kwenye 'getopt()'; it records the
        # original order of options (and their values) on the command-line,
        # but expands short options, converts aliases, etc.
        self.option_order = []

    eleza _build_index(self):
        self.option_index.clear()
        kila option kwenye self.option_table:
            self.option_index[option[0]] = option

    eleza set_option_table(self, option_table):
        self.option_table = option_table
        self._build_index()

    eleza add_option(self, long_option, short_option=Tupu, help_string=Tupu):
        ikiwa long_option kwenye self.option_index:
            ashiria DistutilsGetoptError(
                  "option conflict: already an option '%s'" % long_option)
        isipokua:
            option = (long_option, short_option, help_string)
            self.option_table.append(option)
            self.option_index[long_option] = option

    eleza has_option(self, long_option):
        """Return true ikiwa the option table kila this parser has an
        option ukijumuisha long name 'long_option'."""
        rudisha long_option kwenye self.option_index

    eleza get_attr_name(self, long_option):
        """Translate long option name 'long_option' to the form it
        has kama an attribute of some object: ie., translate hyphens
        to underscores."""
        rudisha long_option.translate(longopt_xlate)

    eleza _check_alias_dict(self, aliases, what):
        assert isinstance(aliases, dict)
        kila (alias, opt) kwenye aliases.items():
            ikiwa alias haiko kwenye self.option_index:
                ashiria DistutilsGetoptError(("invalid %s '%s': "
                       "option '%s' sio defined") % (what, alias, alias))
            ikiwa opt haiko kwenye self.option_index:
                ashiria DistutilsGetoptError(("invalid %s '%s': "
                       "aliased option '%s' sio defined") % (what, alias, opt))

    eleza set_aliases(self, alias):
        """Set the aliases kila this option parser."""
        self._check_alias_dict(alias, "alias")
        self.alias = alias

    eleza set_negative_aliases(self, negative_alias):
        """Set the negative aliases kila this option parser.
        'negative_alias' should be a dictionary mapping option names to
        option names, both the key na value must already be defined
        kwenye the option table."""
        self._check_alias_dict(negative_alias, "negative alias")
        self.negative_alias = negative_alias

    eleza _grok_option_table(self):
        """Populate the various data structures that keep tabs on the
        option table.  Called by 'getopt()' before it can do anything
        worthwhile.
        """
        self.long_opts = []
        self.short_opts = []
        self.short2long.clear()
        self.repeat = {}

        kila option kwenye self.option_table:
            ikiwa len(option) == 3:
                long, short, help = option
                repeat = 0
            lasivyo len(option) == 4:
                long, short, help, repeat = option
            isipokua:
                # the option table ni part of the code, so simply
                # assert that it ni correct
                ashiria ValueError("invalid option tuple: %r" % (option,))

            # Type- na value-check the option names
            ikiwa sio isinstance(long, str) ama len(long) < 2:
                ashiria DistutilsGetoptError(("invalid long option '%s': "
                       "must be a string of length >= 2") % long)

            ikiwa (sio ((short ni Tupu) ama
                     (isinstance(short, str) na len(short) == 1))):
                ashiria DistutilsGetoptError("invalid short option '%s': "
                       "must a single character ama Tupu" % short)

            self.repeat[long] = repeat
            self.long_opts.append(long)

            ikiwa long[-1] == '=':             # option takes an argument?
                ikiwa short: short = short + ':'
                long = long[0:-1]
                self.takes_arg[long] = 1
            isipokua:
                # Is option ni a "negative alias" kila some other option (eg.
                # "quiet" == "!verbose")?
                alias_to = self.negative_alias.get(long)
                ikiwa alias_to ni sio Tupu:
                    ikiwa self.takes_arg[alias_to]:
                        ashiria DistutilsGetoptError(
                              "invalid negative alias '%s': "
                              "aliased option '%s' takes a value"
                              % (long, alias_to))

                    self.long_opts[-1] = long # XXX redundant?!
                self.takes_arg[long] = 0

            # If this ni an alias option, make sure its "takes arg" flag is
            # the same kama the option it's aliased to.
            alias_to = self.alias.get(long)
            ikiwa alias_to ni sio Tupu:
                ikiwa self.takes_arg[long] != self.takes_arg[alias_to]:
                    ashiria DistutilsGetoptError(
                          "invalid alias '%s': inconsistent ukijumuisha "
                          "aliased option '%s' (one of them takes a value, "
                          "the other doesn't"
                          % (long, alias_to))

            # Now enforce some bondage on the long option name, so we can
            # later translate it to an attribute name on some object.  Have
            # to do this a bit late to make sure we've removed any trailing
            # '='.
            ikiwa sio longopt_re.match(long):
                ashiria DistutilsGetoptError(
                       "invalid long option name '%s' "
                       "(must be letters, numbers, hyphens only" % long)

            self.attr_name[long] = self.get_attr_name(long)
            ikiwa short:
                self.short_opts.append(short)
                self.short2long[short[0]] = long

    eleza getopt(self, args=Tupu, object=Tupu):
        """Parse command-line options kwenye args. Store kama attributes on object.

        If 'args' ni Tupu ama sio supplied, uses 'sys.argv[1:]'.  If
        'object' ni Tupu ama sio supplied, creates a new OptionDummy
        object, stores option values there, na returns a tuple (args,
        object).  If 'object' ni supplied, it ni modified kwenye place na
        'getopt()' just returns 'args'; kwenye both cases, the returned
        'args' ni a modified copy of the pitaed-in 'args' list, which
        ni left untouched.
        """
        ikiwa args ni Tupu:
            args = sys.argv[1:]
        ikiwa object ni Tupu:
            object = OptionDummy()
            created_object = Kweli
        isipokua:
            created_object = Uongo

        self._grok_option_table()

        short_opts = ' '.join(self.short_opts)
        jaribu:
            opts, args = getopt.getopt(args, short_opts, self.long_opts)
        tatizo getopt.error kama msg:
            ashiria DistutilsArgError(msg)

        kila opt, val kwenye opts:
            ikiwa len(opt) == 2 na opt[0] == '-': # it's a short option
                opt = self.short2long[opt[1]]
            isipokua:
                assert len(opt) > 2 na opt[:2] == '--'
                opt = opt[2:]

            alias = self.alias.get(opt)
            ikiwa alias:
                opt = alias

            ikiwa sio self.takes_arg[opt]:     # boolean option?
                assert val == '', "boolean option can't have value"
                alias = self.negative_alias.get(opt)
                ikiwa alias:
                    opt = alias
                    val = 0
                isipokua:
                    val = 1

            attr = self.attr_name[opt]
            # The only repeating option at the moment ni 'verbose'.
            # It has a negative option -q quiet, which should set verbose = 0.
            ikiwa val na self.repeat.get(attr) ni sio Tupu:
                val = getattr(object, attr, 0) + 1
            setattr(object, attr, val)
            self.option_order.append((opt, val))

        # kila opts
        ikiwa created_object:
            rudisha args, object
        isipokua:
            rudisha args

    eleza get_option_order(self):
        """Returns the list of (option, value) tuples processed by the
        previous run of 'getopt()'.  Raises RuntimeError if
        'getopt()' hasn't been called yet.
        """
        ikiwa self.option_order ni Tupu:
            ashiria RuntimeError("'getopt()' hasn't been called yet")
        isipokua:
            rudisha self.option_order

    eleza generate_help(self, header=Tupu):
        """Generate help text (a list of strings, one per suggested line of
        output) kutoka the option table kila this FancyGetopt object.
        """
        # Blithely assume the option table ni good: probably wouldn't call
        # 'generate_help()' unless you've already called 'getopt()'.

        # First pita: determine maximum length of long option names
        max_opt = 0
        kila option kwenye self.option_table:
            long = option[0]
            short = option[1]
            l = len(long)
            ikiwa long[-1] == '=':
                l = l - 1
            ikiwa short ni sio Tupu:
                l = l + 5                   # " (-x)" where short == 'x'
            ikiwa l > max_opt:
                max_opt = l

        opt_width = max_opt + 2 + 2 + 2     # room kila indent + dashes + gutter

        # Typical help block looks like this:
        #   --foo       controls foonabulation
        # Help block kila longest option looks like this:
        #   --flimflam  set the flim-flam level
        # na ukijumuisha wrapped text:
        #   --flimflam  set the flim-flam level (must be between
        #               0 na 100, tatizo on Tuesdays)
        # Options ukijumuisha short names will have the short name shown (but
        # it doesn't contribute to max_opt):
        #   --foo (-f)  controls foonabulation
        # If adding the short option would make the left column too wide,
        # we push the explanation off to the next line
        #   --flimflam (-l)
        #               set the flim-flam level
        # Important parameters:
        #   - 2 spaces before option block start lines
        #   - 2 dashes kila each long option name
        #   - min. 2 spaces between option na explanation (gutter)
        #   - 5 characters (incl. space) kila short option name

        # Now generate lines of help text.  (If 80 columns were good enough
        # kila Jesus, then 78 columns are good enough kila me!)
        line_width = 78
        text_width = line_width - opt_width
        big_indent = ' ' * opt_width
        ikiwa header:
            lines = [header]
        isipokua:
            lines = ['Option summary:']

        kila option kwenye self.option_table:
            long, short, help = option[:3]
            text = wrap_text(help, text_width)
            ikiwa long[-1] == '=':
                long = long[0:-1]

            # Case 1: no short option at all (makes life easy)
            ikiwa short ni Tupu:
                ikiwa text:
                    lines.append("  --%-*s  %s" % (max_opt, long, text[0]))
                isipokua:
                    lines.append("  --%-*s  " % (max_opt, long))

            # Case 2: we have a short option, so we have to include it
            # just after the long option
            isipokua:
                opt_names = "%s (-%s)" % (long, short)
                ikiwa text:
                    lines.append("  --%-*s  %s" %
                                 (max_opt, opt_names, text[0]))
                isipokua:
                    lines.append("  --%-*s" % opt_names)

            kila l kwenye text[1:]:
                lines.append(big_indent + l)
        rudisha lines

    eleza print_help(self, header=Tupu, file=Tupu):
        ikiwa file ni Tupu:
            file = sys.stdout
        kila line kwenye self.generate_help(header):
            file.write(line + "\n")


eleza fancy_getopt(options, negative_opt, object, args):
    parser = FancyGetopt(options)
    parser.set_negative_aliases(negative_opt)
    rudisha parser.getopt(args, object)


WS_TRANS = {ord(_wschar) : ' ' kila _wschar kwenye string.whitespace}

eleza wrap_text(text, width):
    """wrap_text(text : string, width : int) -> [string]

    Split 'text' into multiple lines of no more than 'width' characters
    each, na rudisha the list of strings that results.
    """
    ikiwa text ni Tupu:
        rudisha []
    ikiwa len(text) <= width:
        rudisha [text]

    text = text.expandtabs()
    text = text.translate(WS_TRANS)
    chunks = re.split(r'( +|-+)', text)
    chunks = [ch kila ch kwenye chunks ikiwa ch] # ' - ' results kwenye empty strings
    lines = []

    wakati chunks:
        cur_line = []                   # list of chunks (to-be-joined)
        cur_len = 0                     # length of current line

        wakati chunks:
            l = len(chunks[0])
            ikiwa cur_len + l <= width:    # can squeeze (at least) this chunk kwenye
                cur_line.append(chunks[0])
                toa chunks[0]
                cur_len = cur_len + l
            isipokua:                       # this line ni full
                # drop last chunk ikiwa all space
                ikiwa cur_line na cur_line[-1][0] == ' ':
                    toa cur_line[-1]
                koma

        ikiwa chunks:                      # any chunks left to process?
            # ikiwa the current line ni still empty, then we had a single
            # chunk that's too big too fit on a line -- so we koma
            # down na koma it up at the line width
            ikiwa cur_len == 0:
                cur_line.append(chunks[0][0:width])
                chunks[0] = chunks[0][width:]

            # all-whitespace chunks at the end of a line can be discarded
            # (and we know kutoka the re.split above that ikiwa a chunk has
            # *any* whitespace, it ni *all* whitespace)
            ikiwa chunks[0][0] == ' ':
                toa chunks[0]

        # na store this line kwenye the list-of-all-lines -- kama a single
        # string, of course!
        lines.append(''.join(cur_line))

    rudisha lines


eleza translate_longopt(opt):
    """Convert a long option name to a valid Python identifier by
    changing "-" to "_".
    """
    rudisha opt.translate(longopt_xlate)


kundi OptionDummy:
    """Dummy kundi just used kama a place to hold command-line option
    values kama instance attributes."""

    eleza __init__(self, options=[]):
        """Create a new OptionDummy instance.  The attributes listed kwenye
        'options' will be initialized to Tupu."""
        kila opt kwenye options:
            setattr(self, opt, Tupu)


ikiwa __name__ == "__main__":
    text = """\
Tra-la-la, supercalifragilisticexpialidocious.
How *do* you spell that odd word, anyways?
(Someone ask Mary -- she'll know [or she'll
say, "How should I know?"].)"""

    kila w kwenye (10, 20, 30, 40):
        andika("width: %d" % w)
        andika("\n".join(wrap_text(text, w)))
        andika()
