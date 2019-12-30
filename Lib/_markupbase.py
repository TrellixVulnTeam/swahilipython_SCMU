"""Shared support kila scanning document type declarations kwenye HTML na XHTML.

This module ni used kama a foundation kila the html.parser module.  It has no
documented public API na should sio be used directly.

"""

agiza re

_declname_match = re.compile(r'[a-zA-Z][-_.a-zA-Z0-9]*\s*').match
_declstringlit_match = re.compile(r'(\'[^\']*\'|"[^"]*")\s*').match
_commentclose = re.compile(r'--\s*>')
_markedsectionclose = re.compile(r']\s*]\s*>')

# An analysis of the MS-Word extensions ni available at
# http://www.planetpublish.com/xmlarena/xap/Thursday/WordtoXML.pdf

_msmarkedsectionclose = re.compile(r']\s*>')

toa re


kundi ParserBase:
    """Parser base kundi which provides some common support methods used
    by the SGML/HTML na XHTML parsers."""

    eleza __init__(self):
        ikiwa self.__class__ ni ParserBase:
            ashiria RuntimeError(
                "_markupbase.ParserBase must be subclassed")

    eleza error(self, message):
        ashiria NotImplementedError(
            "subclasses of ParserBase must override error()")

    eleza reset(self):
        self.lineno = 1
        self.offset = 0

    eleza getpos(self):
        """Return current line number na offset."""
        rudisha self.lineno, self.offset

    # Internal -- update line number na offset.  This should be
    # called kila each piece of data exactly once, kwenye order -- kwenye other
    # words the concatenation of all the input strings to this
    # function should be exactly the entire input.
    eleza updatepos(self, i, j):
        ikiwa i >= j:
            rudisha j
        rawdata = self.rawdata
        nlines = rawdata.count("\n", i, j)
        ikiwa nlines:
            self.lineno = self.lineno + nlines
            pos = rawdata.rindex("\n", i, j) # Should sio fail
            self.offset = j-(pos+1)
        isipokua:
            self.offset = self.offset + j-i
        rudisha j

    _decl_otherchars = ''

    # Internal -- parse declaration (kila use by subclasses).
    eleza parse_declaration(self, i):
        # This ni some sort of declaration; kwenye "HTML as
        # deployed," this should only be the document type
        # declaration ("<!DOCTYPE html...>").
        # ISO 8879:1986, however, has more complex
        # declaration syntax kila elements kwenye <!...>, including:
        # --comment--
        # [marked section]
        # name kwenye the following list: ENTITY, DOCTYPE, ELEMENT,
        # ATTLIST, NOTATION, SHORTREF, USEMAP,
        # LINKTYPE, LINK, IDLINK, USELINK, SYSTEM
        rawdata = self.rawdata
        j = i + 2
        assert rawdata[i:j] == "<!", "unexpected call to parse_declaration"
        ikiwa rawdata[j:j+1] == ">":
            # the empty comment <!>
            rudisha j + 1
        ikiwa rawdata[j:j+1] kwenye ("-", ""):
            # Start of comment followed by buffer boundary,
            # ama just a buffer boundary.
            rudisha -1
        # A simple, practical version could look like: ((name|stringlit) S*) + '>'
        n = len(rawdata)
        ikiwa rawdata[j:j+2] == '--': #comment
            # Locate --.*-- kama the body of the comment
            rudisha self.parse_comment(i)
        lasivyo rawdata[j] == '[': #marked section
            # Locate [statusWord [...arbitrary SGML...]] kama the body of the marked section
            # Where statusWord ni one of TEMP, CDATA, IGNORE, INCLUDE, RCDATA
            # Note that this ni extended by Microsoft Office "Save kama Web" function
            # to include [if...] na [endif].
            rudisha self.parse_marked_section(i)
        isipokua: #all other declaration elements
            decltype, j = self._scan_name(j, i)
        ikiwa j < 0:
            rudisha j
        ikiwa decltype == "doctype":
            self._decl_otherchars = ''
        wakati j < n:
            c = rawdata[j]
            ikiwa c == ">":
                # end of declaration syntax
                data = rawdata[i+2:j]
                ikiwa decltype == "doctype":
                    self.handle_decl(data)
                isipokua:
                    # According to the HTML5 specs sections "8.2.4.44 Bogus
                    # comment state" na "8.2.4.45 Markup declaration open
                    # state", a comment token should be emitted.
                    # Calling unknown_decl provides more flexibility though.
                    self.unknown_decl(data)
                rudisha j + 1
            ikiwa c kwenye "\"'":
                m = _declstringlit_match(rawdata, j)
                ikiwa sio m:
                    rudisha -1 # incomplete
                j = m.end()
            lasivyo c kwenye "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                name, j = self._scan_name(j, i)
            lasivyo c kwenye self._decl_otherchars:
                j = j + 1
            lasivyo c == "[":
                # this could be handled kwenye a separate doctype parser
                ikiwa decltype == "doctype":
                    j = self._parse_doctype_subset(j + 1, i)
                lasivyo decltype kwenye {"attlist", "linktype", "link", "element"}:
                    # must tolerate []'d groups kwenye a content motoa kwenye an element declaration
                    # also kwenye data attribute specifications of attlist declaration
                    # also link type declaration subsets kwenye linktype declarations
                    # also link attribute specification lists kwenye link declarations
                    self.error("unsupported '[' char kwenye %s declaration" % decltype)
                isipokua:
                    self.error("unexpected '[' char kwenye declaration")
            isipokua:
                self.error(
                    "unexpected %r char kwenye declaration" % rawdata[j])
            ikiwa j < 0:
                rudisha j
        rudisha -1 # incomplete

    # Internal -- parse a marked section
    # Override this to handle MS-word extension syntax <![ikiwa word]>content<![endif]>
    eleza parse_marked_section(self, i, report=1):
        rawdata= self.rawdata
        assert rawdata[i:i+3] == '<![', "unexpected call to parse_marked_section()"
        sectName, j = self._scan_name( i+3, i )
        ikiwa j < 0:
            rudisha j
        ikiwa sectName kwenye {"temp", "cdata", "ignore", "include", "rcdata"}:
            # look kila standard ]]> ending
            match= _markedsectionclose.search(rawdata, i+3)
        lasivyo sectName kwenye {"if", "else", "endif"}:
            # look kila MS Office ]> ending
            match= _msmarkedsectionclose.search(rawdata, i+3)
        isipokua:
            self.error('unknown status keyword %r kwenye marked section' % rawdata[i+3:j])
        ikiwa sio match:
            rudisha -1
        ikiwa report:
            j = match.start(0)
            self.unknown_decl(rawdata[i+3: j])
        rudisha match.end(0)

    # Internal -- parse comment, rudisha length ama -1 ikiwa sio terminated
    eleza parse_comment(self, i, report=1):
        rawdata = self.rawdata
        ikiwa rawdata[i:i+4] != '<!--':
            self.error('unexpected call to parse_comment()')
        match = _commentclose.search(rawdata, i+4)
        ikiwa sio match:
            rudisha -1
        ikiwa report:
            j = match.start(0)
            self.handle_comment(rawdata[i+4: j])
        rudisha match.end(0)

    # Internal -- scan past the internal subset kwenye a <!DOCTYPE declaration,
    # returning the index just past any whitespace following the trailing ']'.
    eleza _parse_doctype_subset(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        j = i
        wakati j < n:
            c = rawdata[j]
            ikiwa c == "<":
                s = rawdata[j:j+2]
                ikiwa s == "<":
                    # end of buffer; incomplete
                    rudisha -1
                ikiwa s != "<!":
                    self.updatepos(declstartpos, j + 1)
                    self.error("unexpected char kwenye internal subset (in %r)" % s)
                ikiwa (j + 2) == n:
                    # end of buffer; incomplete
                    rudisha -1
                ikiwa (j + 4) > n:
                    # end of buffer; incomplete
                    rudisha -1
                ikiwa rawdata[j:j+4] == "<!--":
                    j = self.parse_comment(j, report=0)
                    ikiwa j < 0:
                        rudisha j
                    endelea
                name, j = self._scan_name(j + 2, declstartpos)
                ikiwa j == -1:
                    rudisha -1
                ikiwa name haiko kwenye {"attlist", "element", "entity", "notation"}:
                    self.updatepos(declstartpos, j + 2)
                    self.error(
                        "unknown declaration %r kwenye internal subset" % name)
                # handle the individual names
                meth = getattr(self, "_parse_doctype_" + name)
                j = meth(j, declstartpos)
                ikiwa j < 0:
                    rudisha j
            lasivyo c == "%":
                # parameter entity reference
                ikiwa (j + 1) == n:
                    # end of buffer; incomplete
                    rudisha -1
                s, j = self._scan_name(j + 1, declstartpos)
                ikiwa j < 0:
                    rudisha j
                ikiwa rawdata[j] == ";":
                    j = j + 1
            lasivyo c == "]":
                j = j + 1
                wakati j < n na rawdata[j].isspace():
                    j = j + 1
                ikiwa j < n:
                    ikiwa rawdata[j] == ">":
                        rudisha j
                    self.updatepos(declstartpos, j)
                    self.error("unexpected char after internal subset")
                isipokua:
                    rudisha -1
            lasivyo c.isspace():
                j = j + 1
            isipokua:
                self.updatepos(declstartpos, j)
                self.error("unexpected char %r kwenye internal subset" % c)
        # end of buffer reached
        rudisha -1

    # Internal -- scan past <!ELEMENT declarations
    eleza _parse_doctype_element(self, i, declstartpos):
        name, j = self._scan_name(i, declstartpos)
        ikiwa j == -1:
            rudisha -1
        # style content model; just skip until '>'
        rawdata = self.rawdata
        ikiwa '>' kwenye rawdata[j:]:
            rudisha rawdata.find(">", j) + 1
        rudisha -1

    # Internal -- scan past <!ATTLIST declarations
    eleza _parse_doctype_attlist(self, i, declstartpos):
        rawdata = self.rawdata
        name, j = self._scan_name(i, declstartpos)
        c = rawdata[j:j+1]
        ikiwa c == "":
            rudisha -1
        ikiwa c == ">":
            rudisha j + 1
        wakati 1:
            # scan a series of attribute descriptions; simplified:
            #   name type [value] [#constraint]
            name, j = self._scan_name(j, declstartpos)
            ikiwa j < 0:
                rudisha j
            c = rawdata[j:j+1]
            ikiwa c == "":
                rudisha -1
            ikiwa c == "(":
                # an enumerated type; look kila ')'
                ikiwa ")" kwenye rawdata[j:]:
                    j = rawdata.find(")", j) + 1
                isipokua:
                    rudisha -1
                wakati rawdata[j:j+1].isspace():
                    j = j + 1
                ikiwa sio rawdata[j:]:
                    # end of buffer, incomplete
                    rudisha -1
            isipokua:
                name, j = self._scan_name(j, declstartpos)
            c = rawdata[j:j+1]
            ikiwa sio c:
                rudisha -1
            ikiwa c kwenye "'\"":
                m = _declstringlit_match(rawdata, j)
                ikiwa m:
                    j = m.end()
                isipokua:
                    rudisha -1
                c = rawdata[j:j+1]
                ikiwa sio c:
                    rudisha -1
            ikiwa c == "#":
                ikiwa rawdata[j:] == "#":
                    # end of buffer
                    rudisha -1
                name, j = self._scan_name(j + 1, declstartpos)
                ikiwa j < 0:
                    rudisha j
                c = rawdata[j:j+1]
                ikiwa sio c:
                    rudisha -1
            ikiwa c == '>':
                # all done
                rudisha j + 1

    # Internal -- scan past <!NOTATION declarations
    eleza _parse_doctype_notation(self, i, declstartpos):
        name, j = self._scan_name(i, declstartpos)
        ikiwa j < 0:
            rudisha j
        rawdata = self.rawdata
        wakati 1:
            c = rawdata[j:j+1]
            ikiwa sio c:
                # end of buffer; incomplete
                rudisha -1
            ikiwa c == '>':
                rudisha j + 1
            ikiwa c kwenye "'\"":
                m = _declstringlit_match(rawdata, j)
                ikiwa sio m:
                    rudisha -1
                j = m.end()
            isipokua:
                name, j = self._scan_name(j, declstartpos)
                ikiwa j < 0:
                    rudisha j

    # Internal -- scan past <!ENTITY declarations
    eleza _parse_doctype_entity(self, i, declstartpos):
        rawdata = self.rawdata
        ikiwa rawdata[i:i+1] == "%":
            j = i + 1
            wakati 1:
                c = rawdata[j:j+1]
                ikiwa sio c:
                    rudisha -1
                ikiwa c.isspace():
                    j = j + 1
                isipokua:
                    koma
        isipokua:
            j = i
        name, j = self._scan_name(j, declstartpos)
        ikiwa j < 0:
            rudisha j
        wakati 1:
            c = self.rawdata[j:j+1]
            ikiwa sio c:
                rudisha -1
            ikiwa c kwenye "'\"":
                m = _declstringlit_match(rawdata, j)
                ikiwa m:
                    j = m.end()
                isipokua:
                    rudisha -1    # incomplete
            lasivyo c == ">":
                rudisha j + 1
            isipokua:
                name, j = self._scan_name(j, declstartpos)
                ikiwa j < 0:
                    rudisha j

    # Internal -- scan a name token na the new position na the token, ama
    # rudisha -1 ikiwa we've reached the end of the buffer.
    eleza _scan_name(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        ikiwa i == n:
            rudisha Tupu, -1
        m = _declname_match(rawdata, i)
        ikiwa m:
            s = m.group()
            name = s.strip()
            ikiwa (i + len(s)) == n:
                rudisha Tupu, -1  # end of buffer
            rudisha name.lower(), m.end()
        isipokua:
            self.updatepos(declstartpos, i)
            self.error("expected name token at %r"
                       % rawdata[declstartpos:declstartpos+20])

    # To be overridden -- handlers kila unknown objects
    eleza unknown_decl(self, data):
        pita
