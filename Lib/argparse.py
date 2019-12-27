# Author: Steven J. Bethard <steven.bethard@gmail.com>.
# New maintainer as of 29 August 2019:  Raymond Hettinger <raymond.hettinger@gmail.com>

"""Command-line parsing library

This module is an optparse-inspired command-line parsing library that:

    - handles both optional and positional arguments
    - produces highly informative usage messages
    - supports parsers that dispatch to sub-parsers

The following is a simple usage example that sums integers kutoka the
command-line and writes the result to a file::

    parser = argparse.ArgumentParser(
        description='sum the integers at the command line')
    parser.add_argument(
        'integers', metavar='int', nargs='+', type=int,
        help='an integer to be summed')
    parser.add_argument(
        '--log', default=sys.stdout, type=argparse.FileType('w'),
        help='the file where the sum should be written')
    args = parser.parse_args()
    args.log.write('%s' % sum(args.integers))
    args.log.close()

The module contains the following public classes:

    - ArgumentParser -- The main entry point for command-line parsing. As the
        example above shows, the add_argument() method is used to populate
        the parser with actions for optional and positional arguments. Then
        the parse_args() method is invoked to convert the args at the
        command-line into an object with attributes.

    - ArgumentError -- The exception raised by ArgumentParser objects when
        there are errors with the parser's actions. Errors raised while
        parsing the command-line are caught by ArgumentParser and emitted
        as command-line messages.

    - FileType -- A factory for defining types of files to be created. As the
        example above shows, instances of FileType are typically passed as
        the type= argument of add_argument() calls.

    - Action -- The base kundi for parser actions. Typically actions are
        selected by passing strings like 'store_true' or 'append_const' to
        the action= argument of add_argument(). However, for greater
        customization of ArgumentParser actions, subclasses of Action may
        be defined and passed as the action= argument.

    - HelpFormatter, RawDescriptionHelpFormatter, RawTextHelpFormatter,
        ArgumentDefaultsHelpFormatter -- Formatter classes which
        may be passed as the formatter_class= argument to the
        ArgumentParser constructor. HelpFormatter is the default,
        RawDescriptionHelpFormatter and RawTextHelpFormatter tell the parser
        not to change the formatting for help text, and
        ArgumentDefaultsHelpFormatter adds information about argument defaults
        to the help.

All other classes in this module are considered implementation details.
(Also note that HelpFormatter and RawDescriptionHelpFormatter are only
considered public as object names -- the API of the formatter objects is
still considered an implementation detail.)
"""

__version__ = '1.1'
__all__ = [
    'ArgumentParser',
    'ArgumentError',
    'ArgumentTypeError',
    'FileType',
    'HelpFormatter',
    'ArgumentDefaultsHelpFormatter',
    'RawDescriptionHelpFormatter',
    'RawTextHelpFormatter',
    'MetavarTypeHelpFormatter',
    'Namespace',
    'Action',
    'ONE_OR_MORE',
    'OPTIONAL',
    'PARSER',
    'REMAINDER',
    'SUPPRESS',
    'ZERO_OR_MORE',
]


agiza os as _os
agiza re as _re
agiza shutil as _shutil
agiza sys as _sys

kutoka gettext agiza gettext as _, ngettext

SUPPRESS = '==SUPPRESS=='

OPTIONAL = '?'
ZERO_OR_MORE = '*'
ONE_OR_MORE = '+'
PARSER = 'A...'
REMAINDER = '...'
_UNRECOGNIZED_ARGS_ATTR = '_unrecognized_args'

# =============================
# Utility functions and classes
# =============================

kundi _AttributeHolder(object):
    """Abstract base kundi that provides __repr__.

    The __repr__ method returns a string in the format::
        ClassName(attr=name, attr=name, ...)
    The attributes are determined either by a class-level attribute,
    '_kwarg_names', or by inspecting the instance __dict__.
    """

    eleza __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        star_args = {}
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            ikiwa name.isidentifier():
                arg_strings.append('%s=%r' % (name, value))
            else:
                star_args[name] = value
        ikiwa star_args:
            arg_strings.append('**%s' % repr(star_args))
        rudisha '%s(%s)' % (type_name, ', '.join(arg_strings))

    eleza _get_kwargs(self):
        rudisha sorted(self.__dict__.items())

    eleza _get_args(self):
        rudisha []


eleza _copy_items(items):
    ikiwa items is None:
        rudisha []
    # The copy module is used only in the 'append' and 'append_const'
    # actions, and it is needed only when the default value isn't a list.
    # Delay its agiza for speeding up the common case.
    ikiwa type(items) is list:
        rudisha items[:]
    agiza copy
    rudisha copy.copy(items)


# ===============
# Formatting Help
# ===============

