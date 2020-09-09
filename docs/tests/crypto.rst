Crypto
======

`Cryptography <https://en.wikipedia.org/wiki/Cryptography>`_
(Crypto) is the practice and study of techniques for secure communication
in the presence of third parties. More generally, cryptography is about
constructing and analyzing protocols that prevent third parties or the public
from reading private messages maintaining the confidentiality, authentication,
data integrity and non-repudiation.

crypto.tpliot.decrypt
---------------------

You can use this test case to decrypt the communication between TP-Link smart
devices and Kasa home application.


**Usage details:**

.. code-block:: console

   ef> run crypto.tpliot.decrypt -h

Examples
^^^^^^^^

The input data ``-d`` would be a HEX string from the captured communication.

.. code-block:: text

   ef> run crypto.tpliot.decrypt -d 00000066[...]ae9ee39ee3

   [...]
   [*]Decrypted Data :{"context":{"source":"46a4d58b-6279-432c-ae23-e115c2db8354"},"system":{"set_relay_state":{"state":0}}}
   [+] Test crypto.tpliot.decrypt passed


.. note::

   The HEX input should be without the ``0x`` prefix.
