from unittest.mock import patch, Mock

import mqtt_remote.remote as remote
import mqtt_remote.config as config



class TestRemote:

    @patch('mqtt_remote.remote.Path')
    def test_installation_path(self, mock_path):
        mock_path.return_value.parent = '\\installation_path'

        install_path = remote.installation_path()

        assert install_path == '\\installation_path'


    @patch('mqtt_remote.remote.logging')
    def test_configure_logging(self, mock_logging, completed_config):
        output_file_name = completed_config['logging']['output_file']['name']
        output_file_maxsize = completed_config['logging']['output_file']['max_size']
        output_file_backups = completed_config['logging']['output_file']['max_backups']
        logging_level = completed_config['logging']['pylevel']
        logging_format = completed_config['logging']['log_format']

        remote.configure_logging(completed_config)

        mock_logging.handlers.RotatingFileHandler.assert_called_with(
            output_file_name,
            maxBytes=output_file_maxsize,
            backupCount=output_file_backups)
        mock_logging.StreamHandler.assert_called_with()

        logging_handlers = [mock_logging.handlers.RotatingFileHandler.return_value,
                            mock_logging.StreamHandler.return_value]
        mock_logging.basicConfig.assert_called_with(level=logging_level, format=logging_format,
                                                    handlers=logging_handlers)


    @patch('mqtt_remote.callbacks_local.auto_import_local_callback_modules')
    @patch('mqtt_remote.callbacks_plugins.auto_import_plugins')
    def test_load_all_callbacks(self, mock_load_plugins, mock_import_callbacks):

        remote.load_all_callbacks()

        mock_load_plugins.assert_called_with()
        mock_import_callbacks.assert_called_with()


    def test_setup_callback_caller(self):
        callback_caller = Mock()
        publish_function = Mock()
        completed_config = Mock()

        output = remote.setup_callback_caller(callback_caller, publish_function, completed_config)

        assert output.mqtt_publish == publish_function
        assert output.config == completed_config
        output.auto_add_command_message_callbacks.assert_called_once_with()
        assert output == callback_caller


    def test_setup_message_forwarder(self):
        message_forwarder = Mock()
        callback_caller = Mock()
        message_convertor = Mock()

        output = remote.setup_message_forwarder(message_forwarder, callback_caller,
                                                message_convertor)

        assert output.message_convertor == message_convertor
        assert output.callback == callback_caller.callback_caller


    @patch('mqtt_remote.mqtt_client.MQTTClient')
    def test_create_mqtt_software_client(self, mock_mqtt_client, completed_config):
        mock_mqtt_client.return_value = 'client'
        subscription_config = completed_config['subscriptions']
        subscription_topic = subscription_config['this_mqtt_client']['name']
        subscription_qos = subscription_config['this_mqtt_client']['qos']

        client = remote.create_mqtt_software_client(completed_config)

        mock_mqtt_client.assert_called_with(completed_config['mqtt_broker']['user_name'],
                                            completed_config['mqtt_broker']['password'],
                                            completed_config['mqtt_broker']['ip'],
                                            completed_config['mqtt_broker']['port'],
                                            completed_config['mqtt_broker']['keepalive'],
                                            [(subscription_topic, subscription_qos)],
                                            subscription_topic,
                                            completed_config['mqtt_session']['clean'],
                                            completed_config['mqtt_session']['pyprotocol'],
                                            completed_config['mqtt_session']['transport'],
                                            completed_config['logging']['log_base_client'])
        assert client == 'client'


    @patch('mqtt_remote.remote.setup_message_forwarder')
    @patch('mqtt_remote.remote.setup_callback_caller')
    @patch('mqtt_remote.message.ConvertedCommandMessageForwarder')
    @patch('mqtt_remote.message.PahoToCommandMessageConvertor')
    @patch('mqtt_remote.message.CommandMessageCallbackCaller')
    def test_setup_mqtt_software_client(self, mock_command_message_callback_caller,
                                        mock_paho_to_command_message_convertor,
                                        mock_converted_command_message_forwarder,
                                        mock_setup_callback_caller,
                                        mock_setup_message_forwarder):
        mqtt_software_client = Mock()
        completed_config = Mock()

        output = remote.setup_mqtt_software_client(mqtt_software_client, completed_config)

        mock_command_message_callback_caller.assert_called_with()
        mock_paho_to_command_message_convertor.assert_called_with()
        mock_converted_command_message_forwarder.assert_called_with(
            mock_paho_to_command_message_convertor.return_value,
            mock_command_message_callback_caller.return_value)

        mock_setup_callback_caller.assert_called_with(
            mock_command_message_callback_caller.return_value,
            mqtt_software_client.publish,
            completed_config)

        mock_setup_message_forwarder.assert_called_with(
            mock_converted_command_message_forwarder.return_value,
            mock_setup_callback_caller.return_value,
            mock_paho_to_command_message_convertor.return_value)

        mqtt_software_client.on_message_callbacks.add.assert_called_with(
            mock_setup_message_forwarder.return_value.forward)

        mqtt_software_client.initialise.assert_called_with()
        assert output == mqtt_software_client


    @patch('mqtt_remote.remote.setup_mqtt_software_client')
    @patch('mqtt_remote.remote.create_mqtt_software_client')
    def test_create_configured_mqtt_software_client(self, mock_create_mqtt_software_client,
                                                    mock_setup_mqtt_software_client):
        completed_config = Mock()

        output = remote.create_configured_mqtt_software_client(completed_config)

        mock_create_mqtt_software_client.assert_called_with(completed_config)
        mock_setup_mqtt_software_client.assert_called_with(
            mock_create_mqtt_software_client.return_value,
            completed_config)

        assert output == mock_setup_mqtt_software_client.return_value


    @patch('mqtt_remote.remote.start')
    @patch('mqtt_remote.remote.create_configured_mqtt_software_client')
    @patch('mqtt_remote.remote.load_all_callbacks')
    @patch('mqtt_remote.remote.configure_logging')
    @patch('mqtt_remote.config.completed_config_from_file')
    def test_auto_start(self, mock_completed_config_from_file,
                        mock_configure_logging,
                        mock_load_all_callbacks,
                        mock_create_configured_mqtt_software_client,
                        mock_start):

        remote.auto_start()

        mock_completed_config_from_file.assert_called_with(config.YAML_CONFIG_FILE)
        mock_configure_logging.assert_called_with(mock_completed_config_from_file.return_value)
        mock_load_all_callbacks.assert_called_with()
        mock_create_configured_mqtt_software_client.assert_called_with(
            mock_completed_config_from_file.return_value)

        mock_start.assert_called_with(mock_create_configured_mqtt_software_client.return_value)


    def test_start_no_keyboard_interrupt(self):
        mqtt_software_client = Mock()

        remote.start(mqtt_software_client)

        mqtt_software_client.start.assert_called_with(remote.MQTT_CLIENT_LOOP_TYPE)


    @patch('mqtt_remote.remote.logger')
    def test_controlled_shutdown(self, mock_logger):
        mqtt_software_client = Mock()

        remote.controlled_shutdown(mqtt_software_client)

        mock_logger.info.assert_called_with('KeyboardInterrupt detected: stopping MQTT Client...')
        mqtt_software_client.stop.assert_called_with()
