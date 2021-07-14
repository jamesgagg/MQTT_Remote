from unittest.mock import patch, mock_open, Mock

import mqtt_remote.callback_creation as callback_creation
import mqtt_remote.callbacks_local as callbacks_local


class TestCallbackCreation:
    def test_import_file_as_string(self):
        file_data = 'example text'
        file_name = 'file.txt'

        with patch('builtins.open', mock_open(read_data=file_data)) as mock_open_file:
            file_as_string = callback_creation.import_file_as_string(file_name)

        mock_open_file.assert_called_with(file_name, 'rt')
        assert file_as_string == file_data


    @patch('mqtt_remote.callback_creation.pyperclip')
    def test_copy_string_to_clipboard(self, mock_pyperclip):
        text_to_copy = 'example text'

        callback_creation.copy_string_to_clipboard(text_to_copy)

        mock_pyperclip.copy.assert_called_with(text_to_copy)


    def test_copy_template_to_clipboard_with_arguments(self):
        file_data = 'example text'
        file_name = 'file.txt'
        import_file_as_string_function = Mock()
        string_to_clipboard_function = Mock()

        import_file_as_string_function.return_value = file_data

        callback_creation.copy_template_to_clipboard(file_name, import_file_as_string_function,
                                                     string_to_clipboard_function)

        string_to_clipboard_function.assert_called_with(file_data)
        import_file_as_string_function.assert_called_with(file_name)


    @patch('mqtt_remote.callback_creation.copy_string_to_clipboard')
    @patch('mqtt_remote.callback_creation.import_file_as_string')
    def test_copy_template_to_clipboard_no_arguments(self, mock_import_file_as_string,
                                                     mock_copy_string_to_clipboard):
        mock_import_file_as_string.return_value = 'file contents'

        callback_creation.copy_template_to_clipboard()

        mock_import_file_as_string.assert_called_with(callback_creation.TEMPLATE_FILE)
        mock_copy_string_to_clipboard.assert_called_with('file contents')


    def test_create_callback_file_with_arguments(self):
        file_data = 'example text'
        file_name = 'file.py'
        callback = Mock()

        with patch('builtins.open', mock_open(read_data=file_data)) as mock_open_file:
            callback_creation.create_callback_file(file_name, callback)

        mock_open_file.assert_called_with(file_name, 'wt')
        mock_open_file.return_value.write.assert_called_with(callback)


    @patch('mqtt_remote.callback_creation.import_file_as_string')
    def test_create_callback_file_no_arguments(self, mock_import_file_as_string):
        file_data = 'example text'
        file_name = 'file.py'
        full_path =  ''.join([callbacks_local.LOCAL_CALLBACK_DIR_FULL_PATH, '\\', file_name])
        mock_import_file_as_string.return_value = 'callback'

        with patch('builtins.input', lambda x: file_name):
            with patch('builtins.open', mock_open(read_data=file_data)) as mock_open_file:
                callback_creation.create_callback_file()

        mock_open_file.assert_called_with(full_path, 'wt')
        mock_open_file.return_value.write.assert_called_with('callback')
