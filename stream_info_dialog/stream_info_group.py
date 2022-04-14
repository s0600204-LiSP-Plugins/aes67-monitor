# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2022 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2022 s0600204
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

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QListView,
    QMessageBox,
    QPushButton,
)

from lisp.ui.icons import IconTheme

from ..util import make_api_delete_request
from .delegate import StreamInfoDelegate
from .model import StreamInfoModelTemplate
from .node import StreamDataRole, StreamDirection
from .sink_edit_dialog import SinkEditDialog
from .source_edit_dialog import SourceEditDialog


class StreamInfoGroup(QGroupBox):

    def __init__(self, plugin, stream_direction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plugin = plugin
        self._stream_direction = stream_direction

        self._model = StreamInfoModelTemplate(self._plugin, self._stream_direction)
        self._edit_dialog = None
        self._view_delegate = StreamInfoDelegate()

        self.setLayout(QGridLayout())

        self._list_view = QListView()
        self._list_view.setItemDelegate(self._view_delegate)
        self._list_view.setModel(self._model)
        self._list_view.setSpacing(self._view_delegate.margin)
        self._list_view.setUniformItemSizes(True)
        self._list_view.selectionModel().selectionChanged.connect(self._on_list_select)
        self.layout().addWidget(self._list_view, 0, 0, 1, 3)

        self._create_button = QPushButton(parent=self)
        self._create_button.setDisabled(True)
        self._create_button.setIcon(IconTheme.get("list-add"))
        self._create_button.pressed.connect(self._create_stream)
        self.layout().addWidget(self._create_button, 1, 0)

        self._edit_button = QPushButton(parent=self)
        self._edit_button.setDisabled(True)
        self._edit_button.setIcon(IconTheme.get("applications-accessories"))
        self._edit_button.pressed.connect(self._edit_stream)
        self.layout().addWidget(self._edit_button, 1, 1)

        self._delete_button = QPushButton(parent=self)
        self._delete_button.setDisabled(True)
        self._delete_button.setIcon(IconTheme.get("list-remove"))
        self._delete_button.pressed.connect(self._delete_stream)
        self.layout().addWidget(self._delete_button, 1, 2)

        self.translate()

    def translate(self):
        # todo: Mark for Translation
        self._create_button.setText("New")
        self._edit_button.setText("Edit")
        self._delete_button.setText("Delete")

    def _init_edit_dialog(self):
        if self._edit_dialog:
            return
        if self._stream_direction == StreamDirection.SINK:
            self._edit_dialog = SinkEditDialog(self._plugin, parent=self)
        else:
            self._edit_dialog = SourceEditDialog(self._plugin, parent=self)

    def _create_stream(self):
        if not self._edit_dialog:
            self._init_edit_dialog()
        self._edit_dialog.clear()
        self._edit_dialog.exec()

    def _edit_stream(self):
        idx = self._list_view.selectionModel().currentIndex()
        if not idx.isValid() or not self._model.data(idx, StreamDataRole.IS_LOCAL):
            self._edit_button.setEnabled(False)
            self._delete_button.setEnabled(False)
            return

        if not self._edit_dialog:
            self._init_edit_dialog()

        self._edit_dialog.deserialise(
            self._model.data(idx, StreamDataRole.RAW)
        )
        self._edit_dialog.exec()

    def _delete_stream(self):
        idx = self._list_view.selectionModel().currentIndex()
        if not idx.isValid() or not self._model.data(idx, StreamDataRole.IS_LOCAL):
            self._edit_button.setEnabled(False)
            self._delete_button.setEnabled(False)
            return

        message = QMessageBox(parent=self)
        message.setDefaultButton(QMessageBox.No)
        message.setIcon(QMessageBox.Question)
        message.setInformativeText("Warning: This cannot be undone!")
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        name = self._model.data(idx, StreamDataRole.NAME)
        if self._stream_direction == StreamDirection.SINK:
            message.setText(f'Delete sink "{name}"?')
            message.setWindowTitle("Deleting Audio Sink")
        else:
            message.setText(f'Delete source "{name}"?')
            message.setWindowTitle("Deleting Audio Source")

        if message.exec() & QMessageBox.Yes:
            make_api_delete_request(
                requests, self._plugin.address, 'source_edit', self._model.streamId(idx)
            )

    def _on_list_select(self, _):
        idx = self._list_view.selectionModel().currentIndex()
        is_local = self._model.data(idx, StreamDataRole.IS_LOCAL)
        self._edit_button.setEnabled(is_local)
        self._delete_button.setEnabled(is_local)

    @property
    def model(self):
        return self._model

    def local_stream_ids(self):
        return self._model.localStreamIds()

    def update_local_streams(self, stream_definitions):
        if not stream_definitions:
            self._create_button.setEnabled(False)
            self._edit_button.setEnabled(False)
            self._delete_button.setEnabled(False)
            return
        self._create_button.setEnabled(True)
        self._model.updateLocalStreamsFromDaemon(stream_definitions)

    def update_remote_streams(self, stream_definitions):
        self._model.updateRemoteStreamsFromDaemon(stream_definitions)
