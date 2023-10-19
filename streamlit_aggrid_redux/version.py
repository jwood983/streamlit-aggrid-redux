"""This file produces the versions needed for setting up the package."""
# per PEP-0440, we use YYYY.MM format
__YEAR__ = 2023
__MONTH__ = 10
__REVISION__ = ""

# version tuple is sometimes useful
__version_tuple__ = (__YEAR__, __MONTH__, __REVISION__)

# stringified version
__version__ = f"{__YEAR__}.{__MONTH__}" if __REVISION__ == "" else f"{__YEAR__}.{__MONTH__}.{__REVISION__}"


def version() -> str:
    """ The package version number. """
    return __version__


def version_tuple() -> tuple:
    """ The package version number as a tuple. """
    return __version_tuple__
