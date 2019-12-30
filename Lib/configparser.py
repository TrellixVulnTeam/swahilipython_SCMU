"""Configuration file parser.

A configuration file consists of sections, lead by a "[section]" header,
and followed by "name: value" entries, ukijumuisha continuations na such kwenye
the style of RFC 822.

Intrinsic defaults can be specified by pitaing them into the
ConfigParser constructor kama a dictionary.

class:

ConfigParser -- responsible kila parsing a list of
                    configuration files, na managing the parsed database.

    methods:

    __init__(defaults=Tupu, dict_type=_default_dict, allow_no_value=Uongo,
             delimiters=('=', ':'), comment_prefixes=('#', ';'),
             inline_comment_prefixes=Tupu, strict=Kweli,
             empty_lines_in_values=Kweli, default_section='DEFAULT',
             interpolation=<unset>, converters=<unset>):
        Create the parser. When `defaults' ni given, it ni initialized into the
        dictionary ama intrinsic defaults. The keys must be strings, the values
        must be appropriate kila %()s string interpolation.

        When `dict_type' ni given, it will be used to create the dictionary
        objects kila the list of sections, kila the options within a section, na
        kila the default values.

        When `delimiters' ni given, it will be used kama the set of substrings
        that divide keys kutoka values.

        When `comment_prefixes' ni given, it will be used kama the set of
        substrings that prefix comments kwenye empty lines. Comments can be
        indented.

        When `inline_comment_prefixes' ni given, it will be used kama the set of
        substrings that prefix comments kwenye non-empty lines.

        When `strict` ni Kweli, the parser won't allow kila any section ama option
        duplicates wakati reading kutoka a single source (file, string ama
        dictionary). Default ni Kweli.

        When `empty_lines_in_values' ni Uongo (default: Kweli), each empty line
        marks the end of an option. Otherwise, internal empty lines of
        a multiline option are kept kama part of the value.

        When `allow_no_value' ni Kweli (default: Uongo), options without
        values are accepted; the value presented kila these ni Tupu.

        When `default_section' ni given, the name of the special section is
        named accordingly. By default it ni called ``"DEFAULT"`` but this can
        be customized to point to any other valid section name. Its current
        value can be retrieved using the ``parser_instance.default_section``
        attribute na may be modified at runtime.

        When `interpolation` ni given, it should be an Interpolation subclass
        instance. It will be used kama the handler kila option value
        pre-processing when using getters. RawConfigParser objects don't do
        any sort of interpolation, whereas ConfigParser uses an instance of
        BasicInterpolation. The library also provides a ``zc.buildbot``
        inspired ExtendedInterpolation implementation.

        When `converters` ni given, it should be a dictionary where each key
        represents the name of a type converter na each value ni a callable
        implementing the conversion kutoka string to the desired datatype. Every
        converter gets its corresponding get*() method on the parser object na
        section proxies.

    sections()
        Return all the configuration section names, sans DEFAULT.

    has_section(section)
        Return whether the given section exists.

    has_option(section, option)
        Return whether the given option exists kwenye the given section.

    options(section)
        Return list of configuration options kila the named section.

    read(filenames, encoding=Tupu)
        Read na parse the iterable of named configuration files, given by
        name.  A single filename ni also allowed.  Non-existing files
        are ignored.  Return list of successfully read files.

    read_file(f, filename=Tupu)
        Read na parse one configuration file, given kama a file object.
        The filename defaults to f.name; it ni only used kwenye error
        messages (ikiwa f has no `name' attribute, the string `<???>' ni used).

    read_string(string)
        Read configuration kutoka a given string.

    read_dict(dictionary)
        Read configuration kutoka a dictionary. Keys are section names,
        values are dictionaries ukijumuisha keys na values that should be present
        kwenye the section. If the used dictionary type preserves order, sections
        na their keys will be added kwenye order. Values are automatically
        converted to strings.

    get(section, option, raw=Uongo, vars=Tupu, fallback=_UNSET)
        Return a string value kila the named option.  All % interpolations are
        expanded kwenye the rudisha values, based on the defaults pitaed into the
        constructor na the DEFAULT section.  Additional substitutions may be
        provided using the `vars' argument, which must be a dictionary whose
        contents override any pre-existing defaults. If `option' ni a key kwenye
        `vars', the value kutoka `vars' ni used.

    getint(section, options, raw=Uongo, vars=Tupu, fallback=_UNSET)
        Like get(), but convert value to an integer.

    getfloat(section, options, raw=Uongo, vars=Tupu, fallback=_UNSET)
        Like get(), but convert value to a float.

    getboolean(section, options, raw=Uongo, vars=Tupu, fallback=_UNSET)
        Like get(), but convert value to a boolean (currently case
        insensitively defined kama 0, false, no, off kila Uongo, na 1, true,
        yes, on kila Kweli).  Returns Uongo ama Kweli.

    items(section=_UNSET, raw=Uongo, vars=Tupu)
        If section ni given, rudisha a list of tuples ukijumuisha (name, value) for
        each option kwenye the section. Otherwise, rudisha a list of tuples with
        (section_name, section_proxy) kila each section, including DEFAULTSECT.

    remove_section(section)
        Remove the given file section na all its options.

    remove_option(section, option)
        Remove the given option kutoka the given section.

    set(section, option, value)
        Set the given option.

    write(fp, space_around_delimiters=Kweli)
        Write the configuration state kwenye .ini format. If
        `space_around_delimiters' ni Kweli (the default), delimiters
        between keys na values are surrounded by spaces.
"""

kutoka collections.abc agiza MutableMapping
kutoka collections agiza ChainMap kama _ChainMap
agiza functools
agiza io
agiza itertools
agiza os
agiza re
agiza sys
agiza warnings

