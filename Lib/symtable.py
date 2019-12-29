"""Interface to the compiler's internal symbol tables"""

agiza _symtable
kutoka _symtable agiza (USE, DEF_GLOBAL, DEF_NONLOCAL, DEF_LOCAL, DEF_PARAM,
     DEF_IMPORT, DEF_BOUND, DEF_ANNOT, SCOPE_OFF, SCOPE_MASK, FREE,
     LOCAL, GLOBAL_IMPLICIT, GLOBAL_EXPLICIT, CELL)

agiza weakref

__all__ = ["symtable", "SymbolTable", "Class", "Function", "Symbol"]

eleza symtable(code, filename, compile_type):
    top = _symtable.symtable(code, filename, compile_type)
    rudisha _newSymbolTable(top, filename)

kundi SymbolTableFactory:
    eleza __init__(self):
        self.__memo = weakref.WeakValueDictionary()

    eleza new(self, table, filename):
        ikiwa table.type == _symtable.TYPE_FUNCTION:
            rudisha Function(table, filename)
        ikiwa table.type == _symtable.TYPE_CLASS:
            rudisha Class(table, filename)
        rudisha SymbolTable(table, filename)

    eleza __call__(self, table, filename):
        key = table, filename
        obj = self.__memo.get(key, Tupu)
        ikiwa obj ni Tupu:
            obj = self.__memo[key] = self.new(table, filename)
        rudisha obj

_newSymbolTable = SymbolTableFactory()


kundi SymbolTable(object):

    eleza __init__(self, raw_table, filename):
        self._table = raw_table
        self._filename = filename
        self._symbols = {}

    eleza __repr__(self):
        ikiwa self.__class__ == SymbolTable:
            kind = ""
        isipokua:
            kind = "%s " % self.__class__.__name__

        ikiwa self._table.name == "global":
            rudisha "<{0}SymbolTable kila module {1}>".format(kind, self._filename)
        isipokua:
            rudisha "<{0}SymbolTable kila {1} kwenye {2}>".format(kind,
                                                            self._table.name,
                                                            self._filename)

    eleza get_type(self):
        ikiwa self._table.type == _symtable.TYPE_MODULE:
            rudisha "module"
        ikiwa self._table.type == _symtable.TYPE_FUNCTION:
            rudisha "function"
        ikiwa self._table.type == _symtable.TYPE_CLASS:
            rudisha "class"
        assert self._table.type kwenye (1, 2, 3), \
               "unexpected type: {0}".format(self._table.type)

    eleza get_id(self):
        rudisha self._table.id

    eleza get_name(self):
        rudisha self._table.name

    eleza get_lineno(self):
        rudisha self._table.lineno

    eleza is_optimized(self):
        rudisha bool(self._table.type == _symtable.TYPE_FUNCTION)

    eleza is_nested(self):
        rudisha bool(self._table.nested)

    eleza has_children(self):
        rudisha bool(self._table.children)

    eleza has_exec(self):
        """Return true ikiwa the scope uses exec.  Deprecated method."""
        rudisha Uongo

    eleza get_identifiers(self):
        rudisha self._table.symbols.keys()

    eleza lookup(self, name):
        sym = self._symbols.get(name)
        ikiwa sym ni Tupu:
            flags = self._table.symbols[name]
            namespaces = self.__check_children(name)
            sym = self._symbols[name] = Symbol(name, flags, namespaces)
        rudisha sym

    eleza get_symbols(self):
        rudisha [self.lookup(ident) kila ident kwenye self.get_identifiers()]

    eleza __check_children(self, name):
        rudisha [_newSymbolTable(st, self._filename)
                kila st kwenye self._table.children
                ikiwa st.name == name]

    eleza get_children(self):
        rudisha [_newSymbolTable(st, self._filename)
                kila st kwenye self._table.children]


