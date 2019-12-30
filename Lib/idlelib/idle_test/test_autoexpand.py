"Test autoexpand, coverage 100%."

kutoka idlelib.autoexpand agiza AutoExpand
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Text, Tk


kundi DummyEditwin:
    # AutoExpand.__init__ only needs .text
    eleza __init__(self, text):
        self.text = text

kundi AutoExpandTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.tk = Tk()
        cls.text = Text(cls.tk)
        cls.auto_expand = AutoExpand(DummyEditwin(cls.text))
        cls.auto_expand.bell = lambda: Tupu

# If mock_tk.Text._decode understood indexes 'insert' ukijumuisha suffixed 'linestart',
# 'wordstart', na 'lineend', used by autoexpand, we could use the following
# to run these test on non-gui machines (but check bell).
##        jaribu:
##            requires('gui')
##            # ashiria ResourceDenied()  # Uncomment to test mock.
##        except ResourceDenied:
##            kutoka idlelib.idle_test.mock_tk agiza Text
##            cls.text = Text()
##            cls.text.bell = lambda: Tupu
##        isipokua:
##            kutoka tkinter agiza Tk, Text
##            cls.tk = Tk()
##            cls.text = Text(cls.tk)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text, cls.auto_expand
        ikiwa hasattr(cls, 'tk'):
            cls.tk.destroy()
            toa cls.tk

    eleza tearDown(self):
        self.text.delete('1.0', 'end')

    eleza test_get_prevword(self):
        text = self.text
        previous = self.auto_expand.getprevword
        equal = self.assertEqual

        equal(previous(), '')

        text.insert('insert', 't')
        equal(previous(), 't')

        text.insert('insert', 'his')
        equal(previous(), 'this')

        text.insert('insert', ' ')
        equal(previous(), '')

        text.insert('insert', 'is')
        equal(previous(), 'is')

        text.insert('insert', '\nsample\nstring')
        equal(previous(), 'string')

        text.delete('3.0', 'insert')
        equal(previous(), '')

        text.delete('1.0', 'end')
        equal(previous(), '')

    eleza test_before_only(self):
        previous = self.auto_expand.getprevword
        expand = self.auto_expand.expand_word_event
        equal = self.assertEqual

        self.text.insert('insert', 'ab ac bx ad ab a')
        equal(self.auto_expand.getwords(), ['ab', 'ad', 'ac', 'a'])
        expand('event')
        equal(previous(), 'ab')
        expand('event')
        equal(previous(), 'ad')
        expand('event')
        equal(previous(), 'ac')
        expand('event')
        equal(previous(), 'a')

    eleza test_after_only(self):
        # Also add punctuation 'noise' that should be ignored.
        text = self.text
        previous = self.auto_expand.getprevword
        expand = self.auto_expand.expand_word_event
        equal = self.assertEqual

        text.insert('insert', 'a, [ab] ac: () bx"" cd ac= ad ya')
        text.mark_set('insert', '1.1')
        equal(self.auto_expand.getwords(), ['ab', 'ac', 'ad', 'a'])
        expand('event')
        equal(previous(), 'ab')
        expand('event')
        equal(previous(), 'ac')
        expand('event')
        equal(previous(), 'ad')
        expand('event')
        equal(previous(), 'a')

    eleza test_both_before_after(self):
        text = self.text
        previous = self.auto_expand.getprevword
        expand = self.auto_expand.expand_word_event
        equal = self.assertEqual

        text.insert('insert', 'ab xy yz\n')
        text.insert('insert', 'a ac by ac')

        text.mark_set('insert', '2.1')
        equal(self.auto_expand.getwords(), ['ab', 'ac', 'a'])
        expand('event')
        equal(previous(), 'ab')
        expand('event')
        equal(previous(), 'ac')
        expand('event')
        equal(previous(), 'a')

    eleza test_other_expand_cases(self):
        text = self.text
        expand = self.auto_expand.expand_word_event
        equal = self.assertEqual

        # no expansion candidate found
        equal(self.auto_expand.getwords(), [])
        equal(expand('event'), 'koma')

        text.insert('insert', 'bx cy dz a')
        equal(self.auto_expand.getwords(), [])

        # reset state by successfully expanding once
        # move cursor to another position na expand again
        text.insert('insert', 'ac xy a ac ad a')
        text.mark_set('insert', '1.7')
        expand('event')
        initial_state = self.auto_expand.state
        text.mark_set('insert', '1.end')
        expand('event')
        new_state = self.auto_expand.state
        self.assertNotEqual(initial_state, new_state)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
