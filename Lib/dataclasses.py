agiza re
agiza sys
agiza copy
agiza types
agiza inspect
agiza keyword
agiza builtins
agiza functools
agiza _thread


__all__ = ['dataclass',
           'field',
           'Field',
           'FrozenInstanceError',
           'InitVar',
           'MISSING',

           # Helper functions.
           'fields',
           'asdict',
           'astuple',
           'make_dataclass',
           'replace',
           'is_dataclass',
           ]

# Conditions kila adding methods.  The boxes indicate what action the
# datakundi decorator takes.  For all of these tables, when I talk
# about init=, repr=, eq=, order=, unsafe_hash=, ama frozen=, I'm
# referring to the arguments to the @datakundi decorator.  When
# checking ikiwa a dunder method already exists, I mean check kila an
# entry kwenye the class's __dict__.  I never check to see ikiwa an attribute
# ni defined kwenye a base class.

# Key:
# +=========+=========================================+
# + Value   | Meaning                                 |
# +=========+=========================================+
# | <blank> | No action: no method ni added.          |
# +---------+-----------------------------------------+
# | add     | Generated method ni added.              |
# +---------+-----------------------------------------+
# | ashiria   | TypeError ni raised.                    |
# +---------+-----------------------------------------+
# | Tupu    | Attribute ni set to Tupu.               |
# +=========+=========================================+

# __init__
#
#   +--- init= parameter
#   |
#   v     |       |       |
#         |  no   |  yes  |  <--- kundi has __init__ kwenye __dict__?
# +=======+=======+=======+
# | Uongo |       |       |
# +-------+-------+-------+
# | Kweli  | add   |       |  <- the default
# +=======+=======+=======+

# __repr__
#
#    +--- repr= parameter
#    |
#    v    |       |       |
#         |  no   |  yes  |  <--- kundi has __repr__ kwenye __dict__?
# +=======+=======+=======+
# | Uongo |       |       |
# +-------+-------+-------+
# | Kweli  | add   |       |  <- the default
# +=======+=======+=======+


# __setattr__
# __delattr__
#
#    +--- frozen= parameter
#    |
#    v    |       |       |
#         |  no   |  yes  |  <--- kundi has __setattr__ ama __delattr__ kwenye __dict__?
# +=======+=======+=======+
# | Uongo |       |       |  <- the default
# +-------+-------+-------+
# | Kweli  | add   | ashiria |
# +=======+=======+=======+
# Raise because sio adding these methods would koma the "frozen-ness"
# of the class.

# __eq__
#
#    +--- eq= parameter
#    |
#    v    |       |       |
#         |  no   |  yes  |  <--- kundi has __eq__ kwenye __dict__?
# +=======+=======+=======+
# | Uongo |       |       |
# +-------+-------+-------+
# | Kweli  | add   |       |  <- the default
# +=======+=======+=======+

# __lt__
# __le__
# __gt__
# __ge__
#
#    +--- order= parameter
#    |
#    v    |       |       |
#         |  no   |  yes  |  <--- kundi has any comparison method kwenye __dict__?
# +=======+=======+=======+
# | Uongo |       |       |  <- the default
# +-------+-------+-------+
# | Kweli  | add   | ashiria |
# +=======+=======+=======+
# Raise because to allow this case would interfere ukijumuisha using
# functools.total_ordering.

# __hash__

#    +------------------- unsafe_hash= parameter
#    |       +----------- eq= parameter
#    |       |       +--- frozen= parameter
#    |       |       |
#    v       v       v    |        |        |
#                         |   no   |  yes   |  <--- kundi has explicitly defined __hash__
# +=======+=======+=======+========+========+
# | Uongo | Uongo | Uongo |        |        | No __eq__, use the base kundi __hash__
# +-------+-------+-------+--------+--------+
# | Uongo | Uongo | Kweli  |        |        | No __eq__, use the base kundi __hash__
# +-------+-------+-------+--------+--------+
# | Uongo | Kweli  | Uongo | Tupu   |        | <-- the default, sio hashable
# +-------+-------+-------+--------+--------+
# | Uongo | Kweli  | Kweli  | add    |        | Frozen, so hashable, allows override
# +-------+-------+-------+--------+--------+
# | Kweli  | Uongo | Uongo | add    | ashiria  | Has no __eq__, but hashable
# +-------+-------+-------+--------+--------+
# | Kweli  | Uongo | Kweli  | add    | ashiria  | Has no __eq__, but hashable
# +-------+-------+-------+--------+--------+
# | Kweli  | Kweli  | Uongo | add    | ashiria  | Not frozen, but hashable
# +-------+-------+-------+--------+--------+
# | Kweli  | Kweli  | Kweli  | add    | ashiria  | Frozen, so hashable
# +=======+=======+=======+========+========+
# For boxes that are blank, __hash__ ni untouched na therefore
# inherited kutoka the base class.  If the base ni object, then
# id-based hashing ni used.
#
# Note that a kundi may already have __hash__=Tupu ikiwa it specified an
# __eq__ method kwenye the kundi body (sio one that was created by
# @dataclass).
#
# See _hash_action (below) kila a coded version of this table.


# Raised when an attempt ni made to modify a frozen class.
kundi FrozenInstanceError(AttributeError): pita

# A sentinel object kila default values to signal that a default
# factory will be used.  This ni given a nice repr() which will appear
# kwenye the function signature of dataclasses' constructors.
kundi _HAS_DEFAULT_FACTORY_CLASS:
    eleza __repr__(self):
        rudisha '<factory>'
_HAS_DEFAULT_FACTORY = _HAS_DEFAULT_FACTORY_CLASS()

# A sentinel object to detect ikiwa a parameter ni supplied ama not.  Use
# a kundi to give it a better repr.
kundi _MISSING_TYPE:
    pita
MISSING = _MISSING_TYPE()

# Since most per-field metadata will be unused, create an empty
# read-only proxy that can be shared among all fields.
_EMPTY_METADATA = types.MappingProxyType({})

# Markers kila the various kinds of fields na pseudo-fields.
kundi _FIELD_BASE:
    eleza __init__(self, name):
        self.name = name
    eleza __repr__(self):
        rudisha self.name
