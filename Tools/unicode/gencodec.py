""" Unicode Mapping Parser na Codec Generator.

This script parses Unicode mapping files kama available kutoka the Unicode
site (ftp://ftp.unicode.org/Public/MAPPINGS/) na creates Python codec
modules kutoka them. The codecs use the standard character mapping codec
to actually apply the mapping.

Synopsis: gencodec.py dir codec_prefix

All files kwenye dir are scanned na those producing non-empty mappings
will be written to <codec_prefix><mapname>.py ukijumuisha <mapname> being the
first part of the map's filename ('a' kwenye a.b.c.txt) converted to
lowercase ukijumuisha hyphens replaced by underscores.

The tool also writes marshalled versions of the mapping tables to the
same location (ukijumuisha .mapping extension).

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.
(c) Copyright Guido van Rossum, 2000.

Table generation:
(c) Copyright Marc-Andre Lemburg, 2005.
    Licensed to PSF under a Contributor Agreement.

"""#"

agiza re, os, marshal, codecs

# Maximum allowed size of charmap tables
MAX_TABLE_SIZE = 8192

# Standard undefined Unicode code point
UNI_UNDEFINED = chr(0xFFFE)

# Placeholder kila a missing code point
MISSING_CODE = -1

mapRE = re.compile(r'((?:0x[0-9a-fA-F]+\+?)+)'
                   r'\s+'
                   r'((?:(?:0x[0-9a-fA-Z]+|<[A-Za-z]+>)\+?)*)'
                   r'\s*'
                   r'(#.+)?')

eleza parsecodes(codes, len=len, range=range):

    """ Converts code combinations to either a single code integer
        ama a tuple of integers.

        meta-codes (in angular brackets, e.g. <LR> na <RL>) are
        ignored.

        Empty codes ama illegal ones are returned kama Tupu.

    """
    ikiwa sio codes:
        rudisha MISSING_CODE
    l = codes.split('+')
    ikiwa len(l) == 1:
        rudisha int(l[0],16)
    kila i kwenye range(len(l)):
        jaribu:
            l[i] = int(l[i],16)
        tatizo ValueError:
            l[i] = MISSING_CODE
    l = [x kila x kwenye l ikiwa x != MISSING_CODE]
    ikiwa len(l) == 1:
        rudisha l[0]
    isipokua:
        rudisha tuple(l)

eleza readmap(filename):

    ukijumuisha open(filename) kama f:
        lines = f.readlines()
    enc2uni = {}
    identity = []
    unmapped = list(range(256))

    # UTC mapping tables per convention don't include the identity
    # mappings kila code points 0x00 - 0x1F na 0x7F, unless these are
    # explicitly mapped to different characters ama undefined
    kila i kwenye list(range(32)) + [127]:
        identity.append(i)
        unmapped.remove(i)
        enc2uni[i] = (i, 'CONTROL CHARACTER')

    kila line kwenye lines:
        line = line.strip()
        ikiwa sio line ama line[0] == '#':
            endelea
        m = mapRE.match(line)
        ikiwa sio m:
            #print '* sio matched: %s' % repr(line)
            endelea
        enc,uni,comment = m.groups()
        enc = parsecodes(enc)
        uni = parsecodes(uni)
        ikiwa comment ni Tupu:
            comment = ''
        isipokua:
            comment = comment[1:].strip()
        ikiwa sio isinstance(enc, tuple) na enc < 256:
            ikiwa enc kwenye unmapped:
                unmapped.remove(enc)
            ikiwa enc == uni:
                identity.append(enc)
            enc2uni[enc] = (uni,comment)
        isipokua:
            enc2uni[enc] = (uni,comment)

    # If there are more identity-mapped entries than unmapped entries,
    # it pays to generate an identity dictionary first, na add explicit
    # mappings to Tupu kila the rest
    ikiwa len(identity) >= len(unmapped):
        kila enc kwenye unmapped:
            enc2uni[enc] = (MISSING_CODE, "")
        enc2uni['IDENTITY'] = 256

    rudisha enc2uni

eleza hexrepr(t, precision=4):

    ikiwa t ni Tupu:
        rudisha 'Tupu'
    jaribu:
        len(t)
    tatizo TypeError:
        rudisha '0x%0*X' % (precision, t)
    jaribu:
        rudisha '(' + ', '.join(['0x%0*X' % (precision, item)
                                kila item kwenye t]) + ')'
    tatizo TypeError kama why:
        andika('* failed to convert %r: %s' % (t, why))
        raise

