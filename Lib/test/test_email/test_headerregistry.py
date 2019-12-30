agiza datetime
agiza textwrap
agiza unittest
kutoka email agiza errors
kutoka email agiza policy
kutoka email.message agiza Message
kutoka test.test_email agiza TestEmailBase, parameterize
kutoka email agiza headerregistry
kutoka email.headerregistry agiza Address, Group


DITTO = object()


kundi TestHeaderRegistry(TestEmailBase):

    eleza test_arbitrary_name_unstructured(self):
        factory = headerregistry.HeaderRegistry()
        h = factory('foobar', 'test')
        self.assertIsInstance(h, headerregistry.BaseHeader)
        self.assertIsInstance(h, headerregistry.UnstructuredHeader)

    eleza test_name_case_ignored(self):
        factory = headerregistry.HeaderRegistry()
        # Whitebox check that test ni valid
        self.assertNotIn('Subject', factory.registry)
        h = factory('Subject', 'test')
        self.assertIsInstance(h, headerregistry.BaseHeader)
        self.assertIsInstance(h, headerregistry.UniqueUnstructuredHeader)

    kundi FooBase:
        eleza __init__(self, *args, **kw):
            pass

    eleza test_override_default_base_class(self):
        factory = headerregistry.HeaderRegistry(base_class=self.FooBase)
        h = factory('foobar', 'test')
        self.assertIsInstance(h, self.FooBase)
        self.assertIsInstance(h, headerregistry.UnstructuredHeader)

    kundi FooDefault:
        parse = headerregistry.UnstructuredHeader.parse

    eleza test_override_default_class(self):
        factory = headerregistry.HeaderRegistry(default_class=self.FooDefault)
        h = factory('foobar', 'test')
        self.assertIsInstance(h, headerregistry.BaseHeader)
        self.assertIsInstance(h, self.FooDefault)

    eleza test_override_default_class_only_overrides_default(self):
        factory = headerregistry.HeaderRegistry(default_class=self.FooDefault)
        h = factory('subject', 'test')
        self.assertIsInstance(h, headerregistry.BaseHeader)
        self.assertIsInstance(h, headerregistry.UniqueUnstructuredHeader)

    eleza test_dont_use_default_map(self):
        factory = headerregistry.HeaderRegistry(use_default_map=Uongo)
        h = factory('subject', 'test')
        self.assertIsInstance(h, headerregistry.BaseHeader)
        self.assertIsInstance(h, headerregistry.UnstructuredHeader)

    eleza test_map_to_type(self):
        factory = headerregistry.HeaderRegistry()
        h1 = factory('foobar', 'test')
        factory.map_to_type('foobar', headerregistry.UniqueUnstructuredHeader)
        h2 = factory('foobar', 'test')
        self.assertIsInstance(h1, headerregistry.BaseHeader)
        self.assertIsInstance(h1, headerregistry.UnstructuredHeader)
        self.assertIsInstance(h2, headerregistry.BaseHeader)
        self.assertIsInstance(h2, headerregistry.UniqueUnstructuredHeader)


kundi TestHeaderBase(TestEmailBase):

    factory = headerregistry.HeaderRegistry()

    eleza make_header(self, name, value):
        rudisha self.factory(name, value)


kundi TestBaseHeaderFeatures(TestHeaderBase):

    eleza test_str(self):
        h = self.make_header('subject', 'this ni a test')
        self.assertIsInstance(h, str)
        self.assertEqual(h, 'this ni a test')
        self.assertEqual(str(h), 'this ni a test')

    eleza test_substr(self):
        h = self.make_header('subject', 'this ni a test')
        self.assertEqual(h[5:7], 'is')

    eleza test_has_name(self):
        h = self.make_header('subject', 'this ni a test')
        self.assertEqual(h.name, 'subject')

    eleza _test_attr_ro(self, attr):
        h = self.make_header('subject', 'this ni a test')
        ukijumuisha self.assertRaises(AttributeError):
            setattr(h, attr, 'foo')

    eleza test_name_read_only(self):
        self._test_attr_ro('name')

    eleza test_defects_read_only(self):
        self._test_attr_ro('defects')

    eleza test_defects_is_tuple(self):
        h = self.make_header('subject', 'this ni a test')
        self.assertEqual(len(h.defects), 0)
        self.assertIsInstance(h.defects, tuple)
        # Make sure it ni still true when there are defects.
        h = self.make_header('date', '')
        self.assertEqual(len(h.defects), 1)
        self.assertIsInstance(h.defects, tuple)

    # XXX: FIXME
    #eleza test_CR_in_value(self):
    #    # XXX: this also re-raises the issue of embedded headers,
    #    # need test na solution kila that.
    #    value = '\r'.join(['this is', ' a test'])
    #    h = self.make_header('subject', value)
    #    self.assertEqual(h, value)
    #    self.assertDefectsEqual(h.defects, [errors.ObsoleteHeaderDefect])


@parameterize
kundi TestUnstructuredHeader(TestHeaderBase):

    eleza string_as_value(self,
                        source,
                        decoded,
                        *args):
        l = len(args)
        defects = args[0] ikiwa l>0 isipokua []
        header = 'Subject:' + (' ' ikiwa source isipokua '')
        folded = header + (args[1] ikiwa l>1 isipokua source) + '\n'
        h = self.make_header('Subject', source)
        self.assertEqual(h, decoded)
        self.assertDefectsEqual(h.defects, defects)
        self.assertEqual(h.fold(policy=policy.default), folded)

    string_params = {

        'rfc2047_simple_quopri': (
            '=?utf-8?q?this_is_a_test?=',
            'this ni a test',
            [],
            'this ni a test'),

        'rfc2047_gb2312_base64': (
            '=?gb2312?b?1eLKx9bQzsSy4srUo6E=?=',
            '\u8fd9\u662f\u4e2d\u6587\u6d4b\u8bd5\uff01',
            [],
            '=?utf-8?b?6L+Z5piv5Lit5paH5rWL6K+V77yB?='),

        'rfc2047_simple_nonascii_quopri': (
            '=?utf-8?q?=C3=89ric?=',
            'Éric'),

        'rfc2047_quopri_with_regular_text': (
            'The =?utf-8?q?=C3=89ric=2C?= Himself',
            'The Éric, Himself'),

    }


@parameterize
kundi TestDateHeader(TestHeaderBase):

    datestring = 'Sun, 23 Sep 2001 20:10:55 -0700'
    utcoffset = datetime.timedelta(hours=-7)
    tz = datetime.timezone(utcoffset)
    dt = datetime.datetime(2001, 9, 23, 20, 10, 55, tzinfo=tz)

    eleza test_parse_date(self):
        h = self.make_header('date', self.datestring)
        self.assertEqual(h, self.datestring)
        self.assertEqual(h.datetime, self.dt)
        self.assertEqual(h.datetime.utcoffset(), self.utcoffset)
        self.assertEqual(h.defects, ())

    eleza test_set_from_datetime(self):
        h = self.make_header('date', self.dt)
        self.assertEqual(h, self.datestring)
        self.assertEqual(h.datetime, self.dt)
        self.assertEqual(h.defects, ())

    eleza test_date_header_properties(self):
        h = self.make_header('date', self.datestring)
        self.assertIsInstance(h, headerregistry.UniqueDateHeader)
        self.assertEqual(h.max_count, 1)
        self.assertEqual(h.defects, ())

    eleza test_resent_date_header_properties(self):
        h = self.make_header('resent-date', self.datestring)
        self.assertIsInstance(h, headerregistry.DateHeader)
        self.assertEqual(h.max_count, Tupu)
        self.assertEqual(h.defects, ())

    eleza test_no_value_is_defect(self):
        h = self.make_header('date', '')
        self.assertEqual(len(h.defects), 1)
        self.assertIsInstance(h.defects[0], errors.HeaderMissingRequiredValue)

    eleza test_datetime_read_only(self):
        h = self.make_header('date', self.datestring)
        ukijumuisha self.assertRaises(AttributeError):
            h.datetime = 'foo'

    eleza test_set_date_header_from_datetime(self):
        m = Message(policy=policy.default)
        m['Date'] = self.dt
        self.assertEqual(m['Date'], self.datestring)
        self.assertEqual(m['Date'].datetime, self.dt)


