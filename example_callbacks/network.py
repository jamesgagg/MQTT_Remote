import requests

from mqtt_remote.message import CommandMessageCallback



class PublicIP(CommandMessageCallback):
    """Sends an MQTT message containing the public (external) IP address of your internet
    connected router

    Requires an inbound message MQTT payload of the form:

        {"command": "public_ip",
         "attributes": {"return_message": {"topic": <str>,
                                           "qos": <int>,
                                           "retain": <bool>}}}
    """
    def __init__(self):
        """Constructor
        """
        self._message_name = 'public_ip'
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
            inbound_message (CommandMessage): The CommandMessage with a 'payload['command']' value that
                matches with self._message_name
        """
        public_ip = requests.get('https://api.ipify.org').text

        topic = inbound_message.payload['attributes']['return_message']['topic']
        payload = f'Public IP: {public_ip}'
        qos = inbound_message.payload['attributes']['return_message']['qos']
        retain = inbound_message.payload['attributes']['return_message']['retain']

        self.mqtt_publish(topic, payload, qos, retain)



