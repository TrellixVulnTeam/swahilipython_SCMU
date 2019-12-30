# mock.py
# Test tools kila mocking na patching.
# Maintained by Michael Foord
# Backport kila other versions of Python available from
# https://pypi.org/project/mock

__all__ = (
    'Mock',
    'MagicMock',
    'patch',
    'sentinel',
    'DEFAULT',
    'ANY',
    'call',
    'create_autospec',
    'AsyncMock',
    'FILTER_DIR',
    'NonCallableMock',
    'NonCallableMagicMock',
    'mock_open',
    'PropertyMock',
    'seal',
)


__version__ = '1.0'

agiza asyncio
agiza contextlib
agiza io
agiza inspect
agiza pprint
agiza sys
agiza builtins
kutoka types agiza CodeType, ModuleType, MethodType
kutoka unittest.util agiza safe_repr
kutoka functools agiza wraps, partial


_builtins = {name kila name kwenye dir(builtins) ikiwa sio name.startswith('_')}

FILTER_DIR = Kweli

# Workaround kila issue #12370
# Without this, the __class__ properties wouldn't be set correctly
_safe_super = super

eleza _is_async_obj(obj):
    ikiwa _is_instance_mock(obj) na sio isinstance(obj, AsyncMock):
        rudisha Uongo
    rudisha asyncio.iscoroutinefunction(obj) ama inspect.isawaitable(obj)


eleza _is_async_func(func):
    ikiwa getattr(func, '__code__', Tupu):
        rudisha asyncio.iscoroutinefunction(func)
    isipokua:
        rudisha Uongo


eleza _is_instance_mock(obj):
    # can't use isinstance on Mock objects because they override __class__
    # The base kundi kila all mocks ni NonCallableMock
    rudisha issubclass(type(obj), NonCallableMock)


eleza _is_exception(obj):
    rudisha (
        isinstance(obj, BaseException) ama
        isinstance(obj, type) na issubclass(obj, BaseException)
    )


eleza _extract_mock(obj):
    # Autospecced functions will rudisha a FunctionType ukijumuisha "mock" attribute
    # which ni the actual mock object that needs to be used.
    ikiwa isinstance(obj, FunctionTypes) na hasattr(obj, 'mock'):
        rudisha obj.mock
    isipokua:
        rudisha obj


eleza _get_signature_object(func, as_instance, eat_self):
    """
    Given an arbitrary, possibly callable object, try to create a suitable
    signature object.
    Return a (reduced func, signature) tuple, ama Tupu.
    """
    ikiwa isinstance(func, type) na sio as_instance:
        # If it's a type na should be modelled kama a type, use __init__.
        func = func.__init__
        # Skip the `self` argument kwenye __init__
        eat_self = Kweli
    lasivyo sio isinstance(func, FunctionTypes):
        # If we really want to motoa an instance of the pitaed type,
        # __call__ should be looked up, sio __init__.
        jaribu:
            func = func.__call__
        tatizo AttributeError:
            rudisha Tupu
    ikiwa eat_self:
        sig_func = partial(func, Tupu)
    isipokua:
        sig_func = func
    jaribu:
        rudisha func, inspect.signature(sig_func)
    tatizo ValueError:
        # Certain callable types are sio supported by inspect.signature()
        rudisha Tupu


eleza _check_signature(func, mock, skipfirst, instance=Uongo):
    sig = _get_signature_object(func, instance, skipfirst)
    ikiwa sig ni Tupu:
        return
    func, sig = sig
    eleza checksig(self, /, *args, **kwargs):
        sig.bind(*args, **kwargs)
    _copy_func_details(func, checksig)
    type(mock)._mock_check_sig = checksig
    type(mock).__signature__ = sig


eleza _copy_func_details(func, funcopy):
    # we explicitly don't copy func.__dict__ into this copy kama it would
    # expose original attributes that should be mocked
    kila attribute kwenye (
        '__name__', '__doc__', '__text_signature__',
        '__module__', '__defaults__', '__kwdefaults__',
    ):
        jaribu:
            setattr(funcopy, attribute, getattr(func, attribute))
        tatizo AttributeError:
            pita


eleza _callable(obj):
    ikiwa isinstance(obj, type):
        rudisha Kweli
    ikiwa isinstance(obj, (staticmethod, classmethod, MethodType)):
        rudisha _callable(obj.__func__)
    ikiwa getattr(obj, '__call__', Tupu) ni sio Tupu:
        rudisha Kweli
    rudisha Uongo


eleza _is_list(obj):
    # checks kila list ama tuples
    # XXXX badly named!
    rudisha type(obj) kwenye (list, tuple)


eleza _instance_callable(obj):
    """Given an object, rudisha Kweli ikiwa the object ni callable.
    For classes, rudisha Kweli ikiwa instances would be callable."""
    ikiwa sio isinstance(obj, type):
        # already an instance
        rudisha getattr(obj, '__call__', Tupu) ni sio Tupu

    # *could* be broken by a kundi overriding __mro__ ama __dict__ via
    # a metaclass
    kila base kwenye (obj,) + obj.__mro__:
        ikiwa base.__dict__.get('__call__') ni sio Tupu:
            rudisha Kweli
    rudisha Uongo


eleza _set_signature(mock, original, instance=Uongo):
    # creates a function ukijumuisha signature (*args, **kwargs) that delegates to a
    # mock. It still does signature checking by calling a lambda ukijumuisha the same
    # signature kama the original.

    skipfirst = isinstance(original, type)
    result = _get_signature_object(original, instance, skipfirst)
    ikiwa result ni Tupu:
        rudisha mock
    func, sig = result
    eleza checksig(*args, **kwargs):
        sig.bind(*args, **kwargs)
    _copy_func_details(func, checksig)

    name = original.__name__
    ikiwa sio name.isidentifier():
        name = 'funcopy'
    context = {'_checksig_': checksig, 'mock': mock}
    src = """eleza %s(*args, **kwargs):
    _checksig_(*args, **kwargs)
    rudisha mock(*args, **kwargs)""" % name
    exec (src, context)
    funcopy = context[name]
    _setup_func(funcopy, mock, sig)
    rudisha funcopy


eleza _setup_func(funcopy, mock, sig):
    funcopy.mock = mock

    eleza assert_called_with(*args, **kwargs):
        rudisha mock.assert_called_with(*args, **kwargs)
    eleza assert_called(*args, **kwargs):
        rudisha mock.assert_called(*args, **kwargs)
    eleza assert_not_called(*args, **kwargs):
        rudisha mock.assert_not_called(*args, **kwargs)
    eleza assert_called_once(*args, **kwargs):
        rudisha mock.assert_called_once(*args, **kwargs)
    eleza assert_called_once_with(*args, **kwargs):
        rudisha mock.assert_called_once_with(*args, **kwargs)
    eleza assert_has_calls(*args, **kwargs):
        rudisha mock.assert_has_calls(*args, **kwargs)
    eleza assert_any_call(*args, **kwargs):
        rudisha mock.assert_any_call(*args, **kwargs)
    eleza reset_mock():
        funcopy.method_calls = _CallList()
        funcopy.mock_calls = _CallList()
        mock.reset_mock()
        ret = funcopy.return_value
        ikiwa _is_instance_mock(ret) na sio ret ni mock:
            ret.reset_mock()

    funcopy.called = Uongo
    funcopy.call_count = 0
    funcopy.call_args = Tupu
    funcopy.call_args_list = _CallList()
    funcopy.method_calls = _CallList()
    funcopy.mock_calls = _CallList()

    funcopy.return_value = mock.return_value
    funcopy.side_effect = mock.side_effect
    funcopy._mock_children = mock._mock_children

    funcopy.assert_called_ukijumuisha = assert_called_with
    funcopy.assert_called_once_ukijumuisha = assert_called_once_with
    funcopy.assert_has_calls = assert_has_calls
    funcopy.assert_any_call = assert_any_call
    funcopy.reset_mock = reset_mock
    funcopy.assert_called = assert_called
    funcopy.assert_not_called = assert_not_called
    funcopy.assert_called_once = assert_called_once
    funcopy.__signature__ = sig

    mock._mock_delegate = funcopy


eleza _setup_async_mock(mock):
    mock._is_coroutine = asyncio.coroutines._is_coroutine
    mock.await_count = 0
    mock.await_args = Tupu
    mock.await_args_list = _CallList()

    # Mock ni sio configured yet so the attributes are set
    # to a function na then the corresponding mock helper function
    # ni called when the helper ni accessed similar to _setup_func.
    eleza wrapper(attr, /, *args, **kwargs):
        rudisha getattr(mock.mock, attr)(*args, **kwargs)

    kila attribute kwenye ('assert_awaited',
                      'assert_awaited_once',
                      'assert_awaited_with',
                      'assert_awaited_once_with',
                      'assert_any_await',
                      'assert_has_awaits',
                      'assert_not_awaited'):

        # setattr(mock, attribute, wrapper) causes late binding
        # hence attribute will always be the last value kwenye the loop
        # Use partial(wrapper, attribute) to ensure the attribute ni bound
        # correctly.
        setattr(mock, attribute, partial(wrapper, attribute))


eleza _is_magic(name):
    rudisha '__%s__' % name[2:-2] == name


kundi _SentinelObject(object):
    "A unique, named, sentinel object."
    eleza __init__(self, name):
        self.name = name

    eleza __repr__(self):
        rudisha 'sentinel.%s' % self.name

    eleza __reduce__(self):
        rudisha 'sentinel.%s' % self.name


kundi _Sentinel(object):
    """Access attributes to rudisha a named object, usable kama a sentinel."""
    eleza __init__(self):
        self._sentinels = {}

    eleza __getattr__(self, name):
        ikiwa name == '__bases__':
            # Without this help(unittest.mock) raises an exception
            ashiria AttributeError
        rudisha self._sentinels.setdefault(name, _SentinelObject(name))

    eleza __reduce__(self):
        rudisha 'sentinel'


sentinel = _Sentinel()

DEFAULT = sentinel.DEFAULT
_missing = sentinel.MISSING
_deleted = sentinel.DELETED


_allowed_names = {
    'return_value', '_mock_return_value', 'side_effect',
    '_mock_side_effect', '_mock_parent', '_mock_new_parent',
    '_mock_name', '_mock_new_name'
}


eleza _delegating_property(name):
    _allowed_names.add(name)
    _the_name = '_mock_' + name
    eleza _get(self, name=name, _the_name=_the_name):
        sig = self._mock_delegate
        ikiwa sig ni Tupu:
            rudisha getattr(self, _the_name)
        rudisha getattr(sig, name)
    eleza _set(self, value, name=name, _the_name=_the_name):
        sig = self._mock_delegate
        ikiwa sig ni Tupu:
            self.__dict__[_the_name] = value
        isipokua:
            setattr(sig, name, value)

    rudisha property(_get, _set)



kundi _CallList(list):

    eleza __contains__(self, value):
        ikiwa sio isinstance(value, list):
            rudisha list.__contains__(self, value)
        len_value = len(value)
        len_self = len(self)
        ikiwa len_value > len_self:
            rudisha Uongo

        kila i kwenye range(0, len_self - len_value + 1):
            sub_list = self[i:i+len_value]
            ikiwa sub_list == value:
                rudisha Kweli
        rudisha Uongo

    eleza __repr__(self):
        rudisha pprint.pformat(list(self))


eleza _check_and_set_parent(parent, value, name, new_name):
    value = _extract_mock(value)

    ikiwa sio _is_instance_mock(value):
        rudisha Uongo
    ikiwa ((value._mock_name ama value._mock_new_name) ama
        (value._mock_parent ni sio Tupu) ama
        (value._mock_new_parent ni sio Tupu)):
        rudisha Uongo

    _parent = parent
    wakati _parent ni sio Tupu:
        # setting a mock (value) kama a child ama rudisha value of itself
        # should sio modify the mock
        ikiwa _parent ni value:
            rudisha Uongo
        _parent = _parent._mock_new_parent

    ikiwa new_name:
        value._mock_new_parent = parent
        value._mock_new_name = new_name
    ikiwa name:
        value._mock_parent = parent
        value._mock_name = name
    rudisha Kweli

