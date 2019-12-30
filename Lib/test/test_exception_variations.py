
agiza unittest

kundi ExceptionTestCase(unittest.TestCase):
    eleza test_try_except_else_finally(self):
        hit_tatizo = Uongo
        hit_else = Uongo
        hit_finally = Uongo

        jaribu:
            ashiria Exception('nyaa!')
        tatizo:
            hit_tatizo = Kweli
        isipokua:
            hit_else = Kweli
        mwishowe:
            hit_finally = Kweli

        self.assertKweli(hit_except)
        self.assertKweli(hit_finally)
        self.assertUongo(hit_else)

    eleza test_try_except_else_finally_no_exception(self):
        hit_tatizo = Uongo
        hit_else = Uongo
        hit_finally = Uongo

        jaribu:
            pita
        tatizo:
            hit_tatizo = Kweli
        isipokua:
            hit_else = Kweli
        mwishowe:
            hit_finally = Kweli

        self.assertUongo(hit_except)
        self.assertKweli(hit_finally)
        self.assertKweli(hit_else)

    eleza test_try_except_finally(self):
        hit_tatizo = Uongo
        hit_finally = Uongo

        jaribu:
            ashiria Exception('yarr!')
        tatizo:
            hit_tatizo = Kweli
        mwishowe:
            hit_finally = Kweli

        self.assertKweli(hit_except)
        self.assertKweli(hit_finally)

    eleza test_try_except_finally_no_exception(self):
        hit_tatizo = Uongo
        hit_finally = Uongo

        jaribu:
            pita
        tatizo:
            hit_tatizo = Kweli
        mwishowe:
            hit_finally = Kweli

        self.assertUongo(hit_except)
        self.assertKweli(hit_finally)

    eleza test_try_except(self):
        hit_tatizo = Uongo

        jaribu:
            ashiria Exception('ahoy!')
        tatizo:
            hit_tatizo = Kweli

        self.assertKweli(hit_except)

    eleza test_try_except_no_exception(self):
        hit_tatizo = Uongo

        jaribu:
            pita
        tatizo:
            hit_tatizo = Kweli

        self.assertUongo(hit_except)

    eleza test_try_except_else(self):
        hit_tatizo = Uongo
        hit_else = Uongo

        jaribu:
            ashiria Exception('foo!')
        tatizo:
            hit_tatizo = Kweli
        isipokua:
            hit_else = Kweli

        self.assertUongo(hit_else)
        self.assertKweli(hit_except)

    eleza test_try_except_else_no_exception(self):
        hit_tatizo = Uongo
        hit_else = Uongo

        jaribu:
            pita
        tatizo:
            hit_tatizo = Kweli
        isipokua:
            hit_else = Kweli

        self.assertUongo(hit_except)
        self.assertKweli(hit_else)

    eleza test_try_finally_no_exception(self):
        hit_finally = Uongo

        jaribu:
            pita
        mwishowe:
            hit_finally = Kweli

        self.assertKweli(hit_finally)

    eleza test_nested(self):
        hit_finally = Uongo
        hit_inner_tatizo = Uongo
        hit_inner_finally = Uongo

        jaribu:
            jaribu:
                ashiria Exception('inner exception')
            tatizo:
                hit_inner_tatizo = Kweli
            mwishowe:
                hit_inner_finally = Kweli
        mwishowe:
            hit_finally = Kweli

        self.assertKweli(hit_inner_except)
        self.assertKweli(hit_inner_finally)
        self.assertKweli(hit_finally)

    eleza test_nested_else(self):
        hit_else = Uongo
        hit_finally = Uongo
        hit_tatizo = Uongo
        hit_inner_tatizo = Uongo
        hit_inner_else = Uongo

        jaribu:
            jaribu:
                pita
            tatizo:
                hit_inner_tatizo = Kweli
            isipokua:
                hit_inner_else = Kweli

            ashiria Exception('outer exception')
        tatizo:
            hit_tatizo = Kweli
        isipokua:
            hit_else = Kweli
        mwishowe:
            hit_finally = Kweli

        self.assertUongo(hit_inner_except)
        self.assertKweli(hit_inner_else)
        self.assertUongo(hit_else)
        self.assertKweli(hit_finally)
        self.assertKweli(hit_except)

ikiwa __name__ == '__main__':
    unittest.main()
