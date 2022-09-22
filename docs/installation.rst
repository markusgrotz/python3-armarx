Installation
============

The ArmarX Python bindings are available as packages.
Just grab the latest version from `pypi.org <https://pypi.org/armarx>`__ .

With poetry 

.. highlight:: bash
.. code-block:: bash

    poetry add armarx

or with pip

.. highlight:: bash
.. code-block:: bash

    pip install armarx


Alternatatively, you can create a project template with the `armarx-package`
tool, i.e. `armarx-package add python <your project name>`.  Then you can use
`poetry install` to setup a virtual env.


Since the `zeroc-ice` package requires a rebuild you can grab already precompiled packages
from `pypi.humanoids.kit.edu <https://pypi.humanoids.kit.edu>`__ .
Just add the repository to your `pyproject.toml`

.. highlight:: bash
.. code-block:: bash

    poetry config repositories.h2t https://pypi.humanoids.kit.edu/simple/



If you are using poetry then add the the following lines to `pyproject.toml`

.. highlight:: toml
.. code-block:: toml

    [[tool.poetry.source]]
    name = "h2t"
    url = "https://pypi.humanoids.kit.edu/simple/"



Configuration
-------------

The ArmarX Python bindings read the available ArmarX projects from the
configurtion :file:`$ARMARX_WORKSPACE/armarx_config/armarx.ini`. Here the key 'packages' from the
entry 'AutoCompletion' is relevant.
