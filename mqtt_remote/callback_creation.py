"""Functionality related to creating callbacks

Example:
    To import a file as a string:

    .. code-block:: python

        file_name = 'C:\\mydir\\file.txt'
        file_as_string = import_file_as_string(file_name)

    To copy a string to the clipboard:

    .. code-block:: python

        string_to_copy = 'Spam'
        copy_string_to_clipboard(string_to_copy)

    To copy a callback template to the clipboard:

    .. code-block:: python

        copy_template_to_clipboard()

    To create a file containing a callback:

    .. code-block:: python

        create_callback_file()


Attributes:
    TEMPLATE_FILE(str): Path of the callback template file
"""
from pathlib import Path

import pyperclip

import mqtt_remote.callbacks_local as callbacks_local



TEMPLATE_FILE = str(Path(__file__).parent / 'class_template.txt')



def import_file_as_string(file_name):
    """Returns the contents of a file as a string

    Args:
        file_name (str): The path of the file to import

    Returns:
        str: The contents of the file
    """
    with open(file_name, 'rt') as f:
        return f.read()


def copy_string_to_clipboard(string_to_copy):
    """Copies the supplied string to the OS clipboard

    Args:
        string_to_copy (str): The string to copy to the OS clipboard
    """
    pyperclip.copy(string_to_copy)


def copy_template_to_clipboard(file_name=None,
                               import_file_as_string_function=None,
                               string_to_clipboard_function=None):
    """Copies the callback template to the OS clipboard

    Args:
        file_name (str, optional): The path of the file to import. Defaults to None.
        import_file_as_string_function (Callable, optional): The function that imports a file as a
            string. Defaults to None.
        string_to_clipboard_function (Callable, optional): The function that copies a string to the
            OS clipboard. Defaults to None.
    """
    if not file_name:
        file_name = TEMPLATE_FILE

    if not import_file_as_string_function:
        import_file_as_string_function = import_file_as_string

    if not string_to_clipboard_function:
        string_to_clipboard_function = copy_string_to_clipboard

    template_string = import_file_as_string_function(file_name)
    string_to_clipboard_function(template_string)


def create_callback_file(file_name=None, callback=None):
    """Creates a file containing a callback template

    Args:
        file_name (str, optional): The path and filename to save the callback file to.
            Defaults to None.
        callback (str, optional): The callback to save as the contents of the callback file.
            Defaults to None.
    """
    if not file_name:
        input_string = ''.join(["Please enter a filename to save the callback to. ",
                                "The filename must end with '.py', e.g. 'example.py':"])
        file_name = input(input_string)
        file_name = str(Path(callbacks_local.LOCAL_CALLBACK_DIR_FULL_PATH) / file_name)

    if not callback:
        callback = import_file_as_string(TEMPLATE_FILE)

    with open(file_name, 'wt') as f:
        f.write(callback)
