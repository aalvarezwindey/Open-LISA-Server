from functools import reduce
import os
import sys
import errno

from open_lisa.exceptions.invalid_path_exception import InvalidPathException

# Sadly, Python fails to provide the following magic number for us
ERROR_INVALID_NAME = 123


class FileManager:
    def __init__(self) -> None:
        # NOTE: this class could have CRUDs logic for OpenLISA files (pos process, clibs, etc)
        pass

    def list_directory_recursively(self, directory):
        # Src of as_dict calculation https://code.activestate.com/recipes/577879-create-a-nested-dictionary-from-oswalk/
        as_dict = {}
        rootdir = directory.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, _, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], as_dict)
            parent[folders[-1]] = subdir

        # transform as_dict to list (best for frontend rendering)
        base_key = list(as_dict.keys())[0]
        directory_as_list = self.__transform_directory_represented_as_dict_to_list(
            as_dict[base_key])
        return directory_as_list

    @staticmethod
    def get_file_path(file_name):
        while file_name.startswith('/') or file_name.startswith('\\') or file_name.startswith('.'):
            file_name = file_name[1:]

        file_path = os.path.join(FileManager.__get_sandbox_dir(), file_name)

        if not FileManager.__is_path_exists_or_creatable(file_path):
            raise InvalidPathException(file_path)

        return file_path

    # Reference: https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta

    @staticmethod
    def __get_sandbox_dir():
        project_root_path = os.getcwd()
        sandbox_dir = os.path.join(project_root_path, os.getenv("USER_FILES_FOLDER"))

        return sandbox_dir

    @staticmethod
    def __is_path_creatable(pathname: str) -> bool:
        """
        `True` if the current user has sufficient permissions to create the passed
        pathname; `False` otherwise.
        """
        dirname = os.path.dirname(pathname) or os.getcwd()
        return os.access(dirname, os.W_OK)

    @staticmethod
    def __is_pathname_valid(pathname: str) -> bool:
        """
        `True` if the passed pathname is a valid pathname for the current OS;
        `False` otherwise.
        """
        try:
            if not isinstance(pathname, str) or not pathname:
                return False

            _, pathname = os.path.splitdrive(pathname)

            root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
                if sys.platform == 'win32' else os.path.sep
            assert os.path.isdir(root_dirname)  # ...Murphy and her ironclad Law

            root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

            for pathname_part in pathname.split(os.path.sep):
                try:
                    os.lstat(root_dirname + pathname_part)

                except OSError as exc:
                    if hasattr(exc, 'winerror'):
                        if exc.winerror == ERROR_INVALID_NAME:
                            return False
                    elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        return False
        except TypeError as exc:
            return False
        else:
            return True

    @staticmethod
    def __is_path_exists_or_creatable(pathname: str) -> bool:
        """
        `True` if the passed pathname is a valid pathname for the current OS _and_
        either currently exists or is hypothetically creatable; `False` otherwise.

        This function is guaranteed to _never_ raise exceptions.
        """
        try:
            return FileManager.__is_pathname_valid(pathname) and (
                    os.path.exists(pathname) or FileManager.__is_path_creatable(pathname))
        except OSError:
            return False

    def __transform_directory_represented_as_dict_to_list(self, directory_dict={}):
        result = []
        keys = list(directory_dict.keys())
        keys_that_are_directories = sorted(
            filter(lambda k: type(directory_dict[k]) == dict, keys))
        keys_that_are_files = sorted(
            filter(lambda k: directory_dict[k] == None, keys))
        keys = keys_that_are_directories + keys_that_are_files
        for k in keys:
            if type(directory_dict[k]) == dict:  # it is a directory
                children = self.__transform_directory_represented_as_dict_to_list(
                    directory_dict[k])
                result.append({
                    "name": k,
                    "type": "directory",
                    "children": children
                })
            elif directory_dict[k] == None:  # it is a file
                result.append({
                    "name": k,
                    "type": "file",
                })
        return result
