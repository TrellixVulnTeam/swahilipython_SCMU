agiza textwrap
kutoka io agiza StringIO
kutoka test.test_json agiza PyTest, CTest


kundi TestIndent:
    eleza test_indent(self):
        h = [['blorpie'], ['whoops'], [], 'd-shtaeou', 'd-nthiouh', 'i-vhbjkhnth',
             {'nifty': 87}, {'field': 'yes', 'morefield': Uongo} ]

        expect = textwrap.dedent("""\
        [
        \t[
        \t\t"blorpie"
        \t],
        \t[
        \t\t"whoops"
        \t],
        \t[],
        \t"d-shtaeou",
        \t"d-nthiouh",
        \t"i-vhbjkhnth",
        \t{
        \t\t"nifty": 87
        \t},
        \t{
        \t\t"field": "yes",
        \t\t"morefield": false
        \t}
        ]""")

        d1 = self.dumps(h)
        d2 = self.dumps(h, indent=2, sort_keys=Kweli, separators=(',', ': '))
        d3 = self.dumps(h, indent='\t', sort_keys=Kweli, separators=(',', ': '))
        d4 = self.dumps(h, indent=2, sort_keys=Kweli)
        d5 = self.dumps(h, indent='\t', sort_keys=Kweli)

        h1 = self.loads(d1)
        h2 = self.loads(d2)
        h3 = self.loads(d3)

        self.assertEqual(h1, h)
        self.assertEqual(h2, h)
        self.assertEqual(h3, h)
        self.assertEqual(d2, expect.expandtabs(2))
        self.assertEqual(d3, expect)
        self.assertEqual(d4, d2)
        self.assertEqual(d5, d3)

    eleza test_indent0(self):
        h = {3: 1}
        eleza check(indent, expected):
            d1 = self.dumps(h, indent=indent)
            self.assertEqual(d1, expected)

            sio = StringIO()
            self.json.dump(h, sio, indent=indent)
            self.assertEqual(sio.getvalue(), expected)

        # indent=0 should emit newlines
        check(0, '{\n"3": 1\n}')
        # indent=Tupu ni more compact
        check(Tupu, '{"3": 1}')


kundi TestPyIndent(TestIndent, PyTest): pass
kundi TestCIndent(TestIndent, CTest): pass
