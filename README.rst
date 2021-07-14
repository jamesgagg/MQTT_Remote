README
======

Contents
--------

* `1.0 - What is it?`_
* `2.0 - Ok, why should I be interested?`_
* `3.0 - I still don't quite get it, please give me an example`_
* `4.0 - What other things could MQTT Remote do when it receives an MQTT message?`_
* `5.0 - How does it work?`_
* `6.0 - Are there any callbacks built in to the app?`_
* `7.0 - A quick note on placeholders`_
* `8.0 - Why 'standardised' MQTT message payloads and what do they look like?`_
* `9.0 - What are the main features of the app?`_
* `10.0 - What do I need to install and run it?`_
* `11.0 - How do I install it?`_
* `12.0 - How do I use MQTT Remote?`_

  * `12.1 - How do I switch to the correct virtual environment?`_
  * `12.2 - How do I change directory to the package directory?`_
  * `12.3 - How do I configure MQTT Remote?`_
  * `12.4 - How do I start MQTT Remote?`_
  * `12.5 - How do I stop MQTT Remote?`_
  * `12.6 - Restarting MQTT Remote`_
  * `12.7 - Local callbacks`_

    * `12.7.1 - What is a local callback?`_
    * `12.7.2 - What are the rules for local callbacks?`_
    * `12.7.3 - How do I add a local callback?`_
    * `12.7.4 - How do I use an existing local callback?`_

  * `12.8 - How do I make a callback do what I want?`_

    * `12.8.1 - Imports`_
    * `12.8.2 - Callback class`_

      * `12.8.2.1 - __init__ method`_
      * `12.8.2.2 - execute method`_

* `13 - Examples`_

  * `13.1 - Example 1 - Adding a local callback to sum two positive integers`_

    * `13.1.1 - Problem`_
    * `13.1.2 - Outline solution`_
    * `13.1.3 - Designing the payload message`_
    * `13.1.4 - Creating a local callback file from the template`_
    * `13.1.5 - Editing the new local callback file`_
    * `13.1.6 - Running the new callback`_

  * `13.2 - Example 2 - Adding an existing callback to the app`_

    * `13.2.1 - Problem`_
    * `13.2.2 - Solution`_

* `14 - Project status`_
* `15 - To do`_



1.0 - What is it?
-----------------

It's an app that allows you to easily run python code on a remote computer by
sending MQTT messages.


2.0 - Ok, why should I be interested?
-------------------------------------

Because computers are not created or set up equally. They have differing
resources, e.g.:

- Some are tiny microcontrollers that have just about enough resources to
  do something like blink an LED or send an MQTT message.
- Some are high end servers with crazy amounts of computing power but don't
  have things like monitors or sound playing hardware.
- Some are gaming PCs with premium graphic and sound capabilities.
- Only certain apps can be installed on certain computers.
- Every computer is installed in a different physical location.
- etc.

and because of this you may have a situation where you want computer 'A' to
perform a task but it can't because it doesn't have the required resources.

If, though, you have computer 'B' with the required resources and it can
receive an MQTT message from computer 'A' then MQTT Remote could provide you
with an easy way of getting computer 'A' to get computer 'B' to perform the
required task.


3.0 - I still don't quite get it, please give me an example
-----------------------------------------------------------

No problem, let's say:

- You want to make a DIY doorbell system by connecting a push button to a
  microcontroller.
- When the push button is pressed you want a 'ding-dong' sound to be produced.
- The microcontroller has no built in means of making sounds but it can send
  MQTT messages.
- Your network has an MQTT broker running on it.
- You have another computer, a Raspberry Pi, on your network that can play
  sound through attached speakers.

In this situation you could create a solution by:

- installing MQTT Remote on the Raspberry Pi.
- programming MQTT Remote so that when it receives a specific MQTT message it
  plays a 'ding-dong' sound through the Raspberry Pi's speakers.
- programming the microcontroller to publish the specific MQTT message when the
  push button is pressed.

Then when the push button is pressed:

- the microcontroller publishes the specific MQTT message.
- the MQTT broker receives and then forwards the MQTT message onto the
  Raspberry Pi.
- on the Raspberry Pi the MQTT Remote app receives and processes the MQTT
  message, instructing the Pi to play a 'ding-dong' sound via its speakers.
