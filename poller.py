# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2020 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2020 s0600204
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=missing-docstring

import requests

from lisp.core.clock import Clock

from .util import API_PATHS, make_api_get_request


UPDATE_INTERVAL = 2000 # milliseconds

class DaemonPoller:

    def __init__(self, plugin):
        self._plugin = plugin
        self._clock = Clock(UPDATE_INTERVAL)
        self._clock_started = False
        self._callbacks = {}

    def add_callback(self, what, callback):
        if what not in API_PATHS:
            return

        if what not in self._callbacks:
            self._callbacks[what] = []
        elif callback in self._callbacks[what]:
            return

        self._callbacks[what].append(callback)

        if not self._clock_started:
            self._clock_started = True
            self._clock.add_callback(self.run)

    def remove_callback(self, what, callback):
        if what not in API_PATHS or what not in self._callbacks or callback not in self._callbacks[what]:
            return

        self._callbacks[what].remove(callback)

        if not self._callbacks[what]:
            del self._callbacks[what]

        if not self._callbacks:
            self._clock.remove_callback(self.run)
            self._clock_started = False

    def run(self):
        with requests.Session() as session:
            address = self._plugin.address
            for what, callbacks in self._callbacks.items():
                reply = make_api_get_request(session, address, what)
                reply = reply.json() if reply else None
                for cb in callbacks:
                    cb(reply)
