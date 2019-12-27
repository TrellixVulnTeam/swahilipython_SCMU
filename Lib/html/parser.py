"""A parser for HTML and XHTML."""

# This file is based on sgmllib.py, but the API is slightly different.

# XXX There should be a way to distinguish between PCDATA (parsed
# character data -- the normal case), RCDATA (replaceable character
# data -- only char and entity references and end tags are special)
# and CDATA (character data -- only end tags are special).


agiza re
agiza warnings
agiza _markupbase

kutoka html agiza unescape


__all__ = ['HTMLParser']

# Regular expressions used for parsing

interesting_normal = re.compile('[&<]')
incomplete = re.compile('&[a-zA-Z#]')

entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#(?:[0-9]+|[xX][0-9a-fA-F]+)[^0-9a-fA-F]')

starttagopen = re.compile('<[a-zA-Z]')
piclose = re.compile('>')
commentclose = re.compile(r'--\s*>')
# Note:
#  1) ikiwa you change tagfind/attrfind remember to update locatestarttagend too;
#  2) ikiwa you change tagfind/attrfind and/or locatestarttagend the parser will
#     explode, so don't do it.
# see http://www.w3.org/TR/html5/tokenization.html#tag-open-state
# and http://www.w3.org/TR/html5/tokenization.html#tag-name-state
tagfind_tolerant = re.compile(r'([a-zA-Z][^\t\n\r\f />\x00]*)(?:\s|/(?!>))*')
attrfind_tolerant = re.compile(
    r'((?<=[\'"\s/])[^\s/>][^\s/=>]*)(\s*=+\s*'
    r'(\'[^\']*\'|"[^"]*"|(?![\'"])[^>\s]*))?(?:\s|/(?!>))*')
locatestarttagend_tolerant = re.compile(r"""
  <[a-zA-Z][^\t\n\r\f />\x00]*       # tag name
  (?:[\s/]*                          # optional whitespace before attribute name
    (?:(?<=['"\s/])[^\s/>][^\s/=>]*  # attribute name
      (?:\s*=+\s*                    # value indicator
        (?:'[^']*'                   # LITA-enclosed value
          |"[^"]*"                   # LIT-enclosed value
          |(?!['"])[^>\s]*           # bare value
         )
         (?:\s*,)*                   # possibly followed by a comma
       )?(?:\s|/(?!>))*
     )*
   )?
  \s*                                # trailing whitespace
""", re.VERBOSE)
endendtag = re.compile('>')
# the HTML 5 spec, section 8.1.2.2, doesn't allow spaces between
# </ and the tag name, so maybe this should be fixed
endtagfind = re.compile(r'</\s*([a-zA-Z][-.a-zA-Z0-9:_]*)\s*>')



