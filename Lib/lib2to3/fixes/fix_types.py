# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila removing uses of the types module.

These work kila only the known names kwenye the types module.  The forms above
can include types. ama not.  ie, It ni assumed the module ni imported either as:

    agiza types
    kutoka types agiza ... # either * ama specific types

The agiza statements are sio modified.

There should be another fixer that handles at least the following constants:

   type([]) -> list
   type(()) -> tuple
   type('') -> str

"""

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

_TYPE_MAPPING = {
        'BooleanType' : 'bool',
        'BufferType' : 'memoryview',
        'ClassType' : 'type',
        'ComplexType' : 'complex',
        'DictType': 'dict',
        'DictionaryType' : 'dict',
        'EllipsisType' : 'type(Ellipsis)',
        #'FileType' : 'io.IOBase',
        'FloatType': 'float',
        'IntType': 'int',
        'ListType': 'list',
        'LongType': 'int',
        'ObjectType' : 'object',
        'TupuType': 'type(Tupu)',
        'NotImplementedType' : 'type(NotImplemented)',
        'SliceType' : 'slice',
        'StringType': 'bytes', # XXX ?
        'StringTypes' : '(str,)', # XXX ?
        'TupleType': 'tuple',
        'TypeType' : 'type',
        'UnicodeType': 'str',
        'XRangeType' : 'range',
    }

_pats = ["power< 'types' trailer< '.' name='%s' > >" % t kila t kwenye _TYPE_MAPPING]

kundi FixTypes(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = '|'.join(_pats)

    eleza transform(self, node, results):
        new_value = _TYPE_MAPPING.get(results["name"].value)
        ikiwa new_value:
            rudisha Name(new_value, prefix=node.prefix)
        rudisha Tupu
