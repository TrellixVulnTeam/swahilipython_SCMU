"""A powerful, extensible, and easy-to-use option parser.

By Greg Ward <gward@python.net>

Originally distributed as Optik.

For support, use the optik-users@lists.sourceforge.net mailing list
(http://lists.sourceforge.net/lists/listinfo/optik-users).

Simple usage example:

   kutoka optparse agiza OptionParser

   parser = OptionParser()
   parser.add_option("-f", "--file", dest="filename",
                     help="write report to FILE", metavar="FILE")
   parser.add_option("-q", "--quiet",
                     action="store_false", dest="verbose", default=True,
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

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

  * Neither the name of the author nor the names of its
    contributors may be used to endorse or promote products derived kutoka
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

try:
    kutoka gettext agiza gettext, ngettext
except ImportError:
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
    Raised ikiwa an Option instance is created with invalid or
    inconsistent arguments.
    """

    eleza __init__(self, msg, option):
        self.msg = msg
        self.option_id = str(option)

    eleza __str__(self):
        ikiwa self.option_id:
            rudisha "option %s: %s" % (self.option_id, self.msg)
        else:
            rudisha self.msg

kundi OptionConflictError (OptionError):
    """
    Raised ikiwa conflicting options are added to an OptionParser.
    """

kundi OptionValueError (OptParseError):
    """
    Raised ikiwa an invalid option value is encountered on the command
    line.
    """

kundi BadOptionError (OptParseError):
    """
    Raised ikiwa an invalid option is seen on the command line.
    """
    eleza __init__(self, opt_str):
        self.opt_str = opt_str

    eleza __str__(self):
        rudisha _("no such option: %s") % self.opt_str

kundi AmbiguousOptionError (BadOptionError):
    """
    Raised ikiwa an ambiguous option is seen on the command line.
    """
    eleza __init__(self, opt_str, possibilities):
        BadOptionError.__init__(self, opt_str)
        self.possibilities = possibilities

    eleza __str__(self):
        rudisha (_("ambiguous option: %s (%s?)")
                % (self.opt_str, ", ".join(self.possibilities)))


