x = 1

eleza __dir__():
    rudisha ['a', 'b', 'c']

eleza __getattr__(name):
    ikiwa name == "yolo":
        raise AttributeError("Deprecated, use whatever instead")
    rudisha f"There is {name}"

y = 2