kundi Function(SymbolTable):

    # Default values kila instance variables
    __params = Tupu
    __locals = Tupu
    __frees = Tupu
    __globals = Tupu
    __nonlocals = Tupu

    eleza __idents_matching(self, test_func):
        rudisha tuple(ident kila ident kwenye self.get_identifiers()
                     ikiwa test_func(self._table.symbols[ident]))

    eleza get_parameters(self):
        ikiwa self.__params ni Tupu:
            self.__params = self.__idents_matching(lambda x:x & DEF_PARAM)
        rudisha self.__params

    eleza get_locals(self):
        ikiwa self.__locals ni Tupu:
            locs = (LOCAL, CELL)
            test = lambda x: ((x >> SCOPE_OFF) & SCOPE_MASK) kwenye locs
            self.__locals = self.__idents_matching(test)
        rudisha self.__locals

    eleza get_globals(self):
        ikiwa self.__globals ni Tupu:
            glob = (GLOBAL_IMPLICIT, GLOBAL_EXPLICIT)
            test = lambda x:((x >> SCOPE_OFF) & SCOPE_MASK) kwenye glob
            self.__globals = self.__idents_matching(test)
        rudisha self.__globals

    eleza get_nonlocals(self):
        ikiwa self.__nonlocals ni Tupu:
            self.__nonlocals = self.__idents_matching(lambda x:x & DEF_NONLOCAL)
        rudisha self.__nonlocals

    eleza get_frees(self):
        ikiwa self.__frees ni Tupu:
            is_free = lambda x:((x >> SCOPE_OFF) & SCOPE_MASK) == FREE
            self.__frees = self.__idents_matching(is_free)
        rudisha self.__frees


kundi Class(SymbolTable):

    __methods = Tupu

    eleza get_methods(self):
        ikiwa self.__methods ni Tupu:
            d = {}
            kila st kwenye self._table.children:
                d[st.name] = 1
            self.__methods = tuple(d)
        rudisha self.__methods


kundi Symbol(object):

    eleza __init__(self, name, flags, namespaces=Tupu):
        self.__name = name
        self.__flags = flags
        self.__scope = (flags >> SCOPE_OFF) & SCOPE_MASK # like PyST_GetScope()
        self.__namespaces = namespaces ama ()

    eleza __repr__(self):
        rudisha "<symbol {0!r}>".format(self.__name)

    eleza get_name(self):
        rudisha self.__name

    eleza is_referenced(self):
        rudisha bool(self.__flags & _symtable.USE)

    eleza is_parameter(self):
        rudisha bool(self.__flags & DEF_PARAM)

    eleza is_global(self):
        rudisha bool(self.__scope kwenye (GLOBAL_IMPLICIT, GLOBAL_EXPLICIT))

    eleza is_nonlocal(self):
        rudisha bool(self.__flags & DEF_NONLOCAL)

    eleza is_declared_global(self):
        rudisha bool(self.__scope == GLOBAL_EXPLICIT)

    eleza is_local(self):
        rudisha bool(self.__flags & DEF_BOUND)

    eleza is_annotated(self):
        rudisha bool(self.__flags & DEF_ANNOT)

    eleza is_free(self):
        rudisha bool(self.__scope == FREE)

    eleza is_imported(self):
        rudisha bool(self.__flags & DEF_IMPORT)

    eleza is_assigned(self):
        rudisha bool(self.__flags & DEF_LOCAL)

    eleza is_namespace(self):
        """Returns true ikiwa name binding introduces new namespace.

        If the name ni used kama the target of a function ama class
        statement, this will be true.

        Note that a single name can be bound to multiple objects.  If
        is_namespace() ni true, the name may also be bound to other
        objects, like an int ama list, that does sio introduce a new
        namespace.
        """
        rudisha bool(self.__namespaces)

    eleza get_namespaces(self):
        """Return a list of namespaces bound to this name"""
        rudisha self.__namespaces

    eleza get_namespace(self):
        """Returns the single namespace bound to this name.

        Raises ValueError ikiwa the name ni bound to multiple namespaces.
        """
        ikiwa len(self.__namespaces) != 1:
            ashiria ValueError("name ni bound to multiple namespaces")
        rudisha self.__namespaces[0]

ikiwa __name__ == "__main__":
    agiza os, sys
    ukijumuisha open(sys.argv[0]) kama f:
        src = f.read()
    mod = symtable(src, os.path.split(sys.argv[0])[1], "exec")
    kila ident kwenye mod.get_identifiers():
        info = mod.lookup(ident)
        andika(info, info.is_local(), info.is_namespace())
