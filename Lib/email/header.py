# Copyright (C) 2002-2007 Python Software Foundation
# Author: Ben Gertzfield, Barry Warsaw
# Contact: email-sig@python.org

"""Header encoding na decoding functionality."""

__all__ = [
    'Header',
    'decode_header',
    'make_header',
    ]

agiza re
agiza binascii

agiza email.quoprimime
agiza email.base64mime

kutoka email.errors agiza HeaderParseError
kutoka email agiza charset as _charset
Charset = _charset.Charset

NL = '\n'
SPACE = ' '
BSPACE = b' '
SPACE8 = ' ' * 8
EMPTYSTRING = ''
MAXLINELEN = 78
FWS = ' \t'

USASCII = Charset('us-ascii')
UTF8 = Charset('utf-8')

# Match encoded-word strings kwenye the form =?charset?q?Hello_World?=
ecre = re.compile(r'''
  =\?                   # literal =?
  (?P<charset>[^?]*?)   # non-greedy up to the next ? ni the charset
  \?                    # literal ?
  (?P<encoding>[qQbB])  # either a "q" ama a "b", case insensitive
  \?                    # literal ?
  (?P<encoded>.*?)      # non-greedy up to the next ?= ni the encoded string
  \?=                   # literal ?=
  ''', re.VERBOSE | re.MULTILINE)

# Field name regexp, including trailing colon, but sio separating whitespace,
# according to RFC 2822.  Character range ni kutoka tilde to exclamation mark.
# For use ukijumuisha .match()
fcre = re.compile(r'[\041-\176]+:$')

# Find a header embedded kwenye a putative header value.  Used to check for
# header injection attack.
_embedded_header = re.compile(r'\n[^ \t]+:')



# Helpers
_max_append = email.quoprimime._max_append



eleza decode_header(header):
    """Decode a message header value without converting charset.

    Returns a list of (string, charset) pairs containing each of the decoded
    parts of the header.  Charset ni Tupu kila non-encoded parts of the header,
    otherwise a lower-case string containing the name of the character set
    specified kwenye the encoded string.

    header may be a string that may ama may sio contain RFC2047 encoded words,
    ama it may be a Header object.

    An email.errors.HeaderParseError may be raised when certain decoding error
    occurs (e.g. a base64 decoding exception).
    """
    # If it ni a Header object, we can just rudisha the encoded chunks.
    ikiwa hasattr(header, '_chunks'):
        rudisha [(_charset._encode(string, str(charset)), str(charset))
                    kila string, charset kwenye header._chunks]
    # If no encoding, just rudisha the header ukijumuisha no charset.
    ikiwa sio ecre.search(header):
        rudisha [(header, Tupu)]
    # First step ni to parse all the encoded parts into triplets of the form
    # (encoded_string, encoding, charset).  For unencoded strings, the last
    # two parts will be Tupu.
    words = []
    kila line kwenye header.splitlines():
        parts = ecre.split(line)
        first = Kweli
        wakati parts:
            unencoded = parts.pop(0)
            ikiwa first:
                unencoded = unencoded.lstrip()
                first = Uongo
            ikiwa unencoded:
                words.append((unencoded, Tupu, Tupu))
            ikiwa parts:
                charset = parts.pop(0).lower()
                encoding = parts.pop(0).lower()
                encoded = parts.pop(0)
                words.append((encoded, encoding, charset))
    # Now loop over words na remove words that consist of whitespace
    # between two encoded strings.
    droplist = []
    kila n, w kwenye enumerate(words):
        ikiwa n>1 na w[1] na words[n-2][1] na words[n-1][0].isspace():
            droplist.append(n-1)
    kila d kwenye reversed(droplist):
        toa words[d]

    # The next step ni to decode each encoded word by applying the reverse
    # base64 ama quopri transformation.  decoded_words ni now a list of the
    # form (decoded_word, charset).
    decoded_words = []
    kila encoded_string, encoding, charset kwenye words:
        ikiwa encoding ni Tupu:
            # This ni an unencoded word.
            decoded_words.append((encoded_string, charset))
        elikiwa encoding == 'q':
            word = email.quoprimime.header_decode(encoded_string)
            decoded_words.append((word, charset))
        elikiwa encoding == 'b':
            paderr = len(encoded_string) % 4   # Postel's law: add missing padding
            ikiwa paderr:
                encoded_string += '==='[:4 - paderr]
            jaribu:
                word = email.base64mime.decode(encoded_string)
            except binascii.Error:
                 ashiria HeaderParseError('Base64 decoding error')
            isipokua:
                decoded_words.append((word, charset))
        isipokua:
             ashiria AssertionError('Unexpected encoding: ' + encoding)
    # Now convert all words to bytes na collapse consecutive runs of
    # similarly encoded words.
    collapsed = []
    last_word = last_charset = Tupu
    kila word, charset kwenye decoded_words:
        ikiwa isinstance(word, str):
            word = bytes(word, 'raw-unicode-escape')
        ikiwa last_word ni Tupu:
            last_word = word
            last_charset = charset
        elikiwa charset != last_charset:
            collapsed.append((last_word, last_charset))
            last_word = word
            last_charset = charset
        elikiwa last_charset ni Tupu:
            last_word += BSPACE + word
        isipokua:
            last_word += word
    collapsed.append((last_word, last_charset))
    rudisha collapsed



