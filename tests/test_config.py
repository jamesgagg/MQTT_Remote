from unittest.mock import patch, mock_open
import logging

import pytest
import paho.mqtt.client as mqtt

from mqtt_remote import config



class TestYamlLoader:
    def test_load_yaml_valid_file(self):
        file_data = ''.join(['logging:', '  level: "DEBUG"'])
        file_data_as_dict = {'logging': {'level': 'DEBUG'}}

        with patch('builtins.open', mock_open(read_data=file_data)) as mock_open_file:
            with patch('mqtt_remote.config.yaml.load', side_effect=[file_data_as_dict]):
                yaml = config.load_yaml('config.yaml')

        mock_open_file.assert_called_with('config.yaml')
        assert yaml == file_data_as_dict



class TestConfigCompleter:
    def test_complete_no_logging_levels_no_mqtt_protocols(self, initial_config):
        config_completer = config.ConfigCompleter(initial_config)

        assert config_completer.logging_levels == config.LOGGING_LEVELS
        assert config_completer.mqtt_protocols == config.MQTT_PROTOCOLS


    def test_complete_no_errors(self, initial_config, completed_config):
        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_invalid_logging_level(self, initial_config, completed_config, capsys):
        initial_config['logging']['level'] = 'abcdefg'

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)

        with pytest.raises(KeyError):
            config_completer.complete()

        error_message = ''.join(["The yaml 'logging > level' parameter can only have the",
                                 f" following values: {list(config.LOGGING_LEVELS.keys())}\n"])
        assert error_message == capsys.readouterr().out


    def test_complete_info_logging_level(self, initial_config, completed_config):
        initial_config['logging']['level'] = 'INFO'
        completed_config['logging']['level'] = 'INFO'
        completed_config['logging']['pylevel'] = logging.INFO

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_warning_logging_level(self, initial_config, completed_config):
        initial_config['logging']['level'] = 'WARNING'
        completed_config['logging']['level'] = 'WARNING'
        completed_config['logging']['pylevel'] = logging.WARNING

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_error_logging_level(self, initial_config, completed_config):
        initial_config['logging']['level'] = 'ERROR'
        completed_config['logging']['level'] = 'ERROR'
        completed_config['logging']['pylevel'] = logging.ERROR

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_critical_logging_level(self, initial_config, completed_config):
        initial_config['logging']['level'] = 'CRITICAL'
        completed_config['logging']['level'] = 'CRITICAL'
        completed_config['logging']['pylevel'] = logging.CRITICAL

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_invalid_protocol(self, initial_config, completed_config, capsys):
        initial_config['mqtt_session']['protocol'] = 'abcdefg'

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)

        with pytest.raises(KeyError):
            config_completer.complete()

        error_message = ''.join(["The yaml 'mqtt_session > protocol' parameter can only have",
                                 " the following values: ",
                                 f"{list(config.MQTT_PROTOCOLS.keys())}\n"])
        assert error_message == capsys.readouterr().out


    def test_complete_protocol_convertor_three_one(self, initial_config, completed_config):
        initial_config['mqtt_session']['protocol'] = '3.1'
        completed_config['mqtt_session']['protocol'] = '3.1'
        completed_config['mqtt_session']['pyprotocol'] = mqtt.MQTTv31

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_protocol_convertor_three_one_one(self, initial_config, completed_config):
        initial_config['mqtt_session']['protocol'] = '3.1.1'
        completed_config['mqtt_session']['protocol'] = '3.1.1'
        completed_config['mqtt_session']['pyprotocol'] = mqtt.MQTTv311

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_protocol_convertor_five(self, initial_config, completed_config):
        initial_config['mqtt_session']['protocol'] = '5'
        completed_config['mqtt_session']['protocol'] = '5'
        completed_config['mqtt_session']['pyprotocol'] = mqtt.MQTTv5

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config


    def test_complete_password_required_none_supplied(self, initial_config, completed_config):
        initial_config['mqtt_broker']['password'] = ''
        password = 'password'

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)

        with patch('builtins.input', lambda *args: password):
            finished_config = config_completer.complete()

        assert finished_config['mqtt_broker']['password'] == password


    def test_complete_password_not_required_not_supplied(self, initial_config, completed_config):
        initial_config['mqtt_broker']['password'] = ''
        initial_config['mqtt_broker']['password_required'] = False
        completed_config['mqtt_broker']['password'] = ''
        completed_config['mqtt_broker']['password_required'] = False

        config_completer = config.ConfigCompleter(initial_config, config.LOGGING_LEVELS,
                                                  config.MQTT_PROTOCOLS)
        finished_config = config_completer.complete()

        assert finished_config == completed_config



class TestCompletedConfigs:
    @patch('mqtt_remote.config.ConfigCompleter')
    def test_completed_config_from_initial_config(self, mock_config_completer, initial_config,
                                                  completed_config):
        mock_config_completer.return_value.complete.return_value = completed_config

        output = config.completed_config_from_raw_config(initial_config)

        mock_config_completer.assert_called_with(initial_config)
        assert output == completed_config


    @patch('mqtt_remote.config.completed_config_from_raw_config')
    @patch('mqtt_remote.config.load_yaml')
    def test_completed_config_from_file(self, mock_load_yaml,
                                        mock_completed_config_from_raw_config,
                                        completed_config):
        config_file_path = r'C:\a_config_file_path\a_config_file.yaml'
        mock_completed_config_from_raw_config.return_value = completed_config

        output = config.completed_config_from_file(config_file_path)

        assert output == completed_config
