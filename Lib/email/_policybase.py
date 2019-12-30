"""Policy framework kila the email package.

Allows fine grained feature control of how the package parses na emits data.
"""

agiza abc
kutoka email agiza header
kutoka email agiza charset kama _charset
kutoka email.utils agiza _has_surrogates

__all__ = [
    'Policy',
    'Compat32',
    'compat32',
    ]


kundi _PolicyBase:

    """Policy Object basic framework.

    This kundi ni useless unless subclassed.  A subkundi should define
    kundi attributes ukijumuisha defaults kila any values that are to be
    managed by the Policy object.  The constructor will then allow
    non-default values to be set kila these attributes at instance
    creation time.  The instance will be callable, taking these same
    attributes keyword arguments, na returning a new instance
    identical to the called instance tatizo kila those values changed
    by the keyword arguments.  Instances may be added, tumaing new
    instances ukijumuisha any non-default values kutoka the right hand
    operand overriding those kwenye the left hand operand.  That is,

        A + B == A(<non-default values of B>)

    The repr of an instance can be used to reconstruct the object
    ikiwa na only ikiwa the repr of the values can be used to reconstruct
    those values.

    """

    eleza __init__(self, **kw):
        """Create new Policy, possibly overriding some defaults.

        See kundi docstring kila a list of overridable attributes.

        """
        kila name, value kwenye kw.items():
            ikiwa hasattr(self, name):
                super(_PolicyBase,self).__setattr__(name, value)
            isipokua:
                ashiria TypeError(
                    "{!r} ni an invalid keyword argument kila {}".format(
                        name, self.__class__.__name__))

    eleza __repr__(self):
        args = [ "{}={!r}".format(name, value)
                 kila name, value kwenye self.__dict__.items() ]
        rudisha "{}({})".format(self.__class__.__name__, ', '.join(args))

    eleza clone(self, **kw):
        """Return a new instance ukijumuisha specified attributes changed.

        The new instance has the same attribute values kama the current object,
        tatizo kila the changes pitaed kwenye kama keyword arguments.

        """
        newpolicy = self.__class__.__new__(self.__class__)
        kila attr, value kwenye self.__dict__.items():
            object.__setattr__(newpolicy, attr, value)
        kila attr, value kwenye kw.items():
            ikiwa sio hasattr(self, attr):
                ashiria TypeError(
                    "{!r} ni an invalid keyword argument kila {}".format(
                        attr, self.__class__.__name__))
            object.__setattr__(newpolicy, attr, value)
        rudisha newpolicy

    eleza __setattr__(self, name, value):
        ikiwa hasattr(self, name):
            msg = "{!r} object attribute {!r} ni read-only"
        isipokua:
            msg = "{!r} object has no attribute {!r}"
        ashiria AttributeError(msg.format(self.__class__.__name__, name))

    eleza __add__(self, other):
        """Non-default values kutoka right operand override those kutoka left.

        The object returned ni a new instance of the subclass.

        """
        rudisha self.clone(**other.__dict__)


eleza _append_doc(doc, added_doc):
    doc = doc.rsplit('\n', 1)[0]
    added_doc = added_doc.split('\n', 1)[1]
    rudisha doc + '\n' + added_doc

eleza _extend_docstrings(cls):
    ikiwa cls.__doc__ na cls.__doc__.startswith('+'):
        cls.__doc__ = _append_doc(cls.__bases__[0].__doc__, cls.__doc__)
    kila name, attr kwenye cls.__dict__.items():
        ikiwa attr.__doc__ na attr.__doc__.startswith('+'):
            kila c kwenye (c kila base kwenye cls.__bases__ kila c kwenye base.mro()):
                doc = getattr(getattr(c, name), '__doc__')
                ikiwa doc:
                    attr.__doc__ = _append_doc(doc, attr.__doc__)
                    koma
    rudisha cls


