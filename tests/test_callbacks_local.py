
from unittest.mock import patch, Mock, call

import mqtt_remote.callbacks_local as callbacks_local



class TestCallbacksLocal:
    def test_local_callback_modules(self):
        callback_modules = ['one.py', 'two.py', 'three.py']
        mock_path = Mock()
        mock_path.glob.return_value = callback_modules

        returned_callback_modules = callbacks_local.local_callback_modules(mock_path)

        for module in callback_modules:
            assert module in returned_callback_modules


    def test_import_local_callback_modules(self):
        mock_module_one = Mock()
        mock_module_two = Mock()
        mock_module_three = Mock()

        mock_module_one.stem = 'one'
        mock_module_two.stem = 'two'
        mock_module_three.stem = 'three'

        callback_modules = [mock_module_one, mock_module_two, mock_module_three]
        callback_modules = (module for module in callback_modules)

        callback_directory = callbacks_local.LOCAL_CALLBACKS_DIR_NAME

        with patch('mqtt_remote.callbacks_local.importlib.import_module') as mock_import:
            callbacks_local.import_local_callback_modules(callback_modules, callback_directory)

        for module in callback_modules:
            full_module = ''.join(['mqtt_remote.', callback_directory,
                                   '.', module.stem])
            assert call(full_module) in mock_import.call_args_list


    @patch('mqtt_remote.callbacks_local.Path')
    @patch('mqtt_remote.callbacks_local.local_callback_modules')
    @patch('mqtt_remote.callbacks_local.import_local_callback_modules')
    def test_load_callbacks(self, mock_load_local_callback_modules,
                            mock_local_callback_modules,
                            mock_path):
        callback_modules = ['one.py', 'two.py', 'three.py']
        mock_path.return_value = callbacks_local.LOCAL_CALLBACK_DIR_FULL_PATH
        mock_local_callback_modules.return_value = callback_modules

        callbacks_local.auto_import_local_callback_modules()

        mock_local_callback_modules.assert_called_with(callbacks_local.LOCAL_CALLBACK_DIR_FULL_PATH)
        mock_load_local_callback_modules.assert_called_with(callback_modules,
                                                            callbacks_local.LOCAL_CALLBACKS_DIR_NAME)