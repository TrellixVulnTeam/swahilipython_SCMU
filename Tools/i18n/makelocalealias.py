#!/usr/bin/env python3
"""
    Convert the X11 locale.alias file into a mapping dictionary suitable
    kila locale.py.

    Written by Marc-Andre Lemburg <mal@genix.com>, 2004-12-10.

"""
agiza locale
agiza sys
_locale = locale

# Location of the X11 alias file.
LOCALE_ALIAS = '/usr/share/X11/locale/locale.alias'
# Location of the glibc SUPPORTED locales file.
SUPPORTED = '/usr/share/i18n/SUPPORTED'

eleza parse(filename):

    ukijumuisha open(filename, encoding='latin1') kama f:
        lines = list(f)
    # Remove mojibake kwenye /usr/share/X11/locale/locale.alias.
    # b'\xef\xbf\xbd' == '\ufffd'.encode('utf-8')
    lines = [line kila line kwenye lines ikiwa '\xef\xbf\xbd' haiko kwenye line]
    data = {}
    kila line kwenye lines:
        line = line.strip()
        ikiwa sio line:
            endelea
        ikiwa line[:1] == '#':
            endelea
        locale, alias = line.split()
        # Fix non-standard locale names, e.g. ks_IN@devanagari.UTF-8
        ikiwa '@' kwenye alias:
            alias_lang, _, alias_mod = alias.partition('@')
            ikiwa '.' kwenye alias_mod:
                alias_mod, _, alias_enc = alias_mod.partition('.')
                alias = alias_lang + '.' + alias_enc + '@' + alias_mod
        # Strip ':'
        ikiwa locale[-1] == ':':
            locale = locale[:-1]
        # Lower-case locale
        locale = locale.lower()
        # Ignore one letter locale mappings (tatizo kila 'c')
        ikiwa len(locale) == 1 na locale != 'c':
            endelea
        # Normalize encoding, ikiwa given
        ikiwa '.' kwenye locale:
            lang, encoding = locale.split('.')[:2]
            encoding = encoding.replace('-', '')
            encoding = encoding.replace('_', '')
            locale = lang + '.' + encoding
        data[locale] = alias
    rudisha data

eleza parse_glibc_supported(filename):

    ukijumuisha open(filename, encoding='latin1') kama f:
        lines = list(f)
    data = {}
    kila line kwenye lines:
        line = line.strip()
        ikiwa sio line:
            endelea
        ikiwa line[:1] == '#':
            endelea
        line = line.replace('/', ' ').strip()
        line = line.rstrip('\\').rstrip()
        words = line.split()
        ikiwa len(words) != 2:
            endelea
        alias, alias_encoding = words
        # Lower-case locale
        locale = alias.lower()
        # Normalize encoding, ikiwa given
        ikiwa '.' kwenye locale:
            lang, encoding = locale.split('.')[:2]
            encoding = encoding.replace('-', '')
            encoding = encoding.replace('_', '')
            locale = lang + '.' + encoding
        # Add an encoding to alias
        alias, _, modifier = alias.partition('@')
        alias = _locale._replace_encoding(alias, alias_encoding)
        ikiwa modifier na sio (modifier == 'euro' na alias_encoding == 'ISO-8859-15'):
            alias += '@' + modifier
        data[locale] = alias
    rudisha data

eleza pandika(data):
    items = sorted(data.items())
    kila k, v kwenye items:
        andika('    %-40s%a,' % ('%a:' % k, v))

eleza print_differences(data, olddata):
    items = sorted(olddata.items())
    kila k, v kwenye items:
        ikiwa k haiko kwenye data:
            andika('#    removed %a' % k)
        lasivyo olddata[k] != data[k]:
            andika('#    updated %a -> %a to %a' % \
                  (k, olddata[k], data[k]))
        # Additions are sio mentioned

eleza optimize(data):
    locale_alias = locale.locale_alias
    locale.locale_alias = data.copy()
    kila k, v kwenye data.items():
        toa locale.locale_alias[k]
        ikiwa locale.normalize(k) != v:
            locale.locale_alias[k] = v
    newdata = locale.locale_alias
    errors = check(data)
    locale.locale_alias = locale_alias
    ikiwa errors:
        sys.exit(1)
    rudisha newdata

eleza check(data):
    # Check that all alias definitions kutoka the X11 file
    # are actually mapped to the correct alias locales.
    errors = 0
    kila k, v kwenye data.items():
        ikiwa locale.normalize(k) != v:
            andika('ERROR: %a -> %a != %a' % (k, locale.normalize(k), v),
                  file=sys.stderr)
            errors += 1
    rudisha errors

ikiwa __name__ == '__main__':
    agiza argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--locale-alias', default=LOCALE_ALIAS,
                        help='location of the X11 alias file '
                             '(default: %a)' % LOCALE_ALIAS)
    parser.add_argument('--glibc-supported', default=SUPPORTED,
                        help='location of the glibc SUPPORTED locales file '
                             '(default: %a)' % SUPPORTED)
    args = parser.parse_args()

    data = locale.locale_alias.copy()
    data.update(parse_glibc_supported(args.glibc_supported))
    data.update(parse(args.locale_alias))
    wakati Kweli:
        # Repeat optimization wakati the size ni decreased.
        n = len(data)
        data = optimize(data)
        ikiwa len(data) == n:
            koma
    print_differences(data, locale.locale_alias)
    andika()
    andika('locale_alias = {')
    pandika(data)
    andika('}')