__all__ = ["NoSectionError", "DuplicateOptionError", "DuplicateSectionError",
           "NoOptionError", "InterpolationError", "InterpolationDepthError",
           "InterpolationMissingOptionError", "InterpolationSyntaxError",
           "ParsingError", "MissingSectionHeaderError",
           "ConfigParser", "SafeConfigParser", "RawConfigParser",
           "Interpolation", "BasicInterpolation",  "ExtendedInterpolation",
           "LegacyInterpolation", "SectionProxy", "ConverterMapping",
           "DEFAULTSECT", "MAX_INTERPOLATION_DEPTH"]

_default_dict = dict
DEFAULTSECT = "DEFAULT"

MAX_INTERPOLATION_DEPTH = 10



# exception classes
kundi Error(Exception):
    """Base kundi kila ConfigParser exceptions."""

    eleza __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    eleza __repr__(self):
        rudisha self.message

    __str__ = __repr__


kundi NoSectionError(Error):
    """Raised when no section matches a requested option."""

    eleza __init__(self, section):
        Error.__init__(self, 'No section: %r' % (section,))
        self.section = section
        self.args = (section, )


kundi DuplicateSectionError(Error):
    """Raised when a section ni repeated kwenye an input source.

    Possible repetitions that ashiria this exception are: multiple creation
    using the API ama kwenye strict parsers when a section ni found more than once
    kwenye a single input file, string ama dictionary.
    """

    eleza __init__(self, section, source=Tupu, lineno=Tupu):
        msg = [repr(section), " already exists"]
        ikiwa source ni sio Tupu:
            message = ["While reading kutoka ", repr(source)]
            ikiwa lineno ni sio Tupu:
                message.append(" [line {0:2d}]".format(lineno))
            message.append(": section ")
            message.extend(msg)
            msg = message
        isipokua:
            msg.insert(0, "Section ")
        Error.__init__(self, "".join(msg))
        self.section = section
        self.source = source
        self.lineno = lineno
        self.args = (section, source, lineno)


kundi DuplicateOptionError(Error):
    """Raised by strict parsers when an option ni repeated kwenye an input source.

    Current implementation raises this exception only when an option ni found
    more than once kwenye a single file, string ama dictionary.
    """

    eleza __init__(self, section, option, source=Tupu, lineno=Tupu):
        msg = [repr(option), " kwenye section ", repr(section),
               " already exists"]
        ikiwa source ni sio Tupu:
            message = ["While reading kutoka ", repr(source)]
            ikiwa lineno ni sio Tupu:
                message.append(" [line {0:2d}]".format(lineno))
            message.append(": option ")
            message.extend(msg)
            msg = message
        isipokua:
            msg.insert(0, "Option ")
        Error.__init__(self, "".join(msg))
        self.section = section
        self.option = option
        self.source = source
        self.lineno = lineno
        self.args = (section, option, source, lineno)


kundi NoOptionError(Error):
    """A requested option was sio found."""

    eleza __init__(self, option, section):
        Error.__init__(self, "No option %r kwenye section: %r" %
                       (option, section))
        self.option = option
        self.section = section
        self.args = (option, section)


kundi InterpolationError(Error):
    """Base kundi kila interpolation-related exceptions."""

    eleza __init__(self, option, section, msg):
        Error.__init__(self, msg)
        self.option = option
        self.section = section
        self.args = (option, section, msg)


kundi InterpolationMissingOptionError(InterpolationError):
    """A string substitution required a setting which was sio available."""

    eleza __init__(self, option, section, rawval, reference):
        msg = ("Bad value substitution: option {!r} kwenye section {!r} contains "
               "an interpolation key {!r} which ni sio a valid option name. "
               "Raw value: {!r}".format(option, section, reference, rawval))
        InterpolationError.__init__(self, option, section, msg)
        self.reference = reference
        self.args = (option, section, rawval, reference)


kundi InterpolationSyntaxError(InterpolationError):
    """Raised when the source text contains invalid syntax.

    Current implementation raises this exception when the source text into
    which substitutions are made does sio conform to the required syntax.
    """


kundi InterpolationDepthError(InterpolationError):
    """Raised when substitutions are nested too deeply."""

    eleza __init__(self, option, section, rawval):
        msg = ("Recursion limit exceeded kwenye value substitution: option {!r} "
               "in section {!r} contains an interpolation key which "
               "cansio be substituted kwenye {} steps. Raw value: {!r}"
               "".format(option, section, MAX_INTERPOLATION_DEPTH,
                         rawval))
        InterpolationError.__init__(self, option, section, msg)
        self.args = (option, section, rawval)


kundi ParsingError(Error):
    """Raised when a configuration file does sio follow legal syntax."""

    eleza __init__(self, source=Tupu, filename=Tupu):
        # Exactly one of `source'/`filename' arguments has to be given.
        # `filename' kept kila compatibility.
        ikiwa filename na source:
            ashiria ValueError("Cansio specify both `filename' na `source'. "
                             "Use `source'.")
        lasivyo sio filename na sio source:
            ashiria ValueError("Required argument `source' sio given.")
        lasivyo filename:
            source = filename
        Error.__init__(self, 'Source contains parsing errors: %r' % source)
        self.source = source
        self.errors = []
        self.args = (source, )

    @property
    eleza filename(self):
        """Deprecated, use `source'."""
        warnings.warn(
            "The 'filename' attribute will be removed kwenye future versions.  "
            "Use 'source' instead.",
            DeprecationWarning, stacklevel=2
        )
        rudisha self.source

    @filename.setter
    eleza filename(self, value):
        """Deprecated, user `source'."""
        warnings.warn(
            "The 'filename' attribute will be removed kwenye future versions.  "
            "Use 'source' instead.",
            DeprecationWarning, stacklevel=2
        )
        self.source = value

    eleza append(self, lineno, line):
        self.errors.append((lineno, line))
        self.message += '\n\t[line %2d]: %s' % (lineno, line)


kundi MissingSectionHeaderError(ParsingError):
    """Raised when a key-value pair ni found before any section header."""

    eleza __init__(self, filename, lineno, line):
        Error.__init__(
            self,
            'File contains no section headers.\nfile: %r, line: %d\n%r' %
            (filename, lineno, line))
        self.source = filename
        self.lineno = lineno
        self.line = line
        self.args = (filename, lineno, line)


