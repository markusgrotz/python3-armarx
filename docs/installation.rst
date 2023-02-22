Installation
============

You may install the ArmarX Python bindings either as a pypi package, or from source. 

Installing from source guarantees to use the most up-to-date version of the code and enables you to contribute to the development of the ArmarX Python bindings itself. For installation from source, you can choose between a manual installation and an automated installation via Axii.

Option 1: Installation via PyPi Packages
-----------------------------------------

The ArmarX Python bindings are available as packages.
Just grab the latest version from `pypi.org <https://pypi.org/project/armarx/>`__ .

With Poetry:

.. highlight:: bash
.. code-block:: bash

    poetry add armarx

or with pip:

.. highlight:: bash
.. code-block:: bash

    pip install armarx


Alternatively, you can create a project template with the `armarx-package` tool:

.. highlight:: bash
.. code-block:: bash

    armarx-package add python <your python project name>

Then you can use `poetry install` or Axii to setup a virtual environment.


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


Option 2: Installation From Source, Manually
--------------------------------------------

Clone the repository of the ArmarX Python bindings to a location of your choice. If you have an ArmarX workspace with the module `armarx/python3-armarx` being active, executing `echo $armarx__python3_armarx__PATH` should return a path to the cloned repository in the workspace.

Within the base directory of your ArmarX project, run

.. highlight:: bash
.. code-block:: bash

    armarx-package add python subfolder-name

This creates a pyproject.toml at `python/subfolder-name/`, from which you can delete the armarx-dev dependency and the pypi.humanoids.kit.edu repository.

Still being in `python/subfolder-name/`, create a virtual environment by running

.. highlight:: bash
.. code-block:: bash

    python3 -m venv .venv

Update pip by running

.. highlight:: bash
.. code-block:: bash

    source .venv/bin/activate
    pip install --upgrade pip

Now you can install the dependencies of your python project, by running

.. highlight:: bash
.. code-block:: bash

    pip install -e .
    pip install -e path/to/the/armarx-python/repository
    # Alternatively, with an active ArmarX workspace with the `armarx/python3-armarx` module:
    pip install -e $armarx__python3_armarx__PATH


Option 3: Installation From Source, via Axii
--------------------------------------------

Create an Axii module for your project. Below, you can find a short example. For an extensive documentation, visit https://git.h2t.iar.kit.edu/sw/armarx/meta/axii/-/blob/main/docs/module_authors/README.md.

.. highlight:: json
.. code-block:: json

    {
      "general": {
        "url": "https://git.h2t.iar.kit.edu/path-to-your-project",
        "authors": [
          "FirstName LastName <mail@example.com>"
        ]
      },
    
      "update": {
        "git": {
          "h2t_gitlab_slug": "path-to-your-project"
        }
      },
    
      "prepare": {
        "cmake": {
          "definitions": {
            "CMAKE_C_COMPILER": "$ARMARX_C_COMPILER",
            "CMAKE_CXX_COMPILER": "$ARMARX_CXX_COMPILER"
          }
        },
        "python": {
          "packages": {
            "python/folder_of_your_python_project_in_which_to_create_a_venv": {
              "install_editable": [
                "$armarx__python3_armarx__PATH"
              ]
            }
          }
        }
      },
    
      "build": "cmake",
    
      "required_modules": {
        "tools/default_python_interpreter": {},
    
        "armarx/meta/compiler": {},
        "armarx/python3-armarx": {},
        "optionally/add/further/packages/such/as/armarx/VisionX": {}
      }
    }

Add the Axii module to your workspace and upgrade your workspace as usual (see https://git.h2t.iar.kit.edu/sw/armarx/meta/axii). This will automatically create the virtual environment and install the ArmarX Python bindings.



Configuration
-------------

The ArmarX Python bindings read the available ArmarX projects from the
configuration :file:`$ARMARX_WORKSPACE/armarx_config/armarx.ini`.  The key
'packages' from the entry 'AutoCompletion' lists available packages that can be
loaded by the Python bindings.
