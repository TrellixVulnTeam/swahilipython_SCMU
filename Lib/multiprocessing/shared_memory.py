"""Provides shared memory kila direct access across processes.

The API of this package ni currently provisional. Refer to the
documentation kila details.
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
    _USE_POSIX = Uongo
isipokua:
    agiza _posixshmem
    _USE_POSIX = Kweli


_O_CREX = os.O_CREAT | os.O_EXCL

# FreeBSD (and perhaps other BSDs) limit names to 14 characters.
_SHM_SAFE_NAME_LENGTH = 14

# Shared memory block name prefix
ikiwa _USE_POSIX:
    _SHM_NAME_PREFIX = '/psm_'
isipokua:
    _SHM_NAME_PREFIX = 'wnsm_'


eleza _make_filename():
    "Create a random filename kila the shared memory object."
    # number of random bytes to use kila name
    nbytes = (_SHM_SAFE_NAME_LENGTH - len(_SHM_NAME_PREFIX)) // 2
    assert nbytes >= 2, '_SHM_NAME_PREFIX too long'
    name = _SHM_NAME_PREFIX + secrets.token_hex(nbytes)
    assert len(name) <= _SHM_SAFE_NAME_LENGTH
    rudisha name


kundi SharedMemory:
    """Creates a new shared memory block ama attaches to an existing
    shared memory block.

    Every shared memory block ni assigned a unique name.  This enables
    one process to create a shared memory block with a particular name
    so that a different process can attach to that same shared memory
    block using that same name.

    As a resource kila sharing data across processes, shared memory blocks
    may outlive the original process that created them.  When one process
    no longer needs access to a shared memory block that might still be
    needed by other processes, the close() method should be called.
    When a shared memory block ni no longer needed by any process, the
    unlink() method should be called to ensure proper cleanup."""

    # Defaults; enables close() na unlink() to run without errors.
    _name = Tupu
    _fd = -1
    _mmap = Tupu
    _buf = Tupu
    _flags = os.O_RDWR
    _mode = 0o600
    _prepend_leading_slash = Kweli ikiwa _USE_POSIX else Uongo

    eleza __init__(self, name=Tupu, create=Uongo, size=0):
        ikiwa sio size >= 0:
            ashiria ValueError("'size' must be a positive integer")
        ikiwa create:
            self._flags = _O_CREX | os.O_RDWR
        ikiwa name ni Tupu na sio self._flags & os.O_EXCL:
            ashiria ValueError("'name' can only be Tupu ikiwa create=Kweli")

        ikiwa _USE_POSIX:

            # POSIX Shared Memory

            ikiwa name ni Tupu:
                wakati Kweli:
                    name = _make_filename()
                    jaribu:
                        self._fd = _posixshmem.shm_open(
                            name,
                            self._flags,
                            mode=self._mode
                        )
                    tatizo FileExistsError:
                        endelea
                    self._name = name
                    koma
            isipokua:
                name = "/" + name ikiwa self._prepend_leading_slash else name
                self._fd = _posixshmem.shm_open(
                    name,
                    self._flags,
                    mode=self._mode
                )
                self._name = name
            jaribu:
                ikiwa create na size:
                    os.ftruncate(self._fd, size)
                stats = os.fstat(self._fd)
                size = stats.st_size
                self._mmap = mmap.mmap(self._fd, size)
            tatizo OSError:
                self.unlink()
                ashiria

            kutoka .resource_tracker agiza register
            register(self._name, "shared_memory")

        isipokua:

            # Windows Named Shared Memory

            ikiwa create:
                wakati Kweli:
                    temp_name = _make_filename() ikiwa name ni Tupu else name
                    # Create na reserve shared memory block with this name
                    # until it can be attached to by mmap.
                    h_map = _winapi.CreateFileMapping(
                        _winapi.INVALID_HANDLE_VALUE,
                        _winapi.NULL,
                        _winapi.PAGE_READWRITE,
                        (size >> 32) & 0xFFFFFFFF,
                        size & 0xFFFFFFFF,
                        temp_name
                    )
                    jaribu:
                        last_error_code = _winapi.GetLastError()
                        ikiwa last_error_code == _winapi.ERROR_ALREADY_EXISTS:
                            ikiwa name ni sio Tupu:
                                ashiria FileExistsError(
                                    errno.EEXIST,
                                    os.strerror(errno.EEXIST),
                                    name,
                                    _winapi.ERROR_ALREADY_EXISTS
                                )
                            isipokua:
                                endelea
                        self._mmap = mmap.mmap(-1, size, tagname=temp_name)
                    mwishowe:
                        _winapi.CloseHandle(h_map)
                    self._name = temp_name
                    koma

            isipokua:
                self._name = name
                # Dynamically determine the existing named shared memory
                # block's size which ni likely a multiple of mmap.PAGESIZE.
                h_map = _winapi.OpenFileMapping(
                    _winapi.FILE_MAP_READ,
                    Uongo,
                    name
                )
                jaribu:
                    p_buf = _winapi.MapViewOfFile(
                        h_map,
                        _winapi.FILE_MAP_READ,
                        0,
                        0,
                        0
                    )
                mwishowe:
                    _winapi.CloseHandle(h_map)
                size = _winapi.VirtualQuerySize(p_buf)
                self._mmap = mmap.mmap(-1, size, tagname=name)

        self._size = size
        self._buf = memoryview(self._mmap)

    eleza __del__(self):
        jaribu:
            self.close()
        tatizo OSError:
            pita

    eleza __reduce__(self):
        rudisha (
            self.__class__,
            (
                self.name,
                Uongo,
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
        ikiwa _USE_POSIX na self._prepend_leading_slash:
            ikiwa self._name.startswith("/"):
                reported_name = self._name[1:]
        rudisha reported_name

    @property
    eleza size(self):
        "Size kwenye bytes."
        rudisha self._size

    eleza close(self):
        """Closes access to the shared memory kutoka this instance but does
        sio destroy the shared memory block."""
        ikiwa self._buf ni sio Tupu:
            self._buf.release()
            self._buf = Tupu
        ikiwa self._mmap ni sio Tupu:
            self._mmap.close()
            self._mmap = Tupu
        ikiwa _USE_POSIX na self._fd >= 0:
            os.close(self._fd)
            self._fd = -1

    eleza unlink(self):
        """Requests that the underlying shared memory block be destroyed.

        In order to ensure proper cleanup of resources, unlink should be
        called once (and only once) across all processes which have access
        to the shared memory block."""
        ikiwa _USE_POSIX na self._name:
            kutoka .resource_tracker agiza unregister
            _posixshmem.shm_unlink(self._name)
            unregister(self._name, "shared_memory")


_encoding = "utf8"

kundi ShareableList:
    """Pattern kila a mutable list-like object shareable via a shared
    memory block.  It differs kutoka the built-in list type kwenye that these
    lists can sio change their overall length (i.e. no append, insert,
    etc.)

    Because values are packed into a memoryview kama bytes, the struct
    packing format kila any storable value must require no more than 8
    characters to describe its format."""

    _types_mapping = {
        int: "q",
        float: "d",
        bool: "xxxxxxx?",
        str: "%ds",
        bytes: "%ds",
        Tupu.__class__: "xxxxxx?x",
    }
    _alignment = 8
    _back_transforms_mapping = {
        0: lambda value: value,                   # int, float, bool
        1: lambda value: value.rstrip(b'\x00').decode(_encoding),  # str
        2: lambda value: value.rstrip(b'\x00'),   # bytes
        3: lambda _value: Tupu,                   # Tupu
    }

    @staticmethod
    eleza _extract_recreation_code(value):
        """Used kwenye concert with _back_transforms_mapping to convert values
        into the appropriate Python objects when retrieving them kutoka
        the list kama well kama when storing them."""
        ikiwa sio isinstance(value, (str, bytes, Tupu.__class__)):
            rudisha 0
        elikiwa isinstance(value, str):
            rudisha 1
        elikiwa isinstance(value, bytes):
            rudisha 2
        isipokua:
            rudisha 3  # TupuType

    eleza __init__(self, sequence=Tupu, *, name=Tupu):
        ikiwa sequence ni sio Tupu:
            _formats = [
                self._types_mapping[type(item)]
                    ikiwa sio isinstance(item, (str, bytes))
                    else self._types_mapping[type(item)] % (
                        self._alignment * (len(item) // self._alignment + 1),
                    )
                kila item kwenye sequence
            ]
            self._list_len = len(_formats)
            assert sum(len(fmt) <= 8 kila fmt kwenye _formats) == self._list_len
            self._allocated_bytes = tuple(
                    self._alignment ikiwa fmt[-1] != "s" else int(fmt[:-1])
                    kila fmt kwenye _formats
            )
            _recreation_codes = [
                self._extract_recreation_code(item) kila item kwenye sequence
            ]
            requested_size = struct.calcsize(
                "q" + self._format_size_metainfo +
                "".join(_formats) +
                self._format_packing_metainfo +
                self._format_back_transform_codes
            )

        isipokua:
            requested_size = 8  # Some platforms require > 0.

        ikiwa name ni sio Tupu na sequence ni Tupu:
            self.shm = SharedMemory(name)
        isipokua:
            self.shm = SharedMemory(name, create=Kweli, size=requested_size)

        ikiwa sequence ni sio Tupu:
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
                *(v.encode(_enc) ikiwa isinstance(v, str) else v kila v kwenye sequence)
            )
            struct.pack_into(
                self._format_packing_metainfo,
                self.shm.buf,
                self._offset_packing_formats,
                *(v.encode(_enc) kila v kwenye _formats)
            )
            struct.pack_into(
                self._format_back_transform_codes,
                self.shm.buf,
                self._offset_back_transform_codes,
                *(_recreation_codes)
            )

        isipokua:
            self._list_len = len(self)  # Obtains size kutoka offset 0 kwenye buffer.
            self._allocated_bytes = struct.unpack_kutoka(
                self._format_size_metainfo,
                self.shm.buf,
                1 * 8
            )

    eleza _get_packing_format(self, position):
        "Gets the packing format kila a single value stored kwenye the list."
        position = position ikiwa position >= 0 else position + self._list_len
        ikiwa (position >= self._list_len) ama (self._list_len < 0):
            ashiria IndexError("Requested position out of range.")

        v = struct.unpack_kutoka(
            "8s",
            self.shm.buf,
            self._offset_packing_formats + position * 8
        )[0]
        fmt = v.rstrip(b'\x00')
        fmt_as_str = fmt.decode(_encoding)

        rudisha fmt_as_str

    eleza _get_back_transform(self, position):
        "Gets the back transformation function kila a single value."

        position = position ikiwa position >= 0 else position + self._list_len
        ikiwa (position >= self._list_len) ama (self._list_len < 0):
            ashiria IndexError("Requested position out of range.")

        transform_code = struct.unpack_kutoka(
            "b",
            self.shm.buf,
            self._offset_back_transform_codes + position
        )[0]
        transform_function = self._back_transforms_mapping[transform_code]

        rudisha transform_function

    eleza _set_packing_format_and_transform(self, position, fmt_as_str, value):
        """Sets the packing format na back transformation code kila a
        single value kwenye the list at the specified position."""

        position = position ikiwa position >= 0 else position + self._list_len
        ikiwa (position >= self._list_len) ama (self._list_len < 0):
            ashiria IndexError("Requested position out of range.")

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
        jaribu:
            offset = self._offset_data_start \
                     + sum(self._allocated_bytes[:position])
            (v,) = struct.unpack_kutoka(
                self._get_packing_format(position),
                self.shm.buf,
                offset
            )
        tatizo IndexError:
            ashiria IndexError("index out of range")

        back_transform = self._get_back_transform(position)
        v = back_transform(v)

        rudisha v

    eleza __setitem__(self, position, value):
        jaribu:
            offset = self._offset_data_start \
                     + sum(self._allocated_bytes[:position])
            current_format = self._get_packing_format(position)
        tatizo IndexError:
            ashiria IndexError("assignment index out of range")

        ikiwa sio isinstance(value, (str, bytes)):
            new_format = self._types_mapping[type(value)]
        isipokua:
            ikiwa len(value) > self._allocated_bytes[position]:
                ashiria ValueError("exceeds available storage kila existing str")
            ikiwa current_format[-1] == "s":
                new_format = current_format
            isipokua:
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
            self._get_packing_format(i) kila i kwenye range(self._list_len)
        )

    @property
    eleza _format_size_metainfo(self):
        "The struct packing format used kila metainfo on storage sizes."
        rudisha f"{self._list_len}q"

    @property
    eleza _format_packing_metainfo(self):
        "The struct packing format used kila the values' packing formats."
        rudisha "8s" * self._list_len

    @property
    eleza _format_back_transform_codes(self):
        "The struct packing format used kila the values' back transforms."
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

        rudisha sum(value == entry kila entry kwenye self)

    eleza index(self, value):
        """L.index(value) -> integer -- rudisha first index of value.
        Raises ValueError ikiwa the value ni sio present."""

        kila position, entry kwenye enumerate(self):
            ikiwa value == enjaribu:
                rudisha position
        isipokua:
            ashiria ValueError(f"{value!r} haiko kwenye this container")