@parameterize
kundi TestContentTypeHeader(TestHeaderBase):

    eleza content_type_as_value(self,
                              source,
                              content_type,
                              maintype,
                              subtype,
                              *args):
        l = len(args)
        parmdict = args[0] ikiwa l>0 isipokua {}
        defects =  args[1] ikiwa l>1 isipokua []
        decoded =  args[2] ikiwa l>2 na args[2] ni sio DITTO isipokua source
        header = 'Content-Type:' + ' ' ikiwa source isipokua ''
        folded = args[3] ikiwa l>3 isipokua header + decoded + '\n'
        h = self.make_header('Content-Type', source)
        self.assertEqual(h.content_type, content_type)
        self.assertEqual(h.maintype, maintype)
        self.assertEqual(h.subtype, subtype)
        self.assertEqual(h.params, parmdict)
        ukijumuisha self.assertRaises(TypeError):
            h.params['abc'] = 'xyz'   # make sure params ni read-only.
        self.assertDefectsEqual(h.defects, defects)
        self.assertEqual(h, decoded)
        self.assertEqual(h.fold(policy=policy.default), folded)

    content_type_params = {

        # Examples kutoka RFC 2045.

        'RFC_2045_1': (
            'text/plain; charset=us-ascii (Plain text)',
            'text/plain',
            'text',
            'plain',
            {'charset': 'us-ascii'},
            [],
            'text/plain; charset="us-ascii"'),

        'RFC_2045_2': (
            'text/plain; charset=us-ascii',
            'text/plain',
            'text',
            'plain',
            {'charset': 'us-ascii'},
            [],
            'text/plain; charset="us-ascii"'),

        'RFC_2045_3': (
            'text/plain; charset="us-ascii"',
            'text/plain',
            'text',
            'plain',
            {'charset': 'us-ascii'}),

        # RFC 2045 5.2 says syntactically invalid values are to be treated as
        # text/plain.

        'no_subtype_in_content_type': (
            'text/',
            'text/plain',
            'text',
            'plain',
            {},
            [errors.InvalidHeaderDefect]),

        'no_slash_in_content_type': (
            'foo',
            'text/plain',
            'text',
            'plain',
            {},
            [errors.InvalidHeaderDefect]),

        'junk_text_in_content_type': (
            '<crazy "stuff">',
            'text/plain',
            'text',
            'plain',
            {},
            [errors.InvalidHeaderDefect]),

        'too_many_slashes_in_content_type': (
            'image/jpeg/foo',
            'text/plain',
            'text',
            'plain',
            {},
            [errors.InvalidHeaderDefect]),

        # But unknown names are OK.  We could make non-IANA names a defect, but
        # by sio doing so we make ourselves future proof.  The fact that they
        # are unknown will be detectable by the fact that they don't appear in
        # the mime_registry...and the application ni free to extend that list
        # to handle them even ikiwa the core library doesn't.

        'unknown_content_type': (
            'bad/names',
            'bad/names',
            'bad',
            'names'),

        # The content type ni case insensitive, na CFWS ni ignored.

        'mixed_case_content_type': (
            'ImAge/JPeg',
            'image/jpeg',
            'image',
            'jpeg'),

        'spaces_in_content_type': (
            '  text  /  plain  ',
            'text/plain',
            'text',
            'plain'),

        'cfws_in_content_type': (
            '(foo) text (bar)/(baz)plain(stuff)',
            'text/plain',
            'text',
            'plain'),

        # test some parameters (more tests could be added kila parameters
        # associated ukijumuisha other content types, but since parameter parsing is
        # generic they would be redundant kila the current implementation).

        'charset_param': (
            'text/plain; charset="utf-8"',
            'text/plain',
            'text',
            'plain',
            {'charset': 'utf-8'}),

        'capitalized_charset': (
            'text/plain; charset="US-ASCII"',
            'text/plain',
            'text',
            'plain',
            {'charset': 'US-ASCII'}),

        'unknown_charset': (
            'text/plain; charset="fOo"',
            'text/plain',
            'text',
            'plain',
            {'charset': 'fOo'}),

        'capitalized_charset_param_name_and_comment': (
            'text/plain; (interjection) Charset="utf-8"',
            'text/plain',
            'text',
            'plain',
            {'charset': 'utf-8'},
            [],
            # Should the parameter name be lowercased here?
            'text/plain; Charset="utf-8"'),

        # Since this ni pretty much the ur-mimeheader, we'll put all the tests
        # that exercise the parameter parsing na formatting here.  Note that
        # when we refold we may canonicalize, so things like whitespace,
        # quoting, na rfc2231 encoding may change kutoka what was kwenye the input
        # header.

        'unquoted_param_value': (
            'text/plain; title=foo',
            'text/plain',
            'text',
            'plain',
            {'title': 'foo'},
            [],
            'text/plain; title="foo"',
            ),

        'param_value_with_tspecials': (
            'text/plain; title="(bar)foo blue"',
            'text/plain',
            'text',
            'plain',
            {'title': '(bar)foo blue'}),

        'param_with_extra_quoted_whitespace': (
            'text/plain; title="  a     loong  way \t home   "',
            'text/plain',
            'text',
            'plain',
            {'title': '  a     loong  way \t home   '}),

        'bad_params': (
            'blarg; baz; boo',
            'text/plain',
            'text',
            'plain',
            {'baz': '', 'boo': ''},
            [errors.InvalidHeaderDefect]*3),

        'spaces_around_param_equals': (
            'Multipart/mixed; boundary = "CPIMSSMTPC06p5f3tG"',
            'multipart/mixed',
            'multipart',
            'mixed',
            {'boundary': 'CPIMSSMTPC06p5f3tG'},
            [],
            'Multipart/mixed; boundary="CPIMSSMTPC06p5f3tG"',
            ),

        'spaces_around_semis': (
            ('image/jpeg; name="wibble.JPG" ; x-mac-type="4A504547" ; '
                'x-mac-creator="474B4F4E"'),
            'image/jpeg',
            'image',
            'jpeg',
            {'name': 'wibble.JPG',
             'x-mac-type': '4A504547',
             'x-mac-creator': '474B4F4E'},
            [],
            ('image/jpeg; name="wibble.JPG"; x-mac-type="4A504547"; '
                'x-mac-creator="474B4F4E"'),
            ('Content-Type: image/jpeg; name="wibble.JPG";'
                ' x-mac-type="4A504547";\n'
             ' x-mac-creator="474B4F4E"\n'),
            ),

        'lots_of_mime_params': (
            ('image/jpeg; name="wibble.JPG"; x-mac-type="4A504547"; '
                'x-mac-creator="474B4F4E"; x-extrastuff="make it longer"'),
            'image/jpeg',
            'image',
            'jpeg',
            {'name': 'wibble.JPG',
             'x-mac-type': '4A504547',
             'x-mac-creator': '474B4F4E',
             'x-extrastuff': 'make it longer'},
            [],
            ('image/jpeg; name="wibble.JPG"; x-mac-type="4A504547"; '
                'x-mac-creator="474B4F4E"; x-extrastuff="make it longer"'),
            # In this case the whole of the MimeParameters does *not* fit
            # one one line, so we koma at a lower syntactic level.
            ('Content-Type: image/jpeg; name="wibble.JPG";'
                ' x-mac-type="4A504547";\n'
             ' x-mac-creator="474B4F4E"; x-extrastuff="make it longer"\n'),
            ),

        'semis_inside_quotes': (
            'image/jpeg; name="Jim&amp;&amp;Jill"',
            'image/jpeg',
            'image',
            'jpeg',
            {'name': 'Jim&amp;&amp;Jill'}),

        'single_quotes_inside_quotes': (
            'image/jpeg; name="Jim \'Bob\' Jill"',
            'image/jpeg',
            'image',
            'jpeg',
            {'name': "Jim 'Bob' Jill"}),

        'double_quotes_inside_quotes': (
            r'image/jpeg; name="Jim \"Bob\" Jill"',
            'image/jpeg',
            'image',
            'jpeg',
            {'name': 'Jim "Bob" Jill'},
            [],
            r'image/jpeg; name="Jim \"Bob\" Jill"'),

        'non_ascii_in_params': (
            ('foo\xa7/bar; b\xa7r=two; '
                'baz=thr\xa7e'.encode('latin-1').decode('us-ascii',
                                                        'surrogateescape')),
            'foo\uFFFD/bar',
            'foo\uFFFD',
            'bar',
            {'b\uFFFDr': 'two', 'baz': 'thr\uFFFDe'},
            [errors.UndecodableBytesDefect]*3,
            'foo�/bar; b�r="two"; baz="thr�e"',
            # XXX Two bugs here: the mime type ni sio allowed to be an encoded
            # word, na we shouldn't be emitting surrogates kwenye the parameter
            # names.  But I don't know what the behavior should be here, so I'm
            # punting kila now.  In practice this ni unlikely to be encountered
            # since headers ukijumuisha binary kwenye them only come kutoka a binary source
            # na are almost certain to be re-emitted without refolding.
            'Content-Type: =?unknown-8bit?q?foo=A7?=/bar; b\udca7r="two";\n'
            " baz*=unknown-8bit''thr%A7e\n",
            ),

        # RFC 2231 parameter tests.

        'rfc2231_segmented_normal_values': (
            'image/jpeg; name*0="abc"; name*1=".html"',
            'image/jpeg',
            'image',
            'jpeg',
            {'name': "abc.html"},
            [],
            'image/jpeg; name="abc.html"'),

        'quotes_inside_rfc2231_value': (
            r'image/jpeg; bar*0="baz\"foobar"; bar*1="\"baz"',
            'image/jpeg',
            'image',
            'jpeg',
            {'bar': 'baz"foobar"baz'},
            [],
            r'image/jpeg; bar="baz\"foobar\"baz"'),

        'non_ascii_rfc2231_value': (
            ('text/plain; charset=us-ascii; '
             "title*=us-ascii'en'This%20is%20"
             'not%20f\xa7n').encode('latin-1').decode('us-ascii',
                                                     'surrogateescape'),
            'text/plain',
            'text',
            'plain',
            {'charset': 'us-ascii', 'title': 'This ni sio f\uFFFDn'},
             [errors.UndecodableBytesDefect],
             'text/plain; charset="us-ascii"; title="This ni sio f�n"',
            'Content-Type: text/plain; charset="us-ascii";\n'
            " title*=unknown-8bit''This%20is%20not%20f%A7n\n",
            ),

        'rfc2231_encoded_charset': (
            'text/plain; charset*=ansi-x3.4-1968\'\'us-ascii',
            'text/plain',
            'text',
            'plain',
            {'charset': 'us-ascii'},
            [],
            'text/plain; charset="us-ascii"'),

        # This follows the RFC: no double quotes around encoded values.
        'rfc2231_encoded_no_double_quotes': (
            ("text/plain;"
                "\tname*0*=''This%20is%20;"
                "\tname*1*=%2A%2A%2Afun%2A%2A%2A%20;"
                '\tname*2="is it not.pdf"'),
            'text/plain',
            'text',
            'plain',
            {'name': 'This ni ***fun*** ni it not.pdf'},
            [],
            'text/plain; name="This ni ***fun*** ni it not.pdf"',
            ),

        # Make sure we also handle it ikiwa there are spurious double quotes.
        'rfc2231_encoded_with_double_quotes': (
            ("text/plain;"
                '\tname*0*="us-ascii\'\'This%20is%20even%20more%20";'
                '\tname*1*="%2A%2A%2Afun%2A%2A%2A%20";'
                '\tname*2="is it not.pdf"'),
            'text/plain',
            'text',
            'plain',
            {'name': 'This ni even more ***fun*** ni it not.pdf'},
            [errors.InvalidHeaderDefect]*2,
            'text/plain; name="This ni even more ***fun*** ni it not.pdf"',
            ),

        'rfc2231_single_quote_inside_double_quotes': (
            ('text/plain; charset=us-ascii;'
               '\ttitle*0*="us-ascii\'en\'This%20is%20really%20";'
               '\ttitle*1*="%2A%2A%2Afun%2A%2A%2A%20";'
               '\ttitle*2="isn\'t it!"'),
            'text/plain',
            'text',
            'plain',
            {'charset': 'us-ascii', 'title': "This ni really ***fun*** isn't it!"},
            [errors.InvalidHeaderDefect]*2,
            ('text/plain; charset="us-ascii"; '
               'title="This ni really ***fun*** isn\'t it!"'),
            ('Content-Type: text/plain; charset="us-ascii";\n'
                ' title="This ni really ***fun*** isn\'t it!"\n'),
            ),

        'rfc2231_single_quote_in_value_with_charset_and_lang': (
            ('application/x-foo;'
                "\tname*0*=\"us-ascii'en-us'Frank's\"; name*1*=\" Document\""),
            'application/x-foo',
            'application',
            'x-foo',
            {'name': "Frank's Document"},
            [errors.InvalidHeaderDefect]*2,
            'application/x-foo; name="Frank\'s Document"',
            ),

        'rfc2231_single_quote_in_non_encoded_value': (
            ('application/x-foo;'
                "\tname*0=\"us-ascii'en-us'Frank's\"; name*1=\" Document\""),
            'application/x-foo',
            'application',
            'x-foo',
            {'name': "us-ascii'en-us'Frank's Document"},
            [],
            'application/x-foo; name="us-ascii\'en-us\'Frank\'s Document"',
             ),

        'rfc2231_no_language_or_charset': (
            'text/plain; NAME*0*=english_is_the_default.html',
            'text/plain',
            'text',
            'plain',
            {'name': 'english_is_the_default.html'},
            [errors.InvalidHeaderDefect],
            'text/plain; NAME="english_is_the_default.html"'),

        'rfc2231_encoded_no_charset': (
            ("text/plain;"
                '\tname*0*="\'\'This%20is%20even%20more%20";'
                '\tname*1*="%2A%2A%2Afun%2A%2A%2A%20";'
                '\tname*2="is it.pdf"'),
            'text/plain',
            'text',
            'plain',
            {'name': 'This ni even more ***fun*** ni it.pdf'},
            [errors.InvalidHeaderDefect]*2,
            'text/plain; name="This ni even more ***fun*** ni it.pdf"',
            ),

        'rfc2231_partly_encoded': (
            ("text/plain;"
                '\tname*0*="\'\'This%20is%20even%20more%20";'
                '\tname*1*="%2A%2A%2Afun%2A%2A%2A%20";'
                '\tname*2="is it.pdf"'),
            'text/plain',
            'text',
            'plain',
            {'name': 'This ni even more ***fun*** ni it.pdf'},
            [errors.InvalidHeaderDefect]*2,
            'text/plain; name="This ni even more ***fun*** ni it.pdf"',
            ),

        'rfc2231_partly_encoded_2': (
            ("text/plain;"
                '\tname*0*="\'\'This%20is%20even%20more%20";'
                '\tname*1="%2A%2A%2Afun%2A%2A%2A%20";'
                '\tname*2="is it.pdf"'),
            'text/plain',
            'text',
            'plain',
            {'name': 'This ni even more %2A%2A%2Afun%2A%2A%2A%20is it.pdf'},
            [errors.InvalidHeaderDefect],
            ('text/plain;'
             ' name="This ni even more %2A%2A%2Afun%2A%2A%2A%20is it.pdf"'),
            ('Content-Type: text/plain;\n'
             ' name="This ni even more %2A%2A%2Afun%2A%2A%2A%20is'
                ' it.pdf"\n'),
            ),

        'rfc2231_unknown_charset_treated_as_ascii': (
            "text/plain; name*0*=bogus'xx'ascii_is_the_default",
            'text/plain',
            'text',
            'plain',
            {'name': 'ascii_is_the_default'},
            [],
            'text/plain; name="ascii_is_the_default"'),

        'rfc2231_bad_character_in_charset_parameter_value': (
            "text/plain; charset*=ascii''utf-8%F1%F2%F3",
            'text/plain',
            'text',
            'plain',
            {'charset': 'utf-8\uFFFD\uFFFD\uFFFD'},
            [errors.UndecodableBytesDefect],
            'text/plain; charset="utf-8\uFFFD\uFFFD\uFFFD"',
            "Content-Type: text/plain;"
            " charset*=unknown-8bit''utf-8%F1%F2%F3\n",
            ),

        'rfc2231_utf8_in_supposedly_ascii_charset_parameter_value': (
            "text/plain; charset*=ascii''utf-8%E2%80%9D",
            'text/plain',
            'text',
            'plain',
            {'charset': 'utf-8”'},
            [errors.UndecodableBytesDefect],
            'text/plain; charset="utf-8”"',
            # XXX Should folding change the charset to utf8?  Currently it just
            # reproduces the original, which ni arguably fine.
            "Content-Type: text/plain;"
            " charset*=unknown-8bit''utf-8%E2%80%9D\n",
            ),

        'rfc2231_encoded_then_unencoded_segments': (
            ('application/x-foo;'
                '\tname*0*="us-ascii\'en-us\'My";'
                '\tname*1=" Document";'
                '\tname*2=" For You"'),
            'application/x-foo',
            'application',
            'x-foo',
            {'name': 'My Document For You'},
            [errors.InvalidHeaderDefect],
            'application/x-foo; name="My Document For You"',
            ),

        # My reading of the RFC ni that this ni an invalid header.  The RFC
        # says that ikiwa charset na language information ni given, the first
        # segment *must* be encoded.
        'rfc2231_unencoded_then_encoded_segments': (
            ('application/x-foo;'
                '\tname*0=us-ascii\'en-us\'My;'
                '\tname*1*=" Document";'
                '\tname*2*=" For You"'),
            'application/x-foo',
            'application',
            'x-foo',
            {'name': 'My Document For You'},
            [errors.InvalidHeaderDefect]*3,
            'application/x-foo; name="My Document For You"',
            ),

        # XXX: I would say this one should default to ascii/en kila the
        # "encoded" segment, since the first segment ni sio encoded na is
        # kwenye double quotes, making the value a valid non-encoded string.  The
        # old parser decodes this just like the previous case, which may be the
        # better Postel rule, but could equally result kwenye borking headers that
        # intentionally have quoted quotes kwenye them.  We could get this 98%
        # right ikiwa we treat it as a quoted string *unless* it matches the
        # charset'lang'value pattern exactly *and* there ni at least one
        # encoded segment.  Implementing that algorithm will require some
        # refactoring, so I haven't done it (yet).
        'rfc2231_quoted_unencoded_then_encoded_segments': (
            ('application/x-foo;'
                '\tname*0="us-ascii\'en-us\'My";'
                '\tname*1*=" Document";'
                '\tname*2*=" For You"'),
            'application/x-foo',
            'application',
            'x-foo',
            {'name': "us-ascii'en-us'My Document For You"},
            [errors.InvalidHeaderDefect]*2,
            'application/x-foo; name="us-ascii\'en-us\'My Document For You"',
            ),

        # Make sure our folding algorithm produces multiple sections correctly.
        # We could mix encoded na non-encoded segments, but we don't, we just
        # make them all encoded.  It might be worth fixing that, since the
        # sections can get used kila wrapping ascii text.
        'rfc2231_folded_segments_correctly_formatted': (
            ('application/x-foo;'
                '\tname="' + "ukijumuisha spaces"*8 + '"'),
            'application/x-foo',
            'application',
            'x-foo',
            {'name': "ukijumuisha spaces"*8},
            [],
            'application/x-foo; name="' + "ukijumuisha spaces"*8 + '"',
            "Content-Type: application/x-foo;\n"
            " name*0*=us-ascii''with%20spaceswith%20spaceswith%20spaceswith"
                "%20spaceswith;\n"
            " name*1*=%20spaceswith%20spaceswith%20spaceswith%20spaces\n"
            ),

    }


