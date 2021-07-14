from unittest.mock import patch, Mock, call

import mqtt_remote.callbacks_plugins as callbacks_plugins

from collections import namedtuple



class TestPlugins:
    def test_names_of_all_top_level_modules(self):
        mock_module_info = namedtuple('ModuleInfo', ['module_finder', 'name', 'ispkg'])
        info_module_one = mock_module_info(module_finder=None, name="module_one", ispkg=None)
        info_module_two = mock_module_info(module_finder=None, name="module_two", ispkg=None)

        with patch('mqtt_remote.callbacks_plugins.pkgutil.iter_modules',
                   return_value=[info_module_one, info_module_two]):
            names = callbacks_plugins.names_of_all_top_level_modules()

        assert names == ['module_one', 'module_two']


    def test_top_level_module_plugins(self):
        prefix = 'prefix_'

        all_top_level_module_names = ['module_one', 'prefix_module_two']

        valid_plugins = callbacks_plugins.top_level_module_plugins(all_top_level_module_names,
                                                                   prefix)

        assert 'prefix_module_two' in valid_plugins


    def test_format_plugin_names_for_import(self):
        plugin_module_names = ['mqtt_remote_entry_one',
                               'mqtt_remote_entry_two']

        full_names = callbacks_plugins.format_plugin_names_for_import(plugin_module_names)

        assert full_names == ['mqtt_remote_entry_one.entry_one',
                              'mqtt_remote_entry_two.entry_two']


    def test_import_plugin_modules(self):
        full_plugin_module_names = ['mqtt_remote_entry_one.entry_one',
                                    'mqtt_remote_entry_two.entry_two']

        with patch('mqtt_remote.callbacks_plugins.importlib.import_module') as mock_import:
            callbacks_plugins.import_plugin_modules(full_plugin_module_names)

        assert call('mqtt_remote_entry_one.entry_one') in mock_import.call_args_list
        assert call('mqtt_remote_entry_two.entry_two') in mock_import.call_args_list


    @patch('mqtt_remote.callbacks_plugins.import_plugin_modules')
    @patch('mqtt_remote.callbacks_plugins.format_plugin_names_for_import')
    @patch('mqtt_remote.callbacks_plugins.top_level_module_plugins')
    @patch('mqtt_remote.callbacks_plugins.names_of_all_top_level_modules')
    def test_auto_import_plugins(self, mock_names_of_all_top_level_modules,
                                 mock_plugin_module_names,
                                 mock_full_plugin_names,
                                 mock_import_plugin_modules):
        top_level = ['module_one', 'module_two', 'plugin_module_two']
        plugin_names = ['plugin_module_two']
        full_names = ['mqtt_remote_entry_two.plugin_module_two']
        mock_names_of_all_top_level_modules.return_value = top_level
        mock_plugin_module_names.return_value = plugin_names
        mock_full_plugin_names.return_value = full_names

        callbacks_plugins.auto_import_plugins()

        mock_names_of_all_top_level_modules.assert_called_with()
        mock_plugin_module_names.assert_called_with(top_level,
                                                    callbacks_plugins.PLUGIN_PACKAGE_PREFIX)
        mock_full_plugin_names.assert_called_with(plugin_names)
        mock_import_plugin_modules.assert_called_with(full_names)
