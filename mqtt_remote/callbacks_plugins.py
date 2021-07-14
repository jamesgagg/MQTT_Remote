"""Plugin related functionality

Examples:

    To return all top level modules in the current namespace:

        .. code-block:: python

            all_top_level_module_names = names_of_all_top_level_modules()


    To return the names of all modules that have the plugin prefix:

        .. code-block:: python

            all_top_level_module_names = names_of_all_top_level_modules()
            plugins = top_level_module_plugins(all_top_level_module_names, PLUGIN_PACKAGE_PREFIX)


    To get a list of plugin module names in the format required for importlib.import_module()

        .. code-block:: python

            all_top_level_module_names = names_of_all_top_level_modules()
            plugins = top_level_module_plugins(all_top_level_module_names, PLUGIN_PACKAGE_PREFIX)
            formatted_plugin_names = format_plugin_names_for_import(plugins)


    To manually import the plugin modules:

        .. code-block:: python

            all_top_level_module_names = names_of_all_top_level_modules()
            plugins = top_level_module_plugins(all_top_level_module_names, PLUGIN_PACKAGE_PREFIX)
            formatted_plugin_names = format_plugin_names_for_import(plugins)
            import_plugin_modules(formatted_plugin_names)


    To automatically import the plugin modules:

        .. code-block:: python

            auto_import_plugins()


Attributes:
    PLUGIN_PACKAGE_PREFIX (str): The prefix that denotes that a package is an MQTT remote plugin.
"""
import importlib
import pkgutil



PLUGIN_PACKAGE_PREFIX = 'mqtt_remote_'



def names_of_all_top_level_modules():
    """Returns all top level modules in the current namespace

    Returns:
        list: All top level modules in the current namespace
    """
    return [module.name for module in pkgutil.iter_modules()]


def top_level_module_plugins(all_top_level_module_names, plugin_prefix):
    """Returns the names of all top level modules matching with a plugin prefix

    Args:
        all_top_level_module_names (list[str]): A list of all top level module names.
        plugin_prefix (str): module plugin prefix

    Returns:
        list[str]: A list of all top level modules matching with a plugin prefix
    """
    top_level_plugin_modules = [name
                                for name
                                in all_top_level_module_names
                                if name.startswith(plugin_prefix)]

    return top_level_plugin_modules


def format_plugin_names_for_import(plugin_module_names):
    """Formats plugin module names in the format required for importlib.import_module()

    Args:
        plugin_module_names (list[str]): Top level modules with a plugin prefix

    Returns:
        list[str]: Plugins in the correct format for importing with importlib.import_module()
    """
    formatted_plugin_names = []

    for plugin_module_name in plugin_module_names:
        plugin_entry_point = plugin_module_name.split(PLUGIN_PACKAGE_PREFIX, 1)[1]
        full_plugin_name = f'{plugin_module_name}.{plugin_entry_point}'

        formatted_plugin_names.append(full_plugin_name)

    return formatted_plugin_names


def import_plugin_modules(full_plugin_names):
    """Imports plugin modules

    Args:
        full_plugin_names (list[str]): Correctly formatted top level modules with a plugin prefix
    """
    for full_plugin_name in full_plugin_names:
        importlib.import_module(full_plugin_name)


def auto_import_plugins():
    """Automatically imports plugin modules
    """
    top_level_modules = names_of_all_top_level_modules()
    plugins = top_level_module_plugins(top_level_modules, PLUGIN_PACKAGE_PREFIX)
    full_names_of_plugins = format_plugin_names_for_import(plugins)
    import_plugin_modules(full_names_of_plugins)