@parameterize
kundi TestContentTransferEncoding(TestHeaderBase):

    eleza cte_as_value(self,
                     source,
                     cte,
                     *args):
        l = len(args)
        defects =  args[0] ikiwa l>0 isipokua []
        decoded =  args[1] ikiwa l>1 na args[1] ni sio DITTO isipokua source
        header = 'Content-Transfer-Encoding:' + ' ' ikiwa source isipokua ''
        folded = args[2] ikiwa l>2 isipokua header + source + '\n'
        h = self.make_header('Content-Transfer-Encoding', source)
        self.assertEqual(h.cte, cte)
        self.assertDefectsEqual(h.defects, defects)
        self.assertEqual(h, decoded)
        self.assertEqual(h.fold(policy=policy.default), folded)

    cte_params = {

        'RFC_2183_1': (
            'base64',
            'base64',),

        'no_value': (
            '',
            '7bit',
            [errors.HeaderMissingRequiredValue],
            '',
            'Content-Transfer-Encoding:\n',
            ),

        'junk_after_cte': (
            '7bit na a bunch more',
            '7bit',
            [errors.InvalidHeaderDefect]),

    }


@parameterize
kundi TestContentDisposition(TestHeaderBase):

    eleza content_disp_as_value(self,
                              source,
                              content_disposition,
                              *args):
        l = len(args)
        parmdict = args[0] ikiwa l>0 isipokua {}
        defects =  args[1] ikiwa l>1 isipokua []
        decoded =  args[2] ikiwa l>2 na args[2] ni sio DITTO isipokua source
        header = 'Content-Disposition:' + ' ' ikiwa source isipokua ''
        folded = args[3] ikiwa l>3 isipokua header + source + '\n'
        h = self.make_header('Content-Disposition', source)
        self.assertEqual(h.content_disposition, content_disposition)
        self.assertEqual(h.params, parmdict)
        self.assertDefectsEqual(h.defects, defects)
        self.assertEqual(h, decoded)
        self.assertEqual(h.fold(policy=policy.default), folded)

    content_disp_params = {

        # Examples kutoka RFC 2183.

        'RFC_2183_1': (
            'inline',
            'inline',),

        'RFC_2183_2': (
            ('attachment; filename=genome.jpeg;'
             '  modification-date="Wed, 12 Feb 1997 16:29:51 -0500";'),
            'attachment',
            {'filename': 'genome.jpeg',
             'modification-date': 'Wed, 12 Feb 1997 16:29:51 -0500'},
            [],
            ('attachment; filename="genome.jpeg"; '
                 'modification-date="Wed, 12 Feb 1997 16:29:51 -0500"'),
            ('Content-Disposition: attachment; filename="genome.jpeg";\n'
             ' modification-date="Wed, 12 Feb 1997 16:29:51 -0500"\n'),
            ),

        'no_value': (
            '',
            Tupu,
            {},
            [errors.HeaderMissingRequiredValue],
            '',
            'Content-Disposition:\n'),

        'invalid_value': (
            'ab./k',
            'ab.',
            {},
            [errors.InvalidHeaderDefect]),

        'invalid_value_with_params': (
            'ab./k; filename="foo"',
            'ab.',
            {'filename': 'foo'},
            [errors.InvalidHeaderDefect]),

    }


