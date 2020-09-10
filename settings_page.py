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

# pylint: disable=missing-docstring, invalid-name

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLineEdit,
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

        # @todo: Get a list of all available network interfaces
        #        and their addresses and present them here
        self._ip_input = QLineEdit()
        self._ip_input.setInputMask('000.000.000.000')
        self.settingsGroup.layout().addRow('IP Address:', self._ip_input)

        self._port_input = QSpinBox()
        self._port_input.setRange(1000, 9000)
        self.settingsGroup.layout().addRow('IP Address:', self._port_input)

    def getSettings(self):
        return {
            'daemon_ip': self._ip_input.text(),
            'daemon_port': self._port_input.value(),
        }

    def loadSettings(self, settings):
        self._ip_input.setText(settings['daemon_ip'])
        self._port_input.setValue(settings['daemon_port'])
