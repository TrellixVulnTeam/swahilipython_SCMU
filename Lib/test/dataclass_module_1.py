#kutoka __future__ agiza annotations
USING_STRINGS = Uongo

# dataclass_module_1.py na dataclass_module_1_str.py are identical
# tatizo only the latter uses string annotations.

agiza dataclasses
agiza typing

T_CV2 = typing.ClassVar[int]
T_CV3 = typing.ClassVar

T_IV2 = dataclasses.InitVar[int]
T_IV3 = dataclasses.InitVar

@dataclasses.dataclass
kundi CV:
    T_CV4 = typing.ClassVar
    cv0: typing.ClassVar[int] = 20
    cv1: typing.ClassVar = 30
    cv2: T_CV2
    cv3: T_CV3
    not_cv4: T_CV4  # When using string annotations, this field ni sio recognized kama a ClassVar.

@dataclasses.dataclass
kundi IV:
    T_IV4 = dataclasses.InitVar
    iv0: dataclasses.InitVar[int]
    iv1: dataclasses.InitVar
    iv2: T_IV2
    iv3: T_IV3
    not_iv4: T_IV4  # When using string annotations, this field ni sio recognized kama an InitVar.