_FIELD = _FIELD_BASE('_FIELD')
_FIELD_CLASSVAR = _FIELD_BASE('_FIELD_CLASSVAR')
_FIELD_INITVAR = _FIELD_BASE('_FIELD_INITVAR')

# The name of an attribute on the kundi where we store the Field
# objects.  Also used to check ikiwa a kundi ni a Data Class.
_FIELDS = '__dataclass_fields__'

# The name of an attribute on the kundi that stores the parameters to
# @dataclass.
_PARAMS = '__dataclass_params__'

# The name of the function, that ikiwa it exists, ni called at the end of
# __init__.
_POST_INIT_NAME = '__post_init__'

# String regex that string annotations kila ClassVar ama InitVar must match.
# Allows "identifier.identifier[" ama "identifier[".
# https://bugs.python.org/issue33453 kila details.
_MODULE_IDENTIFIER_RE = re.compile(r'^(?:\s*(\w+)\s*\.)?\s*(\w+)')

kundi _InitVarMeta(type):
    eleza __getitem__(self, params):
        rudisha InitVar(params)

kundi InitVar(metaclass=_InitVarMeta):
    __slots__ = ('type', )

    eleza __init__(self, type):
        self.type = type

    eleza __repr__(self):
        ikiwa isinstance(self.type, type):
            type_name = self.type.__name__
        isipokua:
            # typing objects, e.g. List[int]
            type_name = repr(self.type)
        rudisha f'dataclasses.InitVar[{type_name}]'


# Instances of Field are only ever created kutoka within this module,
# na only kutoka the field() function, although Field instances are
# exposed externally kama (conceptually) read-only objects.
#
# name na type are filled kwenye after the fact, haiko kwenye __init__.
# They're sio known at the time this kundi ni instantiated, but it's
# convenient ikiwa they're available later.
#
# When cls._FIELDS ni filled kwenye ukijumuisha a list of Field objects, the name
# na type fields will have been populated.
kundi Field:
    __slots__ = ('name',
                 'type',
                 'default',
                 'default_factory',
                 'repr',
                 'hash',
                 'init',
                 'compare',
                 'metadata',
                 '_field_type',  # Private: sio to be used by user code.
                 )

    eleza __init__(self, default, default_factory, init, repr, hash, compare,
                 metadata):
        self.name = Tupu
        self.type = Tupu
        self.default = default
        self.default_factory = default_factory
        self.init = init
        self.repr = repr
        self.hash = hash
        self.compare = compare
        self.metadata = (_EMPTY_METADATA
                         ikiwa metadata ni Tupu else
                         types.MappingProxyType(metadata))
        self._field_type = Tupu

    eleza __repr__(self):
        rudisha ('Field('
                f'name={self.name!r},'
                f'type={self.type!r},'
                f'default={self.default!r},'
                f'default_factory={self.default_factory!r},'
                f'init={self.init!r},'
                f'repr={self.repr!r},'
                f'hash={self.hash!r},'
                f'compare={self.compare!r},'
                f'metadata={self.metadata!r},'
                f'_field_type={self._field_type}'
                ')')

    # This ni used to support the PEP 487 __set_name__ protocol kwenye the
    # case where we're using a field that contains a descriptor kama a
    # default value.  For details on __set_name__, see
    # https://www.python.org/dev/peps/pep-0487/#implementation-details.
    #
    # Note that kwenye _process_class, this Field object ni overwritten
    # ukijumuisha the default value, so the end result ni a descriptor that
    # had __set_name__ called on it at the right time.
    eleza __set_name__(self, owner, name):
        func = getattr(type(self.default), '__set_name__', Tupu)
        ikiwa func:
            # There ni a __set_name__ method on the descriptor, call
            # it.
            func(self.default, owner, name)


kundi _DataclassParams:
    __slots__ = ('init',
                 'repr',
                 'eq',
                 'order',
                 'unsafe_hash',
                 'frozen',
                 )

    eleza __init__(self, init, repr, eq, order, unsafe_hash, frozen):
        self.init = init
        self.repr = repr
        self.eq = eq
        self.order = order
        self.unsafe_hash = unsafe_hash
        self.frozen = frozen

    eleza __repr__(self):
        rudisha ('_DataclassParams('
                f'init={self.init!r},'
                f'repr={self.repr!r},'
                f'eq={self.eq!r},'
                f'order={self.order!r},'
                f'unsafe_hash={self.unsafe_hash!r},'
                f'frozen={self.frozen!r}'
                ')')


# This function ni used instead of exposing Field creation directly,
# so that a type checker can be told (via overloads) that this ni a
# function whose type depends on its parameters.
eleza field(*, default=MISSING, default_factory=MISSING, init=Kweli, repr=Kweli,
          hash=Tupu, compare=Kweli, metadata=Tupu):
    """Return an object to identify datakundi fields.

    default ni the default value of the field.  default_factory ni a
    0-argument function called to initialize a field's value.  If init
    ni Kweli, the field will be a parameter to the class's __init__()
    function.  If repr ni Kweli, the field will be included kwenye the
    object's repr().  If hash ni Kweli, the field will be included in
    the object's hash().  If compare ni Kweli, the field will be used
    kwenye comparison functions.  metadata, ikiwa specified, must be a
    mapping which ni stored but sio otherwise examined by dataclass.

    It ni an error to specify both default na default_factory.
    """

    ikiwa default ni sio MISSING na default_factory ni sio MISSING:
        ashiria ValueError('cannot specify both default na default_factory')
    rudisha Field(default, default_factory, init, repr, hash, compare,
                 metadata)


eleza _tuple_str(obj_name, fields):
    # Return a string representing each field of obj_name kama a tuple
    # member.  So, ikiwa fields ni ['x', 'y'] na obj_name ni "self",
    # rudisha "(self.x,self.y)".

    # Special case kila the 0-tuple.
    ikiwa sio fields:
        rudisha '()'
    # Note the trailing comma, needed ikiwa this turns out to be a 1-tuple.
    rudisha f'({",".join([f"{obj_name}.{f.name}" kila f kwenye fields])},)'


