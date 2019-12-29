"""Simple API kila XML (SAX) implementation kila Python.

This module provides an implementation of the SAX 2 interface;
information about the Java version of the interface can be found at
http://www.megginson.com/SAX/.  The Python version of the interface is
documented at <...>.

This package contains the following modules:

handler -- Base classes na constants which define the SAX 2 API for
           the 'client-side' of SAX kila Python.

saxutils -- Implementation of the convenience classes commonly used to
            work ukijumuisha SAX.

xmlreader -- Base classes na constants which define the SAX 2 API for
             the parsers used ukijumuisha SAX kila Python.

expatreader -- Driver that allows use of the Expat parser ukijumuisha SAX.
"""

kutoka .xmlreader agiza InputSource
kutoka .handler agiza ContentHandler, ErrorHandler
kutoka ._exceptions agiza SAXException, SAXNotRecognizedException, \
                        SAXParseException, SAXNotSupportedException, \
                        SAXReaderNotAvailable


eleza parse(source, handler, errorHandler=ErrorHandler()):
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)
    parser.parse(source)

eleza parseString(string, handler, errorHandler=ErrorHandler()):
    agiza io
    ikiwa errorHandler ni Tupu:
        errorHandler = ErrorHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)

    inpsrc = InputSource()
    ikiwa isinstance(string, str):
        inpsrc.setCharacterStream(io.StringIO(string))
    isipokua:
        inpsrc.setByteStream(io.BytesIO(string))
    parser.parse(inpsrc)

# this ni the parser list used by the make_parser function ikiwa no
# alternatives are given kama parameters to the function

default_parser_list = ["xml.sax.expatreader"]

# tell modulefinder that agizaing sax potentially agizas expatreader
_false = 0
ikiwa _false:
    agiza xml.sax.expatreader

agiza os, sys
ikiwa sio sys.flags.ignore_environment na "PY_SAX_PARSER" kwenye os.environ:
    default_parser_list = os.environ["PY_SAX_PARSER"].split(",")
toa os

_key = "python.xml.sax.parser"
ikiwa sys.platform[:4] == "java" na sys.registry.containsKey(_key):
    default_parser_list = sys.registry.getProperty(_key).split(",")


eleza make_parser(parser_list=()):
    """Creates na rudishas a SAX parser.

    Creates the first parser it ni able to instantiate of the ones
    given kwenye the iterable created by chaining parser_list and
    default_parser_list.  The iterables must contain the names of Python
    modules containing both a SAX parser na a create_parser function."""

    kila parser_name kwenye list(parser_list) + default_parser_list:
        jaribu:
            rudisha _create_parser(parser_name)
        tatizo ImportError kama e:
            agiza sys
            ikiwa parser_name kwenye sys.modules:
                # The parser module was found, but agizaing it
                # failed unexpectedly, pita this exception through
                ashiria
        tatizo SAXReaderNotAvailable:
            # The parser module detected that it won't work properly,
            # so try the next one
            pita

    ashiria SAXReaderNotAvailable("No parsers found", Tupu)

# --- Internal utility methods used by make_parser

ikiwa sys.platform[ : 4] == "java":
    eleza _create_parser(parser_name):
        kutoka org.python.core agiza imp
        drv_module = imp.agizaName(parser_name, 0, globals())
        rudisha drv_module.create_parser()

isipokua:
    eleza _create_parser(parser_name):
        drv_module = __import__(parser_name,{},{},['create_parser'])
        rudisha drv_module.create_parser()

toa sys
