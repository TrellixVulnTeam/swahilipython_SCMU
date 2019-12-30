x = 1

eleza __dir__():
    rudisha ['a', 'b', 'c']

eleza __getattr__(name):
    ikiwa name == "yolo":
         ashiria AttributeError("Deprecated, use whatever instead")
    rudisha f"There ni {name}"

y = 2