# This function's logic ni copied kutoka "recursive_repr" function in
# reprlib module to avoid dependency.
eleza _recursive_repr(user_function):
    # Decorator to make a repr function rudisha "..." kila a recursive
    # call.
    repr_running = set()

    @functools.wraps(user_function)
    eleza wrapper(self):
        key = id(self), _thread.get_ident()
        ikiwa key kwenye repr_running:
            rudisha '...'
        repr_running.add(key)
        jaribu:
            result = user_function(self)
        mwishowe:
            repr_running.discard(key)
        rudisha result
    rudisha wrapper


eleza _create_fn(name, args, body, *, globals=Tupu, locals=Tupu,
               return_type=MISSING):
    # Note that we mutate locals when exec() ni called.  Caller
    # beware!  The only callers are internal to this module, so no
    # worries about external callers.
    ikiwa locals ni Tupu:
        locals = {}
    # __builtins__ may be the "builtins" module ama
    # the value of its "__dict__",
    # so make sure "__builtins__" ni the module.
    ikiwa globals ni sio Tupu na '__builtins__' haiko kwenye globals:
        globals['__builtins__'] = builtins
    return_annotation = ''
    ikiwa return_type ni sio MISSING:
        locals['_return_type'] = return_type
        return_annotation = '->_return_type'
    args = ','.join(args)
    body = '\n'.join(f' {b}' kila b kwenye body)

    # Compute the text of the entire function.
    txt = f'eleza {name}({args}){return_annotation}:\n{body}'

    exec(txt, globals, locals)
    rudisha locals[name]


eleza _field_assign(frozen, name, value, self_name):
    # If we're a frozen class, then assign to our fields kwenye __init__
    # via object.__setattr__.  Otherwise, just use a simple
    # assignment.
    #
    # self_name ni what "self" ni called kwenye this function: don't
    # hard-code "self", since that might be a field name.
    ikiwa frozen:
        rudisha f'__builtins__.object.__setattr__({self_name},{name!r},{value})'
    rudisha f'{self_name}.{name}={value}'


eleza _field_init(f, frozen, globals, self_name):
    # Return the text of the line kwenye the body of __init__ that will
    # initialize this field.

    default_name = f'_dflt_{f.name}'
    ikiwa f.default_factory ni sio MISSING:
        ikiwa f.init:
            # This field has a default factory.  If a parameter is
            # given, use it.  If not, call the factory.
            globals[default_name] = f.default_factory
            value = (f'{default_name}() '
                     f'ikiwa {f.name} ni _HAS_DEFAULT_FACTORY '
                     f'else {f.name}')
        isipokua:
            # This ni a field that's haiko kwenye the __init__ params, but
            # has a default factory function.  It needs to be
            # initialized here by calling the factory function,
            # because there's no other way to initialize it.

            # For a field initialized ukijumuisha a default=defaultvalue, the
            # kundi dict just has the default value
            # (cls.fieldname=defaultvalue).  But that won't work kila a
            # default factory, the factory must be called kwenye __init__
            # na we must assign that to self.fieldname.  We can't
            # fall back to the kundi dict's value, both because it's
            # sio set, na because it might be different per-class
            # (which, after all, ni why we have a factory function!).

            globals[default_name] = f.default_factory
            value = f'{default_name}()'
    isipokua:
        # No default factory.
        ikiwa f.init:
            ikiwa f.default ni MISSING:
                # There's no default, just do an assignment.
                value = f.name
            lasivyo f.default ni sio MISSING:
                globals[default_name] = f.default
                value = f.name
        isipokua:
            # This field does sio need initialization.  Signify that
            # to the caller by returning Tupu.
            rudisha Tupu

    # Only test this now, so that we can create variables kila the
    # default.  However, rudisha Tupu to signify that we're sio going
    # to actually do the assignment statement kila InitVars.
    ikiwa f._field_type ni _FIELD_INITVAR:
        rudisha Tupu

    # Now, actually generate the field assignment.
    rudisha _field_assign(frozen, f.name, value, self_name)


eleza _init_param(f):
    # Return the __init__ parameter string kila this field.  For
    # example, the equivalent of 'x:int=3' (tatizo instead of 'int',
    # reference a variable set to int, na instead of '3', reference a
    # variable set to 3).
    ikiwa f.default ni MISSING na f.default_factory ni MISSING:
        # There's no default, na no default_factory, just output the
        # variable name na type.
        default = ''
    lasivyo f.default ni sio MISSING:
        # There's a default, this will be the name that's used to look
        # it up.
        default = f'=_dflt_{f.name}'
    lasivyo f.default_factory ni sio MISSING:
        # There's a factory function.  Set a marker.
        default = '=_HAS_DEFAULT_FACTORY'
    rudisha f'{f.name}:_type_{f.name}{default}'


eleza _init_fn(fields, frozen, has_post_init, self_name):
    # fields contains both real fields na InitVar pseudo-fields.

    # Make sure we don't have fields without defaults following fields
    # ukijumuisha defaults.  This actually would be caught when exec-ing the
    # function source code, but catching it here gives a better error
    # message, na future-proofs us kwenye case we build up the function
    # using ast.
    seen_default = Uongo
    kila f kwenye fields:
        # Only consider fields kwenye the __init__ call.
        ikiwa f.init:
            ikiwa sio (f.default ni MISSING na f.default_factory ni MISSING):
                seen_default = Kweli
            lasivyo seen_default:
                ashiria TypeError(f'non-default argument {f.name!r} '
                                'follows default argument')

    globals = {'MISSING': MISSING,
               '_HAS_DEFAULT_FACTORY': _HAS_DEFAULT_FACTORY}

    body_lines = []
    kila f kwenye fields:
        line = _field_init(f, frozen, globals, self_name)
        # line ni Tupu means that this field doesn't require
        # initialization (it's a pseudo-field).  Just skip it.
        ikiwa line:
            body_lines.append(line)

    # Does this kundi have a post-init function?
    ikiwa has_post_init:
        params_str = ','.join(f.name kila f kwenye fields
                              ikiwa f._field_type ni _FIELD_INITVAR)
        body_lines.append(f'{self_name}.{_POST_INIT_NAME}({params_str})')

    # If no body lines, use 'pita'.
    ikiwa sio body_lines:
        body_lines = ['pita']

    locals = {f'_type_{f.name}': f.type kila f kwenye fields}
    rudisha _create_fn('__init__',
                      [self_name] + [_init_param(f) kila f kwenye fields ikiwa f.init],
                      body_lines,
                      locals=locals,
                      globals=globals,
                      return_type=Tupu)


