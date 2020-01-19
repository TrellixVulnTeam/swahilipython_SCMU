agiza sys
kutoka types agiza MappingProxyType, DynamicClassAttribute


__all__ = [
        'EnumMeta',
        'Enum', 'IntEnum', 'Flag', 'IntFlag',
        'auto', 'unique',
        ]


eleza _is_descriptor(obj):
    """Returns Kweli ikiwa obj ni a descriptor, Uongo otherwise."""
    rudisha (
            hasattr(obj, '__get__') ama
            hasattr(obj, '__set__') ama
            hasattr(obj, '__delete__'))


eleza _is_dunder(name):
    """Returns Kweli ikiwa a __dunder__ name, Uongo otherwise."""
    rudisha (len(name) > 4 na
            name[:2] == name[-2:] == '__' na
            name[2] != '_' na
            name[-3] != '_')


eleza _is_sunder(name):
    """Returns Kweli ikiwa a _sunder_ name, Uongo otherwise."""
    rudisha (len(name) > 2 na
            name[0] == name[-1] == '_' na
            name[1:2] != '_' na
            name[-2:-1] != '_')


eleza _make_class_unpicklable(cls):
    """Make the given kundi un-picklable."""
    eleza _koma_on_call_reduce(self, proto):
        ashiria TypeError('%r cannot be pickled' % self)
    cls.__reduce_ex__ = _koma_on_call_reduce
    cls.__module__ = '<unknown>'

_auto_null = object()
kundi auto:
    """
    Instances are replaced ukijumuisha an appropriate value kwenye Enum kundi suites.
    """
    value = _auto_null


kundi _EnumDict(dict):
    """Track enum member order na ensure member names are sio reused.

    EnumMeta will use the names found kwenye self._member_names kama the
    enumeration member names.

    """
    eleza __init__(self):
        super().__init__()
        self._member_names = []
        self._last_values = []
        self._ignore = []

    eleza __setitem__(self, key, value):
        """Changes anything sio dundered ama sio a descriptor.

        If an enum member name ni used twice, an error ni raised; duplicate
        values are sio checked for.

        Single underscore (sunder) names are reserved.

        """
        ikiwa _is_sunder(key):
            ikiwa key haiko kwenye (
                    '_order_', '_create_pseudo_member_',
                    '_generate_next_value_', '_missing_', '_ignore_',
                    ):
                ashiria ValueError('_names_ are reserved kila future Enum use')
            ikiwa key == '_generate_next_value_':
                setattr(self, '_generate_next_value', value)
            lasivyo key == '_ignore_':
                ikiwa isinstance(value, str):
                    value = value.replace(',',' ').split()
                isipokua:
                    value = list(value)
                self._ignore = value
                already = set(value) & set(self._member_names)
                ikiwa already:
                    ashiria ValueError('_ignore_ cannot specify already set names: %r' % (already, ))
        lasivyo _is_dunder(key):
            ikiwa key == '__order__':
                key = '_order_'
        lasivyo key kwenye self._member_names:
            # descriptor overwriting an enum?
            ashiria TypeError('Attempted to reuse key: %r' % key)
        lasivyo key kwenye self._ignore:
            pita
        lasivyo sio _is_descriptor(value):
            ikiwa key kwenye self:
                # enum overwriting a descriptor?
                ashiria TypeError('%r already defined as: %r' % (key, self[key]))
            ikiwa isinstance(value, auto):
                ikiwa value.value == _auto_null:
                    value.value = self._generate_next_value(key, 1, len(self._member_names), self._last_values[:])
                value = value.value
            self._member_names.append(key)
            self._last_values.append(value)
        super().__setitem__(key, value)


# Dummy value kila Enum kama EnumMeta explicitly checks kila it, but of course
# until EnumMeta finishes running the first time the Enum kundi doesn't exist.
# This ni also why there are checks kwenye EnumMeta like `ikiwa Enum ni sio Tupu`
Enum = Tupu


