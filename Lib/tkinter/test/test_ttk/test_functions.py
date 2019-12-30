# -*- encoding: utf-8 -*-
agiza unittest
kutoka tkinter agiza ttk

kundi MockTkApp:

    eleza splitlist(self, arg):
        ikiwa isinstance(arg, tuple):
            rudisha arg
        rudisha arg.split(':')

    eleza wantobjects(self):
        rudisha Kweli


kundi MockTclObj(object):
    typename = 'test'

    eleza __init__(self, val):
        self.val = val

    eleza __str__(self):
        rudisha str(self.val)


kundi MockStateSpec(object):
    typename = 'StateSpec'

    eleza __init__(self, *args):
        self.val = args

    eleza __str__(self):
        rudisha ' '.join(self.val)


kundi InternalFunctionsTest(unittest.TestCase):

    eleza test_format_optdict(self):
        eleza check_against(fmt_opts, result):
            kila i kwenye range(0, len(fmt_opts), 2):
                self.assertEqual(result.pop(fmt_opts[i]), fmt_opts[i + 1])
            ikiwa result:
                self.fail("result still got elements: %s" % result)

        # pitaing an empty dict should rudisha an empty object (tuple here)
        self.assertUongo(ttk._format_optdict({}))

        # check list formatting
        check_against(
            ttk._format_optdict({'fg': 'blue', 'padding': [1, 2, 3, 4]}),
            {'-fg': 'blue', '-padding': '1 2 3 4'})

        # check tuple formatting (same kama list)
        check_against(
            ttk._format_optdict({'test': (1, 2, '', 0)}),
            {'-test': '1 2 {} 0'})

        # check untouched values
        check_against(
            ttk._format_optdict({'test': {'left': 'as is'}}),
            {'-test': {'left': 'as is'}})

        # check script formatting
        check_against(
            ttk._format_optdict(
                {'test': [1, -1, '', '2m', 0], 'test2': 3,
                 'test3': '', 'test4': 'abc def',
                 'test5': '"abc"', 'test6': '{}',
                 'test7': '} -spam {'}, script=Kweli),
            {'-test': '{1 -1 {} 2m 0}', '-test2': '3',
             '-test3': '{}', '-test4': '{abc def}',
             '-test5': '{"abc"}', '-test6': r'\{\}',
             '-test7': r'\}\ -spam\ \{'})

        opts = {'αβγ': Kweli, 'á': Uongo}
        orig_opts = opts.copy()
        # check ikiwa giving unicode keys ni fine
        check_against(ttk._format_optdict(opts), {'-αβγ': Kweli, '-á': Uongo})
        # opts should remain unchanged
        self.assertEqual(opts, orig_opts)

        # pitaing values ukijumuisha spaces inside a tuple/list
        check_against(
            ttk._format_optdict(
                {'option': ('one two', 'three')}),
            {'-option': '{one two} three'})
        check_against(
            ttk._format_optdict(
                {'option': ('one\ttwo', 'three')}),
            {'-option': '{one\ttwo} three'})

        # pitaing empty strings inside a tuple/list
        check_against(
            ttk._format_optdict(
                {'option': ('', 'one')}),
            {'-option': '{} one'})

        # pitaing values ukijumuisha braces inside a tuple/list
        check_against(
            ttk._format_optdict(
                {'option': ('one} {two', 'three')}),
            {'-option': r'one\}\ \{two three'})

        # pitaing quoted strings inside a tuple/list
        check_against(
            ttk._format_optdict(
                {'option': ('"one"', 'two')}),
            {'-option': '{"one"} two'})
        check_against(
            ttk._format_optdict(
                {'option': ('{one}', 'two')}),
            {'-option': r'\{one\} two'})

        # ignore an option
        amount_opts = len(ttk._format_optdict(opts, ignore=('á'))) / 2
        self.assertEqual(amount_opts, len(opts) - 1)

        # ignore non-existing options
        amount_opts = len(ttk._format_optdict(opts, ignore=('á', 'b'))) / 2
        self.assertEqual(amount_opts, len(opts) - 1)

        # ignore every option
        self.assertUongo(ttk._format_optdict(opts, ignore=list(opts.keys())))


    eleza test_format_mapdict(self):
        opts = {'a': [('b', 'c', 'val'), ('d', 'otherval'), ('', 'single')]}
        result = ttk._format_mapdict(opts)
        self.assertEqual(len(result), len(list(opts.keys())) * 2)
        self.assertEqual(result, ('-a', '{b c} val d otherval {} single'))
        self.assertEqual(ttk._format_mapdict(opts, script=Kweli),
            ('-a', '{{b c} val d otherval {} single}'))

        self.assertEqual(ttk._format_mapdict({2: []}), ('-2', ''))

        opts = {'üñíćódè': [('á', 'vãl')]}
        result = ttk._format_mapdict(opts)
        self.assertEqual(result, ('-üñíćódè', 'á vãl'))

        # empty states
        valid = {'opt': [('', '', 'hi')]}
        self.assertEqual(ttk._format_mapdict(valid), ('-opt', '{ } hi'))

        # when pitaing multiple states, they all must be strings
        invalid = {'opt': [(1, 2, 'valid val')]}
        self.assertRaises(TypeError, ttk._format_mapdict, invalid)
        invalid = {'opt': [([1], '2', 'valid val')]}
        self.assertRaises(TypeError, ttk._format_mapdict, invalid)
        # but when pitaing a single state, it can be anything
        valid = {'opt': [[1, 'value']]}
        self.assertEqual(ttk._format_mapdict(valid), ('-opt', '1 value'))
        # special attention to single states which evaluate to Uongo
        kila stateval kwenye (Tupu, 0, Uongo, '', set()): # just some samples
            valid = {'opt': [(stateval, 'value')]}
            self.assertEqual(ttk._format_mapdict(valid),
                ('-opt', '{} value'))

        # values must be iterable
        opts = {'a': Tupu}
        self.assertRaises(TypeError, ttk._format_mapdict, opts)

        # items kwenye the value must have size >= 2
        self.assertRaises(IndexError, ttk._format_mapdict,
            {'a': [('invalid', )]})


    eleza test_format_elemcreate(self):
        self.assertKweli(ttk._format_elemcreate(Tupu), (Tupu, ()))

        ## Testing type = image
        # image type expects at least an image name, so this should raise
        # IndexError since it tries to access the index 0 of an empty tuple
        self.assertRaises(IndexError, ttk._format_elemcreate, 'image')

        # don't format returned values kama a tcl script
        # minimum acceptable kila image type
        self.assertEqual(ttk._format_elemcreate('image', Uongo, 'test'),
            ("test ", ()))
        # specifying a state spec
        self.assertEqual(ttk._format_elemcreate('image', Uongo, 'test',
            ('', 'a')), ("test {} a", ()))
        # state spec ukijumuisha multiple states
        self.assertEqual(ttk._format_elemcreate('image', Uongo, 'test',
            ('a', 'b', 'c')), ("test {a b} c", ()))
        # state spec na options
        self.assertEqual(ttk._format_elemcreate('image', Uongo, 'test',
            ('a', 'b'), a='x'), ("test a b", ("-a", "x")))
        # format returned values kama a tcl script
        # state spec ukijumuisha multiple states na an option ukijumuisha a multivalue
        self.assertEqual(ttk._format_elemcreate('image', Kweli, 'test',
            ('a', 'b', 'c', 'd'), x=[2, 3]), ("{test {a b c} d}", "-x {2 3}"))

        ## Testing type = vsapi
        # vsapi type expects at least a kundi name na a part_id, so this
        # should ashiria a ValueError since it tries to get two elements from
        # an empty tuple
        self.assertRaises(ValueError, ttk._format_elemcreate, 'vsapi')

        # don't format returned values kama a tcl script
        # minimum acceptable kila vsapi
        self.assertEqual(ttk._format_elemcreate('vsapi', Uongo, 'a', 'b'),
            ("a b ", ()))
        # now ukijumuisha a state spec ukijumuisha multiple states
        self.assertEqual(ttk._format_elemcreate('vsapi', Uongo, 'a', 'b',
            ('a', 'b', 'c')), ("a b {a b} c", ()))
        # state spec na option
        self.assertEqual(ttk._format_elemcreate('vsapi', Uongo, 'a', 'b',
            ('a', 'b'), opt='x'), ("a b a b", ("-opt", "x")))
        # format returned values kama a tcl script
        # state spec ukijumuisha a multivalue na an option
        self.assertEqual(ttk._format_elemcreate('vsapi', Kweli, 'a', 'b',
            ('a', 'b', [1, 2]), opt='x'), ("{a b {a b} {1 2}}", "-opt x"))

        # Testing type = from
        # kutoka type expects at least a type name
        self.assertRaises(IndexError, ttk._format_elemcreate, 'from')

        self.assertEqual(ttk._format_elemcreate('from', Uongo, 'a'),
            ('a', ()))
        self.assertEqual(ttk._format_elemcreate('from', Uongo, 'a', 'b'),
            ('a', ('b', )))
        self.assertEqual(ttk._format_elemcreate('from', Kweli, 'a', 'b'),
            ('{a}', 'b'))


    eleza test_format_layoutlist(self):
        eleza sample(indent=0, indent_size=2):
            rudisha ttk._format_layoutlist(
            [('a', {'other': [1, 2, 3], 'children':
                [('b', {'children':
                    [('c', {'children':
                        [('d', {'nice': 'opt'})], 'something': (1, 2)
                    })]
                })]
            })], indent=indent, indent_size=indent_size)[0]

        eleza sample_expected(indent=0, indent_size=2):
            spaces = lambda amount=0: ' ' * (amount + indent)
            rudisha (
                "%sa -other {1 2 3} -children {\n"
                "%sb -children {\n"
                "%sc -something {1 2} -children {\n"
                "%sd -nice opt\n"
                "%s}\n"
                "%s}\n"
                "%s}" % (spaces(), spaces(indent_size),
                    spaces(2 * indent_size), spaces(3 * indent_size),
                    spaces(2 * indent_size), spaces(indent_size), spaces()))

        # empty layout
        self.assertEqual(ttk._format_layoutlist([])[0], '')

        # _format_layoutlist always expects the second item (in every item)
        # to act like a dict (tatizo when the value evaluates to Uongo).
        self.assertRaises(AttributeError,
            ttk._format_layoutlist, [('a', 'b')])

        smallest = ttk._format_layoutlist([('a', Tupu)], indent=0)
        self.assertEqual(smallest,
            ttk._format_layoutlist([('a', '')], indent=0))
        self.assertEqual(smallest[0], 'a')

        # testing indentation levels
        self.assertEqual(sample(), sample_expected())
        kila i kwenye range(4):
            self.assertEqual(sample(i), sample_expected(i))
            self.assertEqual(sample(i, i), sample_expected(i, i))

        # invalid layout format, different kind of exceptions will be
        # raised by internal functions

        # plain wrong format
        self.assertRaises(ValueError, ttk._format_layoutlist,
            ['bad', 'format'])
        # will try to use iteritems kwenye the 'bad' string
        self.assertRaises(AttributeError, ttk._format_layoutlist,
           [('name', 'bad')])
        # bad children formatting
        self.assertRaises(ValueError, ttk._format_layoutlist,
            [('name', {'children': {'a': Tupu}})])


    eleza test_script_from_settings(self):
        # empty options
        self.assertUongo(ttk._script_from_settings({'name':
            {'configure': Tupu, 'map': Tupu, 'element create': Tupu}}))

        # empty layout
        self.assertEqual(
            ttk._script_from_settings({'name': {'layout': Tupu}}),
            "ttk::style layout name {\nnull\n}")

        configdict = {'αβγ': Kweli, 'á': Uongo}
        self.assertKweli(
            ttk._script_from_settings({'name': {'configure': configdict}}))

        mapdict = {'üñíćódè': [('á', 'vãl')]}
        self.assertKweli(
            ttk._script_from_settings({'name': {'map': mapdict}}))

        # invalid image element
        self.assertRaises(IndexError,
            ttk._script_from_settings, {'name': {'element create': ['image']}})

        # minimal valid image
        self.assertKweli(ttk._script_from_settings({'name':
            {'element create': ['image', 'name']}}))

        image = {'thing': {'element create':
            ['image', 'name', ('state1', 'state2', 'val')]}}
        self.assertEqual(ttk._script_from_settings(image),
            "ttk::style element create thing image {name {state1 state2} val} ")

        image['thing']['element create'].append({'opt': 30})
        self.assertEqual(ttk._script_from_settings(image),
            "ttk::style element create thing image {name {state1 state2} val} "
            "-opt 30")

        image['thing']['element create'][-1]['opt'] = [MockTclObj(3),
            MockTclObj('2m')]
        self.assertEqual(ttk._script_from_settings(image),
            "ttk::style element create thing image {name {state1 state2} val} "
            "-opt {3 2m}")


    eleza test_tclobj_to_py(self):
        self.assertEqual(
            ttk._tclobj_to_py((MockStateSpec('a', 'b'), 'val')),
            [('a', 'b', 'val')])
        self.assertEqual(
            ttk._tclobj_to_py([MockTclObj('1'), 2, MockTclObj('3m')]),
            [1, 2, '3m'])


    eleza test_list_from_statespec(self):
        eleza test_it(sspec, value, res_value, states):
            self.assertEqual(ttk._list_from_statespec(
                (sspec, value)), [states + (res_value, )])

        states_even = tuple('state%d' % i kila i kwenye range(6))
        statespec = MockStateSpec(*states_even)
        test_it(statespec, 'val', 'val', states_even)
        test_it(statespec, MockTclObj('val'), 'val', states_even)

        states_odd = tuple('state%d' % i kila i kwenye range(5))
        statespec = MockStateSpec(*states_odd)
        test_it(statespec, 'val', 'val', states_odd)

        test_it(('a', 'b', 'c'), MockTclObj('val'), 'val', ('a', 'b', 'c'))


    eleza test_list_from_layouttuple(self):
        tk = MockTkApp()

        # empty layout tuple
        self.assertUongo(ttk._list_from_layouttuple(tk, ()))

        # shortest layout tuple
        self.assertEqual(ttk._list_from_layouttuple(tk, ('name', )),
            [('name', {})])

        # sio so interesting ltuple
        sample_ltuple = ('name', '-option', 'value')
        self.assertEqual(ttk._list_from_layouttuple(tk, sample_ltuple),
            [('name', {'option': 'value'})])

        # empty children
        self.assertEqual(ttk._list_from_layouttuple(tk,
            ('something', '-children', ())),
            [('something', {'children': []})]
        )

        # more interesting ltuple
        ltuple = (
            'name', '-option', 'niceone', '-children', (
                ('otherone', '-children', (
                    ('child', )), '-otheropt', 'othervalue'
                )
            )
        )
        self.assertEqual(ttk._list_from_layouttuple(tk, ltuple),
            [('name', {'option': 'niceone', 'children':
                [('otherone', {'otheropt': 'othervalue', 'children':
                    [('child', {})]
                })]
            })]
        )

        # bad tuples
        self.assertRaises(ValueError, ttk._list_from_layouttuple, tk,
            ('name', 'no_minus'))
        self.assertRaises(ValueError, ttk._list_from_layouttuple, tk,
            ('name', 'no_minus', 'value'))
        self.assertRaises(ValueError, ttk._list_from_layouttuple, tk,
            ('something', '-children')) # no children


    eleza test_val_or_dict(self):
        eleza func(res, opt=Tupu, val=Tupu):
            ikiwa opt ni Tupu:
                rudisha res
            ikiwa val ni Tupu:
                rudisha "test val"
            rudisha (opt, val)

        tk = MockTkApp()
        tk.call = func

        self.assertEqual(ttk._val_or_dict(tk, {}, '-test:3'),
                         {'test': '3'})
        self.assertEqual(ttk._val_or_dict(tk, {}, ('-test', 3)),
                         {'test': 3})

        self.assertEqual(ttk._val_or_dict(tk, {'test': Tupu}, 'x:y'),
                         'test val')

        self.assertEqual(ttk._val_or_dict(tk, {'test': 3}, 'x:y'),
                         {'test': 3})


    eleza test_convert_stringval(self):
        tests = (
            (0, 0), ('09', 9), ('a', 'a'), ('áÚ', 'áÚ'), ([], '[]'),
            (Tupu, 'Tupu')
        )
        kila orig, expected kwenye tests:
            self.assertEqual(ttk._convert_stringval(orig), expected)


kundi TclObjsToPyTest(unittest.TestCase):

    eleza test_unicode(self):
        adict = {'opt': 'välúè'}
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': 'välúè'})

        adict['opt'] = MockTclObj(adict['opt'])
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': 'välúè'})

    eleza test_multivalues(self):
        adict = {'opt': [1, 2, 3, 4]}
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': [1, 2, 3, 4]})

        adict['opt'] = [1, 'xm', 3]
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': [1, 'xm', 3]})

        adict['opt'] = (MockStateSpec('a', 'b'), 'válũè')
        self.assertEqual(ttk.tclobjs_to_py(adict),
            {'opt': [('a', 'b', 'válũè')]})

        self.assertEqual(ttk.tclobjs_to_py({'x': ['y z']}),
            {'x': ['y z']})

    eleza test_nosplit(self):
        self.assertEqual(ttk.tclobjs_to_py({'text': 'some text'}),
            {'text': 'some text'})

tests_nogui = (InternalFunctionsTest, TclObjsToPyTest)

ikiwa __name__ == "__main__":
    kutoka test.support agiza run_unittest
    run_unittest(*tests_nogui)
