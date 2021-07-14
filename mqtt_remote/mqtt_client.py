"""MQTT Client

Examples:

    To create a CallbackSet:

        .. code-block:: python

            callback_set = CallbackSet()


    To add a callback to a CallbackSet:

        .. code-block:: python

            def example_cb(message):
                print(message)

            callback_set.add(example_cb)


    To remove a callback from a CallbackSet:

        .. code-block:: python

            callback_set.remove(example_cb)


    To create an MQTT client:

        .. code-block:: python

            mqtt_software_client = mqtt_client.MQTTClient('user_name',
                                                          'password',
                                                          '192.168.1.123',
                                                          1883,
                                                          60,
                                                          [("MyPC", 0)],
                                                          "MyPC",
                                                          True,
                                                          "3.1.1": mqtt.MQTTv311,
                                                          "tcp",
                                                          True)

    To initialise an MQTT client:

        .. code-block:: python

            mqtt_software_client.initialise()


    To start an MQTT client:

        .. code-block:: python

            mqtt_software_client.start('blocking')


    To stop an MQTT client:

        .. code-block:: python

            mqtt_software_client.stop()


    To use the MQTT client to publish an MQTT message:

        .. code-block:: python

            mqtt_software_client.publish("my topic", "hello world", 0, False)

"""
import logging

import paho.mqtt.client as mqtt



# pylint: disable=C0103
logger = logging.getLogger(__name__)
# pylint: enable=C0103



class CallbackSet:
    """Data structure to hold callbacks

    Extends the required methods of a set by adding additional logging and error checking
    capabilities
    """
    def __init__(self):
        self.__callbacks = set()

    def add(self, callback):
        """Adds a callback

        Args:
            callback (function, class): a callable object (e.g. function, method or class)

        Returns:
            set: callbacks
        """
        if callable(callback):
            self.__callbacks.add(callback)
            logger.debug(f"'{callback.__name__}' callback: Registered with CallbackSet")
            return self.__callbacks

        logger.warning('Could not add callback to CallbackSet: object was not callable')
        return self.__callbacks

    def remove(self, callback):
        """Removes a callback

        Args:
            callback (function, class): a callable object (e.g. function, method or class)

        Returns:
            set: callbacks
        """
        self.__callbacks.remove(callback)
        logger.debug(f"'{callback.__name__}' callback removed from CallbackSet", )
        return self.__callbacks

    def __iter__(self):
        return iter(self.__callbacks)

    def __bool__(self):
        if len(self.__callbacks) == 0:
            return False
        return True



