from unittest.mock import patch, Mock
from collections import namedtuple

import paho.mqtt.client as mqtt
from pytest import fixture

from mqtt_remote.mqtt_client import MQTTClient



@fixture(scope='function')
def example_function():
    ex_function = Mock()
    ex_function.__name__ = 'example_function'
    return ex_function


@fixture(scope='function')
def mqtt_config():
    config = {"broker_user_name": "username",
              "broker_password": "password",
              "broker_ip": "192.168.0.100",
              "broker_port": "1883",
              "broker_keepalive": 60,
              "subscription_topics": [("this_client", 0)],
              "mqtt_client_id": "this_client",
              "mqtt_clean_session": True,
              "mqtt_protocol": mqtt.MQTTv311,
              "mqtt_transport": 'tcp',
              "log_client": True}
    return config


@fixture(scope='function')
def mqtt_client(mqtt_config):
    with patch('paho.mqtt.client.Client'):
        client = MQTTClient(mqtt_config["broker_user_name"],
                            mqtt_config["broker_password"],
                            mqtt_config["broker_ip"],
                            mqtt_config["broker_port"],
                            mqtt_config["broker_keepalive"],
                            mqtt_config["subscription_topics"],
                            mqtt_config["mqtt_client_id"],
                            mqtt_config["mqtt_clean_session"],
                            mqtt_config["mqtt_protocol"],
                            mqtt_config["mqtt_transport"],
                            mqtt_config["log_client"])
        yield client


@fixture(scope='function',)
def initial_config():
    ini_config = {'logging': {'level': 'DEBUG',
                              'log_format': '%(asctime)s  %(name)s  %(levelname)s: %(message)s',
                              'output_file': {'name': 'mqtt_remote.log',
                                              'max_size': 5242880,
                                              'max_backups': 2},
                              'log_base_client': True},
                  'mqtt_session': {'protocol': '3.1.1',
                                  'transport': 'tcp',
                                  'clean': True},
                  'mqtt_broker': {'ip': '192.168.1.100',
                                  'port': 1883,
                                  'user_name': 'username',
                                  'password_required': True,
                                  'password': 'password',
                                  'keepalive': 60},
                  'subscriptions':{'this_mqtt_client': {'name': 'this_client',
                                                      'qos': 0}}}
    return ini_config


@fixture(scope='function')
def completed_config(initial_config):
    comp_config = initial_config
    comp_config['logging']['pylevel'] = 10
    comp_config['mqtt_session']['pyprotocol'] = 4
    return comp_config


@fixture(scope="module")
def pub_msg():
    publish_message = namedtuple('pub', ['topic', 'message', 'qos', 'retain'])
    message = publish_message('topic', 'message', 0, False)
    return message
