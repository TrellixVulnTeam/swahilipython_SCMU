"""Internationalization and localization support.

This module provides internationalization (I18N) and localization (L10N)
support for your Python programs by providing an interface to the GNU gettext
message catalog library.

I18N refers to the operation by which a program is made aware of multiple
languages.  L10N refers to the adaptation of your program, once
internationalized, to the local language and cultural habits.

"""

# This module represents the integration of work, contributions, feedback, and
# suggestions kutoka the following people:
#
# Martin von Loewis, who wrote the initial implementation of the underlying
# C-based libintlmodule (later renamed _gettext), along with a skeletal
# gettext.py implementation.
#
# Peter Funk, who wrote fintl.py, a fairly complete wrapper around intlmodule,
# which also included a pure-Python implementation to read .mo files if
# intlmodule wasn't available.
#
# James Henstridge, who also wrote a gettext.py module, which has some
# interesting, but currently unsupported experimental features: the notion of
# a Catalog kundi and instances, and the ability to add to a catalog file via
# a Python API.
#
# Barry Warsaw integrated these modules, wrote the .install() API and code,
# and conformed all C and Python code to Python's coding standards.
#
# Francois Pinard and Marc-Andre Lemburg also contributed valuably to this
# module.
#
# J. David Ibanez implemented plural forms. Bruno Haible fixed some bugs.
#
# TODO:
# - Lazy loading of .mo files.  Currently the entire catalog is loaded into
#   memory, but that's probably bad for large translated programs.  Instead,
#   the lexical sort of original strings in GNU .mo files should be exploited
#   to do binary searches and lazy initializations.  Or you might want to use
#   the undocumented double-hash algorithm for .mo files with hash tables, but
#   you'll need to study the GNU gettext code to do this.
#
# - Support Solaris .mo file formats.  Unfortunately, we've been unable to
#   find this format documented anywhere.


agiza locale
agiza os
agiza re
agiza sys


__all__ = ['NullTranslations', 'GNUTranslations', 'Catalog',
           'find', 'translation', 'install', 'textdomain', 'bindtextdomain',
           'bind_textdomain_codeset',
           'dgettext', 'dngettext', 'gettext', 'lgettext', 'ldgettext',
           'ldngettext', 'lngettext', 'ngettext',
           'pgettext', 'dpgettext', 'npgettext', 'dnpgettext',
           ]

_default_localedir = os.path.join(sys.base_prefix, 'share', 'locale')

# Expression parsing for plural form selection.
#
# The gettext library supports a small subset of C syntax.  The only
# incompatible difference is that integer literals starting with zero are
# decimal.
#
# https://www.gnu.org/software/gettext/manual/gettext.html#Plural-forms
# http://git.savannah.gnu.org/cgit/gettext.git/tree/gettext-runtime/intl/plural.y

_token_pattern = re.compile(r"""
        (?P<WHITESPACES>[ \t]+)                    | # spaces and horizontal tabs
        (?P<NUMBER>[0-9]+\b)                       | # decimal integer
        (?P<NAME>n\b)                              | # only n is allowed
        (?P<PARENTHESIS>[()])                      |
        (?P<OPERATOR>[-*/%+?:]|[><!]=?|==|&&|\|\|) | # !, *, /, %, +, -, <, >,
                                                     # <=, >=, ==, !=, &&, ||,
                                                     # ? :
                                                     # unary and bitwise ops
                                                     # not allowed
        (?P<INVALID>\w+|.)                           # invalid token
    """, re.VERBOSE|re.DOTALL)

eleza _tokenize(plural):
    for mo in re.finditer(_token_pattern, plural):
        kind = mo.lastgroup
        ikiwa kind == 'WHITESPACES':
            continue
        value = mo.group(kind)
        ikiwa kind == 'INVALID':
            raise ValueError('invalid token in plural form: %s' % value)
        yield value
    yield ''

eleza _error(value):
    ikiwa value:
        rudisha ValueError('unexpected token in plural form: %s' % value)
    else:
        rudisha ValueError('unexpected end of plural form')

_binary_ops = (
    ('||',),
    ('&&',),
    ('==', '!='),
    ('<', '>', '<=', '>='),
    ('+', '-'),
    ('*', '/', '%'),
)
_binary_ops = {op: i for i, ops in enumerate(_binary_ops, 1) for op in ops}
_c2py_ops = {'||': 'or', '&&': 'and', '/': '//'}

