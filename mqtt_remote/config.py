""" Configuration related functionality

Example:
    To load a YAML file:

    .. code-block:: python

        file_contents = load_yaml(yaml_file)

    To obtain a completed configuration from the configuration file:

    .. code-block:: python

        initial_config = load_yaml(YAML_CONFIG_FILE)
        config_completer = ConfigCompleter(initial_config)
        completed_config = config_completer.complete()

    To obtain a completed configuration from a raw configuration:

    .. code-block:: python

        raw_config = load_yaml(YAML_CONFIG_FILE)
        completed_config = completed_config_from_raw_config(raw_config)

    To obtain a completed configuration from the configuration file:

    .. code-block:: python

        completed_config = completed_config_from_file(YAML_CONFIG_FILE)


Attributes:
    YAML_CONFIG_FILE (str): Path of the mqtt_remote .yaml configuration file
    LOGGING_LEVELS (dict): For each 'Key: Value' pair in the dict:
        Key (str): string representation of a logging level,
        Value (logging attribute): the python logging attribute associated with the key.
    MQTT_PROTOCOLS (dict): For each 'Key: Value' pair in the dict:
        Key (str): string representation of an mqtt protocol,
        Value (mqtt attribute): mqtt attribute associated with the key.
"""
from copy import deepcopy
import logging
import logging.handlers
from pathlib import Path

import yaml

import paho.mqtt.client as mqtt



YAML_CONFIG_FILE = str(Path(__file__).parent / 'config.yaml')

LOGGING_LEVELS = {'DEBUG': logging.DEBUG,
                  'INFO': logging.INFO,
                  'WARNING': logging.WARNING,
                  'ERROR': logging.ERROR,
                  'CRITICAL': logging.CRITICAL,}

MQTT_PROTOCOLS = {"3.1": mqtt.MQTTv31,
                  "3.1.1": mqtt.MQTTv311,
                  "5": mqtt.MQTTv5,}



def load_yaml(yaml_file):
    """Loads a specified yaml file and returns the contents as a dictionary.

    Args:
       yaml_file (str): YAML file path.

    Returns:
        dict: The structured YAML from 'yaml_file'.
    """
    with open(yaml_file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)



class ConfigCompleter:
    """Allows a raw MQTT Remote configuration to be converted into a completed configuration.

    Attributes:
        raw_cfg (dict): Raw MQTT Remote configuration, e.g. the dict imported from the
            configuration .yaml file.
        logging_levels (dict): For each 'Key: Value' pair in the dict:
            Key (str): string representation of a logging level,
            Value (logging attribute): the python logging attribute associated with the key.
            Defaults to 'LOGGING_LEVELS'.
        mqtt_protocols (dict): For each 'Key: Value' pair in the dict:
            Key (str): string representation of an mqtt protocol,
            Value (mqtt attribute): mqtt protocol attribute associated with the key.
            Defaults to MQTT_PROTOCOLS.
        completed_cfg (dict): Completed MQTT Remote configuration.
    """
    def __init__(self, raw_config, logging_levels=None, mqtt_protocols=None):
        """Constructor

        Args:
            raw_config (dict): Raw MQTT Remote configuration, e.g. the dict imported from the
                configuration .yaml file.
            logging_levels (dict, optional): For each 'Key: Value' pair in the dict:
                Key (str): string representation of a logging level,
                Value (logging attribute): the python logging attribute associated with the key.
                Defaults to None.
            mqtt_protocols (dict, optional): For each 'Key: Value' pair in the dict:
                Key (str): string representation of an mqtt protocol,
                Value (mqtt attribute): mqtt attribute associated with the key.
                Defaults to None.
        """
        self.raw_cfg = raw_config

        if logging_levels is None:
            self.logging_levels = LOGGING_LEVELS
        else:
            self.logging_levels = logging_levels

        if mqtt_protocols is None:
            self.mqtt_protocols = MQTT_PROTOCOLS
        else:
            self.mqtt_protocols = mqtt_protocols

        self.completed_cfg = None


    def _logging_level_convertor(self, config):
        """Adds a logging level object to the supplied configuration
        """
        try:
            config['logging']['pylevel'] = self.logging_levels[config['logging']['level']]
        except KeyError:
            error_message = ''.join(["The yaml 'logging > level' parameter can only have the",
                                     f" following values: {list(self.logging_levels.keys())}"])
            print(error_message)
            raise

        return config


    def _mqtt_protocol_convertor(self, config):
        """Adds an mqtt protocol object to the supplied configuration
        """
        try:
            config_file_protocol = config['mqtt_session']['protocol']
            config['mqtt_session']['pyprotocol'] = self.mqtt_protocols[config_file_protocol]
        except KeyError:
            protocol_list = list(self.mqtt_protocols.keys())
            error_message = ''.join(["The yaml 'mqtt_session > protocol' parameter can only",
                                    f" have the following values: {protocol_list}"])
            print(error_message)
            raise

        return config


    def _process_broker_password(self, config):
        """Allows the user to enter an MQTT broker password at the command line at run time.

        This is for cases where the user doesn't want to store their password in plain text in the
        configuration file

        The following settings are required to be entered in the .yaml configuration file in order
        for a password to be requested at the command line:
            mqtt_broker:
              ...
              password_required: True
              password: ''
              ...
        """
        password_required = config['mqtt_broker']['password_required']
        password = config['mqtt_broker']['password']

        if password_required and not password:
            input_message = 'Please enter your MQTT broker password and press enter: '
            config['mqtt_broker']['password'] = input(input_message)

        return config


    def complete(self):
        """Returns a completed configuration

        Returns:
            dict: Completed configuration
        """
        wip_config = deepcopy(self.raw_cfg)

        wip_config = self._logging_level_convertor(wip_config)
        wip_config = self._mqtt_protocol_convertor(wip_config)
        wip_config = self._process_broker_password(wip_config)

        self.completed_cfg = wip_config

        return self.completed_cfg


def completed_config_from_raw_config(raw_config):
    """Returns a completed config from a raw config

    Args:
        raw_config (dict): Raw MQTT Remote configuration, e.g. the dict imported from the
            configuration .yaml file.

    Returns:
        dict: A completed MQTT Remote configuration
    """
    config_completer = ConfigCompleter(raw_config)
    completed_config = config_completer.complete()
    return completed_config


def completed_config_from_file(config_file):
    """Returns a completed config from a config file

    Args:
        config_file (str): YAML config file path.

    Returns:
        dict: A completed MQTT Remote configuration
    """
    initial_config = load_yaml(config_file)
    completed_config = completed_config_from_raw_config(initial_config)

    return completed_config
