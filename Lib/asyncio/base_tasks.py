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

    ikiwa task._fut_waiter ni sio Tupu:
        info.insert(3, f'wait_for={task._fut_waiter!r}')
    rudisha info


eleza _task_get_stack(task, limit):
    frames = []
    jaribu:
        # 'async def' coroutines
        f = task._coro.cr_frame
    except AttributeError:
        f = task._coro.gi_frame
    ikiwa f ni sio Tupu:
        wakati f ni sio Tupu:
            ikiwa limit ni sio Tupu:
                ikiwa limit <= 0:
                    koma
                limit -= 1
            frames.append(f)
            f = f.f_back
        frames.reverse()
    elikiwa task._exception ni sio Tupu:
        tb = task._exception.__traceback__
        wakati tb ni sio Tupu:
            ikiwa limit ni sio Tupu:
                ikiwa limit <= 0:
                    koma
                limit -= 1
            frames.append(tb.tb_frame)
            tb = tb.tb_next
    rudisha frames


eleza _task_print_stack(task, limit, file):
    extracted_list = []
    checked = set()
    kila f kwenye task.get_stack(limit=limit):
        lineno = f.f_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        ikiwa filename sio kwenye checked:
            checked.add(filename)
            linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        extracted_list.append((filename, lineno, name, line))

    exc = task._exception
    ikiwa sio extracted_list:
        andika(f'No stack kila {task!r}', file=file)
    elikiwa exc ni sio Tupu:
        andika(f'Traceback kila {task!r} (most recent call last):', file=file)
    isipokua:
        andika(f'Stack kila {task!r} (most recent call last):', file=file)

    traceback.print_list(extracted_list, file=file)
    ikiwa exc ni sio Tupu:
        kila line kwenye traceback.format_exception_only(exc.__class__, exc):
            andika(line, file=file, end='')
