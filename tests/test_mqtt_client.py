from unittest.mock import Mock, patch, NonCallableMock

import paho.mqtt.client as mqtt
import pytest

from mqtt_remote.mqtt_client import CallbackSet



class TestCallbackSet:
    def callback(self, suffix):
        callback = Mock()
        callback.__name__ = f'callback_{suffix}'
        return callback


    @patch('mqtt_remote.mqtt_client.logger')
    def test_add_valid_callback(self, mock_logger):
        callback_set = CallbackSet()

        callback_one = self.callback('one')

        return_values = callback_set.add(callback_one)

        assert callback_one in callback_set
        expected_string = f"'{callback_one.__name__}' callback: Registered with CallbackSet"
        mock_logger.debug.assert_called_with(expected_string)

        assert isinstance(return_values, set)
        assert callback_one in return_values


    @patch('mqtt_remote.mqtt_client.logger')
    def test_add_invalid_callback(self, mock_logger):
        callback_set = CallbackSet()

        callback_one = NonCallableMock()
        callback_one.__name__ = 'callback_one'

        return_values = callback_set.add(callback_one)

        assert callback_one not in callback_set
        expected_string = 'Could not add callback to CallbackSet: object was not callable'
        mock_logger.warning.assert_called_with(expected_string)

        assert isinstance(return_values, set)
        assert callback_one not in return_values


    @patch('mqtt_remote.mqtt_client.logger')
    def test_add_multiple_valid_callbacks(self, mock_logger):
        callback_set = CallbackSet()

        callback_one = self.callback('one')
        callback_two = self.callback('two')

        callback_set.add(callback_one)
        return_values = callback_set.add(callback_two)

        expected_string_one = f"'{callback_one.__name__}' callback: Registered with CallbackSet"
        mock_logger.debug.assert_any_call(expected_string_one)

        expected_string_two = f"'{callback_two.__name__}' callback: Registered with CallbackSet"
        mock_logger.debug.assert_any_call(expected_string_two)

        assert callback_one in callback_set
        assert callback_two in callback_set

        assert isinstance(return_values, set)
        assert callback_one in return_values
        assert callback_two in return_values


    @patch('mqtt_remote.mqtt_client.logger')
    def test_remove_callback(self, mock_logger):
        callback_set = CallbackSet()

        callback_one = self.callback('one')

        callback_set.add(callback_one)

        return_values = callback_set.remove(callback_one)
        expected_string = f"'{callback_one.__name__}' callback removed from CallbackSet"
        mock_logger.debug.assert_called_with(expected_string)

        assert callback_one not in callback_set
        assert isinstance(return_values, set)
        assert callback_one not in return_values