- the Raspberry Pi plays the 'ding-dong' sound.

  (This all happens within a few milliseconds and appears to be instant to the
  user.)


4.0 - What other things could MQTT Remote do when it receives an MQTT message?
------------------------------------------------------------------------------

- Play video.
- Make use of an internet connection.
- Perform a task quicker than a computer with a lower spec.
- Interact with apps installed on the computer.
- Log data.
- Switch something on or off.
- Interact with non-MQTT compatible devices, e.g.:

  - Routers.
  - Network speakers.

These are just some examples. The limits of what MQTT Remote can do in
response to receiving an MQTT message are only really defined by the limits of
the resources of the computer it's running on, i.e. the limits of its hardware
and software.


5.0 - How does it work?
-----------------------

The MQTT Remote app is based around a python implemented MQTT client that:

-  allows the user to register multiple MQTT messages that follow a
   standardised payload form.
-  allows the user to associate a callback with each MQTT message they’ve
   registered.
-  listens for registered MQTT messages and if one is detected the
   associated callback is executed.


6.0 - Are there any callbacks built in to the app?
--------------------------------------------------

No, the app starts you off with a blank canvas. It's up to you to create the
callbacks you need or add existing ones. The app is designed to make both very
easy, see:

- `12.7.3 - How do I add a local callback?`_
- `12.7.4 - How do I use an existing local callback?`_

It's hoped that over time a library of callbacks can be built up and stored in
this repository for the user to pick and choose from as required. The user
should then be able to add a new capability within seconds.


7.0 - A quick note on placeholders
----------------------------------

Within this documentation the symbols '<' and '>' are used to indicate
information that's specific to the user. Sometimes the user is required to
replace these symbols and the text between them with their own data, e.g.
if you were asked to enter the following at the command line:

::

  some_command <your name>

and your name was 'Monty' then you'd enter:

::

  some_command Monty


8.0 - Why 'standardised' MQTT message payloads and what do they look like?
--------------------------------------------------------------------------

A standardised MQTT message payload form is required to allow MQTT Remote to
easily recongise and process messages intended for it.

The standardised payload is simple, flexible and json based. It has the form:

::

  {“command”: “<command>”, “attributes”: {<attribute key-value pairs>}}

Where:

- **<command>**.....Is a unique string identifier for the command (task) you
  want to be executed.
- **<attribute key-value pairs>**.....Is a json object containing all of
  the information necessary to execute the command.

  - By nesting items a lot of information can be included whilst maintaining
    useful structure and good readability.

See '`13.1.3 - Designing the payload message`_' for an example.


9.0 - What are the main features of the app?
--------------------------------------------

- It’s easy to use:

  - A .yaml file is used for configuration, see:

    - `12.3 - How do I configure MQTT Remote?`_

  - Significant logging is built in to make debugging easier.
  - Minimal effort is required to get callbacks into operation:

    - Local callbacks:

      - New callbacks - see:
        '`12.7.3 - How do I add a local callback?`_'.
      - Existing callbacks - see:
        '`12.7.4 - How do I use an existing local callback?`_'.

    - Plugin callbacks:

      - Full documentation for plugins is not available yet but further
        information can be found in the '`15 - To do`_' section.

- It’s reliable:

  - Exception handling keeps the MQTT client running if problems occur
    whilst also keeping the user informed of what's happening.
  - There's wide test coverage (pytest).

- It’s multi-platform:

  - Successful tests to date:

    - PC: Windows: Windows 10 Pro
    - PC: Linux: Ubuntu 20.04.
    - Raspberry Pi 4: Linux: Raspberry Pi OS: Buster.


10.0 - What do I need to install and run it?
--------------------------------------------

