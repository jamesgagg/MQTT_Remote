# Running these tests occasionally results in the following error:
# OSError: exception: access violation writing
#
# This seems to be related to an open issue with comtypes, as described in:
# https://github.com/enthought/comtypes/issues/204

from unittest.mock import patch, Mock, call
from pathlib import Path
import platform

import pytest

import mqtt_remote_audio.audio as audio



class TestVLCAudioFilePlayer:
    @patch('mqtt_remote_audio.audio.vlc')
    def test_constructor(self, mock_vlc):
        audio.VLCAudioFilePlayer()

        mock_vlc.Instance.assert_called_with()
        mock_vlc.Instance.return_value.media_player_new.assert_called_with()

    @patch('mqtt_remote_audio.audio.vlc')
    def test_play_file(self, mock_vlc, audio_file):
        vlc_player = audio.VLCAudioFilePlayer()
        vlc_player.play_file(audio_file)

        mock_vlc.Instance.return_value.media_new.assert_called_with(audio_file)

        media = mock_vlc.Instance.return_value.media_new(audio_file)
        mock_player = mock_vlc.Instance.return_value.media_player_new.return_value
        mock_player.set_media.assert_called_with(media)

        mock_player.play.assert_called_with()



class TestLocalAudioFilePlayer:
    def test_no_audio_file_player(self):
        mock_vlc_player = Mock()

        with patch('mqtt_remote_audio.audio.VLCAudioFilePlayer', return_value=mock_vlc_player):
            play_local_audio_file = audio.LocalAudioFilePlayer()

        assert play_local_audio_file.audio_file_player == mock_vlc_player


    def test_message_name(self):
        msg_name = 'play_local_audio_file'
        mock_player = Mock()

        play_local_audio_file = audio.LocalAudioFilePlayer(mock_player)

        assert play_local_audio_file.message_name == msg_name


    def test_required_message_form(self):
        msg_name = 'play_local_audio_file'
        required_message_form = ''.join([f'{{"command": "{msg_name}", ',
                                         '"attributes": {"audio_file": "<str>"}}'])
        mock_player = Mock()

        play_local_audio_file = audio.LocalAudioFilePlayer(mock_player)

        assert play_local_audio_file.required_message_form == required_message_form


    @patch('mqtt_remote_audio.audio.logger')
    def test_execute_good_command_message(self, mock_logger, audio_file, audio_dir, command_msg):
        mock_player = Mock()

        audio_path = str(Path(audio_dir).joinpath(audio_file).resolve())
        payload = {"command": "name", "attributes": {"audio_file": audio_file}}
        command_msg.payload = payload

        play_local_audio_file = audio.LocalAudioFilePlayer(mock_player, audio_dir)
        play_local_audio_file.execute(command_msg)

        play_local_audio_file.audio_file_player.play_file.assert_called_once_with(audio_path)
        mock_logger.info.assert_any_call(''.join(["Sent the following file to the audio ",
                                                  f"file player: '{audio_path}'"]))


    @patch('mqtt_remote.message.logger')
    def test_execute_command_message_wrong_attribute(self, mock_logger, audio_file, audio_dir,
                                                     command_msg):
        mock_player = Mock()

        payload = {"command": "name", "attributes": {"SOUND_file": audio_file}}
        command_msg.payload = payload

        play_local_audio_file = audio.LocalAudioFilePlayer(mock_player, audio_dir)
        play_local_audio_file.execute(command_msg)

        mock_logger.error.assert_any_call(''.join(['A CommandMessage for the callback: \'play_local_audio_file\'',
                                                   'must be of the form:\n{"command": ',
                                                   '"play_local_audio_file", "attributes": ',
                                                   '{"audio_file": "<str>"}}']))


    @patch('mqtt_remote.message.logger')
    def test_execute_command_message_wrong_type(self, mock_logger, audio_dir, command_msg):
        mock_player = Mock()

        audio_file = 12345
        payload = {"command": "name", "attributes": {"audio_file": audio_file}}
        command_msg.payload = payload

        play_local_audio_file = audio.LocalAudioFilePlayer(mock_player, audio_dir)
        play_local_audio_file.execute(command_msg)

        mock_logger.error.assert_any_call(''.join(['A CommandMessage for the callback: \'play_local_audio_file\'',
                                                   'must be of the form:\n{"command": ',
                                                   '"play_local_audio_file", "attributes": ',
                                                   '{"audio_file": "<str>"}}']))



