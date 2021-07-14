from mqtt_remote.message import CommandMessageCallback



class SumPositiveInts(CommandMessageCallback):
    """Sends an MQTT message containing the sum of the two positive integers received in the
    inbound message

    Requires an inbound message MQTT payload of the form:

        {"command": "sum_positive_ints",
         "attributes": {"integer_one": <int>,
                        "integer_two": <int>,
                        "return_message": {"topic": <str>,
                                           "qos": <int>,
                                           "retain": <bool>}}}
    """
    def __init__(self):
        """Constructor
        """
        # self.disabled = True # optional
        self._message_name = 'sum_positive_ints' # required
        # self.config = None # optional
        self.mqtt_publish = None # optional

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
        integer_one = int(inbound_message.payload['attributes']['integer_one'])
        integer_two = int(inbound_message.payload['attributes']['integer_two'])
        outbound_topic = inbound_message.payload['attributes']['return_message']['topic']
        outbound_qos = inbound_message.payload['attributes']['return_message']['qos']
        outbound_retain = inbound_message.payload['attributes']['return_message']['retain']

        sum = integer_one + integer_two
        outbound_payload = str(sum)

        self.mqtt_publish(outbound_topic, outbound_payload, outbound_qos, outbound_retain)