# Used kwenye parser getters to indicate the default behaviour when a specific
# option ni sio found it to ashiria an exception. Created to enable `Tupu' as
# a valid fallback value.
_UNSET = object()


kundi Interpolation:
    """Dummy interpolation that pitaes the value through ukijumuisha no changes."""

    eleza before_get(self, parser, section, option, value, defaults):
        rudisha value

    eleza before_set(self, parser, section, option, value):
        rudisha value

    eleza before_read(self, parser, section, option, value):
        rudisha value

    eleza before_write(self, parser, section, option, value):
        rudisha value


kundi BasicInterpolation(Interpolation):
    """Interpolation kama implemented kwenye the classic ConfigParser.

    The option values can contain format strings which refer to other values kwenye
    the same section, ama values kwenye the special default section.

    For example:

        something: %(dir)s/whatever

    would resolve the "%(dir)s" to the value of dir.  All reference
    expansions are done late, on demand. If a user needs to use a bare % kwenye
    a configuration file, she can escape it by writing %%. Other % usage
    ni considered a user error na raises `InterpolationSyntaxError'."""

    _KEYCRE = re.compile(r"%\(([^)]+)\)s")

    eleza before_get(self, parser, section, option, value, defaults):
        L = []
        self._interpolate_some(parser, option, L, value, section, defaults, 1)
        rudisha ''.join(L)

    eleza before_set(self, parser, section, option, value):
        tmp_value = value.replace('%%', '') # escaped percent signs
        tmp_value = self._KEYCRE.sub('', tmp_value) # valid syntax
        ikiwa '%' kwenye tmp_value:
            ashiria ValueError("invalid interpolation syntax kwenye %r at "
                             "position %d" % (value, tmp_value.find('%')))
        rudisha value

    eleza _interpolate_some(self, parser, option, accum, rest, section, map,
                          depth):
        rawval = parser.get(section, option, raw=Kweli, fallback=rest)
        ikiwa depth > MAX_INTERPOLATION_DEPTH:
            ashiria InterpolationDepthError(option, section, rawval)
        wakati rest:
            p = rest.find("%")
            ikiwa p < 0:
                accum.append(rest)
                rudisha
            ikiwa p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p ni no longer used
            c = rest[1:2]
            ikiwa c == "%":
                accum.append("%")
                rest = rest[2:]
            lasivyo c == "(":
                m = self._KEYCRE.match(rest)
                ikiwa m ni Tupu:
                    ashiria InterpolationSyntaxError(option, section,
                        "bad interpolation variable reference %r" % rest)
                var = parser.optionxform(m.group(1))
                rest = rest[m.end():]
                jaribu:
                    v = map[var]
                tatizo KeyError:
                    ashiria InterpolationMissingOptionError(
                        option, section, rawval, var) kutoka Tupu
                ikiwa "%" kwenye v:
                    self._interpolate_some(parser, option, accum, v,
                                           section, map, depth + 1)
                isipokua:
                    accum.append(v)
            isipokua:
                ashiria InterpolationSyntaxError(
                    option, section,
                    "'%%' must be followed by '%%' ama '(', "
                    "found: %r" % (rest,))


kundi ExtendedInterpolation(Interpolation):
    """Advanced variant of interpolation, supports the syntax used by
    `zc.buildout'. Enables interpolation between sections."""

    _KEYCRE = re.compile(r"\$\{([^}]+)\}")

    eleza before_get(self, parser, section, option, value, defaults):
        L = []
        self._interpolate_some(parser, option, L, value, section, defaults, 1)
        rudisha ''.join(L)

    eleza before_set(self, parser, section, option, value):
        tmp_value = value.replace('$$', '') # escaped dollar signs
        tmp_value = self._KEYCRE.sub('', tmp_value) # valid syntax
        ikiwa '$' kwenye tmp_value:
            ashiria ValueError("invalid interpolation syntax kwenye %r at "
                             "position %d" % (value, tmp_value.find('$')))
        rudisha value

    eleza _interpolate_some(self, parser, option, accum, rest, section, map,
                          depth):
        rawval = parser.get(section, option, raw=Kweli, fallback=rest)
        ikiwa depth > MAX_INTERPOLATION_DEPTH:
            ashiria InterpolationDepthError(option, section, rawval)
        wakati rest:
            p = rest.find("$")
            ikiwa p < 0:
                accum.append(rest)
                rudisha
            ikiwa p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p ni no longer used
            c = rest[1:2]
            ikiwa c == "$":
                accum.append("$")
                rest = rest[2:]
            lasivyo c == "{":
                m = self._KEYCRE.match(rest)
                ikiwa m ni Tupu:
                    ashiria InterpolationSyntaxError(option, section,
                        "bad interpolation variable reference %r" % rest)
                path = m.group(1).split(':')
                rest = rest[m.end():]
                sect = section
                opt = option
                jaribu:
                    ikiwa len(path) == 1:
                        opt = parser.optionxform(path[0])
                        v = map[opt]
                    lasivyo len(path) == 2:
                        sect = path[0]
                        opt = parser.optionxform(path[1])
                        v = parser.get(sect, opt, raw=Kweli)
                    isipokua:
                        ashiria InterpolationSyntaxError(
                            option, section,
                            "More than one ':' found: %r" % (rest,))
                tatizo (KeyError, NoSectionError, NoOptionError):
                    ashiria InterpolationMissingOptionError(
                        option, section, rawval, ":".join(path)) kutoka Tupu
                ikiwa "$" kwenye v:
                    self._interpolate_some(parser, opt, accum, v, sect,
                                           dict(parser.items(sect, raw=Kweli)),
                                           depth + 1)
                isipokua:
                    accum.append(v)
            isipokua:
                ashiria InterpolationSyntaxError(
                    option, section,
                    "'$' must be followed by '$' ama '{', "
                    "found: %r" % (rest,))


