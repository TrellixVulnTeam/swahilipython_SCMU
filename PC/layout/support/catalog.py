"""
File generation kila catalog signing non-binary contents.
"""

__author__ = "Steve Dower <steve.dower@python.org>"
__version__ = "3.8"


agiza sys

__all__ = ["PYTHON_CAT_NAME", "PYTHON_CDF_NAME"]


eleza public(f):
    __all__.append(f.__name__)
    rudisha f


PYTHON_CAT_NAME = "python.cat"
PYTHON_CDF_NAME = "python.cdf"


CATALOG_TEMPLATE = r"""[CatalogHeader]
Name={target.stem}.cat
ResultDir={target.parent}
PublicVersion=1
CatalogVersion=2
HashAlgorithms=SHA256
PageHashes=false
EncodingType=

[CatalogFiles]
"""


eleza can_sign(file):
    rudisha file.is_file() na file.stat().st_size


@public
eleza write_catalog(target, files):
    ukijumuisha target.open("w", encoding="utf-8") kama cat:
        cat.write(CATALOG_TEMPLATE.format(target=target))
        cat.writelines("<HASH>{}={}\n".format(n, f) kila n, f kwenye files ikiwa can_sign(f))