kundi HTMLParser(_markupbase.ParserBase):
    """Find tags and other markup and call handler functions.

    Usage:
        p = HTMLParser()
        p.feed(data)
        ...
        p.close()

    Start tags are handled by calling self.handle_starttag() or
    self.handle_startendtag(); end tags by self.handle_endtag().  The
    data between tags is passed kutoka the parser to the derived class
    by calling self.handle_data() with the data as argument (the data
    may be split up in arbitrary chunks).  If convert_charrefs is
    True the character references are converted automatically to the
    corresponding Unicode character (and self.handle_data() is no
    longer split in chunks), otherwise they are passed by calling
    self.handle_entityref() or self.handle_charref() with the string
    containing respectively the named or numeric reference as the
    argument.
    """

    CDATA_CONTENT_ELEMENTS = ("script", "style")

    eleza __init__(self, *, convert_charrefs=True):
        """Initialize and reset this instance.

        If convert_charrefs is True (the default), all character references
        are automatically converted to the corresponding Unicode characters.
        """
        self.convert_charrefs = convert_charrefs
        self.reset()

    eleza reset(self):
        """Reset this instance.  Loses all unprocessed data."""
        self.rawdata = ''
        self.lasttag = '???'
        self.interesting = interesting_normal
        self.cdata_elem = None
        _markupbase.ParserBase.reset(self)

    eleza feed(self, data):
        r"""Feed data to the parser.

        Call this as often as you want, with as little or as much text
        as you want (may include '\n').
        """
        self.rawdata = self.rawdata + data
        self.goahead(0)

    eleza close(self):
        """Handle any buffered data."""
        self.goahead(1)

    __starttag_text = None

    eleza get_starttag_text(self):
        """Return full source of start tag: '<...>'."""
        rudisha self.__starttag_text

    eleza set_cdata_mode(self, elem):
        self.cdata_elem = elem.lower()
        self.interesting = re.compile(r'</\s*%s\s*>' % self.cdata_elem, re.I)

    eleza clear_cdata_mode(self):
        self.interesting = interesting_normal
        self.cdata_elem = None

    # Internal -- handle data as far as reasonable.  May leave state
    # and data to be processed by a subsequent call.  If 'end' is
    # true, force handling all data as ikiwa followed by EOF marker.
    eleza goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            ikiwa self.convert_charrefs and not self.cdata_elem:
                j = rawdata.find('<', i)
                ikiwa j < 0:
                    # ikiwa we can't find the next <, either we are at the end
                    # or there's more text incoming.  If the latter is True,
                    # we can't pass the text to handle_data in case we have
                    # a charref cut in half at end.  Try to determine if
                    # this is the case before proceeding by looking for an
                    # & near the end and see ikiwa it's followed by a space or ;.
                    amppos = rawdata.rfind('&', max(i, n-34))
                    ikiwa (amppos >= 0 and
                        not re.compile(r'[\s;]').search(rawdata, amppos)):
                        break  # wait till we get all the text
                    j = n
            else:
                match = self.interesting.search(rawdata, i)  # < or &
                ikiwa match:
                    j = match.start()
                else:
                    ikiwa self.cdata_elem:
                        break
                    j = n
            ikiwa i < j:
                ikiwa self.convert_charrefs and not self.cdata_elem:
                    self.handle_data(unescape(rawdata[i:j]))
                else:
                    self.handle_data(rawdata[i:j])
            i = self.updatepos(i, j)
            ikiwa i == n: break
            startswith = rawdata.startswith
            ikiwa startswith('<', i):
                ikiwa starttagopen.match(rawdata, i): # < + letter
                    k = self.parse_starttag(i)
                elikiwa startswith("</", i):
                    k = self.parse_endtag(i)
                elikiwa startswith("<!--", i):
                    k = self.parse_comment(i)
                elikiwa startswith("<?", i):
                    k = self.parse_pi(i)
                elikiwa startswith("<!", i):
                    k = self.parse_html_declaration(i)
                elikiwa (i + 1) < n:
                    self.handle_data("<")
                    k = i + 1
                else:
                    break
                ikiwa k < 0:
                    ikiwa not end:
                        break
                    k = rawdata.find('>', i + 1)
                    ikiwa k < 0:
                        k = rawdata.find('<', i + 1)
                        ikiwa k < 0:
                            k = i + 1
                    else:
                        k += 1
                    ikiwa self.convert_charrefs and not self.cdata_elem:
                        self.handle_data(unescape(rawdata[i:k]))
                    else:
                        self.handle_data(rawdata[i:k])
                i = self.updatepos(i, k)
            elikiwa startswith("&#", i):
                match = charref.match(rawdata, i)
                ikiwa match:
                    name = match.group()[2:-1]
                    self.handle_charref(name)
                    k = match.end()
                    ikiwa not startswith(';', k-1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                else:
                    ikiwa ";" in rawdata[i:]:  # bail by consuming &#
                        self.handle_data(rawdata[i:i+2])
                        i = self.updatepos(i, i+2)
                    break
            elikiwa startswith('&', i):
                match = entityref.match(rawdata, i)
                ikiwa match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    k = match.end()
                    ikiwa not startswith(';', k-1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                match = incomplete.match(rawdata, i)
                ikiwa match:
                    # match.group() will contain at least 2 chars
                    ikiwa end and match.group() == rawdata[i:]:
                        k = match.end()
                        ikiwa k <= i:
                            k = n
                        i = self.updatepos(i, i + 1)
                    # incomplete
                    break
                elikiwa (i + 1) < n:
                    # not the end of the buffer, and can't be confused
                    # with some other construct
                    self.handle_data("&")
                    i = self.updatepos(i, i + 1)
                else:
                    break
            else:
                assert 0, "interesting.search() lied"
        # end while
        ikiwa end and i < n and not self.cdata_elem:
            ikiwa self.convert_charrefs and not self.cdata_elem:
                self.handle_data(unescape(rawdata[i:n]))
            else:
                self.handle_data(rawdata[i:n])
            i = self.updatepos(i, n)
        self.rawdata = rawdata[i:]

    # Internal -- parse html declarations, rudisha length or -1 ikiwa not terminated
    # See w3.org/TR/html5/tokenization.html#markup-declaration-open-state
    # See also parse_declaration in _markupbase
    eleza parse_html_declaration(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i+2] == '<!', ('unexpected call to '
                                        'parse_html_declaration()')
        ikiwa rawdata[i:i+4] == '<!--':
            # this case is actually already handled in goahead()
            rudisha self.parse_comment(i)
        elikiwa rawdata[i:i+3] == '<![':
            rudisha self.parse_marked_section(i)
        elikiwa rawdata[i:i+9].lower() == '<!doctype':
            # find the closing >
            gtpos = rawdata.find('>', i+9)
            ikiwa gtpos == -1:
                rudisha -1
            self.handle_decl(rawdata[i+2:gtpos])
            rudisha gtpos+1
        else:
            rudisha self.parse_bogus_comment(i)

    # Internal -- parse bogus comment, rudisha length or -1 ikiwa not terminated
    # see http://www.w3.org/TR/html5/tokenization.html#bogus-comment-state
    eleza parse_bogus_comment(self, i, report=1):
        rawdata = self.rawdata
        assert rawdata[i:i+2] in ('<!', '</'), ('unexpected call to '
                                                'parse_comment()')
        pos = rawdata.find('>', i+2)
        ikiwa pos == -1:
            rudisha -1
        ikiwa report:
            self.handle_comment(rawdata[i+2:pos])
        rudisha pos + 1

    # Internal -- parse processing instr, rudisha end or -1 ikiwa not terminated
    eleza parse_pi(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i+2] == '<?', 'unexpected call to parse_pi()'
        match = piclose.search(rawdata, i+2) # >
        ikiwa not match:
            rudisha -1
        j = match.start()
        self.handle_pi(rawdata[i+2: j])
        j = match.end()
        rudisha j

    # Internal -- handle starttag, rudisha end or -1 ikiwa not terminated
    eleza parse_starttag(self, i):
        self.__starttag_text = None
        endpos = self.check_for_whole_start_tag(i)
        ikiwa endpos < 0:
            rudisha endpos
        rawdata = self.rawdata
        self.__starttag_text = rawdata[i:endpos]

        # Now parse the data between i+1 and j into a tag and attrs
        attrs = []
        match = tagfind_tolerant.match(rawdata, i+1)
        assert match, 'unexpected call to parse_starttag()'
        k = match.end()
        self.lasttag = tag = match.group(1).lower()
        while k < endpos:
            m = attrfind_tolerant.match(rawdata, k)
            ikiwa not m:
                break
            attrname, rest, attrvalue = m.group(1, 2, 3)
            ikiwa not rest:
                attrvalue = None
            elikiwa attrvalue[:1] == '\'' == attrvalue[-1:] or \
                 attrvalue[:1] == '"' == attrvalue[-1:]:
                attrvalue = attrvalue[1:-1]
            ikiwa attrvalue:
                attrvalue = unescape(attrvalue)
            attrs.append((attrname.lower(), attrvalue))
            k = m.end()

        end = rawdata[k:endpos].strip()
        ikiwa end not in (">", "/>"):
            lineno, offset = self.getpos()
            ikiwa "\n" in self.__starttag_text:
                lineno = lineno + self.__starttag_text.count("\n")
                offset = len(self.__starttag_text) \
                         - self.__starttag_text.rfind("\n")
            else:
                offset = offset + len(self.__starttag_text)
            self.handle_data(rawdata[i:endpos])
            rudisha endpos
        ikiwa end.endswith('/>'):
            # XHTML-style empty tag: <span attr="value" />
            self.handle_startendtag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            ikiwa tag in self.CDATA_CONTENT_ELEMENTS:
                self.set_cdata_mode(tag)
        rudisha endpos

    # Internal -- check to see ikiwa we have a complete starttag; rudisha end
    # or -1 ikiwa incomplete.
    eleza check_for_whole_start_tag(self, i):
        rawdata = self.rawdata
        m = locatestarttagend_tolerant.match(rawdata, i)
        ikiwa m:
            j = m.end()
            next = rawdata[j:j+1]
            ikiwa next == ">":
                rudisha j + 1
            ikiwa next == "/":
                ikiwa rawdata.startswith("/>", j):
                    rudisha j + 2
                ikiwa rawdata.startswith("/", j):
                    # buffer boundary
                    rudisha -1
                # else bogus input
                ikiwa j > i:
                    rudisha j
                else:
                    rudisha i + 1
            ikiwa next == "":
                # end of input
                rudisha -1
            ikiwa next in ("abcdefghijklmnopqrstuvwxyz=/"
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                # end of input in or before attribute value, or we have the
                # '/' kutoka a '/>' ending
                rudisha -1
            ikiwa j > i:
                rudisha j
            else:
                rudisha i + 1
        raise AssertionError("we should not get here!")

    # Internal -- parse endtag, rudisha end or -1 ikiwa incomplete
    eleza parse_endtag(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i+2] == "</", "unexpected call to parse_endtag"
        match = endendtag.search(rawdata, i+1) # >
        ikiwa not match:
            rudisha -1
        gtpos = match.end()
        match = endtagfind.match(rawdata, i) # </ + tag + >
        ikiwa not match:
            ikiwa self.cdata_elem is not None:
                self.handle_data(rawdata[i:gtpos])
                rudisha gtpos
            # find the name: w3.org/TR/html5/tokenization.html#tag-name-state
            namematch = tagfind_tolerant.match(rawdata, i+2)
            ikiwa not namematch:
                # w3.org/TR/html5/tokenization.html#end-tag-open-state
                ikiwa rawdata[i:i+3] == '</>':
                    rudisha i+3
                else:
                    rudisha self.parse_bogus_comment(i)
            tagname = namematch.group(1).lower()
            # consume and ignore other stuff between the name and the >
            # Note: this is not 100% correct, since we might have things like
            # </tag attr=">">, but looking for > after tha name should cover
            # most of the cases and is much simpler
            gtpos = rawdata.find('>', namematch.end())
            self.handle_endtag(tagname)
            rudisha gtpos+1

        elem = match.group(1).lower() # script or style
        ikiwa self.cdata_elem is not None:
            ikiwa elem != self.cdata_elem:
                self.handle_data(rawdata[i:gtpos])
                rudisha gtpos

        self.handle_endtag(elem)
        self.clear_cdata_mode()
        rudisha gtpos

    # Overridable -- finish processing of start+end tag: <tag.../>
    eleza handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    # Overridable -- handle start tag
    eleza handle_starttag(self, tag, attrs):
        pass

    # Overridable -- handle end tag
    eleza handle_endtag(self, tag):
        pass

    # Overridable -- handle character reference
    eleza handle_charref(self, name):
        pass

    # Overridable -- handle entity reference
    eleza handle_entityref(self, name):
        pass

    # Overridable -- handle data
    eleza handle_data(self, data):
        pass

    # Overridable -- handle comment
    eleza handle_comment(self, data):
        pass

    # Overridable -- handle declaration
    eleza handle_decl(self, decl):
        pass

    # Overridable -- handle processing instruction
    eleza handle_pi(self, data):
        pass

    eleza unknown_decl(self, data):
        pass

    # Internal -- helper to remove special character quoting
    eleza unescape(self, s):
        warnings.warn('The unescape method is deprecated and will be removed '
                      'in 3.5, use html.unescape() instead.',
                      DeprecationWarning, stacklevel=2)
        rudisha unescape(s)
