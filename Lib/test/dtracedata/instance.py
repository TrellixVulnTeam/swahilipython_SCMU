agiza gc

kundi old_style_class():
    pita
kundi new_style_class(object):
    pita

a = old_style_class()
toa a
gc.collect()
b = new_style_class()
toa b
gc.collect()

a = old_style_class()
toa old_style_class
gc.collect()
b = new_style_class()
toa new_style_class
gc.collect()
toa a
gc.collect()
toa b
gc.collect()