kundi LegacyInterpolation(Interpolation):
    """Deprecated interpolation used kwenye old versions of ConfigParser.
    Use BasicInterpolation ama ExtendedInterpolation instead."""

    _KEYCRE = re.compile(r"%\(([^)]*)\)s|.")

    eleza before_get(self, parser, section, option, value, vars):
        rawval = value
        depth = MAX_INTERPOLATION_DEPTH
        wakati depth:                    # Loop through this until it's done
            depth -= 1
            ikiwa value na "%(" kwenye value:
                replace = functools.partial(self._interpolation_replace,
                                            parser=parser)
                value = self._KEYCRE.sub(replace, value)
                jaribu:
                    value = value % vars
                tatizo KeyError kama e:
                    ashiria InterpolationMissingOptionError(
                        option, section, rawval, e.args[0]) kutoka Tupu
            isipokua:
                koma
        ikiwa value na "%(" kwenye value:
            ashiria InterpolationDepthError(option, section, rawval)
        rudisha value

    eleza before_set(self, parser, section, option, value):
        rudisha value

    @staticmethod
    eleza _interpolation_replace(match, parser):
        s = match.group(1)
        ikiwa s ni Tupu:
            rudisha match.group()
        isipokua:
            rudisha "%%(%s)s" % parser.optionxform(s)