kundi EnumMeta(type):
    """Metakundi kila Enum"""
    @classmethod
    eleza __prepare__(metacls, cls, bases):
        # create the namespace dict
        enum_dict = _EnumDict()
        # inherit previous flags na _generate_next_value_ function
        member_type, first_enum = metacls._get_mixins_(bases)
        ikiwa first_enum ni sio Tupu:
            enum_dict['_generate_next_value_'] = getattr(first_enum, '_generate_next_value_', Tupu)
        rudisha enum_dict

    eleza __new__(metacls, cls, bases, classdict):
        # an Enum kundi ni final once enumeration items have been defined; it
        # cannot be mixed ukijumuisha other types (int, float, etc.) ikiwa it has an
        # inherited __new__ unless a new __new__ ni defined (or the resulting
        # kundi will fail).
        #
        # remove any keys listed kwenye _ignore_
        classdict.setdefault('_ignore_', []).append('_ignore_')
        ignore = classdict['_ignore_']
        kila key kwenye ignore:
            classdict.pop(key, Tupu)
        member_type, first_enum = metacls._get_mixins_(bases)
        __new__, save_new, use_args = metacls._find_new_(classdict, member_type,
                                                        first_enum)

        # save enum items into separate mapping so they don't get baked into
        # the new class
        enum_members = {k: classdict[k] kila k kwenye classdict._member_names}
        kila name kwenye classdict._member_names:
            toa classdict[name]

        # adjust the sunders
        _order_ = classdict.pop('_order_', Tupu)

        # check kila illegal enum names (any others?)
        invalid_names = set(enum_members) & {'mro', ''}
        ikiwa invalid_names:
            ashiria ValueError('Invalid enum member name: {0}'.format(
                ','.join(invalid_names)))

        # create a default docstring ikiwa one has sio been provided
        ikiwa '__doc__' haiko kwenye classdict:
            classdict['__doc__'] = 'An enumeration.'

        # create our new Enum type
        enum_class = super().__new__(metacls, cls, bases, classdict)
        enum_class._member_names_ = []               # names kwenye definition order
        enum_class._member_map_ = {}                 # name->value map
        enum_class._member_type_ = member_type

        # save DynamicClassAttribute attributes kutoka super classes so we know
        # ikiwa we can take the shortcut of storing members kwenye the kundi dict
        dynamic_attributes = {k kila c kwenye enum_class.mro()
                              kila k, v kwenye c.__dict__.items()
                              ikiwa isinstance(v, DynamicClassAttribute)}

        # Reverse value->name map kila hashable values.
        enum_class._value2member_map_ = {}

        # If a custom type ni mixed into the Enum, na it does sio know how
        # to pickle itself, pickle.dumps will succeed but pickle.loads will
        # fail.  Rather than have the error show up later na possibly far
        # kutoka the source, sabotage the pickle protocol kila this kundi so
        # that pickle.dumps also fails.
        #
        # However, ikiwa the new kundi implements its own __reduce_ex__, do sio
        # sabotage -- it's on them to make sure it works correctly.  We use
        # __reduce_ex__ instead of any of the others kama it ni preferred by
        # pickle over __reduce__, na it handles all pickle protocols.
        ikiwa '__reduce_ex__' haiko kwenye classdict:
            ikiwa member_type ni sio object:
                methods = ('__getnewargs_ex__', '__getnewargs__',
                        '__reduce_ex__', '__reduce__')
                ikiwa sio any(m kwenye member_type.__dict__ kila m kwenye methods):
                    _make_class_unpicklable(enum_class)

        # instantiate them, checking kila duplicates kama we go
        # we instantiate first instead of checking kila duplicates first kwenye case
        # a custom __new__ ni doing something funky ukijumuisha the values -- such as
        # auto-numbering ;)
        kila member_name kwenye classdict._member_names:
            value = enum_members[member_name]
            ikiwa sio isinstance(value, tuple):
                args = (value, )
            isipokua:
                args = value
            ikiwa member_type ni tuple:   # special case kila tuple enums
                args = (args, )     # wrap it one more time
            ikiwa sio use_args:
                enum_member = __new__(enum_class)
                ikiwa sio hasattr(enum_member, '_value_'):
                    enum_member._value_ = value
            isipokua:
                enum_member = __new__(enum_class, *args)
                ikiwa sio hasattr(enum_member, '_value_'):
                    ikiwa member_type ni object:
                        enum_member._value_ = value
                    isipokua:
                        enum_member._value_ = member_type(*args)
            value = enum_member._value_
            enum_member._name_ = member_name
            enum_member.__objclass__ = enum_class
            enum_member.__init__(*args)
            # If another member ukijumuisha the same value was already defined, the
            # new member becomes an alias to the existing one.
            kila name, canonical_member kwenye enum_class._member_map_.items():
                ikiwa canonical_member._value_ == enum_member._value_:
                    enum_member = canonical_member
                    koma
            isipokua:
                # Aliases don't appear kwenye member names (only kwenye __members__).
                enum_class._member_names_.append(member_name)
            # performance boost kila any member that would sio shadow
            # a DynamicClassAttribute
            ikiwa member_name haiko kwenye dynamic_attributes:
                setattr(enum_class, member_name, enum_member)
            # now add to _member_map_
            enum_class._member_map_[member_name] = enum_member
            jaribu:
                # This may fail ikiwa value ni sio hashable. We can't add the value
                # to the map, na by-value lookups kila this value will be
                # linear.
                enum_class._value2member_map_[value] = enum_member
            tatizo TypeError:
                pita

        # double check that repr na friends are sio the mixin's ama various
        # things koma (such kama pickle)
        kila name kwenye ('__repr__', '__str__', '__format__', '__reduce_ex__'):
            class_method = getattr(enum_class, name)
            obj_method = getattr(member_type, name, Tupu)
            enum_method = getattr(first_enum, name, Tupu)
            ikiwa obj_method ni sio Tupu na obj_method ni class_method:
                setattr(enum_class, name, enum_method)

        # replace any other __new__ ukijumuisha our own (as long kama Enum ni sio Tupu,
        # anyway) -- again, this ni to support pickle
        ikiwa Enum ni sio Tupu:
            # ikiwa the user defined their own __new__, save it before it gets
            # clobbered kwenye case they subkundi later
            ikiwa save_new:
                enum_class.__new_member__ = __new__
            enum_class.__new__ = Enum.__new__

        # py3 support kila definition order (helps keep py2/py3 code kwenye sync)
        ikiwa _order_ ni sio Tupu:
            ikiwa isinstance(_order_, str):
                _order_ = _order_.replace(',', ' ').split()
            ikiwa _order_ != enum_class._member_names_:
                ashiria TypeError('member order does sio match _order_')

        rudisha enum_class

    eleza __bool__(self):
        """
        classes/types should always be Kweli.
        """
        rudisha Kweli

    eleza __call__(cls, value, names=Tupu, *, module=Tupu, qualname=Tupu, type=Tupu, start=1):
        """Either returns an existing member, ama creates a new enum class.

        This method ni used both when an enum kundi ni given a value to match
        to an enumeration member (i.e. Color(3)) na kila the functional API
        (i.e. Color = Enum('Color', names='RED GREEN BLUE')).

        When used kila the functional API:

        `value` will be the name of the new class.

        `names` should be either a string of white-space/comma delimited names
        (values will start at `start`), ama an iterator/mapping of name, value pairs.

        `module` should be set to the module this kundi ni being created in;
        ikiwa it ni sio set, an attempt to find that module will be made, but if
        it fails the kundi will sio be picklable.

        `qualname` should be set to the actual location this kundi can be found
        at kwenye its module; by default it ni set to the global scope.  If this is
        sio correct, unpickling will fail kwenye some circumstances.

        `type`, ikiwa set, will be mixed kwenye kama the first base class.

        """
        ikiwa names ni Tupu:  # simple value lookup
            rudisha cls.__new__(cls, value)
        # otherwise, functional API: we're creating a new Enum type
        rudisha cls._create_(value, names, module=module, qualname=qualname, type=type, start=start)

    eleza __contains__(cls, member):
        ikiwa sio isinstance(member, Enum):
            ashiria TypeError(
                "unsupported operand type(s) kila 'in': '%s' na '%s'" % (
                    type(member).__qualname__, cls.__class__.__qualname__))
        rudisha isinstance(member, cls) na member._name_ kwenye cls._member_map_

    eleza __delattr__(cls, attr):
        # nicer error message when someone tries to delete an attribute
        # (see issue19025).
        ikiwa attr kwenye cls._member_map_:
            ashiria AttributeError(
                    "%s: cannot delete Enum member." % cls.__name__)
        super().__delattr__(attr)

    eleza __dir__(self):
        rudisha (['__class__', '__doc__', '__members__', '__module__'] +
                self._member_names_)

    eleza __getattr__(cls, name):
        """Return the enum member matching `name`

        We use __getattr__ instead of descriptors ama inserting into the enum
        class' __dict__ kwenye order to support `name` na `value` being both
        properties kila enum members (which live kwenye the class' __dict__) na
        enum members themselves.

        """
        ikiwa _is_dunder(name):
            ashiria AttributeError(name)
        jaribu:
            rudisha cls._member_map_[name]
        tatizo KeyError:
            ashiria AttributeError(name) kutoka Tupu

    eleza __getitem__(cls, name):
        rudisha cls._member_map_[name]

    eleza __iter__(cls):
        rudisha (cls._member_map_[name] kila name kwenye cls._member_names_)

    eleza __len__(cls):
        rudisha len(cls._member_names_)

    @property
    eleza __members__(cls):
        """Returns a mapping of member name->value.

        This mapping lists all enum members, including aliases. Note that this
        ni a read-only view of the internal mapping.

        """
        rudisha MappingProxyType(cls._member_map_)

    eleza __repr__(cls):
        rudisha "<enum %r>" % cls.__name__

    eleza __reversed__(cls):
        rudisha (cls._member_map_[name] kila name kwenye reversed(cls._member_names_))

    eleza __setattr__(cls, name, value):
        """Block attempts to reassign Enum members.

        A simple assignment to the kundi namespace only changes one of the
        several possible ways to get an Enum member kutoka the Enum class,
        resulting kwenye an inconsistent Enumeration.

        """
        member_map = cls.__dict__.get('_member_map_', {})
        ikiwa name kwenye member_map:
            ashiria AttributeError('Cannot reassign members.')
        super().__setattr__(name, value)

    eleza _create_(cls, class_name, names, *, module=Tupu, qualname=Tupu, type=Tupu, start=1):
        """Convenience method to create a new Enum class.

        `names` can be:

        * A string containing member names, separated either ukijumuisha spaces ama
          commas.  Values are incremented by 1 kutoka `start`.
        * An iterable of member names.  Values are incremented by 1 kutoka `start`.
        * An iterable of (member name, value) pairs.
        * A mapping of member name -> value pairs.

        """
        metacls = cls.__class__
        bases = (cls, ) ikiwa type ni Tupu isipokua (type, cls)
        _, first_enum = cls._get_mixins_(bases)
        classdict = metacls.__prepare__(class_name, bases)

        # special processing needed kila names?
        ikiwa isinstance(names, str):
            names = names.replace(',', ' ').split()
        ikiwa isinstance(names, (tuple, list)) na names na isinstance(names[0], str):
            original_names, names = names, []
            last_values = []
            kila count, name kwenye enumerate(original_names):
                value = first_enum._generate_next_value_(name, start, count, last_values[:])
                last_values.append(value)
                names.append((name, value))

        # Here, names ni either an iterable of (name, value) ama a mapping.
        kila item kwenye names:
            ikiwa isinstance(item, str):
                member_name, member_value = item, names[item]
            isipokua:
                member_name, member_value = item
            classdict[member_name] = member_value
        enum_class = metacls.__new__(metacls, class_name, bases, classdict)

        # TODO: replace the frame hack ikiwa a blessed way to know the calling
        # module ni ever developed
        ikiwa module ni Tupu:
            jaribu:
                module = sys._getframe(2).f_globals['__name__']
            tatizo (AttributeError, ValueError, KeyError) kama exc:
                pita
        ikiwa module ni Tupu:
            _make_class_unpicklable(enum_class)
        isipokua:
            enum_class.__module__ = module
        ikiwa qualname ni sio Tupu:
            enum_class.__qualname__ = qualname

        rudisha enum_class

    eleza _convert_(cls, name, module, filter, source=Tupu):
        """
        Create a new Enum subkundi that replaces a collection of global constants
        """
        # convert all constants kutoka source (or module) that pita filter() to
        # a new Enum called name, na export the enum na its members back to
        # module;
        # also, replace the __reduce_ex__ method so unpickling works kwenye
        # previous Python versions
        module_globals = vars(sys.modules[module])
        ikiwa source:
            source = vars(source)
        isipokua:
            source = module_globals
        # _value2member_map_ ni populated kwenye the same order every time
        # kila a consistent reverse mapping of number to name when there
        # are multiple names kila the same number.
        members = [
                (name, value)
                kila name, value kwenye source.items()
                ikiwa filter(name)]
        jaribu:
            # sort by value
            members.sort(key=lambda t: (t[1], t[0]))
        tatizo TypeError:
            # unless some values aren't comparable, kwenye which case sort by name
            members.sort(key=lambda t: t[0])
        cls = cls(name, members, module=module)
        cls.__reduce_ex__ = _reduce_ex_by_name
        module_globals.update(cls.__members__)
        module_globals[name] = cls
        rudisha cls

    eleza _convert(cls, *args, **kwargs):
        agiza warnings
        warnings.warn("_convert ni deprecated na will be removed kwenye 3.9, use "
                      "_convert_ instead.", DeprecationWarning, stacklevel=2)
        rudisha cls._convert_(*args, **kwargs)

    @staticmethod
    eleza _get_mixins_(bases):
        """Returns the type kila creating enum members, na the first inherited
        enum class.

        bases: the tuple of bases that was given to __new__

        """
        ikiwa sio bases:
            rudisha object, Enum

        eleza _find_data_type(bases):
            kila chain kwenye bases:
                kila base kwenye chain.__mro__:
                    ikiwa base ni object:
                        endelea
                    lasivyo '__new__' kwenye base.__dict__:
                        ikiwa issubclass(base, Enum):
                            endelea
                        rudisha base

        # ensure final parent kundi ni an Enum derivative, find any concrete
        # data type, na check that Enum has no members
        first_enum = bases[-1]
        ikiwa sio issubclass(first_enum, Enum):
            ashiria TypeError("new enumerations should be created kama "
                    "`EnumName([mixin_type, ...] [data_type,] enum_type)`")
        member_type = _find_data_type(bases) ama object
        ikiwa first_enum._member_names_:
            ashiria TypeError("Cannot extend enumerations")
        rudisha member_type, first_enum

    @staticmethod
    eleza _find_new_(classdict, member_type, first_enum):
        """Returns the __new__ to be used kila creating the enum members.

        classdict: the kundi dictionary given to __new__
        member_type: the data type whose __new__ will be used by default
        first_enum: enumeration to check kila an overriding __new__

        """
        # now find the correct __new__, checking to see of one was defined
        # by the user; also check earlier enum classes kwenye case a __new__ was
        # saved kama __new_member__
        __new__ = classdict.get('__new__', Tupu)

        # should __new__ be saved kama __new_member__ later?
        save_new = __new__ ni sio Tupu

        ikiwa __new__ ni Tupu:
            # check all possibles kila __new_member__ before falling back to
            # __new__
            kila method kwenye ('__new_member__', '__new__'):
                kila possible kwenye (member_type, first_enum):
                    target = getattr(possible, method, Tupu)
                    ikiwa target haiko kwenye {
                            Tupu,
                            Tupu.__new__,
                            object.__new__,
                            Enum.__new__,
                            }:
                        __new__ = target
                        koma
                ikiwa __new__ ni sio Tupu:
                    koma
            isipokua:
                __new__ = object.__new__

        # ikiwa a non-object.__new__ ni used then whatever value/tuple was
        # assigned to the enum member name will be pitaed to __new__ na to the
        # new enum member's __init__
        ikiwa __new__ ni object.__new__:
            use_args = Uongo
        isipokua:
            use_args = Kweli
        rudisha __new__, save_new, use_args