eleza _parse(tokens, priority=-1):
    result = ''
    nexttok = next(tokens)
    while nexttok == '!':
        result += 'not '
        nexttok = next(tokens)

    ikiwa nexttok == '(':
        sub, nexttok = _parse(tokens)
        result = '%s(%s)' % (result, sub)
        ikiwa nexttok != ')':
            raise ValueError('unbalanced parenthesis in plural form')
    elikiwa nexttok == 'n':
        result = '%s%s' % (result, nexttok)
    else:
        try:
            value = int(nexttok, 10)
        except ValueError:
            raise _error(nexttok) kutoka None
        result = '%s%d' % (result, value)
    nexttok = next(tokens)

    j = 100
    while nexttok in _binary_ops:
        i = _binary_ops[nexttok]
        ikiwa i < priority:
            break
        # Break chained comparisons
        ikiwa i in (3, 4) and j in (3, 4):  # '==', '!=', '<', '>', '<=', '>='
            result = '(%s)' % result
        # Replace some C operators by their Python equivalents
        op = _c2py_ops.get(nexttok, nexttok)
        right, nexttok = _parse(tokens, i + 1)
        result = '%s %s %s' % (result, op, right)
        j = i
    ikiwa j == priority == 4:  # '<', '>', '<=', '>='
        result = '(%s)' % result

    ikiwa nexttok == '?' and priority <= 0:
        if_true, nexttok = _parse(tokens, 0)
        ikiwa nexttok != ':':
            raise _error(nexttok)
        if_false, nexttok = _parse(tokens)
        result = '%s ikiwa %s else %s' % (if_true, result, if_false)
        ikiwa priority == 0:
            result = '(%s)' % result

    rudisha result, nexttok

eleza _as_int(n):
    try:
        i = round(n)
    except TypeError:
        raise TypeError('Plural value must be an integer, got %s' %
                        (n.__class__.__name__,)) kutoka None
    agiza warnings
    warnings.warn('Plural value must be an integer, got %s' %
                  (n.__class__.__name__,),
                  DeprecationWarning, 4)
    rudisha n

eleza c2py(plural):
    """Gets a C expression as used in PO files for plural forms and returns a
    Python function that implements an equivalent expression.
    """

    ikiwa len(plural) > 1000:
        raise ValueError('plural form expression is too long')
    try:
        result, nexttok = _parse(_tokenize(plural))
        ikiwa nexttok:
            raise _error(nexttok)

        depth = 0
        for c in result:
            ikiwa c == '(':
                depth += 1
                ikiwa depth > 20:
                    # Python compiler limit is about 90.
                    # The most complex example has 2.
                    raise ValueError('plural form expression is too complex')
            elikiwa c == ')':
                depth -= 1

        ns = {'_as_int': _as_int}
        exec('''ikiwa True:
            eleza func(n):
                ikiwa not isinstance(n, int):
                    n = _as_int(n)
                rudisha int(%s)
            ''' % result, ns)
        rudisha ns['func']
    except RecursionError:
        # Recursion error can be raised in _parse() or exec().
        raise ValueError('plural form expression is too complex')


eleza _expand_lang(loc):
    loc = locale.normalize(loc)
    COMPONENT_CODESET   = 1 << 0
    COMPONENT_TERRITORY = 1 << 1
    COMPONENT_MODIFIER  = 1 << 2
    # split up the locale into its base components
    mask = 0
    pos = loc.find('@')
    ikiwa pos >= 0:
        modifier = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_MODIFIER
    else:
        modifier = ''
    pos = loc.find('.')
    ikiwa pos >= 0:
        codeset = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_CODESET
    else:
        codeset = ''
    pos = loc.find('_')
    ikiwa pos >= 0:
        territory = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_TERRITORY
    else:
        territory = ''
    language = loc
    ret = []
    for i in range(mask+1):
        ikiwa not (i & ~mask):  # ikiwa all components for this combo exist ...
            val = language
            ikiwa i & COMPONENT_TERRITORY: val += territory
            ikiwa i & COMPONENT_CODESET:   val += codeset
            ikiwa i & COMPONENT_MODIFIER:  val += modifier
            ret.append(val)
    ret.reverse()
    rudisha ret