kundi HelpFormatter:

    """
    Abstract base kundi for formatting option help.  OptionParser
    instances should use one of the HelpFormatter subclasses for
    formatting help; by default IndentedHelpFormatter is used.

    Instance attributes:
      parser : OptionParser
        the controlling OptionParser instance
      indent_increment : int
        the number of columns to indent per nesting level
      max_help_position : int
        the maximum starting column for option help text
      help_position : int
        the calculated starting column for option help text;
        initially the same as the maximum
      width : int
        total number of columns for output (pass None to constructor for
        this value to be taken kutoka the $COLUMNS environment variable)
      level : int
        current indentation level
      current_indent : int
        current indentation level (in columns)
      help_width : int
        number of columns available for option help text (calculated)
      default_tag : str
        text to replace with each option's default value, "%default"
        by default.  Set to false value to disable default value expansion.
      option_strings : { Option : str }
        maps Option instances to the snippet of help text explaining
        the syntax of that option, e.g. "-h, --help" or
        "-fFILE, --file=FILE"
      _short_opt_fmt : str
        format string controlling how short options with values are
        printed in help text.  Must be either "%s%s" ("-fFILE") or
        "%s %s" ("-f FILE"), because those are the two syntaxes that
        Optik supports.
      _long_opt_fmt : str
        similar but for long options; must be either "%s %s" ("--file FILE")
        or "%s=%s" ("--file=FILE").
    """

    NO_DEFAULT_VALUE = "none"

    eleza __init__(self,
                 indent_increment,
                 max_help_position,
                 width,
                 short_first):
        self.parser = None
        self.indent_increment = indent_increment
        ikiwa width is None:
            try:
                width = int(os.environ['COLUMNS'])
            except (KeyError, ValueError):
                width = 80
            width -= 2
        self.width = width
        self.help_position = self.max_help_position = \
                min(max_help_position, max(width - 20, indent_increment * 2))
        self.current_indent = 0
        self.level = 0
        self.help_width = None          # computed later
        self.short_first = short_first
        self.default_tag = "%default"
        self.option_strings = {}
        self._short_opt_fmt = "%s %s"
        self._long_opt_fmt = "%s=%s"

    eleza set_parser(self, parser):
        self.parser = parser

    eleza set_short_opt_delimiter(self, delim):
        ikiwa delim not in ("", " "):
            raise ValueError(
                "invalid metavar delimiter for short options: %r" % delim)
        self._short_opt_fmt = "%s" + delim + "%s"

    eleza set_long_opt_delimiter(self, delim):
        ikiwa delim not in ("=", " "):
            raise ValueError(
                "invalid metavar delimiter for long options: %r" % delim)
        self._long_opt_fmt = "%s" + delim + "%s"

    eleza indent(self):
        self.current_indent += self.indent_increment
        self.level += 1

    eleza dedent(self):
        self.current_indent -= self.indent_increment
        assert self.current_indent >= 0, "Indent decreased below 0."
        self.level -= 1

    eleza format_usage(self, usage):
        raise NotImplementedError("subclasses must implement")

    eleza format_heading(self, heading):
        raise NotImplementedError("subclasses must implement")

    eleza _format_text(self, text):
        """
        Format a paragraph of free-form text for inclusion in the
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
        else:
            rudisha ""

    eleza format_epilog(self, epilog):
        ikiwa epilog:
            rudisha "\n" + self._format_text(epilog) + "\n"
        else:
            rudisha ""


    eleza expand_default(self, option):
        ikiwa self.parser is None or not self.default_tag:
            rudisha option.help

        default_value = self.parser.defaults.get(option.dest)
        ikiwa default_value is NO_DEFAULT or default_value is None:
            default_value = self.NO_DEFAULT_VALUE

        rudisha option.help.replace(self.default_tag, str(default_value))

    eleza format_option(self, option):
        # The help for each option consists of two parts:
        #   * the opt strings and metavars
        #     eg. ("-x", or "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #     eg. ("turn on expert mode", "read data kutoka FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x      turn on expert mode
        #
        # But ikiwa the opt string list is too long, we put the help
        # string on a second line, indented to the same column it would
        # start in ikiwa it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #           read data kutoka FILENAME
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        ikiwa len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:                       # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        ikiwa option.help:
            help_text = self.expand_default(option)
            help_lines = textwrap.wrap(help_text, self.help_width)
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           for line in help_lines[1:]])
        elikiwa opts[-1] != "\n":
            result.append("\n")
        rudisha "".join(result)

    eleza store_option_strings(self, parser):
        self.indent()
        max_len = 0
        for opt in parser.option_list:
            strings = self.format_option_strings(opt)
            self.option_strings[opt] = strings
            max_len = max(max_len, len(strings) + self.current_indent)
        self.indent()
        for group in parser.option_groups:
            for opt in group.option_list:
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
            metavar = option.metavar or option.dest.upper()
            short_opts = [self._short_opt_fmt % (sopt, metavar)
                          for sopt in option._short_opts]
            long_opts = [self._long_opt_fmt % (lopt, metavar)
                         for lopt in option._long_opts]
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts

        ikiwa self.short_first:
            opts = short_opts + long_opts
        else:
            opts = long_opts + short_opts

        rudisha ", ".join(opts)

kundi IndentedHelpFormatter (HelpFormatter):
    """Format help with indented section bodies.
    """

    eleza __init__(self,
                 indent_increment=2,
                 max_help_position=24,
                 width=None,
                 short_first=1):
        HelpFormatter.__init__(
            self, indent_increment, max_help_position, width, short_first)

    eleza format_usage(self, usage):
        rudisha _("Usage: %s\n") % usage

    eleza format_heading(self, heading):
        rudisha "%*s%s:\n" % (self.current_indent, "", heading)


kundi TitledHelpFormatter (HelpFormatter):
    """Format help with underlined section headers.
    """

    eleza __init__(self,
                 indent_increment=0,
                 max_help_position=24,
                 width=None,
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
    elikiwa val[:2].lower() == "0b":       # binary
        radix = 2
        val = val[2:] or "0"            # have to remove "0b" prefix
    elikiwa val[:1] == "0":                # octal
        radix = 8
    else:                               # decimal
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
    try:
        rudisha cvt(value)
    except ValueError:
        raise OptionValueError(
            _("option %s: invalid %s value: %r") % (opt, what, value))

eleza check_choice(option, opt, value):
    ikiwa value in option.choices:
        rudisha value
    else:
        choices = ", ".join(map(repr, option.choices))
        raise OptionValueError(
            _("option %s: invalid choice: %r (choose kutoka %s)")
            % (opt, value, choices))

# Not supplying a default is different kutoka a default of None,
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
    # also listed just for constructor argument validation.  (If
    # the action is one of these, there must be a destination.)
    STORE_ACTIONS = ("store",
                     "store_const",
                     "store_true",
                     "store_false",
                     "append",
                     "append_const",
                     "count")

    # The set of actions for which it makes sense to supply a value
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

    # The set of known types for option parsers.  Again, listed here for
    # constructor argument validation.
    TYPES = ("string", "int", "long", "float", "complex", "choice")

    # Dictionary of argument checking functions, which convert and
    # validate option arguments according to the option type.
    #
    # Signature of checking functions is:
    #   check(option : Option, opt : string, value : string) -> any
    # where
    #   option is the Option instance calling the checker
    #   opt is the actual option seen on the command-line
    #     (eg. "-a", "--file")
    #   value is the option argument seen on the command-line
    #
    # The rudisha value should be in the appropriate Python type
    # for option.type -- eg. an integer ikiwa option.type == "int".
    #
    # If no checker is defined for a type, arguments will be
    # unchecked and remain strings.
    TYPE_CHECKER = { "int"    : check_builtin,
                     "long"   : check_builtin,
                     "float"  : check_builtin,
                     "complex": check_builtin,
                     "choice" : check_choice,
                   }


    # CHECK_METHODS is a list of unbound method objects; they are called
    # by the constructor, in order, after all attributes are
    # initialized.  The list is created and filled in later, after all
    # the methods are actually defined.  (I just put it here because I
    # like to define and document all kundi attributes in the same
    # place.)  Subclasses that add another _check_*() method should
    # define their own CHECK_METHODS list that adds their check method
    # to those kutoka this class.
    CHECK_METHODS = None


    # -- Constructor/initialization methods ----------------------------

    eleza __init__(self, *opts, **attrs):
        # Set _short_opts, _long_opts attrs kutoka 'opts' tuple.
        # Have to be set now, in case no option strings are supplied.
        self._short_opts = []
        self._long_opts = []
        opts = self._check_opt_strings(opts)
        self._set_opt_strings(opts)

        # Set all other attrs (action, type, etc.) kutoka 'attrs' dict
        self._set_attrs(attrs)

        # Check all the attributes we just set.  There are lots of
        # complicated interdependencies, but luckily they can be farmed
        # out to the _check_*() methods listed in CHECK_METHODS -- which
        # could be handy for subclasses!  The one thing these all share
        # is that they raise OptionError ikiwa they discover a problem.
        for checker in self.CHECK_METHODS:
            checker(self)

    eleza _check_opt_strings(self, opts):
        # Filter out None because early versions of Optik had exactly
        # one short option and one long option, either of which
        # could be None.
        opts = [opt for opt in opts ikiwa opt]
        ikiwa not opts:
            raise TypeError("at least one option string must be supplied")
        rudisha opts

    eleza _set_opt_strings(self, opts):
        for opt in opts:
            ikiwa len(opt) < 2:
                raise OptionError(
                    "invalid option string %r: "
                    "must be at least two characters long" % opt, self)
            elikiwa len(opt) == 2:
                ikiwa not (opt[0] == "-" and opt[1] != "-"):
                    raise OptionError(
                        "invalid short option string %r: "
                        "must be of the form -x, (x any non-dash char)" % opt,
                        self)
                self._short_opts.append(opt)
            else:
                ikiwa not (opt[0:2] == "--" and opt[2] != "-"):
                    raise OptionError(
                        "invalid long option string %r: "
                        "must start with --, followed by non-dash" % opt,
                        self)
                self._long_opts.append(opt)

    eleza _set_attrs(self, attrs):
        for attr in self.ATTRS:
            ikiwa attr in attrs:
                setattr(self, attr, attrs[attr])
                del attrs[attr]
            else:
                ikiwa attr == 'default':
                    setattr(self, attr, NO_DEFAULT)
                else:
                    setattr(self, attr, None)
        ikiwa attrs:
            attrs = sorted(attrs.keys())
            raise OptionError(
                "invalid keyword arguments: %s" % ", ".join(attrs),
                self)


    # -- Constructor validation methods --------------------------------

    eleza _check_action(self):
        ikiwa self.action is None:
            self.action = "store"
        elikiwa self.action not in self.ACTIONS:
            raise OptionError("invalid action: %r" % self.action, self)

    eleza _check_type(self):
        ikiwa self.type is None:
            ikiwa self.action in self.ALWAYS_TYPED_ACTIONS:
                ikiwa self.choices is not None:
                    # The "choices" attribute implies "choice" type.
                    self.type = "choice"
                else:
                    # No type given?  "string" is the most sensible default.
                    self.type = "string"
        else:
            # Allow type objects or builtin type conversion functions
            # (int, str, etc.) as an alternative to their names.
            ikiwa isinstance(self.type, type):
                self.type = self.type.__name__

            ikiwa self.type == "str":
                self.type = "string"

            ikiwa self.type not in self.TYPES:
                raise OptionError("invalid option type: %r" % self.type, self)
            ikiwa self.action not in self.TYPED_ACTIONS:
                raise OptionError(
                    "must not supply a type for action %r" % self.action, self)

    eleza _check_choice(self):
        ikiwa self.type == "choice":
            ikiwa self.choices is None:
                raise OptionError(
                    "must supply a list of choices for type 'choice'", self)
            elikiwa not isinstance(self.choices, (tuple, list)):
                raise OptionError(
                    "choices must be a list of strings ('%s' supplied)"
                    % str(type(self.choices)).split("'")[1], self)
        elikiwa self.choices is not None:
            raise OptionError(
                "must not supply choices for type %r" % self.type, self)

    eleza _check_dest(self):
        # No destination given, and we need one for this action.  The
        # self.type check is for callbacks that take a value.
        takes_value = (self.action in self.STORE_ACTIONS or
                       self.type is not None)
        ikiwa self.dest is None and takes_value:

            # Glean a destination kutoka the first long option string,
            # or kutoka the first short option string ikiwa no long options.
            ikiwa self._long_opts:
                # eg. "--foo-bar" -> "foo_bar"
                self.dest = self._long_opts[0][2:].replace('-', '_')
            else:
                self.dest = self._short_opts[0][1]

    eleza _check_const(self):
        ikiwa self.action not in self.CONST_ACTIONS and self.const is not None:
            raise OptionError(
                "'const' must not be supplied for action %r" % self.action,
                self)

    eleza _check_nargs(self):
        ikiwa self.action in self.TYPED_ACTIONS:
            ikiwa self.nargs is None:
                self.nargs = 1
        elikiwa self.nargs is not None:
            raise OptionError(
                "'nargs' must not be supplied for action %r" % self.action,
                self)

    eleza _check_callback(self):
        ikiwa self.action == "callback":
            ikiwa not callable(self.callback):
                raise OptionError(
                    "callback not callable: %r" % self.callback, self)
            ikiwa (self.callback_args is not None and
                not isinstance(self.callback_args, tuple)):
                raise OptionError(
                    "callback_args, ikiwa supplied, must be a tuple: not %r"
                    % self.callback_args, self)
            ikiwa (self.callback_kwargs is not None and
                not isinstance(self.callback_kwargs, dict)):
                raise OptionError(
                    "callback_kwargs, ikiwa supplied, must be a dict: not %r"
                    % self.callback_kwargs, self)
        else:
            ikiwa self.callback is not None:
                raise OptionError(
                    "callback supplied (%r) for non-callback option"
                    % self.callback, self)
            ikiwa self.callback_args is not None:
                raise OptionError(
                    "callback_args supplied for non-callback option", self)
            ikiwa self.callback_kwargs is not None:
                raise OptionError(
                    "callback_kwargs supplied for non-callback option", self)


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
        rudisha self.type is not None

    eleza get_opt_string(self):
        ikiwa self._long_opts:
            rudisha self._long_opts[0]
        else:
            rudisha self._short_opts[0]


    # -- Processing methods --------------------------------------------

    eleza check_value(self, opt, value):
        checker = self.TYPE_CHECKER.get(self.type)
        ikiwa checker is None:
            rudisha value
        else:
            rudisha checker(self, opt, value)

    eleza convert_value(self, opt, value):
        ikiwa value is not None:
            ikiwa self.nargs == 1:
                rudisha self.check_value(opt, value)
            else:
                rudisha tuple([self.check_value(opt, v) for v in value])

    eleza process(self, opt, value, values, parser):

        # First, convert the value(s) to the right type.  Howl ikiwa any
        # value(s) are bogus.
        value = self.convert_value(opt, value)

        # And then take whatever action is expected of us.
        # This is a separate method to make life easier for
        # subclasses to add new actions.
        rudisha self.take_action(
            self.action, self.dest, opt, value, values, parser)

    eleza take_action(self, action, dest, opt, value, values, parser):
        ikiwa action == "store":
            setattr(values, dest, value)
        elikiwa action == "store_const":
            setattr(values, dest, self.const)
        elikiwa action == "store_true":
            setattr(values, dest, True)
        elikiwa action == "store_false":
            setattr(values, dest, False)
        elikiwa action == "append":
            values.ensure_value(dest, []).append(value)
        elikiwa action == "append_const":
            values.ensure_value(dest, []).append(self.const)
        elikiwa action == "count":
            setattr(values, dest, values.ensure_value(dest, 0) + 1)
        elikiwa action == "callback":
            args = self.callback_args or ()
            kwargs = self.callback_kwargs or {}
            self.callback(self, opt, value, parser, *args, **kwargs)
        elikiwa action == "help":
            parser.print_help()
            parser.exit()
        elikiwa action == "version":
            parser.print_version()
            parser.exit()
        else:
            raise ValueError("unknown action %r" % self.action)

        rudisha 1

# kundi Option


SUPPRESS_HELP = "SUPPRESS"+"HELP"
SUPPRESS_USAGE = "SUPPRESS"+"USAGE"

kundi Values:

    eleza __init__(self, defaults=None):
        ikiwa defaults:
            for (attr, val) in defaults.items():
                setattr(self, attr, val)

    eleza __str__(self):
        rudisha str(self.__dict__)

    __repr__ = _repr

    eleza __eq__(self, other):
        ikiwa isinstance(other, Values):
            rudisha self.__dict__ == other.__dict__
        elikiwa isinstance(other, dict):
            rudisha self.__dict__ == other
        else:
            rudisha NotImplemented

    eleza _update_careful(self, dict):
        """
        Update the option values kutoka an arbitrary dictionary, but only
        use keys kutoka dict that already have a corresponding attribute
        in self.  Any keys in dict without a corresponding attribute
        are silently ignored.
        """
        for attr in dir(self):
            ikiwa attr in dict:
                dval = dict[attr]
                ikiwa dval is not None:
                    setattr(self, attr, dval)

    eleza _update_loose(self, dict):
        """
        Update the option values kutoka an arbitrary dictionary,
        using all keys kutoka the dictionary regardless of whether
        they have a corresponding attribute in self or not.
        """
        self.__dict__.update(dict)

    eleza _update(self, dict, mode):
        ikiwa mode == "careful":
            self._update_careful(dict)
        elikiwa mode == "loose":
            self._update_loose(dict)
        else:
            raise ValueError("invalid update mode: %r" % mode)

    eleza read_module(self, modname, mode="careful"):
        __import__(modname)
        mod = sys.modules[modname]
        self._update(vars(mod), mode)

    eleza read_file(self, filename, mode="careful"):
        vars = {}
        exec(open(filename).read(), vars)
        self._update(vars, mode)

    eleza ensure_value(self, attr, value):
        ikiwa not hasattr(self, attr) or getattr(self, attr) is None:
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
        dictionary mapping short option strings, eg. "-f" or "-X",
        to the Option instances that implement them.  If an Option
        has multiple short option strings, it will appear in this
        dictionary multiple times. [1]
      _long_opt : { string : Option }
        dictionary mapping long option strings, eg. "--file" or
        "--exclude", to the Option instances that implement them.
        Again, a given Option can occur multiple times in this
        dictionary. [1]
      defaults : { string : any }
        dictionary mapping option destination names to default
        values for each destination [1]

    [1] These mappings are common to (shared by) all components of the
        controlling OptionParser, where they are initially created.

    """

    eleza __init__(self, option_class, conflict_handler, description):
        # Initialize the option list and related data structures.
        # This method must be provided by subclasses, and it must
        # initialize at least the following instance attributes:
        # option_list, _short_opt, _long_opt, defaults.
        self._create_option_list()

        self.option_kundi = option_class
        self.set_conflict_handler(conflict_handler)
        self.set_description(description)

    eleza _create_option_mappings(self):
        # For use by OptionParser constructor -- create the main
        # option mappings used by this OptionParser and all
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
        ikiwa handler not in ("error", "resolve"):
            raise ValueError("invalid conflict_resolution value %r" % handler)
        self.conflict_handler = handler

    eleza set_description(self, description):
        self.description = description

    eleza get_description(self):
        rudisha self.description


    eleza destroy(self):
        """see OptionParser.destroy()."""
        del self._short_opt
        del self._long_opt
        del self.defaults


    # -- Option-adding methods -----------------------------------------

    eleza _check_conflict(self, option):
        conflict_opts = []
        for opt in option._short_opts:
            ikiwa opt in self._short_opt:
                conflict_opts.append((opt, self._short_opt[opt]))
        for opt in option._long_opts:
            ikiwa opt in self._long_opt:
                conflict_opts.append((opt, self._long_opt[opt]))

        ikiwa conflict_opts:
            handler = self.conflict_handler
            ikiwa handler == "error":
                raise OptionConflictError(
                    "conflicting option string(s): %s"
                    % ", ".join([co[0] for co in conflict_opts]),
                    option)
            elikiwa handler == "resolve":
                for (opt, c_option) in conflict_opts:
                    ikiwa opt.startswith("--"):
                        c_option._long_opts.remove(opt)
                        del self._long_opt[opt]
                    else:
                        c_option._short_opts.remove(opt)
                        del self._short_opt[opt]
                    ikiwa not (c_option._short_opts or c_option._long_opts):
                        c_option.container.option_list.remove(c_option)

    eleza add_option(self, *args, **kwargs):
        """add_option(Option)
           add_option(opt_str, ..., kwarg=val, ...)
        """
        ikiwa isinstance(args[0], str):
            option = self.option_class(*args, **kwargs)
        elikiwa len(args) == 1 and not kwargs:
            option = args[0]
            ikiwa not isinstance(option, Option):
                raise TypeError("not an Option instance: %r" % option)
        else:
            raise TypeError("invalid arguments")

        self._check_conflict(option)

        self.option_list.append(option)
        option.container = self
        for opt in option._short_opts:
            self._short_opt[opt] = option
        for opt in option._long_opts:
            self._long_opt[opt] = option

        ikiwa option.dest is not None:     # option has a dest, we need a default
            ikiwa option.default is not NO_DEFAULT:
                self.defaults[option.dest] = option.default
            elikiwa option.dest not in self.defaults:
                self.defaults[option.dest] = None

        rudisha option

    eleza add_options(self, option_list):
        for option in option_list:
            self.add_option(option)

    # -- Option query/removal methods ----------------------------------

    eleza get_option(self, opt_str):
        rudisha (self._short_opt.get(opt_str) or
                self._long_opt.get(opt_str))

    eleza has_option(self, opt_str):
        rudisha (opt_str in self._short_opt or
                opt_str in self._long_opt)

    eleza remove_option(self, opt_str):
        option = self._short_opt.get(opt_str)
        ikiwa option is None:
            option = self._long_opt.get(opt_str)
        ikiwa option is None:
            raise ValueError("no such option %r" % opt_str)

        for opt in option._short_opts:
            del self._short_opt[opt]
        for opt in option._long_opts:
            del self._long_opt[opt]
        option.container.option_list.remove(option)


    # -- Help-formatting methods ---------------------------------------

    eleza format_option_help(self, formatter):
        ikiwa not self.option_list:
            rudisha ""
        result = []
        for option in self.option_list:
            ikiwa not option.help is SUPPRESS_HELP:
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

    eleza __init__(self, parser, title, description=None):
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
        del self.option_list

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
        a usage string for your program.  Before it is displayed
        to the user, "%prog" will be expanded to the name of
        your program (self.prog or os.path.basename(sys.argv[0])).
      prog : string
        the name of the current program (to override
        os.path.basename(sys.argv[0])).
      description : string
        A paragraph of text giving a brief overview of your program.
        optparse reformats this paragraph to fit the current terminal
        width and prints it when the user requests help (after usage,
        but before the list of options).
      epilog : string
        paragraph of help text to print after option help

      option_groups : [OptionGroup]
        list of option groups in this parser (option groups are
        irrelevant for parsing the command-line, but very useful
        for generating help)

      allow_interspersed_args : bool = true
        ikiwa true, positional arguments may be interspersed with options.
        Assuming -a and -b each take a single argument, the command-line
          -ablah foo bar -bboo baz
        will be interpreted the same as
          -ablah -bboo -- foo bar baz
        If this flag were false, that command line would be interpreted as
          -ablah -- foo bar -bboo baz
        -- ie. we stop processing options as soon as we see the first
        non-option argument.  (This is the tradition followed by
        Python's getopt module, Perl's Getopt::Std, and other argument-
        parsing libraries, but it is generally annoying to users.)

      process_default_values : bool = true
        ikiwa true, option default values are processed similarly to option
        values kutoka the command line: that is, they are passed to the
        type-checking function for the option's type (as long as the
        default value is a string).  (This really only matters ikiwa you
        have defined custom types; see SF bug #955889.)  Set it to false
        to restore the behaviour of Optik 1.4.1 and earlier.

      rargs : [string]
        the argument list currently being parsed.  Only set when
        parse_args() is active, and continually trimmed down as
        we consume arguments.  Mainly there for the benefit of
        callback options.
      largs : [string]
        the list of leftover arguments that we have skipped while
        parsing options.  If allow_interspersed_args is false, this
        list is always empty.
      values : Values
        the set of option values currently being accumulated.  Only
        set when parse_args() is active.  Also mainly for callbacks.

    Because of the 'rargs', 'largs', and 'values' attributes,
    OptionParser is not thread-safe.  If, for some perverse reason, you
    need to parse command-line arguments simultaneously in different
    threads, use different OptionParser instances.

    """

    standard_option_list = []

    eleza __init__(self,
                 usage=None,
                 option_list=None,
                 option_class=Option,
                 version=None,
                 conflict_handler="error",
                 description=None,
                 formatter=None,
                 add_help_option=True,
                 prog=None,
                 epilog=None):
        OptionContainer.__init__(
            self, option_class, conflict_handler, description)
        self.set_usage(usage)
        self.prog = prog
        self.version = version
        self.allow_interspersed_args = True
        self.process_default_values = True
        ikiwa formatter is None:
            formatter = IndentedHelpFormatter()
        self.formatter = formatter
        self.formatter.set_parser(self)
        self.epilog = epilog

        # Populate the option list; initial sources are the
        # standard_option_list kundi attribute, the 'option_list'
        # argument, and (ikiwa applicable) the _add_version_option() and
        # _add_help_option() methods.
        self._populate_option_list(option_list,
                                   add_help=add_help_option)

        self._init_parsing_state()


    eleza destroy(self):
        """
        Declare that you are done with this OptionParser.  This cleans up
        reference cycles so the OptionParser (and all objects referenced by
        it) can be garbage-collected promptly.  After calling destroy(), the
        OptionParser is unusable.
        """
        OptionContainer.destroy(self)
        for group in self.option_groups:
            group.destroy()
        del self.option_list
        del self.option_groups
        del self.formatter


    # -- Private methods -----------------------------------------------
    # (used by our or OptionContainer's constructor)

    eleza _create_option_list(self):
        self.option_list = []
        self.option_groups = []
        self._create_option_mappings()

    eleza _add_help_option(self):
        self.add_option("-h", "--help",
                        action="help",
                        help=_("show this help message and exit"))

    eleza _add_version_option(self):
        self.add_option("--version",
                        action="version",
                        help=_("show program's version number and exit"))

    eleza _populate_option_list(self, option_list, add_help=True):
        ikiwa self.standard_option_list:
            self.add_options(self.standard_option_list)
        ikiwa option_list:
            self.add_options(option_list)
        ikiwa self.version:
            self._add_version_option()
        ikiwa add_help:
            self._add_help_option()

    eleza _init_parsing_state(self):
        # These are set in parse_args() for the convenience of callbacks.
        self.rargs = None
        self.largs = None
        self.values = None


    # -- Simple modifier methods ---------------------------------------

    eleza set_usage(self, usage):
        ikiwa usage is None:
            self.usage = _("%prog [options]")
        elikiwa usage is SUPPRESS_USAGE:
            self.usage = None
        # For backwards compatibility with Optik 1.3 and earlier.
        elikiwa usage.lower().startswith("usage: "):
            self.usage = usage[7:]
        else:
            self.usage = usage

    eleza enable_interspersed_args(self):
        """Set parsing to not stop on the first non-option, allowing
        interspersing switches with command arguments. This is the
        default behavior. See also disable_interspersed_args() and the
        kundi documentation description of the attribute
        allow_interspersed_args."""
        self.allow_interspersed_args = True

    eleza disable_interspersed_args(self):
        """Set parsing to stop on the first non-option. Use this if
        you have a command processor which runs another command that
        has options of its own and you want to make sure these options
        don't get confused.
        """
        self.allow_interspersed_args = False

    eleza set_process_default_values(self, process):
        self.process_default_values = process

    eleza set_default(self, dest, value):
        self.defaults[dest] = value

    eleza set_defaults(self, **kwargs):
        self.defaults.update(kwargs)

    eleza _get_all_options(self):
        options = self.option_list[:]
        for group in self.option_groups:
            options.extend(group.option_list)
        rudisha options

    eleza get_default_values(self):
        ikiwa not self.process_default_values:
            # Old, pre-Optik 1.5 behaviour.
            rudisha Values(self.defaults)

        defaults = self.defaults.copy()
        for option in self._get_all_options():
            default = defaults.get(option.dest)
            ikiwa isinstance(default, str):
                opt_str = option.get_opt_string()
                defaults[option.dest] = option.check_value(opt_str, default)

        rudisha Values(defaults)


    # -- OptionGroup methods -------------------------------------------

    eleza add_option_group(self, *args, **kwargs):
        # XXX lots of overlap with OptionContainer.add_option()
        ikiwa isinstance(args[0], str):
            group = OptionGroup(self, *args, **kwargs)
        elikiwa len(args) == 1 and not kwargs:
            group = args[0]
            ikiwa not isinstance(group, OptionGroup):
                raise TypeError("not an OptionGroup instance: %r" % group)
            ikiwa group.parser is not self:
                raise ValueError("invalid OptionGroup (wrong parser)")
        else:
            raise TypeError("invalid arguments")

        self.option_groups.append(group)
        rudisha group

    eleza get_option_group(self, opt_str):
        option = (self._short_opt.get(opt_str) or
                  self._long_opt.get(opt_str))
        ikiwa option and option.container is not self:
            rudisha option.container
        rudisha None


    # -- Option-parsing methods ----------------------------------------

    eleza _get_args(self, args):
        ikiwa args is None:
            rudisha sys.argv[1:]
        else:
            rudisha args[:]              # don't modify caller's list

    eleza parse_args(self, args=None, values=None):
        """
        parse_args(args : [string] = sys.argv[1:],
                   values : Values = None)
        -> (values : Values, args : [string])

        Parse the command-line options found in 'args' (default:
        sys.argv[1:]).  Any errors result in a call to 'error()', which
        by default prints the usage message to stderr and calls
        sys.exit() with an error message.  On success returns a pair
        (values, args) where 'values' is a Values instance (with all
        your option values) and 'args' is the list of arguments left
        over after parsing options.
        """
        rargs = self._get_args(args)
        ikiwa values is None:
            values = self.get_default_values()

        # Store the halves of the argument list as attributes for the
        # convenience of callbacks:
        #   rargs
        #     the rest of the command-line (the "r" stands for
        #     "remaining" or "right-hand")
        #   largs
        #     the leftover arguments -- ie. what's left after removing
        #     options and their arguments (the "l" stands for "leftover"
        #     or "left-hand")
        self.rargs = rargs
        self.largs = largs = []
        self.values = values

        try:
            stop = self._process_args(largs, rargs, values)
        except (BadOptionError, OptionValueError) as err:
            self.error(str(err))

        args = largs + rargs
        rudisha self.check_values(values, args)

    eleza check_values(self, values, args):
        """
        check_values(values : Values, args : [string])
        -> (values : Values, args : [string])

        Check that the supplied option values and leftover arguments are
        valid.  Returns the option values and leftover arguments
        (possibly adjusted, possibly completely new -- whatever you
        like).  Default implementation just returns the passed-in
        values; subclasses may override as desired.
        """
        rudisha (values, args)

    eleza _process_args(self, largs, rargs, values):
        """_process_args(largs : [string],
                         rargs : [string],
                         values : Values)

        Process command-line arguments and populate 'values', consuming
        options and arguments kutoka 'rargs'.  If 'allow_interspersed_args' is
        false, stop at the first non-option argument.  If true, accumulate any
        interspersed non-option arguments in 'largs'.
        """
        while rargs:
            arg = rargs[0]
            # We handle bare "--" explicitly, and bare "-" is handled by the
            # standard arg handler since the short arg case ensures that the
            # len of the opt string is greater than 1.
            ikiwa arg == "--":
                del rargs[0]
                return
            elikiwa arg[0:2] == "--":
                # process a single long option (possibly with value(s))
                self._process_long_opt(rargs, values)
            elikiwa arg[:1] == "-" and len(arg) > 1:
                # process a cluster of short options (possibly with
                # value(s) for the last one only)
                self._process_short_opts(rargs, values)
            elikiwa self.allow_interspersed_args:
                largs.append(arg)
                del rargs[0]
            else:
                rudisha                  # stop now, leave this arg in rargs

        # Say this is the original argument list:
        # [arg0, arg1, ..., arg(i-1), arg(i), arg(i+1), ..., arg(N-1)]
        #                            ^
        # (we are about to process arg(i)).
        #
        # Then rargs is [arg(i), ..., arg(N-1)] and largs is a *subset* of
        # [arg0, ..., arg(i-1)] (any options and their arguments will have
        # been removed kutoka largs).
        #
        # The while loop will usually consume 1 or more arguments per pass.
        # If it consumes 1 (eg. arg is an option that takes no arguments),
        # then after _process_arg() is done the situation is:
        #
        #   largs = subset of [arg0, ..., arg(i)]
        #   rargs = [arg(i+1), ..., arg(N-1)]
        #
        # If allow_interspersed_args is false, largs will always be
        # *empty* -- still a subset of [arg0, ..., arg(i-1)], but
        # not a very interesting subset!

    eleza _match_long_opt(self, opt):
        """_match_long_opt(opt : string) -> string

        Determine which long option string 'opt' matches, ie. which one
        it is an unambiguous abbreviation for.  Raises BadOptionError if
        'opt' doesn't unambiguously match any long option string.
        """
        rudisha _match_abbrev(opt, self._long_opt)

    eleza _process_long_opt(self, rargs, values):
        arg = rargs.pop(0)

        # Value explicitly attached to arg?  Pretend it's the next
        # argument.
        ikiwa "=" in arg:
            (opt, next_arg) = arg.split("=", 1)
            rargs.insert(0, next_arg)
            had_explicit_value = True
        else:
            opt = arg
            had_explicit_value = False

        opt = self._match_long_opt(opt)
        option = self._long_opt[opt]
        ikiwa option.takes_value():
            nargs = option.nargs
            ikiwa len(rargs) < nargs:
                self.error(ngettext(
                    "%(option)s option requires %(number)d argument",
                    "%(option)s option requires %(number)d arguments",
                    nargs) % {"option": opt, "number": nargs})
            elikiwa nargs == 1:
                value = rargs.pop(0)
            else:
                value = tuple(rargs[0:nargs])
                del rargs[0:nargs]

        elikiwa had_explicit_value:
            self.error(_("%s option does not take a value") % opt)

        else:
            value = None

        option.process(opt, value, values, self)

    eleza _process_short_opts(self, rargs, values):
        arg = rargs.pop(0)
        stop = False
        i = 1
        for ch in arg[1:]:
            opt = "-" + ch
            option = self._short_opt.get(opt)
            i += 1                      # we have consumed a character

            ikiwa not option:
                raise BadOptionError(opt)
            ikiwa option.takes_value():
                # Any characters left in arg?  Pretend they're the
                # next arg, and stop consuming characters of arg.
                ikiwa i < len(arg):
                    rargs.insert(0, arg[i:])
                    stop = True

                nargs = option.nargs
                ikiwa len(rargs) < nargs:
                    self.error(ngettext(
                        "%(option)s option requires %(number)d argument",
                        "%(option)s option requires %(number)d arguments",
                        nargs) % {"option": opt, "number": nargs})
                elikiwa nargs == 1:
                    value = rargs.pop(0)
                else:
                    value = tuple(rargs[0:nargs])
                    del rargs[0:nargs]

            else:                       # option doesn't take a value
                value = None

            option.process(opt, value, values, self)

            ikiwa stop:
                break


    # -- Feedback methods ----------------------------------------------

    eleza get_prog_name(self):
        ikiwa self.prog is None:
            rudisha os.path.basename(sys.argv[0])
        else:
            rudisha self.prog

    eleza expand_prog_name(self, s):
        rudisha s.replace("%prog", self.get_prog_name())

    eleza get_description(self):
        rudisha self.expand_prog_name(self.description)

    eleza exit(self, status=0, msg=None):
        ikiwa msg:
            sys.stderr.write(msg)
        sys.exit(status)

    eleza error(self, msg):
        """error(msg : string)

        Print a usage message incorporating 'msg' to stderr and exit.
        If you override this in a subclass, it should not rudisha -- it
        should either exit or raise an exception.
        """
        self.print_usage(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.get_prog_name(), msg))

    eleza get_usage(self):
        ikiwa self.usage:
            rudisha self.formatter.format_usage(
                self.expand_prog_name(self.usage))
        else:
            rudisha ""

    eleza print_usage(self, file=None):
        """print_usage(file : file = stdout)

        Print the usage message for the current program (self.usage) to
        'file' (default stdout).  Any occurrence of the string "%prog" in
        self.usage is replaced with the name of the current program
        (basename of sys.argv[0]).  Does nothing ikiwa self.usage is empty
        or not defined.
        """
        ikiwa self.usage:
            andika(self.get_usage(), file=file)

    eleza get_version(self):
        ikiwa self.version:
            rudisha self.expand_prog_name(self.version)
        else:
            rudisha ""

    eleza print_version(self, file=None):
        """print_version(file : file = stdout)

        Print the version message for this program (self.version) to
        'file' (default stdout).  As with print_usage(), any occurrence
        of "%prog" in self.version is replaced by the current program's
        name.  Does nothing ikiwa self.version is empty or undefined.
        """
        ikiwa self.version:
            andika(self.get_version(), file=file)

    eleza format_option_help(self, formatter=None):
        ikiwa formatter is None:
            formatter = self.formatter
        formatter.store_option_strings(self)
        result = []
        result.append(formatter.format_heading(_("Options")))
        formatter.indent()
        ikiwa self.option_list:
            result.append(OptionContainer.format_option_help(self, formatter))
            result.append("\n")
        for group in self.option_groups:
            result.append(group.format_help(formatter))
            result.append("\n")
        formatter.dedent()
        # Drop the last "\n", or the header ikiwa no options or option groups:
        rudisha "".join(result[:-1])

    eleza format_epilog(self, formatter):
        rudisha formatter.format_epilog(self.epilog)

    eleza format_help(self, formatter=None):
        ikiwa formatter is None:
            formatter = self.formatter
        result = []
        ikiwa self.usage:
            result.append(self.get_usage() + "\n")
        ikiwa self.description:
            result.append(self.format_description(formatter) + "\n")
        result.append(self.format_option_help(formatter))
        result.append(self.format_epilog(formatter))
        rudisha "".join(result)

    eleza print_help(self, file=None):
        """print_help(file : file = stdout)

        Print an extended help message, listing all options and any
        help text provided with them, to 'file' (default stdout).
        """
        ikiwa file is None:
            file = sys.stdout
        file.write(self.format_help())

# kundi OptionParser


eleza _match_abbrev(s, wordmap):
    """_match_abbrev(s : string, wordmap : {string : Option}) -> string

    Return the string key in 'wordmap' for which 's' is an unambiguous
    abbreviation.  If 's' is found to be ambiguous or doesn't match any of
    'words', raise BadOptionError.
    """
    # Is there an exact match?
    ikiwa s in wordmap:
        rudisha s
    else:
        # Isolate all words with s as a prefix.
        possibilities = [word for word in wordmap.keys()
                         ikiwa word.startswith(s)]
        # No exact match, so there had better be just one possibility.
        ikiwa len(possibilities) == 1:
            rudisha possibilities[0]
        elikiwa not possibilities:
            raise BadOptionError(s)
        else:
            # More than one possible completion: ambiguous prefix.
            possibilities.sort()
            raise AmbiguousOptionError(s, possibilities)


# Some day, there might be many Option classes.  As of Optik 1.3, the
# preferred way to instantiate Options is indirectly, via make_option(),
# which will become a factory function when there are many Option
# classes.
make_option = Option