kundi Enum(metaclass=EnumMeta):
    """Generic enumeration.

    Derive kutoka this kundi to define new enumerations.

    """
    eleza __new__(cls, value):
        # all enum instances are actually created during kundi construction
        # without calling this method; this method ni called by the metaclass'
        # __call__ (i.e. Color(3) ), na by pickle
        ikiwa type(value) ni cls:
            # For lookups like Color(Color.RED)
            rudisha value
        # by-value search kila a matching enum member
        # see ikiwa it's kwenye the reverse mapping (kila hashable values)
        jaribu:
            rudisha cls._value2member_map_[value]
        tatizo KeyError:
            # Not found, no need to do long O(n) search
            pita
        tatizo TypeError:
            # sio there, now do long search -- O(n) behavior
            kila member kwenye cls._member_map_.values():
                ikiwa member._value_ == value:
                    rudisha member
        # still sio found -- try _missing_ hook
        jaribu:
            exc = Tupu
            result = cls._missing_(value)
        tatizo Exception kama e:
            exc = e
            result = Tupu
        ikiwa isinstance(result, cls):
            rudisha result
        isipokua:
            ve_exc = ValueError("%r ni sio a valid %s" % (value, cls.__name__))
            ikiwa result ni Tupu na exc ni Tupu:
                ashiria ve_exc
            lasivyo exc ni Tupu:
                exc = TypeError(
                        'error kwenye %s._missing_: returned %r instead of Tupu ama a valid member'
                        % (cls.__name__, result)
                        )
            exc.__context__ = ve_exc
            ashiria exc

    eleza _generate_next_value_(name, start, count, last_values):
        kila last_value kwenye reversed(last_values):
            jaribu:
                rudisha last_value + 1
            tatizo TypeError:
                pita
        isipokua:
            rudisha start

    @classmethod
    eleza _missing_(cls, value):
        ashiria ValueError("%r ni sio a valid %s" % (value, cls.__name__))

    eleza __repr__(self):
        rudisha "<%s.%s: %r>" % (
                self.__class__.__name__, self._name_, self._value_)

    eleza __str__(self):
        rudisha "%s.%s" % (self.__class__.__name__, self._name_)

    eleza __dir__(self):
        added_behavior = [
                m
                kila cls kwenye self.__class__.mro()
                kila m kwenye cls.__dict__
                ikiwa m[0] != '_' na m haiko kwenye self._member_map_
                ]
        rudisha (['__class__', '__doc__', '__module__'] + added_behavior)

    eleza __format__(self, format_spec):
        # mixed-in Enums should use the mixed-in type's __format__, otherwise
        # we can get strange results ukijumuisha the Enum name showing up instead of
        # the value

        # pure Enum branch
        ikiwa self._member_type_ ni object:
            cls = str
            val = str(self)
        # mix-in branch
        isipokua:
            cls = self._member_type_
            val = self._value_
        rudisha cls.__format__(val, format_spec)

    eleza __hash__(self):
        rudisha hash(self._name_)

    eleza __reduce_ex__(self, proto):
        rudisha self.__class__, (self._value_, )

    # DynamicClassAttribute ni used to provide access to the `name` na
    # `value` properties of enum members wakati keeping some measure of
    # protection kutoka modification, wakati still allowing kila an enumeration
    # to have members named `name` na `value`.  This works because enumeration
    # members are sio set directly on the enum kundi -- __getattr__ is
    # used to look them up.

    @DynamicClassAttribute
    eleza name(self):
        """The name of the Enum member."""
        rudisha self._name_

    @DynamicClassAttribute
    eleza value(self):
        """The value of the Enum member."""
        rudisha self._value_


