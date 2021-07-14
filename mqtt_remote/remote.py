"""Application entry point

Examples:

    To get the installation path of the app:

        .. code-block:: python

            installed_path = installation_path()


    To configure logging:

        .. code-block:: python

            configure_logging(completed_config)


    To load all local callbacks and plugin callbacks:

        .. code-block:: python

                load_all_callbacks()


    To setup the callback caller:

        .. code-block:: python

            callback_caller = setup_callback_caller(callback_caller,
                                                    publish_function,
                                                    completed_config)


    To setup the message forwarder:

        .. code-block:: python

            message_forwarder = setup_message_forwarder(message_forwarder,
                                                        callback_caller,
                                                        message_convertor)


    To create an unconfigured MQTT client:

        .. code-block:: python

            mqtt_software_client = create_mqtt_software_client(completed_config)


    To setup the MQTT client:

        .. code-block:: python

            mqtt_software_client = setup_mqtt_software_client(mqtt_software_client,
                                                              completed_config)


    To create a configured MQTT client:

        .. code-block:: python

            mqtt_software_client = create_configured_mqtt_software_client(completed_config)


    To stop the MQTT client in a controlled manner:

        .. code-block:: python

            controlled_shutdown(mqtt_software_client)


    To start the application manually:

        .. code-block:: python

            start(mqtt_software_client)


    To start the application automatically:

        .. code-block:: python

            auto_start()


Attributes:
    MQTT_CLIENT_LOOP_TYPE (str): The desired mode for running the MQTT client, i.e. 'blocking'
        or 'non_blocking'
"""
import logging
from pathlib import Path

from mqtt_remote import (callbacks_local,
                         callbacks_plugins,
                         config,
                         message,
                         mqtt_client)



# pylint: disable=C0103
logger = logging.getLogger(__name__)
# pylint: enable=C0103



MQTT_CLIENT_LOOP_TYPE = 'blocking'



def installation_path():
    """Returns the path where MQTT Remote was installed

    Returns:
        str: The path where MQTT Remote was installed
    """
    return str(Path(__file__).parent)


def configure_logging(completed_config):
    """Configures logging for the app

    Args:
        completed_config (dict): A dictionary containing a completed MQTT Remote
        configuration
    """
    output_file_name = completed_config['logging']['output_file']['name']
    output_file_maxsize = completed_config['logging']['output_file']['max_size']
    output_file_backups = completed_config['logging']['output_file']['max_backups']
    logging_level = completed_config['logging']['pylevel']
    logging_format = completed_config['logging']['log_format']

    rotating_file_handler = logging.handlers.RotatingFileHandler(
        output_file_name, maxBytes=output_file_maxsize,
        backupCount=output_file_backups)

    stream_handler = logging.StreamHandler()

    logging_handlers = [rotating_file_handler, stream_handler]

    logging.basicConfig(level=logging_level, format=logging_format,
                        handlers=logging_handlers)


def load_all_callbacks():
    """Loads all available local and plugin based callbacks
    """
    callbacks_plugins.auto_import_plugins()
    callbacks_local.auto_import_local_callback_modules()


def setup_callback_caller(callback_caller, publish_function, completed_config):
    """Sets up the callback caller

    Args:
        callback_caller (CommandMessageCallbackCaller): Callback caller to set up
        publish_function (Callable): A callable object to publish MQTT messages
        completed_config (dict): Completed MQTT Remote configuration

    Returns:
        CommandMessageCallbackCaller: Set up callback caller
    """
    callback_caller.mqtt_publish = publish_function
    callback_caller.config = completed_config
    callback_caller.auto_add_command_message_callbacks()
    return callback_caller


