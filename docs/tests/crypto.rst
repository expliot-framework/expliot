Crypto
=======

`Cryptography <https://en.wikipedia.org/wiki/Cryptography>`_
(Crypto) is the practice and study of techniques for secure communication in the presence of third parties.More generally, cryptography is about constructing and analyzing protocols that prevent third parties or the public from reading private messages maintaining the confidentiality, authentication, data Integrity and non-repudiation. 

crypto.tpliot.decrypt
----------------------

You can use this test case to decrypt the communication between tp-link smart devices and kasa home application.



**Usage details:**

.. code-block:: console

   ef> run crypto.tpliot.decrypt -h

Examples
^^^^^^^^

The input data ``-d`` would be hex string from the captured communication.

.. code-block:: text

   ef> run crypto.tpliot.decrypt -d 00000066d0f291fe90e481f98daf95eeccbfd0a5d7b4d1f3c9ebdfe988bcd8edd5b79aac9ea990bd89ba88ebc6a7c2f0c3ee8bba8bbeddef8be9d1e2d7e3c1bc90b2c1b8cbbfdab795afd4f685e094cbb9dcb0d1a8f784f091e580a298e3c1b2c6a7d3b694ae9ee39ee3

   [...]
   [*]Decrypted Data :{"context":{"source":"46a4d58b-6279-432c-ae23-e115c2db8354"},"system":{"set_relay_state":{"state":0}}}
   [+] Test crypto.tpliot.decrypt passed


.. note::

   The hex input should be without the 0x prefix.
