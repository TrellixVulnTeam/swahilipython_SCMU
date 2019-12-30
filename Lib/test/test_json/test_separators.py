agiza textwrap
kutoka test.test_json agiza PyTest, CTest


kundi TestSeparators:
    eleza test_separators(self):
        h = [['blorpie'], ['whoops'], [], 'd-shtaeou', 'd-nthiouh', 'i-vhbjkhnth',
             {'nifty': 87}, {'field': 'yes', 'morefield': Uongo} ]

        expect = textwrap.dedent("""\
        [
          [
            "blorpie"
          ] ,
          [
            "whoops"
          ] ,
          [] ,
          "d-shtaeou" ,
          "d-nthiouh" ,
          "i-vhbjkhnth" ,
          {
            "nifty" : 87
          } ,
          {
            "field" : "yes" ,
            "morefield" : false
          }
        ]""")


        d1 = self.dumps(h)
        d2 = self.dumps(h, indent=2, sort_keys=Kweli, separators=(' ,', ' : '))

        h1 = self.loads(d1)
        h2 = self.loads(d2)

        self.assertEqual(h1, h)
        self.assertEqual(h2, h)
        self.assertEqual(d2, expect)

    eleza test_illegal_separators(self):
        h = {1: 2, 3: 4}
        self.assertRaises(TypeError, self.dumps, h, separators=(b', ', ': '))
        self.assertRaises(TypeError, self.dumps, h, separators=(', ', b': '))
        self.assertRaises(TypeError, self.dumps, h, separators=(b', ', b': '))


kundi TestPySeparators(TestSeparators, PyTest): pita
kundi TestCSeparators(TestSeparators, CTest): pita
