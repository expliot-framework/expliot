New Plugin (Test Case)
======================

Plugins are classes that inherit from ``Test`` base class and implement a
specific test case which can be an exploit, analysis, recon, fuzzer etc.
To extend the framework one can implement any number of plugins.

Sample Plugin `coap.generic.sample`
-----------------------------------

There is already a sample plugin implemented in the framework
`coap.generic.sample <https://gitlab.com/expliot_framework/expliot/tree/master/expliot/plugins/sample.py>`_
that explains the implementation *How tos* for a plugin. It would be better to
open the code of the plugin now and then follow the below documentation.

.. note::

   The sample plugin does not do any operation. It is only implemented
   to show the features you can use to implement a plugin.

Plugin Directory
----------------

**Module Directory**: ``expliot/plugins``

This is the home for all the plugins that are implemented in the framework.
Any new plugin file **must** be created in its corresponding directory within
the ``plugins`` directory.
For example, any BLE based plugin will go in the directory
``expliot/plugins/ble``. This is done to keep the directory structure clean and
help developers find the relevant plugins.

Plugin sections
---------------

The implementation of a plugin can be divided into four parts:

1. Plugin information
2. Plugin Arguments
3. Plugin methods
4. Plugin output

If you are reading this I'm guessing you want to create a new plugin. Well,
it is pretty simple to implement and add a new plugin to the framework. You
just need to be ready with the idea, logic and arguments. If you need a
specific protocol which is not part of the framework yet, just send us an
email describing your requirement and the reason why you think that the
protocol is important for IoT and needs to be added and we will add it to the
framework, if it looks like an interesting protocol.

.. note::

    #. The plugin file name and class name must be the same.
    #. The plugin must import functionality only from the framework or standard
       library. It must not import any functionality from external packages.

Plugin information
``````````````````

Plugin information can be thought of as an *About me* for the plugin which
defines what category the plugin belongs to and what is the target of the
plugin among other information. All this information goes in the ``__init__()``
method of the plugin as shown in the code below.

.. code-block:: python

   from expliot.core.tests.test import Test, TCategory, TTarget, TLog

   class Sample(Test):
       def __init__(self):
           super().__init__(
               name="Sample",
               summary="Sample Summary",
               descr="Sample Description",
               author="Sample author",
               email="email@example.com",
               ref=["https://example.com", "https://example.dom"],
               category=TCategory(TCategory.COAP, TCategory.SW, TCategory.EXPLOIT),
               target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC)
           )

Let's look at each parameter:

- ``name``: This is the name of the plugin and is part of the plugin ID. Keep
  it short but descriptive about the action and **DO NOT** use white space in
  the name.
- ``summary``: Summary of the plugin. This is displayed in the ``list`` command
- ``descr``: The description of the plugin. This is displayed when the plugin
  is run with the *-h* or *--help* argument. Please be as descriptive as
  possible assuming the user does not have much knowledge about the plugin
  and its features.
- ``author``: Plugin author's name
- ``email``: Plugin author's email ID
- ``ref``: A *list* containing one or more reference or source URLs containing
  either the exploit details or relevant information used as the basis of the
  plugin.
- ``category``: The category of the plugin defined by TCategory's technology,
  interface and action. For more details look at TCategory implementation in
  ``test.py``.
- ``target``: The (vulnerable) target of the Plugin defined by name, version and
  vendor as a ``TTarget`` object. If it is a generic plugin then use generic
  for all. We may start defining names and vendors in TTarget class itself
  for standardization.

**Other important parameters:**  

- ``needroot``: If the plugin needs root privileges, set this to *True*.
  **DO NOT** specify this if root privilege is not required. As of now, the
  framework checks if it has root privileges, if not it fails with the
  relevant message.

Plugin Arguments
````````````````

The plugin can be configured to run based on the requirements. It is done via
plugin arguments. For example, if a plugin needs to send payload to a server
it needs to know the server host name/IP and the port. All these parameters
can be assed with the arguments to the plugin. It is very simple to add and
utilize the arguments within the plugin. The parsing logic for the arguments
**must** be implemented in the ``execute()`` method. The argument implementation
for EXPLIoT is based on python ``argparse`` module which is part of the
`Python Standard Library <https://docs.python.org/3/library/>`_.

