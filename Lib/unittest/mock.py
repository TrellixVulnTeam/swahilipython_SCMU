# mock.py
# Test tools for mocking and patching.
# Maintained by Michael Foord
# Backport for other versions of Python available kutoka
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


_builtins = {name for name in dir(builtins) ikiwa not name.startswith('_')}

FILTER_DIR = True

# Workaround for issue #12370
# Without this, the __class__ properties wouldn't be set correctly
_safe_super = super

eleza _is_async_obj(obj):
    ikiwa _is_instance_mock(obj) and not isinstance(obj, AsyncMock):
        rudisha False
    rudisha asyncio.iscoroutinefunction(obj) or inspect.isawaitable(obj)


eleza _is_async_func(func):
    ikiwa getattr(func, '__code__', None):
        rudisha asyncio.iscoroutinefunction(func)
    else:
        rudisha False


eleza _is_instance_mock(obj):
    # can't use isinstance on Mock objects because they override __class__
    # The base kundi for all mocks is NonCallableMock
    rudisha issubclass(type(obj), NonCallableMock)


eleza _is_exception(obj):
    rudisha (
        isinstance(obj, BaseException) or
        isinstance(obj, type) and issubclass(obj, BaseException)
    )


eleza _extract_mock(obj):
    # Autospecced functions will rudisha a FunctionType with "mock" attribute
    # which is the actual mock object that needs to be used.
    ikiwa isinstance(obj, FunctionTypes) and hasattr(obj, 'mock'):
        rudisha obj.mock
    else:
        rudisha obj


eleza _get_signature_object(func, as_instance, eat_self):
    """
    Given an arbitrary, possibly callable object, try to create a suitable
    signature object.
    Return a (reduced func, signature) tuple, or None.
    """
    ikiwa isinstance(func, type) and not as_instance:
        # If it's a type and should be modelled as a type, use __init__.
        func = func.__init__
        # Skip the `self` argument in __init__
        eat_self = True
    elikiwa not isinstance(func, FunctionTypes):
        # If we really want to model an instance of the passed type,
        # __call__ should be looked up, not __init__.
        try:
            func = func.__call__
        except AttributeError:
            rudisha None
    ikiwa eat_self:
        sig_func = partial(func, None)
    else:
        sig_func = func
    try:
        rudisha func, inspect.signature(sig_func)
    except ValueError:
        # Certain callable types are not supported by inspect.signature()
        rudisha None


eleza _check_signature(func, mock, skipfirst, instance=False):
    sig = _get_signature_object(func, instance, skipfirst)
    ikiwa sig is None:
        return
    func, sig = sig
    eleza checksig(self, /, *args, **kwargs):
        sig.bind(*args, **kwargs)
    _copy_func_details(func, checksig)
    type(mock)._mock_check_sig = checksig
    type(mock).__signature__ = sig


eleza _copy_func_details(func, funcopy):
    # we explicitly don't copy func.__dict__ into this copy as it would
    # expose original attributes that should be mocked
    for attribute in (
        '__name__', '__doc__', '__text_signature__',
        '__module__', '__defaults__', '__kwdefaults__',
    ):
        try:
            setattr(funcopy, attribute, getattr(func, attribute))
        except AttributeError:
            pass


eleza _callable(obj):
    ikiwa isinstance(obj, type):
        rudisha True
    ikiwa isinstance(obj, (staticmethod, classmethod, MethodType)):
        rudisha _callable(obj.__func__)
    ikiwa getattr(obj, '__call__', None) is not None:
        rudisha True
    rudisha False


eleza _is_list(obj):
    # checks for list or tuples
    # XXXX badly named!
    rudisha type(obj) in (list, tuple)


eleza _instance_callable(obj):
    """Given an object, rudisha True ikiwa the object is callable.
    For classes, rudisha True ikiwa instances would be callable."""
    ikiwa not isinstance(obj, type):
        # already an instance
        rudisha getattr(obj, '__call__', None) is not None

    # *could* be broken by a kundi overriding __mro__ or __dict__ via
    # a metaclass
    for base in (obj,) + obj.__mro__:
        ikiwa base.__dict__.get('__call__') is not None:
            rudisha True
    rudisha False


eleza _set_signature(mock, original, instance=False):
    # creates a function with signature (*args, **kwargs) that delegates to a
    # mock. It still does signature checking by calling a lambda with the same
    # signature as the original.

    skipfirst = isinstance(original, type)
    result = _get_signature_object(original, instance, skipfirst)
    ikiwa result is None:
        rudisha mock
    func, sig = result
    eleza checksig(*args, **kwargs):
        sig.bind(*args, **kwargs)
    _copy_func_details(func, checksig)

    name = original.__name__
    ikiwa not name.isidentifier():
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
        ikiwa _is_instance_mock(ret) and not ret is mock:
            ret.reset_mock()

    funcopy.called = False
    funcopy.call_count = 0
    funcopy.call_args = None
    funcopy.call_args_list = _CallList()
    funcopy.method_calls = _CallList()
    funcopy.mock_calls = _CallList()

    funcopy.return_value = mock.return_value
    funcopy.side_effect = mock.side_effect
    funcopy._mock_children = mock._mock_children

    funcopy.assert_called_with = assert_called_with
    funcopy.assert_called_once_with = assert_called_once_with
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
    mock.await_args = None
    mock.await_args_list = _CallList()

    # Mock is not configured yet so the attributes are set
    # to a function and then the corresponding mock helper function
    # is called when the helper is accessed similar to _setup_func.
    eleza wrapper(attr, /, *args, **kwargs):
        rudisha getattr(mock.mock, attr)(*args, **kwargs)

    for attribute in ('assert_awaited',
                      'assert_awaited_once',
                      'assert_awaited_with',
                      'assert_awaited_once_with',
                      'assert_any_await',
                      'assert_has_awaits',
                      'assert_not_awaited'):

        # setattr(mock, attribute, wrapper) causes late binding
        # hence attribute will always be the last value in the loop
        # Use partial(wrapper, attribute) to ensure the attribute is bound
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
    """Access attributes to rudisha a named object, usable as a sentinel."""
    eleza __init__(self):
        self._sentinels = {}

    eleza __getattr__(self, name):
        ikiwa name == '__bases__':
            # Without this help(unittest.mock) raises an exception
            raise AttributeError
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
        ikiwa sig is None:
            rudisha getattr(self, _the_name)
        rudisha getattr(sig, name)
    eleza _set(self, value, name=name, _the_name=_the_name):
        sig = self._mock_delegate
        ikiwa sig is None:
            self.__dict__[_the_name] = value
        else:
            setattr(sig, name, value)

    rudisha property(_get, _set)



kundi _CallList(list):

    eleza __contains__(self, value):
        ikiwa not isinstance(value, list):
            rudisha list.__contains__(self, value)
        len_value = len(value)
        len_self = len(self)
        ikiwa len_value > len_self:
            rudisha False

        for i in range(0, len_self - len_value + 1):
            sub_list = self[i:i+len_value]
            ikiwa sub_list == value:
                rudisha True
        rudisha False

    eleza __repr__(self):
        rudisha pprint.pformat(list(self))


eleza _check_and_set_parent(parent, value, name, new_name):
    value = _extract_mock(value)

    ikiwa not _is_instance_mock(value):
        rudisha False
    ikiwa ((value._mock_name or value._mock_new_name) or
        (value._mock_parent is not None) or
        (value._mock_new_parent is not None)):
        rudisha False

    _parent = parent
    while _parent is not None:
        # setting a mock (value) as a child or rudisha value of itself
        # should not modify the mock
        ikiwa _parent is value:
            rudisha False
        _parent = _parent._mock_new_parent

    ikiwa new_name:
        value._mock_new_parent = parent
        value._mock_new_name = new_name
    ikiwa name:
        value._mock_parent = parent
        value._mock_name = name
    rudisha True

# Internal kundi to identify ikiwa we wrapped an iterator object or not.
kundi _MockIter(object):
    eleza __init__(self, obj):
        self.obj = iter(obj)
    eleza __next__(self):
        rudisha next(self.obj)

kundi Base(object):
    _mock_return_value = DEFAULT
    _mock_side_effect = None
    eleza __init__(self, /, *args, **kwargs):
        pass



