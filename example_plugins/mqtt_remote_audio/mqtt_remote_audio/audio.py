"""Audio related functionality
"""
from abc import ABC, abstractmethod
from pathlib import Path
import logging
import platform

PLATFORM = platform.system()

import vlc
if PLATFORM == 'Windows':
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
if PLATFORM == 'Linux':
    import pulsectl

from mqtt_remote.message import (CommandMessageCallback,
                                 valid_payload_value,
                                 log_wrong_command_message_form)



# pylint: disable=C0103
logger = logging.getLogger(__name__)
# pylint: enable=C0103



AUDIO_FILE_DIRECTORY = str(Path(__file__).parent.parent / 'audio_files')



class AudioFilePlayer(ABC):
    """Abstract base class for players of audio files
    """
    @abstractmethod
    def play_file(self, audio_file):
        """Plays an audio file

        Args:
            audio_file (path like object): Path of the audio file to play
        """



class VLCAudioFilePlayer(AudioFilePlayer):
    """Plays an audio file via VLC

       VLC must be installed on the client computer.
    """
    def __init__(self):
        """Constructor
        """
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

    def play_file(self, audio_file):
        """Plays an audio file with VLC

        Args:
            audio_file (path like object): Path of the audio file to play
        """
        media = self.vlc_instance.media_new(audio_file)
        self.player.set_media(media)
        self.player.play()



class LocalAudioFilePlayer(CommandMessageCallback):
    """Plays an audio file already stored on the local client computer

    Requires an inbound message MQTT payload of the form:

        {"command": "play_local_audio_file", "attributes": {"audio_file": <str>}}
    """
    def __init__(self, audio_file_player=None, audio_file_dir=None):
        """Constructor

        Args:
            audio_file_player (AudioFilePlayer, optional): Specifies the audio file player to use
                to play the audio file specified in the MQTT message. Defaults to None.
            audio_file_dir (str, optional): A string of the directory in which the the audio file
                specified in the MQTT message is expected to be present. Defaults to None.
        """
        self._message_name = 'play_local_audio_file'
        self._required_message_form = ''.join([f'{{"command": "{self._message_name}", ',
                                               '"attributes": {"audio_file": "<str>"}}'])

        if audio_file_player is None:
            self.audio_file_player = VLCAudioFilePlayer()
        else:
            self.audio_file_player = audio_file_player

        if audio_file_dir is None:
            self.audio_file_dir = AUDIO_FILE_DIRECTORY
        else:
            self.audio_file_dir = audio_file_dir

    @property
    def message_name(self):
        """Getter

        Returns:
            str: The message name
        """
        return self._message_name

    @property
    def required_message_form(self):
        """Getter

        Returns:
            str: The required form of a CommandMessage that matches with this class
        """
        return self._required_message_form

    def _play_local_audio_file(self, inbound_message):
        """Plays the local audio file

        Args:
            inbound_message (CommandMessage): The CommandMessage that matched with this
                class
        """
        audio_file = inbound_message.payload['attributes']['audio_file']
        audio_file_to_play = str((Path(self.audio_file_dir) / audio_file).resolve())
        self.audio_file_player.play_file(audio_file_to_play)

        logger.info(f"Sent the following file to the audio file player: '{audio_file_to_play}'")

    def execute(self, inbound_message):
        """The code to be executed when a matching CommandMessage is received by
           CommandMessageCallbackCaller

        Args:
            inbound_message (CommandMessage): The CommandMessage that matched with this
                class
        """
        audio_file_valid = valid_payload_value(inbound_message, ['attributes', 'audio_file'], str)
        if audio_file_valid:
            self._play_local_audio_file(inbound_message)
        else:
            log_wrong_command_message_form(self._message_name, self._required_message_form)



class ComputerVolume(ABC):
    """An abstract base class for a computer volume manager
    """
    @abstractmethod
    def set_vol(self, volume_percent):
        """Sets the volume level of a computer

        Args:
            volume_percent (int): The desired volume percentage for the computer: 0 to 100
        """

    @abstractmethod
    def get_vol(self):
        """Gets the volume level of a computer
        """


def windows_volume_interface():
    """Creates and returns a pycaw.pycaw volume interface

    Returns:
        comtypes.POINTER(IAudioEndpointVolume): pycaw.pycaw volume interface
    """
    output_devices = AudioUtilities.GetSpeakers()
    # pylint: disable=protected-access
    audio_interface = output_devices.Activate(IAudioEndpointVolume._iid_,
                                              CLSCTX_ALL, None)
    # pylint: enable=protected-access
    volume_interface = cast(audio_interface, POINTER(IAudioEndpointVolume))
    return volume_interface