The requirements for the computer MQTT Remote will be installed on are:

  - it must be on a network that has an MQTT broker running on it.

    - mosquitto (https://mosquitto.org/) is a good choice for an MQTT broker
      if you don't already have one set up on your network.

      - The broker can be installed on the same computer as MQTT Remote.

  - it must have Python 3.X installed.

    - The app was developed with python 3.9 and:

      -  paho-mqtt 1.5.1
      -  PyYAML 5.4.1
      -  pyperclip 1.8.2

      however it should work with a range of other versions but this is yet to
      be confirmed with formal testing.

    - https://www.python.org/

  - if you're using git clone during installation then git must be installed.

    -  https://git-scm.com/


11.0 - How do I install it?
---------------------------

For some linux distributions you may have to substitute 'python3' for
'python' in the instructions below.

- Copy this project to a <directory> of your choice using either git clone or a zip file:

  - git clone:

    ::

      cd <directory>
      git clone https://github.com/jamesgagg/MQTT_Remote

  - zip file:

    - download the zip from:
      https://github.com/jamesgagg/MQTT_Remote/archive/master.zip
    - extract it into <directory>

- Change directory to the root of the project you just downloaded:

  - Windows:

    ::

      cd "<your drive>:\<your path>\<directory>\<project root>"

  - Linux:

    ::

      cd "/<your path>/<directory>/<project root>"

  Depending on which method you used to copy the project files <project root>
  should be either:

  - 'MQTT_Remote'
  - 'MQTT_Remote-master' or

- Create a new python environment:

  ::

    python -m venv env

- Activate the new environment:

  - Windows:

    ::

      env\Scripts\activate

  - Linux:

    ::

      source env/bin/activate

- Install MQTT remote:

  ::

    pip install .

  - if you get an error update pip:

    ::

      python -m pip install --upgrade pip

    and try again.


12.0 - How do I use MQTT Remote?
--------------------------------

12.1 - How do I switch to the correct virtual environment?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. If you're in another virtual environment type the following at the command
   line to exit:

   ::

     deactivate

   If you're not in another virtual environment then skip this step and
   proceed to 2.

2. At the command line change your path to the root directory of the project,
   i.e. <project root> in `11.0 - How do I install it?`_.

3. At the command line type the following:

  - Windows:

    ::

      env\Scripts\activate

  - Linux:

    ::

      source /env/bin/activate


12.2 - How do I change directory to the package directory?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type the following at the command line to find the package directory:

::

  mr_where

This should then return a string of the package directory. As it will be
different in each case let's represent it with:

::

  <package directory>

Then to change directory it's simple a case of typing the following at the
command line:

::

  cd "<package directory>"


12.3 - How do I configure MQTT Remote?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Make sure you're in the correct virtual environment:

  - See `12.1 - How do I switch to the correct virtual environment?`_

- At the command line change the directory to where the MQTT Remote package
  was installed and find the 'config.yaml' file.

  - If you don't know where the package was installed then see
    `12.2 - How do I change directory to the package directory?`_

- Open 'config.yaml' with an editor of your choice. It's contents will look
  something like:

  .. code-block:: yaml

    logging:
      level: "DEBUG"
      log_format: '%(asctime)s  %(name)s  %(levelname)s: %(message)s'
      output_file:
        name: "mqtt_remote.log"
        max_size: 5242880
        max_backups: 2
      log_base_client: True

    mqtt_broker:
      ip: "192.168.1.123"
      port: 1883
      user_name: 'monty'
      password_required: True
      password: 'monty_python'
      keepalive: 60

    mqtt_session:
      protocol: "3.1.1"
      transport: 'tcp'
      clean: True

    subscriptions:
      this_mqtt_client:
        name: "spam"
        qos: 0

- Here's an explanation of the yaml key-value pairs:

  - **logging**: the parameters for setting up the logging:

    - **level**: the required minimum logging level, five choices:

      - "DEBUG"
      - "INFO"
      - "WARNING"
      - "ERROR"
      - "CRITICAL"

    see: https://docs.python.org/3/library/logging.html#logging-levels for
    more information.

    - **log_format**: the required format for the logs - see:
      https://docs.python.org/3/library/logging.html#logging.Formatter for
      more information.
    - **output_file**: the parameters for the file to save all logging data
      to:

      - **name**: the name of the logging file.
      - **max_size**: the maximum allowable size of the logging file.
      - **max_backups**: the maximum number of logging files allowed before
        they start being overwritten.

    - **log_base_client**: whether to add the logs from the underlying MQTT
      Client (Paho) into the logs for this app, two choices:

      - True
      - False

  - **mqtt_broker**: the parameters for setting up access to the MQTT broker:

    - **ip**: the IP address of the MQTT broker.
    - **port**: the port the MQTT broker uses for MQTT traffic.
    - **user_name**: the user name for MQTT broker authentication.
    - **password_required**: whether the MQTT broker requires a password for
      authentication, two choices:

      - True
      - False

    - **password**: the password for MQTT broker authentication:

      - If no password is required:

        - Leave blank.
        - Make sure 'password_required' is set to False.

      - If you don't want to store your password in the yaml file in plain
        text but instead want to be prompted for it each time you start the
        app:

        - Leave blank.
        - Make sure 'password_required' is set to True.

    - **keepalive**: The maximum time, in integer seconds, that you want the
      client to remain quiet without sending an MQTT packet to the broker to
      confirm it is still connected.

  - **mqtt_session**: the parameters for setting up each MQTT session:

    - **protocol**: The MQTT protocol that your MQTT broker uses. Can be:

      - "3.1"
      - "3.1.1"
      - "5"

    - **transport**: The MQTT network transport type. Can be:

      - "websockets"
      - "tcp"

    - **clean**: Determines whether the broker will remove all information
      about the client when it disconnects, two choices:

      - True

        - All client information will be removed.

      - False

        - Client information will be retained.

  - **subscriptions**: the parameters for setting up the topic for the client
    to subscribe to:

    - **this_mqtt_client**:

      - **name**: The name you want to give to the MQTT Remote's MQTT Client.
        The client will subscribe to an MQTT topic with this name in order
        to receive relevant MQTT messages. All MQTT messages to be received
        by MQTT Remote must be publishing using this name as the MQTT topic.
      - **qos**: the desired Quality Of Service for MQTT messages.

- Using the information above change the 'config.yaml' file to match with your
  particular set up.


12.4 - How do I start MQTT Remote?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Make sure the environment you created is activated, if not see:
  `12.1 - How do I switch to the correct virtual environment?`_

- Then type the following at the command line:

  ::

    mr_start


12.5 - How do I stop MQTT Remote?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure the the command line window where MQTT Remote is running is
selected and then simply type hold down 'Ctrl' and hit 'C'. MQTT
Remote should then shut down gracefully.


12.6 - Restarting MQTT Remote
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each time a change is made to the configuration file or a callback MQTT Remote
will need to be stopped and restarted for those changes to take effect. To do
this follow the instructions in:

  - `12.5 - How do I stop MQTT Remote?`_
  - `12.4 - How do I start MQTT Remote?`_


12.7 - Local callbacks
^^^^^^^^^^^^^^^^^^^^^^

12.7.1 - What is a local callback?
""""""""""""""""""""""""""""""""""

A local callback is a callback that's run locally from a sub directory in the
installed package directory.

(The other type of callback is a plugin callback, see `15 - To do`_.)


12.7.2 - What are the rules for local callbacks?
""""""""""""""""""""""""""""""""""""""""""""""""

1. The code for local callbacks must be of the form defined in the
   **'class_template.txt'** file found in the package installation directory.

  - If you don't know where the package was installed then see
    `12.2 - How do I change directory to the package directory?`_

2. The code for each callback must be contained in a python file with a
   **'.py'** extension within the **'\local_callbacks'** sub directory of the
   package installation directory.

  - If you don't know where the package was installed then see
    `12.2 - How do I change directory to the package directory?`_

3. Multiple callback classes, as defined in **'class_template.txt'**, can be
   held within a single **'.py'** file.

4. Multiple **'.py'** callback files can exist within the
   **'\local_callbacks'** sub directory.

   - All enabled callbacks in all files within the **'\local_callbacks'** sub
     directory will be automatically found and loaded by MQTT Remote at run time.


12.7.3 - How do I add a local callback?
"""""""""""""""""""""""""""""""""""""""

There are a few choices for how we can add a new callback:

(For 2. and 3. you will need to be in the correct virtual environment, see:
`12.1 - How do I switch to the correct virtual environment?`_)

1. Manually:

  - Find the 'class_template.txt' file.

    - For it's location see:
      `12.7.2 - What are the rules for local callbacks?`_

  - Open the file.
  - Copy the file contents.
  - Open the target '.py' file in the 'local_callbacks' sub directory:

    - see `12.7.2 - What are the rules for local callbacks?`_ for the location
      of the 'local_callbacks' sub directory.
    - Create a new '.py' file first if required or...
    - Choose an existing '.py' file that already contains a working callback.

  - Paste the copied file contents into the '.py' file.

    - Don't copy and paste the import statement into an existing '.py' file as
      only one is required per file.

  - Edit the copied class to suit your needs.

    - See: `12.8 - How do I make a callback do what I want?`_

2. Semi-automatically:

  - Type the following at the command line:

    ::

      mr_copy_clip

    (This command uses copy/paste mechanisms tied into display functionality.
    For this reason if the computer you are running is headless then this command
    may not work.)

  - Open the target '.py' file in the 'local_callbacks' sub directory

    - see `12.7.2 - What are the rules for local callbacks?`_ for the location
      of the 'local_callbacks' sub directory.
    - Create a new '.py' file first if required or...
    - Choose an existing '.py' file that already contains a working callback.

  - Paste the copied file contents into the '.py' file.

    - Don't copy and paste the import statement into an existing '.py' file as
      only one is required per file.

  - Open the newly created file and edit the copied class to suit your needs.

    - See: `12.8 - How do I make a callback do what I want?`_

3. Automatically:

  - Type the following at the command line and respond to the prompts:

    ::

      mr_create_callback_file

  - Open the newly created file in the 'local_callbacks' sub directory

    - see `12.7.2 - What are the rules for local callbacks?`_ for the location
      of the 'local_callbacks' sub directory.

  - Edit the copied class to suit your needs.

    - See: `12.8 - How do I make a callback do what I want?`_


12.7.4 - How do I use an existing local callback?
"""""""""""""""""""""""""""""""""""""""""""""""""

1. Copy or move the '.py' file that contains the existing callback into the
   'local_callbacks' directory.

   - To find the location of your 'local_callbacks' directory please
     see `12.7.2 - What are the rules for local callbacks?`_.

2. Examine the imports section of the '.py' file to see if the callback
   requires any external libraries that aren't already installed.

   - To get a list of the external libraries that are already installed:

     - Make sure you are in the correct virtual environment, see
       `12.1 - How do I switch to the correct virtual environment?`_
     - Type the following at the command line:

       ::

         pip freeze

     - To install any missing external libraries please see the home page of each
       individual library for instructions. Generally though external libraries
       are installed in the following way:

       - Make sure you are in the correct virtual environment, see
         `12.1 - How do I switch to the correct virtual environment?`_
       - Type the following at the command line:

         ::

           pip install <library name>


12.8 - How do I make a callback do what I want?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's start off by seeing what a raw callback taken from 'class_template.txt'
looks like. We can then break this down into its constituent parts to see what
we may need to change to get it to do what we want.

::

  from mqtt_remote.message import CommandMessageCallback



  class ClassName(CommandMessageCallback):
  """Class docstring
  """
  def __init__(self):
      """Constructor
      """
      # self.disabled = True # optional
      self._message_name = 'message' # required
      # self.config = None # optional
      # self.mqtt_publish = None # optional

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
      pass


12.8.1 - Imports
""""""""""""""""

This is the statement to import the base class that our callback class inherits
from:

::

  from mqtt_remote.message import CommandMessageCallback

This line should only be included once per '.py' file.


12.8.2 - Callback class
"""""""""""""""""""""""

The lines from 'class ClassName(CommandMessageCallback):' to 'pass' define
the callback class.

::

  class ClassName(CommandMessageCallback):
  """Class docstring
  """
  def __init__(self):
      """Constructor
      """
      # self.disabled = True # optional
      self._message_name = 'message' # required
      # self.config = None # optional
      # self.mqtt_publish = None # optional

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
      pass

Within the callback class three methods are defined:

1. __init__
2. message_name
3. execute

We only need to be concerned with 1. and 3. as 2. is just a simple getter
method that we're not required to change.


12.8.2.1 - __init__ method
""""""""""""""""""""""""""
This is the constructor for the class. This is the method that's called when
an object is created from the class.

There are four important lines in this method:

::

  # self.disabled = True # optional
  self._message_name = 'message' # required
  # self.config = None # optional
  # self.mqtt_publish = None # optional

|

**# self.disabled = True # optional**

If

::

  # self.disabled = True # optional'

is uncommented, i.e. changed to:

::

  self.disabled = True # optional

then this will disable this callback. This means if an MQTT message that
matches with this callback is received then the callback won't be called.

|

**self._message_name = 'message' # required**

In the line:

::

  self._message_name = 'message' # required

'message' must be changed to the string that you want to use to trigger the
callback to be called, i.e. the <command> string in the standardised MQTT
message payload as defined in:
`8.0 - Why 'standardised' MQTT message payloads and what do they look like?`_

As an example: if you want the following MQTT message payload to trigger
your callback:

::

  {“command”: “do_something”, “attributes”: {}}

then you'd need to have the following line in the constructor:

::

  self._message_name = 'do_something' # required

|

**# self.config = None # optional**

If

::

  # self.config = None # optional

is uncommented to:

::

  self.config = None # optional

then you will be able to access all of the configuration data via
'self.config' within the code you define in the 'execute' method.

The configuration data is stored in a python dictionary so can be accessed
with traditional techniques. As an example:

  To get the MQTT broker IP address from the configuration you could write
  the following code:

  ::

    mqtt_broker_ip = self.config['mqtt_broker']['ip']

see 'mqtt_remote.config module' in the API documents to get a better
idea of the information available.

|

**# self.mqtt_publish = None # optional**

If

::

  # self.mqtt_publish = None # optional

is uncommented to:

::

  self.mqtt_publish = None # optional

then 'self.mqtt_publish' can be used to publish MQTT messages within the
code you define in the ‘execute’ method, e.g.:

::

  self.mqtt_publish('spam', 'I love spam!', 0, False)

would result in the payload 'I love spam!' being sent to the MQTT broker
with a request to publish it to devices subscribed to the 'spam' topic.
This would be with a quality of service of 0 and an instruction for the
message not to be retained.

See the 'mqtt_remote.mqtt_client module' section of the API documentation
for more information.


12.8.2.2 - execute method
"""""""""""""""""""""""""
Here

::

  pass

should be replaced with the code you want to run when the callback is called,
e.g. if you wanted to print something to the command line when you received
a message then you'd just need to replace 'pass' with something like:

::

  print('Yeah! I received a message.')

so then your execute method would look like:

::

  def execute(self, inbound_message):
    """The code to be executed when a matching MQTT message is received

    Execution occurs when a CommandMessage containing a 'payload['command']' value that
    matches with self._message_name is received by CommandMessageCallbackCaller

    Args:
        inbound_message (CommandMessage): The CommandMessage with a 'payload['command']'
            value that matches with self._message_name
    """
    print('Yeah! I received a message.')

Note that the execute method has 'inbound_message' as an argument. This is
the inbound message payload in dictionary form and is always supplied when the
execute method is called.

Because the inbound message payload is a dictionary it can be accessed using
standard python dictionary techniques, e.g. to access the attributes section
of a payload message you'd use something like:

::

  attributes = inbound_message.payload['attributes']


13 - Examples
-------------

13.1 - Example 1 - Adding a local callback to sum two positive integers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

13.1.1 - Problem
""""""""""""""""

Let's say we have a situation where we're using a home automation server and
we need to use a remote computer to sum two positive integers and return that
value to us.

The MQTT client running on the home automation server is subscribed to the
'HA' topic and so will receive any messages published with this name.

Both the remote computer and the home automation server are on the same local
network. An MQTT broker is also running on the network.

The remote computer has already had MQTT Remote installed, configured and
started.

- `11.0 - How do I install it?`_
- `12.3 - How do I configure MQTT Remote?`_
- `12.4 - How do I start MQTT Remote?`_

MQTT Remote on the remote computer has been set up to subscribe to the 'RC'
topic.


13.1.2 - Outline solution
"""""""""""""""""""""""""

Our plan to solve the problem could then be as simple as doing the following
on our remote computer:

- Writing a callback for MQTT Remote that does the following when a particular
  MQTT message is received:

    - Calculates the sum of the two positive integers received in that message.
    - Sends an MQTT message containing the sum to the 'HA' topic so that it
      will be received by the home automation server.

- Quickly stopping and restarting MQTT Remote to put the changes into place.


13.1.3 - Designing the payload message
""""""""""""""""""""""""""""""""""""""

In order to create our callback later on we first need to decide what
information the callback will need to receive. We then need to decide how
we're going to structure that information within the standardised MQTT
message payload. This is so we know where we're going to be able to find
specific items of information within the payload when we write the callback.

We know from
'`8.0 - Why 'standardised' MQTT message payloads and what do they look like?`_'
that the standardised MQTT message form that MQTT Remote must receive messages
in is:

.. code-block:: none

   {“command”: “<command>”, “attributes”: {<attribute key-value pairs>}}

so let's start off by setting <command> to a nice descriptive name, i.e.:
"sum_positive_ints"

For the <attribute key-value pairs>:

- We know the message we're sending needs to contain two positive integers
  otherwise we'll have nothing to sum.
- We also know we'll need the MQTT Remote app to send an MQTT message to the
  broker so that it can forward the calculated sum onto the home automation
  server. We therefore know that we need to include all of the information
  necessary to send this MQTT message.

  - From `12.8.2.1 - __init__ method`_ we know that to send an MQTT message
    using MQTT remote the following information is required:

    - An MQTT topic
    - An MQTT message payload
    - An MQTT qos value
    - An MQTT retain flag

With the above in mind we can structure our <attribute key-value pairs> to be:

.. code-block:: none

   "integer_one": <int>,
   "integer_two": <int>,
   "return_message": {"topic": <str>,
                      "qos": <int>,
                      "retain": <bool>}



The final standardised payload would therefore be:

.. code-block:: none

   {"command": "sum_positive_ints",
    "attributes": {"integer_one": <int>,
                   "integer_two": <int>,
                   "return_message": {"topic": <str>,
                                      "qos": <int>,
                                      "retain": <bool>}}}


13.1.4 - Creating a local callback file from the template
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The template code we need to create our local callback is contained within the
'class_template.txt' file (for it's location see:
'`12.7.2 - What are the rules for local callbacks?`_').

As seen in '`12.7.3 - How do I add a local callback?`_' there are three ways we
can get that code into a file. After sure we're in the correct virtual
environment, see:
'`12.1 - How do I switch to the correct virtual environment?`_' we're going to
use the most convenient option:

::

  mr_create_callback_file

This will result in us being prompted for a file name to save the file to:

::

  Please enter a filename to save the callback to. The filename must end
  with '.py', e.g. 'example.py':

Lets type in the file name 'sum_positive_ints.py' and press enter.

If we now check the 'local_callbacks' folder in the package installation
directory we'll see that we now have that new file: 'sum_positive_ints.py'.

  - If you don’t know where the package was installed then see
    `12.2 - How do I change directory to the package directory?`_


13.1.5 - Editing the new local callback file
""""""""""""""""""""""""""""""""""""""""""""

If we open 'sum_positive_ints.py' in our editor of choice we can see the
starting point for our code is as follows:

::

  from mqtt_remote.message import CommandMessageCallback



  class ClassName(CommandMessageCallback):
  """Class docstring
  """
  def __init__(self):
      """Constructor
      """
      # self.disabled = True # optional
      self._message_name = 'message' # required
      # self.config = None # optional
      # self.mqtt_publish = None # optional

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
      pass


  # Changes to make to the above to make it into usable code:
  #     Required:
  #         - Line 5: Replace 'ClassName' with an appropriate class name
  #         - Line 12: Replace 'message' after 'self._message_name =' with an appropriate message
  #                    name
  #         - Line 35: Replace 'pass' in the execute method with the code to execute if an MQTT
  #                    message json 'payload['command']' value matches self._message_name
  #     Optional:
  #         - Lines 6-7: Update the class docstring
  #         - Line 11: uncomment this line if you want to disable this callback (useful for
  #                    debugging)
  #         - Line 13: uncomment this line if you want to have access to the app configuration
  #                    from this class (via self.config)
  #         - Line 14: uncomment this line if you want to have access to the MQTT message publisher
  #                    via self.mqtt_publish (required if you want to send an MQTT message)


For this example it makes sense to introduce the finished code below and then
explain what was added and changed (highlighted) in order to form our
solution.


.. code-block:: python
  :linenos:
  :emphasize-lines: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 22, 24, 45,
   46, 47, 48, 49, 51, 52, 54

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

Taking a lead from '`12.8.2 - Callback class`_':

- Line 5: We've given the class a unique name.
- Lines 6 to 17: We've given the class a useful docstring.
- Line 22: We've set the message name to our unique descriptive string as
  defined in `13.1.3 - Designing the payload message`_.
- Line 24: We know we need to send an MQTT message as part of our solution so
  this line has been uncommented to enable the message publishing method.
- Lines 45 to 49: Here we're gathering all of the information we need from
  the inbound message.
- Lines 51 and 52: Here we calculate the sum using the data from our inbound
  message. We then convert this to a string ready for sending it as part of
  the outbound message.
- Line 54: This is where we publish our outbound message containing our sum.

(The block of comments was no longer required so was deleted.)


13.1.6 - Running the new callback
"""""""""""""""""""""""""""""""""

Now, if we stop and restart MQTT Remote then the changes will be picked up.

- `12.5 - How do I stop MQTT Remote?`_
- `12.4 - How do I start MQTT Remote?`_

meaning that if we now send the following MQTT message from our home
automation server MQTT client:

.. code-block:: none

  TOPIC: "RC"
  PAYLOAD: "{"command": "sum_positive_ints",
             "attributes": {"integer_one": 1,
                            "integer_two": 2,
                            "return_message": {"topic": "HA",
                                               "qos": 0,
                                               "retain": false}}}
  QOS: 0
  RETAIN: False

