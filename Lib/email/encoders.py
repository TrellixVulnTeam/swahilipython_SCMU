# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Encodings na related functions."""

__all__ = [
    'encode_7or8bit',
    'encode_base64',
    'encode_noop',
    'encode_quopri',
    ]


kutoka base64 agiza encodebytes kama _bencode
kutoka quopri agiza encodestring kama _encodestring



eleza _qencode(s):
    enc = _encodestring(s, quotetabs=Kweli)
    # Must encode spaces, which quopri.encodestring() doesn't do
    rudisha enc.replace(b' ', b'=20')


eleza encode_base64(msg):
    """Encode the message's payload kwenye Base64.

    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload(decode=Kweli)
    encdata = str(_bencode(orig), 'ascii')
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'base64'



eleza encode_quopri(msg):
    """Encode the message's payload kwenye quoted-printable.

    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload(decode=Kweli)
    encdata = _qencode(orig)
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'quoted-printable'



eleza encode_7or8bit(msg):
    """Set the Content-Transfer-Encoding header to 7bit ama 8bit."""
    orig = msg.get_payload(decode=Kweli)
    ikiwa orig ni Tupu:
        # There's no payload.  For backwards compatibility we use 7bit
        msg['Content-Transfer-Encoding'] = '7bit'
        return
    # We play a trick to make this go fast.  If decoding kutoka ASCII succeeds,
    # we know the data must be 7bit, otherwise treat it kama 8bit.
    jaribu:
        orig.decode('ascii')
    tatizo UnicodeError:
        msg['Content-Transfer-Encoding'] = '8bit'
    isipokua:
        msg['Content-Transfer-Encoding'] = '7bit'



eleza encode_noop(msg):
    """Do nothing."""
