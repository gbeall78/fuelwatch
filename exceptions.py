__all__ = [
    "invalidStyleParameter", 
    "invalidClassParameter", 
    "noTableHeaderException",
    "tableHeaderDataSizeMismatchException",
]

class Error(Exception):
    pass

class invalidStyleParameter(Exception):
    pass

class invalidClassParameter(Exception):
    pass

class noTableHeaderException(Exception):
    pass

class tableHeaderDataSizeMismatchException(Exception):
    pass

class cacheFailureException(Exception):
    pass