kundi NullTranslations:
    eleza __init__(self, fp=None):
        self._info = {}
        self._charset = None
        self._output_charset = None
        self._fallback = None
        ikiwa fp is not None:
            self._parse(fp)

    eleza _parse(self, fp):
        pass

    eleza add_fallback(self, fallback):
        ikiwa self._fallback:
            self._fallback.add_fallback(fallback)
        else:
            self._fallback = fallback

    eleza gettext(self, message):
        ikiwa self._fallback:
            rudisha self._fallback.gettext(message)
        rudisha message

    eleza lgettext(self, message):
        agiza warnings
        warnings.warn('lgettext() is deprecated, use gettext() instead',
                      DeprecationWarning, 2)
        ikiwa self._fallback:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', r'.*\blgettext\b.*',
                                        DeprecationWarning)
                rudisha self._fallback.lgettext(message)
        ikiwa self._output_charset:
            rudisha message.encode(self._output_charset)
        rudisha message.encode(locale.getpreferredencoding())

    eleza ngettext(self, msgid1, msgid2, n):
        ikiwa self._fallback:
            rudisha self._fallback.ngettext(msgid1, msgid2, n)
        ikiwa n == 1:
            rudisha msgid1
        else:
            rudisha msgid2

    eleza lngettext(self, msgid1, msgid2, n):
        agiza warnings
        warnings.warn('lngettext() is deprecated, use ngettext() instead',
                      DeprecationWarning, 2)
        ikiwa self._fallback:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', r'.*\blngettext\b.*',
                                        DeprecationWarning)
                rudisha self._fallback.lngettext(msgid1, msgid2, n)
        ikiwa n == 1:
            tmsg = msgid1
        else:
            tmsg = msgid2
        ikiwa self._output_charset:
            rudisha tmsg.encode(self._output_charset)
        rudisha tmsg.encode(locale.getpreferredencoding())

    eleza pgettext(self, context, message):
        ikiwa self._fallback:
            rudisha self._fallback.pgettext(context, message)
        rudisha message

    eleza npgettext(self, context, msgid1, msgid2, n):
        ikiwa self._fallback:
            rudisha self._fallback.npgettext(context, msgid1, msgid2, n)
        ikiwa n == 1:
            rudisha msgid1
        else:
            rudisha msgid2

    eleza info(self):
        rudisha self._info

    eleza charset(self):
        rudisha self._charset

    eleza output_charset(self):
        agiza warnings
        warnings.warn('output_charset() is deprecated',
                      DeprecationWarning, 2)
        rudisha self._output_charset

    eleza set_output_charset(self, charset):
        agiza warnings
        warnings.warn('set_output_charset() is deprecated',
                      DeprecationWarning, 2)
        self._output_charset = charset

    eleza install(self, names=None):
        agiza builtins
        builtins.__dict__['_'] = self.gettext
        ikiwa names is not None:
            allowed = {'gettext', 'lgettext', 'lngettext',
                       'ngettext', 'npgettext', 'pgettext'}
            for name in allowed & set(names):
                builtins.__dict__[name] = getattr(self, name)


