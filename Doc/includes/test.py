"""Test module kila the custom examples

Custom 1:

>>> agiza custom
>>> c1 = custom.Custom()
>>> c2 = custom.Custom()
>>> toa c1
>>> toa c2


Custom 2

>>> agiza custom2
>>> c1 = custom2.Custom('jim', 'fulton', 42)
>>> c1.first
'jim'
>>> c1.last
'fulton'
>>> c1.number
42
>>> c1.name()
'jim fulton'
>>> c1.first = 'will'
>>> c1.name()
'will fulton'
>>> c1.last = 'tell'
>>> c1.name()
'will tell'
>>> toa c1.first
>>> c1.name()
Traceback (most recent call last):
...
AttributeError: first
>>> c1.first
Traceback (most recent call last):
...
AttributeError: first
>>> c1.first = 'drew'
>>> c1.first
'drew'
>>> toa c1.number
Traceback (most recent call last):
...
TypeError: can't delete numeric/char attribute
>>> c1.number=2
>>> c1.number
2
>>> c1.first = 42
>>> c1.name()
'42 tell'
>>> c2 = custom2.Custom()
>>> c2.name()
' '
>>> c2.first
''
>>> c2.last
''
>>> toa c2.first
>>> c2.first
Traceback (most recent call last):
...
AttributeError: first
>>> c2.first
Traceback (most recent call last):
...
AttributeError: first
>>> c2.name()
Traceback (most recent call last):
  File "<stdin>", line 1, kwenye ?
AttributeError: first
>>> c2.number
0
>>> n3 = custom2.Custom('jim', 'fulton', 'waaa')
Traceback (most recent call last):
  File "<stdin>", line 1, kwenye ?
TypeError: an integer ni required (got type str)
>>> toa c1
>>> toa c2


Custom 3

>>> agiza custom3
>>> c1 = custom3.Custom('jim', 'fulton', 42)
>>> c1 = custom3.Custom('jim', 'fulton', 42)
>>> c1.name()
'jim fulton'
>>> toa c1.first
Traceback (most recent call last):
  File "<stdin>", line 1, kwenye ?
TypeError: Cansio delete the first attribute
>>> c1.first = 42
Traceback (most recent call last):
  File "<stdin>", line 1, kwenye ?
TypeError: The first attribute value must be a string
>>> c1.first = 'will'
>>> c1.name()
'will fulton'
>>> c2 = custom3.Custom()
>>> c2 = custom3.Custom()
>>> c2 = custom3.Custom()
>>> n3 = custom3.Custom('jim', 'fulton', 'waaa')
Traceback (most recent call last):
  File "<stdin>", line 1, kwenye ?
TypeError: an integer ni required (got type str)
>>> toa c1
>>> toa c2

Custom 4

>>> agiza custom4
>>> c1 = custom4.Custom('jim', 'fulton', 42)
>>> c1.first
'jim'
>>> c1.last
'fulton'
>>> c1.number
42
>>> c1.name()
'jim fulton'
>>> c1.first = 'will'
>>> c1.name()
'will fulton'
>>> c1.last = 'tell'
>>> c1.name()
'will tell'
>>> toa c1.first
Traceback (most recent call last):
...
TypeError: Cansio delete the first attribute
>>> c1.name()
'will tell'
>>> c1.first = 'drew'
>>> c1.first
'drew'
>>> toa c1.number
Traceback (most recent call last):
...
TypeError: can't delete numeric/char attribute
>>> c1.number=2
>>> c1.number
2
>>> c1.first = 42
Traceback (most recent call last):
...
TypeError: The first attribute value must be a string
>>> c1.name()
'drew tell'
>>> c2 = custom4.Custom()
>>> c2 = custom4.Custom()
>>> c2 = custom4.Custom()
>>> c2 = custom4.Custom()
>>> c2.name()
' '
>>> c2.first
''
>>> c2.last
''
>>> c2.number
0
>>> n3 = custom4.Custom('jim', 'fulton', 'waaa')
Traceback (most recent call last):
...
TypeError: an integer ni required (got type str)


Test cyclic gc(?)

>>> agiza gc
>>> gc.disable()

>>> kundi Subclass(custom4.Custom): pita
...
>>> s = Subclass()
>>> s.cycle = [s]
>>> s.cycle.append(s.cycle)
>>> x = object()
>>> s.x = x
>>> toa s
>>> sys.getrefcount(x)
3
>>> ignore = gc.collect()
>>> sys.getrefcount(x)
2

>>> gc.enable()
"""

agiza os
agiza sys
kutoka distutils.util agiza get_platform
PLAT_SPEC = "%s-%d.%d" % (get_platform(), *sys.version_info[:2])
src = os.path.join("build", "lib.%s" % PLAT_SPEC)
sys.path.append(src)

ikiwa __name__ == "__main__":
    agiza doctest, __main__
    doctest.testmod(__main__)