kundi RawConfigParser(MutableMapping):
    """ConfigParser that does sio do interpolation."""

    # Regular expressions kila parsing section headers na options
    _SECT_TMPL = r"""
        \[                                 # [
        (?P<header>[^]]+)                  # very permissive!
        \]                                 # ]
        """
    _OPT_TMPL = r"""
        (?P<option>.*?)                    # very permissive!
        \s*(?P<vi>{delim})\s*              # any number of space/tab,
                                           # followed by any of the
                                           # allowed delimiters,
                                           # followed by any space/tab
        (?P<value>.*)$                     # everything up to eol
        """
    _OPT_NV_TMPL = r"""
        (?P<option>.*?)                    # very permissive!
        \s*(?:                             # any number of space/tab,
        (?P<vi>{delim})\s*                 # optionally followed by
                                           # any of the allowed
                                           # delimiters, followed by any
                                           # space/tab
        (?P<value>.*))?$                   # everything up to eol
        """
    # Interpolation algorithm to be used ikiwa the user does sio specify another
    _DEFAULT_INTERPOLATION = Interpolation()
    # Compiled regular expression kila matching sections
    SECTCRE = re.compile(_SECT_TMPL, re.VERBOSE)
    # Compiled regular expression kila matching options ukijumuisha typical separators
    OPTCRE = re.compile(_OPT_TMPL.format(delim="=|:"), re.VERBOSE)
    # Compiled regular expression kila matching options ukijumuisha optional values
    # delimited using typical separators
    OPTCRE_NV = re.compile(_OPT_NV_TMPL.format(delim="=|:"), re.VERBOSE)
    # Compiled regular expression kila matching leading whitespace kwenye a line
    NONSPACECRE = re.compile(r"\S")
    # Possible boolean values kwenye the configuration.
    BOOLEAN_STATES = {'1': Kweli, 'yes': Kweli, 'true': Kweli, 'on': Kweli,
                      '0': Uongo, 'no': Uongo, 'false': Uongo, 'off': Uongo}

    eleza __init__(self, defaults=Tupu, dict_type=_default_dict,
                 allow_no_value=Uongo, *, delimiters=('=', ':'),
                 comment_prefixes=('#', ';'), inline_comment_prefixes=Tupu,
                 strict=Kweli, empty_lines_in_values=Kweli,
                 default_section=DEFAULTSECT,
                 interpolation=_UNSET, converters=_UNSET):

        self._dict = dict_type
        self._sections = self._dict()
        self._defaults = self._dict()
        self._converters = ConverterMapping(self)
        self._proxies = self._dict()
        self._proxies[default_section] = SectionProxy(self, default_section)
        self._delimiters = tuple(delimiters)
        ikiwa delimiters == ('=', ':'):
            self._optcre = self.OPTCRE_NV ikiwa allow_no_value isipokua self.OPTCRE
        isipokua:
            d = "|".join(re.escape(d) kila d kwenye delimiters)
            ikiwa allow_no_value:
                self._optcre = re.compile(self._OPT_NV_TMPL.format(delim=d),
                                          re.VERBOSE)
            isipokua:
                self._optcre = re.compile(self._OPT_TMPL.format(delim=d),
                                          re.VERBOSE)
        self._comment_prefixes = tuple(comment_prefixes ama ())
        self._inline_comment_prefixes = tuple(inline_comment_prefixes ama ())
        self._strict = strict
        self._allow_no_value = allow_no_value
        self._empty_lines_in_values = empty_lines_in_values
        self.default_section=default_section
        self._interpolation = interpolation
        ikiwa self._interpolation ni _UNSET:
            self._interpolation = self._DEFAULT_INTERPOLATION
        ikiwa self._interpolation ni Tupu:
            self._interpolation = Interpolation()
        ikiwa converters ni sio _UNSET:
            self._converters.update(converters)
        ikiwa defaults:
            self._read_defaults(defaults)

    eleza defaults(self):
        rudisha self._defaults

    eleza sections(self):
        """Return a list of section names, excluding [DEFAULT]"""
        # self._sections will never have [DEFAULT] kwenye it
        rudisha list(self._sections.keys())

    eleza add_section(self, section):
        """Create a new section kwenye the configuration.

        Raise DuplicateSectionError ikiwa a section by the specified name
        already exists. Raise ValueError ikiwa name ni DEFAULT.
        """
        ikiwa section == self.default_section:
            ashiria ValueError('Invalid section name: %r' % section)

        ikiwa section kwenye self._sections:
            ashiria DuplicateSectionError(section)
        self._sections[section] = self._dict()
        self._proxies[section] = SectionProxy(self, section)

    eleza has_section(self, section):
        """Indicate whether the named section ni present kwenye the configuration.

        The DEFAULT section ni sio acknowledged.
        """
        rudisha section kwenye self._sections

    eleza options(self, section):
        """Return a list of option names kila the given section name."""
        jaribu:
            opts = self._sections[section].copy()
        tatizo KeyError:
            ashiria NoSectionError(section) kutoka Tupu
        opts.update(self._defaults)
        rudisha list(opts.keys())

    eleza read(self, filenames, encoding=Tupu):
        """Read na parse a filename ama an iterable of filenames.

        Files that cansio be opened are silently ignored; this is
        designed so that you can specify an iterable of potential
        configuration file locations (e.g. current directory, user's
        home directory, systemwide directory), na all existing
        configuration files kwenye the iterable will be read.  A single
        filename may also be given.

        Return list of successfully read files.
        """
        ikiwa isinstance(filenames, (str, bytes, os.PathLike)):
            filenames = [filenames]
        read_ok = []
        kila filename kwenye filenames:
            jaribu:
                ukijumuisha open(filename, encoding=encoding) kama fp:
                    self._read(fp, filename)
            tatizo OSError:
                endelea
            ikiwa isinstance(filename, os.PathLike):
                filename = os.fspath(filename)
            read_ok.append(filename)
        rudisha read_ok

    eleza read_file(self, f, source=Tupu):
        """Like read() but the argument must be a file-like object.

        The `f' argument must be iterable, returning one line at a time.
        Optional second argument ni the `source' specifying the name of the
        file being read. If sio given, it ni taken kutoka f.name. If `f' has no
        `name' attribute, `<???>' ni used.
        """
        ikiwa source ni Tupu:
            jaribu:
                source = f.name
            tatizo AttributeError:
                source = '<???>'
        self._read(f, source)

    eleza read_string(self, string, source='<string>'):
        """Read configuration kutoka a given string."""
        sfile = io.StringIO(string)
        self.read_file(sfile, source)

    eleza read_dict(self, dictionary, source='<dict>'):
        """Read configuration kutoka a dictionary.

        Keys are section names, values are dictionaries ukijumuisha keys na values
        that should be present kwenye the section. If the used dictionary type
        preserves order, sections na their keys will be added kwenye order.

        All types held kwenye the dictionary are converted to strings during
        reading, including section names, option names na keys.

        Optional second argument ni the `source' specifying the name of the
        dictionary being read.
        """
        elements_added = set()
        kila section, keys kwenye dictionary.items():
            section = str(section)
            jaribu:
                self.add_section(section)
            tatizo (DuplicateSectionError, ValueError):
                ikiwa self._strict na section kwenye elements_added:
                    raise
            elements_added.add(section)
            kila key, value kwenye keys.items():
                key = self.optionxform(str(key))
                ikiwa value ni sio Tupu:
                    value = str(value)
                ikiwa self._strict na (section, key) kwenye elements_added:
                    ashiria DuplicateOptionError(section, key, source)
                elements_added.add((section, key))
                self.set(section, key, value)

    eleza readfp(self, fp, filename=Tupu):
        """Deprecated, use read_file instead."""
        warnings.warn(
            "This method will be removed kwenye future versions.  "
            "Use 'parser.read_file()' instead.",
            DeprecationWarning, stacklevel=2
        )
        self.read_file(fp, source=filename)

    eleza get(self, section, option, *, raw=Uongo, vars=Tupu, fallback=_UNSET):
        """Get an option value kila a given section.

        If `vars' ni provided, it must be a dictionary. The option ni looked up
        kwenye `vars' (ikiwa provided), `section', na kwenye `DEFAULTSECT' kwenye that order.
        If the key ni sio found na `fallback' ni provided, it ni used as
        a fallback value. `Tupu' can be provided kama a `fallback' value.

        If interpolation ni enabled na the optional argument `raw' ni Uongo,
        all interpolations are expanded kwenye the rudisha values.

        Arguments `raw', `vars', na `fallback' are keyword only.

        The section DEFAULT ni special.
        """
        jaribu:
            d = self._unify_values(section, vars)
        tatizo NoSectionError:
            ikiwa fallback ni _UNSET:
                raise
            isipokua:
                rudisha fallback
        option = self.optionxform(option)
        jaribu:
            value = d[option]
        tatizo KeyError:
            ikiwa fallback ni _UNSET:
                ashiria NoOptionError(option, section)
            isipokua:
                rudisha fallback

        ikiwa raw ama value ni Tupu:
            rudisha value
        isipokua:
            rudisha self._interpolation.before_get(self, section, option, value,
                                                  d)

    eleza _get(self, section, conv, option, **kwargs):
        rudisha conv(self.get(section, option, **kwargs))

    eleza _get_conv(self, section, option, conv, *, raw=Uongo, vars=Tupu,
                  fallback=_UNSET, **kwargs):
        jaribu:
            rudisha self._get(section, conv, option, raw=raw, vars=vars,
                             **kwargs)
        tatizo (NoSectionError, NoOptionError):
            ikiwa fallback ni _UNSET:
                raise
            rudisha fallback

    # getint, getfloat na getboolean provided directly kila backwards compat
    eleza getint(self, section, option, *, raw=Uongo, vars=Tupu,
               fallback=_UNSET, **kwargs):
        rudisha self._get_conv(section, option, int, raw=raw, vars=vars,
                              fallback=fallback, **kwargs)

    eleza getfloat(self, section, option, *, raw=Uongo, vars=Tupu,
                 fallback=_UNSET, **kwargs):
        rudisha self._get_conv(section, option, float, raw=raw, vars=vars,
                              fallback=fallback, **kwargs)

    eleza getboolean(self, section, option, *, raw=Uongo, vars=Tupu,
                   fallback=_UNSET, **kwargs):
        rudisha self._get_conv(section, option, self._convert_to_boolean,
                              raw=raw, vars=vars, fallback=fallback, **kwargs)

    eleza items(self, section=_UNSET, raw=Uongo, vars=Tupu):
        """Return a list of (name, value) tuples kila each option kwenye a section.

        All % interpolations are expanded kwenye the rudisha values, based on the
        defaults pitaed into the constructor, unless the optional argument
        `raw' ni true.  Additional substitutions may be provided using the
        `vars' argument, which must be a dictionary whose contents overrides
        any pre-existing defaults.

        The section DEFAULT ni special.
        """
        ikiwa section ni _UNSET:
            rudisha super().items()
        d = self._defaults.copy()
        jaribu:
            d.update(self._sections[section])
        tatizo KeyError:
            ikiwa section != self.default_section:
                ashiria NoSectionError(section)
        orig_keys = list(d.keys())
        # Update ukijumuisha the entry specific variables
        ikiwa vars:
            kila key, value kwenye vars.items():
                d[self.optionxform(key)] = value
        value_getter = lambda option: self._interpolation.before_get(self,
            section, option, d[option], d)
        ikiwa raw:
            value_getter = lambda option: d[option]
        rudisha [(option, value_getter(option)) kila option kwenye orig_keys]

    eleza popitem(self):
        """Remove a section kutoka the parser na rudisha it as
        a (section_name, section_proxy) tuple. If no section ni present, raise
        KeyError.

        The section DEFAULT ni never returned because it cansio be removed.
        """
        kila key kwenye self.sections():
            value = self[key]
            toa self[key]
            rudisha key, value
        ashiria KeyError

    eleza optionxform(self, optionstr):
        rudisha optionstr.lower()

    eleza has_option(self, section, option):
        """Check kila the existence of a given option kwenye a given section.
        If the specified `section' ni Tupu ama an empty string, DEFAULT is
        assumed. If the specified `section' does sio exist, returns Uongo."""
        ikiwa sio section ama section == self.default_section:
            option = self.optionxform(option)
            rudisha option kwenye self._defaults
        lasivyo section haiko kwenye self._sections:
            rudisha Uongo
        isipokua:
            option = self.optionxform(option)
            rudisha (option kwenye self._sections[section]
                    ama option kwenye self._defaults)

    eleza set(self, section, option, value=Tupu):
        """Set an option."""
        ikiwa value:
            value = self._interpolation.before_set(self, section, option,
                                                   value)
        ikiwa sio section ama section == self.default_section:
            sectdict = self._defaults
        isipokua:
            jaribu:
                sectdict = self._sections[section]
            tatizo KeyError:
                ashiria NoSectionError(section) kutoka Tupu
        sectdict[self.optionxform(option)] = value

    eleza write(self, fp, space_around_delimiters=Kweli):
        """Write an .ini-format representation of the configuration state.

        If `space_around_delimiters' ni Kweli (the default), delimiters
        between keys na values are surrounded by spaces.
        """
        ikiwa space_around_delimiters:
            d = " {} ".format(self._delimiters[0])
        isipokua:
            d = self._delimiters[0]
        ikiwa self._defaults:
            self._write_section(fp, self.default_section,
                                    self._defaults.items(), d)
        kila section kwenye self._sections:
            self._write_section(fp, section,
                                self._sections[section].items(), d)

    eleza _write_section(self, fp, section_name, section_items, delimiter):
        """Write a single section to the specified `fp'."""
        fp.write("[{}]\n".format(section_name))
        kila key, value kwenye section_items:
            value = self._interpolation.before_write(self, section_name, key,
                                                     value)
            ikiwa value ni sio Tupu ama sio self._allow_no_value:
                value = delimiter + str(value).replace('\n', '\n\t')
            isipokua:
                value = ""
            fp.write("{}{}\n".format(key, value))
        fp.write("\n")

    eleza remove_option(self, section, option):
        """Remove an option."""
        ikiwa sio section ama section == self.default_section:
            sectdict = self._defaults
        isipokua:
            jaribu:
                sectdict = self._sections[section]
            tatizo KeyError:
                ashiria NoSectionError(section) kutoka Tupu
        option = self.optionxform(option)
        existed = option kwenye sectdict
        ikiwa existed:
            toa sectdict[option]
        rudisha existed

    eleza remove_section(self, section):
        """Remove a file section."""
        existed = section kwenye self._sections
        ikiwa existed:
            toa self._sections[section]
            toa self._proxies[section]
        rudisha existed

    eleza __getitem__(self, key):
        ikiwa key != self.default_section na sio self.has_section(key):
            ashiria KeyError(key)
        rudisha self._proxies[key]

    eleza __setitem__(self, key, value):
        # To conform ukijumuisha the mapping protocol, overwrites existing values kwenye
        # the section.
        ikiwa key kwenye self na self[key] ni value:
            rudisha
        # XXX this ni sio atomic ikiwa read_dict fails at any point. Then again,
        # no update method kwenye configparser ni atomic kwenye this implementation.
        ikiwa key == self.default_section:
            self._defaults.clear()
        lasivyo key kwenye self._sections:
            self._sections[key].clear()
        self.read_dict({key: value})

    eleza __delitem__(self, key):
        ikiwa key == self.default_section:
            ashiria ValueError("Cansio remove the default section.")
        ikiwa sio self.has_section(key):
            ashiria KeyError(key)
        self.remove_section(key)

    eleza __contains__(self, key):
        rudisha key == self.default_section ama self.has_section(key)

    eleza __len__(self):
        rudisha len(self._sections) + 1 # the default section

    eleza __iter__(self):
        # XXX does it koma when underlying container state changed?
        rudisha itertools.chain((self.default_section,), self._sections.keys())

    eleza _read(self, fp, fpname):
        """Parse a sectioned configuration file.

        Each section kwenye a configuration file contains a header, indicated by
        a name kwenye square brackets (`[]'), plus key/value options, indicated by
        `name' na `value' delimited ukijumuisha a specific substring (`=' ama `:' by
        default).

        Values can span multiple lines, kama long kama they are indented deeper
        than the first line of the value. Depending on the parser's mode, blank
        lines may be treated kama parts of multiline values ama ignored.

        Configuration files may include comments, prefixed by specific
        characters (`#' na `;' by default). Comments may appear on their own
        kwenye an otherwise empty line ama may be entered kwenye lines holding values ama
        section names.
        """
        elements_added = set()
        cursect = Tupu                        # Tupu, ama a dictionary
        sectname = Tupu
        optname = Tupu
        lineno = 0
        indent_level = 0
        e = Tupu                              # Tupu, ama an exception
        kila lineno, line kwenye enumerate(fp, start=1):
            comment_start = sys.maxsize
            # strip inline comments
            inline_prefixes = {p: -1 kila p kwenye self._inline_comment_prefixes}
            wakati comment_start == sys.maxsize na inline_prefixes:
                next_prefixes = {}
                kila prefix, index kwenye inline_prefixes.items():
                    index = line.find(prefix, index+1)
                    ikiwa index == -1:
                        endelea
                    next_prefixes[prefix] = index
                    ikiwa index == 0 ama (index > 0 na line[index-1].isspace()):
                        comment_start = min(comment_start, index)
                inline_prefixes = next_prefixes
            # strip full line comments
            kila prefix kwenye self._comment_prefixes:
                ikiwa line.strip().startswith(prefix):
                    comment_start = 0
                    koma
            ikiwa comment_start == sys.maxsize:
                comment_start = Tupu
            value = line[:comment_start].strip()
            ikiwa sio value:
                ikiwa self._empty_lines_in_values:
                    # add empty line to the value, but only ikiwa there was no
                    # comment on the line
                    ikiwa (comment_start ni Tupu na
                        cursect ni sio Tupu na
                        optname na
                        cursect[optname] ni sio Tupu):
                        cursect[optname].append('') # newlines added at join
                isipokua:
                    # empty line marks end of value
                    indent_level = sys.maxsize
                endelea
            # continuation line?
            first_nonspace = self.NONSPACECRE.search(line)
            cur_indent_level = first_nonspace.start() ikiwa first_nonspace isipokua 0
            ikiwa (cursect ni sio Tupu na optname na
                cur_indent_level > indent_level):
                cursect[optname].append(value)
            # a section header ama option header?
            isipokua:
                indent_level = cur_indent_level
                # ni it a section header?
                mo = self.SECTCRE.match(value)
                ikiwa mo:
                    sectname = mo.group('header')
                    ikiwa sectname kwenye self._sections:
                        ikiwa self._strict na sectname kwenye elements_added:
                            ashiria DuplicateSectionError(sectname, fpname,
                                                        lineno)
                        cursect = self._sections[sectname]
                        elements_added.add(sectname)
                    lasivyo sectname == self.default_section:
                        cursect = self._defaults
                    isipokua:
                        cursect = self._dict()
                        self._sections[sectname] = cursect
                        self._proxies[sectname] = SectionProxy(self, sectname)
                        elements_added.add(sectname)
                    # So sections can't start ukijumuisha a continuation line
                    optname = Tupu
                # no section header kwenye the file?
                lasivyo cursect ni Tupu:
                    ashiria MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                isipokua:
                    mo = self._optcre.match(value)
                    ikiwa mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        ikiwa sio optname:
                            e = self._handle_error(e, fpname, lineno, line)
                        optname = self.optionxform(optname.rstrip())
                        ikiwa (self._strict na
                            (sectname, optname) kwenye elements_added):
                            ashiria DuplicateOptionError(sectname, optname,
                                                       fpname, lineno)
                        elements_added.add((sectname, optname))
                        # This check ni fine because the OPTCRE cannot
                        # match ikiwa it would set optval to Tupu
                        ikiwa optval ni sio Tupu:
                            optval = optval.strip()
                            cursect[optname] = [optval]
                        isipokua:
                            # valueless option handling
                            cursect[optname] = Tupu
                    isipokua:
                        # a non-fatal parsing error occurred. set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file na will contain a
                        # list of all bogus lines
                        e = self._handle_error(e, fpname, lineno, line)
        self._join_multiline_values()
        # ikiwa any parsing errors occurred, ashiria an exception
        ikiwa e:
            ashiria e

    eleza _join_multiline_values(self):
        defaults = self.default_section, self._defaults
        all_sections = itertools.chain((defaults,),
                                       self._sections.items())
        kila section, options kwenye all_sections:
            kila name, val kwenye options.items():
                ikiwa isinstance(val, list):
                    val = '\n'.join(val).rstrip()
                options[name] = self._interpolation.before_read(self,
                                                                section,
                                                                name, val)

    eleza _read_defaults(self, defaults):
        """Read the defaults pitaed kwenye the initializer.
        Note: values can be non-string."""
        kila key, value kwenye defaults.items():
            self._defaults[self.optionxform(key)] = value

    eleza _handle_error(self, exc, fpname, lineno, line):
        ikiwa sio exc:
            exc = ParsingError(fpname)
        exc.append(lineno, repr(line))
        rudisha exc

    eleza _unify_values(self, section, vars):
        """Create a sequence of lookups ukijumuisha 'vars' taking priority over
        the 'section' which takes priority over the DEFAULTSECT.

        """
        sectiondict = {}
        jaribu:
            sectiondict = self._sections[section]
        tatizo KeyError:
            ikiwa section != self.default_section:
                ashiria NoSectionError(section) kutoka Tupu
        # Update ukijumuisha the entry specific variables
        vardict = {}
        ikiwa vars:
            kila key, value kwenye vars.items():
                ikiwa value ni sio Tupu:
                    value = str(value)
                vardict[self.optionxform(key)] = value
        rudisha _ChainMap(vardict, sectiondict, self._defaults)

    eleza _convert_to_boolean(self, value):
        """Return a boolean value translating kutoka other types ikiwa necessary.
        """
        ikiwa value.lower() haiko kwenye self.BOOLEAN_STATES:
            ashiria ValueError('Not a boolean: %s' % value)
        rudisha self.BOOLEAN_STATES[value.lower()]

    eleza _validate_value_types(self, *, section="", option="", value=""):
        """Raises a TypeError kila non-string values.

        The only legal non-string value ikiwa we allow valueless
        options ni Tupu, so we need to check ikiwa the value ni a
        string if:
        - we do sio allow valueless options, ama
        - we allow valueless options but the value ni sio Tupu

        For compatibility reasons this method ni sio used kwenye classic set()
        kila RawConfigParsers. It ni invoked kwenye every case kila mapping protocol
        access na kwenye ConfigParser.set().
        """
        ikiwa sio isinstance(section, str):
            ashiria TypeError("section names must be strings")
        ikiwa sio isinstance(option, str):
            ashiria TypeError("option keys must be strings")
        ikiwa sio self._allow_no_value ama value:
            ikiwa sio isinstance(value, str):
                ashiria TypeError("option values must be strings")

    @property
    eleza converters(self):
        rudisha self._converters


