agiza functools
agiza inspect
agiza reprlib
agiza sys
agiza traceback

kutoka . agiza constants


eleza _get_function_source(func):
    func = inspect.unwrap(func)
    ikiwa inspect.isfunction(func):
        code = func.__code__
        rudisha (code.co_filename, code.co_firstlineno)
    ikiwa isinstance(func, functools.partial):
        rudisha _get_function_source(func.func)
    ikiwa isinstance(func, functools.partialmethod):
        rudisha _get_function_source(func.func)
    rudisha None


eleza _format_callback_source(func, args):
    func_repr = _format_callback(func, args, None)
    source = _get_function_source(func)
    ikiwa source:
        func_repr += f' at {source[0]}:{source[1]}'
    rudisha func_repr


eleza _format_args_and_kwargs(args, kwargs):
    """Format function arguments and keyword arguments.

    Special case for a single parameter: ('hello',) is formatted as ('hello').
    """
    # use reprlib to limit the length of the output
    items = []
    ikiwa args:
        items.extend(reprlib.repr(arg) for arg in args)
    ikiwa kwargs:
        items.extend(f'{k}={reprlib.repr(v)}' for k, v in kwargs.items())
    rudisha '({})'.format(', '.join(items))


eleza _format_callback(func, args, kwargs, suffix=''):
    ikiwa isinstance(func, functools.partial):
        suffix = _format_args_and_kwargs(args, kwargs) + suffix
        rudisha _format_callback(func.func, func.args, func.keywords, suffix)

    ikiwa hasattr(func, '__qualname__') and func.__qualname__:
        func_repr = func.__qualname__
    elikiwa hasattr(func, '__name__') and func.__name__:
        func_repr = func.__name__
    else:
        func_repr = repr(func)

    func_repr += _format_args_and_kwargs(args, kwargs)
    ikiwa suffix:
        func_repr += suffix
    rudisha func_repr


eleza extract_stack(f=None, limit=None):
    """Replacement for traceback.extract_stack() that only does the
    necessary work for asyncio debug mode.
    """
    ikiwa f is None:
        f = sys._getframe().f_back
    ikiwa limit is None:
        # Limit the amount of work to a reasonable amount, as extract_stack()
        # can be called for each coroutine and future in debug mode.
        limit = constants.DEBUG_STACK_DEPTH
    stack = traceback.StackSummary.extract(traceback.walk_stack(f),
                                           limit=limit,
                                           lookup_lines=False)
    stack.reverse()
    rudisha stack
