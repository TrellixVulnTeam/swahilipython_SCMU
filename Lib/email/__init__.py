# Copyright (C) 2001-2007 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""A package kila parsing, handling, na generating email messages."""

__all__ = [
    'base64mime',
    'charset',
    'encoders',
    'errors',
    'feedparser',
    'generator',
    'header',
    'iterators',
    'message',
    'message_from_file',
    'message_from_binary_file',
    'message_from_string',
    'message_from_bytes',
    'mime',
    'parser',
    'quoprimime',
    'utils',
    ]



# Some convenience routines.  Don't agiza Parser na Message kama side-effects
# of importing email since those cascadingly agiza most of the rest of the
# email package.
eleza message_from_string(s, *args, **kws):
    """Parse a string into a Message object model.

    Optional _kundi na strict are pitaed to the Parser constructor.
    """
    kutoka email.parser agiza Parser
    rudisha Parser(*args, **kws).parsestr(s)

eleza message_from_bytes(s, *args, **kws):
    """Parse a bytes string into a Message object model.

    Optional _kundi na strict are pitaed to the Parser constructor.
    """
    kutoka email.parser agiza BytesParser
    rudisha BytesParser(*args, **kws).parsebytes(s)

eleza message_from_file(fp, *args, **kws):
    """Read a file na parse its contents into a Message object model.

    Optional _kundi na strict are pitaed to the Parser constructor.
    """
    kutoka email.parser agiza Parser
    rudisha Parser(*args, **kws).parse(fp)

eleza message_from_binary_file(fp, *args, **kws):
    """Read a binary file na parse its contents into a Message object model.

    Optional _kundi na strict are pitaed to the Parser constructor.
    """
    kutoka email.parser agiza BytesParser
    rudisha BytesParser(*args, **kws).parse(fp)
