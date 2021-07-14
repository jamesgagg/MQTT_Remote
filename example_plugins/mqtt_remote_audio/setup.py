from distutils.core import setup

setup(name='mqtt_remote_audio',
      version='0.1',
      description='MQTT Computer Remote Control - Audio Plugin',
      author='James Gagg',
      packages=['mqtt_remote_audio'],
      install_requires=["pycaw;platform_system=='Windows'",
                        'python-vlc',
                        "pulsectl;platform_system=='Linux'"],
     )
