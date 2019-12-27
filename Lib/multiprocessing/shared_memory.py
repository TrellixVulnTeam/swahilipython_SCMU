"""Provides shared memory for direct access across processes.

The API of this package is currently provisional. Refer to the
documentation for details.
"""


__all__ = [ 'SharedMemory', 'ShareableList' ]


kutoka functools agiza partial
agiza mmap
agiza os
agiza errno
agiza struct
agiza secrets

ikiwa os.name == "nt":
    agiza _winapi
    _USE_POSIX = False
else:
    agiza _posixshmem
    _USE_POSIX = True


_O_CREX = os.O_CREAT | os.O_EXCL

# FreeBSD (and perhaps other BSDs) limit names to 14 characters.
_SHM_SAFE_NAME_LENGTH = 14

# Shared memory block name prefix
ikiwa _USE_POSIX:
    _SHM_NAME_PREFIX = '/psm_'
else:
    _SHM_NAME_PREFIX = 'wnsm_'


eleza _make_filename():
    "Create a random filename for the shared memory object."
    # number of random bytes to use for name
    nbytes = (_SHM_SAFE_NAME_LENGTH - len(_SHM_NAME_PREFIX)) // 2
    assert nbytes >= 2, '_SHM_NAME_PREFIX too long'
    name = _SHM_NAME_PREFIX + secrets.token_hex(nbytes)
    assert len(name) <= _SHM_SAFE_NAME_LENGTH
    rudisha name


kundi SharedMemory:
    """Creates a new shared memory block or attaches to an existing
    shared memory block.

    Every shared memory block is assigned a unique name.  This enables
    one process to create a shared memory block with a particular name
    so that a different process can attach to that same shared memory
    block using that same name.

    As a resource for sharing data across processes, shared memory blocks
    may outlive the original process that created them.  When one process
    no longer needs access to a shared memory block that might still be
    needed by other processes, the close() method should be called.
    When a shared memory block is no longer needed by any process, the
    unlink() method should be called to ensure proper cleanup."""

    # Defaults; enables close() and unlink() to run without errors.
    _name = None
    _fd = -1
    _mmap = None
    _buf = None
    _flags = os.O_RDWR
    _mode = 0o600
    _prepend_leading_slash = True ikiwa _USE_POSIX else False

    eleza __init__(self, name=None, create=False, size=0):
        ikiwa not size >= 0:
            raise ValueError("'size' must be a positive integer")
        ikiwa create:
            self._flags = _O_CREX | os.O_RDWR
        ikiwa name is None and not self._flags & os.O_EXCL:
            raise ValueError("'name' can only be None ikiwa create=True")

        ikiwa _USE_POSIX:

            # POSIX Shared Memory

            ikiwa name is None:
                while True:
                    name = _make_filename()
                    try:
                        self._fd = _posixshmem.shm_open(
                            name,
                            self._flags,
                            mode=self._mode
                        )
                    except FileExistsError:
                        continue
                    self._name = name
                    break
            else:
                name = "/" + name ikiwa self._prepend_leading_slash else name
                self._fd = _posixshmem.shm_open(
                    name,
                    self._flags,
                    mode=self._mode
                )
                self._name = name
            try:
                ikiwa create and size:
                    os.ftruncate(self._fd, size)
                stats = os.fstat(self._fd)
                size = stats.st_size
                self._mmap = mmap.mmap(self._fd, size)
            except OSError:
                self.unlink()
                raise

            kutoka .resource_tracker agiza register
            register(self._name, "shared_memory")

        else:

            # Windows Named Shared Memory

            ikiwa create:
                while True:
                    temp_name = _make_filename() ikiwa name is None else name
                    # Create and reserve shared memory block with this name
                    # until it can be attached to by mmap.
                    h_map = _winapi.CreateFileMapping(
                        _winapi.INVALID_HANDLE_VALUE,
                        _winapi.NULL,
                        _winapi.PAGE_READWRITE,
                        (size >> 32) & 0xFFFFFFFF,
                        size & 0xFFFFFFFF,
                        temp_name
                    )
                    try:
                        last_error_code = _winapi.GetLastError()
                        ikiwa last_error_code == _winapi.ERROR_ALREADY_EXISTS:
                            ikiwa name is not None:
                                raise FileExistsError(
                                    errno.EEXIST,
                                    os.strerror(errno.EEXIST),
                                    name,
                                    _winapi.ERROR_ALREADY_EXISTS
                                )
                            else:
                                continue
                        self._mmap = mmap.mmap(-1, size, tagname=temp_name)
                    finally:
                        _winapi.CloseHandle(h_map)
                    self._name = temp_name
                    break

            else:
                self._name = name
                # Dynamically determine the existing named shared memory
                # block's size which is likely a multiple of mmap.PAGESIZE.
                h_map = _winapi.OpenFileMapping(
                    _winapi.FILE_MAP_READ,
                    False,
                    name
                )
                try:
                    p_buf = _winapi.MapViewOfFile(
                        h_map,
                        _winapi.FILE_MAP_READ,
                        0,
                        0,
                        0
                    )
                finally:
                    _winapi.CloseHandle(h_map)
                size = _winapi.VirtualQuerySize(p_buf)
                self._mmap = mmap.mmap(-1, size, tagname=name)

        self._size = size
        self._buf = memoryview(self._mmap)

    eleza __del__(self):
        try:
            self.close()
        except OSError:
            pass

    eleza __reduce__(self):
        rudisha (
            self.__class__,
            (
                self.name,
                False,
                self.size,
            ),
        )

    eleza __repr__(self):
        rudisha f'{self.__class__.__name__}({self.name!r}, size={self.size})'

    @property
    eleza buf(self):
        "A memoryview of contents of the shared memory block."
        rudisha self._buf

    @property
    eleza name(self):
        "Unique name that identifies the shared memory block."
        reported_name = self._name
        ikiwa _USE_POSIX and self._prepend_leading_slash:
            ikiwa self._name.startswith("/"):
                reported_name = self._name[1:]
        rudisha reported_name

    @property
    eleza size(self):
        "Size in bytes."
        rudisha self._size

    eleza close(self):
        """Closes access to the shared memory kutoka this instance but does
        not destroy the shared memory block."""
        ikiwa self._buf is not None:
            self._buf.release()
            self._buf = None
        ikiwa self._mmap is not None:
            self._mmap.close()
            self._mmap = None
        ikiwa _USE_POSIX and self._fd >= 0:
            os.close(self._fd)
            self._fd = -1

    eleza unlink(self):
        """Requests that the underlying shared memory block be destroyed.

        In order to ensure proper cleanup of resources, unlink should be
        called once (and only once) across all processes which have access
        to the shared memory block."""
        ikiwa _USE_POSIX and self._name:
            kutoka .resource_tracker agiza unregister
            _posixshmem.shm_unlink(self._name)
            unregister(self._name, "shared_memory")


