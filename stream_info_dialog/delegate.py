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

# pylint: disable=missing-docstring

# pylint: disable=no-name-in-module
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QStyleOptionFocusRect

from .node import StreamDataRole, StreamDirection

class StreamInfoDelegate(QStyledItemDelegate):
    '''Display a Source or Sink'''
    # pylint: disable=too-few-public-methods

    margin = 3

    def createEditor(self, parent, option, index):
        # pylint: disable=invalid-name, no-self-use, unused-argument
        '''Disable the Editor'''
        return None

    def paint(self, painter, option, index):
        w = option.rect.width()
        h = option.rect.height()

        if option.state & QStyle.State_Selected:
            hi_rect = QRect(option.rect)
            hi_rect.adjust(1, 1, -1, -1)
            painter.save()
            painter.setPen(option.palette.highlight().color())
            painter.setBrush(option.palette.highlight())
            painter.drawRect(hi_rect)
            painter.restore()

        focrec = QStyleOptionFocusRect()
        focrec.palette = option.palette
        focrec.rect = QRect(option.rect)
        QApplication.style().drawPrimitive(QStyle.PE_FrameFocusRect, focrec, painter)

        painter.save()
        if option.state & QStyle.State_Selected:
            painter.setPen(option.palette.highlightedText().color())

        name_rect = QRect(option.rect)
        name_rect.adjust(
            self.margin,
            self.margin,
            self.margin,
            -h / 2 - self.margin
        )
        painter.drawText(name_rect, Qt.AlignVCenter, index.model().data(index, StreamDataRole.NAME))

        ch_rect = QRect(option.rect)
        ch_rect.adjust(
            self.margin,
            h / 2 + self.margin,
            -self.margin,
            -self.margin
        )
        painter.drawText(ch_rect, Qt.AlignVCenter, f"{index.internalPointer().data(StreamDataRole.CH_COUNT)} ch")

        if index.internalPointer().data(StreamDataRole.DIRECTION) == StreamDirection.SOURCE:
            info_rect = QRect(option.rect)
            info_rect.adjust(
                w / 2 + self.margin,
                h / 2 + self.margin,
                -self.margin,
                -self.margin
            )
            loc_text = 'Local' if index.internalPointer().data(StreamDataRole.IS_LOCAL) else 'Remote'
            painter.drawText(info_rect, Qt.AlignRight | Qt.AlignVCenter, loc_text)

        painter.restore()
