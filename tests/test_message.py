from unittest.mock import Mock, patch

import pytest

import mqtt_remote.message as message



class CallbackOne(message.CommandMessageCallback):
    def __init__(self):
        self.__message_name = 'one'
        self.message = None
        self.mqtt_publish = None

    @property
    def message_name(self):
        return self.__message_name

    def execute(self, message):
        pass



class CallbackTwo(message.CommandMessageCallback):
    def __init__(self):
        self.__message_name = 'two'
        self.message = None
        self.config = None

    @property
    def message_name(self):
        return self.__message_name

    def execute(self, message):
        pass



class DisabledCallback(message.CommandMessageCallback):
    def __init__(self):
        self.__message_name = 'three'
        self.message = None
        self.disabled = True

    @property
    def message_name(self):
        return self.__message_name

    def execute(self, message):
        pass


class TestCommandMessage:
    def test_payload_getter(self):
        payload = {'command': 'command',
                   'attributes': {}}

        msg = message.CommandMessage('topic', payload, 0, False)

        assert msg.payload == payload


    def test_payload_setter_incorrect_string(self):
        payload = 'payload'

        with pytest.raises(TypeError):
            message.CommandMessage('topic', payload, 0, False)


    def test_payload_setter_missing_attributes(self):
        payload = {'command': 'command',
                   'attr': {}}

        with pytest.raises(ValueError):
            message.CommandMessage('topic', payload, 0, False)


    def test_payload_setter_incorrect_command_type(self):
        payload = {'command': {},
                   'attributes': {}}

        with pytest.raises(TypeError):
            message.CommandMessage('topic', payload, 0, False)


    def test_payload_setter_no_attributes_dict(self):
        payload = {'command': 'command',
                   'attributes': ''}

        with pytest.raises(TypeError):
            message.CommandMessage('topic', payload, 0, False)


    def test_payload_deleter(self):
        payload = {'command': 'command',
                   'attributes': {}}

        msg = message.CommandMessage('topic', payload, 0, False)

        del msg.payload

        assert msg.payload == {}



class TestPahoToCommandMessageConvertor:
    def paho_mqtt_msg(self, payload):
        paho_msg = Mock()
        paho_msg.topic = 'topic'
        paho_msg.payload = payload
        paho_msg.qos = 0
        paho_msg.retain = False

        return paho_msg


    def test_convert_good_payload(self):
        payload = b'{"command": "name", "attributes": {}}'
        paho_mqtt_msg = self.paho_mqtt_msg(payload)

        with patch('mqtt_remote.message.CommandMessage') as cmd_msg:
            convertor = message.PahoToCommandMessageConvertor()
            convertor.convert(paho_mqtt_msg)

        expected_output = {"command": "name", "attributes": {}}

        assert cmd_msg.call_args[0][1] == expected_output


    def test_convert_empty_payload(self):
        payload = b'{}'
        paho_mqtt_msg = self.paho_mqtt_msg(payload)

        convertor = message.PahoToCommandMessageConvertor()
        output = convertor.convert(paho_mqtt_msg)

        assert output is None


    def test_convert_non_standard_quotes(self):
        payload = bytes('{“command“: “name“, “attributes“: {}}', 'utf-8')
        paho_mqtt_msg = self.paho_mqtt_msg(payload)

        with patch('mqtt_remote.message.CommandMessage') as cmd_msg:
            convertor = message.PahoToCommandMessageConvertor()
            convertor.convert(paho_mqtt_msg)

        expected_output = {"command": "name", "attributes": {}}

        assert cmd_msg.call_args[0][1] == expected_output


    def test_convert_non_bytes_payload(self):
        payload = '{"command": "name", "attributes": {}}'
        paho_mqtt_msg = self.paho_mqtt_msg(payload)

        with patch('mqtt_remote.message.CommandMessage') as cmd_msg:
            convertor = message.PahoToCommandMessageConvertor()
            convertor.convert(paho_mqtt_msg)

        expected_output = {"command": "name", "attributes": {}}

        assert cmd_msg.call_args[0][1] == expected_output



class TestConvertedCommandMessageForwarder:
    def test_forward_with_command_message_argument(self):
        message_convertor = Mock()
        callback = Mock()
        raw_message = Mock()
        command_message = Mock()

        forwarder = message.ConvertedCommandMessageForwarder(message_convertor, callback)
        forwarder.forward(raw_message, command_message)

        callback.assert_called_with(command_message)


    def test_forward_no_command_message_argument(self):
        message_convertor = Mock()
        callback = Mock()
        raw_message = Mock()

        forwarder = message.ConvertedCommandMessageForwarder(message_convertor, callback)
        forwarder.forward(raw_message)

        forwarder.message_convertor.convert.assert_called_with(raw_message)



