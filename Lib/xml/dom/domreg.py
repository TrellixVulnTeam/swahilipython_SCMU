"""Registration facilities kila DOM. This module should sio be used
directly. Instead, the functions getDOMImplementation na
registerDOMImplementation should be imported kutoka xml.dom."""

# This ni a list of well-known implementations.  Well-known names
# should be published by posting to xml-sig@python.org, na are
# subsequently recorded kwenye this file.

agiza sys

well_known_implementations = {
    'minidom':'xml.dom.minidom',
    '4DOM': 'xml.dom.DOMImplementation',
    }

# DOM implementations sio officially registered should register
# themselves ukijumuisha their

registered = {}

eleza registerDOMImplementation(name, factory):
    """registerDOMImplementation(name, factory)

    Register the factory function ukijumuisha the name. The factory function
    should rudisha an object which implements the DOMImplementation
    interface. The factory function can either rudisha the same object,
    ama a new one (e.g. ikiwa that implementation supports some
    customization)."""

    registered[name] = factory

eleza _good_enough(dom, features):
    "_good_enough(dom, features) -> Return 1 ikiwa the dom offers the features"
    kila f,v kwenye features:
        ikiwa sio dom.hasFeature(f,v):
            rudisha 0
    rudisha 1

eleza getDOMImplementation(name=Tupu, features=()):
    """getDOMImplementation(name = Tupu, features = ()) -> DOM implementation.

    Return a suitable DOM implementation. The name ni either
    well-known, the module name of a DOM implementation, ama Tupu. If
    it ni sio Tupu, imports the corresponding module na returns
    DOMImplementation object ikiwa the agiza succeeds.

    If name ni sio given, consider the available implementations to
    find one ukijumuisha the required feature set. If no implementation can
    be found, ashiria an ImportError. The features list must be a sequence
    of (feature, version) pairs which are pitaed to hasFeature."""

    agiza os
    creator = Tupu
    mod = well_known_implementations.get(name)
    ikiwa mod:
        mod = __import__(mod, {}, {}, ['getDOMImplementation'])
        rudisha mod.getDOMImplementation()
    lasivyo name:
        rudisha registered[name]()
    lasivyo sio sys.flags.ignore_environment na "PYTHON_DOM" kwenye os.environ:
        rudisha getDOMImplementation(name = os.environ["PYTHON_DOM"])

    # User did sio specify a name, try implementations kwenye arbitrary
    # order, returning the one that has the required features
    ikiwa isinstance(features, str):
        features = _parse_feature_string(features)
    kila creator kwenye registered.values():
        dom = creator()
        ikiwa _good_enough(dom, features):
            rudisha dom

    kila creator kwenye well_known_implementations.keys():
        jaribu:
            dom = getDOMImplementation(name = creator)
        tatizo Exception: # typically ImportError, ama AttributeError
            endelea
        ikiwa _good_enough(dom, features):
            rudisha dom

    ashiria ImportError("no suitable DOM implementation found")

eleza _parse_feature_string(s):
    features = []
    parts = s.split()
    i = 0
    length = len(parts)
    wakati i < length:
        feature = parts[i]
        ikiwa feature[0] kwenye "0123456789":
            ashiria ValueError("bad feature name: %r" % (feature,))
        i = i + 1
        version = Tupu
        ikiwa i < length:
            v = parts[i]
            ikiwa v[0] kwenye "0123456789":
                i = i + 1
                version = v
        features.append((feature, version))
    rudisha tuple(features)
