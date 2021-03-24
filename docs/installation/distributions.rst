Distributions
=============

**EXPLIoT** might be available for your favorite Linux distribution as
package. By using this installation method you don't need to take care
about pre-requirements and system's dependencies.

The downside is that you not always will get the latest release.

Fedora
------

The `Fedora Package Collection <https://apps.fedoraproject.org/packages/s/expliot>`_
contains **EXPLIoT**.

.. code-block:: console

   $ sudo dnf -y install expliot

It's also part of the `Fedora Security Lab <https://labs.fedoraproject.org/en/security/>`_.

Nix/NixOS
---------

The `NixOS package set <https://search.nixos.org/packages?channel=unstable&query=expliot>`_
contains the **EXPLIoT** release usually in the ``unstable`` channel.

.. code-block:: console

   $ nix-env -iA nixos.expliot