class TestWindowsVolume:
    def test_set_vol(self, volume_percent, volume_scaler):
        volume_interface = Mock()

        windows_volume = audio.WindowsVolume(volume_interface)
        windows_volume.set_vol(volume_percent)

        master_vol_level_scalar = volume_interface.SetMasterVolumeLevelScalar
        master_vol_level_scalar.assert_called_with(volume_scaler, None)

    def test_get_vol(self, volume_percent, volume_scaler):
        volume_interface = Mock()
        volume_interface.GetMasterVolumeLevelScalar.return_value = volume_scaler

        windows_volume = audio.WindowsVolume(volume_interface)
        volume_info = windows_volume.get_vol()

        volume_interface.GetMasterVolumeLevelScalar.assert_called()
        assert volume_info == [['Master', [volume_percent]]]

    def test_no_volume_interface(self):
        mock_vol_interface = Mock()

        with patch('mqtt_remote_audio.audio.windows_volume_interface',
                   return_value=mock_vol_interface):
            windows_volume = audio.WindowsVolume()

        assert windows_volume.volume_interface == mock_vol_interface



class TestLinuxVolume:
    @pytest.mark.skipif(platform.system() != 'Linux', reason="requires linux platform")
    def test_set_vol(self, volume_percent, volume_scaler, mock_sound_interface):
        calls = [call(mock_sound_interface.sink_list[0].name, volume_scaler),
                 call(mock_sound_interface.sink_list[1].name, volume_scaler)]

        with patch('mqtt_remote_audio.audio.pulsectl.Pulse', return_value=mock_sound_interface):
            linux_volume = audio.LinuxVolume()
            linux_volume.set_vol(volume_percent)

        mock_sound_interface.volume_set_all_chans.assert_has_calls(calls)


    @pytest.mark.skipif(platform.system() != 'Linux', reason="requires linux platform")
    def test_get_vol(self, volume_percent, mock_sound_interface):
        with patch('mqtt_remote_audio.audio.pulsectl.Pulse', return_value=mock_sound_interface):
            linux_volume = audio.LinuxVolume()
            volume_info = linux_volume.get_vol()

        assert volume_info == [[mock_sound_interface.sink_list[0].name,
                                [volume_percent, volume_percent]],
                               [mock_sound_interface.sink_list[1].name,
                                [volume_percent, volume_percent]]]



class TestOtherVolume:
    @patch('mqtt_remote_audio.audio.logger')
    def test_set_vol(self, mock_logger, volume_percent, platform_os):
        error_message = f"No set speaker volume implementation for: '{platform_os}'"

        with patch('mqtt_remote_audio.audio.PLATFORM', new=platform_os):
            other_volume = audio.OtherVolume()
            other_volume.set_vol(volume_percent)

        mock_logger.warning.assert_called_with(error_message)

    @patch('mqtt_remote_audio.audio.logger')
    def test_get_vol(self, mock_logger, platform_os):
        error_message = f"No get speaker volume implementation for: '{platform_os}'"

        with patch('mqtt_remote_audio.audio.PLATFORM', new=platform_os):
            other_volume = audio.OtherVolume()
            other_volume.get_vol()

        mock_logger.warning.assert_called_with(error_message)



