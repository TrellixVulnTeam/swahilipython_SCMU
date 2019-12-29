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
    rudisha Tupu


eleza _format_callback_source(func, args):
    func_repr = _format_callback(func, args, Tupu)
    source = _get_function_source(func)
    ikiwa source:
        func_repr += f' at {source[0]}:{source[1]}'
    rudisha func_repr


eleza _format_args_and_kwargs(args, kwargs):
    """Format function arguments na keyword arguments.

    Special case kila a single parameter: ('hello',) ni formatted kama ('hello').
    """
    # use reprlib to limit the length of the output
    items = []
    ikiwa args:
        items.extend(reprlib.repr(arg) kila arg kwenye args)
    ikiwa kwargs:
        items.extend(f'{k}={reprlib.repr(v)}' kila k, v kwenye kwargs.items())
    rudisha '({})'.format(', '.join(items))


eleza _format_callback(func, args, kwargs, suffix=''):
    ikiwa isinstance(func, functools.partial):
        suffix = _format_args_and_kwargs(args, kwargs) + suffix
        rudisha _format_callback(func.func, func.args, func.keywords, suffix)

    ikiwa hasattr(func, '__qualname__') na func.__qualname__:
        func_repr = func.__qualname__
    elikiwa hasattr(func, '__name__') na func.__name__:
        func_repr = func.__name__
    isipokua:
        func_repr = repr(func)

    func_repr += _format_args_and_kwargs(args, kwargs)
    ikiwa suffix:
        func_repr += suffix
    rudisha func_repr


eleza extract_stack(f=Tupu, limit=Tupu):
    """Replacement kila traceback.extract_stack() that only does the
    necessary work kila asyncio debug mode.
    """
    ikiwa f ni Tupu:
        f = sys._getframe().f_back
    ikiwa limit ni Tupu:
        # Limit the amount of work to a reasonable amount, kama extract_stack()
        # can be called kila each coroutine na future kwenye debug mode.
        limit = constants.DEBUG_STACK_DEPTH
    stack = traceback.StackSummary.extract(traceback.walk_stack(f),
                                           limit=limit,
                                           lookup_lines=Uongo)
    stack.reverse()
    rudisha stack