class TestCommandMessageCallbackCaller:
    def test_add_callback_with_function(self, example_function):
        msg_router = message.CommandMessageCallbackCaller()

        result = msg_router.add_callback('name', example_function)

        assert result['name'] == example_function
        assert msg_router._callbacks['name'] == example_function


    def test_remove_callback_with_function(self, example_function):
        msg_router = message.CommandMessageCallbackCaller()

        msg_router._callbacks['name'] = example_function

        result = msg_router.remove_callback('name')

        assert 'name' not in result
        assert 'name' not in msg_router._callbacks


    def test_callback_caller(self, example_function):
        msg_router = message.CommandMessageCallbackCaller()

        payload = {"command": "name", "attributes": {}}

        command_msg = Mock()
        command_msg.topic = 'topic'
        command_msg.payload = payload
        command_msg.qos = 0
        command_msg.retain = False

        msg_router.add_callback('name', example_function)

        msg_router.callback_caller(command_msg)

        assert example_function.call_args[0][0].topic == 'topic'
        assert example_function.call_args[0][0].payload == payload
        assert example_function.call_args[0][0].qos == 0
        assert not example_function.call_args[0][0].retain


    @patch('mqtt_remote.message.logger')
    def test_callback_caller_none(self, mock_logger):
        msg_router = message.CommandMessageCallbackCaller()

        command_msg = None

        msg_router.callback_caller(command_msg)

        expected_string = 'Unable to call any callback: Command Message is \'None\''
        mock_logger.warning.assert_called_with(expected_string)


    @patch('mqtt_remote.message.logger')
    def test_callback_caller_keyerror(self, mock_logger):
        msg_router = message.CommandMessageCallbackCaller()

        payload = {"command": "name", "attributes": {}}

        command_message = message.CommandMessage('topic', payload, 0, False)

        msg_router.callback_caller(command_message)

        mock_logger.warning.assert_called_with(f'No callback registered for: \'name\'')


    def test_auto_add_command_message_callbacks(self):
        msg_router = message.CommandMessageCallbackCaller()

        msg_router.auto_add_command_message_callbacks()

        assert msg_router._callbacks['one'].__name__ == 'execute'
        assert msg_router._callbacks['two'].__name__ == 'execute'


    def test_auto_add_command_message_callbacks_mqtt_publish(self):
        msg_router = message.CommandMessageCallbackCaller()
        msg_router.mqtt_publish = 'publish'

        msg_router.auto_add_command_message_callbacks()

        msg_router._callbacks['one'].__self__.mqtt_publish == 'publish'
        assert not hasattr(msg_router._callbacks['two'].__self__, 'mqtt_publish')


    def test_auto_add_command_message_callbacks_config(self):
        msg_router = message.CommandMessageCallbackCaller()
        msg_router.config = 'config'

        msg_router.auto_add_command_message_callbacks()

        msg_router._callbacks['two'].__self__.config == 'config'
        assert not hasattr(msg_router._callbacks['one'].__self__, 'config')


    @patch('mqtt_remote.message.logger')
    def test_auto_add_command_message_callbacks_disabled_callback(self, mock_logger):
        msg_router = message.CommandMessageCallbackCaller()

        msg_router.auto_add_command_message_callbacks()

        assert 'three' not in msg_router.get_callbacks()
        mock_logger.debug.assert_called_with(''.join(['\'three\' callback: Not registered ',
                                                      '(disabled with \'self.disabled = True\')']))


class TestValidPayloadValue:
    def test_key_is_present_correct_type(self):
        payload = {"command": "name", "attributes": {"lounge": {"temperature": 20}}}

        command_msg = Mock()
        command_msg.topic = 'topic'
        command_msg.payload = payload
        command_msg.qos = 0
        command_msg.retain = False

        keys = ['attributes', 'lounge', 'temperature']
        required_type = int

        result = message.valid_payload_value(command_msg, keys, required_type)

        assert result


    def test_key_is_present_incorrect_type(self):
        payload = {"command": "name", "attributes": {"lounge": {"temperature": 20}}}

        command_msg = Mock()
        command_msg.topic = 'topic'
        command_msg.payload = payload
        command_msg.qos = 0
        command_msg.retain = False

        keys = ['attributes', 'lounge', 'temperature']
        required_type = str

        result = message.valid_payload_value(command_msg, keys, required_type)

        assert not result


    def test_key_is_not_present(self):
        payload = {"command": "name", "attributes": {"lounge": {"temperature": 20}}}

        command_msg = Mock()
        command_msg.topic = 'topic'
        command_msg.payload = payload
        command_msg.qos = 0
        command_msg.retain = False

        keys = ['attributes', 'kitchen', 'temperature']
        required_type = str

        result = message.valid_payload_value(command_msg, keys, required_type)

        assert not result



class TestLogWrongCommandMessageForm:
    @patch('mqtt_remote.message.logger')
    def test_logger_called(self, mock_logger):
        callback_name = 'name of callback'
        required_message_form = 'form of required message'

        error_message = ''.join([f'A CommandMessage for the callback: \'{callback_name}\'',
                                 f'must be of the form:\n{required_message_form}'])

        message.log_wrong_command_message_form(callback_name, required_message_form)

        mock_logger.error.assert_called_with(error_message)
