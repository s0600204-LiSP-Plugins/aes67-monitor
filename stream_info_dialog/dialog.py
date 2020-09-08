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
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QLabel, QListView, QVBoxLayout

from .delegate import StreamInfoDelegate
from .model import StreamInfoModelTemplate
from .node import StreamDirection


class StreamInfoDialog(QDialog):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle('AES67 Audio Streams')
        self.setMinimumSize(800, 600)
        self.setLayout(QGridLayout())

        self._source_model = StreamInfoModelTemplate(StreamDirection.SOURCE)
        self._source_model.addEntry()
        self._source_model.addEntry()

        self._sink_model = StreamInfoModelTemplate(StreamDirection.SINK)
        self._sink_model.addEntry()
        self._sink_model.addEntry()
        self._sink_model.addEntry()

        self._source_group = QGroupBox(parent=self)
        self._source_group.setTitle("Available Sources")
        self._source_group.setLayout(QVBoxLayout())
        self.layout().addWidget(self._source_group, 0, 0)

        self._source_list = _ListView()
        self._source_list.setModel(self._source_model)
        self._source_group.layout().addWidget(self._source_list)

        self._sink_group = QGroupBox(parent=self)
        self._sink_group.setTitle("Local Audio Sinks")
        self._sink_group.setLayout(QVBoxLayout())
        self.layout().addWidget(self._sink_group, 0, 1)

        self._sink_list = _ListView()
        self._sink_list.setModel(self._sink_model)
        self._sink_group.layout().addWidget(self._sink_list)


class _ListView(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._delegate = StreamInfoDelegate()
        self.setItemDelegate(self._delegate)
        self.setSpacing(self._delegate.margin)
        self.setUniformItemSizes(True)