kundi HelpFormatter(object):
    """Formatter for generating usage messages and argument help strings.

    Only the name of this kundi is considered a public API. All the methods
    provided by the kundi are considered an implementation detail.
    """

    eleza __init__(self,
                 prog,
                 indent_increment=2,
                 max_help_position=24,
                 width=None):

        # default setting for width
        ikiwa width is None:
            width = _shutil.get_terminal_size().columns
            width -= 2

        self._prog = prog
        self._indent_increment = indent_increment
        self._max_help_position = min(max_help_position,
                                      max(width - 20, indent_increment * 2))
        self._width = width

        self._current_indent = 0
        self._level = 0
        self._action_max_length = 0

        self._root_section = self._Section(self, None)
        self._current_section = self._root_section

        self._whitespace_matcher = _re.compile(r'\s+', _re.ASCII)
        self._long_break_matcher = _re.compile(r'\n\n\n+')

    # ===============================
    # Section and indentation methods
    # ===============================
    eleza _indent(self):
        self._current_indent += self._indent_increment
        self._level += 1

    eleza _dedent(self):
        self._current_indent -= self._indent_increment
        assert self._current_indent >= 0, 'Indent decreased below 0.'
        self._level -= 1

    kundi _Section(object):

        eleza __init__(self, formatter, parent, heading=None):
            self.formatter = formatter
            self.parent = parent
            self.heading = heading
            self.items = []

        eleza format_help(self):
            # format the indented section
            ikiwa self.parent is not None:
                self.formatter._indent()
            join = self.formatter._join_parts
            item_help = join([func(*args) for func, args in self.items])
            ikiwa self.parent is not None:
                self.formatter._dedent()

            # rudisha nothing ikiwa the section was empty
            ikiwa not item_help:
                rudisha ''

            # add the heading ikiwa the section was non-empty
            ikiwa self.heading is not SUPPRESS and self.heading is not None:
                current_indent = self.formatter._current_indent
                heading = '%*s%s:\n' % (current_indent, '', self.heading)
            else:
                heading = ''

            # join the section-initial newline, the heading and the help
            rudisha join(['\n', heading, item_help, '\n'])

    eleza _add_item(self, func, args):
        self._current_section.items.append((func, args))

    # ========================
    # Message building methods
    # ========================
    eleza start_section(self, heading):
        self._indent()
        section = self._Section(self, self._current_section, heading)
        self._add_item(section.format_help, [])
        self._current_section = section

    eleza end_section(self):
        self._current_section = self._current_section.parent
        self._dedent()

    eleza add_text(self, text):
        ikiwa text is not SUPPRESS and text is not None:
            self._add_item(self._format_text, [text])

    eleza add_usage(self, usage, actions, groups, prefix=None):
        ikiwa usage is not SUPPRESS:
            args = usage, actions, groups, prefix
            self._add_item(self._format_usage, args)

    eleza add_argument(self, action):
        ikiwa action.help is not SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            for subaction in self._iter_indented_subactions(action):
                invocations.append(get_invocation(subaction))

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    eleza add_arguments(self, actions):
        for action in actions:
            self.add_argument(action)

    # =======================
    # Help-formatting methods
    # =======================
    eleza format_help(self):
        help = self._root_section.format_help()
        ikiwa help:
            help = self._long_break_matcher.sub('\n\n', help)
            help = help.strip('\n') + '\n'
        rudisha help

    eleza _join_parts(self, part_strings):
        rudisha ''.join([part
                        for part in part_strings
                        ikiwa part and part is not SUPPRESS])

    eleza _format_usage(self, usage, actions, groups, prefix):
        ikiwa prefix is None:
            prefix = _('usage: ')

        # ikiwa usage is specified, use that
        ikiwa usage is not None:
            usage = usage % dict(prog=self._prog)

        # ikiwa no optionals or positionals are available, usage is just prog
        elikiwa usage is None and not actions:
            usage = '%(prog)s' % dict(prog=self._prog)

        # ikiwa optionals and positionals are available, calculate usage
        elikiwa usage is None:
            prog = '%(prog)s' % dict(prog=self._prog)

            # split optionals kutoka positionals
            optionals = []
            positionals = []
            for action in actions:
                ikiwa action.option_strings:
                    optionals.append(action)
                else:
                    positionals.append(action)

            # build full usage string
            format = self._format_actions_usage
            action_usage = format(optionals + positionals, groups)
            usage = ' '.join([s for s in [prog, action_usage] ikiwa s])

            # wrap the usage parts ikiwa it's too long
            text_width = self._width - self._current_indent
            ikiwa len(prefix) + len(usage) > text_width:

                # break usage into wrappable parts
                part_regexp = (
                    r'\(.*?\)+(?=\s|$)|'
                    r'\[.*?\]+(?=\s|$)|'
                    r'\S+'
                )
                opt_usage = format(optionals, groups)
                pos_usage = format(positionals, groups)
                opt_parts = _re.findall(part_regexp, opt_usage)
                pos_parts = _re.findall(part_regexp, pos_usage)
                assert ' '.join(opt_parts) == opt_usage
                assert ' '.join(pos_parts) == pos_usage

                # helper for wrapping lines
                eleza get_lines(parts, indent, prefix=None):
                    lines = []
                    line = []
                    ikiwa prefix is not None:
                        line_len = len(prefix) - 1
                    else:
                        line_len = len(indent) - 1
                    for part in parts:
                        ikiwa line_len + 1 + len(part) > text_width and line:
                            lines.append(indent + ' '.join(line))
                            line = []
                            line_len = len(indent) - 1
                        line.append(part)
                        line_len += len(part) + 1
                    ikiwa line:
                        lines.append(indent + ' '.join(line))
                    ikiwa prefix is not None:
                        lines[0] = lines[0][len(indent):]
                    rudisha lines

                # ikiwa prog is short, follow it with optionals or positionals
                ikiwa len(prefix) + len(prog) <= 0.75 * text_width:
                    indent = ' ' * (len(prefix) + len(prog) + 1)
                    ikiwa opt_parts:
                        lines = get_lines([prog] + opt_parts, indent, prefix)
                        lines.extend(get_lines(pos_parts, indent))
                    elikiwa pos_parts:
                        lines = get_lines([prog] + pos_parts, indent, prefix)
                    else:
                        lines = [prog]

                # ikiwa prog is long, put it on its own line
                else:
                    indent = ' ' * len(prefix)
                    parts = opt_parts + pos_parts
                    lines = get_lines(parts, indent)
                    ikiwa len(lines) > 1:
                        lines = []
                        lines.extend(get_lines(opt_parts, indent))
                        lines.extend(get_lines(pos_parts, indent))
                    lines = [prog] + lines

                # join lines into usage
                usage = '\n'.join(lines)

        # prefix with 'usage:'
        rudisha '%s%s\n\n' % (prefix, usage)

    eleza _format_actions_usage(self, actions, groups):
        # find group indices and identify actions in groups
        group_actions = set()
        inserts = {}
        for group in groups:
            try:
                start = actions.index(group._group_actions[0])
            except ValueError:
                continue
            else:
                end = start + len(group._group_actions)
                ikiwa actions[start:end] == group._group_actions:
                    for action in group._group_actions:
                        group_actions.add(action)
                    ikiwa not group.required:
                        ikiwa start in inserts:
                            inserts[start] += ' ['
                        else:
                            inserts[start] = '['
                        ikiwa end in inserts:
                            inserts[end] += ']'
                        else:
                            inserts[end] = ']'
                    else:
                        ikiwa start in inserts:
                            inserts[start] += ' ('
                        else:
                            inserts[start] = '('
                        ikiwa end in inserts:
                            inserts[end] += ')'
                        else:
                            inserts[end] = ')'
                    for i in range(start + 1, end):
                        inserts[i] = '|'

        # collect all actions format strings
        parts = []
        for i, action in enumerate(actions):

            # suppressed arguments are marked with None
            # remove | separators for suppressed arguments
            ikiwa action.help is SUPPRESS:
                parts.append(None)
                ikiwa inserts.get(i) == '|':
                    inserts.pop(i)
                elikiwa inserts.get(i + 1) == '|':
                    inserts.pop(i + 1)

            # produce all arg strings
            elikiwa not action.option_strings:
                default = self._get_default_metavar_for_positional(action)
                part = self._format_args(action, default)

                # ikiwa it's in a group, strip the outer []
                ikiwa action in group_actions:
                    ikiwa part[0] == '[' and part[-1] == ']':
                        part = part[1:-1]

                # add the action string to the list
                parts.append(part)

            # produce the first way to invoke the option in brackets
            else:
                option_string = action.option_strings[0]

                # ikiwa the Optional doesn't take a value, format is:
                #    -s or --long
                ikiwa action.nargs == 0:
                    part = '%s' % option_string

                # ikiwa the Optional takes a value, format is:
                #    -s ARGS or --long ARGS
                else:
                    default = self._get_default_metavar_for_optional(action)
                    args_string = self._format_args(action, default)
                    part = '%s %s' % (option_string, args_string)

                # make it look optional ikiwa it's not required or in a group
                ikiwa not action.required and action not in group_actions:
                    part = '[%s]' % part

                # add the action string to the list
                parts.append(part)

        # insert things at the necessary indices
        for i in sorted(inserts, reverse=True):
            parts[i:i] = [inserts[i]]

        # join all the action items with spaces
        text = ' '.join([item for item in parts ikiwa item is not None])

        # clean up separators for mutually exclusive groups
        open = r'[\[(]'
        close = r'[\])]'
        text = _re.sub(r'(%s) ' % open, r'\1', text)
        text = _re.sub(r' (%s)' % close, r'\1', text)
        text = _re.sub(r'%s *%s' % (open, close), r'', text)
        text = _re.sub(r'\(([^|]*)\)', r'\1', text)
        text = text.strip()

        # rudisha the text
        rudisha text

    eleza _format_text(self, text):
        ikiwa '%(prog)' in text:
            text = text % dict(prog=self._prog)
        text_width = max(self._width - self._current_indent, 11)
        indent = ' ' * self._current_indent
        rudisha self._fill_text(text, text_width, indent) + '\n\n'

    eleza _format_action(self, action):
        # determine the required width and the entry label
        help_position = min(self._action_max_length + 2,
                            self._max_help_position)
        help_width = max(self._width - help_position, 11)
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)

        # no help; start on same line and add a final newline
        ikiwa not action.help:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup

        # short action name; start on the same line and pad two spaces
        elikiwa len(action_header) <= action_width:
            tup = self._current_indent, '', action_width, action_header
            action_header = '%*s%-*s  ' % tup
            indent_first = 0

        # long action name; start on the next line
        else:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup
            indent_first = help_position

        # collect the pieces of the action help
        parts = [action_header]

        # ikiwa there was help for the action, add lines of help text
        ikiwa action.help:
            help_text = self._expand_help(action)
            help_lines = self._split_lines(help_text, help_width)
            parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
            for line in help_lines[1:]:
                parts.append('%*s%s\n' % (help_position, '', line))

        # or add a newline ikiwa the description doesn't end with one
        elikiwa not action_header.endswith('\n'):
            parts.append('\n')

        # ikiwa there are any sub-actions, add their help as well
        for subaction in self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))

        # rudisha a single string
        rudisha self._join_parts(parts)

    eleza _format_action_invocation(self, action):
        ikiwa not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            rudisha metavar

        else:
            parts = []

            # ikiwa the Optional doesn't take a value, format is:
            #    -s, --long
            ikiwa action.nargs == 0:
                parts.extend(action.option_strings)

            # ikiwa the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s %s' % (option_string, args_string))

            rudisha ', '.join(parts)

    eleza _metavar_formatter(self, action, default_metavar):
        ikiwa action.metavar is not None:
            result = action.metavar
        elikiwa action.choices is not None:
            choice_strs = [str(choice) for choice in action.choices]
            result = '{%s}' % ','.join(choice_strs)
        else:
            result = default_metavar

        eleza format(tuple_size):
            ikiwa isinstance(result, tuple):
                rudisha result
            else:
                rudisha (result, ) * tuple_size
        rudisha format

    eleza _format_args(self, action, default_metavar):
        get_metavar = self._metavar_formatter(action, default_metavar)
        ikiwa action.nargs is None:
            result = '%s' % get_metavar(1)
        elikiwa action.nargs == OPTIONAL:
            result = '[%s]' % get_metavar(1)
        elikiwa action.nargs == ZERO_OR_MORE:
            result = '[%s [%s ...]]' % get_metavar(2)
        elikiwa action.nargs == ONE_OR_MORE:
            result = '%s [%s ...]' % get_metavar(2)
        elikiwa action.nargs == REMAINDER:
            result = '...'
        elikiwa action.nargs == PARSER:
            result = '%s ...' % get_metavar(1)
        elikiwa action.nargs == SUPPRESS:
            result = ''
        else:
            try:
                formats = ['%s' for _ in range(action.nargs)]
            except TypeError:
                raise ValueError("invalid nargs value") kutoka None
            result = ' '.join(formats) % get_metavar(action.nargs)
        rudisha result

    eleza _expand_help(self, action):
        params = dict(vars(action), prog=self._prog)
        for name in list(params):
            ikiwa params[name] is SUPPRESS:
                del params[name]
        for name in list(params):
            ikiwa hasattr(params[name], '__name__'):
                params[name] = params[name].__name__
        ikiwa params.get('choices') is not None:
            choices_str = ', '.join([str(c) for c in params['choices']])
            params['choices'] = choices_str
        rudisha self._get_help_string(action) % params

    eleza _iter_indented_subactions(self, action):
        try:
            get_subactions = action._get_subactions
        except AttributeError:
            pass
        else:
            self._indent()
            yield kutoka get_subactions()
            self._dedent()

    eleza _split_lines(self, text, width):
        text = self._whitespace_matcher.sub(' ', text).strip()
        # The textwrap module is used only for formatting help.
        # Delay its agiza for speeding up the common usage of argparse.
        agiza textwrap
        rudisha textwrap.wrap(text, width)

    eleza _fill_text(self, text, width, indent):
        text = self._whitespace_matcher.sub(' ', text).strip()
        agiza textwrap
        rudisha textwrap.fill(text, width,
                             initial_indent=indent,
                             subsequent_indent=indent)

    eleza _get_help_string(self, action):
        rudisha action.help

    eleza _get_default_metavar_for_optional(self, action):
        rudisha action.dest.upper()

    eleza _get_default_metavar_for_positional(self, action):
        rudisha action.dest


