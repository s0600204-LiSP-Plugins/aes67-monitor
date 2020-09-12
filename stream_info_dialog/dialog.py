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

# pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QLabel, QListView, QMessageBox, QPushButton

from lisp.ui.icons import IconTheme

from ..util import make_api_delete_request
from .delegate import StreamInfoDelegate
from .model import StreamInfoModelTemplate
from .node import StreamDataRole, StreamDirection
from .sink_edit_dialog import SinkEditDialog
from .source_edit_dialog import SourceEditDialog


class StreamInfoDialog(QDialog):

    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self._plugin = plugin

        self.setWindowTitle('AES67 Audio Streams')
        self.setMinimumSize(800, 600)
        self.setLayout(QGridLayout())

        self._source_model = StreamInfoModelTemplate(plugin, StreamDirection.SOURCE)
        self._sink_model = StreamInfoModelTemplate(plugin, StreamDirection.SINK)

        self._source_edit_dialog = None
        self._sink_edit_dialog = None

        # Sources
        self._source_group = QGroupBox(parent=self)
        self._source_group.setTitle("Available Sources")
        self._source_group.setLayout(QGridLayout())
        self.layout().addWidget(self._source_group, 0, 0)

        self._source_list = _ListView()
        self._source_list.setModel(self._source_model)
        self._source_list.selectionModel().selectionChanged.connect(self._on_source_list_select)
        self._source_group.layout().addWidget(self._source_list, 0, 0, 1, 3)

        self._source_new_btn = QPushButton(parent=self._source_group)
        self._source_new_btn.setText("New")
        self._source_new_btn.setIcon(IconTheme.get("list-add"))
        self._source_new_btn.pressed.connect(self._new_source)
        self._source_new_btn.setDisabled(True)
        self._source_group.layout().addWidget(self._source_new_btn, 1, 0)

        self._source_edit_btn = QPushButton(parent=self._source_group)
        self._source_edit_btn.setText("Edit")
        self._source_edit_btn.setIcon(IconTheme.get("applications-accessories"))
        self._source_edit_btn.pressed.connect(self._edit_source)
        self._source_edit_btn.setDisabled(True)
        self._source_group.layout().addWidget(self._source_edit_btn, 1, 1)

        self._source_delete_btn = QPushButton(parent=self._source_group)
        self._source_delete_btn.setText("Delete")
        self._source_delete_btn.setIcon(IconTheme.get("list-remove"))
        self._source_delete_btn.pressed.connect(self._del_source)
        self._source_delete_btn.setDisabled(True)
        self._source_group.layout().addWidget(self._source_delete_btn, 1, 2)

        # Sinks
        self._sink_group = QGroupBox(parent=self)
        self._sink_group.setTitle("Local Audio Sinks")
        self._sink_group.setLayout(QGridLayout())
        self.layout().addWidget(self._sink_group, 0, 1)

        self._sink_list = _ListView()
        self._sink_list.setModel(self._sink_model)
        self._sink_list.selectionModel().selectionChanged.connect(self._on_sink_list_select)
        self._sink_group.layout().addWidget(self._sink_list, 0, 0, 1, 3)

        self._sink_new_btn = QPushButton(parent=self._sink_group)
        self._sink_new_btn.setText("New")
        self._sink_new_btn.setIcon(IconTheme.get("list-add"))
        self._sink_new_btn.pressed.connect(self._new_sink)
        self._sink_new_btn.setDisabled(True)
        self._sink_group.layout().addWidget(self._sink_new_btn, 1, 0)

        self._sink_edit_btn = QPushButton(parent=self._sink_group)
        self._sink_edit_btn.setText("Edit")
        self._sink_edit_btn.setIcon(IconTheme.get("applications-accessories"))
        self._sink_edit_btn.pressed.connect(self._edit_sink)
        self._sink_edit_btn.setDisabled(True)
        self._sink_group.layout().addWidget(self._sink_edit_btn, 1, 1)

        self._sink_delete_btn = QPushButton(parent=self._sink_group)
        self._sink_delete_btn.setText("Delete")
        self._sink_delete_btn.setIcon(IconTheme.get("list-remove"))
        self._sink_delete_btn.pressed.connect(self._del_sink)
        self._sink_delete_btn.setDisabled(True)
        self._sink_group.layout().addWidget(self._sink_delete_btn, 1, 2)

        # Close button
        self._button_box = QDialogButtonBox(parent=self)
        self._button_box.addButton(QDialogButtonBox.Close)
        self._button_box.rejected.connect(self.reject)
        self.layout().addWidget(self._button_box, 1, 0, 1, 2)

    def open(self, *args, **kwargs):
        super().open(*args, **kwargs)
        self._plugin.poller.add_callback('streams', self.update_local_streams)
        self._plugin.poller.add_callback('remote_sources', self._source_model.updateRemoteSourcesFromDaemon)

    def reject(self, *args, **kwargs):
        super().reject(*args, **kwargs)
        self._plugin.poller.remove_callback('streams', self.update_local_streams)
        self._plugin.poller.remove_callback('remote_sources', self._source_model.updateRemoteSourcesFromDaemon)

    def update_local_streams(self, stream_json):
        self._source_new_btn.setEnabled(bool(stream_json))
        self._sink_new_btn.setEnabled(bool(stream_json))
        if not stream_json:
            self._source_edit_btn.setEnabled(False)
            self._source_delete_btn.setEnabled(False)
            self._sink_edit_btn.setEnabled(False)
            self._sink_delete_btn.setEnabled(False)
            return
        self._source_model.updateStreamsFromDaemon(stream_json['sources'])
        self._sink_model.updateStreamsFromDaemon(stream_json['sinks'])

    def local_stream_ids(self, direction):
        if direction == StreamDirection.SOURCE:
            return self._source_model.localStreamIds()
        else:
            return self._sink_model.localStreamIds()

    def source_model(self):
        return self._source_model

    def _init_source_dialog(self):
        self._source_edit_dialog = SourceEditDialog(self._plugin, parent=self)

    def _new_source(self):
        if not self._source_edit_dialog:
            self._init_source_dialog()
        self._source_edit_dialog.clear()
        self._source_edit_dialog.exec()

    def _edit_source(self):
        idx = self._source_list.selectionModel().currentIndex()
        if not idx.isValid() or not self._source_model.data(idx, StreamDataRole.IS_LOCAL):
            self._source_edit_btn.setEnabled(False)
            self._source_delete_btn.setEnabled(False)
            return

        if not self._source_edit_dialog:
            self._init_source_dialog()

        self._source_edit_dialog.deserialise(
            self._source_model.data(idx, StreamDataRole.RAW)
        )
        self._source_edit_dialog.exec()

    def _del_source(self):
        idx = self._source_list.selectionModel().currentIndex()
        if not idx.isValid() or not self._source_model.data(idx, StreamDataRole.IS_LOCAL):
            self._source_edit_btn.setEnabled(False)
            self._source_delete_btn.setEnabled(False)
            return
        msg_dia = _DelMsgBox(parent=self);
        msg_dia.setText(f'Delete source "{self._source_model.data(idx, StreamDataRole.NAME)}"?')

        if msg_dia.exec() & QMessageBox.Yes:
            make_api_delete_request(
                requests, self._plugin.address, 'source_edit', self._source_model.streamId(idx)
            )

    def _on_source_list_select(self, *args):
        idx = self._source_list.selectionModel().currentIndex()
        is_local = self._source_model.data(idx, StreamDataRole.IS_LOCAL)
        self._source_edit_btn.setEnabled(is_local)
        self._source_delete_btn.setEnabled(is_local)

    def _init_sink_dialog(self):
        self._sink_edit_dialog = SinkEditDialog(self._plugin, parent=self)

    def _new_sink(self):
        if not self._sink_edit_dialog:
            self._init_sink_dialog()
        self._sink_edit_dialog.clear()
        self._sink_edit_dialog.exec()

    def _edit_sink(self):
        idx = self._sink_list.selectionModel().currentIndex()
        if not idx.isValid():
            self._sink_edit_btn.setEnabled(False)
            self._sink_delete_btn.setEnabled(False)
            return

        if not self._sink_edit_dialog:
            self._init_sink_dialog()

        self._sink_edit_dialog.deserialise(
            self._sink_model.data(idx, StreamDataRole.RAW)
        )
        self._sink_edit_dialog.exec()

    def _del_sink(self):
        idx = self._sink_list.selectionModel().currentIndex()
        if not idx.isValid():
            self._sink_edit_btn.setEnabled(False)
            self._sink_delete_btn.setEnabled(False)
            return
        msg_dia = _DelMsgBox(parent=self);
        msg_dia.setText(f'Delete sink "{self._sink_model.data(idx, StreamDataRole.NAME)}"?')

        if msg_dia.exec() & QMessageBox.Yes:
            make_api_delete_request(
                requests, self._plugin.address, 'sink_edit', self._sink_model.streamId(idx)
            )

    def _on_sink_list_select(self, *args):
        self._sink_edit_btn.setEnabled(True)
        self._sink_delete_btn.setEnabled(True)

class _ListView(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._delegate = StreamInfoDelegate()
        self.setItemDelegate(self._delegate)
        self.setSpacing(self._delegate.margin)
        self.setUniformItemSizes(True)

class _DelMsgBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Deleting Audio Stream")
        self.setInformativeText("Warning: This cannot be undone!")
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