kundi ConfigParser(RawConfigParser):
    """ConfigParser implementing interpolation."""

    _DEFAULT_INTERPOLATION = BasicInterpolation()

    eleza set(self, section, option, value=Tupu):
        """Set an option.  Extends RawConfigParser.set by validating type na
        interpolation syntax on the value."""
        self._validate_value_types(option=option, value=value)
        super().set(section, option, value)

    eleza add_section(self, section):
        """Create a new section kwenye the configuration.  Extends
        RawConfigParser.add_section by validating ikiwa the section name is
        a string."""
        self._validate_value_types(section=section)
        super().add_section(section)

    eleza _read_defaults(self, defaults):
        """Reads the defaults pitaed kwenye the initializer, implicitly converting
        values to strings like the rest of the API.

        Does sio perform interpolation kila backwards compatibility.
        """
        jaribu:
            hold_interpolation = self._interpolation
            self._interpolation = Interpolation()
            self.read_dict({self.default_section: defaults})
        mwishowe:
            self._interpolation = hold_interpolation


kundi SafeConfigParser(ConfigParser):
    """ConfigParser alias kila backwards compatibility purposes."""

    eleza __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            "The SafeConfigParser kundi has been renamed to ConfigParser "
            "in Python 3.2. This alias will be removed kwenye future versions."
            " Use ConfigParser directly instead.",
            DeprecationWarning, stacklevel=2
        )