Then we'll receive the following payload back from the remote computer:

.. code-block:: none

  "3"


13.2 - Example 2 - Adding an existing callback to the app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

13.2.1 - Problem
""""""""""""""""

Let's say we need to reverse a string. Specifically:

- we have a microcontroller that's logging key presses from a keyboard
- the microcontroller is capable of sending and receiving MQTT messages
- the microcontroller is subscribed to the 'micro' MQTT topic
- we have a PC based server on our network
- the PC based server is running MQTT Remote
- MQTT Remote is subscribed to the 'server' MQTT topic
- both computers can communicate with an MQTT broker that's also on the
  network
- we want to be able to send a string of key presses from the microcontroller
  via an MQTT message and receive the reverse of that string back as an MQTT
  message.


13.2.2 - Solution
"""""""""""""""""

Luckily for us it seems someone else also wanted to reverse a string and has
already created a callback that does just that.

This callback class is called 'ReverseString' and can be found in the
'reverse_string.py' file in the 'example_callbacks' sub directory under
<project root> defined in '`11.0 - How do I install it?`_'.

To add this callback to the app we simply copy the 'reverse_string.py' file
from the 'example_callbacks' directory to the 'local_callbacks'
directory in our package installation directory.

  - See `12.7.2 - What are the rules for local callbacks?`_ for how to find
    the location of the 'local_callbacks' directory