kundi GNUTranslations(NullTranslations):
    # Magic number of .mo files
    LE_MAGIC = 0x950412de
    BE_MAGIC = 0xde120495

    # The encoding of a msgctxt and a msgid in a .mo file is
    # msgctxt + "\x04" + msgid (gettext version >= 0.15)
    CONTEXT = "%s\x04%s"

    # Acceptable .mo versions
    VERSIONS = (0, 1)

    eleza _get_versions(self, version):
        """Returns a tuple of major version, minor version"""
        rudisha (version >> 16, version & 0xffff)

    eleza _parse(self, fp):
        """Override this method to support alternative .mo formats."""
        # Delay struct agiza for speeding up gettext agiza when .mo files
        # are not used.
        kutoka struct agiza unpack
        filename = getattr(fp, 'name', '')
        # Parse the .mo file header, which consists of 5 little endian 32
        # bit words.
        self._catalog = catalog = {}
        self.plural = lambda n: int(n != 1) # germanic plural by default
        buf = fp.read()
        buflen = len(buf)
        # Are we big endian or little endian?
        magic = unpack('<I', buf[:4])[0]
        ikiwa magic == self.LE_MAGIC:
            version, msgcount, masteridx, transidx = unpack('<4I', buf[4:20])
            ii = '<II'
        elikiwa magic == self.BE_MAGIC:
            version, msgcount, masteridx, transidx = unpack('>4I', buf[4:20])
            ii = '>II'
        else:
            raise OSError(0, 'Bad magic number', filename)

        major_version, minor_version = self._get_versions(version)

        ikiwa major_version not in self.VERSIONS:
            raise OSError(0, 'Bad version number ' + str(major_version), filename)

        # Now put all messages kutoka the .mo file buffer into the catalog
        # dictionary.
        for i in range(0, msgcount):
            mlen, moff = unpack(ii, buf[masteridx:masteridx+8])
            mend = moff + mlen
            tlen, toff = unpack(ii, buf[transidx:transidx+8])
            tend = toff + tlen
            ikiwa mend < buflen and tend < buflen:
                msg = buf[moff:mend]
                tmsg = buf[toff:tend]
            else:
                raise OSError(0, 'File is corrupt', filename)
            # See ikiwa we're looking at GNU .mo conventions for metadata
            ikiwa mlen == 0:
                # Catalog description
                lastk = None
                for b_item in tmsg.split(b'\n'):
                    item = b_item.decode().strip()
                    ikiwa not item:
                        continue
                    # Skip over comment lines:
                    ikiwa item.startswith('#-#-#-#-#') and item.endswith('#-#-#-#-#'):
                        continue
                    k = v = None
                    ikiwa ':' in item:
                        k, v = item.split(':', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        self._info[k] = v
                        lastk = k
                    elikiwa lastk:
                        self._info[lastk] += '\n' + item
                    ikiwa k == 'content-type':
                        self._charset = v.split('charset=')[1]
                    elikiwa k == 'plural-forms':
                        v = v.split(';')
                        plural = v[1].split('plural=')[1]
                        self.plural = c2py(plural)
            # Note: we unconditionally convert both msgids and msgstrs to
            # Unicode using the character encoding specified in the charset
            # parameter of the Content-Type header.  The gettext documentation
            # strongly encourages msgids to be us-ascii, but some applications
            # require alternative encodings (e.g. Zope's ZCML and ZPT).  For
            # traditional gettext applications, the msgid conversion will
            # cause no problems since us-ascii should always be a subset of
            # the charset encoding.  We may want to fall back to 8-bit msgids
            # ikiwa the Unicode conversion fails.
            charset = self._charset or 'ascii'
            ikiwa b'\x00' in msg:
                # Plural forms
                msgid1, msgid2 = msg.split(b'\x00')
                tmsg = tmsg.split(b'\x00')
                msgid1 = str(msgid1, charset)
                for i, x in enumerate(tmsg):
                    catalog[(msgid1, i)] = str(x, charset)
            else:
                catalog[str(msg, charset)] = str(tmsg, charset)
            # advance to next entry in the seek tables
            masteridx += 8
            transidx += 8

    eleza lgettext(self, message):
        agiza warnings
        warnings.warn('lgettext() is deprecated, use gettext() instead',
                      DeprecationWarning, 2)
        missing = object()
        tmsg = self._catalog.get(message, missing)
        ikiwa tmsg is missing:
            ikiwa self._fallback:
                rudisha self._fallback.lgettext(message)
            tmsg = message
        ikiwa self._output_charset:
            rudisha tmsg.encode(self._output_charset)
        rudisha tmsg.encode(locale.getpreferredencoding())

    eleza lngettext(self, msgid1, msgid2, n):
        agiza warnings
        warnings.warn('lngettext() is deprecated, use ngettext() instead',
                      DeprecationWarning, 2)
        try:
            tmsg = self._catalog[(msgid1, self.plural(n))]
        except KeyError:
            ikiwa self._fallback:
                rudisha self._fallback.lngettext(msgid1, msgid2, n)
            ikiwa n == 1:
                tmsg = msgid1
            else:
                tmsg = msgid2
        ikiwa self._output_charset:
            rudisha tmsg.encode(self._output_charset)
        rudisha tmsg.encode(locale.getpreferredencoding())

    eleza gettext(self, message):
        missing = object()
        tmsg = self._catalog.get(message, missing)
        ikiwa tmsg is missing:
            ikiwa self._fallback:
                rudisha self._fallback.gettext(message)
            rudisha message
        rudisha tmsg

    eleza ngettext(self, msgid1, msgid2, n):
        try:
            tmsg = self._catalog[(msgid1, self.plural(n))]
        except KeyError:
            ikiwa self._fallback:
                rudisha self._fallback.ngettext(msgid1, msgid2, n)
            ikiwa n == 1:
                tmsg = msgid1
            else:
                tmsg = msgid2
        rudisha tmsg

    eleza pgettext(self, context, message):
        ctxt_msg_id = self.CONTEXT % (context, message)
        missing = object()
        tmsg = self._catalog.get(ctxt_msg_id, missing)
        ikiwa tmsg is missing:
            ikiwa self._fallback:
                rudisha self._fallback.pgettext(context, message)
            rudisha message
        rudisha tmsg

    eleza npgettext(self, context, msgid1, msgid2, n):
        ctxt_msg_id = self.CONTEXT % (context, msgid1)
        try:
            tmsg = self._catalog[ctxt_msg_id, self.plural(n)]
        except KeyError:
            ikiwa self._fallback:
                rudisha self._fallback.npgettext(context, msgid1, msgid2, n)
            ikiwa n == 1:
                tmsg = msgid1
            else:
                tmsg = msgid2
        rudisha tmsg


# Locate a .mo file using the gettext strategy
eleza find(domain, localedir=None, languages=None, all=False):
    # Get some reasonable defaults for arguments that were not supplied
    ikiwa localedir is None:
        localedir = _default_localedir
    ikiwa languages is None:
        languages = []
        for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            ikiwa val:
                languages = val.split(':')
                break
        ikiwa 'C' not in languages:
            languages.append('C')
    # now normalize and expand the languages
    nelangs = []
    for lang in languages:
        for nelang in _expand_lang(lang):
            ikiwa nelang not in nelangs:
                nelangs.append(nelang)
    # select a language
    ikiwa all:
        result = []
    else:
        result = None
    for lang in nelangs:
        ikiwa lang == 'C':
            break
        mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.mo' % domain)
        ikiwa os.path.exists(mofile):
            ikiwa all:
                result.append(mofile)
            else:
                rudisha mofile
    rudisha result



# a mapping between absolute .mo file path and Translation object
_translations = {}
_unspecified = ['unspecified']

eleza translation(domain, localedir=None, languages=None,
                class_=None, fallback=False, codeset=_unspecified):
    ikiwa class_ is None:
        class_ = GNUTranslations
    mofiles = find(domain, localedir, languages, all=True)
    ikiwa not mofiles:
        ikiwa fallback:
            rudisha NullTranslations()
        kutoka errno agiza ENOENT
        raise FileNotFoundError(ENOENT,
                                'No translation file found for domain', domain)
    # Avoid opening, reading, and parsing the .mo file after it's been done
    # once.
    result = None
    for mofile in mofiles:
        key = (class_, os.path.abspath(mofile))
        t = _translations.get(key)
        ikiwa t is None:
            with open(mofile, 'rb') as fp:
                t = _translations.setdefault(key, class_(fp))
        # Copy the translation object to allow setting fallbacks and
        # output charset. All other instance data is shared with the
        # cached object.
        # Delay copy agiza for speeding up gettext agiza when .mo files
        # are not used.
        agiza copy
        t = copy.copy(t)
        ikiwa codeset is not _unspecified:
            agiza warnings
            warnings.warn('parameter codeset is deprecated',
                          DeprecationWarning, 2)
            ikiwa codeset:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', r'.*\bset_output_charset\b.*',
                                            DeprecationWarning)
                    t.set_output_charset(codeset)
        ikiwa result is None:
            result = t
        else:
            result.add_fallback(t)
    rudisha result


