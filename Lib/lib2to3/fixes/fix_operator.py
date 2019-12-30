"""Fixer kila operator functions.

operator.isCallable(obj)       -> callable(obj)
operator.sequenceIncludes(obj) -> operator.contains(obj)
operator.isSequenceType(obj)   -> isinstance(obj, collections.abc.Sequence)
operator.isMappingType(obj)    -> isinstance(obj, collections.abc.Mapping)
operator.isNumberType(obj)     -> isinstance(obj, numbers.Number)
operator.repeat(obj, n)        -> operator.mul(obj, n)
operator.irepeat(obj, n)       -> operator.imul(obj, n)
"""

agiza collections.abc

# Local imports
kutoka lib2to3 agiza fixer_base
kutoka lib2to3.fixer_util agiza Call, Name, String, touch_import


eleza invocation(s):
    eleza dec(f):
        f.invocation = s
        rudisha f
    rudisha dec


kundi FixOperator(fixer_base.BaseFix):
    BM_compatible = Kweli
    order = "pre"

    methods = """
              method=('isCallable'|'sequenceIncludes'
                     |'isSequenceType'|'isMappingType'|'isNumberType'
                     |'repeat'|'irepeat')
              """
    obj = "'(' obj=any ')'"
    PATTERN = """
              power< module='operator'
                trailer< '.' %(methods)s > trailer< %(obj)s > >
              |
              power< %(methods)s trailer< %(obj)s > >
              """ % dict(methods=methods, obj=obj)

    eleza transform(self, node, results):
        method = self._check_method(node, results)
        ikiwa method ni sio Tupu:
            rudisha method(node, results)

    @invocation("operator.contains(%s)")
    eleza _sequenceIncludes(self, node, results):
        rudisha self._handle_rename(node, results, "contains")

    @invocation("callable(%s)")
    eleza _isCallable(self, node, results):
        obj = results["obj"]
        rudisha Call(Name("callable"), [obj.clone()], prefix=node.prefix)

    @invocation("operator.mul(%s)")
    eleza _repeat(self, node, results):
        rudisha self._handle_rename(node, results, "mul")

    @invocation("operator.imul(%s)")
    eleza _irepeat(self, node, results):
        rudisha self._handle_rename(node, results, "imul")

    @invocation("isinstance(%s, collections.abc.Sequence)")
    eleza _isSequenceType(self, node, results):
        rudisha self._handle_type2abc(node, results, "collections.abc", "Sequence")

    @invocation("isinstance(%s, collections.abc.Mapping)")
    eleza _isMappingType(self, node, results):
        rudisha self._handle_type2abc(node, results, "collections.abc", "Mapping")

    @invocation("isinstance(%s, numbers.Number)")
    eleza _isNumberType(self, node, results):
        rudisha self._handle_type2abc(node, results, "numbers", "Number")

    eleza _handle_rename(self, node, results, name):
        method = results["method"][0]
        method.value = name
        method.changed()

    eleza _handle_type2abc(self, node, results, module, abc):
        touch_import(Tupu, module, node)
        obj = results["obj"]
        args = [obj.clone(), String(", " + ".".join([module, abc]))]
        rudisha Call(Name("isinstance"), args, prefix=node.prefix)

    eleza _check_method(self, node, results):
        method = getattr(self, "_" + results["method"][0].value)
        ikiwa isinstance(method, collections.abc.Callable):
            ikiwa "module" kwenye results:
                rudisha method
            isipokua:
                sub = (str(results["obj"]),)
                invocation_str = method.invocation % sub
                self.warning(node, "You should use '%s' here." % invocation_str)
        rudisha Tupu
