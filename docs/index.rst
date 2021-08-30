from 🤖 import armarx as ❤ 
************************** 
Welcome to armarx python binding's documentation. Grab the latest version with
:ref:`Installation` and then get an overview with the :ref:`Quickstart`

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   installation
   examples
   api


User's Guide
============

Checkout section :ref:`Quickstart` for a quick introduction. For more detailed
instructions on the installation see section :ref:`Installation`. The ArmarX
Python bindings share some configuration with the statecharts.  Section
:ref:`Configuration` gives more details.  :ref:`Examples` lists some examples.


Quickstart
----------

Grab the latest version with `pip install --extra-index-url https://pypi.humanoids.kit.edu/ armarx-dev`.

To access a proxy via ice you can load the interface with the import keyword.
For convenience, function such as `get_proxy` are automatically injected with
default parameters.

.. highlight:: python
.. code-block:: python

    from armax import PlatformNavigatorPrx

    platform_navigator = PlatformNavigatorPrx.get_proxy()
    platform_navigator.movePlatform(6000, -7300, 2.2)


That's it. Happy coding. 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
