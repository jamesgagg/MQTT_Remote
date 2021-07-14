from unittest.mock import Mock

from pytest import fixture



@fixture(scope='function')
def command_msg():
    cmd_msg = Mock()
    cmd_msg.topic = 'topic'
    cmd_msg.payload = None
    cmd_msg.qos = 0
    cmd_msg.retain = False

    return cmd_msg


@fixture(scope='function')
def audio_file():
    return 'audio_file.mp3'


@fixture(scope='function')
def audio_dir():
    return 'C:\\audio_dir\\'


@fixture(scope='function')
def volume_percent():
    return 50


@fixture(scope='function')
def volume_scaler(volume_percent):
    return volume_percent / 100


@fixture(scope='function')
def mock_sound_interface(volume_scaler):
    sound_interface = Mock()

    sink_one = Mock()
    sink_one.name = 'sink_one'
    sink_one.volume.values = [volume_scaler, volume_scaler]

    sink_two = Mock()
    sink_two.name = 'sink_two'
    sink_two.volume.values = [volume_scaler, volume_scaler]

    sound_interface.sink_list.return_value = [sink_one, sink_two]

    return sound_interface


@fixture(scope='function')
def platform_os():
    return 'Windows'
