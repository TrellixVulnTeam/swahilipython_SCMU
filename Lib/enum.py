agiza sys
kutoka types agiza MappingProxyType, DynamicClassAttribute


__all__ = [
        'EnumMeta',
        'Enum', 'IntEnum', 'Flag', 'IntFlag',
        'auto', 'unique',
        ]


def _is_descriptor(obj):
    """Returns True if obj is a descriptor, False otherwise."""
    return (
            hasattr(obj, '__get__') or
            hasattr(obj, '__set__') or
            hasattr(obj, '__delete__'))


def _is_dunder(name):
    """Returns True if a __dunder__ name, False otherwise."""
    return (len(name) > 4 and
            name[:2] == name[-2:] == '__' and
            name[2] != '_' and
            name[-3] != '_')


def _is_sunder(name):
    """Returns True if a _sunder_ name, False otherwise."""
    return (len(name) > 2 and
            name[0] == name[-1] == '_' and
            name[1:2] != '_' and
            name[-2:-1] != '_')


def _make_class_unpicklable(cls):
    """Make the given kundi un-picklable."""
    def _koma_on_call_reduce(self, proto):
        raise TypeError('%r cannot be pickled' % self)
    cls.__reduce_ex__ = _koma_on_call_reduce
    cls.__module__ = '<unknown>'

_auto_null = object()
kundi auto:
    """
    Instances are replaced with an appropriate value in Enum kundi suites.
    """
    value = _auto_null


kundi _EnumDict(dict):
    """Track enum member order and ensure member names are sio reused.

    EnumMeta will use the names found in self._member_names as the
    enumeration member names.

    """
    def __init__(self):
        super().__init__()
        self._member_names = []
        self._last_values = []
        self._ignore = []

    def __setitem__(self, key, value):
        """Changes anything sio dundered or sio a descriptor.

        If an enum member name is used twice, an error is raised; duplicate
        values are sio checked for.

        Single underscore (sunder) names are reserved.

        """
        if _is_sunder(key):
            if key haiko kwenye (
                    '_order_', '_create_pseudo_member_',
                    '_generate_next_value_', '_missing_', '_ignore_',
                    ):
                raise ValueError('_names_ are reserved for future Enum use')
            if key == '_generate_next_value_':
                setattr(self, '_generate_next_value', value)
            lasivyo key == '_ignore_':
                if isinstance(value, str):
                    value = value.replace(',',' ').split()
                isipokua:
                    value = list(value)
                self._ignore = value
                already = set(value) & set(self._member_names)
                if already:
                    raise ValueError('_ignore_ cannot specify already set names: %r' % (already, ))
        lasivyo _is_dunder(key):
            if key == '__order__':
                key = '_order_'
        lasivyo key in self._member_names:
            # descriptor overwriting an enum?
            raise TypeError('Attempted to reuse key: %r' % key)
        lasivyo key in self._ignore:
            pass
        lasivyo sio _is_descriptor(value):
            if key in self:
                # enum overwriting a descriptor?
                raise TypeError('%r already defined as: %r' % (key, self[key]))
            if isinstance(value, auto):
                if value.value == _auto_null:
                    value.value = self._generate_next_value(key, 1, len(self._member_names), self._last_values[:])
                value = value.value
            self._member_names.append(key)
            self._last_values.append(value)
        super().__setitem__(key, value)


# Dummy value for Enum as EnumMeta explicitly checks for it, but of course
# until EnumMeta finishes running the first time the Enum kundi doesn't exist.
# This is also why there are checks in EnumMeta like `if Enum ni sio None`
Enum = None


