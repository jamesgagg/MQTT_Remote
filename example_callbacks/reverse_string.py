from mqtt_remote.message import CommandMessageCallback



class ReverseString(CommandMessageCallback):
    """Sends an MQTT message containing the reverse of a supplied string.

    Requires an inbound message MQTT payload of the form:

        {"command": "reverse_string",
        "attributes": {"string_to_reverse": <str>,
                       "return_message": {"topic": <str>,
                                          "qos": <int>,
                                          "retain": <bool>}}}

    """
    def __init__(self):
        """Constructor
        """
        self._message_name = 'reverse_string'
        self.mqtt_publish = None

    @property
    def message_name(self):
        """Getter

        Returns:
            str: The message name
        """
        return self._message_name

    def execute(self, inbound_message):
        """The code to be executed when a matching MQTT message is received

        Execution occurs when a CommandMessage containing a 'payload['command']' value that
        matches with self._message_name is received by CommandMessageCallbackCaller

        Args:
            inbound_message (CommandMessage): The CommandMessage with a 'payload['command']'
                value that matches with self._message_name
        """
        string_to_reverse = inbound_message.payload['attributes']['string_to_reverse']
        reversed_string = string_to_reverse[::-1]

        outbound_topic = inbound_message.payload['attributes']['return_message']['topic']
        outbound_payload = reversed_string
        outbound_qos = inbound_message.payload['attributes']['return_message']['qos']
        outbound_retain = inbound_message.payload['attributes']['return_message']['retain']

        self.mqtt_publish(outbound_topic, outbound_payload, outbound_qos, outbound_retain)
