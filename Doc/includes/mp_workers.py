agiza time
agiza random

kutoka multiprocessing agiza Process, Queue, current_process, freeze_support

#
# Function run by worker processes
#

eleza worker(input, output):
    kila func, args kwenye iter(input.get, 'STOP'):
        result = calculate(func, args)
        output.put(result)

#
# Function used to calculate result
#

eleza calculate(func, args):
    result = func(*args)
    rudisha '%s says that %s%s = %s' % \
        (current_process().name, func.__name__, args, result)

#
# Functions referenced by tasks
#

eleza mul(a, b):
    time.sleep(0.5*random.random())
    rudisha a * b

eleza plus(a, b):
    time.sleep(0.5*random.random())
    rudisha a + b

#
#
#

eleza test():
    NUMBER_OF_PROCESSES = 4
    TASKS1 = [(mul, (i, 7)) kila i kwenye range(20)]
    TASKS2 = [(plus, (i, 8)) kila i kwenye range(10)]

    # Create queues
    task_queue = Queue()
    done_queue = Queue()

    # Submit tasks
    kila task kwenye TASKS1:
        task_queue.put(task)

    # Start worker processes
    kila i kwenye range(NUMBER_OF_PROCESSES):
        Process(target=worker, args=(task_queue, done_queue)).start()

    # Get na andika results
    andika('Unordered results:')
    kila i kwenye range(len(TASKS1)):
        andika('\t', done_queue.get())

    # Add more tasks using `put()`
    kila task kwenye TASKS2:
        task_queue.put(task)

    # Get na andika some more results
    kila i kwenye range(len(TASKS2)):
        andika('\t', done_queue.get())

    # Tell child processes to stop
    kila i kwenye range(NUMBER_OF_PROCESSES):
        task_queue.put('STOP')


ikiwa __name__ == '__main__':
    freeze_support()
    test()
