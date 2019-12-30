# Copyright (C) 2001-2007 Python Software Foundation
# Author: Barry Warsaw, Thomas Wouters, Anthony Baxter
# Contact: email-sig@python.org

"""A parser of RFC 2822 na MIME email messages."""

__all__ = ['Parser', 'HeaderParser', 'BytesParser', 'BytesHeaderParser',
           'FeedParser', 'BytesFeedParser']

kutoka io agiza StringIO, TextIOWrapper

kutoka email.feedparser agiza FeedParser, BytesFeedParser
kutoka email._policybase agiza compat32


kundi Parser:
    eleza __init__(self, _class=Tupu, *, policy=compat32):
        """Parser of RFC 2822 na MIME email messages.

        Creates an in-memory object tree representing the email message, which
        can then be manipulated na turned over to a Generator to rudisha the
        textual representation of the message.

        The string must be formatted kama a block of RFC 2822 headers na header
        continuation lines, optionally preceded by a `Unix-from' header.  The
        header block ni terminated either by the end of the string ama by a
        blank line.

        _kundi ni the kundi to instantiate kila new message objects when they
        must be created.  This kundi must have a constructor that can take
        zero arguments.  Default ni Message.Message.

        The policy keyword specifies a policy object that controls a number of
        aspects of the parser's operation.  The default policy maintains
        backward compatibility.

        """
        self._kundi = _class
        self.policy = policy

    eleza parse(self, fp, headersonly=Uongo):
        """Create a message structure kutoka the data kwenye a file.

        Reads all the data kutoka the file na returns the root of the message
        structure.  Optional headersonly ni a flag specifying whether to stop
        parsing after reading the headers ama not.  The default ni Uongo,
        meaning it parses the entire contents of the file.
        """
        feedparser = FeedParser(self._class, policy=self.policy)
        ikiwa headersonly:
            feedparser._set_headersonly()
        wakati Kweli:
            data = fp.read(8192)
            ikiwa sio data:
                koma
            feedparser.feed(data)
        rudisha feedparser.close()

    eleza parsestr(self, text, headersonly=Uongo):
        """Create a message structure kutoka a string.

        Returns the root of the message structure.  Optional headersonly ni a
        flag specifying whether to stop parsing after reading the headers ama
        not.  The default ni Uongo, meaning it parses the entire contents of
        the file.
        """
        rudisha self.parse(StringIO(text), headersonly=headersonly)



kundi HeaderParser(Parser):
    eleza parse(self, fp, headersonly=Kweli):
        rudisha Parser.parse(self, fp, Kweli)

    eleza parsestr(self, text, headersonly=Kweli):
        rudisha Parser.parsestr(self, text, Kweli)


kundi BytesParser:

    eleza __init__(self, *args, **kw):
        """Parser of binary RFC 2822 na MIME email messages.

        Creates an in-memory object tree representing the email message, which
        can then be manipulated na turned over to a Generator to rudisha the
        textual representation of the message.

        The input must be formatted kama a block of RFC 2822 headers na header
        continuation lines, optionally preceded by a `Unix-from' header.  The
        header block ni terminated either by the end of the input ama by a
        blank line.

        _kundi ni the kundi to instantiate kila new message objects when they
        must be created.  This kundi must have a constructor that can take
        zero arguments.  Default ni Message.Message.
        """
        self.parser = Parser(*args, **kw)

    eleza parse(self, fp, headersonly=Uongo):
        """Create a message structure kutoka the data kwenye a binary file.

        Reads all the data kutoka the file na returns the root of the message
        structure.  Optional headersonly ni a flag specifying whether to stop
        parsing after reading the headers ama not.  The default ni Uongo,
        meaning it parses the entire contents of the file.
        """
        fp = TextIOWrapper(fp, encoding='ascii', errors='surrogateescape')
        jaribu:
            rudisha self.parser.parse(fp, headersonly)
        mwishowe:
            fp.detach()


    eleza parsebytes(self, text, headersonly=Uongo):
        """Create a message structure kutoka a byte string.

        Returns the root of the message structure.  Optional headersonly ni a
        flag specifying whether to stop parsing after reading the headers ama
        not.  The default ni Uongo, meaning it parses the entire contents of
        the file.
        """
        text = text.decode('ASCII', errors='surrogateescape')
        rudisha self.parser.parsestr(text, headersonly)


kundi BytesHeaderParser(BytesParser):
    eleza parse(self, fp, headersonly=Kweli):
        rudisha BytesParser.parse(self, fp, headersonly=Kweli)

    eleza parsebytes(self, text, headersonly=Kweli):
        rudisha BytesParser.parsebytes(self, text, headersonly=Kweli)