def setup_message_forwarder(message_forwarder, callback_caller, message_convertor):
    """Sets up the message forwarder

    Args:
        message_forwarder (ConvertedCommandMessageForwarder): Message forwarder to set up
        callback_caller (CommandMessageCallbackCaller): Callback caller
        message_convertor (CommandMessageConvertor): Message convertor

    Returns:
        ConvertedCommandMessageForwarder: Set up message forwarder
    """
    message_forwarder.message_convertor = message_convertor
    message_forwarder.callback = callback_caller.callback_caller

    return message_forwarder


def create_mqtt_software_client(completed_config):
    """Creates an MQTT software client

    Args:
        completed_config (dict): A dictionary containing a completed MQTT Remote configuration

    Returns:
        MQTT Client (mqtt_client.MQTTClient): MQTT software client
    """
    subscription_config = completed_config['subscriptions']
    subscription_topic = subscription_config['this_mqtt_client']['name']
    subscription_qos = subscription_config['this_mqtt_client']['qos']

    mqtt_software_client = mqtt_client.MQTTClient(completed_config['mqtt_broker']['user_name'],
                                                completed_config['mqtt_broker']['password'],
                                                completed_config['mqtt_broker']['ip'],
                                                completed_config['mqtt_broker']['port'],
                                                completed_config['mqtt_broker']['keepalive'],
                                                [(subscription_topic, subscription_qos)],
                                                subscription_topic,
                                                completed_config['mqtt_session']['clean'],
                                                completed_config['mqtt_session']['pyprotocol'],
                                                completed_config['mqtt_session']['transport'],
                                                completed_config['logging']['log_base_client']) \

    return mqtt_software_client


def setup_mqtt_software_client(mqtt_software_client, completed_config):
    """Sets up the MQTT software client

    Args:
        mqtt_software_client (mqtt_client.MQTTClient): The MQTT software client to set up
        completed_config (dict): A dictionary containing a completed MQTT Remote configuration

    Returns:
        MQTT Client (mqtt_client.MQTTClient): The MQTT software client
    """
    callback_caller = message.CommandMessageCallbackCaller()
    message_convertor = message.PahoToCommandMessageConvertor()
    message_forwarder = message.ConvertedCommandMessageForwarder(message_convertor, callback_caller)

    callback_caller = setup_callback_caller(callback_caller,
                                            mqtt_software_client.publish,
                                            completed_config)
    message_forwarder = setup_message_forwarder(message_forwarder, callback_caller,
                                                message_convertor)

    mqtt_software_client.on_message_callbacks.add(message_forwarder.forward)
    mqtt_software_client.initialise()

    return mqtt_software_client


def create_configured_mqtt_software_client(completed_config):
    """Returns a configured MQTT software client

    Args:
        completed_config (dict): A dictionary containing a completed MQTT Remote configuration

    Returns:
        MQTT Client (mqtt_client.MQTTClient): A configured MQTT software client
    """
    mqtt_software_client = create_mqtt_software_client(completed_config)
    mqtt_software_client = setup_mqtt_software_client(mqtt_software_client,
                                                      completed_config)
    return mqtt_software_client


def controlled_shutdown(mqtt_software_client):
    """Attempts to shutdown the app in a controlled way

    Args:
        MQTT Client (mqtt_client.MQTTClient): The running MQTT software client
    """
    logger.info('KeyboardInterrupt detected: stopping MQTT Client...')
    mqtt_software_client.stop()


def start(mqtt_software_client):
    """Starts the app

    Args:
        MQTT Client (mqtt_client.MQTTClient): A configured MQTT software client
    """
    try:
        mqtt_software_client.start(MQTT_CLIENT_LOOP_TYPE)
    except KeyboardInterrupt: #pragma: no cover
        controlled_shutdown(mqtt_software_client)


def auto_start():
    """Automatically starts the app

    This is the entry point for the app
    """
    completed_config = config.completed_config_from_file(config.YAML_CONFIG_FILE)

    configure_logging(completed_config)
    load_all_callbacks()

    mqtt_software_client = create_configured_mqtt_software_client(completed_config)
    start(mqtt_software_client)



if __name__ == '__main__':
    auto_start() #pragma: no cover