class MQTTClient:
    """MQTT client

    Extends the paho client with additional logging, error handling and convenience feature

    Attributes:
        broker_user_name (str): The user name required to access the MQTT broker
        broker_password (str): The password required to access the MQTT broker
        broker_ip (str): The IP address of the MQTT broker
        broker_port (int): The port for the MQTT broker
        broker_keepalive (int): The maximum time, in seconds, that the client will remain
            quiet without sending an MQTT packet to the broker to confirm it is still connected
        subscription_topics (list[Tuple]): [(<topic>, <qos>), (...)]:
            topic: the MQTT topic to subscribe to,
            qos: the desired Quality Of Service for topic
        mqtt_client_id (str): An identifier for the MQTT client
        mqtt_clean_session (bool):
            True: the broker will remove all information about this client when it disconnects.
            False: the client will be a durable client (subscription information and queued
            messages will be retained when the client disconnects).
        mqtt_protocol (str): the version of the MQTT protocol to use for this client (as
            allowed by paho.mqtt.client)
        mqtt_transport (str): MQTT network transport:
            "websockets" to send MQTT over WebSockets.
            "tcp" to use raw TCP.
        log_client (bool): True: allow the log messages from the underlying paho client to
            pass through and be logged by this client, False: do not allow the log messages
            from the underlying paho client to pass through and be logged by this client
        on_message_callbacks (CallbackSet): The callbacks to be called when an MQTT message
            is received
        initialised (bool): Whether the client has been initialised, i.e. whether
            self.initialise has been run
    """
    def __init__(self, broker_user_name, broker_password,
                 broker_ip, broker_port, broker_keepalive,
                 subscription_topics, mqtt_client_id,
                 mqtt_clean_session, mqtt_protocol,
                 mqtt_transport, log_client):
        """Constructor

        Args:
            broker_user_name (str): The user name required to access the MQTT broker
            broker_password (str): The password required to access the MQTT broker
            broker_ip (str): The IP address of the MQTT broker
            broker_port (int): The port for the MQTT broker
            broker_keepalive (int): The maximum time, in seconds, that the client will remain
                quiet without sending an MQTT packet to the broker to confirm it is still connected
            subscription_topics (list[Tuple]): [(<topic>, <qos>), (...)]:
                topic: the MQTT topic to subscribe to,
                qos: the desired Quality Of Service for topic
            mqtt_client_id (str): An identifier for the MQTT client
            mqtt_clean_session (bool):
                True: the broker will remove all information about this client when it disconnects.
                False: the client will be a durable client (subscription information and queued
                messages will be retained when the client disconnects).
            mqtt_protocol (str): the version of the MQTT protocol to use for this client (as
                allowed by paho.mqtt.client)
            mqtt_transport (str): MQTT network transport:
                "websockets" to send MQTT over WebSockets.
                "tcp" to use raw TCP.
            log_client (bool): True: allow the log messages from the underlying paho client to
                pass through and be logged by this client, False: do not allow the log messages
                from the underlying paho client to pass through and be logged by this client
        """
        self.broker_user_name = broker_user_name
        self.broker_password = broker_password
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.broker_keepalive = broker_keepalive
        self.subscription_topics = subscription_topics
        self.mqtt_client_id = mqtt_client_id
        self.mqtt_clean_session = mqtt_clean_session
        self.mqtt_protocol = mqtt_protocol
        self.mqtt_transport = mqtt_transport
        self.log_client = log_client

        self.on_message_callbacks = CallbackSet()
        self.initialised = False

        self._mqtt_client = None

        self._subscription_mid = set()
        self._publish_mid = set()
        self._connected = False
        self._subscribed = False


    def initialise(self):
        """Gets the underlying MQTT client ready to start
        """
        self._mqtt_client = mqtt.Client(client_id=self.mqtt_client_id,
                                        clean_session=self.mqtt_clean_session,
                                        protocol=self.mqtt_protocol,
                                        transport=self.mqtt_transport)

        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_log = self._on_log
        self._mqtt_client.on_message = self._on_message
        self._mqtt_client.on_publish = self._on_publish
        self._mqtt_client.on_subscribe = self._on_subscribe

        self._mqtt_client.username_pw_set(self.broker_user_name, password=self.broker_password)

        self.initialised = True


    def start(self, loop_type):
        """Starts the client

        Args:
            loop_type (str): determines in which mode the client is run:
                'blocking' or
                'non_blocking'

        Raises:
            RuntimeError: if the client has not been initialised prior to using this method
            ValueError: if an unacceptable loop_type is provided
        """
        if not self.initialised:
            raise RuntimeError('MQTTClient has not been initialised')

        try:
            self._mqtt_client.connect(host=self.broker_ip, port=self.broker_port,
                                      keepalive=self.broker_keepalive)
        except ConnectionRefusedError as error:
            logger.warning(error)

        if loop_type == 'blocking':
            self._mqtt_client.loop_forever()
        elif loop_type == 'non_blocking':
            self._mqtt_client.loop_start()
        else:
            error = ''.join(['MQTTClient.start() \'loop_type\' argument ',
                             'can only be \'blocking\' or \'non_blocking\''])
            raise ValueError(error)

        logger.info("MQTTClient has started")


    def stop(self):
        """Stops the client
        """
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()
        logger.info("MQTTClient has stopped")


    def _process_publish_results(self, result, mid):
        """Processes the results that come from publishing a message

        Args:
            result (int): Paho result code
            mid (int): Paho message id
        """
        self._publish_mid.add(mid)

        if result == 0:
            logger.debug("".join(["Preperations for sending message and ",
                                  f"connecting to MQTT Broker succeeded (mid: {mid})"]))

        else:
            logger.warning("".join(["Message publishing: preperation error or ",
                                    "problem connecting to MQTT Broker: "
                                    f"{mqtt.error_string(result)} (mid: {mid})"]))


    def publish(self, topic, message, qos, retain):
        """Requests that the client sends an MQTT message to the broker for publishing

        Args:
            topic (str): The topic of the MQTT message to publish
            message (str): The MQTT payload to publish
            qos (int): The required Quality Of Service for the MQTT message
            retain (bool): True: the message will be set as the "last known good" / retained
                message for the topic. False: the message will not be set as the
                "last known good" / retained message for the topic.

        Raises:
            RuntimeError: if the client has not been initialised prior to using this method
        """
        if not self.initialised:
            raise RuntimeError('MQTTClient has not been initialised')

        (result, mid) = self._mqtt_client.publish(topic, payload=message, qos=qos,
                                                   retain=retain)

        self._process_publish_results(result, mid)


    def _process_paho_subscribe_results(self, result, mid):
        """Processes the results that come from the paho client upon subscribing

        Args:
            result (int): Paho result code
            mid (int): Paho message id
        """
        subscriptions = [sub[0] for sub in self.subscription_topics]

        if result == 0:
            logger_message = ''.join([f"Subscribe request for {subscriptions} successfully",
                                      f" submitted to MQTT Broker (mid: {mid})"])
            logger.info(logger_message)
            self._subscription_mid.add(mid)
        else:
            logger.warning("".join(["Problem submitting the subscribe request to the ",
                                    f"MQTT Broker: {mqtt.error_string(result)} (mid: {mid})"]))


    def _process_paho_connection_result(self, connection_result):
        """Processes the connection result (rc) that comes from the paho client upon connecting

        Args:
            connection_result (int): Paho connection result (rc)
        """
        if connection_result == 0:
            logger.info("Connection accepted by MQTT Broker")
            self._connected = True
        elif 1 <= connection_result <= 5:
            logger.warning(f"{mqtt.connack_string(connection_result)}")
        else:
            logger.warning(f"{mqtt.connack_string(connection_result)}{connection_result}")


    #pylint: disable=unused-argument, invalid-name
    def _on_connect(self, client, userdata, flags, rc):
        """Manages activities that occur as a result of the client connecting to the broker

        This connection callback is required by the underlying paho client
        """
        self._process_paho_connection_result(rc)

        # placed here to ensure resubscription occurs on reconnection if connection is lost
        (result, mid) = client.subscribe(self.subscription_topics)

        self._process_paho_subscribe_results(result, mid)
    #pylint: enable=unused-argument, invalid-name


    #pylint: disable=unused-argument, invalid-name
    def _on_disconnect(self, client, userdata, rc):
        """Manages activities that occur as a result of the client disconnecting from the broker

        This disconnection callback is required by the underlying paho client
        """
        self._connected = False
        self._subscribed = False

        if rc != 0:
            logger.warning("Unexpected loss of connection to MQTT Broker")
    #pylint: enable=unused-argument, invalid-name


    #pylint: disable=unused-argument
    def _on_log(self, mqttc, obj, level, string):
        """Manages activities that occur as a result of the underlying client creating a log

        This callback is required by the underlying paho client
        """
        if self.log_client:
            logger.debug(f'PAHO: {string}')
    #pylint: enable=unused-argument


    #pylint: disable=unused-argument
    def _on_message(self, client, userdata, msg):
        """Manages activities that occur as a result of the underlying client receiving a message

        This callback is required by the underlying paho client
        """
        if self.on_message_callbacks:
            for callback in self.on_message_callbacks:
                callback(msg)
        else:
            warning = "MQTT message received but no 'on_message_callbacks' are set for MQTTClient"
            logger.warning(warning)
    #pylint: enable=unused-argument


   #pylint: disable=unused-argument
    def _on_publish(self, client, userdata, mid):
        """Manages activities that occur as a result of the underlying client publishing a message

        This callback is required by the underlying paho client
        """
        if mid in self._publish_mid:
            logger.debug(f"Message successfully sent to the MQTT Broker (mid: {mid})")
            self._publish_mid.remove(mid)
        else:
            logger.warning(f"Problem sending the message to the MQTT Broker (mid: {mid})")
    #pylint: enable=unused-argument


   #pylint: disable=unused-argument
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Manages activities that occur as a result of the underlying client requesting
        subscriptions from the broker

        This callback is required by the underlying paho client
        """
        subscriptions = [sub[0] for sub in self.subscription_topics]

        if mid in self._subscription_mid:
            info = ''.join([f"Subscribe request for {subscriptions} ",
                            f"successfully processed by MQTT Broker (mid: {mid})"])
            logger.info(info)
            self._subscription_mid.remove(mid)
            self._subscribed = True
        else:
            warning = ''.join([f"MQTT Broker reports subscribe request for {subscriptions}",
                               f" was unsuccessful (mid: {mid})"])
            logger.warning(warning)
    #pylint: enable=unused-argument
