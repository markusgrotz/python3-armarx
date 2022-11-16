Examples
========


Example code snippets can be found in the [examples
folder](https://git.h2t.iar.kit.edu/sw/armarx/python3-armarx/-/tree/master/examples)
of the code repository.

In the following, 



Retrieving a proxy
------------------

Retrieving a proxy of a running component is straightforward.  Interface can be
directly imported and proxy can be accessed using  the `get_proxy` method.

.. highlight:: python
.. code-block:: python


    from armarx import RNGProviderComponentInterface

    rng_provider = RNGProviderComponentInterfacePrx.get_proxy()
    rng_provider.generateRandomInt()


Creating a proxy
----------------

An instance of the class that inherits the interace has to be created first.
Methods that are specified in the interface have to be implemented. In this
case `generateRandomInt`. Result parameters have to match the return value as
specified in the interface. The parameter `Ice::IceContext` is also passed to
every method that are defined in the interface.  Once an instance of the class
is created it can be registered with `ice_manager.register_object` and a name
of the proxy.  Other components can then load the interface and access the
component via the name of the proxy.


.. highlight:: python
.. code-block:: python


    import random

    from armarx import RNGProviderComponentInterface
    from armarx_core import ice_manager


    class RNGProvider(RNGProviderComponentInterface):

        def generateRandomInt(self, current=None):
            r = int(random.random() * 1000)
            return r


    def main():
        ice_manager.register_object(RNGProvider(), 'RNGProvider')
        ice_manager.wait_for_shutdown()


    if __name__ == '__main__':
        main()



Processing images
-----------------

The module `armarx_vision.image_processor` provides a class to conveniently
process images from armarx. Here the `process_images` method has to be
implemented.  The method has two parameters `images` and `info`.  The former
contains the images and the latter contains information about the images, e.g.
the timestamp. The return value of the method is a tuple of result images and
information about these.
The approach is similar to  :ref:`Creating a proxy`.  Note that
this method does not have an `Ice::IceContext` as it is not specified by a
slice interface. The method `ImageProcessor.on_connect()` takes care of
subscribing to the component that publishes the images, i.e.
`visionx::ImageProviderInterface`. Additionally, a component is created
internally that handles the result images.



.. highlight:: python
.. code-block:: python

    from armarx_vision.image_processor import ImageProcessor



    class TestImageProcessor(ImageProcessor):

        def process_images(self, images, info):
            info.timeProvided = 1633428148974550
            result_image = np.random.random(images.shape) * 128
            return result_image, info

    image_processor = TestImageProcessor("ExampleImageProvider")
    image_processor.on_connect()