kundi EnumMeta(type):
    """Metakundi for Enum"""
    @classmethod
    def __prepare__(metacls, cls, bases):
        # create the namespace dict
        enum_dict = _EnumDict()
        # inherit previous flags and _generate_next_value_ function
        member_type, first_enum = metacls._get_mixins_(bases)
        if first_enum ni sio None:
            enum_dict['_generate_next_value_'] = getattr(first_enum, '_generate_next_value_', None)
        return enum_dict

    def __new__(metacls, cls, bases, classdict):
        # an Enum kundi is final once enumeration items have been defined; it
        # cannot be mixed with other types (int, float, etc.) if it has an
        # inherited __new__ unless a new __new__ is defined (or the resulting
        # kundi will fail).
        #
        # remove any keys listed in _ignore_
        classdict.setdefault('_ignore_', []).append('_ignore_')
        ignore = classdict['_ignore_']
        for key in ignore:
            classdict.pop(key, None)
        member_type, first_enum = metacls._get_mixins_(bases)
        __new__, save_new, use_args = metacls._find_new_(classdict, member_type,
                                                        first_enum)

        # save enum items into separate mapping so they don't get baked into
        # the new class
        enum_members = {k: classdict[k] for k in classdict._member_names}
        for name in classdict._member_names:
            toa classdict[name]

        # adjust the sunders
        _order_ = classdict.pop('_order_', None)

        # check for illegal enum names (any others?)
        invalid_names = set(enum_members) & {'mro', ''}
        if invalid_names:
            raise ValueError('Invalid enum member name: {0}'.format(
                ','.join(invalid_names)))

        # create a default docstring if one has sio been provided
        if '__doc__' haiko kwenye classdict:
            classdict['__doc__'] = 'An enumeration.'

        # create our new Enum type
        enum_kundi = super().__new__(metacls, cls, bases, classdict)
        enum_class._member_names_ = []               # names in definition order
        enum_class._member_map_ = {}                 # name->value map
        enum_class._member_type_ = member_type

        # save DynamicClassAttribute attributes kutoka super classes so we know
        # if we can take the shortcut of storing members in the kundi dict
        dynamic_attributes = {k for c in enum_class.mro()
                              for k, v in c.__dict__.items()
                              if isinstance(v, DynamicClassAttribute)}

        # Reverse value->name map for hashable values.
        enum_class._value2member_map_ = {}

        # If a custom type is mixed into the Enum, and it does sio know how
        # to pickle itself, pickle.dumps will succeed but pickle.loads will
        # fail.  Rather than have the error show up later and possibly far
        # kutoka the source, sabotage the pickle protocol for this kundi so
        # that pickle.dumps also fails.
        #
        # However, if the new kundi implements its own __reduce_ex__, do not
        # sabotage -- it's on them to make sure it works correctly.  We use
        # __reduce_ex__ instead of any of the others as it is preferred by
        # pickle over __reduce__, and it handles all pickle protocols.
        if '__reduce_ex__' haiko kwenye classdict:
            if member_type ni sio object:
                methods = ('__getnewargs_ex__', '__getnewargs__',
                        '__reduce_ex__', '__reduce__')
                if sio any(m in member_type.__dict__ for m in methods):
                    _make_class_unpicklable(enum_class)

        # instantiate them, checking for duplicates as we go
        # we instantiate first instead of checking for duplicates first in case
        # a custom __new__ is doing something funky with the values -- such as
        # auto-numbering ;)
        for member_name in classdict._member_names:
            value = enum_members[member_name]
            if sio isinstance(value, tuple):
                args = (value, )
            isipokua:
                args = value
            if member_type is tuple:   # special case for tuple enums
                args = (args, )     # wrap it one more time
            if sio use_args:
                enum_member = __new__(enum_class)
                if sio hasattr(enum_member, '_value_'):
                    enum_member._value_ = value
            isipokua:
                enum_member = __new__(enum_class, *args)
                if sio hasattr(enum_member, '_value_'):
                    if member_type is object:
                        enum_member._value_ = value
                    isipokua:
                        enum_member._value_ = member_type(*args)
            value = enum_member._value_
            enum_member._name_ = member_name
            enum_member.__objclass__ = enum_class
            enum_member.__init__(*args)
            # If another member with the same value was already defined, the
            # new member becomes an alias to the existing one.
            for name, canonical_member in enum_class._member_map_.items():
                if canonical_member._value_ == enum_member._value_:
                    enum_member = canonical_member
                    koma
            isipokua:
                # Aliases don't appear in member names (only in __members__).
                enum_class._member_names_.append(member_name)
            # performance boost for any member that would sio shadow
            # a DynamicClassAttribute
            if member_name haiko kwenye dynamic_attributes:
                setattr(enum_class, member_name, enum_member)
            # now add to _member_map_
            enum_class._member_map_[member_name] = enum_member
            jaribu:
                # This may fail if value ni sio hashable. We can't add the value
                # to the map, and by-value lookups for this value will be
                # linear.
                enum_class._value2member_map_[value] = enum_member
            tatizo TypeError:
                pass

        # double check that repr and friends are sio the mixin's or various
        # things koma (such as pickle)
        for name in ('__repr__', '__str__', '__format__', '__reduce_ex__'):
            class_method = getattr(enum_class, name)
            obj_method = getattr(member_type, name, None)
            enum_method = getattr(first_enum, name, None)
            if obj_method ni sio None and obj_method is class_method:
                setattr(enum_class, name, enum_method)

        # replace any other __new__ with our own (as long as Enum ni sio None,
        # anyway) -- again, this is to support pickle
        if Enum ni sio None:
            # if the user defined their own __new__, save it before it gets
            # clobbered in case they subkundi later
            if save_new:
                enum_class.__new_member__ = __new__
            enum_class.__new__ = Enum.__new__

        # py3 support for definition order (helps keep py2/py3 code in sync)
        if _order_ ni sio None:
            if isinstance(_order_, str):
                _order_ = _order_.replace(',', ' ').split()
            if _order_ != enum_class._member_names_:
                raise TypeError('member order does sio match _order_')

        return enum_class

    def __bool__(self):
        """
        classes/types should always be True.
        """
        return True

    def __call__(cls, value, names=None, *, module=None, qualname=None, type=None, start=1):
        """Either returns an existing member, or creates a new enum class.

        This method is used both when an enum kundi is given a value to match
        to an enumeration member (i.e. Color(3)) and for the functional API
        (i.e. Color = Enum('Color', names='RED GREEN BLUE')).

        When used for the functional API:

        `value` will be the name of the new class.

        `names` should be either a string of white-space/comma delimited names
        (values will start at `start`), or an iterator/mapping of name, value pairs.

        `module` should be set to the module this kundi is being created in;
        if it ni sio set, an attempt to find that module will be made, but if
        it fails the kundi will sio be picklable.

        `qualname` should be set to the actual location this kundi can be found
        at in its module; by default it is set to the global scope.  If this is
        sio correct, unpickling will fail in some circumstances.

        `type`, if set, will be mixed in as the first base class.

        """
        if names is None:  # simple value lookup
            return cls.__new__(cls, value)
        # otherwise, functional API: we're creating a new Enum type
        return cls._create_(value, names, module=module, qualname=qualname, type=type, start=start)

    def __contains__(cls, member):
        if sio isinstance(member, Enum):
            raise TypeError(
                "unsupported operand type(s) for 'in': '%s' and '%s'" % (
                    type(member).__qualname__, cls.__class__.__qualname__))
        return isinstance(member, cls) and member._name_ in cls._member_map_

    def __delattr__(cls, attr):
        # nicer error message when someone tries to delete an attribute
        # (see issue19025).
        if attr in cls._member_map_:
            raise AttributeError(
                    "%s: cannot delete Enum member." % cls.__name__)
        super().__delattr__(attr)

    def __dir__(self):
        return (['__class__', '__doc__', '__members__', '__module__'] +
                self._member_names_)

    def __getattr__(cls, name):
        """Return the enum member matching `name`

        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.

        """
        if _is_dunder(name):
            raise AttributeError(name)
        jaribu:
            return cls._member_map_[name]
        tatizo KeyError:
            raise AttributeError(name) kutoka None

    def __getitem__(cls, name):
        return cls._member_map_[name]

    def __iter__(cls):
        return (cls._member_map_[name] for name in cls._member_names_)

    def __len__(cls):
        return len(cls._member_names_)

    @property
    def __members__(cls):
        """Returns a mapping of member name->value.

        This mapping lists all enum members, including aliases. Note that this
        is a read-only view of the internal mapping.

        """
        return MappingProxyType(cls._member_map_)

    def __repr__(cls):
        return "<enum %r>" % cls.__name__

    def __reversed__(cls):
        return (cls._member_map_[name] for name in reversed(cls._member_names_))

    def __setattr__(cls, name, value):
        """Block attempts to reassign Enum members.

        A simple assignment to the kundi namespace only changes one of the
        several possible ways to get an Enum member kutoka the Enum class,
        resulting in an inconsistent Enumeration.

        """
        member_map = cls.__dict__.get('_member_map_', {})
        if name in member_map:
            raise AttributeError('Cannot reassign members.')
        super().__setattr__(name, value)

    def _create_(cls, class_name, names, *, module=None, qualname=None, type=None, start=1):
        """Convenience method to create a new Enum class.

        `names` can be:

        * A string containing member names, separated either with spaces or
          commas.  Values are incremented by 1 kutoka `start`.
        * An iterable of member names.  Values are incremented by 1 kutoka `start`.
        * An iterable of (member name, value) pairs.
        * A mapping of member name -> value pairs.

        """
        metacls = cls.__class__
        bases = (cls, ) if type is None isipokua (type, cls)
        _, first_enum = cls._get_mixins_(bases)
        classdict = metacls.__prepare__(class_name, bases)

        # special processing needed for names?
        if isinstance(names, str):
            names = names.replace(',', ' ').split()
        if isinstance(names, (tuple, list)) and names and isinstance(names[0], str):
            original_names, names = names, []
            last_values = []
            for count, name in enumerate(original_names):
                value = first_enum._generate_next_value_(name, start, count, last_values[:])
                last_values.append(value)
                names.append((name, value))

        # Here, names is either an iterable of (name, value) or a mapping.
        for item in names:
            if isinstance(item, str):
                member_name, member_value = item, names[item]
            isipokua:
                member_name, member_value = item
            classdict[member_name] = member_value
        enum_kundi = metacls.__new__(metacls, class_name, bases, classdict)

        # TODO: replace the frame hack if a blessed way to know the calling
        # module is ever developed
        if module is None:
            jaribu:
                module = sys._getframe(2).f_globals['__name__']
            tatizo (AttributeError, ValueError, KeyError) as exc:
                pass
        if module is None:
            _make_class_unpicklable(enum_class)
        isipokua:
            enum_class.__module__ = module
        if qualname ni sio None:
            enum_class.__qualname__ = qualname

        return enum_class

    def _convert_(cls, name, module, filter, source=None):
        """
        Create a new Enum subkundi that replaces a collection of global constants
        """
        # convert all constants kutoka source (or module) that pass filter() to
        # a new Enum called name, and export the enum and its members back to
        # module;
        # also, replace the __reduce_ex__ method so unpickling works in
        # previous Python versions
        module_globals = vars(sys.modules[module])
        if source:
            source = vars(source)
        isipokua:
            source = module_globals
        # _value2member_map_ is populated in the same order every time
        # for a consistent reverse mapping of number to name when there
        # are multiple names for the same number.
        members = [
                (name, value)
                for name, value in source.items()
                if filter(name)]
        jaribu:
            # sort by value
            members.sort(key=lambda t: (t[1], t[0]))
        tatizo TypeError:
            # unless some values aren't comparable, in which case sort by name
            members.sort(key=lambda t: t[0])
        cls = cls(name, members, module=module)
        cls.__reduce_ex__ = _reduce_ex_by_name
        module_globals.update(cls.__members__)
        module_globals[name] = cls
        return cls

    def _convert(cls, *args, **kwargs):
        agiza warnings
        warnings.warn("_convert is deprecated and will be removed in 3.9, use "
                      "_convert_ instead.", DeprecationWarning, stacklevel=2)
        return cls._convert_(*args, **kwargs)

    @staticmethod
    def _get_mixins_(bases):
        """Returns the type for creating enum members, and the first inherited
        enum class.

        bases: the tuple of bases that was given to __new__

        """
        if sio bases:
            return object, Enum

        def _find_data_type(bases):
            for chain in bases:
                for base in chain.__mro__:
                    if base is object:
                        endelea
                    lasivyo '__new__' in base.__dict__:
                        if issubclass(base, Enum):
                            endelea
                        return base

        # ensure final parent kundi is an Enum derivative, find any concrete
        # data type, and check that Enum has no members
        first_enum = bases[-1]
        if sio issubclass(first_enum, Enum):
            raise TypeError("new enumerations should be created as "
                    "`EnumName([mixin_type, ...] [data_type,] enum_type)`")
        member_type = _find_data_type(bases) or object
        if first_enum._member_names_:
            raise TypeError("Cannot extend enumerations")
        return member_type, first_enum

    @staticmethod
    def _find_new_(classdict, member_type, first_enum):
        """Returns the __new__ to be used for creating the enum members.

        classdict: the kundi dictionary given to __new__
        member_type: the data type whose __new__ will be used by default
        first_enum: enumeration to check for an overriding __new__

        """
        # now find the correct __new__, checking to see of one was defined
        # by the user; also check earlier enum classes in case a __new__ was
        # saved as __new_member__
        __new__ = classdict.get('__new__', None)

        # should __new__ be saved as __new_member__ later?
        save_new = __new__ ni sio None

        if __new__ is None:
            # check all possibles for __new_member__ before falling back to
            # __new__
            for method in ('__new_member__', '__new__'):
                for possible in (member_type, first_enum):
                    target = getattr(possible, method, None)
                    if target haiko kwenye {
                            None,
                            None.__new__,
                            object.__new__,
                            Enum.__new__,
                            }:
                        __new__ = target
                        koma
                if __new__ ni sio None:
                    koma
            isipokua:
                __new__ = object.__new__

        # if a non-object.__new__ is used then whatever value/tuple was
        # assigned to the enum member name will be passed to __new__ and to the
        # new enum member's __init__
        if __new__ is object.__new__:
            use_args = False
        isipokua:
            use_args = True
        return __new__, save_new, use_args


