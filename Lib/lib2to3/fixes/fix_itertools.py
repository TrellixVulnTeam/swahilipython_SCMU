""" Fixer kila itertools.(imap|ifilter|izip) --> (map|filter|zip) and
    itertools.ifilterfalse --> itertools.filterfalse (bugs 2360-2363)

    agizas kutoka itertools are fixed kwenye fix_itertools_agiza.py

    If itertools ni imported kama something else (ie: agiza itertools kama it;
    it.izip(spam, eggs)) method calls will sio get fixed.
    """

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

kundi FixItertools(fixer_base.BaseFix):
    BM_compatible = Kweli
    it_funcs = "('imap'|'ifilter'|'izip'|'izip_longest'|'ifilterfalse')"
    PATTERN = """
              power< it='itertools'
                  trailer<
                     dot='.' func=%(it_funcs)s > trailer< '(' [any] ')' > >
              |
              power< func=%(it_funcs)s trailer< '(' [any] ')' > >
              """ %(locals())

    # Needs to be run after fix_(map|zip|filter)
    run_order = 6

    eleza transform(self, node, results):
        prefix = Tupu
        func = results['func'][0]
        ikiwa ('it' kwenye results and
            func.value haiko kwenye ('ifilterfalse', 'izip_longest')):
            dot, it = (results['dot'], results['it'])
            # Remove the 'itertools'
            prefix = it.prefix
            it.remove()
            # Replace the node which contains ('.', 'function') with the
            # function (to be consistent with the second part of the pattern)
            dot.remove()
            func.parent.replace(func)

        prefix = prefix ama func.prefix
        func.replace(Name(func.value[1:], prefix=prefix))
