"""W3C Document Object Motoa implementation kila Python.

The Python mapping of the Document Object Motoa ni documented kwenye the
Python Library Reference kwenye the section on the xml.dom package.

This package contains the following modules:

minidom -- A simple implementation of the Level 1 DOM with namespace
           support added (based on the Level 2 specification) na other
           minor Level 2 functionality.

pulldom -- DOM builder supporting on-demand tree-building kila selected
           subtrees of the document.

"""


kundi Node:
    """Class giving the NodeType constants."""
    __slots__ = ()

    # DOM implementations may use this kama a base kundi kila their own
    # Node implementations.  If they don't, the constants defined here
    # should still be used kama the canonical definitions kama they match
    # the values given kwenye the W3C recommendation.  Client code can
    # safely refer to these values kwenye all tests of Node.nodeType
    # values.

    ELEMENT_NODE                = 1
    ATTRIBUTE_NODE              = 2
    TEXT_NODE                   = 3
    CDATA_SECTION_NODE          = 4
    ENTITY_REFERENCE_NODE       = 5
    ENTITY_NODE                 = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE                = 8
    DOCUMENT_NODE               = 9
    DOCUMENT_TYPE_NODE          = 10
    DOCUMENT_FRAGMENT_NODE      = 11
    NOTATION_NODE               = 12


#ExceptionCode
INDEX_SIZE_ERR                 = 1
DOMSTRING_SIZE_ERR             = 2
HIERARCHY_REQUEST_ERR          = 3
WRONG_DOCUMENT_ERR             = 4
INVALID_CHARACTER_ERR          = 5
NO_DATA_ALLOWED_ERR            = 6
NO_MODIFICATION_ALLOWED_ERR    = 7
NOT_FOUND_ERR                  = 8
NOT_SUPPORTED_ERR              = 9
INUSE_ATTRIBUTE_ERR            = 10
INVALID_STATE_ERR              = 11
SYNTAX_ERR                     = 12
INVALID_MODIFICATION_ERR       = 13
NAMESPACE_ERR                  = 14
INVALID_ACCESS_ERR             = 15
VALIDATION_ERR                 = 16


kundi DOMException(Exception):
    """Abstract base kundi kila DOM exceptions.
    Exceptions with specific codes are specializations of this class."""

    eleza __init__(self, *args, **kw):
        ikiwa self.__class__ ni DOMException:
            ashiria RuntimeError(
                "DOMException should sio be instantiated directly")
        Exception.__init__(self, *args, **kw)

    eleza _get_code(self):
        rudisha self.code


kundi IndexSizeErr(DOMException):
    code = INDEX_SIZE_ERR

kundi DomstringSizeErr(DOMException):
    code = DOMSTRING_SIZE_ERR

kundi HierarchyRequestErr(DOMException):
    code = HIERARCHY_REQUEST_ERR

kundi WrongDocumentErr(DOMException):
    code = WRONG_DOCUMENT_ERR

kundi InvalidCharacterErr(DOMException):
    code = INVALID_CHARACTER_ERR

kundi NoDataAllowedErr(DOMException):
    code = NO_DATA_ALLOWED_ERR

kundi NoModificationAllowedErr(DOMException):
    code = NO_MODIFICATION_ALLOWED_ERR

kundi NotFoundErr(DOMException):
    code = NOT_FOUND_ERR

kundi NotSupportedErr(DOMException):
    code = NOT_SUPPORTED_ERR

kundi InuseAttributeErr(DOMException):
    code = INUSE_ATTRIBUTE_ERR

kundi InvalidStateErr(DOMException):
    code = INVALID_STATE_ERR

kundi SyntaxErr(DOMException):
    code = SYNTAX_ERR

kundi InvalidModificationErr(DOMException):
    code = INVALID_MODIFICATION_ERR

kundi NamespaceErr(DOMException):
    code = NAMESPACE_ERR

kundi InvalidAccessErr(DOMException):
    code = INVALID_ACCESS_ERR

kundi ValidationErr(DOMException):
    code = VALIDATION_ERR

kundi UserDataHandler:
    """Class giving the operation constants kila UserDataHandler.handle()."""

    # Based on DOM Level 3 (WD 9 April 2002)

    NODE_CLONED   = 1
    NODE_IMPORTED = 2
    NODE_DELETED  = 3
    NODE_RENAMED  = 4

XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
XMLNS_NAMESPACE = "http://www.w3.org/2000/xmlns/"
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
EMPTY_NAMESPACE = Tupu
EMPTY_PREFIX = Tupu

kutoka .domreg agiza getDOMImplementation, registerDOMImplementation
