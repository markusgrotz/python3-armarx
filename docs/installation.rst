Installation
============

You may install the ArmarX Python either as pypi packages, or from source via axii.

Option 1: Installation via PyPi Packages:
-----------------------------------------

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

Option 2: Installation via axii
-------------------------------

Create an axii module for your project. Below, you can find a short example. For an extensive documentation, visit https://git.h2t.iar.kit.edu/sw/armarx/meta/axii/-/blob/main/docs/module_authors/README.md.

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
        "optionally/add/further/packages/just/as/armarx/VisionX": {}
      }
    }

Add the axii package to your workspace and upgrade your workspace as usual (see https://git.h2t.iar.kit.edu/sw/armarx/meta/axii). This will automatically create the virtual environment and setup ArmarX Python.

Configuration
-------------

The ArmarX Python bindings read the available ArmarX projects from the
configuration :file:`$ARMARX_WORKSPACE/armarx_config/armarx.ini`.  The key
'packages' from the entry 'AutoCompletion' lists available packages that can be
loaded by the Python bindings.