class TestMQTTClient:
    def test_initialise(self, mqtt_client):
        mqtt_client.initialise()

        assert mqtt_client.initialised


    def test_start_no_initialisation(self, mqtt_client):
        with pytest.raises(RuntimeError) as excinfo:
            mqtt_client.start('blocking')

        assert 'MQTTClient has not been initialised' in str(excinfo.value)


    @patch('mqtt_remote.mqtt_client.logger')
    def test_start_blocking(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        mqtt_client.start('blocking')

        mock_logger.info.assert_called_with("MQTTClient has started")


    @patch('mqtt_remote.mqtt_client.logger')
    def test_start_non_blocking(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        mqtt_client.start('non_blocking')

        mock_logger.info.assert_called_with("MQTTClient has started")


    @patch('mqtt_remote.mqtt_client.logger')
    def test_start_blocking_connectionrefusederror(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        error = ConnectionRefusedError('TestError')
        mqtt_client._mqtt_client.connect.side_effect = error

        mqtt_client.start('blocking')

        mock_logger.warning.assert_called_with(error)


    def test_start_invalid_loop_type(self, mqtt_client):
        mqtt_client.initialise()

        with pytest.raises(ValueError) as excinfo:
            mqtt_client.start('invalid method')

        error_message = ''.join(['MQTTClient.start() \'loop_type\' argument can only be ',
                                 '\'blocking\' or \'non_blocking\''])

        assert error_message in str(excinfo.value)


    @patch('mqtt_remote.mqtt_client.logger')
    def test_stop(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        mqtt_client.stop()

        mock_logger.info.assert_called_with("MQTTClient has stopped")


    def test_publish_no_initialisation(self, mqtt_client, pub_msg):
        with pytest.raises(RuntimeError) as excinfo:
            mqtt_client.publish(pub_msg.topic, pub_msg.message, pub_msg.qos, pub_msg.retain)

        assert 'MQTTClient has not been initialised' in str(excinfo.value)


    @patch('mqtt_remote.mqtt_client.logger')
    def test_publish_result_zero(self, mock_logger, mqtt_client, pub_msg):
        mqtt_client.initialise()

        result = 0
        mid = 1

        mqtt_client._mqtt_client.publish.return_value = (result, mid)

        mqtt_client.publish(pub_msg.topic, pub_msg.message, pub_msg.qos, pub_msg.retain)

        log_message = ("".join(["Preperations for sending message and ",
                                f"connecting to MQTT Broker succeeded (mid: {mid})"]))

        mock_logger.debug.assert_called_with(log_message)


    @patch('mqtt_remote.mqtt_client.logger')
    def test_publish_result_one(self, mock_logger, mqtt_client, pub_msg):
        mqtt_client.initialise()

        result = 1
        mid = 1

        mqtt_client._mqtt_client.publish.return_value = (result, mid)

        mqtt_client.publish(pub_msg.topic, pub_msg.message, pub_msg.qos, pub_msg.retain)

        log_message = ("".join(["Message publishing: preperation error or ",
                                "problem connecting to MQTT Broker: "
                                f"{mqtt.error_string(result)} (mid: {mid})"]))

        mock_logger.warning.assert_called_with(log_message)


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_connect_rc_zero_result_zero(self, mock_logger, mqtt_client, mqtt_config):
        mqtt_client.initialise()

        rc = 0
        result = 0
        mid = 1

        mqtt_client._mqtt_client.subscribe.return_value = (result, mid)

        mqtt_client._on_connect(mqtt_client._mqtt_client, "", "", rc)

        mock_logger.info.assert_any_call("Connection accepted by MQTT Broker")

        subscriptions = [sub[0] for sub in mqtt_config["subscription_topics"]]
        mock_logger.info.assert_any_call("".join([f"Subscribe request for {subscriptions} ",
                                                  "successfully submitted to MQTT Broker",
                                                  f" (mid: {mid})"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_connect_rc_three_result_zero(self, mock_logger, mqtt_client, mqtt_config):
        mqtt_client.initialise()

        rc = 3
        result = 0
        mid = 1

        mqtt_client._mqtt_client.subscribe.return_value = (result, mid)

        mqtt_client._on_connect(mqtt_client._mqtt_client, "", "", rc)

        mock_logger.warning.assert_any_call(f"{mqtt.connack_string(rc)}")

        subscriptions = [sub[0] for sub in mqtt_config["subscription_topics"]]
        mock_logger.info.assert_any_call(''.join([f"Subscribe request for {subscriptions} ",
                                                  "successfully submitted to MQTT Broker",
                                                  f" (mid: {mid})"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_connect_rc_six_result_zero(self, mock_logger, mqtt_client, mqtt_config):
        mqtt_client.initialise()

        rc = 6
        result = 0
        mid = 1

        mqtt_client._mqtt_client.subscribe.return_value = (result, mid)

        mqtt_client._on_connect(mqtt_client._mqtt_client, "", "", rc)

        mock_logger.warning.assert_any_call(f"{mqtt.connack_string(rc)}{rc}")

        subscriptions = [sub[0] for sub in mqtt_config["subscription_topics"]]
        mock_logger.info.assert_any_call(''.join([f"Subscribe request for {subscriptions} ",
                                                  "successfully submitted to MQTT Broker",
                                                  f" (mid: {mid})"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_connect_rc_zero_result_one(self, mock_logger, mqtt_client, mqtt_config):
        mqtt_client.initialise()

        rc = 0
        result = 1
        mid = 1

        mqtt_client._mqtt_client.subscribe.return_value = (result, mid)

        mqtt_client._on_connect(mqtt_client._mqtt_client, "", "", rc)

        mock_logger.info.assert_any_call("Connection accepted by MQTT Broker")

        mock_logger.warning.assert_any_call("".join(["Problem submitting the subscribe request",
                                                     " to the MQTT Broker: ",
                                                     f"{mqtt.error_string(result)} (mid: {mid})"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_disconnect_rc_one(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        rc = 1

        mqtt_client._on_disconnect(mqtt_client._mqtt_client, "", rc)

        mock_logger.warning.assert_called_with("Unexpected loss of connection to MQTT Broker")


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_log(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        log_string = 'this is a test message'

        mqtt_client._on_log(mqtt_client._mqtt_client, "", "logging.DEBUG", log_string)

        mock_logger.debug.assert_called_with(f"PAHO: {log_string}")


    def test__on_message_one_function(self, mqtt_client):
        mqtt_client.initialise()

        message = "message"

        object_one = Mock()
        object_one.callback.__name__ = 'callback_one'

        mqtt_client.on_message_callbacks.add(object_one.callback)

        mqtt_client._on_message(mqtt_client._mqtt_client, "", message)

        object_one.callback.assert_called_with(message)


    def test__on_message_two_functions(self, mqtt_client):
        mqtt_client.initialise()

        message = "message"

        object_one = Mock()
        object_two = Mock()

        object_one.callback.__name__ = 'callback_one'
        object_two.callback.__name__ = 'callback_two'

        mqtt_client.on_message_callbacks.add(object_one.callback)
        mqtt_client.on_message_callbacks.add(object_two.callback)

        mqtt_client._on_message(mqtt_client._mqtt_client, "", message)

        object_one.callback.assert_called_with(message)
        object_two.callback.assert_called_with(message)


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_message_no_functions(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        message = "message"

        mqtt_client._on_message(mqtt_client._mqtt_client, "", message)

        mock_logger.warning.assert_called_with(''.join(["MQTT message received but no ",
                                                        "'on_message_callbacks' are set",
                                                        " for MQTTClient"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_publish_mid_in__publish(self, mock_logger, mqtt_client):
        mqtt_client.initialise()

        mid = 0

        mqtt_client._publish_mid = {mid}

        mqtt_client._on_publish(mqtt_client._mqtt_client, "", mid)

        mock_logger.debug.assert_called_with(''.join(["Message successfully sent ",
                                                      f"to the MQTT Broker (mid: {mid})"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_publish_mid_not_in__publish(self, mock_logger, mqtt_client):
        mid_in_publish = 0
        mid_for_message = 1

        mqtt_client._publish_mid = {mid_in_publish}

        mqtt_client._on_publish(mqtt_client._mqtt_client, "", mid_for_message)

        mock_logger.warning.assert_called_with(''.join(["Problem sending the message to the",
                                                        f" MQTT Broker (mid: {mid_for_message})"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_subscribe_mid_in__subscription_mid(self, mock_logger, mqtt_client, mqtt_config):
        mid = 0

        mqtt_client._subscription_mid = {mid}

        mqtt_client._on_subscribe(mqtt_client._mqtt_client, "", mid, "")

        subscriptions = [sub[0] for sub in mqtt_config["subscription_topics"]]
        mock_logger.info.assert_called_with(''.join([f"Subscribe request for {subscriptions}",
                                                     " successfully processed by MQTT Broker",
                                                     f" (mid: {mid})"]))


    @patch('mqtt_remote.mqtt_client.logger')
    def test__on_subscribe_mid_not_in__subscription_mid(self, mock_logger, mqtt_client,
                                                        mqtt_config):
        mid = 1

        mqtt_client._subscription_mid = {0}

        mqtt_client._on_subscribe(mqtt_client._mqtt_client, "", mid, "")

        subscriptions = [sub[0] for sub in mqtt_config["subscription_topics"]]
        mock_logger.warning.assert_called_with(''.join(["MQTT Broker reports subscribe request",
                                                        f" for {subscriptions} was unsuccessful",
                                                        f" (mid: {mid})"]))
