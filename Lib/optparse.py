"""A powerful, extensible, na easy-to-use option parser.

By Greg Ward <gward@python.net>

Originally distributed kama Optik.

For support, use the optik-users@lists.sourceforge.net mailing list
(http://lists.sourceforge.net/lists/listinfo/optik-users).

Simple usage example:

   kutoka optparse agiza OptionParser

   parser = OptionParser()
   parser.add_option("-f", "--file", dest="filename",
                     help="write report to FILE", metavar="FILE")
   parser.add_option("-q", "--quiet",
                     action="store_false", dest="verbose", default=Kweli,
                     help="don't print status messages to stdout")

   (options, args) = parser.parse_args()
"""

__version__ = "1.5.3"

__all__ = ['Option',
           'make_option',
           'SUPPRESS_HELP',
           'SUPPRESS_USAGE',
           'Values',
           'OptionContainer',
           'OptionGroup',
           'OptionParser',
           'HelpFormatter',
           'IndentedHelpFormatter',
           'TitledHelpFormatter',
           'OptParseError',
           'OptionError',
           'OptionConflictError',
           'OptionValueError',
           'BadOptionError',
           'check_choice']

__copyright__ = """
Copyright (c) 2001-2006 Gregory P. Ward.  All rights reserved.
Copyright (c) 2002-2006 Python Software Foundation.  All rights reserved.

Redistribution na use kwenye source na binary forms, ukijumuisha ama without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions na the following disclaimer.

  * Redistributions kwenye binary form must reproduce the above copyright
    notice, this list of conditions na the following disclaimer kwenye the
    documentation and/or other materials provided ukijumuisha the distribution.

  * Neither the name of the author nor the names of its
    contributors may be used to endorse ama promote products derived kutoka
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

agiza sys, os
agiza textwrap

eleza _repr(self):
    rudisha "<%s at 0x%x: %s>" % (self.__class__.__name__, id(self), self)


# This file was generated kutoka:
#   Id: option_parser.py 527 2006-07-23 15:21:30Z greg
#   Id: option.py 522 2006-06-11 16:22:03Z gward
#   Id: help.py 527 2006-07-23 15:21:30Z greg
#   Id: errors.py 509 2006-04-20 00:58:24Z gward

jaribu:
    kutoka gettext agiza gettext, ngettext
tatizo ImportError:
    eleza gettext(message):
        rudisha message

    eleza ngettext(singular, plural, n):
        ikiwa n == 1:
            rudisha singular
        rudisha plural

_ = gettext


kundi OptParseError (Exception):
    eleza __init__(self, msg):
        self.msg = msg

    eleza __str__(self):
        rudisha self.msg


kundi OptionError (OptParseError):
    """
    Raised ikiwa an Option instance ni created ukijumuisha invalid or
    inconsistent arguments.
    """

    eleza __init__(self, msg, option):
        self.msg = msg
        self.option_id = str(option)

    eleza __str__(self):
        ikiwa self.option_id:
            rudisha "option %s: %s" % (self.option_id, self.msg)
        isipokua:
            rudisha self.msg

kundi OptionConflictError (OptionError):
    """
    Raised ikiwa conflicting options are added to an OptionParser.
    """

kundi OptionValueError (OptParseError):
    """
    Raised ikiwa an invalid option value ni encountered on the command
    line.
    """

kundi BadOptionError (OptParseError):
    """
    Raised ikiwa an invalid option ni seen on the command line.
    """
    eleza __init__(self, opt_str):
        self.opt_str = opt_str

    eleza __str__(self):
        rudisha _("no such option: %s") % self.opt_str

kundi AmbiguousOptionError (BadOptionError):
    """
    Raised ikiwa an ambiguous option ni seen on the command line.
    """
    eleza __init__(self, opt_str, possibilities):
        BadOptionError.__init__(self, opt_str)
        self.possibilities = possibilities

    eleza __str__(self):
        rudisha (_("ambiguous option: %s (%s?)")
                % (self.opt_str, ", ".join(self.possibilities)))


kundi HelpFormatter:

    """
    Abstract base kundi kila formatting option help.  OptionParser
    instances should use one of the HelpFormatter subclasses for
    formatting help; by default IndentedHelpFormatter ni used.

    Instance attributes:
      parser : OptionParser
        the controlling OptionParser instance
      indent_increment : int
        the number of columns to indent per nesting level
      max_help_position : int
        the maximum starting column kila option help text
      help_position : int
        the calculated starting column kila option help text;
        initially the same kama the maximum
      width : int
        total number of columns kila output (pita Tupu to constructor for
        this value to be taken kutoka the $COLUMNS environment variable)
      level : int
        current indentation level
      current_indent : int
        current indentation level (in columns)
      help_width : int
        number of columns available kila option help text (calculated)
      default_tag : str
        text to replace ukijumuisha each option's default value, "%default"
        by default.  Set to false value to disable default value expansion.
      option_strings : { Option : str }
        maps Option instances to the snippet of help text explaining
        the syntax of that option, e.g. "-h, --help" or
        "-fFILE, --file=FILE"
      _short_opt_fmt : str
        format string controlling how short options ukijumuisha values are
        printed kwenye help text.  Must be either "%s%s" ("-fFILE") or
        "%s %s" ("-f FILE"), because those are the two syntaxes that
        Optik supports.
      _long_opt_fmt : str
        similar but kila long options; must be either "%s %s" ("--file FILE")
        ama "%s=%s" ("--file=FILE").
    """

    NO_DEFAULT_VALUE = "none"

    eleza __init__(self,
                 indent_increment,
                 max_help_position,
                 width,
                 short_first):
        self.parser = Tupu
        self.indent_increment = indent_increment
        ikiwa width ni Tupu:
            jaribu:
                width = int(os.environ['COLUMNS'])
            tatizo (KeyError, ValueError):
                width = 80
            width -= 2
        self.width = width
        self.help_position = self.max_help_position = \
                min(max_help_position, max(width - 20, indent_increment * 2))
        self.current_indent = 0
        self.level = 0
        self.help_width = Tupu          # computed later
        self.short_first = short_first
        self.default_tag = "%default"
        self.option_strings = {}
        self._short_opt_fmt = "%s %s"
        self._long_opt_fmt = "%s=%s"

    eleza set_parser(self, parser):
        self.parser = parser

    eleza set_short_opt_delimiter(self, delim):
        ikiwa delim haiko kwenye ("", " "):
            ashiria ValueError(
                "invalid metavar delimiter kila short options: %r" % delim)
        self._short_opt_fmt = "%s" + delim + "%s"

    eleza set_long_opt_delimiter(self, delim):
        ikiwa delim haiko kwenye ("=", " "):
            ashiria ValueError(
                "invalid metavar delimiter kila long options: %r" % delim)
        self._long_opt_fmt = "%s" + delim + "%s"

    eleza indent(self):
        self.current_indent += self.indent_increment
        self.level += 1

    eleza dedent(self):
        self.current_indent -= self.indent_increment
        assert self.current_indent >= 0, "Indent decreased below 0."
        self.level -= 1

    eleza format_usage(self, usage):
        ashiria NotImplementedError("subclasses must implement")

    eleza format_heading(self, heading):
        ashiria NotImplementedError("subclasses must implement")

    eleza _format_text(self, text):
        """
        Format a paragraph of free-form text kila inclusion kwenye the
        help output at the current indentation level.
        """
        text_width = max(self.width - self.current_indent, 11)
        indent = " "*self.current_indent
        rudisha textwrap.fill(text,
                             text_width,
                             initial_indent=indent,
                             subsequent_indent=indent)

    eleza format_description(self, description):
        ikiwa description:
            rudisha self._format_text(description) + "\n"
        isipokua:
            rudisha ""

    eleza format_epilog(self, epilog):
        ikiwa epilog:
            rudisha "\n" + self._format_text(epilog) + "\n"
        isipokua:
            rudisha ""


    eleza expand_default(self, option):
        ikiwa self.parser ni Tupu ama sio self.default_tag:
            rudisha option.help

        default_value = self.parser.defaults.get(option.dest)
        ikiwa default_value ni NO_DEFAULT ama default_value ni Tupu:
            default_value = self.NO_DEFAULT_VALUE

        rudisha option.help.replace(self.default_tag, str(default_value))

    eleza format_option(self, option):
        # The help kila each option consists of two parts:
        #   * the opt strings na metavars
        #     eg. ("-x", ama "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #     eg. ("turn on expert mode", "read data kutoka FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x      turn on expert mode
        #
        # But ikiwa the opt string list ni too long, we put the help
        # string on a second line, indented to the same column it would
        # start kwenye ikiwa it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #           read data kutoka FILENAME
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        ikiwa len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        isipokua:                       # start help on same line kama opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        ikiwa option.help:
            help_text = self.expand_default(option)
            help_lines = textwrap.wrap(help_text, self.help_width)
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           kila line kwenye help_lines[1:]])
        lasivyo opts[-1] != "\n":
            result.append("\n")
        rudisha "".join(result)

    eleza store_option_strings(self, parser):
        self.indent()
        max_len = 0
        kila opt kwenye parser.option_list:
            strings = self.format_option_strings(opt)
            self.option_strings[opt] = strings
            max_len = max(max_len, len(strings) + self.current_indent)
        self.indent()
        kila group kwenye parser.option_groups:
            kila opt kwenye group.option_list:
                strings = self.format_option_strings(opt)
                self.option_strings[opt] = strings
                max_len = max(max_len, len(strings) + self.current_indent)
        self.dedent()
        self.dedent()
        self.help_position = min(max_len + 2, self.max_help_position)
        self.help_width = max(self.width - self.help_position, 11)

    eleza format_option_strings(self, option):
        """Return a comma-separated list of option strings & metavariables."""
        ikiwa option.takes_value():
            metavar = option.metavar ama option.dest.upper()
            short_opts = [self._short_opt_fmt % (sopt, metavar)
                          kila sopt kwenye option._short_opts]
            long_opts = [self._long_opt_fmt % (lopt, metavar)
                         kila lopt kwenye option._long_opts]
        isipokua:
            short_opts = option._short_opts
            long_opts = option._long_opts

        ikiwa self.short_first:
            opts = short_opts + long_opts
        isipokua:
            opts = long_opts + short_opts

        rudisha ", ".join(opts)

kundi IndentedHelpFormatter (HelpFormatter):
    """Format help ukijumuisha indented section bodies.
    """

    eleza __init__(self,
                 indent_increment=2,
                 max_help_position=24,
                 width=Tupu,
                 short_first=1):
        HelpFormatter.__init__(
            self, indent_increment, max_help_position, width, short_first)

    eleza format_usage(self, usage):
        rudisha _("Usage: %s\n") % usage

    eleza format_heading(self, heading):
        rudisha "%*s%s:\n" % (self.current_indent, "", heading)


kundi TitledHelpFormatter (HelpFormatter):
    """Format help ukijumuisha underlined section headers.
    """

    eleza __init__(self,
                 indent_increment=0,
                 max_help_position=24,
                 width=Tupu,
                 short_first=0):
        HelpFormatter.__init__ (
            self, indent_increment, max_help_position, width, short_first)

    eleza format_usage(self, usage):
        rudisha "%s  %s\n" % (self.format_heading(_("Usage")), usage)

    eleza format_heading(self, heading):
        rudisha "%s\n%s\n" % (heading, "=-"[self.level] * len(heading))


eleza _parse_num(val, type):
    ikiwa val[:2].lower() == "0x":         # hexadecimal
        radix = 16
    lasivyo val[:2].lower() == "0b":       # binary
        radix = 2
        val = val[2:] ama "0"            # have to remove "0b" prefix
    lasivyo val[:1] == "0":                # octal
        radix = 8
    isipokua:                               # decimal
        radix = 10

    rudisha type(val, radix)

eleza _parse_int(val):
    rudisha _parse_num(val, int)

_builtin_cvt = { "int" : (_parse_int, _("integer")),
                 "long" : (_parse_int, _("integer")),
                 "float" : (float, _("floating-point")),
                 "complex" : (complex, _("complex")) }

eleza check_builtin(option, opt, value):
    (cvt, what) = _builtin_cvt[option.type]
    jaribu:
        rudisha cvt(value)
    tatizo ValueError:
        ashiria OptionValueError(
            _("option %s: invalid %s value: %r") % (opt, what, value))

eleza check_choice(option, opt, value):
    ikiwa value kwenye option.choices:
        rudisha value
    isipokua:
        choices = ", ".join(map(repr, option.choices))
        ashiria OptionValueError(
            _("option %s: invalid choice: %r (choose kutoka %s)")
            % (opt, value, choices))

# Not supplying a default ni different kutoka a default of Tupu,
# so we need an explicit "not supplied" value.
NO_DEFAULT = ("NO", "DEFAULT")


kundi Option:
    """
    Instance attributes:
      _short_opts : [string]
      _long_opts : [string]

      action : string
      type : string
      dest : string
      default : any
      nargs : int
      const : any
      choices : [string]
      callback : function
      callback_args : (any*)
      callback_kwargs : { string : any }
      help : string
      metavar : string
    """

    # The list of instance attributes that may be set through
    # keyword args to the constructor.
    ATTRS = ['action',
             'type',
             'dest',
             'default',
             'nargs',
             'const',
             'choices',
             'callback',
             'callback_args',
             'callback_kwargs',
             'help',
             'metavar']

    # The set of actions allowed by option parsers.  Explicitly listed
    # here so the constructor can validate its arguments.
    ACTIONS = ("store",
               "store_const",
               "store_true",
               "store_false",
               "append",
               "append_const",
               "count",
               "callback",
               "help",
               "version")

    # The set of actions that involve storing a value somewhere;
    # also listed just kila constructor argument validation.  (If
    # the action ni one of these, there must be a destination.)
    STORE_ACTIONS = ("store",
                     "store_const",
                     "store_true",
                     "store_false",
                     "append",
                     "append_const",
                     "count")

    # The set of actions kila which it makes sense to supply a value
    # type, ie. which may consume an argument kutoka the command line.
    TYPED_ACTIONS = ("store",
                     "append",
                     "callback")

    # The set of actions which *require* a value type, ie. that
    # always consume an argument kutoka the command line.
    ALWAYS_TYPED_ACTIONS = ("store",
                            "append")

    # The set of actions which take a 'const' attribute.
    CONST_ACTIONS = ("store_const",
                     "append_const")

    # The set of known types kila option parsers.  Again, listed here for
    # constructor argument validation.
    TYPES = ("string", "int", "long", "float", "complex", "choice")

    # Dictionary of argument checking functions, which convert and
    # validate option arguments according to the option type.
    #
    # Signature of checking functions is:
    #   check(option : Option, opt : string, value : string) -> any
    # where
    #   option ni the Option instance calling the checker
    #   opt ni the actual option seen on the command-line
    #     (eg. "-a", "--file")
    #   value ni the option argument seen on the command-line
    #
    # The rudisha value should be kwenye the appropriate Python type
    # kila option.type -- eg. an integer ikiwa option.type == "int".
    #
    # If no checker ni defined kila a type, arguments will be
    # unchecked na remain strings.
    TYPE_CHECKER = { "int"    : check_builtin,
                     "long"   : check_builtin,
                     "float"  : check_builtin,
                     "complex": check_builtin,
                     "choice" : check_choice,
                   }


    # CHECK_METHODS ni a list of unbound method objects; they are called
    # by the constructor, kwenye order, after all attributes are
    # initialized.  The list ni created na filled kwenye later, after all
    # the methods are actually defined.  (I just put it here because I
    # like to define na document all kundi attributes kwenye the same
    # place.)  Subclasses that add another _check_*() method should
    # define their own CHECK_METHODS list that adds their check method
    # to those kutoka this class.
    CHECK_METHODS = Tupu


    # -- Constructor/initialization methods ----------------------------

    eleza __init__(self, *opts, **attrs):
        # Set _short_opts, _long_opts attrs kutoka 'opts' tuple.
        # Have to be set now, kwenye case no option strings are supplied.
        self._short_opts = []
        self._long_opts = []
        opts = self._check_opt_strings(opts)
        self._set_opt_strings(opts)

        # Set all other attrs (action, type, etc.) kutoka 'attrs' dict
        self._set_attrs(attrs)

        # Check all the attributes we just set.  There are lots of
        # complicated interdependencies, but luckily they can be farmed
        # out to the _check_*() methods listed kwenye CHECK_METHODS -- which
        # could be handy kila subclasses!  The one thing these all share
        # ni that they ashiria OptionError ikiwa they discover a problem.
        kila checker kwenye self.CHECK_METHODS:
            checker(self)

    eleza _check_opt_strings(self, opts):
        # Filter out Tupu because early versions of Optik had exactly
        # one short option na one long option, either of which
        # could be Tupu.
        opts = [opt kila opt kwenye opts ikiwa opt]
        ikiwa sio opts:
            ashiria TypeError("at least one option string must be supplied")
        rudisha opts

    eleza _set_opt_strings(self, opts):
        kila opt kwenye opts:
            ikiwa len(opt) < 2:
                ashiria OptionError(
                    "invalid option string %r: "
                    "must be at least two characters long" % opt, self)
            lasivyo len(opt) == 2:
                ikiwa sio (opt[0] == "-" na opt[1] != "-"):
                    ashiria OptionError(
                        "invalid short option string %r: "
                        "must be of the form -x, (x any non-dash char)" % opt,
                        self)
                self._short_opts.append(opt)
            isipokua:
                ikiwa sio (opt[0:2] == "--" na opt[2] != "-"):
                    ashiria OptionError(
                        "invalid long option string %r: "
                        "must start ukijumuisha --, followed by non-dash" % opt,
                        self)
                self._long_opts.append(opt)

    eleza _set_attrs(self, attrs):
        kila attr kwenye self.ATTRS:
            ikiwa attr kwenye attrs:
                setattr(self, attr, attrs[attr])
                toa attrs[attr]
            isipokua:
                ikiwa attr == 'default':
                    setattr(self, attr, NO_DEFAULT)
                isipokua:
                    setattr(self, attr, Tupu)
        ikiwa attrs:
            attrs = sorted(attrs.keys())
            ashiria OptionError(
                "invalid keyword arguments: %s" % ", ".join(attrs),
                self)


    # -- Constructor validation methods --------------------------------

    eleza _check_action(self):
        ikiwa self.action ni Tupu:
            self.action = "store"
        lasivyo self.action haiko kwenye self.ACTIONS:
            ashiria OptionError("invalid action: %r" % self.action, self)

    eleza _check_type(self):
        ikiwa self.type ni Tupu:
            ikiwa self.action kwenye self.ALWAYS_TYPED_ACTIONS:
                ikiwa self.choices ni sio Tupu:
                    # The "choices" attribute implies "choice" type.
                    self.type = "choice"
                isipokua:
                    # No type given?  "string" ni the most sensible default.
                    self.type = "string"
        isipokua:
            # Allow type objects ama builtin type conversion functions
            # (int, str, etc.) kama an alternative to their names.
            ikiwa isinstance(self.type, type):
                self.type = self.type.__name__

            ikiwa self.type == "str":
                self.type = "string"

            ikiwa self.type haiko kwenye self.TYPES:
                ashiria OptionError("invalid option type: %r" % self.type, self)
            ikiwa self.action haiko kwenye self.TYPED_ACTIONS:
                ashiria OptionError(
                    "must sio supply a type kila action %r" % self.action, self)

    eleza _check_choice(self):
        ikiwa self.type == "choice":
            ikiwa self.choices ni Tupu:
                ashiria OptionError(
                    "must supply a list of choices kila type 'choice'", self)
            lasivyo sio isinstance(self.choices, (tuple, list)):
                ashiria OptionError(
                    "choices must be a list of strings ('%s' supplied)"
                    % str(type(self.choices)).split("'")[1], self)
        lasivyo self.choices ni sio Tupu:
            ashiria OptionError(
                "must sio supply choices kila type %r" % self.type, self)

    eleza _check_dest(self):
        # No destination given, na we need one kila this action.  The
        # self.type check ni kila callbacks that take a value.
        takes_value = (self.action kwenye self.STORE_ACTIONS or
                       self.type ni sio Tupu)
        ikiwa self.dest ni Tupu na takes_value:

            # Glean a destination kutoka the first long option string,
            # ama kutoka the first short option string ikiwa no long options.
            ikiwa self._long_opts:
                # eg. "--foo-bar" -> "foo_bar"
                self.dest = self._long_opts[0][2:].replace('-', '_')
            isipokua:
                self.dest = self._short_opts[0][1]

    eleza _check_const(self):
        ikiwa self.action haiko kwenye self.CONST_ACTIONS na self.const ni sio Tupu:
            ashiria OptionError(
                "'const' must sio be supplied kila action %r" % self.action,
                self)

    eleza _check_nargs(self):
        ikiwa self.action kwenye self.TYPED_ACTIONS:
            ikiwa self.nargs ni Tupu:
                self.nargs = 1
        lasivyo self.nargs ni sio Tupu:
            ashiria OptionError(
                "'nargs' must sio be supplied kila action %r" % self.action,
                self)

    eleza _check_callback(self):
        ikiwa self.action == "callback":
            ikiwa sio callable(self.callback):
                ashiria OptionError(
                    "callback sio callable: %r" % self.callback, self)
            ikiwa (self.callback_args ni sio Tupu and
                sio isinstance(self.callback_args, tuple)):
                ashiria OptionError(
                    "callback_args, ikiwa supplied, must be a tuple: sio %r"
                    % self.callback_args, self)
            ikiwa (self.callback_kwargs ni sio Tupu and
                sio isinstance(self.callback_kwargs, dict)):
                ashiria OptionError(
                    "callback_kwargs, ikiwa supplied, must be a dict: sio %r"
                    % self.callback_kwargs, self)
        isipokua:
            ikiwa self.callback ni sio Tupu:
                ashiria OptionError(
                    "callback supplied (%r) kila non-callback option"
                    % self.callback, self)
            ikiwa self.callback_args ni sio Tupu:
                ashiria OptionError(
                    "callback_args supplied kila non-callback option", self)
            ikiwa self.callback_kwargs ni sio Tupu:
                ashiria OptionError(
                    "callback_kwargs supplied kila non-callback option", self)


    CHECK_METHODS = [_check_action,
                     _check_type,
                     _check_choice,
                     _check_dest,
                     _check_const,
                     _check_nargs,
                     _check_callback]


    # -- Miscellaneous methods -----------------------------------------

    eleza __str__(self):
        rudisha "/".join(self._short_opts + self._long_opts)

    __repr__ = _repr

    eleza takes_value(self):
        rudisha self.type ni sio Tupu

    eleza get_opt_string(self):
        ikiwa self._long_opts:
            rudisha self._long_opts[0]
        isipokua:
            rudisha self._short_opts[0]


    # -- Processing methods --------------------------------------------

    eleza check_value(self, opt, value):
        checker = self.TYPE_CHECKER.get(self.type)
        ikiwa checker ni Tupu:
            rudisha value
        isipokua:
            rudisha checker(self, opt, value)

    eleza convert_value(self, opt, value):
        ikiwa value ni sio Tupu:
            ikiwa self.nargs == 1:
                rudisha self.check_value(opt, value)
            isipokua:
                rudisha tuple([self.check_value(opt, v) kila v kwenye value])

    eleza process(self, opt, value, values, parser):

        # First, convert the value(s) to the right type.  Howl ikiwa any
        # value(s) are bogus.
        value = self.convert_value(opt, value)

        # And then take whatever action ni expected of us.
        # This ni a separate method to make life easier for
        # subclasses to add new actions.
        rudisha self.take_action(
            self.action, self.dest, opt, value, values, parser)

    eleza take_action(self, action, dest, opt, value, values, parser):
        ikiwa action == "store":
            setattr(values, dest, value)
        lasivyo action == "store_const":
            setattr(values, dest, self.const)
        lasivyo action == "store_true":
            setattr(values, dest, Kweli)
        lasivyo action == "store_false":
            setattr(values, dest, Uongo)
        lasivyo action == "append":
            values.ensure_value(dest, []).append(value)
        lasivyo action == "append_const":
            values.ensure_value(dest, []).append(self.const)
        lasivyo action == "count":
            setattr(values, dest, values.ensure_value(dest, 0) + 1)
        lasivyo action == "callback":
            args = self.callback_args ama ()
            kwargs = self.callback_kwargs ama {}
            self.callback(self, opt, value, parser, *args, **kwargs)
        lasivyo action == "help":
            parser.print_help()
            parser.exit()
        lasivyo action == "version":
            parser.print_version()
            parser.exit()
        isipokua:
            ashiria ValueError("unknown action %r" % self.action)

        rudisha 1

# kundi Option


SUPPRESS_HELP = "SUPPRESS"+"HELP"
SUPPRESS_USAGE = "SUPPRESS"+"USAGE"

kundi Values:

    eleza __init__(self, defaults=Tupu):
        ikiwa defaults:
            kila (attr, val) kwenye defaults.items():
                setattr(self, attr, val)

    eleza __str__(self):
        rudisha str(self.__dict__)

    __repr__ = _repr

    eleza __eq__(self, other):
        ikiwa isinstance(other, Values):
            rudisha self.__dict__ == other.__dict__
        lasivyo isinstance(other, dict):
            rudisha self.__dict__ == other
        isipokua:
            rudisha NotImplemented

    eleza _update_careful(self, dict):
        """
        Update the option values kutoka an arbitrary dictionary, but only
        use keys kutoka dict that already have a corresponding attribute
        kwenye self.  Any keys kwenye dict without a corresponding attribute
        are silently ignored.
        """
        kila attr kwenye dir(self):
            ikiwa attr kwenye dict:
                dval = dict[attr]
                ikiwa dval ni sio Tupu:
                    setattr(self, attr, dval)

    eleza _update_loose(self, dict):
        """
        Update the option values kutoka an arbitrary dictionary,
        using all keys kutoka the dictionary regardless of whether
        they have a corresponding attribute kwenye self ama not.
        """
        self.__dict__.update(dict)

    eleza _update(self, dict, mode):
        ikiwa mode == "careful":
            self._update_careful(dict)
        lasivyo mode == "loose":
            self._update_loose(dict)
        isipokua:
            ashiria ValueError("invalid update mode: %r" % mode)

    eleza read_module(self, modname, mode="careful"):
        __import__(modname)
        mod = sys.modules[modname]
        self._update(vars(mod), mode)

    eleza read_file(self, filename, mode="careful"):
        vars = {}
        exec(open(filename).read(), vars)
        self._update(vars, mode)

    eleza ensure_value(self, attr, value):
        ikiwa sio hasattr(self, attr) ama getattr(self, attr) ni Tupu:
            setattr(self, attr, value)
        rudisha getattr(self, attr)


kundi OptionContainer:

    """
    Abstract base class.

    Class attributes:
      standard_option_list : [Option]
        list of standard options that will be accepted by all instances
        of this parser kundi (intended to be overridden by subclasses).

    Instance attributes:
      option_list : [Option]
        the list of Option objects contained by this OptionContainer
      _short_opt : { string : Option }
        dictionary mapping short option strings, eg. "-f" ama "-X",
        to the Option instances that implement them.  If an Option
        has multiple short option strings, it will appear kwenye this
        dictionary multiple times. [1]
      _long_opt : { string : Option }
        dictionary mapping long option strings, eg. "--file" or
        "--exclude", to the Option instances that implement them.
        Again, a given Option can occur multiple times kwenye this
        dictionary. [1]
      defaults : { string : any }
        dictionary mapping option destination names to default
        values kila each destination [1]

    [1] These mappings are common to (shared by) all components of the
        controlling OptionParser, where they are initially created.

    """

    eleza __init__(self, option_class, conflict_handler, description):
        # Initialize the option list na related data structures.
        # This method must be provided by subclasses, na it must
        # initialize at least the following instance attributes:
        # option_list, _short_opt, _long_opt, defaults.
        self._create_option_list()

        self.option_kundi = option_class
        self.set_conflict_handler(conflict_handler)
        self.set_description(description)

    eleza _create_option_mappings(self):
        # For use by OptionParser constructor -- create the main
        # option mappings used by this OptionParser na all
        # OptionGroups that it owns.
        self._short_opt = {}            # single letter -> Option instance
        self._long_opt = {}             # long option -> Option instance
        self.defaults = {}              # maps option dest -> default value


    eleza _share_option_mappings(self, parser):
        # For use by OptionGroup constructor -- use shared option
        # mappings kutoka the OptionParser that owns this OptionGroup.
        self._short_opt = parser._short_opt
        self._long_opt = parser._long_opt
        self.defaults = parser.defaults

    eleza set_conflict_handler(self, handler):
        ikiwa handler haiko kwenye ("error", "resolve"):
            ashiria ValueError("invalid conflict_resolution value %r" % handler)
        self.conflict_handler = handler

    eleza set_description(self, description):
        self.description = description

    eleza get_description(self):
        rudisha self.description


    eleza destroy(self):
        """see OptionParser.destroy()."""
        toa self._short_opt
        toa self._long_opt
        toa self.defaults


    # -- Option-adding methods -----------------------------------------

    eleza _check_conflict(self, option):
        conflict_opts = []
        kila opt kwenye option._short_opts:
            ikiwa opt kwenye self._short_opt:
                conflict_opts.append((opt, self._short_opt[opt]))
        kila opt kwenye option._long_opts:
            ikiwa opt kwenye self._long_opt:
                conflict_opts.append((opt, self._long_opt[opt]))

        ikiwa conflict_opts:
            handler = self.conflict_handler
            ikiwa handler == "error":
                ashiria OptionConflictError(
                    "conflicting option string(s): %s"
                    % ", ".join([co[0] kila co kwenye conflict_opts]),
                    option)
            lasivyo handler == "resolve":
                kila (opt, c_option) kwenye conflict_opts:
                    ikiwa opt.startswith("--"):
                        c_option._long_opts.remove(opt)
                        toa self._long_opt[opt]
                    isipokua:
                        c_option._short_opts.remove(opt)
                        toa self._short_opt[opt]
                    ikiwa sio (c_option._short_opts ama c_option._long_opts):
                        c_option.container.option_list.remove(c_option)

    eleza add_option(self, *args, **kwargs):
        """add_option(Option)
           add_option(opt_str, ..., kwarg=val, ...)
        """
        ikiwa isinstance(args[0], str):
            option = self.option_class(*args, **kwargs)
        lasivyo len(args) == 1 na sio kwargs:
            option = args[0]
            ikiwa sio isinstance(option, Option):
                ashiria TypeError("not an Option instance: %r" % option)
        isipokua:
            ashiria TypeError("invalid arguments")

        self._check_conflict(option)

        self.option_list.append(option)
        option.container = self
        kila opt kwenye option._short_opts:
            self._short_opt[opt] = option
        kila opt kwenye option._long_opts:
            self._long_opt[opt] = option

        ikiwa option.dest ni sio Tupu:     # option has a dest, we need a default
            ikiwa option.default ni sio NO_DEFAULT:
                self.defaults[option.dest] = option.default
            lasivyo option.dest haiko kwenye self.defaults:
                self.defaults[option.dest] = Tupu

        rudisha option

    eleza add_options(self, option_list):
        kila option kwenye option_list:
            self.add_option(option)

    # -- Option query/removal methods ----------------------------------

    eleza get_option(self, opt_str):
        rudisha (self._short_opt.get(opt_str) or
                self._long_opt.get(opt_str))

    eleza has_option(self, opt_str):
        rudisha (opt_str kwenye self._short_opt or
                opt_str kwenye self._long_opt)

    eleza remove_option(self, opt_str):
        option = self._short_opt.get(opt_str)
        ikiwa option ni Tupu:
            option = self._long_opt.get(opt_str)
        ikiwa option ni Tupu:
            ashiria ValueError("no such option %r" % opt_str)

        kila opt kwenye option._short_opts:
            toa self._short_opt[opt]
        kila opt kwenye option._long_opts:
            toa self._long_opt[opt]
        option.container.option_list.remove(option)


    # -- Help-formatting methods ---------------------------------------

    eleza format_option_help(self, formatter):
        ikiwa sio self.option_list:
            rudisha ""
        result = []
        kila option kwenye self.option_list:
            ikiwa sio option.help ni SUPPRESS_HELP:
                result.append(formatter.format_option(option))
        rudisha "".join(result)

    eleza format_description(self, formatter):
        rudisha formatter.format_description(self.get_description())

    eleza format_help(self, formatter):
        result = []
        ikiwa self.description:
            result.append(self.format_description(formatter))
        ikiwa self.option_list:
            result.append(self.format_option_help(formatter))
        rudisha "\n".join(result)


kundi OptionGroup (OptionContainer):

    eleza __init__(self, parser, title, description=Tupu):
        self.parser = parser
        OptionContainer.__init__(
            self, parser.option_class, parser.conflict_handler, description)
        self.title = title

    eleza _create_option_list(self):
        self.option_list = []
        self._share_option_mappings(self.parser)

    eleza set_title(self, title):
        self.title = title

    eleza destroy(self):
        """see OptionParser.destroy()."""
        OptionContainer.destroy(self)
        toa self.option_list

    # -- Help-formatting methods ---------------------------------------

    eleza format_help(self, formatter):
        result = formatter.format_heading(self.title)
        formatter.indent()
        result += OptionContainer.format_help(self, formatter)
        formatter.dedent()
        rudisha result


kundi OptionParser (OptionContainer):

    """
    Class attributes:
      standard_option_list : [Option]
        list of standard options that will be accepted by all instances
        of this parser kundi (intended to be overridden by subclasses).

    Instance attributes:
      usage : string
        a usage string kila your program.  Before it ni displayed
        to the user, "%prog" will be expanded to the name of
        your program (self.prog ama os.path.basename(sys.argv[0])).
      prog : string
        the name of the current program (to override
        os.path.basename(sys.argv[0])).
      description : string
        A paragraph of text giving a brief overview of your program.
        optparse reformats this paragraph to fit the current terminal
        width na prints it when the user requests help (after usage,
        but before the list of options).
      epilog : string
        paragraph of help text to print after option help

      option_groups : [OptionGroup]
        list of option groups kwenye this parser (option groups are
        irrelevant kila parsing the command-line, but very useful
        kila generating help)

      allow_interspersed_args : bool = true
        ikiwa true, positional arguments may be interspersed ukijumuisha options.
        Assuming -a na -b each take a single argument, the command-line
          -ablah foo bar -bboo baz
        will be interpreted the same as
          -ablah -bboo -- foo bar baz
        If this flag were false, that command line would be interpreted as
          -ablah -- foo bar -bboo baz
        -- ie. we stop processing options kama soon kama we see the first
        non-option argument.  (This ni the tradition followed by
        Python's getopt module, Perl's Getopt::Std, na other argument-
        parsing libraries, but it ni generally annoying to users.)

      process_default_values : bool = true
        ikiwa true, option default values are processed similarly to option
        values kutoka the command line: that is, they are pitaed to the
        type-checking function kila the option's type (as long kama the
        default value ni a string).  (This really only matters ikiwa you
        have defined custom types; see SF bug #955889.)  Set it to false
        to restore the behaviour of Optik 1.4.1 na earlier.

      rargs : [string]
        the argument list currently being parsed.  Only set when
        parse_args() ni active, na continually trimmed down as
        we consume arguments.  Mainly there kila the benefit of
        callback options.
      largs : [string]
        the list of leftover arguments that we have skipped while
        parsing options.  If allow_interspersed_args ni false, this
        list ni always empty.
      values : Values
        the set of option values currently being accumulated.  Only
        set when parse_args() ni active.  Also mainly kila callbacks.

    Because of the 'rargs', 'largs', na 'values' attributes,
    OptionParser ni sio thread-safe.  If, kila some perverse reason, you
    need to parse command-line arguments simultaneously kwenye different
    threads, use different OptionParser instances.

    """

    standard_option_list = []

    eleza __init__(self,
                 usage=Tupu,
                 option_list=Tupu,
                 option_class=Option,
                 version=Tupu,
                 conflict_handler="error",
                 description=Tupu,
                 formatter=Tupu,
                 add_help_option=Kweli,
                 prog=Tupu,
                 epilog=Tupu):
        OptionContainer.__init__(
            self, option_class, conflict_handler, description)
        self.set_usage(usage)
        self.prog = prog
        self.version = version
        self.allow_interspersed_args = Kweli
        self.process_default_values = Kweli
        ikiwa formatter ni Tupu:
            formatter = IndentedHelpFormatter()
        self.formatter = formatter
        self.formatter.set_parser(self)
        self.epilog = epilog

        # Populate the option list; initial sources are the
        # standard_option_list kundi attribute, the 'option_list'
        # argument, na (ikiwa applicable) the _add_version_option() and
        # _add_help_option() methods.
        self._populate_option_list(option_list,
                                   add_help=add_help_option)

        self._init_parsing_state()


    eleza destroy(self):
        """
        Declare that you are done ukijumuisha this OptionParser.  This cleans up
        reference cycles so the OptionParser (and all objects referenced by
        it) can be garbage-collected promptly.  After calling destroy(), the
        OptionParser ni unusable.
        """
        OptionContainer.destroy(self)
        kila group kwenye self.option_groups:
            group.destroy()
        toa self.option_list
        toa self.option_groups
        toa self.formatter


    # -- Private methods -----------------------------------------------
    # (used by our ama OptionContainer's constructor)

    eleza _create_option_list(self):
        self.option_list = []
        self.option_groups = []
        self._create_option_mappings()

    eleza _add_help_option(self):
        self.add_option("-h", "--help",
                        action="help",
                        help=_("show this help message na exit"))

    eleza _add_version_option(self):
        self.add_option("--version",
                        action="version",
                        help=_("show program's version number na exit"))

    eleza _populate_option_list(self, option_list, add_help=Kweli):
        ikiwa self.standard_option_list:
            self.add_options(self.standard_option_list)
        ikiwa option_list:
            self.add_options(option_list)
        ikiwa self.version:
            self._add_version_option()
        ikiwa add_help:
            self._add_help_option()

    eleza _init_parsing_state(self):
        # These are set kwenye parse_args() kila the convenience of callbacks.
        self.rargs = Tupu
        self.largs = Tupu
        self.values = Tupu


    # -- Simple modifier methods ---------------------------------------

    eleza set_usage(self, usage):
        ikiwa usage ni Tupu:
            self.usage = _("%prog [options]")
        lasivyo usage ni SUPPRESS_USAGE:
            self.usage = Tupu
        # For backwards compatibility ukijumuisha Optik 1.3 na earlier.
        lasivyo usage.lower().startswith("usage: "):
            self.usage = usage[7:]
        isipokua:
            self.usage = usage

    eleza enable_interspersed_args(self):
        """Set parsing to sio stop on the first non-option, allowing
        interspersing switches ukijumuisha command arguments. This ni the
        default behavior. See also disable_interspersed_args() na the
        kundi documentation description of the attribute
        allow_interspersed_args."""
        self.allow_interspersed_args = Kweli

    eleza disable_interspersed_args(self):
        """Set parsing to stop on the first non-option. Use this if
        you have a command processor which runs another command that
        has options of its own na you want to make sure these options
        don't get confused.
        """
        self.allow_interspersed_args = Uongo

    eleza set_process_default_values(self, process):
        self.process_default_values = process

    eleza set_default(self, dest, value):
        self.defaults[dest] = value

    eleza set_defaults(self, **kwargs):
        self.defaults.update(kwargs)

    eleza _get_all_options(self):
        options = self.option_list[:]
        kila group kwenye self.option_groups:
            options.extend(group.option_list)
        rudisha options

    eleza get_default_values(self):
        ikiwa sio self.process_default_values:
            # Old, pre-Optik 1.5 behaviour.
            rudisha Values(self.defaults)

        defaults = self.defaults.copy()
        kila option kwenye self._get_all_options():
            default = defaults.get(option.dest)
            ikiwa isinstance(default, str):
                opt_str = option.get_opt_string()
                defaults[option.dest] = option.check_value(opt_str, default)

        rudisha Values(defaults)


    # -- OptionGroup methods -------------------------------------------

    eleza add_option_group(self, *args, **kwargs):
        # XXX lots of overlap ukijumuisha OptionContainer.add_option()
        ikiwa isinstance(args[0], str):
            group = OptionGroup(self, *args, **kwargs)
        lasivyo len(args) == 1 na sio kwargs:
            group = args[0]
            ikiwa sio isinstance(group, OptionGroup):
                ashiria TypeError("not an OptionGroup instance: %r" % group)
            ikiwa group.parser ni sio self:
                ashiria ValueError("invalid OptionGroup (wrong parser)")
        isipokua:
            ashiria TypeError("invalid arguments")

        self.option_groups.append(group)
        rudisha group

    eleza get_option_group(self, opt_str):
        option = (self._short_opt.get(opt_str) or
                  self._long_opt.get(opt_str))
        ikiwa option na option.container ni sio self:
            rudisha option.container
        rudisha Tupu


    # -- Option-parsing methods ----------------------------------------

    eleza _get_args(self, args):
        ikiwa args ni Tupu:
            rudisha sys.argv[1:]
        isipokua:
            rudisha args[:]              # don't modify caller's list

    eleza parse_args(self, args=Tupu, values=Tupu):
        """
        parse_args(args : [string] = sys.argv[1:],
                   values : Values = Tupu)
        -> (values : Values, args : [string])

        Parse the command-line options found kwenye 'args' (default:
        sys.argv[1:]).  Any errors result kwenye a call to 'error()', which
        by default prints the usage message to stderr na calls
        sys.exit() ukijumuisha an error message.  On success rudishas a pair
        (values, args) where 'values' ni a Values instance (ukijumuisha all
        your option values) na 'args' ni the list of arguments left
        over after parsing options.
        """
        rargs = self._get_args(args)
        ikiwa values ni Tupu:
            values = self.get_default_values()

        # Store the halves of the argument list kama attributes kila the
        # convenience of callbacks:
        #   rargs
        #     the rest of the command-line (the "r" stands for
        #     "remaining" ama "right-hand")
        #   largs
        #     the leftover arguments -- ie. what's left after removing
        #     options na their arguments (the "l" stands kila "leftover"
        #     ama "left-hand")
        self.rargs = rargs
        self.largs = largs = []
        self.values = values

        jaribu:
            stop = self._process_args(largs, rargs, values)
        tatizo (BadOptionError, OptionValueError) kama err:
            self.error(str(err))

        args = largs + rargs
        rudisha self.check_values(values, args)

    eleza check_values(self, values, args):
        """
        check_values(values : Values, args : [string])
        -> (values : Values, args : [string])

        Check that the supplied option values na leftover arguments are
        valid.  Returns the option values na leftover arguments
        (possibly adjusted, possibly completely new -- whatever you
        like).  Default implementation just rudishas the pitaed-in
        values; subclasses may override kama desired.
        """
        rudisha (values, args)

    eleza _process_args(self, largs, rargs, values):
        """_process_args(largs : [string],
                         rargs : [string],
                         values : Values)

        Process command-line arguments na populate 'values', consuming
        options na arguments kutoka 'rargs'.  If 'allow_interspersed_args' is
        false, stop at the first non-option argument.  If true, accumulate any
        interspersed non-option arguments kwenye 'largs'.
        """
        wakati rargs:
            arg = rargs[0]
            # We handle bare "--" explicitly, na bare "-" ni handled by the
            # standard arg handler since the short arg case ensures that the
            # len of the opt string ni greater than 1.
            ikiwa arg == "--":
                toa rargs[0]
                rudisha
            lasivyo arg[0:2] == "--":
                # process a single long option (possibly ukijumuisha value(s))
                self._process_long_opt(rargs, values)
            lasivyo arg[:1] == "-" na len(arg) > 1:
                # process a cluster of short options (possibly with
                # value(s) kila the last one only)
                self._process_short_opts(rargs, values)
            lasivyo self.allow_interspersed_args:
                largs.append(arg)
                toa rargs[0]
            isipokua:
                rudisha                  # stop now, leave this arg kwenye rargs

        # Say this ni the original argument list:
        # [arg0, arg1, ..., arg(i-1), arg(i), arg(i+1), ..., arg(N-1)]
        #                            ^
        # (we are about to process arg(i)).
        #
        # Then rargs ni [arg(i), ..., arg(N-1)] na largs ni a *subset* of
        # [arg0, ..., arg(i-1)] (any options na their arguments will have
        # been removed kutoka largs).
        #
        # The wakati loop will usually consume 1 ama more arguments per pita.
        # If it consumes 1 (eg. arg ni an option that takes no arguments),
        # then after _process_arg() ni done the situation is:
        #
        #   largs = subset of [arg0, ..., arg(i)]
        #   rargs = [arg(i+1), ..., arg(N-1)]
        #
        # If allow_interspersed_args ni false, largs will always be
        # *empty* -- still a subset of [arg0, ..., arg(i-1)], but
        # sio a very interesting subset!

    eleza _match_long_opt(self, opt):
        """_match_long_opt(opt : string) -> string

        Determine which long option string 'opt' matches, ie. which one
        it ni an unambiguous abbreviation for.  Raises BadOptionError if
        'opt' doesn't unambiguously match any long option string.
        """
        rudisha _match_abbrev(opt, self._long_opt)

    eleza _process_long_opt(self, rargs, values):
        arg = rargs.pop(0)

        # Value explicitly attached to arg?  Pretend it's the next
        # argument.
        ikiwa "=" kwenye arg:
            (opt, next_arg) = arg.split("=", 1)
            rargs.insert(0, next_arg)
            had_explicit_value = Kweli
        isipokua:
            opt = arg
            had_explicit_value = Uongo

        opt = self._match_long_opt(opt)
        option = self._long_opt[opt]
        ikiwa option.takes_value():
            nargs = option.nargs
            ikiwa len(rargs) < nargs:
                self.error(ngettext(
                    "%(option)s option requires %(number)d argument",
                    "%(option)s option requires %(number)d arguments",
                    nargs) % {"option": opt, "number": nargs})
            lasivyo nargs == 1:
                value = rargs.pop(0)
            isipokua:
                value = tuple(rargs[0:nargs])
                toa rargs[0:nargs]

        lasivyo had_explicit_value:
            self.error(_("%s option does sio take a value") % opt)

        isipokua:
            value = Tupu

        option.process(opt, value, values, self)

    eleza _process_short_opts(self, rargs, values):
        arg = rargs.pop(0)
        stop = Uongo
        i = 1
        kila ch kwenye arg[1:]:
            opt = "-" + ch
            option = self._short_opt.get(opt)
            i += 1                      # we have consumed a character

            ikiwa sio option:
                ashiria BadOptionError(opt)
            ikiwa option.takes_value():
                # Any characters left kwenye arg?  Pretend they're the
                # next arg, na stop consuming characters of arg.
                ikiwa i < len(arg):
                    rargs.insert(0, arg[i:])
                    stop = Kweli

                nargs = option.nargs
                ikiwa len(rargs) < nargs:
                    self.error(ngettext(
                        "%(option)s option requires %(number)d argument",
                        "%(option)s option requires %(number)d arguments",
                        nargs) % {"option": opt, "number": nargs})
                lasivyo nargs == 1:
                    value = rargs.pop(0)
                isipokua:
                    value = tuple(rargs[0:nargs])
                    toa rargs[0:nargs]

            isipokua:                       # option doesn't take a value
                value = Tupu

            option.process(opt, value, values, self)

            ikiwa stop:
                koma


    # -- Feedback methods ----------------------------------------------

    eleza get_prog_name(self):
        ikiwa self.prog ni Tupu:
            rudisha os.path.basename(sys.argv[0])
        isipokua:
            rudisha self.prog

    eleza expand_prog_name(self, s):
        rudisha s.replace("%prog", self.get_prog_name())

    eleza get_description(self):
        rudisha self.expand_prog_name(self.description)

    eleza exit(self, status=0, msg=Tupu):
        ikiwa msg:
            sys.stderr.write(msg)
        sys.exit(status)

    eleza error(self, msg):
        """error(msg : string)

        Print a usage message incorporating 'msg' to stderr na exit.
        If you override this kwenye a subclass, it should sio rudisha -- it
        should either exit ama ashiria an exception.
        """
        self.print_usage(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.get_prog_name(), msg))

    eleza get_usage(self):
        ikiwa self.usage:
            rudisha self.formatter.format_usage(
                self.expand_prog_name(self.usage))
        isipokua:
            rudisha ""

    eleza print_usage(self, file=Tupu):
        """print_usage(file : file = stdout)

        Print the usage message kila the current program (self.usage) to
        'file' (default stdout).  Any occurrence of the string "%prog" in
        self.usage ni replaced ukijumuisha the name of the current program
        (basename of sys.argv[0]).  Does nothing ikiwa self.usage ni empty
        ama sio defined.
        """
        ikiwa self.usage:
            andika(self.get_usage(), file=file)

    eleza get_version(self):
        ikiwa self.version:
            rudisha self.expand_prog_name(self.version)
        isipokua:
            rudisha ""

    eleza print_version(self, file=Tupu):
        """print_version(file : file = stdout)

        Print the version message kila this program (self.version) to
        'file' (default stdout).  As ukijumuisha print_usage(), any occurrence
        of "%prog" kwenye self.version ni replaced by the current program's
        name.  Does nothing ikiwa self.version ni empty ama undefined.
        """
        ikiwa self.version:
            andika(self.get_version(), file=file)

    eleza format_option_help(self, formatter=Tupu):
        ikiwa formatter ni Tupu:
            formatter = self.formatter
        formatter.store_option_strings(self)
        result = []
        result.append(formatter.format_heading(_("Options")))
        formatter.indent()
        ikiwa self.option_list:
            result.append(OptionContainer.format_option_help(self, formatter))
            result.append("\n")
        kila group kwenye self.option_groups:
            result.append(group.format_help(formatter))
            result.append("\n")
        formatter.dedent()
        # Drop the last "\n", ama the header ikiwa no options ama option groups:
        rudisha "".join(result[:-1])

    eleza format_epilog(self, formatter):
        rudisha formatter.format_epilog(self.epilog)

    eleza format_help(self, formatter=Tupu):
        ikiwa formatter ni Tupu:
            formatter = self.formatter
        result = []
        ikiwa self.usage:
            result.append(self.get_usage() + "\n")
        ikiwa self.description:
            result.append(self.format_description(formatter) + "\n")
        result.append(self.format_option_help(formatter))
        result.append(self.format_epilog(formatter))
        rudisha "".join(result)

    eleza print_help(self, file=Tupu):
        """print_help(file : file = stdout)

        Print an extended help message, listing all options na any
        help text provided ukijumuisha them, to 'file' (default stdout).
        """
        ikiwa file ni Tupu:
            file = sys.stdout
        file.write(self.format_help())

# kundi OptionParser


eleza _match_abbrev(s, wordmap):
    """_match_abbrev(s : string, wordmap : {string : Option}) -> string

    Return the string key kwenye 'wordmap' kila which 's' ni an unambiguous
    abbreviation.  If 's' ni found to be ambiguous ama doesn't match any of
    'words', ashiria BadOptionError.
    """
    # Is there an exact match?
    ikiwa s kwenye wordmap:
        rudisha s
    isipokua:
        # Isolate all words ukijumuisha s kama a prefix.
        possibilities = [word kila word kwenye wordmap.keys()
                         ikiwa word.startswith(s)]
        # No exact match, so there had better be just one possibility.
        ikiwa len(possibilities) == 1:
            rudisha possibilities[0]
        lasivyo sio possibilities:
            ashiria BadOptionError(s)
        isipokua:
            # More than one possible completion: ambiguous prefix.
            possibilities.sort()
            ashiria AmbiguousOptionError(s, possibilities)


# Some day, there might be many Option classes.  As of Optik 1.3, the
# preferred way to instantiate Options ni indirectly, via make_option(),
# which will become a factory function when there are many Option
# classes.
make_option = Option