# Internal kundi to identify ikiwa we wrapped an iterator object ama not.
kundi _MockIter(object):
    eleza __init__(self, obj):
        self.obj = iter(obj)
    eleza __next__(self):
        rudisha next(self.obj)

kundi Base(object):
    _mock_return_value = DEFAULT
    _mock_side_effect = Tupu
    eleza __init__(self, /, *args, **kwargs):
        pita



kundi NonCallableMock(Base):
    """A non-callable version of `Mock`"""

    eleza __new__(cls, /, *args, **kw):
        # every instance has its own class
        # so we can create magic methods on the
        # kundi without stomping on other mocks
        bases = (cls,)
        ikiwa sio issubclass(cls, AsyncMock):
            # Check ikiwa spec ni an async object ama function
            sig = inspect.signature(NonCallableMock.__init__)
            bound_args = sig.bind_partial(cls, *args, **kw).arguments
            spec_arg = [
                arg kila arg kwenye bound_args.keys()
                ikiwa arg.startswith('spec')
            ]
            ikiwa spec_arg:
                # what ikiwa spec_set ni different than spec?
                ikiwa _is_async_obj(bound_args[spec_arg[0]]):
                    bases = (AsyncMockMixin, cls,)
        new = type(cls.__name__, bases, {'__doc__': cls.__doc__})
        instance = _safe_super(NonCallableMock, cls).__new__(new)
        rudisha instance


    eleza __init__(
            self, spec=Tupu, wraps=Tupu, name=Tupu, spec_set=Tupu,
            parent=Tupu, _spec_state=Tupu, _new_name='', _new_parent=Tupu,
            _spec_as_instance=Uongo, _eat_self=Tupu, unsafe=Uongo, **kwargs
        ):
        ikiwa _new_parent ni Tupu:
            _new_parent = parent

        __dict__ = self.__dict__
        __dict__['_mock_parent'] = parent
        __dict__['_mock_name'] = name
        __dict__['_mock_new_name'] = _new_name
        __dict__['_mock_new_parent'] = _new_parent
        __dict__['_mock_sealed'] = Uongo

        ikiwa spec_set ni sio Tupu:
            spec = spec_set
            spec_set = Kweli
        ikiwa _eat_self ni Tupu:
            _eat_self = parent ni sio Tupu

        self._mock_add_spec(spec, spec_set, _spec_as_instance, _eat_self)

        __dict__['_mock_children'] = {}
        __dict__['_mock_wraps'] = wraps
        __dict__['_mock_delegate'] = Tupu

        __dict__['_mock_called'] = Uongo
        __dict__['_mock_call_args'] = Tupu
        __dict__['_mock_call_count'] = 0
        __dict__['_mock_call_args_list'] = _CallList()
        __dict__['_mock_mock_calls'] = _CallList()

        __dict__['method_calls'] = _CallList()
        __dict__['_mock_unsafe'] = unsafe

        ikiwa kwargs:
            self.configure_mock(**kwargs)

        _safe_super(NonCallableMock, self).__init__(
            spec, wraps, name, spec_set, parent,
            _spec_state
        )


    eleza attach_mock(self, mock, attribute):
        """
        Attach a mock kama an attribute of this one, replacing its name na
        parent. Calls to the attached mock will be recorded kwenye the
        `method_calls` na `mock_calls` attributes of this one."""
        inner_mock = _extract_mock(mock)

        inner_mock._mock_parent = Tupu
        inner_mock._mock_new_parent = Tupu
        inner_mock._mock_name = ''
        inner_mock._mock_new_name = Tupu

        setattr(self, attribute, mock)


    eleza mock_add_spec(self, spec, spec_set=Uongo):
        """Add a spec to a mock. `spec` can either be an object ama a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes kutoka the mock.

        If `spec_set` ni Kweli then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)


    eleza _mock_add_spec(self, spec, spec_set, _spec_as_instance=Uongo,
                       _eat_self=Uongo):
        _spec_class = Tupu
        _spec_signature = Tupu
        _spec_asyncs = []

        kila attr kwenye dir(spec):
            ikiwa asyncio.iscoroutinefunction(getattr(spec, attr, Tupu)):
                _spec_asyncs.append(attr)

        ikiwa spec ni sio Tupu na sio _is_list(spec):
            ikiwa isinstance(spec, type):
                _spec_class = spec
            isipokua:
                _spec_class = type(spec)
            res = _get_signature_object(spec,
                                        _spec_as_instance, _eat_self)
            _spec_signature = res na res[1]

            spec = dir(spec)

        __dict__ = self.__dict__
        __dict__['_spec_class'] = _spec_class
        __dict__['_spec_set'] = spec_set
        __dict__['_spec_signature'] = _spec_signature
        __dict__['_mock_methods'] = spec
        __dict__['_spec_asyncs'] = _spec_asyncs

    eleza __get_return_value(self):
        ret = self._mock_return_value
        ikiwa self._mock_delegate ni sio Tupu:
            ret = self._mock_delegate.return_value

        ikiwa ret ni DEFAULT:
            ret = self._get_child_mock(
                _new_parent=self, _new_name='()'
            )
            self.return_value = ret
        rudisha ret


    eleza __set_return_value(self, value):
        ikiwa self._mock_delegate ni sio Tupu:
            self._mock_delegate.return_value = value
        isipokua:
            self._mock_return_value = value
            _check_and_set_parent(self, value, Tupu, '()')

    __return_value_doc = "The value to be returned when the mock ni called."
    return_value = property(__get_return_value, __set_return_value,
                            __return_value_doc)


    @property
    eleza __class__(self):
        ikiwa self._spec_class ni Tupu:
            rudisha type(self)
        rudisha self._spec_class

    called = _delegating_property('called')
    call_count = _delegating_property('call_count')
    call_args = _delegating_property('call_args')
    call_args_list = _delegating_property('call_args_list')
    mock_calls = _delegating_property('mock_calls')


    eleza __get_side_effect(self):
        delegated = self._mock_delegate
        ikiwa delegated ni Tupu:
            rudisha self._mock_side_effect
        sf = delegated.side_effect
        ikiwa (sf ni sio Tupu na sio callable(sf)
                na sio isinstance(sf, _MockIter) na sio _is_exception(sf)):
            sf = _MockIter(sf)
            delegated.side_effect = sf
        rudisha sf

    eleza __set_side_effect(self, value):
        value = _try_iter(value)
        delegated = self._mock_delegate
        ikiwa delegated ni Tupu:
            self._mock_side_effect = value
        isipokua:
            delegated.side_effect = value

    side_effect = property(__get_side_effect, __set_side_effect)


    eleza reset_mock(self,  visited=Tupu,*, return_value=Uongo, side_effect=Uongo):
        "Restore the mock object to its initial state."
        ikiwa visited ni Tupu:
            visited = []
        ikiwa id(self) kwenye visited:
            return
        visited.append(id(self))

        self.called = Uongo
        self.call_args = Tupu
        self.call_count = 0
        self.mock_calls = _CallList()
        self.call_args_list = _CallList()
        self.method_calls = _CallList()

        ikiwa return_value:
            self._mock_return_value = DEFAULT
        ikiwa side_effect:
            self._mock_side_effect = Tupu

        kila child kwenye self._mock_children.values():
            ikiwa isinstance(child, _SpecState) ama child ni _deleted:
                endelea
            child.reset_mock(visited)

        ret = self._mock_return_value
        ikiwa _is_instance_mock(ret) na ret ni sio self:
            ret.reset_mock(visited)


    eleza configure_mock(self, /, **kwargs):
        """Set attributes on the mock through keyword arguments.

        Attributes plus rudisha values na side effects can be set on child
        mocks using standard dot notation na unpacking a dictionary kwenye the
        method call:

        >>> attrs = {'method.return_value': 3, 'other.side_effect': KeyError}
        >>> mock.configure_mock(**attrs)"""
        kila arg, val kwenye sorted(kwargs.items(),
                               # we sort on the number of dots so that
                               # attributes are set before we set attributes on
                               # attributes
                               key=lambda enjaribu: entry[0].count('.')):
            args = arg.split('.')
            final = args.pop()
            obj = self
            kila entry kwenye args:
                obj = getattr(obj, entry)
            setattr(obj, final, val)


    eleza __getattr__(self, name):
        ikiwa name kwenye {'_mock_methods', '_mock_unsafe'}:
            ashiria AttributeError(name)
        lasivyo self._mock_methods ni sio Tupu:
            ikiwa name haiko kwenye self._mock_methods ama name kwenye _all_magics:
                ashiria AttributeError("Mock object has no attribute %r" % name)
        lasivyo _is_magic(name):
            ashiria AttributeError(name)
        ikiwa sio self._mock_unsafe:
            ikiwa name.startswith(('assert', 'assret')):
                ashiria AttributeError("Attributes cannot start ukijumuisha 'assert' "
                                     "or 'assret'")

        result = self._mock_children.get(name)
        ikiwa result ni _deleted:
            ashiria AttributeError(name)
        lasivyo result ni Tupu:
            wraps = Tupu
            ikiwa self._mock_wraps ni sio Tupu:
                # XXXX should we get the attribute without triggering code
                # execution?
                wraps = getattr(self._mock_wraps, name)

            result = self._get_child_mock(
                parent=self, name=name, wraps=wraps, _new_name=name,
                _new_parent=self
            )
            self._mock_children[name]  = result

        lasivyo isinstance(result, _SpecState):
            result = create_autospec(
                result.spec, result.spec_set, result.instance,
                result.parent, result.name
            )
            self._mock_children[name]  = result

        rudisha result


    eleza _extract_mock_name(self):
        _name_list = [self._mock_new_name]
        _parent = self._mock_new_parent
        last = self

        dot = '.'
        ikiwa _name_list == ['()']:
            dot = ''

        wakati _parent ni sio Tupu:
            last = _parent

            _name_list.append(_parent._mock_new_name + dot)
            dot = '.'
            ikiwa _parent._mock_new_name == '()':
                dot = ''

            _parent = _parent._mock_new_parent

        _name_list = list(reversed(_name_list))
        _first = last._mock_name ama 'mock'
        ikiwa len(_name_list) > 1:
            ikiwa _name_list[1] haiko kwenye ('()', '().'):
                _first += '.'
        _name_list[0] = _first
        rudisha ''.join(_name_list)

    eleza __repr__(self):
        name = self._extract_mock_name()

        name_string = ''
        ikiwa name haiko kwenye ('mock', 'mock.'):
            name_string = ' name=%r' % name

        spec_string = ''
        ikiwa self._spec_class ni sio Tupu:
            spec_string = ' spec=%r'
            ikiwa self._spec_set:
                spec_string = ' spec_set=%r'
            spec_string = spec_string % self._spec_class.__name__
        rudisha "<%s%s%s id='%s'>" % (
            type(self).__name__,
            name_string,
            spec_string,
            id(self)
        )


    eleza __dir__(self):
        """Filter the output of `dir(mock)` to only useful members."""
        ikiwa sio FILTER_DIR:
            rudisha object.__dir__(self)

        extras = self._mock_methods ama []
        from_type = dir(type(self))
        from_dict = list(self.__dict__)
        from_child_mocks = [
            m_name kila m_name, m_value kwenye self._mock_children.items()
            ikiwa m_value ni sio _deleted]

        from_type = [e kila e kwenye from_type ikiwa sio e.startswith('_')]
        from_dict = [e kila e kwenye from_dict ikiwa sio e.startswith('_') ama
                     _is_magic(e)]
        rudisha sorted(set(extras + from_type + from_dict + from_child_mocks))


    eleza __setattr__(self, name, value):
        ikiwa name kwenye _allowed_names:
            # property setters go through here
            rudisha object.__setattr__(self, name, value)
        lasivyo (self._spec_set na self._mock_methods ni sio Tupu na
            name haiko kwenye self._mock_methods na
            name haiko kwenye self.__dict__):
            ashiria AttributeError("Mock object has no attribute '%s'" % name)
        lasivyo name kwenye _unsupported_magics:
            msg = 'Attempting to set unsupported magic method %r.' % name
            ashiria AttributeError(msg)
        lasivyo name kwenye _all_magics:
            ikiwa self._mock_methods ni sio Tupu na name haiko kwenye self._mock_methods:
                ashiria AttributeError("Mock object has no attribute '%s'" % name)

            ikiwa sio _is_instance_mock(value):
                setattr(type(self), name, _get_method(name, value))
                original = value
                value = lambda *args, **kw: original(self, *args, **kw)
            isipokua:
                # only set _new_name na sio name so that mock_calls ni tracked
                # but sio method calls
                _check_and_set_parent(self, value, Tupu, name)
                setattr(type(self), name, value)
                self._mock_children[name] = value
        lasivyo name == '__class__':
            self._spec_class = value
            return
        isipokua:
            ikiwa _check_and_set_parent(self, value, name, name):
                self._mock_children[name] = value

        ikiwa self._mock_sealed na sio hasattr(self, name):
            mock_name = f'{self._extract_mock_name()}.{name}'
            ashiria AttributeError(f'Cannot set {mock_name}')

        rudisha object.__setattr__(self, name, value)


    eleza __delattr__(self, name):
        ikiwa name kwenye _all_magics na name kwenye type(self).__dict__:
            delattr(type(self), name)
            ikiwa name haiko kwenye self.__dict__:
                # kila magic methods that are still MagicProxy objects na
                # sio set on the instance itself
                return

        obj = self._mock_children.get(name, _missing)
        ikiwa name kwenye self.__dict__:
            _safe_super(NonCallableMock, self).__delattr__(name)
        lasivyo obj ni _deleted:
            ashiria AttributeError(name)
        ikiwa obj ni sio _missing:
            toa self._mock_children[name]
        self._mock_children[name] = _deleted


    eleza _format_mock_call_signature(self, args, kwargs):
        name = self._mock_name ama 'mock'
        rudisha _format_call_signature(name, args, kwargs)


    eleza _format_mock_failure_message(self, args, kwargs, action='call'):
        message = 'expected %s sio found.\nExpected: %s\nActual: %s'
        expected_string = self._format_mock_call_signature(args, kwargs)
        call_args = self.call_args
        actual_string = self._format_mock_call_signature(*call_args)
        rudisha message % (action, expected_string, actual_string)


    eleza _get_call_signature_from_name(self, name):
        """
        * If call objects are asserted against a method/function like obj.meth1
        then there could be no name kila the call object to lookup. Hence just
        rudisha the spec_signature of the method/function being asserted against.
        * If the name ni sio empty then remove () na split by '.' to get
        list of names to iterate through the children until a potential
        match ni found. A child mock ni created only during attribute access
        so ikiwa we get a _SpecState then no attributes of the spec were accessed
        na can be safely exited.
        """
        ikiwa sio name:
            rudisha self._spec_signature

        sig = Tupu
        names = name.replace('()', '').split('.')
        children = self._mock_children

        kila name kwenye names:
            child = children.get(name)
            ikiwa child ni Tupu ama isinstance(child, _SpecState):
                koma
            isipokua:
                children = child._mock_children
                sig = child._spec_signature

        rudisha sig


    eleza _call_matcher(self, _call):
        """
        Given a call (or simply an (args, kwargs) tuple), rudisha a
        comparison key suitable kila matching ukijumuisha other calls.
        This ni a best effort method which relies on the spec's signature,
        ikiwa available, ama falls back on the arguments themselves.
        """

        ikiwa isinstance(_call, tuple) na len(_call) > 2:
            sig = self._get_call_signature_from_name(_call[0])
        isipokua:
            sig = self._spec_signature

        ikiwa sig ni sio Tupu:
            ikiwa len(_call) == 2:
                name = ''
                args, kwargs = _call
            isipokua:
                name, args, kwargs = _call
            jaribu:
                rudisha name, sig.bind(*args, **kwargs)
            tatizo TypeError kama e:
                rudisha e.with_traceback(Tupu)
        isipokua:
            rudisha _call

    eleza assert_not_called(self):
        """assert that the mock was never called.
        """
        ikiwa self.call_count != 0:
            msg = ("Expected '%s' to sio have been called. Called %s times.%s"
                   % (self._mock_name ama 'mock',
                      self.call_count,
                      self._calls_repr()))
            ashiria AssertionError(msg)

    eleza assert_called(self):
        """assert that the mock was called at least once
        """
        ikiwa self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name ama 'mock'))
            ashiria AssertionError(msg)

    eleza assert_called_once(self):
        """assert that the mock was called only once.
        """
        ikiwa sio self.call_count == 1:
            msg = ("Expected '%s' to have been called once. Called %s times.%s"
                   % (self._mock_name ama 'mock',
                      self.call_count,
                      self._calls_repr()))
            ashiria AssertionError(msg)

    eleza assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made ukijumuisha the specified arguments.

        Raises an AssertionError ikiwa the args na keyword args pitaed kwenye are
        different to the last call to the mock."""
        ikiwa self.call_args ni Tupu:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call sio found.\nExpected: %s\nActual: %s'
                    % (expected, actual))
            ashiria AssertionError(error_message)

        eleza _error_message():
            msg = self._format_mock_failure_message(args, kwargs)
            rudisha msg
        expected = self._call_matcher((args, kwargs))
        actual = self._call_matcher(self.call_args)
        ikiwa expected != actual:
            cause = expected ikiwa isinstance(expected, Exception) isipokua Tupu
            ashiria AssertionError(_error_message()) kutoka cause


    eleza assert_called_once_with(self, /, *args, **kwargs):
        """assert that the mock was called exactly once na that that call was
        ukijumuisha the specified arguments."""
        ikiwa sio self.call_count == 1:
            msg = ("Expected '%s' to be called once. Called %s times.%s"
                   % (self._mock_name ama 'mock',
                      self.call_count,
                      self._calls_repr()))
            ashiria AssertionError(msg)
        rudisha self.assert_called_with(*args, **kwargs)


    eleza assert_has_calls(self, calls, any_order=Uongo):
        """assert the mock has been called ukijumuisha the specified calls.
        The `mock_calls` list ni checked kila the calls.

        If `any_order` ni Uongo (the default) then the calls must be
        sequential. There can be extra calls before ama after the
        specified calls.

        If `any_order` ni Kweli then the calls can be kwenye any order, but
        they must all appear kwenye `mock_calls`."""
        expected = [self._call_matcher(c) kila c kwenye calls]
        cause = next((e kila e kwenye expected ikiwa isinstance(e, Exception)), Tupu)
        all_calls = _CallList(self._call_matcher(c) kila c kwenye self.mock_calls)
        ikiwa sio any_order:
            ikiwa expected haiko kwenye all_calls:
                ikiwa cause ni Tupu:
                    problem = 'Calls sio found.'
                isipokua:
                    problem = ('Error processing expected calls.\n'
                               'Errors: {}').format(
                                   [e ikiwa isinstance(e, Exception) isipokua Tupu
                                    kila e kwenye expected])
                ashiria AssertionError(
                    f'{problem}\n'
                    f'Expected: {_CallList(calls)}'
                    f'{self._calls_repr(prefix="Actual").rstrip(".")}'
                ) kutoka cause
            return

        all_calls = list(all_calls)

        not_found = []
        kila kall kwenye expected:
            jaribu:
                all_calls.remove(kall)
            tatizo ValueError:
                not_found.append(kall)
        ikiwa not_found:
            ashiria AssertionError(
                '%r does sio contain all of %r kwenye its call list, '
                'found %r instead' % (self._mock_name ama 'mock',
                                      tuple(not_found), all_calls)
            ) kutoka cause


    eleza assert_any_call(self, /, *args, **kwargs):
        """assert the mock has been called ukijumuisha the specified arguments.

        The assert pitaes ikiwa the mock has *ever* been called, unlike
        `assert_called_with` na `assert_called_once_with` that only pita if
        the call ni the most recent one."""
        expected = self._call_matcher((args, kwargs))
        actual = [self._call_matcher(c) kila c kwenye self.call_args_list]
        ikiwa expected haiko kwenye actual:
            cause = expected ikiwa isinstance(expected, Exception) isipokua Tupu
            expected_string = self._format_mock_call_signature(args, kwargs)
            ashiria AssertionError(
                '%s call sio found' % expected_string
            ) kutoka cause


    eleza _get_child_mock(self, /, **kw):
        """Create the child mocks kila attributes na rudisha value.
        By default child mocks will be the same type kama the parent.
        Subclasses of Mock may want to override this to customize the way
        child mocks are made.

        For non-callable mocks the callable variant will be used (rather than
        any custom subclass)."""
        _new_name = kw.get("_new_name")
        ikiwa _new_name kwenye self.__dict__['_spec_asyncs']:
            rudisha AsyncMock(**kw)

        _type = type(self)
        ikiwa issubclass(_type, MagicMock) na _new_name kwenye _async_method_magics:
            # Any asynchronous magic becomes an AsyncMock
            klass = AsyncMock
        lasivyo issubclass(_type, AsyncMockMixin):
            ikiwa (_new_name kwenye _all_sync_magics ama
                    self._mock_methods na _new_name kwenye self._mock_methods):
                # Any synchronous method on AsyncMock becomes a MagicMock
                klass = MagicMock
            isipokua:
                klass = AsyncMock
        lasivyo sio issubclass(_type, CallableMixin):
            ikiwa issubclass(_type, NonCallableMagicMock):
                klass = MagicMock
            lasivyo issubclass(_type, NonCallableMock):
                klass = Mock
        isipokua:
            klass = _type.__mro__[1]

        ikiwa self._mock_sealed:
            attribute = "." + kw["name"] ikiwa "name" kwenye kw isipokua "()"
            mock_name = self._extract_mock_name() + attribute
            ashiria AttributeError(mock_name)

        rudisha klass(**kw)


    eleza _calls_repr(self, prefix="Calls"):
        """Renders self.mock_calls kama a string.

        Example: "\nCalls: [call(1), call(2)]."

        If self.mock_calls ni empty, an empty string ni returned. The
        output will be truncated ikiwa very long.
        """
        ikiwa sio self.mock_calls:
            rudisha ""
        rudisha f"\n{prefix}: {safe_repr(self.mock_calls)}."