After we define the plugin information in the ``__init__()`` method (as shown
above), we have to populate the arguments for the plugin (also in the
``__init__()`` method). The *Test* base calls defines an ``argparse`` object and
initializes it in its ``__init__()`` method as shown below
(from ``expliot/core/tests/test.py``):

.. code-block:: python

   self.argparser = argparse.ArgumentParser(prog=self.id, description=self.descr)

For the *argument parser* in the framework the *self.id*  and *self.descr*
of the plugin become the name and the description respectively. Now, let's
look at how to add and use the arguments.

.. note::

   For more details on the API and how to use different methods like
   ``add_argument()``, please refer to the
   `argparse <https://docs.python.org/3/library/argparse.htm>`_ documentation.

Below is an excerpt from the ``coap.generic.sample`` plugin.

.. code-block:: python

   from expliot.core.tests.test import Test, TCategory, TTarget, TLog

   class Sample(Test):
       def __init__(self):
           super().__init__(
               name="Sample",
               summary="Sample Summary",
               descr="Sample Description",
               author="Sample author",
               email="email@example.com",
               ref=["https://example.com", "https://example.dom"],
               category=TCategory(TCategory.COAP, TCategory.SW, TCategory.EXPLOIT),
               target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC)
           )

           self.argparser.add_argument("-r", "--rhost", required=True, help="IP address of the target")
           self.argparser.add_argument("-p", "--rport", default=80, type=int, help="Port number of the target. Default is 80")
           self.argparser.add_argument("-v", "--verbose", action="store_true", help="show verbose output")


We have already discussed the information parameters above, let's focus on
adding arguments. To add an argument, you need to call the ``add_argument()``
method on the ``argparser`` object and pass the parameters as per the argument's
requirement. You can add as many arguments as required by the plugin by
invoking ``add_argument()`` method that many number of times.

- ``-r``: First parameter is the single hyphen-character representation of
   the argument.
- ``--rhost``: Second parameter is the double hyphen-word representation of
   the argument.
- ``help="IP address of the target"``: Specify the help string. It is
  **mandatory** to fill this. This is displayed along with the argument when
  plugin is run with *-h* or *--help* argument.
- ``required=True``: Set the *required* parameter to *True* the argument is
  mandatory. If it is optional, no need to specify this option.
- ``default=80``: If you want you can specify a default value for an argument.
- ``type=int``: You can specify the data type of the argument value. If not,
  specified, default data type is *string*.
- ``action="store_true"``: If an argument does not take any value. You can use
  this as a toggle to set the value of the argument to true (in this example)
  and decide your action based on whether the user specified this argument or
  not. As shown in the sample above it is used with the *verbose* argument.
- For any other requirements, not covered here refer to the
  `argparse <https://docs.python.org/3/library/argparse.htm>`_ documentation.

**Conventions for arguments:**

- Do not define *-h* and *--help* in the plugin as they are internally
  generated on the fly for help text of a plugin.
- Prefer to define *-r* and *--rhost* for remote server hostname or IP.
- Prefer to define *-p* and *--rport* for remote server port number.
- Prefer to define *-l* and *-lhost* for local server hostname or IP.
- Prefer to define *-q* and *--lport* for local server port number.
- Prefer to define *-v* and *--verbose* when you require verbose output option.
- Prefer to define *-a* and *--addr* for hardware addresses (MAC, BLE etc.).

Plugin methods
``````````````

There are three methods defined in the *Test* base calls which the plugins
will override for its execution. They are:

#. ``pre(self)``: This is an optional method. Any dependency/setup related
   logic for the plugin will go here. Please **DO NOT** add argument parsing
   logic in this method, that must go in the *execute()* method. The plugin
   author does not need to override this otherwise. As of now none of the
   plugins implement this (well, actually there are a few plugins, but the
   code will be changed soon).
#. ``post(self)``: This is an optional method. Any dependency/cleanup related
   logic for the plugin will go here. Please **DO NOT** add plugin fail/success
   logic in this method, that must go in the *execute()* method. The plugin
   author does not need to override this otherwise. As of now none of the
   plugins implement this (well, actually there are a few plugins, but the
   code will be changed soon).
#. ``execute(self)``: This method is **mandatory** to be overridden by the
   plugin class. This is where the exploit etc. logic will go. At the end of
   the method you need to set the status of the test case, if it failed as
   explained below. Also, the plugin needs to use *TLog* class methods for
   logging any output.

