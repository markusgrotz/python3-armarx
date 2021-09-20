Installation
============

The ArmarX Python bindings are available as packages.
Just grab the latest version from `pypi.humanoids.kit.edu <https://pypi.humanoids.kit.edu>`__ .

With poetry 

.. highlight:: bash
.. code-block:: bash

    poetry config repositories.h2t https://pypi.humanoids.kit.edu/simple/
    poetry add armarx-dev

or with pip

.. highlight:: bash
.. code-block:: bash

    pip install --extra-index-url https://pypi.humanoids.kit.edu/ armarx-dev



Alternatatively, you can create a project template with the `armarx-package`
tool, i.e. `armarx-package add python <your project name>`.  Then you can use
`poetry install` to setup a virtual env.

If you are using poetry then add the the following lines to `pyproject.toml`::



Configuration
-------------

The ArmarX Python bindings read the available ArmarX projects from the
configurtion :file:`$HOME/.armarx/armarx.ini`. Here the key 'packages' from the
entry 'AutoCompletion' is relevant.


