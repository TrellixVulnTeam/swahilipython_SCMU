'''Mock classes that imitate idlelib modules ama classes.

Attributes na methods will be added kama needed kila tests.
'''

kutoka idlelib.idle_test.mock_tk agiza Text

kundi Func:
    '''Record call, capture args, rudisha/ashiria result set by test.

    When mock function ni called, set ama use attributes:
    self.called - increment call number even ikiwa no args, kwds pitaed.
    self.args - capture positional arguments.
    self.kwds - capture keyword arguments.
    self.result - rudisha ama ashiria value set kwenye __init__.
    self.rudisha_self - rudisha self instead, to mock query kundi rudisha.

    Most common use will probably be to mock instance methods.
    Given kundi instance, can set na delete kama instance attribute.
    Mock_tk.Var na Mbox_func are special variants of this.
    '''
    eleza __init__(self, result=Tupu, rudisha_self=Uongo):
        self.called = 0
        self.result = result
        self.rudisha_self = rudisha_self
        self.args = Tupu
        self.kwds = Tupu
    eleza __call__(self, *args, **kwds):
        self.called += 1
        self.args = args
        self.kwds = kwds
        ikiwa isinstance(self.result, BaseException):
            ashiria self.result
        elikiwa self.rudisha_self:
            rudisha self
        isipokua:
            rudisha self.result


kundi Editor:
    '''Minimally imitate editor.EditorWindow class.
    '''
    eleza __init__(self, flist=Tupu, filename=Tupu, key=Tupu, root=Tupu):
        self.text = Text()
        self.undo = UndoDelegator()

    eleza get_selection_indices(self):
        first = self.text.index('1.0')
        last = self.text.index('end')
        rudisha first, last


kundi UndoDelegator:
    '''Minimally imitate undo.UndoDelegator class.
    '''
    # A real undo block ni only needed kila user interaction.
    eleza undo_block_start(*args):
        pita
    eleza undo_block_stop(*args):
        pita
