# MetaSimulator

The goal of this project is a feature-complete [MetaWatch](http://www.metawatch.org/) emulator, implementing the [MetaWatch Remote Protocol](http://www.metawatch.org/assets/images/developers/MetaWatchRemoteMessageProtocolV1.0.pdf). At the moment, it supports the most important message types. The emulator communicates with real devices (Android and MetaWatchManager tested) over Bluetooth, and with software on the same machine using a virtual serial port.

It allows developers to write and test MetaWatch-compatible software without having to buy a development kit for their first experimentations, lowering the entry barrier to the platform.

![Screenshot](http://media.leoluk.de/metawatch-revolution.png)

## Installation

MetaSimulator runs on Windows, Linux and Mac. Theoretically, it could support iOS and Android, but this would require some non-trivial changes to the code.

You need Python 2.7 and wxPython 2.9, as well as the packages numpy, bitarray and pyserial. For Windows, you can download the binary packages: [Python](http://python.org/ftp/python/2.7.3/python-2.7.3.msi), [wxPython](http://downloads.sourceforge.net/wxpython/wxPython2.9-win32-2.9.3.1-py27.exe) and everything else from the [inofficial Python package site](http://www.lfd.uci.edu/~gohlke/pythonlibs/). On Linux and Mac, you should recompile Python from source, and use pip to download and compile the additional packages.
 
## Participation

This project is already usable, but far from finished. Expect that some buttons have no effect, and that things may not work as expected. Pull requests, feature proposals and bug reports are highly appreciated. Please report any problem or bug you encounter! The source code shouldn't be too hard to understand, and feel free to contact the author if you don't find your way around.

## Communication

MetaSimulator communicates using a serial port. Most bluetooth stacks (including the Microsoft stack) create virtual COM ports after pairing with a device implementing the serial port profile, which allows the simulator to talk to real bluetooth devices ([Picture](http://media.leoluk.de/metawatch-real_life2.jpg)).

If the emulator and the control software are running on the same computer, a virtual COM port like [com2com](http://com0com.sourceforge.net/). Note that all COM port names above COM9 (or the virtual names) have to be entered in the format `\\.\COM22` (or `\\.\CNCA0` for com2com).

## Implemented features

The current version supports all message types necessary for MetaWatchManager. Features like scrolling a SMS notification are fully working. Some non-essential ones are missing, but are easy to implement.

 * LCD screen, including different buffers 
 * Buttons (including press-and-hold event types and buffer awareness)
 * RTC clock
 * Device type request
 * LED
 * Vibration (including cycles and on/off timing)
 
## Missing features

 * Support for the analog watch (OLED display and watch hands)
 * NVAL store (GUI already working, parser missing)
 * Light readings
 * Battery/bluetooth power warnings