eleza _try_iter(obj):
    ikiwa obj ni Tupu:
        rudisha obj
    ikiwa _is_exception(obj):
        rudisha obj
    ikiwa _callable(obj):
        rudisha obj
    jaribu:
        rudisha iter(obj)
    tatizo TypeError:
        # XXXX backwards compatibility
        # but this will blow up on first call - so maybe we should fail early?
        rudisha obj


kundi CallableMixin(Base):

    eleza __init__(self, spec=Tupu, side_effect=Tupu, return_value=DEFAULT,
                 wraps=Tupu, name=Tupu, spec_set=Tupu, parent=Tupu,
                 _spec_state=Tupu, _new_name='', _new_parent=Tupu, **kwargs):
        self.__dict__['_mock_return_value'] = return_value
        _safe_super(CallableMixin, self).__init__(
            spec, wraps, name, spec_set, parent,
            _spec_state, _new_name, _new_parent, **kwargs
        )

        self.side_effect = side_effect


    eleza _mock_check_sig(self, /, *args, **kwargs):
        # stub method that can be replaced ukijumuisha one ukijumuisha a specific signature
        pita


    eleza __call__(self, /, *args, **kwargs):
        # can't use self in-case a function / method we are mocking uses self
        # kwenye the signature
        self._mock_check_sig(*args, **kwargs)
        self._increment_mock_call(*args, **kwargs)
        rudisha self._mock_call(*args, **kwargs)


    eleza _mock_call(self, /, *args, **kwargs):
        rudisha self._execute_mock_call(*args, **kwargs)

    eleza _increment_mock_call(self, /, *args, **kwargs):
        self.called = Kweli
        self.call_count += 1

        # handle call_args
        # needs to be set here so assertions on call arguments pita before
        # execution kwenye the case of awaited calls
        _call = _Call((args, kwargs), two=Kweli)
        self.call_args = _call
        self.call_args_list.append(_call)

        # initial stuff kila method_calls:
        do_method_calls = self._mock_parent ni sio Tupu
        method_call_name = self._mock_name

        # initial stuff kila mock_calls:
        mock_call_name = self._mock_new_name
        is_a_call = mock_call_name == '()'
        self.mock_calls.append(_Call(('', args, kwargs)))

        # follow up the chain of mocks:
        _new_parent = self._mock_new_parent
        wakati _new_parent ni sio Tupu:

            # handle method_calls:
            ikiwa do_method_calls:
                _new_parent.method_calls.append(_Call((method_call_name, args, kwargs)))
                do_method_calls = _new_parent._mock_parent ni sio Tupu
                ikiwa do_method_calls:
                    method_call_name = _new_parent._mock_name + '.' + method_call_name

            # handle mock_calls:
            this_mock_call = _Call((mock_call_name, args, kwargs))
            _new_parent.mock_calls.append(this_mock_call)

            ikiwa _new_parent._mock_new_name:
                ikiwa is_a_call:
                    dot = ''
                isipokua:
                    dot = '.'
                is_a_call = _new_parent._mock_new_name == '()'
                mock_call_name = _new_parent._mock_new_name + dot + mock_call_name

            # follow the parental chain:
            _new_parent = _new_parent._mock_new_parent

    eleza _execute_mock_call(self, /, *args, **kwargs):
        # seperate kutoka _increment_mock_call so that awaited functions are
        # executed seperately kutoka their call

        effect = self.side_effect
        ikiwa effect ni sio Tupu:
            ikiwa _is_exception(effect):
                ashiria effect
            lasivyo sio _callable(effect):
                result = next(effect)
                ikiwa _is_exception(result):
                    ashiria result
            isipokua:
                result = effect(*args, **kwargs)

            ikiwa result ni sio DEFAULT:
                rudisha result

        ikiwa self._mock_return_value ni sio DEFAULT:
            rudisha self.return_value

        ikiwa self._mock_wraps ni sio Tupu:
            rudisha self._mock_wraps(*args, **kwargs)

        rudisha self.return_value



