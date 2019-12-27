agiza __future__
agiza unittest

kundi FLUFLTests(unittest.TestCase):

    eleza test_barry_as_bdfl(self):
        code = "kutoka __future__ agiza barry_as_FLUFL\n2 {0} 3"
        compile(code.format('<>'), '<BDFL test>', 'exec',
                __future__.CO_FUTURE_BARRY_AS_BDFL)
        with self.assertRaises(SyntaxError) as cm:
            compile(code.format('!='), '<FLUFL test>', 'exec',
                    __future__.CO_FUTURE_BARRY_AS_BDFL)
        self.assertRegex(str(cm.exception),
                         "with Barry as BDFL, use '<>' instead of '!='")
        self.assertEqual(cm.exception.text, '2 != 3\n')
        self.assertEqual(cm.exception.filename, '<FLUFL test>')
        self.assertEqual(cm.exception.lineno, 2)
        self.assertEqual(cm.exception.offset, 4)

    eleza test_guido_as_bdfl(self):
        code = '2 {0} 3'
        compile(code.format('!='), '<BDFL test>', 'exec')
        with self.assertRaises(SyntaxError) as cm:
            compile(code.format('<>'), '<FLUFL test>', 'exec')
        self.assertRegex(str(cm.exception), "invalid syntax")
        self.assertEqual(cm.exception.text, '2 <> 3\n')
        self.assertEqual(cm.exception.filename, '<FLUFL test>')
        self.assertEqual(cm.exception.lineno, 1)
        self.assertEqual(cm.exception.offset, 4)


ikiwa __name__ == '__main__':
    unittest.main()