Plugin output
`````````````

The last but not the least is the output format of the plugin. Each plugin
needs to define a clear and standard output without any ambiguities. This
will solve two major concerns:

#. Automation: To help the users (devs, testers) to be able to automate the
   system within their CI/CD and testing phase with a reliable mechanism of
   parsing the output and deciding the course of action based on that.
#. Plugin Chaining: To be able to execute multiple plugins using a single
   plugin. In simple terms, one plugin may have a dependency on other
   plugin(s). A standardized output format will ensure that a plugin will
   be able to execute plugins that it is dependent on and get the required
   information from the output of that plugin(s).

The output format of a plugin is a list of dicts/lists. The main list is
created by the ``Test`` base class. The contents of the lists/dicts have to be
defined by the plugin author. All current plugins define their output and
can be referred to understand how to specify the format and create it in
the plugin. The `coap.generic.sample <https://gitlab.com/expliot_framework/expliot/tree/master/expliot/plugins/sample.py>`_
plugin also shows an example output format. The ``Test`` base class method
``output_handler()`` does the job of adding the dict/list to the main output
list as well as logging(printing) the output. The plugin author needs to call
this method whenever there is information to be added to the output. Please
read the method documentation as well as other plugin code for information
on how to implement it. In case there is a need to specifically call
``TLog`` class logging methods, they can still be used

The output format of a plugin must ensure:

#. It is clearly defined in the docstring of the plugin class
#. There are comments in front of optional fields of the output, specifying
   that it is optional.
#. It is indented clearly to show the hierarchy.
#. There are comments for repeatable lists/dicts. For example,
   "one or more", zero or more", etc.
#. String data is specified in double quotes and others without them.
#. Will use double quotes for specifying dict keys.

The output of a plugin is stored in ``TResult`` class object's ``self.output``
member. This must never be updated directly by the plugin even though it is
accessible via ``self.result.output`` of the plugin class. It is updated by
calling ``output_handler()`` method as of now.

**Example Format**

.. code-block::

    Output Format:
    [
        {
            "host": "192.168.12.11",
            "port": 1900,
            "services":
            [
                {
                    "name": "foo",
                    "type": "bar",
                    "actions":
                    [
                        {
                            "name": "foo",
                            "arguments":
                            [
                                {
                                    "name": "bar",
                                    "direction": "in",
                                    "return_value": None,
                                }, # Zero or more arguments
                            ]
                        }, # Zero or more actions
                    ],
                    "state_variables":
                    [
                        "foobar",
                        "barfoo",
                    ] # Zero or more state variables
                }, # Zero or more services
            ]
        }, # Zero or more device entries
        {
            "final_actions": 2
        }
    ]


Result
------

It is implemented by an object of ``TResult`` class which is a member of plugin
class object called ``result``, created and maintained by the ``Test`` base class.
The plugin's failure status (basically a Boolean and a message string) after
execution needs to be determined and then set accordingly before returning
from ``execute()`` method in case of failure. The plugin **MUST NOT** set
anything for successful execution. The complete result including the output
and the status can be obtained by calling plugin class object's
``self.result.getresult()`` method. There are two ways to set the status:

#. *Set specific message*: When you know the exact reason, you can set it
   using ``self.result.setstatus(passed=False, reason="Whatever reason")``
#. *Unknown/External Exception*: If there was an exception raised by another
   package and the plugin cannot handle all the cases, it can use
   ``self.result.exception()`` which basically sets the ``reason`` to the
   exception's message.

Refer to the `coap.generic.sample <https://gitlab.com/expliot_framework/expliot/tree/master/expliot/plugins/sample.py>`_
plugin's ``execute()`` method.

.. note:: It is mandatory to determine the fail criteria and call any of these
          methods in ``execute()``.

Logging
-------

All the logging within the plugin must use ``TLog`` class methods based on why/
what is being logged.

Refer to:

#. `TLog <https://gitlab.com/expliot_framework/expliot/tree/master/expliot/core/tests/test.py>`_
   class details for methods.
#. `coap.generic.sample <https://gitlab.com/expliot_framework/expliot/tree/master/expliot/plugins/sample.py>`_
   plugin's ``execute()`` method for usage.

.. note:: It is mandatory to use only ``TLog`` methods for logging. Please do
          not use any other Python ``print`` style methods.