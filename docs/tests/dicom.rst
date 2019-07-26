DICOM
=====

`Digital Imaging and Communications in Medicine <https://en.wikipedia.org/wiki/DICOM>`_
(DICOM) is a healthcare standard for communication and management of patient
information. It is used in various medical equipment to store and share image,
patient data, etc. If you are into medical security research the plugins will
help you in testing the security of these devices.

dicom.generic.c-echo
--------------------


This test is basically used to check if you can connect to a DICOM server and
get information about the software used as well. If you are not familiar with
DICOM, you can go through `this tutorial <http://dicomiseasy.blogspot.com/2011/10/introduction-to-dicom-chapter-1.html>`_
which explains the basics and essentials of the protocol. 

**Usage details:**

.. code-block:: console

   ef> run dicom.generic.c-echo -h

dicom.generic.c-find
--------------------

This test allows you to query data from the DICOM server. The protocol does
not specify any authentication process. The authentication for CFIND is
typically based on:

- Client IP: You can't do much about this, unless there is another way to
  extract that information or test from local network and hope there is no
  IP restriction.
- Client port: Can be specified using *-q* or *--lport* argument
- Called AET (server): Can be specified using *-s* or *--aetscp* argument

**Usage details:**

.. code-block:: console

   ef> run dicom.generic.c-find -h
