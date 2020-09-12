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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
)

from ..util import make_api_put_request
from .node import StreamDirection


class SinkEditDialog(QDialog):

    # See comment in SourceEditDialog class
    _channel_limit = 8

    # Not sure about these...
    _sample_delays = [
        192,
        384,
        576,
        768,
        960,
    ]

    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self._plugin = plugin
        self._editing_id = None

        self.setMinimumWidth(600)
        self.setLayout(QFormLayout())

        # Meta
        self._meta_label = QLabel()
        self._meta_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._meta_label.setIndent(2)
        self._meta_label.setMargin(2)
        self._meta_label.setText("Sink")
        self.layout().addRow(self._meta_label)

        self._sink_name = QLineEdit()
        self.layout().addRow("Sink Name:", self._sink_name)

        # Source
        self._source_label = QLabel()
        self._source_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._source_label.setIndent(4)
        self._source_label.setMargin(2)
        self._source_label.setText("Attached Source")
        self.layout().addRow(self._source_label)

        self._use_sdp = QCheckBox()
        self._use_sdp.setChecked(False)
        self._use_sdp.setDisabled(True) # Temporary
        self._use_sdp.stateChanged.connect(self._on_use_sdp_pressed)
        self.layout().addRow("Manual SDP:", self._use_sdp)

        self._sdp_url = QLineEdit()
        self._sdp_url.setDisabled(True)
        self.layout().addRow("SDP URL:", self._sdp_url)

        self._sdp_raw = QTextEdit()
        self._sdp_raw.setAcceptRichText(False)
        self._sdp_raw.setDisabled(True)
        self._sdp_raw.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addRow("SDP Text:", self._sdp_raw)

        self._ignore_refclk_gmid = QCheckBox()
        self.layout().addRow("Ignore Source PTP Master:", self._ignore_refclk_gmid)

        # Channels
        self._channels_label = QLabel()
        self._channels_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._channels_label.setIndent(4)
        self._channels_label.setMargin(2)
        self._channels_label.setText("ALSA Channels")
        self.layout().addRow(self._channels_label)

        self._channel_count = QSpinBox()
        self._channel_count.setRange(1, self._channel_limit)
        self._channel_count.valueChanged.connect(self._on_channel_count_change)
        self.layout().addRow("Channel Count:", self._channel_count)

        self._channel_start = QSpinBox()
        self._channel_start.setRange(1, self._channel_limit)
        self._channel_start.valueChanged.connect(self._on_channel_start_change)
        self.layout().addRow("Start Channel:", self._channel_start)

        self._channel_list = QLabel()
        self.layout().addRow("Mapped Channels:", self._channel_list)

        # Audio Configuration
        self._spec_label = QLabel()
        self._spec_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._spec_label.setIndent(4)
        self._spec_label.setMargin(2)
        self._spec_label.setText("Audio Config")
        self.layout().addRow(self._spec_label)

        self._delay = QComboBox()
        for sample in self._sample_delays:
            self._delay.addItem(str(sample))
        self.layout().addRow("Playout Sample Delay:", self._delay)

        # Buttons
        self._button_box = QDialogButtonBox()
        self._button_box.setStandardButtons(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self._button_box.accepted.connect(self.submit)
        self._button_box.rejected.connect(self.reject)
        self.layout().addRow(self._button_box)

    def _on_channel_count_change(self, value):
        value -= 1
        self._channel_start.setMaximum(self._channel_limit - value)
        self._update_channel_message()

    def _on_channel_start_change(self, value):
        value -= 1
        self._channel_count.setMaximum(self._channel_limit - value)
        self._update_channel_message()

    def _update_channel_message(self):
        start = self._channel_start.value()
        self._channel_list.setText(
            ", ".join([str(i + start) for i in range(self._channel_count.value())])
        )

    def _on_use_sdp_pressed(self, _):
        use_sdp = self._use_sdp.isChecked()
        self._sdp_url.setDisabled(use_sdp)
        self._sdp_raw.setEnabled(use_sdp)
        if use_sdp:
            self._sdp_url.setText("")
        else:
            self._sdp_raw.setPlainText("")

    def clear(self):
        self._editing_id = None
        self.setWindowTitle("Creating New Sink")

        self._sink_name.setText("New Sink")

        self._use_sdp.setChecked(True)
        self._sdp_url.setText("")
        self._sdp_raw.setText("")

        self._channel_start.setValue(1)
        self._channel_count.setValue(2)

    def deserialise(self, sink_json):
        self._editing_id = sink_json['id']
        self.setWindowTitle(f"Editing Sink '{sink_json['name']}'")

        # Meta
        self._sink_name.setText(sink_json['name'])

        # Source
        self._use_sdp.setChecked(sink_json['use_sdp'])
        self._sdp_url.setText(sink_json['source'])
        self._sdp_raw.setPlainText(sink_json['sdp'])
        self._ignore_refclk_gmid.setChecked(sink_json['ignore_refclk_gmid'])

        # Update channel mapping
        self._channel_start.setValue(1)
        self._channel_count.setValue(len(sink_json['map']))
        self._channel_start.setValue(sink_json['map'][0] + 1)

        # Audio Config
        self._delay.setCurrentText(str(sink_json['delay']))

    def serialise(self):
        start = self._channel_start.value() - 1
        return {
            "name": self._sink_name.text(),
            "io": "Audio Device",
            "delay": int(self._delay.currentText()),
            "use_sdp": self._use_sdp.isChecked(),
            "source": self._sdp_url.text(),
            "sdp": self._sdp_raw.toPlainText(),
            "ignore_refclk_gmid": self._ignore_refclk_gmid.isChecked(),
            "map": [i + start for i in range(self._channel_count.value())]
        }

    def submit(self):
        if self._editing_id is not None:
            stream_id = self._editing_id
        else:
            stream_id = max(self.parent().local_stream_ids(StreamDirection.SINK)) + 1

        reply = make_api_put_request(
            requests,
            self._plugin.address,
            'sink_edit',
            stream_id,
            self.serialise()
        )

        if reply:
            self.close()
        else:
            # todo: Implement error checking/messages
            print(reply)
