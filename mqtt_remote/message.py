"""Message related functionality

Examples:

    To create a command message:

        .. code-block:: python

            topic = 'a_topic'
            payload = {"command": "print_something", "attributes": {"thing_to_print": "Spam"}}
            qos = 0
            retain = False

            command_message = CommandMessage(topic, payload, qos, retain)


    To create a Paho to command message convertor:

        .. code-block:: python

            message_convertor = PahoToCommandMessageConvertor()


    To create a converted message forwarder:

        .. code-block:: python

            message_forwarder = ConvertedCommandMessageForwarder()


    To create a callback caller:

        .. code-block:: python

            callback_caller = CommandMessageCallbackCaller()


    To setup the message forwarder:

        .. code-block:: python

            message_convertor = PahoToCommandMessageConvertor()
            message_forwarder = ConvertedCommandMessageForwarder()
            callback_caller = CommandMessageCallbackCaller()

            message_forwarder.message_convertor = message_convertor
            message_forwarder.callback = callback_caller.callback_caller


    To setup the callback_caller:

        .. code-block:: python

            callback_caller.mqtt_publish = publish_function
            callback_caller.config = completed_config


    To automatically register CommandMessageCallback callbacks with the callback caller:

        .. code-block:: python

            callback_caller.auto_add_command_message_callbacks()


    To check if a payload message is valid:

        .. code-block:: python

            is_valid = valid_payload_value(message, keys, required_value_type)


    To log that a command message was of the wrong form:

        .. code-block:: python

            log_wrong_command_message_form(callback_name, required_message_form)
"""
from abc import ABC, abstractmethod
import json
import logging



# pylint: disable=C0103
logger = logging.getLogger(__name__)
# pylint: enable=C0103



class CommandMessage:
    """Standardised MQTT message format

    Attributes:
        topic (str): MQTT message topic
        qos (int): MQTT message Quality Of Service
        retain (bool): MQTT message retain flag
    """
    def __init__(self, topic, payload, qos, retain):
        """Constructor

        Args:
            topic (str): MQTT message topic
            payload (dict): MQTT message payload. Must be in the following format:
                {"command": "<command_name>", "attributes": {<attributes in key: value pairs>}}
            qos (int): MQTT message Quality Of Service
            retain (bool): MQTT message retain flag
        """
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain


    @property
    def payload(self):
        """dict: MQTT message payload.

        Setter:

            Raises:

                :TypeError: if 'payload' is not a dictionary
                :ValueError: if the 'command' and/or 'attributes' keys are not found in the
                    dictionary
                :TypeError: if the value for the 'command' key in 'payload' is not a string
                :TypeError: if the value for the 'attributes' key in 'payload' is not a dict
        """
        return self._payload


    @payload.setter
    def payload(self, payload):

        if not isinstance(payload, dict):
            raise TypeError

        if not all([attr in payload for attr in ('command', 'attributes')]):
            raise ValueError

        if not isinstance(payload['command'], str):
            raise TypeError

        if not isinstance(payload['attributes'], dict):
            raise TypeError

        self._payload = payload


    @payload.deleter
    def payload(self):
        self._payload = {}
        return self._payload


class CommandMessageConvertor(ABC):
    """Abstract base class for convertors that convert messages to the CommandMessage format
    """
    def __init__(self):
        """Constructor
        """


    @abstractmethod
    def convert(self, message):
        """Abstract method for converting a message into a CommandMessage

        Args:
            message (Any): message to be converted
        """


class PahoToCommandMessageConvertor(CommandMessageConvertor):
    """Provides the functionality to convert a Paho message to a CommandMessage
    """
    def _bytes_to_string(self, character_input):
        """Converts bytes to a string if the input is bytes
        """
        if isinstance(character_input, bytes):
            return character_input.decode("utf-8")
        return character_input


    def _standardise_double_quotes(self, input_string):
        """Converts non-standard double quotes to standard double quotes
        """
        translation_table = ''.maketrans('“”', '""')
        output = input_string.translate(translation_table)
        return output


    def convert(self, message):
        """Converts a paho message into a CommandMessage

        Args:
            message (paho.mqtt.client.MQTTMessage): Paho message

        Returns:
            CommandMessage: A CommandMessage object
        """
        payload = self._bytes_to_string(message.payload)
        payload = self._standardise_double_quotes(payload)
        payload = json.loads(payload)

        try:
            command_message = CommandMessage(message.topic, payload,
                                             message.qos, message.retain)
            command = payload['command']
            logger.debug(f'Paho \'{command}\' message successfully converted to CommandMessage')

        except (TypeError, ValueError):
            logger.warning(''.join(['Unable to convert Paho message to CommandMessage: ',
                                    'Paho payload must be of the following form:\n',
                                    '{"command": "<command>", "attributes": {<attributes in key:',
                                    ' value pairs>}}']))
            command_message = None

        return command_message