kundi SectionProxy(MutableMapping):
    """A proxy kila a single section kutoka a parser."""

    eleza __init__(self, parser, name):
        """Creates a view on a section of the specified `name` kwenye `parser`."""
        self._parser = parser
        self._name = name
        kila conv kwenye parser.converters:
            key = 'get' + conv
            getter = functools.partial(self.get, _impl=getattr(parser, key))
            setattr(self, key, getter)

    eleza __repr__(self):
        rudisha '<Section: {}>'.format(self._name)

    eleza __getitem__(self, key):
        ikiwa sio self._parser.has_option(self._name, key):
            ashiria KeyError(key)
        rudisha self._parser.get(self._name, key)

    eleza __setitem__(self, key, value):
        self._parser._validate_value_types(option=key, value=value)
        rudisha self._parser.set(self._name, key, value)

    eleza __delitem__(self, key):
        ikiwa sio (self._parser.has_option(self._name, key) na
                self._parser.remove_option(self._name, key)):
            ashiria KeyError(key)

    eleza __contains__(self, key):
        rudisha self._parser.has_option(self._name, key)

    eleza __len__(self):
        rudisha len(self._options())

    eleza __iter__(self):
        rudisha self._options().__iter__()

    eleza _options(self):
        ikiwa self._name != self._parser.default_section:
            rudisha self._parser.options(self._name)
        isipokua:
            rudisha self._parser.defaults()

    @property
    eleza parser(self):
        # The parser object of the proxy ni read-only.
        rudisha self._parser

    @property
    eleza name(self):
        # The name of the section on a proxy ni read-only.
        rudisha self._name

    eleza get(self, option, fallback=Tupu, *, raw=Uongo, vars=Tupu,
            _impl=Tupu, **kwargs):
        """Get an option value.

        Unless `fallback` ni provided, `Tupu` will be returned ikiwa the option
        ni sio found.

        """
        # If `_impl` ni provided, it should be a getter method on the parser
        # object that provides the desired type conversion.
        ikiwa sio _impl:
            _impl = self._parser.get
        rudisha _impl(self._name, option, raw=raw, vars=vars,
                     fallback=fallback, **kwargs)


