'''Mock classes that imitate idlelib modules or classes.

Attributes and methods will be added as needed for tests.
'''

kutoka idlelib.idle_test.mock_tk agiza Text

kundi Func:
    '''Record call, capture args, return/raise result set by test.

    When mock function is called, set or use attributes:
    self.called - increment call number even ikiwa no args, kwds passed.
    self.args - capture positional arguments.
    self.kwds - capture keyword arguments.
    self.result - rudisha or raise value set in __init__.
    self.return_self - rudisha self instead, to mock query kundi return.

    Most common use will probably be to mock instance methods.
    Given kundi instance, can set and delete as instance attribute.
    Mock_tk.Var and Mbox_func are special variants of this.
    '''
    eleza __init__(self, result=None, return_self=False):
        self.called = 0
        self.result = result
        self.return_self = return_self
        self.args = None
        self.kwds = None
    eleza __call__(self, *args, **kwds):
        self.called += 1
        self.args = args
        self.kwds = kwds
        ikiwa isinstance(self.result, BaseException):
            raise self.result
        elikiwa self.return_self:
            rudisha self
        else:
            rudisha self.result


kundi Editor:
    '''Minimally imitate editor.EditorWindow class.
    '''
    eleza __init__(self, flist=None, filename=None, key=None, root=None):
        self.text = Text()
        self.undo = UndoDelegator()

    eleza get_selection_indices(self):
        first = self.text.index('1.0')
        last = self.text.index('end')
        rudisha first, last


kundi UndoDelegator:
    '''Minimally imitate undo.UndoDelegator class.
    '''
    # A real undo block is only needed for user interaction.
    eleza undo_block_start(*args):
        pass
    eleza undo_block_stop(*args):
        pass