eleza _repr_fn(fields):
    fn = _create_fn('__repr__',
                    ('self',),
                    ['rudisha self.__class__.__qualname__ + f"(' +
                     ', '.join([f"{f.name}={{self.{f.name}!r}}"
                                kila f kwenye fields]) +
                     ')"'])
    rudisha _recursive_repr(fn)


eleza _frozen_get_del_attr(cls, fields):
    # XXX: globals ni modified on the first call to _create_fn, then
    # the modified version ni used kwenye the second call.  Is this okay?
    globals = {'cls': cls,
              'FrozenInstanceError': FrozenInstanceError}
    ikiwa fields:
        fields_str = '(' + ','.join(repr(f.name) kila f kwenye fields) + ',)'
    isipokua:
        # Special case kila the zero-length tuple.
        fields_str = '()'
    rudisha (_create_fn('__setattr__',
                      ('self', 'name', 'value'),
                      (f'ikiwa type(self) ni cls ama name kwenye {fields_str}:',
                        ' ashiria FrozenInstanceError(f"cannot assign to field {name!r}")',
                       f'super(cls, self).__setattr__(name, value)'),
                       globals=globals),
            _create_fn('__delattr__',
                      ('self', 'name'),
                      (f'ikiwa type(self) ni cls ama name kwenye {fields_str}:',
                        ' ashiria FrozenInstanceError(f"cannot delete field {name!r}")',
                       f'super(cls, self).__delattr__(name)'),
                       globals=globals),
            )


eleza _cmp_fn(name, op, self_tuple, other_tuple):
    # Create a comparison function.  If the fields kwenye the object are
    # named 'x' na 'y', then self_tuple ni the string
    # '(self.x,self.y)' na other_tuple ni the string
    # '(other.x,other.y)'.

    rudisha _create_fn(name,
                      ('self', 'other'),
                      [ 'ikiwa other.__class__ ni self.__class__:',
                       f' rudisha {self_tuple}{op}{other_tuple}',
                        'rudisha NotImplemented'])


eleza _hash_fn(fields):
    self_tuple = _tuple_str('self', fields)
    rudisha _create_fn('__hash__',
                      ('self',),
                      [f'rudisha hash({self_tuple})'])


eleza _is_classvar(a_type, typing):
    # This test uses a typing internal class, but it's the best way to
    # test ikiwa this ni a ClassVar.
    rudisha (a_type ni typing.ClassVar
            ama (type(a_type) ni typing._GenericAlias
                na a_type.__origin__ ni typing.ClassVar))


eleza _is_initvar(a_type, dataclasses):
    # The module we're checking against ni the module we're
    # currently kwenye (dataclasses.py).
    rudisha (a_type ni dataclasses.InitVar
            ama type(a_type) ni dataclasses.InitVar)


eleza _is_type(annotation, cls, a_module, a_type, is_type_predicate):
    # Given a type annotation string, does it refer to a_type in
    # a_module?  For example, when checking that annotation denotes a
    # ClassVar, then a_module ni typing, na a_type is
    # typing.ClassVar.

    # It's possible to look up a_module given a_type, but it involves
    # looking kwenye sys.modules (again!), na seems like a waste since
    # the caller already knows a_module.

    # - annotation ni a string type annotation
    # - cls ni the kundi that this annotation was found in
    # - a_module ni the module we want to match
    # - a_type ni the type kwenye that module we want to match
    # - is_type_predicate ni a function called ukijumuisha (obj, a_module)
    #   that determines ikiwa obj ni of the desired type.

    # Since this test does sio do a local namespace lookup (and
    # instead only a module (global) lookup), there are some things it
    # gets wrong.

    # With string annotations, cv0 will be detected kama a ClassVar:
    #   CV = ClassVar
    #   @dataclass
    #   kundi C0:
    #     cv0: CV

    # But kwenye this example cv1 will sio be detected kama a ClassVar:
    #   @dataclass
    #   kundi C1:
    #     CV = ClassVar
    #     cv1: CV

    # In C1, the code kwenye this function (_is_type) will look up "CV" in
    # the module na sio find it, so it will sio consider cv1 kama a
    # ClassVar.  This ni a fairly obscure corner case, na the best
    # way to fix it would be to eval() the string "CV" ukijumuisha the
    # correct global na local namespaces.  However that would involve
    # a eval() penalty kila every single field of every dataclass
    # that's defined.  It was judged sio worth it.

    match = _MODULE_IDENTIFIER_RE.match(annotation)
    ikiwa match:
        ns = Tupu
        module_name = match.group(1)
        ikiwa sio module_name:
            # No module name, assume the class's module did
            # "kutoka dataclasses agiza InitVar".
            ns = sys.modules.get(cls.__module__).__dict__
        isipokua:
            # Look up module_name kwenye the class's module.
            module = sys.modules.get(cls.__module__)
            ikiwa module na module.__dict__.get(module_name) ni a_module:
                ns = sys.modules.get(a_type.__module__).__dict__
        ikiwa ns na is_type_predicate(ns.get(match.group(2)), a_module):
            rudisha Kweli
    rudisha Uongo


