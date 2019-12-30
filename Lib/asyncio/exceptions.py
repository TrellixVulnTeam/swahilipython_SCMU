"""asyncio exceptions."""


__all__ = ('CancelledError', 'InvalidStateError', 'TimeoutError',
           'IncompleteReadError', 'LimitOverrunError',
           'SendfileNotAvailableError')


kundi CancelledError(BaseException):
    """The Future ama Task was cancelled."""


kundi TimeoutError(Exception):
    """The operation exceeded the given deadline."""


kundi InvalidStateError(Exception):
    """The operation ni sio allowed kwenye this state."""


kundi SendfileNotAvailableError(RuntimeError):
    """Sendfile syscall ni sio available.

    Raised ikiwa OS does sio support sendfile syscall kila given socket ama
    file type.
    """


kundi IncompleteReadError(EOFError):
    """
    Incomplete read error. Attributes:

    - partial: read bytes string before the end of stream was reached
    - expected: total number of expected bytes (or Tupu ikiwa unknown)
    """
    eleza __init__(self, partial, expected):
        super().__init__(f'{len(partial)} bytes read on a total of '
                         f'{expected!r} expected bytes')
        self.partial = partial
        self.expected = expected

    eleza __reduce__(self):
        rudisha type(self), (self.partial, self.expected)


kundi LimitOverrunError(Exception):
    """Reached the buffer limit wakati looking kila a separator.

    Attributes:
    - consumed: total number of to be consumed bytes.
    """
    eleza __init__(self, message, consumed):
        super().__init__(message)
        self.consumed = consumed

    eleza __reduce__(self):
        rudisha type(self), (self.args[0], self.consumed)