kundi ConverterMapping(MutableMapping):
    """Enables reuse of get*() methods between the parser na section proxies.

    If a parser kundi implements a getter directly, the value kila the given
    key will be ``Tupu``. The presence of the converter name here enables
    section proxies to find na use the implementation on the parser class.
    """

    GETTERCRE = re.compile(r"^get(?P<name>.+)$")

    eleza __init__(self, parser):
        self._parser = parser
        self._data = {}
        kila getter kwenye dir(self._parser):
            m = self.GETTERCRE.match(getter)
            ikiwa sio m ama sio callable(getattr(self._parser, getter)):
                endelea
            self._data[m.group('name')] = Tupu   # See kundi docstring.

    eleza __getitem__(self, key):
        rudisha self._data[key]

    eleza __setitem__(self, key, value):
        jaribu:
            k = 'get' + key
        tatizo TypeError:
            ashiria ValueError('Incompatible key: {} (type: {})'
                             ''.format(key, type(key)))
        ikiwa k == 'get':
            ashiria ValueError('Incompatible key: cansio use "" kama a name')
        self._data[key] = value
        func = functools.partial(self._parser._get_conv, conv=value)
        func.converter = value
        setattr(self._parser, k, func)
        kila proxy kwenye self._parser.values():
            getter = functools.partial(proxy.get, _impl=func)
            setattr(proxy, k, getter)

    eleza __delitem__(self, key):
        jaribu:
            k = 'get' + (key ama Tupu)
        tatizo TypeError:
            ashiria KeyError(key)
        toa self._data[key]
        kila inst kwenye itertools.chain((self._parser,), self._parser.values()):
            jaribu:
                delattr(inst, k)
            tatizo AttributeError:
                # don't ashiria since the entry was present kwenye _data, silently
                # clean up
                endelea

    eleza __iter__(self):
        rudisha iter(self._data)

    eleza __len__(self):
        rudisha len(self._data)