eleza _get_field(cls, a_name, a_type):
    # Return a Field object kila this field name na type.  ClassVars
    # na InitVars are also returned, but marked kama such (see
    # f._field_type).

    # If the default value isn't derived kutoka Field, then it's only a
    # normal default value.  Convert it to a Field().
    default = getattr(cls, a_name, MISSING)
    ikiwa isinstance(default, Field):
        f = default
    isipokua:
        ikiwa isinstance(default, types.MemberDescriptorType):
            # This ni a field kwenye __slots__, so it has no default value.
            default = MISSING
        f = field(default=default)

    # Only at this point do we know the name na the type.  Set them.
    f.name = a_name
    f.type = a_type

    # Assume it's a normal field until proven otherwise.  We're next
    # going to decide ikiwa it's a ClassVar ama InitVar, everything else
    # ni just a normal field.
    f._field_type = _FIELD

    # In addition to checking kila actual types here, also check for
    # string annotations.  get_type_hints() won't always work kila us
    # (see https://github.com/python/typing/issues/508 kila example),
    # plus it's expensive na would require an eval kila every stirng
    # annotation.  So, make a best effort to see ikiwa this ni a ClassVar
    # ama InitVar using regex's na checking that the thing referenced
    # ni actually of the correct type.

    # For the complete discussion, see https://bugs.python.org/issue33453

    # If typing has sio been imported, then it's impossible kila any
    # annotation to be a ClassVar.  So, only look kila ClassVar if
    # typing has been imported by any module (sio necessarily cls's
    # module).
    typing = sys.modules.get('typing')
    ikiwa typing:
        ikiwa (_is_classvar(a_type, typing)
            ama (isinstance(f.type, str)
                na _is_type(f.type, cls, typing, typing.ClassVar,
                             _is_classvar))):
            f._field_type = _FIELD_CLASSVAR

    # If the type ni InitVar, ama ikiwa it's a matching string annotation,
    # then it's an InitVar.
    ikiwa f._field_type ni _FIELD:
        # The module we're checking against ni the module we're
        # currently kwenye (dataclasses.py).
        dataclasses = sys.modules[__name__]
        ikiwa (_is_initvar(a_type, dataclasses)
            ama (isinstance(f.type, str)
                na _is_type(f.type, cls, dataclasses, dataclasses.InitVar,
                             _is_initvar))):
            f._field_type = _FIELD_INITVAR

    # Validations kila individual fields.  This ni delayed until now,
    # instead of kwenye the Field() constructor, since only here do we
    # know the field name, which allows kila better error reporting.

    # Special restrictions kila ClassVar na InitVar.
    ikiwa f._field_type kwenye (_FIELD_CLASSVAR, _FIELD_INITVAR):
        ikiwa f.default_factory ni sio MISSING:
            ashiria TypeError(f'field {f.name} cannot have a '
                            'default factory')
        # Should I check kila other field settings? default_factory
        # seems the most serious to check for.  Maybe add others.  For
        # example, how about init=Uongo (or really,
        # init=<not-the-default-init-value>)?  It makes no sense for
        # ClassVar na InitVar to specify init=<anything>.

    # For real fields, disallow mutable defaults kila known types.
    ikiwa f._field_type ni _FIELD na isinstance(f.default, (list, dict, set)):
        ashiria ValueError(f'mutable default {type(f.default)} kila field '
                         f'{f.name} ni sio allowed: use default_factory')

    rudisha f


eleza _set_new_attribute(cls, name, value):
    # Never overwrites an existing attribute.  Returns Kweli ikiwa the
    # attribute already exists.
    ikiwa name kwenye cls.__dict__:
        rudisha Kweli
    setattr(cls, name, value)
    rudisha Uongo


# Decide if/how we're going to create a hash function.  Key is
# (unsafe_hash, eq, frozen, does-hash-exist).  Value ni the action to
# take.  The common case ni to do nothing, so instead of providing a
# function that ni a no-op, use Tupu to signify that.

eleza _hash_set_none(cls, fields):
    rudisha Tupu

eleza _hash_add(cls, fields):
    flds = [f kila f kwenye fields ikiwa (f.compare ikiwa f.hash ni Tupu isipokua f.hash)]
    rudisha _hash_fn(flds)

eleza _hash_exception(cls, fields):
    # Raise an exception.
    ashiria TypeError(f'Cannot overwrite attribute __hash__ '
                    f'in kundi {cls.__name__}')

#
#                +-------------------------------------- unsafe_hash?
#                |      +------------------------------- eq?
#                |      |      +------------------------ frozen?
#                |      |      |      +----------------  has-explicit-hash?
#                |      |      |      |
#                |      |      |      |        +-------  action
#                |      |      |      |        |
#                v      v      v      v        v
_hash_action = {(Uongo, Uongo, Uongo, Uongo): Tupu,
                (Uongo, Uongo, Uongo, Kweli ): Tupu,
                (Uongo, Uongo, Kweli,  Uongo): Tupu,
                (Uongo, Uongo, Kweli,  Kweli ): Tupu,
                (Uongo, Kweli,  Uongo, Uongo): _hash_set_none,
                (Uongo, Kweli,  Uongo, Kweli ): Tupu,
                (Uongo, Kweli,  Kweli,  Uongo): _hash_add,
                (Uongo, Kweli,  Kweli,  Kweli ): Tupu,
                (Kweli,  Uongo, Uongo, Uongo): _hash_add,
                (Kweli,  Uongo, Uongo, Kweli ): _hash_exception,
                (Kweli,  Uongo, Kweli,  Uongo): _hash_add,
                (Kweli,  Uongo, Kweli,  Kweli ): _hash_exception,
                (Kweli,  Kweli,  Uongo, Uongo): _hash_add,
                (Kweli,  Kweli,  Uongo, Kweli ): _hash_exception,
                (Kweli,  Kweli,  Kweli,  Uongo): _hash_add,
                (Kweli,  Kweli,  Kweli,  Kweli ): _hash_exception,
                }
# See https://bugs.python.org/issue32929#msg312829 kila an if-statement
# version of this table.