We then need to open the 'reverse_string.py' file to see if there are any
import references to any libraries that we don't have installed. The import
references for 'reverse_string.py' are simply:

::

  from mqtt_remote.message import CommandMessageCallback

so there are no references to any external libraries meaning we don't need
to install anything.

And that's basically it. We can see from the callback docstring that the
callback requires a message in the form:

.. code-block:: none

  {"command": "reverse_string",
  "attributes": {"string_to_reverse": <str>,
                 "return_message": {"topic": <str>,
                                    "qos": <int>,
                                    "retain": <bool>}}}

So lets say someone typed 'racecar is a palindrome' on the keyboard. The
microcontroller would then send the following MQTT message:

.. code-block:: none

  TOPIC: "server"
  PAYLOAD:   {"command": "reverse_string",
              "attributes": {"string_to_reverse": "racecar is a palindrome",
                             "return_message": {"topic": "micro",
                                                "qos": 0,
                                                "retain": false}}}
  QOS: 0
  RETAIN: False

and in response it would receive an MQTT message back with the following
payload:

::

  "emordnilap a si racecar"


14 - Project status
-------------------

-  It's early days. If there’s significant interest I’ll try and find some
   time to work on it some more.
-  Feedback, feature requests, pull requests and issue reporting are all
   welcomed.


15 - To do
----------

- Write documentation for plugins.

  - Plugins are installed as separate apps within the same environment as
    MQTT Remote.

    - They allow for things like easy dependency management, e.g. when
      the plugin is installed the dependencies for its callbacks can be
      automatically installed at the same time.
    - Once installed, plugins are detected by MQTT Remote and their
      callbacks are automatically loaded when MQTT Remote is started.

  - An example plugin is included in the 'example_plugins' sub directory under
    <project root> defined in '`11.0 - How do I install it?`_'..

- Write documentation for development.
