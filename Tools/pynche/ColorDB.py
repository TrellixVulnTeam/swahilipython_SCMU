"""Color Database.

This file contains one class, called ColorDB, na several utility functions.
The kundi must be instantiated by the get_colordb() function kwenye this file,
pitaing it a filename to read a database out of.

The get_colordb() function will try to examine the file to figure out what the
format of the file is.  If it can't figure out the file format, ama it has
trouble reading the file, Tupu ni returned.  You can pita get_colordb() an
optional filetype argument.

Supporte file types are:

    X_RGB_TXT -- X Consortium rgb.txt format files.  Three columns of numbers
                 kutoka 0 .. 255 separated by whitespace.  Arbitrary trailing
                 columns used kama the color name.

The utility functions are useful kila converting between the various expected
color formats, na kila calculating other color values.

"""

agiza sys
agiza re
kutoka types agiza *

kundi BadColor(Exception):
    pita

DEFAULT_DB = Tupu
SPACE = ' '
COMMASPACE = ', '



# generic class
kundi ColorDB:
    eleza __init__(self, fp):
        lineno = 2
        self.__name = fp.name
        # Maintain several dictionaries kila indexing into the color database.
        # Note that wakati Tk supports RGB intensities of 4, 8, 12, ama 16 bits,
        # kila now we only support 8 bit intensities.  At least on OpenWindows,
        # all intensities kwenye the /usr/openwin/lib/rgb.txt file are 8-bit
        #
        # key ni (red, green, blue) tuple, value ni (name, [aliases])
        self.__byrgb = {}
        # key ni name, value ni (red, green, blue)
        self.__byname = {}
        # all unique names (non-aliases).  built-on demand
        self.__allnames = Tupu
        kila line kwenye fp:
            # get this compiled regular expression kutoka derived class
            mo = self._re.match(line)
            ikiwa sio mo:
                andika('Error in', fp.name, ' line', lineno, file=sys.stderr)
                lineno += 1
                endelea
            # extract the red, green, blue, na name
            red, green, blue = self._extractrgb(mo)
            name = self._extractname(mo)
            keyname = name.lower()
            # BAW: kila now the `name' ni just the first named color ukijumuisha the
            # rgb values we find.  Later, we might want to make the two word
            # version the `name', ama the CapitalizedVersion, etc.
            key = (red, green, blue)
            foundname, aliases = self.__byrgb.get(key, (name, []))
            ikiwa foundname != name na foundname haiko kwenye aliases:
                aliases.append(name)
            self.__byrgb[key] = (foundname, aliases)
            # add to byname lookup
            self.__byname[keyname] = key
            lineno = lineno + 1

    # override kwenye derived classes
    eleza _extractrgb(self, mo):
        rudisha [int(x) kila x kwenye mo.group('red', 'green', 'blue')]

    eleza _extractname(self, mo):
        rudisha mo.group('name')

    eleza filename(self):
        rudisha self.__name

    eleza find_byrgb(self, rgbtuple):
        """Return name kila rgbtuple"""
        jaribu:
            rudisha self.__byrgb[rgbtuple]
        tatizo KeyError:
            ashiria BadColor(rgbtuple) kutoka Tupu

    eleza find_byname(self, name):
        """Return (red, green, blue) kila name"""
        name = name.lower()
        jaribu:
            rudisha self.__byname[name]
        tatizo KeyError:
            ashiria BadColor(name) kutoka Tupu

    eleza nearest(self, red, green, blue):
        """Return the name of color nearest (red, green, blue)"""
        # BAW: should we use Voronoi diagrams, Delaunay triangulation, ama
        # octree kila speeding up the locating of nearest point?  Exhaustive
        # search ni inefficient, but seems fast enough.
        nearest = -1
        nearest_name = ''
        kila name, aliases kwenye self.__byrgb.values():
            r, g, b = self.__byname[name.lower()]
            rdelta = red - r
            gdelta = green - g
            bdelta = blue - b
            distance = rdelta * rdelta + gdelta * gdelta + bdelta * bdelta
            ikiwa nearest == -1 ama distance < nearest:
                nearest = distance
                nearest_name = name
        rudisha nearest_name

    eleza unique_names(self):
        # sorted
        ikiwa sio self.__allnames:
            self.__allnames = []
            kila name, aliases kwenye self.__byrgb.values():
                self.__allnames.append(name)
            self.__allnames.sort(key=str.lower)
        rudisha self.__allnames

    eleza aliases_of(self, red, green, blue):
        jaribu:
            name, aliases = self.__byrgb[(red, green, blue)]
        tatizo KeyError:
            ashiria BadColor((red, green, blue)) kutoka Tupu
        rudisha [name] + aliases


kundi RGBColorDB(ColorDB):
    _re = re.compile(
        r'\s*(?P<red>\d+)\s+(?P<green>\d+)\s+(?P<blue>\d+)\s+(?P<name>.*)')