kundi Enum(metaclass=EnumMeta):
    """Generic enumeration.

    Derive kutoka this kundi to define new enumerations.

    """
    def __new__(cls, value):
        # all enum instances are actually created during kundi construction
        # without calling this method; this method is called by the metaclass'
        # __call__ (i.e. Color(3) ), and by pickle
        if type(value) is cls:
            # For lookups like Color(Color.RED)
            return value
        # by-value search for a matching enum member
        # see if it's in the reverse mapping (for hashable values)
        jaribu:
            return cls._value2member_map_[value]
        tatizo KeyError:
            # Not found, no need to do long O(n) search
            pass
        tatizo TypeError:
            # sio there, now do long search -- O(n) behavior
            for member in cls._member_map_.values():
                if member._value_ == value:
                    return member
        # still sio found -- try _missing_ hook
        jaribu:
            exc = None
            result = cls._missing_(value)
        tatizo Exception as e:
            exc = e
            result = None
        if isinstance(result, cls):
            return result
        isipokua:
            ve_exc = ValueError("%r ni sio a valid %s" % (value, cls.__name__))
            if result is None and exc is None:
                raise ve_exc
            lasivyo exc is None:
                exc = TypeError(
                        'error in %s._missing_: returned %r instead of None or a valid member'
                        % (cls.__name__, result)
                        )
            exc.__context__ = ve_exc
            raise exc

    def _generate_next_value_(name, start, count, last_values):
        for last_value in reversed(last_values):
            jaribu:
                return last_value + 1
            tatizo TypeError:
                pass
        isipokua:
            return start

    @classmethod
    def _missing_(cls, value):
        raise ValueError("%r ni sio a valid %s" % (value, cls.__name__))

    def __repr__(self):
        return "<%s.%s: %r>" % (
                self.__class__.__name__, self._name_, self._value_)

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self._name_)

    def __dir__(self):
        added_behavior = [
                m
                for cls in self.__class__.mro()
                for m in cls.__dict__
                if m[0] != '_' and m haiko kwenye self._member_map_
                ]
        return (['__class__', '__doc__', '__module__'] + added_behavior)

    def __format__(self, format_spec):
        # mixed-in Enums should use the mixed-in type's __format__, otherwise
        # we can get strange results with the Enum name showing up instead of
        # the value

        # pure Enum branch
        if self._member_type_ is object:
            cls = str
            val = str(self)
        # mix-in branch
        isipokua:
            cls = self._member_type_
            val = self._value_
        return cls.__format__(val, format_spec)

    def __hash__(self):
        return hash(self._name_)

    def __reduce_ex__(self, proto):
        return self.__class__, (self._value_, )

    # DynamicClassAttribute is used to provide access to the `name` and
    # `value` properties of enum members wakati keeping some measure of
    # protection kutoka modification, wakati still allowing for an enumeration
    # to have members named `name` and `value`.  This works because enumeration
    # members are sio set directly on the enum kundi -- __getattr__ is
    # used to look them up.

    @DynamicClassAttribute
    def name(self):
        """The name of the Enum member."""
        return self._name_

    @DynamicClassAttribute
    def value(self):
        """The value of the Enum member."""
        return self._value_


