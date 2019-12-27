"""asyncio exceptions."""


__all__ = ('CancelledError', 'InvalidStateError', 'TimeoutError',
           'IncompleteReadError', 'LimitOverrunError',
           'SendfileNotAvailableError')


kundi CancelledError(BaseException):
    """The Future or Task was cancelled."""


kundi TimeoutError(Exception):
    """The operation exceeded the given deadline."""


kundi InvalidStateError(Exception):
    """The operation is not allowed in this state."""


kundi SendfileNotAvailableError(RuntimeError):
    """Sendfile syscall is not available.

    Raised ikiwa OS does not support sendfile syscall for given socket or
    file type.
    """


kundi IncompleteReadError(EOFError):
    """
    Incomplete read error. Attributes:

    - partial: read bytes string before the end of stream was reached
    - expected: total number of expected bytes (or None ikiwa unknown)
    """
    eleza __init__(self, partial, expected):
        super().__init__(f'{len(partial)} bytes read on a total of '
                         f'{expected!r} expected bytes')
        self.partial = partial
        self.expected = expected

    eleza __reduce__(self):
        rudisha type(self), (self.partial, self.expected)


kundi LimitOverrunError(Exception):
    """Reached the buffer limit while looking for a separator.

    Attributes:
    - consumed: total number of to be consumed bytes.
    """
    eleza __init__(self, message, consumed):
        super().__init__(message)
        self.consumed = consumed

    eleza __reduce__(self):
        rudisha type(self), (self.args[0], self.consumed)
