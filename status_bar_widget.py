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

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

class StatusBarWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(5)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._title = QLabel(parent=self)
        self._title.setText("AES67:")
        self._title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addWidget(self._title)

        self._disconnect_caption = QLabel(parent=self)
        self._disconnect_caption.setText("Unable to Connect")
        self._disconnect_caption.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addWidget(self._disconnect_caption)

        self._ptp_caption = QLabel(parent=self)
        self._ptp_caption.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addWidget(self._ptp_caption)

        self._sinks_caption = QLabel(parent=self)
        self._sinks_caption.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addWidget(self._sinks_caption)

        self.clear()

    def update(self, *_, ptp=None, sinks=None):
        self._disconnect_caption.setVisible(False)
        if ptp:
            self._ptp_caption.setText(ptp)
            self._ptp_caption.setVisible(True)
        if sinks:
            self._sinks_caption.setText(sinks)
            self._sinks_caption.setVisible(True)

    def clear(self):
        self._disconnect_caption.setVisible(True)
        self._ptp_caption.setVisible(False)
        self._sinks_caption.setVisible(False)
