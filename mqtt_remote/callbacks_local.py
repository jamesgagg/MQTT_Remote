"""Local callback related functionality.

Examples:

    To get the local callback modules:

        .. code-block:: python

            full_path_of_local_callbacks = Path(LOCAL_CALLBACK_DIR_FULL_PATH)
            local_callbacks = local_callback_modules(full_path_of_local_callbacks)


    To import the local callback modules manually:

        .. code-block:: python

            full_path_of_local_callbacks = Path(LOCAL_CALLBACK_DIR_FULL_PATH)
            local_callbacks = local_callback_modules(full_path_of_local_callbacks)
            import_local_callback_modules(local_callbacks, LOCAL_CALLBACKS_DIR_NAME)


    To import the local callback modules automatically:

        .. code-block:: python

            auto_import_local_callback_modules()


Attributes:
    LOCAL_CALLBACKS_DIR_NAME (str): The name of the directory where the files containing the local
        callbacks are stored.
    LOCAL_CALLBACK_DIR_FULL_PATH (str): The full path of the directory where the files containing
        the local callbacks are stored.
"""
from pathlib import Path

import importlib



LOCAL_CALLBACKS_DIR_NAME = 'local_callbacks'
LOCAL_CALLBACK_DIR_FULL_PATH = str(Path(__file__).parent / LOCAL_CALLBACKS_DIR_NAME)



def local_callback_modules(local_callback_path):
    """Gets the local callback modules

    Args:
        local_callback_path (pathlib.Path): The directory where the files containing the local
            callbacks are stored.

    Returns:
        generator[pathlib.Path]: The local callback modules.
    """
    return local_callback_path.glob('*.py')


def import_local_callback_modules(local_callbacks, directory):
    """Imports local callback modules

    Args:
        local_callbacks (generator[pathlib.Path]): The local callback modules.
        directory (str): The name of the directory where the files containing the local
            callbacks are stored.
    """
    for module in local_callbacks:
        filename = module.stem
        full_module = ''.join(['mqtt_remote.', directory, '.', filename])
        importlib.import_module(full_module)


def auto_import_local_callback_modules():
    """Automatically imports local callback modules
    """
    full_path_of_local_callbacks = Path(LOCAL_CALLBACK_DIR_FULL_PATH)
    callbacks = local_callback_modules(full_path_of_local_callbacks)

    import_local_callback_modules(callbacks, LOCAL_CALLBACKS_DIR_NAME)