kundi Mock(CallableMixin, NonCallableMock):
    """
    Create a new `Mock` object. `Mock` takes several optional arguments
    that specify the behaviour of the Mock object:

    * `spec`: This can be either a list of strings ama an existing object (a
      kundi ama instance) that acts kama the specification kila the mock object. If
      you pita kwenye an object then a list of strings ni formed by calling dir on
      the object (excluding unsupported magic attributes na methods). Accessing
      any attribute haiko kwenye this list will ashiria an `AttributeError`.

      If `spec` ni an object (rather than a list of strings) then
      `mock.__class__` returns the kundi of the spec object. This allows mocks
      to pita `isinstance` tests.

    * `spec_set`: A stricter variant of `spec`. If used, attempting to *set*
      ama get an attribute on the mock that isn't on the object pitaed as
      `spec_set` will ashiria an `AttributeError`.

    * `side_effect`: A function to be called whenever the Mock ni called. See
      the `side_effect` attribute. Useful kila raising exceptions ama
      dynamically changing rudisha values. The function ni called ukijumuisha the same
      arguments kama the mock, na unless it returns `DEFAULT`, the return
      value of this function ni used kama the rudisha value.

      If `side_effect` ni an iterable then each call to the mock will return
      the next value kutoka the iterable. If any of the members of the iterable
      are exceptions they will be raised instead of returned.

    * `return_value`: The value returned when the mock ni called. By default
      this ni a new Mock (created on first access). See the
      `return_value` attribute.

    * `wraps`: Item kila the mock object to wrap. If `wraps` ni sio Tupu then
      calling the Mock will pita the call through to the wrapped object
      (returning the real result). Attribute access on the mock will rudisha a
      Mock object that wraps the corresponding attribute of the wrapped object
      (so attempting to access an attribute that doesn't exist will ashiria an
      `AttributeError`).

      If the mock has an explicit `return_value` set then calls are sio pitaed
      to the wrapped object na the `return_value` ni returned instead.

    * `name`: If the mock has a name then it will be used kwenye the repr of the
      mock. This can be useful kila debugging. The name ni propagated to child
      mocks.

    Mocks can also be called ukijumuisha arbitrary keyword arguments. These will be
    used to set attributes on the mock after it ni created.
    """


eleza _dot_lookup(thing, comp, import_path):
    jaribu:
        rudisha getattr(thing, comp)
    tatizo AttributeError:
        __import__(import_path)
        rudisha getattr(thing, comp)


eleza _importer(target):
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    kila comp kwenye components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    rudisha thing


eleza _is_started(patcher):
    # XXXX horrible
    rudisha hasattr(patcher, 'is_local')


