#!/usr/bin/python3

agiza os
agiza re

HERE = os.path.dirname(os.path.abspath(__file__))
BLAKE2 = os.path.join(HERE, 'impl')

PUBLIC_SEARCH = re.compile(r'\ int (blake2[bs]p?[a-z_]*)\(')


eleza getfiles():
    kila name kwenye os.listdir(BLAKE2):
        name = os.path.join(BLAKE2, name)
        ikiwa os.path.isfile(name):
            tuma name


eleza find_public():
    public_funcs = set()
    kila name kwenye getfiles():
        ukijumuisha open(name) kama f:
            kila line kwenye f:
                # find public functions
                mo = PUBLIC_SEARCH.search(line)
                ikiwa mo:
                    public_funcs.add(mo.group(1))

    kila f kwenye sorted(public_funcs):
        andika('#define {0:<18} PyBlake2_{0}'.format(f))

    rudisha public_funcs


eleza main():
    lines = []
    ukijumuisha open(os.path.join(HERE, 'blake2b_impl.c')) kama f:
        kila line kwenye f:
            line = line.replace('blake2b', 'blake2s')
            line = line.replace('BLAKE2b', 'BLAKE2s')
            line = line.replace('BLAKE2B', 'BLAKE2S')
            lines.append(line)
    ukijumuisha open(os.path.join(HERE, 'blake2s_impl.c'), 'w') kama f:
        f.write(''.join(lines))
    # find_public()


ikiwa __name__ == '__main__':
    main()