eleza _process_class(cls, init, repr, eq, order, unsafe_hash, frozen):
    # Now that dicts retain insertion order, there's no reason to use
    # an ordered dict.  I am leveraging that ordering here, because
    # derived kundi fields overwrite base kundi fields, but the order
    # ni defined by the base class, which ni found first.
    fields = {}

    setattr(cls, _PARAMS, _DataclassParams(init, repr, eq, order,
                                           unsafe_hash, frozen))

    # Find our base classes kwenye reverse MRO order, na exclude
    # ourselves.  In reversed order so that more derived classes
    # override earlier field definitions kwenye base classes.  As long as
    # we're iterating over them, see ikiwa any are frozen.
    any_frozen_base = Uongo
    has_dataclass_bases = Uongo
    kila b kwenye cls.__mro__[-1:0:-1]:
        # Only process classes that have been processed by our
        # decorator.  That is, they have a _FIELDS attribute.
        base_fields = getattr(b, _FIELDS, Tupu)
        ikiwa base_fields:
            has_dataclass_bases = Kweli
            kila f kwenye base_fields.values():
                fields[f.name] = f
            ikiwa getattr(b, _PARAMS).frozen:
                any_frozen_base = Kweli

    # Annotations that are defined kwenye this kundi (sio kwenye base
    # classes).  If __annotations__ isn't present, then this class
    # adds no new annotations.  We use this to compute fields that are
    # added by this class.
    #
    # Fields are found kutoka cls_annotations, which ni guaranteed to be
    # ordered.  Default values are kutoka kundi attributes, ikiwa a field
    # has a default.  If the default value ni a Field(), then it
    # contains additional info beyond (and possibly including) the
    # actual default value.  Pseudo-fields ClassVars na InitVars are
    # included, despite the fact that they're sio real fields.  That's
    # dealt ukijumuisha later.
    cls_annotations = cls.__dict__.get('__annotations__', {})

    # Now find fields kwenye our class.  While doing so, validate some
    # things, na set the default values (as kundi attributes) where
    # we can.
    cls_fields = [_get_field(cls, name, type)
                  kila name, type kwenye cls_annotations.items()]
    kila f kwenye cls_fields:
        fields[f.name] = f

        # If the kundi attribute (which ni the default value kila this
        # field) exists na ni of type 'Field', replace it ukijumuisha the
        # real default.  This ni so that normal kundi introspection
        # sees a real default value, sio a Field.
        ikiwa isinstance(getattr(cls, f.name, Tupu), Field):
            ikiwa f.default ni MISSING:
                # If there's no default, delete the kundi attribute.
                # This happens ikiwa we specify field(repr=Uongo), for
                # example (that is, we specified a field object, but
                # no default value).  Also ikiwa we're using a default
                # factory.  The kundi attribute should sio be set at
                # all kwenye the post-processed class.
                delattr(cls, f.name)
            isipokua:
                setattr(cls, f.name, f.default)

    # Do we have any Field members that don't also have annotations?
    kila name, value kwenye cls.__dict__.items():
        ikiwa isinstance(value, Field) na sio name kwenye cls_annotations:
            ashiria TypeError(f'{name!r} ni a field but has no type annotation')

    # Check rules that apply ikiwa we are derived kutoka any dataclasses.
    ikiwa has_dataclass_bases:
        # Raise an exception ikiwa any of our bases are frozen, but we're not.
        ikiwa any_frozen_base na sio frozen:
            ashiria TypeError('cannot inherit non-frozen datakundi kutoka a '
                            'frozen one')

        # Raise an exception ikiwa we're frozen, but none of our bases are.
        ikiwa sio any_frozen_base na frozen:
            ashiria TypeError('cannot inherit frozen datakundi kutoka a '
                            'non-frozen one')

    # Remember all of the fields on our kundi (including bases).  This
    # also marks this kundi kama being a dataclass.
    setattr(cls, _FIELDS, fields)

    # Was this kundi defined ukijumuisha an explicit __hash__?  Note that if
    # __eq__ ni defined kwenye this class, then python will automatically
    # set __hash__ to Tupu.  This ni a heuristic, kama it's possible
    # that such a __hash__ == Tupu was sio auto-generated, but it
    # close enough.
    class_hash = cls.__dict__.get('__hash__', MISSING)
    has_explicit_hash = sio (class_hash ni MISSING ama
                             (class_hash ni Tupu na '__eq__' kwenye cls.__dict__))

    # If we're generating ordering methods, we must be generating the
    # eq methods.
    ikiwa order na sio eq:
        ashiria ValueError('eq must be true ikiwa order ni true')

    ikiwa init:
        # Does this kundi have a post-init function?
        has_post_init = hasattr(cls, _POST_INIT_NAME)

        # Include InitVars na regular fields (so, sio ClassVars).
        flds = [f kila f kwenye fields.values()
                ikiwa f._field_type kwenye (_FIELD, _FIELD_INITVAR)]
        _set_new_attribute(cls, '__init__',
                           _init_fn(flds,
                                    frozen,
                                    has_post_init,
                                    # The name to use kila the "self"
                                    # param kwenye __init__.  Use "self"
                                    # ikiwa possible.
                                    '__dataclass_self__' ikiwa 'self' kwenye fields
                                            isipokua 'self',
                          ))

    # Get the fields kama a list, na include only real fields.  This is
    # used kwenye all of the following methods.
    field_list = [f kila f kwenye fields.values() ikiwa f._field_type ni _FIELD]

    ikiwa repr:
        flds = [f kila f kwenye field_list ikiwa f.repr]
        _set_new_attribute(cls, '__repr__', _repr_fn(flds))

    ikiwa eq:
        # Create _eq__ method.  There's no need kila a __ne__ method,
        # since python will call __eq__ na negate it.
        flds = [f kila f kwenye field_list ikiwa f.compare]
        self_tuple = _tuple_str('self', flds)
        other_tuple = _tuple_str('other', flds)
        _set_new_attribute(cls, '__eq__',
                           _cmp_fn('__eq__', '==',
                                   self_tuple, other_tuple))

    ikiwa order:
        # Create na set the ordering methods.
        flds = [f kila f kwenye field_list ikiwa f.compare]
        self_tuple = _tuple_str('self', flds)
        other_tuple = _tuple_str('other', flds)
        kila name, op kwenye [('__lt__', '<'),
                         ('__le__', '<='),
                         ('__gt__', '>'),
                         ('__ge__', '>='),
                         ]:
            ikiwa _set_new_attribute(cls, name,
                                  _cmp_fn(name, op, self_tuple, other_tuple)):
                ashiria TypeError(f'Cannot overwrite attribute {name} '
                                f'in kundi {cls.__name__}. Consider using '
                                'functools.total_ordering')

    ikiwa frozen:
        kila fn kwenye _frozen_get_del_attr(cls, field_list):
            ikiwa _set_new_attribute(cls, fn.__name__, fn):
                ashiria TypeError(f'Cannot overwrite attribute {fn.__name__} '
                                f'in kundi {cls.__name__}')

    # Decide if/how we're going to create a hash function.
    hash_action = _hash_action[bool(unsafe_hash),
                               bool(eq),
                               bool(frozen),
                               has_explicit_hash]
    ikiwa hash_action:
        # No need to call _set_new_attribute here, since by the time
        # we're here the overwriting ni unconditional.
        cls.__hash__ = hash_action(cls, field_list)

    ikiwa sio getattr(cls, '__doc__'):
        # Create a kundi doc-string.
        cls.__doc__ = (cls.__name__ +
                       str(inspect.signature(cls)).replace(' -> Tupu', ''))

    rudisha cls