kundi IntEnum(int, Enum):
    """Enum where members are also (and must be) ints"""


eleza _reduce_ex_by_name(self, proto):
    rudisha self.name

kundi Flag(Enum):
    """Support kila flags"""

    eleza _generate_next_value_(name, start, count, last_values):
        """
        Generate the next value when sio given.

        name: the name of the member
        start: the initial start value ama Tupu
        count: the number of existing members
        last_value: the last value assigned ama Tupu
        """
        ikiwa sio count:
            rudisha start ikiwa start ni sio Tupu isipokua 1
        kila last_value kwenye reversed(last_values):
            jaribu:
                high_bit = _high_bit(last_value)
                koma
            tatizo Exception:
                ashiria TypeError('Invalid Flag value: %r' % last_value) kutoka Tupu
        rudisha 2 ** (high_bit+1)

    @classmethod
    eleza _missing_(cls, value):
        original_value = value
        ikiwa value < 0:
            value = ~value
        possible_member = cls._create_pseudo_member_(value)
        ikiwa original_value < 0:
            possible_member = ~possible_member
        rudisha possible_member

    @classmethod
    eleza _create_pseudo_member_(cls, value):
        """
        Create a composite member iff value contains only members.
        """
        pseudo_member = cls._value2member_map_.get(value, Tupu)
        ikiwa pseudo_member ni Tupu:
            # verify all bits are accounted for
            _, extra_flags = _decompose(cls, value)
            ikiwa extra_flags:
                ashiria ValueError("%r ni sio a valid %s" % (value, cls.__name__))
            # construct a singleton enum pseudo-member
            pseudo_member = object.__new__(cls)
            pseudo_member._name_ = Tupu
            pseudo_member._value_ = value
            # use setdefault kwenye case another thread already created a composite
            # ukijumuisha this value
            pseudo_member = cls._value2member_map_.setdefault(value, pseudo_member)
        rudisha pseudo_member

    eleza __contains__(self, other):
        ikiwa sio isinstance(other, self.__class__):
            ashiria TypeError(
                "unsupported operand type(s) kila 'in': '%s' na '%s'" % (
                    type(other).__qualname__, self.__class__.__qualname__))
        rudisha other._value_ & self._value_ == other._value_

    eleza __repr__(self):
        cls = self.__class__
        ikiwa self._name_ ni sio Tupu:
            rudisha '<%s.%s: %r>' % (cls.__name__, self._name_, self._value_)
        members, uncovered = _decompose(cls, self._value_)
        rudisha '<%s.%s: %r>' % (
                cls.__name__,
                '|'.join([str(m._name_ ama m._value_) kila m kwenye members]),
                self._value_,
                )

    eleza __str__(self):
        cls = self.__class__
        ikiwa self._name_ ni sio Tupu:
            rudisha '%s.%s' % (cls.__name__, self._name_)
        members, uncovered = _decompose(cls, self._value_)
        ikiwa len(members) == 1 na members[0]._name_ ni Tupu:
            rudisha '%s.%r' % (cls.__name__, members[0]._value_)
        isipokua:
            rudisha '%s.%s' % (
                    cls.__name__,
                    '|'.join([str(m._name_ ama m._value_) kila m kwenye members]),
                    )

    eleza __bool__(self):
        rudisha bool(self._value_)

    eleza __or__(self, other):
        ikiwa sio isinstance(other, self.__class__):
            rudisha NotImplemented
        rudisha self.__class__(self._value_ | other._value_)

    eleza __and__(self, other):
        ikiwa sio isinstance(other, self.__class__):
            rudisha NotImplemented
        rudisha self.__class__(self._value_ & other._value_)

    eleza __xor__(self, other):
        ikiwa sio isinstance(other, self.__class__):
            rudisha NotImplemented
        rudisha self.__class__(self._value_ ^ other._value_)

    eleza __invert__(self):
        members, uncovered = _decompose(self.__class__, self._value_)
        inverted = self.__class__(0)
        kila m kwenye self.__class__:
            ikiwa m haiko kwenye members na sio (m._value_ & self._value_):
                inverted = inverted | m
        rudisha self.__class__(inverted)


