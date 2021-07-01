Examples
========



Retrieving a proxy
------------------

.. highlight:: python
.. code-block:: python


    from armarx import RNGProviderComponentInterface

    rng_provider = RNGProviderComponentInterfacePrx.get_proxy()
    rng_provider.generateRandomInt()


Creating a proxy
----------------


.. highlight:: python
.. code-block:: python


    #!/usr/bin/env python

    from armarx import RNGProviderComponentInterface
    from armarx import ice_manager

    import random


    class RNGProvider(RNGProviderComponentInterface):

        def generateRandomInt(self, current=None):
            r = int(random.random() * 1000)
            return r


    def main():
        ice_manager.register_object(RNGProvider(), 'RNGProvider')
        ice_manager.wait_for_shutdown()


    if __name__ == '__main__':
        main()