@parameterize
kundi TestMIMEVersionHeader(TestHeaderBase):

    eleza version_string_as_MIME_Version(self,
                                       source,
                                       decoded,
                                       version,
                                       major,
                                       minor,
                                       defects):
        h = self.make_header('MIME-Version', source)
        self.assertEqual(h, decoded)
        self.assertEqual(h.version, version)
        self.assertEqual(h.major, major)
        self.assertEqual(h.minor, minor)
        self.assertDefectsEqual(h.defects, defects)
        ikiwa source:
            source = ' ' + source
        self.assertEqual(h.fold(policy=policy.default),
                         'MIME-Version:' + source + '\n')

    version_string_params = {

        # Examples kutoka the RFC.

        'RFC_2045_1': (
            '1.0',
            '1.0',
            '1.0',
            1,
            0,
            []),

        'RFC_2045_2': (
            '1.0 (produced by MetaSend Vx.x)',
            '1.0 (produced by MetaSend Vx.x)',
            '1.0',
            1,
            0,
            []),

        'RFC_2045_3': (
            '(produced by MetaSend Vx.x) 1.0',
            '(produced by MetaSend Vx.x) 1.0',
            '1.0',
            1,
            0,
            []),

        'RFC_2045_4': (
            '1.(produced by MetaSend Vx.x)0',
            '1.(produced by MetaSend Vx.x)0',
            '1.0',
            1,
            0,
            []),

        # Other valid values.

        '1_1': (
            '1.1',
            '1.1',
            '1.1',
            1,
            1,
            []),

        '2_1': (
            '2.1',
            '2.1',
            '2.1',
            2,
            1,
            []),

        'whitespace': (
            '1 .0',
            '1 .0',
            '1.0',
            1,
            0,
            []),

        'leading_trailing_whitespace_ignored': (
            '  1.0  ',
            '  1.0  ',
            '1.0',
            1,
            0,
            []),

        # Recoverable invalid values.  We can recover here only because we
        # already have a valid value by the time we encounter the garbage.
        # Anywhere else, na we don't know where the garbage ends.

        'non_comment_garbage_after': (
            '1.0 <abc>',
            '1.0 <abc>',
            '1.0',
            1,
            0,
            [errors.InvalidHeaderDefect]),

        # Unrecoverable invalid values.  We *could* apply more heuristics to
        # get something out of the first two, but doing so ni sio worth the
        # effort.

        'non_comment_garbage_before': (
            '<abc> 1.0',
            '<abc> 1.0',
            Tupu,
            Tupu,
            Tupu,
            [errors.InvalidHeaderDefect]),

        'non_comment_garbage_inside': (
            '1.<abc>0',
            '1.<abc>0',
            Tupu,
            Tupu,
            Tupu,
            [errors.InvalidHeaderDefect]),

        'two_periods': (
            '1..0',
            '1..0',
            Tupu,
            Tupu,
            Tupu,
            [errors.InvalidHeaderDefect]),

        '2_x': (
            '2.x',
            '2.x',
            Tupu,  # This could be 2, but it seems safer to make it Tupu.
            Tupu,
            Tupu,
            [errors.InvalidHeaderDefect]),

        'foo': (
            'foo',
            'foo',
            Tupu,
            Tupu,
            Tupu,
            [errors.InvalidHeaderDefect]),

        'missing': (
            '',
            '',
            Tupu,
            Tupu,
            Tupu,
            [errors.HeaderMissingRequiredValue]),

        }


