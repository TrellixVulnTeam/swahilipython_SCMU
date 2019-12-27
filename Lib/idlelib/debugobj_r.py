kutoka idlelib agiza rpc

eleza remote_object_tree_item(item):
    wrapper = WrappedObjectTreeItem(item)
    oid = id(wrapper)
    rpc.objecttable[oid] = wrapper
    rudisha oid

kundi WrappedObjectTreeItem:
    # Lives in PYTHON subprocess

    eleza __init__(self, item):
        self.__item = item

    eleza __getattr__(self, name):
        value = getattr(self.__item, name)
        rudisha value

    eleza _GetSubList(self):
        sub_list = self.__item._GetSubList()
        rudisha list(map(remote_object_tree_item, sub_list))

kundi StubObjectTreeItem:
    # Lives in IDLE process

    eleza __init__(self, sockio, oid):
        self.sockio = sockio
        self.oid = oid

    eleza __getattr__(self, name):
        value = rpc.MethodProxy(self.sockio, self.oid, name)
        rudisha value

    eleza _GetSubList(self):
        sub_list = self.sockio.remotecall(self.oid, "_GetSubList", (), {})
        rudisha [StubObjectTreeItem(self.sockio, oid) for oid in sub_list]


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_debugobj_r', verbosity=2)
