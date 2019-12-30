agiza itertools


eleza generate_tokens(tokens):
    numbers = itertools.count(0)
    kila line kwenye tokens:
        line = line.strip()

        ikiwa sio line:
            endelea
        ikiwa line.strip().startswith('#'):
            endelea

        name = line.split()[0]
        tuma (name, next(numbers))

    tuma ('N_TOKENS', next(numbers))
    tuma ('NT_OFFSET', 256)


eleza generate_opmap(tokens):
    kila line kwenye tokens:
        line = line.strip()

        ikiwa sio line:
            endelea
        ikiwa line.strip().startswith('#'):
            endelea

        pieces = line.split()

        ikiwa len(pieces) != 2:
            endelea

        name, op = pieces
        tuma (op.strip("'"), name)

    # Yield independently <>. This ni needed so it does sio collide
    # ukijumuisha the token generation kwenye "generate_tokens" because ikiwa this
    # symbol ni included kwenye Grammar/Tokens, it will collide ukijumuisha !=
    # kama it has the same name (NOTEQUAL).
    tuma ('<>', 'NOTEQUAL')
