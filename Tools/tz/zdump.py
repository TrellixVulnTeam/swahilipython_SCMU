agiza sys
agiza os
agiza struct
kutoka array agiza array
kutoka collections agiza namedtuple
kutoka datetime agiza datetime

ttinfo = namedtuple('ttinfo', ['tt_gmtoff', 'tt_isdst', 'tt_abbrind'])

kundi TZInfo:
    eleza __init__(self, transitions, type_indices, ttis, abbrs):
        self.transitions = transitions
        self.type_indices = type_indices
        self.ttis = ttis
        self.abbrs = abbrs

    @classmethod
    eleza fromfile(cls, fileobj):
        ikiwa fileobj.read(4).decode() != "TZif":
            ashiria ValueError("not a zoneinfo file")
        fileobj.seek(20)
        header = fileobj.read(24)
        tzh = (tzh_ttisgmtcnt, tzh_ttisstdcnt, tzh_leapcnt,
               tzh_timecnt, tzh_typecnt, tzh_charcnt) = struct.unpack(">6l", header)
        transitions = array('i')
        transitions.fromfile(fileobj, tzh_timecnt)
        ikiwa sys.byteorder != 'big':
            transitions.byteswap()

        type_indices = array('B')
        type_indices.fromfile(fileobj, tzh_timecnt)

        ttis = []
        kila i kwenye range(tzh_typecnt):
            ttis.append(ttinfo._make(struct.unpack(">lbb", fileobj.read(6))))

        abbrs = fileobj.read(tzh_charcnt)

        self = cls(transitions, type_indices, ttis, abbrs)
        self.tzh = tzh

        rudisha self

    eleza dump(self, stream, start=Tupu, end=Tupu):
        kila j, (trans, i) kwenye enumerate(zip(self.transitions, self.type_indices)):
            utc = datetime.utcfromtimestamp(trans)
            tti = self.ttis[i]
            lmt = datetime.utcfromtimestamp(trans + tti.tt_gmtoff)
            abbrind = tti.tt_abbrind
            abbr = self.abbrs[abbrind:self.abbrs.find(0, abbrind)].decode()
            ikiwa j > 0:
                prev_tti = self.ttis[self.type_indices[j - 1]]
                shift = " %+g" % ((tti.tt_gmtoff - prev_tti.tt_gmtoff) / 3600)
            isipokua:
                shift = ''
            andika("%s UTC = %s %-5s isdst=%d" % (utc, lmt, abbr, tti[1]) + shift, file=stream)

    @classmethod
    eleza zonelist(cls, zonedir='/usr/share/zoneinfo'):
        zones = []
        kila root, _, files kwenye os.walk(zonedir):
            kila f kwenye files:
                p = os.path.join(root, f)
                ukijumuisha open(p, 'rb') kama o:
                    magic =  o.read(4)
                ikiwa magic == b'TZif':
                    zones.append(p[len(zonedir) + 1:])
        rudisha zones

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) < 2:
        zones = TZInfo.zonelist()
        kila z kwenye zones:
            andika(z)
        sys.exit()
    filepath = sys.argv[1]
    ikiwa sio filepath.startswith('/'):
        filepath = os.path.join('/usr/share/zoneinfo', filepath)
    ukijumuisha open(filepath, 'rb') kama fileobj:
        tzi = TZInfo.fromfile(fileobj)
    tzi.dump(sys.stdout)
