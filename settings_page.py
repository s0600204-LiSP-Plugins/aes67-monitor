# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2021 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2021 s0600204
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

# pylint: disable=missing-docstring, invalid-name

import netifaces as ni

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QVBoxLayout,
)

# pylint: disable=import-error
from lisp.ui.settings.pages import SettingsPage

class Aes67Settings(SettingsPage):
    Name = "AES67 Daemon"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())

        self.settingsGroup = QGroupBox(self)
        self.settingsGroup.setTitle("AES67 Daemon")
        self.settingsGroup.setLayout(QFormLayout())
        self.layout().addWidget(self.settingsGroup)

        self._iface_input = QComboBox()
        self.refresh_ifaces()
        self.settingsGroup.layout().addRow('Interface and IP Address:', self._iface_input)

        self._port_input = QSpinBox()
        self._port_input.setRange(1000, 9000)
        self.settingsGroup.layout().addRow('Port Number:', self._port_input)

    def refresh_ifaces(self):
        self._iface_input.clear()
        for iface in ni.interfaces():
            try:
                for addr in ni.ifaddresses(iface)[ni.AF_INET]:
                    addr = addr['addr']
                    self._iface_input.addItem(f"{iface}: {addr}", (iface, addr))
            except KeyError:
                continue

    def update_iface(self, iface, ip):
        '''
        Sets a suitable index in the combobox.

        If the supplied interface doesn't exist, or doesn't have IPv4 addresses,
        we fallback to the first interface and IPv4 address in the list.

        If the supplied interface exists, but doesn't have the stored IPv4 address,
        we fallback to that interface, but use the first IPv4 address that it has.
        '''
        iface_fallback = None
        for idx in range(self._iface_input.count()):
            entry = self._iface_input.itemData(idx)

            if entry[0] != iface:
                continue

            if entry[1] == ip:
                self._iface_input.setCurrentIndex(idx)
                return

            if not iface_fallback:
                iface_fallback = idx

        if iface_fallback:
            self._iface_input.setCurrentIndex(iface_fallback)
        else:
            self._iface_input.setCurrentIndex(0)

    def getSettings(self):
        iface = self._iface_input.currentData()
        return {
            'daemon_iface': iface[0],
            'daemon_ip': iface[1],
            'daemon_port': self._port_input.value(),
        }

    def loadSettings(self, settings):
        self.update_iface(settings['daemon_iface'], settings['daemon_ip'])
        self._port_input.setValue(settings['daemon_port'])
