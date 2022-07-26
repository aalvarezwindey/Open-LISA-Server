from .base_exception import OpenLISAException


class InvalidPathException(OpenLISAException):
    """
    Raised when trying to manipulate an invalid path in file system
    """

    def __init__(self, file_path):
        self.file_path = file_path
        message = "the given path {} is invalid.".format(file_path)
        super().__init__(message)
