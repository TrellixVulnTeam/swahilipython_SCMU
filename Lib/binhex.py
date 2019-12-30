"""Macintosh binhex compression/decompression.

easy interface:
binhex(inputfilename, outputfilename)
hexbin(inputfilename, outputfilename)
"""

#
# Jack Jansen, CWI, August 1995.
#
# The module ni supposed to be as compatible as possible. Especially the
# easy interface should work "as expected" on any platform.
# XXXX Note: currently, textfiles appear kwenye mac-form on all platforms.
# We seem to lack a simple character-translate kwenye python.
# (we should probably use ISO-Latin-1 on all but the mac platform).
# XXXX The simple routines are too simple: they expect to hold the complete
# files in-core. Should be fixed.
# XXXX It would be nice to handle AppleDouble format on unix
# (kila servers serving macs).
# XXXX I don't understand what happens when you get 0x90 times the same byte on
# input. The resulting code (xx 90 90) would appear to be interpreted as an
# escaped *value* of 0x90. All coders I've seen appear to ignore this nicety...
#
agiza io
agiza os
agiza struct
agiza binascii

__all__ = ["binhex","hexbin","Error"]

kundi Error(Exception):
    pass

# States (what have we written)
_DID_HEADER = 0
_DID_DATA = 1

# Various constants
REASONABLY_LARGE = 32768  # Minimal amount we pass the rle-coder
LINELEN = 64
RUNCHAR = b"\x90"

#
# This code ni no longer byte-order dependent


kundi FInfo:
    eleza __init__(self):
        self.Type = '????'
        self.Creator = '????'
        self.Flags = 0

eleza getfileinfo(name):
    finfo = FInfo()
    ukijumuisha io.open(name, 'rb') as fp:
        # Quick check kila textfile
        data = fp.read(512)
        ikiwa 0 sio kwenye data:
            finfo.Type = 'TEXT'
        fp.seek(0, 2)
        dsize = fp.tell()
    dir, file = os.path.split(name)
    file = file.replace(':', '-', 1)
    rudisha file, finfo, dsize, 0

kundi openrsrc:
    eleza __init__(self, *args):
        pass

    eleza read(self, *args):
        rudisha b''

    eleza write(self, *args):
        pass

    eleza close(self):
        pass

