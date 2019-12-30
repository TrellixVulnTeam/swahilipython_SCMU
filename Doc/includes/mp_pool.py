agiza multiprocessing
agiza time
agiza random
agiza sys

#
# Functions used by test code
#

eleza calculate(func, args):
    result = func(*args)
    rudisha '%s says that %s%s = %s' % (
        multiprocessing.current_process().name,
        func.__name__, args, result
        )

eleza calculatestar(args):
    rudisha calculate(*args)

eleza mul(a, b):
    time.sleep(0.5 * random.random())
    rudisha a * b

eleza plus(a, b):
    time.sleep(0.5 * random.random())
    rudisha a + b

eleza f(x):
    rudisha 1.0 / (x - 5.0)

eleza pow3(x):
    rudisha x ** 3

eleza noop(x):
    pita

#
# Test code
#

eleza test():
    PROCESSES = 4
    andika('Creating pool ukijumuisha %d processes\n' % PROCESSES)

    ukijumuisha multiprocessing.Pool(PROCESSES) kama pool:
        #
        # Tests
        #

        TASKS = [(mul, (i, 7)) kila i kwenye range(10)] + \
                [(plus, (i, 8)) kila i kwenye range(10)]

        results = [pool.apply_async(calculate, t) kila t kwenye TASKS]
        imap_it = pool.imap(calculatestar, TASKS)
        imap_unordered_it = pool.imap_unordered(calculatestar, TASKS)

        andika('Ordered results using pool.apply_async():')
        kila r kwenye results:
            andika('\t', r.get())
        andika()

        andika('Ordered results using pool.imap():')
        kila x kwenye imap_it:
            andika('\t', x)
        andika()

        andika('Unordered results using pool.imap_unordered():')
        kila x kwenye imap_unordered_it:
            andika('\t', x)
        andika()

        andika('Ordered results using pool.map() --- will block till complete:')
        kila x kwenye pool.map(calculatestar, TASKS):
            andika('\t', x)
        andika()

        #
        # Test error handling
        #

        andika('Testing error handling:')

        jaribu:
            andika(pool.apply(f, (5,)))
        tatizo ZeroDivisionError:
            andika('\tGot ZeroDivisionError kama expected kutoka pool.apply()')
        isipokua:
            ashiria AssertionError('expected ZeroDivisionError')

        jaribu:
            andika(pool.map(f, list(range(10))))
        tatizo ZeroDivisionError:
            andika('\tGot ZeroDivisionError kama expected kutoka pool.map()')
        isipokua:
            ashiria AssertionError('expected ZeroDivisionError')

        jaribu:
            andika(list(pool.imap(f, list(range(10)))))
        tatizo ZeroDivisionError:
            andika('\tGot ZeroDivisionError kama expected kutoka list(pool.imap())')
        isipokua:
            ashiria AssertionError('expected ZeroDivisionError')

        it = pool.imap(f, list(range(10)))
        kila i kwenye range(10):
            jaribu:
                x = next(it)
            tatizo ZeroDivisionError:
                ikiwa i == 5:
                    pita
            tatizo StopIteration:
                koma
            isipokua:
                ikiwa i == 5:
                    ashiria AssertionError('expected ZeroDivisionError')

        assert i == 9
        andika('\tGot ZeroDivisionError kama expected kutoka IMapIterator.next()')
        andika()

        #
        # Testing timeouts
        #

        andika('Testing ApplyResult.get() ukijumuisha timeout:', end=' ')
        res = pool.apply_async(calculate, TASKS[0])
        wakati 1:
            sys.stdout.flush()
            jaribu:
                sys.stdout.write('\n\t%s' % res.get(0.02))
                koma
            tatizo multiprocessing.TimeoutError:
                sys.stdout.write('.')
        andika()
        andika()

        andika('Testing IMapIterator.next() ukijumuisha timeout:', end=' ')
        it = pool.imap(calculatestar, TASKS)
        wakati 1:
            sys.stdout.flush()
            jaribu:
                sys.stdout.write('\n\t%s' % it.next(0.02))
            tatizo StopIteration:
                koma
            tatizo multiprocessing.TimeoutError:
                sys.stdout.write('.')
        andika()
        andika()


ikiwa __name__ == '__main__':
    multiprocessing.freeze_support()
    test()
