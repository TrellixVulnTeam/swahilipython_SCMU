agiza linecache
agiza traceback

kutoka . agiza base_futures
kutoka . agiza coroutines


eleza _task_repr_info(task):
    info = base_futures._future_repr_info(task)

    ikiwa task._must_cancel:
        # replace status
        info[0] = 'cancelling'

    info.insert(1, 'name=%r' % task.get_name())

    coro = coroutines._format_coroutine(task._coro)
    info.insert(2, f'coro=<{coro}>')

    ikiwa task._fut_waiter is not None:
        info.insert(3, f'wait_for={task._fut_waiter!r}')
    rudisha info


eleza _task_get_stack(task, limit):
    frames = []
    try:
        # 'async def' coroutines
        f = task._coro.cr_frame
    except AttributeError:
        f = task._coro.gi_frame
    ikiwa f is not None:
        while f is not None:
            ikiwa limit is not None:
                ikiwa limit <= 0:
                    break
                limit -= 1
            frames.append(f)
            f = f.f_back
        frames.reverse()
    elikiwa task._exception is not None:
        tb = task._exception.__traceback__
        while tb is not None:
            ikiwa limit is not None:
                ikiwa limit <= 0:
                    break
                limit -= 1
            frames.append(tb.tb_frame)
            tb = tb.tb_next
    rudisha frames


eleza _task_print_stack(task, limit, file):
    extracted_list = []
    checked = set()
    for f in task.get_stack(limit=limit):
        lineno = f.f_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        ikiwa filename not in checked:
            checked.add(filename)
            linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        extracted_list.append((filename, lineno, name, line))

    exc = task._exception
    ikiwa not extracted_list:
        andika(f'No stack for {task!r}', file=file)
    elikiwa exc is not None:
        andika(f'Traceback for {task!r} (most recent call last):', file=file)
    else:
        andika(f'Stack for {task!r} (most recent call last):', file=file)

    traceback.print_list(extracted_list, file=file)
    ikiwa exc is not None:
        for line in traceback.format_exception_only(exc.__class__, exc):
            andika(line, file=file, end='')
