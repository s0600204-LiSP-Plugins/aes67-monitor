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

# pylint: disable=import-error
from lisp.core.plugin import Plugin
from lisp.core.util import compose_url

from aes67_monitor.status_bar.indicator import StatusBarIndicator

class Aes67Monitor(Plugin):
    """Provides the ability to monitor AES67 connections"""

    Name = 'AES67 Daemon Monitor'
    Authors = ('s0600204',)
    Depends = ()
    Description = 'Monitors a running AES67 Daemon'

    SCHEME = "http"

    def __init__(self, app):
        super().__init__(app)

        self._ip = "127.0.0.1"
        self._port = 8080

        self.indicator = StatusBarIndicator(self)
        self.indicator.show()

    @property
    def address(self):
        return compose_url(self.SCHEME, self._ip, self._port)
