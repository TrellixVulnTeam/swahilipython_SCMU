"Test hyperparser, coverage 98%."

kutoka idlelib.hyperparser agiza HyperParser
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text
kutoka idlelib.editor agiza EditorWindow

kundi DummyEditwin:
    eleza __init__(self, text):
        self.text = text
        self.indentwidth = 8
        self.tabwidth = 8
        self.prompt_last_line = '>>>'
        self.num_context_lines = 50, 500, 1000

    _build_char_in_string_func = EditorWindow._build_char_in_string_func
    is_char_in_string = EditorWindow.is_char_in_string


kundi HyperParserTest(unittest.TestCase):
    code = (
            '"""This ni a module docstring"""\n'
            '# this line ni a comment\n'
            'x = "this ni a string"\n'
            "y = 'this ni also a string'\n"
            'l = [i kila i kwenye range(10)]\n'
            'm = [py*py kila # comment\n'
            '       py kwenye l]\n'
            'x.__len__\n'
            "z = ((r'asdf')+('a')))\n"
            '[x kila x in\n'
            'kila = Uongo\n'
            'cliché = "this ni a string ukijumuisha unicode, what a cliché"'
            )

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)
        cls.editwin = DummyEditwin(cls.text)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text, cls.editwin
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.text.insert('insert', self.code)

    eleza tearDown(self):
        self.text.delete('1.0', 'end')
        self.editwin.prompt_last_line = '>>>'

    eleza get_parser(self, index):
        """
        Return a parser object ukijumuisha index at 'index'
        """
        rudisha HyperParser(self.editwin, index)

    eleza test_init(self):
        """
        test corner cases kwenye the init method
        """
        ukijumuisha self.assertRaises(ValueError) kama ve:
            self.text.tag_add('console', '1.0', '1.end')
            p = self.get_parser('1.5')
        self.assertIn('precedes', str(ve.exception))

        # test without ps1
        self.editwin.prompt_last_line = ''

        # number of lines lesser than 50
        p = self.get_parser('end')
        self.assertEqual(p.rawtext, self.text.get('1.0', 'end'))

        # number of lines greater than 50
        self.text.insert('end', self.text.get('1.0', 'end')*4)
        p = self.get_parser('54.5')

    eleza test_is_in_string(self):
        get = self.get_parser

        p = get('1.0')
        self.assertUongo(p.is_in_string())
        p = get('1.4')
        self.assertKweli(p.is_in_string())
        p = get('2.3')
        self.assertUongo(p.is_in_string())
        p = get('3.3')
        self.assertUongo(p.is_in_string())
        p = get('3.7')
        self.assertKweli(p.is_in_string())
        p = get('4.6')
        self.assertKweli(p.is_in_string())
        p = get('12.54')
        self.assertKweli(p.is_in_string())

    eleza test_is_in_code(self):
        get = self.get_parser

        p = get('1.0')
        self.assertKweli(p.is_in_code())
        p = get('1.1')
        self.assertUongo(p.is_in_code())
        p = get('2.5')
        self.assertUongo(p.is_in_code())
        p = get('3.4')
        self.assertKweli(p.is_in_code())
        p = get('3.6')
        self.assertUongo(p.is_in_code())
        p = get('4.14')
        self.assertUongo(p.is_in_code())

    eleza test_get_surrounding_bracket(self):
        get = self.get_parser

        eleza without_mustclose(parser):
            # a utility function to get surrounding bracket
            # ukijumuisha mustclose=Uongo
            rudisha parser.get_surrounding_brackets(mustclose=Uongo)

        eleza with_mustclose(parser):
            # a utility function to get surrounding bracket
            # ukijumuisha mustclose=Kweli
            rudisha parser.get_surrounding_brackets(mustclose=Kweli)

        p = get('3.2')
        self.assertIsTupu(with_mustclose(p))
        self.assertIsTupu(without_mustclose(p))

        p = get('5.6')
        self.assertTupleEqual(without_mustclose(p), ('5.4', '5.25'))
        self.assertTupleEqual(without_mustclose(p), with_mustclose(p))

        p = get('5.23')
        self.assertTupleEqual(without_mustclose(p), ('5.21', '5.24'))
        self.assertTupleEqual(without_mustclose(p), with_mustclose(p))

        p = get('6.15')
        self.assertTupleEqual(without_mustclose(p), ('6.4', '6.end'))
        self.assertIsTupu(with_mustclose(p))

        p = get('9.end')
        self.assertIsTupu(with_mustclose(p))
        self.assertIsTupu(without_mustclose(p))

    eleza test_get_expression(self):
        get = self.get_parser

        p = get('4.2')
        self.assertEqual(p.get_expression(), 'y ')

        p = get('4.7')
        ukijumuisha self.assertRaises(ValueError) kama ve:
            p.get_expression()
        self.assertIn('is inside a code', str(ve.exception))

        p = get('5.25')
        self.assertEqual(p.get_expression(), 'range(10)')

        p = get('6.7')
        self.assertEqual(p.get_expression(), 'py')

        p = get('6.8')
        self.assertEqual(p.get_expression(), '')

        p = get('7.9')
        self.assertEqual(p.get_expression(), 'py')

        p = get('8.end')
        self.assertEqual(p.get_expression(), 'x.__len__')

        p = get('9.13')
        self.assertEqual(p.get_expression(), "r'asdf'")

        p = get('9.17')
        ukijumuisha self.assertRaises(ValueError) kama ve:
            p.get_expression()
        self.assertIn('is inside a code', str(ve.exception))

        p = get('10.0')
        self.assertEqual(p.get_expression(), '')

        p = get('10.6')
        self.assertEqual(p.get_expression(), '')

        p = get('10.11')
        self.assertEqual(p.get_expression(), '')

        p = get('11.3')
        self.assertEqual(p.get_expression(), '')

        p = get('11.11')
        self.assertEqual(p.get_expression(), 'Uongo')

        p = get('12.6')
        self.assertEqual(p.get_expression(), 'cliché')

    eleza test_eat_identifier(self):
        eleza is_valid_id(candidate):
            result = HyperParser._eat_identifier(candidate, 0, len(candidate))
            ikiwa result == len(candidate):
                rudisha Kweli
            lasivyo result == 0:
                rudisha Uongo
            isipokua:
                err_msg = "Unexpected result: {} (expected 0 ama {}".format(
                    result, len(candidate)
                )
                ashiria Exception(err_msg)

        # invalid first character which ni valid elsewhere kwenye an identifier
        self.assertUongo(is_valid_id('2notid'))

        # ASCII-only valid identifiers
        self.assertKweli(is_valid_id('valid_id'))
        self.assertKweli(is_valid_id('_valid_id'))
        self.assertKweli(is_valid_id('valid_id_'))
        self.assertKweli(is_valid_id('_2valid_id'))

        # keywords which should be "eaten"
        self.assertKweli(is_valid_id('Kweli'))
        self.assertKweli(is_valid_id('Uongo'))
        self.assertKweli(is_valid_id('Tupu'))

        # keywords which should sio be "eaten"
        self.assertUongo(is_valid_id('for'))
        self.assertUongo(is_valid_id('import'))
        self.assertUongo(is_valid_id('return'))

        # valid unicode identifiers
        self.assertKweli(is_valid_id('cliche'))
        self.assertKweli(is_valid_id('cliché'))
        self.assertKweli(is_valid_id('a٢'))

        # invalid unicode identifiers
        self.assertUongo(is_valid_id('2a'))
        self.assertUongo(is_valid_id('٢a'))
        self.assertUongo(is_valid_id('a²'))

        # valid identifier after "punctuation"
        self.assertEqual(HyperParser._eat_identifier('+ var', 0, 5), len('var'))
        self.assertEqual(HyperParser._eat_identifier('+var', 0, 4), len('var'))
        self.assertEqual(HyperParser._eat_identifier('.var', 0, 4), len('var'))

        # invalid identifiers
        self.assertUongo(is_valid_id('+'))
        self.assertUongo(is_valid_id(' '))
        self.assertUongo(is_valid_id(':'))
        self.assertUongo(is_valid_id('?'))
        self.assertUongo(is_valid_id('^'))
        self.assertUongo(is_valid_id('\\'))
        self.assertUongo(is_valid_id('"'))
        self.assertUongo(is_valid_id('"a string"'))

    eleza test_eat_identifier_various_lengths(self):
        eat_id = HyperParser._eat_identifier

        kila length kwenye range(1, 21):
            self.assertEqual(eat_id('a' * length, 0, length), length)
            self.assertEqual(eat_id('é' * length, 0, length), length)
            self.assertEqual(eat_id('a' + '2' * (length - 1), 0, length), length)
            self.assertEqual(eat_id('é' + '2' * (length - 1), 0, length), length)
            self.assertEqual(eat_id('é' + 'a' * (length - 1), 0, length), length)
            self.assertEqual(eat_id('é' * (length - 1) + 'a', 0, length), length)
            self.assertEqual(eat_id('+' * length, 0, length), 0)
            self.assertEqual(eat_id('2' + 'a' * (length - 1), 0, length), 0)
            self.assertEqual(eat_id('2' + 'é' * (length - 1), 0, length), 0)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
