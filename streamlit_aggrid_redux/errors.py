""" This file contains exception classes to help with diagnosing where errors occurred. """


class GridBuilderError(Exception):
    """ For errors in the builder. """
    pass


class GridOptionsBuilderError(Exception):
    """ For errors in the options builder. """
    pass
