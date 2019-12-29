agiza multiprocessing, sys

eleza foo():
    andika("123")

# Because "ikiwa __name__ == '__main__'" ni missing this will sio work
# correctly on Windows.  However, we should get a RuntimeError rather
# than the Windows equivalent of a fork bomb.

ikiwa len(sys.argv) > 1:
    multiprocessing.set_start_method(sys.argv[1])
isipokua:
    multiprocessing.set_start_method('spawn')

p = multiprocessing.Process(target=foo)
p.start()
p.join()
sys.exit(p.exitcode)
