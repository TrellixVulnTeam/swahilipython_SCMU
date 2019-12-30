# Copyright (C) 2004-2006 Python Software Foundation
# Authors: Baxter, Wouters na Warsaw
# Contact: email-sig@python.org

"""FeedParser - An email feed parser.

The feed parser implements an interface kila incrementally parsing an email
message, line by line.  This has advantages kila certain applications, such as
those reading email messages off a socket.

FeedParser.feed() ni the primary interface kila pushing new data into the
parser.  It returns when there's nothing more it can do ukijumuisha the available
data.  When you have no more data to push into the parser, call .close().
This completes the parsing na returns the root message object.

The other advantage of this parser ni that it will never ashiria a parsing
exception.  Instead, when it finds something unexpected, it adds a 'defect' to
the current message.  Defects are just instances that live on the message
object's .defects attribute.
"""

__all__ = ['FeedParser', 'BytesFeedParser']

agiza re

kutoka email agiza errors
kutoka email._policybase agiza compat32
kutoka collections agiza deque
kutoka io agiza StringIO

NLCRE = re.compile(r'\r\n|\r|\n')
NLCRE_bol = re.compile(r'(\r\n|\r|\n)')
NLCRE_eol = re.compile(r'(\r\n|\r|\n)\Z')
NLCRE_crack = re.compile(r'(\r\n|\r|\n)')
# RFC 2822 $3.6.8 Optional fields.  ftext ni %d33-57 / %d59-126, Any character
# tatizo controls, SP, na ":".
headerRE = re.compile(r'^(From |[\041-\071\073-\176]*:|[\t ])')
EMPTYSTRING = ''
NL = '\n'

NeedMoreData = object()



kundi BufferedSubFile(object):
    """A file-ish object that can have new data loaded into it.

    You can also push na pop line-matching predicates onto a stack.  When the
    current predicate matches the current line, a false EOF response
    (i.e. empty string) ni returned instead.  This lets the parser adhere to a
    simple abstraction -- it parses until EOF closes the current message.
    """
    eleza __init__(self):
        # Text stream of the last partial line pushed into this object.
        # See issue 22233 kila why this ni a text stream na sio a list.
        self._partial = StringIO(newline='')
        # A deque of full, pushed lines
        self._lines = deque()
        # The stack of false-EOF checking predicates.
        self._eofstack = []
        # A flag indicating whether the file has been closed ama not.
        self._closed = Uongo

    eleza push_eof_matcher(self, pred):
        self._eofstack.append(pred)

    eleza pop_eof_matcher(self):
        rudisha self._eofstack.pop()

    eleza close(self):
        # Don't forget any trailing partial line.
        self._partial.seek(0)
        self.pushlines(self._partial.readlines())
        self._partial.seek(0)
        self._partial.truncate()
        self._closed = Kweli

    eleza readline(self):
        ikiwa sio self._lines:
            ikiwa self._closed:
                rudisha ''
            rudisha NeedMoreData
        # Pop the line off the stack na see ikiwa it matches the current
        # false-EOF predicate.
        line = self._lines.popleft()
        # RFC 2046, section 5.1.2 requires us to recognize outer level
        # boundaries at any level of inner nesting.  Do this, but be sure it's
        # kwenye the order of most to least nested.
        kila ateof kwenye reversed(self._eofstack):
            ikiwa ateof(line):
                # We're at the false EOF.  But push the last line back first.
                self._lines.appendleft(line)
                rudisha ''
        rudisha line

    eleza unreadline(self, line):
        # Let the consumer push a line back into the buffer.
        assert line ni sio NeedMoreData
        self._lines.appendleft(line)

    eleza push(self, data):
        """Push some new data into this object."""
        self._partial.write(data)
        ikiwa '\n' haiko kwenye data na '\r' haiko kwenye data:
            # No new complete lines, wait kila more.
            rudisha

        # Crack into lines, preserving the linesep characters.
        self._partial.seek(0)
        parts = self._partial.readlines()
        self._partial.seek(0)
        self._partial.truncate()

        # If the last element of the list does sio end kwenye a newline, then treat
        # it kama a partial line.  We only check kila '\n' here because a line
        # ending ukijumuisha '\r' might be a line that was split kwenye the middle of a
        # '\r\n' sequence (see bugs 1555570 na 1721862).
        ikiwa sio parts[-1].endswith('\n'):
            self._partial.write(parts.pop())
        self.pushlines(parts)

    eleza pushlines(self, lines):
        self._lines.extend(lines)

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        line = self.readline()
        ikiwa line == '':
            ashiria StopIteration
        rudisha line



