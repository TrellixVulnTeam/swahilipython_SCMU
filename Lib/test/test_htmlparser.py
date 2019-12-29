"""Tests kila HTMLParser.py."""

agiza html.parser
agiza pprint
agiza unittest


kundi EventCollector(html.parser.HTMLParser):

    eleza __init__(self, *args, **kw):
        self.events = []
        self.append = self.events.append
        html.parser.HTMLParser.__init__(self, *args, **kw)

    eleza get_events(self):
        # Normalize the list of events so that buffer artefacts don't
        # separate runs of contiguous characters.
        L = []
        prevtype = Tupu
        kila event kwenye self.events:
            type = event[0]
            ikiwa type == prevtype == "data":
                L[-1] = ("data", L[-1][1] + event[1])
            isipokua:
                L.append(event)
            prevtype = type
        self.events = L
        rudisha L

    # structure markup

    eleza handle_starttag(self, tag, attrs):
        self.append(("starttag", tag, attrs))

    eleza handle_startendtag(self, tag, attrs):
        self.append(("startendtag", tag, attrs))

    eleza handle_endtag(self, tag):
        self.append(("endtag", tag))

    # all other markup

    eleza handle_comment(self, data):
        self.append(("comment", data))

    eleza handle_charref(self, data):
        self.append(("charref", data))

    eleza handle_data(self, data):
        self.append(("data", data))

    eleza handle_decl(self, data):
        self.append(("decl", data))

    eleza handle_entityref(self, data):
        self.append(("entityref", data))

    eleza handle_pi(self, data):
        self.append(("pi", data))

    eleza unknown_decl(self, decl):
        self.append(("unknown decl", decl))


kundi EventCollectorExtra(EventCollector):

    eleza handle_starttag(self, tag, attrs):
        EventCollector.handle_starttag(self, tag, attrs)
        self.append(("starttag_text", self.get_starttag_text()))


kundi EventCollectorCharrefs(EventCollector):

    eleza handle_charref(self, data):
        self.fail('This should never be called ukijumuisha convert_charrefs=Kweli')

    eleza handle_entityref(self, data):
        self.fail('This should never be called ukijumuisha convert_charrefs=Kweli')


kundi TestCaseBase(unittest.TestCase):

    eleza get_collector(self):
        rudisha EventCollector(convert_charrefs=Uongo)

    eleza _run_check(self, source, expected_events, collector=Tupu):
        ikiwa collector ni Tupu:
            collector = self.get_collector()
        parser = collector
        kila s kwenye source:
            parser.feed(s)
        parser.close()
        events = parser.get_events()
        ikiwa events != expected_events:
            self.fail("received events did sio match expected events" +
                      "\nSource:\n" + repr(source) +
                      "\nExpected:\n" + pprint.pformat(expected_events) +
                      "\nReceived:\n" + pprint.pformat(events))

    eleza _run_check_extra(self, source, events):
        self._run_check(source, events,
                        EventCollectorExtra(convert_charrefs=Uongo))