eleza dataclass(cls=Tupu, /, *, init=Kweli, repr=Kweli, eq=Kweli, order=Uongo,
              unsafe_hash=Uongo, frozen=Uongo):
    """Returns the same kundi kama was pitaed in, ukijumuisha dunder methods
    added based on the fields defined kwenye the class.

    Examines PEP 526 __annotations__ to determine fields.

    If init ni true, an __init__() method ni added to the class. If
    repr ni true, a __repr__() method ni added. If order ni true, rich
    comparison dunder methods are added. If unsafe_hash ni true, a
    __hash__() method function ni added. If frozen ni true, fields may
    sio be assigned to after instance creation.
    """

    eleza wrap(cls):
        rudisha _process_class(cls, init, repr, eq, order, unsafe_hash, frozen)

    # See ikiwa we're being called kama @datakundi ama @dataclass().
    ikiwa cls ni Tupu:
        # We're called ukijumuisha parens.
        rudisha wrap

    # We're called kama @datakundi without parens.
    rudisha wrap(cls)


eleza fields(class_or_instance):
    """Return a tuple describing the fields of this dataclass.

    Accepts a datakundi ama an instance of one. Tuple elements are of
    type Field.
    """

    # Might it be worth caching this, per class?
    jaribu:
        fields = getattr(class_or_instance, _FIELDS)
    tatizo AttributeError:
        ashiria TypeError('must be called ukijumuisha a datakundi type ama instance')

    # Exclude pseudo-fields.  Note that fields ni sorted by insertion
    # order, so the order of the tuple ni kama the fields were defined.
    rudisha tuple(f kila f kwenye fields.values() ikiwa f._field_type ni _FIELD)


eleza _is_dataclass_instance(obj):
    """Returns Kweli ikiwa obj ni an instance of a dataclass."""
    rudisha hasattr(type(obj), _FIELDS)


eleza is_dataclass(obj):
    """Returns Kweli ikiwa obj ni a datakundi ama an instance of a
    dataclass."""
    cls = obj ikiwa isinstance(obj, type) isipokua type(obj)
    rudisha hasattr(cls, _FIELDS)


eleza asdict(obj, *, dict_factory=dict):
    """Return the fields of a datakundi instance kama a new dictionary mapping
    field names to field values.

    Example usage:

      @dataclass
      kundi C:
          x: int
          y: int

      c = C(1, 2)
      assert asdict(c) == {'x': 1, 'y': 2}

    If given, 'dict_factory' will be used instead of built-in dict.
    The function applies recursively to field values that are
    datakundi instances. This will also look into built-in containers:
    tuples, lists, na dicts.
    """
    ikiwa sio _is_dataclass_instance(obj):
        ashiria TypeError("asdict() should be called on datakundi instances")
    rudisha _asdict_inner(obj, dict_factory)


eleza _asdict_inner(obj, dict_factory):
    ikiwa _is_dataclass_instance(obj):
        result = []
        kila f kwenye fields(obj):
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        rudisha dict_factory(result)
    lasivyo isinstance(obj, tuple) na hasattr(obj, '_fields'):
        # obj ni a namedtuple.  Recurse into it, but the returned
        # object ni another namedtuple of the same type.  This is
        # similar to how other list- ama tuple-derived classes are
        # treated (see below), but we just need to create them
        # differently because a namedtuple's __init__ needs to be
        # called differently (see bpo-34363).

        # I'm sio using namedtuple's _asdict()
        # method, because:
        # - it does sio recurse kwenye to the namedtuple fields na
        #   convert them to dicts (using dict_factory).
        # - I don't actually want to rudisha a dict here.  The the main
        #   use case here ni json.dumps, na it handles converting
        #   namedtuples to lists.  Admittedly we're losing some
        #   information here when we produce a json list instead of a
        #   dict.  Note that ikiwa we returned dicts here instead of
        #   namedtuples, we could no longer call asdict() on a data
        #   structure where a namedtuple was used kama a dict key.

        rudisha type(obj)(*[_asdict_inner(v, dict_factory) kila v kwenye obj])
    lasivyo isinstance(obj, (list, tuple)):
        # Assume we can create an object of this type by pitaing kwenye a
        # generator (which ni sio true kila namedtuples, handled
        # above).
        rudisha type(obj)(_asdict_inner(v, dict_factory) kila v kwenye obj)
    lasivyo isinstance(obj, dict):
        rudisha type(obj)((_asdict_inner(k, dict_factory),
                          _asdict_inner(v, dict_factory))
                         kila k, v kwenye obj.items())
    isipokua:
        rudisha copy.deepcopy(obj)


eleza astuple(obj, *, tuple_factory=tuple):
    """Return the fields of a datakundi instance kama a new tuple of field values.

    Example usage::

      @dataclass
      kundi C:
          x: int
          y: int

    c = C(1, 2)
    assert astuple(c) == (1, 2)

    If given, 'tuple_factory' will be used instead of built-in tuple.
    The function applies recursively to field values that are
    datakundi instances. This will also look into built-in containers:
    tuples, lists, na dicts.
    """

    ikiwa sio _is_dataclass_instance(obj):
        ashiria TypeError("astuple() should be called on datakundi instances")
    rudisha _astuple_inner(obj, tuple_factory)


