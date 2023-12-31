from 🤖 import armarx as ❤ 
************************** 
Welcome to armarx python binding's documentation. Grab the latest version with
:ref:`Installation` and then get an overview with the :ref:`Quickstart`
If you are looking for information on a specific function checkout the API :ref:`API Reference`.

.. image:: _static/war-machine.jpg
   :scale: 50 %
   :alt: ArmarX Python bindings
   :align: center


User's Guide
============

Checkout section :ref:`Quickstart` for a quick introduction. For more detailed
instructions on the installation see section :ref:`Installation`. The ArmarX
Python bindings share some configuration with the statecharts.  Section
:ref:`Configuration` gives more details.  :ref:`Examples` lists some examples.


Quickstart
----------

Grab the latest version with `poetry add armarx` or `pip install armarx`.

To access a proxy via ice you can load the interface with the import keyword.
For convenience, functions such as `get_proxy` are automatically injected with
default parameters.

.. highlight:: python
.. code-block:: python

    from armax import PlatformNavigatorPrx

    platform_navigator = PlatformNavigatorPrx.get_proxy()
    platform_navigator.movePlatform(6000, -7300, 2.2)


That's it. Happy coding. 



Robots module
-------------

The `armarx_robots` module is an easy and convient way to control a robot.

.. highlight:: python
.. code-block:: python

    from armarx_robots import A6
    
    # we use the ARMAR-6 robot
    robot = A6()
    # use the text-to-speech system to say something
    robot.say('Hello World')

    # look at a specific target, i.e. in front of the robot
    from armarx import FramedPositionBase
    position = FramedPositionBase(0, 1000, 1650, frame='root', agent='Armar6'))
    robot.gaze.fixate(position)

    # close both hands
    robot.close_hand('both')
    robot.say('Here it is.')

    #execute the handover action. 
    robot.handover()