kundi _patch(object):

    attribute_name = Tupu
    _active_patches = []

    eleza __init__(
            self, getter, attribute, new, spec, create,
            spec_set, autospec, new_callable, kwargs
        ):
        ikiwa new_callable ni sio Tupu:
            ikiwa new ni sio DEFAULT:
                ashiria ValueError(
                    "Cannot use 'new' na 'new_callable' together"
                )
            ikiwa autospec ni sio Tupu:
                ashiria ValueError(
                    "Cannot use 'autospec' na 'new_callable' together"
                )

        self.getter = getter
        self.attribute = attribute
        self.new = new
        self.new_callable = new_callable
        self.spec = spec
        self.create = create
        self.has_local = Uongo
        self.spec_set = spec_set
        self.autospec = autospec
        self.kwargs = kwargs
        self.additional_patchers = []


    eleza copy(self):
        patcher = _patch(
            self.getter, self.attribute, self.new, self.spec,
            self.create, self.spec_set,
            self.autospec, self.new_callable, self.kwargs
        )
        patcher.attribute_name = self.attribute_name
        patcher.additional_patchers = [
            p.copy() kila p kwenye self.additional_patchers
        ]
        rudisha patcher


    eleza __call__(self, func):
        ikiwa isinstance(func, type):
            rudisha self.decorate_class(func)
        ikiwa inspect.iscoroutinefunction(func):
            rudisha self.decorate_async_callable(func)
        rudisha self.decorate_callable(func)


    eleza decorate_class(self, klass):
        kila attr kwenye dir(klass):
            ikiwa sio attr.startswith(patch.TEST_PREFIX):
                endelea

            attr_value = getattr(klass, attr)
            ikiwa sio hasattr(attr_value, "__call__"):
                endelea

            patcher = self.copy()
            setattr(klass, attr, patcher(attr_value))
        rudisha klass


    @contextlib.contextmanager
    eleza decoration_helper(self, patched, args, keywargs):
        extra_args = []
        entered_patchers = []
        patching = Tupu

        exc_info = tuple()
        jaribu:
            kila patching kwenye patched.patchings:
                arg = patching.__enter__()
                entered_patchers.append(patching)
                ikiwa patching.attribute_name ni sio Tupu:
                    keywargs.update(arg)
                lasivyo patching.new ni DEFAULT:
                    extra_args.append(arg)

            args += tuple(extra_args)
            tuma (args, keywargs)
        tatizo:
            ikiwa (patching haiko kwenye entered_patchers na
                _is_started(patching)):
                # the patcher may have been started, but an exception
                # raised whilst entering one of its additional_patchers
                entered_patchers.append(patching)
            # Pass the exception to __exit__
            exc_info = sys.exc_info()
            # re-ashiria the exception
            raise
        mwishowe:
            kila patching kwenye reversed(entered_patchers):
                patching.__exit__(*exc_info)


    eleza decorate_callable(self, func):
        # NB. Keep the method kwenye sync ukijumuisha decorate_async_callable()
        ikiwa hasattr(func, 'patchings'):
            func.patchings.append(self)
            rudisha func

        @wraps(func)
        eleza patched(*args, **keywargs):
            ukijumuisha self.decoration_helper(patched,
                                        args,
                                        keywargs) kama (newargs, newkeywargs):
                rudisha func(*newargs, **newkeywargs)

        patched.patchings = [self]
        rudisha patched


    eleza decorate_async_callable(self, func):
        # NB. Keep the method kwenye sync ukijumuisha decorate_callable()
        ikiwa hasattr(func, 'patchings'):
            func.patchings.append(self)
            rudisha func

        @wraps(func)
        async eleza patched(*args, **keywargs):
            ukijumuisha self.decoration_helper(patched,
                                        args,
                                        keywargs) kama (newargs, newkeywargs):
                rudisha await func(*newargs, **newkeywargs)

        patched.patchings = [self]
        rudisha patched


    eleza get_original(self):
        target = self.getter()
        name = self.attribute

        original = DEFAULT
        local = Uongo

        jaribu:
            original = target.__dict__[name]
        tatizo (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        isipokua:
            local = Kweli

        ikiwa name kwenye _builtins na isinstance(target, ModuleType):
            self.create = Kweli

        ikiwa sio self.create na original ni DEFAULT:
            ashiria AttributeError(
                "%s does sio have the attribute %r" % (target, name)
            )
        rudisha original, local


    eleza __enter__(self):
        """Perform the patch."""
        new, spec, spec_set = self.new, self.spec, self.spec_set
        autospec, kwargs = self.autospec, self.kwargs
        new_callable = self.new_callable
        self.target = self.getter()

        # normalise Uongo to Tupu
        ikiwa spec ni Uongo:
            spec = Tupu
        ikiwa spec_set ni Uongo:
            spec_set = Tupu
        ikiwa autospec ni Uongo:
            autospec = Tupu

        ikiwa spec ni sio Tupu na autospec ni sio Tupu:
            ashiria TypeError("Can't specify spec na autospec")
        ikiwa ((spec ni sio Tupu ama autospec ni sio Tupu) na
            spec_set haiko kwenye (Kweli, Tupu)):
            ashiria TypeError("Can't provide explicit spec_set *and* spec ama autospec")

        original, local = self.get_original()

        ikiwa new ni DEFAULT na autospec ni Tupu:
            inherit = Uongo
            ikiwa spec ni Kweli:
                # set spec to the object we are replacing
                spec = original
                ikiwa spec_set ni Kweli:
                    spec_set = original
                    spec = Tupu
            lasivyo spec ni sio Tupu:
                ikiwa spec_set ni Kweli:
                    spec_set = spec
                    spec = Tupu
            lasivyo spec_set ni Kweli:
                spec_set = original

            ikiwa spec ni sio Tupu ama spec_set ni sio Tupu:
                ikiwa original ni DEFAULT:
                    ashiria TypeError("Can't use 'spec' ukijumuisha create=Kweli")
                ikiwa isinstance(original, type):
                    # If we're patching out a kundi na there ni a spec
                    inherit = Kweli
            ikiwa spec ni Tupu na _is_async_obj(original):
                Klass = AsyncMock
            isipokua:
                Klass = MagicMock
            _kwargs = {}
            ikiwa new_callable ni sio Tupu:
                Klass = new_callable
            lasivyo spec ni sio Tupu ama spec_set ni sio Tupu:
                this_spec = spec
                ikiwa spec_set ni sio Tupu:
                    this_spec = spec_set
                ikiwa _is_list(this_spec):
                    not_callable = '__call__' haiko kwenye this_spec
                isipokua:
                    not_callable = sio callable(this_spec)
                ikiwa _is_async_obj(this_spec):
                    Klass = AsyncMock
                lasivyo not_callable:
                    Klass = NonCallableMagicMock

            ikiwa spec ni sio Tupu:
                _kwargs['spec'] = spec
            ikiwa spec_set ni sio Tupu:
                _kwargs['spec_set'] = spec_set

            # add a name to mocks
            ikiwa (isinstance(Klass, type) na
                issubclass(Klass, NonCallableMock) na self.attribute):
                _kwargs['name'] = self.attribute

            _kwargs.update(kwargs)
            new = Klass(**_kwargs)

            ikiwa inherit na _is_instance_mock(new):
                # we can only tell ikiwa the instance should be callable ikiwa the
                # spec ni sio a list
                this_spec = spec
                ikiwa spec_set ni sio Tupu:
                    this_spec = spec_set
                ikiwa (sio _is_list(this_spec) na not
                    _instance_callable(this_spec)):
                    Klass = NonCallableMagicMock

                _kwargs.pop('name')
                new.return_value = Klass(_new_parent=new, _new_name='()',
                                         **_kwargs)
        lasivyo autospec ni sio Tupu:
            # spec ni ignored, new *must* be default, spec_set ni treated
            # kama a boolean. Should we check spec ni sio Tupu na that spec_set
            # ni a bool?
            ikiwa new ni sio DEFAULT:
                ashiria TypeError(
                    "autospec creates the mock kila you. Can't specify "
                    "autospec na new."
                )
            ikiwa original ni DEFAULT:
                ashiria TypeError("Can't use 'autospec' ukijumuisha create=Kweli")
            spec_set = bool(spec_set)
            ikiwa autospec ni Kweli:
                autospec = original

            new = create_autospec(autospec, spec_set=spec_set,
                                  _name=self.attribute, **kwargs)
        lasivyo kwargs:
            # can't set keyword args when we aren't creating the mock
            # XXXX If new ni a Mock we could call new.configure_mock(**kwargs)
            ashiria TypeError("Can't pita kwargs to a mock we aren't creating")

        new_attr = new

        self.temp_original = original
        self.is_local = local
        setattr(self.target, self.attribute, new_attr)
        ikiwa self.attribute_name ni sio Tupu:
            extra_args = {}
            ikiwa self.new ni DEFAULT:
                extra_args[self.attribute_name] =  new
            kila patching kwenye self.additional_patchers:
                arg = patching.__enter__()
                ikiwa patching.new ni DEFAULT:
                    extra_args.update(arg)
            rudisha extra_args

        rudisha new


    eleza __exit__(self, *exc_info):
        """Undo the patch."""
        ikiwa sio _is_started(self):
            return

        ikiwa self.is_local na self.temp_original ni sio DEFAULT:
            setattr(self.target, self.attribute, self.temp_original)
        isipokua:
            delattr(self.target, self.attribute)
            ikiwa sio self.create na (sio hasattr(self.target, self.attribute) ama
                        self.attribute kwenye ('__doc__', '__module__',
                                           '__defaults__', '__annotations__',
                                           '__kwdefaults__')):
                # needed kila proxy objects like django settings
                setattr(self.target, self.attribute, self.temp_original)

        toa self.temp_original
        toa self.is_local
        toa self.target
        kila patcher kwenye reversed(self.additional_patchers):
            ikiwa _is_started(patcher):
                patcher.__exit__(*exc_info)


    eleza start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        self._active_patches.append(self)
        rudisha result


    eleza stop(self):
        """Stop an active patch."""
        jaribu:
            self._active_patches.remove(self)
        tatizo ValueError:
            # If the patch hasn't been started this will fail
            pita

        rudisha self.__exit__()



eleza _get_target(target):
    jaribu:
        target, attribute = target.rsplit('.', 1)
    tatizo (TypeError, ValueError):
        ashiria TypeError("Need a valid target to patch. You supplied: %r" %
                        (target,))
    getter = lambda: _importer(target)
    rudisha getter, attribute


eleza _patch_object(
        target, attribute, new=DEFAULT, spec=Tupu,
        create=Uongo, spec_set=Tupu, autospec=Tupu,
        new_callable=Tupu, **kwargs
    ):
    """
    patch the named member (`attribute`) on an object (`target`) ukijumuisha a mock
    object.

    `patch.object` can be used kama a decorator, kundi decorator ama a context
    manager. Arguments `new`, `spec`, `create`, `spec_set`,
    `autospec` na `new_callable` have the same meaning kama kila `patch`. Like
    `patch`, `patch.object` takes arbitrary keyword arguments kila configuring
    the mock object it creates.

    When used kama a kundi decorator `patch.object` honours `patch.TEST_PREFIX`
    kila choosing which methods to wrap.
    """
    getter = lambda: target
    rudisha _patch(
        getter, attribute, new, spec, create,
        spec_set, autospec, new_callable, kwargs
    )


eleza _patch_multiple(target, spec=Tupu, create=Uongo, spec_set=Tupu,
                    autospec=Tupu, new_callable=Tupu, **kwargs):
    """Perform multiple patches kwenye a single call. It takes the object to be
    patched (either kama an object ama a string to fetch the object by importing)
    na keyword arguments kila the patches::

        ukijumuisha patch.multiple(settings, FIRST_PATCH='one', SECOND_PATCH='two'):
            ...

    Use `DEFAULT` kama the value ikiwa you want `patch.multiple` to create
    mocks kila you. In this case the created mocks are pitaed into a decorated
    function by keyword, na a dictionary ni returned when `patch.multiple` is
    used kama a context manager.

    `patch.multiple` can be used kama a decorator, kundi decorator ama a context
    manager. The arguments `spec`, `spec_set`, `create`,
    `autospec` na `new_callable` have the same meaning kama kila `patch`. These
    arguments will be applied to *all* patches done by `patch.multiple`.

    When used kama a kundi decorator `patch.multiple` honours `patch.TEST_PREFIX`
    kila choosing which methods to wrap.
    """
    ikiwa type(target) ni str:
        getter = lambda: _importer(target)
    isipokua:
        getter = lambda: target

    ikiwa sio kwargs:
        ashiria ValueError(
            'Must supply at least one keyword argument ukijumuisha patch.multiple'
        )
    # need to wrap kwenye a list kila python 3, where items ni a view
    items = list(kwargs.items())
    attribute, new = items[0]
    patcher = _patch(
        getter, attribute, new, spec, create, spec_set,
        autospec, new_callable, {}
    )
    patcher.attribute_name = attribute
    kila attribute, new kwenye items[1:]:
        this_patcher = _patch(
            getter, attribute, new, spec, create, spec_set,
            autospec, new_callable, {}
        )
        this_patcher.attribute_name = attribute
        patcher.additional_patchers.append(this_patcher)
    rudisha patcher


eleza patch(
        target, new=DEFAULT, spec=Tupu, create=Uongo,
        spec_set=Tupu, autospec=Tupu, new_callable=Tupu, **kwargs
    ):
    """
    `patch` acts kama a function decorator, kundi decorator ama a context
    manager. Inside the body of the function ama ukijumuisha statement, the `target`
    ni patched ukijumuisha a `new` object. When the function/ukijumuisha statement exits
    the patch ni undone.

    If `new` ni omitted, then the target ni replaced ukijumuisha an
    `AsyncMock ikiwa the patched object ni an async function ama a
    `MagicMock` otherwise. If `patch` ni used kama a decorator na `new` is
    omitted, the created mock ni pitaed kwenye kama an extra argument to the
    decorated function. If `patch` ni used kama a context manager the created
    mock ni returned by the context manager.

    `target` should be a string kwenye the form `'package.module.ClassName'`. The
    `target` ni imported na the specified object replaced ukijumuisha the `new`
    object, so the `target` must be importable kutoka the environment you are
    calling `patch` from. The target ni imported when the decorated function
    ni executed, sio at decoration time.

    The `spec` na `spec_set` keyword arguments are pitaed to the `MagicMock`
    ikiwa patch ni creating one kila you.

    In addition you can pita `spec=Kweli` ama `spec_set=Kweli`, which causes
    patch to pita kwenye the object being mocked kama the spec/spec_set object.

    `new_callable` allows you to specify a different class, ama callable object,
    that will be called to create the `new` object. By default `AsyncMock` is
    used kila async functions na `MagicMock` kila the rest.

    A more powerful form of `spec` ni `autospec`. If you set `autospec=Kweli`
    then the mock will be created ukijumuisha a spec kutoka the object being replaced.
    All attributes of the mock will also have the spec of the corresponding
    attribute of the object being replaced. Methods na functions being
    mocked will have their arguments checked na will ashiria a `TypeError` if
    they are called ukijumuisha the wrong signature. For mocks replacing a class,
    their rudisha value (the 'instance') will have the same spec kama the class.

    Instead of `autospec=Kweli` you can pita `autospec=some_object` to use an
    arbitrary object kama the spec instead of the one being replaced.

    By default `patch` will fail to replace attributes that don't exist. If
    you pita kwenye `create=Kweli`, na the attribute doesn't exist, patch will
    create the attribute kila you when the patched function ni called, na
    delete it again afterwards. This ni useful kila writing tests against
    attributes that your production code creates at runtime. It ni off by
    default because it can be dangerous. With it switched on you can write
    pitaing tests against APIs that don't actually exist!

    Patch can be used kama a `TestCase` kundi decorator. It works by
    decorating each test method kwenye the class. This reduces the boilerplate
    code when your test methods share a common patchings set. `patch` finds
    tests by looking kila method names that start ukijumuisha `patch.TEST_PREFIX`.
    By default this ni `test`, which matches the way `unittest` finds tests.
    You can specify an alternative prefix by setting `patch.TEST_PREFIX`.

    Patch can be used kama a context manager, ukijumuisha the ukijumuisha statement. Here the
    patching applies to the indented block after the ukijumuisha statement. If you
    use "as" then the patched object will be bound to the name after the
    "as"; very useful ikiwa `patch` ni creating a mock object kila you.

    `patch` takes arbitrary keyword arguments. These will be pitaed to
    the `Mock` (or `new_callable`) on construction.

    `patch.dict(...)`, `patch.multiple(...)` na `patch.object(...)` are
    available kila alternate use-cases.
    """
    getter, attribute = _get_target(target)
    rudisha _patch(
        getter, attribute, new, spec, create,
        spec_set, autospec, new_callable, kwargs
    )


kundi _patch_dict(object):
    """
    Patch a dictionary, ama dictionary like object, na restore the dictionary
    to its original state after the test.

    `in_dict` can be a dictionary ama a mapping like container. If it ni a
    mapping then it must at least support getting, setting na deleting items
    plus iterating over keys.

    `in_dict` can also be a string specifying the name of the dictionary, which
    will then be fetched by importing it.

    `values` can be a dictionary of values to set kwenye the dictionary. `values`
    can also be an iterable of `(key, value)` pairs.

    If `clear` ni Kweli then the dictionary will be cleared before the new
    values are set.

    `patch.dict` can also be called ukijumuisha arbitrary keyword arguments to set
    values kwenye the dictionary::

        ukijumuisha patch.dict('sys.modules', mymodule=Mock(), other_module=Mock()):
            ...

    `patch.dict` can be used kama a context manager, decorator ama class
    decorator. When used kama a kundi decorator `patch.dict` honours
    `patch.TEST_PREFIX` kila choosing which methods to wrap.
    """

    eleza __init__(self, in_dict, values=(), clear=Uongo, **kwargs):
        self.in_dict = in_dict
        # support any argument supported by dict(...) constructor
        self.values = dict(values)
        self.values.update(kwargs)
        self.clear = clear
        self._original = Tupu


    eleza __call__(self, f):
        ikiwa isinstance(f, type):
            rudisha self.decorate_class(f)
        @wraps(f)
        eleza _inner(*args, **kw):
            self._patch_dict()
            jaribu:
                rudisha f(*args, **kw)
            mwishowe:
                self._unpatch_dict()

        rudisha _inner


    eleza decorate_class(self, klass):
        kila attr kwenye dir(klass):
            attr_value = getattr(klass, attr)
            ikiwa (attr.startswith(patch.TEST_PREFIX) na
                 hasattr(attr_value, "__call__")):
                decorator = _patch_dict(self.in_dict, self.values, self.clear)
                decorated = decorator(attr_value)
                setattr(klass, attr, decorated)
        rudisha klass


    eleza __enter__(self):
        """Patch the dict."""
        self._patch_dict()
        rudisha self.in_dict


    eleza _patch_dict(self):
        values = self.values
        ikiwa isinstance(self.in_dict, str):
            self.in_dict = _importer(self.in_dict)
        in_dict = self.in_dict
        clear = self.clear

        jaribu:
            original = in_dict.copy()
        tatizo AttributeError:
            # dict like object ukijumuisha no copy method
            # must support iteration over keys
            original = {}
            kila key kwenye in_dict:
                original[key] = in_dict[key]
        self._original = original

        ikiwa clear:
            _clear_dict(in_dict)

        jaribu:
            in_dict.update(values)
        tatizo AttributeError:
            # dict like object ukijumuisha no update method
            kila key kwenye values:
                in_dict[key] = values[key]


    eleza _unpatch_dict(self):
        in_dict = self.in_dict
        original = self._original

        _clear_dict(in_dict)

        jaribu:
            in_dict.update(original)
        tatizo AttributeError:
            kila key kwenye original:
                in_dict[key] = original[key]


    eleza __exit__(self, *args):
        """Unpatch the dict."""
        self._unpatch_dict()
        rudisha Uongo

    start = __enter__
    stop = __exit__


eleza _clear_dict(in_dict):
    jaribu:
        in_dict.clear()
    tatizo AttributeError:
        keys = list(in_dict)
        kila key kwenye keys:
            toa in_dict[key]


eleza _patch_stopall():
    """Stop all active patches. LIFO to unroll nested patches."""
    kila patch kwenye reversed(_patch._active_patches):
        patch.stop()


patch.object = _patch_object
patch.dict = _patch_dict
patch.multiple = _patch_multiple
patch.stopall = _patch_stopall
patch.TEST_PREFIX = 'test'

magic_methods = (
    "lt le gt ge eq ne "
    "getitem setitem delitem "
    "len contains iter "
    "hash str sizeof "
    "enter exit "
    # we added divmod na rdivmod here instead of numerics
    # because there ni no idivmod
    "divmod rdivmod neg pos abs invert "
    "complex int float index "
    "round trunc floor ceil "
    "bool next "
    "fspath "
    "aiter "
)

numerics = (
    "add sub mul matmul div floordiv mod lshift rshift na xor ama pow truediv"
)
inplace = ' '.join('i%s' % n kila n kwenye numerics.split())
right = ' '.join('r%s' % n kila n kwenye numerics.split())

# sio including __prepare__, __instancecheck__, __subclasscheck__
# (as they are metakundi methods)
# __del__ ni sio supported at all kama it causes problems ikiwa it exists

_non_defaults = {
    '__get__', '__set__', '__delete__', '__reversed__', '__missing__',
    '__reduce__', '__reduce_ex__', '__getinitargs__', '__getnewargs__',
    '__getstate__', '__setstate__', '__getformat__', '__setformat__',
    '__repr__', '__dir__', '__subclasses__', '__format__',
    '__getnewargs_ex__',
}


eleza _get_method(name, func):
    "Turns a callable object (like a mock) into a real function"
    eleza method(self, /, *args, **kw):
        rudisha func(self, *args, **kw)
    method.__name__ = name
    rudisha method


_magics = {
    '__%s__' % method kila method in
    ' '.join([magic_methods, numerics, inplace, right]).split()
}

# Magic methods used kila async `with` statements
_async_method_magics = {"__aenter__", "__aexit__", "__anext__"}
# Magic methods that are only used ukijumuisha async calls but are synchronous functions themselves
_sync_async_magics = {"__aiter__"}
_async_magics = _async_method_magics | _sync_async_magics

_all_sync_magics = _magics | _non_defaults
_all_magics = _all_sync_magics | _async_magics

_unsupported_magics = {
    '__getattr__', '__setattr__',
    '__init__', '__new__', '__prepare__',
    '__instancecheck__', '__subclasscheck__',
    '__del__'
}

_calculate_return_value = {
    '__hash__': lambda self: object.__hash__(self),
    '__str__': lambda self: object.__str__(self),
    '__sizeof__': lambda self: object.__sizeof__(self),
    '__fspath__': lambda self: f"{type(self).__name__}/{self._extract_mock_name()}/{id(self)}",
}

_return_values = {
    '__lt__': NotImplemented,
    '__gt__': NotImplemented,
    '__le__': NotImplemented,
    '__ge__': NotImplemented,
    '__int__': 1,
    '__contains__': Uongo,
    '__len__': 0,
    '__exit__': Uongo,
    '__complex__': 1j,
    '__float__': 1.0,
    '__bool__': Kweli,
    '__index__': 1,
    '__aexit__': Uongo,
}


eleza _get_eq(self):
    eleza __eq__(other):
        ret_val = self.__eq__._mock_return_value
        ikiwa ret_val ni sio DEFAULT:
            rudisha ret_val
        ikiwa self ni other:
            rudisha Kweli
        rudisha NotImplemented
    rudisha __eq__

eleza _get_ne(self):
    eleza __ne__(other):
        ikiwa self.__ne__._mock_return_value ni sio DEFAULT:
            rudisha DEFAULT
        ikiwa self ni other:
            rudisha Uongo
        rudisha NotImplemented
    rudisha __ne__

eleza _get_iter(self):
    eleza __iter__():
        ret_val = self.__iter__._mock_return_value
        ikiwa ret_val ni DEFAULT:
            rudisha iter([])
        # ikiwa ret_val was already an iterator, then calling iter on it should
        # rudisha the iterator unchanged
        rudisha iter(ret_val)
    rudisha __iter__

eleza _get_async_iter(self):
    eleza __aiter__():
        ret_val = self.__aiter__._mock_return_value
        ikiwa ret_val ni DEFAULT:
            rudisha _AsyncIterator(iter([]))
        rudisha _AsyncIterator(iter(ret_val))
    rudisha __aiter__

_side_effect_methods = {
    '__eq__': _get_eq,
    '__ne__': _get_ne,
    '__iter__': _get_iter,
    '__aiter__': _get_async_iter
}



eleza _set_return_value(mock, method, name):
    fixed = _return_values.get(name, DEFAULT)
    ikiwa fixed ni sio DEFAULT:
        method.return_value = fixed
        return

    return_calculator = _calculate_return_value.get(name)
    ikiwa return_calculator ni sio Tupu:
        return_value = return_calculator(mock)
        method.return_value = return_value
        return

    side_effector = _side_effect_methods.get(name)
    ikiwa side_effector ni sio Tupu:
        method.side_effect = side_effector(mock)



kundi MagicMixin(Base):
    eleza __init__(self, /, *args, **kw):
        self._mock_set_magics()  # make magic work kila kwargs kwenye init
        _safe_super(MagicMixin, self).__init__(*args, **kw)
        self._mock_set_magics()  # fix magic broken by upper level init


    eleza _mock_set_magics(self):
        orig_magics = _magics | _async_method_magics
        these_magics = orig_magics

        ikiwa getattr(self, "_mock_methods", Tupu) ni sio Tupu:
            these_magics = orig_magics.intersection(self._mock_methods)

            remove_magics = set()
            remove_magics = orig_magics - these_magics

            kila entry kwenye remove_magics:
                ikiwa entry kwenye type(self).__dict__:
                    # remove unneeded magic methods
                    delattr(self, entry)

        # don't overwrite existing attributes ikiwa called a second time
        these_magics = these_magics - set(type(self).__dict__)

        _type = type(self)
        kila entry kwenye these_magics:
            setattr(_type, entry, MagicProxy(entry, self))



kundi NonCallableMagicMock(MagicMixin, NonCallableMock):
    """A version of `MagicMock` that isn't callable."""
    eleza mock_add_spec(self, spec, spec_set=Uongo):
        """Add a spec to a mock. `spec` can either be an object ama a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes kutoka the mock.

        If `spec_set` ni Kweli then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)
        self._mock_set_magics()


kundi AsyncMagicMixin(MagicMixin):
    eleza __init__(self, /, *args, **kw):
        self._mock_set_magics()  # make magic work kila kwargs kwenye init
        _safe_super(AsyncMagicMixin, self).__init__(*args, **kw)
        self._mock_set_magics()  # fix magic broken by upper level init

kundi MagicMock(MagicMixin, Mock):
    """
    MagicMock ni a subkundi of Mock ukijumuisha default implementations
    of most of the magic methods. You can use MagicMock without having to
    configure the magic methods yourself.

    If you use the `spec` ama `spec_set` arguments then *only* magic
    methods that exist kwenye the spec will be created.

    Attributes na the rudisha value of a `MagicMock` will also be `MagicMocks`.
    """
    eleza mock_add_spec(self, spec, spec_set=Uongo):
        """Add a spec to a mock. `spec` can either be an object ama a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes kutoka the mock.

        If `spec_set` ni Kweli then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)
        self._mock_set_magics()