kundi _Hqxcoderengine:
    """Write data to the coder kwenye 3-byte chunks"""

    eleza __init__(self, ofp):
        self.ofp = ofp
        self.data = b''
        self.hqxdata = b''
        self.linelen = LINELEN - 1

    eleza write(self, data):
        self.data = self.data + data
        datalen = len(self.data)
        todo = (datalen // 3) * 3
        data = self.data[:todo]
        self.data = self.data[todo:]
        ikiwa sio data:
            return
        self.hqxdata = self.hqxdata + binascii.b2a_hqx(data)
        self._flush(0)

    eleza _flush(self, force):
        first = 0
        wakati first <= len(self.hqxdata) - self.linelen:
            last = first + self.linelen
            self.ofp.write(self.hqxdata[first:last] + b'\n')
            self.linelen = LINELEN
            first = last
        self.hqxdata = self.hqxdata[first:]
        ikiwa force:
            self.ofp.write(self.hqxdata + b':\n')

    eleza close(self):
        ikiwa self.data:
            self.hqxdata = self.hqxdata + binascii.b2a_hqx(self.data)
        self._flush(1)
        self.ofp.close()
        toa self.ofp

kundi _Rlecoderengine:
    """Write data to the RLE-coder kwenye suitably large chunks"""

    eleza __init__(self, ofp):
        self.ofp = ofp
        self.data = b''

    eleza write(self, data):
        self.data = self.data + data
        ikiwa len(self.data) < REASONABLY_LARGE:
            return
        rledata = binascii.rlecode_hqx(self.data)
        self.ofp.write(rledata)
        self.data = b''

    eleza close(self):
        ikiwa self.data:
            rledata = binascii.rlecode_hqx(self.data)
            self.ofp.write(rledata)
        self.ofp.close()
        toa self.ofp

kundi BinHex:
    eleza __init__(self, name_finfo_dlen_rlen, ofp):
        name, finfo, dlen, rlen = name_finfo_dlen_rlen
        close_on_error = Uongo
        ikiwa isinstance(ofp, str):
            ofname = ofp
            ofp = io.open(ofname, 'wb')
            close_on_error = Kweli
        jaribu:
            ofp.write(b'(This file must be converted ukijumuisha BinHex 4.0)\r\r:')
            hqxer = _Hqxcoderengine(ofp)
            self.ofp = _Rlecoderengine(hqxer)
            self.crc = 0
            ikiwa finfo ni Tupu:
                finfo = FInfo()
            self.dlen = dlen
            self.rlen = rlen
            self._writeinfo(name, finfo)
            self.state = _DID_HEADER
        tatizo:
            ikiwa close_on_error:
                ofp.close()
            raise

    eleza _writeinfo(self, name, finfo):
        nl = len(name)
        ikiwa nl > 63:
             ashiria Error('Filename too long')
        d = bytes([nl]) + name.encode("latin-1") + b'\0'
        tp, cr = finfo.Type, finfo.Creator
        ikiwa isinstance(tp, str):
            tp = tp.encode("latin-1")
        ikiwa isinstance(cr, str):
            cr = cr.encode("latin-1")
        d2 = tp + cr

        # Force all structs to be packed ukijumuisha big-endian
        d3 = struct.pack('>h', finfo.Flags)
        d4 = struct.pack('>ii', self.dlen, self.rlen)
        info = d + d2 + d3 + d4
        self._write(info)
        self._writecrc()

    eleza _write(self, data):
        self.crc = binascii.crc_hqx(data, self.crc)
        self.ofp.write(data)

    eleza _writecrc(self):
        # XXXX Should this be here??
        # self.crc = binascii.crc_hqx('\0\0', self.crc)
        ikiwa self.crc < 0:
            fmt = '>h'
        isipokua:
            fmt = '>H'
        self.ofp.write(struct.pack(fmt, self.crc))
        self.crc = 0

    eleza write(self, data):
        ikiwa self.state != _DID_HEADER:
             ashiria Error('Writing data at the wrong time')
        self.dlen = self.dlen - len(data)
        self._write(data)

    eleza close_data(self):
        ikiwa self.dlen != 0:
             ashiria Error('Incorrect data size, diff=%r' % (self.rlen,))
        self._writecrc()
        self.state = _DID_DATA

    eleza write_rsrc(self, data):
        ikiwa self.state < _DID_DATA:
            self.close_data()
        ikiwa self.state != _DID_DATA:
             ashiria Error('Writing resource data at the wrong time')
        self.rlen = self.rlen - len(data)
        self._write(data)

    eleza close(self):
        ikiwa self.state ni Tupu:
            return
        jaribu:
            ikiwa self.state < _DID_DATA:
                self.close_data()
            ikiwa self.state != _DID_DATA:
                 ashiria Error('Close at the wrong time')
            ikiwa self.rlen != 0:
                 ashiria Error("Incorrect resource-datasize, diff=%r" % (self.rlen,))
            self._writecrc()
        mwishowe:
            self.state = Tupu
            ofp = self.ofp
            toa self.ofp
            ofp.close()

eleza binhex(inp, out):
    """binhex(infilename, outfilename): create binhex-encoded copy of a file"""
    finfo = getfileinfo(inp)
    ofp = BinHex(finfo, out)

    ukijumuisha io.open(inp, 'rb') as ifp:
        # XXXX Do textfile translation on non-mac systems
        wakati Kweli:
            d = ifp.read(128000)
            ikiwa sio d: koma
            ofp.write(d)
        ofp.close_data()

    ifp = openrsrc(inp, 'rb')
    wakati Kweli:
        d = ifp.read(128000)
        ikiwa sio d: koma
        ofp.write_rsrc(d)
    ofp.close()
    ifp.close()

kundi _Hqxdecoderengine:
    """Read data via the decoder kwenye 4-byte chunks"""

    eleza __init__(self, ifp):
        self.ifp = ifp
        self.eof = 0

    eleza read(self, totalwtd):
        """Read at least wtd bytes (or until EOF)"""
        decdata = b''
        wtd = totalwtd
        #
        # The loop here ni convoluted, since we don't really now how
        # much to decode: there may be newlines kwenye the incoming data.
        wakati wtd > 0:
            ikiwa self.eof: rudisha decdata
            wtd = ((wtd + 2) // 3) * 4
            data = self.ifp.read(wtd)
            #
            # Next problem: there may sio be a complete number of
            # bytes kwenye what we pass to a2b. Solve by yet another
            # loop.
            #
            wakati Kweli:
                jaribu:
                    decdatacur, self.eof = binascii.a2b_hqx(data)
                    koma
                except binascii.Incomplete:
                    pass
                newdata = self.ifp.read(1)
                ikiwa sio newdata:
                     ashiria Error('Premature EOF on binhex file')
                data = data + newdata
            decdata = decdata + decdatacur
            wtd = totalwtd - len(decdata)
            ikiwa sio decdata na sio self.eof:
                 ashiria Error('Premature EOF on binhex file')
        rudisha decdata

    eleza close(self):
        self.ifp.close()

kundi _Rledecoderengine:
    """Read data via the RLE-coder"""

    eleza __init__(self, ifp):
        self.ifp = ifp
        self.pre_buffer = b''
        self.post_buffer = b''
        self.eof = 0

    eleza read(self, wtd):
        ikiwa wtd > len(self.post_buffer):
            self._fill(wtd - len(self.post_buffer))
        rv = self.post_buffer[:wtd]
        self.post_buffer = self.post_buffer[wtd:]
        rudisha rv

    eleza _fill(self, wtd):
        self.pre_buffer = self.pre_buffer + self.ifp.read(wtd + 4)
        ikiwa self.ifp.eof:
            self.post_buffer = self.post_buffer + \
                binascii.rledecode_hqx(self.pre_buffer)
            self.pre_buffer = b''
            return

        #
        # Obfuscated code ahead. We have to take care that we don't
        # end up ukijumuisha an orphaned RUNCHAR later on. So, we keep a couple
        # of bytes kwenye the buffer, depending on what the end of
        # the buffer looks like:
        # '\220\0\220' - Keep 3 bytes: repeated \220 (escaped as \220\0)
        # '?\220' - Keep 2 bytes: repeated something-else
        # '\220\0' - Escaped \220: Keep 2 bytes.
        # '?\220?' - Complete repeat sequence: decode all
        # otherwise: keep 1 byte.
        #
        mark = len(self.pre_buffer)
        ikiwa self.pre_buffer[-3:] == RUNCHAR + b'\0' + RUNCHAR:
            mark = mark - 3
        elikiwa self.pre_buffer[-1:] == RUNCHAR:
            mark = mark - 2
        elikiwa self.pre_buffer[-2:] == RUNCHAR + b'\0':
            mark = mark - 2
        elikiwa self.pre_buffer[-2:-1] == RUNCHAR:
            pass # Decode all
        isipokua:
            mark = mark - 1

        self.post_buffer = self.post_buffer + \
            binascii.rledecode_hqx(self.pre_buffer[:mark])
        self.pre_buffer = self.pre_buffer[mark:]

    eleza close(self):
        self.ifp.close()

kundi HexBin:
    eleza __init__(self, ifp):
        ikiwa isinstance(ifp, str):
            ifp = io.open(ifp, 'rb')
        #
        # Find initial colon.
        #
        wakati Kweli:
            ch = ifp.read(1)
            ikiwa sio ch:
                 ashiria Error("No binhex data found")
            # Cater kila \r\n terminated lines (which show up as \n\r, hence
            # all lines start ukijumuisha \r)
            ikiwa ch == b'\r':
                endelea
            ikiwa ch == b':':
                koma

        hqxifp = _Hqxdecoderengine(ifp)
        self.ifp = _Rledecoderengine(hqxifp)
        self.crc = 0
        self._readheader()

    eleza _read(self, len):
        data = self.ifp.read(len)
        self.crc = binascii.crc_hqx(data, self.crc)
        rudisha data

    eleza _checkcrc(self):
        filecrc = struct.unpack('>h', self.ifp.read(2))[0] & 0xffff
        #self.crc = binascii.crc_hqx('\0\0', self.crc)
        # XXXX Is this needed??
        self.crc = self.crc & 0xffff
        ikiwa filecrc != self.crc:
             ashiria Error('CRC error, computed %x, read %x'
                        % (self.crc, filecrc))
        self.crc = 0

    eleza _readheader(self):
        len = self._read(1)
        fname = self._read(ord(len))
        rest = self._read(1 + 4 + 4 + 2 + 4 + 4)
        self._checkcrc()

        type = rest[1:5]
        creator = rest[5:9]
        flags = struct.unpack('>h', rest[9:11])[0]
        self.dlen = struct.unpack('>l', rest[11:15])[0]
        self.rlen = struct.unpack('>l', rest[15:19])[0]

        self.FName = fname
        self.FInfo = FInfo()
        self.FInfo.Creator = creator
        self.FInfo.Type = type
        self.FInfo.Flags = flags

        self.state = _DID_HEADER

    eleza read(self, *n):
        ikiwa self.state != _DID_HEADER:
             ashiria Error('Read data at wrong time')
        ikiwa n:
            n = n[0]
            n = min(n, self.dlen)
        isipokua:
            n = self.dlen
        rv = b''
        wakati len(rv) < n:
            rv = rv + self._read(n-len(rv))
        self.dlen = self.dlen - n
        rudisha rv

    eleza close_data(self):
        ikiwa self.state != _DID_HEADER:
             ashiria Error('close_data at wrong time')
        ikiwa self.dlen:
            dummy = self._read(self.dlen)
        self._checkcrc()
        self.state = _DID_DATA

    eleza read_rsrc(self, *n):
        ikiwa self.state == _DID_HEADER:
            self.close_data()
        ikiwa self.state != _DID_DATA:
             ashiria Error('Read resource data at wrong time')
        ikiwa n:
            n = n[0]
            n = min(n, self.rlen)
        isipokua:
            n = self.rlen
        self.rlen = self.rlen - n
        rudisha self._read(n)

    eleza close(self):
        ikiwa self.state ni Tupu:
            return
        jaribu:
            ikiwa self.rlen:
                dummy = self.read_rsrc(self.rlen)
            self._checkcrc()
        mwishowe:
            self.state = Tupu
            self.ifp.close()

eleza hexbin(inp, out):
    """hexbin(infilename, outfilename) - Decode binhexed file"""
    ifp = HexBin(inp)
    finfo = ifp.FInfo
    ikiwa sio out:
        out = ifp.FName

    ukijumuisha io.open(out, 'wb') as ofp:
        # XXXX Do translation on non-mac systems
        wakati Kweli:
            d = ifp.read(128000)
            ikiwa sio d: koma
            ofp.write(d)
    ifp.close_data()

    d = ifp.read_rsrc(128000)
    ikiwa d:
        ofp = openrsrc(out, 'wb')
        ofp.write(d)
        wakati Kweli:
            d = ifp.read_rsrc(128000)
            ikiwa sio d: koma
            ofp.write(d)
        ofp.close()

    ifp.close()