class WindowsVolume(ComputerVolume):
    def __init__(self, volume_interface=None):
        """Allows Windows master volume to be determined and set

        Args:
            volume_interface (comtypes.POINTER(IAudioEndpointVolume), optional):
                pycaw.pycaw volume interface. Defaults to None.
        """
        if volume_interface is None:
            self.volume_interface = windows_volume_interface()
        else:
            self.volume_interface = volume_interface

    def set_vol(self, volume_percent):
        """Sets the Windows master volume

        Args:
            volume_percent (int): The desired volume percentage for the computer: 0 to 100
        """
        volume_scalar = volume_percent / 100
        self.volume_interface.SetMasterVolumeLevelScalar(volume_scalar, None)

    def get_vol(self):
        """Gets the Windows master volume

        Returns:
            List[List[str, List[int]]]: List of output devices and their associated volume levels:
                [[<output_device>, [<volume_level_one>, <volume_level_two>, ...], [...], [...]]
        """
        volume_level = int(self.volume_interface.GetMasterVolumeLevelScalar() * 100)
        return [['Master', [volume_level]]]



class LinuxVolume(ComputerVolume):
    """Allows all Linux volumes to be determined and set

    Requires the linux system to be using pulse audio for sound management
    """
    def _sound_interface(self):
        """Returns a pulsectl sound interface

        Returns:
            pulsectl.Pulse: pulsectl sound interface
        """
        return pulsectl.Pulse('')

    def set_vol(self, volume_percent):
        """Sets all Linux output device volumes

        Args:
            volume_percent (int): The desired volume percentage for the computer: 0 to 100
        """
        sound_interface = self._sound_interface()

        volume_scalar = volume_percent / 100

        for sink in sound_interface.sink_list():
            sound_interface.volume_set_all_chans(sink, volume_scalar)

    def get_vol(self):
        """Gets all Linux output device volumes

        Returns:
            List[List[str, List[int]]]: List of output devices and their associated volume levels:
                [[<output_device>, [<volume_level_one>, <volume_level_two>, ...], [...], [...]]
        """
        sound_interface = self._sound_interface()

        volumes = []
        for sink in sound_interface.sink_list():
            sink_name = sink.name
            sink_volumes = sink.volume.values
            sink_volumes = [int(vol * 100) for vol in sink_volumes]
            volumes.append([sink_name, sink_volumes])
        return volumes


class OtherVolume(ComputerVolume):
    """Logs messages for unsupported platforms
    """
    def set_vol(self, volume_percent):
        logger.warning(f"No set speaker volume implementation for: '{PLATFORM}'")

    def get_vol(self):
        logger.warning(f"No get speaker volume implementation for: '{PLATFORM}'")


class ChangeSpeakerVolume(CommandMessageCallback):
    """Callback to change the speaker volume

    Requires an inbound message MQTT payload of the form:

        {"command": "change_speaker_volume", "attributes": {"vol_percent": <int>}}

    """
    def __init__(self, platform_os=None, set_speaker_volume=None):
        """Constructor

        Args:
            platform_os (str, optional): The platform OS, as compatible with platform.system.
                Defaults to None.
            set_speaker_volume (function, optional): Function to change the speaker volume,
                must be from a class that inherits from ComputerVolume. Defaults to None.
        """
        self._message_name = 'change_speaker_volume'
        self._required_message_form = ''.join([f'{{"command": "{self._message_name}", ',
                                               '"attributes": {"vol_percent": <int>}}'])

        if platform_os is None:
            platform_os = PLATFORM

        if set_speaker_volume is None:
            if platform_os == 'Windows':
                self.set_speaker_volume = WindowsVolume().set_vol
            elif platform_os == 'Linux':
                self.set_speaker_volume = LinuxVolume().set_vol
            else:
                self.set_speaker_volume = OtherVolume().set_vol
        else:
            self.set_speaker_volume = set_speaker_volume

    @property
    def message_name(self):
        """Getter

        Returns:
            str: Message name
        """
        return self._message_name

    @property
    def required_message_form(self):
        """Getter

        Returns:
            str: Required message form
        """
        return self._required_message_form

    def execute(self, inbound_message):
        """The code to be executed when a matching CommandMessage is received by
           CommandMessageCallbackCaller

        Args:
            inbound_message (CommandMessage): The CommandMessage that matched with this
                class
        """
        volume_percent_valid = valid_payload_value(
            inbound_message, ['attributes', 'vol_percent'], int)
        if volume_percent_valid:
            volume_percent = inbound_message.payload['attributes']['vol_percent']
            self.set_speaker_volume(volume_percent)
            logger.info(f"Requested that speaker volume is changed to: '{volume_percent}%'")
        else:
            log_wrong_command_message_form(self.message_name, self._required_message_form)