eleza python_mapdef_code(varname, map, comments=1, precisions=(2, 4)):

    l = []
    append = l.append
    ikiwa "IDENTITY" kwenye map:
        append("%s = codecs.make_identity_dict(range(%d))" %
               (varname, map["IDENTITY"]))
        append("%s.update({" % varname)
        splits = 1
        toa map["IDENTITY"]
        identity = 1
    isipokua:
        append("%s = {" % varname)
        splits = 0
        identity = 0

    mappings = sorted(map.items())
    i = 0
    key_precision, value_precision = precisions
    kila mapkey, mapvalue kwenye mappings:
        mapcomment = ''
        ikiwa isinstance(mapkey, tuple):
            (mapkey, mapcomment) = mapkey
        ikiwa isinstance(mapvalue, tuple):
            (mapvalue, mapcomment) = mapvalue
        ikiwa mapkey ni Tupu:
            endelea
        ikiwa (identity na
            mapkey == mapvalue na
            mapkey < 256):
            # No need to include identity mappings, since these
            # are already set kila the first 256 code points.
            endelea
        key = hexrepr(mapkey, key_precision)
        value = hexrepr(mapvalue, value_precision)
        ikiwa mapcomment na comments:
            append('    %s: %s,\t#  %s' % (key, value, mapcomment))
        isipokua:
            append('    %s: %s,' % (key, value))
        i += 1
        ikiwa i == 4096:
            # Split the definition into parts to that the Python
            # parser doesn't dump core
            ikiwa splits == 0:
                append('}')
            isipokua:
                append('})')
            append('%s.update({' % varname)
            i = 0
            splits = splits + 1
    ikiwa splits == 0:
        append('}')
    isipokua:
        append('})')

    rudisha l

eleza python_tabledef_code(varname, map, comments=1, key_precision=2):

    l = []
    append = l.append
    append('%s = (' % varname)

    # Analyze map na create table dict
    mappings = sorted(map.items())
    table = {}
    maxkey = 255
    ikiwa 'IDENTITY' kwenye map:
        kila key kwenye range(256):
            table[key] = (key, '')
        toa map['IDENTITY']
    kila mapkey, mapvalue kwenye mappings:
        mapcomment = ''
        ikiwa isinstance(mapkey, tuple):
            (mapkey, mapcomment) = mapkey
        ikiwa isinstance(mapvalue, tuple):
            (mapvalue, mapcomment) = mapvalue
        ikiwa mapkey == MISSING_CODE:
            endelea
        table[mapkey] = (mapvalue, mapcomment)
        ikiwa mapkey > maxkey:
            maxkey = mapkey
    ikiwa maxkey > MAX_TABLE_SIZE:
        # Table too large
        rudisha Tupu

    # Create table code
    maxchar = 0
    kila key kwenye range(maxkey + 1):
        ikiwa key haiko kwenye table:
            mapvalue = MISSING_CODE
            mapcomment = 'UNDEFINED'
        isipokua:
            mapvalue, mapcomment = table[key]
        ikiwa mapvalue == MISSING_CODE:
            mapchar = UNI_UNDEFINED
        isipokua:
            ikiwa isinstance(mapvalue, tuple):
                # 1-n mappings sio supported
                rudisha Tupu
            isipokua:
                mapchar = chr(mapvalue)
        maxchar = max(maxchar, ord(mapchar))
        ikiwa mapcomment na comments:
            append('    %a \t#  %s -> %s' % (mapchar,
                                            hexrepr(key, key_precision),
                                            mapcomment))
        isipokua:
            append('    %a' % mapchar)

    ikiwa maxchar < 256:
        append('    %a \t## Widen to UCS2 kila optimization' % UNI_UNDEFINED)
    append(')')
    rudisha l