kundi IntFlag(int, Flag):
    """Support kila integer-based Flags"""

    @classmethod
    eleza _missing_(cls, value):
        ikiwa sio isinstance(value, int):
            ashiria ValueError("%r ni sio a valid %s" % (value, cls.__name__))
        new_member = cls._create_pseudo_member_(value)
        rudisha new_member

    @classmethod
    eleza _create_pseudo_member_(cls, value):
        pseudo_member = cls._value2member_map_.get(value, Tupu)
        ikiwa pseudo_member ni Tupu:
            need_to_create = [value]
            # get unaccounted kila bits
            _, extra_flags = _decompose(cls, value)
            # timer = 10
            wakati extra_flags:
                # timer -= 1
                bit = _high_bit(extra_flags)
                flag_value = 2 ** bit
                ikiwa (flag_value haiko kwenye cls._value2member_map_ na
                        flag_value haiko kwenye need_to_create
                        ):
                    need_to_create.append(flag_value)
                ikiwa extra_flags == -flag_value:
                    extra_flags = 0
                isipokua:
                    extra_flags ^= flag_value
            kila value kwenye reversed(need_to_create):
                # construct singleton pseudo-members
                pseudo_member = int.__new__(cls, value)
                pseudo_member._name_ = Tupu
                pseudo_member._value_ = value
                # use setdefault kwenye case another thread already created a composite
                # ukijumuisha this value
                pseudo_member = cls._value2member_map_.setdefault(value, pseudo_member)
        rudisha pseudo_member

    eleza __or__(self, other):
        ikiwa sio isinstance(other, (self.__class__, int)):
            rudisha NotImplemented
        result = self.__class__(self._value_ | self.__class__(other)._value_)
        rudisha result

    eleza __and__(self, other):
        ikiwa sio isinstance(other, (self.__class__, int)):
            rudisha NotImplemented
        rudisha self.__class__(self._value_ & self.__class__(other)._value_)

    eleza __xor__(self, other):
        ikiwa sio isinstance(other, (self.__class__, int)):
            rudisha NotImplemented
        rudisha self.__class__(self._value_ ^ self.__class__(other)._value_)

    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__

    eleza __invert__(self):
        result = self.__class__(~self._value_)
        rudisha result