eleza _astuple_inner(obj, tuple_factory):
    ikiwa _is_dataclass_instance(obj):
        result = []
        kila f kwenye fields(obj):
            value = _astuple_inner(getattr(obj, f.name), tuple_factory)
            result.append(value)
        rudisha tuple_factory(result)
    lasivyo isinstance(obj, tuple) na hasattr(obj, '_fields'):
        # obj ni a namedtuple.  Recurse into it, but the returned
        # object ni another namedtuple of the same type.  This is
        # similar to how other list- ama tuple-derived classes are
        # treated (see below), but we just need to create them
        # differently because a namedtuple's __init__ needs to be
        # called differently (see bpo-34363).
        rudisha type(obj)(*[_astuple_inner(v, tuple_factory) kila v kwenye obj])
    lasivyo isinstance(obj, (list, tuple)):
        # Assume we can create an object of this type by pitaing kwenye a
        # generator (which ni sio true kila namedtuples, handled
        # above).
        rudisha type(obj)(_astuple_inner(v, tuple_factory) kila v kwenye obj)
    lasivyo isinstance(obj, dict):
        rudisha type(obj)((_astuple_inner(k, tuple_factory), _astuple_inner(v, tuple_factory))
                          kila k, v kwenye obj.items())
    isipokua:
        rudisha copy.deepcopy(obj)


eleza make_dataclass(cls_name, fields, *, bases=(), namespace=Tupu, init=Kweli,
                   repr=Kweli, eq=Kweli, order=Uongo, unsafe_hash=Uongo,
                   frozen=Uongo):
    """Return a new dynamically created dataclass.

    The datakundi name will be 'cls_name'.  'fields' ni an iterable
    of either (name), (name, type) ama (name, type, Field) objects. If type is
    omitted, use the string 'typing.Any'.  Field objects are created by
    the equivalent of calling 'field(name, type [, Field-info])'.

      C = make_dataclass('C', ['x', ('y', int), ('z', int, field(init=Uongo))], bases=(Base,))

    ni equivalent to:

      @dataclass
      kundi C(Base):
          x: 'typing.Any'
          y: int
          z: int = field(init=Uongo)

    For the bases na namespace parameters, see the builtin type() function.

    The parameters init, repr, eq, order, unsafe_hash, na frozen are pitaed to
    dataclass().
    """

    ikiwa namespace ni Tupu:
        namespace = {}
    isipokua:
        # Copy namespace since we're going to mutate it.
        namespace = namespace.copy()

    # While we're looking through the field names, validate that they
    # are identifiers, are sio keywords, na sio duplicates.
    seen = set()
    anns = {}
    kila item kwenye fields:
        ikiwa isinstance(item, str):
            name = item
            tp = 'typing.Any'
        lasivyo len(item) == 2:
            name, tp, = item
        lasivyo len(item) == 3:
            name, tp, spec = item
            namespace[name] = spec
        isipokua:
            ashiria TypeError(f'Invalid field: {item!r}')

        ikiwa sio isinstance(name, str) ama sio name.isidentifier():
            ashiria TypeError(f'Field names must be valid identifiers: {name!r}')
        ikiwa keyword.iskeyword(name):
            ashiria TypeError(f'Field names must sio be keywords: {name!r}')
        ikiwa name kwenye seen:
            ashiria TypeError(f'Field name duplicated: {name!r}')

        seen.add(name)
        anns[name] = tp

    namespace['__annotations__'] = anns
    # We use `types.new_class()` instead of simply `type()` to allow dynamic creation
    # of generic dataclassses.
    cls = types.new_class(cls_name, bases, {}, lambda ns: ns.update(namespace))
    rudisha dataclass(cls, init=init, repr=repr, eq=eq, order=order,
                     unsafe_hash=unsafe_hash, frozen=frozen)


eleza replace(*args, **changes):
    """Return a new object replacing specified fields ukijumuisha new values.

    This ni especially useful kila frozen classes.  Example usage:

      @dataclass(frozen=Kweli)
      kundi C:
          x: int
          y: int

      c = C(1, 2)
      c1 = replace(c, x=3)
      assert c1.x == 3 na c1.y == 2
      """
    ikiwa len(args) > 1:
        ashiria TypeError(f'replace() takes 1 positional argument but {len(args)} were given')
    ikiwa args:
        obj, = args
    lasivyo 'obj' kwenye changes:
        obj = changes.pop('obj')
        agiza warnings
        warnings.warn("Passing 'obj' kama keyword argument ni deprecated",
                      DeprecationWarning, stacklevel=2)
    isipokua:
        ashiria TypeError("replace() missing 1 required positional argument: 'obj'")

    # We're going to mutate 'changes', but that's okay because it's a
    # new dict, even ikiwa called ukijumuisha 'replace(obj, **my_changes)'.

    ikiwa sio _is_dataclass_instance(obj):
        ashiria TypeError("replace() should be called on datakundi instances")

    # It's an error to have init=Uongo fields kwenye 'changes'.
    # If a field ni haiko kwenye 'changes', read its value kutoka the provided obj.

    kila f kwenye getattr(obj, _FIELDS).values():
        # Only consider normal fields ama InitVars.
        ikiwa f._field_type ni _FIELD_CLASSVAR:
            endelea

        ikiwa sio f.init:
            # Error ikiwa this field ni specified kwenye changes.
            ikiwa f.name kwenye changes:
                ashiria ValueError(f'field {f.name} ni declared ukijumuisha '
                                 'init=Uongo, it cannot be specified ukijumuisha '
                                 'replace()')
            endelea

        ikiwa f.name haiko kwenye changes:
            ikiwa f._field_type ni _FIELD_INITVAR:
                ashiria ValueError(f"InitVar {f.name!r} "
                                 'must be specified ukijumuisha replace()')
            changes[f.name] = getattr(obj, f.name)

    # Create the new object, which calls __init__() na
    # __post_init__() (ikiwa defined), using all of the init fields we've
    # added and/or left kwenye 'changes'.  If there are values supplied in
    # changes that aren't fields, this will correctly ashiria a
    # TypeError.
    rudisha obj.__class__(**changes)
replace.__text_signature__ = '(obj, /, **kwargs)'