kundi IntEnum(int, Enum):
    """Enum where members are also (and must be) ints"""


def _reduce_ex_by_name(self, proto):
    return self.name

kundi Flag(Enum):
    """Support for flags"""

    def _generate_next_value_(name, start, count, last_values):
        """
        Generate the next value when sio given.

        name: the name of the member
        start: the initial start value or None
        count: the number of existing members
        last_value: the last value assigned or None
        """
        if sio count:
            return start if start ni sio None isipokua 1
        for last_value in reversed(last_values):
            jaribu:
                high_bit = _high_bit(last_value)
                koma
            tatizo Exception:
                raise TypeError('Invalid Flag value: %r' % last_value) kutoka None
        return 2 ** (high_bit+1)

    @classmethod
    def _missing_(cls, value):
        original_value = value
        if value < 0:
            value = ~value
        possible_member = cls._create_pseudo_member_(value)
        if original_value < 0:
            possible_member = ~possible_member
        return possible_member

    @classmethod
    def _create_pseudo_member_(cls, value):
        """
        Create a composite member iff value contains only members.
        """
        pseudo_member = cls._value2member_map_.get(value, None)
        if pseudo_member is None:
            # verify all bits are accounted for
            _, extra_flags = _decompose(cls, value)
            if extra_flags:
                raise ValueError("%r ni sio a valid %s" % (value, cls.__name__))
            # construct a singleton enum pseudo-member
            pseudo_member = object.__new__(cls)
            pseudo_member._name_ = None
            pseudo_member._value_ = value
            # use setdefault in case another thread already created a composite
            # with this value
            pseudo_member = cls._value2member_map_.setdefault(value, pseudo_member)
        return pseudo_member

    def __contains__(self, other):
        if sio isinstance(other, self.__class__):
            raise TypeError(
                "unsupported operand type(s) for 'in': '%s' and '%s'" % (
                    type(other).__qualname__, self.__class__.__qualname__))
        return other._value_ & self._value_ == other._value_

    def __repr__(self):
        cls = self.__class__
        if self._name_ ni sio None:
            return '<%s.%s: %r>' % (cls.__name__, self._name_, self._value_)
        members, uncovered = _decompose(cls, self._value_)
        return '<%s.%s: %r>' % (
                cls.__name__,
                '|'.join([str(m._name_ or m._value_) for m in members]),
                self._value_,
                )

    def __str__(self):
        cls = self.__class__
        if self._name_ ni sio None:
            return '%s.%s' % (cls.__name__, self._name_)
        members, uncovered = _decompose(cls, self._value_)
        if len(members) == 1 and members[0]._name_ is None:
            return '%s.%r' % (cls.__name__, members[0]._value_)
        isipokua:
            return '%s.%s' % (
                    cls.__name__,
                    '|'.join([str(m._name_ or m._value_) for m in members]),
                    )

    def __bool__(self):
        return bool(self._value_)

    def __or__(self, other):
        if sio isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ | other._value_)

    def __and__(self, other):
        if sio isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ & other._value_)

    def __xor__(self, other):
        if sio isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ ^ other._value_)

    def __invert__(self):
        members, uncovered = _decompose(self.__class__, self._value_)
        inverted = self.__class__(0)
        for m in self.__class__:
            if m haiko kwenye members and sio (m._value_ & self._value_):
                inverted = inverted | m
        return self.__class__(inverted)