_encoding = "utf8"

kundi ShareableList:
    """Pattern for a mutable list-like object shareable via a shared
    memory block.  It differs kutoka the built-in list type in that these
    lists can not change their overall length (i.e. no append, insert,
    etc.)

    Because values are packed into a memoryview as bytes, the struct
    packing format for any storable value must require no more than 8
    characters to describe its format."""

    _types_mapping = {
        int: "q",
        float: "d",
        bool: "xxxxxxx?",
        str: "%ds",
        bytes: "%ds",
        None.__class__: "xxxxxx?x",
    }
    _alignment = 8
    _back_transforms_mapping = {
        0: lambda value: value,                   # int, float, bool
        1: lambda value: value.rstrip(b'\x00').decode(_encoding),  # str
        2: lambda value: value.rstrip(b'\x00'),   # bytes
        3: lambda _value: None,                   # None
    }

    @staticmethod
    eleza _extract_recreation_code(value):
        """Used in concert with _back_transforms_mapping to convert values
        into the appropriate Python objects when retrieving them kutoka
        the list as well as when storing them."""
        ikiwa not isinstance(value, (str, bytes, None.__class__)):
            rudisha 0
        elikiwa isinstance(value, str):
            rudisha 1
        elikiwa isinstance(value, bytes):
            rudisha 2
        else:
            rudisha 3  # NoneType

    eleza __init__(self, sequence=None, *, name=None):
        ikiwa sequence is not None:
            _formats = [
                self._types_mapping[type(item)]
                    ikiwa not isinstance(item, (str, bytes))
                    else self._types_mapping[type(item)] % (
                        self._alignment * (len(item) // self._alignment + 1),
                    )
                for item in sequence
            ]
            self._list_len = len(_formats)
            assert sum(len(fmt) <= 8 for fmt in _formats) == self._list_len
            self._allocated_bytes = tuple(
                    self._alignment ikiwa fmt[-1] != "s" else int(fmt[:-1])
                    for fmt in _formats
            )
            _recreation_codes = [
                self._extract_recreation_code(item) for item in sequence
            ]
            requested_size = struct.calcsize(
                "q" + self._format_size_metainfo +
                "".join(_formats) +
                self._format_packing_metainfo +
                self._format_back_transform_codes
            )

        else:
            requested_size = 8  # Some platforms require > 0.

        ikiwa name is not None and sequence is None:
            self.shm = SharedMemory(name)
        else:
            self.shm = SharedMemory(name, create=True, size=requested_size)

        ikiwa sequence is not None:
            _enc = _encoding
            struct.pack_into(
                "q" + self._format_size_metainfo,
                self.shm.buf,
                0,
                self._list_len,
                *(self._allocated_bytes)
            )
            struct.pack_into(
                "".join(_formats),
                self.shm.buf,
                self._offset_data_start,
                *(v.encode(_enc) ikiwa isinstance(v, str) else v for v in sequence)
            )
            struct.pack_into(
                self._format_packing_metainfo,
                self.shm.buf,
                self._offset_packing_formats,
                *(v.encode(_enc) for v in _formats)
            )
            struct.pack_into(
                self._format_back_transform_codes,
                self.shm.buf,
                self._offset_back_transform_codes,
                *(_recreation_codes)
            )

        else:
            self._list_len = len(self)  # Obtains size kutoka offset 0 in buffer.
            self._allocated_bytes = struct.unpack_kutoka(
                self._format_size_metainfo,
                self.shm.buf,
                1 * 8
            )

    eleza _get_packing_format(self, position):
        "Gets the packing format for a single value stored in the list."
        position = position ikiwa position >= 0 else position + self._list_len
        ikiwa (position >= self._list_len) or (self._list_len < 0):
            raise IndexError("Requested position out of range.")

        v = struct.unpack_kutoka(
            "8s",
            self.shm.buf,
            self._offset_packing_formats + position * 8
        )[0]
        fmt = v.rstrip(b'\x00')
        fmt_as_str = fmt.decode(_encoding)

        rudisha fmt_as_str

    eleza _get_back_transform(self, position):
        "Gets the back transformation function for a single value."

        position = position ikiwa position >= 0 else position + self._list_len
        ikiwa (position >= self._list_len) or (self._list_len < 0):
            raise IndexError("Requested position out of range.")

        transform_code = struct.unpack_kutoka(
            "b",
            self.shm.buf,
            self._offset_back_transform_codes + position
        )[0]
        transform_function = self._back_transforms_mapping[transform_code]

        rudisha transform_function

    eleza _set_packing_format_and_transform(self, position, fmt_as_str, value):
        """Sets the packing format and back transformation code for a
        single value in the list at the specified position."""

        position = position ikiwa position >= 0 else position + self._list_len
        ikiwa (position >= self._list_len) or (self._list_len < 0):
            raise IndexError("Requested position out of range.")

        struct.pack_into(
            "8s",
            self.shm.buf,
            self._offset_packing_formats + position * 8,
            fmt_as_str.encode(_encoding)
        )

        transform_code = self._extract_recreation_code(value)
        struct.pack_into(
            "b",
            self.shm.buf,
            self._offset_back_transform_codes + position,
            transform_code
        )

    eleza __getitem__(self, position):
        try:
            offset = self._offset_data_start \
                     + sum(self._allocated_bytes[:position])
            (v,) = struct.unpack_kutoka(
                self._get_packing_format(position),
                self.shm.buf,
                offset
            )
        except IndexError:
            raise IndexError("index out of range")

        back_transform = self._get_back_transform(position)
        v = back_transform(v)

        rudisha v

    eleza __setitem__(self, position, value):
        try:
            offset = self._offset_data_start \
                     + sum(self._allocated_bytes[:position])
            current_format = self._get_packing_format(position)
        except IndexError:
            raise IndexError("assignment index out of range")

        ikiwa not isinstance(value, (str, bytes)):
            new_format = self._types_mapping[type(value)]
        else:
            ikiwa len(value) > self._allocated_bytes[position]:
                raise ValueError("exceeds available storage for existing str")
            ikiwa current_format[-1] == "s":
                new_format = current_format
            else:
                new_format = self._types_mapping[str] % (
                    self._allocated_bytes[position],
                )

        self._set_packing_format_and_transform(
            position,
            new_format,
            value
        )
        value = value.encode(_encoding) ikiwa isinstance(value, str) else value
        struct.pack_into(new_format, self.shm.buf, offset, value)

    eleza __reduce__(self):
        rudisha partial(self.__class__, name=self.shm.name), ()

    eleza __len__(self):
        rudisha struct.unpack_kutoka("q", self.shm.buf, 0)[0]

    eleza __repr__(self):
        rudisha f'{self.__class__.__name__}({list(self)}, name={self.shm.name!r})'

    @property
    eleza format(self):
        "The struct packing format used by all currently stored values."
        rudisha "".join(
            self._get_packing_format(i) for i in range(self._list_len)
        )

    @property
    eleza _format_size_metainfo(self):
        "The struct packing format used for metainfo on storage sizes."
        rudisha f"{self._list_len}q"

    @property
    eleza _format_packing_metainfo(self):
        "The struct packing format used for the values' packing formats."
        rudisha "8s" * self._list_len

    @property
    eleza _format_back_transform_codes(self):
        "The struct packing format used for the values' back transforms."
        rudisha "b" * self._list_len

    @property
    eleza _offset_data_start(self):
        rudisha (self._list_len + 1) * 8  # 8 bytes per "q"

    @property
    eleza _offset_packing_formats(self):
        rudisha self._offset_data_start + sum(self._allocated_bytes)

    @property
    eleza _offset_back_transform_codes(self):
        rudisha self._offset_packing_formats + self._list_len * 8

    eleza count(self, value):
        "L.count(value) -> integer -- rudisha number of occurrences of value."

        rudisha sum(value == entry for entry in self)

    eleza index(self, value):
        """L.index(value) -> integer -- rudisha first index of value.
        Raises ValueError ikiwa the value is not present."""

        for position, entry in enumerate(self):
            ikiwa value == entry:
                rudisha position
        else:
            raise ValueError(f"{value!r} not in this container")
