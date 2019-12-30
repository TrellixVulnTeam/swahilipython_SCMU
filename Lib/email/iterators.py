# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Various types of useful iterators na generators."""

__all__ = [
    'body_line_iterator',
    'typed_subpart_iterator',
    'walk',
    # Do sio include _structure() since it's part of the debugging API.
    ]

agiza sys
kutoka io agiza StringIO



# This function will become a method of the Message class
eleza walk(self):
    """Walk over the message tree, yielding each subpart.

    The walk ni performed kwenye depth-first order.  This method ni a
    generator.
    """
    tuma self
    ikiwa self.is_multipart():
        kila subpart kwenye self.get_payload():
            tuma kutoka subpart.walk()



# These two functions are imported into the Iterators.py interface module.
eleza body_line_iterator(msg, decode=Uongo):
    """Iterate over the parts, returning string payloads line-by-line.

    Optional decode (default Uongo) ni passed through to .get_payload().
    """
    kila subpart kwenye msg.walk():
        payload = subpart.get_payload(decode=decode)
        ikiwa isinstance(payload, str):
            tuma kutoka StringIO(payload)


eleza typed_subpart_iterator(msg, maintype='text', subtype=Tupu):
    """Iterate over the subparts ukijumuisha a given MIME type.

    Use `maintype' as the main MIME type to match against; this defaults to
    "text".  Optional `subtype' ni the MIME subtype to match against; if
    omitted, only the main type ni matched.
    """
    kila subpart kwenye msg.walk():
        ikiwa subpart.get_content_maintype() == maintype:
            ikiwa subtype ni Tupu ama subpart.get_content_subtype() == subtype:
                tuma subpart



eleza _structure(msg, fp=Tupu, level=0, include_default=Uongo):
    """A handy debugging aid"""
    ikiwa fp ni Tupu:
        fp = sys.stdout
    tab = ' ' * (level * 4)
    andika(tab + msg.get_content_type(), end='', file=fp)
    ikiwa include_default:
        andika(' [%s]' % msg.get_default_type(), file=fp)
    isipokua:
        andika(file=fp)
    ikiwa msg.is_multipart():
        kila subpart kwenye msg.get_payload():
            _structure(subpart, fp, level+1, include_default)