kundi Policy(_PolicyBase, metaclass=abc.ABCMeta):

    r"""Controls kila how messages are interpreted na formatted.

    Most of the classes na many of the methods kwenye the email package accept
    Policy objects kama parameters.  A Policy object contains a set of values na
    functions that control how input ni interpreted na how output ni rendered.
    For example, the parameter 'raise_on_defect' controls whether ama sio an RFC
    violation results kwenye an error being raised ama not, wakati 'max_line_length'
    controls the maximum length of output lines when a Message ni serialized.

    Any valid attribute may be overridden when a Policy ni created by pitaing
    it kama a keyword argument to the constructor.  Policy objects are immutable,
    but a new Policy object can be created ukijumuisha only certain values changed by
    calling the Policy instance ukijumuisha keyword arguments.  Policy objects can
    also be added, producing a new Policy object kwenye which the non-default
    attributes set kwenye the right hand operand overwrite those specified kwenye the
    left operand.

    Settable attributes:

    raise_on_defect     -- If true, then defects should be raised kama errors.
                           Default: Uongo.

    linesep             -- string containing the value to use kama separation
                           between output lines.  Default '\n'.

    cte_type            -- Type of allowed content transfer encodings

                           7bit  -- ASCII only
                           8bit  -- Content-Transfer-Encoding: 8bit ni allowed

                           Default: 8bit.  Also controls the disposition of
                           (RFC invalid) binary data kwenye headers; see the
                           documentation of the binary_fold method.

    max_line_length     -- maximum length of lines, excluding 'linesep',
                           during serialization.  Tupu ama 0 means no line
                           wrapping ni done.  Default ni 78.

    mangle_from_        -- a flag that, when Kweli escapes From_ lines kwenye the
                           body of the message by putting a `>' kwenye front of
                           them. This ni used when the message ni being
                           serialized by a generator. Default: Kweli.

    message_factory     -- the kundi to use to create new message objects.
                           If the value ni Tupu, the default ni Message.

    """

    raise_on_defect = Uongo
    linesep = '\n'
    cte_type = '8bit'
    max_line_length = 78
    mangle_from_ = Uongo
    message_factory = Tupu

    eleza handle_defect(self, obj, defect):
        """Based on policy, either ashiria defect ama call register_defect.

            handle_defect(obj, defect)

        defect should be a Defect subclass, but kwenye any case must be an
        Exception subclass.  obj ni the object on which the defect should be
        registered ikiwa it ni sio raised.  If the raise_on_defect ni Kweli, the
        defect ni raised kama an error, otherwise the object na the defect are
        pitaed to register_defect.

        This method ni intended to be called by parsers that discover defects.
        The email package parsers always call it ukijumuisha Defect instances.

        """
        ikiwa self.raise_on_defect:
            ashiria defect
        self.register_defect(obj, defect)

    eleza register_defect(self, obj, defect):
        """Record 'defect' on 'obj'.

        Called by handle_defect ikiwa raise_on_defect ni Uongo.  This method is
        part of the Policy API so that Policy subclasses can implement custom
        defect handling.  The default implementation calls the append method of
        the defects attribute of obj.  The objects used by the email package by
        default that get pitaed to this method will always have a defects
        attribute ukijumuisha an append method.

        """
        obj.defects.append(defect)

    eleza header_max_count(self, name):
        """Return the maximum allowed number of headers named 'name'.

        Called when a header ni added to a Message object.  If the returned
        value ni sio 0 ama Tupu, na there are already a number of headers with
        the name 'name' equal to the value returned, a ValueError ni raised.

        Because the default behavior of Message's __setitem__ ni to append the
        value to the list of headers, it ni easy to create duplicate headers
        without realizing it.  This method allows certain headers to be limited
        kwenye the number of instances of that header that may be added to a
        Message programmatically.  (The limit ni sio observed by the parser,
        which will faithfully produce kama many headers kama exist kwenye the message
        being parsed.)

        The default implementation returns Tupu kila all header names.
        """
        rudisha Tupu

    @abc.abstractmethod
    eleza header_source_parse(self, sourcelines):
        """Given a list of linesep terminated strings constituting the lines of
        a single header, rudisha the (name, value) tuple that should be stored
        kwenye the model.  The input lines should retain their terminating linesep
        characters.  The lines pitaed kwenye by the email package may contain
        surrogateescaped binary data.
        """
        ashiria NotImplementedError

    @abc.abstractmethod
    eleza header_store_parse(self, name, value):
        """Given the header name na the value provided by the application
        program, rudisha the (name, value) that should be stored kwenye the model.
        """
        ashiria NotImplementedError

    @abc.abstractmethod
    eleza header_fetch_parse(self, name, value):
        """Given the header name na the value kutoka the model, rudisha the value
        to be returned to the application program that ni requesting that
        header.  The value pitaed kwenye by the email package may contain
        surrogateescaped binary data ikiwa the lines were parsed by a BytesParser.
        The returned value should sio contain any surrogateescaped data.

        """
        ashiria NotImplementedError

    @abc.abstractmethod
    eleza fold(self, name, value):
        """Given the header name na the value kutoka the model, rudisha a string
        containing linesep characters that implement the folding of the header
        according to the policy controls.  The value pitaed kwenye by the email
        package may contain surrogateescaped binary data ikiwa the lines were
        parsed by a BytesParser.  The returned value should sio contain any
        surrogateescaped data.

        """
        ashiria NotImplementedError

    @abc.abstractmethod
    eleza fold_binary(self, name, value):
        """Given the header name na the value kutoka the model, rudisha binary
        data containing linesep characters that implement the folding of the
        header according to the policy controls.  The value pitaed kwenye by the
        email package may contain surrogateescaped binary data.

        """
        ashiria NotImplementedError