kundi MagicProxy(Base):
    eleza __init__(self, name, parent):
        self.name = name
        self.parent = parent

    eleza create_mock(self):
        entry = self.name
        parent = self.parent
        m = parent._get_child_mock(name=entry, _new_name=entry,
                                   _new_parent=parent)
        setattr(parent, entry, m)
        _set_return_value(parent, m, entry)
        rudisha m

    eleza __get__(self, obj, _type=Tupu):
        rudisha self.create_mock()


kundi AsyncMockMixin(Base):
    await_count = _delegating_property('await_count')
    await_args = _delegating_property('await_args')
    await_args_list = _delegating_property('await_args_list')

    eleza __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # asyncio.iscoroutinefunction() checks _is_coroutine property to say ikiwa an
        # object ni a coroutine. Without this check it looks to see ikiwa it ni a
        # function/method, which kwenye this case it ni sio (since it ni an
        # AsyncMock).
        # It ni set through __dict__ because when spec_set ni Kweli, this
        # attribute ni likely undefined.
        self.__dict__['_is_coroutine'] = asyncio.coroutines._is_coroutine
        self.__dict__['_mock_await_count'] = 0
        self.__dict__['_mock_await_args'] = Tupu
        self.__dict__['_mock_await_args_list'] = _CallList()
        code_mock = NonCallableMock(spec_set=CodeType)
        code_mock.co_flags = inspect.CO_COROUTINE
        self.__dict__['__code__'] = code_mock

    async eleza _mock_call(self, /, *args, **kwargs):
        jaribu:
            result = super()._mock_call(*args, **kwargs)
        tatizo (BaseException, StopIteration) kama e:
            side_effect = self.side_effect
            ikiwa side_effect ni sio Tupu na sio callable(side_effect):
                raise
            rudisha await _raise(e)

        _call = self.call_args

        async eleza proxy():
            jaribu:
                ikiwa inspect.isawaitable(result):
                    rudisha await result
                isipokua:
                    rudisha result
            mwishowe:
                self.await_count += 1
                self.await_args = _call
                self.await_args_list.append(_call)

        rudisha await proxy()

    eleza assert_awaited(self):
        """
        Assert that the mock was awaited at least once.
        """
        ikiwa self.await_count == 0:
            msg = f"Expected {self._mock_name ama 'mock'} to have been awaited."
            ashiria AssertionError(msg)

    eleza assert_awaited_once(self):
        """
        Assert that the mock was awaited exactly once.
        """
        ikiwa sio self.await_count == 1:
            msg = (f"Expected {self._mock_name ama 'mock'} to have been awaited once."
                   f" Awaited {self.await_count} times.")
            ashiria AssertionError(msg)

    eleza assert_awaited_with(self, /, *args, **kwargs):
        """
        Assert that the last await was ukijumuisha the specified arguments.
        """
        ikiwa self.await_args ni Tupu:
            expected = self._format_mock_call_signature(args, kwargs)
            ashiria AssertionError(f'Expected await: {expected}\nNot awaited')

        eleza _error_message():
            msg = self._format_mock_failure_message(args, kwargs, action='await')
            rudisha msg

        expected = self._call_matcher((args, kwargs))
        actual = self._call_matcher(self.await_args)
        ikiwa expected != actual:
            cause = expected ikiwa isinstance(expected, Exception) isipokua Tupu
            ashiria AssertionError(_error_message()) kutoka cause

    eleza assert_awaited_once_with(self, /, *args, **kwargs):
        """
        Assert that the mock was awaited exactly once na ukijumuisha the specified
        arguments.
        """
        ikiwa sio self.await_count == 1:
            msg = (f"Expected {self._mock_name ama 'mock'} to have been awaited once."
                   f" Awaited {self.await_count} times.")
            ashiria AssertionError(msg)
        rudisha self.assert_awaited_with(*args, **kwargs)

    eleza assert_any_await(self, /, *args, **kwargs):
        """
        Assert the mock has ever been awaited ukijumuisha the specified arguments.
        """
        expected = self._call_matcher((args, kwargs))
        actual = [self._call_matcher(c) kila c kwenye self.await_args_list]
        ikiwa expected haiko kwenye actual:
            cause = expected ikiwa isinstance(expected, Exception) isipokua Tupu
            expected_string = self._format_mock_call_signature(args, kwargs)
            ashiria AssertionError(
                '%s await sio found' % expected_string
            ) kutoka cause

    eleza assert_has_awaits(self, calls, any_order=Uongo):
        """
        Assert the mock has been awaited ukijumuisha the specified calls.
        The :attr:`await_args_list` list ni checked kila the awaits.

        If `any_order` ni Uongo (the default) then the awaits must be
        sequential. There can be extra calls before ama after the
        specified awaits.

        If `any_order` ni Kweli then the awaits can be kwenye any order, but
        they must all appear kwenye :attr:`await_args_list`.
        """
        expected = [self._call_matcher(c) kila c kwenye calls]
        cause = next((e kila e kwenye expected ikiwa isinstance(e, Exception)), Tupu)
        all_awaits = _CallList(self._call_matcher(c) kila c kwenye self.await_args_list)
        ikiwa sio any_order:
            ikiwa expected haiko kwenye all_awaits:
                ikiwa cause ni Tupu:
                    problem = 'Awaits sio found.'
                isipokua:
                    problem = ('Error processing expected awaits.\n'
                               'Errors: {}').format(
                                   [e ikiwa isinstance(e, Exception) isipokua Tupu
                                    kila e kwenye expected])
                ashiria AssertionError(
                    f'{problem}\n'
                    f'Expected: {_CallList(calls)}\n'
                    f'Actual: {self.await_args_list}'
                ) kutoka cause
            return

        all_awaits = list(all_awaits)

        not_found = []
        kila kall kwenye expected:
            jaribu:
                all_awaits.remove(kall)
            tatizo ValueError:
                not_found.append(kall)
        ikiwa not_found:
            ashiria AssertionError(
                '%r sio all found kwenye await list' % (tuple(not_found),)
            ) kutoka cause

    eleza assert_not_awaited(self):
        """
        Assert that the mock was never awaited.
        """
        ikiwa self.await_count != 0:
            msg = (f"Expected {self._mock_name ama 'mock'} to sio have been awaited."
                   f" Awaited {self.await_count} times.")
            ashiria AssertionError(msg)

    eleza reset_mock(self, /, *args, **kwargs):
        """
        See :func:`.Mock.reset_mock()`
        """
        super().reset_mock(*args, **kwargs)
        self.await_count = 0
        self.await_args = Tupu
        self.await_args_list = _CallList()


