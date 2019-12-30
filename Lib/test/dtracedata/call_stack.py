eleza function_1():
    function_3(1, 2)

# Check stacktrace
eleza function_2():
    function_1()

# CALL_FUNCTION_VAR
eleza function_3(dummy, dummy2):
    pass

# CALL_FUNCTION_KW
eleza function_4(**dummy):
    rudisha 1
    rudisha 2  # unreachable

# CALL_FUNCTION_VAR_KW
eleza function_5(dummy, dummy2, **dummy3):
    ikiwa Uongo:
        rudisha 7
    rudisha 8

eleza start():
    function_1()
    function_2()
    function_3(1, 2)
    function_4(test=42)
    function_5(*(1, 2), **{"test": 42})

start()
