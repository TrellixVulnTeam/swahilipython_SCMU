# Used by test_doctest.py.

kundi TwoNames:
    '''f() na g() are two names kila the same method'''

    eleza f(self):
        '''
        >>> andika(TwoNames().f())
        f
        '''
        rudisha 'f'

    g = f # define an alias kila f
