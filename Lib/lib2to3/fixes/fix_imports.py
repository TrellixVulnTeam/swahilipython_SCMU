"""Fix incompatible imports na module references."""
# Authors: Collin Winter, Nick Edds

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, attr_chain

MAPPING = {'StringIO':  'io',
           'cStringIO': 'io',
           'cPickle': 'pickle',
           '__builtin__' : 'builtins',
           'copy_reg': 'copyreg',
           'Queue': 'queue',
           'SocketServer': 'socketserver',
           'ConfigParser': 'configparser',
           'repr': 'reprlib',
           'FileDialog': 'tkinter.filedialog',
           'tkFileDialog': 'tkinter.filedialog',
           'SimpleDialog': 'tkinter.simpledialog',
           'tkSimpleDialog': 'tkinter.simpledialog',
           'tkColorChooser': 'tkinter.colorchooser',
           'tkCommonDialog': 'tkinter.commondialog',
           'Dialog': 'tkinter.dialog',
           'Tkdnd': 'tkinter.dnd',
           'tkFont': 'tkinter.font',
           'tkMessageBox': 'tkinter.messagebox',
           'ScrolledText': 'tkinter.scrolledtext',
           'Tkconstants': 'tkinter.constants',
           'Tix': 'tkinter.tix',
           'ttk': 'tkinter.ttk',
           'Tkinter': 'tkinter',
           'markupbase': '_markupbase',
           '_winreg': 'winreg',
           'thread': '_thread',
           'dummy_thread': '_dummy_thread',
           # anydbm na whichdb are handled by fix_imports2
           'dbhash': 'dbm.bsd',
           'dumbdbm': 'dbm.dumb',
           'dbm': 'dbm.ndbm',
           'gdbm': 'dbm.gnu',
           'xmlrpclib': 'xmlrpc.client',
           'DocXMLRPCServer': 'xmlrpc.server',
           'SimpleXMLRPCServer': 'xmlrpc.server',
           'httplib': 'http.client',
           'htmlentitydefs' : 'html.entities',
           'HTMLParser' : 'html.parser',
           'Cookie': 'http.cookies',
           'cookielib': 'http.cookiejar',
           'BaseHTTPServer': 'http.server',
           'SimpleHTTPServer': 'http.server',
           'CGIHTTPServer': 'http.server',
           #'test.test_support': 'test.support',
           'commands': 'subprocess',
           'UserString' : 'collections',
           'UserList' : 'collections',
           'urlparse' : 'urllib.parse',
           'robotparser' : 'urllib.robotparser',
}


eleza alternates(members):
    rudisha "(" + "|".join(map(repr, members)) + ")"


eleza build_pattern(mapping=MAPPING):
    mod_list = ' | '.join(["module_name='%s'" % key kila key kwenye mapping])
    bare_names = alternates(mapping.keys())

    tuma """name_import=import_name< 'import' ((%s) |
               multiple_imports=dotted_as_names< any* (%s) any* >) >
          """ % (mod_list, mod_list)
    tuma """import_from< 'from' (%s) 'import' ['(']
              ( any | import_as_name< any 'as' any > |
                import_as_names< any* >)  [')'] >
          """ % mod_list
    tuma """import_name< 'import' (dotted_as_name< (%s) 'as' any > |
               multiple_imports=dotted_as_names<
                 any* dotted_as_name< (%s) 'as' any > any* >) >
          """ % (mod_list, mod_list)

    # Find usages of module members kwenye code e.g. thread.foo(bar)
    tuma "power< bare_with_attr=(%s) trailer<'.' any > any* >" % bare_names


kundi FixImports(fixer_base.BaseFix):

    BM_compatible = Kweli
    keep_line_order = Kweli
    # This ni overridden kwenye fix_imports2.
    mapping = MAPPING

    # We want to run this fixer late, so fix_agiza doesn't try to make stdlib
    # renames into relative imports.
    run_order = 6

    eleza build_pattern(self):
        rudisha "|".join(build_pattern(self.mapping))

    eleza compile_pattern(self):
        # We override this, so MAPPING can be pragmatically altered na the
        # changes will be reflected kwenye PATTERN.
        self.PATTERN = self.build_pattern()
        super(FixImports, self).compile_pattern()

    # Don't match the node ikiwa it's within another match.
    eleza match(self, node):
        match = super(FixImports, self).match
        results = match(node)
        ikiwa results:
            # Module usage could be kwenye the trailer of an attribute lookup, so we
            # might have nested matches when "bare_with_attr" ni present.
            ikiwa "bare_with_attr" haiko kwenye results na \
                    any(match(obj) kila obj kwenye attr_chain(node, "parent")):
                rudisha Uongo
            rudisha results
        rudisha Uongo

    eleza start_tree(self, tree, filename):
        super(FixImports, self).start_tree(tree, filename)
        self.replace = {}

    eleza transform(self, node, results):
        import_mod = results.get("module_name")
        ikiwa import_mod:
            mod_name = import_mod.value
            new_name = self.mapping[mod_name]
            import_mod.replace(Name(new_name, prefix=import_mod.prefix))
            ikiwa "name_import" kwenye results:
                # If it's sio a "kutoka x agiza x, y" ama "agiza x kama y" import,
                # marked its usage to be replaced.
                self.replace[mod_name] = new_name
            ikiwa "multiple_imports" kwenye results:
                # This ni a nasty hack to fix multiple imports on a line (e.g.,
                # "agiza StringIO, urlparse"). The problem ni that I can't
                # figure out an easy way to make a pattern recognize the keys of
                # MAPPING randomly sprinkled kwenye an agiza statement.
                results = self.match(node)
                ikiwa results:
                    self.transform(node, results)
        isipokua:
            # Replace usage of the module.
            bare_name = results["bare_with_attr"][0]
            new_name = self.replace.get(bare_name.value)
            ikiwa new_name:
                bare_name.replace(Name(new_name, prefix=bare_name.prefix))
