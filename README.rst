
AES67 Monitor
=============

The **AES67 Monitor** is a community-created plugin for `Linux Show Player`_.

This plugin adds the ability to monitor a running instance of the bondagit_
`AES67 Daemon`_, and through it *AES67* and *AES67*-compatible audio streams on
the network.


Description
-----------

*AES67* is an Audio-over-IP technical standard that can either be used
standalone, or as a way to connect certain proprietary AoIP systems with
support for *AES67* (e.g. Dante, Ravenna, LiveWire+) that would be otherwise
unable to interoperate. More information can be found on the `AES67 page on
Wikipedia`_.

For Linux Systems, *AES67* support can be obtained by using the *Merging
Technologies*' `kernel driver`_ that adds *Ravenna* and *AES67* capabilities to
*ALSA*. Unfortunately, whilst the kernel driver itself is Open Source
(``GPLv3.0``), the "Butler" (the interface allowing configuration of audio
streams entering and leaving the computer running the driver) is not.

There is a way around that however: Andrea Bondavalli's `AES67 Daemon`_.

Andrea's daemon has an API that this plugin communicates with, allowing
in-program at-a-glance indication of status, in addition to rudimentary routing
of the local *AES67* audio connections.


Installation
------------

To use, navigate to ``$XDG_DATA_HOME/LinuxShowPlayer/$LiSP_Version/plugins/`` (on
most Linux systems ``$XDG_DATA_HOME`` is ``~/.local/share``), and create a subfolder
named ``aes67_monitor``.

Place the files comprising this plugin into this new folder.

When you next start *Linux Show Player*, the program should load the plugin
automatically.


.. _Linux Show Player: https://github.com/FrancescoCeruti/linux-show-player
.. _bondagit: https://github.com/bondagit
.. _AES67 page on Wikipedia: https://en.wikipedia.org/wiki/AES67
.. _kernel driver: https://bitbucket.org/MergingTechnologies/ravenna-alsa-lkm/src/master/
.. _AES67 Daemon: https://github.com/bondagit/aes67-linux-daemon