eleza install(domain, localedir=None, codeset=_unspecified, names=None):
    t = translation(domain, localedir, fallback=True, codeset=codeset)
    t.install(names)



# a mapping b/w domains and locale directories
_localedirs = {}
# a mapping b/w domains and codesets
_localecodesets = {}
# current global domain, `messages' used for compatibility w/ GNU gettext
_current_domain = 'messages'


eleza textdomain(domain=None):
    global _current_domain
    ikiwa domain is not None:
        _current_domain = domain
    rudisha _current_domain


eleza bindtextdomain(domain, localedir=None):
    global _localedirs
    ikiwa localedir is not None:
        _localedirs[domain] = localedir
    rudisha _localedirs.get(domain, _default_localedir)


eleza bind_textdomain_codeset(domain, codeset=None):
    agiza warnings
    warnings.warn('bind_textdomain_codeset() is deprecated',
                  DeprecationWarning, 2)
    global _localecodesets
    ikiwa codeset is not None:
        _localecodesets[domain] = codeset
    rudisha _localecodesets.get(domain)


eleza dgettext(domain, message):
    try:
        t = translation(domain, _localedirs.get(domain, None))
    except OSError:
        rudisha message
    rudisha t.gettext(message)

eleza ldgettext(domain, message):
    agiza warnings
    warnings.warn('ldgettext() is deprecated, use dgettext() instead',
                  DeprecationWarning, 2)
    codeset = _localecodesets.get(domain)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'.*\bparameter codeset\b.*',
                                    DeprecationWarning)
            t = translation(domain, _localedirs.get(domain, None), codeset=codeset)
    except OSError:
        rudisha message.encode(codeset or locale.getpreferredencoding())
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'.*\blgettext\b.*',
                                DeprecationWarning)
        rudisha t.lgettext(message)

