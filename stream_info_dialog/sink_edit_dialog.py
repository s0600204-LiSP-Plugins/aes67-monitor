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

import re

# pylint: disable=no-name-in-module
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QTextEdit,
)

from .node import StreamDataRole, StreamDirection
from .stream_edit_dialog import StreamEditDialog
from .ui import GroupHeader


class SinkEditDialog(StreamEditDialog):

    # Not sure about these...
    _sample_delays = [
        192,
        384,
        576,
        768,
        960,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(StreamDirection.SINK, *args, **kwargs)

        self.setMinimumWidth(600)

        # Meta
        self._meta_header = GroupHeader()
        self._meta_header.setText("Sink")
        self.layout().addRow(self._meta_header)

        self._stream_name = QLineEdit()
        self.layout().addRow("Sink Name:", self._stream_name)

        # Source
        self._source_header = GroupHeader()
        self._source_header.setText("Attached Source")
        self.layout().addRow(self._source_header)

        self._use_sdp = QCheckBox()
        self._use_sdp.setChecked(False)
        self._use_sdp.stateChanged.connect(self._on_use_sdp_pressed)
        self.layout().addRow("Manual SDP:", self._use_sdp)

        self._sdp_url = QLineEdit()
        self._sdp_url.setDisabled(True)
        self.layout().addRow("SDP URL:", self._sdp_url)

        self._sdp_sources = QComboBox()
        self._sdp_sources.currentIndexChanged.connect(self._on_sdp_source_select)
        self.layout().addRow("SDP Sources:", self._sdp_sources)

        self._sdp_raw = QTextEdit()
        self._sdp_raw.setAcceptRichText(False)
        self._sdp_raw.setDisabled(True)
        self._sdp_raw.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addRow("SDP Text:", self._sdp_raw)

        self._ignore_refclk_gmid = QCheckBox()
        self.layout().addRow("Ignore Source PTP Master:", self._ignore_refclk_gmid)

        # Channels
        self._place_channel_widgets()

        # Audio Configuration
        self._spec_header = GroupHeader()
        self._spec_header.setText("Audio Config")
        self.layout().addRow(self._spec_header)

        self._delay = QComboBox()
        for sample in self._sample_delays:
            self._delay.addItem(str(sample))
        self.layout().addRow("Playout Sample Delay:", self._delay)

        # Buttons
        self.layout().addRow(self._button_box)

    def _on_use_sdp_pressed(self, _):
        use_sdp = self._use_sdp.isChecked()
        self._sdp_url.setDisabled(use_sdp)
        self._sdp_sources.setEnabled(use_sdp)
        self._sdp_raw.setEnabled(use_sdp)
        if use_sdp:
            self._sdp_url.setText("")
        else:
            self._sdp_sources.setCurrentIndex(0)
            self._sdp_raw.setPlainText("")

    def _on_sdp_source_select(self, _):
        text = self._sdp_sources.currentData()
        if text:
            self._sdp_raw.setPlainText(text)

    def _build_sdp_source_list(self):
        self._sdp_sources.clear()
        self._sdp_sources.addItem("-- Manual Entry Below --", None)

        model = self.parent().parent().sources.model
        for source in model:
            sdp = source.data(StreamDataRole.SDP)
            if not sdp:
                continue
            name = re.search(r's=(.*)\n', sdp).group(1)
            self._sdp_sources.addItem(name, sdp)

    def clear(self):
        super().clear()
        self.setWindowTitle("Creating New Sink")

        self._stream_name.setText("New Sink")

        self._use_sdp.setChecked(True)
        self._build_sdp_source_list()
        self._sdp_url.setText("")
        self._sdp_raw.setText("")

    def deserialise(self, stream_definition):
        super().deserialise(stream_definition)
        self.setWindowTitle(f"Editing Sink '{stream_definition['name']}'")

        # Meta
        self._stream_name.setText(stream_definition['name'])

        # Source
        self._use_sdp.setChecked(stream_definition['use_sdp'])
        self._sdp_url.setText(stream_definition['source'])
        self._ignore_refclk_gmid.setChecked(stream_definition['ignore_refclk_gmid'])

        self._build_sdp_source_list()
        if stream_definition['use_sdp']:
            idx = self._sdp_sources.findData(stream_definition['sdp'])
            if idx == -1:
                self._sdp_raw.setPlainText(stream_definition['sdp'])
            else:
                self._sdp_sources.setCurrentIndex(idx)

        # Audio Config
        self._delay.setCurrentText(str(stream_definition['delay']))

    def serialise(self):
        start = self._channel_start.value() - 1
        return {
            "name": self._stream_name.text(),
            "io": "Audio Device",
            "delay": int(self._delay.currentText()),
            "use_sdp": self._use_sdp.isChecked(),
            "source": self._sdp_url.text(),
            "sdp": self._sdp_raw.toPlainText(),
            "ignore_refclk_gmid": self._ignore_refclk_gmid.isChecked(),
            "map": [i + start for i in range(self._channel_count.value())]
        }
