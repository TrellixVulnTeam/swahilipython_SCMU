# Remove all the .pyc files under ../Lib.


eleza deltree(root):
    agiza os
    kutoka os.path agiza join

    npyc = 0
    kila root, dirs, files kwenye os.walk(root):
        kila name kwenye files:
            # to be thorough
            ikiwa name.endswith(('.pyc', '.pyo')):
                npyc += 1
                os.remove(join(root, name))

    rudisha npyc

npyc = deltree("../Lib")
andika(npyc, ".pyc deleted")
