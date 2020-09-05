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
from PyQt5.QtWidgets import QLabel, QSizePolicy

from lisp.ui.icons import IconTheme

from ..util import StatusEnum


class StatusIcon(QLabel):

    ICON_SIZE = 12
    ICON_MAP = {
        StatusEnum.UNKNOWN: 'led-off',
        StatusEnum.NORMAL: 'led-running',
        StatusEnum.WARNING: 'led-pause',
        StatusEnum.ERROR: 'led-error',
    }

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.update(StatusEnum.UNKNOWN)

    def update(self, new_status):
        self.setPixmap(
            IconTheme.get(
                self.ICON_MAP.get(new_status)
            ).pixmap(self.ICON_SIZE)
        )