eleza make_header(decoded_seq, maxlinelen=Tupu, header_name=Tupu,
                continuation_ws=' '):
    """Create a Header kutoka a sequence of pairs as returned by decode_header()

    decode_header() takes a header value string na returns a sequence of
    pairs of the format (decoded_string, charset) where charset ni the string
    name of the character set.

    This function takes one of those sequence of pairs na returns a Header
    instance.  Optional maxlinelen, header_name, na continuation_ws are as in
    the Header constructor.
    """
    h = Header(maxlinelen=maxlinelen, header_name=header_name,
               continuation_ws=continuation_ws)
    kila s, charset kwenye decoded_seq:
        # Tupu means us-ascii but we can simply pass it on to h.append()
        ikiwa charset ni sio Tupu na sio isinstance(charset, Charset):
            charset = Charset(charset)
        h.append(s, charset)
    rudisha h



kundi Header:
    eleza __init__(self, s=Tupu, charset=Tupu,
                 maxlinelen=Tupu, header_name=Tupu,
                 continuation_ws=' ', errors='strict'):
        """Create a MIME-compliant header that can contain many character sets.

        Optional s ni the initial header value.  If Tupu, the initial header
        value ni sio set.  You can later append to the header ukijumuisha .append()
        method calls.  s may be a byte string ama a Unicode string, but see the
        .append() documentation kila semantics.

        Optional charset serves two purposes: it has the same meaning as the
        charset argument to the .append() method.  It also sets the default
        character set kila all subsequent .append() calls that omit the charset
        argument.  If charset ni sio provided kwenye the constructor, the us-ascii
        charset ni used both as s's initial charset na as the default for
        subsequent .append() calls.

        The maximum line length can be specified explicitly via maxlinelen. For
        splitting the first line to a shorter value (to account kila the field
        header which isn't included kwenye s, e.g. `Subject') pass kwenye the name of
        the field kwenye header_name.  The default maxlinelen ni 78 as recommended
        by RFC 2822.

        continuation_ws must be RFC 2822 compliant folding whitespace (usually
        either a space ama a hard tab) which will be prepended to continuation
        lines.

        errors ni passed through to the .append() call.
        """
        ikiwa charset ni Tupu:
            charset = USASCII
        elikiwa sio isinstance(charset, Charset):
            charset = Charset(charset)
        self._charset = charset
        self._continuation_ws = continuation_ws
        self._chunks = []
        ikiwa s ni sio Tupu:
            self.append(s, charset, errors)
        ikiwa maxlinelen ni Tupu:
            maxlinelen = MAXLINELEN
        self._maxlinelen = maxlinelen
        ikiwa header_name ni Tupu:
            self._headerlen = 0
        isipokua:
            # Take the separating colon na space into account.
            self._headerlen = len(header_name) + 2

    eleza __str__(self):
        """Return the string value of the header."""
        self._normalize()
        uchunks = []
        lastcs = Tupu
        lastspace = Tupu
        kila string, charset kwenye self._chunks:
            # We must preserve spaces between encoded na non-encoded word
            # boundaries, which means kila us we need to add a space when we go
            # kutoka a charset to Tupu/us-ascii, ama kutoka Tupu/us-ascii to a
            # charset.  Only do this kila the second na subsequent chunks.
            # Don't add a space ikiwa the Tupu/us-ascii string already has
            # a space (trailing ama leading depending on transition)
            nextcs = charset
            ikiwa nextcs == _charset.UNKNOWN8BIT:
                original_bytes = string.encode('ascii', 'surrogateescape')
                string = original_bytes.decode('ascii', 'replace')
            ikiwa uchunks:
                hasspace = string na self._nonctext(string[0])
                ikiwa lastcs sio kwenye (Tupu, 'us-ascii'):
                    ikiwa nextcs kwenye (Tupu, 'us-ascii') na sio hasspace:
                        uchunks.append(SPACE)
                        nextcs = Tupu
                elikiwa nextcs sio kwenye (Tupu, 'us-ascii') na sio lastspace:
                    uchunks.append(SPACE)
            lastspace = string na self._nonctext(string[-1])
            lastcs = nextcs
            uchunks.append(string)
        rudisha EMPTYSTRING.join(uchunks)

    # Rich comparison operators kila equality only.  BAW: does it make sense to
    # have ama explicitly disable <, <=, >, >= operators?
    eleza __eq__(self, other):
        # other may be a Header ama a string.  Both are fine so coerce
        # ourselves to a unicode (of the unencoded header value), swap the
        # args na do another comparison.
        rudisha other == str(self)

    eleza append(self, s, charset=Tupu, errors='strict'):
        """Append a string to the MIME header.

        Optional charset, ikiwa given, should be a Charset instance ama the name
        of a character set (which will be converted to a Charset instance).  A
        value of Tupu (the default) means that the charset given kwenye the
        constructor ni used.

        s may be a byte string ama a Unicode string.  If it ni a byte string
        (i.e. isinstance(s, str) ni false), then charset ni the encoding of
        that byte string, na a UnicodeError will be raised ikiwa the string
        cannot be decoded ukijumuisha that charset.  If s ni a Unicode string, then
        charset ni a hint specifying the character set of the characters in
        the string.  In either case, when producing an RFC 2822 compliant
        header using RFC 2047 rules, the string will be encoded using the
        output codec of the charset.  If the string cannot be encoded to the
        output codec, a UnicodeError will be raised.

        Optional `errors' ni passed as the errors argument to the decode
        call ikiwa s ni a byte string.
        """
        ikiwa charset ni Tupu:
            charset = self._charset
        elikiwa sio isinstance(charset, Charset):
            charset = Charset(charset)
        ikiwa sio isinstance(s, str):
            input_charset = charset.input_codec ama 'us-ascii'
            ikiwa input_charset == _charset.UNKNOWN8BIT:
                s = s.decode('us-ascii', 'surrogateescape')
            isipokua:
                s = s.decode(input_charset, errors)
        # Ensure that the bytes we're storing can be decoded to the output
        # character set, otherwise an early error ni raised.
        output_charset = charset.output_codec ama 'us-ascii'
        ikiwa output_charset != _charset.UNKNOWN8BIT:
            jaribu:
                s.encode(output_charset, errors)
            except UnicodeEncodeError:
                ikiwa output_charset!='us-ascii':
                    raise
                charset = UTF8
        self._chunks.append((s, charset))

    eleza _nonctext(self, s):
        """Kweli ikiwa string s ni sio a ctext character of RFC822.
        """
        rudisha s.isspace() ama s kwenye ('(', ')', '\\')

    eleza encode(self, splitchars=';, \t', maxlinelen=Tupu, linesep='\n'):
        r"""Encode a message header into an RFC-compliant format.

        There are many issues involved kwenye converting a given string kila use in
        an email header.  Only certain character sets are readable kwenye most
        email clients, na as header strings can only contain a subset of
        7-bit ASCII, care must be taken to properly convert na encode (with
        Base64 ama quoted-printable) header strings.  In addition, there ni a
        75-character length limit on any given encoded header field, so
        line-wrapping must be performed, even ukijumuisha double-byte character sets.

        Optional maxlinelen specifies the maximum length of each generated
        line, exclusive of the linesep string.  Individual lines may be longer
        than maxlinelen ikiwa a folding point cannot be found.  The first line
        will be shorter by the length of the header name plus ": " ikiwa a header
        name was specified at Header construction time.  The default value for
        maxlinelen ni determined at header construction time.

        Optional splitchars ni a string containing characters which should be
        given extra weight by the splitting algorithm during normal header
        wrapping.  This ni kwenye very rough support of RFC 2822's `higher level
        syntactic komas':  split points preceded by a splitchar are preferred
        during line splitting, ukijumuisha the characters preferred kwenye the order in
        which they appear kwenye the string.  Space na tab may be included kwenye the
        string to indicate whether preference should be given to one over the
        other as a split point when other split chars do sio appear kwenye the line
        being split.  Splitchars does sio affect RFC 2047 encoded lines.

        Optional linesep ni a string to be used to separate the lines of
        the value.  The default value ni the most useful kila typical
        Python applications, but it can be set to \r\n to produce RFC-compliant
        line separators when needed.
        """
        self._normalize()
        ikiwa maxlinelen ni Tupu:
            maxlinelen = self._maxlinelen
        # A maxlinelen of 0 means don't wrap.  For all practical purposes,
        # choosing a huge number here accomplishes that na makes the
        # _ValueFormatter algorithm much simpler.
        ikiwa maxlinelen == 0:
            maxlinelen = 1000000
        formatter = _ValueFormatter(self._headerlen, maxlinelen,
                                    self._continuation_ws, splitchars)
        lastcs = Tupu
        hasspace = lastspace = Tupu
        kila string, charset kwenye self._chunks:
            ikiwa hasspace ni sio Tupu:
                hasspace = string na self._nonctext(string[0])
                ikiwa lastcs sio kwenye (Tupu, 'us-ascii'):
                    ikiwa sio hasspace ama charset sio kwenye (Tupu, 'us-ascii'):
                        formatter.add_transition()
                elikiwa charset sio kwenye (Tupu, 'us-ascii') na sio lastspace:
                    formatter.add_transition()
            lastspace = string na self._nonctext(string[-1])
            lastcs = charset
            hasspace = Uongo
            lines = string.splitlines()
            ikiwa lines:
                formatter.feed('', lines[0], charset)
            isipokua:
                formatter.feed('', '', charset)
            kila line kwenye lines[1:]:
                formatter.newline()
                ikiwa charset.header_encoding ni sio Tupu:
                    formatter.feed(self._continuation_ws, ' ' + line.lstrip(),
                                   charset)
                isipokua:
                    sline = line.lstrip()
                    fws = line[:len(line)-len(sline)]
                    formatter.feed(fws, sline, charset)
            ikiwa len(lines) > 1:
                formatter.newline()
        ikiwa self._chunks:
            formatter.add_transition()
        value = formatter._str(linesep)
        ikiwa _embedded_header.search(value):
             ashiria HeaderParseError("header value appears to contain "
                "an embedded header: {!r}".format(value))
        rudisha value

    eleza _normalize(self):
        # Step 1: Normalize the chunks so that all runs of identical charsets
        # get collapsed into a single unicode string.
        chunks = []
        last_charset = Tupu
        last_chunk = []
        kila string, charset kwenye self._chunks:
            ikiwa charset == last_charset:
                last_chunk.append(string)
            isipokua:
                ikiwa last_charset ni sio Tupu:
                    chunks.append((SPACE.join(last_chunk), last_charset))
                last_chunk = [string]
                last_charset = charset
        ikiwa last_chunk:
            chunks.append((SPACE.join(last_chunk), last_charset))
        self._chunks = chunks