eleza dngettext(domain, msgid1, msgid2, n):
    try:
        t = translation(domain, _localedirs.get(domain, None))
    except OSError:
        ikiwa n == 1:
            rudisha msgid1
        else:
            rudisha msgid2
    rudisha t.ngettext(msgid1, msgid2, n)

eleza ldngettext(domain, msgid1, msgid2, n):
    agiza warnings
    warnings.warn('ldngettext() is deprecated, use dngettext() instead',
                  DeprecationWarning, 2)
    codeset = _localecodesets.get(domain)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'.*\bparameter codeset\b.*',
                                    DeprecationWarning)
            t = translation(domain, _localedirs.get(domain, None), codeset=codeset)
    except OSError:
        ikiwa n == 1:
            tmsg = msgid1
        else:
            tmsg = msgid2
        rudisha tmsg.encode(codeset or locale.getpreferredencoding())
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'.*\blngettext\b.*',
                                DeprecationWarning)
        rudisha t.lngettext(msgid1, msgid2, n)


eleza dpgettext(domain, context, message):
    try:
        t = translation(domain, _localedirs.get(domain, None))
    except OSError:
        rudisha message
    rudisha t.pgettext(context, message)


eleza dnpgettext(domain, context, msgid1, msgid2, n):
    try:
        t = translation(domain, _localedirs.get(domain, None))
    except OSError:
        ikiwa n == 1:
            rudisha msgid1
        else:
            rudisha msgid2
    rudisha t.npgettext(context, msgid1, msgid2, n)


eleza gettext(message):
    rudisha dgettext(_current_domain, message)

eleza lgettext(message):
    agiza warnings
    warnings.warn('lgettext() is deprecated, use gettext() instead',
                  DeprecationWarning, 2)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'.*\bldgettext\b.*',
                                DeprecationWarning)
        rudisha ldgettext(_current_domain, message)

eleza ngettext(msgid1, msgid2, n):
    rudisha dngettext(_current_domain, msgid1, msgid2, n)

eleza lngettext(msgid1, msgid2, n):
    agiza warnings
    warnings.warn('lngettext() is deprecated, use ngettext() instead',
                  DeprecationWarning, 2)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'.*\bldngettext\b.*',
                                DeprecationWarning)
        rudisha ldngettext(_current_domain, msgid1, msgid2, n)


eleza pgettext(context, message):
    rudisha dpgettext(_current_domain, context, message)


eleza npgettext(context, msgid1, msgid2, n):
    rudisha dnpgettext(_current_domain, context, msgid1, msgid2, n)


# dcgettext() has been deemed unnecessary and is not implemented.

# James Henstridge's Catalog constructor kutoka GNOME gettext.  Documented usage
# was:
#
#    agiza gettext
#    cat = gettext.Catalog(PACKAGE, localedir=LOCALEDIR)
#    _ = cat.gettext
#    print _('Hello World')

# The resulting catalog object currently don't support access through a
# dictionary API, which was supported (but apparently unused) in GNOME
# gettext.

Catalog = translation
