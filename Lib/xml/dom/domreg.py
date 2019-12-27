"""Registration facilities for DOM. This module should not be used
directly. Instead, the functions getDOMImplementation and
registerDOMImplementation should be imported kutoka xml.dom."""

# This is a list of well-known implementations.  Well-known names
# should be published by posting to xml-sig@python.org, and are
# subsequently recorded in this file.

agiza sys

well_known_implementations = {
    'minidom':'xml.dom.minidom',
    '4DOM': 'xml.dom.DOMImplementation',
    }

# DOM implementations not officially registered should register
# themselves with their

registered = {}

eleza registerDOMImplementation(name, factory):
    """registerDOMImplementation(name, factory)

    Register the factory function with the name. The factory function
    should rudisha an object which implements the DOMImplementation
    interface. The factory function can either rudisha the same object,
    or a new one (e.g. ikiwa that implementation supports some
    customization)."""

    registered[name] = factory

eleza _good_enough(dom, features):
    "_good_enough(dom, features) -> Return 1 ikiwa the dom offers the features"
    for f,v in features:
        ikiwa not dom.hasFeature(f,v):
            rudisha 0
    rudisha 1

eleza getDOMImplementation(name=None, features=()):
    """getDOMImplementation(name = None, features = ()) -> DOM implementation.

    Return a suitable DOM implementation. The name is either
    well-known, the module name of a DOM implementation, or None. If
    it is not None, agizas the corresponding module and returns
    DOMImplementation object ikiwa the agiza succeeds.

    If name is not given, consider the available implementations to
    find one with the required feature set. If no implementation can
    be found, raise an ImportError. The features list must be a sequence
    of (feature, version) pairs which are passed to hasFeature."""

    agiza os
    creator = None
    mod = well_known_implementations.get(name)
    ikiwa mod:
        mod = __import__(mod, {}, {}, ['getDOMImplementation'])
        rudisha mod.getDOMImplementation()
    elikiwa name:
        rudisha registered[name]()
    elikiwa not sys.flags.ignore_environment and "PYTHON_DOM" in os.environ:
        rudisha getDOMImplementation(name = os.environ["PYTHON_DOM"])

    # User did not specify a name, try implementations in arbitrary
    # order, returning the one that has the required features
    ikiwa isinstance(features, str):
        features = _parse_feature_string(features)
    for creator in registered.values():
        dom = creator()
        ikiwa _good_enough(dom, features):
            rudisha dom

    for creator in well_known_implementations.keys():
        try:
            dom = getDOMImplementation(name = creator)
        except Exception: # typically ImportError, or AttributeError
            continue
        ikiwa _good_enough(dom, features):
            rudisha dom

    raise ImportError("no suitable DOM implementation found")

eleza _parse_feature_string(s):
    features = []
    parts = s.split()
    i = 0
    length = len(parts)
    while i < length:
        feature = parts[i]
        ikiwa feature[0] in "0123456789":
            raise ValueError("bad feature name: %r" % (feature,))
        i = i + 1
        version = None
        ikiwa i < length:
            v = parts[i]
            ikiwa v[0] in "0123456789":
                i = i + 1
                version = v
        features.append((feature, version))
    rudisha tuple(features)