class GetSpeakerVolume(CommandMessageCallback):
    """Callback to get the speaker volume and send it via an MQTT message

    The details of the MQTT message to return are included in the inbound message

    Requires an inbound message MQTT payload of the form:

        {"command": "get_speaker_volume",
         "attributes": {"return_message": {"topic": <str>,
                                           "qos": <int>,
                                           "retain": <bool>}}}
    """
    def __init__(self, platform_os=None, get_speaker_volume=None):
        """Constructor

        Args:
            platform_os (str, optional): The platform OS, as compatible with platform.system.
                Defaults to None.
            get_speaker_volume (function, optional): Function to get the speaker volume, must
                be from a class that inherits from ComputerVolume. Defaults to None.
        """
        self._message_name = 'get_speaker_volume'
        self._required_message_form = ''.join([f'{{"command": "{self._message_name}", ',
                                               '"attributes": {"return_message": {'
                                                    '"topic": <str>,'
                                                    '"qos": <int>'
                                                    '"retain": <bool>}}}'])
        self.mqtt_publish = None

        if platform_os is None:
            self.platform_os = PLATFORM
        else:
            self.platform_os = platform_os

        if get_speaker_volume is None:
            if self.platform_os == 'Windows':
                self.get_speaker_volume = WindowsVolume().get_vol
            elif self.platform_os == 'Linux':
                self.get_speaker_volume = LinuxVolume().get_vol
            else:
                self.get_speaker_volume = OtherVolume().get_vol
        else:
            self.get_speaker_volume = get_speaker_volume

    @property
    def message_name(self):
        """Getter

        Returns:
            str: Message name
        """
        return self._message_name

    @property
    def required_message_form(self):
        """Getter

        Returns:
            str: Required message form
        """
        return self._required_message_form

    def _outbound_payload_from_volume_info(self, volume_info):
        """Converts volume_info into a string

        The string is for sending as the payload in an outbound MQTT message

        Args:
            volume_info List[List[str, List[int]]]: List of output devices and their associated
            volume levels:
                [[<output_device>, [<volume_level_one>, <volume_level_two>, ...], [...], [...]]

        Returns:
            str: The message for sending via MQTT
        """
        volume_message = []

        for vol in volume_info:
            output_name = vol[0]
            output_volumes = vol[1]
            volume_message.append(f'\'{output_name}\' volumes are: {output_volumes} (%)')
        volume_message = '\n'.join(volume_message)

        return volume_message

    def _inbound_message_values_valid(self, inbound_message):
        """Checks to see if required inbound message values are valid

        Args:
            inbound_message (CommandMessage): The CommandMessage that matched with this
                class

        Returns:
            bool:
                True: all required inbound message values are valid
                False: one or more required inbound message values are not valid
        """
        topic_valid = valid_payload_value(
            inbound_message, ['attributes', 'return_message', 'topic'], str)
        qos_valid = valid_payload_value(
            inbound_message, ['attributes', 'return_message', 'qos'], int)
        retain_valid = valid_payload_value(
            inbound_message, ['attributes', 'return_message', 'retain'], bool)

        return all([topic_valid, qos_valid, retain_valid])


    def _publish_volume_mqtt_message(self, inbound_message, outbound_payload):
        """Publishes the outbound MQTT message containing data on the current volume(s)

        Args:
            inbound_message (CommandMessage): The CommandMessage that matched with this
                class
            outbound_payload (str): The payload for the outbound MQTT message
        """
        if self._inbound_message_values_valid(inbound_message):
            topic = inbound_message.payload['attributes']['return_message']['topic']
            qos = inbound_message.payload['attributes']['return_message']['qos']
            retain = inbound_message.payload['attributes']['return_message']['retain']

            # pylint: disable=not-callable
            self.mqtt_publish(topic, outbound_payload, qos, retain)
            # pylint: enable=not-callable
            logger.info("Speaker volume published using details supplied")
        else:
            log_wrong_command_message_form(self.message_name, self._required_message_form)


    def execute(self, inbound_message):
        """The code to be executed when a matching CommandMessage is received by
           CommandMessageCallbackCaller

        Args:
            inbound_message (CommandMessage): The CommandMessage that matched with this
                class
        """
        volume_info = self.get_speaker_volume()
        outbound_message = self._outbound_payload_from_volume_info(volume_info)
        self._publish_volume_mqtt_message(inbound_message, outbound_message)
