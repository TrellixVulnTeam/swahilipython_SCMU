# Used by test_doctest.py.

kundi TwoNames:
    '''f() and g() are two names for the same method'''

    eleza f(self):
        '''
        >>> andika(TwoNames().f())
        f
        '''
        rudisha 'f'

    g = f # define an alias for f
