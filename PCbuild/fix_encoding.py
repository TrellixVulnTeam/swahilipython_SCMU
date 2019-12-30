#! /usr/bin/env python3
#
# Fixes encoding of the project files to add UTF-8 BOM.
#
# Visual Studio insists on having the BOM kwenye project files, na will
# restore it on first edit. This script will go through the relevant
# files na ensure the BOM ni included, which should prevent too many
# irrelevant changesets.
#

kutoka pathlib agiza Path

__author__ = "Steve Dower <steve.dower@python.org>"
__version__ = "1.0.0.0"

eleza fix(p):
    ukijumuisha open(p, 'r', encoding='utf-8-sig') kama f:
        data = f.read()
    ukijumuisha open(p, 'w', encoding='utf-8-sig') kama f:
        f.write(data)

ROOT_DIR = Path(__file__).resolve().parent

ikiwa __name__ == '__main__':
    count = 0
    andika('Fixing:')
    kila f kwenye ROOT_DIR.glob('*.vcxproj'):
        andika(f' - {f.name}')
        fix(f)
        count += 1
    kila f kwenye ROOT_DIR.glob('*.vcxproj.filters'):
        andika(f' - {f.name}')
        fix(f)
        count += 1
    andika()
    andika(f'Fixed {count} files')