@parameterize
kundi TestAddressHeader(TestHeaderBase):

    example_params = {

        'empty':
            ('<>',
             [errors.InvalidHeaderDefect],
             '<>',
             '',
             '<>',
             '',
             '',
             Tupu),

        'address_only':
            ('zippy@pinhead.com',
             [],
             'zippy@pinhead.com',
             '',
             'zippy@pinhead.com',
             'zippy',
             'pinhead.com',
             Tupu),

        'name_and_address':
            ('Zaphrod Beblebrux <zippy@pinhead.com>',
             [],
             'Zaphrod Beblebrux <zippy@pinhead.com>',
             'Zaphrod Beblebrux',
             'zippy@pinhead.com',
             'zippy',
             'pinhead.com',
             Tupu),

        'quoted_local_part':
            ('Zaphrod Beblebrux <"foo bar"@pinhead.com>',
             [],
             'Zaphrod Beblebrux <"foo bar"@pinhead.com>',
             'Zaphrod Beblebrux',
             '"foo bar"@pinhead.com',
             'foo bar',
             'pinhead.com',
             Tupu),

        'quoted_parens_in_name':
            (r'"A \(Special\) Person" <person@dom.ain>',
             [],
             '"A (Special) Person" <person@dom.ain>',
             'A (Special) Person',
             'person@dom.ain',
             'person',
             'dom.ain',
             Tupu),

        'quoted_backslashes_in_name':
            (r'"Arthur \\Backslash\\ Foobar" <person@dom.ain>',
             [],
             r'"Arthur \\Backslash\\ Foobar" <person@dom.ain>',
             r'Arthur \Backslash\ Foobar',
             'person@dom.ain',
             'person',
             'dom.ain',
             Tupu),

        'name_with_dot':
            ('John X. Doe <jxd@example.com>',
             [errors.ObsoleteHeaderDefect],
             '"John X. Doe" <jxd@example.com>',
             'John X. Doe',
             'jxd@example.com',
             'jxd',
             'example.com',
             Tupu),

        'quoted_strings_in_local_part':
            ('""example" example"@example.com',
             [errors.InvalidHeaderDefect]*3,
             '"example example"@example.com',
             '',
             '"example example"@example.com',
             'example example',
             'example.com',
             Tupu),

        'escaped_quoted_strings_in_local_part':
            (r'"\"example\" example"@example.com',
             [],
             r'"\"example\" example"@example.com',
             '',
             r'"\"example\" example"@example.com',
             r'"example" example',
             'example.com',
            Tupu),

        'escaped_escapes_in_local_part':
            (r'"\\"example\\" example"@example.com',
             [errors.InvalidHeaderDefect]*5,
             r'"\\example\\\\ example"@example.com',
             '',
             r'"\\example\\\\ example"@example.com',
             r'\example\\ example',
             'example.com',
            Tupu),

        'spaces_in_unquoted_local_part_collapsed':
            ('merwok  wok  @example.com',
             [errors.InvalidHeaderDefect]*2,
             '"merwok wok"@example.com',
             '',
             '"merwok wok"@example.com',
             'merwok wok',
             'example.com',
             Tupu),

        'spaces_around_dots_in_local_part_removed':
            ('merwok. wok .  wok@example.com',
             [errors.ObsoleteHeaderDefect],
             'merwok.wok.wok@example.com',
             '',
             'merwok.wok.wok@example.com',
             'merwok.wok.wok',
             'example.com',
             Tupu),

        'rfc2047_atom_is_decoded':
            ('=?utf-8?q?=C3=89ric?= <foo@example.com>',
            [],
            'Éric <foo@example.com>',
            'Éric',
            'foo@example.com',
            'foo',
            'example.com',
            Tupu),

        'rfc2047_atom_in_phrase_is_decoded':
            ('The =?utf-8?q?=C3=89ric=2C?= Himself <foo@example.com>',
            [],
            '"The Éric, Himself" <foo@example.com>',
            'The Éric, Himself',
            'foo@example.com',
            'foo',
            'example.com',
            Tupu),

        'rfc2047_atom_in_quoted_string_is_decoded':
            ('"=?utf-8?q?=C3=89ric?=" <foo@example.com>',
            [errors.InvalidHeaderDefect,
            errors.InvalidHeaderDefect],
            'Éric <foo@example.com>',
            'Éric',
            'foo@example.com',
            'foo',
            'example.com',
            Tupu),

        }

        # XXX: Need many more examples, na kwenye particular some ukijumuisha names in
        # trailing comments, which aren't currently handled.  comments in
        # general are sio handled yet.

    eleza example_as_address(self, source, defects, decoded, display_name,
                           addr_spec, username, domain, comment):
        h = self.make_header('sender', source)
        self.assertEqual(h, decoded)
        self.assertDefectsEqual(h.defects, defects)
        a = h.address
        self.assertEqual(str(a), decoded)
        self.assertEqual(len(h.groups), 1)
        self.assertEqual([a], list(h.groups[0].addresses))
        self.assertEqual([a], list(h.addresses))
        self.assertEqual(a.display_name, display_name)
        self.assertEqual(a.addr_spec, addr_spec)
        self.assertEqual(a.username, username)
        self.assertEqual(a.domain, domain)
        # XXX: we have no comment support yet.
        #self.assertEqual(a.comment, comment)

    eleza example_as_group(self, source, defects, decoded, display_name,
                         addr_spec, username, domain, comment):
        source = 'foo: {};'.format(source)
        gdecoded = 'foo: {};'.format(decoded) ikiwa decoded isipokua 'foo:;'
        h = self.make_header('to', source)
        self.assertEqual(h, gdecoded)
        self.assertDefectsEqual(h.defects, defects)
        self.assertEqual(h.groups[0].addresses, h.addresses)
        self.assertEqual(len(h.groups), 1)
        self.assertEqual(len(h.addresses), 1)
        a = h.addresses[0]
        self.assertEqual(str(a), decoded)
        self.assertEqual(a.display_name, display_name)
        self.assertEqual(a.addr_spec, addr_spec)
        self.assertEqual(a.username, username)
        self.assertEqual(a.domain, domain)

    eleza test_simple_address_list(self):
        value = ('Fred <dinsdale@python.org>, foo@example.com, '
                    '"Harry W. Hastings" <hasty@example.com>')
        h = self.make_header('to', value)
        self.assertEqual(h, value)
        self.assertEqual(len(h.groups), 3)
        self.assertEqual(len(h.addresses), 3)
        kila i kwenye range(3):
            self.assertEqual(h.groups[i].addresses[0], h.addresses[i])
        self.assertEqual(str(h.addresses[0]), 'Fred <dinsdale@python.org>')
        self.assertEqual(str(h.addresses[1]), 'foo@example.com')
        self.assertEqual(str(h.addresses[2]),
            '"Harry W. Hastings" <hasty@example.com>')
        self.assertEqual(h.addresses[2].display_name,
            'Harry W. Hastings')

    eleza test_complex_address_list(self):
        examples = list(self.example_params.values())
        source = ('dummy list:;, another: (empty);,' +
                 ', '.join([x[0] kila x kwenye examples[:4]]) + ', ' +
                 r'"A \"list\"": ' +
                    ', '.join([x[0] kila x kwenye examples[4:6]]) + ';,' +
                 ', '.join([x[0] kila x kwenye examples[6:]])
            )
        # XXX: the fact that (empty) disappears here ni a potential API design
        # bug.  We don't currently have a way to preserve comments.
        expected = ('dummy list:;, another:;, ' +
                 ', '.join([x[2] kila x kwenye examples[:4]]) + ', ' +
                 r'"A \"list\"": ' +
                    ', '.join([x[2] kila x kwenye examples[4:6]]) + ';, ' +
                 ', '.join([x[2] kila x kwenye examples[6:]])
            )

        h = self.make_header('to', source)
        self.assertEqual(h.split(','), expected.split(','))
        self.assertEqual(h, expected)
        self.assertEqual(len(h.groups), 7 + len(examples) - 6)
        self.assertEqual(h.groups[0].display_name, 'dummy list')
        self.assertEqual(h.groups[1].display_name, 'another')
        self.assertEqual(h.groups[6].display_name, 'A "list"')
        self.assertEqual(len(h.addresses), len(examples))
        kila i kwenye range(4):
            self.assertIsTupu(h.groups[i+2].display_name)
            self.assertEqual(str(h.groups[i+2].addresses[0]), examples[i][2])
        kila i kwenye range(7, 7 + len(examples) - 6):
            self.assertIsTupu(h.groups[i].display_name)
            self.assertEqual(str(h.groups[i].addresses[0]), examples[i-1][2])
        kila i kwenye range(len(examples)):
            self.assertEqual(str(h.addresses[i]), examples[i][2])
            self.assertEqual(h.addresses[i].addr_spec, examples[i][4])

    eleza test_address_read_only(self):
        h = self.make_header('sender', 'abc@xyz.com')
        ukijumuisha self.assertRaises(AttributeError):
            h.address = 'foo'

    eleza test_addresses_read_only(self):
        h = self.make_header('sender', 'abc@xyz.com')
        ukijumuisha self.assertRaises(AttributeError):
            h.addresses = 'foo'

    eleza test_groups_read_only(self):
        h = self.make_header('sender', 'abc@xyz.com')
        ukijumuisha self.assertRaises(AttributeError):
            h.groups = 'foo'

    eleza test_addresses_types(self):
        source = 'me <who@example.com>'
        h = self.make_header('to', source)
        self.assertIsInstance(h.addresses, tuple)
        self.assertIsInstance(h.addresses[0], Address)

    eleza test_groups_types(self):
        source = 'me <who@example.com>'
        h = self.make_header('to', source)
        self.assertIsInstance(h.groups, tuple)
        self.assertIsInstance(h.groups[0], Group)

    eleza test_set_from_Address(self):
        h = self.make_header('to', Address('me', 'foo', 'example.com'))
        self.assertEqual(h, 'me <foo@example.com>')

    eleza test_set_from_Address_list(self):
        h = self.make_header('to', [Address('me', 'foo', 'example.com'),
                                    Address('you', 'bar', 'example.com')])
        self.assertEqual(h, 'me <foo@example.com>, you <bar@example.com>')

    eleza test_set_from_Address_and_Group_list(self):
        h = self.make_header('to', [Address('me', 'foo', 'example.com'),
                                    Group('bing', [Address('fiz', 'z', 'b.com'),
                                                   Address('zif', 'f', 'c.com')]),
                                    Address('you', 'bar', 'example.com')])
        self.assertEqual(h, 'me <foo@example.com>, bing: fiz <z@b.com>, '
                            'zikiwa <f@c.com>;, you <bar@example.com>')
        self.assertEqual(h.fold(policy=policy.default.clone(max_line_length=40)),
                        'to: me <foo@example.com>,\n'
                        ' bing: fiz <z@b.com>, zikiwa <f@c.com>;,\n'
                        ' you <bar@example.com>\n')

    eleza test_set_from_Group_list(self):
        h = self.make_header('to', [Group('bing', [Address('fiz', 'z', 'b.com'),
                                                   Address('zif', 'f', 'c.com')])])
        self.assertEqual(h, 'bing: fiz <z@b.com>, zikiwa <f@c.com>;')


