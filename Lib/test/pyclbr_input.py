"""Test cases kila test_pyclbr.py"""

eleza f(): pass

kundi Other(object):
    @classmethod
    eleza foo(c): pass

    eleza om(self): pass

kundi B (object):
    eleza bm(self): pass

kundi C (B):
    foo = Other().foo
    om = Other.om

    d = 10

    # XXX: This causes test_pyclbr.py to fail, but only because the
    #      introspection-based is_method() code kwenye the test can't
    #      distinguish between this na a genuine method function like m().
    #      The pyclbr.py module gets this right as it parses the text.
    #
    #f = f

    eleza m(self): pass

    @staticmethod
    eleza sm(self): pass

    @classmethod
    eleza cm(self): pass