kundi NonCallableMock(Base):
    """A non-callable version of `Mock`"""

    eleza __new__(cls, /, *args, **kw):
        # every instance has its own class
        # so we can create magic methods on the
        # kundi without stomping on other mocks
        bases = (cls,)
        ikiwa not issubclass(cls, AsyncMock):
            # Check ikiwa spec is an async object or function
            sig = inspect.signature(NonCallableMock.__init__)
            bound_args = sig.bind_partial(cls, *args, **kw).arguments
            spec_arg = [
                arg for arg in bound_args.keys()
                ikiwa arg.startswith('spec')
            ]
            ikiwa spec_arg:
                # what ikiwa spec_set is different than spec?
                ikiwa _is_async_obj(bound_args[spec_arg[0]]):
                    bases = (AsyncMockMixin, cls,)
        new = type(cls.__name__, bases, {'__doc__': cls.__doc__})
        instance = _safe_super(NonCallableMock, cls).__new__(new)
        rudisha instance


    eleza __init__(
            self, spec=None, wraps=None, name=None, spec_set=None,
            parent=None, _spec_state=None, _new_name='', _new_parent=None,
            _spec_as_instance=False, _eat_self=None, unsafe=False, **kwargs
        ):
        ikiwa _new_parent is None:
            _new_parent = parent

        __dict__ = self.__dict__
        __dict__['_mock_parent'] = parent
        __dict__['_mock_name'] = name
        __dict__['_mock_new_name'] = _new_name
        __dict__['_mock_new_parent'] = _new_parent
        __dict__['_mock_sealed'] = False

        ikiwa spec_set is not None:
            spec = spec_set
            spec_set = True
        ikiwa _eat_self is None:
            _eat_self = parent is not None

        self._mock_add_spec(spec, spec_set, _spec_as_instance, _eat_self)

        __dict__['_mock_children'] = {}
        __dict__['_mock_wraps'] = wraps
        __dict__['_mock_delegate'] = None

        __dict__['_mock_called'] = False
        __dict__['_mock_call_args'] = None
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
        Attach a mock as an attribute of this one, replacing its name and
        parent. Calls to the attached mock will be recorded in the
        `method_calls` and `mock_calls` attributes of this one."""
        inner_mock = _extract_mock(mock)

        inner_mock._mock_parent = None
        inner_mock._mock_new_parent = None
        inner_mock._mock_name = ''
        inner_mock._mock_new_name = None

        setattr(self, attribute, mock)


    eleza mock_add_spec(self, spec, spec_set=False):
        """Add a spec to a mock. `spec` can either be an object or a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes kutoka the mock.

        If `spec_set` is True then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)


    eleza _mock_add_spec(self, spec, spec_set, _spec_as_instance=False,
                       _eat_self=False):
        _spec_kundi = None
        _spec_signature = None
        _spec_asyncs = []

        for attr in dir(spec):
            ikiwa asyncio.iscoroutinefunction(getattr(spec, attr, None)):
                _spec_asyncs.append(attr)

        ikiwa spec is not None and not _is_list(spec):
            ikiwa isinstance(spec, type):
                _spec_kundi = spec
            else:
                _spec_kundi = type(spec)
            res = _get_signature_object(spec,
                                        _spec_as_instance, _eat_self)
            _spec_signature = res and res[1]

            spec = dir(spec)

        __dict__ = self.__dict__
        __dict__['_spec_class'] = _spec_class
        __dict__['_spec_set'] = spec_set
        __dict__['_spec_signature'] = _spec_signature
        __dict__['_mock_methods'] = spec
        __dict__['_spec_asyncs'] = _spec_asyncs

    eleza __get_return_value(self):
        ret = self._mock_return_value
        ikiwa self._mock_delegate is not None:
            ret = self._mock_delegate.return_value

        ikiwa ret is DEFAULT:
            ret = self._get_child_mock(
                _new_parent=self, _new_name='()'
            )
            self.return_value = ret
        rudisha ret


    eleza __set_return_value(self, value):
        ikiwa self._mock_delegate is not None:
            self._mock_delegate.return_value = value
        else:
            self._mock_return_value = value
            _check_and_set_parent(self, value, None, '()')

    __return_value_doc = "The value to be returned when the mock is called."
    return_value = property(__get_return_value, __set_return_value,
                            __return_value_doc)


    @property
    eleza __class__(self):
        ikiwa self._spec_kundi is None:
            rudisha type(self)
        rudisha self._spec_class

    called = _delegating_property('called')
    call_count = _delegating_property('call_count')
    call_args = _delegating_property('call_args')
    call_args_list = _delegating_property('call_args_list')
    mock_calls = _delegating_property('mock_calls')


    eleza __get_side_effect(self):
        delegated = self._mock_delegate
        ikiwa delegated is None:
            rudisha self._mock_side_effect
        sf = delegated.side_effect
        ikiwa (sf is not None and not callable(sf)
                and not isinstance(sf, _MockIter) and not _is_exception(sf)):
            sf = _MockIter(sf)
            delegated.side_effect = sf
        rudisha sf

    eleza __set_side_effect(self, value):
        value = _try_iter(value)
        delegated = self._mock_delegate
        ikiwa delegated is None:
            self._mock_side_effect = value
        else:
            delegated.side_effect = value

    side_effect = property(__get_side_effect, __set_side_effect)


    eleza reset_mock(self,  visited=None,*, return_value=False, side_effect=False):
        "Restore the mock object to its initial state."
        ikiwa visited is None:
            visited = []
        ikiwa id(self) in visited:
            return
        visited.append(id(self))

        self.called = False
        self.call_args = None
        self.call_count = 0
        self.mock_calls = _CallList()
        self.call_args_list = _CallList()
        self.method_calls = _CallList()

        ikiwa return_value:
            self._mock_return_value = DEFAULT
        ikiwa side_effect:
            self._mock_side_effect = None

        for child in self._mock_children.values():
            ikiwa isinstance(child, _SpecState) or child is _deleted:
                continue
            child.reset_mock(visited)

        ret = self._mock_return_value
        ikiwa _is_instance_mock(ret) and ret is not self:
            ret.reset_mock(visited)


    eleza configure_mock(self, /, **kwargs):
        """Set attributes on the mock through keyword arguments.

        Attributes plus rudisha values and side effects can be set on child
        mocks using standard dot notation and unpacking a dictionary in the
        method call:

        >>> attrs = {'method.return_value': 3, 'other.side_effect': KeyError}
        >>> mock.configure_mock(**attrs)"""
        for arg, val in sorted(kwargs.items(),
                               # we sort on the number of dots so that
                               # attributes are set before we set attributes on
                               # attributes
                               key=lambda entry: entry[0].count('.')):
            args = arg.split('.')
            final = args.pop()
            obj = self
            for entry in args:
                obj = getattr(obj, entry)
            setattr(obj, final, val)


    eleza __getattr__(self, name):
        ikiwa name in {'_mock_methods', '_mock_unsafe'}:
            raise AttributeError(name)
        elikiwa self._mock_methods is not None:
            ikiwa name not in self._mock_methods or name in _all_magics:
                raise AttributeError("Mock object has no attribute %r" % name)
        elikiwa _is_magic(name):
            raise AttributeError(name)
        ikiwa not self._mock_unsafe:
            ikiwa name.startswith(('assert', 'assret')):
                raise AttributeError("Attributes cannot start with 'assert' "
                                     "or 'assret'")

        result = self._mock_children.get(name)
        ikiwa result is _deleted:
            raise AttributeError(name)
        elikiwa result is None:
            wraps = None
            ikiwa self._mock_wraps is not None:
                # XXXX should we get the attribute without triggering code
                # execution?
                wraps = getattr(self._mock_wraps, name)

            result = self._get_child_mock(
                parent=self, name=name, wraps=wraps, _new_name=name,
                _new_parent=self
            )
            self._mock_children[name]  = result

        elikiwa isinstance(result, _SpecState):
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

        while _parent is not None:
            last = _parent

            _name_list.append(_parent._mock_new_name + dot)
            dot = '.'
            ikiwa _parent._mock_new_name == '()':
                dot = ''

            _parent = _parent._mock_new_parent

        _name_list = list(reversed(_name_list))
        _first = last._mock_name or 'mock'
        ikiwa len(_name_list) > 1:
            ikiwa _name_list[1] not in ('()', '().'):
                _first += '.'
        _name_list[0] = _first
        rudisha ''.join(_name_list)

    eleza __repr__(self):
        name = self._extract_mock_name()

        name_string = ''
        ikiwa name not in ('mock', 'mock.'):
            name_string = ' name=%r' % name

        spec_string = ''
        ikiwa self._spec_kundi is not None:
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
        ikiwa not FILTER_DIR:
            rudisha object.__dir__(self)

        extras = self._mock_methods or []
        kutoka_type = dir(type(self))
        kutoka_dict = list(self.__dict__)
        kutoka_child_mocks = [
            m_name for m_name, m_value in self._mock_children.items()
            ikiwa m_value is not _deleted]

        kutoka_type = [e for e in kutoka_type ikiwa not e.startswith('_')]
        kutoka_dict = [e for e in kutoka_dict ikiwa not e.startswith('_') or
                     _is_magic(e)]
        rudisha sorted(set(extras + kutoka_type + kutoka_dict + kutoka_child_mocks))


    eleza __setattr__(self, name, value):
        ikiwa name in _allowed_names:
            # property setters go through here
            rudisha object.__setattr__(self, name, value)
        elikiwa (self._spec_set and self._mock_methods is not None and
            name not in self._mock_methods and
            name not in self.__dict__):
            raise AttributeError("Mock object has no attribute '%s'" % name)
        elikiwa name in _unsupported_magics:
            msg = 'Attempting to set unsupported magic method %r.' % name
            raise AttributeError(msg)
        elikiwa name in _all_magics:
            ikiwa self._mock_methods is not None and name not in self._mock_methods:
                raise AttributeError("Mock object has no attribute '%s'" % name)

            ikiwa not _is_instance_mock(value):
                setattr(type(self), name, _get_method(name, value))
                original = value
                value = lambda *args, **kw: original(self, *args, **kw)
            else:
                # only set _new_name and not name so that mock_calls is tracked
                # but not method calls
                _check_and_set_parent(self, value, None, name)
                setattr(type(self), name, value)
                self._mock_children[name] = value
        elikiwa name == '__class__':
            self._spec_kundi = value
            return
        else:
            ikiwa _check_and_set_parent(self, value, name, name):
                self._mock_children[name] = value

        ikiwa self._mock_sealed and not hasattr(self, name):
            mock_name = f'{self._extract_mock_name()}.{name}'
            raise AttributeError(f'Cannot set {mock_name}')

        rudisha object.__setattr__(self, name, value)


    eleza __delattr__(self, name):
        ikiwa name in _all_magics and name in type(self).__dict__:
            delattr(type(self), name)
            ikiwa name not in self.__dict__:
                # for magic methods that are still MagicProxy objects and
                # not set on the instance itself
                return

        obj = self._mock_children.get(name, _missing)
        ikiwa name in self.__dict__:
            _safe_super(NonCallableMock, self).__delattr__(name)
        elikiwa obj is _deleted:
            raise AttributeError(name)
        ikiwa obj is not _missing:
            del self._mock_children[name]
        self._mock_children[name] = _deleted


    eleza _format_mock_call_signature(self, args, kwargs):
        name = self._mock_name or 'mock'
        rudisha _format_call_signature(name, args, kwargs)


    eleza _format_mock_failure_message(self, args, kwargs, action='call'):
        message = 'expected %s not found.\nExpected: %s\nActual: %s'
        expected_string = self._format_mock_call_signature(args, kwargs)
        call_args = self.call_args
        actual_string = self._format_mock_call_signature(*call_args)
        rudisha message % (action, expected_string, actual_string)


    eleza _get_call_signature_kutoka_name(self, name):
        """
        * If call objects are asserted against a method/function like obj.meth1
        then there could be no name for the call object to lookup. Hence just
        rudisha the spec_signature of the method/function being asserted against.
        * If the name is not empty then remove () and split by '.' to get
        list of names to iterate through the children until a potential
        match is found. A child mock is created only during attribute access
        so ikiwa we get a _SpecState then no attributes of the spec were accessed
        and can be safely exited.
        """
        ikiwa not name:
            rudisha self._spec_signature

        sig = None
        names = name.replace('()', '').split('.')
        children = self._mock_children

        for name in names:
            child = children.get(name)
            ikiwa child is None or isinstance(child, _SpecState):
                break
            else:
                children = child._mock_children
                sig = child._spec_signature

        rudisha sig


    eleza _call_matcher(self, _call):
        """
        Given a call (or simply an (args, kwargs) tuple), rudisha a
        comparison key suitable for matching with other calls.
        This is a best effort method which relies on the spec's signature,
        ikiwa available, or falls back on the arguments themselves.
        """

        ikiwa isinstance(_call, tuple) and len(_call) > 2:
            sig = self._get_call_signature_kutoka_name(_call[0])
        else:
            sig = self._spec_signature

        ikiwa sig is not None:
            ikiwa len(_call) == 2:
                name = ''
                args, kwargs = _call
            else:
                name, args, kwargs = _call
            try:
                rudisha name, sig.bind(*args, **kwargs)
            except TypeError as e:
                rudisha e.with_traceback(None)
        else:
            rudisha _call

    eleza assert_not_called(self):
        """assert that the mock was never called.
        """
        ikiwa self.call_count != 0:
            msg = ("Expected '%s' to not have been called. Called %s times.%s"
                   % (self._mock_name or 'mock',
                      self.call_count,
                      self._calls_repr()))
            raise AssertionError(msg)

    eleza assert_called(self):
        """assert that the mock was called at least once
        """
        ikiwa self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
            raise AssertionError(msg)

    eleza assert_called_once(self):
        """assert that the mock was called only once.
        """
        ikiwa not self.call_count == 1:
            msg = ("Expected '%s' to have been called once. Called %s times.%s"
                   % (self._mock_name or 'mock',
                      self.call_count,
                      self._calls_repr()))
            raise AssertionError(msg)

    eleza assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.

        Raises an AssertionError ikiwa the args and keyword args passed in are
        different to the last call to the mock."""
        ikiwa self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\nActual: %s'
                    % (expected, actual))
            raise AssertionError(error_message)

        eleza _error_message():
            msg = self._format_mock_failure_message(args, kwargs)
            rudisha msg
        expected = self._call_matcher((args, kwargs))
        actual = self._call_matcher(self.call_args)
        ikiwa expected != actual:
            cause = expected ikiwa isinstance(expected, Exception) else None
            raise AssertionError(_error_message()) kutoka cause


    eleza assert_called_once_with(self, /, *args, **kwargs):
        """assert that the mock was called exactly once and that that call was
        with the specified arguments."""
        ikiwa not self.call_count == 1:
            msg = ("Expected '%s' to be called once. Called %s times.%s"
                   % (self._mock_name or 'mock',
                      self.call_count,
                      self._calls_repr()))
            raise AssertionError(msg)
        rudisha self.assert_called_with(*args, **kwargs)


    eleza assert_has_calls(self, calls, any_order=False):
        """assert the mock has been called with the specified calls.
        The `mock_calls` list is checked for the calls.

        If `any_order` is False (the default) then the calls must be
        sequential. There can be extra calls before or after the
        specified calls.

        If `any_order` is True then the calls can be in any order, but
        they must all appear in `mock_calls`."""
        expected = [self._call_matcher(c) for c in calls]
        cause = next((e for e in expected ikiwa isinstance(e, Exception)), None)
        all_calls = _CallList(self._call_matcher(c) for c in self.mock_calls)
        ikiwa not any_order:
            ikiwa expected not in all_calls:
                ikiwa cause is None:
                    problem = 'Calls not found.'
                else:
                    problem = ('Error processing expected calls.\n'
                               'Errors: {}').format(
                                   [e ikiwa isinstance(e, Exception) else None
                                    for e in expected])
                raise AssertionError(
                    f'{problem}\n'
                    f'Expected: {_CallList(calls)}'
                    f'{self._calls_repr(prefix="Actual").rstrip(".")}'
                ) kutoka cause
            return

        all_calls = list(all_calls)

        not_found = []
        for kall in expected:
            try:
                all_calls.remove(kall)
            except ValueError:
                not_found.append(kall)
        ikiwa not_found:
            raise AssertionError(
                '%r does not contain all of %r in its call list, '
                'found %r instead' % (self._mock_name or 'mock',
                                      tuple(not_found), all_calls)
            ) kutoka cause


    eleza assert_any_call(self, /, *args, **kwargs):
        """assert the mock has been called with the specified arguments.

        The assert passes ikiwa the mock has *ever* been called, unlike
        `assert_called_with` and `assert_called_once_with` that only pass if
        the call is the most recent one."""
        expected = self._call_matcher((args, kwargs))
        actual = [self._call_matcher(c) for c in self.call_args_list]
        ikiwa expected not in actual:
            cause = expected ikiwa isinstance(expected, Exception) else None
            expected_string = self._format_mock_call_signature(args, kwargs)
            raise AssertionError(
                '%s call not found' % expected_string
            ) kutoka cause


    eleza _get_child_mock(self, /, **kw):
        """Create the child mocks for attributes and rudisha value.
        By default child mocks will be the same type as the parent.
        Subclasses of Mock may want to override this to customize the way
        child mocks are made.

        For non-callable mocks the callable variant will be used (rather than
        any custom subclass)."""
        _new_name = kw.get("_new_name")
        ikiwa _new_name in self.__dict__['_spec_asyncs']:
            rudisha AsyncMock(**kw)

        _type = type(self)
        ikiwa issubclass(_type, MagicMock) and _new_name in _async_method_magics:
            # Any asynchronous magic becomes an AsyncMock
            klass = AsyncMock
        elikiwa issubclass(_type, AsyncMockMixin):
            ikiwa (_new_name in _all_sync_magics or
                    self._mock_methods and _new_name in self._mock_methods):
                # Any synchronous method on AsyncMock becomes a MagicMock
                klass = MagicMock
            else:
                klass = AsyncMock
        elikiwa not issubclass(_type, CallableMixin):
            ikiwa issubclass(_type, NonCallableMagicMock):
                klass = MagicMock
            elikiwa issubclass(_type, NonCallableMock):
                klass = Mock
        else:
            klass = _type.__mro__[1]

        ikiwa self._mock_sealed:
            attribute = "." + kw["name"] ikiwa "name" in kw else "()"
            mock_name = self._extract_mock_name() + attribute
            raise AttributeError(mock_name)

        rudisha klass(**kw)


    eleza _calls_repr(self, prefix="Calls"):
        """Renders self.mock_calls as a string.

        Example: "\nCalls: [call(1), call(2)]."

        If self.mock_calls is empty, an empty string is returned. The
        output will be truncated ikiwa very long.
        """
        ikiwa not self.mock_calls:
            rudisha ""
        rudisha f"\n{prefix}: {safe_repr(self.mock_calls)}."



eleza _try_iter(obj):
    ikiwa obj is None:
        rudisha obj
    ikiwa _is_exception(obj):
        rudisha obj
    ikiwa _callable(obj):
        rudisha obj
    try:
        rudisha iter(obj)
    except TypeError:
        # XXXX backwards compatibility
        # but this will blow up on first call - so maybe we should fail early?
        rudisha obj


kundi CallableMixin(Base):

    eleza __init__(self, spec=None, side_effect=None, return_value=DEFAULT,
                 wraps=None, name=None, spec_set=None, parent=None,
                 _spec_state=None, _new_name='', _new_parent=None, **kwargs):
        self.__dict__['_mock_return_value'] = return_value
        _safe_super(CallableMixin, self).__init__(
            spec, wraps, name, spec_set, parent,
            _spec_state, _new_name, _new_parent, **kwargs
        )

        self.side_effect = side_effect


    eleza _mock_check_sig(self, /, *args, **kwargs):
        # stub method that can be replaced with one with a specific signature
        pass


    eleza __call__(self, /, *args, **kwargs):
        # can't use self in-case a function / method we are mocking uses self
        # in the signature
        self._mock_check_sig(*args, **kwargs)
        self._increment_mock_call(*args, **kwargs)
        rudisha self._mock_call(*args, **kwargs)


    eleza _mock_call(self, /, *args, **kwargs):
        rudisha self._execute_mock_call(*args, **kwargs)

    eleza _increment_mock_call(self, /, *args, **kwargs):
        self.called = True
        self.call_count += 1

        # handle call_args
        # needs to be set here so assertions on call arguments pass before
        # execution in the case of awaited calls
        _call = _Call((args, kwargs), two=True)
        self.call_args = _call
        self.call_args_list.append(_call)

        # initial stuff for method_calls:
        do_method_calls = self._mock_parent is not None
        method_call_name = self._mock_name

        # initial stuff for mock_calls:
        mock_call_name = self._mock_new_name
        is_a_call = mock_call_name == '()'
        self.mock_calls.append(_Call(('', args, kwargs)))

        # follow up the chain of mocks:
        _new_parent = self._mock_new_parent
        while _new_parent is not None:

            # handle method_calls:
            ikiwa do_method_calls:
                _new_parent.method_calls.append(_Call((method_call_name, args, kwargs)))
                do_method_calls = _new_parent._mock_parent is not None
                ikiwa do_method_calls:
                    method_call_name = _new_parent._mock_name + '.' + method_call_name

            # handle mock_calls:
            this_mock_call = _Call((mock_call_name, args, kwargs))
            _new_parent.mock_calls.append(this_mock_call)

            ikiwa _new_parent._mock_new_name:
                ikiwa is_a_call:
                    dot = ''
                else:
                    dot = '.'
                is_a_call = _new_parent._mock_new_name == '()'
                mock_call_name = _new_parent._mock_new_name + dot + mock_call_name

            # follow the parental chain:
            _new_parent = _new_parent._mock_new_parent

    eleza _execute_mock_call(self, /, *args, **kwargs):
        # seperate kutoka _increment_mock_call so that awaited functions are
        # executed seperately kutoka their call

        effect = self.side_effect
        ikiwa effect is not None:
            ikiwa _is_exception(effect):
                raise effect
            elikiwa not _callable(effect):
                result = next(effect)
                ikiwa _is_exception(result):
                    raise result
            else:
                result = effect(*args, **kwargs)

            ikiwa result is not DEFAULT:
                rudisha result

        ikiwa self._mock_return_value is not DEFAULT:
            rudisha self.return_value

        ikiwa self._mock_wraps is not None:
            rudisha self._mock_wraps(*args, **kwargs)

        rudisha self.return_value



kundi Mock(CallableMixin, NonCallableMock):
    """
    Create a new `Mock` object. `Mock` takes several optional arguments
    that specify the behaviour of the Mock object:

    * `spec`: This can be either a list of strings or an existing object (a
      kundi or instance) that acts as the specification for the mock object. If
      you pass in an object then a list of strings is formed by calling dir on
      the object (excluding unsupported magic attributes and methods). Accessing
      any attribute not in this list will raise an `AttributeError`.

      If `spec` is an object (rather than a list of strings) then
      `mock.__class__` returns the kundi of the spec object. This allows mocks
      to pass `isinstance` tests.

    * `spec_set`: A stricter variant of `spec`. If used, attempting to *set*
      or get an attribute on the mock that isn't on the object passed as
      `spec_set` will raise an `AttributeError`.

    * `side_effect`: A function to be called whenever the Mock is called. See
      the `side_effect` attribute. Useful for raising exceptions or
      dynamically changing rudisha values. The function is called with the same
      arguments as the mock, and unless it returns `DEFAULT`, the return
      value of this function is used as the rudisha value.

      If `side_effect` is an iterable then each call to the mock will return
      the next value kutoka the iterable. If any of the members of the iterable
      are exceptions they will be raised instead of returned.

    * `return_value`: The value returned when the mock is called. By default
      this is a new Mock (created on first access). See the
      `return_value` attribute.

    * `wraps`: Item for the mock object to wrap. If `wraps` is not None then
      calling the Mock will pass the call through to the wrapped object
      (returning the real result). Attribute access on the mock will rudisha a
      Mock object that wraps the corresponding attribute of the wrapped object
      (so attempting to access an attribute that doesn't exist will raise an
      `AttributeError`).

      If the mock has an explicit `return_value` set then calls are not passed
      to the wrapped object and the `return_value` is returned instead.

    * `name`: If the mock has a name then it will be used in the repr of the
      mock. This can be useful for debugging. The name is propagated to child
      mocks.

    Mocks can also be called with arbitrary keyword arguments. These will be
    used to set attributes on the mock after it is created.
    """


eleza _dot_lookup(thing, comp, import_path):
    try:
        rudisha getattr(thing, comp)
    except AttributeError:
        __import__(import_path)
        rudisha getattr(thing, comp)


eleza _importer(target):
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    for comp in components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    rudisha thing


eleza _is_started(patcher):
    # XXXX horrible
    rudisha hasattr(patcher, 'is_local')


kundi _patch(object):

    attribute_name = None
    _active_patches = []

    eleza __init__(
            self, getter, attribute, new, spec, create,
            spec_set, autospec, new_callable, kwargs
        ):
        ikiwa new_callable is not None:
            ikiwa new is not DEFAULT:
                raise ValueError(
                    "Cannot use 'new' and 'new_callable' together"
                )
            ikiwa autospec is not None:
                raise ValueError(
                    "Cannot use 'autospec' and 'new_callable' together"
                )

        self.getter = getter
        self.attribute = attribute
        self.new = new
        self.new_callable = new_callable
        self.spec = spec
        self.create = create
        self.has_local = False
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
            p.copy() for p in self.additional_patchers
        ]
        rudisha patcher


    eleza __call__(self, func):
        ikiwa isinstance(func, type):
            rudisha self.decorate_class(func)
        ikiwa inspect.iscoroutinefunction(func):
            rudisha self.decorate_async_callable(func)
        rudisha self.decorate_callable(func)


    eleza decorate_class(self, klass):
        for attr in dir(klass):
            ikiwa not attr.startswith(patch.TEST_PREFIX):
                continue

            attr_value = getattr(klass, attr)
            ikiwa not hasattr(attr_value, "__call__"):
                continue

            patcher = self.copy()
            setattr(klass, attr, patcher(attr_value))
        rudisha klass


    @contextlib.contextmanager
    eleza decoration_helper(self, patched, args, keywargs):
        extra_args = []
        entered_patchers = []
        patching = None

        exc_info = tuple()
        try:
            for patching in patched.patchings:
                arg = patching.__enter__()
                entered_patchers.append(patching)
                ikiwa patching.attribute_name is not None:
                    keywargs.update(arg)
                elikiwa patching.new is DEFAULT:
                    extra_args.append(arg)

            args += tuple(extra_args)
            yield (args, keywargs)
        except:
            ikiwa (patching not in entered_patchers and
                _is_started(patching)):
                # the patcher may have been started, but an exception
                # raised whilst entering one of its additional_patchers
                entered_patchers.append(patching)
            # Pass the exception to __exit__
            exc_info = sys.exc_info()
            # re-raise the exception
            raise
        finally:
            for patching in reversed(entered_patchers):
                patching.__exit__(*exc_info)


    eleza decorate_callable(self, func):
        # NB. Keep the method in sync with decorate_async_callable()
        ikiwa hasattr(func, 'patchings'):
            func.patchings.append(self)
            rudisha func

        @wraps(func)
        eleza patched(*args, **keywargs):
            with self.decoration_helper(patched,
                                        args,
                                        keywargs) as (newargs, newkeywargs):
                rudisha func(*newargs, **newkeywargs)

        patched.patchings = [self]
        rudisha patched


    eleza decorate_async_callable(self, func):
        # NB. Keep the method in sync with decorate_callable()
        ikiwa hasattr(func, 'patchings'):
            func.patchings.append(self)
            rudisha func

        @wraps(func)
        async eleza patched(*args, **keywargs):
            with self.decoration_helper(patched,
                                        args,
                                        keywargs) as (newargs, newkeywargs):
                rudisha await func(*newargs, **newkeywargs)

        patched.patchings = [self]
        rudisha patched


    eleza get_original(self):
        target = self.getter()
        name = self.attribute

        original = DEFAULT
        local = False

        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True

        ikiwa name in _builtins and isinstance(target, ModuleType):
            self.create = True

        ikiwa not self.create and original is DEFAULT:
            raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
        rudisha original, local


    eleza __enter__(self):
        """Perform the patch."""
        new, spec, spec_set = self.new, self.spec, self.spec_set
        autospec, kwargs = self.autospec, self.kwargs
        new_callable = self.new_callable
        self.target = self.getter()

        # normalise False to None
        ikiwa spec is False:
            spec = None
        ikiwa spec_set is False:
            spec_set = None
        ikiwa autospec is False:
            autospec = None

        ikiwa spec is not None and autospec is not None:
            raise TypeError("Can't specify spec and autospec")
        ikiwa ((spec is not None or autospec is not None) and
            spec_set not in (True, None)):
            raise TypeError("Can't provide explicit spec_set *and* spec or autospec")

        original, local = self.get_original()

        ikiwa new is DEFAULT and autospec is None:
            inherit = False
            ikiwa spec is True:
                # set spec to the object we are replacing
                spec = original
                ikiwa spec_set is True:
                    spec_set = original
                    spec = None
            elikiwa spec is not None:
                ikiwa spec_set is True:
                    spec_set = spec
                    spec = None
            elikiwa spec_set is True:
                spec_set = original

            ikiwa spec is not None or spec_set is not None:
                ikiwa original is DEFAULT:
                    raise TypeError("Can't use 'spec' with create=True")
                ikiwa isinstance(original, type):
                    # If we're patching out a kundi and there is a spec
                    inherit = True
            ikiwa spec is None and _is_async_obj(original):
                Klass = AsyncMock
            else:
                Klass = MagicMock
            _kwargs = {}
            ikiwa new_callable is not None:
                Klass = new_callable
            elikiwa spec is not None or spec_set is not None:
                this_spec = spec
                ikiwa spec_set is not None:
                    this_spec = spec_set
                ikiwa _is_list(this_spec):
                    not_callable = '__call__' not in this_spec
                else:
                    not_callable = not callable(this_spec)
                ikiwa _is_async_obj(this_spec):
                    Klass = AsyncMock
                elikiwa not_callable:
                    Klass = NonCallableMagicMock

            ikiwa spec is not None:
                _kwargs['spec'] = spec
            ikiwa spec_set is not None:
                _kwargs['spec_set'] = spec_set

            # add a name to mocks
            ikiwa (isinstance(Klass, type) and
                issubclass(Klass, NonCallableMock) and self.attribute):
                _kwargs['name'] = self.attribute

            _kwargs.update(kwargs)
            new = Klass(**_kwargs)

            ikiwa inherit and _is_instance_mock(new):
                # we can only tell ikiwa the instance should be callable ikiwa the
                # spec is not a list
                this_spec = spec
                ikiwa spec_set is not None:
                    this_spec = spec_set
                ikiwa (not _is_list(this_spec) and not
                    _instance_callable(this_spec)):
                    Klass = NonCallableMagicMock

                _kwargs.pop('name')
                new.return_value = Klass(_new_parent=new, _new_name='()',
                                         **_kwargs)
        elikiwa autospec is not None:
            # spec is ignored, new *must* be default, spec_set is treated
            # as a boolean. Should we check spec is not None and that spec_set
            # is a bool?
            ikiwa new is not DEFAULT:
                raise TypeError(
                    "autospec creates the mock for you. Can't specify "
                    "autospec and new."
                )
            ikiwa original is DEFAULT:
                raise TypeError("Can't use 'autospec' with create=True")
            spec_set = bool(spec_set)
            ikiwa autospec is True:
                autospec = original

            new = create_autospec(autospec, spec_set=spec_set,
                                  _name=self.attribute, **kwargs)
        elikiwa kwargs:
            # can't set keyword args when we aren't creating the mock
            # XXXX If new is a Mock we could call new.configure_mock(**kwargs)
            raise TypeError("Can't pass kwargs to a mock we aren't creating")

        new_attr = new

        self.temp_original = original
        self.is_local = local
        setattr(self.target, self.attribute, new_attr)
        ikiwa self.attribute_name is not None:
            extra_args = {}
            ikiwa self.new is DEFAULT:
                extra_args[self.attribute_name] =  new
            for patching in self.additional_patchers:
                arg = patching.__enter__()
                ikiwa patching.new is DEFAULT:
                    extra_args.update(arg)
            rudisha extra_args

        rudisha new


    eleza __exit__(self, *exc_info):
        """Undo the patch."""
        ikiwa not _is_started(self):
            return

        ikiwa self.is_local and self.temp_original is not DEFAULT:
            setattr(self.target, self.attribute, self.temp_original)
        else:
            delattr(self.target, self.attribute)
            ikiwa not self.create and (not hasattr(self.target, self.attribute) or
                        self.attribute in ('__doc__', '__module__',
                                           '__defaults__', '__annotations__',
                                           '__kwdefaults__')):
                # needed for proxy objects like django settings
                setattr(self.target, self.attribute, self.temp_original)

        del self.temp_original
        del self.is_local
        del self.target
        for patcher in reversed(self.additional_patchers):
            ikiwa _is_started(patcher):
                patcher.__exit__(*exc_info)


    eleza start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        self._active_patches.append(self)
        rudisha result


    eleza stop(self):
        """Stop an active patch."""
        try:
            self._active_patches.remove(self)
        except ValueError:
            # If the patch hasn't been started this will fail
            pass

        rudisha self.__exit__()



eleza _get_target(target):
    try:
        target, attribute = target.rsplit('.', 1)
    except (TypeError, ValueError):
        raise TypeError("Need a valid target to patch. You supplied: %r" %
                        (target,))
    getter = lambda: _importer(target)
    rudisha getter, attribute


eleza _patch_object(
        target, attribute, new=DEFAULT, spec=None,
        create=False, spec_set=None, autospec=None,
        new_callable=None, **kwargs
    ):
    """
    patch the named member (`attribute`) on an object (`target`) with a mock
    object.

    `patch.object` can be used as a decorator, kundi decorator or a context
    manager. Arguments `new`, `spec`, `create`, `spec_set`,
    `autospec` and `new_callable` have the same meaning as for `patch`. Like
    `patch`, `patch.object` takes arbitrary keyword arguments for configuring
    the mock object it creates.

    When used as a kundi decorator `patch.object` honours `patch.TEST_PREFIX`
    for choosing which methods to wrap.
    """
    getter = lambda: target
    rudisha _patch(
        getter, attribute, new, spec, create,
        spec_set, autospec, new_callable, kwargs
    )


eleza _patch_multiple(target, spec=None, create=False, spec_set=None,
                    autospec=None, new_callable=None, **kwargs):
    """Perform multiple patches in a single call. It takes the object to be
    patched (either as an object or a string to fetch the object by agizaing)
    and keyword arguments for the patches::

        with patch.multiple(settings, FIRST_PATCH='one', SECOND_PATCH='two'):
            ...

    Use `DEFAULT` as the value ikiwa you want `patch.multiple` to create
    mocks for you. In this case the created mocks are passed into a decorated
    function by keyword, and a dictionary is returned when `patch.multiple` is
    used as a context manager.

    `patch.multiple` can be used as a decorator, kundi decorator or a context
    manager. The arguments `spec`, `spec_set`, `create`,
    `autospec` and `new_callable` have the same meaning as for `patch`. These
    arguments will be applied to *all* patches done by `patch.multiple`.

    When used as a kundi decorator `patch.multiple` honours `patch.TEST_PREFIX`
    for choosing which methods to wrap.
    """
    ikiwa type(target) is str:
        getter = lambda: _importer(target)
    else:
        getter = lambda: target

    ikiwa not kwargs:
        raise ValueError(
            'Must supply at least one keyword argument with patch.multiple'
        )
    # need to wrap in a list for python 3, where items is a view
    items = list(kwargs.items())
    attribute, new = items[0]
    patcher = _patch(
        getter, attribute, new, spec, create, spec_set,
        autospec, new_callable, {}
    )
    patcher.attribute_name = attribute
    for attribute, new in items[1:]:
        this_patcher = _patch(
            getter, attribute, new, spec, create, spec_set,
            autospec, new_callable, {}
        )
        this_patcher.attribute_name = attribute
        patcher.additional_patchers.append(this_patcher)
    rudisha patcher


eleza patch(
        target, new=DEFAULT, spec=None, create=False,
        spec_set=None, autospec=None, new_callable=None, **kwargs
    ):
    """
    `patch` acts as a function decorator, kundi decorator or a context
    manager. Inside the body of the function or with statement, the `target`
    is patched with a `new` object. When the function/with statement exits
    the patch is undone.

    If `new` is omitted, then the target is replaced with an
    `AsyncMock ikiwa the patched object is an async function or a
    `MagicMock` otherwise. If `patch` is used as a decorator and `new` is
    omitted, the created mock is passed in as an extra argument to the
    decorated function. If `patch` is used as a context manager the created
    mock is returned by the context manager.

    `target` should be a string in the form `'package.module.ClassName'`. The
    `target` is imported and the specified object replaced with the `new`
    object, so the `target` must be agizaable kutoka the environment you are
    calling `patch` kutoka. The target is imported when the decorated function
    is executed, not at decoration time.

    The `spec` and `spec_set` keyword arguments are passed to the `MagicMock`
    ikiwa patch is creating one for you.

    In addition you can pass `spec=True` or `spec_set=True`, which causes
    patch to pass in the object being mocked as the spec/spec_set object.

    `new_callable` allows you to specify a different class, or callable object,
    that will be called to create the `new` object. By default `AsyncMock` is
    used for async functions and `MagicMock` for the rest.

    A more powerful form of `spec` is `autospec`. If you set `autospec=True`
    then the mock will be created with a spec kutoka the object being replaced.
    All attributes of the mock will also have the spec of the corresponding
    attribute of the object being replaced. Methods and functions being
    mocked will have their arguments checked and will raise a `TypeError` if
    they are called with the wrong signature. For mocks replacing a class,
    their rudisha value (the 'instance') will have the same spec as the class.

    Instead of `autospec=True` you can pass `autospec=some_object` to use an
    arbitrary object as the spec instead of the one being replaced.

    By default `patch` will fail to replace attributes that don't exist. If
    you pass in `create=True`, and the attribute doesn't exist, patch will
    create the attribute for you when the patched function is called, and
    delete it again afterwards. This is useful for writing tests against
    attributes that your production code creates at runtime. It is off by
    default because it can be dangerous. With it switched on you can write
    passing tests against APIs that don't actually exist!

    Patch can be used as a `TestCase` kundi decorator. It works by
    decorating each test method in the class. This reduces the boilerplate
    code when your test methods share a common patchings set. `patch` finds
    tests by looking for method names that start with `patch.TEST_PREFIX`.
    By default this is `test`, which matches the way `unittest` finds tests.
    You can specify an alternative prefix by setting `patch.TEST_PREFIX`.

    Patch can be used as a context manager, with the with statement. Here the
    patching applies to the indented block after the with statement. If you
    use "as" then the patched object will be bound to the name after the
    "as"; very useful ikiwa `patch` is creating a mock object for you.

    `patch` takes arbitrary keyword arguments. These will be passed to
    the `Mock` (or `new_callable`) on construction.

    `patch.dict(...)`, `patch.multiple(...)` and `patch.object(...)` are
    available for alternate use-cases.
    """
    getter, attribute = _get_target(target)
    rudisha _patch(
        getter, attribute, new, spec, create,
        spec_set, autospec, new_callable, kwargs
    )


kundi _patch_dict(object):
    """
    Patch a dictionary, or dictionary like object, and restore the dictionary
    to its original state after the test.

    `in_dict` can be a dictionary or a mapping like container. If it is a
    mapping then it must at least support getting, setting and deleting items
    plus iterating over keys.

    `in_dict` can also be a string specifying the name of the dictionary, which
    will then be fetched by agizaing it.

    `values` can be a dictionary of values to set in the dictionary. `values`
    can also be an iterable of `(key, value)` pairs.

    If `clear` is True then the dictionary will be cleared before the new
    values are set.

    `patch.dict` can also be called with arbitrary keyword arguments to set
    values in the dictionary::

        with patch.dict('sys.modules', mymodule=Mock(), other_module=Mock()):
            ...

    `patch.dict` can be used as a context manager, decorator or class
    decorator. When used as a kundi decorator `patch.dict` honours
    `patch.TEST_PREFIX` for choosing which methods to wrap.
    """

    eleza __init__(self, in_dict, values=(), clear=False, **kwargs):
        self.in_dict = in_dict
        # support any argument supported by dict(...) constructor
        self.values = dict(values)
        self.values.update(kwargs)
        self.clear = clear
        self._original = None


    eleza __call__(self, f):
        ikiwa isinstance(f, type):
            rudisha self.decorate_class(f)
        @wraps(f)
        eleza _inner(*args, **kw):
            self._patch_dict()
            try:
                rudisha f(*args, **kw)
            finally:
                self._unpatch_dict()

        rudisha _inner


    eleza decorate_class(self, klass):
        for attr in dir(klass):
            attr_value = getattr(klass, attr)
            ikiwa (attr.startswith(patch.TEST_PREFIX) and
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

        try:
            original = in_dict.copy()
        except AttributeError:
            # dict like object with no copy method
            # must support iteration over keys
            original = {}
            for key in in_dict:
                original[key] = in_dict[key]
        self._original = original

        ikiwa clear:
            _clear_dict(in_dict)

        try:
            in_dict.update(values)
        except AttributeError:
            # dict like object with no update method
            for key in values:
                in_dict[key] = values[key]


    eleza _unpatch_dict(self):
        in_dict = self.in_dict
        original = self._original

        _clear_dict(in_dict)

        try:
            in_dict.update(original)
        except AttributeError:
            for key in original:
                in_dict[key] = original[key]


    eleza __exit__(self, *args):
        """Unpatch the dict."""
        self._unpatch_dict()
        rudisha False

    start = __enter__
    stop = __exit__


eleza _clear_dict(in_dict):
    try:
        in_dict.clear()
    except AttributeError:
        keys = list(in_dict)
        for key in keys:
            del in_dict[key]


eleza _patch_stopall():
    """Stop all active patches. LIFO to unroll nested patches."""
    for patch in reversed(_patch._active_patches):
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
    # we added divmod and rdivmod here instead of numerics
    # because there is no idivmod
    "divmod rdivmod neg pos abs invert "
    "complex int float index "
    "round trunc floor ceil "
    "bool next "
    "fspath "
    "aiter "
)

numerics = (
    "add sub mul matmul div floordiv mod lshift rshift and xor or pow truediv"
)
inplace = ' '.join('i%s' % n for n in numerics.split())
right = ' '.join('r%s' % n for n in numerics.split())

# not including __prepare__, __instancecheck__, __subclasscheck__
# (as they are metakundi methods)
# __del__ is not supported at all as it causes problems ikiwa it exists

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
    '__%s__' % method for method in
    ' '.join([magic_methods, numerics, inplace, right]).split()
}

# Magic methods used for async `with` statements
_async_method_magics = {"__aenter__", "__aexit__", "__anext__"}
# Magic methods that are only used with async calls but are synchronous functions themselves
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
    '__contains__': False,
    '__len__': 0,
    '__exit__': False,
    '__complex__': 1j,
    '__float__': 1.0,
    '__bool__': True,
    '__index__': 1,
    '__aexit__': False,
}


eleza _get_eq(self):
    eleza __eq__(other):
        ret_val = self.__eq__._mock_return_value
        ikiwa ret_val is not DEFAULT:
            rudisha ret_val
        ikiwa self is other:
            rudisha True
        rudisha NotImplemented
    rudisha __eq__

eleza _get_ne(self):
    eleza __ne__(other):
        ikiwa self.__ne__._mock_return_value is not DEFAULT:
            rudisha DEFAULT
        ikiwa self is other:
            rudisha False
        rudisha NotImplemented
    rudisha __ne__

eleza _get_iter(self):
    eleza __iter__():
        ret_val = self.__iter__._mock_return_value
        ikiwa ret_val is DEFAULT:
            rudisha iter([])
        # ikiwa ret_val was already an iterator, then calling iter on it should
        # rudisha the iterator unchanged
        rudisha iter(ret_val)
    rudisha __iter__

eleza _get_async_iter(self):
    eleza __aiter__():
        ret_val = self.__aiter__._mock_return_value
        ikiwa ret_val is DEFAULT:
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
    ikiwa fixed is not DEFAULT:
        method.return_value = fixed
        return

    return_calculator = _calculate_return_value.get(name)
    ikiwa return_calculator is not None:
        return_value = return_calculator(mock)
        method.return_value = return_value
        return

    side_effector = _side_effect_methods.get(name)
    ikiwa side_effector is not None:
        method.side_effect = side_effector(mock)



kundi MagicMixin(Base):
    eleza __init__(self, /, *args, **kw):
        self._mock_set_magics()  # make magic work for kwargs in init
        _safe_super(MagicMixin, self).__init__(*args, **kw)
        self._mock_set_magics()  # fix magic broken by upper level init


    eleza _mock_set_magics(self):
        orig_magics = _magics | _async_method_magics
        these_magics = orig_magics

        ikiwa getattr(self, "_mock_methods", None) is not None:
            these_magics = orig_magics.intersection(self._mock_methods)

            remove_magics = set()
            remove_magics = orig_magics - these_magics

            for entry in remove_magics:
                ikiwa entry in type(self).__dict__:
                    # remove unneeded magic methods
                    delattr(self, entry)

        # don't overwrite existing attributes ikiwa called a second time
        these_magics = these_magics - set(type(self).__dict__)

        _type = type(self)
        for entry in these_magics:
            setattr(_type, entry, MagicProxy(entry, self))



kundi NonCallableMagicMock(MagicMixin, NonCallableMock):
    """A version of `MagicMock` that isn't callable."""
    eleza mock_add_spec(self, spec, spec_set=False):
        """Add a spec to a mock. `spec` can either be an object or a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes kutoka the mock.

        If `spec_set` is True then only attributes on the spec can be set."""
        self._mock_add_spec(spec, spec_set)
        self._mock_set_magics()


kundi AsyncMagicMixin(MagicMixin):
    eleza __init__(self, /, *args, **kw):
        self._mock_set_magics()  # make magic work for kwargs in init
        _safe_super(AsyncMagicMixin, self).__init__(*args, **kw)
        self._mock_set_magics()  # fix magic broken by upper level init

kundi MagicMock(MagicMixin, Mock):
    """
    MagicMock is a subkundi of Mock with default implementations
    of most of the magic methods. You can use MagicMock without having to
    configure the magic methods yourself.

    If you use the `spec` or `spec_set` arguments then *only* magic
    methods that exist in the spec will be created.

    Attributes and the rudisha value of a `MagicMock` will also be `MagicMocks`.
    """
    eleza mock_add_spec(self, spec, spec_set=False):
        """Add a spec to a mock. `spec` can either be an object or a
        list of strings. Only attributes on the `spec` can be fetched as
        attributes kutoka the mock.

        If `spec_set` is True then only attributes on the spec can be set."""
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

    eleza __get__(self, obj, _type=None):
        rudisha self.create_mock()


kundi AsyncMockMixin(Base):
    await_count = _delegating_property('await_count')
    await_args = _delegating_property('await_args')
    await_args_list = _delegating_property('await_args_list')

    eleza __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # asyncio.iscoroutinefunction() checks _is_coroutine property to say ikiwa an
        # object is a coroutine. Without this check it looks to see ikiwa it is a
        # function/method, which in this case it is not (since it is an
        # AsyncMock).
        # It is set through __dict__ because when spec_set is True, this
        # attribute is likely undefined.
        self.__dict__['_is_coroutine'] = asyncio.coroutines._is_coroutine
        self.__dict__['_mock_await_count'] = 0
        self.__dict__['_mock_await_args'] = None
        self.__dict__['_mock_await_args_list'] = _CallList()
        code_mock = NonCallableMock(spec_set=CodeType)
        code_mock.co_flags = inspect.CO_COROUTINE
        self.__dict__['__code__'] = code_mock

    async eleza _mock_call(self, /, *args, **kwargs):
        try:
            result = super()._mock_call(*args, **kwargs)
        except (BaseException, StopIteration) as e:
            side_effect = self.side_effect
            ikiwa side_effect is not None and not callable(side_effect):
                raise
            rudisha await _raise(e)

        _call = self.call_args

        async eleza proxy():
            try:
                ikiwa inspect.isawaitable(result):
                    rudisha await result
                else:
                    rudisha result
            finally:
                self.await_count += 1
                self.await_args = _call
                self.await_args_list.append(_call)

        rudisha await proxy()

    eleza assert_awaited(self):
        """
        Assert that the mock was awaited at least once.
        """
        ikiwa self.await_count == 0:
            msg = f"Expected {self._mock_name or 'mock'} to have been awaited."
            raise AssertionError(msg)

    eleza assert_awaited_once(self):
        """
        Assert that the mock was awaited exactly once.
        """
        ikiwa not self.await_count == 1:
            msg = (f"Expected {self._mock_name or 'mock'} to have been awaited once."
                   f" Awaited {self.await_count} times.")
            raise AssertionError(msg)

    eleza assert_awaited_with(self, /, *args, **kwargs):
        """
        Assert that the last await was with the specified arguments.
        """
        ikiwa self.await_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            raise AssertionError(f'Expected await: {expected}\nNot awaited')

        eleza _error_message():
            msg = self._format_mock_failure_message(args, kwargs, action='await')
            rudisha msg

        expected = self._call_matcher((args, kwargs))
        actual = self._call_matcher(self.await_args)
        ikiwa expected != actual:
            cause = expected ikiwa isinstance(expected, Exception) else None
            raise AssertionError(_error_message()) kutoka cause

    eleza assert_awaited_once_with(self, /, *args, **kwargs):
        """
        Assert that the mock was awaited exactly once and with the specified
        arguments.
        """
        ikiwa not self.await_count == 1:
            msg = (f"Expected {self._mock_name or 'mock'} to have been awaited once."
                   f" Awaited {self.await_count} times.")
            raise AssertionError(msg)
        rudisha self.assert_awaited_with(*args, **kwargs)

    eleza assert_any_await(self, /, *args, **kwargs):
        """
        Assert the mock has ever been awaited with the specified arguments.
        """
        expected = self._call_matcher((args, kwargs))
        actual = [self._call_matcher(c) for c in self.await_args_list]
        ikiwa expected not in actual:
            cause = expected ikiwa isinstance(expected, Exception) else None
            expected_string = self._format_mock_call_signature(args, kwargs)
            raise AssertionError(
                '%s await not found' % expected_string
            ) kutoka cause

    eleza assert_has_awaits(self, calls, any_order=False):
        """
        Assert the mock has been awaited with the specified calls.
        The :attr:`await_args_list` list is checked for the awaits.

        If `any_order` is False (the default) then the awaits must be
        sequential. There can be extra calls before or after the
        specified awaits.

        If `any_order` is True then the awaits can be in any order, but
        they must all appear in :attr:`await_args_list`.
        """
        expected = [self._call_matcher(c) for c in calls]
        cause = next((e for e in expected ikiwa isinstance(e, Exception)), None)
        all_awaits = _CallList(self._call_matcher(c) for c in self.await_args_list)
        ikiwa not any_order:
            ikiwa expected not in all_awaits:
                ikiwa cause is None:
                    problem = 'Awaits not found.'
                else:
                    problem = ('Error processing expected awaits.\n'
                               'Errors: {}').format(
                                   [e ikiwa isinstance(e, Exception) else None
                                    for e in expected])
                raise AssertionError(
                    f'{problem}\n'
                    f'Expected: {_CallList(calls)}\n'
                    f'Actual: {self.await_args_list}'
                ) kutoka cause
            return

        all_awaits = list(all_awaits)

        not_found = []
        for kall in expected:
            try:
                all_awaits.remove(kall)
            except ValueError:
                not_found.append(kall)
        ikiwa not_found:
            raise AssertionError(
                '%r not all found in await list' % (tuple(not_found),)
            ) kutoka cause

    eleza assert_not_awaited(self):
        """
        Assert that the mock was never awaited.
        """
        ikiwa self.await_count != 0:
            msg = (f"Expected {self._mock_name or 'mock'} to not have been awaited."
                   f" Awaited {self.await_count} times.")
            raise AssertionError(msg)

    eleza reset_mock(self, /, *args, **kwargs):
        """
        See :func:`.Mock.reset_mock()`
        """
        super().reset_mock(*args, **kwargs)
        self.await_count = 0
        self.await_args = None
        self.await_args_list = _CallList()


kundi AsyncMock(AsyncMockMixin, AsyncMagicMixin, Mock):
    """
    Enhance :class:`Mock` with features allowing to mock
    an async function.

    The :class:`AsyncMock` object will behave so the object is
    recognized as an async function, and the result of a call is an awaitable:

    >>> mock = AsyncMock()
    >>> asyncio.iscoroutinefunction(mock)
    True
    >>> inspect.isawaitable(mock())
    True


    The result of ``mock()`` is an async function which will have the outcome
    of ``side_effect`` or ``return_value``:

    - ikiwa ``side_effect`` is a function, the async function will rudisha the
      result of that function,
    - ikiwa ``side_effect`` is an exception, the async function will raise the
      exception,
    - ikiwa ``side_effect`` is an iterable, the async function will rudisha the
      next value of the iterable, however, ikiwa the sequence of result is
      exhausted, ``StopIteration`` is raised immediately,
    - ikiwa ``side_effect`` is not defined, the async function will rudisha the
      value defined by ``return_value``, hence, by default, the async function
      returns a new :class:`AsyncMock` object.

    If the outcome of ``side_effect`` or ``return_value`` is an async function,
    the mock async function obtained when the mock object is called will be this
    async function itself (and not an async function returning an async
    function).

    The test author can also specify a wrapped object with ``wraps``. In this
    case, the :class:`Mock` object behavior is the same as with an
    :class:`.Mock` object: the wrapped object may have methods
    defined as async function functions.

    Based on Martin Richard's asynctest project.
    """


kundi _ANY(object):
    "A helper object that compares equal to everything."

    eleza __eq__(self, other):
        rudisha True

    eleza __ne__(self, other):
        rudisha False

    eleza __repr__(self):
        rudisha '<ANY>'

ANY = _ANY()



eleza _format_call_signature(name, args, kwargs):
    message = '%s(%%s)' % name
    formatted_args = ''
    args_string = ', '.join([repr(arg) for arg in args])
    kwargs_string = ', '.join([
        '%s=%r' % (key, value) for key, value in kwargs.items()
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
    A tuple for holding the results of a call to a mock, either in the form
    `(args, kwargs)` or `(name, args, kwargs)`.

    If args or kwargs are empty then a call tuple will compare equal to
    a tuple without those values. This makes comparisons less verbose::

        _Call(('name', (), {})) == ('name',)
        _Call(('name', (1,), {})) == ('name', (1,))
        _Call(((), {'a': 'b'})) == ({'a': 'b'},)

    The `_Call` object provides a useful shortcut for comparing with call::

        _Call(((1, 2), {'a': 3})) == call(1, 2, a=3)
        _Call(('foo', (1, 2), {'a': 3})) == call.foo(1, 2, a=3)

    If the _Call has no name then it will match any name.
    """
    eleza __new__(cls, value=(), name='', parent=None, two=False,
                kutoka_kall=True):
        args = ()
        kwargs = {}
        _len = len(value)
        ikiwa _len == 3:
            name, args, kwargs = value
        elikiwa _len == 2:
            first, second = value
            ikiwa isinstance(first, str):
                name = first
                ikiwa isinstance(second, tuple):
                    args = second
                else:
                    kwargs = second
            else:
                args, kwargs = first, second
        elikiwa _len == 1:
            value, = value
            ikiwa isinstance(value, str):
                name = value
            elikiwa isinstance(value, tuple):
                args = value
            else:
                kwargs = value

        ikiwa two:
            rudisha tuple.__new__(cls, (args, kwargs))

        rudisha tuple.__new__(cls, (name, args, kwargs))


    eleza __init__(self, value=(), name=None, parent=None, two=False,
                 kutoka_kall=True):
        self._mock_name = name
        self._mock_parent = parent
        self._mock_kutoka_kall = kutoka_kall


    eleza __eq__(self, other):
        ikiwa other is ANY:
            rudisha True
        try:
            len_other = len(other)
        except TypeError:
            rudisha False

        self_name = ''
        ikiwa len(self) == 2:
            self_args, self_kwargs = self
        else:
            self_name, self_args, self_kwargs = self

        ikiwa (getattr(self, '_mock_parent', None) and getattr(other, '_mock_parent', None)
                and self._mock_parent != other._mock_parent):
            rudisha False

        other_name = ''
        ikiwa len_other == 0:
            other_args, other_kwargs = (), {}
        elikiwa len_other == 3:
            other_name, other_args, other_kwargs = other
        elikiwa len_other == 1:
            value, = other
            ikiwa isinstance(value, tuple):
                other_args = value
                other_kwargs = {}
            elikiwa isinstance(value, str):
                other_name = value
                other_args, other_kwargs = (), {}
            else:
                other_args = ()
                other_kwargs = value
        elikiwa len_other == 2:
            # could be (name, args) or (name, kwargs) or (args, kwargs)
            first, second = other
            ikiwa isinstance(first, str):
                other_name = first
                ikiwa isinstance(second, tuple):
                    other_args, other_kwargs = second, {}
                else:
                    other_args, other_kwargs = (), second
            else:
                other_args, other_kwargs = first, second
        else:
            rudisha False

        ikiwa self_name and other_name != self_name:
            rudisha False

        # this order is agizaant for ANY to work!
        rudisha (other_args, other_kwargs) == (self_args, self_kwargs)


    __ne__ = object.__ne__


    eleza __call__(self, /, *args, **kwargs):
        ikiwa self._mock_name is None:
            rudisha _Call(('', args, kwargs), name='()')

        name = self._mock_name + '()'
        rudisha _Call((self._mock_name, args, kwargs), name=name, parent=self)


    eleza __getattr__(self, attr):
        ikiwa self._mock_name is None:
            rudisha _Call(name=attr, kutoka_kall=False)
        name = '%s.%s' % (self._mock_name, attr)
        rudisha _Call(name=name, parent=self, kutoka_kall=False)


    eleza __getattribute__(self, attr):
        ikiwa attr in tuple.__dict__:
            raise AttributeError
        rudisha tuple.__getattribute__(self, attr)


    eleza count(self, /, *args, **kwargs):
        rudisha self.__getattr__('count')(*args, **kwargs)

    eleza index(self, /, *args, **kwargs):
        rudisha self.__getattr__('index')(*args, **kwargs)

    eleza _get_call_arguments(self):
        ikiwa len(self) == 2:
            args, kwargs = self
        else:
            name, args, kwargs = self

        rudisha args, kwargs

    @property
    eleza args(self):
        rudisha self._get_call_arguments()[0]

    @property
    eleza kwargs(self):
        rudisha self._get_call_arguments()[1]

    eleza __repr__(self):
        ikiwa not self._mock_kutoka_kall:
            name = self._mock_name or 'call'
            ikiwa name.startswith('()'):
                name = 'call%s' % name
            rudisha name

        ikiwa len(self) == 2:
            name = 'call'
            args, kwargs = self
        else:
            name, args, kwargs = self
            ikiwa not name:
                name = 'call'
            elikiwa not name.startswith('()'):
                name = 'call.%s' % name
            else:
                name = 'call%s' % name
        rudisha _format_call_signature(name, args, kwargs)


    eleza call_list(self):
        """For a call object that represents multiple calls, `call_list`
        returns a list of all the intermediate calls as well as the
        final call."""
        vals = []
        thing = self
        while thing is not None:
            ikiwa thing._mock_kutoka_kall:
                vals.append(thing)
            thing = thing._mock_parent
        rudisha _CallList(reversed(vals))


call = _Call(kutoka_kall=False)


eleza create_autospec(spec, spec_set=False, instance=False, _parent=None,
                    _name=None, **kwargs):
    """Create a mock object using another object as a spec. Attributes on the
    mock will use the corresponding attribute on the `spec` object as their
    spec.

    Functions or methods being mocked will have their arguments checked
    to check that they are called with the correct signature.

    If `spec_set` is True then attempting to set attributes that don't exist
    on the spec object will raise an `AttributeError`.

    If a kundi is used as a spec then the rudisha value of the mock (the
    instance of the class) will have the same spec. You can use a kundi as the
    spec for an instance object by passing `instance=True`. The returned mock
    will only be callable ikiwa instances of the mock are callable.

    `create_autospec` also takes arbitrary keyword arguments that are passed to
    the constructor of the created mock."""
    ikiwa _is_list(spec):
        # can't pass a list instance to the mock constructor as it will be
        # interpreted as a list of strings
        spec = type(spec)

    is_type = isinstance(spec, type)
    is_async_func = _is_async_func(spec)
    _kwargs = {'spec': spec}
    ikiwa spec_set:
        _kwargs = {'spec_set': spec}
    elikiwa spec is None:
        # None we mock with a normal mock without a spec
        _kwargs = {}
    ikiwa _kwargs and instance:
        _kwargs['_spec_as_instance'] = True

    _kwargs.update(kwargs)

    Klass = MagicMock
    ikiwa inspect.isdatadescriptor(spec):
        # descriptors don't have a spec
        # because we don't know what type they return
        _kwargs = {}
    elikiwa is_async_func:
        ikiwa instance:
            raise RuntimeError("Instance can not be True when create_autospec "
                               "is mocking an async function")
        Klass = AsyncMock
    elikiwa not _callable(spec):
        Klass = NonCallableMagicMock
    elikiwa is_type and instance and not _instance_callable(spec):
        Klass = NonCallableMagicMock

    _name = _kwargs.pop('name', _name)

    _new_name = _name
    ikiwa _parent is None:
        # for a top level object no _new_name should be set
        _new_name = ''

    mock = Klass(parent=_parent, _new_parent=_parent, _new_name=_new_name,
                 name=_name, **_kwargs)

    ikiwa isinstance(spec, FunctionTypes):
        # should only happen at the top level because we don't
        # recurse for functions
        mock = _set_signature(mock, spec)
        ikiwa is_async_func:
            _setup_async_mock(mock)
    else:
        _check_signature(spec, mock, is_type, instance)

    ikiwa _parent is not None and not instance:
        _parent._mock_children[_name] = mock

    ikiwa is_type and not instance and 'return_value' not in kwargs:
        mock.return_value = create_autospec(spec, spec_set, instance=True,
                                            _name='()', _parent=mock)

    for entry in dir(spec):
        ikiwa _is_magic(entry):
            # MagicMock already does the useful magic methods for us
            continue

        # XXXX do we need a better way of getting attributes without
        # triggering code execution (?) Probably not - we need the actual
        # object to mock it so we would rather trigger a property than mock
        # the property descriptor. Likewise we want to mock out dynamically
        # provided attributes.
        # XXXX what about attributes that raise exceptions other than
        # AttributeError on being fetched?
        # we could be resilient against it, or catch and propagate the
        # exception when the attribute is fetched kutoka the mock
        try:
            original = getattr(spec, entry)
        except AttributeError:
            continue

        kwargs = {'spec': original}
        ikiwa spec_set:
            kwargs = {'spec_set': original}

        ikiwa not isinstance(original, FunctionTypes):
            new = _SpecState(original, spec_set, mock, entry, instance)
            mock._mock_children[entry] = new
        else:
            parent = mock
            ikiwa isinstance(spec, FunctionTypes):
                parent = mock.mock

            skipfirst = _must_skip(spec, entry, is_type)
            kwargs['_eat_self'] = skipfirst
            ikiwa asyncio.iscoroutinefunction(original):
                child_klass = AsyncMock
            else:
                child_klass = MagicMock
            new = child_klass(parent=parent, name=entry, _new_name=entry,
                              _new_parent=parent,
                              **kwargs)
            mock._mock_children[entry] = new
            _check_signature(original, new, skipfirst=skipfirst)

        # so functions created with _set_signature become instance attributes,
        # *plus* their underlying mock exists in _mock_children of the parent
        # mock. Adding to _mock_children may be unnecessary where we are also
        # setting as an instance attribute?
        ikiwa isinstance(new, FunctionTypes):
            setattr(mock, entry, new)

    rudisha mock


eleza _must_skip(spec, entry, is_type):
    """
    Return whether we should skip the first argument on spec's `entry`
    attribute.
    """
    ikiwa not isinstance(spec, type):
        ikiwa entry in getattr(spec, '__dict__', {}):
            # instance attribute - shouldn't skip
            rudisha False
        spec = spec.__class__

    for klass in spec.__mro__:
        result = klass.__dict__.get(entry, DEFAULT)
        ikiwa result is DEFAULT:
            continue
        ikiwa isinstance(result, (staticmethod, classmethod)):
            rudisha False
        elikiwa isinstance(getattr(result, '__get__', None), MethodWrapperTypes):
            # Normal method => skip ikiwa looked up on type
            # (ikiwa looked up on instance, self is already skipped)
            rudisha is_type
        else:
            rudisha False

    # function is a dynamically provided attribute
    rudisha is_type


kundi _SpecState(object):

    eleza __init__(self, spec, spec_set=False, parent=None,
                 name=None, ids=None, instance=False):
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


file_spec = None


eleza _to_stream(read_data):
    ikiwa isinstance(read_data, bytes):
        rudisha io.BytesIO(read_data)
    else:
        rudisha io.StringIO(read_data)


eleza mock_open(mock=None, read_data=''):
    """
    A helper function to create a mock to replace the use of `open`. It works
    for `open` called directly or used as a context manager.

    The `mock` argument is the mock object to configure. If `None` (the
    default) then a `MagicMock` will be created for you, with the API limited
    to methods or attributes available on standard file handles.

    `read_data` is a string for the `read`, `readline` and `readlines` of the
    file handle to return.  This is an empty string by default.
    """
    _read_data = _to_stream(read_data)
    _state = [_read_data, None]

    eleza _readlines_side_effect(*args, **kwargs):
        ikiwa handle.readlines.return_value is not None:
            rudisha handle.readlines.return_value
        rudisha _state[0].readlines(*args, **kwargs)

    eleza _read_side_effect(*args, **kwargs):
        ikiwa handle.read.return_value is not None:
            rudisha handle.read.return_value
        rudisha _state[0].read(*args, **kwargs)

    eleza _readline_side_effect(*args, **kwargs):
        yield kutoka _iter_side_effect()
        while True:
            yield _state[0].readline(*args, **kwargs)

    eleza _iter_side_effect():
        ikiwa handle.readline.return_value is not None:
            while True:
                yield handle.readline.return_value
        for line in _state[0]:
            yield line

    eleza _next_side_effect():
        ikiwa handle.readline.return_value is not None:
            rudisha handle.readline.return_value
        rudisha next(_state[0])

    global file_spec
    ikiwa file_spec is None:
        agiza _io
        file_spec = list(set(dir(_io.TextIOWrapper)).union(set(dir(_io.BytesIO))))

    ikiwa mock is None:
        mock = MagicMock(name='open', spec=open)

    handle = MagicMock(spec=file_spec)
    handle.__enter__.return_value = handle

    handle.write.return_value = None
    handle.read.return_value = None
    handle.readline.return_value = None
    handle.readlines.return_value = None

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
    A mock intended to be used as a property, or other descriptor, on a class.
    `PropertyMock` provides `__get__` and `__set__` methods so you can specify
    a rudisha value when it is fetched.

    Fetching a `PropertyMock` instance kutoka an object calls the mock, with
    no args. Setting it calls the mock with the value being set.
    """
    eleza _get_child_mock(self, /, **kwargs):
        rudisha MagicMock(**kwargs)

    eleza __get__(self, obj, obj_type=None):
        rudisha self()
    eleza __set__(self, obj, val):
        self(val)


eleza seal(mock):
    """Disable the automatic generation of child mocks.

    Given an input Mock, seals it to ensure no further mocks will be generated
    when accessing an attribute that was not already defined.

    The operation recursively seals the mock passed in, meaning that
    the mock itself, any mocks generated by accessing one of its attributes,
    and all assigned mocks without a name or spec will be sealed.
    """
    mock._mock_sealed = True
    for attr in dir(mock):
        try:
            m = getattr(mock, attr)
        except AttributeError:
            continue
        ikiwa not isinstance(m, NonCallableMock):
            continue
        ikiwa m._mock_new_parent is mock:
            seal(m)


async eleza _raise(exception):
    raise exception


kundi _AsyncIterator:
    """
    Wraps an iterator in an asynchronous iterator.
    """
    eleza __init__(self, iterator):
        self.iterator = iterator
        code_mock = NonCallableMock(spec_set=CodeType)
        code_mock.co_flags = inspect.CO_ITERABLE_COROUTINE
        self.__dict__['__code__'] = code_mock

    eleza __aiter__(self):
        rudisha self

    async eleza __anext__(self):
        try:
            rudisha next(self.iterator)
        except StopIteration:
            pass
        raise StopAsyncIteration