class ConvertedCommandMessageForwarder:
    """Provides functionality to call a callback with a CommandMessage converted from a raw message
    """
    def __init__(self, message_convertor, callback):
        """Constructor

        Args:
            message_convertor (CommandMessageConvertor, optional): A message convertor.
            callback (function, class): a callable object (e.g. function, method or class).
        """
        self.message_convertor = message_convertor
        self.callback = callback


    def _command_message(self, raw_message):
        return self.message_convertor.convert(raw_message)


    def forward(self, raw_message, command_message=None):
        """Calls 'self.callback' with a 'CommandMessage' converted from 'raw_message'

        Args:
            raw_message (Any): The raw message from an MQTT client. Must be compatible with
                the specific convertor referenced by 'self.message_convertor'.
        """
        if command_message is None:
            command_message = self._command_message(raw_message)

        self.callback(command_message)


class CommandMessageCallback(ABC):
    """Abstract base class for command message callback objects
    """
    @abstractmethod
    def __init__(self):
        """Abstract method Constructor
        """


    @property
    @abstractmethod
    def message_name(self):
        """Abstract method for a 'message_name' property getter
        """


    @abstractmethod
    def execute(self, inbound_message):
        """Abstract method for the callback

        Callbacks added by 'CommandMessageCallbackCaller.auto_add_command_message_callbacks()' will
        call this method of the callback object
        """


class CommandMessageCallbackCaller:
    """Associates callbacks with CommandMessages and calls a callback if a matching CommandMessage
    is received
    """
    def __init__(self):
        """Constructor
        """
        self._callbacks = {}
        self.mqtt_publish = None
        self.config = None


    def add_callback(self, command_name, callback):
        """Adds a 'command_name': 'callback' key:value pair to the registered callbacks

        Args:
            command_name (str): Name of the command. This must match exactly with a
                'CommandMessage.payload['command']' to result in the 'callback' associated with
                this argument being called.
            callback (function, class): a callable object (e.g. function, method or class)

        Returns:
            dict: All of the currently registered callbacks
        """
        self._callbacks[command_name] = callback
        logger.debug(f'\'{command_name}\' callback: Registered with CommandMessageCallbackCaller')
        return self._callbacks


    def remove_callback(self, command_name):
        """Removes a callback key:value pair from the registered callbacks

        Args:
            command_name (str): Key corresponding to the callback to be removed.

        Returns:
            dict: All of the currently registered callbacks
        """
        del self._callbacks[command_name]
        debug = f"'{command_name}' callback: Unregistered from CommandMessageCallbackCaller"
        logger.debug(debug)
        return self._callbacks


    def get_callbacks(self):
        """Returns a dictionary containing all of the registered callbacks

        Returns:
            dict: All of the currently registered callbacks
        """
        return self._callbacks


    def auto_add_command_message_callbacks(self):
        """Automatically adds callbacks that inherit from CommandMessageCallback to the registered
        callbacks

        The callback classes that inherit from CommandMessageCallback must be present in the
        namespace in order for them to be automatically found, instantiated and added
        """
        for sub_class in CommandMessageCallback.__subclasses__():
            instance = sub_class()
            instance = self._setup_command_message_callback_instance(instance)

            if hasattr(instance, 'disabled') and instance.disabled:
                logger.debug(''.join([f'\'{instance.message_name}\' callback: ',
                                      'Not registered (disabled with \'self.disabled = True\')']))
                continue

            self.add_callback(instance.message_name, instance.execute)


    def _setup_command_message_callback_instance(self, instance):
        """Sets up an instance of a class that inherits from CommandMessageCallback
        """
        if hasattr(instance, 'mqtt_publish'):
            instance.mqtt_publish = self.mqtt_publish

        if hasattr(instance, 'config'):
            instance.config = self.config

        return instance


    def callback_caller(self, command_message):
        """Calls a registered callback if 'CommandMessage.payload['command']' matches with a
        key in the registered callbacks

        Args:
            command_message (CommandMessage): CommandMessage
        """
        if command_message:
            command_name = command_message.payload['command']
            try:
                self._callbacks[command_name](command_message)
            except KeyError:
                logger.warning(f'No callback registered for: \'{command_name}\'')
            else:
                logger.debug(f'Called callback for {command_name}')
        else:
            logger.warning('Unable to call any callback: Command Message is \'None\'')


def valid_payload_value(message, keys, required_value_type):
    """Checks if a value for a particular payload key within a command message is valid

    :Checks two things:
        1.) whether the key is present

        2.) whether the value associated with the key is of the expected type

    Args:
        message (CommandMessage): CommandMessage to check
        keys (list): A list of keys ordered from root to leaf where the leaf is the key, value
            pair to check e.g. 'keys' for message.payload['attributes']['lounge']['temperature']
            would be: ['attributes', 'lounge', 'temperature']
        required_value_type (type): The expected type of the value corresponding to the key being
            checked

    Returns:
        bool:
            True: if the 'key: value' pair is valid,
            False: if the 'key: value' pair is invalid
    """
    valid = True
    try:
        output = message.payload[keys[0]]
        for i in range(1, len(keys)):
            output = output[keys[i]]

    except KeyError:
        valid = False

    if valid:
        if not isinstance(output, required_value_type):
            valid = False

    return valid


def log_wrong_command_message_form(callback_name, required_message_form):
    """Issues a logger message reporting that a CommandMessage payload is not of the form
    required by a callback

    Args:
        callback_name (str): Name of callback
        required_message_form (str): Required message form
    """
    error_message = ''.join([f'A CommandMessage for the callback: \'{callback_name}\'',
                             f'must be of the form:\n{required_message_form}'])
    logger.error(error_message)
