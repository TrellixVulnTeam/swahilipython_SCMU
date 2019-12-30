eleza test_line():
    a = 1
    andika('# Preamble', a)
    kila i kwenye range(2):
        a = i
        b = i+2
        c = i+3
        ikiwa c < 4:
            a = c
        d = a + b +c
        andika('#', a, b, c, d)
    a = 1
    andika('# Epilogue', a)


ikiwa __name__ == '__main__':
    test_line()
