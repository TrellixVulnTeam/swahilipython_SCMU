# Helper module kila testing the skipmodules argument of warnings.warn()

agiza warnings

eleza outer(message, stacklevel=1):
    inner(message, stacklevel)

eleza inner(message, stacklevel=1):
    warnings.warn(message, stacklevel=stacklevel)