kundi HTMLParserTestCase(TestCaseBase):

    eleza test_processing_instruction_only(self):
        self._run_check("<?processing instruction>", [
            ("pi", "processing instruction"),
            ])
        self._run_check("<?processing instruction ?>", [
            ("pi", "processing instruction ?"),
            ])

    eleza test_simple_html(self):
        self._run_check("""
<!DOCTYPE html PUBLIC 'foo'>
<HTML>&entity;&#32;
<!--comment1a
-></foo><bar>&lt;<?pi?></foo<bar
comment1b-->
<Img sRc='Bar' isMAP>sample
text
&#x201C;
<!--comment2a-- --comment2b-->
</Html>
""", [
    ("data", "\n"),
    ("decl", "DOCTYPE html PUBLIC 'foo'"),
    ("data", "\n"),
    ("starttag", "html", []),
    ("entityref", "entity"),
    ("charref", "32"),
    ("data", "\n"),
    ("comment", "comment1a\n-></foo><bar>&lt;<?pi?></foo<bar\ncomment1b"),
    ("data", "\n"),
    ("starttag", "img", [("src", "Bar"), ("ismap", Tupu)]),
    ("data", "sample\ntext\n"),
    ("charref", "x201C"),
    ("data", "\n"),
    ("comment", "comment2a-- --comment2b"),
    ("data", "\n"),
    ("endtag", "html"),
    ("data", "\n"),
    ])

    eleza test_malformatted_charref(self):
        self._run_check("<p>&#bad;</p>", [
            ("starttag", "p", []),
            ("data", "&#bad;"),
            ("endtag", "p"),
        ])
        # add the [] kama a workaround to avoid buffering (see #20288)
        self._run_check(["<div>&#bad;</div>"], [
            ("starttag", "div", []),
            ("data", "&#bad;"),
            ("endtag", "div"),
        ])

    eleza test_unclosed_entityref(self):
        self._run_check("&entityref foo", [
            ("entityref", "entityref"),
            ("data", " foo"),
            ])

    eleza test_bad_nesting(self):
        # Strangely, this *is* supposed to test that overlapping
        # elements are allowed.  HTMLParser ni more geared toward
        # lexing the input that parsing the structure.
        self._run_check("<a><b></a></b>", [
            ("starttag", "a", []),
            ("starttag", "b", []),
            ("endtag", "a"),
            ("endtag", "b"),
            ])

    eleza test_bare_ampersands(self):
        self._run_check("this text & contains & ampersands &", [
            ("data", "this text & contains & ampersands &"),
            ])

    eleza test_bare_pointy_brackets(self):
        self._run_check("this < text > contains < bare>pointy< brackets", [
            ("data", "this < text > contains < bare>pointy< brackets"),
            ])

    eleza test_starttag_end_boundary(self):
        self._run_check("""<a b='<'>""", [("starttag", "a", [("b", "<")])])
        self._run_check("""<a b='>'>""", [("starttag", "a", [("b", ">")])])

    eleza test_buffer_artefacts(self):
        output = [("starttag", "a", [("b", "<")])]
        self._run_check(["<a b='<'>"], output)
        self._run_check(["<a ", "b='<'>"], output)
        self._run_check(["<a b", "='<'>"], output)
        self._run_check(["<a b=", "'<'>"], output)
        self._run_check(["<a b='<", "'>"], output)
        self._run_check(["<a b='<'", ">"], output)

        output = [("starttag", "a", [("b", ">")])]
        self._run_check(["<a b='>'>"], output)
        self._run_check(["<a ", "b='>'>"], output)
        self._run_check(["<a b", "='>'>"], output)
        self._run_check(["<a b=", "'>'>"], output)
        self._run_check(["<a b='>", "'>"], output)
        self._run_check(["<a b='>'", ">"], output)

        output = [("comment", "abc")]
        self._run_check(["", "<!--abc-->"], output)
        self._run_check(["<", "!--abc-->"], output)
        self._run_check(["<!", "--abc-->"], output)
        self._run_check(["<!-", "-abc-->"], output)
        self._run_check(["<!--", "abc-->"], output)
        self._run_check(["<!--a", "bc-->"], output)
        self._run_check(["<!--ab", "c-->"], output)
        self._run_check(["<!--abc", "-->"], output)
        self._run_check(["<!--abc-", "->"], output)
        self._run_check(["<!--abc--", ">"], output)
        self._run_check(["<!--abc-->", ""], output)

    eleza test_valid_doctypes(self):
        # kutoka http://www.w3.org/QA/2002/04/valid-dtd-list.html
        dtds = ['HTML',  # HTML5 doctype
                ('HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd"'),
                ('HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" '
                 '"http://www.w3.org/TR/html4/loose.dtd"'),
                ('html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'),
                ('html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" '
                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"'),
                ('math PUBLIC "-//W3C//DTD MathML 2.0//EN" '
                 '"http://www.w3.org/Math/DTD/mathml2/mathml2.dtd"'),
                ('html PUBLIC "-//W3C//DTD '
                 'XHTML 1.1 plus MathML 2.0 plus SVG 1.1//EN" '
                 '"http://www.w3.org/2002/04/xhtml-math-svg/xhtml-math-svg.dtd"'),
                ('svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
                 '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"'),
                'html PUBLIC "-//IETF//DTD HTML 2.0//EN"',
                'html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"']
        kila dtd kwenye dtds:
            self._run_check("<!DOCTYPE %s>" % dtd,
                            [('decl', 'DOCTYPE ' + dtd)])

    eleza test_startendtag(self):
        self._run_check("<p/>", [
            ("startendtag", "p", []),
            ])
        self._run_check("<p></p>", [
            ("starttag", "p", []),
            ("endtag", "p"),
            ])
        self._run_check("<p><img src='foo' /></p>", [
            ("starttag", "p", []),
            ("startendtag", "img", [("src", "foo")]),
            ("endtag", "p"),
            ])

    eleza test_get_starttag_text(self):
        s = """<foo:bar   \n   one="1"\ttwo=2   >"""
        self._run_check_extra(s, [
            ("starttag", "foo:bar", [("one", "1"), ("two", "2")]),
            ("starttag_text", s)])

    eleza test_cdata_content(self):
        contents = [
            '<!-- sio a comment --> &not-an-entity-ref;',
            "<not a='start tag'>",
            '<a href="" /> <p> <span></span>',
            'foo = "</scr" + "ipt>";',
            'foo = "</SCRIPT" + ">";',
            'foo = <\n/script> ',
            '<!-- document.write("</scr" + "ipt>"); -->',
            ('\n//<![CDATA[\n'
             'document.write(\'<s\'+\'cript type="text/javascript" '
             'src="http://www.example.org/r=\'+new '
             'Date().getTime()+\'"><\\/s\'+\'cript>\');\n//]]>'),
            '\n<!-- //\nvar foo = 3.14;\n// -->\n',
            'foo = "</sty" + "le>";',
            '<!-- \u2603 -->',
            # these two should be invalid according to the HTML 5 spec,
            # section 8.1.2.2
            #'foo = </\nscript>',
            #'foo = </ script>',
        ]
        elements = ['script', 'style', 'SCRIPT', 'STYLE', 'Script', 'Style']
        kila content kwenye contents:
            kila element kwenye elements:
                element_lower = element.lower()
                s = '<{element}>{content}</{element}>'.format(element=element,
                                                               content=content)
                self._run_check(s, [("starttag", element_lower, []),
                                    ("data", content),
                                    ("endtag", element_lower)])

    eleza test_cdata_with_closing_tags(self):
        # see issue #13358
        # make sure that HTMLParser calls handle_data only once kila each CDATA.
        # The normal event collector normalizes  the events kwenye get_events,
        # so we override it to rudisha the original list of events.
        kundi Collector(EventCollector):
            eleza get_events(self):
                rudisha self.events

        content = """<!-- sio a comment --> &not-an-entity-ref;
                  <a href="" /> </p><p> <span></span></style>
                  '</script' + '>'"""
        kila element kwenye [' script', 'script ', ' script ',
                        '\nscript', 'script\n', '\nscript\n']:
            element_lower = element.lower().strip()
            s = '<script>{content}</{element}>'.format(element=element,
                                                       content=content)
            self._run_check(s, [("starttag", element_lower, []),
                                ("data", content),
                                ("endtag", element_lower)],
                            collector=Collector(convert_charrefs=Uongo))

    eleza test_comments(self):
        html = ("<!-- I'm a valid comment -->"
                '<!--me too!-->'
                '<!------>'
                '<!---->'
                '<!----I have many hyphens---->'
                '<!-- I have a > kwenye the middle -->'
                '<!-- na I have -- kwenye the middle! -->')
        expected = [('comment', " I'm a valid comment "),
                    ('comment', 'me too!'),
                    ('comment', '--'),
                    ('comment', ''),
                    ('comment', '--I have many hyphens--'),
                    ('comment', ' I have a > kwenye the middle '),
                    ('comment', ' na I have -- kwenye the middle! ')]
        self._run_check(html, expected)

    eleza test_condcoms(self):
        html = ('<!--[ikiwa IE & !(lte IE 8)]>aren\'t<![endif]-->'
                '<!--[ikiwa IE 8]>condcoms<![endif]-->'
                '<!--[ikiwa lte IE 7]>pretty?<![endif]-->')
        expected = [('comment', "[ikiwa IE & !(lte IE 8)]>aren't<![endif]"),
                    ('comment', '[ikiwa IE 8]>condcoms<![endif]'),
                    ('comment', '[ikiwa lte IE 7]>pretty?<![endif]')]
        self._run_check(html, expected)

    eleza test_convert_charrefs(self):
        # default value kila convert_charrefs ni now Kweli
        collector = lambda: EventCollectorCharrefs()
        self.assertKweli(collector().convert_charrefs)
        charrefs = ['&quot;', '&#34;', '&#x22;', '&quot', '&#34', '&#x22']
        # check charrefs kwenye the middle of the text/attributes
        expected = [('starttag', 'a', [('href', 'foo"zar')]),
                    ('data', 'a"z'), ('endtag', 'a')]
        kila charref kwenye charrefs:
            self._run_check('<a href="foo{0}zar">a{0}z</a>'.format(charref),
                            expected, collector=collector())
        # check charrefs at the beginning/end of the text/attributes
        expected = [('data', '"'),
                    ('starttag', 'a', [('x', '"'), ('y', '"X'), ('z', 'X"')]),
                    ('data', '"'), ('endtag', 'a'), ('data', '"')]
        kila charref kwenye charrefs:
            self._run_check('{0}<a x="{0}" y="{0}X" z="X{0}">'
                            '{0}</a>{0}'.format(charref),
                            expected, collector=collector())
        # check charrefs kwenye <script>/<style> elements
        kila charref kwenye charrefs:
            text = 'X'.join([charref]*3)
            expected = [('data', '"'),
                        ('starttag', 'script', []), ('data', text),
                        ('endtag', 'script'), ('data', '"'),
                        ('starttag', 'style', []), ('data', text),
                        ('endtag', 'style'), ('data', '"')]
            self._run_check('{1}<script>{0}</script>{1}'
                            '<style>{0}</style>{1}'.format(text, charref),
                            expected, collector=collector())
        # check truncated charrefs at the end of the file
        html = '&quo &# &#x'
        kila x kwenye range(1, len(html)):
            self._run_check(html[:x], [('data', html[:x])],
                            collector=collector())
        # check a string ukijumuisha no charrefs
        self._run_check('no charrefs here', [('data', 'no charrefs here')],
                        collector=collector())

    # the remaining tests were kila the "tolerant" parser (which ni now
    # the default), na check various kind of broken markup
    eleza test_tolerant_parsing(self):
        self._run_check('<html <html>te>>xt&a<<bc</a></html>\n'
                        '<img src="URL><//img></html</html>', [
                            ('starttag', 'html', [('<html', Tupu)]),
                            ('data', 'te>>xt'),
                            ('entityref', 'a'),
                            ('data', '<'),
                            ('starttag', 'bc<', [('a', Tupu)]),
                            ('endtag', 'html'),
                            ('data', '\n<img src="URL>'),
                            ('comment', '/img'),
                            ('endtag', 'html<')])

    eleza test_starttag_junk_chars(self):
        self._run_check("</>", [])
        self._run_check("</$>", [('comment', '$')])
        self._run_check("</", [('data', '</')])
        self._run_check("</a", [('data', '</a')])
        self._run_check("<a<a>", [('starttag', 'a<a', [])])
        self._run_check("</a<a>", [('endtag', 'a<a')])
        self._run_check("<!", [('data', '<!')])
        self._run_check("<a", [('data', '<a')])
        self._run_check("<a foo='bar'", [('data', "<a foo='bar'")])
        self._run_check("<a foo='bar", [('data', "<a foo='bar")])
        self._run_check("<a foo='>'", [('data', "<a foo='>'")])
        self._run_check("<a foo='>", [('data', "<a foo='>")])
        self._run_check("<a$>", [('starttag', 'a$', [])])
        self._run_check("<a$b>", [('starttag', 'a$b', [])])
        self._run_check("<a$b/>", [('startendtag', 'a$b', [])])
        self._run_check("<a$b  >", [('starttag', 'a$b', [])])
        self._run_check("<a$b  />", [('startendtag', 'a$b', [])])

    eleza test_slashes_in_starttag(self):
        self._run_check('<a foo="var"/>', [('startendtag', 'a', [('foo', 'var')])])
        html = ('<img width=902 height=250px '
                'src="/sites/default/files/images/homepage/foo.jpg" '
                '/*what am I doing here*/ />')
        expected = [(
            'startendtag', 'img',
            [('width', '902'), ('height', '250px'),
             ('src', '/sites/default/files/images/homepage/foo.jpg'),
             ('*what', Tupu), ('am', Tupu), ('i', Tupu),
             ('doing', Tupu), ('here*', Tupu)]
        )]
        self._run_check(html, expected)
        html = ('<a / /foo/ / /=/ / /bar/ / />'
                '<a / /foo/ / /=/ / /bar/ / >')
        expected = [
            ('startendtag', 'a', [('foo', Tupu), ('=', Tupu), ('bar', Tupu)]),
            ('starttag', 'a', [('foo', Tupu), ('=', Tupu), ('bar', Tupu)])
        ]
        self._run_check(html, expected)
        #see issue #14538
        html = ('<meta><meta / ><meta // ><meta / / >'
                '<meta/><meta /><meta //><meta//>')
        expected = [
            ('starttag', 'meta', []), ('starttag', 'meta', []),
            ('starttag', 'meta', []), ('starttag', 'meta', []),
            ('startendtag', 'meta', []), ('startendtag', 'meta', []),
            ('startendtag', 'meta', []), ('startendtag', 'meta', []),
        ]
        self._run_check(html, expected)

    eleza test_declaration_junk_chars(self):
        self._run_check("<!DOCTYPE foo $ >", [('decl', 'DOCTYPE foo $ ')])

    eleza test_illegal_declarations(self):
        self._run_check('<!spacer type="block" height="25">',
                        [('comment', 'spacer type="block" height="25"')])

    eleza test_with_unquoted_attributes(self):
        # see #12008
        html = ("<html><body bgcolor=d0ca90 text='181008'>"
                "<table cellspacing=0 cellpadding=1 width=100% ><tr>"
                "<td align=left><font size=-1>"
                "- <a href=/rabota/><span class=en> software-and-i</span></a>"
                "- <a href='/1/'><span class=en> library</span></a></table>")
        expected = [
            ('starttag', 'html', []),
            ('starttag', 'body', [('bgcolor', 'd0ca90'), ('text', '181008')]),
            ('starttag', 'table',
                [('cellspacing', '0'), ('cellpadding', '1'), ('width', '100%')]),
            ('starttag', 'tr', []),
            ('starttag', 'td', [('align', 'left')]),
            ('starttag', 'font', [('size', '-1')]),
            ('data', '- '), ('starttag', 'a', [('href', '/rabota/')]),
            ('starttag', 'span', [('class', 'en')]), ('data', ' software-and-i'),
            ('endtag', 'span'), ('endtag', 'a'),
            ('data', '- '), ('starttag', 'a', [('href', '/1/')]),
            ('starttag', 'span', [('class', 'en')]), ('data', ' library'),
            ('endtag', 'span'), ('endtag', 'a'), ('endtag', 'table')
        ]
        self._run_check(html, expected)

    eleza test_comma_between_attributes(self):
        self._run_check('<form action="/xxx.php?a=1&amp;b=2&amp", '
                        'method="post">', [
                            ('starttag', 'form',
                                [('action', '/xxx.php?a=1&b=2&'),
                                 (',', Tupu), ('method', 'post')])])

    eleza test_weird_chars_in_unquoted_attribute_values(self):
        self._run_check('<form action=bogus|&#()value>', [
                            ('starttag', 'form',
                                [('action', 'bogus|&#()value')])])

    eleza test_invalid_end_tags(self):
        # A collection of broken end tags. <br> ni used kama separator.
        # see http://www.w3.org/TR/html5/tokenization.html#end-tag-open-state
        # na #13993
        html = ('<br></label</p><br></div end tmAd-leaderBoard><br></<h4><br>'
                '</li class="unit"><br></li\r\n\t\t\t\t\t\t</ul><br></><br>')
        expected = [('starttag', 'br', []),
                    # < ni part of the name, / ni discarded, p ni an attribute
                    ('endtag', 'label<'),
                    ('starttag', 'br', []),
                    # text na attributes are discarded
                    ('endtag', 'div'),
                    ('starttag', 'br', []),
                    # comment because the first char after </ ni sio a-zA-Z
                    ('comment', '<h4'),
                    ('starttag', 'br', []),
                    # attributes are discarded
                    ('endtag', 'li'),
                    ('starttag', 'br', []),
                    # everything till ul (included) ni discarded
                    ('endtag', 'li'),
                    ('starttag', 'br', []),
                    # </> ni ignored
                    ('starttag', 'br', [])]
        self._run_check(html, expected)

    eleza test_broken_invalid_end_tag(self):
        # This ni technically wrong (the "> shouldn't be included kwenye the 'data')
        # but ni probably sio worth fixing it (in addition to all the cases of
        # the previous test, it would require a full attribute parsing).
        # see #13993
        html = '<b>This</b attr=">"> confuses the parser'
        expected = [('starttag', 'b', []),
                    ('data', 'This'),
                    ('endtag', 'b'),
                    ('data', '"> confuses the parser')]
        self._run_check(html, expected)

    eleza test_correct_detection_of_start_tags(self):
        # see #13273
        html = ('<div style=""    ><b>The <a href="some_url">rain</a> '
                '<br /> kwenye <span>Spain</span></b></div>')
        expected = [
            ('starttag', 'div', [('style', '')]),
            ('starttag', 'b', []),
            ('data', 'The '),
            ('starttag', 'a', [('href', 'some_url')]),
            ('data', 'rain'),
            ('endtag', 'a'),
            ('data', ' '),
            ('startendtag', 'br', []),
            ('data', ' kwenye '),
            ('starttag', 'span', []),
            ('data', 'Spain'),
            ('endtag', 'span'),
            ('endtag', 'b'),
            ('endtag', 'div')
        ]
        self._run_check(html, expected)

        html = '<div style="", foo = "bar" ><b>The <a href="some_url">rain</a>'
        expected = [
            ('starttag', 'div', [('style', ''), (',', Tupu), ('foo', 'bar')]),
            ('starttag', 'b', []),
            ('data', 'The '),
            ('starttag', 'a', [('href', 'some_url')]),
            ('data', 'rain'),
            ('endtag', 'a'),
        ]
        self._run_check(html, expected)

    eleza test_EOF_in_charref(self):
        # see #17802
        # This test checks that the UnboundLocalError reported kwenye the issue
        # ni sio ashiriad, however I'm sio sure the rudishaed values are correct.
        # Maybe HTMLParser should use self.unescape kila these
        data = [
            ('a&', [('data', 'a&')]),
            ('a&b', [('data', 'ab')]),
            ('a&b ', [('data', 'a'), ('entityref', 'b'), ('data', ' ')]),
            ('a&b;', [('data', 'a'), ('entityref', 'b')]),
        ]
        kila html, expected kwenye data:
            self._run_check(html, expected)

    eleza test_unescape_method(self):
        kutoka html agiza unescape
        p = self.get_collector()
        ukijumuisha self.assertWarns(DeprecationWarning):
            s = '&quot;&#34;&#x22;&quot&#34&#x22&#bad;'
            self.assertEqual(p.unescape(s), unescape(s))

    eleza test_broken_comments(self):
        html = ('<! sio really a comment >'
                '<! sio a comment either -->'
                '<! -- close enough -->'
                '<!><!<-- this was an empty comment>'
                '<!!! another bogus comment !!!>')
        expected = [
            ('comment', ' sio really a comment '),
            ('comment', ' sio a comment either --'),
            ('comment', ' -- close enough --'),
            ('comment', ''),
            ('comment', '<-- this was an empty comment'),
            ('comment', '!! another bogus comment !!!'),
        ]
        self._run_check(html, expected)

    eleza test_broken_condcoms(self):
        # these condcoms are missing the '--' after '<!' na before the '>'
        html = ('<![ikiwa !(IE)]>broken condcom<![endif]>'
                '<![ikiwa ! IE]><link href="favicon.tiff"/><![endif]>'
                '<![ikiwa !IE 6]><img src="firefox.png" /><![endif]>'
                '<![ikiwa !ie 6]><b>foo</b><![endif]>'
                '<![ikiwa (!IE)|(lt IE 9)]><img src="mammoth.bmp" /><![endif]>')
        # According to the HTML5 specs sections "8.2.4.44 Bogus comment state"
        # na "8.2.4.45 Markup declaration open state", comment tokens should
        # be emitted instead of 'unknown decl', but calling unknown_decl
        # provides more flexibility.
        # See also Lib/_markupbase.py:parse_declaration
        expected = [
            ('unknown decl', 'ikiwa !(IE)'),
            ('data', 'broken condcom'),
            ('unknown decl', 'endif'),
            ('unknown decl', 'ikiwa ! IE'),
            ('startendtag', 'link', [('href', 'favicon.tiff')]),
            ('unknown decl', 'endif'),
            ('unknown decl', 'ikiwa !IE 6'),
            ('startendtag', 'img', [('src', 'firefox.png')]),
            ('unknown decl', 'endif'),
            ('unknown decl', 'ikiwa !ie 6'),
            ('starttag', 'b', []),
            ('data', 'foo'),
            ('endtag', 'b'),
            ('unknown decl', 'endif'),
            ('unknown decl', 'ikiwa (!IE)|(lt IE 9)'),
            ('startendtag', 'img', [('src', 'mammoth.bmp')]),
            ('unknown decl', 'endif')
        ]
        self._run_check(html, expected)

    eleza test_convert_charrefs_dropped_text(self):
        # #23144: make sure that all the events are triggered when
        # convert_charrefs ni Kweli, even ikiwa we don't call .close()
        parser = EventCollector(convert_charrefs=Kweli)
        # before the fix, bar & baz was missing
        parser.feed("foo <a>link</a> bar &amp; baz")
        self.assertEqual(
            parser.get_events(),
            [('data', 'foo '), ('starttag', 'a', []), ('data', 'link'),
             ('endtag', 'a'), ('data', ' bar & baz')]
        )


kundi AttributesTestCase(TestCaseBase):

    eleza test_attr_syntax(self):
        output = [
          ("starttag", "a", [("b", "v"), ("c", "v"), ("d", "v"), ("e", Tupu)])
        ]
        self._run_check("""<a b='v' c="v" d=v e>""", output)
        self._run_check("""<a  b = 'v' c = "v" d = v e>""", output)
        self._run_check("""<a\nb\n=\n'v'\nc\n=\n"v"\nd\n=\nv\ne>""", output)
        self._run_check("""<a\tb\t=\t'v'\tc\t=\t"v"\td\t=\tv\te>""", output)

    eleza test_attr_values(self):
        self._run_check("""<a b='xxx\n\txxx' c="yyy\t\nyyy" d='\txyz\n'>""",
                        [("starttag", "a", [("b", "xxx\n\txxx"),
                                            ("c", "yyy\t\nyyy"),
                                            ("d", "\txyz\n")])])
        self._run_check("""<a b='' c="">""",
                        [("starttag", "a", [("b", ""), ("c", "")])])
        # Regression test kila SF patch #669683.
        self._run_check("<e a=rgb(1,2,3)>",
                        [("starttag", "e", [("a", "rgb(1,2,3)")])])
        # Regression test kila SF bug #921657.
        self._run_check(
            "<a href=mailto:xyz@example.com>",
            [("starttag", "a", [("href", "mailto:xyz@example.com")])])

    eleza test_attr_nonascii(self):
        # see issue 7311
        self._run_check(
            "<img src=/foo/bar.png alt=\u4e2d\u6587>",
            [("starttag", "img", [("src", "/foo/bar.png"),
                                  ("alt", "\u4e2d\u6587")])])
        self._run_check(
            "<a title='\u30c6\u30b9\u30c8' href='\u30c6\u30b9\u30c8.html'>",
            [("starttag", "a", [("title", "\u30c6\u30b9\u30c8"),
                                ("href", "\u30c6\u30b9\u30c8.html")])])
        self._run_check(
            '<a title="\u30c6\u30b9\u30c8" href="\u30c6\u30b9\u30c8.html">',
            [("starttag", "a", [("title", "\u30c6\u30b9\u30c8"),
                                ("href", "\u30c6\u30b9\u30c8.html")])])

    eleza test_attr_entity_replacement(self):
        self._run_check(
            "<a b='&amp;&gt;&lt;&quot;&apos;'>",
            [("starttag", "a", [("b", "&><\"'")])])

    eleza test_attr_funky_names(self):
        self._run_check(
            "<a a.b='v' c:d=v e-f=v>",
            [("starttag", "a", [("a.b", "v"), ("c:d", "v"), ("e-f", "v")])])

    eleza test_entityrefs_in_attributes(self):
        self._run_check(
            "<html foo='&euro;&amp;&#97;&#x61;&unsupported;'>",
            [("starttag", "html", [("foo", "\u20AC&aa&unsupported;")])])


    eleza test_attr_funky_names2(self):
        self._run_check(
            r"<a $><b $=%><c \=/>",
            [("starttag", "a", [("$", Tupu)]),
             ("starttag", "b", [("$", "%")]),
             ("starttag", "c", [("\\", "/")])])

    eleza test_entities_in_attribute_value(self):
        # see #1200313
        kila entity kwenye ['&', '&amp;', '&#38;', '&#x26;']:
            self._run_check('<a href="%s">' % entity,
                            [("starttag", "a", [("href", "&")])])
            self._run_check("<a href='%s'>" % entity,
                            [("starttag", "a", [("href", "&")])])
            self._run_check("<a href=%s>" % entity,
                            [("starttag", "a", [("href", "&")])])

    eleza test_malformed_attributes(self):
        # see #13357
        html = (
            "<a href=test'style='color:red;bad1'>test - bad1</a>"
            "<a href=test'+style='color:red;ba2'>test - bad2</a>"
            "<a href=test'&nbsp;style='color:red;bad3'>test - bad3</a>"
            "<a href = test'&nbsp;style='color:red;bad4'  >test - bad4</a>"
        )
        expected = [
            ('starttag', 'a', [('href', "test'style='color:red;bad1'")]),
            ('data', 'test - bad1'), ('endtag', 'a'),
            ('starttag', 'a', [('href', "test'+style='color:red;ba2'")]),
            ('data', 'test - bad2'), ('endtag', 'a'),
            ('starttag', 'a', [('href', "test'\xa0style='color:red;bad3'")]),
            ('data', 'test - bad3'), ('endtag', 'a'),
            ('starttag', 'a', [('href', "test'\xa0style='color:red;bad4'")]),
            ('data', 'test - bad4'), ('endtag', 'a')
        ]
        self._run_check(html, expected)

    eleza test_malformed_adjacent_attributes(self):
        # see #12629
        self._run_check('<x><y z=""o"" /></x>',
                        [('starttag', 'x', []),
                            ('startendtag', 'y', [('z', ''), ('o""', Tupu)]),
                            ('endtag', 'x')])
        self._run_check('<x><y z="""" /></x>',
                        [('starttag', 'x', []),
                            ('startendtag', 'y', [('z', ''), ('""', Tupu)]),
                            ('endtag', 'x')])

    # see #755670 kila the following 3 tests
    eleza test_adjacent_attributes(self):
        self._run_check('<a width="100%"cellspacing=0>',
                        [("starttag", "a",
                          [("width", "100%"), ("cellspacing","0")])])

        self._run_check('<a id="foo"class="bar">',
                        [("starttag", "a",
                          [("id", "foo"), ("class","bar")])])

    eleza test_missing_attribute_value(self):
        self._run_check('<a v=>',
                        [("starttag", "a", [("v", "")])])

    eleza test_javascript_attribute_value(self):
        self._run_check("<a href=javascript:popup('/popup/help.html')>",
                        [("starttag", "a",
                          [("href", "javascript:popup('/popup/help.html')")])])

    eleza test_end_tag_in_attribute_value(self):
        # see #1745761
        self._run_check("<a href='http://www.example.org/\">;'>spam</a>",
                        [("starttag", "a",
                          [("href", "http://www.example.org/\">;")]),
                         ("data", "spam"), ("endtag", "a")])


ikiwa __name__ == "__main__":
    unittest.main()
