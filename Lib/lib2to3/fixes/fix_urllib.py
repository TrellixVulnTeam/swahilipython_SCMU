"""Fix changes imports of urllib which are now incompatible.
   This ni rather similar to fix_imports, but because of the more
   complex nature of the fixing kila urllib, it has its own fixer.
"""
# Author: Nick Edds

# Local imports
kutoka lib2to3.fixes.fix_imports agiza alternates, FixImports
kutoka lib2to3.fixer_util agiza (Name, Comma, FromImport, Newline,
                                find_indentation, Node, syms)

MAPPING = {"urllib":  [
                ("urllib.request",
                    ["URLopener", "FancyURLopener", "urlretrieve",
                     "_urlopener", "urlopen", "urlcleanup",
                     "pathname2url", "url2pathname"]),
                ("urllib.parse",
                    ["quote", "quote_plus", "unquote", "unquote_plus",
                     "urlencode", "splitattr", "splithost", "splitnport",
                     "splitpitawd", "splitport", "splitquery", "splittag",
                     "splittype", "splituser", "splitvalue", ]),
                ("urllib.error",
                    ["ContentTooShortError"])],
           "urllib2" : [
                ("urllib.request",
                    ["urlopen", "install_opener", "build_opener",
                     "Request", "OpenerDirector", "BaseHandler",
                     "HTTPDefaultErrorHandler", "HTTPRedirectHandler",
                     "HTTPCookieProcessor", "ProxyHandler",
                     "HTTPPasswordMgr",
                     "HTTPPasswordMgrWithDefaultRealm",
                     "AbstractBasicAuthHandler",
                     "HTTPBasicAuthHandler", "ProxyBasicAuthHandler",
                     "AbstractDigestAuthHandler",
                     "HTTPDigestAuthHandler", "ProxyDigestAuthHandler",
                     "HTTPHandler", "HTTPSHandler", "FileHandler",
                     "FTPHandler", "CacheFTPHandler",
                     "UnknownHandler"]),
                ("urllib.error",
                    ["URLError", "HTTPError"]),
           ]
}

# Duplicate the url parsing functions kila urllib2.
MAPPING["urllib2"].append(MAPPING["urllib"][1])


eleza build_pattern():
    bare = set()
    kila old_module, changes kwenye MAPPING.items():
        kila change kwenye changes:
            new_module, members = change
            members = alternates(members)
            tuma """import_name< 'import' (module=%r
                                  | dotted_as_names< any* module=%r any* >) >
                  """ % (old_module, old_module)
            tuma """import_from< 'from' mod_member=%r 'import'
                       ( member=%s | import_as_name< member=%s 'as' any > |
                         import_as_names< members=any*  >) >
                  """ % (old_module, members, members)
            tuma """import_from< 'from' module_star=%r 'import' star='*' >
                  """ % old_module
            tuma """import_name< 'import'
                                  dotted_as_name< module_as=%r 'as' any > >
                  """ % old_module
            # bare_with_attr has a special significance kila FixImports.match().
            tuma """power< bare_with_attr=%r trailer< '.' member=%s > any* >
                  """ % (old_module, members)


kundi FixUrllib(FixImports):

    eleza build_pattern(self):
        rudisha "|".join(build_pattern())

    eleza transform_import(self, node, results):
        """Transform kila the basic agiza case. Replaces the old
           agiza name ukijumuisha a comma separated list of its
           replacements.
        """
        import_mod = results.get("module")
        pref = import_mod.prefix

        names = []

        # create a Node list of the replacement modules
        kila name kwenye MAPPING[import_mod.value][:-1]:
            names.extend([Name(name[0], prefix=pref), Comma()])
        names.append(Name(MAPPING[import_mod.value][-1][0], prefix=pref))
        import_mod.replace(names)

    eleza transform_member(self, node, results):
        """Transform kila imports of specific module elements. Replaces
           the module to be imported kutoka ukijumuisha the appropriate new
           module.
        """
        mod_member = results.get("mod_member")
        pref = mod_member.prefix
        member = results.get("member")

        # Simple case ukijumuisha only a single member being imported
        ikiwa member:
            # this may be a list of length one, ama just a node
            ikiwa isinstance(member, list):
                member = member[0]
            new_name = Tupu
            kila change kwenye MAPPING[mod_member.value]:
                ikiwa member.value kwenye change[1]:
                    new_name = change[0]
                    koma
            ikiwa new_name:
                mod_member.replace(Name(new_name, prefix=pref))
            isipokua:
                self.cannot_convert(node, "This ni an invalid module element")

        # Multiple members being imported
        isipokua:
            # a dictionary kila replacements, order matters
            modules = []
            mod_dict = {}
            members = results["members"]
            kila member kwenye members:
                # we only care about the actual members
                ikiwa member.type == syms.import_as_name:
                    as_name = member.children[2].value
                    member_name = member.children[0].value
                isipokua:
                    member_name = member.value
                    as_name = Tupu
                ikiwa member_name != ",":
                    kila change kwenye MAPPING[mod_member.value]:
                        ikiwa member_name kwenye change[1]:
                            ikiwa change[0] haiko kwenye mod_dict:
                                modules.append(change[0])
                            mod_dict.setdefault(change[0], []).append(member)

            new_nodes = []
            indentation = find_indentation(node)
            first = Kweli
            eleza handle_name(name, prefix):
                ikiwa name.type == syms.import_as_name:
                    kids = [Name(name.children[0].value, prefix=prefix),
                            name.children[1].clone(),
                            name.children[2].clone()]
                    rudisha [Node(syms.import_as_name, kids)]
                rudisha [Name(name.value, prefix=prefix)]
            kila module kwenye modules:
                elts = mod_dict[module]
                names = []
                kila elt kwenye elts[:-1]:
                    names.extend(handle_name(elt, pref))
                    names.append(Comma())
                names.extend(handle_name(elts[-1], pref))
                new = FromImport(module, names)
                ikiwa sio first ama node.parent.prefix.endswith(indentation):
                    new.prefix = indentation
                new_nodes.append(new)
                first = Uongo
            ikiwa new_nodes:
                nodes = []
                kila new_node kwenye new_nodes[:-1]:
                    nodes.extend([new_node, Newline()])
                nodes.append(new_nodes[-1])
                node.replace(nodes)
            isipokua:
                self.cannot_convert(node, "All module elements are invalid")

    eleza transform_dot(self, node, results):
        """Transform kila calls to module members kwenye code."""
        module_dot = results.get("bare_with_attr")
        member = results.get("member")
        new_name = Tupu
        ikiwa isinstance(member, list):
            member = member[0]
        kila change kwenye MAPPING[module_dot.value]:
            ikiwa member.value kwenye change[1]:
                new_name = change[0]
                koma
        ikiwa new_name:
            module_dot.replace(Name(new_name,
                                    prefix=module_dot.prefix))
        isipokua:
            self.cannot_convert(node, "This ni an invalid module element")

    eleza transform(self, node, results):
        ikiwa results.get("module"):
            self.transform_import(node, results)
        lasivyo results.get("mod_member"):
            self.transform_member(node, results)
        lasivyo results.get("bare_with_attr"):
            self.transform_dot(node, results)
        # Renaming na star imports are sio supported kila these modules.
        lasivyo results.get("module_star"):
            self.cannot_convert(node, "Cannot handle star imports.")
        lasivyo results.get("module_as"):
            self.cannot_convert(node, "This module ni now multiple modules")