@_extend_docstrings
kundi Compat32(Policy):

    """+
    This particular policy ni the backward compatibility Policy.  It
    replicates the behavior of the email package version 5.1.
    """

    mangle_from_ = Kweli

    eleza _sanitize_header(self, name, value):
        # If the header value contains surrogates, rudisha a Header using
        # the unknown-8bit charset to encode the bytes kama encoded words.
        ikiwa sio isinstance(value, str):
            # Assume it ni already a header object
            rudisha value
        ikiwa _has_surrogates(value):
            rudisha header.Header(value, charset=_charset.UNKNOWN8BIT,
                                 header_name=name)
        isipokua:
            rudisha value

    eleza header_source_parse(self, sourcelines):
        """+
        The name ni parsed kama everything up to the ':' na returned unmodified.
        The value ni determined by stripping leading whitespace off the
        remainder of the first line, joining all subsequent lines together, na
        stripping any trailing carriage rudisha ama linefeed characters.

        """
        name, value = sourcelines[0].split(':', 1)
        value = value.lstrip(' \t') + ''.join(sourcelines[1:])
        rudisha (name, value.rstrip('\r\n'))

    eleza header_store_parse(self, name, value):
        """+
        The name na value are returned unmodified.
        """
        rudisha (name, value)

    eleza header_fetch_parse(self, name, value):
        """+
        If the value contains binary data, it ni converted into a Header object
        using the unknown-8bit charset.  Otherwise it ni returned unmodified.
        """
        rudisha self._sanitize_header(name, value)

    eleza fold(self, name, value):
        """+
        Headers are folded using the Header folding algorithm, which preserves
        existing line komas kwenye the value, na wraps each resulting line to the
        max_line_length.  Non-ASCII binary data are CTE encoded using the
        unknown-8bit charset.

        """
        rudisha self._fold(name, value, sanitize=Kweli)

    eleza fold_binary(self, name, value):
        """+
        Headers are folded using the Header folding algorithm, which preserves
        existing line komas kwenye the value, na wraps each resulting line to the
        max_line_length.  If cte_type ni 7bit, non-ascii binary data ni CTE
        encoded using the unknown-8bit charset.  Otherwise the original source
        header ni used, ukijumuisha its existing line komas and/or binary data.

        """
        folded = self._fold(name, value, sanitize=self.cte_type=='7bit')
        rudisha folded.encode('ascii', 'surrogateescape')

    eleza _fold(self, name, value, sanitize):
        parts = []
        parts.append('%s: ' % name)
        ikiwa isinstance(value, str):
            ikiwa _has_surrogates(value):
                ikiwa sanitize:
                    h = header.Header(value,
                                      charset=_charset.UNKNOWN8BIT,
                                      header_name=name)
                isipokua:
                    # If we have raw 8bit data kwenye a byte string, we have no idea
                    # what the encoding is.  There ni no safe way to split this
                    # string.  If it's ascii-subset, then we could do a normal
                    # ascii split, but ikiwa it's multibyte then we could koma the
                    # string.  There's no way to know so the least harm seems to
                    # be to sio split the string na risk it being too long.
                    parts.append(value)
                    h = Tupu
            isipokua:
                h = header.Header(value, header_name=name)
        isipokua:
            # Assume it ni a Header-like object.
            h = value
        ikiwa h ni sio Tupu:
            # The Header kundi interprets a value of Tupu kila maxlinelen kama the
            # default value of 78, kama recommended by RFC 2822.
            maxlinelen = 0
            ikiwa self.max_line_length ni sio Tupu:
                maxlinelen = self.max_line_length
            parts.append(h.encode(linesep=self.linesep, maxlinelen=maxlinelen))
        parts.append(self.linesep)
        rudisha ''.join(parts)


compat32 = Compat32()
