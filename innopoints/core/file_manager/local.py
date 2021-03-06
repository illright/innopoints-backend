"""Manages static files. This particular module uses local file system to store files."""

import os
from typing import Union

from PIL import Image
from werkzeug.datastructures import FileStorage


class FileManagerLocal:
    """Implementation of the file manager using local file system."""
    def __init__(self, url='./static_files/'):
        self.base_path = url
        if not os.path.exists(url):
            os.makedirs(url)

    def _join_base(self, *paths: str) -> str:
        """Helper function to join path to base and normalize it according to OS."""
        return os.path.normpath(os.path.join(self.base_path, *paths))

    def retrieve(self, handle: str) -> bytes:
        """Get the file with given handle."""
        path = self._join_base(handle)
        if not os.path.exists(path):
            raise FileNotFoundError()
        file = open(path, 'rb')
        return file.read()

    def store(self, file: Union[FileStorage, Image.Image], handle: str):
        """Upload the given file with the handle."""
        filename = self._join_base(handle)
        if isinstance(file, Image.Image):
            file.save(filename, format='WebP', quality=100)
        else:
            file.save(filename)

    def delete(self, handle: str):
        """Delete the file with a given handle."""
        filename = self._join_base(handle)
        if not os.path.exists(filename):
            raise FileNotFoundError()
        os.remove(filename)