kundi RawDescriptionHelpFormatter(HelpFormatter):
    """Help message formatter which retains any formatting in descriptions.

    Only the name of this kundi is considered a public API. All the methods
    provided by the kundi are considered an implementation detail.
    """

    eleza _fill_text(self, text, width, indent):
        rudisha ''.join(indent + line for line in text.splitlines(keepends=True))


kundi RawTextHelpFormatter(RawDescriptionHelpFormatter):
    """Help message formatter which retains formatting of all help text.

    Only the name of this kundi is considered a public API. All the methods
    provided by the kundi are considered an implementation detail.
    """

    eleza _split_lines(self, text, width):
        rudisha text.splitlines()


kundi ArgumentDefaultsHelpFormatter(HelpFormatter):
    """Help message formatter which adds default values to argument help.

    Only the name of this kundi is considered a public API. All the methods
    provided by the kundi are considered an implementation detail.
    """

    eleza _get_help_string(self, action):
        help = action.help
        ikiwa '%(default)' not in action.help:
            ikiwa action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                ikiwa action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        rudisha help


kundi MetavarTypeHelpFormatter(HelpFormatter):
    """Help message formatter which uses the argument 'type' as the default
    metavar value (instead of the argument 'dest')

    Only the name of this kundi is considered a public API. All the methods
    provided by the kundi are considered an implementation detail.
    """

    eleza _get_default_metavar_for_optional(self, action):
        rudisha action.type.__name__

    eleza _get_default_metavar_for_positional(self, action):
        rudisha action.type.__name__



# =====================
# Options and Arguments
# =====================

eleza _get_action_name(argument):
    ikiwa argument is None:
        rudisha None
    elikiwa argument.option_strings:
        rudisha  '/'.join(argument.option_strings)
    elikiwa argument.metavar not in (None, SUPPRESS):
        rudisha argument.metavar
    elikiwa argument.dest not in (None, SUPPRESS):
        rudisha argument.dest
    else:
        rudisha None


kundi ArgumentError(Exception):
    """An error kutoka creating or using an argument (optional or positional).

    The string value of this exception is the message, augmented with
    information about the argument that caused it.
    """

    eleza __init__(self, argument, message):
        self.argument_name = _get_action_name(argument)
        self.message = message

    eleza __str__(self):
        ikiwa self.argument_name is None:
            format = '%(message)s'
        else:
            format = 'argument %(argument_name)s: %(message)s'
        rudisha format % dict(message=self.message,
                             argument_name=self.argument_name)


kundi ArgumentTypeError(Exception):
    """An error kutoka trying to convert a command line string to a type."""
    pass


# ==============
# Action classes
# ==============

kundi Action(_AttributeHolder):
    """Information about how to convert command line strings to Python objects.

    Action objects are used by an ArgumentParser to represent the information
    needed to parse a single argument kutoka one or more strings kutoka the
    command line. The keyword arguments to the Action constructor are also
    all attributes of Action instances.

    Keyword Arguments:

        - option_strings -- A list of command-line option strings which
            should be associated with this action.

        - dest -- The name of the attribute to hold the created object(s)

        - nargs -- The number of command-line arguments that should be
            consumed. By default, one argument will be consumed and a single
            value will be produced.  Other values include:
                - N (an integer) consumes N arguments (and produces a list)
                - '?' consumes zero or one arguments
                - '*' consumes zero or more arguments (and produces a list)
                - '+' consumes one or more arguments (and produces a list)
            Note that the difference between the default and nargs=1 is that
            with the default, a single value will be produced, while with
            nargs=1, a list containing a single value will be produced.

        - const -- The value to be produced ikiwa the option is specified and the
            option uses an action that takes no values.

        - default -- The value to be produced ikiwa the option is not specified.

        - type -- A callable that accepts a single string argument, and
            returns the converted value.  The standard Python types str, int,
            float, and complex are useful examples of such callables.  If None,
            str is used.

        - choices -- A container of values that should be allowed. If not None,
            after a command-line argument has been converted to the appropriate
            type, an exception will be raised ikiwa it is not a member of this
            collection.

        - required -- True ikiwa the action must always be specified at the
            command line. This is only meaningful for optional command-line
            arguments.

        - help -- The help string describing the argument.

        - metavar -- The name to be used for the option's argument with the
            help string. If None, the 'dest' value will be used as the name.
    """

    eleza __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        self.option_strings = option_strings
        self.dest = dest
        self.nargs = nargs
        self.const = const
        self.default = default
        self.type = type
        self.choices = choices
        self.required = required
        self.help = help
        self.metavar = metavar

    eleza _get_kwargs(self):
        names = [
            'option_strings',
            'dest',
            'nargs',
            'const',
            'default',
            'type',
            'choices',
            'help',
            'metavar',
        ]
        rudisha [(name, getattr(self, name)) for name in names]

    eleza __call__(self, parser, namespace, values, option_string=None):
        raise NotImplementedError(_('.__call__() not defined'))