kundi _ValueFormatter:
    eleza __init__(self, headerlen, maxlen, continuation_ws, splitchars):
        self._maxlen = maxlen
        self._continuation_ws = continuation_ws
        self._continuation_ws_len = len(continuation_ws)
        self._splitchars = splitchars
        self._lines = []
        self._current_line = _Accumulator(headerlen)

    eleza _str(self, linesep):
        self.newline()
        rudisha linesep.join(self._lines)

    eleza __str__(self):
        rudisha self._str(NL)

    eleza newline(self):
        end_of_line = self._current_line.pop()
        ikiwa end_of_line != (' ', ''):
            self._current_line.push(*end_of_line)
        ikiwa len(self._current_line) > 0:
            ikiwa self._current_line.is_onlyws() na self._lines:
                self._lines[-1] += str(self._current_line)
            isipokua:
                self._lines.append(str(self._current_line))
        self._current_line.reset()

    eleza add_transition(self):
        self._current_line.push(' ', '')

    eleza feed(self, fws, string, charset):
        # If the charset has no header encoding (i.e. it ni an ASCII encoding)
        # then we must split the header at the "highest level syntactic koma"
        # possible. Note that we don't have a lot of smarts about field
        # syntax; we just try to koma on semi-colons, then commas, then
        # whitespace.  Eventually, this should be pluggable.
        ikiwa charset.header_encoding ni Tupu:
            self._ascii_split(fws, string, self._splitchars)
            return
        # Otherwise, we're doing either a Base64 ama a quoted-printable
        # encoding which means we don't need to split the line on syntactic
        # komas.  We can basically just find enough characters to fit on the
        # current line, minus the RFC 2047 chrome.  What makes this trickier
        # though ni that we have to split at octet boundaries, sio character
        # boundaries but it's only safe to split at character boundaries so at
        # best we can only get close.
        encoded_lines = charset.header_encode_lines(string, self._maxlengths())
        # The first element extends the current line, but ikiwa it's Tupu then
        # nothing more fit on the current line so start a new line.
        jaribu:
            first_line = encoded_lines.pop(0)
        except IndexError:
            # There are no encoded lines, so we're done.
            return
        ikiwa first_line ni sio Tupu:
            self._append_chunk(fws, first_line)
        jaribu:
            last_line = encoded_lines.pop()
        except IndexError:
            # There was only one line.
            return
        self.newline()
        self._current_line.push(self._continuation_ws, last_line)
        # Everything isipokua are full lines kwenye themselves.
        kila line kwenye encoded_lines:
            self._lines.append(self._continuation_ws + line)

    eleza _maxlengths(self):
        # The first line's length.
        tuma self._maxlen - len(self._current_line)
        wakati Kweli:
            tuma self._maxlen - self._continuation_ws_len

    eleza _ascii_split(self, fws, string, splitchars):
        # The RFC 2822 header folding algorithm ni simple kwenye principle but
        # complex kwenye practice.  Lines may be folded any place where "folding
        # white space" appears by inserting a linesep character kwenye front of the
        # FWS.  The complication ni that sio all spaces ama tabs qualify as FWS,
        # na we are also supposed to prefer to koma at "higher level
        # syntactic komas".  We can't do either of these without intimate
        # knowledge of the structure of structured headers, which we don't have
        # here.  So the best we can do here ni prefer to koma at the specified
        # splitchars, na hope that we don't choose any spaces ama tabs that
        # aren't legal FWS.  (This ni at least better than the old algorithm,
        # where we would sometimes *introduce* FWS after a splitchar, ama the
        # algorithm before that, where we would turn all white space runs into
        # single spaces ama tabs.)
        parts = re.split("(["+FWS+"]+)", fws+string)
        ikiwa parts[0]:
            parts[:0] = ['']
        isipokua:
            parts.pop(0)
        kila fws, part kwenye zip(*[iter(parts)]*2):
            self._append_chunk(fws, part)

    eleza _append_chunk(self, fws, string):
        self._current_line.push(fws, string)
        ikiwa len(self._current_line) > self._maxlen:
            # Find the best split point, working backward kutoka the end.
            # There might be none, on a long first line.
            kila ch kwenye self._splitchars:
                kila i kwenye range(self._current_line.part_count()-1, 0, -1):
                    ikiwa ch.isspace():
                        fws = self._current_line[i][0]
                        ikiwa fws na fws[0]==ch:
                            koma
                    prevpart = self._current_line[i-1][1]
                    ikiwa prevpart na prevpart[-1]==ch:
                        koma
                isipokua:
                    endelea
                koma
            isipokua:
                fws, part = self._current_line.pop()
                ikiwa self._current_line._initial_size > 0:
                    # There will be a header, so leave it on a line by itself.
                    self.newline()
                    ikiwa sio fws:
                        # We don't use continuation_ws here because the whitespace
                        # after a header should always be a space.
                        fws = ' '
                self._current_line.push(fws, part)
                return
            remainder = self._current_line.pop_from(i)
            self._lines.append(str(self._current_line))
            self._current_line.reset(remainder)


kundi _Accumulator(list):

    eleza __init__(self, initial_size=0):
        self._initial_size = initial_size
        super().__init__()

    eleza push(self, fws, string):
        self.append((fws, string))

    eleza pop_from(self, i=0):
        popped = self[i:]
        self[i:] = []
        rudisha popped

    eleza pop(self):
        ikiwa self.part_count()==0:
            rudisha ('', '')
        rudisha super().pop()

    eleza __len__(self):
        rudisha sum((len(fws)+len(part) kila fws, part kwenye self),
                   self._initial_size)

    eleza __str__(self):
        rudisha EMPTYSTRING.join((EMPTYSTRING.join((fws, part))
                                kila fws, part kwenye self))

    eleza reset(self, startval=Tupu):
        ikiwa startval ni Tupu:
            startval = []
        self[:] = startval
        self._initial_size = 0

    eleza is_onlyws(self):
        rudisha self._initial_size==0 na (not self ama str(self).isspace())

    eleza part_count(self):
        rudisha super().__len__()
