"""Something just to look at via pydoc."""

agiza types

kundi A_classic:
    "A classic class."
    eleza A_method(self):
        "Method defined kwenye A."
    eleza AB_method(self):
        "Method defined kwenye A na B."
    eleza AC_method(self):
        "Method defined kwenye A na C."
    eleza AD_method(self):
        "Method defined kwenye A na D."
    eleza ABC_method(self):
        "Method defined kwenye A, B na C."
    eleza ABD_method(self):
        "Method defined kwenye A, B na D."
    eleza ACD_method(self):
        "Method defined kwenye A, C na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."


kundi B_classic(A_classic):
    "A classic class, derived kutoka A_classic."
    eleza AB_method(self):
        "Method defined kwenye A na B."
    eleza ABC_method(self):
        "Method defined kwenye A, B na C."
    eleza ABD_method(self):
        "Method defined kwenye A, B na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."
    eleza B_method(self):
        "Method defined kwenye B."
    eleza BC_method(self):
        "Method defined kwenye B na C."
    eleza BD_method(self):
        "Method defined kwenye B na D."
    eleza BCD_method(self):
        "Method defined kwenye B, C na D."

kundi C_classic(A_classic):
    "A classic class, derived kutoka A_classic."
    eleza AC_method(self):
        "Method defined kwenye A na C."
    eleza ABC_method(self):
        "Method defined kwenye A, B na C."
    eleza ACD_method(self):
        "Method defined kwenye A, C na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."
    eleza BC_method(self):
        "Method defined kwenye B na C."
    eleza BCD_method(self):
        "Method defined kwenye B, C na D."
    eleza C_method(self):
        "Method defined kwenye C."
    eleza CD_method(self):
        "Method defined kwenye C na D."

kundi D_classic(B_classic, C_classic):
    "A classic class, derived kutoka B_classic na C_classic."
    eleza AD_method(self):
        "Method defined kwenye A na D."
    eleza ABD_method(self):
        "Method defined kwenye A, B na D."
    eleza ACD_method(self):
        "Method defined kwenye A, C na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."
    eleza BD_method(self):
        "Method defined kwenye B na D."
    eleza BCD_method(self):
        "Method defined kwenye B, C na D."
    eleza CD_method(self):
        "Method defined kwenye C na D."
    eleza D_method(self):
        "Method defined kwenye D."


kundi A_new(object):
    "A new-style class."

    eleza A_method(self):
        "Method defined kwenye A."
    eleza AB_method(self):
        "Method defined kwenye A na B."
    eleza AC_method(self):
        "Method defined kwenye A na C."
    eleza AD_method(self):
        "Method defined kwenye A na D."
    eleza ABC_method(self):
        "Method defined kwenye A, B na C."
    eleza ABD_method(self):
        "Method defined kwenye A, B na D."
    eleza ACD_method(self):
        "Method defined kwenye A, C na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."

    eleza A_classmethod(cls, x):
        "A kundi method defined kwenye A."
    A_classmethod = classmethod(A_classmethod)

    eleza A_staticmethod():
        "A static method defined kwenye A."
    A_staticmethod = staticmethod(A_staticmethod)

    eleza _getx(self):
        "A property getter function."
    eleza _setx(self, value):
        "A property setter function."
    eleza _delx(self):
        "A property deleter function."
    A_property = property(fdel=_delx, fget=_getx, fset=_setx,
                          doc="A sample property defined kwenye A.")

    A_int_alias = int

kundi B_new(A_new):
    "A new-style class, derived kutoka A_new."

    eleza AB_method(self):
        "Method defined kwenye A na B."
    eleza ABC_method(self):
        "Method defined kwenye A, B na C."
    eleza ABD_method(self):
        "Method defined kwenye A, B na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."
    eleza B_method(self):
        "Method defined kwenye B."
    eleza BC_method(self):
        "Method defined kwenye B na C."
    eleza BD_method(self):
        "Method defined kwenye B na D."
    eleza BCD_method(self):
        "Method defined kwenye B, C na D."

kundi C_new(A_new):
    "A new-style class, derived kutoka A_new."

    eleza AC_method(self):
        "Method defined kwenye A na C."
    eleza ABC_method(self):
        "Method defined kwenye A, B na C."
    eleza ACD_method(self):
        "Method defined kwenye A, C na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."
    eleza BC_method(self):
        "Method defined kwenye B na C."
    eleza BCD_method(self):
        "Method defined kwenye B, C na D."
    eleza C_method(self):
        "Method defined kwenye C."
    eleza CD_method(self):
        "Method defined kwenye C na D."

kundi D_new(B_new, C_new):
    """A new-style class, derived kutoka B_new na C_new.
    """

    eleza AD_method(self):
        "Method defined kwenye A na D."
    eleza ABD_method(self):
        "Method defined kwenye A, B na D."
    eleza ACD_method(self):
        "Method defined kwenye A, C na D."
    eleza ABCD_method(self):
        "Method defined kwenye A, B, C na D."
    eleza BD_method(self):
        "Method defined kwenye B na D."
    eleza BCD_method(self):
        "Method defined kwenye B, C na D."
    eleza CD_method(self):
        "Method defined kwenye C na D."
    eleza D_method(self):
        "Method defined kwenye D."

kundi FunkyProperties(object):
    """From SF bug 472347, by Roeland Rengelink.

    Property getters etc may sio be vanilla functions ama methods,
    na this used to make GUI pydoc blow up.
    """

    eleza __init__(self):
        self.desc = {'x':0}

    kundi get_desc:
        eleza __init__(self, attr):
            self.attr = attr
        eleza __call__(self, inst):
            andika('Get called', self, inst)
            rudisha inst.desc[self.attr]
    kundi set_desc:
        eleza __init__(self, attr):
            self.attr = attr
        eleza __call__(self, inst, val):
            andika('Set called', self, inst, val)
            inst.desc[self.attr] = val
    kundi del_desc:
        eleza __init__(self, attr):
            self.attr = attr
        eleza __call__(self, inst):
            andika('Del called', self, inst)
            toa inst.desc[self.attr]

    x = property(get_desc('x'), set_desc('x'), del_desc('x'), 'prop x')


submodule = types.ModuleType(__name__ + '.submodule',
    """A submodule, which should appear kwenye its parent's summary""")