class TestChangeSpeakerVolume:
    def test_execute_good_command_message(self, command_msg, volume_percent, platform_os):
        payload = {"command": "name", "attributes": {'vol_percent': volume_percent}}
        command_msg.payload = payload
        mock_speaker_vol_setter = Mock()

        volume_changer = audio.ChangeSpeakerVolume(platform_os=platform_os,
                                             set_speaker_volume=mock_speaker_vol_setter)
        volume_changer.execute(command_msg)

        mock_speaker_vol_setter.assert_called_with(volume_percent)


    @patch('mqtt_remote.message.logger')
    def test_execute_command_message_wrong_attribute(self, mock_logger, command_msg,
                                                     volume_percent, platform_os):
        payload = {"command": "name", "attributes": {'vol_SCALAR': volume_percent}}
        command_msg.payload = payload
        mock_speaker_vol_setter = Mock()

        volume_changer = audio.ChangeSpeakerVolume(platform_os=platform_os,
                                             set_speaker_volume=mock_speaker_vol_setter)
        volume_changer.execute(command_msg)

        error_message = ''.join([f'A CommandMessage for the callback: \'{volume_changer.message_name}\'',
                                 f'must be of the form:\n{volume_changer.required_message_form}'])
        mock_logger.error.assert_any_call(error_message)


    @patch('mqtt_remote.message.logger')
    def test_execute_command_message_wrong_type(self, mock_logger, command_msg,
                                                volume_percent, platform_os):
        payload = {"command": "name", "attributes": {'vol_percent': str(volume_percent)}}
        command_msg.payload = payload
        mock_speaker_vol_setter = Mock()

        volume_changer = audio.ChangeSpeakerVolume(platform_os=platform_os,
                                             set_speaker_volume=mock_speaker_vol_setter)
        volume_changer.execute(command_msg)

        error_message = ''.join([f'A CommandMessage for the callback: \'{volume_changer.message_name}\'',
                                 f'must be of the form:\n{volume_changer.required_message_form}'])
        mock_logger.error.assert_any_call(error_message)


    def test_other_volume(self):
        mock_other_volume = Mock()

        with patch('mqtt_remote_audio.audio.OtherVolume', return_value=mock_other_volume):
            volume_changer = audio.ChangeSpeakerVolume(platform_os='Other')

        assert volume_changer.set_speaker_volume == mock_other_volume.set_vol


    def test_message_name(self):
        msg_name = 'change_speaker_volume'

        change_speaker_volume = audio.ChangeSpeakerVolume()

        assert change_speaker_volume.message_name == msg_name


    def test_required_message_form(self, platform_os):
        message_name = 'change_speaker_volume'
        required_message = ''.join([f'{{"command": "{message_name}", ',
                                    '"attributes": {"vol_percent": <int>}}'])

        volume_changer = audio.ChangeSpeakerVolume(platform_os, '')

        assert volume_changer.required_message_form == required_message



class TestGetSpeakerVolume:
    def test_execute_good_message(self, command_msg, volume_percent, platform_os):
        mock_mqtt_publish = Mock()
        mock_get_speaker_volume = Mock()
        mock_get_speaker_volume.return_value = [['Master', [volume_percent]]]
        expected_volume_message = f'\'Master\' volumes are: [{volume_percent}] (%)'
        command_msg.payload = {"command": "name",
                               "attributes": {"return_message": {"topic": "topic",
                                                                 "qos": 0,
                                                                 "retain": False}}}

        get_speaker_volume = audio.GetSpeakerVolume(platform_os, mock_get_speaker_volume)
        get_speaker_volume.mqtt_publish = mock_mqtt_publish
        get_speaker_volume.execute(command_msg)

        mock_mqtt_publish.assert_called_with(command_msg.topic, expected_volume_message,
                                             command_msg.qos, command_msg.retain)


    def test_execute_incorrect_message(self, command_msg, volume_percent, platform_os):
        mock_get_speaker_volume = Mock()
        mock_get_speaker_volume.return_value = [['Master', [volume_percent]]]
        command_msg.payload = {"command": "get_speaker_volume",
                               "attributes": {"return_message": {"TOPIC_WRONG": "topic",
                                                                 "qos": 0,
                                                                 "retain": False}}}

        with patch('mqtt_remote_audio.audio.log_wrong_command_message_form') as mock_log_wrong_command_message_form:
            get_speaker_volume = audio.GetSpeakerVolume(platform_os, mock_get_speaker_volume)
            get_speaker_volume.execute(command_msg)

        mock_log_wrong_command_message_form.assert_called_with(get_speaker_volume.message_name,
                                               get_speaker_volume.required_message_form)


    def test_other_volume(self):
        mock_other_volume = Mock()

        with patch('mqtt_remote_audio.audio.OtherVolume', return_value=mock_other_volume):
            get_speaker_volume = audio.GetSpeakerVolume(platform_os='Other')

        assert get_speaker_volume.get_speaker_volume == mock_other_volume.get_vol


    def test_no_platform(self, platform_os):
        with patch('mqtt_remote_audio.audio.PLATFORM', new=platform_os):
            get_speaker_volume = audio.GetSpeakerVolume()

        assert get_speaker_volume.platform_os == platform_os


    def test_required_message_form(self, platform_os):
        required_message_form = ''.join(['{"command": "get_speaker_volume", ',
                                         '"attributes": {"return_message": {'
                                         '"topic": <str>,'
                                         '"qos": <int>'
                                         '"retain": <bool>}}}'])
        mock_get_speaker_volume = Mock()

        get_speaker_volume = audio.GetSpeakerVolume(platform_os, mock_get_speaker_volume)

        assert get_speaker_volume.required_message_form == required_message_form