kundi _StoreAction(Action):

    eleza __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        ikiwa nargs == 0:
            raise ValueError('nargs for store actions must be != 0; ikiwa you '
                             'have nothing to store, actions such as store '
                             'true or store const may be more appropriate')
        ikiwa const is not None and nargs != OPTIONAL:
            raise ValueError('nargs must be %r to supply const' % OPTIONAL)
        super(_StoreAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    eleza __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


kundi _StoreConstAction(Action):

    eleza __init__(self,
                 option_strings,
                 dest,
                 const,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(_StoreConstAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=const,
            default=default,
            required=required,
            help=help)

    eleza __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.const)


kundi _StoreTrueAction(_StoreConstAction):

    eleza __init__(self,
                 option_strings,
                 dest,
                 default=False,
                 required=False,
                 help=None):
        super(_StoreTrueAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            const=True,
            default=default,
            required=required,
            help=help)


kundi _StoreFalseAction(_StoreConstAction):

    eleza __init__(self,
                 option_strings,
                 dest,
                 default=True,
                 required=False,
                 help=None):
        super(_StoreFalseAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            const=False,
            default=default,
            required=required,
            help=help)


kundi _AppendAction(Action):

    eleza __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        ikiwa nargs == 0:
            raise ValueError('nargs for append actions must be != 0; ikiwa arg '
                             'strings are not supplying the value to append, '
                             'the append const action may be more appropriate')
        ikiwa const is not None and nargs != OPTIONAL:
            raise ValueError('nargs must be %r to supply const' % OPTIONAL)
        super(_AppendAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    eleza __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = _copy_items(items)
        items.append(values)
        setattr(namespace, self.dest, items)


kundi _AppendConstAction(Action):

    eleza __init__(self,
                 option_strings,
                 dest,
                 const,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(_AppendConstAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=const,
            default=default,
            required=required,
            help=help,
            metavar=metavar)

    eleza __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = _copy_items(items)
        items.append(self.const)
        setattr(namespace, self.dest, items)


kundi _CountAction(Action):

    eleza __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 required=False,
                 help=None):
        super(_CountAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            required=required,
            help=help)

    eleza __call__(self, parser, namespace, values, option_string=None):
        count = getattr(namespace, self.dest, None)
        ikiwa count is None:
            count = 0
        setattr(namespace, self.dest, count + 1)


kundi _HelpAction(Action):

    eleza __init__(self,
                 option_strings,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 help=None):
        super(_HelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    eleza __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        parser.exit()


kundi _VersionAction(Action):

    eleza __init__(self,
                 option_strings,
                 version=None,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 help="show program's version number and exit"):
        super(_VersionAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)
        self.version = version

    eleza __call__(self, parser, namespace, values, option_string=None):
        version = self.version
        ikiwa version is None:
            version = parser.version
        formatter = parser._get_formatter()
        formatter.add_text(version)
        parser._print_message(formatter.format_help(), _sys.stdout)
        parser.exit()


kundi _SubParsersAction(Action):

    kundi _ChoicesPseudoAction(Action):

        eleza __init__(self, name, aliases, help):
            metavar = dest = name
            ikiwa aliases:
                metavar += ' (%s)' % ', '.join(aliases)
            sup = super(_SubParsersAction._ChoicesPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help,
                         metavar=metavar)

    eleza __init__(self,
                 option_strings,
                 prog,
                 parser_class,
                 dest=SUPPRESS,
                 required=False,
                 help=None,
                 metavar=None):

        self._prog_prefix = prog
        self._parser_kundi = parser_class
        self._name_parser_map = {}
        self._choices_actions = []

        super(_SubParsersAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=PARSER,
            choices=self._name_parser_map,
            required=required,
            help=help,
            metavar=metavar)

    eleza add_parser(self, name, **kwargs):
        # set prog kutoka the existing prefix
        ikiwa kwargs.get('prog') is None:
            kwargs['prog'] = '%s %s' % (self._prog_prefix, name)

        aliases = kwargs.pop('aliases', ())

        # create a pseudo-action to hold the choice help
        ikiwa 'help' in kwargs:
            help = kwargs.pop('help')
            choice_action = self._ChoicesPseudoAction(name, aliases, help)
            self._choices_actions.append(choice_action)

        # create the parser and add it to the map
        parser = self._parser_class(**kwargs)
        self._name_parser_map[name] = parser

        # make parser available under aliases also
        for alias in aliases:
            self._name_parser_map[alias] = parser

        rudisha parser

    eleza _get_subactions(self):
        rudisha self._choices_actions

    eleza __call__(self, parser, namespace, values, option_string=None):
        parser_name = values[0]
        arg_strings = values[1:]

        # set the parser name ikiwa requested
        ikiwa self.dest is not SUPPRESS:
            setattr(namespace, self.dest, parser_name)

        # select the parser
        try:
            parser = self._name_parser_map[parser_name]
        except KeyError:
            args = {'parser_name': parser_name,
                    'choices': ', '.join(self._name_parser_map)}
            msg = _('unknown parser %(parser_name)r (choices: %(choices)s)') % args
            raise ArgumentError(self, msg)

        # parse all the remaining options into the namespace
        # store any unrecognized options on the object, so that the top
        # level parser can decide what to do with them

        # In case this subparser defines new defaults, we parse them
        # in a new namespace object and then update the original
        # namespace for the relevant parts.
        subnamespace, arg_strings = parser.parse_known_args(arg_strings, None)
        for key, value in vars(subnamespace).items():
            setattr(namespace, key, value)

        ikiwa arg_strings:
            vars(namespace).setdefault(_UNRECOGNIZED_ARGS_ATTR, [])
            getattr(namespace, _UNRECOGNIZED_ARGS_ATTR).extend(arg_strings)

kundi _ExtendAction(_AppendAction):
    eleza __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = _copy_items(items)
        items.extend(values)
        setattr(namespace, self.dest, items)

# ==============
# Type classes
# ==============

kundi FileType(object):
    """Factory for creating file object types

    Instances of FileType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - mode -- A string indicating how the file is to be opened. Accepts the
            same values as the builtin open() function.
        - bufsize -- The file's desired buffer size. Accepts the same values as
            the builtin open() function.
        - encoding -- The file's encoding. Accepts the same values as the
            builtin open() function.
        - errors -- A string indicating how encoding and decoding errors are to
            be handled. Accepts the same value as the builtin open() function.
    """

    eleza __init__(self, mode='r', bufsize=-1, encoding=None, errors=None):
        self._mode = mode
        self._bufsize = bufsize
        self._encoding = encoding
        self._errors = errors

    eleza __call__(self, string):
        # the special argument "-" means sys.std{in,out}
        ikiwa string == '-':
            ikiwa 'r' in self._mode:
                rudisha _sys.stdin
            elikiwa 'w' in self._mode:
                rudisha _sys.stdout
            else:
                msg = _('argument "-" with mode %r') % self._mode
                raise ValueError(msg)

        # all other arguments are used as file names
        try:
            rudisha open(string, self._mode, self._bufsize, self._encoding,
                        self._errors)
        except OSError as e:
            args = {'filename': string, 'error': e}
            message = _("can't open '%(filename)s': %(error)s")
            raise ArgumentTypeError(message % args)

    eleza __repr__(self):
        args = self._mode, self._bufsize
        kwargs = [('encoding', self._encoding), ('errors', self._errors)]
        args_str = ', '.join([repr(arg) for arg in args ikiwa arg != -1] +
                             ['%s=%r' % (kw, arg) for kw, arg in kwargs
                              ikiwa arg is not None])
        rudisha '%s(%s)' % (type(self).__name__, args_str)

# ===========================
# Optional and Positional Parsing
# ===========================

kundi Namespace(_AttributeHolder):
    """Simple object for storing attributes.

    Implements equality by attribute names and values, and provides a simple
    string representation.
    """

    eleza __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

    eleza __eq__(self, other):
        ikiwa not isinstance(other, Namespace):
            rudisha NotImplemented
        rudisha vars(self) == vars(other)

    eleza __contains__(self, key):
        rudisha key in self.__dict__


kundi _ActionsContainer(object):

    eleza __init__(self,
                 description,
                 prefix_chars,
                 argument_default,
                 conflict_handler):
        super(_ActionsContainer, self).__init__()

        self.description = description
        self.argument_default = argument_default
        self.prefix_chars = prefix_chars
        self.conflict_handler = conflict_handler

        # set up registries
        self._registries = {}

        # register actions
        self.register('action', None, _StoreAction)
        self.register('action', 'store', _StoreAction)
        self.register('action', 'store_const', _StoreConstAction)
        self.register('action', 'store_true', _StoreTrueAction)
        self.register('action', 'store_false', _StoreFalseAction)
        self.register('action', 'append', _AppendAction)
        self.register('action', 'append_const', _AppendConstAction)
        self.register('action', 'count', _CountAction)
        self.register('action', 'help', _HelpAction)
        self.register('action', 'version', _VersionAction)
        self.register('action', 'parsers', _SubParsersAction)
        self.register('action', 'extend', _ExtendAction)

        # raise an exception ikiwa the conflict handler is invalid
        self._get_handler()

        # action storage
        self._actions = []
        self._option_string_actions = {}

        # groups
        self._action_groups = []
        self._mutually_exclusive_groups = []

        # defaults storage
        self._defaults = {}

        # determines whether an "option" looks like a negative number
        self._negative_number_matcher = _re.compile(r'^-\d+$|^-\d*\.\d+$')

        # whether or not there are any optionals that look like negative
        # numbers -- uses a list so it can be shared and edited
        self._has_negative_number_optionals = []

    # ====================
    # Registration methods
    # ====================
    eleza register(self, registry_name, value, object):
        registry = self._registries.setdefault(registry_name, {})
        registry[value] = object

    eleza _registry_get(self, registry_name, value, default=None):
        rudisha self._registries[registry_name].get(value, default)

    # ==================================
    # Namespace default accessor methods
    # ==================================
    eleza set_defaults(self, **kwargs):
        self._defaults.update(kwargs)

        # ikiwa these defaults match any existing arguments, replace
        # the previous default on the object with the new one
        for action in self._actions:
            ikiwa action.dest in kwargs:
                action.default = kwargs[action.dest]

    eleza get_default(self, dest):
        for action in self._actions:
            ikiwa action.dest == dest and action.default is not None:
                rudisha action.default
        rudisha self._defaults.get(dest, None)


    # =======================
    # Adding argument actions
    # =======================
    eleza add_argument(self, *args, **kwargs):
        """
        add_argument(dest, ..., name=value, ...)
        add_argument(option_string, option_string, ..., name=value, ...)
        """

        # ikiwa no positional args are supplied or only one is supplied and
        # it doesn't look like an option string, parse a positional
        # argument
        chars = self.prefix_chars
        ikiwa not args or len(args) == 1 and args[0][0] not in chars:
            ikiwa args and 'dest' in kwargs:
                raise ValueError('dest supplied twice for positional argument')
            kwargs = self._get_positional_kwargs(*args, **kwargs)

        # otherwise, we're adding an optional argument
        else:
            kwargs = self._get_optional_kwargs(*args, **kwargs)

        # ikiwa no default was supplied, use the parser-level default
        ikiwa 'default' not in kwargs:
            dest = kwargs['dest']
            ikiwa dest in self._defaults:
                kwargs['default'] = self._defaults[dest]
            elikiwa self.argument_default is not None:
                kwargs['default'] = self.argument_default

        # create the action object, and add it to the parser
        action_kundi = self._pop_action_class(kwargs)
        ikiwa not callable(action_class):
            raise ValueError('unknown action "%s"' % (action_class,))
        action = action_class(**kwargs)

        # raise an error ikiwa the action type is not callable
        type_func = self._registry_get('type', action.type, action.type)
        ikiwa not callable(type_func):
            raise ValueError('%r is not callable' % (type_func,))

        ikiwa type_func is FileType:
            raise ValueError('%r is a FileType kundi object, instance of it'
                             ' must be passed' % (type_func,))

        # raise an error ikiwa the metavar does not match the type
        ikiwa hasattr(self, "_get_formatter"):
            try:
                self._get_formatter()._format_args(action, None)
            except TypeError:
                raise ValueError("length of metavar tuple does not match nargs")

        rudisha self._add_action(action)

    eleza add_argument_group(self, *args, **kwargs):
        group = _ArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        rudisha group

    eleza add_mutually_exclusive_group(self, **kwargs):
        group = _MutuallyExclusiveGroup(self, **kwargs)
        self._mutually_exclusive_groups.append(group)
        rudisha group

    eleza _add_action(self, action):
        # resolve any conflicts
        self._check_conflict(action)

        # add to actions list
        self._actions.append(action)
        action.container = self

        # index the action by any option strings it has
        for option_string in action.option_strings:
            self._option_string_actions[option_string] = action

        # set the flag ikiwa any option strings look like negative numbers
        for option_string in action.option_strings:
            ikiwa self._negative_number_matcher.match(option_string):
                ikiwa not self._has_negative_number_optionals:
                    self._has_negative_number_optionals.append(True)

        # rudisha the created action
        rudisha action

    eleza _remove_action(self, action):
        self._actions.remove(action)

    eleza _add_container_actions(self, container):
        # collect groups by titles
        title_group_map = {}
        for group in self._action_groups:
            ikiwa group.title in title_group_map:
                msg = _('cannot merge actions - two groups are named %r')
                raise ValueError(msg % (group.title))
            title_group_map[group.title] = group

        # map each action to its group
        group_map = {}
        for group in container._action_groups:

            # ikiwa a group with the title exists, use that, otherwise
            # create a new group matching the container's group
            ikiwa group.title not in title_group_map:
                title_group_map[group.title] = self.add_argument_group(
                    title=group.title,
                    description=group.description,
                    conflict_handler=group.conflict_handler)

            # map the actions to their new group
            for action in group._group_actions:
                group_map[action] = title_group_map[group.title]

        # add container's mutually exclusive groups
        # NOTE: ikiwa add_mutually_exclusive_group ever gains title= and
        # description= then this code will need to be expanded as above
        for group in container._mutually_exclusive_groups:
            mutex_group = self.add_mutually_exclusive_group(
                required=group.required)

            # map the actions to their new mutex group
            for action in group._group_actions:
                group_map[action] = mutex_group

        # add all actions to this container or their group
        for action in container._actions:
            group_map.get(action, self)._add_action(action)

    eleza _get_positional_kwargs(self, dest, **kwargs):
        # make sure required is not specified
        ikiwa 'required' in kwargs:
            msg = _("'required' is an invalid argument for positionals")
            raise TypeError(msg)

        # mark positional arguments as required ikiwa at least one is
        # always required
        ikiwa kwargs.get('nargs') not in [OPTIONAL, ZERO_OR_MORE]:
            kwargs['required'] = True
        ikiwa kwargs.get('nargs') == ZERO_OR_MORE and 'default' not in kwargs:
            kwargs['required'] = True

        # rudisha the keyword arguments with no option strings
        rudisha dict(kwargs, dest=dest, option_strings=[])

    eleza _get_optional_kwargs(self, *args, **kwargs):
        # determine short and long option strings
        option_strings = []
        long_option_strings = []
        for option_string in args:
            # error on strings that don't start with an appropriate prefix
            ikiwa not option_string[0] in self.prefix_chars:
                args = {'option': option_string,
                        'prefix_chars': self.prefix_chars}
                msg = _('invalid option string %(option)r: '
                        'must start with a character %(prefix_chars)r')
                raise ValueError(msg % args)

            # strings starting with two prefix characters are long options
            option_strings.append(option_string)
            ikiwa option_string[0] in self.prefix_chars:
                ikiwa len(option_string) > 1:
                    ikiwa option_string[1] in self.prefix_chars:
                        long_option_strings.append(option_string)

        # infer destination, '--foo-bar' -> 'foo_bar' and '-x' -> 'x'
        dest = kwargs.pop('dest', None)
        ikiwa dest is None:
            ikiwa long_option_strings:
                dest_option_string = long_option_strings[0]
            else:
                dest_option_string = option_strings[0]
            dest = dest_option_string.lstrip(self.prefix_chars)
            ikiwa not dest:
                msg = _('dest= is required for options like %r')
                raise ValueError(msg % option_string)
            dest = dest.replace('-', '_')

        # rudisha the updated keyword arguments
        rudisha dict(kwargs, dest=dest, option_strings=option_strings)

    eleza _pop_action_class(self, kwargs, default=None):
        action = kwargs.pop('action', default)
        rudisha self._registry_get('action', action, action)

    eleza _get_handler(self):
        # determine function kutoka conflict handler string
        handler_func_name = '_handle_conflict_%s' % self.conflict_handler
        try:
            rudisha getattr(self, handler_func_name)
        except AttributeError:
            msg = _('invalid conflict_resolution value: %r')
            raise ValueError(msg % self.conflict_handler)

    eleza _check_conflict(self, action):

        # find all options that conflict with this option
        confl_optionals = []
        for option_string in action.option_strings:
            ikiwa option_string in self._option_string_actions:
                confl_optional = self._option_string_actions[option_string]
                confl_optionals.append((option_string, confl_optional))

        # resolve any conflicts
        ikiwa confl_optionals:
            conflict_handler = self._get_handler()
            conflict_handler(action, confl_optionals)

    eleza _handle_conflict_error(self, action, conflicting_actions):
        message = ngettext('conflicting option string: %s',
                           'conflicting option strings: %s',
                           len(conflicting_actions))
        conflict_string = ', '.join([option_string
                                     for option_string, action
                                     in conflicting_actions])
        raise ArgumentError(action, message % conflict_string)

    eleza _handle_conflict_resolve(self, action, conflicting_actions):

        # remove all conflicting options
        for option_string, action in conflicting_actions:

            # remove the conflicting option
            action.option_strings.remove(option_string)
            self._option_string_actions.pop(option_string, None)

            # ikiwa the option now has no option string, remove it kutoka the
            # container holding it
            ikiwa not action.option_strings:
                action.container._remove_action(action)


kundi _ArgumentGroup(_ActionsContainer):

    eleza __init__(self, container, title=None, description=None, **kwargs):
        # add any missing keyword arguments by checking the container
        update = kwargs.setdefault
        update('conflict_handler', container.conflict_handler)
        update('prefix_chars', container.prefix_chars)
        update('argument_default', container.argument_default)
        super_init = super(_ArgumentGroup, self).__init__
        super_init(description=description, **kwargs)

        # group attributes
        self.title = title
        self._group_actions = []

        # share most attributes with the container
        self._registries = container._registries
        self._actions = container._actions
        self._option_string_actions = container._option_string_actions
        self._defaults = container._defaults
        self._has_negative_number_optionals = \
            container._has_negative_number_optionals
        self._mutually_exclusive_groups = container._mutually_exclusive_groups

    eleza _add_action(self, action):
        action = super(_ArgumentGroup, self)._add_action(action)
        self._group_actions.append(action)
        rudisha action

    eleza _remove_action(self, action):
        super(_ArgumentGroup, self)._remove_action(action)
        self._group_actions.remove(action)


kundi _MutuallyExclusiveGroup(_ArgumentGroup):

    eleza __init__(self, container, required=False):
        super(_MutuallyExclusiveGroup, self).__init__(container)
        self.required = required
        self._container = container

    eleza _add_action(self, action):
        ikiwa action.required:
            msg = _('mutually exclusive arguments must be optional')
            raise ValueError(msg)
        action = self._container._add_action(action)
        self._group_actions.append(action)
        rudisha action

    eleza _remove_action(self, action):
        self._container._remove_action(action)
        self._group_actions.remove(action)


kundi ArgumentParser(_AttributeHolder, _ActionsContainer):
    """Object for parsing command line strings into Python objects.

    Keyword Arguments:
        - prog -- The name of the program (default: sys.argv[0])
        - usage -- A usage message (default: auto-generated kutoka arguments)
        - description -- A description of what the program does
        - epilog -- Text following the argument descriptions
        - parents -- Parsers whose arguments should be copied into this one
        - formatter_kundi -- HelpFormatter kundi for printing help messages
        - prefix_chars -- Characters that prefix optional arguments
        - kutokafile_prefix_chars -- Characters that prefix files containing
            additional arguments
        - argument_default -- The default value for all arguments
        - conflict_handler -- String indicating how to handle conflicts
        - add_help -- Add a -h/-help option
        - allow_abbrev -- Allow long options to be abbreviated unambiguously
    """

    eleza __init__(self,
                 prog=None,
                 usage=None,
                 description=None,
                 epilog=None,
                 parents=[],
                 formatter_class=HelpFormatter,
                 prefix_chars='-',
                 kutokafile_prefix_chars=None,
                 argument_default=None,
                 conflict_handler='error',
                 add_help=True,
                 allow_abbrev=True):

        superinit = super(ArgumentParser, self).__init__
        superinit(description=description,
                  prefix_chars=prefix_chars,
                  argument_default=argument_default,
                  conflict_handler=conflict_handler)

        # default setting for prog
        ikiwa prog is None:
            prog = _os.path.basename(_sys.argv[0])

        self.prog = prog
        self.usage = usage
        self.epilog = epilog
        self.formatter_kundi = formatter_class
        self.kutokafile_prefix_chars = kutokafile_prefix_chars
        self.add_help = add_help
        self.allow_abbrev = allow_abbrev

        add_group = self.add_argument_group
        self._positionals = add_group(_('positional arguments'))
        self._optionals = add_group(_('optional arguments'))
        self._subparsers = None

        # register types
        eleza identity(string):
            rudisha string
        self.register('type', None, identity)

        # add help argument ikiwa necessary
        # (using explicit default to override global argument_default)
        default_prefix = '-' ikiwa '-' in prefix_chars else prefix_chars[0]
        ikiwa self.add_help:
            self.add_argument(
                default_prefix+'h', default_prefix*2+'help',
                action='help', default=SUPPRESS,
                help=_('show this help message and exit'))

        # add parent arguments and defaults
        for parent in parents:
            self._add_container_actions(parent)
            try:
                defaults = parent._defaults
            except AttributeError:
                pass
            else:
                self._defaults.update(defaults)

    # =======================
    # Pretty __repr__ methods
    # =======================
    eleza _get_kwargs(self):
        names = [
            'prog',
            'usage',
            'description',
            'formatter_class',
            'conflict_handler',
            'add_help',
        ]
        rudisha [(name, getattr(self, name)) for name in names]

    # ==================================
    # Optional/Positional adding methods
    # ==================================
    eleza add_subparsers(self, **kwargs):
        ikiwa self._subparsers is not None:
            self.error(_('cannot have multiple subparser arguments'))

        # add the parser kundi to the arguments ikiwa it's not present
        kwargs.setdefault('parser_class', type(self))

        ikiwa 'title' in kwargs or 'description' in kwargs:
            title = _(kwargs.pop('title', 'subcommands'))
            description = _(kwargs.pop('description', None))
            self._subparsers = self.add_argument_group(title, description)
        else:
            self._subparsers = self._positionals

        # prog defaults to the usage message of this parser, skipping
        # optional arguments and with no "usage:" prefix
        ikiwa kwargs.get('prog') is None:
            formatter = self._get_formatter()
            positionals = self._get_positional_actions()
            groups = self._mutually_exclusive_groups
            formatter.add_usage(self.usage, positionals, groups, '')
            kwargs['prog'] = formatter.format_help().strip()

        # create the parsers action and add it to the positionals list
        parsers_kundi = self._pop_action_class(kwargs, 'parsers')
        action = parsers_class(option_strings=[], **kwargs)
        self._subparsers._add_action(action)

        # rudisha the created parsers action
        rudisha action

    eleza _add_action(self, action):
        ikiwa action.option_strings:
            self._optionals._add_action(action)
        else:
            self._positionals._add_action(action)
        rudisha action

    eleza _get_optional_actions(self):
        rudisha [action
                for action in self._actions
                ikiwa action.option_strings]

    eleza _get_positional_actions(self):
        rudisha [action
                for action in self._actions
                ikiwa not action.option_strings]

    # =====================================
    # Command line argument parsing methods
    # =====================================
    eleza parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        ikiwa argv:
            msg = _('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        rudisha args

    eleza parse_known_args(self, args=None, namespace=None):
        ikiwa args is None:
            # args default to the system args
            args = _sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)

        # default Namespace built kutoka parser defaults
        ikiwa namespace is None:
            namespace = Namespace()

        # add any action defaults that aren't present
        for action in self._actions:
            ikiwa action.dest is not SUPPRESS:
                ikiwa not hasattr(namespace, action.dest):
                    ikiwa action.default is not SUPPRESS:
                        setattr(namespace, action.dest, action.default)

        # add any parser defaults that aren't present
        for dest in self._defaults:
            ikiwa not hasattr(namespace, dest):
                setattr(namespace, dest, self._defaults[dest])

        # parse the arguments and exit ikiwa there are any errors
        try:
            namespace, args = self._parse_known_args(args, namespace)
            ikiwa hasattr(namespace, _UNRECOGNIZED_ARGS_ATTR):
                args.extend(getattr(namespace, _UNRECOGNIZED_ARGS_ATTR))
                delattr(namespace, _UNRECOGNIZED_ARGS_ATTR)
            rudisha namespace, args
        except ArgumentError:
            err = _sys.exc_info()[1]
            self.error(str(err))

    eleza _parse_known_args(self, arg_strings, namespace):
        # replace arg strings that are file references
        ikiwa self.kutokafile_prefix_chars is not None:
            arg_strings = self._read_args_kutoka_files(arg_strings)

        # map all mutually exclusive arguments to the other arguments
        # they can't occur with
        action_conflicts = {}
        for mutex_group in self._mutually_exclusive_groups:
            group_actions = mutex_group._group_actions
            for i, mutex_action in enumerate(mutex_group._group_actions):
                conflicts = action_conflicts.setdefault(mutex_action, [])
                conflicts.extend(group_actions[:i])
                conflicts.extend(group_actions[i + 1:])

        # find all option indices, and determine the arg_string_pattern
        # which has an 'O' ikiwa there is an option at an index,
        # an 'A' ikiwa there is an argument, or a '-' ikiwa there is a '--'
        option_string_indices = {}
        arg_string_pattern_parts = []
        arg_strings_iter = iter(arg_strings)
        for i, arg_string in enumerate(arg_strings_iter):

            # all args after -- are non-options
            ikiwa arg_string == '--':
                arg_string_pattern_parts.append('-')
                for arg_string in arg_strings_iter:
                    arg_string_pattern_parts.append('A')

            # otherwise, add the arg to the arg strings
            # and note the index ikiwa it was an option
            else:
                option_tuple = self._parse_optional(arg_string)
                ikiwa option_tuple is None:
                    pattern = 'A'
                else:
                    option_string_indices[i] = option_tuple
                    pattern = 'O'
                arg_string_pattern_parts.append(pattern)

        # join the pieces together to form the pattern
        arg_strings_pattern = ''.join(arg_string_pattern_parts)

        # converts arg strings to the appropriate and then takes the action
        seen_actions = set()
        seen_non_default_actions = set()

        eleza take_action(action, argument_strings, option_string=None):
            seen_actions.add(action)
            argument_values = self._get_values(action, argument_strings)

            # error ikiwa this argument is not allowed with other previously
            # seen arguments, assuming that actions that use the default
            # value don't really count as "present"
            ikiwa argument_values is not action.default:
                seen_non_default_actions.add(action)
                for conflict_action in action_conflicts.get(action, []):
                    ikiwa conflict_action in seen_non_default_actions:
                        msg = _('not allowed with argument %s')
                        action_name = _get_action_name(conflict_action)
                        raise ArgumentError(action, msg % action_name)

            # take the action ikiwa we didn't receive a SUPPRESS value
            # (e.g. kutoka a default)
            ikiwa argument_values is not SUPPRESS:
                action(self, namespace, argument_values, option_string)

        # function to convert arg_strings into an optional action
        eleza consume_optional(start_index):

            # get the optional identified at this index
            option_tuple = option_string_indices[start_index]
            action, option_string, explicit_arg = option_tuple

            # identify additional optionals in the same arg string
            # (e.g. -xyz is the same as -x -y -z ikiwa no args are required)
            match_argument = self._match_argument
            action_tuples = []
            while True:

                # ikiwa we found no optional action, skip it
                ikiwa action is None:
                    extras.append(arg_strings[start_index])
                    rudisha start_index + 1

                # ikiwa there is an explicit argument, try to match the
                # optional's string arguments to only this
                ikiwa explicit_arg is not None:
                    arg_count = match_argument(action, 'A')

                    # ikiwa the action is a single-dash option and takes no
                    # arguments, try to parse more single-dash options out
                    # of the tail of the option string
                    chars = self.prefix_chars
                    ikiwa arg_count == 0 and option_string[1] not in chars:
                        action_tuples.append((action, [], option_string))
                        char = option_string[0]
                        option_string = char + explicit_arg[0]
                        new_explicit_arg = explicit_arg[1:] or None
                        optionals_map = self._option_string_actions
                        ikiwa option_string in optionals_map:
                            action = optionals_map[option_string]
                            explicit_arg = new_explicit_arg
                        else:
                            msg = _('ignored explicit argument %r')
                            raise ArgumentError(action, msg % explicit_arg)

                    # ikiwa the action expect exactly one argument, we've
                    # successfully matched the option; exit the loop
                    elikiwa arg_count == 1:
                        stop = start_index + 1
                        args = [explicit_arg]
                        action_tuples.append((action, args, option_string))
                        break

                    # error ikiwa a double-dash option did not use the
                    # explicit argument
                    else:
                        msg = _('ignored explicit argument %r')
                        raise ArgumentError(action, msg % explicit_arg)

                # ikiwa there is no explicit argument, try to match the
                # optional's string arguments with the following strings
                # ikiwa successful, exit the loop
                else:
                    start = start_index + 1
                    selected_patterns = arg_strings_pattern[start:]
                    arg_count = match_argument(action, selected_patterns)
                    stop = start + arg_count
                    args = arg_strings[start:stop]
                    action_tuples.append((action, args, option_string))
                    break

            # add the Optional to the list and rudisha the index at which
            # the Optional's string args stopped
            assert action_tuples
            for action, args, option_string in action_tuples:
                take_action(action, args, option_string)
            rudisha stop

        # the list of Positionals left to be parsed; this is modified
        # by consume_positionals()
        positionals = self._get_positional_actions()

        # function to convert arg_strings into positional actions
        eleza consume_positionals(start_index):
            # match as many Positionals as possible
            match_partial = self._match_arguments_partial
            selected_pattern = arg_strings_pattern[start_index:]
            arg_counts = match_partial(positionals, selected_pattern)

            # slice off the appropriate arg strings for each Positional
            # and add the Positional and its args to the list
            for action, arg_count in zip(positionals, arg_counts):
                args = arg_strings[start_index: start_index + arg_count]
                start_index += arg_count
                take_action(action, args)

            # slice off the Positionals that we just parsed and rudisha the
            # index at which the Positionals' string args stopped
            positionals[:] = positionals[len(arg_counts):]
            rudisha start_index

        # consume Positionals and Optionals alternately, until we have
        # passed the last option string
        extras = []
        start_index = 0
        ikiwa option_string_indices:
            max_option_string_index = max(option_string_indices)
        else:
            max_option_string_index = -1
        while start_index <= max_option_string_index:

            # consume any Positionals preceding the next option
            next_option_string_index = min([
                index
                for index in option_string_indices
                ikiwa index >= start_index])
            ikiwa start_index != next_option_string_index:
                positionals_end_index = consume_positionals(start_index)

                # only try to parse the next optional ikiwa we didn't consume
                # the option string during the positionals parsing
                ikiwa positionals_end_index > start_index:
                    start_index = positionals_end_index
                    continue
                else:
                    start_index = positionals_end_index

            # ikiwa we consumed all the positionals we could and we're not
            # at the index of an option string, there were extra arguments
            ikiwa start_index not in option_string_indices:
                strings = arg_strings[start_index:next_option_string_index]
                extras.extend(strings)
                start_index = next_option_string_index

            # consume the next optional and any arguments for it
            start_index = consume_optional(start_index)

        # consume any positionals following the last Optional
        stop_index = consume_positionals(start_index)

        # ikiwa we didn't consume all the argument strings, there were extras
        extras.extend(arg_strings[stop_index:])

        # make sure all required actions were present and also convert
        # action defaults which were not given as arguments
        required_actions = []
        for action in self._actions:
            ikiwa action not in seen_actions:
                ikiwa action.required:
                    required_actions.append(_get_action_name(action))
                else:
                    # Convert action default now instead of doing it before
                    # parsing arguments to avoid calling convert functions
                    # twice (which may fail) ikiwa the argument was given, but
                    # only ikiwa it was defined already in the namespace
                    ikiwa (action.default is not None and
                        isinstance(action.default, str) and
                        hasattr(namespace, action.dest) and
                        action.default is getattr(namespace, action.dest)):
                        setattr(namespace, action.dest,
                                self._get_value(action, action.default))

        ikiwa required_actions:
            self.error(_('the following arguments are required: %s') %
                       ', '.join(required_actions))

        # make sure all required groups had one option present
        for group in self._mutually_exclusive_groups:
            ikiwa group.required:
                for action in group._group_actions:
                    ikiwa action in seen_non_default_actions:
                        break

                # ikiwa no actions were used, report the error
                else:
                    names = [_get_action_name(action)
                             for action in group._group_actions
                             ikiwa action.help is not SUPPRESS]
                    msg = _('one of the arguments %s is required')
                    self.error(msg % ' '.join(names))

        # rudisha the updated namespace and the extra arguments
        rudisha namespace, extras

    eleza _read_args_kutoka_files(self, arg_strings):
        # expand arguments referencing files
        new_arg_strings = []
        for arg_string in arg_strings:

            # for regular arguments, just add them back into the list
            ikiwa not arg_string or arg_string[0] not in self.kutokafile_prefix_chars:
                new_arg_strings.append(arg_string)

            # replace arguments referencing files with the file content
            else:
                try:
                    with open(arg_string[1:]) as args_file:
                        arg_strings = []
                        for arg_line in args_file.read().splitlines():
                            for arg in self.convert_arg_line_to_args(arg_line):
                                arg_strings.append(arg)
                        arg_strings = self._read_args_kutoka_files(arg_strings)
                        new_arg_strings.extend(arg_strings)
                except OSError:
                    err = _sys.exc_info()[1]
                    self.error(str(err))

        # rudisha the modified argument list
        rudisha new_arg_strings

    eleza convert_arg_line_to_args(self, arg_line):
        rudisha [arg_line]

    eleza _match_argument(self, action, arg_strings_pattern):
        # match the pattern for this action to the arg strings
        nargs_pattern = self._get_nargs_pattern(action)
        match = _re.match(nargs_pattern, arg_strings_pattern)

        # raise an exception ikiwa we weren't able to find a match
        ikiwa match is None:
            nargs_errors = {
                None: _('expected one argument'),
                OPTIONAL: _('expected at most one argument'),
                ONE_OR_MORE: _('expected at least one argument'),
            }
            default = ngettext('expected %s argument',
                               'expected %s arguments',
                               action.nargs) % action.nargs
            msg = nargs_errors.get(action.nargs, default)
            raise ArgumentError(action, msg)

        # rudisha the number of arguments matched
        rudisha len(match.group(1))

    eleza _match_arguments_partial(self, actions, arg_strings_pattern):
        # progressively shorten the actions list by slicing off the
        # final actions until we find a match
        result = []
        for i in range(len(actions), 0, -1):
            actions_slice = actions[:i]
            pattern = ''.join([self._get_nargs_pattern(action)
                               for action in actions_slice])
            match = _re.match(pattern, arg_strings_pattern)
            ikiwa match is not None:
                result.extend([len(string) for string in match.groups()])
                break

        # rudisha the list of arg string counts
        rudisha result

    eleza _parse_optional(self, arg_string):
        # ikiwa it's an empty string, it was meant to be a positional
        ikiwa not arg_string:
            rudisha None

        # ikiwa it doesn't start with a prefix, it was meant to be positional
        ikiwa not arg_string[0] in self.prefix_chars:
            rudisha None

        # ikiwa the option string is present in the parser, rudisha the action
        ikiwa arg_string in self._option_string_actions:
            action = self._option_string_actions[arg_string]
            rudisha action, arg_string, None

        # ikiwa it's just a single character, it was meant to be positional
        ikiwa len(arg_string) == 1:
            rudisha None

        # ikiwa the option string before the "=" is present, rudisha the action
        ikiwa '=' in arg_string:
            option_string, explicit_arg = arg_string.split('=', 1)
            ikiwa option_string in self._option_string_actions:
                action = self._option_string_actions[option_string]
                rudisha action, option_string, explicit_arg

        ikiwa self.allow_abbrev or not arg_string.startswith('--'):
            # search through all possible prefixes of the option string
            # and all actions in the parser for possible interpretations
            option_tuples = self._get_option_tuples(arg_string)

            # ikiwa multiple actions match, the option string was ambiguous
            ikiwa len(option_tuples) > 1:
                options = ', '.join([option_string
                    for action, option_string, explicit_arg in option_tuples])
                args = {'option': arg_string, 'matches': options}
                msg = _('ambiguous option: %(option)s could match %(matches)s')
                self.error(msg % args)

            # ikiwa exactly one action matched, this segmentation is good,
            # so rudisha the parsed action
            elikiwa len(option_tuples) == 1:
                option_tuple, = option_tuples
                rudisha option_tuple

        # ikiwa it was not found as an option, but it looks like a negative
        # number, it was meant to be positional
        # unless there are negative-number-like options
        ikiwa self._negative_number_matcher.match(arg_string):
            ikiwa not self._has_negative_number_optionals:
                rudisha None

        # ikiwa it contains a space, it was meant to be a positional
        ikiwa ' ' in arg_string:
            rudisha None

        # it was meant to be an optional but there is no such option
        # in this parser (though it might be a valid option in a subparser)
        rudisha None, arg_string, None

    eleza _get_option_tuples(self, option_string):
        result = []

        # option strings starting with two prefix characters are only
        # split at the '='
        chars = self.prefix_chars
        ikiwa option_string[0] in chars and option_string[1] in chars:
            ikiwa '=' in option_string:
                option_prefix, explicit_arg = option_string.split('=', 1)
            else:
                option_prefix = option_string
                explicit_arg = None
            for option_string in self._option_string_actions:
                ikiwa option_string.startswith(option_prefix):
                    action = self._option_string_actions[option_string]
                    tup = action, option_string, explicit_arg
                    result.append(tup)

        # single character options can be concatenated with their arguments
        # but multiple character options always have to have their argument
        # separate
        elikiwa option_string[0] in chars and option_string[1] not in chars:
            option_prefix = option_string
            explicit_arg = None
            short_option_prefix = option_string[:2]
            short_explicit_arg = option_string[2:]

            for option_string in self._option_string_actions:
                ikiwa option_string == short_option_prefix:
                    action = self._option_string_actions[option_string]
                    tup = action, option_string, short_explicit_arg
                    result.append(tup)
                elikiwa option_string.startswith(option_prefix):
                    action = self._option_string_actions[option_string]
                    tup = action, option_string, explicit_arg
                    result.append(tup)

        # shouldn't ever get here
        else:
            self.error(_('unexpected option string: %s') % option_string)

        # rudisha the collected option tuples
        rudisha result

    eleza _get_nargs_pattern(self, action):
        # in all examples below, we have to allow for '--' args
        # which are represented as '-' in the pattern
        nargs = action.nargs

        # the default (None) is assumed to be a single argument
        ikiwa nargs is None:
            nargs_pattern = '(-*A-*)'

        # allow zero or one arguments
        elikiwa nargs == OPTIONAL:
            nargs_pattern = '(-*A?-*)'

        # allow zero or more arguments
        elikiwa nargs == ZERO_OR_MORE:
            nargs_pattern = '(-*[A-]*)'

        # allow one or more arguments
        elikiwa nargs == ONE_OR_MORE:
            nargs_pattern = '(-*A[A-]*)'

        # allow any number of options or arguments
        elikiwa nargs == REMAINDER:
            nargs_pattern = '([-AO]*)'

        # allow one argument followed by any number of options or arguments
        elikiwa nargs == PARSER:
            nargs_pattern = '(-*A[-AO]*)'

        # suppress action, like nargs=0
        elikiwa nargs == SUPPRESS:
            nargs_pattern = '(-*-*)'

        # all others should be integers
        else:
            nargs_pattern = '(-*%s-*)' % '-*'.join('A' * nargs)

        # ikiwa this is an optional action, -- is not allowed
        ikiwa action.option_strings:
            nargs_pattern = nargs_pattern.replace('-*', '')
            nargs_pattern = nargs_pattern.replace('-', '')

        # rudisha the pattern
        rudisha nargs_pattern

    # ========================
    # Alt command line argument parsing, allowing free intermix
    # ========================

    eleza parse_intermixed_args(self, args=None, namespace=None):
        args, argv = self.parse_known_intermixed_args(args, namespace)
        ikiwa argv:
            msg = _('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        rudisha args

    eleza parse_known_intermixed_args(self, args=None, namespace=None):
        # returns a namespace and list of extras
        #
        # positional can be freely intermixed with optionals.  optionals are
        # first parsed with all positional arguments deactivated.  The 'extras'
        # are then parsed.  If the parser definition is incompatible with the
        # intermixed assumptions (e.g. use of REMAINDER, subparsers) a
        # TypeError is raised.
        #
        # positionals are 'deactivated' by setting nargs and default to
        # SUPPRESS.  This blocks the addition of that positional to the
        # namespace

        positionals = self._get_positional_actions()
        a = [action for action in positionals
             ikiwa action.nargs in [PARSER, REMAINDER]]
        ikiwa a:
            raise TypeError('parse_intermixed_args: positional arg'
                            ' with nargs=%s'%a[0].nargs)

        ikiwa [action.dest for group in self._mutually_exclusive_groups
            for action in group._group_actions ikiwa action in positionals]:
            raise TypeError('parse_intermixed_args: positional in'
                            ' mutuallyExclusiveGroup')

        try:
            save_usage = self.usage
            try:
                ikiwa self.usage is None:
                    # capture the full usage for use in error messages
                    self.usage = self.format_usage()[7:]
                for action in positionals:
                    # deactivate positionals
                    action.save_nargs = action.nargs
                    # action.nargs = 0
                    action.nargs = SUPPRESS
                    action.save_default = action.default
                    action.default = SUPPRESS
                namespace, remaining_args = self.parse_known_args(args,
                                                                  namespace)
                for action in positionals:
                    # remove the empty positional values kutoka namespace
                    ikiwa (hasattr(namespace, action.dest)
                            and getattr(namespace, action.dest)==[]):
                        kutoka warnings agiza warn
                        warn('Do not expect %s in %s' % (action.dest, namespace))
                        delattr(namespace, action.dest)
            finally:
                # restore nargs and usage before exiting
                for action in positionals:
                    action.nargs = action.save_nargs
                    action.default = action.save_default
            optionals = self._get_optional_actions()
            try:
                # parse positionals.  optionals aren't normally required, but
                # they could be, so make sure they aren't.
                for action in optionals:
                    action.save_required = action.required
                    action.required = False
                for group in self._mutually_exclusive_groups:
                    group.save_required = group.required
                    group.required = False
                namespace, extras = self.parse_known_args(remaining_args,
                                                          namespace)
            finally:
                # restore parser values before exiting
                for action in optionals:
                    action.required = action.save_required
                for group in self._mutually_exclusive_groups:
                    group.required = group.save_required
        finally:
            self.usage = save_usage
        rudisha namespace, extras

    # ========================
    # Value conversion methods
    # ========================
    eleza _get_values(self, action, arg_strings):
        # for everything but PARSER, REMAINDER args, strip out first '--'
        ikiwa action.nargs not in [PARSER, REMAINDER]:
            try:
                arg_strings.remove('--')
            except ValueError:
                pass

        # optional argument produces a default when not present
        ikiwa not arg_strings and action.nargs == OPTIONAL:
            ikiwa action.option_strings:
                value = action.const
            else:
                value = action.default
            ikiwa isinstance(value, str):
                value = self._get_value(action, value)
                self._check_value(action, value)

        # when nargs='*' on a positional, ikiwa there were no command-line
        # args, use the default ikiwa it is anything other than None
        elikiwa (not arg_strings and action.nargs == ZERO_OR_MORE and
              not action.option_strings):
            ikiwa action.default is not None:
                value = action.default
            else:
                value = arg_strings
            self._check_value(action, value)

        # single argument or optional argument produces a single value
        elikiwa len(arg_strings) == 1 and action.nargs in [None, OPTIONAL]:
            arg_string, = arg_strings
            value = self._get_value(action, arg_string)
            self._check_value(action, value)

        # REMAINDER arguments convert all values, checking none
        elikiwa action.nargs == REMAINDER:
            value = [self._get_value(action, v) for v in arg_strings]

        # PARSER arguments convert all values, but check only the first
        elikiwa action.nargs == PARSER:
            value = [self._get_value(action, v) for v in arg_strings]
            self._check_value(action, value[0])

        # SUPPRESS argument does not put anything in the namespace
        elikiwa action.nargs == SUPPRESS:
            value = SUPPRESS

        # all other types of nargs produce a list
        else:
            value = [self._get_value(action, v) for v in arg_strings]
            for v in value:
                self._check_value(action, v)

        # rudisha the converted value
        rudisha value

    eleza _get_value(self, action, arg_string):
        type_func = self._registry_get('type', action.type, action.type)
        ikiwa not callable(type_func):
            msg = _('%r is not callable')
            raise ArgumentError(action, msg % type_func)

        # convert the value to the appropriate type
        try:
            result = type_func(arg_string)

        # ArgumentTypeErrors indicate errors
        except ArgumentTypeError:
            name = getattr(action.type, '__name__', repr(action.type))
            msg = str(_sys.exc_info()[1])
            raise ArgumentError(action, msg)

        # TypeErrors or ValueErrors also indicate errors
        except (TypeError, ValueError):
            name = getattr(action.type, '__name__', repr(action.type))
            args = {'type': name, 'value': arg_string}
            msg = _('invalid %(type)s value: %(value)r')
            raise ArgumentError(action, msg % args)

        # rudisha the converted value
        rudisha result

    eleza _check_value(self, action, value):
        # converted value must be one of the choices (ikiwa specified)
        ikiwa action.choices is not None and value not in action.choices:
            args = {'value': value,
                    'choices': ', '.join(map(repr, action.choices))}
            msg = _('invalid choice: %(value)r (choose kutoka %(choices)s)')
            raise ArgumentError(action, msg % args)

    # =======================
    # Help-formatting methods
    # =======================
    eleza format_usage(self):
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)
        rudisha formatter.format_help()

    eleza format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help kutoka format above
        rudisha formatter.format_help()

    eleza _get_formatter(self):
        rudisha self.formatter_class(prog=self.prog)

    # =====================
    # Help-printing methods
    # =====================
    eleza print_usage(self, file=None):
        ikiwa file is None:
            file = _sys.stdout
        self._print_message(self.format_usage(), file)

    eleza print_help(self, file=None):
        ikiwa file is None:
            file = _sys.stdout
        self._print_message(self.format_help(), file)

    eleza _print_message(self, message, file=None):
        ikiwa message:
            ikiwa file is None:
                file = _sys.stderr
            file.write(message)

    # ===============
    # Exiting methods
    # ===============
    eleza exit(self, status=0, message=None):
        ikiwa message:
            self._print_message(message, _sys.stderr)
        _sys.exit(status)

    eleza error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.

        If you override this in a subclass, it should not rudisha -- it
        should either exit or raise an exception.
        """
        self.print_usage(_sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