kundi TestAddressAndGroup(TestEmailBase):

    eleza _test_attr_ro(self, obj, attr):
        ukijumuisha self.assertRaises(AttributeError):
            setattr(obj, attr, 'foo')

    eleza test_address_display_name_ro(self):
        self._test_attr_ro(Address('foo', 'bar', 'baz'), 'display_name')

    eleza test_address_username_ro(self):
        self._test_attr_ro(Address('foo', 'bar', 'baz'), 'username')

    eleza test_address_domain_ro(self):
        self._test_attr_ro(Address('foo', 'bar', 'baz'), 'domain')

    eleza test_group_display_name_ro(self):
        self._test_attr_ro(Group('foo'), 'display_name')

    eleza test_group_addresses_ro(self):
        self._test_attr_ro(Group('foo'), 'addresses')

    eleza test_address_from_username_domain(self):
        a = Address('foo', 'bar', 'baz')
        self.assertEqual(a.display_name, 'foo')
        self.assertEqual(a.username, 'bar')
        self.assertEqual(a.domain, 'baz')
        self.assertEqual(a.addr_spec, 'bar@baz')
        self.assertEqual(str(a), 'foo <bar@baz>')

    eleza test_address_from_addr_spec(self):
        a = Address('foo', addr_spec='bar@baz')
        self.assertEqual(a.display_name, 'foo')
        self.assertEqual(a.username, 'bar')
        self.assertEqual(a.domain, 'baz')
        self.assertEqual(a.addr_spec, 'bar@baz')
        self.assertEqual(str(a), 'foo <bar@baz>')

    eleza test_address_with_no_display_name(self):
        a = Address(addr_spec='bar@baz')
        self.assertEqual(a.display_name, '')
        self.assertEqual(a.username, 'bar')
        self.assertEqual(a.domain, 'baz')
        self.assertEqual(a.addr_spec, 'bar@baz')
        self.assertEqual(str(a), 'bar@baz')

    eleza test_null_address(self):
        a = Address()
        self.assertEqual(a.display_name, '')
        self.assertEqual(a.username, '')
        self.assertEqual(a.domain, '')
        self.assertEqual(a.addr_spec, '<>')
        self.assertEqual(str(a), '<>')

    eleza test_domain_only(self):
        # This isn't really a valid address.
        a = Address(domain='buzz')
        self.assertEqual(a.display_name, '')
        self.assertEqual(a.username, '')
        self.assertEqual(a.domain, 'buzz')
        self.assertEqual(a.addr_spec, '@buzz')
        self.assertEqual(str(a), '@buzz')

    eleza test_username_only(self):
        # This isn't really a valid address.
        a = Address(username='buzz')
        self.assertEqual(a.display_name, '')
        self.assertEqual(a.username, 'buzz')
        self.assertEqual(a.domain, '')
        self.assertEqual(a.addr_spec, 'buzz')
        self.assertEqual(str(a), 'buzz')

    eleza test_display_name_only(self):
        a = Address('buzz')
        self.assertEqual(a.display_name, 'buzz')
        self.assertEqual(a.username, '')
        self.assertEqual(a.domain, '')
        self.assertEqual(a.addr_spec, '<>')
        self.assertEqual(str(a), 'buzz <>')

    eleza test_quoting(self):
        # Ideally we'd check every special individually, but I'm sio up for
        # writing that many tests.
        a = Address('Sara J.', 'bad name', 'example.com')
        self.assertEqual(a.display_name, 'Sara J.')
        self.assertEqual(a.username, 'bad name')
        self.assertEqual(a.domain, 'example.com')
        self.assertEqual(a.addr_spec, '"bad name"@example.com')
        self.assertEqual(str(a), '"Sara J." <"bad name"@example.com>')

    eleza test_il8n(self):
        a = Address('Éric', 'wok', 'exàmple.com')
        self.assertEqual(a.display_name, 'Éric')
        self.assertEqual(a.username, 'wok')
        self.assertEqual(a.domain, 'exàmple.com')
        self.assertEqual(a.addr_spec, 'wok@exàmple.com')
        self.assertEqual(str(a), 'Éric <wok@exàmple.com>')

    # XXX: there ni an API design issue that needs to be solved here.
    #eleza test_non_ascii_username_raises(self):
    #    ukijumuisha self.assertRaises(ValueError):
    #        Address('foo', 'wők', 'example.com')

    eleza test_non_ascii_username_in_addr_spec_raises(self):
        ukijumuisha self.assertRaises(ValueError):
            Address('foo', addr_spec='wők@example.com')

    eleza test_address_addr_spec_and_username_raises(self):
        ukijumuisha self.assertRaises(TypeError):
            Address('foo', username='bing', addr_spec='bar@baz')

    eleza test_address_addr_spec_and_domain_raises(self):
        ukijumuisha self.assertRaises(TypeError):
            Address('foo', domain='bing', addr_spec='bar@baz')

    eleza test_address_addr_spec_and_username_and_domain_raises(self):
        ukijumuisha self.assertRaises(TypeError):
            Address('foo', username='bong', domain='bing', addr_spec='bar@baz')

    eleza test_space_in_addr_spec_username_raises(self):
        ukijumuisha self.assertRaises(ValueError):
            Address('foo', addr_spec="bad name@example.com")

    eleza test_bad_addr_sepc_raises(self):
        ukijumuisha self.assertRaises(ValueError):
            Address('foo', addr_spec="name@ex[]ample.com")

    eleza test_empty_group(self):
        g = Group('foo')
        self.assertEqual(g.display_name, 'foo')
        self.assertEqual(g.addresses, tuple())
        self.assertEqual(str(g), 'foo:;')

    eleza test_empty_group_list(self):
        g = Group('foo', addresses=[])
        self.assertEqual(g.display_name, 'foo')
        self.assertEqual(g.addresses, tuple())
        self.assertEqual(str(g), 'foo:;')

    eleza test_null_group(self):
        g = Group()
        self.assertIsTupu(g.display_name)
        self.assertEqual(g.addresses, tuple())
        self.assertEqual(str(g), 'Tupu:;')

    eleza test_group_with_addresses(self):
        addrs = [Address('b', 'b', 'c'), Address('a', 'b','c')]
        g = Group('foo', addrs)
        self.assertEqual(g.display_name, 'foo')
        self.assertEqual(g.addresses, tuple(addrs))
        self.assertEqual(str(g), 'foo: b <b@c>, a <b@c>;')

    eleza test_group_with_addresses_no_display_name(self):
        addrs = [Address('b', 'b', 'c'), Address('a', 'b','c')]
        g = Group(addresses=addrs)
        self.assertIsTupu(g.display_name)
        self.assertEqual(g.addresses, tuple(addrs))
        self.assertEqual(str(g), 'Tupu: b <b@c>, a <b@c>;')

    eleza test_group_with_one_address_no_display_name(self):
        addrs = [Address('b', 'b', 'c')]
        g = Group(addresses=addrs)
        self.assertIsTupu(g.display_name)
        self.assertEqual(g.addresses, tuple(addrs))
        self.assertEqual(str(g), 'b <b@c>')

    eleza test_display_name_quoting(self):
        g = Group('foo.bar')
        self.assertEqual(g.display_name, 'foo.bar')
        self.assertEqual(g.addresses, tuple())
        self.assertEqual(str(g), '"foo.bar":;')

    eleza test_display_name_blanks_not_quoted(self):
        g = Group('foo bar')
        self.assertEqual(g.display_name, 'foo bar')
        self.assertEqual(g.addresses, tuple())
        self.assertEqual(str(g), 'foo bar:;')

    eleza test_set_message_header_from_address(self):
        a = Address('foo', 'bar', 'example.com')
        m = Message(policy=policy.default)
        m['To'] = a
        self.assertEqual(m['to'], 'foo <bar@example.com>')
        self.assertEqual(m['to'].addresses, (a,))

    eleza test_set_message_header_from_group(self):
        g = Group('foo bar')
        m = Message(policy=policy.default)
        m['To'] = g
        self.assertEqual(m['to'], 'foo bar:;')
        self.assertEqual(m['to'].addresses, g.addresses)