kundi FeedParser:
    """A feed-style parser of email."""

    eleza __init__(self, _factory=Tupu, *, policy=compat32):
        """_factory ni called ukijumuisha no arguments to create a new message obj

        The policy keyword specifies a policy object that controls a number of
        aspects of the parser's operation.  The default policy maintains
        backward compatibility.

        """
        self.policy = policy
        self._old_style_factory = Uongo
        ikiwa _factory ni Tupu:
            ikiwa policy.message_factory ni Tupu:
                kutoka email.message agiza Message
                self._factory = Message
            isipokua:
                self._factory = policy.message_factory
        isipokua:
            self._factory = _factory
            jaribu:
                _factory(policy=self.policy)
            tatizo TypeError:
                # Assume this ni an old-style factory
                self._old_style_factory = Kweli
        self._input = BufferedSubFile()
        self._msgstack = []
        self._parse = self._parsegen().__next__
        self._cur = Tupu
        self._last = Tupu
        self._headersonly = Uongo

    # Non-public interface kila supporting Parser's headersonly flag
    eleza _set_headersonly(self):
        self._headersonly = Kweli

    eleza feed(self, data):
        """Push more data into the parser."""
        self._input.push(data)
        self._call_parse()

    eleza _call_parse(self):
        jaribu:
            self._parse()
        tatizo StopIteration:
            pita

    eleza close(self):
        """Parse all remaining data na rudisha the root message object."""
        self._input.close()
        self._call_parse()
        root = self._pop_message()
        assert sio self._msgstack
        # Look kila final set of defects
        ikiwa root.get_content_maintype() == 'multipart' \
               na sio root.is_multipart():
            defect = errors.MultipartInvariantViolationDefect()
            self.policy.handle_defect(root, defect)
        rudisha root

    eleza _new_message(self):
        ikiwa self._old_style_factory:
            msg = self._factory()
        isipokua:
            msg = self._factory(policy=self.policy)
        ikiwa self._cur na self._cur.get_content_type() == 'multipart/digest':
            msg.set_default_type('message/rfc822')
        ikiwa self._msgstack:
            self._msgstack[-1].attach(msg)
        self._msgstack.append(msg)
        self._cur = msg
        self._last = msg

    eleza _pop_message(self):
        retval = self._msgstack.pop()
        ikiwa self._msgstack:
            self._cur = self._msgstack[-1]
        isipokua:
            self._cur = Tupu
        rudisha retval

    eleza _parsegen(self):
        # Create a new message na start by parsing headers.
        self._new_message()
        headers = []
        # Collect the headers, searching kila a line that doesn't match the RFC
        # 2822 header ama continuation pattern (including an empty line).
        kila line kwenye self._input:
            ikiwa line ni NeedMoreData:
                tuma NeedMoreData
                endelea
            ikiwa sio headerRE.match(line):
                # If we saw the RFC defined header/body separator
                # (i.e. newline), just throw it away. Otherwise the line is
                # part of the body so push it back.
                ikiwa sio NLCRE.match(line):
                    defect = errors.MissingHeaderBodySeparatorDefect()
                    self.policy.handle_defect(self._cur, defect)
                    self._input.unreadline(line)
                koma
            headers.append(line)
        # Done ukijumuisha the headers, so parse them na figure out what we're
        # supposed to see kwenye the body of the message.
        self._parse_headers(headers)
        # Headers-only parsing ni a backwards compatibility hack, which was
        # necessary kwenye the older parser, which could ashiria errors.  All
        # remaining lines kwenye the input are thrown into the message body.
        ikiwa self._headersonly:
            lines = []
            wakati Kweli:
                line = self._input.readline()
                ikiwa line ni NeedMoreData:
                    tuma NeedMoreData
                    endelea
                ikiwa line == '':
                    koma
                lines.append(line)
            self._cur.set_payload(EMPTYSTRING.join(lines))
            rudisha
        ikiwa self._cur.get_content_type() == 'message/delivery-status':
            # message/delivery-status contains blocks of headers separated by
            # a blank line.  We'll represent each header block kama a separate
            # nested message object, but the processing ni a bit different
            # than standard message/* types because there ni no body kila the
            # nested messages.  A blank line separates the subparts.
            wakati Kweli:
                self._input.push_eof_matcher(NLCRE.match)
                kila retval kwenye self._parsegen():
                    ikiwa retval ni NeedMoreData:
                        tuma NeedMoreData
                        endelea
                    koma
                msg = self._pop_message()
                # We need to pop the EOF matcher kwenye order to tell ikiwa we're at
                # the end of the current file, sio the end of the last block
                # of message headers.
                self._input.pop_eof_matcher()
                # The input stream must be sitting at the newline ama at the
                # EOF.  We want to see ikiwa we're at the end of this subpart, so
                # first consume the blank line, then test the next line to see
                # ikiwa we're at this subpart's EOF.
                wakati Kweli:
                    line = self._input.readline()
                    ikiwa line ni NeedMoreData:
                        tuma NeedMoreData
                        endelea
                    koma
                wakati Kweli:
                    line = self._input.readline()
                    ikiwa line ni NeedMoreData:
                        tuma NeedMoreData
                        endelea
                    koma
                ikiwa line == '':
                    koma
                # Not at EOF so this ni a line we're going to need.
                self._input.unreadline(line)
            rudisha
        ikiwa self._cur.get_content_maintype() == 'message':
            # The message claims to be a message/* type, then what follows is
            # another RFC 2822 message.
            kila retval kwenye self._parsegen():
                ikiwa retval ni NeedMoreData:
                    tuma NeedMoreData
                    endelea
                koma
            self._pop_message()
            rudisha
        ikiwa self._cur.get_content_maintype() == 'multipart':
            boundary = self._cur.get_boundary()
            ikiwa boundary ni Tupu:
                # The message /claims/ to be a multipart but it has sio
                # defined a boundary.  That's a problem which we'll handle by
                # reading everything until the EOF na marking the message as
                # defective.
                defect = errors.NoBoundaryInMultipartDefect()
                self.policy.handle_defect(self._cur, defect)
                lines = []
                kila line kwenye self._input:
                    ikiwa line ni NeedMoreData:
                        tuma NeedMoreData
                        endelea
                    lines.append(line)
                self._cur.set_payload(EMPTYSTRING.join(lines))
                rudisha
            # Make sure a valid content type was specified per RFC 2045:6.4.
            ikiwa (str(self._cur.get('content-transfer-encoding', '8bit')).lower()
                    haiko kwenye ('7bit', '8bit', 'binary')):
                defect = errors.InvalidMultipartContentTransferEncodingDefect()
                self.policy.handle_defect(self._cur, defect)
            # Create a line match predicate which matches the inter-part
            # boundary kama well kama the end-of-multipart boundary.  Don't push
            # this onto the input stream until we've scanned past the
            # preamble.
            separator = '--' + boundary
            boundaryre = re.compile(
                '(?P<sep>' + re.escape(separator) +
                r')(?P<end>--)?(?P<ws>[ \t]*)(?P<linesep>\r\n|\r|\n)?$')
            capturing_preamble = Kweli
            preamble = []
            linesep = Uongo
            close_boundary_seen = Uongo
            wakati Kweli:
                line = self._input.readline()
                ikiwa line ni NeedMoreData:
                    tuma NeedMoreData
                    endelea
                ikiwa line == '':
                    koma
                mo = boundaryre.match(line)
                ikiwa mo:
                    # If we're looking at the end boundary, we're done with
                    # this multipart.  If there was a newline at the end of
                    # the closing boundary, then we need to initialize the
                    # epilogue ukijumuisha the empty string (see below).
                    ikiwa mo.group('end'):
                        close_boundary_seen = Kweli
                        linesep = mo.group('linesep')
                        koma
                    # We saw an inter-part boundary.  Were we kwenye the preamble?
                    ikiwa capturing_preamble:
                        ikiwa preamble:
                            # According to RFC 2046, the last newline belongs
                            # to the boundary.
                            lastline = preamble[-1]
                            eolmo = NLCRE_eol.search(lastline)
                            ikiwa eolmo:
                                preamble[-1] = lastline[:-len(eolmo.group(0))]
                            self._cur.preamble = EMPTYSTRING.join(preamble)
                        capturing_preamble = Uongo
                        self._input.unreadline(line)
                        endelea
                    # We saw a boundary separating two parts.  Consume any
                    # multiple boundary lines that may be following.  Our
                    # interpretation of RFC 2046 BNF grammar does sio produce
                    # body parts within such double boundaries.
                    wakati Kweli:
                        line = self._input.readline()
                        ikiwa line ni NeedMoreData:
                            tuma NeedMoreData
                            endelea
                        mo = boundaryre.match(line)
                        ikiwa sio mo:
                            self._input.unreadline(line)
                            koma
                    # Recurse to parse this subpart; the input stream points
                    # at the subpart's first line.
                    self._input.push_eof_matcher(boundaryre.match)
                    kila retval kwenye self._parsegen():
                        ikiwa retval ni NeedMoreData:
                            tuma NeedMoreData
                            endelea
                        koma
                    # Because of RFC 2046, the newline preceding the boundary
                    # separator actually belongs to the boundary, sio the
                    # previous subpart's payload (or epilogue ikiwa the previous
                    # part ni a multipart).
                    ikiwa self._last.get_content_maintype() == 'multipart':
                        epilogue = self._last.epilogue
                        ikiwa epilogue == '':
                            self._last.epilogue = Tupu
                        lasivyo epilogue ni sio Tupu:
                            mo = NLCRE_eol.search(epilogue)
                            ikiwa mo:
                                end = len(mo.group(0))
                                self._last.epilogue = epilogue[:-end]
                    isipokua:
                        payload = self._last._payload
                        ikiwa isinstance(payload, str):
                            mo = NLCRE_eol.search(payload)
                            ikiwa mo:
                                payload = payload[:-len(mo.group(0))]
                                self._last._payload = payload
                    self._input.pop_eof_matcher()
                    self._pop_message()
                    # Set the multipart up kila newline cleansing, which will
                    # happen ikiwa we're kwenye a nested multipart.
                    self._last = self._cur
                isipokua:
                    # I think we must be kwenye the preamble
                    assert capturing_preamble
                    preamble.append(line)
            # We've seen either the EOF ama the end boundary.  If we're still
            # capturing the preamble, we never saw the start boundary.  Note
            # that kama a defect na store the captured text kama the payload.
            ikiwa capturing_preamble:
                defect = errors.StartBoundaryNotFoundDefect()
                self.policy.handle_defect(self._cur, defect)
                self._cur.set_payload(EMPTYSTRING.join(preamble))
                epilogue = []
                kila line kwenye self._input:
                    ikiwa line ni NeedMoreData:
                        tuma NeedMoreData
                        endelea
                self._cur.epilogue = EMPTYSTRING.join(epilogue)
                rudisha
            # If we're sio processing the preamble, then we might have seen
            # EOF without seeing that end boundary...that ni also a defect.
            ikiwa sio close_boundary_seen:
                defect = errors.CloseBoundaryNotFoundDefect()
                self.policy.handle_defect(self._cur, defect)
                rudisha
            # Everything kutoka here to the EOF ni epilogue.  If the end boundary
            # ended kwenye a newline, we'll need to make sure the epilogue isn't
            # Tupu
            ikiwa linesep:
                epilogue = ['']
            isipokua:
                epilogue = []
            kila line kwenye self._input:
                ikiwa line ni NeedMoreData:
                    tuma NeedMoreData
                    endelea
                epilogue.append(line)
            # Any CRLF at the front of the epilogue ni sio technically part of
            # the epilogue.  Also, watch out kila an empty string epilogue,
            # which means a single newline.
            ikiwa epilogue:
                firstline = epilogue[0]
                bolmo = NLCRE_bol.match(firstline)
                ikiwa bolmo:
                    epilogue[0] = firstline[len(bolmo.group(0)):]
            self._cur.epilogue = EMPTYSTRING.join(epilogue)
            rudisha
        # Otherwise, it's some non-multipart type, so the entire rest of the
        # file contents becomes the payload.
        lines = []
        kila line kwenye self._input:
            ikiwa line ni NeedMoreData:
                tuma NeedMoreData
                endelea
            lines.append(line)
        self._cur.set_payload(EMPTYSTRING.join(lines))

    eleza _parse_headers(self, lines):
        # Passed a list of lines that make up the headers kila the current msg
        lastheader = ''
        lastvalue = []
        kila lineno, line kwenye enumerate(lines):
            # Check kila continuation
            ikiwa line[0] kwenye ' \t':
                ikiwa sio lastheader:
                    # The first line of the headers was a continuation.  This
                    # ni illegal, so let's note the defect, store the illegal
                    # line, na ignore it kila purposes of headers.
                    defect = errors.FirstHeaderLineIsContinuationDefect(line)
                    self.policy.handle_defect(self._cur, defect)
                    endelea
                lastvalue.append(line)
                endelea
            ikiwa lastheader:
                self._cur.set_raw(*self.policy.header_source_parse(lastvalue))
                lastheader, lastvalue = '', []
            # Check kila envelope header, i.e. unix-from
            ikiwa line.startswith('From '):
                ikiwa lineno == 0:
                    # Strip off the trailing newline
                    mo = NLCRE_eol.search(line)
                    ikiwa mo:
                        line = line[:-len(mo.group(0))]
                    self._cur.set_unixfrom(line)
                    endelea
                lasivyo lineno == len(lines) - 1:
                    # Something looking like a unix-kutoka at the end - it's
                    # probably the first line of the body, so push back the
                    # line na stop.
                    self._input.unreadline(line)
                    rudisha
                isipokua:
                    # Weirdly placed unix-kutoka line.  Note this kama a defect
                    # na ignore it.
                    defect = errors.MisplacedEnvelopeHeaderDefect(line)
                    self._cur.defects.append(defect)
                    endelea
            # Split the line on the colon separating field name kutoka value.
            # There will always be a colon, because ikiwa there wasn't the part of
            # the parser that calls us would have started parsing the body.
            i = line.find(':')

            # If the colon ni on the start of the line the header ni clearly
            # malformed, but we might be able to salvage the rest of the
            # message. Track the error but keep going.
            ikiwa i == 0:
                defect = errors.InvalidHeaderDefect("Missing header name.")
                self._cur.defects.append(defect)
                endelea

            assert i>0, "_parse_headers fed line ukijumuisha no : na no leading WS"
            lastheader = line[:i]
            lastvalue = [line]
        # Done ukijumuisha all the lines, so handle the last header.
        ikiwa lastheader:
            self._cur.set_raw(*self.policy.header_source_parse(lastvalue))


kundi BytesFeedParser(FeedParser):
    """Like FeedParser, but feed accepts bytes."""

    eleza feed(self, data):
        super().feed(data.decode('ascii', 'surrogateescape'))
