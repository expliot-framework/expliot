Developer Guide
===============

EXPLIoT Framework is a brilliant choice for vendors, smart infrastructure
admins, developers and security researchers for various reasons:

- It will streamline your security/regression testing.
- You will be able to identify security loopholes prior to deployment on an
  IoT solution in your infrastructure.
- It will help you in automating time consuming test cases.
- If you fall under any compliance or regulatory requirements for the IoT
  product or Smart Infrastructure, it will help you in automating and
  performing compliance checks regularly.
- It will save a lot of time during IoT security research or assessments.
- You can mold it to your needs by simply extending it with your own plugins.

If you are interested in extending the framework i.e. writing new plugins,
follow on.

Coding style
------------

Please follow the below coding style, when writing new code, if you are used
to some other style.

We use `Black <https://black.readthedocs.io/>`_ for code formatting. Every
merge request is automatically checked as part of the linting process and we
never merge submissions that diverge. We recommend to run ``black``, ``pylint``
and ``flake8`` locally before creating a merge request.

#. The code **must** follow `PEP8 (Style Guide for Python Code) <https://www.python.org/dev/peps/pep-0008/>`_.
#. Class names should be short, simple and define the purpose. It **must**
   be in `CamelCase <https://en.wikipedia.org/wiki/Camel_case>`_.
#. Import should be grouped and ordered, use ``isort``.
#. The method names **must not** use *CamelCase*.
   It may use underscores ("\_") for a name with more than one word.
#. Class member names should follow the same convention as method names.
#. Every module, function, class or method definition **must** have at least a
   `Docstring <https://www.python.org/dev/peps/pep-0257/>`_.

   It's preferred to have additional details for the API documentation.

   .. code-block:: console

      """ Method description.

      Args:
          param1 (type): param1 description
          param2 (type): param2 description

      Returns: (or Yields: for generators)
          type: Description of return value

      Raises:
          type: Description/reason of the exception
      """

Please refer to the `Google Python Style Guide <http://google.github.io/styleguide/pyguide.html>`_
for further information or if you are unsure about a specific topic.

Contribute
----------

If you are interested in contributing to the project. Please follow these
steps:

#. You must have an idea or a bug fix.
#. If this is your first time contributing to EXPLIoT, then please DO NOT
   submit a pull/merge request first thing. Instead please open an
   `issue <https://gitlab.com/expliot_framework/expliot/issues/new>`_
   describing your code changes.
#. Setup your development environment, see :ref:`development-setup`.
#. You will need to sign a contributor license agreement. Please sign, scan
   and email the same.
#. Create the merge request following the mentioned points in the previous
   section.

Additional details
------------------

.. toctree::
    :maxdepth: 1
    :glob:

    **