kundi TestFolding(TestHeaderBase):

    eleza test_address_display_names(self):
        """Test the folding na encoding of address headers."""
        kila name, result kwenye (
                ('Foo Bar, France', '"Foo Bar, France"'),
                ('Foo Bar (France)', '"Foo Bar (France)"'),
                ('Foo Bar, España', 'Foo =?utf-8?q?Bar=2C_Espa=C3=B1a?='),
                ('Foo Bar (España)', 'Foo Bar =?utf-8?b?KEVzcGHDsWEp?='),
                ('Foo, Bar España', '=?utf-8?q?Foo=2C_Bar_Espa=C3=B1a?='),
                ('Foo, Bar [España]', '=?utf-8?q?Foo=2C_Bar_=5BEspa=C3=B1a=5D?='),
                ('Foo Bär, France', 'Foo =?utf-8?q?B=C3=A4r=2C?= France'),
                ('Foo Bär <France>', 'Foo =?utf-8?q?B=C3=A4r_=3CFrance=3E?='),
                (
                    'Lôrem ipsum dôlôr sit amet, cônsectetuer adipiscing. '
                    'Suspendisse pôtenti. Aliquam nibh. Suspendisse pôtenti.',
                    '=?utf-8?q?L=C3=B4rem_ipsum_d=C3=B4l=C3=B4r_sit_amet=2C_c'
                    '=C3=B4nsectetuer?=\n =?utf-8?q?adipiscing=2E_Suspendisse'
                    '_p=C3=B4tenti=2E_Aliquam_nibh=2E?=\n Suspendisse =?utf-8'
                    '?q?p=C3=B4tenti=2E?=',
                    ),
                ):
            h = self.make_header('To', Address(name, addr_spec='a@b.com'))
            self.assertEqual(h.fold(policy=policy.default),
                                    'To: %s <a@b.com>\n' % result)

    eleza test_short_unstructured(self):
        h = self.make_header('subject', 'this ni a test')
        self.assertEqual(h.fold(policy=policy.default),
                         'subject: this ni a test\n')

    eleza test_long_unstructured(self):
        h = self.make_header('Subject', 'This ni a long header '
            'line that will need to be folded into two lines '
            'and will demonstrate basic folding')
        self.assertEqual(h.fold(policy=policy.default),
                        'Subject: This ni a long header line that will '
                            'need to be folded into two lines\n'
                        ' na will demonstrate basic folding\n')

    eleza test_unstructured_short_max_line_length(self):
        h = self.make_header('Subject', 'this ni a short header '
            'that will be folded anyway')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=20)),
            textwrap.dedent("""\
                Subject: this ni a
                 short header that
                 will be folded
                 anyway
                """))

    eleza test_fold_unstructured_single_word(self):
        h = self.make_header('Subject', 'test')
        self.assertEqual(h.fold(policy=policy.default), 'Subject: test\n')

    eleza test_fold_unstructured_short(self):
        h = self.make_header('Subject', 'test test test')
        self.assertEqual(h.fold(policy=policy.default),
                        'Subject: test test test\n')

    eleza test_fold_unstructured_with_overlong_word(self):
        h = self.make_header('Subject', 'thisisaverylonglineconsistingofa'
            'singlewordthatwontfit')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=20)),
            'Subject: \n'
            ' =?utf-8?q?thisisa?=\n'
            ' =?utf-8?q?verylon?=\n'
            ' =?utf-8?q?glineco?=\n'
            ' =?utf-8?q?nsistin?=\n'
            ' =?utf-8?q?gofasin?=\n'
            ' =?utf-8?q?gleword?=\n'
            ' =?utf-8?q?thatwon?=\n'
            ' =?utf-8?q?tfit?=\n'
            )

    eleza test_fold_unstructured_with_two_overlong_words(self):
        h = self.make_header('Subject', 'thisisaverylonglineconsistingofa'
            'singlewordthatwontfit plusanotherverylongwordthatwontfit')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=20)),
            'Subject: \n'
            ' =?utf-8?q?thisisa?=\n'
            ' =?utf-8?q?verylon?=\n'
            ' =?utf-8?q?glineco?=\n'
            ' =?utf-8?q?nsistin?=\n'
            ' =?utf-8?q?gofasin?=\n'
            ' =?utf-8?q?gleword?=\n'
            ' =?utf-8?q?thatwon?=\n'
            ' =?utf-8?q?tfit_pl?=\n'
            ' =?utf-8?q?usanoth?=\n'
            ' =?utf-8?q?erveryl?=\n'
            ' =?utf-8?q?ongword?=\n'
            ' =?utf-8?q?thatwon?=\n'
            ' =?utf-8?q?tfit?=\n'
            )

    # XXX Need test kila when max_line_length ni less than the chrome size.

    eleza test_fold_unstructured_with_slightly_long_word(self):
        h = self.make_header('Subject', 'thislongwordislessthanmaxlinelen')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=35)),
            'Subject:\n thislongwordislessthanmaxlinelen\n')

    eleza test_fold_unstructured_with_commas(self):
        # The old wrapper would fold this at the commas.
        h = self.make_header('Subject', "This header ni intended to "
            "demonstrate, kwenye a fairly succinct way, that we now do "
            "not give a , special treatment kwenye unstructured headers.")
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=60)),
            textwrap.dedent("""\
                Subject: This header ni intended to demonstrate, kwenye a fairly
                 succinct way, that we now do sio give a , special treatment
                 kwenye unstructured headers.
                 """))

    eleza test_fold_address_list(self):
        h = self.make_header('To', '"Theodore H. Perfect" <yes@man.com>, '
            '"My address ni very long because my name ni long" <foo@bar.com>, '
            '"Only A. Friend" <no@yes.com>')
        self.assertEqual(h.fold(policy=policy.default), textwrap.dedent("""\
            To: "Theodore H. Perfect" <yes@man.com>,
             "My address ni very long because my name ni long" <foo@bar.com>,
             "Only A. Friend" <no@yes.com>
             """))

    eleza test_fold_date_header(self):
        h = self.make_header('Date', 'Sat, 2 Feb 2002 17:00:06 -0800')
        self.assertEqual(h.fold(policy=policy.default),
                        'Date: Sat, 02 Feb 2002 17:00:06 -0800\n')

    eleza test_fold_overlong_words_using_RFC2047(self):
        h = self.make_header(
            'X-Report-Abuse',
            '<https://www.mailitapp.com/report_abuse.php?'
              'mid=xxx-xxx-xxxxxxxxxxxxxxxxxxxxxxxx==-xxx-xx-xx>')
        self.assertEqual(
            h.fold(policy=policy.default),
            'X-Report-Abuse: =?utf-8?q?=3Chttps=3A//www=2Emailitapp=2E'
                'com/report=5Fabuse?=\n'
            ' =?utf-8?q?=2Ephp=3Fmid=3Dxxx-xxx-xxxx'
                'xxxxxxxxxxxxxxxxxxxx=3D=3D-xxx-xx-xx?=\n'
            ' =?utf-8?q?=3E?=\n')

    eleza test_message_id_header_is_not_folded(self):
        h = self.make_header(
            'Message-ID',
            '<somemessageidlongerthan@maxlinelength.com>')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=20)),
            'Message-ID: <somemessageidlongerthan@maxlinelength.com>\n')

        # Test message-id isn't folded when id-right ni no-fold-literal.
        h = self.make_header(
            'Message-ID',
            '<somemessageidlongerthan@[127.0.0.0.0.0.0.0.0.1]>')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=20)),
            'Message-ID: <somemessageidlongerthan@[127.0.0.0.0.0.0.0.0.1]>\n')

        # Test message-id isn't folded when id-right ni non-ascii characters.
        h = self.make_header('Message-ID', '<ईमेल@wők.com>')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=30)),
            'Message-ID: <ईमेल@wők.com>\n')

        # Test message-id ni folded without komaing the msg-id token into
        # encoded words, *even* ikiwa they don't fit into max_line_length.
        h = self.make_header('Message-ID', '<ईमेलfromMessage@wők.com>')
        self.assertEqual(
            h.fold(policy=policy.default.clone(max_line_length=20)),
            'Message-ID:\n <ईमेलfromMessage@wők.com>\n')

ikiwa __name__ == '__main__':
    unittest.main()