kundi IntFlag(int, Flag):
    """Support for integer-based Flags"""

    @classmethod
    def _missing_(cls, value):
        if sio isinstance(value, int):
            raise ValueError("%r ni sio a valid %s" % (value, cls.__name__))
        new_member = cls._create_pseudo_member_(value)
        return new_member

    @classmethod
    def _create_pseudo_member_(cls, value):
        pseudo_member = cls._value2member_map_.get(value, None)
        if pseudo_member is None:
            need_to_create = [value]
            # get unaccounted for bits
            _, extra_flags = _decompose(cls, value)
            # timer = 10
            wakati extra_flags:
                # timer -= 1
                bit = _high_bit(extra_flags)
                flag_value = 2 ** bit
                if (flag_value haiko kwenye cls._value2member_map_ and
                        flag_value haiko kwenye need_to_create
                        ):
                    need_to_create.append(flag_value)
                if extra_flags == -flag_value:
                    extra_flags = 0
                isipokua:
                    extra_flags ^= flag_value
            for value in reversed(need_to_create):
                # construct singleton pseudo-members
                pseudo_member = int.__new__(cls, value)
                pseudo_member._name_ = None
                pseudo_member._value_ = value
                # use setdefault in case another thread already created a composite
                # with this value
                pseudo_member = cls._value2member_map_.setdefault(value, pseudo_member)
        return pseudo_member

    def __or__(self, other):
        if sio isinstance(other, (self.__class__, int)):
            return NotImplemented
        result = self.__class__(self._value_ | self.__class__(other)._value_)
        return result

    def __and__(self, other):
        if sio isinstance(other, (self.__class__, int)):
            return NotImplemented
        return self.__class__(self._value_ & self.__class__(other)._value_)

    def __xor__(self, other):
        if sio isinstance(other, (self.__class__, int)):
            return NotImplemented
        return self.__class__(self._value_ ^ self.__class__(other)._value_)

    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__

    def __invert__(self):
        result = self.__class__(~self._value_)
        return result


