"""Parser kila command line options.

This module helps scripts to parse the command line arguments in
sys.argv.  It supports the same conventions kama the Unix getopt()
function (including the special meanings of arguments of the form `-'
and `--').  Long options similar to those supported by GNU software
may be used kama well via an optional third argument.  This module
provides two functions na an exception:

getopt() -- Parse command line options
gnu_getopt() -- Like getopt(), but allow option na non-option arguments
to be intermixed.
GetoptError -- exception (class) ashiriad ukijumuisha 'opt' attribute, which ni the
option involved ukijumuisha the exception.
"""

# Long option support added by Lars Wirzenius <liw@iki.fi>.
#
# Gerrit Holl <gerrit@nl.linux.org> moved the string-based exceptions
# to class-based exceptions.
#
# Peter Åstrand <astrand@lysator.liu.se> added gnu_getopt().
#
# TODO kila gnu_getopt():
#
# - GNU getopt_long_only mechanism
# - allow the caller to specify ordering
# - RETURN_IN_ORDER option
# - GNU extension ukijumuisha '-' kama first character of option string
# - optional arguments, specified by double colons
# - an option string ukijumuisha a W followed by semicolon should
#   treat "-W foo" kama "--foo"

__all__ = ["GetoptError","error","getopt","gnu_getopt"]

agiza os
jaribu:
    kutoka gettext agiza gettext kama _
tatizo ImportError:
    # Bootstrapping Python: gettext's dependencies sio built yet
    eleza _(s): rudisha s

kundi GetoptError(Exception):
    opt = ''
    msg = ''
    eleza __init__(self, msg, opt=''):
        self.msg = msg
        self.opt = opt
        Exception.__init__(self, msg, opt)

    eleza __str__(self):
        rudisha self.msg

error = GetoptError # backward compatibility

eleza getopt(args, shortopts, longopts = []):
    """getopt(args, options[, long_options]) -> opts, args

    Parses command line options na parameter list.  args ni the
    argument list to be parsed, without the leading reference to the
    running program.  Typically, this means "sys.argv[1:]".  shortopts
    ni the string of option letters that the script wants to
    recognize, ukijumuisha options that require an argument followed by a
    colon (i.e., the same format that Unix getopt() uses).  If
    specified, longopts ni a list of strings ukijumuisha the names of the
    long options which should be supported.  The leading '--'
    characters should sio be included kwenye the option name.  Options
    which require an argument should be followed by an equal sign
    ('=').

    The rudisha value consists of two elements: the first ni a list of
    (option, value) pairs; the second ni the list of program arguments
    left after the option list was stripped (this ni a trailing slice
    of the first argument).  Each option-and-value pair rudishaed has
    the option kama its first element, prefixed ukijumuisha a hyphen (e.g.,
    '-x'), na the option argument kama its second element, ama an empty
    string ikiwa the option has no argument.  The options occur kwenye the
    list kwenye the same order kwenye which they were found, thus allowing
    multiple occurrences.  Long na short options may be mixed.

    """

    opts = []
    ikiwa type(longopts) == type(""):
        longopts = [longopts]
    isipokua:
        longopts = list(longopts)
    wakati args na args[0].startswith('-') na args[0] != '-':
        ikiwa args[0] == '--':
            args = args[1:]
            koma
        ikiwa args[0].startswith('--'):
            opts, args = do_longs(opts, args[0][2:], longopts, args[1:])
        isipokua:
            opts, args = do_shorts(opts, args[0][1:], shortopts, args[1:])

    rudisha opts, args

eleza gnu_getopt(args, shortopts, longopts = []):
    """getopt(args, options[, long_options]) -> opts, args

    This function works like getopt(), tatizo that GNU style scanning
    mode ni used by default. This means that option na non-option
    arguments may be intermixed. The getopt() function stops
    processing options kama soon kama a non-option argument is
    encountered.

    If the first character of the option string ni `+', ama ikiwa the
    environment variable POSIXLY_CORRECT ni set, then option
    processing stops kama soon kama a non-option argument ni encountered.

    """

    opts = []
    prog_args = []
    ikiwa isinstance(longopts, str):
        longopts = [longopts]
    isipokua:
        longopts = list(longopts)

    # Allow options after non-option arguments?
    ikiwa shortopts.startswith('+'):
        shortopts = shortopts[1:]
        all_options_first = Kweli
    lasivyo os.environ.get("POSIXLY_CORRECT"):
        all_options_first = Kweli
    isipokua:
        all_options_first = Uongo

    wakati args:
        ikiwa args[0] == '--':
            prog_args += args[1:]
            koma

        ikiwa args[0][:2] == '--':
            opts, args = do_longs(opts, args[0][2:], longopts, args[1:])
        lasivyo args[0][:1] == '-' na args[0] != '-':
            opts, args = do_shorts(opts, args[0][1:], shortopts, args[1:])
        isipokua:
            ikiwa all_options_first:
                prog_args += args
                koma
            isipokua:
                prog_args.append(args[0])
                args = args[1:]

    rudisha opts, prog_args

eleza do_longs(opts, opt, longopts, args):
    jaribu:
        i = opt.index('=')
    tatizo ValueError:
        optarg = Tupu
    isipokua:
        opt, optarg = opt[:i], opt[i+1:]

    has_arg, opt = long_has_args(opt, longopts)
    ikiwa has_arg:
        ikiwa optarg ni Tupu:
            ikiwa sio args:
                ashiria GetoptError(_('option --%s requires argument') % opt, opt)
            optarg, args = args[0], args[1:]
    lasivyo optarg ni sio Tupu:
        ashiria GetoptError(_('option --%s must sio have an argument') % opt, opt)
    opts.append(('--' + opt, optarg ama ''))
    rudisha opts, args

# Return:
#   has_arg?
#   full option name
eleza long_has_args(opt, longopts):
    possibilities = [o kila o kwenye longopts ikiwa o.startswith(opt)]
    ikiwa sio possibilities:
        ashiria GetoptError(_('option --%s sio recognized') % opt, opt)
    # Is there an exact match?
    ikiwa opt kwenye possibilities:
        rudisha Uongo, opt
    lasivyo opt + '=' kwenye possibilities:
        rudisha Kweli, opt
    # No exact match, so better be unique.
    ikiwa len(possibilities) > 1:
        # XXX since possibilities contains all valid continuations, might be
        # nice to work them into the error msg
        ashiria GetoptError(_('option --%s sio a unique prefix') % opt, opt)
    assert len(possibilities) == 1
    unique_match = possibilities[0]
    has_arg = unique_match.endswith('=')
    ikiwa has_arg:
        unique_match = unique_match[:-1]
    rudisha has_arg, unique_match

eleza do_shorts(opts, optstring, shortopts, args):
    wakati optstring != '':
        opt, optstring = optstring[0], optstring[1:]
        ikiwa short_has_arg(opt, shortopts):
            ikiwa optstring == '':
                ikiwa sio args:
                    ashiria GetoptError(_('option -%s requires argument') % opt,
                                      opt)
                optstring, args = args[0], args[1:]
            optarg, optstring = optstring, ''
        isipokua:
            optarg = ''
        opts.append(('-' + opt, optarg))
    rudisha opts, args

eleza short_has_arg(opt, shortopts):
    kila i kwenye range(len(shortopts)):
        ikiwa opt == shortopts[i] != ':':
            rudisha shortopts.startswith(':', i+1)
    ashiria GetoptError(_('option -%s sio recognized') % opt, opt)

ikiwa __name__ == '__main__':
    agiza sys
    andika(getopt(sys.argv[1:], "a:b", ["alpha=", "beta"]))
