A Python package for interfacing the Raspberry Pi board with the
Lelo(tm) Remote controller, with a TI CC2500 antenna.

Original idea & SPI debugging by Beth [#]_.

.. [#] http://scanlime.org/2012/11/hacking-my-vagina/

cc2500
------

This Python module implements some of stack for the Texas Instrument CC2500 2.4 GHz RF radio [#]_.

.. [#] http://www.ti.com/product/cc2500

The CC2500 is a relatively cheap antenna usually found in consumer devices.

The module implements various methods to control the radio, such as
configuring it, sending and receiving packages, etc.
It does not cover the full specs, so you will still need to get a copy
of them and read through them sometimes.

It has been written with a RaspberryPi in mind, but should be easy to
port it to other devices that support *spidev* and *GPIO* by changing
the appropriate modules.