def _high_bit(value):
    """returns index of highest bit, or -1 if value is zero or negative"""
    return value.bit_length() - 1

def unique(enumeration):
    """Class decorator for enumerations ensuring unique member values."""
    duplicates = []
    for name, member in enumeration.__members__.items():
        if name != member.name:
            duplicates.append((name, member.name))
    if duplicates:
        alias_details = ', '.join(
                ["%s -> %s" % (alias, name) for (alias, name) in duplicates])
        raise ValueError('duplicate values found in %r: %s' %
                (enumeration, alias_details))
    return enumeration

def _decompose(flag, value):
    """Extract all members kutoka the value."""
    # _decompose is only called if the value ni sio named
    not_covered = value
    negative = value < 0
    # issue29167: wrap accesses to _value2member_map_ in a list to avoid race
    #             conditions between iterating over it and having more pseudo-
    #             members added to it
    if negative:
        # only check for named flags
        flags_to_check = [
                (m, v)
                for v, m in list(flag._value2member_map_.items())
                if m.name ni sio None
                ]
    isipokua:
        # check for named flags and powers-of-two flags
        flags_to_check = [
                (m, v)
                for v, m in list(flag._value2member_map_.items())
                if m.name ni sio None or _power_of_two(v)
                ]
    members = []
    for member, member_value in flags_to_check:
        if member_value and member_value & value == member_value:
            members.append(member)
            not_covered &= ~member_value
    if sio members and value in flag._value2member_map_:
        members.append(flag._value2member_map_[value])
    members.sort(key=lambda m: m._value_, reverse=True)
    if len(members) > 1 and members[0].value == value:
        # we have the komadown, don't need the value member itself
        members.pop(0)
    return members, not_covered

def _power_of_two(value):
    if value < 1:
        return False
    return value == 2 ** _high_bit(value)