eleza codegen(name, map, encodingname, comments=1):

    """ Returns Python source kila the given map.

        Comments are included kwenye the source, ikiwa comments ni true (default).

    """
    # Generate code
    decoding_map_code = python_mapdef_code(
        'decoding_map',
        map,
        comments=comments)
    decoding_table_code = python_tabledef_code(
        'decoding_table',
        map,
        comments=comments)
    encoding_map_code = python_mapdef_code(
        'encoding_map',
        codecs.make_encoding_map(map),
        comments=comments,
        precisions=(4, 2))

    ikiwa decoding_table_code:
        suffix = 'table'
    isipokua:
        suffix = 'map'

    l = [
        '''\
""" Python Character Mapping Codec %s generated kutoka '%s' ukijumuisha gencodec.py.

"""#"

agiza codecs

### Codec APIs

kundi Codec(codecs.Codec):

    eleza encode(self, input, errors='strict'):
        rudisha codecs.charmap_encode(input, errors, encoding_%s)

    eleza decode(self, input, errors='strict'):
        rudisha codecs.charmap_decode(input, errors, decoding_%s)
''' % (encodingname, name, suffix, suffix)]
    l.append('''\
kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        rudisha codecs.charmap_encode(input, self.errors, encoding_%s)[0]

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=Uongo):
        rudisha codecs.charmap_decode(input, self.errors, decoding_%s)[0]''' %
        (suffix, suffix))

    l.append('''
kundi StreamWriter(Codec, codecs.StreamWriter):
    pita

kundi StreamReader(Codec, codecs.StreamReader):
    pita

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name=%r,
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
''' % encodingname.replace('_', '-'))

    # Add decoding table ama map (ukijumuisha preference to the table)
    ikiwa sio decoding_table_code:
        l.append('''
### Decoding Map
''')
        l.extend(decoding_map_code)
    isipokua:
        l.append('''
### Decoding Table
''')
        l.extend(decoding_table_code)

    # Add encoding map
    ikiwa decoding_table_code:
        l.append('''
### Encoding table
encoding_table = codecs.charmap_build(decoding_table)
''')
    isipokua:
        l.append('''
### Encoding Map
''')
        l.extend(encoding_map_code)

    # Final new-line
    l.append('')

    rudisha '\n'.join(l).expandtabs()

eleza pymap(name,map,pyfile,encodingname,comments=1):

    code = codegen(name,map,encodingname,comments)
    ukijumuisha open(pyfile,'w') kama f:
        f.write(code)

eleza marshalmap(name,map,marshalfile):

    d = {}
    kila e,(u,c) kwenye map.items():
        d[e] = (u,c)
    ukijumuisha open(marshalfile,'wb') kama f:
        marshal.dump(d,f)

eleza convertdir(dir, dirprefix='', nameprefix='', comments=1):

    mapnames = os.listdir(dir)
    kila mapname kwenye mapnames:
        mappathname = os.path.join(dir, mapname)
        ikiwa sio os.path.isfile(mappathname):
            endelea
        name = os.path.split(mapname)[1]
        name = name.replace('-','_')
        name = name.split('.')[0]
        name = name.lower()
        name = nameprefix + name
        codefile = name + '.py'
        marshalfile = name + '.mapping'
        andika('converting %s to %s na %s' % (mapname,
                                              dirprefix + codefile,
                                              dirprefix + marshalfile))
        jaribu:
            map = readmap(os.path.join(dir,mapname))
            ikiwa sio map:
                andika('* map ni empty; skipping')
            isipokua:
                pymap(mappathname, map, dirprefix + codefile,name,comments)
                marshalmap(mappathname, map, dirprefix + marshalfile)
        tatizo ValueError kama why:
            andika('* conversion failed: %s' % why)
            raise

eleza rewritepythondir(dir, dirprefix='', comments=1):

    mapnames = os.listdir(dir)
    kila mapname kwenye mapnames:
        ikiwa sio mapname.endswith('.mapping'):
            endelea
        name = mapname[:-len('.mapping')]
        codefile = name + '.py'
        andika('converting %s to %s' % (mapname,
                                       dirprefix + codefile))
        jaribu:
            ukijumuisha open(os.path.join(dir, mapname), 'rb') kama f:
                map = marshal.load(f)
            ikiwa sio map:
                andika('* map ni empty; skipping')
            isipokua:
                pymap(mapname, map, dirprefix + codefile,name,comments)
        tatizo ValueError kama why:
            andika('* conversion failed: %s' % why)

ikiwa __name__ == '__main__':

    agiza sys
    ikiwa 1:
        convertdir(*sys.argv[1:])
    isipokua:
        rewritepythondir(*sys.argv[1:])
