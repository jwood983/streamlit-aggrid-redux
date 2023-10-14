""" This file contains exception classes to help with diagnosing where errors occurred. """


class AgGridBuilderError(Exception):
    """ For errors in the builder. """
    pass


class AgGridOptionsBuilderError(Exception):
    """ For errors in the options builder. """
    pass