kundi AsyncMock(AsyncMockMixin, AsyncMagicMixin, Mock):
    """
    Enhance :class:`Mock` ukijumuisha features allowing to mock
    an async function.

    The :class:`AsyncMock` object will behave so the object is
    recognized kama an async function, na the result of a call ni an awaitable:

    >>> mock = AsyncMock()
    >>> asyncio.iscoroutinefunction(mock)
    Kweli
    >>> inspect.isawaitable(mock())
    Kweli


    The result of ``mock()`` ni an async function which will have the outcome
    of ``side_effect`` ama ``return_value``:

    - ikiwa ``side_effect`` ni a function, the async function will rudisha the
      result of that function,
    - ikiwa ``side_effect`` ni an exception, the async function will ashiria the
      exception,
    - ikiwa ``side_effect`` ni an iterable, the async function will rudisha the
      next value of the iterable, however, ikiwa the sequence of result is
      exhausted, ``StopIteration`` ni raised immediately,
    - ikiwa ``side_effect`` ni sio defined, the async function will rudisha the
      value defined by ``return_value``, hence, by default, the async function
      returns a new :class:`AsyncMock` object.

    If the outcome of ``side_effect`` ama ``return_value`` ni an async function,
    the mock async function obtained when the mock object ni called will be this
    async function itself (and sio an async function returning an async
    function).

    The test author can also specify a wrapped object ukijumuisha ``wraps``. In this
    case, the :class:`Mock` object behavior ni the same kama ukijumuisha an
    :class:`.Mock` object: the wrapped object may have methods
    defined kama async function functions.

    Based on Martin Richard's asynctest project.
    """


kundi _ANY(object):
    "A helper object that compares equal to everything."

    eleza __eq__(self, other):
        rudisha Kweli

    eleza __ne__(self, other):
        rudisha Uongo

    eleza __repr__(self):
        rudisha '<ANY>'

ANY = _ANY()



eleza _format_call_signature(name, args, kwargs):
    message = '%s(%%s)' % name
    formatted_args = ''
    args_string = ', '.join([repr(arg) kila arg kwenye args])
    kwargs_string = ', '.join([
        '%s=%r' % (key, value) kila key, value kwenye kwargs.items()
    ])
    ikiwa args_string:
        formatted_args = args_string
    ikiwa kwargs_string:
        ikiwa formatted_args:
            formatted_args += ', '
        formatted_args += kwargs_string

    rudisha message % formatted_args



kundi _Call(tuple):
    """
    A tuple kila holding the results of a call to a mock, either kwenye the form
    `(args, kwargs)` ama `(name, args, kwargs)`.

    If args ama kwargs are empty then a call tuple will compare equal to
    a tuple without those values. This makes comparisons less verbose::

        _Call(('name', (), {})) == ('name',)
        _Call(('name', (1,), {})) == ('name', (1,))
        _Call(((), {'a': 'b'})) == ({'a': 'b'},)

    The `_Call` object provides a useful shortcut kila comparing ukijumuisha call::

        _Call(((1, 2), {'a': 3})) == call(1, 2, a=3)
        _Call(('foo', (1, 2), {'a': 3})) == call.foo(1, 2, a=3)

    If the _Call has no name then it will match any name.
    """
    eleza __new__(cls, value=(), name='', parent=Tupu, two=Uongo,
                from_kall=Kweli):
        args = ()
        kwargs = {}
        _len = len(value)
        ikiwa _len == 3:
            name, args, kwargs = value
        lasivyo _len == 2:
            first, second = value
            ikiwa isinstance(first, str):
                name = first
                ikiwa isinstance(second, tuple):
                    args = second
                isipokua:
                    kwargs = second
            isipokua:
                args, kwargs = first, second
        lasivyo _len == 1:
            value, = value
            ikiwa isinstance(value, str):
                name = value
            lasivyo isinstance(value, tuple):
                args = value
            isipokua:
                kwargs = value

        ikiwa two:
            rudisha tuple.__new__(cls, (args, kwargs))

        rudisha tuple.__new__(cls, (name, args, kwargs))


    eleza __init__(self, value=(), name=Tupu, parent=Tupu, two=Uongo,
                 from_kall=Kweli):
        self._mock_name = name
        self._mock_parent = parent
        self._mock_from_kall = from_kall


    eleza __eq__(self, other):
        ikiwa other ni ANY:
            rudisha Kweli
        jaribu:
            len_other = len(other)
        tatizo TypeError:
            rudisha Uongo

        self_name = ''
        ikiwa len(self) == 2:
            self_args, self_kwargs = self
        isipokua:
            self_name, self_args, self_kwargs = self

        ikiwa (getattr(self, '_mock_parent', Tupu) na getattr(other, '_mock_parent', Tupu)
                na self._mock_parent != other._mock_parent):
            rudisha Uongo

        other_name = ''
        ikiwa len_other == 0:
            other_args, other_kwargs = (), {}
        lasivyo len_other == 3:
            other_name, other_args, other_kwargs = other
        lasivyo len_other == 1:
            value, = other
            ikiwa isinstance(value, tuple):
                other_args = value
                other_kwargs = {}
            lasivyo isinstance(value, str):
                other_name = value
                other_args, other_kwargs = (), {}
            isipokua:
                other_args = ()
                other_kwargs = value
        lasivyo len_other == 2:
            # could be (name, args) ama (name, kwargs) ama (args, kwargs)
            first, second = other
            ikiwa isinstance(first, str):
                other_name = first
                ikiwa isinstance(second, tuple):
                    other_args, other_kwargs = second, {}
                isipokua:
                    other_args, other_kwargs = (), second
            isipokua:
                other_args, other_kwargs = first, second
        isipokua:
            rudisha Uongo

        ikiwa self_name na other_name != self_name:
            rudisha Uongo

        # this order ni important kila ANY to work!
        rudisha (other_args, other_kwargs) == (self_args, self_kwargs)


    __ne__ = object.__ne__


    eleza __call__(self, /, *args, **kwargs):
        ikiwa self._mock_name ni Tupu:
            rudisha _Call(('', args, kwargs), name='()')

        name = self._mock_name + '()'
        rudisha _Call((self._mock_name, args, kwargs), name=name, parent=self)


    eleza __getattr__(self, attr):
        ikiwa self._mock_name ni Tupu:
            rudisha _Call(name=attr, from_kall=Uongo)
        name = '%s.%s' % (self._mock_name, attr)
        rudisha _Call(name=name, parent=self, from_kall=Uongo)


    eleza __getattribute__(self, attr):
        ikiwa attr kwenye tuple.__dict__:
            ashiria AttributeError
        rudisha tuple.__getattribute__(self, attr)


    eleza count(self, /, *args, **kwargs):
        rudisha self.__getattr__('count')(*args, **kwargs)

    eleza index(self, /, *args, **kwargs):
        rudisha self.__getattr__('index')(*args, **kwargs)

    eleza _get_call_arguments(self):
        ikiwa len(self) == 2:
            args, kwargs = self
        isipokua:
            name, args, kwargs = self

        rudisha args, kwargs

    @property
    eleza args(self):
        rudisha self._get_call_arguments()[0]

    @property
    eleza kwargs(self):
        rudisha self._get_call_arguments()[1]

    eleza __repr__(self):
        ikiwa sio self._mock_from_kall:
            name = self._mock_name ama 'call'
            ikiwa name.startswith('()'):
                name = 'call%s' % name
            rudisha name

        ikiwa len(self) == 2:
            name = 'call'
            args, kwargs = self
        isipokua:
            name, args, kwargs = self
            ikiwa sio name:
                name = 'call'
            lasivyo sio name.startswith('()'):
                name = 'call.%s' % name
            isipokua:
                name = 'call%s' % name
        rudisha _format_call_signature(name, args, kwargs)


    eleza call_list(self):
        """For a call object that represents multiple calls, `call_list`
        returns a list of all the intermediate calls kama well kama the
        final call."""
        vals = []
        thing = self
        wakati thing ni sio Tupu:
            ikiwa thing._mock_from_kall:
                vals.append(thing)
            thing = thing._mock_parent
        rudisha _CallList(reversed(vals))


