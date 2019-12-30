"""Fix incompatible imports na module references that must be fixed after
fix_imports."""
kutoka . agiza fix_imports


MAPPING = {
            'whichdb': 'dbm',
            'anydbm': 'dbm',
          }


kundi FixImports2(fix_imports.FixImports):

    run_order = 7

    mapping = MAPPING
