"""Fix incompatible agizas and module references that must be fixed after
fix_agizas."""
kutoka . agiza fix_agizas


MAPPING = {
            'whichdb': 'dbm',
            'anydbm': 'dbm',
          }


class FixImports2(fix_agizas.FixImports):

    run_order = 7

    mapping = MAPPING