call = _Call(from_kall=Uongo)


eleza create_autospec(spec, spec_set=Uongo, instance=Uongo, _parent=Tupu,
                    _name=Tupu, **kwargs):
    """Create a mock object using another object kama a spec. Attributes on the
    mock will use the corresponding attribute on the `spec` object kama their
    spec.

    Functions ama methods being mocked will have their arguments checked
    to check that they are called ukijumuisha the correct signature.

    If `spec_set` ni Kweli then attempting to set attributes that don't exist
    on the spec object will ashiria an `AttributeError`.

    If a kundi ni used kama a spec then the rudisha value of the mock (the
    instance of the class) will have the same spec. You can use a kundi kama the
    spec kila an instance object by pitaing `instance=Kweli`. The returned mock
    will only be callable ikiwa instances of the mock are callable.

    `create_autospec` also takes arbitrary keyword arguments that are pitaed to
    the constructor of the created mock."""
    ikiwa _is_list(spec):
        # can't pita a list instance to the mock constructor kama it will be
        # interpreted kama a list of strings
        spec = type(spec)

    is_type = isinstance(spec, type)
    is_async_func = _is_async_func(spec)
    _kwargs = {'spec': spec}
    ikiwa spec_set:
        _kwargs = {'spec_set': spec}
    lasivyo spec ni Tupu:
        # Tupu we mock ukijumuisha a normal mock without a spec
        _kwargs = {}
    ikiwa _kwargs na instance:
        _kwargs['_spec_as_instance'] = Kweli

    _kwargs.update(kwargs)

    Klass = MagicMock
    ikiwa inspect.isdatadescriptor(spec):
        # descriptors don't have a spec
        # because we don't know what type they return
        _kwargs = {}
    lasivyo is_async_func:
        ikiwa instance:
            ashiria RuntimeError("Instance can sio be Kweli when create_autospec "
                               "is mocking an async function")
        Klass = AsyncMock
    lasivyo sio _callable(spec):
        Klass = NonCallableMagicMock
    lasivyo is_type na instance na sio _instance_callable(spec):
        Klass = NonCallableMagicMock

    _name = _kwargs.pop('name', _name)

    _new_name = _name
    ikiwa _parent ni Tupu:
        # kila a top level object no _new_name should be set
        _new_name = ''

    mock = Klass(parent=_parent, _new_parent=_parent, _new_name=_new_name,
                 name=_name, **_kwargs)

    ikiwa isinstance(spec, FunctionTypes):
        # should only happen at the top level because we don't
        # recurse kila functions
        mock = _set_signature(mock, spec)
        ikiwa is_async_func:
            _setup_async_mock(mock)
    isipokua:
        _check_signature(spec, mock, is_type, instance)

    ikiwa _parent ni sio Tupu na sio instance:
        _parent._mock_children[_name] = mock

    ikiwa is_type na sio instance na 'return_value' haiko kwenye kwargs:
        mock.return_value = create_autospec(spec, spec_set, instance=Kweli,
                                            _name='()', _parent=mock)

    kila entry kwenye dir(spec):
        ikiwa _is_magic(entry):
            # MagicMock already does the useful magic methods kila us
            endelea

        # XXXX do we need a better way of getting attributes without
        # triggering code execution (?) Probably sio - we need the actual
        # object to mock it so we would rather trigger a property than mock
        # the property descriptor. Likewise we want to mock out dynamically
        # provided attributes.
        # XXXX what about attributes that ashiria exceptions other than
        # AttributeError on being fetched?
        # we could be resilient against it, ama catch na propagate the
        # exception when the attribute ni fetched kutoka the mock
        jaribu:
            original = getattr(spec, entry)
        tatizo AttributeError:
            endelea

        kwargs = {'spec': original}
        ikiwa spec_set:
            kwargs = {'spec_set': original}

        ikiwa sio isinstance(original, FunctionTypes):
            new = _SpecState(original, spec_set, mock, entry, instance)
            mock._mock_children[entry] = new
        isipokua:
            parent = mock
            ikiwa isinstance(spec, FunctionTypes):
                parent = mock.mock

            skipfirst = _must_skip(spec, entry, is_type)
            kwargs['_eat_self'] = skipfirst
            ikiwa asyncio.iscoroutinefunction(original):
                child_klass = AsyncMock
            isipokua:
                child_klass = MagicMock
            new = child_klass(parent=parent, name=entry, _new_name=entry,
                              _new_parent=parent,
                              **kwargs)
            mock._mock_children[entry] = new
            _check_signature(original, new, skipfirst=skipfirst)

        # so functions created ukijumuisha _set_signature become instance attributes,
        # *plus* their underlying mock exists kwenye _mock_children of the parent
        # mock. Adding to _mock_children may be unnecessary where we are also
        # setting kama an instance attribute?
        ikiwa isinstance(new, FunctionTypes):
            setattr(mock, entry, new)

    rudisha mock


eleza _must_skip(spec, entry, is_type):
    """
    Return whether we should skip the first argument on spec's `entry`
    attribute.
    """
    ikiwa sio isinstance(spec, type):
        ikiwa entry kwenye getattr(spec, '__dict__', {}):
            # instance attribute - shouldn't skip
            rudisha Uongo
        spec = spec.__class__

    kila klass kwenye spec.__mro__:
        result = klass.__dict__.get(entry, DEFAULT)
        ikiwa result ni DEFAULT:
            endelea
        ikiwa isinstance(result, (staticmethod, classmethod)):
            rudisha Uongo
        lasivyo isinstance(getattr(result, '__get__', Tupu), MethodWrapperTypes):
            # Normal method => skip ikiwa looked up on type
            # (ikiwa looked up on instance, self ni already skipped)
            rudisha is_type
        isipokua:
            rudisha Uongo

    # function ni a dynamically provided attribute
    rudisha is_type


kundi _SpecState(object):

    eleza __init__(self, spec, spec_set=Uongo, parent=Tupu,
                 name=Tupu, ids=Tupu, instance=Uongo):
        self.spec = spec
        self.ids = ids
        self.spec_set = spec_set
        self.parent = parent
        self.instance = instance
        self.name = name


FunctionTypes = (
    # python function
    type(create_autospec),
    # instance method
    type(ANY.__eq__),
)

MethodWrapperTypes = (
    type(ANY.__eq__.__get__),
)


file_spec = Tupu


eleza _to_stream(read_data):
    ikiwa isinstance(read_data, bytes):
        rudisha io.BytesIO(read_data)
    isipokua:
        rudisha io.StringIO(read_data)


eleza mock_open(mock=Tupu, read_data=''):
    """
    A helper function to create a mock to replace the use of `open`. It works
    kila `open` called directly ama used kama a context manager.

    The `mock` argument ni the mock object to configure. If `Tupu` (the
    default) then a `MagicMock` will be created kila you, ukijumuisha the API limited
    to methods ama attributes available on standard file handles.

    `read_data` ni a string kila the `read`, `readline` na `readlines` of the
    file handle to return.  This ni an empty string by default.
    """
    _read_data = _to_stream(read_data)
    _state = [_read_data, Tupu]

    eleza _readlines_side_effect(*args, **kwargs):
        ikiwa handle.readlines.return_value ni sio Tupu:
            rudisha handle.readlines.return_value
        rudisha _state[0].readlines(*args, **kwargs)

    eleza _read_side_effect(*args, **kwargs):
        ikiwa handle.read.return_value ni sio Tupu:
            rudisha handle.read.return_value
        rudisha _state[0].read(*args, **kwargs)

    eleza _readline_side_effect(*args, **kwargs):
        tuma kutoka _iter_side_effect()
        wakati Kweli:
            tuma _state[0].readline(*args, **kwargs)

    eleza _iter_side_effect():
        ikiwa handle.readline.return_value ni sio Tupu:
            wakati Kweli:
                tuma handle.readline.return_value
        kila line kwenye _state[0]:
            tuma line

    eleza _next_side_effect():
        ikiwa handle.readline.return_value ni sio Tupu:
            rudisha handle.readline.return_value
        rudisha next(_state[0])

    global file_spec
    ikiwa file_spec ni Tupu:
        agiza _io
        file_spec = list(set(dir(_io.TextIOWrapper)).union(set(dir(_io.BytesIO))))

    ikiwa mock ni Tupu:
        mock = MagicMock(name='open', spec=open)

    handle = MagicMock(spec=file_spec)
    handle.__enter__.return_value = handle

    handle.write.return_value = Tupu
    handle.read.return_value = Tupu
    handle.readline.return_value = Tupu
    handle.readlines.return_value = Tupu

    handle.read.side_effect = _read_side_effect
    _state[1] = _readline_side_effect()
    handle.readline.side_effect = _state[1]
    handle.readlines.side_effect = _readlines_side_effect
    handle.__iter__.side_effect = _iter_side_effect
    handle.__next__.side_effect = _next_side_effect

    eleza reset_data(*args, **kwargs):
        _state[0] = _to_stream(read_data)
        ikiwa handle.readline.side_effect == _state[1]:
            # Only reset the side effect ikiwa the user hasn't overridden it.
            _state[1] = _readline_side_effect()
            handle.readline.side_effect = _state[1]
        rudisha DEFAULT

    mock.side_effect = reset_data
    mock.return_value = handle
    rudisha mock


kundi PropertyMock(Mock):
    """
    A mock intended to be used kama a property, ama other descriptor, on a class.
    `PropertyMock` provides `__get__` na `__set__` methods so you can specify
    a rudisha value when it ni fetched.

    Fetching a `PropertyMock` instance kutoka an object calls the mock, with
    no args. Setting it calls the mock ukijumuisha the value being set.
    """
    eleza _get_child_mock(self, /, **kwargs):
        rudisha MagicMock(**kwargs)

    eleza __get__(self, obj, obj_type=Tupu):
        rudisha self()
    eleza __set__(self, obj, val):
        self(val)


eleza seal(mock):
    """Disable the automatic generation of child mocks.

    Given an input Mock, seals it to ensure no further mocks will be generated
    when accessing an attribute that was sio already defined.

    The operation recursively seals the mock pitaed in, meaning that
    the mock itself, any mocks generated by accessing one of its attributes,
    na all assigned mocks without a name ama spec will be sealed.
    """
    mock._mock_sealed = Kweli
    kila attr kwenye dir(mock):
        jaribu:
            m = getattr(mock, attr)
        tatizo AttributeError:
            endelea
        ikiwa sio isinstance(m, NonCallableMock):
            endelea
        ikiwa m._mock_new_parent ni mock:
            seal(m)


async eleza _raise(exception):
    ashiria exception


kundi _AsyncIterator:
    """
    Wraps an iterator kwenye an asynchronous iterator.
    """
    eleza __init__(self, iterator):
        self.iterator = iterator
        code_mock = NonCallableMock(spec_set=CodeType)
        code_mock.co_flags = inspect.CO_ITERABLE_COROUTINE
        self.__dict__['__code__'] = code_mock

    eleza __aiter__(self):
        rudisha self

    async eleza __anext__(self):
        jaribu:
            rudisha next(self.iterator)
        tatizo StopIteration:
            pita
        ashiria StopAsyncIteration