eleza _high_bit(value):
    """returns index of highest bit, ama -1 ikiwa value ni zero ama negative"""
    rudisha value.bit_length() - 1

eleza unique(enumeration):
    """Class decorator kila enumerations ensuring unique member values."""
    duplicates = []
    kila name, member kwenye enumeration.__members__.items():
        ikiwa name != member.name:
            duplicates.append((name, member.name))
    ikiwa duplicates:
        alias_details = ', '.join(
                ["%s -> %s" % (alias, name) kila (alias, name) kwenye duplicates])
        ashiria ValueError('duplicate values found kwenye %r: %s' %
                (enumeration, alias_details))
    rudisha enumeration

eleza _decompose(flag, value):
    """Extract all members kutoka the value."""
    # _decompose ni only called ikiwa the value ni sio named
    not_covered = value
    negative = value < 0
    # issue29167: wrap accesses to _value2member_map_ kwenye a list to avoid race
    #             conditions between iterating over it na having more pseudo-
    #             members added to it
    ikiwa negative:
        # only check kila named flags
        flags_to_check = [
                (m, v)
                kila v, m kwenye list(flag._value2member_map_.items())
                ikiwa m.name ni sio Tupu
                ]
    isipokua:
        # check kila named flags na powers-of-two flags
        flags_to_check = [
                (m, v)
                kila v, m kwenye list(flag._value2member_map_.items())
                ikiwa m.name ni sio Tupu ama _power_of_two(v)
                ]
    members = []
    kila member, member_value kwenye flags_to_check:
        ikiwa member_value na member_value & value == member_value:
            members.append(member)
            not_covered &= ~member_value
    ikiwa sio members na value kwenye flag._value2member_map_:
        members.append(flag._value2member_map_[value])
    members.sort(key=lambda m: m._value_, reverse=Kweli)
    ikiwa len(members) > 1 na members[0].value == value:
        # we have the komadown, don't need the value member itself
        members.pop(0)
    rudisha members, not_covered

eleza _power_of_two(value):
    ikiwa value < 1:
        rudisha Uongo
    rudisha value == 2 ** _high_bit(value)