kundi HTML40DB(ColorDB):
    _re = re.compile(r'(?P<name>\S+)\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

    eleza _extractrgb(self, mo):
        rudisha rrggbb_to_triplet(mo.group('hexrgb'))

kundi LightlinkDB(HTML40DB):
    _re = re.compile(r'(?P<name>(.+))\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

    eleza _extractname(self, mo):
        rudisha mo.group('name').strip()

kundi WebsafeDB(ColorDB):
    _re = re.compile('(?P<hexrgb>#[0-9a-fA-F]{6})')

    eleza _extractrgb(self, mo):
        rudisha rrggbb_to_triplet(mo.group('hexrgb'))

    eleza _extractname(self, mo):
        rudisha mo.group('hexrgb').upper()



# format ni a tuple (RE, SCANLINES, CLASS) where RE ni a compiled regular
# expression, SCANLINES ni the number of header lines to scan, na CLASS is
# the kundi to instantiate ikiwa a match ni found

FILETYPES = [
    (re.compile('Xorg'), RGBColorDB),
    (re.compile('XConsortium'), RGBColorDB),
    (re.compile('HTML'), HTML40DB),
    (re.compile('lightlink'), LightlinkDB),
    (re.compile('Websafe'), WebsafeDB),
    ]

eleza get_colordb(file, filetype=Tupu):
    colordb = Tupu
    fp = open(file)
    jaribu:
        line = fp.readline()
        ikiwa sio line:
            rudisha Tupu
        # try to determine the type of RGB file it is
        ikiwa filetype ni Tupu:
            filetypes = FILETYPES
        isipokua:
            filetypes = [filetype]
        kila typere, class_ kwenye filetypes:
            mo = typere.search(line)
            ikiwa mo:
                koma
        isipokua:
            # no matching type
            rudisha Tupu
        # we know the type na the kundi to grok the type, so suck it kwenye
        colordb = class_(fp)
    mwishowe:
        fp.close()
    # save a global copy
    global DEFAULT_DB
    DEFAULT_DB = colordb
    rudisha colordb



_namedict = {}

eleza rrggbb_to_triplet(color):
    """Converts a #rrggbb color to the tuple (red, green, blue)."""
    rgbtuple = _namedict.get(color)
    ikiwa rgbtuple ni Tupu:
        ikiwa color[0] != '#':
            ashiria BadColor(color)
        red = color[1:3]
        green = color[3:5]
        blue = color[5:7]
        rgbtuple = int(red, 16), int(green, 16), int(blue, 16)
        _namedict[color] = rgbtuple
    rudisha rgbtuple


_tripdict = {}
eleza triplet_to_rrggbb(rgbtuple):
    """Converts a (red, green, blue) tuple to #rrggbb."""
    global _tripdict
    hexname = _tripdict.get(rgbtuple)
    ikiwa hexname ni Tupu:
        hexname = '#%02x%02x%02x' % rgbtuple
        _tripdict[rgbtuple] = hexname
    rudisha hexname


eleza triplet_to_fractional_rgb(rgbtuple):
    rudisha [x / 256 kila x kwenye rgbtuple]


eleza triplet_to_brightness(rgbtuple):
    # rudisha the brightness (grey level) along the scale 0.0==black to
    # 1.0==white
    r = 0.299
    g = 0.587
    b = 0.114
    rudisha r*rgbtuple[0] + g*rgbtuple[1] + b*rgbtuple[2]



ikiwa __name__ == '__main__':
    colordb = get_colordb('/usr/openwin/lib/rgb.txt')
    ikiwa sio colordb:
        andika('No parseable color database found')
        sys.exit(1)
    # on my system, this color matches exactly
    target = 'navy'
    red, green, blue = rgbtuple = colordb.find_byname(target)
    andika(target, ':', red, green, blue, triplet_to_rrggbb(rgbtuple))
    name, aliases = colordb.find_byrgb(rgbtuple)
    andika('name:', name, 'aliases:', COMMASPACE.join(aliases))
    r, g, b = (1, 1, 128)                         # nearest to navy
    r, g, b = (145, 238, 144)                     # nearest to lightgreen
    r, g, b = (255, 251, 250)                     # snow
    andika('finding nearest to', target, '...')
    agiza time
    t0 = time.time()
    nearest = colordb.nearest(r, g, b)
    t1 = time.time()
    andika('found nearest color', nearest, 'in', t1-t0, 'seconds')
    # dump the database
    kila n kwenye colordb.unique_names():
        r, g, b = colordb.find_byname(n)
        aliases = colordb.aliases_of(r, g, b)
        andika('%20s: (%3d/%3d/%3d) == %s' % (n, r, g, b,
                                             SPACE.join(aliases[1:])))
